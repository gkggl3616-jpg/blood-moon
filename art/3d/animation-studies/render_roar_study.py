"""Render the complete actual study action, 30fps; no screen-capture time warp."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];STUDY='02' if '--study02' in sys.argv else '01';END=51 if STUDY=='02' else 36;OUT=R/('dist/roar-study-'+STUDY)
bpy.ops.wm.open_mainfile(filepath=str(R/('art/3d/animation-studies/bilge-roar-study-'+STUDY+'.blend')))
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');cam=s.camera;s.cycles.samples=6
views={'reference':(-3,5,4.4),'front':(0,-6,2),'side':(6,0,2)}
feet={side:rig.data.bones['Foot'+side].head_local.copy() for side in ['L','R']};errors=[]
for f in range(END+1):
 s.frame_set(f)
 errors.append(max((rig.pose.bones['Foot'+side].head-feet[side]).length for side in feet))
body=next(o for o in s.objects if o.name.startswith('Body_'));armids={g.index for g in body.vertex_groups if any(x in g.name.lower() for x in ['arm','hand','digits','clavicle'])}
leaks=[sum(g.weight for g in v.groups if g.group in armids) for v in body.data.vertices if abs(v.co.x)<.175*2.25 and .24*2.25<v.co.z<.57*2.25]
s.frame_set(0);jaw0=(rig.data.bones['Head'].matrix_local@rig.pose.bones['Head'].matrix.inverted()@rig.pose.bones['Jaw'].tail).z
s.frame_set(8 if STUDY=='02' else 17);jaw1=(rig.data.bones['Head'].matrix_local@rig.pose.bones['Head'].matrix.inverted()@rig.pose.bones['Jaw'].tail).z
assert jaw0-jaw1>.04,('jaw must open downward',jaw0,jaw1)
report={'jaw_tip_opening_down_m':jaw0-jaw1,'action':rig.animation_data.action.name,'duration_s':END/30,'fps':30,'unique_frames':END+1,'max_sampled_ankle_drift_m':max(errors),'garment_all_arm_chain_weight_max':max(leaks),'runtime_assets_modified':False,'visual_approval':'PENDING','physical_device_tested':False}
assert max(leaks)<.0001
assert max(errors)<.025,errors
(OUT/'study-audit.json').write_text(json.dumps(report,indent=2))
for name,location in views.items():
 folder=OUT/name;folder.mkdir(exist_ok=True);cam.location=location;cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
 for f in range(END+1):
  s.frame_set(f);s.render.filepath=str(folder/f'{f:03}.png');bpy.ops.render.render(write_still=True)
print('RENDER_COMPLETE',json.dumps(report))
