"""Pose-space art correction for the legacy Behamah roar neck.
Keep every original source clip/bone channel; add one explicitly derived clip
and one corrective morph. Jaw, upper/lower teeth and horns move together.
"""
import sys,json,struct,copy,math
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from export_bilge_native_basis import Reader
P=R/'art/characters/karahan/wolf.glb';raw=P.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);meta=g['scenes'][0]['extras'];model=Reader().from_file(str(R/'art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb'));motion=Reader().from_file(str(R/'art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb'));source=next(a for a in motion.animations if a.name=='T_cry');frame=min(range(len(source.keyframes)),key=lambda i:abs(source.keyframes[i].time-866));indices={n.name:i for i,n in enumerate(model.nodes)};lengths={n.name:(n.parent.bind_matrix.inverted()@n.bind_matrix).translation.length for n in model.nodes if n.parent and n.name not in ['Bip01 Pelvis']};meta['nativeJointRestLengths']=lengths;pose=[]
for i,node in enumerate(model.nodes):
 t=source.node_keyframe_transforms[i][frame];location=t.location.copy();length=lengths.get(node.name)
 if length and location.length>1e-6:location*=length/location.length
 local=Matrix.LocRotScale(location,t.rotation.normalized(),Vector((1,1,1)));pose.append(pose[indices[node.parent.name]]@local if node.parent else local)
skin=[p@node.bind_matrix.inverted() for p,node in zip(pose,model.nodes)]
def read(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];code={5126:'f',5123:'H',5125:'I'}[a['componentType']];size=struct.calcsize('<'+code*width);return [struct.unpack_from('<'+code*width,binary,v.get('byteOffset',0)+a.get('byteOffset',0)+j*v.get('byteStride',size)) for j in range(a['count'])]
def acc(values,kind,width):
 while len(binary)%4:binary.append(0)
 offset=len(binary);flat=[x for v in values for x in (v if isinstance(v,(list,tuple,Vector)) else [v])];data=struct.pack('<'+'f'*len(flat),*flat);binary.extend(data);view=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data)});g['accessors'].append({'bufferView':view,'componentType':5126,'count':len(values),'type':kind})
 if kind=='SCALAR':g['accessors'][-1].update(min=[min(values)],max=[max(values)])
 return len(g['accessors'])-1
original=[copy.deepcopy(a) for a in g['animations'] if a['name']!='DerivedBehamahRoar'];g['animations']=copy.deepcopy(original);derived=copy.deepcopy(next(a for a in original if a['name']=='T_cry'));derived['name']='DerivedBehamahRoar';derived['extras']['derived_from']='T_cry; rotations/times retained, body-rest length adaptation and pose-space mesh correction';
for channel in derived['channels']:
 if channel['target']['path']!='translation':continue
 node_name=g['nodes'][channel['target']['node']]['name'];length=lengths.get(node_name)
 if not length:continue
 sampler=derived['samplers'][channel['sampler']];values=[]
 for position in read(sampler['output']):
  p=Vector(position)
  if p.length>1e-6:p*=length/p.length
  values.append(list(p))
 sampler['output']=acc(values,'VEC3',3)
zero=Matrix([[0.0]*4 for _ in range(4)]);modified=0
for node_id,node in enumerate(g['nodes']):
 if 'mesh' not in node:continue
 mesh=g['meshes'][node['mesh']];active=False
 for primitive in mesh['primitives']:
  a=primitive['attributes'];positions=read(a['POSITION']);joints=read(a['JOINTS_0']);weights=read(a['WEIGHTS_0']);deltas=[]
  for p,js,ws in zip(positions,joints,weights):
   influence=sum(w*(1 if model.nodes[j].name in ['Bip01 Head','Bip01 Ponytail2'] else .6 if model.nodes[j].name=='Bip01 Neck' else 0) for j,w in zip(js,ws));blend=sum((skin[j]*w for j,w in zip(js,ws) if w>0),zero.copy());delta=blend.to_3x3().inverted_safe()@Vector((0,-14*influence,0)) if influence>.001 else Vector();deltas.append(list(delta));active|=influence>.001
  primitive['targets']=[{'POSITION':acc(deltas,'VEC3',3)}]
 mesh['weights']=[0];mesh.setdefault('extras',{})['targetNames']=['NativeRoarNeckCorrective']
 times=[k.time/1000 for k in source.keyframes];duration=times[-1];peak=866/1000/duration
 values=[]
 for time in times:
  phase=time/duration
  # Smooth preparation, full correction at the original FX peak and long hold,
  # then complete recovery. No pose is cut or source key time replaced.
  u=max(0,min(1,(phase-.1)/max(.001,peak-.1)));rise=u*u*(3-2*u);v=max(0,min(1,(1-phase)/.2));fall=v*v*(3-2*v);values.append(rise*fall)
 sampler=len(derived['samplers']);derived['samplers'].append({'input':acc(times,'SCALAR',1),'output':acc(values,'SCALAR',1),'interpolation':'LINEAR'});derived['channels'].append({'sampler':sampler,'target':{'node':node_id,'path':'weights'}});modified+=1
# Tattoos use the same head/neck contributions through their own morph target.
# The back patch is below the corrective zone; direct source skin remains intact.
g['animations'].append(derived);meta['nativeRoleRecipes']['WolfRoar']=['DerivedBehamahRoar'];meta['nativeClipEvents']['DerivedBehamahRoar']=meta['nativeClipEvents']['T_cry'];meta['derivedSourceClips']=['DerivedBehamahRoar'];meta['roarPoseCorrective']={'method':'pose-space mesh morph; all raw bone keys retained','source':'T_cry','derived':'DerivedBehamahRoar','max_head_translation_m':14*meta['nativeUnitScaleMeters'],'source_key_count':len(times),'full_duration_seconds':duration};assert g['animations'][:-1]==original
g['buffers'][0]['byteLength']=len(binary);text=json.dumps(g,separators=(',',':')).encode();text+=b' '*(-len(text)%4);binary+=b'\0'*(-len(binary)%4);P.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(binary),0x004e4942)+binary);print('ROAR_CORRECTIVE',modified,meta['roarPoseCorrective'])
