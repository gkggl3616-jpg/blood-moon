"""Validate native Bilge assets and their actual WebGL playback, not a concept image."""
import json,struct,hashlib,os,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];A=R/'app/src/main/assets';OUT=R/'docs/bilge-original-complete';checks=[]
for form,key,bones,clips,budget in [('wolf','bilge',40,68,15000),('human','human-bilge',47,11,12000)]:
 raw=(A/'models'/f'{key}.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);meta=g['scenes'][g.get('scene',0)]['extras'];assert meta['nativeSourceKeyPreserved'] and meta['wardrobeOrigin']=='original_authored';assert len(g['skins'][0]['joints'])==bones;assert len(g['animations'])==clips
 triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert triangles<=budget
 for a in g['animations']:
  times=a['extras']['nativeKeyTimesMs'];assert len(times)==a['extras']['sourceKeyCount']
  for sampler in a['samplers']:
   accessor=g['accessors'][sampler['input']];assert accessor['count']==len(times);assert abs(accessor['max'][0]-times[-1]/1000)<1e-6
 assert all('uri' not in b for b in g['buffers']) and all('uri' not in i for i in g.get('images',[]))
 checks.append({'form':form,'bones':bones,'clips':clips,'triangles':triangles,'embedded_textures':True,'sha256':hashlib.sha256(raw).hexdigest()})
with sync_playwright() as p:
 options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']}
 if os.getenv('ROGUE_BROWSER_CHANNEL'):options['channel']=os.environ['ROGUE_BROWSER_CHANNEL']
 elif shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
 browser=p.chromium.launch(**options);page=browser.new_page(viewport={'width':800,'height':450});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  f=(A/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
  route.fulfill(path=str(f)) if f.is_relative_to(A) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/index.html');page.locator('#skipIntro').click();page.locator('#join').click();page.wait_for_function('()=>window.arenaDebug?.state().ready',timeout=90000)
 assert page.evaluate('arenaDebug.state().modelType')=='ice40';page.locator('#arenaTransform').click();page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct');page.screenshot(path=str(OUT/'runtime-idle.png'))
 page.locator('#arenaTrial').select_option('legendary');page.evaluate('arenaDebug.place(0,25);arenaDebug.action("run")');page.keyboard.down('KeyW');page.wait_for_function('()=>arenaDebug.state().motion==="WolfRunQuad"')
 start=page.evaluate('arenaDebug.state()');page.wait_for_function('(t)=>arenaDebug.state().simulationTime>t+.5',arg=start['simulationTime']);end=page.evaluate('arenaDebug.state()');speed=(start['position'][2]-end['position'][2])/(end['simulationTime']-start['simulationTime']);assert abs(speed-8*end['stats']['speed']/100)<.02
 page.evaluate('arenaDebug.action("roar")');page.wait_for_function('()=>arenaDebug.state().effects.flameSprites>0');roar=page.evaluate('arenaDebug.state()');assert abs(roar['motionProfile']['roarDuration']-1.933)<1e-5;assert roar['effects']['nativeEventTime']==.933
 page.wait_for_function('()=>arenaDebug.state().effects.roarPhase>.48&&arenaDebug.state().effects.roarPhase<.8');page.screenshot(path=str(OUT/'runtime-roar.png'));stopped=page.evaluate('arenaDebug.state()');assert sum((a-b)**2 for a,b in zip(roar['position'],stopped['position']))<1e-6
 page.keyboard.up('KeyW');page.wait_for_function('()=>arenaDebug.state().canAct');page.evaluate('arenaDebug.place(0,10);arenaDebug.action("roll")');page.wait_for_function('()=>arenaDebug.state().rollTime===0');roll=page.evaluate('arenaDebug.state()');assert abs(roll['rollDuration']-1)<1e-6 and 1.85<roll['rollDistance']<2.15
 assert not errors,errors
 (OUT/'native-runtime-test.json').write_text(json.dumps({'assets':checks,'measured_run_mps':speed,'roar_duration':1.933,'native_effect_event':.933,'roll_distance_m':roll['rollDistance'],'held_direction_stopped':True,'browser_errors':errors},indent=2));browser.close()
print('PASS: native Bilge contracts, runtime movement, source roar duration/event, hand flames, stopped movement and compact roll')
