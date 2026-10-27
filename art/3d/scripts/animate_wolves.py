"""Create editable articulated rigs and gameplay animation clips.
Uses the existing Meshy/Blender meshes; no new remote generation or charge.
"""
import bpy,math,json
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
MODELS=ROOT/'app/src/main/assets/models'
model_meta=json.loads((ROOT/'art/3d/model-report.json').read_text())
BACKUP=ROOT/model_meta.get('static_source_dir','art/3d/source/static');BACKUP.mkdir(parents=True,exist_ok=True)
profiles=model_meta['variants']
report={'rig_type':'procedural humanoid/quadrupedal prototype rig with length-constrained limbs','clips':['WolfIdle','WolfMove','WolfRoll','WolfRunQuad','WolfClaw','WolfRoar','WolfJump','WolfTransform','HumanIdle','HumanMove'],'shared_run_roll_template':'wolf-shared-v4','root_motion':False,'new_meshy_credits':0,'notes':['All 119 frames of the uploaded 4.91-second screen recording reviewed; it is a short edited excerpt, not the complete YouTube source.','Shared 0.533s bounding run: timed paw contacts/recovery, stabilized head, source limb lengths preserved by two-bone IK; idle keeps the approved source arm pose exactly.','Shared 0.8s compact roll; gameplay travel is about 2m. Values are local tuning, not measured world units from the video.','Roar: anticipation, raised/open arms, held chest/head lift, recovery; Bilge has articulated jaw, interior and rigid upper/lower teeth.','Weights use geometric regions and bone distance; manual deformation polish remains.'],'models':[]}

def smoothstep(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)))
 return u*u*(3-2*u)

def roll_angle(t):
 return math.tau*smoothstep(.10,.82,t)

def two_bone(start,goal,pole,l1,l2):
 axis=goal-start
 if axis.length<1e-7:axis=Vector((0,0,-1))
 d=max(abs(l1-l2)+1e-5,min(axis.length,(l1+l2)*.99999));axis.normalize()
 along=(l1*l1-l2*l2+d*d)/(2*d);lift=math.sqrt(max(0,l1*l1-along*along))
 bend=pole-start; bend-=axis*bend.dot(axis)
 if bend.length<1e-7:
  bend=axis.cross(Vector((1,0,0)))
  if bend.length<1e-7:bend=axis.cross(Vector((0,1,0)))
 bend.normalize()
 return start+axis*along+bend*lift,start+axis*d

def fit_limbs(p,base):
 for side in ['L','R']:
  for a,j,b,tip in [('shoulder','elbow','wrist','finger'),('hip','knee','ankle','toe')]:
   a+=side;j+=side;b+=side;tip+=side
   tip_direction=p[tip]-p[b]
   p[j],p[b]=two_bone(p[a],p[b],p[j],(base[j]-base[a]).length,(base[b]-base[j]).length)
   if tip_direction.length<1e-7:tip_direction=base[tip]-base[b]
   p[tip]=p[b]+tip_direction.normalized()*(base[tip]-base[b]).length
 return p

def paw_cycle(t,stance=.26):
 u=t%1
 if u<stance:return -1+2*u/stance,0
 s=(u-stance)/(1-stance)
 return math.cos(math.pi*s),math.sin(math.pi*s)**1.5

# Rebuild missing static inputs from the committed optimized source scenes.
# For legacy wolves extract the GLB bind mesh, explicitly removing armature,
# parenting and vertex groups; never use a posed/animated mesh as a new source.
for profile in profiles:
 path=BACKUP/(profile['id']+'.glb')
 if path.exists():continue
 key=profile['id'];scene_file={'bilge':'bilge-refined.blend','human-bilge':'bilge-human-refined.blend'}.get(key)
 if scene_file:bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/3d'/scene_file))
 else:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(MODELS/(key+'.glb')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in meshes:
  matrix=o.matrix_world.copy();o.parent=None;o.matrix_world=matrix
  for mod in list(o.modifiers):
   if mod.type=='ARMATURE':o.modifiers.remove(mod)
  o.vertex_groups.clear()
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)

