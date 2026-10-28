"""Create editable articulated rigs and gameplay animation clips.
Uses the existing Meshy/Blender meshes; no new remote generation or charge.
"""
import bpy,math,json,sys
sys.path.insert(0,str(__import__("pathlib").Path(__file__).resolve().parent))
from mouth_parts import add_mouth
from reference_motion import run_pose,roar_pose,setup_digits,pose_digits,wrist_roll,jaw_envelope,RUN_METERS,set_sole_offsets
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
MODELS=ROOT/'app/src/main/assets/models'
model_meta=json.loads((ROOT/'art/3d/model-report.json').read_text())
BACKUP=ROOT/model_meta.get('static_source_dir','art/3d/source/static');BACKUP.mkdir(parents=True,exist_ok=True)
profiles=model_meta['variants']
report={'rig_type':'procedural humanoid/quadrupedal prototype rig with length-constrained limbs','clips':['WolfIdle','WolfMove','WolfRoll','WolfRunQuad','WolfClaw','WolfRoar','WolfJump','WolfTransform','HumanIdle','HumanMove'],'shared_run_roll_template':'wolf-reference-v5','root_motion':False,'new_meshy_credits':0,'run_stride_m':RUN_METERS,'reference_review':'docs/uc-video-kosu-kukreme-analizi-20261028.md','notes':['301 frames across the three new clips reviewed; target run footage is slowed as confirmed by the match clock.','All 119 frames of the uploaded 4.91-second screen recording reviewed; it is a short edited excerpt, not the complete YouTube source.','Authored 0.533s run, 4.2667m stride at 8m/s: reach/front support/gather/hind push/suspension. Fixed trunk and limb lengths, source idle unchanged.','Shared 0.8s compact roll; gameplay travel is about 2m. Values are local tuning, not measured world units from the video.','Shared 1.2s overhead roar: crouch/spread/hands above head/open digits/chest lift/recovery. No paid generation.','Weights use geometric regions and bone distance; manual deformation polish remains.'],'models':[]}

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

for side in ['L','R']:
 for label in ['Inner','Outer']:chains.append(('Digits'+label+side,'digits'+label+side,'digits'+label+'End'+side,'Hand'+side))

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
 elif kind=='WolfRoar':
  p=roar_pose(base,t,h,two_bone)
 elif kind=='WolfTransform':
  p=pose_points(base,'WolfIdle',0,h,variant);strength=math.sin(math.pi*t)**2
  for k in ['chest','neck','head','headEnd']:p[k].z+=strength*.025*h
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
  p=run_pose(base,t,h,two_bone)
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
 # Jaw follows head in every pose, including the full-body roll. The roar
 # rotates the real lower jaw and its teeth, exposing the dark oral interior.
 headrot=(base['headEnd']-base['head']).rotation_difference(p['headEnd']-p['head']).to_matrix()
 p['jaw']=p['head']+headrot@(base['jaw']-base['head'])
 strength=jaw_envelope(kind,t)
 jawrot=Matrix.Rotation(.60*strength,3,'X')
 p['jawEnd']=p['jaw']+headrot@jawrot@(base['jawEnd']-base['jaw'])
 return pose_digits(p if kind in ['WolfIdle','WolfRunQuad','WolfRoar'] else fit_limbs(p,base),base,kind,t,h)

