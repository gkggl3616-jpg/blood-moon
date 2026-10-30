"""Screenshots of the new wolf inside the real arena (idle, run, roar, roll, claw)."""
from pathlib import Path
import os,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'app/src/main/assets'
with sync_playwright() as p:
 options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required']}
 if shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
 b=p.chromium.launch(**options);page=b.new_page(viewport={'width':1280,'height':720},is_mobile=True,has_touch=True);errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  f=(ASSETS/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
  route.fulfill(path=str(f)) if f.is_relative_to(ASSETS) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve)
 page.goto('https://rogue.local/index.html');page.locator('#skipIntro').click();page.locator('#join').click()
 page.wait_for_function('()=>window.arenaDebug&&arenaDebug.state().ready',timeout=90000)
 page.evaluate('arenaDebug.place(0,5)');page.locator('#arenaTransform').click()
 page.wait_for_function('()=>arenaDebug.state().form==="wolf"',timeout=30000);page.wait_for_timeout(1500)
 page.screenshot(path='/tmp/game_idle.png')
 page.locator('#arenaRun').click();page.keyboard.down('KeyW');page.wait_for_timeout(900);page.screenshot(path='/tmp/game_run1.png');page.wait_for_timeout(180);page.screenshot(path='/tmp/game_run2.png');page.keyboard.up('KeyW')
 page.wait_for_timeout(500);page.locator('#arenaRoarButton').click();page.wait_for_timeout(250);page.screenshot(path='/tmp/game_roar0.png');page.wait_for_timeout(350);page.screenshot(path='/tmp/game_roar.png')
 page.wait_for_timeout(1600);page.locator('#arenaRoll').click();page.wait_for_timeout(250);page.screenshot(path='/tmp/game_roll.png')
 print('errors',errors[:5]);b.close()
