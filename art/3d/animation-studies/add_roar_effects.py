"""Study-only, hand-anchored flame sprites + tattoo pulse + timed energy streaks.
Bake separate palette-controlled effects; none change the underlying skin mesh.
"""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path('/workspace/rogue-blood-moon');D=R/'dist/roar-study-03';s=bpy.context.scene;rig=bpy.data.objects['BilgeRigify'];ref=json.loads((R/'art/3d/animation-studies/reference_roar_38.json').read_text())
# A small generated flame alpha texture; packed in .blend. No external image dependency.
w,hh=128,192;yy,xx=np.mgrid[0:hh,0:w];u=(xx/(w-1)-.5)*2;v=yy/(hh-1)
center=.13*np.sin(v*14)+.07*np.sin(v*31);width=.32*(1-v)**.6+.02
shape=np.exp(-((u-center)/width)**2*2)*np.sin(np.pi*np.clip(v*1.02,0,1))**.45
wisps=.65+.22*np.sin(v*53+u*9)+.13*np.sin(v*27-u*23);alpha=np.clip(shape*wisps*1.5,0,1)
color=np.zeros((hh,w,4),dtype=np.float32);color[:,:,:3]=1;color[:,:,3]=alpha
im=bpy.data.images.new('RoarFlameAlpha',width=w,height=hh,alpha=True);im.pixels.foreach_set(color.ravel());im.pack()
fx=bpy.data.collections.new('ROAR_FX');s.collection.children.link(fx)
def move_collection(obj):
 for c in list(obj.users_collection):c.objects.unlink(obj)
 fx.objects.link(obj)
def sprite_mat(name,rgb,energy):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');tex=n.new('ShaderNodeTexImage');tex.image=im;emit=n.new('ShaderNodeEmission');emit.inputs[0].default_value=(*rgb,1);emit.inputs[1].default_value=energy;trans=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');m.node_tree.links.new(tex.outputs['Alpha'],mix.inputs[0]);m.node_tree.links.new(trans.outputs[0],mix.inputs[1]);m.node_tree.links.new(emit.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs[0]);return m
cyan=sprite_mat('BilgeFlame_Cyan',(.08,.62,1),4);violet=sprite_mat('RoarFlame_Violet',(.38,.045,1),2.5)
random.seed(84);flames=[]
for side in ['L','R']:
 for j in range(6):
  mesh=bpy.data.meshes.new(f'FlameRibbon{side}{j}');mesh.from_pydata([(-.5,0,0),(.5,0,0),(.5,0,1),(-.5,0,1)],[],[(0,1,2,3)]);mesh.uv_layers.new();uvs=[(0,0),(1,0),(1,1),(0,1)]
  for li,vi in enumerate(mesh.polygons[0].vertices):mesh.uv_layers[0].data[li].uv=uvs[vi]
  obj=bpy.data.objects.new(f'HandFlame.{side}.{j}',mesh);fx.objects.link(obj);obj.data.materials.append(violet if j%3==0 else cyan);flames.append((obj,side,j,random.random()*6))
# Share the exact hand path; float upward in world space, not sideways when the palm rotates.
pts=np.array([r[1] for r in ref['samples']]);fl=np.array([r[11] for r in ref['samples']]);pulse=np.array([r[12] for r in ref['samples']])
for f in range(52):
 s.frame_set(f);bpy.context.view_layer.update();t=f/30;env=float(np.interp(t,pts,fl))
 for obj,side,j,seed in flames:
  bone=rig.pose.bones['DEF-hand.'+side];p=rig.matrix_world@(bone.head.lerp(bone.tail,.5));wave=math.sin(t*13+seed)
  obj.location=p+Vector((math.cos(seed)*.075,math.sin(seed)*.065,.02+(j%3)*.025));obj.rotation_euler=(0,0,seed*.16+wave*.18)
  # Two crossed world-upright sprite planes keep flames visible in front/side views.
  obj.rotation_euler.z=(j%2)*math.pi/2+.2*wave
  height=(.19+.11*(j%3))*(.9+.12*wave)*env;width=(.105+.035*(j%2))*env
  obj.scale=(width,1,height);obj.keyframe_insert('location',frame=f);obj.keyframe_insert('rotation_euler',frame=f);obj.keyframe_insert('scale',frame=f)
# Tattoo pulse follows the skin material, with its original texture as emission mask.
tattoos=[]
for obj in list(s.objects):
 if not obj.name.startswith('Tattoo'):continue
 for slot in obj.material_slots:
  if not slot.material:continue
  mat=slot.material.copy();slot.material=mat;bs=mat.node_tree.nodes.get('Principled BSDF')
  if not bs:continue
  base=bs.inputs['Base Color'];em=bs.inputs['Emission Color']
  if base.is_linked:mat.node_tree.links.new(base.links[0].from_socket,em)
  else:em.default_value=base.default_value
  for f in range(52):
   t=f/30;strength=float(np.interp(t,pts,pulse));strength*=max(0,1-(t-1.522)/.178) if t>1.522 else 1
   bs.inputs['Emission Strength'].default_value=2.2*strength;bs.inputs['Emission Strength'].keyframe_insert('default_value',frame=f)
  tattoos.append(obj.name)
# Crossing energy streak: separate late envelope from the original footage, no broad body bloom.
streakmat=sprite_mat('BilgeEnergyTail',(.06,.8,1),2.0);streaks=[]
for j in range(2):
 bpy.ops.mesh.primitive_plane_add(size=1);obj=bpy.context.object;obj.name='RoarEnergyStreak'+str(j);move_collection(obj);obj.data.materials.append(streakmat);obj.rotation_euler=(math.pi/2,(-1 if j else 1)*.36,0);streaks.append(obj)
 for f in range(52):
  t=f/30;env=max(0,math.sin(math.pi*(t-1.13)/.5)) if 1.13<t<1.63 else 0
  obj.location=(.05, .24,1.52+(-1 if j else 1)*.07+max(0,t-1.13)*.1);obj.scale=(1.25*env,.14*env,1);obj.keyframe_insert('location',frame=f);obj.keyframe_insert('scale',frame=f)
# Mild bloom only; no full-screen flash.
s.use_nodes=True;nodes=s.node_tree.nodes;nodes.clear();rl=nodes.new('CompositorNodeRLayers');glow=nodes.new('CompositorNodeGlare');glow.glare_type='FOG_GLOW';glow.quality='MEDIUM';glow.threshold=2;glow.size=6;glow.mix=-.90;out=nodes.new('CompositorNodeComposite');s.node_tree.links.new(rl.outputs['Image'],glow.inputs[0]);s.node_tree.links.new(glow.outputs['Image'],out.inputs[0])
s.frame_set(8);bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(R/'art/3d/animation-studies/bilge-roar-study-03.blend'),compress=True)
(D/'effects.json').write_text(json.dumps({'hand_flame_sprites':len(flames),'hand_bones':['DEF-hand.L','DEF-hand.R'],'tattoo_meshes':tattoos,'palette':'Bilge cyan with violet flame edges','reference_timing':'38 sample timestamps, full 1.7s including recovery and late streak','new_credits':0,'runtime_installed':False},indent=2));print('FX03_READY',tattoos)
