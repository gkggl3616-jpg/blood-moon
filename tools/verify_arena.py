"""Play the actual offline arena: inputs, camera modes, motion, damage and VFX."""
from pathlib import Path
import os,shutil,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'app/src/main/assets';(ROOT/'dist').mkdir(exist_ok=True)
with sync_playwright() as p:
 options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required']}
 if os.environ.get('ROGUE_BROWSER_CHANNEL'):options['channel']=os.environ['ROGUE_BROWSER_CHANNEL']
 elif shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
 browser=p.chromium.launch(**options);page=browser.new_page(viewport={'width':1280,'height':720},is_mobile=True,has_touch=True);errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:errors.append(m.text) if m.type=='error' and ('Shader' in m.text or 'WebGL' in m.text) else None)
 def serve(route):
  f=(ASSETS/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
  if not f.is_relative_to(ASSETS) or not f.is_file():route.fulfill(status=404,body='missing')
  else:route.fulfill(path=str(f))
 page.route('https://rogue.local/**',serve)
 page.goto('https://rogue.local/index.html');page.locator('#skipIntro').click();page.locator('#join').click()
 page.wait_for_function('()=>window.arenaDebug&&arenaDebug.state().ready',timeout=90000)
 def state():return page.evaluate('arenaDebug.state()')
 assert state()['form']=='human' and state()['render']['contexts']==1
 def check_vertical_look():
  baseline=state()['lookDirection'][1]
  page.mouse.move(750,330);page.mouse.down();page.mouse.move(750,260,steps=4);page.mouse.up()
  page.wait_for_function('(base)=>arenaDebug.state().lookDirection[1]>base+.12',arg=baseline,timeout=10000)
  raised=state()['lookDirection'][1]
  page.mouse.move(750,260);page.mouse.down();page.mouse.move(750,400,steps=4);page.mouse.up()
  page.wait_for_function('(base)=>arenaDebug.state().lookDirection[1]<base-.18',arg=raised,timeout=10000)
 check_vertical_look()
 page.evaluate('arenaDebug.place(0,8)')
 page.evaluate('arenaDebug.aimAt(0)');page.wait_for_timeout(200);page.locator('#arenaFire').click()
 page.wait_for_function('()=>arenaDebug.state().targets[0].hp<100',timeout=15000)
 assert state()['ammo']<30
 page.locator('#arenaRoarButton').click();page.wait_for_function('()=>arenaDebug.state().ammo===30',timeout=15000)
 page.evaluate('arenaDebug.place(-5,1)');page.keyboard.down('KeyW');page.wait_for_function('()=>arenaDebug.state().position[2]<-1.2',timeout=20000);page.keyboard.up('KeyW')
 assert state()['position'][2]>=-1.4,'player went through cover'
 page.evaluate('arenaDebug.place(0,5)');page.locator('#arenaTransform').click();page.wait_for_function('()=>arenaDebug.state().form==="wolf"',timeout=10000);page.wait_for_timeout(500)
 page.locator('#arenaTrial').select_option('normal');assert page.locator('#arenaRun').is_disabled()
 assert not page.evaluate('arenaDebug.action("run")')
 check_vertical_look()
 page.evaluate('arenaDebug.place(0,-3)')
 hp=state()['targets'][0]['hp'];hit_count=state()['hits'];expected=38*state()['stats']['damage']/100
 page.locator('#arenaRoll').click()
 page.wait_for_function('(n)=>arenaDebug.state().hits===n+1',arg=hit_count,timeout=15000)
 page.wait_for_function('()=>arenaDebug.state().rollTime===0',timeout=15000)
 assert abs(state()['targets'][0]['hp']-(hp-expected))<.02,'wrong roll damage or repeated damage'
 assert state()['hits']==hit_count+1 and state()['rollHitTargets']==[0]
 # A straight roll into cover must stop at its near side; no distant dummy takes damage.
 page.evaluate('arenaDebug.place(-8,-10,0)');hp_cover=state()['targets'][1]['hp']
 page.locator('#arenaRoll').click();page.wait_for_function('()=>arenaDebug.state().rollTime===0',timeout=15000)
 assert state()['position'][2]>=-11.84 and state()['targets'][1]['hp']==hp_cover,'roll crossed cover'
 page.evaluate('arenaDebug.place(0,5)')
 page.locator('#arenaTrial').select_option('legendary')
 page.locator('#moveForward').click(click_count=2,delay=70)
 page.wait_for_function('()=>arenaDebug.state().run',timeout=10000)
 rect=page.locator('#moveForward').bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down()
 page.wait_for_function('()=>arenaDebug.state().motion==="WolfRunQuad"',timeout=10000);page.mouse.up()
 assert state()['input']=={'x':0,'y':0}
 page.locator('#arenaRun').click();page.evaluate('arenaDebug.place(0,1)');page.locator('#arenaJump').click()
 page.wait_for_function('()=>arenaDebug.state().position[1]>.3',timeout=10000)
 page.wait_for_function('()=>arenaDebug.state().grounded',timeout=15000)
 assert state()['position'][2]<.5,'wolf did not jump forward'
 page.locator('#arenaRoarButton').click();page.wait_for_function('()=>arenaDebug.state().effects.particles>0',timeout=10000)
 assert 17<state()['roarTime']<=20 and max(state()['stats'].values())<=180.001
 assert not page.evaluate('arenaDebug.action("roll")'),'roar pose was interrupted'
 page.wait_for_function('()=>arenaDebug.state().roarPoseTime===0',timeout=10000)
 page.evaluate('arenaDebug.place(0,-5.8)');page.locator('#arenaFire').click()
 page.wait_for_function('()=>arenaDebug.state().attackTime>0',timeout=10000)
 assert state()['effects']['trail']
 page.wait_for_function('()=>arenaDebug.state().hits>=2',timeout=15000)
 assert state()['effects']['pool']==72 and state()['shadow']['type']=='PCFSoft'
 page.screenshot(path=str(ROOT/'dist/arena-wolf-preview.png'))
 page.evaluate('arenaDebug.expireRoar()');page.wait_for_function('()=>arenaDebug.state().effects.particles===0',timeout=10000)
 # Model switching must release inactive GPU resources; all wolves have common run/roll clips.
 for id in ['kultigin','alparslan','konuralp','bilge']:
  page.locator('#arenaCharacter').select_option(id);page.wait_for_selector('#arenaLoad[hidden]',state='attached',timeout=60000)
  assert len(state()['render']['cacheKeys'])<=2
 page.locator('#arenaTransform').click();page.wait_for_function('()=>arenaDebug.state().form==="human"',timeout=10000)
 page.screenshot(path=str(ROOT/'dist/arena-human-preview.png'))
 page.locator('#arenaExit').click();assert page.locator('#lobby.active').count()==1
 page.locator('[data-nav="inventory"]').click();page.locator('#previewWolf').click();page.wait_for_function('()=>document.getElementById("wolfModelViewport").dataset.modelReady==="true"',timeout=60000)
 page.wait_for_function('()=>wolf3DInfo().visible&&rogueEngineInfo().triangles>5000',timeout=15000)
 assert page.evaluate('rogueEngineInfo().contexts')==1
 assert page.locator('canvas').count()==1
 page.screenshot(path=str(ROOT/'dist/inventory-v019-preview.png'))
 page.locator('#previewHuman').click();page.wait_for_function('()=>wolf3DInfo().loaded==="human-bilge"&&wolf3DInfo().visible',timeout=60000)
 page.screenshot(path=str(ROOT/'dist/bilge-human-preview.png'))
 assert not errors,errors
 browser.close()
 print('PASS: FPS fire/reload, cover collision, human/wolf transition, normal/legendary gates, double-tap direction run, one-hit swept roll damage and cover blocking, consistent vertical drag in both forms, forward jump, melee and VFX, roar cap/expiry, soft character shadow, bounded cache and one WebGL context.')
