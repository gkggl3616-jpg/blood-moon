"""Persist lazy embedded JPEG albedo before Blender scene/library replacement.
A material link without loaded image pixels is not a textured runtime asset.
"""
import bpy,sys,json,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as ex
O=R/'art/characters/karahan';rows=[]
for form,folder in [('wolf','20261029_184802_karahan-battle-wolf-pbr_01a188fc'),('human','20261029_183440_karahan-human-pbr_01a188f0')]:
 raw=(R/'meshy_output'/folder/f'karahan-{form}-textured.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];mi=g['textures'][g['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['index']]['source'];view=g['bufferViews'][g['images'][mi]['bufferView']];path=O/'pbr'/form/'original-albedo.jpg';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]);bpy.ops.wm.open_mainfile(filepath=str(O/(form+'-static.blend')));image=bpy.data.images.load(str(path),check_existing=False);image.name='Karahan_'+form+'_OriginalAlbedo4K';image.colorspace_settings.name='sRGB';sample=image.pixels[0];assert image.size[0]>=4096 and image.has_data;image.pack();fixed=0
 for mat in bpy.data.materials:
  if not mat.name.startswith('Karahan_'+form+'_') or not mat.use_nodes:continue
  shader=mat.node_tree.nodes.get('Principled BSDF')
  if not shader or mat.name.endswith('_Mouth'):continue
  for link in list(shader.inputs['Base Color'].links):mat.node_tree.links.remove(link)
  tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);fixed+=1
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/(form+'-color-fixed.blend')));bpy.ops.export_scene.gltf(filepath=str(O/(form+'-static.glb')),export_format='GLB',export_animations=False,export_extras=True);(O/(form+'-color-fixed.blend')).replace(O/(form+'-static.blend'));r=(O/(form+'.glb')).read_bytes();meta=json.loads(r[20:20+struct.unpack_from('<I',r,12)[0]])['scenes'][0]['extras'];meta.pop('tattooPolicyHash',None);ex.OUT=O;report=ex.build(form,meta,body_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb' if form=='wolf' else 'art/3d/source/pedro-native/main/pedro.ltb',motion_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb' if form=='wolf' else 'art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb')
 if form=='wolf':
  from apply_tattoo_policy import apply
  r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload)
 data=(O/(form+'.glb')).read_bytes();j=json.loads(data[20:20+struct.unpack_from('<I',data,12)[0]])
 for mat in j['materials']:
  if mat.get('name','').startswith('Karahan_'+form+'_') and not mat['name'].endswith('_Mouth'):assert 'baseColorTexture' in mat['pbrMetallicRoughness'],mat['name']
 rows.append({'form':form,'materials_fixed':fixed,'all_body_albedo_textures_embedded':True,'triangles_before_tattoo':report['triangles'],'bytes':len(data)})
print('ALBEDO_PACK_FIXED',rows);(R/'docs/karahan-v0118/albedo-pack-fixed.json').write_text(json.dumps(rows,indent=2))
