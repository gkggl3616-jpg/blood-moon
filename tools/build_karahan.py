"""Karahan: selected Behamah anatomy, native skin/jaw; original surface art.
No generated body fitted to another rig, no source DTX wardrobe pixels.
Two small head-bound keratin horns; no new bones or dangling garments.
"""
import bpy,bmesh,sys,math,json,inspect,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import build_ice40_family as base;import export_bilge_native_basis as ex
O=R/'art/characters/karahan';O.mkdir(parents=True,exist_ok=True);D=R/'docs/karahan-v0118';D.mkdir(exist_ok=True)
BODY='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb';MOTION='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb';model=ex.Reader().from_file(str(R/BODY));base.OUT=O;base.model=model
photo=Image.open(R/'art/characters/reference/grey-wolf-faithful-large.png').convert('RGB').crop((205,530,295,690));a=np.array(photo,dtype=np.float32)/255;blur=np.array(photo.filter(ImageFilter.GaussianBlur(3)),dtype=np.float32)/255;hair=np.clip((a-blur).mean(2)*2.5,-.2,.2)
def region(piece,lod,face,parts):
 ids=[c.vertex_index for c in face.vertices];p=sum((lod.vertices[i].location for i in ids),Vector())/3;n,c=parts[ids[0]]
 if piece=='lower':
  if c.y>110 or (64<c.y<83 and n<100 and ((abs(c.x)>10 and c.y>75) or all(sum(w.bias for w in lod.vertices[i].weights if model.nodes[w.node_index].name=='Bip01 Pelvis')>.999 for i,(_,center) in parts.items() if (center-c).length<.001))):return 'Remove' # disconnected elaborate head ornaments, not face
  if p.y>24:return 'Pants'
  if p.y<8 and p.z<-11:return 'Claws'
  return 'Fur'
 if c.y>110 and c.z<-22:
  if n in [9,14] or n==3 and c.y<128:return 'Teeth'
  if n==11:return 'Eyes'
  if n in [25,39]:return 'Mouth'
 if p.y>129 and p.z<-32 and abs(p.x)<4:return 'Nose'
 # Native oral surface points inward; never add an external red mouth object.
 normal=sum((lod.vertices[i].normal for i in ids),Vector())/3
 if abs(p.x)<5 and p.z<-22 and 119<p.y<128 and abs(normal.y)>.6:return 'Mouth'
 forearm=sum(w.bias for i in ids for w in lod.vertices[i].weights if model.nodes[w.node_index].name.endswith('Forearm'))/3
 if forearm>.72 and abs(p.x)>45:return 'Bracer'
 if abs(p.x)>65 and p.y<60:return 'Claws'
 return 'Fur'
def appearance(points,normals,kind):
 x,y,z=points.T;noise=base.noise3(points*.8)
 if kind=='Fur':
  blend=np.abs(normals)**4;blend/=np.maximum(.00001,blend.sum(1))[:,None]
  def tex(u,v):
   u=1-np.abs((u%2)-1);v=1-np.abs((v%2)-1);return hair[(v*(hair.shape[0]-1)).astype(int),(u*(hair.shape[1]-1)).astype(int)]
  detail=tex(z*.07+noise*.31,y*.07)*blend[:,0]+tex(x*.07+noise*.31,z*.07)*blend[:,1]+tex(x*.07+noise*.31,y*.07)*blend[:,2]
  chest=np.exp(-(x/18)**2)*np.clip((-z-4)/14,0,1)*np.clip((y-79)/12,0,1)*np.clip((123-y)/12,0,1)
  rgb=np.tile([.17,.18,.19],(len(points),1))+(detail*.16+chest*.09)[:,None];h=detail*.35
  # Three narrow healed claw scars and a little dried blood on left shoulder.
  for shift in [-2,0,2]:
   line=(y-(113+(x-25)*.48+shift));mask=np.exp(-(line/.20)**2)*np.exp(-((x-28)/6)**6)*np.clip((-z-2)/10,0,1)
   rgb=rgb*(1-mask[:,None]*.72)+np.array([.14,.025,.019])*mask[:,None]*.72;h-=mask*.3
 elif kind=='Pants':
  weave=np.sin(x*57+y*49)*np.sin(y*61+z*39);rgb=np.tile([.026,.032,.04],(len(points),1))+(noise*.009+weave*.004)[:,None];h=weave*.4
  seams=(np.abs(np.abs(x)-13)<.20)&(y>30)&(y<64);rgb[seams]=[.19,.13,.064];waist=y>73;rgb[waist]=[.045,.032,.02]
 elif kind=='Bracer':
  rgb=np.tile([.055,.065,.078],(len(points),1))+noise[:,None]*.012;h=noise*.15
  edge=(np.sin(y*1.4+x*.8)>.92);rgb[edge]=[.23,.135,.055]
 else:
  color={'Teeth':[.67,.62,.48],'Eyes':[.72,.29,.035],'Mouth':[.013,.004,.006],'Nose':[.009,.012,.014],'Claws':[.025,.028,.031],'Remove':[0,0,0]}.get(kind,[.15]*3);rgb=np.tile(color,(len(points),1))+noise[:,None]*.006;h=noise*.1
 if kind=='Eyes':rgb[np.abs(np.abs(x)-3.6)<.17]=[.006,.008,.009]
 return np.clip(rgb,0,1),h
