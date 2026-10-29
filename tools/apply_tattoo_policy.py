"""Apply the shared tattoo surface policy to a GLB without re-exporting its rig.
Changes only three tattoo primitives and their metadata. Body, bind matrices,
all original animation channels and keys remain byte-for-byte referenced.
Run with Blender for mathutils. Works with native Bip01 and legacy role names.
"""
import json,struct,sys,hashlib,copy,argparse
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
POLICY=json.loads((R/'art/characters/model-families/tattoo-policy.json').read_text())
def apply(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);nodes=g['nodes'];meta=g['scenes'][g.get('scene',0)].setdefault('extras',{});policy_hash=hashlib.sha256(json.dumps(POLICY,sort_keys=True).encode()).hexdigest();before_animation=copy.deepcopy(g['animations']);before_skin=copy.deepcopy(g['skins']);before_nodes=copy.deepcopy(nodes);parents={c:i for i,node in enumerate(nodes) for c in node.get('children',[])}
 if meta.get('tattooPolicyHash')==policy_hash:
  return {'asset':path.name,'already_current':True,'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(raw).hexdigest(),'body_skin_and_all_animation_objects_unchanged':True,'policy_version':POLICY['version'],'policy_hash':policy_hash},raw,raw
 def read(ai):
  a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];code={5126:'f',5123:'H',5125:'I',5121:'B'}[a['componentType']];size=struct.calcsize('<'+code*width);return [struct.unpack_from('<'+code*width,binary,v.get('byteOffset',0)+a.get('byteOffset',0)+i*v.get('byteStride',size)) for i in range(a['count'])]
 def acc(values,kind,width,component=5126):
  while len(binary)%4:binary.append(0)
  offset=len(binary);flat=[x for v in values for x in (list(v) if isinstance(v,(list,tuple,Vector)) else [v])];code={5126:'f',5123:'H',5125:'I'}[component];payload=struct.pack('<'+code*len(flat),*flat);binary.extend(payload);vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(payload)});a={'bufferView':vi,'componentType':component,'count':len(values),'type':kind}
  if kind=='VEC3':a.update(min=[min(flat[i::3]) for i in range(3)],max=[max(flat[i::3]) for i in range(3)])
  g['accessors'].append(a);return len(g['accessors'])-1
 local=[]
 for node in nodes:
  if 'matrix' in node:p,q,s=Matrix([node['matrix'][i:i+4] for i in range(0,16,4)]).transposed().decompose()
  else:p=Vector(node.get('translation',[0,0,0]));q=node.get('rotation',[0,0,0,1]);q=Quaternion((q[3],*q[:3]));s=Vector(node.get('scale',[1,1,1]))
  local.append([p,q,s])
 upper=set(meta.get('nativeUpperBoneNames',[]));native=bool(meta.get('nativeSourceKeyPreserved'))
 for role in (['LSt','UMSt'] if native else ['WolfIdle']):
  animation=next(a for a in g['animations'] if a['name']==role)
  for c in animation['channels']:
   i=c['target']['node'];name=nodes[i].get('name')
   if native and (role=='LSt' and name in upper or role=='UMSt' and name not in upper):continue
   v=read(animation['samplers'][c['sampler']]['output'])[0]
   if c['target']['path']=='translation':local[i][0]=Vector(v)
   elif c['target']['path']=='rotation':local[i][1]=Quaternion((v[3],*v[:3])).normalized()
   elif c['target']['path']=='scale':local[i][2]=Vector(v)
 for i,node in enumerate(nodes):
  length=meta.get('nativeJointRestLengths',{}).get(node.get('name'))
  if length and local[i][0].length>1e-6:local[i][0]*=length/local[i][0].length
 world={}
 def pose(i):
  if i not in world:world[i]=(pose(parents[i]) if i in parents else Matrix.Identity(4))@Matrix.LocRotScale(*local[i])
  return world[i]
 body_node=next((node for node in nodes if node.get('name')==meta.get('tattooProjectionBodyName') and 'mesh' in node),None) or next(node for node in nodes if node.get('name','').startswith('Body_') and 'mesh' in node);skin=g['skins'][body_node['skin']];inverse=[Matrix([v[i:i+4] for i in range(0,16,4)]).transposed() for v in read(skin['inverseBindMatrices'])];matrices=[pose(i)@b for i,b in zip(skin['joints'],inverse)];norm=lambda name:name.replace('_','').replace(' ','').lower();joint_nodes={norm(nodes[i]['name']):i for i in skin['joints']}
 def joint(legacy,bip):
  i=joint_nodes.get(norm(bip),joint_nodes.get(norm(legacy)));assert i is not None,(path.name,legacy,bip);return pose(i).translation
 positions=[];bind_positions=[];weights=[];faces=[];face_materials=[]
 body_mesh_before=copy.deepcopy(g['meshes'][body_node['mesh']])
 for p in body_mesh_before['primitives']:
  a=p['attributes'];ps=read(a['POSITION']);js=read(a['JOINTS_0']);ws=read(a['WEIGHTS_0']);start=len(positions)
  for point,j,w in zip(ps,js,ws):
   bind_positions.append(Vector(point))
   value={i:v for i,v in zip(j,w) if v>1e-7};weights.append(value);positions.append(sum(((matrices[i]@Vector(point))*v for i,v in value.items()),Vector()))
  ix=[i[0] for i in read(p['indices'])] if 'indices' in p else list(range(len(ps)))
  for k in range(0,len(ix),3):faces.append(tuple(start+i for i in ix[k:k+3]));face_materials.append(g['materials'][p['material']]['name'].lower())
 tree=BVHTree.FromPolygons(positions,faces,all_triangles=True);zero=Matrix([[0.0]*4 for _ in range(4)]);direction=Vector((0,0,1));report=[];back=POLICY['back'];height_scale=meta.get('modelHeightMeters',2.4)/2.4;offset=.00085
 def clip(poly,axis,edge,lower):
  result=[]
  for current,previous in zip(poly,poly[-1:]+poly[:-1]):
   p,pw=previous;q,qw=current;ip=p[axis]>=edge if lower else p[axis]<=edge;iq=q[axis]>=edge if lower else q[axis]<=edge
   if ip!=iq:
    t=(edge-p[axis])/(q[axis]-p[axis]);result.append((p.lerp(q,t),pw.lerp(qw,t)))
   if iq:result.append(current)
  return result
 for slot in ['back','left','right']:
  if slot=='back':
   center=joint('Chest',back['anchor_lower']).lerp(joint('Neck',back['anchor_upper']),back['anchor_mix']);center.y+=back['raise_m_at_2_4m_height']*height_scale;width=back['width_m_at_2_4m_height']*height_scale;height=back['height_m_at_2_4m_height']*height_scale
  else:
   side='L' if slot=='left' else 'R';center=joint('UpperArm'+side,'Bip01 '+side+' UpperArm').lerp(joint('Forearm'+side,'Bip01 '+side+' Forearm'),POLICY['arms']['anchor_mix']);width=POLICY['arms']['width_m_at_2_4m_height']*height_scale;height=POLICY['arms']['height_m_at_2_4m_height']*height_scale
  requested_height=height
  left,right=center.x-width/2,center.x+width/2;bottom,top=center.y-height/2,center.y+height/2
  if slot=='back':bottom=max(bottom,joint('Hips','Bip01 Pelvis').y+back['minimum_above_pelvis_m_at_2_4m_height']*height_scale);height=top-bottom
  if slot=='back' and meta.get('modelType')=='ice40' and meta.get('wardrobeOrigin')=='original_authored' and not meta.get('bodyGeometryOrigin'):
   bottom=max(bottom,POLICY['geometry_skin_regions']['legacy_generated_bilge_wolf']['back_min_height_m']);height=top-bottom
  if slot=='back' and back['preserve_patch_aspect_when_clipped']:
   width*=height/requested_height;left,right=center.x-width/2,center.x+width/2
  assert height>.12,(slot,'invalid tattoo rectangle');ps=[];ns=[];uv=[];js=[];ws=[];clothing=0
  for face,inds in enumerate(faces):
   if any(token in face_materials[face] for token in POLICY['excluded_material_tokens']) or face_materials[face].rsplit('_',1)[-1] in POLICY['excluded_material_regions']:continue
   points=[positions[i] for i in inds]
   if min(p.x for p in points)>right or max(p.x for p in points)<left or min(p.y for p in points)>top or max(p.y for p in points)<bottom:continue
   mid=sum(points,Vector())/3;hit,normal,visible,distance=tree.ray_cast(Vector((mid.x,mid.y,-4)),direction,8)
   if hit is None or visible!=face:continue
   if normal.dot(direction)>0:normal.negate()
   poly=[(p,Vector(tuple(int(k==j) for k in range(3)))) for j,p in enumerate(points)]
   for axis,edge,lower in [(0,left,True),(0,right,False),(1,bottom,True),(1,top,False)]:
    if not poly:break
    poly=clip(poly,axis,edge,lower)
   if len(poly)<3:continue
   vertices=[]
   for point,factors in poly:
    value={}
    for i,factor in zip(inds,factors):
     for bone,w in weights[i].items():value[bone]=value.get(bone,0)+w*factor
    value=dict(sorted(value.items(),key=lambda v:-v[1])[:4]);total=sum(value.values());value={i:w/total for i,w in value.items()};matrix=sum((matrices[i]*w for i,w in value.items()),zero.copy());p=matrix.inverted_safe()@(point+normal*offset);normal_bind=(matrix.to_3x3().transposed()@normal).normalized()
    if meta.get('tattooSkinMethod')=='barycentric_bind_surface':p=sum((bind_positions[i]*f for i,f in zip(inds,factors)),Vector())+normal_bind*(offset/meta['nativeUnitScaleMeters'])
    indices=list(value);values=list(value.values());vertices.append((p,normal_bind,[(point.x-left)/width*426/1274,(1-(point.y-bottom)/height)*431/1234],indices+[0]*(4-len(indices)),values+[0]*(4-len(values))))
   for j in range(1,len(vertices)-1):
    for vertex in [vertices[0],vertices[j],vertices[j+1]]:
     p,n,u,joint_ids,bias=vertex;ps.append(p);ns.append(n);uv.append(u);js.append(joint_ids);ws.append(bias)
  assert ps,(path.name,'no skin patch',slot)
  node=next(n for n in nodes if n.get('name','').startswith('Tattoo_'+slot+'_surface'));mesh=g['meshes'][node['mesh']];material=mesh['primitives'][0]['material'];mesh['primitives']=[{'attributes':{'POSITION':acc(ps,'VEC3',3),'NORMAL':acc(ns,'VEC3',3),'TEXCOORD_0':acc(uv,'VEC2',2),'JOINTS_0':acc(js,'VEC4',4,5123),'WEIGHTS_0':acc(ws,'VEC4',4)},'indices':acc(list(range(len(ps))),'SCALAR',1,5125),'material':material}];node.setdefault('extras',{}).update(atlas_uv_base=[0,0,426/1274,431/1234],tattoo_uv_basis='gltf-top-left',tattoo_policy_version=POLICY['version'],placement_reference='actual_neutral_body_triangles_back_inverse_skin',clothing_faces_excluded=True,neutral_min_height_m=bottom,neutral_max_height_m=top,surface_offset_m=offset,patch_width_m=width,patch_height_m=height)
  report.append({'slot':slot,'triangles':len(ps)//3,'height_min_m':bottom,'height_max_m':top,'patch_width_m':width,'patch_height_m':height,'clothing_faces':0})
 assert g['animations']==before_animation and g['skins']==before_skin
 assert all(node==before_nodes[i] for i,node in enumerate(nodes) if 'Tattoo_' not in node.get('name',''))
 assert g['meshes'][body_node['mesh']]==body_mesh_before
 meta['tattooPolicyVersion']=POLICY['version'];meta['tattooPolicyHash']=policy_hash;g['buffers'][0]['byteLength']=len(binary);text=json.dumps(g,separators=(',',':')).encode();text+=b' '*((-len(text))%4);binary+=b'\0'*((-len(binary))%4);payload=struct.pack('<4sII',b'glTF',2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4E4F534A)+text+struct.pack('<II',len(binary),0x004E4942)+binary
 return {'asset':path.name,'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(payload).hexdigest(),'body_skin_and_all_animation_objects_unchanged':True,'patches':report,'policy_version':POLICY['version'],'policy_hash':policy_hash},payload,raw
if __name__=='__main__':
 raw_args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 parser=argparse.ArgumentParser();parser.add_argument('models',nargs='*');parser.add_argument('--asset',action='append',default=[]);parser.add_argument('--report');args=parser.parse_args(raw_args)
 paths=[R/path for path in args.asset] if args.asset else [R/'app/src/main/assets/models'/(key+'.glb') for key in (args.models or ['bilge','kultigin','alparslan','konuralp'])];built=[apply(path) for path in paths]
 # Validate the complete batch before replacing any runtime file.
 for path,(report,payload,raw) in zip(paths,built):
  backup=R/'art/3d/source/tattoo-policy-backups'/path.name;backup.parent.mkdir(parents=True,exist_ok=True)
  if not backup.exists():backup.write_bytes(raw)
  temporary=path.with_suffix('.glb.tmp');temporary.write_bytes(payload);temporary.replace(path)
 out=R/args.report if args.report else R/'docs/full-archive-review'/('tattoo-policy-idempotence.json' if all(r.get('already_current') for r,_,_ in built) else 'tattoo-policy-application.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps([r for r,_,_ in built],indent=2));print('TATTOO_POLICY_APPLIED',[r for r,_,_ in built])
