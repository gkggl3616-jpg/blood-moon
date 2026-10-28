"""Render diagnostic poses or complete 52-frame, 30fps study from saved .blend."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];D=R/'dist/roar-study-03';bpy.ops.wm.open_mainfile(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-03.blend'))
s=bpy.context.scene;cam=s.camera;rig=bpy.data.objects['BilgeRigify'];body=bpy.data.objects['Body_bilge'];s.cycles.samples=12;s.cycles.use_denoising=False
views={'reference':(-3,5,4.4),'front':(0,-6,2.1),'side':(6,0,2.1)}
cam.data.ortho_scale=3.05;s.render.resolution_x=420;s.render.resolution_y=520
if '--stills' in sys.argv:frames=[0,8,20,27,38,51]
else:frames=list(range(52))
if '--reference-only' in sys.argv:views={k:v for k,v in views.items() if k=='reference'}
report=[];positions={};bone_report=[]
for f in range(52):
 s.frame_set(f);bpy.context.view_layer.update();bones=rig.pose.bones
 if f==0:positions={n:bones[n].head.copy() for n in ['DEF-foot.L','DEF-foot.R']}
 bone_report.append({'frame':f,'feet_drift':max((bones[n].head-p).length for n,p in positions.items()),'arm_lengths':{n:(bones[n].tail-bones[n].head).length for n in ['ORG-upper_arm.L','ORG-forearm.L','ORG-upper_arm.R','ORG-forearm.R']}})
 if f in frames:
  ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();report.append({'frame':f,'min_z':min(v.co.z for v in m.vertices),'max_z':max(v.co.z for v in m.vertices),'max_abs_x':max(abs(v.co.x) for v in m.vertices)});ev.to_mesh_clear()
(D/'pose-audit.json').write_text(json.dumps({'frames':report,'bones':bone_report,'max_foot_drift':max(r['feet_drift'] for r in bone_report),'visual_approval':'PENDING','runtime_assets_replaced':False},indent=2))
if '--audit-only' in sys.argv:
 print('AUDIT03_COMPLETE');raise SystemExit
for name,loc in views.items():
 cam.location=loc;cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler();folder=D/name;folder.mkdir(exist_ok=True)
 for f in frames:
  s.frame_set(f);s.render.filepath=str(folder/f'{f:03}.png');bpy.ops.render.render(write_still=True)
print('RENDER03_COMPLETE')