base.region=region;base.appearance=appearance
bpy.ops.wm.read_factory_settings(use_empty=True);arm=bpy.data.armatures.new('ImmutableBehamah40');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n in model.nodes:
 b=arm.edit_bones.new(n.name);b.head=(0,0,0);b.tail=(0,2,0);b.matrix=n.bind_matrix
 if n.parent:b.parent=arm.edit_bones[n.parent.name]
bpy.ops.object.mode_set(mode='OBJECT');objects=[]
for piece in model.pieces:
 if piece.name not in ['upper','lower']:continue
 lod=piece.lods[0];parts=base.components(lod);color,normal=base.make_atlas([(piece.name,lod)]);color.name='Karahan_'+piece.name+'_Color';normal.name='Karahan_'+piece.name+'_Normal'
 for im in [color,normal]:im.filepath_raw=str(O/(im.name+'.png'));im.save();im.pack()
 kinds=['Fur','Pants','Bracer','Teeth','Eyes','Mouth','Nose','Claws'];mats=[]
 for kind in kinds:
  m=bpy.data.materials.new('Karahan_'+piece.name+'_'+kind);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=.55 if kind=='Bracer' else 0;p.inputs['Roughness'].default_value=.6 if kind=='Bracer' else .9 if kind in ['Fur','Pants'] else .5
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=color;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=normal;conv=m.node_tree.nodes.new('ShaderNodeNormalMap');conv.inputs['Strength'].default_value=.2 if kind=='Fur' else .25;m.node_tree.links.new(t.outputs['Color'],conv.inputs['Color']);m.node_tree.links.new(conv.outputs['Normal'],p.inputs['Normal']);mats.append(m)
 faces=[f for f in lod.faces if region(piece.name,lod,f,parts)!='Remove'];mesh=bpy.data.meshes.new(piece.name);mesh.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in faces]);obj=bpy.data.objects.new('Body_karahan' if piece.name=='upper' else 'Body_karahan_lower',mesh);bpy.context.collection.objects.link(obj);obj.parent=rig;objects.append(obj)
 for m in mats:mesh.materials.append(m)
 uv=mesh.uv_layers.new(name='NativeUV');normals=[]
 for poly,f in zip(mesh.polygons,faces):
  poly.use_smooth=True;poly.material_index=kinds.index(region(piece.name,lod,f,parts))
  for li,c in zip(poly.loop_indices,f.vertices):uv.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(lod.vertices[c.vertex_index].normal)
 mesh.normals_split_custom_set(normals)
 for i,n in enumerate(model.nodes):
  group=obj.vertex_groups.new(name=n.name)
  for vi,v in enumerate(lod.vertices):
   for w in v.weights:
    if w.node_index==i and w.bias>0:group.add([vi],w.bias,'REPLACE')
 # Only refine large skin polygons; preserve face/jaw topology and weights.
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');edges=[e for e in bm.edges if all(80<v.co.y<115 and abs(v.co.x)<48 for v in e.verts)]
 bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True);bm.to_mesh(mesh);bm.free();mesh.update();
 obj.modifiers.new('PreservedNativeSkin','ARMATURE').object=rig
