"""Preserve generated geometry/UV/PBR; resize embedded maps for game memory budget.
The untouched 8K master remains in meshy_output. No generated image is repainted.
"""
from pathlib import Path
import json,struct,io,hashlib,argparse
from PIL import Image
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--source');ap.add_argument('--output');ap.add_argument('--report',default='docs/premium-wolf-01/mobile-textures.json');args=ap.parse_args();source=R/'meshy_output/20261029_143217_premium-wolf-01_01a1878d/mobile.glb';target=R/'art/characters/premium-wolf-01/mobile-2k.glb';source=R/args.source if args.source else source;target=R/args.output if args.output else target;target.parent.mkdir(parents=True,exist_ok=True);raw=source.read_bytes();length=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+length]);start=20+length;blob=raw[start+8:start+8+struct.unpack_from('<I',raw,start)[0]];out=bytearray();views=[];images={im['bufferView']:im for im in g['images'] if 'bufferView' in im};records=[]
for i,v in enumerate(g['bufferViews']):
 data=blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 if i in images:
  im=Image.open(io.BytesIO(data));before=im.size;im.thumbnail((2048,2048),Image.Resampling.LANCZOS);b=io.BytesIO();im.save(b,format='PNG',optimize=True);data=b.getvalue();images[i]['mimeType']='image/png';records.append({'image':images[i].get('name',i),'master_size':before,'mobile_size':im.size})
 out.extend(b'\0'*(-len(out)%4));nv=dict(v);nv.update(buffer=0,byteOffset=len(out),byteLength=len(data));views.append(nv);out.extend(data)
g['bufferViews']=views;g['buffers']=[{'byteLength':len(out)}];j=json.dumps(g,separators=(',',':')).encode();j+=b' '*(-len(j)%4);out+=b'\0'*(-len(out)%4);target.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(out))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(out),0x004e4942)+out);report={'master':str(source.relative_to(R)),'mobile':str(target.relative_to(R)),'master_bytes':len(raw),'mobile_bytes':target.stat().st_size,'images':records,'geometry_and_uv_changed':False,'rigged':False,'runtime_installed':False,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()};(R/args.report).write_text(json.dumps(report,indent=2));print(json.dumps(report))
