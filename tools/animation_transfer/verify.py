"""Fail if an animation-only update changes appearance, protected clips, cameras or FP assets."""
from pathlib import Path
import copy,gzip,hashlib,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[2];ASSETS=ROOT/'app/src/main/assets'
def unpack(b):
 n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def original(path):return subprocess.run(['git','show','HEAD:'+path],cwd=ROOT,check=True,capture_output=True).stdout
report=[]
for path in sorted((Path(__file__).parent/'data').glob('*.json.gz')):
 p=json.loads(gzip.decompress(path.read_bytes()));file=ASSETS/'models'/p['target'];before=original('app/src/main/assets/models/'+p['target']);after=file.read_bytes();assert hashlib.sha256(before).hexdigest()==p['base_sha256'];a,ab=unpack(before);b,bb=unpack(after);assert bb.startswith(ab),'Original geometry/texture/skin bytes altered'
 for k in ['meshes','skins','materials','textures','images','samplers','scenes','scene']:
  assert a.get(k)==b.get(k),(file.name,k)
 assert a['accessors']==b['accessors'][:len(a['accessors'])];assert a['bufferViews']==b['bufferViews'][:len(a['bufferViews'])]
 for x,y in zip(a['nodes'],b['nodes']):
  x=copy.deepcopy(x);y=copy.deepcopy(y)
  for k in ['walk_foot_speed_mps','jog_foot_speed_mps','run_measured_foot_speed_mps','run_foot_speed_mps','run_stride_m','run_reference_speed_mps']:
   x.get('extras',{}).pop(k,None);y.get('extras',{}).pop(k,None)
  assert x==y,(file.name,'Skeleton / node transform changed')
 changed={c['name'] for c in p['clips']};old={c['name']:c for c in a['animations']};new={c['name']:c for c in b['animations']}
 assert set(old)==set(new)
 if p['target'].startswith('human-'):assert changed<= {'HumanIdle','HumanWalk','HumanRun'}
 for name in set(old)-changed:assert old[name]==new[name],(file.name,'Protected animation modified',name)
 for name in changed:
  for ch in new[name]['channels']:
   t=ch['target'];sampler=new[name]['samplers'][ch['sampler']]
   if sampler['input']<len(a['accessors']) and sampler['output']<len(a['accessors']):
    assert any(x['target']==t and old[name]['samplers'][x['sampler']]==sampler for x in old[name]['channels']);continue
   assert t['path']=='rotation' or (t['path']=='translation' and b['nodes'][t['node']]['name']=='Hips')
 report.append({'model':file.name,'mesh_material_skin_rest_unchanged':True,'clips_replaced':sorted(changed),'protected_clips_unchanged':True})
protected=json.loads((Path(__file__).parent/'protected-assets.json').read_text())
for rel,sha in protected.items():assert hashlib.sha256((ASSETS/rel).read_bytes()).hexdigest()==sha,('Protected runtime asset changed',rel)
bundle=(ASSETS/'wolf3d.js').read_text()
def marked(begin,end):
 start=bundle.index(begin);finish=bundle.index(end,start)+len(end);return bundle[start:finish].encode()
assert hashlib.sha256(marked('/*FPHANDS-BEGIN*/','/*FPHANDS-END*/')).hexdigest()=='1c441cc1b0b4b706e5534c4d95468c610508af9f134c70cce7c8ffa29165bab9'
assert hashlib.sha256(marked('/*VIEWMODEL-BEGIN*/','/*VIEWMODEL-END*/')).hexdigest()=='bb80701ab625359d5dc7070842ec701d0f31f912074b8f667b704df0cbbce7ae'
(ROOT/'dist').mkdir(exist_ok=True);(ROOT/'dist/animation-only-verification.json').write_text(json.dumps({'models':report,'protected_runtime_assets':len(protected),'first_person_assets_identical':True,'first_person_marker_blocks_identical':True},indent=2));print('PASS: appearance, first-person/camera marker blocks and protected animation clips unchanged')
