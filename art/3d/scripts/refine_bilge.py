"""Preserve the approved source mesh. Latest user correction rejects the
experimental coat reconstruction. Only internal mouth pieces and material
separation are added; the body coordinates, UV and silhouette are unchanged.
"""
import bpy,json,math,shutil
import numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];A=R/'art/3d';SRC=A/'source/mobile-v019';SRC=SRC if (SRC/'bilge.glb').exists() else A/'approved-source';OUT=A/'source/mobile-v012';OUT.mkdir(parents=True,exist_ok=True)
for p in SRC.glob('*.glb'):shutil.copy2(p,OUT/p.name)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SRC/'bilge.glb'))
body=next(o for o in bpy.context.scene.objects if o.name.startswith('Body_'));h=2.25
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
original=[v.co.copy() for v in body.data.vertices]
# Keep the source's actual color/normal textures, fur silhouette and ice arms.
# Scalar response is non-metallic fur instead of shiny generated coat.
source=body.data.materials[0];source.name='Fur_Bilge_Source';bs=source.node_tree.nodes.get('Principled BSDF')
for socket in ['Metallic','Roughness']:
 for link in list(bs.inputs[socket].links):source.node_tree.links.remove(link)
bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.86
for node in source.node_tree.nodes:
 if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.4
ice=source.copy();ice.name='Ice_Bilge';b=ice.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.32;b.inputs['Metallic'].default_value=.03;body.data.materials.append(ice)
for poly in body.data.polygons:
 if .43<poly.center.z/h<.68 and abs(poly.center.x/h)>.20:poly.material_index=1
# The unchanged body provides the visible lower jaw. Oral pieces remain inside
# its silhouette; Head/Jaw rigid skin tags prevent teeth stretching.
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);return m
mouth=mat('Mouth_Interior',(.025,.008,.013));tooth=mat('Teeth_Ivory',(.72,.69,.53))
for bone,co,scale in [('Head',(0,-.110,.854),(.028,.038,.018)),('Jaw',(0,-.135,.835),(.028,.031,.008))]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=Vector(co)*h);o=bpy.context.object;o.name='Mouth_'+bone;o.scale=Vector(scale)*h;o.data.materials.append(mouth);o['skin_bone']=bone
for sg in [-1,1]:
 for j in range(4):
  for lower in [False,True]:
   bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=.004*h,depth=(.014 if j==0 else .008)*h,location=(sg*(.022-.002*j)*h,(-.122-.009*j)*h,(.852 if not lower else .835)*h));o=bpy.context.object;o.name='Tooth';o.rotation_euler.x=0 if lower else math.pi;o.data.materials.append(tooth);o['skin_bone']='Jaw' if lower else 'Head'
for bone in ['Head','Jaw']:
 parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('skin_bone')==bone];bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();bpy.context.object.name='Mouth_'+bone
# Optional equipment stays separate from the approved body. Purchasing or
# removing a slot switches these real meshes without modifying the source.
gold=mat('Metal_Bilge_Accessory',(.40,.27,.08));bs=gold.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.65;bs.inputs['Roughness'].default_value=.45
bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=6,major_radius=.078*h,minor_radius=.007*h,location=(0,0,.80*h));o=bpy.context.object;o.name='Accessory_collar';o.scale.y=.8;o.data.materials.append(gold);o['skin_bone']='Neck'
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=(.19*h,-.012*h,.75*h));o=bpy.context.object;o.name='Accessory_shoulder';o.scale=(.055*h,.06*h,.018*h);o.data.materials.append(gold);o['skin_bone']='ClavicleL'
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.019*h,location=(.08*h,-.075*h,.54*h));o=bpy.context.object;o.name='Accessory_charm';o.scale.y=.4;o.data.materials.append(gold);o['skin_bone']='Hips'
assert max((v.co-original[i]).length for i,v in enumerate(body.data.vertices))<1e-9
body['source_kind']='new approved Meshy image model; original shape preserved'
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=body
tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes);assert tri<=15000,tri
bpy.ops.export_scene.gltf(filepath=str(OUT/'bilge.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
bpy.data.orphans_purge(do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(A/'bilge-refined.blend'),compress=True)
meta=json.loads((A/'model-report.json').read_text());meta['static_source_dir']='art/3d/source/mobile-v012';meta['refinement_new_credits']=0
b=next(p for p in meta['variants'] if p['id']=='bilge');b.update(triangles=tri,body_triangles=sum(len(p.vertices)-2 for p in body.data.polygons),objects=len(meshes),refinement='v012 approved shape preserved; arm rest fidelity and internal articulated mouth')
(A/'model-report.json').write_text(json.dumps(meta,indent=2));(A/'refinement-report.json').write_text(json.dumps({'approved_body_coordinate_change_m':0,'body_triangles':b['body_triangles'],'total_triangles':tri,'rejected_reconstruction':True,'new_credits':0,'limitations':['Original generated fur topology retained per latest user correction; further artistic changes need comparison to the approved model.']},indent=2));print('SOURCE_FIDELITY',tri)
# Human form: preserve the approved historical mesh/UV, separate real surface
# responses and constrain the same shoulder/elbow/wrist lengths in animation.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SRC/'human-bilge.glb'))
human=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.context.view_layer.objects.active=human
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
source=human.data.materials[0];source.name='Cloth_Bilge_Human';bs=source.node_tree.nodes.get('Principled BSDF')
for socket in ['Metallic','Roughness']:
 for link in list(bs.inputs[socket].links):source.node_tree.links.remove(link)
bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.9
for node in source.node_tree.nodes:
 if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.45
for name,r,m in [('Skin_Bilge_Human',.64,0),('Metal_Bilge_Human',.43,.65),('Leather_Bilge_Human',.72,.02)]:
 mat=source.copy();mat.name=name;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m;human.data.materials.append(mat)
tex=next((n.image for n in source.node_tree.nodes if n.type=='TEX_IMAGE' and n.image.colorspace_settings.name=='sRGB'),None)
pixels=np.array(tex.pixels[:]).reshape(tex.size[1],tex.size[0],4) if tex else None
uv=human.data.uv_layers.active
for poly in human.data.polygons:
 z=poly.center.z/1.85
 if z>.845:poly.material_index=1
 elif z<.20:poly.material_index=3
 elif pixels is not None:
  point=sum((uv.data[i].uv for i in poly.loop_indices),Vector((0,0)))/len(poly.loop_indices);r,g,b,_=pixels[int(point.y*tex.size[1])%tex.size[1],int(point.x*tex.size[0])%tex.size[0]]
  if r>.12 and g>.07 and b<r*.6:poly.material_index=2
for vert in human.data.vertices:
 z=vert.co.z/1.85
 if abs(vert.co.x)<.19*1.85:vert.co.x*=1+.03*math.exp(-((z-.75)/.06)**2)-.02*math.exp(-((z-.52)/.06)**2)
human['refinement']='Material-separated historical Bilge human, preserved UV and modest anatomical silhouette polish'
bpy.ops.object.select_all(action='DESELECT');human.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'human-bilge.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False)
bpy.data.orphans_purge(do_recursive=True);bpy.ops.wm.save_as_mainfile(filepath=str(A/'bilge-human-refined.blend'),compress=True)
