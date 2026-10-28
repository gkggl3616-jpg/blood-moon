"""Study 03: reference-timed FK acting -> Rokoko -> Rigify; staged only.
Execute in an open Blender scene (MCP execute-file), or Blender --python.
No runtime mesh is overwritten; MP4 poses are manually interpreted, not mocap.
"""
import bpy,addon_utils,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from rigify.metarigs.Basic import basic_human
R=Path('/workspace/rogue-blood-moon');D=R/'dist/roar-study-03';D.mkdir(parents=True,exist_ok=True)
REF=json.loads((R/'art/3d/animation-studies/reference_roar_38.json').read_text());END=51
addon_utils.enable('rigify',default_set=True,persistent=True)
addon_utils.enable('rokoko_studio_live',default_set=True,persistent=True)
if bpy.context.view_layer.objects.active and bpy.context.view_layer.objects.active.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.import_scene.gltf(filepath=str(R/'app/src/main/assets/models/bilge.glb'))
source=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');source.name='ReferenceActingSource'
source.animation_data_clear();rest={b.name:b.matrix_local.copy() for b in source.data.bones}
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Body_','Mouth_','Tattoo_','Accessory_'))];body=next(o for o in meshes if o.name.startswith('Body_'));h=2.25
bind=np.array([tuple(v.co) for v in body.data.vertices]);source_points={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in source.data.bones}
# Repaint original geometry using the corrected entire arm-chain classification.
# Keep disconnected fur on the local anatomical region; restrict garment from arms.
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
segments=[(n,np.array(a),np.array(b)) for n,(a,b) in source_points.items() if n!='Root']
for obj in meshes:
 xyz=np.array([tuple(v.co) for v in obj.data.vertices]);N=len(xyz)
 if not N:continue
 dist=np.zeros((N,len(segments)));x,y,z=xyz[:,0]/h,xyz[:,1]/h,xyz[:,2]/h
 # Continuous anatomical domains: the old hard x cutoff split adjacent skin
 # vertices between torso and forearm, producing 30x stretched triangles.
 domain=np.ones_like(dist)
 for j,(n,a,b) in enumerate(segments):
  ab=b-a;u=np.clip(((xyz-a)@ab)/np.dot(ab,ab),0,1);dist[:,j]=np.linalg.norm(xyz-a-u[:,None]*ab,axis=1)
  side=1 if n.endswith('L') else -1;ss='L' if side==1 else 'R'
  boundary=np.interp(z,[.25,.45,.55,.62,.73,.82,.90],[.25,.235,.22,.15,.13,.21,.30])
  arm=np.clip((abs(x)-boundary+.055)/.11,0,1);arm=arm*arm*(3-2*arm)
  leg=np.clip((.53-z)/.12,0,1);leg=leg*leg*(3-2*leg)
  if n=='Jaw':
   jaw=(abs(x)<.047)&(y<-.10)&(z>.815)&(z<.849);domain[:,j]=np.where(jaw,1,0)
  elif any(p in n.lower() for p in ['arm','hand','clavicle','digits']):
   domain[:,j]=arm*(x*side>0)
   if n.startswith('Clavicle'):domain[:,j]*=np.clip((z-.60)/.13,0,1)
   if n.startswith('Digits'):
    wrist,finger=source_points['Hand'+ss];axis=(finger-wrist).normalized();nearhand=np.linalg.norm(xyz-np.array(finger),axis=1);ahead=(xyz-np.array(finger))@np.array(axis)
    domain[:,j]*=np.clip((.11*h-nearhand)/(.045*h),0,1)*np.clip((ahead+.035*h)/(.04*h),0,1)
   if n.startswith('Hand'):domain[:,j]*=np.clip((source_points['Hand'+ss][0].z/h+.06-z)/.08,0,1)
  elif n.startswith(('Thigh','Shin','Foot')):domain[:,j]=leg*(x*side>=0)
  elif n.startswith('Tail'):domain[:,j]=0
  else:domain[:,j]=(1-arm)*(1-leg*.85)
 raw=domain/np.maximum(.025*h,dist)**3.5
 near=np.argsort(-raw,axis=1)[:,:6];weights=np.take_along_axis(raw,near,axis=1);weights/=np.maximum(weights.sum(axis=1,keepdims=True),1e-12)
 obj.vertex_groups.clear();groups=[obj.vertex_groups.new(name=n) for n,_,_ in segments];idx={g.name:g.index for g in groups}
 for i in range(N):
  co=Vector(xyz[i]);ss='L' if co.x>0 else 'R';sg=1 if co.x>0 else -1;wrist,finger=source_points['Hand'+ss];axis=(finger-wrist).normalized();along=(co-wrist).dot(axis);inner=max(.215,min(abs(wrist.x),abs(finger.x))/h-.055)
  entries=list(zip(near[i],weights[i]))
  total=sum(w for _,w in entries)
  for k,w in entries:
   if w>.00001:groups[int(k)].add([i],float(w/total),'REPLACE')
 if obj.get('skin_bone'):
  obj.vertex_groups.clear();g=obj.vertex_groups.new(name=obj['skin_bone']);g.add(list(range(N)),1,'REPLACE')
