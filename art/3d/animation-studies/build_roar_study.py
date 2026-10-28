"""Editable Bilge FK acting study; does not overwrite runtime GLBs or APK.
Run with Blender. Individually authored rotation poses; foot targets alone use IK.
"""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).resolve().parents[3];OUT=R/'dist/roar-study-01';OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'app/src/main/assets/models/bilge.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
for t in rig.animation_data.nla_tracks:t.mute=True
rig.animation_data.action=None
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
# Paint the garment/hip region independently of all arm bones. Previous checks
# excluded Hands/Digits only and missed Forearm leakage into the waist cloth.
body=next(o for o in bpy.context.scene.objects if o.name.startswith('Body_'))
armgroups={g.index:g for g in body.vertex_groups if any(x in g.name.lower() for x in ['arm','hand','digits','clavicle'])}
painted=[]
for v in body.data.vertices:
 x,z=abs(v.co.x)/2.25,v.co.z/2.25
 if not (x<.175 and .24<z<.57):continue
 armweight=sum(g.weight for g in v.groups if g.group in armgroups)
 if armweight<.00001:continue
 remaining=[(g.group,g.weight) for g in v.groups if g.group not in armgroups];total=sum(w for _,w in remaining)
 for group in armgroups.values():group.remove([v.index])
 if total>0:
  for i,w in remaining:body.vertex_groups[i].add([v.index],w/total,'REPLACE')
 else:body.vertex_groups['Hips'].add([v.index],1,'REPLACE')
 painted.append({'vertex':v.index,'removed_arm_weight':armweight})
(OUT/'weight-paint.json').write_text(json.dumps({'vertices_corrected':len(painted),'max_removed_arm_weight':max((v['removed_arm_weight'] for v in painted),default=0),'region':'waist/skirt/upper thigh, excluding the source hands','entries':painted},indent=2))

# frame, pelvis drop m, lumbar/chest/neck/head global pitch, upper-arm elevation,
# forearm elevation, arm depth, palm tilt, finger opening, jaw opening.
# Elevations are anatomical FK directions. No hand-height goals, no arm IK.
KEYS=[
 (0,0,0,0,0,0,None,None,0,0,0,0),
 (5,.065,10,14,8,5,-48,-74,-.12,-18,0,.05),
 (9,.040,7,8,2,-2,-12,18,-.12,-4,.15,.14),
 (13,.010,-4,-8,-18,-20,28,108,.04,10,.75,.78),
 (17,0,-7,-14,-28,-34,38,120,.10,18,1,1),
 (22,.005,-6,-12,-26,-30,36,117,.08,15,.95,.94),
 (27,.015,2,4,-8,-12,3,63,-.03,0,.55,.45),
 (32,.018,3,4,2,0,-45,-37,-.10,-10,.08,.05),
 (36,0,0,0,0,0,None,None,0,0,0,0)]
scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=0;scene.frame_end=36
act=bpy.data.actions.new('BilgeRoarStudy01_FK');rig.animation_data.action=act

def rotation(name,direction,twist=0):
 r=rest[name].to_3x3();v=r@Vector((0,1,0));m=v.rotation_difference(direction.normalized()).to_matrix()@r
 return m@Matrix.Rotation(math.radians(twist),3,'Y')

def ik(a,b,pole,l1,l2):
 d=b-a;length=min(l1+l2-.00001,max(abs(l1-l2)+.00001,d.length));axis=d.normalized();along=(l1*l1-l2*l2+length*length)/(2*length)
 ortho=pole-a-axis*(pole-a).dot(axis);ortho.normalize();return a+axis*along+ortho*math.sqrt(max(0,l1*l1-along*along))

