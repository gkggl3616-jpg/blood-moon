# REJECTED VISUAL EXPERIMENT: not a production template. See docs/karahan-v0118/GUNCEL-RAPOR-TR.md.
"""Karahan human: native Pedro47 body/skin, original already-produced face.
Short black armour/bronze trim and fitted trousers, no long coat or wrist strips.
Original game DTX clothes are not imported.
"""
import bpy,sys,math,json,struct,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import build_ice40_family as base;import export_bilge_native_basis as ex
O=R/'art/characters/karahan';D=R/'docs/karahan-v0118';BODY='art/3d/source/pedro-native/main/pedro.ltb';MOTION='art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb';model=ex.Reader().from_file(str(R/BODY));base.OUT=O;base.model=model
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'app/src/main/assets/models/human-bilge.glb'));original=next(o for o in bpy.context.scene.objects if o.type=='MESH');face_material=original.data.materials[0].copy();face_material.name='Karahan_OriginalProducedFace';p=face_material.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.78
for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
arm=bpy.data.armatures.new('ImmutableHuman47');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n in model.nodes:
 b=arm.edit_bones.new(n.name);b.head=(0,0,0);b.tail=(0,2,0);b.matrix=n.bind_matrix
 if n.parent:b.parent=arm.edit_bones[n.parent.name]
bpy.ops.object.mode_set(mode='OBJECT')
def region(piece,lod,face,parts):return piece
def appearance(points,normals,kind):
 x,y,z=points.T;noise=base.noise3(points*1.6);h=noise*.15
 if kind=='Hand':rgb=np.tile([.43,.28,.20],(len(points),1))+noise[:,None]*.012
 elif kind=='Shoes':rgb=np.tile([.028,.024,.021],(len(points),1))+noise[:,None]*.006
 elif kind=='Red_Lowerbody':
  weave=np.sin(x*52+y*43)*np.sin(y*72+z*39);rgb=np.tile([.025,.031,.038],(len(points),1))+(noise*.008+weave*.003)[:,None];seam=(np.abs(np.abs(x)-11)<.25)&(y>30);rgb[seam]=[.17,.10,.045];h=weave*.4
 else:
  rgb=np.tile([.055,.065,.077],(len(points),1))+noise[:,None]*.012
  collar=y>94;belt=y<65;edge=(np.abs(np.abs(x)-12)<.45)&(y>78)&(z<-7)
  rgb[collar|belt|edge]=[.23,.14,.059];h+=np.sin(y*4)*.1
 return np.clip(rgb,0,1),h
base.region=region;base.appearance=appearance
for piece in model.pieces:
 if piece.name=='Head':continue
 lod=piece.lods[0];color,normal=base.make_atlas([(piece.name,lod)])
 for im,suffix in [(color,'Color'),(normal,'Normal')]:im.name='KarahanHuman_'+piece.name+'_'+suffix;im.filepath_raw=str(O/(im.name+'.png'));im.save();im.pack()
 mat=bpy.data.materials.new('KarahanHuman_'+piece.name);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=.35 if piece.name=='Red_Upperbody' else 0;p.inputs['Roughness'].default_value=.65 if piece.name=='Red_Upperbody' else .85
 t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=color;mat.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=normal;c=mat.node_tree.nodes.new('ShaderNodeNormalMap');c.inputs['Strength'].default_value=.22;mat.node_tree.links.new(n.outputs['Color'],c.inputs['Color']);mat.node_tree.links.new(c.outputs['Normal'],p.inputs['Normal'])
 mesh=bpy.data.meshes.new(piece.name);mesh.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new('Body_human_karahan_'+piece.name,mesh);bpy.context.collection.objects.link(obj);obj.parent=rig;mesh.materials.append(mat);uv=mesh.uv_layers.new();normals=[]
 for poly,f in zip(mesh.polygons,lod.faces):
  poly.use_smooth=True
  for li,c in zip(poly.loop_indices,f.vertices):uv.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(lod.vertices[c.vertex_index].normal)
 mesh.normals_split_custom_set(normals)
 for i,n in enumerate(model.nodes):
  group=obj.vertex_groups.new(name=n.name)
  for vi,v in enumerate(lod.vertices):
   for w in v.weights:
    if w.node_index==i and w.bias>0:group.add([vi],w.bias,'REPLACE')
 obj.modifiers.new('NativeSkin','ARMATURE').object=rig
