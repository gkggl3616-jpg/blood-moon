"""Blender 4.3: derive four editable low-poly wolf variants from the Meshy source.
Tattoo motifs are original curve geometry projected onto the body, not copied textures.
"""
import bpy,sys,json,math,os
from pathlib import Path
from mathutils import Vector
ROOT=Path('/workspace/rogue-blood-moon')
SOURCE=ROOT/'meshy_output/wolf-textured.glb'
OUT=ROOT/'app/src/main/assets/models'
ART=ROOT/'art/3d'
OUT.mkdir(parents=True,exist_ok=True)
PROFILES={
 'bilge':dict(name='Boz Kagan',height=2.35,shoulder=1.02,waist=.88,depth=.94,tint=(.43,.49,.52,1),color=(1,.58,.06,1),accessory='collar'),
 'kultigin':dict(name='Kara Tigin',height=2.08,shoulder=1.24,waist=1.06,depth=1.20,tint=(.19,.23,.27,1),color=(1,.10,.12,1),accessory='shoulder'),
 'alparslan':dict(name='Boz Arslan',height=2.40,shoulder=1.38,waist=1.19,depth=1.34,tint=(.46,.43,.39,1),color=(1,.42,.05,1),accessory='collar'),
 'konuralp':dict(name='Uc Avcisi',height=2.25,shoulder=.87,waist=.78,depth=.84,tint=(.32,.24,.18,1),color=(.09,.85,.76,1),accessory='charm')}

