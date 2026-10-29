# REJECTED VISUAL EXPERIMENT: not a production template. See docs/karahan-v0118/GUNCEL-RAPOR-TR.md.
"""Bake the paid original surface onto the proven native body in real 3D.
Selected-to-active Cycles baking preserves UV islands and tangent-space normals;
no interpolation between unrelated donor UV islands or skeleton refitting.
"""
import bpy,bmesh,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as e
O=R/'art/characters/karahan';BODY='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb';MOTION='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb';bpy.ops.wm.open_mainfile(filepath=str(O/'wolf-static.blend'));rig=bpy.data.objects['NativeRig'];rig.matrix_world=Matrix.Rotation(-math.pi,4,'Z')@rig.matrix_world;bpy.context.view_layer.update();body=bpy.data.objects['Body_karahan'];receiver=body.copy();receiver.data=body.data.copy();bpy.context.collection.objects.link(receiver);receiver.name='TemporaryBakeReceiver'
for v in receiver.data.vertices:v.co=body.matrix_world@v.co
receiver.parent=None;receiver.matrix_world=Matrix.Identity(4)
for modifier in list(receiver.modifiers):receiver.modifiers.remove(modifier)
old_objects=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(R/'art/characters/premium-wolf-01/v2/mobile-2k.glb'));donor=next(o for o in bpy.context.scene.objects if o not in old_objects and o.type=='MESH');coords=[donor.matrix_world@v.co for v in donor.data.vertices];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
for v,p in zip(donor.data.vertices,coords):v.co=(p-center)*2.6/(hi.z-lo.z)
donor.matrix_world=Matrix.Identity(4);donor.parent=None;scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False;scene.render.bake.use_selected_to_active=True;results=[]
for kind in ['Fur']:
 source=donor.copy();source.data=donor.data.copy();bpy.context.collection.objects.link(source);source.name='TemporaryDonor_'+kind;bm=bmesh.new();bm.from_mesh(source.data);remove=[]
 for f in bm.faces:
  p=f.calc_center_median();is_pants=.17<p.z<1.4 and abs(p.x)<.45
  if (kind=='Fur' and (is_pants or p.z>2.12)) or (kind=='Pants' and not is_pants):remove.append(f)
 bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(source.data);bm.free();target_material=bpy.data.materials['Karahan_upper_'+kind];old_base=next(n.image for n in target_material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.colorspace_settings.name=='sRGB');old_pixels=np.array(old_base.pixels[:],dtype=np.float32).reshape(-1,4)
 for mode in ['DIFFUSE','NORMAL']:
  image=bpy.data.images.new('BakedNative_'+kind+'_'+mode,width=2048,height=2048,alpha=True)
  if mode=='NORMAL':image.colorspace_settings.name='Non-Color'
  mat=bpy.data.materials.new('TemporaryBakeMaterial');mat.use_nodes=True;node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.nodes.active=node;receiver.data.materials.clear();receiver.data.materials.append(mat)
  for f in receiver.data.polygons:f.material_index=0
  bpy.ops.object.select_all(action='DESELECT');source.select_set(True);receiver.select_set(True);bpy.context.view_layer.objects.active=receiver;bpy.ops.object.bake(type=mode,pass_filter={'COLOR'} if mode=='DIFFUSE' else set(),use_clear=True,margin=12,cage_extrusion=.35,max_ray_distance=.80)
  pixels=np.array(image.pixels[:],dtype=np.float32).reshape(-1,4);valid=pixels[:,3]>.5
  if mode=='DIFFUSE':
   valid&=pixels[:,:3].max(1)>.015
   if kind=='Fur':valid&=(pixels[:,:3].max(1)-pixels[:,:3].min(1)<.17)&(pixels[:,2]<pixels[:,0]*1.15+.02)
   pixels[~valid]=old_pixels[~valid];pixels[valid,:3]=pixels[valid,:3]*.75+old_pixels[valid,:3]*.25
  else:pixels[~valid]=[.5,.5,1,1]
  image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(O/(image.name+'.png'));image.file_format='PNG';image.save();image.pack();shader=target_material.node_tree.nodes['Principled BSDF']
  if mode=='DIFFUSE':
   tex=target_material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;target_material.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
  else:
   tex=target_material.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;normal=target_material.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.45;target_material.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);target_material.node_tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
  results.append({'kind':kind,'mode':mode,'valid_fraction':float(valid.mean())});print('BAKED',results[-1],flush=True)
 bpy.data.objects.remove(source,do_unlink=True)
bpy.data.objects.remove(receiver,do_unlink=True);
for extra in list(bpy.context.scene.objects):
 if extra not in old_objects:bpy.data.objects.remove(extra,do_unlink=True)
rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@rig.matrix_world
# Remove unlinked old image nodes so GLB embeds only the maps actually in use.
for kind in ['Fur']:
 m=bpy.data.materials['Karahan_upper_'+kind]
 for n in list(m.node_tree.nodes):
  if n.type=='TEX_IMAGE' and not n.outputs['Color'].is_linked and not n.outputs['Alpha'].is_linked:m.node_tree.nodes.remove(n)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-baked.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True)
# The exporter uses the same baked rest mesh and immutable native contract.
original=O/'wolf-static.blend';backup=O/'wolf-unbaked.blend';original.rename(backup);(O/'wolf-baked.blend').replace(original)
raw=(O/'wolf.glb').read_bytes();import struct;meta=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])['scenes'][0]['extras'];meta.pop('tattooPolicyHash',None);meta['tattooProjectionBodyName']='Body_karahan';meta['appearanceMethod']='selected-to-active Cycles color/normal from project-original paid production, plus native continuous microfur';e.OUT=O;report=e.build('wolf',meta,body_source=BODY,motion_source=MOTION)
from apply_tattoo_policy import apply
r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload);report['bakes']=results;(R/'docs/karahan-v0118/pbr-bake.json').write_text(json.dumps(report,indent=2));print('KARAHAN_PBR_BAKED',report)
