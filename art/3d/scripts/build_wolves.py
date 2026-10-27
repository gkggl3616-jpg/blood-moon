"""Blender 4.3: derive four editable low-poly wolf variants from the Meshy source.
Athletic torso sculpt and original alpha ink projected onto the body surface.
"""
import bpy,sys,json,math,os
from pathlib import Path
from mathutils import Vector
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'meshy_output/wolf-textured.glb'
OUT=ROOT/'app/src/main/assets/models'
ART=ROOT/'art/3d'
OUT.mkdir(parents=True,exist_ok=True)
STATIC=ART/'source/athletic-static';STATIC.mkdir(parents=True,exist_ok=True)
PROFILES={
 'bilge':dict(name='Boz Kagan',height=2.35,shoulder=1.08,waist=.88,depth=.98,waist_depth=.80,tint=(.68,.75,.84,1),color=(1,.58,.06,1),accessory='collar'),
 'kultigin':dict(name='Kara Tigin',height=2.08,shoulder=1.24,waist=.94,depth=1.08,waist_depth=.78,tint=(.48,.57,.70,1),color=(1,.10,.12,1),accessory='shoulder'),
 'alparslan':dict(name='Boz Arslan',height=2.40,shoulder=1.34,waist=.99,depth=1.15,waist_depth=.80,tint=(.78,.69,.57,1),color=(1,.42,.05,1),accessory='collar'),
 'konuralp':dict(name='Uc Avcisi',height=2.25,shoulder=.97,waist=.84,depth=.91,waist_depth=.77,tint=(.62,.69,.59,1),color=(.09,.85,.76,1),accessory='charm')}

def shape_point(co,p):
 x,y,z=co
 upper=math.exp(-((z-.715)/.105)**2)
 waist=math.exp(-((z-.545)/.075)**2)
 trunk=max(0,min(1,(.235-abs(x))/.065))
 xs=1+(p['shoulder']-1)*upper+(p['waist']-1)*waist*trunk
 ys=p['depth']*(1+(p['waist_depth']-1)*waist*trunk)
 return Vector((x*xs,y*ys,z))*p['height']

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
mod=base.modifiers.new('Mobile_LOD0','DECIMATE');mod.ratio=min(1,28000/max(1,original_faces));bpy.context.view_layer.objects.active=base;bpy.ops.object.modifier_apply(modifier=mod.name)
for poly in base.data.polygons:poly.use_smooth=True
base.data.update();base.hide_render=True;base.hide_viewport=True
master=base.data.copy();source_mats=list(base.data.materials)
report={'source':'Existing Meshy refine; athletic sculpt v2','source_faces':original_faces,'base_faces':len(master.polygons),'variants':[],'rigged':False,'tattoo_method':'skin-triangle alpha ink; nine detailed back motifs','new_meshy_credits':0,'static_source_dir':'art/3d/source/athletic-static','scale_unit':'meters'}
atlas=bpy.data.images.load(str(ART/'textures/tattoo-atlas.png'));atlas.pack()
rects={'dragon':[0,0,426,431],'phoenix':[428,0,847,430],'lion':[848,0,1274,431],
 'pegasus':[0,431,428,826],'spider':[429,431,845,826],'bull':[846,431,1274,826],
 'dice':[0,827,427,1234],'unicorn':[428,827,846,1234],'reaper':[847,827,1274,1234]}
