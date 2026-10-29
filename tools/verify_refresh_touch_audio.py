"""Focused regression from the actual phone report: fixed/render clocks,
secondary-touch actions while running, one decoded roar and preserved identities.
No shop, map, intro-button or full UI regression suite.
"""
import json,shutil,os,math,hashlib,zipfile,wave,argparse
parser=argparse.ArgumentParser();parser.add_argument("--character",default="bilge");args=parser.parse_args()
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];A=R/'app/src/main/assets';D=R/'docs/karahan-v0118';D.mkdir(exist_ok=True);report={'physical_phone_tested':False};errors=[]
with wave.open(str(A/'media/roar-voice.wav')) as w:
 import array
 pcm=array.array('h',w.readframes(w.getnframes()));report['audio_buffer']={'duration':w.getnframes()/w.getframerate(),'peak':max(abs(v) for v in pcm)/32768};assert report['audio_buffer']['peak']<=.66
with sync_playwright() as p:
 options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required']}
 if os.getenv('ROGUE_BROWSER_CHANNEL'):options['channel']=os.environ['ROGUE_BROWSER_CHANNEL']
 else:options['executable_path']=shutil.which('chromium')
 b=p.chromium.launch(**options);page=b.new_page(viewport={'width':1280,'height':720},has_touch=True);page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  f=(A/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve();route.fulfill(path=str(f)) if f.is_relative_to(A) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/index.html');page.evaluate('rogueOpenScreen("lobby")');page.locator('#arenaCharacter').select_option(args.character,force=True);page.locator('#join').click();page.wait_for_function('()=>arenaDebug.state().ready',timeout=90000);report['character']=page.evaluate('arenaDebug.state().character');assert report['character']==args.character;page.locator('#arenaTransform').tap();page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct');page.evaluate('arenaDebug.action("run")');page.keyboard.down('KeyW')
 report['refresh_rates']=page.evaluate('''()=>[60,90,120,144].map(hz=>{arenaDebug.place(0,25);const trace=[];for(let i=0;i<hz;i++){arenaDebug.advance(1/hz);const s=arenaDebug.state();trace.push({motion:s.motion,rate:s.motionRate,speed:s.locomotionSpeed,time:s.motionTime});}return {hz,samples:trace.length,motions:[...new Set(trace.slice(3).map(s=>s.motion))],minRate:Math.min(...trace.slice(3).map(s=>s.rate)),maxRate:Math.max(...trace.slice(3).map(s=>s.rate)),speed:trace.at(-1).speed};})''')
 for r in report['refresh_rates']:assert r['motions']==['WolfRunQuad'] and r['maxRate']-r['minRate']<1e-6,r
 page.keyboard.up('KeyW');page.evaluate('arenaDebug.place(0,20)');cdp=page.context.new_cdp_session(page)
 def point(selector,id):
  r=page.locator(selector).bounding_box();return {'x':r['x']+r['width']/2,'y':r['y']+r['height']/2,'id':id}
 forward=point('[data-move="forward"]',1)
 def touch(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
 touch('touchStart',[forward]);page.wait_for_function('()=>arenaDebug.state().locomotionSpeed>=8')
 second=point('#arenaJump',2);touch('touchStart',[forward,second]);jump=page.evaluate('arenaDebug.state()');assert not jump['grounded'] and jump['velocity'][1]>0,jump;touch('touchEnd',[forward]);page.wait_for_function('()=>arenaDebug.state().grounded&&arenaDebug.state().canAct',timeout=10000)
 second=point('#arenaRoll',3);touch('touchStart',[forward,second]);roll=page.evaluate('arenaDebug.state()');assert roll['rollTime']>0,roll;touch('touchEnd',[forward]);page.wait_for_function('()=>arenaDebug.state().rollTime===0',timeout=10000);after=page.evaluate('arenaDebug.state()');assert 1.85<after['rollDistance']<2.15,after['rollDistance'];assert after['run']
 second=point('#arenaRoarButton',4);touch('touchStart',[forward,second]);roar=page.evaluate('({state:arenaDebug.state(),audio:roarAudioInfo(),delay:performance.now()-roarAudioInfo().started})');assert roar['state']['roarPoseTime']>0;assert roar['audio']['count']==1 and roar['audio']['singleVoice'] and roar['delay']<120,roar
 touch('touchEnd',[forward]);page.evaluate('()=>{for(let i=0;i<40;i++)arenaDebug.advance(1/120)}');stopped=page.evaluate('arenaDebug.state()');assert math.dist(roar['state']['position'],stopped['position'])<1e-6
 touch('touchEnd',[]);report['multi_touch']={'run_jump':True,'run_roll':True,'roll_distance':after['rollDistance'],'jump_peak_speed':after['jumpPeakSpeed'],'held_direction_roar_stops':True};report['roar_audio']={**roar['audio'],'gesture_to_scheduled_start_ms':roar['delay'],'pose_duration':roar['state']['motionProfile']['roarDuration']};assert abs(roar['audio']['duration']-roar['state']['motionProfile']['roarDuration'])<1e-5
 if args.character=='karahan':
  report['roar_fx']=page.evaluate('''()=>{let s=arenaDebug.state();for(let i=0;i<100&&s.motionProfile.roarDuration-s.roarPoseTime<1.02;i++){arenaDebug.advance(1/120);s=arenaDebug.state();}return {effects:s.effects,shakeCount:s.roarShakeCount,jitter:s.cameraJitter};}''')
  assert report['roar_fx']['effects']['nativeEffect']['group']=='cryguardian'
  assert not report['roar_fx']['effects']['nativeEffect']['unhandled']
 page.screenshot(path=str(D/('runtime-controls.png' if args.character=='bilge' else 'karahan-runtime-controls.png')));page.evaluate('stopArena()');assert not errors,errors;report['browser_errors']=errors;b.close()
previous=R/'dist/published-v0117/Rogue-Blood-Moon-v0.1.17.apk'
if previous.exists():
 with zipfile.ZipFile(previous) as z:
  report['bilge_identity_preserved']={key:hashlib.sha256((A/'models'/f'{key}.glb').read_bytes()).hexdigest() for key in ['bilge','human-bilge']}
  for key in report['bilge_identity_preserved']:assert z.read(f'assets/models/{key}.glb')==(A/'models'/f'{key}.glb').read_bytes(),key
(D/('refresh-touch-audio-test.json' if args.character=='bilge' else args.character+'-touch-audio-test.json')).write_text(json.dumps(report,indent=2));print('PASS: 60/90/120/144 Hz locomotion continuity, real CDP secondary-touch jump/roll, held-input roar stop, single scheduled voice and preserved Bilge assets')