# Smooth weights across coincident and closely spaced disconnected skin facets.
# Do not weld/change source geometry or UV seams. Keep the full authoring field;
# export checks separately quantify any conversion into four game influences.
from mathutils.kdtree import KDTree
for obj in meshes:
 if not obj.name.startswith('Body_'):continue
 coords=[v.co.copy() for v in obj.data.vertices];treew=KDTree(len(coords))
 for i,co in enumerate(coords):treew.insert(co,i)
 treew.balance();ng=len(obj.vertex_groups);ww=np.zeros((len(coords),ng))
 for v in obj.data.vertices:
  for g in v.groups:ww[v.index,g.group]=g.weight
 neighbors=[[(idx,math.exp(-d*d/(2*.025**2))) for _,idx,d in treew.find_range(co,.055)] for co in coords]
 for _ in range(3):
  out=ww.copy()
  for i,nn in enumerate(neighbors):
   if nn:
    ids,fac=zip(*nn);fac=np.array(fac);out[i]=.25*ww[i]+.75*(ww[list(ids)]*fac[:,None]).sum(axis=0)/fac.sum()
  ww=out
 for g in obj.vertex_groups:g.remove(list(range(len(coords))))
 for i,row in enumerate(ww):
  for k in np.flatnonzero(row>1e-5):obj.vertex_groups[int(k)].add([i],float(row[k]),'REPLACE')
# Tattoo weights are barycentrically interpolated from the actual body surface.
body.data.calc_loop_triangles();tri=[tuple(t.vertices) for t in body.data.loop_triangles];tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],tri,all_triangles=True)
for obj in meshes:
 if not obj.name.startswith('Tattoo'):continue
 obj.vertex_groups.clear();groups={g.name:obj.vertex_groups.new(name=g.name) for g in body.vertex_groups}
 for v in obj.data.vertices:
  hit,_,face,_=tree.find_nearest(v.co)
  if hit is None:continue
  ids=tri[face];co=[body.data.vertices[i].co for i in ids];uvw=barycentric_transform(hit,*co,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)));ww={}
  for vi,f in zip(ids,uvw):
   for g in body.data.vertices[vi].groups:
    name=body.vertex_groups[g.group].name;ww[name]=ww.get(name,0)+g.weight*max(0,f)
  top=sorted(ww.items(),key=lambda q:-q[1])[:4];total=sum(w for _,w in top)
  for n,w in top:
   if w>1e-6:groups[n].add([v.index],w/total,'REPLACE')
# Build a source FK action with real timestamps (not a nine-pose recycled clip).
s=bpy.context.scene;s.render.fps=30;s.frame_start=0;s.frame_end=END
source.animation_data_create();act=bpy.data.actions.new('Reference38_ManualActing');source.animation_data.action=act
previous={}
def aim(n,v,twist=0):
 r=rest[n].to_3x3();out=(r@Vector((0,1,0))).rotation_difference(v.normalized()).to_matrix()@r
 return out@Matrix.Rotation(math.radians(twist),3,'Y')
