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
    browser_options = {'headless': True, 'args': ['--no-sandbox', '--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader', '--use-angle=swiftshader']}
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
    page.evaluate('rogueOpenScreen("map")')
    assert page.locator('#map.active').count() == 1
    page.locator('#mapDetails').click()
    page.evaluate('window.goBack()')
    assert page.locator('.map-image.expanded').count() == 0
    page.evaluate('window.goBack()')
    page.locator('[data-nav="settings"]').click()
    page.locator('#soundToggle').click()
    page.locator('#volume').evaluate('(el) => { el.value = "25"; }')
    page.locator('#volume').dispatch_event('input')
    assert json.loads(page.evaluate("localStorage.getItem('rogue-settings')")) == {'audio': False, 'volume': .25, 'lookSensitivity': 1.45, 'graphicsQuality': 'sharp'}
    page.reload()
    assert page.locator('#openingSound').inner_text() == 'SES KAPALI'
    page.evaluate('document.getElementById("skipIntro").click()')
    page.wait_for_selector('#lobby.active')
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
    assert page.locator('#collection.active').count()==1
    page.locator('#previewHuman').click()
    assert page.locator('[data-equip-slot]').count()==4
    page.evaluate('window.goBack()')
    page.locator('[data-nav="inventory"]').click()
    page.locator('#previewWolf').click()
    page.locator('[data-category="characters"]').click()
    page.locator('[data-character="bilge"]').click()
    page.locator('#characterAction').click()
    page.wait_for_function('()=>wolf3DInfo().visible',timeout=60000)
    # Pure bonus semantics, independent of character: +240 means 340, not 240.
    values=page.evaluate("""()=>{const base={damage:100,health:100,defense:100,speed:100};return [RogueGear.aggregate(base,{}, {damage:240}).values.damage,RogueGear.aggregate(base,{damage:20},{damage:240}).values.damage,RogueGear.aggregate(base,{damage:20},{damage:240},true).values.damage];}""")
    assert all(abs(a-b)<.001 for a,b in zip(values,[340,360,414])),values
    # Real purchase, owned grid, mouse drag, wrong slot, full slot replacement.
    page.locator('#shopMode').click();page.locator('[data-category="skills"]').click();page.locator('[data-power-filter="tattoos"]').click()
    page.locator('[data-gear-item="tattoo-reaper-back"]').click();page.locator('#itemAction').click()
    assert page.evaluate('collectionState.credits')==700
    assert page.evaluate('RogueGear.owns("tattoo-reaper-back")')
    page.locator('#inventoryMode').click()
    def drag_item(item,slot,touch=False):
        src=page.locator(f'[data-gear-item="{item}"]');src.scroll_into_view_if_needed();dst=page.locator(f'[data-equip-slot="{slot}"]');dst.scroll_into_view_if_needed()
        a=src.bounding_box();b=dst.bounding_box();sx=a['x']+a['width']/2;sy=a['y']+a['height']/2;ex=b['x']+b['width']/2;ey=b['y']+b['height']/2
        if not touch:
            page.mouse.move(sx,sy);page.mouse.down();page.mouse.move(ex,ey,steps=12);page.mouse.up()
        else:
            c=page.context.new_cdp_session(page)
            c.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':sx,'y':sy}]});page.wait_for_timeout(230)
            for n in range(1,13):c.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':sx+(ex-sx)*n/12,'y':sy+(ey-sy)*n/12}]})
            c.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});c.detach()
        page.wait_for_timeout(100)
    page.locator('#shopMode').click()
    old=page.evaluate('RogueGear.current("bilge").back');drag_item('tattoo-reaper-back','left')
    assert page.evaluate('RogueGear.current("bilge").back')==old
    drag_item('tattoo-reaper-back','back')
    assert page.evaluate('RogueGear.current("bilge").back')=='tattoo-reaper-back'
    assert abs(page.evaluate('RogueGear.stats("bilge").values.damage')-385)<.001
    assert 'Kullanılıyor' in page.locator('[data-gear-item="tattoo-reaper-back"]').inner_text()
    assert page.evaluate('RogueGear.owns("tattoo-dragon-back")'),'replacement destroyed previous item'
    page.locator('#inventoryMode').click()
    page.locator('[data-remove-slot="back"]').click()
    assert abs(page.evaluate('RogueGear.stats("bilge").values.damage')-145)<.001
    drag_item('tattoo-reaper-back','back',touch=True)
    assert page.evaluate('RogueGear.current("bilge").back')=='tattoo-reaper-back','touch drag failed'
    page.set_viewport_size({'width':800,'height':360})
    page.locator('[data-remove-slot="back"]').click();drag_item('tattoo-reaper-back','back',touch=True)
    assert page.evaluate('RogueGear.current("bilge").back')=='tattoo-reaper-back'
    page.set_viewport_size({'width':1280,'height':720})
    page.locator('[data-preset="1"]').click()
    assert page.evaluate('RogueGear.current("bilge").back') is None
    page.locator('[data-gear-item="tattoo-reaper-back"]').click();page.locator('#itemAction').click()
    assert page.evaluate('RogueGear.current("bilge").back')=='tattoo-reaper-back'
    page.locator('[data-preset="0"]').click()
    # Drag cancellation on blur and pointer cancellation leave previous loadout.
    src=page.locator('[data-gear-item="tattoo-dragon-back"]');src.scroll_into_view_if_needed();a=src.bounding_box()
    page.mouse.move(a['x']+20,a['y']+20);page.mouse.down();page.mouse.move(a['x']-20,a['y']+20);page.evaluate('window.dispatchEvent(new Event("blur"))');page.mouse.up()
    assert page.locator('.gear-drag-ghost').count()==0 and not page.evaluate('gearDragInfo().active')
    assert not page.evaluate('RogueGear.equip("bilge","wolf","left","tattoo-reaper-back").ok')
    assert not page.evaluate('RogueGear.equip("bilge","wolf","back","tattoo-unicorn-back").ok')
    page.screenshot(path=str(ROOT/'dist/inventory-wolf-v012.png'))
    # Human equipment is separate, and purchased weapon reaches actual arena.
    page.locator('#shopMode').click();page.locator('[data-category="weapons"]').click()
    page.locator('[data-gear-item="rifle-sr01"]').click();page.locator('#itemAction').click()
    assert page.evaluate('collectionState.credits')==150
    page.locator('#inventoryMode').click();drag_item('rifle-sr01','primary',touch=True)
    assert page.evaluate('RogueGear.current("bilge","human").primary')=='rifle-sr01'
    assert page.evaluate('RogueGear.current("bilge").back')=='tattoo-reaper-back'
    for width,height in [(1280,720),(800,360),(915,412),(740,360)]:
        page.set_viewport_size({'width':width,'height':height})
        assert_fits(page,['#loadoutTabs','#equipmentSlots','#collectionCards','#collectionDetail'])
    page.screenshot(path=str(ROOT/'dist/inventory-human-v012.png'))
    page.reload();page.locator('#skipIntro').click();page.locator('[data-nav="inventory"]').click()
    assert page.evaluate('RogueGear.current("bilge","human").primary')=='rifle-sr01'
    assert page.evaluate('RogueGear.current("bilge").back')=='tattoo-reaper-back'
    assert abs(page.evaluate('RogueGear.stats("bilge").values.damage')-385)<.001
    assert page.evaluate('collectionState.credits')==150
    page.evaluate('openArena()');page.wait_for_function('()=>arenaDebug.state().ready&&arenaDebug.state().time>.3',timeout=60000)
    assert page.evaluate('arenaDebug.state().weapon')=='rifle-sr01'
    assert page.evaluate('arenaDebug.state().ammo')==5
    page.evaluate('arenaDebug.aimAt(0)');page.wait_for_timeout(250);page.locator('#arenaFire').click()
    page.wait_for_function('()=>arenaDebug.state().targets[0].hp<100')
    assert abs(page.evaluate('arenaDebug.state().targets[0].hp')-33)<.01
    page.locator('[data-weapon-slot="secondary"]').click()
    assert page.evaluate('arenaDebug.state().weapon')=='pistol-p01'
    page.locator('#arenaTransform').click();page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct')
    assert page.evaluate('arenaDebug.state().attackCooldown')==0,'human weapon cooldown leaked into wolf form'
    assert abs(page.evaluate('arenaDebug.state().stats.damage')-385)<.001
    page.evaluate('arenaDebug.place(0,-5.8)');page.wait_for_timeout(500);before=page.evaluate('arenaDebug.state().hits');page.locator('#arenaFire').click()
    page.wait_for_function('(n)=>arenaDebug.state().hits>n',arg=before)
    assert page.evaluate('arenaDebug.state().targets[0].hp')==0,'tattoo not applied to melee'
    taken=page.evaluate('arenaDebug.receiveDamage(18)');assert abs(taken-11.25)<.001,'defense rating not used'
    assert page.evaluate('RogueGear.equip("bilge","wolf","back","tattoo-reaper-back").ok')
    page.locator('#arenaCharacter').select_option('bilge');page.wait_for_function('()=>arenaDebug.state().character==="bilge"&&document.getElementById("arenaLoad").hidden')
    assert abs(page.evaluate('arenaDebug.state().stats.damage')-385)<.001,'real tattoo bonus requires character passive (bilge beast dmg 45 + reaper 240)'
    # Migration preserves wallet and owned characters; old selected tattoos are granted once.
    legacy=browser.new_context(viewport={'width':960,'height':540});legacy.route('https://rogue.local/**',serve)
    legacy.add_init_script("localStorage.setItem('rogue-collection',JSON.stringify({credits:1234,owned:['basibozuk','bilge'],equipped:'bilge'}));localStorage.setItem('rogue-wolf-loadouts',JSON.stringify({bilge:{tattoos:{back:'phoenix',left:'runes',right:'dragon'}}}));")
    lp=legacy.new_page();lp.goto('https://rogue.local/index.html')
    assert lp.evaluate('collectionState.credits')==1234
    assert lp.evaluate('RogueGear.current("bilge").back')=='tattoo-phoenix-back'
    assert lp.evaluate('RogueGear.owns("tattoo-dragon-right")')
    lp.locator('#skipIntro').click();lp.locator('[data-nav="shop"]').click();lp.locator('[data-category="grenades"]').click()
    lp.locator('[data-gear-item="grenade-frag"]').click();lp.locator('#itemAction').click();lp.locator('#itemAction').click()
    assert lp.evaluate('RogueGear.current("bilge","human").grenade')=='grenade-frag'
    page.evaluate('stopArena()')
    lp.evaluate('openArena()');lp.wait_for_function('()=>arenaDebug.state().ready&&arenaDebug.state().time>.3',timeout=60000)
    lp.locator('[data-weapon-slot="grenade"]').click();lp.evaluate('arenaDebug.place(0,.5)');lp.wait_for_timeout(250);lp.locator('#arenaFire').click()
    assert lp.evaluate('arenaDebug.state().grenadeTime')>0
    lp.wait_for_function('()=>arenaDebug.state().projectiles===0&&arenaDebug.state().targets[0].hp<100',timeout=15000)
    assert lp.evaluate('RogueGear.owns("grenade-frag")'),'equipping or throwing consumed ownership'
    lp.locator('[data-weapon-slot="knife"]').click();lp.evaluate('arenaDebug.place(0,-6.7)');lp.wait_for_timeout(150)
    hp_before=lp.evaluate('arenaDebug.state().targets[0].hp');lp.locator('#arenaFire').click()
    lp.wait_for_function('(hp)=>arenaDebug.state().targets[0].hp<hp',arg=hp_before)
    assert abs(hp_before-lp.evaluate('arenaDebug.state().targets[0].hp')-34)<.01
    assert not errors,errors
    print(json.dumps({'result':'PASS','bonus_examples':values,'mouse_touch_drag':True,'presets_reload':True,'weapon_combat':True,'migration':True}))
    browser.close()
