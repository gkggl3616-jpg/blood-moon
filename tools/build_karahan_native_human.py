"""Complete native Human47 target for the already-finished original PBR job.
No copied Bilge face, cut coat, new rig or paid generation.
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as e
O=R/'art/characters/karahan';bpy.ops.wm.read_factory_settings(use_empty=True);BODY='art/3d/source/pedro-native/main/pedro.ltb';MOTION='art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb';model=e.Reader().from_file(str(R/BODY));arm=bpy.data.armatures.new('ImmutableHuman47');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n in model.nodes:
 bone=arm.edit_bones.new(n.name);bone.head=(0,0,0);bone.tail=(0,2,0);bone.matrix=n.bind_matrix
 if n.parent:bone.parent=arm.edit_bones[n.parent.name]
bpy.ops.object.mode_set(mode='OBJECT')
for piece in model.pieces:
 lod=piece.lods[0];mesh=bpy.data.meshes.new(piece.name);mesh.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new('Body_human_karahan_'+piece.name,mesh);bpy.context.collection.objects.link(obj);obj.parent=rig;uv=mesh.uv_layers.new();normals=[]
 for poly,f in zip(mesh.polygons,lod.faces):
  poly.use_smooth=True
  for li,c in zip(poly.loop_indices,f.vertices):uv.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(lod.vertices[c.vertex_index].normal)
 mesh.normals_split_custom_set(normals)
 for i,n in enumerate(model.nodes):
  group=obj.vertex_groups.new(name=n.name)
  for vi,v in enumerate(lod.vertices):
   for w in v.weights:
    if w.node_index==i and w.bias>0:group.add([vi],w.bias,'REPLACE')
 obj.modifiers.new('NativeSkin','ARMATURE').object=rig;mat=bpy.data.materials.new('KarahanHuman_'+piece.name);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;mesh.materials.append(mat)
pts=[v.location for p in model.pieces for v in p.lods[0].vertices];low=min(p.y for p in pts);scale=1.85/(max(p.y for p in pts)-low);rig.matrix_world=Matrix(((scale,0,0,0),(0,0,-scale,0),(0,scale,0,-low*scale),(0,0,0,1)));bpy.ops.wm.save_as_mainfile(filepath=str(O/'human-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'human-static.glb'),export_format='GLB',export_animations=False,export_extras=True);e.OUT=O;report=e.build('human',{'modelType':'human47','wardrobeOrigin':'original_authored_on_selected_body','sourceClothingTexturesUsed':False,'bodyGeometryOrigin':'complete selected native Human47 anatomy including its own head; original Meshy PBR pending application','faceSharedWithBilge':False,'fittedPants':True,'longHangingPanels':False},body_source=BODY,motion_source=MOTION);print('KARAHAN_NATIVE_HUMAN',report)
