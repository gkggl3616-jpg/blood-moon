"""Attach generated UV/PBR to the original native rig/mesh.
Meshy coordinates are registered to the frozen input by its uniform AABB
normalization; geometry agreement is asserted. Copy UV per source triangle,
never interpolate UVs from unrelated islands or regenerate a rig/animation.
"""
import bpy,bmesh,sys,json,struct,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import barycentric_transform
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as ex
form=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'wolf';O=R/'art/characters/karahan';D=R/'docs/karahan-v0118'
folder='20261029_184802_karahan-battle-wolf-pbr_01a188fc' if form=='wolf' else '20261029_183440_karahan-human-pbr_01a188f0';input_path=O/'texture-inputs'/('wolf-battle-v2.glb' if form=='wolf' else 'human-texture-input.glb');output_path=R/'meshy_output'/folder/f'karahan-{form}-textured.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(input_path));original_points=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices];lo=Vector(tuple(min(p[i] for p in original_points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in original_points) for i in range(3)));center=(lo+hi)/2
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(output_path));donor=next(o for o in bpy.context.scene.objects if o.type=='MESH');donor.data.calc_loop_triangles();world=[donor.matrix_world@v.co for v in donor.data.vertices];out_lo=Vector(tuple(min(p[i] for p in world) for i in range(3)));out_hi=Vector(tuple(max(p[i] for p in world) for i in range(3)));out_center=(out_hi+out_lo)/2;scale=max(hi-lo)/max(out_hi-out_lo);registered=[(p-out_center)*scale+center for p in world];tree=KDTree(len(original_points))
for i,p in enumerate(original_points):tree.insert(p,i)
tree.balance();error=max(tree.find(p)[2] for p in registered);assert error<.0001,('geometry changed rather than texture only',form,error)
triangles=[tuple(t.vertices) for t in donor.data.loop_triangles];uvs=[[donor.data.uv_layers.active.data[i].uv.copy() for i in t.loops] for t in donor.data.loop_triangles];surface=BVHTree.FromPolygons(registered,triangles,all_triangles=True)
# Keep the one generated material/images alive across scene replacement.
source_material=donor.data.materials[0];source_material.use_fake_user=True
for node in source_material.node_tree.nodes:
 if node.type=='TEX_IMAGE' and node.image:
  im=node.image;im.use_fake_user=True
  if im.colorspace_settings.name!='sRGB':
   normal=any(link.to_node.type=='NORMAL_MAP' for link in node.outputs['Color'].links);limit=2048 if normal else 1024
   if max(im.size)>limit:im.scale(limit,limit)
  im.pack()
# Append native production scene without losing the downloaded material.
with bpy.data.libraries.load(str(O/(form+'-static.blend')),link=False) as (src,dst):dst.objects=list(src.objects)
for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
for obj in dst.objects:
 if obj is not None:bpy.context.collection.objects.link(obj)
bpy.context.view_layer.update();materials={};rough_images={};reports=[]
def kind_for(obj,old):
 if form=='human':
  return 'Skin' if any(s in obj.name for s in ['_Head','_Hand']) else 'Leather' if '_Shoes' in obj.name else 'Cloth' if '_Lowerbody' in obj.name else 'Metal'
 if obj.name.startswith('Cloth_'):return 'Cloth'
 if obj.name.startswith('Behamah_'):return 'Keratin'
 kind=old.rsplit('_',1)[-1]
 if kind=='Pants':return 'Fur' # Intact fur body below the separate torn cloth.
 return kind if kind in ['Fur','Teeth','Mouth','Eyes','Nose','Claws','Bracer'] else 'Fur'
