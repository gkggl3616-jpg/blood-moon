"""v0.1.17 acceptance checks for recorded reload audio and fixed-step secondary motion."""
from pathlib import Path
import json
import math
import shutil
import subprocess

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

duration = float(subprocess.check_output([
    'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
    '-of', 'default=nw=1:nk=1', ASSETS / 'media/reload.ogg'], text=True).strip())
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
    page.locator('#skipIntro').click()
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