def material(name,color,metal=0,rough=.55,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=emission
 return m

def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

clear();bpy.ops.import_scene.gltf(filepath=str(SOURCE))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
# Normalize imported transforms and combine body components; no rig is generated here.
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();base=bpy.context.object;base.name='Meshy_Wolf_Source'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
zmin=min(v.co.z for v in base.data.vertices);zmax=max(v.co.z for v in base.data.vertices);height=zmax-zmin
for v in base.data.vertices:v.co.z-=zmin;v.co/=height
original_faces=len(base.data.polygons)
# Decimate once, then reuse the same mesh data as separate editable variants.
mod=base.modifiers.new('Mobile_LOD0','DECIMATE');mod.ratio=min(1,18000/max(1,original_faces));bpy.context.view_layer.objects.active=base;bpy.ops.object.modifier_apply(modifier=mod.name)
for poly in base.data.polygons:poly.use_smooth=True
base.data.update();base.hide_render=True;base.hide_viewport=True
master=base.data.copy();source_mats=list(base.data.materials)
report={'source':'Meshy text-to-3d refine','source_faces':original_faces,'base_faces':len(master.polygons),'variants':[],'rigged':False,'tattoo_method':'separate projected emissive curve meshes','scale_unit':'meters'}
all_variants=[]
for key,p in PROFILES.items():
 c=bpy.data.collections.new('Wolf_'+key);bpy.context.scene.collection.children.link(c)
 body=bpy.data.objects.new('Body_'+key,master.copy());c.objects.link(body)
 h=p['height']
 for v in body.data.vertices:
  z=v.co.z
  upper=math.exp(-((z-.68)/.19)**2)
  waist=math.exp(-((z-.48)/.12)**2)
  xscale=1+(p['shoulder']-1)*upper+(p['waist']-1)*waist
  v.co.x*=h*xscale;v.co.y*=h*p['depth'];v.co.z*=h
 body.data.update();body['character_id']=key;body['rig_status']='Unrigged production draft';body['source_preview_task']='01a17d03-bab7-711f-b69b-c240896cfc81'
 # Keep source PBR maps, with a subtle per-variant material tint multiplier.
 for i,sm in enumerate(source_mats):
  m=sm.copy();m.name='Fur_'+key+'_'+str(i);body.data.materials[i]=m
  if m.use_nodes:
   bs=m.node_tree.nodes.get('Principled BSDF')
   if bs:
    for sockname,value in [('Metallic',0.0),('Roughness',.78)]:
     sock=bs.inputs[sockname]
     for link in list(sock.links):m.node_tree.links.remove(link)
     sock.default_value=value
    for node in m.node_tree.nodes:
     if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.35
    socket=bs.inputs['Base Color']
    if socket.is_linked:
     link=socket.links[0];source=link.from_socket;m.node_tree.links.remove(link)
     mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.35;mix.inputs[2].default_value=p['tint'];m.node_tree.links.new(source,mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],socket)
 bpy.context.view_layer.update()
 objects=[body]
 def move_to_collection(o):
  for cc in list(o.users_collection):cc.objects.unlink(o)
  c.objects.link(o);objects.append(o)
 def curve(name,coords,mat,radius=.005):
  data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=1;data.bevel_depth=radius;data.bevel_resolution=1
  sp=data.splines.new('POLY');sp.points.add(len(coords)-1)
  for pt,co in zip(sp.points,coords):pt.co=(*co,1)
  o=bpy.data.objects.new(name,data);c.objects.link(o);o.data.materials.append(mat);objects.append(o);return o
 def project(x,z,side=1):
  hit,loc,normal,_=body.ray_cast(Vector((x,side*5,z)),Vector((0,-side,0)))
  return loc+normal*.008 if hit else None
 def decal(name,pattern,slot,side=1):
  mat=material('Tattoo_'+slot+'_'+name,p['color'],rough=.35,emission=.15)
  mat['tattoo_slot']=slot;mat['roar_emission']=6.0
  # Blender timeline demonstration: 20 seconds at 30 fps; GLB is exported in idle state.
  strength=mat.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength']
  for frame,val in [(1,6),(600,6),(601,.15)]:strength.default_value=val;strength.keyframe_insert(data_path='default_value',frame=frame)
  strength.default_value=.15
  for j,line in enumerate(pattern):
   pts=[]
   for u,v in line:
    x=u*h;z=v*h;q=project(x,z,side)
    if q is not None:pts.append(q)
   if len(pts)>1:curve('Tattoo_'+slot+'_'+name+'_'+str(j),pts,mat,.0035*h)
 # Symbol geometry uses loops/branches from a common original parametrization.
 motifs={
  'dragon':[[(-.11+.04*math.sin(t*math.pi*4),.58+t*.22) for t in [i/50 for i in range(51)]],[(-.10,.76),(-.02,.82),(.07,.78),(.01,.75)],[(-.1,.65),(.06,.70),(.1,.67)]],
  'phoenix':[[(-.14,.70),(-.04,.75),(0,.79),(.04,.75),(.14,.70)], [(-.14,.76),(-.06,.73),(0,.66),(.06,.73),(.14,.76)],[(0,.78),(0,.61),(-.05,.57)],[(0,.66),(.05,.57)]],
  'lion':[[(-.10,.78),(-.14,.72),(-.09,.63),(0,.59),(.09,.63),(.14,.72),(.10,.78),(0,.81),(-.10,.78)],[(-.07,.74),(-.03,.71),(0,.72),(.03,.71),(.07,.74)],[(-.04,.66),(0,.63),(.04,.66)]],
  'pegasus':[[(-.13,.72),(-.04,.78),(0,.73),(.03,.79),(.14,.82),(.09,.74),(.03,.68),(0,.61)],[(-.04,.78),(-.09,.80),(-.11,.77),(-.06,.74)],[(0,.61),(-.04,.57)],[(.02,.65),(.08,.58)]],
  'spider':[[(-.03,.72),(0,.77),(.03,.72),(.02,.65),(0,.62),(-.02,.65),(-.03,.72)]]+[[ (sign*.02,.72-i*.025),(sign*.11,.78-i*.06),(sign*.15,.73-i*.06)] for sign in [-1,1] for i in range(4)],
  'bull':[[(-.14,.8),(-.1,.73),(-.05,.76),(0,.7),(.05,.76),(.1,.73),(.14,.8)],[(-.09,.72),(-.06,.65),(0,.60),(.06,.65),(.09,.72)],[(-.04,.67),(0,.65),(.04,.67)]]}
 for name,pattern in motifs.items():decal(name,pattern,'back')
 # Local arm tattoos on the sloped upper arm rather than the torso center.
 for sign,slot in [(-1,'left'),(1,'right')]:
  mat=material('Tattoo_'+slot+'_runes',p['color'],emission=.15)
  for k in range(3):
   coords=[]
   for i in range(16):
    t=i/15;x=sign*h*(.22+t*.07);z=h*(.70-t*.07-k*.014);q=project(x,z,1)
    if q is not None:coords.append(q)
   if len(coords)>1:curve('Tattoo_'+slot+'_runes_'+str(k),coords,mat,.003*h)
 # Modular metal/leather accessories.
 metal=material('Accessory_Bronze_'+key,(.24,.16,.065,1),metal=.72,rough=.38)
 leather=material('Accessory_Leather_'+key,(.075,.042,.025,1),rough=.8)
 bpy.ops.mesh.primitive_torus_add(major_radius=.14*h,minor_radius=.018*h,major_segments=20,minor_segments=6,location=(0,0,.80*h));o=bpy.context.object;o.name='Accessory_collar';o.scale=(1,.8,1);o.data.materials.append(metal);move_to_collection(o)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(.22*h,0,.74*h));o=bpy.context.object;o.name='Accessory_shoulder';o.scale=(.14*h,.12*h,.06*h);o.data.materials.append(metal);move_to_collection(o)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.045*h,location=(.07*h,-.14*h,.65*h));o=bpy.context.object;o.name='Accessory_charm';o.scale=(.6,.35,1.3);o.data.materials.append(metal);move_to_collection(o)
 curve('Accessory_cross_strap',[(-.16*h,-.16*h,.76*h),(.12*h,-.16*h,.46*h)],leather,.012*h)
 # Convert curve geometry once for interchange and record a real triangle budget.
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=body;bpy.ops.object.convert(target='MESH')
 objects=[o for o in c.objects if o.type=='MESH']
 for o in objects:
  if o.name.startswith('Tattoo_back_') and not o.name.startswith('Tattoo_back_dragon'):o.hide_render=True;o.hide_set(True)
  if o.name.startswith('Accessory_') and o.name not in ['Accessory_'+p['accessory'],'Accessory_cross_strap']:o.hide_render=True;o.hide_set(True)
 bpy.context.scene.frame_set(601)
 # Export all modular parts even when their default visibility is off; viewer chooses slots.
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=body
 for o in objects:o['default_visible']=not o.hide_render
 bpy.ops.export_scene.gltf(filepath=str(OUT/(key+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
 triangles=sum(sum(len(poly.vertices)-2 for poly in o.data.polygons) for o in objects)
 report['variants'].append({'id':key,'height_m':h,'triangles':triangles,'objects':len(objects),'file':key+'.glb','bytes':(OUT/(key+'.glb')).stat().st_size})
 all_variants.append((key,c,objects))
# Keep one editable scene containing all four variants, arranged for comparison.
for i,(key,c,objects) in enumerate(all_variants):
 for o in objects:o.location.x+=i*2.8;o.hide_set(o.hide_render)
bpy.data.objects.remove(base,do_unlink=True)
bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=601
bpy.context.scene.world.color=(.08,.08,.08)
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'wolves-modular.blend'))
(ART/'model-report.json').write_text(json.dumps(report,indent=2))
print('WOLF_BUILD_REPORT',json.dumps(report))
