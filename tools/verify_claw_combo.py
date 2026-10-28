"""Play the actual arena: alternate accepted attacks, blocked inputs, held input."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,shutil
R=Path(__file__).resolve().parents[1];A=R/'app/src/main/assets';report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']);page=b.new_page(viewport={'width':1280,'height':720},is_mobile=True,has_touch=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  f=(A/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
  if f.is_relative_to(A) and f.is_file():route.fulfill(path=str(f))
  else:route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/index.html');page.locator('#skipIntro').click();page.locator('#join').click();page.wait_for_function('()=>window.arenaDebug?.state().ready',timeout=90000)
 start=page.evaluate('arenaDebug.state()');page.keyboard.down('KeyW');page.wait_for_function('(z)=>arenaDebug.state().position[2]<z-.65',arg=start['position'][2],timeout=10000);sway=page.evaluate('arenaDebug.state()');assert sway['walkSway']>.1 and sway['walkPhase']>0;page.keyboard.up('KeyW');page.wait_for_function('()=>arenaDebug.state().walkSway<.01',timeout=10000);stopped=page.evaluate('arenaDebug.state().walkPhase');page.wait_for_timeout(150);assert abs(page.evaluate('arenaDebug.state().walkPhase')-stopped)<.001
 page.evaluate('arenaDebug.action("transform")');page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct',timeout=10000);page.wait_for_timeout(400);page.evaluate('arenaDebug.place(0,-5.7)')
 baseline=page.evaluate('arenaDebug.state()');assert page.evaluate('arenaDebug.action("fire")');right=page.evaluate('arenaDebug.state()');assert right['attackSide']=='right' and right['motion']=='WolfClawRight' and right['clawSequence']==1
 assert not page.evaluate('arenaDebug.action("fire")');assert page.evaluate('arenaDebug.state().clawSequence')==1
 page.wait_for_function('(n)=>arenaDebug.state().hits===n+1',arg=baseline['hits'],timeout=10000);hp=page.evaluate('arenaDebug.state().targets[0].hp');page.wait_for_function('()=>arenaDebug.state().attackCooldown===0',timeout=10000);assert page.evaluate('arenaDebug.state().hits')==baseline['hits']+1
 assert page.evaluate('arenaDebug.action("fire")');left=page.evaluate('arenaDebug.state()');assert left['attackSide']=='left' and left['motion']=='WolfClawLeft' and left['clawSequence']==2;assert left['effects']['trailSide']=='left'
 page.wait_for_function('()=>arenaDebug.state().attackCooldown===0',timeout=10000);page.evaluate('arenaDebug.place(0,8)')
 page.evaluate('''window.clawLog=[];window.clawLast=2;window.clawWatch=setInterval(()=>{const s=arenaDebug.state();if(s.clawSequence!==clawLast){clawLog.push(s.attackSide);clawLast=s.clawSequence;}},10)''')
 rect=page.locator('#arenaFire').bounding_box();page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down();page.wait_for_function('()=>arenaDebug.state().clawSequence>=5',timeout=15000);page.mouse.up();page.wait_for_timeout(50);log=page.evaluate('clawLog');page.evaluate('clearInterval(clawWatch)');assert log[:3]==['right','left','right'],log
 report={'right_clip':right['motion'],'left_clip':left['motion'],'rejected_input_does_not_advance':True,'single_hit_first_attack':True,'first_target_hp':hp,'held_input_sides':log,'left_trail_matches_hand':True,'errors':errors,'distance_driven_human_sway':True,'sway_settles_on_stop':True,'new_character_animation_quality':'NOT evaluated; legacy arm-mask compatibility only'};assert not errors,errors;b.close()
(R/'docs/grey-wolf-production/claw-combo-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
