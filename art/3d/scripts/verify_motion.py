"""Inspect exported GLB deformations, loop seams and limb reach in Blender.
Run: blender -b -t 2 --python art/3d/scripts/verify_motion.py
"""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
results=[]
for key in ['bilge','kultigin','alparslan','konuralp']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.scene.render.fps=30
 bpy.ops.import_scene.gltf(filepath=str(ROOT/'app/src/main/assets/models'/f'{key}.glb'))
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
 body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Body_'))
 tracks=list(rig.animation_data.nla_tracks)
 for track in tracks:track.mute=True
 record={'id':key,'clips':{}}
 for kind in ['WolfIdle','WolfMove','WolfRunQuad','WolfRoll','WolfRoar']:
  track=next(t for t in tracks if t.name==kind);action=track.strips[0].action;rig.animation_data.action=action
  lo,hi=action.frame_range;heights=[];floors=[];reach_errors=[];ends=[]
  for fraction in [i/24 for i in range(25)]:
   frame=lo+(hi-lo)*fraction;bpy.context.scene.frame_set(math.floor(frame),subframe=frame%1)
   deps=bpy.context.evaluated_depsgraph_get();evaluated=body.evaluated_get(deps);mesh=evaluated.to_mesh()
   zs=[(evaluated.matrix_world@v.co).z for v in mesh.vertices];heights.append(max(zs));floors.append(min(zs));evaluated.to_mesh_clear()
   sample={}
   for side in ['L','R']:
    for parent,child in [('UpperArm','Forearm'),('Forearm','Hand'),('Thigh','Shin'),('Shin','Foot')]:
     a=parent+side;b=child+side
     rest=(rig.data.bones[b].matrix_local.translation-rig.data.bones[a].matrix_local.translation).length
     now=(rig.pose.bones[b].head-rig.pose.bones[a].head).length
     reach_errors.append(abs(now-rest)/rest)
    for part in ['Hand','Foot']:sample[part+side]=rig.pose.bones[part+side].head.copy()
   if fraction in [0,1]:ends.append(sample)
  assert max(heights)<3.25,(key,kind,'body shot upward',max(heights))
  assert min(floors)>(-.04 if kind=='WolfRunQuad' else -.24),(key,kind,'body penetrated floor',min(floors))
  assert max(reach_errors)<.055,(key,kind,'limb reach changed',max(reach_errors))
  seam=max((ends[0][n]-ends[1][n]).length for n in ends[0])
  if kind in ['WolfIdle','WolfMove','WolfRunQuad']:assert seam<.008,(key,kind,'loop seam',seam)
  record['clips'][kind]={'min_z':round(min(floors),4),'max_z':round(max(heights),4),'max_limb_error':round(max(reach_errors),5),'loop_seam_m':round(seam,5)}
 results.append(record)
 print('MOTION_CHECK_PASS',key,flush=True)
(ROOT/'dist/motion-verification.json').write_text(json.dumps(results,indent=2))
print('PASS: exported mesh bounds, limb reach and looping clips for all four wolves.',flush=True)
