from pathlib import Path
import json,struct,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; P=R/'art/characters/karahan/wolf.glb'; measurements={}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader']); page=b.new_page()
 def serve(route):
  f=(R/route.request.url.split('https://rogue.local/')[1].split('?')[0]).resolve();route.fulfill(path=str(f)) if f.is_relative_to(R) and f.is_file() else route.fulfill(status=404,body='missing')
 page.route('https://rogue.local/**',serve);page.goto('https://rogue.local/tools/viewer/model-review.html?asset=../../art/characters/karahan/wolf.glb');page.wait_for_function('()=>window.modelReview?.ready',timeout=90000)
 for role in ['WolfIdle','WolfWalk','WolfRunQuad','WolfRoar']:
  measurements[role]=page.evaluate('r=>modelReview.rawContact(r,25)',role);print(role,flush=True)
 b.close()
raw=P.read_bytes(); n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]); binary=raw[28+n:];meta=g['scenes'][0]['extras'];curves={}
for role,result in measurements.items():
 if role=='WolfRunQuad':
  baseline=.008-min(y for _,y in result['samples']);curves[role]=[[0,baseline],[result['duration'],baseline]]
 else:curves[role]=[[round(t,7),round(.008-y,7)] for t,y in result['samples']]
curves['WolfMove']=curves['WolfWalk'];meta['nativeLocomotionClearance']=curves;meta['nativeGroundingMethod']='Karahan: 25 actual Three.js morphed/skinned contact samples per grounded role; quad constant baseline retains aerial phases; source keys unchanged.'
t=json.dumps(g,separators=(',',':')).encode();t+=b' '*((-len(t))%4);P.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(t)+len(binary))+struct.pack('<II',len(t),0x4E4F534A)+t+struct.pack('<II',len(binary),0x004E4942)+binary)
(R/'docs/karahan-v0118/karahan-grounding.json').write_text(json.dumps({'measurements':measurements,'curves':curves},indent=2));print('grounding saved')
