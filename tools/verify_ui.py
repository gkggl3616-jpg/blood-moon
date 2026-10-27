"""Exercise automatic intro playback and the offline mobile interface in a real browser."""
from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'
(ROOT / 'dist').mkdir(exist_ok=True)


def serve(route):
    path = route.request.url.split('https://rogue.local/', 1)[-1].split('?', 1)[0]
    file = (ASSETS / (path or 'index.html')).resolve()
    if not file.is_relative_to(ASSETS) or not file.is_file():
        route.fulfill(status=404, body='Not Found')
        return
    route.fulfill(path=str(file))


def assert_fits(page, selectors):
    page.wait_for_function('''() => {
        const r = document.getElementById('stage').getBoundingClientRect();
        const v = document.getElementById('viewport').getBoundingClientRect();
        return r.left >= v.left - 1 && r.top >= v.top - 1 &&
               r.right <= v.right + 1 && r.bottom <= v.bottom + 1;
    }''')
    viewport = page.locator('#viewport').bounding_box()
    for selector in selectors:
        rect = page.locator(selector).bounding_box()
        assert rect and rect['x'] >= viewport['x'] - 1 and rect['y'] >= viewport['y'] - 1, (selector, rect)
        assert rect['x'] + rect['width'] <= viewport['x'] + viewport['width'] + 1, (selector, rect, viewport)
        assert rect['y'] + rect['height'] <= viewport['y'] + viewport['height'] + 1, (selector, rect, viewport)