previous={}
for row in KEYS:
 frame,drop,lumbar,chest,neck,head,upper,fore,depth,palm,digits,jaw=row
 desired={}
 for b in rig.data.bones:
  name=b.name;parent=b.parent.name if b.parent else None
  mat=rest[name].copy() if parent is None else desired[parent]@rest[parent].inverted()@rest[name]
  if name=='Hips':mat.translation.z-=drop
  pitch={'Spine':lumbar,'Chest':chest,'Neck':neck,'Head':head}.get(name)
  if pitch is not None:mat=Matrix.Translation(mat.translation)@(Matrix.Rotation(math.radians(pitch),3,'X')@rest[name].to_3x3()).to_4x4()
  side=name[-1];sg=1 if side=='L' else -1
  if upper is not None:
   if name.startswith('UpperArm'):
    a=math.radians(upper+(1 if side=='R' and frame<17 else 0));direction=Vector((sg*math.cos(a),depth,math.sin(a)));mat=Matrix.Translation(mat.translation)@rotation(name,direction).to_4x4()
   if name.startswith('Forearm'):
    a=math.radians(fore+(-3 if side=='R' and frame<17 else 0));direction=Vector((sg*math.cos(a),-.04,math.sin(a)));mat=Matrix.Translation(mat.translation)@rotation(name,direction).to_4x4()
   if name.startswith('Hand'):
    # Palm/claws unfurl only after the elbow has led the rising arc.
    a=math.radians(fore-18);direction=Vector((sg*math.cos(a),-.18,math.sin(a)));mat=Matrix.Translation(mat.translation)@rotation(name,direction,sg*palm).to_4x4()
  if name.startswith('Digits'):
   mat=mat@Matrix.Rotation(math.radians(-18*digits),4,'X')@Matrix.Rotation(math.radians((1 if 'Outer' in name else -1)*sg*9*digits),4,'Z')
  if name=='Jaw':mat=mat@Matrix.Rotation(.58*jaw,4,'X')
  desired[name]=mat
 # Keep the two planted feet at the original support points during the weight shift.
 for side in ['L','R']:
  names=['Thigh'+side,'Shin'+side,'Foot'+side];a=desired[names[0]].translation;ankle=rest[names[2]].translation
  l1=(rest[names[1]].translation-rest[names[0]].translation).length;l2=(ankle-rest[names[1]].translation).length
  knee=ik(a,ankle,rest[names[1]].translation+Vector((0,-.4,0)),l1,l2)
  for name,start,end in [(names[0],a,knee),(names[1],knee,ankle)]:desired[name]=Matrix.Translation(start)@rotation(name,end-start).to_4x4()
  desired[names[2]]=rest[names[2]].copy()
 for b in rig.data.bones:
  name=b.name;par=b.parent.name if b.parent else None;mat=desired[name]
  basis=rest[name].inverted()@mat if par is None else rest[name].inverted()@rest[par]@desired[par].inverted()@mat
  pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix_basis=basis
  if name in previous and pb.rotation_quaternion.dot(previous[name])<0:pb.rotation_quaternion.negate()
  previous[name]=pb.rotation_quaternion.copy();pb.keyframe_insert('location',frame=frame,group=name);pb.keyframe_insert('rotation_quaternion',frame=frame,group=name)
# Independent timing: shoulders lead; wrist/digits arrive later, jaw releases earlier.
for fc in act.fcurves:
 delay=.7 if any(n in fc.data_path for n in ['Hand','Digits']) else .35 if 'Forearm' in fc.data_path else 0
 for point in fc.keyframe_points:
  if point.co.x not in [0,36]:point.co.x+=delay
  point.interpolation='BEZIER';point.handle_left_type='AUTO_CLAMPED';point.handle_right_type='AUTO_CLAMPED'

# Neutral matte lighting: remove only temporary glow; keep approved textures/geometry.
for o in scene.objects:
 if o.type=='MESH':
  if o.name.startswith('Accessory_'):o.hide_render=True
  for mat in o.data.materials:
   if mat and mat.use_nodes:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:bs.inputs['Emission Strength'].default_value=0
scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.cycles.device='CPU';scene.world.color=(.08,.08,.08)
mat=bpy.data.materials.new('StudyFloor');mat.diffuse_color=(.105,.12,.14,1)
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.data.materials.append(mat);floor.location.z=-.012
for co,power,size in [((3,-4,5),650,4),((-3,1,4),450,4),((0,5,5),450,3)]:
 bpy.ops.object.light_add(type='AREA',location=co);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=3.0
views={'reference':(-3.0,5.0,4.4),'front':(0,-6,2),'side':(6,0,2)}
scene.render.resolution_x=420;scene.render.resolution_y=500;scene.render.resolution_percentage=100

def view(name):
 cam.location=views[name];cam.rotation_euler=(Vector((0,0,1.18))-cam.location).to_track_quat('-Z','Y').to_euler()
view('reference');scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-01.blend'),compress=True)
(OUT/'authored-keys.json').write_text(json.dumps({'fps':30,'duration':1.2,'keys':KEYS,'method':'FK joint orientation keys with separate finger/wrist timing. Foot IK only. No runtime replacement.'},indent=2))
# Audit actual skin near shoulders at every frame, preserving the approved bind mesh.
body=next(o for o in scene.objects if o.name.startswith('Body_'));stats=[]
for frame in range(37):
 scene.frame_set(frame);ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();zs=[v.co.z for v in me.vertices];stats.append({'frame':frame,'min_z':min(zs),'max_z':max(zs)});ev.to_mesh_clear()
(OUT/'mesh-bounds.json').write_text(json.dumps(stats,indent=2))
if '--stills' in sys.argv:
 for name in views:
  view(name)
  for f in [0,5,9,17,27,36]:
   scene.frame_set(f);scene.render.filepath=str(OUT/f'{name}-{f:02}.png');bpy.ops.render.render(write_still=True)
else:
 for name in views:
  view(name);folder=OUT/name;folder.mkdir(exist_ok=True)
  for f in range(37):
   scene.frame_set(f);scene.render.filepath=str(folder/f'{f:03}.png');bpy.ops.render.render(write_still=True)
print('STUDY_COMPLETE',str(OUT))