def rest_points(h,profile):
 p={'root':(0,0,0),'rootEnd':(0,0,.14),'hip':(0,0,.47),'spine':(0,0,.59),'chest':(0,0,.74),'neck':(0,0,.83),'head':(0,-.018,.91),'headEnd':(0,-.035,.99),'jaw':(0,-.075,.854),'jawEnd':(0,-.16,.834),'tail':(0,.09,.43),'tailMid':(0,.13,.27),'tailEnd':(0,.14,.12)}
 for side,sg in [('L',1),('R',-1)]:
  p.update({f'shoulder{side}':(sg*.16,0,.75),f'elbow{side}':(sg*.27,0,.64),f'wrist{side}':(sg*.35,-.015,.53),f'finger{side}':(sg*.39,-.02,.49),f'hip{side}':(sg*.07,0,.47),f'knee{side}':(sg*.09,-.015,.27),f'ankle{side}':(sg*.095,.04,.09),f'toe{side}':(sg*.10,-.08,.025)})
 result={}
 for k,(x,y,z) in p.items():
  upper=math.exp(-((z-.715)/.105)**2);waist=math.exp(-((z-.545)/.075)**2)
  trunk=max(0,min(1,(.235-abs(x))/.065))
  xs=1+(profile.get('shoulder',1)-1)*upper+(profile.get('waist',1)-1)*waist*trunk
  ys=profile.get('depth',1)*(1+(profile.get('waist_depth',1)-1)*waist*trunk)
  result[k]=Vector((x*xs,y*ys,z))*h
 return result

chains=[('Root','root','rootEnd',None),('Hips','hip','spine','Root'),('Spine','spine','chest','Hips'),('Chest','chest','neck','Spine'),('Neck','neck','head','Chest'),('Head','head','headEnd','Neck'),('Jaw','jaw','jawEnd','Head'),('Tail','tail','tailMid','Hips'),('TailTip','tailMid','tailEnd','Tail')]
for side in ['L','R']:
 chains += [(f'Clavicle{side}','chest',f'shoulder{side}','Chest'),(f'UpperArm{side}',f'shoulder{side}',f'elbow{side}',f'Clavicle{side}'),(f'Forearm{side}',f'elbow{side}',f'wrist{side}',f'UpperArm{side}'),(f'Hand{side}',f'wrist{side}',f'finger{side}',f'Forearm{side}'),(f'Thigh{side}',f'hip{side}',f'knee{side}','Hips'),(f'Shin{side}',f'knee{side}',f'ankle{side}',f'Thigh{side}'),(f'Foot{side}',f'ankle{side}',f'toe{side}',f'Shin{side}')]