# Reuse the project's original produced face, not the game's clothing pixels.
raw=(R/'app/src/main/assets/models/human-bilge.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:]
def read(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];code={5126:'f',5123:'H',5125:'I'}[a['componentType']];size=struct.calcsize('<'+code*width);return [struct.unpack_from('<'+code*width,binary,v.get('byteOffset',0)+a.get('byteOffset',0)+j*v.get('byteStride',size)) for j in range(a['count'])]
for primitive in g['meshes'][0]['primitives']:
 a=primitive['attributes'];points=read(a['POSITION']);normals=read(a['NORMAL']);uvs=read(a['TEXCOORD_0']);js=read(a['JOINTS_0']);ws=read(a['WEIGHTS_0']);indices=[i[0] for i in read(primitive['indices'])];faces=[tuple(indices[k:k+3]) for k in range(0,len(indices),3) if min(points[i][1] for i in indices[k:k+3])>99.5];used=sorted(set(i for f in faces for i in f));mapping={i:k for k,i in enumerate(used)};mesh=bpy.data.meshes.new('OriginalFace');mesh.from_pydata([points[i] for i in used],[],[tuple(mapping[i] for i in f) for f in faces]);obj=bpy.data.objects.new('Head_karahan_original',mesh);bpy.context.collection.objects.link(obj);obj.parent=rig;mesh.materials.append(face_material);uv=mesh.uv_layers.new();ns=[]
 for poly,f in zip(mesh.polygons,faces):
  poly.use_smooth=True
  for li,i in zip(poly.loop_indices,f):uv.data[li].uv=(uvs[i][0],1-uvs[i][1]);ns.append(Vector(normals[i]))
 mesh.normals_split_custom_set(ns)
 for vertex in mesh.vertices:
  if vertex.co.y>102:vertex.co.x*=1.045;vertex.co.z=-1+(vertex.co.z+1)*1.025
 for bi,node in enumerate(model.nodes):
  group=obj.vertex_groups.new(name=node.name)
  for i in used:
   for j,w in zip(js[i],ws[i]):
    if j==bi and w>0:group.add([mapping[i]],w,'REPLACE')
 obj.modifiers.new('Original47Skin','ARMATURE').object=rig
# Compact bronze emblem, fully Spine2-bound. No dangling cloth or new joints.
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=(0,87,-11));obj=bpy.context.object;obj.name='Crest_Karahan';obj.scale=(2.0,2.8,.7);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.parent=rig;obj.vertex_groups.new(name='Bip01 Spine2').add(list(range(len(obj.data.vertices))),1,'REPLACE');obj.modifiers.new('RigidChest','ARMATURE').object=rig;mat=bpy.data.materials.new('KarahanBronze');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.23,.12,.045,1);p.inputs['Metallic'].default_value=.6;p.inputs['Roughness'].default_value=.5;obj.data.materials.append(mat)
pts=[v.location for p in model.pieces for v in p.lods[0].vertices];low=min(p.y for p in pts);scale=1.85/(max(p.y for p in pts)-low);rig.matrix_world=Matrix(((scale,0,0,0),(0,0,-scale,0),(0,scale,0,-low*scale),(0,0,0,1)));bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'human-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'human-static.glb'),export_format='GLB',export_animations=False,export_extras=True);ex.OUT=O;report=ex.build('human',{'modelType':'human47','wardrobeOrigin':'original_authored_on_selected_body','sourceClothingTexturesUsed':False,'bodyGeometryOrigin':'native Pedro47 short armoured body with project original face, PBR baked original armour and original fitted trousers','fittedPants':True,'longHangingPanels':False,'faceOrigin':'project original paid Bilge human face, shared approved Human47 family'},body_source=BODY,motion_source=MOTION);(D/'karahan-human-build.json').write_text(json.dumps(report,indent=2));print('KARAHAN_HUMAN',report)
