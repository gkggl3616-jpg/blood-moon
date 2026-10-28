"""Bake only ordinary deform bones and verify linear-skin parity before GLB export."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
import numpy as np
R=Path(__file__).resolve().parents[3];D=R/'dist/roar-study-03';bpy.ops.wm.open_mainfile(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-03.blend'))
s=bpy.context.scene;rig=bpy.data.objects['BilgeRigify'];originals=[o for o in s.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers) and not o.hide_render and o.name.startswith(('Body_','Mouth_','Tattoo_'))]
names=[b.name for b in rig.data.bones if b.use_deform];data=bpy.data.armatures.new('BilgeRoarExportSkin');out=bpy.data.objects.new('BilgeRoarExport',data);s.collection.objects.link(out);bpy.ops.object.select_all(action='DESELECT');out.select_set(True);bpy.context.view_layer.objects.active=out;bpy.ops.object.mode_set(mode='EDIT')
for n in names:
 src=rig.data.bones[n];b=data.edit_bones.new(n);b.head=src.head_local;b.tail=src.tail_local;b.matrix=src.matrix_local.copy();b.length=src.length;b.use_deform=True
# Flat export joints preserve the evaluated Rigify matrices without inherited shear.
bpy.ops.object.mode_set(mode='OBJECT');out.animation_data_create();out.animation_data.action=bpy.data.actions.new('WolfRoar')
last={}
for f in range(52):
 s.frame_set(f);bpy.context.view_layer.update()
 for b in out.data.bones:
  p=out.pose.bones[b.name];p.rotation_mode='QUATERNION';mat=rig.pose.bones[b.name].matrix.copy();par=b.parent
  basis=b.matrix_local.inverted()@mat if not par else b.matrix_local.inverted()@par.matrix_local@rig.pose.bones[par.name].matrix.inverted()@mat
  p.matrix_basis=basis
  if b.name in last and p.rotation_quaternion.dot(last[b.name])<0:p.rotation_quaternion.negate()
  last[b.name]=p.rotation_quaternion.copy()
  for prop in ['location','rotation_quaternion','scale']:p.keyframe_insert(prop,frame=f,group=b.name)
for fc in out.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
copies=[]
for obj in originals:
 cp=obj.copy();cp.data=obj.data.copy();s.collection.objects.link(cp);world=obj.matrix_world.copy();cp.parent=out;cp.matrix_world=world
 for mod in cp.modifiers:
  if mod.type=='ARMATURE':mod.object=out;mod.use_deform_preserve_volume=False
 cp.name='Study03_'+obj.name;copies.append((obj,cp))
errors=[];expected={}
for f in [0,4,8,14,20,24,27,32,38,44,51]:
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for a,b in copies:
  ea=a.evaluated_get(dg);eb=b.evaluated_get(dg);ma=ea.to_mesh();mb=eb.to_mesh();ca=np.array([tuple(v.co) for v in ma.vertices]);cb=np.array([tuple(v.co) for v in mb.vertices]);err=float(np.max(np.linalg.norm(ca-cb,axis=1)));errors.append({'frame':f,'mesh':a.name,'max_vertex_error_m':err})
  if a.name=='Body_bilge':expected[str(f)]=ca
  ea.to_mesh_clear();eb.to_mesh_clear()
assert max(x['max_vertex_error_m'] for x in errors)<.001,errors
expected['bind']=np.array([tuple(v.co) for v in bpy.data.objects['Body_bilge'].data.vertices]);np.savez_compressed(D/'export-expected.npz',**expected)
bpy.ops.object.select_all(action='DESELECT');out.select_set(True)
for _,cp in copies:cp.select_set(True)
bpy.context.view_layer.objects.active=out;s.frame_set(0)
for old_action in list(bpy.data.actions):
 if old_action!=out.animation_data.action:bpy.data.actions.remove(old_action)
bpy.ops.export_scene.gltf(filepath=str(D/'bilge-roar-study-03.glb'),export_format='GLB',use_selection=True,export_animations=True,export_nla_strips=False,export_force_sampling=True,export_extras=True)
(D/'export-audit.json').write_text(json.dumps({'deform_bones':len(names),'comparison':errors,'max_vertex_error_m':max(x['max_vertex_error_m'] for x in errors),'ordinary_linear_skin':True,'file':'bilge-roar-study-03.glb','runtime_replaced':False},indent=2));print('EXPORT03_COMPLETE',max(x['max_vertex_error_m'] for x in errors))
