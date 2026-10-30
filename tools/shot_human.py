from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'app/src/main/assets'
with sync_playwright() as p:
 options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required']}
 if shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
 b=p.chromium.launch(**options);page=b.new_page(viewport={'width':1280,'height':720},is_mobile=True,has_touch=True);errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type in('error','warning') else None)
 def serve(route):
  f=(ASSETS/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
  route.fulfill(path=str(f)) if f.is_relative_to(ASSETS) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve)
 page.goto('https://rogue.local/index.html');page.locator('#skipIntro').click();page.locator('#join').click()
 page.wait_for_function('()=>window.arenaDebug&&arenaDebug.state().ready',timeout=90000);page.wait_for_timeout(4000)
 page.screenshot(path='/tmp/fps_idle.png')
 print('errors',[e for e in errors if 'GPU' not in e][:5]);b.close()
