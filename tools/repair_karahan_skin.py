"""Continuous native skin repair with a soft boundary; no rig/key changes.
Protect actual face/jaw/finger geometry. Smooth UV-seam discontinuities in body
weights and apply an anatomical clothing-only pelvis/thigh transition.
"""
import bpy,sys,math,json,struct
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import build_ice40_family as base;import export_bilge_native_basis as ex
O=R/'art/characters/karahan';D=R/'docs/karahan-v0118';bpy.ops.wm.open_mainfile(filepath=str(O/'wolf-static.blend'));obj=bpy.data.objects['Body_karahan'];tree=KDTree(len(obj.data.vertices))
for v in obj.data.vertices:tree.insert(v.co,v.index)
tree.balance();changed=set()
for iteration in range(8):
 values=[{g.group:g.weight for g in v.groups if g.weight>0} for v in obj.data.vertices]
 for vertex in obj.data.vertices:
  x,y,z=vertex.co;influence=.85*base.common.smooth((y-76)/15)*base.common.smooth((145-y)/12)*base.common.smooth((62-abs(x))/12)*base.common.smooth((z+25)/6)
  if influence<.001:continue
  if any('Ponytail' in obj.vertex_groups[i].name and w>.05 for i,w in values[vertex.index].items()):continue
  result={i:w*(1-influence) for i,w in values[vertex.index].items()};neighbors=tree.find_range(vertex.co,6.5);acc={};total=0
  for _,i,d in neighbors:
   if any('Ponytail' in obj.vertex_groups[j].name and w>.05 for j,w in values[i].items()):continue
   factor=math.exp(-(d/3.6)**2);total+=factor
   for j,w in values[i].items():acc[j]=acc.get(j,0)+w*factor
  for j,w in acc.items():result[j]=result.get(j,0)+w/total*influence
  best=sorted(result.items(),key=lambda pair:-pair[1])[:4];norm=sum(w for _,w in best)
  for group in obj.vertex_groups:group.remove([vertex.index])
  for i,w in best:
   if w>1e-7:obj.vertex_groups[i].add([vertex.index],w/norm,'REPLACE')
  changed.add(vertex.index)
lower=bpy.data.objects['Body_karahan_lower'];pants=0
for vertex in lower.data.vertices:
 x,y,z=vertex.co
 if not (47<y<79 and abs(x)<16):continue
 influence=base.common.smooth((16-abs(x))/5)*base.common.smooth((y-47)/5)*base.common.smooth((79-y)/5);pelvis=base.common.smooth((y-50)/23);left=.5+.5*math.tanh(x/3);target={'Bip01 Pelvis':pelvis,'Bip01 L Thigh':(1-pelvis)*left,'Bip01 R Thigh':(1-pelvis)*(1-left)};weights={lower.vertex_groups[g.group].name:g.weight*(1-influence) for g in vertex.groups}
 for name,w in target.items():weights[name]=weights.get(name,0)+w*influence
 best=sorted(weights.items(),key=lambda p:-p[1])[:4];total=sum(w for _,w in best)
 for group in lower.vertex_groups:group.remove([vertex.index])
 for name,w in best:
  if w>1e-7:lower.vertex_groups[name].add([vertex.index],w/total,'REPLACE')
 pants+=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True);raw=(O/'wolf.glb').read_bytes();meta=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])['scenes'][0]['extras'];meta.pop('tattooPolicyHash',None);meta.pop('nativeBindingCorrections',None);meta['nativeRebindRequired']=False;meta['nativeBindingMethod']='source raw T_cry exactly matches the same-body AI T_Explosion; no extra bind delta';meta['tattooProjectionBodyName']='Body_karahan';ex.OUT=O;report=ex.build('wolf',meta,body_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb',motion_source='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb')
from apply_tattoo_policy import apply
r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload);report.update(body_smoothed=len(changed),pants_smoothed=pants,tattoo=r);(D/'native-skin-repair.json').write_text(json.dumps(report,indent=2));print('KARAHAN_SKIN_REPAIR',report)
