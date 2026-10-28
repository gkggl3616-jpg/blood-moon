"""Check opt-in native pair in actual menu/arena without touching save schema."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,shutil
R=Path(__file__).resolve().parents[1];report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader'])
 page=b.new_page(viewport={'width':1280,'height':720},is_mobile=True,has_touch=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://localhost:8123/index.html?nativePair=1');page.locator('#skipIntro').click();page.locator('#join').click();page.wait_for_function('()=>window.arenaDebug?.state().ready',timeout=90000)
 page.evaluate('arenaDebug.action("transform")');page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct',timeout=15000)
 assert page.evaluate('arenaDebug.action("roar")');page.wait_for_function('()=>arenaDebug.state().effects.particles>0',timeout=15000)
 s=page.evaluate('arenaDebug.state()');assert s['effects']['flames']==2 and s['effects']['particles']>0;assert s['motion']=='WolfRoar';assert abs(s['motionProfile']['roarDuration']-4/3)<.001
 assert not page.evaluate('arenaDebug.action("run")');assert not page.evaluate('arenaDebug.action("roll")')
 page.screenshot(path=str(R/'docs/native-pair-review/runtime-roar.png'))
 page.wait_for_function('()=>arenaDebug.state().canAct',timeout=15000);page.evaluate('arenaDebug.action("fire")');assert page.evaluate('arenaDebug.state().motion')=='WolfClawRight'
 page.wait_for_function('()=>arenaDebug.state().attackCooldown===0',timeout=10000);page.evaluate('arenaDebug.action("fire")');assert page.evaluate('arenaDebug.state().motion')=='WolfClawLeft'
 page.locator('#arenaExit').click();page.locator('[data-nav=inventory]').click();page.locator('#loadoutCharacter').select_option('bilge');page.locator('#previewHuman').click();page.wait_for_function('()=>wolf3DInfo().loaded==="human-bilge"',timeout=90000);info=page.evaluate('wolf3DInfo()');assert 'HumanWalk' in info['clips']
 page.wait_for_timeout(1000);page.screenshot(path=str(R/'docs/native-pair-review/runtime-human.png'))
 # GLB selection in engine is explicit; confirm network fetched both new files.
 paths=page.evaluate('performance.getEntriesByType("resource").map(r=>r.name)');assert any('guardian-wolf.glb' in n for n in paths);assert any('guardian-human.glb' in n for n in paths)
 report={'variant':'nativePair=1','wolf_loaded':True,'human_loaded':True,'roar_duration_s':s['motionProfile']['roarDuration'],'hand_flames':s['effects']['flames'],'live_particles':s['effects']['particles'],'alternating_claws':True,'unsupported_quad_and_roll_rejected':True,'errors':errors,'art_quality_approved':False,'physical_android_test':False};assert not errors,errors;b.close()
(R/'docs/native-pair-review/runtime-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
