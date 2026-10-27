"""Small internal oral meshes for legacy wolves; approved outer mesh unchanged."""
import bpy,math
from mathutils import Vector

def add_mouth(h,depth):
 if any(o.name.startswith('Mouth_') for o in bpy.context.scene.objects):return
 def material(name,color):
  m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=.72;return m
 inside=material('Mouth_Interior',(.021,.005,.010));ivory=material('Teeth_Ivory',(.70,.67,.49))
 for bone,co,scale in [('Head',(0,-.132*depth,.821),(.026,.036*depth,.016)),('Jaw',(0,-.146*depth,.806),(.025,.029*depth,.007))]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=5,location=Vector(co)*h);o=bpy.context.object;o.name='Mouth_'+bone;o.scale=Vector(scale)*h;o.data.materials.append(inside);o['skin_bone']=bone
 for side in [-1,1]:
  for j in range(4):
   for lower in [False,True]:
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=.0038*h,depth=(.013 if j==0 else .008)*h,location=(side*(.022-.002*j)*h,(-.132-.008*j)*depth*h,(.821 if not lower else .807)*h));o=bpy.context.object;o.name='Tooth';o.rotation_euler.x=0 if lower else math.pi;o.data.materials.append(ivory);o['skin_bone']='Jaw' if lower else 'Head'
 for bone in ['Head','Jaw']:
  parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('skin_bone')==bone];bpy.ops.object.select_all(action='DESELECT')
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();bpy.context.object.name='Mouth_'+bone