def material(kind):
 if kind in materials:return materials[kind]
 m=source_material.copy();m.name='Karahan_'+form+'_'+kind;m.use_fake_user=False;p=m.node_tree.nodes.get('Principled BSDF')
 for n in m.node_tree.nodes:
  if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.55 if kind=='Fur' else .65
 if kind not in ['Metal','Bracer']:
  for link in list(p.inputs['Metallic'].links):m.node_tree.links.remove(link)
  p.inputs['Metallic'].default_value=0
 # Clamp material roughness using a small dedicated packed map. Albedo remains
 # true 4K, normal 2K and roughness/metal 1K to bound mobile texture memory.
 floor=.80 if kind in ['Fur','Cloth'] else .62 if kind in ['Skin','Leather','Keratin','Nose','Claws'] else .48 if kind=='Mouth' else .35
 for node in m.node_tree.nodes:
  if node.type!='TEX_IMAGE' or not node.image or node.image.colorspace_settings.name=='sRGB':continue
  if any(link.to_node.type=='NORMAL_MAP' for link in node.outputs['Color'].links):continue
  key=(node.image.name,kind)
  if key not in rough_images:
   im=node.image.copy();im.name='Karahan_'+form+'_'+kind+'_ORM';pixels=np.array(im.pixels[:],dtype=np.float32).reshape(-1,4);pixels[:,1]=np.maximum(pixels[:,1],floor)
   if kind not in ['Metal','Bracer']:pixels[:,2]=0
   im.pixels.foreach_set(pixels.ravel());im.pack();rough_images[key]=im
  node.image=rough_images[key]
 if kind=='Mouth':
  # Interior only: no emissive exterior red oval, no overbright oral surfaces.
  for link in list(p.inputs['Base Color'].links):m.node_tree.links.remove(link)
  p.inputs['Base Color'].default_value=(.017,.005,.007,1)
 materials[kind]=m;return m
for obj in list(bpy.context.scene.objects):
 if obj.type!='MESH' or obj.name.startswith('Tattoo_'):continue
 mesh=obj.data;old_names=[m.name for m in mesh.materials];bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();uv=mesh.uv_layers.active or mesh.uv_layers.new();max_distance=0
 for face in mesh.polygons:
  points=[obj.matrix_world@mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices];mid=sum(points,Vector())/3;p,n,fi,d=surface.find_nearest(mid);max_distance=max(max_distance,d);ids=triangles[fi];a,b,c=[registered[i] for i in ids];ua,ub,uc=[Vector((u.x,u.y,0)) for u in uvs[fi]]
  for li,point in zip(face.loop_indices,points):v=barycentric_transform(point,a,b,c,ua,ub,uc);uv.data[li].uv=(v.x,v.y)
 assert max_distance<.003,(obj.name,'target does not lie on frozen source mesh',max_distance)
 for i,old in enumerate(old_names):mesh.materials[i]=material(kind_for(obj,old))
 reports.append({'mesh':obj.name,'uv_max_surface_error_m':max_distance,'vertices':len(mesh.vertices),'triangles':len(mesh.polygons)})
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/(form+'-pbr-static.blend')));bpy.ops.export_scene.gltf(filepath=str(O/(form+'-static.glb')),export_format='GLB',export_animations=False,export_extras=True);(O/(form+'-pbr-static.blend')).replace(O/(form+'-static.blend'));raw=(O/(form+'.glb')).read_bytes();meta=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])['scenes'][0]['extras'];meta.pop('tattooPolicyHash',None);meta.update(appearanceMethod='Meshy original 4K PBR on frozen selected-body anatomy, triangle-corner UV transfer; native skin and source animation retained',meshTextureTask='01a188fc-2079-766d-b337-6759221b5482' if form=='wolf' else '01a188f0-3489-71d1-bfe1-dd7fff0337cd',sourceClothingTexturesUsed=False)
ex.OUT=O;report=ex.build(form,meta,body_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb' if form=='wolf' else 'art/3d/source/pedro-native/main/pedro.ltb',motion_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb' if form=='wolf' else 'art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb')
if form=='wolf':
 from apply_tattoo_policy import apply
 r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload);report['tattoo']=r
report.update(registration_scale=scale,registration_error_m=error,meshes=reports,base_color_resolution='4K',normal_resolution='2K',roughness_metal_resolution='1K');(D/(form+'-pbr-integration.json')).write_text(json.dumps(report,indent=2));print('KARAHAN_PBR_INTEGRATED',report)
