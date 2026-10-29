"""Render actual exported GLBs at named clip phases, with no concept substitution."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/bilge-original-complete/views';OUT.mkdir(exist_ok=True)
form=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/'art/characters/bilge-original/working'/(form+'.glb')))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=560;s.render.resolution_y=700;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('ReviewWorld');s.world.color=(.045,.05,.065);s.view_settings.view_transform='AgX'
rig=next(o for o in s.objects if o.type=='ARMATURE');meshes=[o for o in s.objects if o.type=='MESH'];
for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
actions=list(bpy.data.actions)
print('ROUNDTRIP_ACTIONS',[(a.name,list(a.frame_range)) for a in actions])
def action(name):
 a=next(a for a in actions if a.name==name or a.name.startswith(name+'_') or a.name.endswith('_'+name) or a.name.endswith('|'+name))
 rig.animation_data.action=a;return a
idle='LSt' if form=='wolf' else 'UI_Default_Idle';action(idle);s.frame_set(0);bpy.context.view_layer.update()
coords=[o.matrix_world@v.co for o in meshes for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));center=(lo+hi)/2;height=hi.z-lo.z
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));floor=bpy.context.object;m=bpy.data.materials.new('ReviewFloor');m.diffuse_color=(.065,.08,.1,1);floor.data.materials.append(m)
for co,energy,size in [((3,-4,5),700,4),((-3,-1,3),400,3),((0,3,5),650,3)]:
 bpy.ops.object.light_add(type='AREA',location=co);o=bpy.context.object;o.data.energy=energy;o.data.size=size;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=max(2.6,height*1.22)
s.render.image_settings.file_format='PNG'
records=[]
def render(clip,phase,view,label):
 a=action(clip);f=a.frame_range[0]+(a.frame_range[1]-a.frame_range[0])*phase;s.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
 offset={'front':(0,-5,.15),'back':(0,5,.15),'side':(5,0,.15),'three':(3,-5,.2)}[view]
 cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(OUT/f'{form}-{label}.png');bpy.ops.render.render(write_still=True)
 records.append({'form':form,'clip':clip,'phase':phase,'frame':f,'view':view,'file':Path(s.render.filepath).name})
for view in (['front'] if '--quick' in sys.argv else ['front','back','side']):render(idle,.2,view,'idle-'+view)
if form=='wolf' and '--quick' not in sys.argv:
 for clip,label in [('T_CRY','roar'),('LRF','run-native'),('T_Specialatk','roll'),('LWF','walk')]:
  for i,phase in enumerate([0,.25,.5,.75,1]):render(clip,phase,'three',label+f'-{i}')
elif form!='wolf' and '--quick' not in sys.argv:
 for i,phase in enumerate([0,.25,.5,.75,1]):render('LWF',phase,'three',f'walk-{i}')
(OUT/f'{form}-frames.json').write_text(json.dumps(records,indent=2))
