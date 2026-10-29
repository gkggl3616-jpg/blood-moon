"""Build on the selected Ice40 body, never fit a generated mesh onto another rig.
Source body topology, skin weights and facial/jaw geometry remain unchanged.
All appearance pixels are generated here; no source DTX pixels are read.
Run with Blender. Production candidates stay outside runtime until reviewed.
"""
import sys,json,math,hashlib,struct
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
import build_bilge_original as common
import export_bilge_native_basis as exporter
OUT=R/'art/characters/model-families/ice40/working';OUT.mkdir(parents=True,exist_ok=True)
D=R/'docs/ice40-production';D.mkdir(exist_ok=True)
SOURCE=R/'art/3d/source/wolfteam-archive/selected/wt_wolf_ice_r.ltb'
model=common.Reader().from_file(str(SOURCE))
SIZE=2048

def components(lod):
 parent=list(range(len(lod.vertices)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for face in lod.faces:
  a,b,c=[v.vertex_index for v in face.vertices];parent[root(b)]=root(a);parent[root(c)]=root(a)
 groups={}
 for i in range(len(parent)):groups.setdefault(root(i),[]).append(i)
 result={}
 for ids in groups.values():
  center=sum((lod.vertices[i].location for i in ids),Vector())/len(ids)
  for i in ids:result[i]=(len(ids),center)
 return result

def region(piece,lod,face,parts):
 ids=[c.vertex_index for c in face.vertices];center=sum((lod.vertices[i].location for i in ids),Vector())/3
 count,component=parts[ids[0]];x,y,z=center
 if piece=='cap':return 'Fur'
 if 117.4<component.y<118.3 and component.z<-19 and count==20:return 'Eyes'
 if 103<component.y<116 and component.z<-18 and abs(component.x)<3.6:
  if count in [27,32]:return 'Fur' # Native chin / beard, not the oral cavity.
  if count==46:return 'Tongue'
  return 'Teeth' if count<=15 and abs(component.x)>.2 else 'Mouth'
 if y>115 and z<-25 and abs(x)<2:return 'Nose'
 if 44<y<73.4 and abs(x)<18:return 'Pants'
 forearm=sum(w.bias for i in ids for w in lod.vertices[i].weights if model.nodes[w.node_index].name.endswith('Forearm'))/3
 if forearm>.55:return 'Ice'
 if y<4.5 and z<-13:return 'Claws'
 if y<62 and abs(x)>43:return 'Claws'
 return 'Fur'

def noise3(points):
 cell=np.floor(points);fraction=points-cell;fraction=fraction*fraction*(3-2*fraction);value=np.zeros(len(points))
 for a in [0,1]:
  for b in [0,1]:
   for c in [0,1]:
    lattice=cell+np.array([a,b,c]);hashed=np.sin(lattice@np.array([127.1,311.7,74.7]))*43758.5453;hashed=hashed-np.floor(hashed);weight=np.prod(np.where(np.array([a,b,c]),fraction,1-fraction),axis=1);value+=hashed*weight
 return value*2-1

def appearance(points,normals,kind):
 x,y,z=points.T;detail_points=points.copy();detail_points[:,0]=np.abs(detail_points[:,0])
 # Deterministic spatial detail is continuous across UV seams.
 noise=noise3(detail_points*.8)
 fine=noise3(detail_points*np.array([16,2,16]))
 height=np.zeros(len(points),dtype=np.float32)
 if kind=='Fur':
  base=np.tile([.24,.29,.33],(len(points),1));front=np.clip((-z-4)/15,0,1);chest=np.exp(-((x/15)**2))*np.clip((y-72)/15,0,1)*np.clip((110-y)/12,0,1)*front
  muzzle=np.clip((y-110)/10,0,1)*front
  base+=np.maximum(chest*.13,muzzle*.08)[:,None]
  strands=noise3(detail_points*np.array([5,.35,5])+noise[:,None]*.4)
  crease=np.exp(-((y-86)/1.1)**2)*np.exp(-((x/19)**4))*front
  midline=np.exp(-((x/1.5)**2))*np.clip((y-75)/6,0,1)*np.clip((100-y)/6,0,1)*front
  base+=(noise*.035+strands*.03+fine*.013-crease*.065-midline*.04)[:,None];height=noise*.15+strands*.5+fine*.35
 elif kind=='Pants':
  weave=np.sin(x*76+y*41)*np.sin(y*81+z*39);base=np.tile([.035,.075,.13],(len(points),1));base+=(noise*.009+weave*.008)[:,None];height=weave*.8+noise*.2
  # Woven seam and knee reinforcement follow the body, without hanging geometry.
  seam=(np.abs(np.abs(x)-12.5)<.32)&(y<65)&(y>38);base[seam]=[.32,.24,.10]
  stitch=seam&(np.sin(y*8)>0.35);base[stitch]=[.52,.41,.20]
  knee=(y<43)&(y>36)&(z<-9);base[knee]*=.7
  waist=y>68;base[waist]=[.06,.055,.045]
 elif kind=='Ice':
  crystal=np.sin(x*.8+y*.65+z*1.5)*np.sin(x*1.7-y*.5+z*.9);base=np.tile([.13,.30,.40],(len(points),1));base+=(crystal*.065+fine*.013)[:,None];height=crystal*.7+fine*.2
 elif kind=='Teeth':base=np.tile([.70,.67,.55],(len(points),1));base+=(noise*.015)[:,None];height=fine*.1
 elif kind=='Mouth':base=np.tile([.018,.009,.012],(len(points),1));height=noise*.05
 elif kind=='Tongue':base=np.tile([.075,.025,.033],(len(points),1));height=noise*.08
 elif kind=='Eyes':
  base=np.tile([.05,.20,.24],(len(points),1));iris=np.abs(np.abs(x)-2.55)<.22;base[iris]=[.34,.72,.76];pupil=np.abs(np.abs(x)-2.55)<.065;base[pupil]=[.005,.008,.01]
 elif kind=='Claws':base=np.tile([.12,.14,.15],(len(points),1));base+=(noise*.015)[:,None];height=fine*.15
 else:base=np.tile([.015,.02,.025],(len(points),1));height=noise*.1
 return np.clip(base,0,1),height

def make_atlas(surface):
 color=np.zeros((SIZE,SIZE,4),dtype=np.float32);color[:,:,:3]=[.18,.22,.25];color[:,:,3]=1
 bump=np.zeros((SIZE,SIZE),dtype=np.float32);mask=np.zeros((SIZE,SIZE),bool)
 for piece,lod in surface:
  parts=components(lod)
  for face in lod.faces:
   tex=np.array([list(v.texcoord) for v in face.vertices],dtype=np.float32)*(SIZE-1)
   lo=np.maximum(0,np.floor(tex.min(0)).astype(int));hi=np.minimum(SIZE-1,np.ceil(tex.max(0)).astype(int))
   if np.any(hi<lo):continue
   xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1));p=np.stack([xx.ravel(),yy.ravel()],axis=1)
   a,b,c=tex;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-6:continue
   u=((b[1]-c[1])*(p[:,0]-c[0])+(c[0]-b[0])*(p[:,1]-c[1]))/den;v=((c[1]-a[1])*(p[:,0]-c[0])+(a[0]-c[0])*(p[:,1]-c[1]))/den;w=1-u-v;inside=(u>=-.002)&(v>=-.002)&(w>=-.002)
   if not inside.any():continue
   p=p[inside];factors=np.stack([u[inside],v[inside],w[inside]],axis=1);points=factors@np.array([list(lod.vertices[c.vertex_index].location) for c in face.vertices]);normals=factors@np.array([list(lod.vertices[c.vertex_index].normal) for c in face.vertices]);rgb,h=appearance(points,normals,region(piece,lod,face,parts));color[p[:,1],p[:,0],:3]=rgb;bump[p[:,1],p[:,0]]=h;mask[p[:,1],p[:,0]]=True
 # Padding prevents black seams in mip levels; it does not alter source UVs.
 for _ in range(12):
  old=mask.copy()
  for axis in [0,1]:
   for direction in [-1,1]:
    shifted=np.roll(old,direction,axis);new=shifted&~mask;color[new]=np.roll(color,direction,axis)[new];bump[new]=np.roll(bump,direction,axis)[new];mask|=new
 def save(name,pixels,space='sRGB'):
  im=bpy.data.images.new(name,width=SIZE,height=SIZE,alpha=True);im.colorspace_settings.name=space;im.pixels.foreach_set(np.flipud(pixels).ravel());im.filepath_raw=str(OUT/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
 base=save('ice40-original-color',color)
 # Tangent-space micro-normal derived from the authored height map, never DTX.
 dy,dx=np.gradient(bump);normal=np.stack([-dx*.26,dy*.26,np.ones_like(bump)],axis=2);normal/=np.linalg.norm(normal,axis=2)[:,:,None];rgba=np.ones_like(color);rgba[:,:,:3]=normal*.5+.5
 normal=save('ice40-original-normal',rgba,'Non-Color');return base,normal

def build():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 surface=[(p.name,p.lods[0]) for p in model.pieces if p.name in ['icewolf','cap']]
 base,normal=make_atlas(surface);materials={}
 for name,rough,metal in [('Fur',.92,0),('Pants',.86,0),('Ice',.37,.08),('Teeth',.54,0),('Mouth',.8,0),('Tongue',.65,0),('Eyes',.28,0),('Nose',.74,0),('Claws',.58,0)]:
  mat=bpy.data.materials.new('Ice40_'+name);mat.use_nodes=True;shader=mat.node_tree.nodes['Principled BSDF'];shader.inputs['Roughness'].default_value=rough;shader.inputs['Metallic'].default_value=metal;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=base;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=normal;convert=mat.node_tree.nodes.new('ShaderNodeNormalMap');convert.inputs['Strength'].default_value=.25 if name in ['Fur','Pants'] else .12;mat.node_tree.links.new(n.outputs['Color'],convert.inputs['Color']);mat.node_tree.links.new(convert.outputs['Normal'],shader.inputs['Normal']);materials[name]=mat
 arm=bpy.data.armatures.new('ImmutableIce40');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in model.nodes:
  b=arm.edit_bones.new(n.name);b.head=(0,0,0);b.tail=(0,2,0);b.matrix=n.bind_matrix
  if n.parent:b.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT');points=[v.location for p in model.pieces for v in p.lods[0].vertices];low=min(v.y for v in points);scale=2.4/(max(v.y for v in points)-low);T=Matrix(((-scale,0,0,0),(0,0,scale,0),(0,scale,0,-low*scale),(0,0,0,1)))
 objects=[];material_names=list(materials)
 for piece,lod in surface:
  data=bpy.data.meshes.new(piece);data.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new('Body_bilge' if piece=='icewolf' else 'Head_native_detail',data);bpy.context.collection.objects.link(obj);obj.parent=rig;objects.append(obj);parts=components(lod)
  for mat in materials.values():data.materials.append(mat)
  uv=data.uv_layers.new(name='NativeUV');normals=[]
  for poly,face in zip(data.polygons,lod.faces):
   poly.use_smooth=True;poly.material_index=material_names.index(region(piece,lod,face,parts))
   for li,c in zip(poly.loop_indices,face.vertices):uv.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(lod.vertices[c.vertex_index].normal)
  data.normals_split_custom_set(normals)
  for i,n in enumerate(model.nodes):
   group=obj.vertex_groups.new(name=n.name)
   for vi,v in enumerate(lod.vertices):
    for w in v.weights:
     if w.node_index==i:group.add([vi],w.bias,'REPLACE')
  if piece=='icewolf' and '--neck-weight-experiment' in sys.argv:
   spine=obj.vertex_groups['Bip01 Spine2'];neck=obj.vertex_groups['Bip01 Neck'];head=obj.vertex_groups['Bip01 Head'];jaw=obj.vertex_groups['Bip01 Ponytail2'];changed=0
   for vertex in data.vertices:
    x,y,z=vertex.co;value={g.group:g.weight for g in vertex.groups}
    if not(94<y<109 and abs(x)<12 and z<-3) or value.get(jaw.index,0)>.05:continue
    moving=sum(value.get(i,0) for i in [spine.index,neck.index,head.index])
    if moving<.7:continue
    t=max(0,min(1,(y-99)/10));t=t*t*(3-2*t)
    for group in [spine,neck,head]:group.remove([vertex.index])
    spine.add([vertex.index],moving*(1-t),'REPLACE');neck.add([vertex.index],moving*t,'REPLACE');changed+=1
   obj['focused_neck_weight_repair_vertices']=changed;print('FOCUSED_NECK_REPAIR',changed)
  mod=obj.modifiers.new('PreservedNativeSkin','ARMATURE');mod.object=rig;obj['source_geometry']='selected Ice40 body; original positions and skin weights';obj['texture_origin']='procedural_original_no_source_DTX_pixels';obj['fitted_pants']=True;obj['long_hanging_panels']=False
 # Tattoos are projected onto the actual neutral-pose back, with copied skin.
 common.tattoos(objects[0],rig,model,T)
 rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@T;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(OUT/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True)
 gaits=json.loads((D/'gait-measurements.json').read_text());walk=next(g for g in gaits if g['clip']=='LWF');quad=next(g for g in gaits if g['clip']=='T_WallDash');locomotion={'quadClip':'T_WallDash','walkStrideMeters':walk['stride_m'],'runStrideMeters':quad['stride_m'],'source':'same selected Ice40 child motion; original tracks unchanged','measurement':'median low-contact joint backward velocity times cycle duration'}
 exporter.OUT=OUT;report=exporter.build('wolf',{'bodyGeometryOrigin':'user_supplied_ice40_base','skinOrigin':'source weights with focused neck/chest repair; bones and keys unchanged','wardrobeOrigin':'original_authored_on_selected_body','sourceClothingTexturesUsed':False,'fittedPants':True,'longHangingPanels':False,'productionStage':'base_candidate_visual_review_pending','nativeLocomotion':locomotion})
 from apply_tattoo_policy import apply as apply_shared_policy
 tattoo_report,payload,_=apply_shared_policy(OUT/'wolf.glb');(OUT/'wolf.glb').write_bytes(payload);report['shared_tattoo_policy']=tattoo_report;final=json.loads(payload[20:20+struct.unpack_from('<I',payload,12)[0]]);report['triangles']=sum(final['accessors'][p['indices']]['count']//3 for m in final['meshes'] for p in m['primitives']);report['bytes']=len(payload)
 report.update(source_geometry_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),source_vertices_unchanged=True,source_weights_unchanged='--neck-weight-experiment' not in sys.argv,neck_weights_locally_repaired='--neck-weight-experiment' in sys.argv,source_clothing_DTX_pixels_read=False,mouth='native face / teeth / jaw geometry; no external mouth ellipsoid',status='candidate_not_visual_accepted',runtime_installed=False)
 (D/'base-build.json').write_text(json.dumps(report,indent=2));print('ICE40_BASE',json.dumps(report))
if __name__=='__main__':build()
