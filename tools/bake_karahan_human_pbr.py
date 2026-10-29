# REJECTED VISUAL EXPERIMENT: not a production template. See docs/karahan-v0118/GUNCEL-RAPOR-TR.md.
"""Bake original produced armour onto the native short Human47 body.
Source game clothes are never read; native joints, hands and animation stay fixed.
"""
import bpy,sys,json,struct,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as ex
O=R/'art/characters/karahan';D=R/'docs/karahan-v0118';bpy.ops.wm.open_mainfile(filepath=str(O/'human-static.blend'));body=bpy.data.objects['Body_human_karahan_Red_Upperbody'];material=bpy.data.materials['KarahanHuman_Red_Upperbody'];face=bpy.data.materials['Karahan_OriginalProducedFace'];raw=(R/'app/src/main/assets/models/human-bilge.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:]
def read(i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];code={5126:'f',5123:'H',5125:'I'}[a['componentType']];size=struct.calcsize('<'+code*width);return [struct.unpack_from('<'+code*width,binary,v.get('byteOffset',0)+a.get('byteOffset',0)+j*v.get('byteStride',size)) for j in range(a['count'])]
p=g['meshes'][0]['primitives'][0];a=p['attributes'];points=read(a['POSITION']);normals=read(a['NORMAL']);uvs=read(a['TEXCOORD_0']);ix=[v[0] for v in read(p['indices'])];faces=[tuple(ix[k:k+3]) for k in range(0,len(ix),3) if min(points[i][1] for i in ix[k:k+3])>61];mesh=bpy.data.meshes.new('OriginalArmourDonor');mesh.from_pydata(points,[],faces);donor=bpy.data.objects.new('OriginalArmourDonor',mesh);bpy.context.collection.objects.link(donor);mesh.materials.append(face);uv=mesh.uv_layers.new();ns=[]
for poly,f in zip(mesh.polygons,faces):
 poly.use_smooth=True
 for li,i in zip(poly.loop_indices,f):uv.data[li].uv=(uvs[i][0],1-uvs[i][1]);ns.append(Vector(normals[i]))
mesh.normals_split_custom_set(ns);receiver=body.copy();receiver.data=body.data.copy();receiver.parent=None;receiver.matrix_world.identity();bpy.context.collection.objects.link(receiver)
for mod in list(receiver.modifiers):receiver.modifiers.remove(mod)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False;scene.render.bake.use_selected_to_active=True;results=[]
for mode in ['DIFFUSE','NORMAL']:
 image=bpy.data.images.new('KarahanHumanOriginalArmour_'+mode,width=2048,height=2048,alpha=True)
 if mode=='NORMAL':image.colorspace_settings.name='Non-Color'
 mat=bpy.data.materials.new('TemporaryBake');mat.use_nodes=True;tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.nodes.active=tex;receiver.data.materials.clear();receiver.data.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');donor.select_set(True);receiver.select_set(True);bpy.context.view_layer.objects.active=receiver;bpy.ops.object.bake(type=mode,pass_filter={'COLOR'} if mode=='DIFFUSE' else set(),use_clear=True,margin=12,cage_extrusion=8,max_ray_distance=18)
 pixels=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4);valid=pixels[:,3]>.5
 if mode=='DIFFUSE':
  dark=pixels[:,:3].max(1)<.015;pixels[dark|~valid]=[.055,.063,.073,1];blue=(pixels[:,2]>pixels[:,0]*1.1)&(pixels[:,2]>.07);pixels[blue,:3]*=np.array([.7,.55,.4]);pixels[:,3]=1
 else:pixels[~valid]=[.5,.5,1,1]
 image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(O/(image.name+'.png'));image.file_format='PNG';image.save();image.pack();shader=material.node_tree.nodes['Principled BSDF'];node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
 if mode=='DIFFUSE':material.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color'])
 else:
  convert=material.node_tree.nodes.new('ShaderNodeNormalMap');convert.inputs['Strength'].default_value=.45;material.node_tree.links.new(node.outputs['Color'],convert.inputs['Color']);material.node_tree.links.new(convert.outputs['Normal'],shader.inputs['Normal'])
 results.append({'mode':mode,'valid_fraction':float(valid.mean())})
for node in list(material.node_tree.nodes):
 if node.type=='TEX_IMAGE' and not any(o.is_linked for o in node.outputs):material.node_tree.nodes.remove(node)
material.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.28;material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.62
bpy.data.objects.remove(receiver,do_unlink=True);bpy.data.objects.remove(donor,do_unlink=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'human-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'human-static.glb'),export_format='GLB',export_animations=False,export_extras=True);raw=(O/'human.glb').read_bytes();meta=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])['scenes'][0]['extras'];meta['appearanceMethod']='original project-produced armour selected-to-active color and normal bake on native short-body geometry';ex.OUT=O;report=ex.build('human',meta,body_source='art/3d/source/pedro-native/main/pedro.ltb',motion_source='art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb');report['bakes']=results;(D/'human-pbr-bake.json').write_text(json.dumps(report,indent=2));print('KARAHAN_HUMAN_PBR',report)
