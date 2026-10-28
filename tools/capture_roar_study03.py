"""Capture the exported GLB + shared game VFX in actual Three.js, at exact times."""
from pathlib import Path
import os,shutil,json,sys
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];D=R/'dist/roar-study-03';errors=[];audit=[]
with sync_playwright() as p:
 opts={'headless':True,'args':['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required']}
 if shutil.which('chromium'):opts['executable_path']=shutil.which('chromium')
 browser=p.chromium.launch(**opts);page=browser.new_page(viewport={'width':960,'height':960},device_scale_factor=1);page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:errors.append(m.text) if m.type=='error' and ('Shader' in m.text or 'WebGL' in m.text) else None)
 def serve(route):
  f=(R/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve()
  if not f.is_relative_to(R) or not f.is_file():route.fulfill(status=404,body='missing')
  else:route.fulfill(path=str(f))
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/tools/viewer/study03.html');page.wait_for_function('()=>window.study03?.ready',timeout=90000)
 page.add_style_tag(content='nav{display:none!important}')
 views=['reference','front','side']
 for view in views:
  folder=D/('game-'+view);folder.mkdir(exist_ok=True)
  frames=[0,8,20,27,38,51] if '--stills' in sys.argv else range(52)
  for f in frames:
   result=page.evaluate('([t,v,fx])=>study03.sample(t,v,fx)',[f/30,view,True]);audit.append(result);page.screenshot(path=str(folder/f'{f:03}.png'))
  print('CAPTURED',view,flush=True)
 for view in ['front','side']:
  page.evaluate('([t,v])=>study03.sample(t,v,false)',[8/30,view]);page.screenshot(path=str(D/f'game-no-fx-{view}.png'))
 assert not errors,errors
 assert audit[1]['duration']==1.7000000476837158 or abs(audit[1]['duration']-1.7)<.001
 assert any(r['effects']['flames']==2 and r['effects']['flameSprites']==6 for r in audit)
 assert all(r['effects']['pool']==72 and r['effects']['particles']<=72 for r in audit)
 (D/'browser-audit.json').write_text(json.dumps({'errors':errors,'samples':audit,'physical_device_tested':False,'runtime_assets_replaced':False},indent=2));browser.close()
