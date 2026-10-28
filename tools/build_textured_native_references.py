"""Native UV/texture reference pair; preserve source geometry and weights.
Not a replacement for approved game characters. No paid generation.
"""
import bpy,types,importlib,sys,json,math,bisect
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
OUT=R/'art/3d/source/wolfteam-archive/textured-references';OUT.mkdir(exist_ok=True);reports=[]
for form,filename,height in [('wolf','pedro_wolf',2.4),('human','pedro',1.85)]:
 bpy.ops.wm.read_factory_settings(use_empty=True);model=Reader().from_file(str(R/'art/3d/source/pedro-native/main'/(filename+'.ltb')));motion=Reader().from_file(str(R/'art/3d/source/pedro-native/new-motion'/('wt_new_wolf_ch.ltb' if form=='wolf' else 'wt_new_man_ch.ltb')))
 mappings={'upper':'wt_chars/newchars/pedro_wolf/pedro_wolf_upper.png','lower':'wt_chars/newchars/pedro_wolf/pedro_wolf_lower.png','hair':'wt_chars/newchars/pedro_wolf/pedro_wolf_hair.png'} if form=='wolf' else {'Red_Upperbody':'wt_chars/newchars/pedro_red/pedro_r_upperbody.png','Head':'wt_chars/newchars/pedro_red/pedro_r_upperbody.png','Red_Lowerbody':'wt_chars/newchars/pedro_red/pedro_r_lowerbody.png','Hand':'wt_chars/newchars/pedro_red/pedro_gloves01.png','Shoes':'wt_chars/newchars/pedro_red/pedro_boots01.png'}
 arm=bpy.data.armatures.new('NativeSkeleton');rig=bpy.data.objects.new('NativeSkeleton',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in model.nodes:
  b=arm.edit_bones.new(n.name);b.head=(0,0,0);b.tail=(0,2,0);b.matrix=n.bind_matrix
  if n.parent:b.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT');points=[v.location for p in model.pieces for v in p.lods[0].vertices];low=min(v.y for v in points);s=height/(max(v.y for v in points)-low);T=Matrix(((-s,0,0,0),(0,0,s,0),(0,s,0,-low*s),(0,0,0,1)));rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@T;triangles=0
 for piece in model.pieces:
  if piece.name.startswith('Tattoo'):continue
  lod=piece.lods[0];data=bpy.data.meshes.new(piece.name);data.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new(piece.name,data);bpy.context.collection.objects.link(obj);obj.parent=rig
  uv=data.uv_layers.new(name='NativeUV');normals=[]
  for poly,face in zip(data.polygons,lod.faces):
   poly.use_smooth=True
   for li,c in zip(poly.loop_indices,face.vertices):uv.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(lod.vertices[c.vertex_index].normal)
  data.normals_split_custom_set(normals)
  for index,n in enumerate(model.nodes):
   g=obj.vertex_groups.new(name=n.name)
   for vi,v in enumerate(lod.vertices):
    for weight in v.weights:
     if weight.node_index==index:g.add([vi],weight.bias,'REPLACE')
  modifier=obj.modifiers.new('OriginalNativeSkin','ARMATURE');modifier.object=rig
  mat=bpy.data.materials.new(piece.name+'_NativeDiffuse');mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.85;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'art/3d/source/wolfteam-archive/decoded'/mappings[piece.name]),check_existing=True);tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);data.materials.append(mat);triangles+=len(lod.faces)
 # Native idle only: verify source UV/weights without transferring onto another body.
 animations={a.name:a for a in motion.animations};lower=animations['LSt'];upper=animations['UMSt'] if form=='wolf' else animations['UI_Default_Idle'];weights=next(w.node_weights for w in motion.weight_sets if w.name=='Upper');target_local=[n.parent.bind_matrix.inverted()@n.bind_matrix if n.parent else n.bind_matrix for n in model.nodes];source_local=[n.parent.bind_matrix.inverted()@n.bind_matrix if n.parent else n.bind_matrix for n in motion.nodes]
 rig.animation_data_create();action=bpy.data.actions.new('NativeReferenceIdle');action.use_fake_user=True;rig.animation_data.action=action
 for i,n in enumerate(model.nodes):
  a=upper if weights[i]>0 else lower;x=a.node_keyframe_transforms[i][0];bone=rig.pose.bones[n.name];bone.rotation_mode='QUATERNION';bone.rotation_quaternion=source_local[i].to_quaternion().inverted()@x.rotation;bone.location=target_local[i].to_3x3().inverted()@(x.location-source_local[i].to_translation()) if n.name=='Bip01' else Vector();bone.keyframe_insert('rotation_quaternion',frame=0);bone.keyframe_insert('location',frame=0)
 bpy.context.scene.frame_set(0);bpy.ops.file.pack_all();bpy.context.scene['status']='TEXTURED_NATIVE_REFERENCE_ONLY_NOT_FINAL_DESIGN';bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(form+'.blend')));bpy.ops.export_scene.gltf(filepath=str(OUT/(form+'.glb')),export_format='GLB',export_animations=True,export_extras=True)
 reports.append({'form':form,'native_nodes':len(model.nodes),'triangles_without_unequipped_tattoos':triangles,'piece_textures':mappings,'original_weights':True,'reference_only':True,'game_runtime_replaced':False})
( R/'docs/native-pair-review/textured-native-reference.json').write_text(json.dumps(reports,indent=2));print('TEXTURED_REFERENCES',json.dumps(reports))
