"""Prepare two concrete untextured inputs, without spending credits.
Wolf uses selected authored native-family static geometry; human uses complete
native Human47 anatomy, preventing a copied Bilge head or chopped coat seam.
No rig/animation regeneration is requested by the proposed texture-only job.
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as e
O=R/'art/characters/karahan/texture-inputs';O.mkdir(parents=True,exist_ok=True)
for form in ['wolf','human']:
 if form=='wolf':
  bpy.ops.wm.open_mainfile(filepath=str(R/'art/characters/karahan/wolf-static.blend'))
  for obj in list(bpy.context.scene.objects):
   if obj.type=='MESH' and obj.name.startswith('Tattoo_'):bpy.data.objects.remove(obj,do_unlink=True)
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);m=e.Reader().from_file(str(R/'art/3d/source/pedro-native/main/pedro.ltb'));points=[v.location for p in m.pieces for v in p.lods[0].vertices];lo=min(p.y for p in points);scale=1.85/(max(p.y for p in points)-lo);basis=Matrix(((scale,0,0,0),(0,0,-scale,0),(0,scale,0,-lo*scale),(0,0,0,1)))
  for p in m.pieces:
   l=p.lods[0];mesh=bpy.data.meshes.new(p.name);mesh.from_pydata([v.location for v in l.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in l.faces]);obj=bpy.data.objects.new(p.name,mesh);bpy.context.collection.objects.link(obj);obj.matrix_world=basis;uv=mesh.uv_layers.new();normals=[]
   for poly,f in zip(mesh.polygons,l.faces):
    poly.use_smooth=True
    for li,c in zip(poly.loop_indices,f.vertices):uv.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(l.vertices[c.vertex_index].normal)
   mesh.normals_split_custom_set(normals)
 # Remove modifiers before static export: mesh rest anatomy, not an animated pose.
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  for mod in list(obj.modifiers):obj.modifiers.remove(mod)
  obj.data.materials.clear();mat=bpy.data.materials.new('Karahan_'+form+'_'+obj.name);mat.use_nodes=True;shader=mat.node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(.4,.4,.4,1);shader.inputs['Roughness'].default_value=.8;obj.data.materials.append(mat)
  for poly in obj.data.polygons:poly.material_index=0
 bpy.ops.export_scene.gltf(filepath=str(O/(form+'-texture-input.glb')),export_format='GLB',export_animations=False,export_skins=False,export_extras=True)
print('PREPARED_TEXTURE_INPUTS',str(O))
