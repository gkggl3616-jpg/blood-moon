"""Render source bind poses only. Do not sample, edit or retarget animations."""
import bpy,sys,types,importlib,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
plan=json.loads((R/'docs/four-character-rigs/selection.json').read_text());O=R/'docs/four-character-rigs';WORK=R/'art/3d/source/four-rig-bind-references';WORK.mkdir(exist_ok=True);records=[]
for item in plan['characters']:
 bpy.ops.wm.read_factory_settings(use_empty=True);m=Reader().from_file(str(R/item['source']));arm=bpy.data.armatures.new('OriginalSkeleton');rig=bpy.data.objects.new('OriginalSkeleton',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in m.nodes:
  b=arm.edit_bones.new(n.name);b.head=(0,0,0);b.tail=(0,2,0);b.matrix=n.bind_matrix
  if n.parent:b.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT')
 pts=[v.location for p in m.pieces if not p.name.lower().startswith('tattoo') for v in p.lods[0].vertices];low=min(v.y for v in pts);scale=2.4/(max(v.y for v in pts)-low);rig.matrix_world=Matrix(((-scale,0,0,0),(0,0,scale,0),(0,scale,0,-low*scale),(0,0,0,1)))
 material=bpy.data.materials.new('NeutralGeometryComparison');material.use_nodes=True;material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.24,.29,.33,1);material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.88
 for piece in m.pieces:
  if piece.name.lower().startswith('tattoo'):continue
  lod=piece.lods[0];data=bpy.data.meshes.new(piece.name);data.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new(piece.name,data);bpy.context.collection.objects.link(obj);obj.parent=rig;data.materials.append(material)
  for poly in data.polygons:poly.use_smooth=True
  for index,n in enumerate(m.nodes):
   group=obj.vertex_groups.new(name=n.name)
   for vi,v in enumerate(lod.vertices):
    for w in v.weights:
     if w.node_index==index:group.add([vi],w.bias,'REPLACE')
  mod=obj.modifiers.new('OriginalSkin','ARMATURE');mod.object=rig
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=720;s.world=bpy.data.worlds.new('World');s.world.color=(.04,.04,.04);s['purpose']='STATIC_BIND_REFERENCE_NOT_FINAL_CHARACTER';s['animations_locked']=True;center=Vector((0,0,1.2))
 bpy.ops.mesh.primitive_plane_add(size=100);floor=bpy.context.object;mat=bpy.data.materials.new('Floor');mat.diffuse_color=(.045,.055,.065,1);floor.data.materials.append(mat)
 for loc,energy in [((3,-4,5),850),((-3,0,3),600)]:
  bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=energy;light.data.size=4;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();camera=bpy.context.object;s.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=3.0
 for label,loc in [('front',(0,-5,1.5)),('three',(3,-5,2.3))]:
  camera.location=Vector(loc);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(item['id']+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
 assert not bpy.data.actions
 bpy.ops.wm.save_as_mainfile(filepath=str(WORK/(item['id']+'.blend')));records.append({'character':item['id'],'bones':len(m.nodes),'reference_only':True,'animations_created_or_edited':False})
for name,info in plan['frozen_source_files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==info['sha256'],name
(O/'preview-check.json').write_text(json.dumps({'models':records,'all_frozen_source_hashes_match':True,'runtime_changed':False},indent=2));print('FROZEN_SOURCE_HASHES_PASS')