def pose_points(base,kind,t,h,variant="shared"):
 p={k:v.copy() for k,v in base.items()}
 span=base['shoulderL'].x/(.16*h)
 if kind in ['WolfIdle','HumanIdle']:
  # Preserve the approved mesh's original arm/shoulder rest positions. Previous
  # generic elbow goals made this near-straight A pose bow outward like wings.
  # Move the complete upper chain together for a subtle breath, keeping segment
  # lengths fixed and both planted feet at the original source coordinates.
  breath=.001*h*math.sin(t*math.tau)
  for name in ['chest','neck','head','headEnd','shoulderL','shoulderR','elbowL','elbowR','wristL','wristR','fingerL','fingerR']:p[name].z+=breath
  if kind=='HumanIdle':
   for side,sg in [('L',1),('R',-1)]:
    for part,x,z in [('elbow',.18,.635),('wrist',.20,.51),('finger',.205,.465)]:p[part+side]=Vector((sg*x,-.035,z))*h
 elif kind=='WolfMove':
  p=pose_points(base,'WolfIdle',t,h,variant)
  bob=.008*h*math.cos(t*math.tau*2)
  for k in ['hip','hipL','hipR','spine','chest','shoulderL','shoulderR','neck']:p[k].z+=bob
  for side,sg,phase in [('L',1,0),('R',-1,.5)]:
   stride,lift=paw_cycle(t+phase,.38)
   p['ankle'+side]=Vector((sg*.105,.025+.16*stride,.07+.10*lift))*h
   p['toe'+side]=p['ankle'+side]+Vector((0,-.08,-.045))*h
   p['knee'+side]=p['hip'+side]+Vector((sg*.04,-.15,-.15))*h
   for part in ['elbow','wrist','finger']:p[part+side].y-=.065*h*math.sin((t+phase)*math.tau)
 elif kind=='HumanMove':
  p=pose_points(base,'HumanIdle' if kind=='HumanMove' else 'WolfIdle',t,h,variant)
  for side,sg,offset in [('L',1,0),('R',-1,math.pi)]:
   a=t*math.tau+offset;swing=math.sin(a)
   for part in ['knee','ankle','toe']:p[part+side].y-=.065*h*swing
   for part in ['ankle','toe']:p[part+side].z+=.045*h*max(0,swing)
   for part in ['elbow','wrist','finger']:p[part+side].y+=.07*h*swing
  bob=.008*h*math.cos(t*math.tau*2)
  for k in ['hip','spine','chest','neck','head','headEnd']:p[k].z+=bob
 elif kind=='WolfClaw':
  p=pose_points(base,'WolfIdle',0,h,variant)
  for side,sg,phase in [('L',1,0),('R',-1,.5)]:
   if variant=='kultigin':u=max(0,min(1,(t-phase)*2));strength=math.sin(math.pi*u)**2;x=sg*.30*math.cos(math.pi*u);z=.55+.13*math.sin(math.tau*u)
   elif variant=='alparslan':strength=math.sin(math.pi*t)**2;x=sg*.13;z=.49+.33*math.sin(math.pi*t)
   elif variant=='konuralp':strength=math.sin(math.pi*t)**2;x=sg*.24*math.cos(t*math.pi*3+phase*2);z=.52+.13*math.sin(t*math.pi*3)
   else:strength=math.sin(math.pi*t)**2;x=sg*(.28-.40*t);z=.63-.23*t
   p['elbow'+side]=p['elbow'+side].lerp(Vector((sg*.24,-.12,.65))*h,strength)
   for part,drop in [('wrist',0),('finger',.04)]:p[part+side]=p[part+side].lerp(Vector((x,-.28,z-drop))*h,strength)
  p['chest'].y-=.035*h*math.sin(math.pi*t)
 elif kind in ['WolfRoar','WolfTransform']:
  p=pose_points(base,'WolfIdle',0,h,variant)
  strength=smoothstep(.10,.42,t)*(1-smoothstep(.70,1,t)) if kind=='WolfRoar' else math.sin(math.pi*t)**2
  for k in ['chest','neck','head','headEnd']:p[k].z+=strength*.025*h
  p['head'].y+=.035*h*strength;p['headEnd'].y+=.08*h*strength
  for side,sg in [('L',1),('R',-1)]:
   p['elbow'+side]=p['elbow'+side].lerp(Vector((sg*.30*span,-.06,.68))*h,strength)
   p['wrist'+side]=p['wrist'+side].lerp(Vector((sg*.34*span,-.17,.64))*h,strength)
   p['finger'+side]=p['finger'+side].lerp(Vector((sg*.35*span,-.20,.60))*h,strength)
 elif kind=='WolfJump':
  p=pose_points(base,'WolfIdle',0,h,variant);strength=math.sin(math.pi*t)**2
  for side,sg in [('L',1),('R',-1)]:
   for part,dz,dy in [('knee',.08,-.11),('ankle',.16,-.05),('toe',.16,-.07)]:p[part+side].z+=dz*h*strength;p[part+side].y+=dy*h*strength
   for part in ['wrist','finger']:p[part+side].y-=.12*h*strength
 elif kind=='WolfRunQuad':
  arm=sum((base[b+'L']-base[a+'L']).length for a,b in [('shoulder','elbow'),('elbow','wrist')])/h
  leg=sum((base[b+'L']-base[a+'L']).length for a,b in [('hip','knee'),('knee','ankle')])/h
  b=.012*math.sin(t*math.tau*2);front_z=.07+arm*.70+b;rear_z=.07+leg*.78+b
  vals={'hip':(0,.15,rear_z),'spine':(0,.015,(front_z+rear_z)/2),'chest':(0,-.12,front_z),'neck':(0,-.19,front_z+.045),'head':(0,-.29,front_z+.11-b*.8),'headEnd':(0,-.38,front_z+.12-b*.8),'tail':(0,.23,rear_z),'tailMid':(0,.36,rear_z+.025),'tailEnd':(0,.46,rear_z-.02)}
  for k,v in vals.items():p[k]=Vector(v)*h
  for side,sg,phase in [('L',1,0),('R',-1,.09)]:
   fy,fz=paw_cycle(t+phase);ry,rz=paw_cycle(t+phase+.5)
   vals={f'shoulder{side}':(sg*.16*span,-.12,front_z),f'elbow{side}':(sg*.19*span,.015,front_z-.12),f'wrist{side}':(sg*.17*span,-.14+.17*fy,.075+.11*fz),f'finger{side}':(sg*.17*span,-.20+.17*fy,.018+.11*fz),f'hip{side}':(sg*.075,.15,rear_z),f'knee{side}':(sg*.11,-.04,rear_z-.12),f'ankle{side}':(sg*.11,.17+.17*ry,.07+.10*rz),f'toe{side}':(sg*.11,.09+.17*ry,.025+.10*rz)}
   for k,v in vals.items():
    p[k]=Vector(v)*h
 elif kind=='WolfRoll':
  p=pose_points(base,'WolfIdle',0,h)
  tuck=smoothstep(.02,.16,t)*(1-smoothstep(.76,1,t))
  for side,sg in [('L',1),('R',-1)]:
   targets={f'elbow{side}':(sg*.18,-.10,.60),f'wrist{side}':(sg*.13,-.18,.68),f'finger{side}':(sg*.1,-.20,.69),f'knee{side}':(sg*.13,-.23,.47),f'ankle{side}':(sg*.13,-.11,.32),f'toe{side}':(sg*.13,-.22,.32)}
   for k,v in targets.items():p[k]=p[k].lerp(Vector(v)*h,tuck)
  flight=max(0,min(1,(t-.08)/.78));arc=math.sin(math.pi*flight)
  p=fit_limbs(p,base)
  pivot=Vector((0,0,.5*h));jump=Vector((0,-.05*h*arc,.16*h*arc))
  rot=Matrix.Rotation(roll_angle(t),4,'X')
  for k in p:p[k]=pivot+jump+rot.to_3x3()@(p[k]-pivot)
 if kind=='WolfRunQuad':
  # Joint targets describe ankle/wrist centers; lift the body by the paw sole
  # thickness so the actual skinned claws, not just the joints, meet the floor.
  for name in p:
   if name not in ['root','rootEnd']:p[name].z+=.04*h
 # Jaw follows head in every pose, including the full-body roll. The roar
 # rotates the real lower jaw and its teeth, exposing the dark oral interior.
 headrot=(base['headEnd']-base['head']).rotation_difference(p['headEnd']-p['head']).to_matrix()
 p['jaw']=p['head']+headrot@(base['jaw']-base['head'])
 strength=smoothstep(.10,.42,t)*(1-smoothstep(.70,1,t)) if kind=='WolfRoar' else 0
 jawrot=Matrix.Rotation(.60*strength,3,'X')
 p['jawEnd']=p['jaw']+headrot@jawrot@(base['jawEnd']-base['jaw'])
 return p if kind=='WolfIdle' else fit_limbs(p,base)