for row in REF['samples']+[[39,1.7,*REF['samples'][-1][2:]]]:
 _,t,upper,fore,depth,palm,digits,chest,head,jaw,drop,_,_,phase=row;f=t*30;desired={};return_rest=smooth(.90,1.522,t)
 for b in source.data.bones:
  n=b.name;par=b.parent.name if b.parent else None;m=rest[n].copy() if not par else desired[par]@rest[par].inverted()@rest[n]
  if n=='Hips':m.translation.z-=drop
  pitch={'Spine':chest*.45,'Chest':chest,'Neck':head*.65,'Head':head}.get(n)
  if pitch is not None:m=Matrix.Translation(m.translation)@(Matrix.Rotation(math.radians(pitch),3,'X')@rest[n].to_3x3()).to_4x4()
  sg=1 if n.endswith('L') else -1
  if n.startswith(('UpperArm','Forearm','Hand')):
   elev=upper if n.startswith('UpperArm') else fore if n.startswith('Forearm') else fore-6
   if n.endswith('R') and t<.3:elev-=2
   a=math.radians(elev);v=Vector((sg*math.cos(a),depth if n.startswith('UpperArm') else -.08,math.sin(a)))
   mat=aim(n,v,sg*palm if n.startswith('Hand') else 0)
   # Recover to the approved bind-pose local orientation, preserving exact original arm lengths.
   inherited=m.to_quaternion();q=mat.to_quaternion().slerp(inherited,return_rest)
   m=Matrix.Translation(m.translation)@q.to_matrix().to_4x4()
  if n.startswith('Digits'):m=m@Matrix.Rotation(math.radians(-23*digits),4,'X')@Matrix.Rotation(math.radians((1 if 'Outer' in n else -1)*sg*8*digits),4,'Z')
  if n=='Jaw':m=m@Matrix.Rotation(.58*jaw,4,'X')
  desired[n]=m
 for b in source.data.bones:
  n=b.name;par=b.parent.name if b.parent else None;m=desired[n];basis=rest[n].inverted()@m if not par else rest[n].inverted()@rest[par]@desired[par].inverted()@m
  p=source.pose.bones[n];p.rotation_mode='QUATERNION';p.matrix_basis=basis
  if n in previous and p.rotation_quaternion.dot(previous[n])<0:p.rotation_quaternion.negate()
  previous[n]=p.rotation_quaternion.copy();p.keyframe_insert('rotation_quaternion',frame=f,group=n);p.keyframe_insert('location',frame=f,group=n)
for fc in act.fcurves:
 for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
# Build fitted Rigify from the original joint centers, retaining the complete neck chain.
bpy.ops.object.select_all(action='DESELECT');data=bpy.data.armatures.new('BilgeMetarigData');meta=bpy.data.objects.new('BilgeMetarig',data);s.collection.objects.link(meta);meta.select_set(True);bpy.context.view_layer.objects.active=meta
basic_human.create(meta);bpy.ops.object.mode_set(mode='EDIT');connected={b.name:b.use_connect for b in data.edit_bones}
for b in data.edit_bones:b.use_connect=False
sp=[source_points['Hips'][0],source_points['Spine'][0],source_points['Spine'][0].lerp(source_points['Chest'][0],.5),source_points['Chest'][0],source_points['Neck'][0],source_points['Neck'][0].lerp(source_points['Head'][0],.5),source_points['Head'][0],source_points['Head'][1]]
for i in range(7):
 b=data.edit_bones['spine'+(f'.{i:03}' if i else '')];b.head=sp[i];b.tail=sp[i+1];b.roll=0
