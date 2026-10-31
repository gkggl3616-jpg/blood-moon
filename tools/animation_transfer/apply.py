"""Apply animation channels only; original geometry/skin buffers remain an exact prefix."""
from pathlib import Path
import gzip,hashlib,json,struct,copy
ROOT=Path(__file__).resolve().parents[2];MODELS=ROOT/'app/src/main/assets/models'
def unpack(data):
 n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
def apply(payload_path):
 p=json.loads(gzip.decompress(payload_path.read_bytes()));file=MODELS/p['target'];original=file.read_bytes();g,binary=unpack(original)
 if g.get('extras',{}).get('animation_transfer',{}).get('base_sha256')==p['base_sha256']:
  assert g['extras']['animation_transfer'].get('payload_sha256')==hashlib.sha256(payload_path.read_bytes()).hexdigest(),'Payload changed: restore original GLB before applying again'
  return
 assert hashlib.sha256(original).hexdigest()==p['base_sha256'],('Unsupported source model version',file.name)
 protected={k:copy.deepcopy(g.get(k)) for k in ['meshes','skins','materials','textures','images','samplers','nodes','scenes','scene']};base=bytes(binary);buf=bytearray(binary)
 def acc(values,typ):
  flat=[float(x) for row in values for x in row] if typ!='SCALAR' else [float(x) for x in values];packed=struct.pack('<'+'f'*len(flat),*flat);buf.extend(b'\0'*((-len(buf))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(buf),'byteLength':len(packed)});buf.extend(packed);a={'bufferView':vi,'componentType':5126,'count':len(values),'type':typ}
  if typ=='SCALAR':a.update(min=[min(flat)],max=[max(flat)])
  ai=len(g['accessors']);g['accessors'].append(a);return ai
 replacements={}
 for clip in p['clips']:
  a=copy.deepcopy(next(a for a in g['animations'] if a['name']==clip['name'])) if clip.get('mode')=='override_channels' else {'name':clip['name'],'samplers':[],'channels':[]}
  a.setdefault('extras',{}).update({'source':clip['source'],'animation_only_transfer':True})
  for ch in clip['channels']:
   assert ch['path']=='rotation' or (ch['path']=='translation' and g['nodes'][ch['node']]['name']=='Hips')
   a['channels']=[x for x in a['channels'] if x['target']!={'node':ch['node'],'path':ch['path']}]
   ti=acc(ch['times'],'SCALAR');oi=acc(ch['values'],'VEC4' if ch['path']=='rotation' else 'VEC3');si=len(a['samplers']);a['samplers'].append({'input':ti,'output':oi,'interpolation':'LINEAR'});a['channels'].append({'sampler':si,'target':{'node':ch['node'],'path':ch['path']}})
  replacements[a['name']]=a
 names={a['name'] for a in g['animations']};assert replacements.keys()<=names
 g['animations']=[replacements.get(a['name'],a) for a in g['animations']]
 assert bytes(buf[:len(base)])==base
 for k,v in protected.items():assert g.get(k)==v,('Geometry, skeleton or materials changed',k)
 # Measurement metadata influences only third-person / wolf locomotion clip playback.
 if p.get('metrics'):
  body=next(n for n in g['nodes'] if n.get('name','').startswith('Body') and 'skin' in n);body.setdefault('extras',{}).update(p['metrics'])
 g.setdefault('extras',{})['animation_transfer']={'base_sha256':p['base_sha256'],'clip_names':list(replacements),'version':1,'payload_sha256':hashlib.sha256(payload_path.read_bytes()).hexdigest()};g['buffers'][0]['byteLength']=len(buf);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);buf.extend(b'\0'*((-len(buf))%4));data=struct.pack('<III',0x46546c67,2,28+len(j)+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf;file.write_bytes(data);print('Animation-only update:',file.name,', '.join(replacements))
if __name__=='__main__':
 for path in sorted((Path(__file__).parent/'data').glob('*.json.gz')):apply(path)