for profile in profiles:
 key=profile['id'];h=profile['height_m'];src=BACKUP/(key+'.glb')
 assert src.is_file(), 'Static source export is missing'
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 bpy.ops.import_scene.gltf(filepath=str(src))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 base=rest_points(h,profile.get('shape_profile',{}))
 for joint,co in profile.get('rest_joints',{}).items():base[joint]=Vector(co)*h
 data=bpy.data.armatures.new('WolfSkeleton');rig=bpy.data.objects.new('WolfRig',data);bpy.context.scene.collection.objects.link(rig)
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for name,a,b,parent in chains:
  bone=data.edit_bones.new(name);bone.head=base[a];bone.tail=base[b]
  if parent:bone.parent=data.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
 rest_mats={bone.name:bone.matrix_local.copy() for bone in data.bones}
 # Geometric weights, with torso/limb regions to avoid connecting arms to chest.
 segments=[(name,np.array(base[a]),np.array(base[b])) for name,a,b,_ in chains if name!='Root']
 for o in meshes:
  xyz=np.array([tuple(v.co) for v in o.data.vertices]);N=len(xyz)
  if not N:continue
  dist=np.zeros((N,len(segments)))
  for j,(name,a,b) in enumerate(segments):
   ab=b-a;u=np.clip(((xyz-a)@ab)/np.dot(ab,ab),0,1);dist[:,j]=np.linalg.norm(xyz-(a+u[:,None]*ab),axis=1)
   z=xyz[:,2]/h;x=xyz[:,0]/h;y=xyz[:,1]/h
   if name=='Jaw':
    dist[:,j]+=h*3
    if key=='bilge':
     jaw=(np.abs(x)<.047)&(y<-.10)&(z>.815)&(z<.849);dist[jaw,j]=.001*h
   elif any(s in name for s in ['Arm','Hand','Clavicle']):
    side=1 if name.endswith('L') else -1;dist[(x*side<.13)|(z<.28),j]+=h
   elif any(s in name for s in ['Thigh','Shin','Foot']):
    side=1 if name.endswith('L') else -1;dist[(x*side<-.01)|(z>.54),j]+=h
   elif name.startswith('Tail'):
    if not profile.get('has_tail',True):dist[:,j]+=h*3
    else:dist[(y<.06)|(z>.52),j]+=h
   else:dist[((np.abs(x)>.20)&(z<.76))|((z<.43)&(np.abs(x)>.035)),j]+=h
  near=np.argsort(dist,axis=1)[:,:3];weights=1/np.maximum(.01*h,np.take_along_axis(dist,near,axis=1))**4;weights/=weights.sum(axis=1,keepdims=True)
  groups=[o.vertex_groups.new(name=n) for n,_,_ in segments]
  for i in range(N):
   for idx,w in zip(near[i],weights[i]):
    if w>.005:groups[int(idx)].add([i],float(w),'REPLACE')
  if o.get('skin_bone'):
   o.vertex_groups.clear();g=o.vertex_groups.new(name=o['skin_bone']);g.add(list(range(N)),1,'REPLACE')
  mod=o.modifiers.new('WolfSkin','ARMATURE');mod.object=rig;o.parent=rig
 # Interpolate the actual body's weights onto tattoo vertices. An independent
 # distance rig made surface ink drift away from the skin at bending joints.
 body=next(o for o in meshes if o.name.startswith('Body_'))
 body.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in body.data.loop_triangles]
 tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],triangles,all_triangles=True)
 body_weights=np.zeros((len(body.data.vertices),len(body.vertex_groups)))
 for vertex in body.data.vertices:
  for g in vertex.groups:body_weights[vertex.index,g.group]=g.weight
 for o in meshes:
  if not o.name.startswith('Tattoo_'):continue
  o.vertex_groups.clear();groups=[o.vertex_groups.new(name=g.name) for g in body.vertex_groups]
  for vertex in o.data.vertices:
   hit=tree.find_nearest(vertex.co)
   if hit[2] is None:continue
   ids=triangles[hit[2]];a,b,c=[body.data.vertices[i].co for i in ids]
   ab=b-a;ac=c-a;ap=hit[0]-a
   d00=ab.dot(ab);d01=ab.dot(ac);d11=ac.dot(ac);d20=ap.dot(ab);d21=ap.dot(ac);den=d00*d11-d01*d01
   if abs(den)<1e-16:w=np.array([1.,0.,0.])
   else:
    v=(d11*d20-d01*d21)/den;w2=(d00*d21-d01*d20)/den;w=np.clip([1-v-w2,v,w2],0,1);w/=w.sum()
   weights=w@body_weights[list(ids)];top=np.argsort(weights)[-4:];total=weights[top].sum()
   for index in top:
    if weights[index]>.0001:groups[index].add([vertex.index],float(weights[index]/total),'REPLACE')
 rig.animation_data_create();bpy.context.scene.render.fps=30
 specs=[('HumanIdle',60),('HumanMove',30)] if profile.get('kind')=='human' else [('WolfIdle',30),('WolfMove',20),('WolfRunQuad',16),('WolfRoll',24),('WolfClaw',20),('WolfRoar',36),('WolfJump',24),('WolfTransform',30)]
 for kind,frames in specs:
  action=bpy.data.actions.new(kind);rig.animation_data.action=action
  previous_quaternions={}
  for frame in range(0,frames+1,2):
   t=frame/frames;points=pose_points(base,kind,min(t,1),h,key);desired={}
   for name,a,b,parent in chains:
    start,end=points[a],points[b];direction=end-start
    global_rotation=Matrix.Rotation(roll_angle(min(t,1)),3,'X') if kind=='WolfRoll' else Matrix.Identity(3)
    local_direction=global_rotation.inverted()@direction
    rest_rotation=rest_mats[name].to_3x3()
    rest_direction=rest_rotation@Vector((0,1,0))
    align=rest_direction.rotation_difference(local_direction.normalized()).to_matrix()
    orientation=(global_rotation@align@rest_rotation).to_4x4()
    mat=Matrix.Translation(start)@orientation
    desired[name]=mat
    basis=rest_mats[name].inverted()@mat if parent is None else rest_mats[name].inverted()@rest_mats[parent]@desired[parent].inverted()@mat
    pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix_basis=basis
    # Blender's component F-curves otherwise interpolate opposite quaternion
    # signs through zero at a 180-degree turn, briefly straightening the roll.
    if name in previous_quaternions and pb.rotation_quaternion.dot(previous_quaternions[name])<0:
     pb.rotation_quaternion.negate()
    previous_quaternions[name]=pb.rotation_quaternion.copy()
    pb.keyframe_insert('location',frame=frame,group=name);pb.keyframe_insert('rotation_quaternion',frame=frame,group=name)
  for fc in action.fcurves:
   for point in fc.keyframe_points:point.interpolation='LINEAR'
  track=rig.animation_data.nla_tracks.new();track.name=kind;strip=track.strips.new(kind,0,action);strip.extrapolation='NOTHING'
 rig.animation_data.action=None
 bpy.context.scene.frame_start=0;bpy.context.scene.frame_end=60;bpy.context.scene.frame_set(0)
 # The exporter's NLA track mode makes three distinct clips, not a single mixed timeline.
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 for o in meshes:
  if o.name.startswith('Body_'):o['rig_status']='23-bone length-constrained rig; Bilge jaw and oral geometry, source topology limitations documented'
 bpy.ops.export_scene.gltf(filepath=str(MODELS/(key+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True)
 report['models'].append({'id':key,'bones':len(data.bones),'skinned_parts':len(meshes),'tattoo_skinning':'barycentric transfer from body triangles','clips':{name:frames/30 for name,frames in specs},'file':key+'.glb','bytes':(MODELS/(key+'.glb')).stat().st_size})
 print('RIGGED',key,flush=True)
# Assemble the exported characters into an editable source scene.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for i,p in enumerate(profiles):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(MODELS/(p['id']+'.glb')))
 imported=set(bpy.data.objects)-before
 for o in imported:
  if o.parent is None:o.location.x+=i*2.8
bpy.context.scene.render.fps=30
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art/3d/wolves-rigged.blend'),compress=True)
(ROOT/'art/3d/animation-report.json').write_text(json.dumps(report,indent=2))
model_report=json.loads((ROOT/'art/3d/model-report.json').read_text())
model_report.update(rigged=True,rig_status='23-bone length-constrained rig; Bilge jaw and oral geometry, source topology limitations documented',animation_report='animation-report.json')
for p in model_report['variants']:p['bytes']=(MODELS/(p['id']+'.glb')).stat().st_size
(ROOT/'art/3d/model-report.json').write_text(json.dumps(model_report,indent=2))
print('ANIMATION_REPORT',json.dumps(report),flush=True)