for side in ['L','R']:
 for name,src in [('shoulder','Clavicle'),('upper_arm','UpperArm'),('forearm','Forearm'),('hand','Hand'),('thigh','Thigh'),('shin','Shin'),('foot','Foot')]:
  b=data.edit_bones[name+'.'+side];b.head,b.tail=source_points[src+side];b.align_roll(Vector((0,0,1)) if name in ['shoulder','upper_arm','forearm','hand'] else Vector((0,-1,0)))
 b=data.edit_bones['toe.'+side];b.head=source_points['Foot'+side][1];b.tail=b.head+Vector((0,-.10,0))
 b=data.edit_bones['heel.02.'+side];b.head=source_points['Foot'+side][1]+Vector((-.07,.18,0));b.tail=b.head+Vector((.14,0,0))
 for n in ['pelvis','breast']:
  b=data.edit_bones[n+'.'+side];b.head=sp[0] if n=='pelvis' else sp[3];b.tail=b.head+Vector((.14 if side=='L' else -.14,-.08,.08 if n=='pelvis' else 0))
for b in data.edit_bones:b.use_connect=connected.get(b.name,False)
extra={'jaw':('Jaw','spine.006')}
for side in ['L','R']:
 for label in ['Inner','Outer']:extra['digits_'+label.lower()+'.'+side]=('Digits'+label+side,'hand.'+side)
for name,(src,par) in extra.items():
 b=data.edit_bones.new(name);b.head,b.tail=source_points[src];b.parent=data.edit_bones[par];b.roll=source.data.bones[src].matrix_local.to_3x3().to_euler().y
bpy.ops.object.mode_set(mode='OBJECT')
for name in extra:
 p=meta.pose.bones[name];p.rigify_type='basic.super_copy';p.rigify_parameters.make_control=True;p.rigify_parameters.make_deform=True
for side in ['L','R']:
 for n in ['upper_arm','thigh']:
  p=meta.pose.bones[n+'.'+side];p.rigify_parameters.segments=2;p.rigify_parameters.bbones=1
bpy.ops.pose.rigify_generate();rig=bpy.context.view_layer.objects.active;rig.name='BilgeRigify';assert rig.name=='BilgeRigify'
for b in rig.data.bones:b.bbone_segments=1
for side in ['L','R']:
 rig.pose.bones['upper_arm_parent.'+side]['IK_FK']=1.0;rig.pose.bones['upper_arm_parent.'+side]['IK_Stretch']=0.0
 rig.pose.bones['thigh_parent.'+side]['IK_FK']=0.0;rig.pose.bones['thigh_parent.'+side]['IK_Stretch']=0.0
rig.pose.bones['torso']['head_follow']=1.0;rig.pose.bones['torso']['neck_follow']=1.0
# Map skin weights onto real ordinary segmented deform bones (B-Bone segments=1).
base_map={'Hips':'spine','Spine':'spine.001','Chest':'spine.003','Neck':'spine.004','Head':'spine.006','Jaw':'jaw','Tail':'spine','TailTip':'spine'}
for side in ['L','R']:
 for src,tgt in [('Clavicle','shoulder'),('UpperArm','upper_arm'),('Forearm','forearm'),('Hand','hand'),('Thigh','thigh'),('Shin','shin'),('Foot','foot')]:base_map[src+side]=tgt+'.'+side
 for label in ['Inner','Outer']:base_map['Digits'+label+side]='digits_'+label.lower()+'.'+side
