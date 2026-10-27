"""Build mobile LODs from the approved Bilge pair and existing wolf sources.
No remote calls: approved Meshy sources are supplied as local GLBs.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'art/3d';OUT=ART/'source/mobile-v019';OUT.mkdir(parents=True,exist_ok=True)
profiles=[{'id':'bilge','kind':'wolf','height_m':2.25,'source':'meshy_output/bilge-v019/bilge-wolf.glb','target':12000,'new':True,'has_tail':False},
 {'id':'kultigin','kind':'wolf','height_m':2.08,'source':'art/3d/source/athletic-static/kultigin.glb','target':8200,'has_tail':True},
 {'id':'alparslan','kind':'wolf','height_m':2.4,'source':'art/3d/source/athletic-static/alparslan.glb','target':8200,'has_tail':True},
 {'id':'konuralp','kind':'wolf','height_m':2.25,'source':'art/3d/source/athletic-static/konuralp.glb','target':8200,'has_tail':True},
 {'id':'human-bilge','kind':'human','height_m':1.85,'source':'meshy_output/bilge-v019/bilge-human.glb','target':9000,'new':True,'has_tail':False}]
report={'source':'Approved Bilge image-to-3D pair and existing Meshy/Blender wolf variants','static_source_dir':'art/3d/source/mobile-v019','variants':[],'rigged':False,'tattoo_method':'one skinned surface per slot, shared atlas with runtime UV selection','scale_unit':'meters','new_meshy_credits':60}
rect=[0,0,426,431];atlas_w,atlas_h=1274,1234
for profile in profiles:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.data.orphans_purge(do_recursive=True)
 key=profile['id'];h=profile['height_m'];bpy.ops.import_scene.gltf(filepath=str(ROOT/profile['source']))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 # Discard duplicate tattoo geometry before constructing one shared UV surface.
 for o in list(meshes):
  if o.name.startswith('Tattoo_'):bpy.data.objects.remove(o,do_unlink=True);meshes.remove(o)
 body=next((o for o in meshes if o.name.startswith('Body_')),meshes[0])
 if profile.get('new'):
  bpy.ops.object.select_all(action='DESELECT')
  for o in meshes:o.select_set(True)
  bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body=bpy.context.object;meshes=[body]
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  coords=[v.co.copy() for v in body.data.vertices];lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)));hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)));scale=h/(hi.z-lo.z);center=(lo+hi)/2
  for v in body.data.vertices:v.co=Vector(((v.co.x-center.x)*scale,(v.co.y-center.y)*scale,(v.co.z-lo.z)*scale))
  del coords
 body.name='Body_'+key
 for o in meshes:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 before=len(body.data.polygons);bpy.context.view_layer.objects.active=body
 mod=body.modifiers.new('MobileBudget','DECIMATE');mod.ratio=min(1,profile['target']/max(1,before));mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 for poly in body.data.polygons:poly.use_smooth=True
 body.data.update();body['character_id']=key;body['source_kind']='new approved Meshy image model' if profile.get('new') else 'existing model, optimized';body['rig_status']='Mobile rig input'
 # Base color retains 2K, normal 1K, scalar maps <=512 to bound GPU memory.
 images={}
 for material in body.data.materials:
  if not material or not material.use_nodes:continue
  for node in material.node_tree.nodes:
   if node.type!='TEX_IMAGE' or not node.image:continue
   image=node.image;cap=2048 if image.colorspace_settings.name=='sRGB' else 1024
   for link in node.outputs['Color'].links:
    if link.to_node.type=='SEPARATE_COLOR' or 'Rough' in link.to_socket.name or 'Metallic' in link.to_socket.name:cap=512
   images[image.name]=(image,min(cap,images.get(image.name,(None,cap))[1]))
 texture_dir=OUT/'textures';texture_dir.mkdir(exist_ok=True)
 for index,(image,cap) in enumerate(images.values()):
  w,hh=image.size;colorspace=image.colorspace_settings.name
  if not w or not hh:raise RuntimeError('Source image has no data: '+image.name)
  if max(w,hh)>cap:image.scale(int(w*cap/max(w,hh)),int(hh*cap/max(w,hh)))
  # Reload a real resized PNG: copied packed images can lose their pixel data
  # in Blender's glTF exporter after image.scale().
  path=texture_dir/(key+'-'+str(index)+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save()
  replacement=bpy.data.images.load(str(path),check_existing=False);replacement.colorspace_settings.name=colorspace;replacement.pack()
  for material in body.data.materials:
   if material and material.use_nodes:
    for node in material.node_tree.nodes:
     if node.type=='TEX_IMAGE' and node.image==image:node.image=replacement
 objects=list(meshes)
 if profile['kind']=='wolf':
  atlas=bpy.data.images.load(str(ART/'textures/tattoo-atlas.png'),check_existing=True);atlas.pack()
  def surface(slot,x0,x1,z0,z1):
   mat=bpy.data.materials.new('Tattoo_'+slot+'_atlas');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas
   for out,sock in [('Color','Base Color'),('Color','Emission Color'),('Alpha','Alpha')]:mat.node_tree.links.new(tex.outputs[out],bs.inputs[sock])
   bs.inputs['Emission Strength'].default_value=.15;mat.surface_render_method='DITHERED';mat.use_backface_culling=True
   verts=[];uv=[];faces=[];lookup={}
   for poly in body.data.polygons:
    if poly.normal.y<.08:continue
    points=[]
    for index in poly.vertices:
     co=body.data.vertices[index].co/h;v=(co.z-z0)/(z1-z0)
     if not 0<=v<=1:break
     width=(x1-x0)*(.58+.42*v**.6) if slot=='back' else x1-x0;u=(co.x-(x0+x1)/2)/width+.5
     if not 0<=u<=1:break
     points.append((index,u,v))
    if len(points)!=len(poly.vertices):continue
    face=[]
    for index,u,v in points:
     if index not in lookup:
      lookup[index]=len(verts);vertex=body.data.vertices[index];verts.append(vertex.co+vertex.normal*(.0008*h));uv.append(((rect[0]+u*(rect[2]-rect[0]))/atlas_w,1-(rect[3]-v*(rect[3]-rect[1]))/atlas_h))
     face.append(lookup[index])
    faces.append(face)
   mesh=bpy.data.meshes.new('TattooSurface');mesh.from_pydata(verts,[],faces);mesh.update();layer=mesh.uv_layers.new(name='TattooUV')
   for poly in mesh.polygons:
    poly.use_smooth=True
    for li in poly.loop_indices:layer.data[li].uv=uv[mesh.loops[li].vertex_index]
   obj=bpy.data.objects.new('Tattoo_'+slot+'_surface',mesh);bpy.context.scene.collection.objects.link(obj);obj.data.materials.append(mat);obj['atlas_uv_base']=[rect[0]/atlas_w,1-rect[3]/atlas_h,(rect[2]-rect[0])/atlas_w,(rect[3]-rect[1])/atlas_h];objects.append(obj)
  surface('back',-.16,.16,.545,.823)
  for name,side in [('left',-1),('right',1)]:
   # New Bilge has lowered A-pose hands; old wolves keep their wider A-pose.
   x0,x1=sorted([side*.19,side*(.32 if profile.get('new') else .36)])
   surface(name,x0,x1,.46 if profile.get('new') else .54,.72)
 # Remove source camera/lights/empty objects from exports.
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=body
 bpy.ops.export_scene.gltf(filepath=str(OUT/(key+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
 triangle_count=sum(sum(len(poly.vertices)-2 for poly in o.data.polygons) for o in objects)
 # Torso center and arm pivots for this source's A pose, in normalized units.
 joints={}
 if profile.get('new'):
  for side,sign in [('L',1),('R',-1)]:
   for part,z,fallback in [('shoulder',.75,.17),('elbow',.61,.245),('wrist',.44,.29),('finger',.375,.31)]:
    selected=[v.co/h for v in body.data.vertices if abs(v.co.z/h-z)<.018 and .16<v.co.x/h*sign<.43]
    if selected:
     xs=sorted(v.x for v in selected);ys=sorted(v.y for v in selected);joints[part+side]=[xs[len(xs)//2],ys[len(ys)//2],z]
    else:joints[part+side]=[sign*fallback,0,z]
 if profile['kind']=='human':
  joints={}
  for side,sg in [('L',1),('R',-1)]:
   for part,x,y,z in [('shoulder',.17,-.02,.775),('elbow',.265,-.04,.66),('wrist',.33,-.075,.565),('finger',.35,-.09,.52)]:joints[part+side]=[sg*x,y,z]
 if not profile.get('new'):profile['shape_profile']=json.loads((ART/'legacy-shape-profiles.json').read_text()).get(key,{})
 report['variants'].append({**{k:v for k,v in profile.items() if k not in ['source','target']},'file':key+'.glb','source_faces':before,'triangles':triangle_count,'body_triangles':len(body.data.polygons),'objects':len(objects),'rest_joints':joints,'bytes':(OUT/(key+'.glb')).stat().st_size})
 print('MOBILE_LOD',key,'source',before,'triangles',triangle_count,flush=True)
 # A standalone editable optimized source per character; no 100MB raw mesh is committed.
 bpy.data.orphans_purge(do_recursive=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(ART/(key+'-mobile.blend')),compress=True)
(ROOT/'art/3d/model-report.json').write_text(json.dumps(report,indent=2))
print('MOBILE_REPORT_READY',flush=True)
