"""Attach native animation keys to a static GLB with fixed basis conversion only.
No key resampling, added keys, duration edits, pose authoring or source-file writes.
"""
import sys,types,importlib,json,struct,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
OUT=R/'art/characters/bilge-original/working'
def local(node):
 if 'matrix' in node:return Matrix([node['matrix'][i:i+4] for i in range(0,16,4)]).transposed()
 q=node.get('rotation',[0,0,0,1]);return Matrix.LocRotScale(Vector(node.get('translation',[0,0,0])),Quaternion((q[3],q[0],q[1],q[2])),Vector(node.get('scale',[1,1,1])))
def attach(form):
 bodypath=R/('art/3d/source/wolfteam-archive/selected/wt_wolf_ice_r.ltb' if form=='wolf' else 'art/3d/source/pedro-native/main/pedro.ltb');motionpath=R/('art/3d/source/wolfteam-archive/selected/wt_wolf_ice_ch.ltb' if form=='wolf' else 'art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb');before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [bodypath,motionpath]};body=Reader().from_file(str(bodypath));motion=Reader().from_file(str(motionpath));assert [n.name for n in body.nodes]==[n.name for n in motion.nodes]
 raw=(OUT/(form+'-static.glb')).read_bytes();size=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+size]);start=20+size;bs=struct.unpack_from('<I',raw,start)[0];binary=bytearray(raw[start+8:start+8+bs]);names={n.get('name'):i for i,n in enumerate(g['nodes'])};joint_set=set(g['skins'][0]['joints']);assert len(joint_set)==len(body.nodes);assert all(names[n.name] in joint_set for n in body.nodes)
 coordinate_basis=Matrix.Rotation(-math.pi/2,4,'X');globals_=[];basis=[]
 for i,n in enumerate(body.nodes):
  parent=body.nodes.index(n.parent) if n.parent else None;M=local(g['nodes'][names[n.name]]);G=globals_[parent]@M if parent is not None else M;globals_.append(G);basis.append(n.bind_matrix.inverted()@coordinate_basis.inverted()@G)
 g['animations']=[];g.setdefault('accessors',[]);g.setdefault('bufferViews',[])
 def accessor(values,components,type_,bounds=False):
  while len(binary)%4:binary.append(0)
  offset=len(binary);flat=[float(x) for v in values for x in (v if isinstance(v,(list,tuple,Vector,Quaternion)) else [v])];encoded=struct.pack('<'+'f'*len(flat),*flat);binary.extend(encoded);vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(encoded)});out={'bufferView':vi,'componentType':5126,'count':len(values),'type':type_}
  if bounds:out.update(min=[min(flat)],max=[max(flat)])
  index=len(g['accessors']);g['accessors'].append(out);return index
 human_names={'UI_Default_Idle','LSt','LWF','LRF','URi1WF','URi1RF','URi1Fi','URi1Re','LJJ','LJT','LJL'};clips=motion.animations if form=='wolf' else [a for a in motion.animations if a.name in human_names];report=[];max_error=0;max_scale_error=0
 for a in clips:
  times=[k.time/1000 for k in a.keyframes];inp=accessor(times,1,'SCALAR',True);animation={'name':a.name,'samplers':[],'channels':[],'extras':{'nativeKeyTimesMs':[k.time for k in a.keyframes],'nativeEvents':[{'timeMs':k.time,'event':k.string} for k in a.keyframes if k.string],'nativeInterpolationTimeMs':a.interpolation_time,'sourceKeyCount':len(times)}}
  for i,n in enumerate(body.nodes):
   parent=body.nodes.index(n.parent) if n.parent else None;parent_basis=basis[parent] if parent is not None else coordinate_basis.inverted();positions=[];rotations=[];previous=None
   for frame,t in enumerate(a.node_keyframe_transforms[i]):
    source=Matrix.LocRotScale(t.location,t.rotation.normalized(),Vector((1,1,1)));converted=parent_basis.inverted()@source@basis[i];p,q,s=converted.decompose();max_scale_error=max(max_scale_error,max(abs(x-1) for x in s))
    if previous is not None and q.dot(previous)<0:q.negate()
    previous=q.copy();p=Vector(struct.unpack('<3f',struct.pack('<3f',*p)));q=Quaternion(struct.unpack('<4f',struct.pack('<4f',*q)))
    reconstructed=parent_basis@Matrix.LocRotScale(p,q,Vector((1,1,1)))@basis[i].inverted();error=max(abs(reconstructed[x][y]-source[x][y]) for x in range(4) for y in range(4));
    if error>max_error+.05:print('CONVERSION_ERROR',a.name,n.name,frame,error,tuple(s),tuple(basis[i].to_scale()),tuple(parent_basis.to_scale()))
    max_error=max(max_error,error);positions.append(list(p));rotations.append([q.x,q.y,q.z,q.w])
   for path,values,components,type_ in [('translation',positions,3,'VEC3'),('rotation',rotations,4,'VEC4')]:
    out=accessor(values,components,type_);si=len(animation['samplers']);animation['samplers'].append({'input':inp,'output':out,'interpolation':'LINEAR'});animation['channels'].append({'sampler':si,'target':{'node':names[n.name],'path':path}})
  g['animations'].append(animation);report.append({'name':a.name,'key_count':len(times),'duration_ms':a.keyframes[-1].time-a.keyframes[0].time})
 assert max_error<.005,(form,max_error);assert max_scale_error<.001,(form,max_scale_error)
 upper=next((w.node_weights for w in motion.weight_sets if w.name=='Upper'),None)
 if upper is None:
  upper=[]
  for n in body.nodes:
   ancestors=[];parent=n
   while parent:ancestors.append(parent.name);parent=parent.parent
   upper.append(1 if 'Bip01 Spine1' in ancestors else 0)
 extras=g['scenes'][g.get('scene',0)].setdefault('extras',{});extras.update(modelType='ice40' if form=='wolf' else 'human47',nativeSkeletonNames=[n.name for n in body.nodes],nativeUpperBoneNames=[n.name for n,w in zip(body.nodes,upper) if w>0],nativeClipEvents={a['name']:a['extras']['nativeEvents'] for a in g['animations']},nativeSourceKeyPreserved=True,wardrobeOrigin='original_authored',sourceAnimationSha256=before[str(motionpath)],nativeUpperMaskSource='weight_set' if motion.weight_sets else 'hierarchy_fallback',motionVersion='native-unchanged-v1')
 g['buffers'][0]['byteLength']=len(binary);text=json.dumps(g,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);payload=struct.pack('<4sII',b'glTF',2,12+8+len(text)+8+len(binary))+struct.pack('<II',len(text),0x4E4F534A)+text+struct.pack('<II',len(binary),0x004E4942)+binary;(OUT/(form+'.glb')).write_bytes(payload)
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items());return {'form':form,'bones':len(body.nodes),'clips':report,'max_pose_matrix_conversion_error_native_units':max_error,'max_coordinate_scale_roundoff':max_scale_error,'source_files_unchanged':True,'resampled_keys':0,'quaternion_normalization':'Unit normalization required by glTF; original source quaternion floats and files remain unchanged','output_bytes':len(payload)}
forms=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['wolf','human'];reports=[attach(f) for f in forms];(R/'docs/bilge-original-complete/native-conversion.json').write_text(json.dumps(reports,indent=2));print('NATIVE_CONVERSION',[(x['form'],x['bones'],len(x['clips']),x['max_pose_matrix_conversion_error_native_units']) for x in reports])