for obj in meshes:
 original={g.index:g.name for g in obj.vertex_groups};old_weights=[[(original[g.group],g.weight) for g in v.groups] for v in obj.data.vertices]
 obj.vertex_groups.clear();groups={b.name:obj.vertex_groups.new(name=b.name) for b in rig.data.bones if b.use_deform}
 for v,ww in zip(obj.data.vertices,old_weights):
  out={}
  for n,w in ww:
   target='DEF-'+base_map.get(n,'spine');parts=[(target,1)]
   if n.startswith(('UpperArm','Forearm','Thigh','Shin')):
    a,b=source_points[n];axis=b-a;u=(v.co-a).dot(axis)/axis.length_squared;fac=smooth(.15,.85,u);parts=[(target,1-fac),(target[:-2]+'.'+target[-1]+'.001',fac)]
   if n=='Neck':
    a,b=source_points[n];u=(v.co-a).dot(b-a)/(b-a).length_squared;fac=smooth(.1,.9,u);parts=[('DEF-spine.004',1-fac),('DEF-spine.005',fac)]
   for dst,factor in parts:
    if dst in groups:out[dst]=out.get(dst,0)+w*factor
  total=sum(out.values())
  for n,w in out.items():
   if w>1e-6:groups[n].add([v.index],w/total,'REPLACE')
 for mod in list(obj.modifiers):
  if mod.type=='ARMATURE':obj.modifiers.remove(mod)
 mod=obj.modifiers.new('BilgeRigifySkin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False
 matrix=obj.matrix_world.copy();obj.parent=rig;obj.matrix_world=matrix
# Reload the local Rokoko custom-map KeyError fix before retargeting.
import importlib
from rokoko_studio_live.core import custom_schemes_manager
importlib.reload(custom_schemes_manager)
# Actual Rokoko retarget operation into Rigify FK controls.
mapping={'Root':'root','Hips':'spine_fk','Spine':'spine_fk.002','Chest':'spine_fk.003','Neck':'neck','Head':'head','Jaw':'jaw'}
for side in ['L','R']:
 for src,tgt in [('Clavicle','shoulder'),('UpperArm','upper_arm_fk'),('Forearm','forearm_fk'),('Hand','hand_fk')]:mapping[src+side]=tgt+'.'+side
 for label in ['Inner','Outer']:mapping['Digits'+label+side]='digits_'+label.lower()+'.'+side
s.rsl_retargeting_armature_source=source;s.rsl_retargeting_armature_target=rig;s.rsl_retargeting_auto_scaling=False;s.rsl_retargeting_use_pose='REST';s.rsl_retargeting_bone_list.clear()
for src,tgt in mapping.items():
 item=s.rsl_retargeting_bone_list.add();item.bone_name_source=src;item.bone_name_target=tgt
result=bpy.ops.rsl.retarget_animation();assert 'FINISHED' in result,result
rig.animation_data.action.name='BilgeRoar03_RokokoRigify'
# Plant the feet through Rigify leg IK. Torso receives only the observed vertical settle.
for row in REF['samples']+[[39,1.7,*REF['samples'][-1][2:]]]:
 t=row[1];drop=row[10];p=rig.pose.bones['torso'];p.location.z=-drop;p.keyframe_insert('location',frame=t*30,group='torso')
source.hide_render=True;source.hide_set(True);meta.hide_render=True;meta.hide_set(True)
# Hide source authoring accessory decals until corresponding gameplay slot is equipped.
for obj in meshes:
 if obj.name.startswith('Accessory_'):obj.hide_render=True
 for mat in obj.data.materials:
  if mat and mat.use_nodes:
   bs=mat.node_tree.nodes.get('Principled BSDF')
   if bs:bs.inputs['Emission Strength'].default_value=0
# Neutral stage, soft real contact shadows, equivalent reference camera.
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.cycles.device='CPU';s.world.color=(.045,.055,.075)
mat=bpy.data.materials.new('ReviewGround');mat.diffuse_color=(.075,.095,.12,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.014));floor=bpy.context.object;floor.name='ReviewFloor';floor.data.materials.append(mat)
for co,power,size in [((3,-4,5),750,4),((-3,1,4),500,4),((0,5,5),550,3)]:
 bpy.ops.object.light_add(type='AREA',location=co);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='ReviewCamera';s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=3.05;cam.location=(-3,5,4.4);cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=480;s.render.resolution_y=600;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
s.frame_set(8);bpy.context.view_layer.update()
assert np.max(abs(bind-np.array([tuple(v.co) for v in body.data.vertices])))==0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-03.blend'),compress=True)
report={'retarget_result':list(result),'mapped_bones':mapping,'rig_total_bones':len(rig.data.bones),'deform_bones':sum(b.use_deform for b in rig.data.bones),'reference_frames':38,'duration_s':END/30,'mesh_bind_max_delta':0,'arm_IK_stretch':0,'skin':'Linear ordinary segmented bones; no preserve-volume dependency','runtime_replaced':False,'paid_credits':0,'visual_approval':'PENDING'}
(D/'rig-build.json').write_text(json.dumps(report,indent=2));print('STUDY03_RIG_CREATED',json.dumps(report))
