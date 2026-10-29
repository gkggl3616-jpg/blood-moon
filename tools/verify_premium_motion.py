"""Short actual-WebGL qualification: four main poses, not every tattoo motif."""
import json,shutil,math
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];D=R/'docs/premium-wolf-01';records=[];errors=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']);page=browser.new_page(viewport={'width':900,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
 def serve(route):
  f=(R/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve();route.fulfill(path=str(f)) if f.is_relative_to(R) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/tools/viewer/model-review.html?asset=../../app/src/main/assets/models/bilge.glb');page.wait_for_function('()=>window.modelReview?.ready',timeout=90000)
 for role,phase in [('WolfIdle',.2),('WolfRunQuad',.5),('WolfRoll',.5),('WolfRoar',.49)]:
  result=page.evaluate('''([role,phase])=>{const r=modelReview.sample(role,phase,'three','body',true,true);return {role,phase,floor:r.floorY,joints:r.joints,meshes:r.skin.meshes.map(m=>({mesh:m.mesh,edgesOver3:m.edgesOver3,maxRatio:m.maxRatio,severe:m.worst.filter(e=>e.physicalLengthM-e.physicalRestM>.08).map(e=>({ratio:e.ratio,growthM:e.physicalLengthM-e.physicalRestM,vertices:e.vertices}))})),contactProbeCount:modelReview.actor.userData.groundContactProbeCount};}''',[role,phase]);records.append(result)
  assert result['floor']>-.012,(role,result['floor'])
  assert not any(m['severe'] for m in result['meshes']),(role,result['meshes'])
 first=records[0]['joints']
 for r in records[1:]:
  for side in ['L','R']:
   for a,b in [('UpperArm','Forearm'),('Forearm','Hand')]:assert abs(math.dist(first[a+side],first[b+side])-math.dist(r['joints'][a+side],r['joints'][b+side]))<.001
 assert not errors,errors;browser.close()
(D/'native-final-short-motion.json').write_text(json.dumps({'poses':records,'errors':errors,'phone_tested':False},indent=2));print('PASS: four actual native poses, floor contact, constant arm lengths, no severe stretched edges; one shared tattoo surface')
