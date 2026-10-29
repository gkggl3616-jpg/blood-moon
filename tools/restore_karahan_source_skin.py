"""Restore the selected body's authored skin after proportions are normalized.
The old broad blur is no longer needed and must not blend chest into shoulders.
"""
import bpy,sys,json,struct
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as e;from build_bilge_original import bary
O=R/'art/characters/karahan';b=e.Reader().from_file(str(R/'art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb'));lod=next(p for p in b.pieces if p.name=='upper').lods[0];points=[v.location for v in lod.vertices];faces=[tuple(c.vertex_index for c in f.vertices) for f in lod.faces];tree=KDTree(len(points))
for i,p in enumerate(points):tree.insert(p,i)
tree.balance();surface=BVHTree.FromPolygons(points,faces,all_triangles=True);bpy.ops.wm.open_mainfile(filepath=str(O/'wolf-static.blend'));obj=bpy.data.objects['Body_karahan']
for vertex in obj.data.vertices:
 _,i,d=tree.find(vertex.co)
 if d<.0001:weights={w.node_index:w.bias for w in lod.vertices[i].weights if w.bias>0}
 else:
  point,normal,fi,d=surface.find_nearest(vertex.co);ids=faces[fi];factors=bary(point,*(points[i] for i in ids));weights={}
  for i,factor in zip(ids,factors):
   for w in lod.vertices[i].weights:weights[w.node_index]=weights.get(w.node_index,0)+w.bias*factor
 top=sorted(weights.items(),key=lambda p:-p[1])[:4];total=sum(w for _,w in top)
 for group in obj.vertex_groups:group.remove([vertex.index])
 for i,w in top:
  if w>1e-7:obj.vertex_groups[b.nodes[i].name].add([vertex.index],w/total,'REPLACE')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True);raw=(O/'wolf.glb').read_bytes();meta=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])['scenes'][0]['extras'];meta.pop('tattooPolicyHash',None);meta['nativeRoleRecipes']['WolfRoar']=['T_cry'];meta.pop('derivedSourceClips',None);e.OUT=O;report=e.build('wolf',meta,body_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb',motion_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb')
from apply_tattoo_policy import apply
r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload);print('SOURCE_BODY_SKIN_RESTORED',report)
