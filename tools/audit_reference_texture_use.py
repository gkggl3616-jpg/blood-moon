"""Detect the selected reference character textures in current runtime GLBs.
A scoped byte/pixel audit, not a claim about all visual similarity or all archive assets.
"""
from pathlib import Path
import json,hashlib,struct,io
from PIL import Image
R=Path(__file__).resolve().parents[1];refs={}
for x in json.loads((R/'docs/native-pair-review/texture-decode.json').read_text()):
 if x['source'].startswith('wt_chars/'):
  refs[x['rgba_sha256']]=x['source']
matches=[];checked=0
for p in (R/'app/src/main/assets').rglob('*.glb'):
 raw=p.read_bytes();length,kind=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+length]);offset=20+length;size,tag=struct.unpack_from('<II',raw,offset);binary=memoryview(raw)[offset+8:offset+8+size]
 for im in g.get('images',[]):
  if 'bufferView' not in im:continue
  v=g['bufferViews'][im['bufferView']];start=v.get('byteOffset',0);data=bytes(binary[start:start+v['byteLength']]);image=Image.open(io.BytesIO(data)).convert('RGBA');digest=hashlib.sha256(image.tobytes()).hexdigest();checked+=1
  if digest in refs:matches.append({'runtime_model':str(p.relative_to(R)),'image':im.get('name'),'reference':refs[digest]})
report={'reference_character_textures_checked':len(refs),'runtime_embedded_images_checked':checked,'matches':matches,'scope':'Only selected decoded character DTX atlases; does not prove all archive textures absent or complete visual originality','pass':not matches}
(R/'docs/four-character-rigs/reference-texture-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not matches
