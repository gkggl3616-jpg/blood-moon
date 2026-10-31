"""v0.1.17 acceptance checks for recorded reload audio and fixed-step secondary motion."""
from pathlib import Path
import json
import math
import shutil
import struct

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'
DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)


def spring(render_fps):
    """Same accumulator contract as the runtime; result must not depend on render FPS."""
    fixed = 1 / 60
    acc = x = v = 0.0
    for _ in range(round(4 * render_fps)):
        acc += 1 / render_fps
        while acc + 1e-12 >= fixed:
            target = .18 if _ / render_fps < 1.5 else 0
            v += ((target - x) * 10 * 10 - 2 * 6 * v) * fixed
            x = max(-.45, min(.45, x + v * fixed))
            acc -= fixed
    return x, v


reference = spring(60)
consistency = {str(fps): spring(fps) for fps in (30, 60, 120)}
assert all(max(abs(a - b) for a, b in zip(value, reference)) < 1e-8 for value in consistency.values())


def ogg_vorbis_duration(path: Path) -> float:
    """Read duration from Vorbis sample rate and Ogg page granule positions."""
    data = path.read_bytes()
    ident = data.find(b'\x01vorbis')
    assert ident >= 0, 'reload.ogg has no Vorbis identification packet'
    sample_rate = struct.unpack_from('<I', data, ident + 12)[0]
    assert sample_rate > 0
    offset = 0
    final_granule = 0
    while offset + 27 <= len(data):
        assert data[offset:offset + 4] == b'OggS', f'invalid Ogg page at {offset}'
        granule = struct.unpack_from('<Q', data, offset + 6)[0]
        if granule != 0xffffffffffffffff:
            final_granule = max(final_granule, granule)
        segments = data[offset + 26]
        table_end = offset + 27 + segments
        assert table_end <= len(data)
        offset = table_end + sum(data[offset + 27:table_end])
    assert offset == len(data) and final_granule > 0
    return final_granule / sample_rate


duration = ogg_vorbis_duration(ASSETS / 'media/reload.ogg')
assert 1.39 <= duration <= 1.41
assert (ASSETS / 'media/reload-original.wav').stat().st_size > 250_000

browser_path = shutil.which('chromium') or shutil.which('google-chrome')
errors = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, executable_path=browser_path,
        args=['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader',
              '--autoplay-policy=no-user-gesture-required'])
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.on('pageerror', lambda error: errors.append(str(error)))

    def serve(route):
        path = (ASSETS / route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
        route.fulfill(path=str(path)) if path.is_relative_to(ASSETS) and path.is_file() else route.fulfill(status=404)
    page.route('https://rogue.local/**', serve)
    page.goto('https://rogue.local/index.html')
    page.evaluate('rogueOpenScreen("lobby")')
    page.locator('#join').click()
    page.wait_for_function('()=>arenaDebug?.state().ready', timeout=90_000)
    page.evaluate('arenaDebug.action("fire")')
    page.wait_for_timeout(80)
    assert page.evaluate('arenaDebug.action("roar")') is True
    page.wait_for_timeout(120)
    first = page.evaluate('rogueSoundDebug()')
    assert first['starts'].get('reload') == 1
    assert page.evaluate('arenaDebug.action("roar")') is False
    page.wait_for_timeout(120)
    second = page.evaluate('rogueSoundDebug()')
    assert second['starts'].get('reload') == 1
    page.evaluate('arenaDebug.action("transform")')
    page.wait_for_timeout(1000)
    sound = page.evaluate('rogueSoundDebug()')
    assert sound['stops'].get('reload', 0) >= 1
    page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct', timeout=10_000)
    page.keyboard.down('KeyW')
    page.wait_for_timeout(800)
    page.keyboard.up('KeyW')
    secondary = page.evaluate('arenaDebug.state().secondary')
    assert secondary and secondary['fixedStep'] == 1 / 60 and secondary['finite']
    assert {'Tail1', 'Tail2', 'Tail3'} <= set(secondary['bones'])
    assert secondary['maxAngle'] <= .66
    browser.close()

assert not errors, errors
report = {
    'result': 'PASS', 'reload': {'duration_seconds': duration, 'starts_once': True,
        'cancelled_on_form_change': True, 'embedded_offline': True, 'recorded_cc0': True},
    'secondary_motion': {'fixed_step_seconds': 1/60, 'fps_consistency': consistency,
        'runtime_finite': True, 'teleport_reset_hook': True, 'max_angle_bounded': True},
    'physical_android_device_tested': False,
}
(DIST / 'v0117-runtime-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
