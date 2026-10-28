"""Blender: capture the delivered GLB, not a concept image or separate menu mesh."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];key=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'bilge';OUT=R/('dist/model-review' if key=='bilge' else 'dist/model-review-'+key);OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/f'app/src/main/assets/models/{key}.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');tracks=list(rig.animation_data.nla_tracks)
for t in tracks:t.mute=True
for o in bpy.context.scene.objects:
 if o.name.startswith('Accessory_'):o.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=6;scene.cycles.use_denoising=False;scene.cycles.device='CPU';scene.render.fps=30;scene.world.color=(.10,.10,.10)
for co,power,size in [((3,-4,5),550,4),((-3,-2,3),350,3),((1,4,4),650,3)]:
 bpy.ops.object.light_add(type='AREA',location=co);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=2.8;scene.render.resolution_x=480;scene.render.resolution_y=480;scene.render.resolution_percentage=100
views={'front':(0,-5,1.4),'back':(0,5,1.4),'side':(5,0,1.4),'three-quarter':(3,-4,1.6)}
shots=[]
sequence=[('WolfIdle',[0]),('WolfRunQuad',[0,.125,.25,.375,.5,.625,.75,.875]),('WolfRoll',[0,.15,.3,.45,.6,.75,.9]),('WolfRoar',[0,.15,.30,.50,.67,.82,1])]
if '--roar-only' in sys.argv:sequence=[sequence[-1]]
for clip,fractions in sequence:
 track=next(t for t in tracks if t.name==clip);rig.animation_data.action=track.strips[0].action;lo,hi=rig.animation_data.action.frame_range
 for fraction in fractions:
  f=lo+(hi-lo)*fraction;scene.frame_set(int(f),subframe=f%1)
  for view in (views if clip in ['WolfIdle','WolfRoar'] else ['three-quarter']):
   camera.data.ortho_scale=3.15 if clip=='WolfRoar' else 2.8;camera.location=views[view];camera.rotation_euler=(Vector((0,0,1.30 if clip=='WolfRoar' else 1.1))-camera.location).to_track_quat('-Z','Y').to_euler();name=f'{clip}-{int(fraction*100):02}-{view}';scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);shots.append(name)
(OUT/'shots.json').write_text(json.dumps(shots))
