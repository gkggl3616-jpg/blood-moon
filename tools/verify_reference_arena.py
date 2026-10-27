"""Exercise the shipped clips, stride timing and shared colour-only roar in WebGL."""
from pathlib import Path
import json, os, shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'app/src/main/assets'
OUT=ROOT/'dist';OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    options={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']}
    if os.environ.get('ROGUE_BROWSER_CHANNEL'):options['channel']=os.environ['ROGUE_BROWSER_CHANNEL']
    elif shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':960,'height':540},is_mobile=True,has_touch=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    def serve(route):
        f=(ASSETS/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
        if not f.is_relative_to(ASSETS) or not f.is_file():route.fulfill(status=404,body='missing')
        else:route.fulfill(path=str(f))
    page.route('https://rogue.local/**',serve)
    page.goto('https://rogue.local/index.html');page.locator('#skipIntro').click();page.locator('#join').click()
    page.wait_for_function('()=>window.arenaDebug&&arenaDebug.state().ready',timeout=90000)
    page.locator('#arenaTransform').click()
    page.wait_for_function('()=>arenaDebug.state().form==="wolf"&&arenaDebug.state().canAct')
    page.locator('#arenaTrial').select_option('legendary')
    report=[]
    for key,color in [('bilge','#70dfff'),('kultigin','#ff354d'),('alparslan','#ffae36'),('konuralp','#af65ff')]:
        page.locator('#arenaCharacter').select_option(key)
        page.wait_for_function('(key)=>arenaDebug.state().character===key&&document.getElementById("arenaLoad").hidden',arg=key,timeout=60000)
        page.evaluate('arenaDebug.expireRoar();arenaDebug.place(0,25)')
        if not page.evaluate('arenaDebug.state().run'):assert page.evaluate('arenaDebug.action("run")')
        page.keyboard.down('KeyW')
        page.wait_for_function('()=>arenaDebug.state().motion==="WolfRunQuad"&&arenaDebug.state().motionTime>.08')
        # Integrate actual clip time across wraps and actual metres across the same rendered frames.
        run=page.evaluate('''()=>new Promise(resolve=>{
          const first=arenaDebug.state();let prev=first,clipTime=0;
          function sample(){const s=arenaDebug.state();let d=s.motionTime-prev.motionTime;
            if(d<0)d+=s.motionProfile.runDuration;clipTime+=d;prev=s;
            if(s.simulationTime-first.simulationTime>.9)resolve({distance:first.position[2]-s.position[2],seconds:s.simulationTime-first.simulationTime,clipTime,rate:s.motionRate,profile:s.motionProfile});
            else requestAnimationFrame(sample);
          }requestAnimationFrame(sample);
        })''')
        speed=run['distance']/run['seconds'];expected=page.evaluate('8*arenaDebug.state().stats.speed/100')
        assert abs(speed-expected)<.015,(key,speed,expected)
        clip_distance=run['clipTime']/run['profile']['runDuration']*run['profile']['runStride']
        assert abs(clip_distance-run['distance'])<.025,(key,'stride drift',run,clip_distance)
        average_rate=run['clipTime']/run['seconds']
        assert abs(average_rate-expected/8)<.005,(key,'old speed multiplier remains',run)
        before=page.evaluate('()=>{const s=arenaDebug.state();if(!arenaDebug.action("roar"))throw new Error("roar blocked");return s;}')
        page.wait_for_function('()=>arenaDebug.state().effects.roarPhase>.5&&arenaDebug.state().effects.roarPhase<.72')
        peak=page.evaluate('arenaDebug.state()')
        assert peak['motion']=='WolfRoar' and not peak['run']
        assert peak['effects']['roarPeaks']==before['effects']['roarPeaks']+1
        assert peak['effects']['roarColor']==color and peak['effects']['pool']==72
        rgb=peak['effects']['particleColor'];assert rgb and max(rgb)>0
        # Compare emitted RGB hue, independent of per-particle fading / sRGB conversion.
        if key=='bilge':assert rgb[2]>rgb[1]>rgb[0]
        elif key=='kultigin':assert rgb[0]>rgb[2]>rgb[1]
        elif key=='alparslan':assert rgb[0]>rgb[1]>rgb[2]
        else:assert rgb[2]>rgb[0]>rgb[1]
        assert all(peak['joints'][hand][1]>peak['joints']['Head'][1]+.06 for hand in ['HandL','HandR']),(key,peak['joints'])
        assert sum((a-b)**2 for a,b in zip(before['position'],peak['position']))<.0001,'held forward moved during roar'
        for stat,mult in [('damage',1.15),('defense',1.3),('speed',1.2)]:assert abs(peak['stats'][stat]-before['stats'][stat]*mult)<.001
        assert not page.evaluate('arenaDebug.action("roll")')
        page.screenshot(path=str(OUT/f'roar-{key}.png'))
        page.wait_for_function('()=>arenaDebug.state().roarPoseTime===0')
        page.keyboard.up('KeyW')
        assert page.evaluate('arenaDebug.state().effects.roarPeaks')==peak['effects']['roarPeaks'],'duplicate peak burst'
        report.append({'id':key,'measured_speed_mps':speed,'action_rate':average_rate,'stride_error_m':clip_distance-run['distance'],'roar_color':color,'emitted_rgb':rgb,'hands_above_head_m':min(peak['joints'][h][1]-peak['joints']['Head'][1] for h in ['HandL','HandR']),'held_direction_stopped':True,'peak_bursts_per_roar':1})
    # The same actual clip/stride data must drive the inventory preview.
    page.locator('#arenaExit').click();page.locator('[data-nav="inventory"]').click()
    page.locator('#previewWolf').click()
    page.wait_for_function('()=>wolf3DInfo().visible&&wolf3DInfo().loaded==="bilge"',timeout=60000)
    page.evaluate('RogueGear.buy("skill-legendary");RogueGear.equip("bilge","wolf","skill","skill-legendary")')
    assert page.evaluate('playWolfMotion("WolfRunQuad")')
    page.wait_for_function('()=>wolf3DInfo().actionTime>.1')
    preview=page.evaluate('wolf3DInfo()')
    assert abs(preview['actionRate']-1.05)<.001
    assert abs(preview['motionProfile']['runStride']-report[0]['measured_speed_mps']/1.05*16/30)<.002
    assert not errors,errors
    (OUT/'reference-arena-verification.json').write_text(json.dumps({'wolves':report,'preview_run_rate':preview['actionRate'],'browser_errors':errors},indent=2))
    browser.close()
print('PASS: four actual run strides, shared overhead roar, emitted character colours, one peak burst, stopped held movement, unchanged buff layers and inventory timing.')
