"""Reimport the exported game GLB and compare sampled skin positions to the baked rig."""
import bpy,json,numpy as np
from pathlib import Path
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[3];D=R/'dist/roar-study-03';expected=np.load(D/'export-expected.npz')
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-03.glb'))
body=next(o for o in bpy.context.scene.objects if o.name=='Study03_Body_bilge');rig=next(m.object for m in body.modifiers if m.type=='ARMATURE')
for tr in rig.animation_data.nla_tracks:tr.mute=True
act=rig.animation_data.action or next(a for a in bpy.data.actions if 'WolfRoar' in a.name);rig.animation_data.action=act
kd=KDTree(len(expected['bind']))
for i,v in enumerate(expected['bind']):kd.insert(v,i)
kd.balance();mapping=[kd.find(v.co)[1] for v in body.data.vertices];s=bpy.context.scene;s.render.fps=30;results=[]
for f in [0,4,8,14,20,24,27,32,38,44,51]:
 s.frame_set(f);bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();co=np.array([tuple(v.co) for v in me.vertices]);err=np.linalg.norm(co-expected[str(f)][mapping],axis=1);ev.to_mesh_clear();results.append({'frame':f,'max_error_m':float(err.max()),'mean_error_m':float(err.mean())})
report={'mesh':'Body_bilge','source':'Rigify 40-joint bake','imported_vertices':len(mapping),'frames':results,'max_error_m':max(x['max_error_m'] for x in results)}
(D/'roundtrip-audit.json').write_text(json.dumps(report,indent=2));print('ROUNDTRIP',report);assert report['max_error_m']<.002,report
