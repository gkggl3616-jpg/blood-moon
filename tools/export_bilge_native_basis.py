"""Export original geometry directly in source-native units; no Blender bone-axis conversion.
Source hierarchy, bind matrices and local key positions are represented directly.
"""
import bpy,sys,types,importlib,json,struct,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];OUT=R/'art/characters/bilge-original/working';D=R/'docs/bilge-original-complete';pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg;Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader

def build(form,scene_extras=None,body_source=None,motion_source=None):
 bodypath=R/('art/3d/source/wolfteam-archive/selected/wt_wolf_ice_r.ltb' if form=='wolf' else 'art/3d/source/pedro-native/main/pedro.ltb');motionpath=R/('art/3d/source/wolfteam-archive/selected/wt_wolf_ice_ch.ltb' if form=='wolf' else 'art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb');bodypath=R/body_source if body_source else bodypath;motionpath=R/motion_source if motion_source else motionpath;body=Reader().from_file(str(bodypath));motion=Reader().from_file(str(motionpath));assert [n.name for n in body.nodes]==[n.name for n in motion.nodes]
 raw=(OUT/(form+'-static.glb')).read_bytes();jl=struct.unpack_from('<I',raw,12)[0];old=json.loads(raw[20:20+jl]);bs=20+jl;binary=bytearray(raw[bs+8:bs+8+struct.unpack_from('<I',raw,bs)[0]]);g={k:old[k] for k in ['asset','bufferViews','buffers','materials','textures','images','samplers'] if k in old};g.update(nodes=[],meshes=[],skins=[],animations=[],accessors=[],scenes=[{'nodes':[0]}],scene=0)
 def acc(values,type_,components,component=5126,bounds=False):
  while len(binary)%4:binary.append(0)
  offset=len(binary);flat=[x for v in values for x in (v if isinstance(v,(list,tuple,Vector)) else [v])];fmt={5126:'f',5123:'H',5125:'I'}[component];encoded=struct.pack('<'+fmt*len(flat),*flat);binary.extend(encoded);view=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(encoded)});a={'bufferView':view,'componentType':component,'count':len(values),'type':type_}
  if bounds:a.update(min=[min(flat[i::components]) for i in range(components)],max=[max(flat[i::components]) for i in range(components)])
  index=len(g['accessors']);g['accessors'].append(a);return index
 points=[v.location for p in body.pieces for v in p.lods[0].vertices];low=min(v.y for v in points);height=(scene_extras or {}).get('modelHeightMeters',2.4 if form=='wolf' else 1.85);scale=height/(max(v.y for v in points)-low);g['nodes'].append({'name':'NativeGameBasis','translation':[0,-low*scale,0],'scale':[scale]*3,'children':[]});index={n.name:i for i,n in enumerate(body.nodes)}
 for i,n in enumerate(body.nodes):
  local=n.parent.bind_matrix.inverted()@n.bind_matrix if n.parent else n.bind_matrix;p,q,s=local.decompose();g['nodes'].append({'name':n.name,'translation':list(p),'rotation':[q.x,q.y,q.z,q.w],'children':[]});parent=index[n.parent.name]+1 if n.parent else 0;g['nodes'][parent]['children'].append(i+1)
 inverses=[[n.bind_matrix.inverted()[row][col] for col in range(4) for row in range(4)] for n in body.nodes];g['skins'].append({'joints':list(range(1,len(body.nodes)+1)),'inverseBindMatrices':acc(inverses,'MAT4',16),'skeleton':1})
 bpy.ops.wm.open_mainfile(filepath=str(OUT/(form+'-static.blend')));material_names={m.get('name'):i for i,m in enumerate(g['materials'])};tris=0
 for obj in list(bpy.context.scene.objects):
  if obj.type!='MESH':continue
  data=obj.data;data.calc_loop_triangles();primitives=[]
  for material in sorted({t.material_index for t in data.loop_triangles}):
   pos=[];normal=[];uv=[];joints=[];weights=[]
   for triangle in data.loop_triangles:
    if triangle.material_index!=material:continue
    for li in triangle.loops:
     loop=data.loops[li];v=data.vertices[loop.vertex_index];p=obj.matrix_basis@v.co;pos.append(list(p));normal.append(list((obj.matrix_basis.to_3x3().inverted().transposed()@data.corner_normals[li].vector).normalized()));tex=data.uv_layers.active.data[li].uv if data.uv_layers.active else Vector((0,0));uv.append([tex.x,1-tex.y]);w=sorted([(index[obj.vertex_groups[x.group].name],x.weight) for x in v.groups if obj.vertex_groups[x.group].name in index],key=lambda x:-x[1])[:4];total=sum(x[1] for x in w);assert total>0;w=[(i,value/total) for i,value in w];joints.append([i for i,_ in w]+[0]*(4-len(w)));weights.append([value for _,value in w]+[0]*(4-len(w)))
   attrs={'POSITION':acc(pos,'VEC3',3,bounds=True),'NORMAL':acc(normal,'VEC3',3),'TEXCOORD_0':acc(uv,'VEC2',2),'JOINTS_0':acc(joints,'VEC4',4,5123),'WEIGHTS_0':acc(weights,'VEC4',4)};matname=obj.data.materials[material].name;mat=material_names.get(matname);assert mat is not None,(obj.name,matname);primitives.append({'attributes':attrs,'indices':acc(list(range(len(pos))),'SCALAR',1,5125),'material':mat});tris+=len(pos)//3
  node={'name':obj.name,'mesh':len(g['meshes']),'skin':0,'extras':{k:obj[k] for k in obj.keys() if isinstance(obj[k],(str,int,float,bool))}}
  if 'atlas_uv_base' in obj:
   u,v,du,dv=list(obj['atlas_uv_base']);node['extras']['atlas_uv_base']=[u,1-v-dv,du,dv]
  g['nodes'].append(node);g['nodes'][0]['children'].append(len(g['nodes'])-1);g['meshes'].append({'name':obj.name,'primitives':primitives})
 human={'UI_Default_Idle','LSt','LWF','LRF','URi1WF','URi1RF','URi1Fi','URi1Re','LJJ','LJT','LJL'};clips=motion.animations if form=='wolf' else [a for a in motion.animations if a.name in human]
 for a in clips:
  inp=acc([k.time/1000 for k in a.keyframes],'SCALAR',1,bounds=True);anim={'name':a.name,'samplers':[],'channels':[],'extras':{'nativeKeyTimesMs':[k.time for k in a.keyframes],'sourceKeyCount':len(a.keyframes),'nativeEvents':[{'timeMs':k.time,'event':k.string} for k in a.keyframes if k.string]}}
  for i,n in enumerate(body.nodes):
   positions=[];rotations=[];last=None
   for t in a.node_keyframe_transforms[i]:
    q=t.rotation.normalized()
    if last is not None and q.dot(last)<0:q.negate()
    positions.append(list(t.location));rotations.append([q.x,q.y,q.z,q.w]);last=q.copy()
   for path,values,type_,width in [('translation',positions,'VEC3',3),('rotation',rotations,'VEC4',4)]:
    si=len(anim['samplers']);anim['samplers'].append({'input':inp,'output':acc(values,type_,width),'interpolation':'LINEAR'});anim['channels'].append({'sampler':si,'target':{'node':i+1,'path':path}})
  g['animations'].append(anim)
 upper=next((w.node_weights for w in motion.weight_sets if w.name=='Upper'),None)
 if upper is None:
  upper=[]
  for n in body.nodes:
   p=n;names=[]
   while p:names.append(p.name);p=p.parent
   upper.append(int('Bip01 Spine1' in names))
 sockets=[]
 for socket in body.sockets:
  s=Matrix.LocRotScale(socket.location,socket.rotation.normalized(),Vector((1,1,1)));sockets.append({'name':socket.name,'bone':body.nodes[socket.node_index].name,'matrix':[s[row][col] for col in range(4) for row in range(4)]})
 g['scenes'][0]['extras']={'modelType':'ice40' if form=='wolf' else 'human47','nativeSourceKeyPreserved':True,'nativeGeometryBasis':'native-game-units-v1','nativeForwardAxis':'+Z','nativeSourceToGameRotation':[0,0,0,1],'nativeUnitScaleMeters':scale,'nativeSkeletonNames':[n.name for n in body.nodes],'nativeUpperBoneNames':[n.name for n,w in zip(body.nodes,upper) if w>0],'nativeClipEvents':{a['name']:a['extras']['nativeEvents'] for a in g['animations']},'nativeSocketFrames':sockets,'wardrobeOrigin':'original_authored','sourceAnimationSha256':hashlib.sha256(motionpath.read_bytes()).hexdigest(),'motionVersion':'native-direct-v2'}
 if scene_extras:g['scenes'][0]['extras'].update(scene_extras)
 g['buffers'][0]['byteLength']=len(binary);text=json.dumps(g,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);payload=struct.pack('<4sII',b'glTF',2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4E4F534A)+text+struct.pack('<II',len(binary),0x004E4942)+binary;(OUT/(form+'.glb')).write_bytes(payload);return {'form':form,'bones':len(body.nodes),'clips':len(clips),'triangles':tris,'source_native_basis':True,'source_positions_copied_without_basis_conversion':True,'bytes':len(payload)}
if __name__=='__main__':
 forms=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['wolf','human'];report=[build(f) for f in forms];(D/'direct-native-export.json').write_text(json.dumps(report,indent=2));print('DIRECT_EXPORT',report)
