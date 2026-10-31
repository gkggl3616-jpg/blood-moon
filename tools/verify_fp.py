"""First-person check for every character: arms load, both hands reach their grip on every weapon at level, up and
down pitch, and the arm mesh only follows the arm chain (static part lives in verify_models.py)."""
from pathlib import Path
import os, shutil, json
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]; ASSETS = ROOT / 'app/src/main/assets'
CHARS = ['bilge', 'ates', 'kral', 'ay', 'hellgate', 'zeynos']; MAX_GAP = .02   # palm centre to the weapon's grip socket (m)
with sync_playwright() as p:
    opts = {'headless': True, 'args': ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader']}
    if os.environ.get('ROGUE_BROWSER_CHANNEL'): opts['channel'] = os.environ['ROGUE_BROWSER_CHANNEL']
    elif shutil.which('chromium'): opts['executable_path'] = shutil.which('chromium')
    b = p.chromium.launch(**opts); page = b.new_page(viewport={'width': 960, 'height': 540}); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    def serve(route):
        f = (ASSETS / route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
        route.fulfill(path=str(f)) if f.is_file() and f.is_relative_to(ASSETS) else route.fulfill(status=404, body='missing')
    page.route('https://rogue.local/**', serve)
    page.goto('https://rogue.local/index.html'); page.locator('#skipIntro').click(); page.locator('#join').click()
    page.wait_for_function('()=>window.arenaDebug&&arenaDebug.state().ready', timeout=120000)
    bad = []
    for c in CHARS:
        page.evaluate('c=>arenaDebug.setCharacter(c)', c)
        page.wait_for_function('()=>arenaDebug.fp()&&arenaDebug.fp().fit', timeout=120000)
        for slot in ('primary', 'secondary'):
            page.evaluate('w=>arenaDebug.selectWeapon(w)', slot); page.wait_for_timeout(300)
            for pitch in (0, .9, -.9):
                page.evaluate('p=>arenaDebug.place(0,6,0,p)', pitch)
                try:   # allow the weapon-swap / character-load transition to finish (a few frames in headless)
                    page.wait_for_function('m=>{let r=arenaDebug.fp();return r&&r.model&&r.sockL!=null&&r.sockL<m&&r.sockR<m}', arg=MAX_GAP, timeout=12000)
                except Exception: pass
                r = page.evaluate('arenaDebug.fp()')
                if not r or not r.get('model') or r.get('sockL') is None or r['sockL'] > MAX_GAP or r['sockR'] > MAX_GAP: bad.append((c, slot, pitch, r))
            if slot == 'primary':   # third person: the full body holds the same weapon with both palms on its grips
                page.evaluate('arenaDebug.action("view")'); page.evaluate('arenaDebug.place(0,6,0,0)')
                try: page.wait_for_function('m=>{let r=arenaDebug.tp();return r.visible&&r.sockL!=null&&r.sockL<m&&r.sockR<m}', arg=MAX_GAP, timeout=12000)
                except Exception: pass
                t = page.evaluate('arenaDebug.tp()')
                if not t.get('visible') or t.get('sockL') is None or t['sockL'] > MAX_GAP or t['sockR'] > MAX_GAP: bad.append((c, 'third-person', t))
                page.evaluate('arenaDebug.action("view")')
    b.close()
    assert not errors, errors
    assert not bad, ('first-person hands miss their grip', bad)
    print('PASS: %d characters hold rifle and pistol by their grip sockets in first person (level/up/down) and the rifle in third person' % len(CHARS))
