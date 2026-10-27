"""Create an initial articulated rig and three editable preview clips.
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
report={'rig_type':'initial procedural humanoid/quadrupedal preview rig','clips':['WolfIdle','WolfRoll','WolfRunQuad'],'root_motion':False,'new_meshy_credits':0,'notes':['Preview animation in equipment screen, not collision-tested gameplay.','Weights use geometric regions and bone distance; manual deformation polish remains.'],'models':[]}

# Reproducible from the committed static Blender scene. Never back up an
# already-rigged GLB as an unrigged source on a clean checkout.
missing=[p for p in profiles if not (BACKUP/(p['id']+'.glb')).exists()]
if missing:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art/3d/wolves-modular.blend'))
 for profile in missing:
  bpy.ops.object.select_all(action='DESELECT')
  collection=bpy.data.collections['Wolf_'+profile['id']]
  for o in collection.objects:
   o.hide_set(False);o.select_set(True)
   o.location.x-=profiles.index(profile)*2.8
  bpy.context.view_layer.objects.active=next(o for o in collection.objects if o.name.startswith('Body_'))
  bpy.ops.export_scene.gltf(filepath=str(BACKUP/(profile['id']+'.glb')),export_format='GLB',use_selection=True,export_animations=False)

def rest_points(h,profile):
 p={'root':(0,0,0),'rootEnd':(0,0,.14),'hip':(0,0,.47),'spine':(0,0,.59),'chest':(0,0,.74),'neck':(0,0,.83),'head':(0,-.018,.91),'headEnd':(0,-.035,.99),'tail':(0,.09,.43),'tailMid':(0,.13,.27),'tailEnd':(0,.14,.12)}
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

chains=[('Root','root','rootEnd',None),('Hips','hip','spine','Root'),('Spine','spine','chest','Hips'),('Chest','chest','neck','Spine'),('Neck','neck','head','Chest'),('Head','head','headEnd','Neck'),('Tail','tail','tailMid','Hips'),('TailTip','tailMid','tailEnd','Tail')]
for side in ['L','R']:
 chains += [(f'Clavicle{side}','chest',f'shoulder{side}','Chest'),(f'UpperArm{side}',f'shoulder{side}',f'elbow{side}',f'Clavicle{side}'),(f'Forearm{side}',f'elbow{side}',f'wrist{side}',f'UpperArm{side}'),(f'Hand{side}',f'wrist{side}',f'finger{side}',f'Forearm{side}'),(f'Thigh{side}',f'hip{side}',f'knee{side}','Hips'),(f'Shin{side}',f'knee{side}',f'ankle{side}',f'Thigh{side}'),(f'Foot{side}',f'ankle{side}',f'toe{side}',f'Shin{side}')]

def pose_points(base,kind,t,h):
 p={k:v.copy() for k,v in base.items()}
 span=base['shoulderL'].x/(.16*h)
 if kind=='WolfIdle':
  breath=.003*h*math.sin(t*math.tau)
  for k in ['chest','neck','head','headEnd']:p[k].z+=breath
  # Lower the A-pose arms into a relaxed standing stance.
  for side,sg in [('L',1),('R',-1)]:
   p[f'elbow{side}']=Vector((sg*.22*span,-.01,.62))*h;p[f'wrist{side}']=Vector((sg*.23*span,-.025,.47))*h;p[f'finger{side}']=Vector((sg*.24*span,-.03,.42))*h
 elif kind=='WolfRunQuad':
  b=.022*math.sin(t*math.tau*2)
  vals={'hip':(0,.13,.43+b),'spine':(0,.03,.45+b),'chest':(0,-.16,.45+b),'neck':(0,-.24,.46+b),'head':(0,-.31,.49+b),'headEnd':(0,-.40,.50+b),'tail':(0,.20,.43+b),'tailMid':(0,.33,.45+b),'tailEnd':(0,.43,.42+b)}
  for k,v in vals.items():p[k]=Vector(v)*h
  for side,sg,phase in [('L',1,0),('R',-1,.35)]:
   front=t*math.tau+phase;rear=front+math.pi
   fy=.11*math.cos(front);fz=.06*max(0,math.sin(front));ry=.11*math.cos(rear);rz=.065*max(0,math.sin(rear))
   vals={f'shoulder{side}':(sg*.15,-.16,.44+b),f'elbow{side}':(sg*.165,-.20+fy*.4,.25+b),f'wrist{side}':(sg*.17,-.20+fy,.055+fz),f'finger{side}':(sg*.17,-.26+fy,.018+fz),f'hip{side}':(sg*.075,.13,.43+b),f'knee{side}':(sg*.11,.05+ry*.3,.25+b),f'ankle{side}':(sg*.11,.20+ry,.07+rz),f'toe{side}':(sg*.11,.12+ry,.025+rz)}
   for k,v in vals.items():
    p[k]=Vector(v)*h
    if any(part in k for part in ['shoulder','elbow','wrist','finger']):p[k].x*=span
 elif kind=='WolfRoll':
  p=pose_points(base,'WolfIdle',0,h)
  tuck=math.sin(math.pi*t)**2
  for side,sg in [('L',1),('R',-1)]:
   targets={f'elbow{side}':(sg*.18,-.10,.60),f'wrist{side}':(sg*.13,-.18,.68),f'finger{side}':(sg*.1,-.20,.69),f'knee{side}':(sg*.13,-.23,.47),f'ankle{side}':(sg*.13,-.11,.32),f'toe{side}':(sg*.13,-.22,.32)}
   for k,v in targets.items():p[k]=p[k].lerp(Vector(v)*h,tuck)
  pivot=Vector((0,0,.5*h));jump=Vector((0,-.18*h*math.sin(math.pi*t),.36*h*math.sin(math.pi*t)))
  rot=Matrix.Rotation(math.tau*t,4,'X')
  for k in p:p[k]=pivot+jump+rot.to_3x3()@(p[k]-pivot)
 return p

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
   if any(s in name for s in ['Arm','Hand','Clavicle']):
    side=1 if name.endswith('L') else -1;dist[(x*side<.13)|(z<.42),j]+=h
   elif any(s in name for s in ['Thigh','Shin','Foot']):
    side=1 if name.endswith('L') else -1;dist[(x*side<-.01)|(z>.54),j]+=h
   elif name.startswith('Tail'):dist[(y<.06)|(z>.52),j]+=h
   else:dist[((np.abs(x)>.20)&(z<.76))|((z<.43)&(np.abs(x)>.035)),j]+=h
  near=np.argsort(dist,axis=1)[:,:3];weights=1/np.maximum(.01*h,np.take_along_axis(dist,near,axis=1))**4;weights/=weights.sum(axis=1,keepdims=True)
  groups=[o.vertex_groups.new(name=n) for n,_,_ in segments]
  for i in range(N):
   for idx,w in zip(near[i],weights[i]):
    if w>.005:groups[int(idx)].add([i],float(w),'REPLACE')
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
 for kind,frames in [('WolfIdle',30),('WolfRunQuad',24),('WolfRoll',42)]:
  action=bpy.data.actions.new(kind);rig.animation_data.action=action
  for frame in range(1,frames+2,2):
   t=(frame-1)/frames;points=pose_points(base,kind,min(t,1),h);desired={}
   for name,a,b,parent in chains:
    start,end=points[a],points[b];direction=end-start
    global_rotation=Matrix.Rotation(math.tau*min(t,1),3,'X') if kind=='WolfRoll' else Matrix.Identity(3)
    local_direction=global_rotation.inverted()@direction
    rest_rotation=rest_mats[name].to_3x3()
    rest_direction=rest_rotation@Vector((0,1,0))
    align=rest_direction.rotation_difference(local_direction.normalized()).to_matrix()
    orientation=(global_rotation@align@rest_rotation).to_4x4()
    mat=Matrix.Translation(start)@orientation
    desired[name]=mat
    basis=rest_mats[name].inverted()@mat if parent is None else rest_mats[name].inverted()@rest_mats[parent]@desired[parent].inverted()@mat
    pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix_basis=basis
    pb.keyframe_insert('location',frame=frame,group=name);pb.keyframe_insert('rotation_quaternion',frame=frame,group=name)
  for fc in action.fcurves:
   for point in fc.keyframe_points:point.interpolation='LINEAR'
  track=rig.animation_data.nla_tracks.new();track.name=kind;strip=track.strips.new(kind,1,action);strip.extrapolation='NOTHING'
 rig.animation_data.action=None
 bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=43;bpy.context.scene.frame_set(1)
 # The exporter's NLA track mode makes three distinct clips, not a single mixed timeline.
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 for o in meshes:
  if o.name.startswith('Body_'):o['rig_status']='Initial 22-bone preview rig; manual weight polish required'
 bpy.ops.export_scene.gltf(filepath=str(MODELS/(key+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True)
 report['models'].append({'id':key,'bones':len(data.bones),'skinned_parts':len(meshes),'tattoo_skinning':'barycentric transfer from body triangles','file':key+'.glb','bytes':(MODELS/(key+'.glb')).stat().st_size})
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
model_report.update(rigged=True,rig_status='Initial 22-bone preview rig; manual weight polish required',animation_report='animation-report.json')
for p in model_report['variants']:p['bytes']=(MODELS/(p['id']+'.glb')).stat().st_size
(ROOT/'art/3d/model-report.json').write_text(json.dumps(model_report,indent=2))
print('ANIMATION_REPORT',json.dumps(report),flush=True)
