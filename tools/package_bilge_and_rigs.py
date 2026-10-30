"""Build the user's character-only bundle; no game source code is shipped."""
from pathlib import Path
import json,zipfile,hashlib,struct
R=Path(__file__).resolve().parents[1];D=R/'dist/bilge-four-models';D.mkdir(parents=True,exist_ok=True);files={}
# Preserve the final runtime models byte for byte.
for key,label in [('bilge','Kurt'),('human-bilge','Insan')]:
 raw=(R/'app/src/main/assets/models'/f'{key}.glb').read_bytes();files[f'BilgeKagan/{label}.glb']=raw;n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);b=raw[28+n:]
 for i,image in enumerate(g.get('images',[])):
  view=g['bufferViews'][image['bufferView']];off=view.get('byteOffset',0);ext={'image/png':'png','image/jpeg':'jpg'}[image['mimeType']];files[f'BilgeKagan/Dokular/{label}/{i:02d}.{ext}']=b[off:off+view['byteLength']]
with zipfile.ZipFile(R/'deliveries/Bilge-Kagan-Sources-v0.1.18.zip') as z:
 assert z.testzip() is None
 for name in z.namelist():
  if name.startswith('Blender/'):dest='BilgeKagan/Calisma/'+name.split('/',1)[1]
  elif name.startswith('Kaynak/FX/'):continue
  else:dest='BilgeKagan/'+name
  files[dest]=z.read(name)
rig=R/'deliveries/Four-Rig-Families-v1.zip';record=json.loads((R/'docs/bilge-four-models/rig-package.json').read_text());assert hashlib.sha256(rig.read_bytes()).hexdigest()==record['sha256']
with zipfile.ZipFile(rig) as z:
 assert z.testzip() is None
 for name in z.namelist():files[name]=z.read(name)
for src,dest in [('art/3d/textures/tattoo-atlas.png','BilgeKagan/Dovme/Atlas.png'),('art/characters/model-families/tattoo-policy.json','BilgeKagan/Dovme/Politika.json'),('app/src/main/assets/media/roar-voice.wav','BilgeKagan/Ses/Kukreme.wav')]:files[dest]=(R/src).read_bytes()
files['README-TR.md']=(R/'docs/bilge-four-models/README-TR.md').read_bytes()
assert not any(Path(name).suffix.lower() in ['.js','.py','.java','.css','.html','.exe','.dll','.sh','.psh','.vsh','.gd'] for name in files)
for name,data in files.items():
 assert not Path(name).is_absolute() and '..' not in Path(name).parts
 if name.endswith('.glb'):
  magic,version,length,n,kind=struct.unpack_from('<4sIIII',data);assert magic==b'glTF' and version==2 and length==len(data) and kind==0x4e4f534a;g=json.loads(data[20:20+n]);assert g['skins'] and g['animations'];assert all('uri' not in b for b in g.get('buffers',[])+g.get('images',[]));binary_len=len(data)-28-n
  for view in g['bufferViews']:assert view.get('byteOffset',0)+view['byteLength']<=binary_len
manifest={name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in files.items()};files['DOSYA-MANIFESTOSU.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode();p=D/'Bilge-Kagan-ve-4-Model.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,data in files.items():
  info=zipfile.ZipInfo(name,date_time=(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data,compresslevel=6)
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for name,item in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==item['sha256']
report={'zip':p.name,'bytes':p.stat().st_size,'files':len(files),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'glb_files':[n for n in files if n.endswith('.glb')],'game_code_included':False};(D/'bundle-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
