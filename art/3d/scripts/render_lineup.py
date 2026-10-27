import bpy,math
from mathutils import Vector
from pathlib import Path
root=Path('/workspace/rogue-blood-moon/art/3d')
bpy.ops.wm.open_mainfile(filepath=str(root/'wolves-modular.blend'))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=False
scene.render.resolution_x=1440;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.065,.085,.11,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.mesh.primitive_plane_add(size=200,location=(4,0,-.03));ground=bpy.context.object;ground.name='Render_Ground'
m=bpy.data.materials.new('Ground');m.diffuse_color=(.025,.035,.05,1);ground.data.materials.append(m)
for loc,power,size in [((3,-5,6),1800,7),((5,5,5),2000,6),((-3,1,4),900,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;light.rotation_euler=(Vector((4,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4.2,-11,3.3));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=11.8;scene.camera=cam
for view,y,frame in [('front',-11,601),('back-roar',11,1)]:
 scene.frame_set(frame);cam.location=(4.2,y,3.3);cam.rotation_euler=(Vector((4.2,0,1.2))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(root/('wolves-'+view+'.png'));bpy.ops.render.render(write_still=True)
