from pathlib import Path
import json,struct,hashlib,zipfile
R=Path(__file__).resolve().parents[1];D=R/'dist/bilge-kagan-assets';D.mkdir(parents=True,exist_ok=True);files={};modeldata={}
def add(src,dest):
 p=R/src;assert p.is_file(),str(p);files[dest]=p.read_bytes()
for key,form in [('bilge','Kurt'),('human-bilge','Insan')]:
 p=R/'app/src/main/assets/models'/f'{key}.glb';raw=p.read_bytes();files[f'Oyun/Modeller/{key}.glb']=raw;n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);b=raw[28+n:];meta=g['scenes'][0]['extras'];modeldata[key]={'bones':len(g['skins'][0]['joints']),'clips':[{'name':a['name'],'duration_ms':a.get('extras',{}).get('nativeKeyTimesMs',[-1])[-1]} for a in g['animations']],'metadata':meta}
 for i,image in enumerate(g.get('images',[])):
  assert 'uri' not in image
  v=g['bufferViews'][image['bufferView']];o=v.get('byteOffset',0);ext={'image/png':'png','image/jpeg':'jpg','image/webp':'webp'}[image['mimeType']];files[f'Oyun/Dokular/{form}/{i:02d}.{ext}']=b[o:o+v['byteLength']]
source_path=R/'deliveries/Bilge-Kagan-Sources-v0.1.18.zip'
source_record=json.loads((R/'docs/bilge-assets/source-package.json').read_text())
assert hashlib.sha256(source_path.read_bytes()).hexdigest()==source_record['sha256']
with zipfile.ZipFile(source_path) as source_zip:
 assert source_zip.testzip() is None
 for name in source_zip.namelist():
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  files[name]=source_zip.read(name)
A=R/'app/src/main/assets'
for p in sorted((A/'fx/native').rglob('*')):
 if p.is_file():files['Oyun/'+p.relative_to(A).as_posix()]=p.read_bytes()
for src,dest in [('app/src/main/assets/media/roar-voice.wav','Oyun/Ses/roar-voice.wav'),('art/3d/textures/tattoo-atlas.png','Oyun/Dovme/tattoo-atlas.png'),('art/characters/model-families/tattoo-policy.json','Oyun/Dovme/tattoo-policy.json'),('app/src/main/assets/models/native-contracts.json','Oyun/native-contracts.json'),('docs/KARAKTER-DOSYA-ESLESTIRMELERI-TR.md','Belgeler/KARAKTER-DOSYA-ESLESTIRMELERI-TR.md'),('docs/karahan-v0118/GUNCEL-RAPOR-TR.md','Belgeler/GUNCEL-RAPOR-TR.md')]:add(src,dest)
for name in ['native-motion.js','native-roar-layer.js','model-roar-fx.js','motion.js','rig-bones.js','engine.js']:
 add('tools/viewer/'+name,'Entegrasyon-Referansi/'+name)
files['ANIMASYON-LISTESI.json']=json.dumps(modeldata,ensure_ascii=False,indent=2).encode()
readme=(R/'docs/bilge-assets/OKU-BENI-TR.md').read_text()
files['OKU-BENI-TR.md']=readme.encode();(D/'OKU-BENI-TR.md').write_text(readme)
manifest={k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in files.items()};files['DOSYA-MANIFESTOSU.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
p=D/'Bilge-Kagan-Assets-v0.1.18.zip'
with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,data in files.items():
  entry=zipfile.ZipInfo(name,date_time=(2026,10,30,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o644<<16;z.writestr(entry,data,compresslevel=6)
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for name,record in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==record['sha256']
report={'zip':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':len(files),'runtime_models':{k:manifest['Oyun/Modeller/'+k+'.glb'] for k in ['bilge','human-bilge']}}
(D/'package-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