# Horn rings sweep backward from the upper cranium, rigid to the Head bone.
hornmat=bpy.data.materials.new('Karahan_Keratin');hornmat.use_nodes=True;p=hornmat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.04,.028,.02,1);p.inputs['Roughness'].default_value=.67
for side in [-1,1]:
 vertices=[];faces=[]
 for k in range(7):
  t=k/6;center=Vector((side*(8+3*t),135+13*t,-17+8*t*t));radius=2.8*(1-t)**.7+.05
  for j in range(12):
   angle=j/12*math.tau;vertices.append(center+Vector((math.cos(angle)*radius,0,math.sin(angle)*radius)))
 for k in range(6):
  for j in range(12):faces.append((k*12+j,k*12+(j+1)%12,(k+1)*12+(j+1)%12,(k+1)*12+j))
 faces.append(tuple(reversed(range(12))));faces.append(tuple(range(72,84)));mesh=bpy.data.meshes.new('ShortHorn');mesh.from_pydata(vertices,[],faces);obj=bpy.data.objects.new('Horn_Karahan_'+str(side),mesh);bpy.context.collection.objects.link(obj);obj.parent=rig;mesh.materials.append(hornmat);obj.vertex_groups.new(name='Bip01 Head').add(list(range(len(vertices))),1,'REPLACE');obj.modifiers.new('HeadBound','ARMATURE').object=rig
 for p in mesh.polygons:p.use_smooth=True
# Three placeholders are replaced by the shared inverse-skinned surface projector.
atlas=bpy.data.images.load(str(R/'art/3d/textures/tattoo-atlas.png'));atlas.pack();mat=bpy.data.materials.new('Tattoo_Karahan');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas;mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.025;mat.surface_render_method='DITHERED'
for slot in ['back','left','right']:
 mesh=bpy.data.meshes.new('PatchPlaceholder');mesh.from_pydata([(0,95,10),(1,95,10),(0,96,10)],[],[(0,1,2)]);mesh.uv_layers.new();obj=bpy.data.objects.new('Tattoo_'+slot+'_surface',mesh);bpy.context.collection.objects.link(obj);obj.parent=rig;mesh.materials.append(mat);obj.vertex_groups.new(name='Bip01 Spine2').add([0,1,2],1,'REPLACE');obj['atlas_uv_base']=[0,0,426/1274,431/1234];obj.modifiers.new('Skin','ARMATURE').object=rig
points=[v.location for p in model.pieces for v in p.lods[0].vertices];lo=min(p.y for p in points);scale=2.6/(max(p.y for p in points)-lo);rig.matrix_world=Matrix(((scale,0,0,0),(0,0,-scale,0),(0,scale,0,-lo*scale),(0,0,0,1)));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True)
ex.OUT=O;report=ex.build('wolf',{'modelType':'behamah40','modelHeightMeters':2.6,'nativeRebindRequired':False,'nativeRoleRecipes':{'WolfRoar':['T_cry'],'WolfJump':['T_Dash_JJ'],'WolfJumpAir':['T_Dash_JT'],'WolfLand':['T_Dash_JL']},'wardrobeOrigin':'original_authored_on_selected_body','nativeMouthGeometry':True,'nativeJawBone':'Bip01 Ponytail2','bodyGeometryOrigin':'selected Behamah source skin with original authored continuous fur/pants/bracer surfaces and small Head-bound horns','sourceClothingTexturesUsed':False,'fittedPants':True,'longHangingPanels':False,'tattooProjectionBodyName':'Body_karahan','nativeRoarEffect':'cryguardian','nativeLocomotion':{'quadClip':'T_Dash','walkStrideMeters':2.9,'runStrideMeters':2.6}},body_source=BODY,motion_source=MOTION)
from apply_tattoo_policy import apply
r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload);report['tattoo']=r;report['source_body']=BODY;report['source_motion']=MOTION;(D/'karahan-build.json').write_text(json.dumps(report,indent=2));print('KARAHAN_BUILD',report)