for profile in profiles:
 key=profile['id'];h=profile['height_m'];src=BACKUP/(key+'.glb')
 assert src.is_file(), 'Static source export is missing'
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 bpy.ops.import_scene.gltf(filepath=str(src))
 legacy_face=profile.get('kind')!='human' and key!='bilge'
 face_depth=profile.get('shape_profile',{}).get('depth',1.08)/1.08
 if legacy_face:add_mouth(h,face_depth)
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 if legacy_face and not profile.get('rest_joints'):
  # Measure the actual approved A-pose, rather than assuming the former wide
  # generic wrist/finger points. No source vertex is moved.
  src_body=next(o for o in meshes if o.name.startswith('Body_'));coords=np.array([tuple(v.co/h) for v in src_body.data.vertices]);joints={}
  for side,sg in [('L',1),('R',-1)]:
   for part,z,min_x in [('shoulder',.75,.155),('elbow',.64,.205),('wrist',.535,.255),('finger',.485,.285)]:
    band=coords[(np.abs(coords[:,2]-z)<.016)&(coords[:,0]*sg>min_x)]
    if len(band):joints[part+side]=[float(np.median(band[:,0])),float(np.median(band[:,1])),z]
  profile['rest_joints']=joints
 base=rest_points(h,profile.get('shape_profile',{}))
 for joint,co in profile.get('rest_joints',{}).items():base[joint]=Vector(co)*h
 if legacy_face:base['jaw']=Vector((0,-.10*face_depth,.827))*h;base['jawEnd']=Vector((0,-.165*face_depth,.808))*h
 setup_digits(base,h)
 data=bpy.data.armatures.new('WolfSkeleton');rig=bpy.data.objects.new('WolfRig',data);bpy.context.scene.collection.objects.link(rig)
 rig['motion_profile']='wolf-reference-v5';rig['run_stride_m']=RUN_METERS;rig['run_reference_speed_mps']=8;rig['roar_duration_s']=1.2
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
    elif legacy_face:
     jaw=(np.abs(x)<.05)&(y<-.112*face_depth)&(z>.79)&(z<.824);dist[jaw,j]=.001*h
   elif any(part in name.lower() for part in ['arm','hand','clavicle','digits']):
    side=1 if name.endswith('L') else -1;ss='L' if side==1 else 'R'
    # Paint the A-pose hand/arm domain explicitly. A pure nearest-bone rule
    # attached skirt panels at x=.17,z=.32 to finger bones at x=.25,z=.37.
    hand_inner=max(.215 if key=='bilge' else .20,min(abs(base['wrist'+ss].x),abs(base['finger'+ss].x))/h-.055)
    boundary=np.interp(z,[.25,.50,.62,.73,.82],[hand_inner,hand_inner,max(.13,abs(base['elbow'+ss].x)/h-.065),.125,.16])
    valid=(x*side>boundary)&(z>.27)
    if 'Hand' in name or 'Digits' in name:valid&=(z<base['wrist'+ss].z/h+.035)
    if 'Digits' in name:
     pivot=base['finger'+ss];d=(base['finger'+ss]-base['wrist'+ss]).normalized()
     valid&=(np.linalg.norm(xyz-np.array(pivot),axis=1)<.095*h)&(((xyz-np.array(pivot))@np.array(d))>-.018*h)&(x*side>hand_inner+.008)
    dist[~valid,j]+=h*3
   elif any(s in name for s in ['Thigh','Shin','Foot']):
    side=1 if name.endswith('L') else -1;dist[(x*side<-.01)|(z>.54),j]+=h
   elif name.startswith('Tail'):
    if not profile.get('has_tail',True):dist[:,j]+=h*3
    else:dist[(y<.06)|(z>.52),j]+=h
   else:dist[((np.abs(x)>.20)&(z<.76))|((z<.43)&(np.abs(x)>.035)),j]+=h
  near=np.argsort(dist,axis=1)[:,:3];weights=1/np.maximum(.018*h,np.take_along_axis(dist,near,axis=1))**3.5;weights/=weights.sum(axis=1,keepdims=True)
  groups=[o.vertex_groups.new(name=n) for n,_,_ in segments]
  segment_ids={n:i for i,(n,_,_) in enumerate(segments)}
  for i in range(N):
   entries=list(zip(near[i],weights[i]));co=Vector(xyz[i]);side='L' if co.x>0 else 'R';sg=1 if co.x>0 else -1
   wrist=base['wrist'+side];finger=base['finger'+side];axis=(finger-wrist).normalized();along=(co-wrist).dot(axis)
   inner=max(.215 if key=='bilge' else .20,min(abs(wrist.x),abs(finger.x))/h-.055)
   hand_domain=co.x*sg>inner*h and co.z<wrist.z+.035*h and (co-finger).length<.14*h
   if hand_domain and along>-.012*h:
    # A planted palm is rigid. Blending its sole with the elbow made the sole
    # sag through the floor as the forearm bent, even with a fixed wrist goal.
    palm=smoothstep(-.012*h,.018*h,along)
    curl=smoothstep((finger-wrist).length*.60,(finger-wrist).length*1.05,along)*.90
    digit_ids=[segment_ids['Digits'+label+side] for label in ['Inner','Outer']]
    distances=np.maximum(.009*h,dist[i,digit_ids]);share=(1/distances**2);share/=share.sum()
    entries=[(segment_ids['Forearm'+side],1-palm),(segment_ids['Hand'+side],palm*(1-curl))]+[(idx,float(palm*curl*w)) for idx,w in zip(digit_ids,share)]
   for idx,w in entries:
    if w>.001:groups[int(idx)].add([i],float(w),'REPLACE')
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
 def place_pose(kind,t):
  points=pose_points(base,kind,min(t,1),h,key);desired={}
  for name,a,b,parent in chains:
   start,end=points[a],points[b];direction=end-start
   global_rotation=Matrix.Rotation(roll_angle(min(t,1)),3,'X') if kind=='WolfRoll' else Matrix.Identity(3)
   local_direction=global_rotation.inverted()@direction
   rest_rotation=rest_mats[name].to_3x3();rest_direction=rest_rotation@Vector((0,1,0))
   align=rest_direction.rotation_difference(local_direction.normalized()).to_matrix()
   orientation=(global_rotation@align@rest_rotation).to_4x4()
   if name.startswith('Hand'):orientation=orientation@Matrix.Rotation(wrist_roll(kind,t,name[-1]),4,'Y')
   mat=Matrix.Translation(start)@orientation;desired[name]=mat
   basis=rest_mats[name].inverted()@mat if parent is None else rest_mats[name].inverted()@rest_mats[parent]@desired[parent].inverted()@mat
   pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix_basis=basis
 # Calibrate actual skinned sole vertices at a support pose, independently for
 # all four paws. This changes IK goal height, never the approved mesh or scale.
 set_sole_offsets();sole_offsets={k:0. for k in ['frontL','frontR','rearL','rearR']}
 if profile.get('kind')!='human':
  groups_by_name={g.name:g.index for g in body.vertex_groups};masks={}
  for side in ['L','R']:
   hand=[g.index for g in body.vertex_groups if g.name=='Hand'+side or g.name.startswith('Digits') and g.name.endswith(side)]
   masks['front'+side]=np.flatnonzero(body_weights[:,hand].sum(axis=1)>.65)
   masks['rear'+side]=np.flatnonzero(body_weights[:,groups_by_name['Foot'+side]]>.45)
  for iteration in range(2):
   for family,phase in [('front',.06),('rear',.55)]:
    place_pose('WolfRunQuad',phase);bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    for side in ['L','R']:
     name=family+side;ids=masks[name]
     if len(ids):sole_offsets[name]+=.004-min(mesh.vertices[int(i)].co.z for i in ids)
    ev.to_mesh_clear();set_sole_offsets(sole_offsets)
  place_pose('WolfIdle',0)
 rig['paw_sole_offsets_m']=sole_offsets
 rig.animation_data_create();bpy.context.scene.render.fps=60
 specs=[('HumanIdle',60),('HumanMove',30)] if profile.get('kind')=='human' else [('WolfIdle',30),('WolfMove',20),('WolfRunQuad',16),('WolfRoll',24),('WolfClaw',20),('WolfRoar',36),('WolfJump',24),('WolfTransform',30)]
 specs=[(name,frames*2) for name,frames in specs]
 for kind,frames in specs:
  action=bpy.data.actions.new(kind);rig.animation_data.action=action;previous_quaternions={}
  for frame in range(0,frames+1):
   t=frame/frames;place_pose(kind,t)
   for pb in rig.pose.bones:
    name=pb.name
    if name in previous_quaternions and pb.rotation_quaternion.dot(previous_quaternions[name])<0:pb.rotation_quaternion.negate()
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
  if o.name.startswith('Body_'):o['rig_status']='27-bone source-preserving rig; authored support/gather/push poses and overhead roar with wrist roll and digits'
 bpy.ops.export_scene.gltf(filepath=str(MODELS/(key+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True)
 triangle_count=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 report['models'].append({'id':key,'triangles':triangle_count,'oral_parts':sum(o.name.startswith('Mouth_') for o in meshes),'sole_offsets_m':sole_offsets,'bones':len(data.bones),'skinned_parts':len(meshes),'tattoo_skinning':'barycentric transfer from body triangles','clips':{name:frames/60 for name,frames in specs},'bake_fps':60,'file':key+'.glb','bytes':(MODELS/(key+'.glb')).stat().st_size})
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
model_report.update(rigged=True,rig_status='27-bone source-preserving rig; authored support/gather/push poses and overhead roar with wrist roll and digits',animation_report='animation-report.json')
for p in model_report['variants']:
 p['bytes']=(MODELS/(p['id']+'.glb')).stat().st_size
 p['rest_joints']=next(pr.get('rest_joints',{}) for pr in profiles if pr['id']==p['id'])
 p['triangles']=next(m['triangles'] for m in report['models'] if m['id']==p['id'])
(ROOT/'art/3d/model-report.json').write_text(json.dumps(model_report,indent=2))
print('ANIMATION_REPORT',json.dumps(report),flush=True)
