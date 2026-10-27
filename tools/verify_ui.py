"""Exercise the offline mobile interface using a real Chromium instance."""
from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'

with sync_playwright() as p:
    browser_options = {'headless': True, 'args': ['--no-sandbox']}
    if os.environ.get('ROGUE_BROWSER_CHANNEL'):
        browser_options['channel'] = os.environ['ROGUE_BROWSER_CHANNEL']
    elif shutil.which('chromium'):
        browser_options['executable_path'] = shutil.which('chromium')
    browser = p.chromium.launch(**browser_options)
    page = browser.new_page(viewport={'width': 960, 'height': 540}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))

    def serve(route):
        path = route.request.url.split('https://rogue.local/', 1)[-1].split('?', 1)[0]
        file = (ASSETS / (path or 'index.html')).resolve()
        if not file.is_relative_to(ASSETS) or not file.is_file():
            route.fulfill(status=404, body='Not Found')
            return
        route.fulfill(path=str(file))

    page.route('https://rogue.local/**', serve)
    page.goto('https://rogue.local/index.html')
    if (ASSETS / 'media/intro.mp4').exists():
        page.locator('#replay').click()
        try:
            page.wait_for_function('() => document.getElementById("intro").currentTime > 0.1', timeout=15000)
        except Exception:
            print(page.locator('#intro').evaluate('(v) => ({error: v.error && v.error.message, readyState: v.readyState, h264: v.canPlayType(\'video/mp4; codecs="avc1.4D401F"\'), aac: v.canPlayType(\'audio/mp4; codecs="mp4a.40.2"\')})'))
            raise
        page.evaluate('window.pauseApp()')
    page.locator('#enter').click()
    assert page.locator('#lobby.active').count() == 1
    page.locator('[data-event="moon"]').click()
    assert page.locator('#modal[open]').count() == 1
    assert page.locator('#modalTitle').inner_text() == 'KANLI AY'
    page.locator('#modalOk').click()
    page.locator('[data-room="foundry"]').click()
    assert page.locator('#selectedName').inner_text() == 'DÖKÜMHANE'
    page.locator('#join').click()
    assert page.locator('#modalTitle').inner_text() == 'DÖKÜMHANE'
    page.locator('#modalOk').click()
    page.locator('[data-room="bunker"]').click()
    page.locator('#join').click()
    assert page.locator('#map.active').count() == 1
    page.locator('#mapDetails').click()
    assert page.locator('.map-image.expanded').count() == 1
    page.evaluate('window.goBack()')
    assert page.locator('.map-image.expanded').count() == 0
    page.evaluate('window.goBack()')
    assert page.locator('#lobby.active').count() == 1
    page.locator('[data-nav="settings"]').click()
    page.locator('#soundToggle').click()
    page.locator('#volume').evaluate('(el) => { el.value = "25"; }')
    page.locator('#volume').dispatch_event('input')
    assert json.loads(page.evaluate("localStorage.getItem('rogue-settings')")) == {'audio': False, 'volume': .25}
    page.reload()
    assert page.locator('#openingSound').inner_text() == 'SES KAPALI'
    page.locator('#enter').click()
    for key, title in [('gear', 'TEÇHİZAT'), ('events', 'ETKİNLİKLER'), ('clan', 'KLAN')]:
        page.locator(f'[data-nav="{key}"]').click()
        assert page.locator('#modalTitle').inner_text() == title
        page.locator('#closeModal').click()
    # Touch targets remain within the landscape viewport at a small phone size.
    page.set_viewport_size({'width': 800, 'height': 360})
    for selector in ['#join', '[data-room="bunker"]', '[data-event="moon"]']:
        rect = page.locator(selector).bounding_box()
        assert rect and rect['x'] >= 0 and rect['y'] >= 0
        assert rect['x'] + rect['width'] <= 801 and rect['y'] + rect['height'] <= 361
    page.set_viewport_size({'width': 1280, 'height': 720})
    page.screenshot(path=str(ROOT / 'dist/lobby-preview.png'))
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.locator('.portrait-hint').is_visible()
    assert not errors, errors
    browser.close()
    print('PASS: lobby, events, map selection, map zoom, back navigation, persisted audio settings, all tabs, small landscape layout, portrait prompt; no JS errors.')
