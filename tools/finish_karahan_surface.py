# REJECTED VISUAL EXPERIMENT: not a production template. See docs/karahan-v0118/GUNCEL-RAPOR-TR.md.
"""Final original PBR surfaces, healed scars and worn trousers on fixed anatomy.
No bone/key editing; only local garment/neck skin continuity repairs.
"""
import bpy,sys,json,struct,math,inspect,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as ex;import build_ice40_family as base
O=R/'art/characters/karahan';D=R/'docs/karahan-v0118';BODY='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb';MOTION='art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb';bpy.ops.wm.open_mainfile(filepath=str(O/'wolf-static.blend'));obj=bpy.data.objects['Body_karahan'];rig=bpy.data.objects['NativeRig'];changed=0
for vertex in obj.data.vertices:
 x,y,z=vertex.co
 if not (106<y<139 and abs(x)<17 and z>-22):continue
 weights={obj.vertex_groups[g.group].name:g.weight for g in vertex.groups}
 if weights.get('Bip01 Ponytail2',0)>.05:continue
 influence=base.common.smooth((17-abs(x))/5)*base.common.smooth((y-106)/5)*base.common.smooth((z+22)/3);head=base.common.smooth((y-119)/12);spine=1-base.common.smooth((y-106)/16);neck=max(0,1-head-spine);targets={'Bip01 Spine2':spine,'Bip01 Neck':neck,'Bip01 Head':head};values={k:w*(1-influence) for k,w in weights.items()}
 for k,w in targets.items():values[k]=values.get(k,0)+w*influence
 best=sorted(values.items(),key=lambda pair:-pair[1])[:4];total=sum(w for _,w in best)
 for group in obj.vertex_groups:group.remove([vertex.index])
 for k,w in best:
  if w>1e-7:obj.vertex_groups[k].add([vertex.index],w/total,'REPLACE')
 changed+=1
# Paint real surface-position wear, never random geometry deletions at a knee.
model=ex.Reader().from_file(str(R/BODY));base.OUT=O;piece=next(p for p in model.pieces if p.name=='lower');lod=piece.lods[0]
def appearance(points,normals,kind):
 x,y,z=points.T;n=base.noise3(points*2);weave=np.sin(x*57+y*49)*np.sin(y*61+z*39);rgb=np.tile([.03,.036,.044],(len(points),1))+(n*.007+weave*.003)[:,None];h=weave*.35
 seam=(np.abs(np.abs(x)-13)<.2)&(y>30)&(y<64);rgb[seam]=[.2,.135,.065]
 # Two small asymmetric torn cloth areas reveal fur on the same skin surface.
 front=np.clip((-z-4)/5,0,1)
 for cx,cy,rx,ry in [(9.5,44,3.1,2.0),(-11,54,2.2,1.1)]:
  radius=((x-cx)/rx)**2+((y-cy)/ry)**2+n*.17;inside=(radius<.75)&(front>.6);rim=(radius>=.75)&(radius<1.2)&(front>.6);rgb[inside]=np.stack([.25+n[inside]*.025,.27+n[inside]*.025,.28+n[inside]*.025],axis=1);rgb[rim]=[.15,.14,.115];h[rim]+=.25;h[inside]=n[inside]*.5
 waist=y>73;rgb[waist]=[.044,.031,.021];return np.clip(rgb,0,1),h
source=inspect.getsource(base.make_atlas).replace('def make_atlas(surface):','def pants_atlas(surface):').replace('appearance(points,normals,region(piece,lod,face,parts))',"appearance(points,normals,'Pants')");namespace=dict(base.__dict__);namespace['appearance']=appearance;exec(source,namespace);color,normal=namespace['pants_atlas']([('lower',lod)])
for im,name in [(color,'Karahan_WornPantsColor'),(normal,'Karahan_WornPantsNormal')]:im.name=name;im.filepath_raw=str(O/(name+'.png'));im.save();im.pack()
mat=bpy.data.materials['Karahan_lower_Pants'];shader=mat.node_tree.nodes['Principled BSDF'];node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=color;mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Base Color']);node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=normal;convert=shader.inputs['Normal'].links[0].from_node;mat.node_tree.links.new(node.outputs['Color'],convert.inputs['Color'])
# Dedicated roughness variation, independent of the base colour and lighting.
for mat in list(bpy.data.materials):
 if not mat.name.startswith('Karahan_') or not mat.use_nodes:continue
 shader=mat.node_tree.nodes.get('Principled BSDF')
 if not shader:continue
 kind=mat.name.rsplit('_',1)[-1]
 if kind not in ['Fur','Pants','Bracer']:continue
 image=bpy.data.images.new(mat.name+'_Roughness',width=512,height=512,alpha=False);image.colorspace_settings.name='Non-Color';yy,xx=np.indices((512,512));fine=np.sin(xx*1.713+yy*.53)*np.sin(yy*1.133);value=(.91 if kind=='Fur' else .84 if kind=='Pants' else .53)+fine*(.025 if kind!='Bracer' else .065);pixels=np.ones((512,512,4),dtype=np.float32);pixels[:,:,:3]=value[:,:,None];image.pixels.foreach_set(pixels.ravel());image.filepath_raw=str(O/(image.name+'.png'));image.file_format='PNG';image.save();image.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.links.new(node.outputs['Color'],shader.inputs['Roughness'])
 # Only real links export; no stale hidden texture copies.
 for node in list(mat.node_tree.nodes):
  if node.type=='TEX_IMAGE' and not any(output.is_linked for output in node.outputs):mat.node_tree.nodes.remove(node)
# Remove remaining disconnected waist trim fragments; never cut actual pants.
lower=bpy.data.objects['Body_karahan_lower'];import bmesh
bm=bmesh.new();bm.from_mesh(lower.data);seen=set();remove=[]
for vertex in bm.verts:
 if vertex in seen:continue
 stack=[vertex];component=[];seen.add(vertex)
 while stack:
  v=stack.pop();component.append(v)
  for edge in v.link_edges:
   other=edge.other_vert(v)
   if other not in seen:seen.add(other);stack.append(other)
 center=sum((v.co for v in component),Vector())/len(component)
 if 65<center.y<84 and len(component)<48 and max(v.co.y for v in component)>76:remove.extend(component)
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(lower.data);bm.free();lower.data.update()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True);raw=(O/'wolf.glb').read_bytes();meta=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])['scenes'][0]['extras'];meta.pop('tattooPolicyHash',None);meta['tattooProjectionBodyName']='Body_karahan';meta['nativeLocomotion']['walkSpeedMetersPerSecond']=2.4;ex.OUT=O;report=ex.build('wolf',meta,body_source=BODY,motion_source=MOTION)
from apply_tattoo_policy import apply
r,payload,_=apply(O/'wolf.glb');(O/'wolf.glb').write_bytes(payload);report.update(neck_skin_continuity_vertices=changed,removed_disconnected_waist_vertices=len(remove),tattoo=r,original_pbr_bake=True,source_dtx_clothing_used=False);(D/'surface-finish.json').write_text(json.dumps(report,indent=2));print('KARAHAN_SURFACE_FINISH',report)
