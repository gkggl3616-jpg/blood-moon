"""Check delivered deformed assets: source fidelity, contacts, overhead roar.
Not a visual similarity score. Run in Blender, after animate_wolves.py.
"""
import bpy,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[3];meta=json.loads((R/'art/3d/model-report.json').read_text());results=[]
for profile in meta['variants']:
 if profile.get('kind')=='human':continue
 key=profile['id'];h=profile['height_m'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(R/meta['static_source_dir']/(key+'.glb')));source=next(o for o in bpy.context.scene.objects if o.name.startswith('Body_'));points=[source.matrix_world@v.co for v in source.data.vertices];source_tri=sum(len(p.vertices)-2 for p in source.data.polygons);tree=KDTree(len(points))
 for i,point in enumerate(points):tree.insert(point,i)
 tree.balance();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'app/src/main/assets/models'/(key+'.glb')))
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=next(o for o in bpy.context.scene.objects if o.name.startswith('Body_'));tracks=list(rig.animation_data.nla_tracks)
 for t in tracks:t.mute=True
 def pose(name,t):
  rig.animation_data.action=next(tr.strips[0].action for tr in tracks if tr.name==name);lo,hi=rig.animation_data.action.frame_range;f=lo+(hi-lo)*t;bpy.context.scene.frame_set(int(f),subframe=f%1)
 def verts():
  ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();xyz=np.array([tuple(ev.matrix_world@v.co) for v in me.vertices]);ev.to_mesh_clear();return xyz
 pose('WolfIdle',0);source_error=max(tree.find(Vector(v))[2] for v in verts());assert source_error<3e-5,(key,'source shape changed',source_error);assert source_tri==sum(len(p.vertices)-2 for p in body.data.polygons)
 names={g.name:g.index for g in body.vertex_groups};weights=np.zeros((len(body.data.vertices),len(names)))
 for v in body.data.vertices:
  for g in v.groups:weights[v.index,g.group]=g.weight
 # Clothing may bend with hips/legs but must never be dragged up by a hand.
 garment=np.array([abs(v.co.x)<.19*h and .28*h<v.co.z<.57*h for v in body.data.vertices]);armcols=[i for name,i in names.items() if name.startswith(('Hand','Digits'))]
 contamination=float(weights[garment][:,armcols].sum(axis=1).max(initial=0));assert contamination<.02,(key,'garment attached to hands',contamination)
 contacts={};stride=rig.get('run_stride_m',8*16/30)
 for side,delay in [('L',0),('R',.085)]:
  for family,bone,stance,offset in [('front','Hand',.18,delay),('rear','Foot',.20,delay+.49)]:
   cols=[i for name,i in names.items() if name==bone+side or family=='front' and name.startswith('Digits') and name.endswith(side)]
   mask=weights[:,cols].sum(axis=1)>(.65 if family=='front' else .45);zs=[];ys=[];length_errors=[]
   phases=[.035,.075,.115,.155] if family=='front' else [.035,.08,.125,.17]
   for u in phases:
    t=(u-offset)%1;pose('WolfRunQuad',t);xyz=verts();zs.append(float(xyz[mask,2].min()));ys.append(float(rig.pose.bones[bone+side].head.y-stride*t))
   # Unwrap the virtual root at the periodic boundary.
   for i in range(1,len(ys)):
    while ys[i]-ys[i-1]>stride*.5:ys[i]-=stride
    while ys[i]-ys[i-1]<-stride*.5:ys[i]+=stride
   drift=max(ys)-min(ys);contacts[family+side]={'sole_min_m':min(zs),'sole_max_m':max(zs),'support_drift_m':drift}
   assert drift<.045,(key,family+side,'support slides',contacts[family+side])
   assert min(zs)>-.035 and max(zs)<.065,(key,family+side,'sole not near ground',contacts[family+side])
 # All five torso links as well as limbs retain their actual bind lengths.
 stretch=[]
 for t in [i/32 for i in range(33)]:
  pose('WolfRunQuad',t)
  for a,b in [('Hips','Spine'),('Spine','Chest'),('Chest','Neck'),('Neck','Head')]+[(a+s,b+s) for s in ['L','R'] for a,b in [('UpperArm','Forearm'),('Forearm','Hand'),('Thigh','Shin'),('Shin','Foot')]]:
   rest=(rig.data.bones[b].head_local-rig.data.bones[a].head_local).length;now=(rig.pose.bones[b].head-rig.pose.bones[a].head).length;stretch.append(abs(now/rest-1))
 assert max(stretch)<.01,(key,'trunk or limb stretched',max(stretch))
 pose('WolfRoar',.56);overhead=min(rig.pose.bones['Hand'+s].head.z-rig.pose.bones['Head'].head.z for s in ['L','R']);assert overhead>.035*h,(key,'hands do not reach above head',overhead)
 digits=[rig.pose.bones['Digits'+label+s].rotation_quaternion.angle for s in ['L','R'] for label in ['Inner','Outer']];assert min(digits)>.08,(key,'digits not animated',digits)
 pose('WolfRoar',0);jaw0=rig.pose.bones['Jaw'].rotation_quaternion.copy();pose('WolfRoar',.56);jaw=jaw0.rotation_difference(rig.pose.bones['Jaw'].rotation_quaternion).angle;assert jaw>.35
 oral=sum(o.name.startswith('Mouth_') and o.type=='MESH' for o in bpy.context.scene.objects);assert oral>=2,(key,'missing mouth geometry')
 result={'id':key,'approved_body_error_m':source_error,'body_triangles':source_tri,'bone_count':len(rig.data.bones),'garment_hand_weight_max':contamination,'contacts':contacts,'max_segment_length_error':max(stretch),'hands_above_head_m':overhead,'jaw_rotation_rad':jaw,'oral_parts':oral};results.append(result);print('REFERENCE_MOTION',json.dumps(result),flush=True)
(R/'dist/reference-motion-verification.json').write_text(json.dumps(results,indent=2));print('PASS: actual contacts, preserved sources, fixed trunk/limbs, overhead hands, digits and jaws for all wolves.')
