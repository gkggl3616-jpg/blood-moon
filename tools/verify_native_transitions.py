"""Observe actual blended arena poses, not isolated animation clips."""
import json,shutil,os
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];A=R/'app/src/main/assets';D=R/'docs/premium-wolf-01';results=[];errors=[]
with sync_playwright() as p:
 options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']}
 if os.getenv('ROGUE_BROWSER_CHANNEL'):options['channel']=os.environ['ROGUE_BROWSER_CHANNEL']
 elif shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
 browser=p.chromium.launch(**options);page=browser.new_page(viewport={'width':800,'height':450});page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  f=(A/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve();route.fulfill(path=str(f)) if f.is_relative_to(A) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/index.html');page.evaluate('()=>{if(document.getElementById("opening").classList.contains("active"))document.getElementById("skipIntro").click();}');page.locator('#join').click();page.wait_for_function('()=>window.arenaDebug?.state().ready',timeout=90000);page.locator('#arenaTransform').click();page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct');page.locator('#arenaTrial').select_option('legendary');page.evaluate('arenaDebug.place(0,30)')
 def observe(label,duration=.6):
  samples=page.evaluate('''duration=>new Promise(resolve=>{const start=arenaDebug.state().simulationTime,samples=[];function sample(){const s=arenaDebug.state();samples.push({time:s.simulationTime,motion:s.motion,grounded:s.grounded,playerY:s.position[1],floor:arenaDebug.meshFloor()});if(s.simulationTime-start>=duration)resolve(samples);else requestAnimationFrame(sample);}requestAnimationFrame(sample);})''',duration)
  grounded=[s['floor']-s['playerY'] for s in samples if s['grounded']];r={'transition':label,'samples':samples,'minimum_grounded_floor_relative_m':min(grounded) if grounded else None};results.append(r);(D/'arena-transition-verification.json').write_text(json.dumps({'transitions':results,'errors':errors},indent=2));assert not grounded or min(grounded)>-.006,(label,min(grounded));print('PASS_TRANSITION',label,r['minimum_grounded_floor_relative_m'],flush=True)
 page.evaluate('arenaDebug.action("run")');page.keyboard.down('KeyW');observe('idle_to_quad')
 assert page.evaluate('arenaDebug.action("roar")');observe('quad_to_roar',1.8);page.wait_for_function('()=>arenaDebug.state().canAct');observe('roar_to_walk')
 page.evaluate('arenaDebug.place(0,25);arenaDebug.action("run")');observe('walk_to_quad');assert page.evaluate('arenaDebug.action("roll")');observe('quad_to_roll_and_recovery',1.25)
 page.evaluate('arenaDebug.place(0,25)');assert page.evaluate('arenaDebug.action("jump")');observe('quad_to_jump_and_land',1.5)
 page.keyboard.up('KeyW');observe('moving_to_idle');assert not errors,errors;browser.close()
print('PASS: actual blended native transitions retain grounded mesh contact')