with sync_playwright() as p:
    # Native Android WebView also permits media playback without a user gesture.
    browser_options = {'headless': True, 'args': ['--no-sandbox', '--autoplay-policy=no-user-gesture-required']}
    if os.environ.get('ROGUE_BROWSER_CHANNEL'):
        browser_options['channel'] = os.environ['ROGUE_BROWSER_CHANNEL']
    elif shutil.which('chromium'):
        browser_options['executable_path'] = shutil.which('chromium')
    browser = p.chromium.launch(**browser_options)
    context = browser.new_context(viewport={'width': 960, 'height': 540}, device_scale_factor=1, is_mobile=True, has_touch=True)
    context.route('https://rogue.local/**', serve)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('https://rogue.local/index.html')
    # No click: the real video must begin on launch, then naturally end in the lobby.
    page.wait_for_function('() => document.getElementById("intro").currentTime > 0.1', timeout=15000)
    assert page.locator('#opening.active').count() == 1
    assert_fits(page, ['#intro', '#skipIntro', '#openingSound'])
    page.wait_for_selector('#lobby.active', timeout=15000)
    assert page.locator('#intro').evaluate('(v) => v.ended')
    page.locator('[data-event="moon"]').click()
    assert page.locator('#modalTitle').inner_text() == 'ETKİNLİK MERKEZİ'
    page.locator('#modalOk').click()
    page.locator('[data-room="foundry"]').click()
    page.locator('#join').click()
    assert page.locator('#modalTitle').inner_text() == 'DÖKÜMHANE'
    page.locator('#modalOk').click()
    page.locator('[data-room="bunker"]').click()
    page.locator('#join').click()
    assert page.locator('#map.active').count() == 1
    page.locator('#mapDetails').click()
    page.evaluate('window.goBack()')
    assert page.locator('.map-image.expanded').count() == 0
    page.evaluate('window.goBack()')
    page.locator('[data-nav="settings"]').click()
    page.locator('#soundToggle').click()
    page.locator('#volume').evaluate('(el) => { el.value = "25"; }')
    page.locator('#volume').dispatch_event('input')
    assert json.loads(page.evaluate("localStorage.getItem('rogue-settings')")) == {'audio': False, 'volume': .25}
    page.reload()
    assert page.locator('#openingSound').inner_text() == 'SES KAPALI'
    page.locator('#skipIntro').click()
    for key, title in [('events', 'ETKİNLİK MERKEZİ')]:
        page.locator(f'[data-nav="{key}"]').click()
        assert page.locator('#modalTitle').inner_text() == title
        page.locator('#closeModal').click()
    # Full-width design and compact overlays on real mobile viewports.
    for width, height in [(1280, 576), (800, 360), (915, 412), (740, 360), (1280, 720)]:
        page.set_viewport_size({'width': width, 'height': height})
        assert_fits(page, ['.brand', '#join', '[data-room="bunker"]', '[data-event="moon"]', '.bottomnav'])
        page.wait_for_function('() => Math.abs(document.getElementById("stage").getBoundingClientRect().width - document.getElementById("viewport").clientWidth) < 1')
        for tab in ['settings', 'events']:
            page.locator(f'[data-nav="{tab}"]').click()
            assert_fits(page, ['.modal-panel', '#modalOk', '#closeModal'])
            assert page.locator('.modal-panel').evaluate('(el) => el.scrollHeight <= el.clientHeight + 1'), tab
            page.locator('#closeModal').click()
    page.locator('[data-nav="events"]').click()
    page.locator('[data-event-tab="pack"]').click()
    assert '1.000 kredi' in page.locator('#modalBody').inner_text()
    assert 'henüz aktif değil' in page.locator('#modalBody').inner_text()
    page.screenshot(path=str(ROOT / 'dist/events-preview.png'))
    page.locator('#closeModal').click()
    page.locator('[data-nav="settings"]').click()
    page.screenshot(path=str(ROOT / 'dist/settings-preview.png'))
    page.locator('#closeModal').click()
    page.locator('[data-nav="gear"]').click()
    assert page.locator('#gear.active').count() == 1
    page.locator('[data-loadout="2"]').click()
    page.locator('[data-form="wolf"]').click()
    page.locator('[data-slot="Taktik ekipman"]').click()
    assert page.locator('#slotName').inner_text() == 'TAKTİK EKİPMAN'
    page.locator('#saveLoadout').click()
    assert json.loads(page.evaluate("localStorage.getItem('rogue-loadout')")) == {'set':'2','form':'wolf'}
    assert_fits(page, ['.gear-left', '.gear-right', '#saveLoadout', '#gear .gear-footer'])
    page.screenshot(path=str(ROOT / 'dist/gear-preview.png'))
    page.evaluate('window.goBack()')
    page.locator('[data-nav="shop"]').click()
    page.locator('[data-character="kul"]').click()
    page.locator('#previewWolf').click()
    assert '+8.5%' in page.locator('#collectionDetail').inner_text()
    page.locator('#characterAction').click()
    assert page.locator('#walletAmount').inner_text() == '1.750'
    page.locator('#characterAction').click()
    assert page.locator('#walletAmount').inner_text() == '1.750'
    page.locator('#inventoryMode').click()
    assert page.locator('[data-character]').count() == 2
    page.screenshot(path=str(ROOT / 'dist/inventory-preview.png'), animations='disabled')
    page.locator('[data-category="equipment"]').click()
    assert 'Silahlar' in page.locator('#collectionCards').inner_text()
    page.reload()
    page.locator('#skipIntro').click()
    page.locator('[data-nav="gear"]').click()
    assert page.locator('#operatorName').inner_text() == 'KÜL PENÇESİ'
    page.evaluate('window.goBack()')
    page.locator('[data-nav="shop"]').click()
    assert page.locator('[data-character]').count() == 7
    profiles = page.evaluate('roster')
    assert max(c['power'] for c in profiles) / min(c['power'] for c in profiles) <= 1.8
    assert all(0 <= value <= 80 for c in profiles for _, value in c['beast'])
    assert len({c['claw'] for c in profiles}) == len(profiles)
    assert len({c['trail'] for c in profiles}) == len(profiles)
    for character in ['bilge', 'kultigin', 'alparslan', 'konuralp']:
        page.locator(f'[data-character="{character}"]').click()
        assert 'Sıçrama düz ileriye' in page.locator('#collectionDetail').inner_text()
        assert 'İz sürme korunur' in page.locator('#collectionDetail').inner_text()
    assert page.locator('#abilities').count() == 0
    page.locator('[data-category="grenades"]').click()
    assert 'Duman bombası' in page.locator('#collectionCards').inner_text()
    page.locator('[data-category="weapons"]').click()
    assert page.locator('.blueprint-item').count() == 2
    page.locator('[data-category="knives"]').click()
    assert 'KAMA-01' in page.locator('#collectionCards').inner_text()
    page.locator('#openWolfGear').click()
    page.locator('#runPreview').click()
    assert not page.locator('#wolfFigure').evaluate('(e)=>e.classList.contains("run-preview")')
    page.locator('#equipRun').check()
    page.locator('#equipRoll').check()
    page.locator('#wolfAccessory').select_option('shoulder')
    page.locator('#saveWolfGear').click()
    equipment=json.loads(page.evaluate("localStorage.getItem('rogue-wolf-equipment')"))
    assert equipment == {'run':True,'roll':True,'accessory':'shoulder'}
    assert page.evaluate('wolfLoadouts.kul.run && wolfLoadouts.kul.roll')
    page.evaluate('collectionState.equipped="basibozuk";openWolfEquipment()')
    assert not page.locator('#equipRun').is_checked()
    assert not page.locator('#equipRoll').is_checked()
    page.evaluate('collectionState.equipped="kul";openWolfEquipment()')
    assert page.locator('#equipRun').is_checked()
    page.locator('#runPreview').click()
    assert page.locator('#wolfFigure.run-preview').count() == 1
    page.locator('#rollPreview').click()
    assert page.locator('#wolfFigure.roll-preview').count() == 1
    page.locator('#activateRoar').click()
    stats=page.evaluate('wolfStats()')
    assert stats['active'] and 19000 < stats['remaining'] <= 20000
    assert abs(stats['speed']-138) < .001
    assert page.locator('#wolfFigure.roaring').count() == 1
    assert page.locator('#activateRoar').is_disabled()
    # Check the real expiry calculation without sleeping for 20 seconds.
    page.evaluate('roarUntil = Date.now() - 1; updateRoar()')
    assert not page.evaluate('wolfStats().active')
    assert page.locator('#wolfFigure.roaring').count() == 0
    for character in page.evaluate('roster.map(c=>c.id)'):
        page.evaluate('(id)=>{collectionState.equipped=id;roarUntil=Date.now()+20000;}',character)
        assert max(page.evaluate('(()=>{const s=wolfStats();return [s.speed,s.damage,s.defense]})()')) <= 180.001
    page.evaluate('collectionState.equipped="kul";roarUntil=0;renderWolfEquipment()')
    assert_fits(page, ['.wolf-slots','.wolf-showcase','.roar-panel','#activateRoar'])
    page.screenshot(path=str(ROOT / 'dist/wolf-equipment-preview.png'), animations='disabled')
    page.evaluate('window.goBack()')
    (ROOT / 'dist/character-profiles.json').write_text(json.dumps(profiles, ensure_ascii=False, indent=2))
    page.screenshot(path=str(ROOT / 'dist/characters-preview.png'), animations='disabled')
    page.evaluate('window.goBack()')
    page.locator('#viewport').evaluate('(v) => { v.style.left="32px"; v.style.right="24px"; v.style.bottom="16px"; }')
    assert_fits(page, ['.brand', '#join', '.bottomnav'])
    page.locator('#viewport').evaluate('(v) => { v.style.left="0"; v.style.right="0"; v.style.bottom="0"; }')
    page.set_viewport_size({'width': 1280, 'height': 576})
    assert_fits(page, ['#join'])
    page.screenshot(path=str(ROOT / 'dist/lobby-preview.png'))
    # Replaying and skipping must stop the video without later reopening the intro.
    page.locator('.brand').click()
    page.wait_for_function('() => document.getElementById("intro").currentTime > 0.1')
    page.locator('#skipIntro').click()
    assert page.locator('#intro').evaluate('(v) => v.paused')
    assert page.locator('#lobby.active').count() == 1
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.locator('.portrait-hint').is_visible()
    # Missing or unsupported video must open the menu instead of leaving a dead intro.
    fallback = context.new_page()
    fallback.route('**/media/intro.mp4', lambda route: route.fulfill(status=404, body='Missing'))
    fallback.goto('https://rogue.local/index.html')
    fallback.wait_for_selector('#lobby.active', timeout=10000)
    assert not errors, errors
    browser.close()
    print('PASS: automatic video start and natural menu transition; skip and replay; media failure fallback; mobile viewport containment at five sizes and safe insets; lobby, events, map, tabs and persisted audio; no JS errors.')