(ART/'textures/tattoo-atlas.json').write_text(json.dumps({'texture':'tattoo-atlas.png','size':list(atlas.size),'rects_top_left_pixels':rects,'method':'original generated alpha ink; surface-projected UV patches','source':'OpenAI image generation'},indent=2))
all_variants=[]
for key,p in PROFILES.items():
 c=bpy.data.collections.new('Wolf_'+key);bpy.context.scene.collection.children.link(c)
 body=bpy.data.objects.new('Body_'+key,master.copy());c.objects.link(body)
 h=p['height']
 before=np.array([tuple(v.co) for v in body.data.vertices])
 for v in body.data.vertices:v.co=shape_point(v.co,p)
 body.data.update();body['character_id']=key;body['rig_status']='Unrigged athletic source';body['proportion_revision']='Athletic V2: tapered waist and abdomen, shoulder mass preserved';body['source_preview_task']='01a17d03-bab7-711f-b69b-c240896cfc81'
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
     if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.5
    socket=bs.inputs['Base Color']
    if socket.is_linked:
     link=socket.links[0];source=link.from_socket;m.node_tree.links.remove(link)
     mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=p['tint'];m.node_tree.links.new(source,mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],socket)
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
 def project(x,z):
  hit,loc,normal,_=body.ray_cast(Vector((x,5*h,z)),Vector((0,-1,0)))
  return loc+normal*(.0015*h) if hit and normal.y>.1 else None
 def ink_patch(motif,slot,x0,x1,z0,z1,nx=20,nz=26):
  mat=material('Tattoo_'+slot+'_'+motif,(1,1,1,1),rough=.85)
  bs=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas
  mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Emission Color'])
  mat.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
  bs.inputs['Emission Strength'].default_value=.12
  mat.surface_render_method='DITHERED';mat.use_backface_culling=True
  rect=rects['phoenix' if motif=='runes' else motif];iw,ih=atlas.size
  # Copy the real skin triangles, not a coarse plane bridging fur ridges.
  verts=[];uv=[];faces=[];indices={}
  for poly in body.data.polygons:
   if poly.normal.y<.08:continue
   face_uv=[]
   for vi in poly.vertices:
    co=body.data.vertices[vi].co/h;v=(co.z-z0)/(z1-z0)
    if not 0<=v<=1:break
    span=(x1-x0)*(.58+.42*v**.6) if slot=='back' else x1-x0
    u=(co.x-(x0+x1)/2)/span+.5
    if not 0<=u<=1:break
    face_uv.append((vi,u,v))
   if len(face_uv)!=len(poly.vertices):continue
   face=[]
   for vi,u,v in face_uv:
    if vi not in indices:
     source=body.data.vertices[vi];indices[vi]=len(verts)
     verts.append(source.co+source.normal*(.0007*h))
     uv.append(((rect[0]+2+(rect[2]-rect[0]-4)*u)/iw,1-(rect[3]-2-(rect[3]-rect[1]-4)*v)/ih))
    face.append(indices[vi])
   faces.append(face)
  mesh=bpy.data.meshes.new('InkSurface');mesh.from_pydata(verts,[],faces);mesh.update();uv_layer=mesh.uv_layers.new(name='TattooUV')
  for poly in mesh.polygons:
   poly.use_smooth=True
   for li in poly.loop_indices:uv_layer.data[li].uv=uv[mesh.loops[li].vertex_index]
  o=bpy.data.objects.new('Tattoo_'+slot+'_'+motif+'_ink',mesh);c.objects.link(o);o.data.materials.append(mat);objects.append(o)
  o['slot']=slot;o['motif']=motif
 for motif in rects:ink_patch(motif,'back',-.16,.16,.545,.823)
 for side,sg in [('left',-1),('right',1)]:
  a=shape_point((sg*.205,0,.71),p);b=shape_point((sg*.315,0,.59),p);x0,x1=sorted([a.x/h,b.x/h])
  for motif in ['runes','dragon','phoenix','reaper']:ink_patch(motif,side,x0,x1,.59,.715,14,18)
 # Modular metal/leather accessories.
 metal=material('Accessory_Bronze_'+key,(.24,.16,.065,1),metal=.72,rough=.38)
 leather=material('Accessory_Leather_'+key,(.075,.042,.025,1),rough=.8)
 bpy.ops.mesh.primitive_torus_add(major_radius=.083*h,minor_radius=.012*h,major_segments=20,minor_segments=6,location=(0,.017*h,.805*h));o=bpy.context.object;o.name='Accessory_collar';o.scale=(1,.8,1);o.data.materials.append(metal);move_to_collection(o)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=shape_point((.22,0,.74),p));o=bpy.context.object;o.name='Accessory_shoulder';o.scale=(.14*h,.12*h,.06*h);o.data.materials.append(metal);move_to_collection(o)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.045*h,location=(.07*h,-.14*h,.65*h));o=bpy.context.object;o.name='Accessory_charm';o.scale=(.6,.35,1.3);o.data.materials.append(metal);move_to_collection(o)
 # Flat leather ribbon projected onto the front torso, with no floating rod.
 strap_verts=[];strap_faces=[]
 for i in range(33):
  t=i/32
  for offset in [-.011,.011]:
   x=(-.15*(1-t)+.10*t+offset)*h;z=(.76*(1-t)+.49*t+offset*.7)*h
   hit,loc,n,_=body.ray_cast(Vector((x,-5*h,z)),Vector((0,1,0)))
   strap_verts.append(loc+n*(.0018*h) if hit else Vector((x,-.12*h,z)))
  if i:strap_faces.append((2*i-2,2*i,2*i+1,2*i-1))
 data=bpy.data.meshes.new('LeatherRibbon');data.from_pydata(strap_verts,[],strap_faces);data.update()
 o=bpy.data.objects.new('Accessory_cross_strap',data);c.objects.link(o);o.data.materials.append(leather);objects.append(o)
 # Convert curve geometry once for interchange and record a real triangle budget.
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=body;bpy.ops.object.convert(target='MESH')
 objects=[o for o in c.objects if o.type=='MESH']
 for o in objects:
  if o.name.startswith('Tattoo_') and not o.name.startswith(('Tattoo_back_dragon_','Tattoo_left_runes_','Tattoo_right_runes_')):o.hide_render=True;o.hide_set(True)
  if o.name.startswith('Accessory_') and not (o.name=='Accessory_'+p['accessory'] or o.name=='Accessory_cross_strap' and p['accessory']=='charm'):o.hide_render=True;o.hide_set(True)
 bpy.context.scene.frame_set(601)
 # Export all modular parts even when their default visibility is off; viewer chooses slots.
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=body
 for o in objects:o['default_visible']=not o.hide_render
 bpy.ops.export_scene.gltf(filepath=str(STATIC/(key+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
 triangles=sum(sum(len(poly.vertices)-2 for poly in o.data.polygons) for o in objects)
 after=np.array([tuple(v.co) for v in body.data.vertices])/h
 trunk=(np.abs(before[:,0])<.16)&(np.abs(before[:,1])<.18)
 def section(z):
  selected=after[trunk&(abs(before[:,2]-z)<.013)]
  return {'width':round(float(np.ptp(selected[:,0])),4),'depth':round(float(np.ptp(selected[:,1])),4)}
 report['variants'].append({'id':key,'height_m':h,'triangles':triangles,'objects':len(objects),'shape_profile':p,'normalized_trunk_sections':{'waist':section(.545),'chest':section(.715)},'file':key+'.glb','bytes':(STATIC/(key+'.glb')).stat().st_size})
 all_variants.append((key,c,objects))
# Keep one editable scene containing all four variants, arranged for comparison.
for i,(key,c,objects) in enumerate(all_variants):
 for o in objects:o.location.x+=i*2.8;o.hide_set(o.hide_render)
bpy.data.objects.remove(base,do_unlink=True)
bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=601
bpy.context.scene.world.color=(.08,.08,.08)
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ART/'wolves-modular.blend'),compress=True)
(ART/'model-report.json').write_text(json.dumps(report,indent=2))
print('WOLF_BUILD_REPORT',json.dumps(report))
