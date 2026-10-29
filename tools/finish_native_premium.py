"""Finish continuous photographic fur detail and a smooth trouser hip falloff.
Only original/reference appearance and the new garment's skin are edited;
source hierarchy, rest joints, native face weights and motion keys are retained.
"""
import bpy,sys,json,math,inspect,numpy as np
from PIL import Image,ImageFilter
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import build_ice40_family as base;import export_bilge_native_basis as e
O=R/'art/characters/premium-wolf-01/native-final';BODY='art/3d/source/wolfteam-archive/selected/wt_wolf_power_r.ltb';MOTION='art/3d/source/pedro-native/new-motion/wt_new_wolf_ch.ltb';model=base.common.Reader().from_file(str(R/BODY));lod=next(p for p in model.pieces if p.name=='WOLF_BODY_R').lods[0];base.OUT=O
# Remove broad lighting from a genuine fur swatch; retain the actual hair detail.
photo=Image.open(R/'art/characters/reference/grey-wolf-faithful-large.png').convert('RGB').crop((420,600,620,800));a=np.array(photo,dtype=np.float32)/255;blur=np.array(photo.filter(ImageFilter.GaussianBlur(9)),dtype=np.float32)/255;hair=(a-blur).mean(2);hair=np.clip(hair*2.5,-.22,.22)
bpy.ops.wm.open_mainfile(filepath=str(O/'wolf-static.blend'));obj=bpy.data.objects['Body_bilge'];rig=bpy.data.objects['NativeRig'];mat=bpy.data.materials['NativePremium_Fur'];shader=mat.node_tree.nodes['Principled BSDF'];base_tex=shader.inputs['Base Color'].links[0].from_node.image;old=np.flipud(np.array(base_tex.pixels[:],dtype=np.float32).reshape(2048,2048,4));normal_node=shader.inputs['Normal'].links[0].from_node;normal_tex=normal_node.inputs['Color'].links[0].from_node.image;old_normal=np.array(normal_tex.pixels[:],dtype=np.float32).reshape(2048,2048,4)
def appearance(points,normals,kind):
 x,y,z=points.T
 def tex(u,v):
  u=1-np.abs((u%2)-1);v=1-np.abs((v%2)-1);ix=(u*(hair.shape[1]-1)).astype(int);iy=(v*(hair.shape[0]-1)).astype(int);return hair[iy,ix]
 blend=np.abs(normals)**4;blend/=np.maximum(1e-6,blend.sum(1))[:,None];detail=tex(z*.18,y*.18)*blend[:,0]+tex(x*.18,z*.18)*blend[:,1]+tex(x*.18,y*.18)*blend[:,2];front=np.clip((-z-4)/14,0,1);chest=np.exp(-(x/15)**2)*np.clip((y-72)/16,0,1)*np.clip((112-y)/15,0,1)*front;rgb=np.tile([.32,.35,.38],(len(points),1));rgb+=(detail*.85+chest*.065)[:,None];return np.clip(rgb,0,1),detail*3
source=inspect.getsource(base.make_atlas).replace('def make_atlas(surface):','def fur_atlas(surface):').replace('appearance(points,normals,region(piece,lod,face,parts))',"appearance(points,normals,'Fur')");source=source.replace('color[p[:,1],p[:,0],:3]=rgb','color[p[:,1],p[:,0],:3]=rgb*.75+baked_pixels[p[:,1],p[:,0],:3]*.25');namespace=dict(base.__dict__);namespace.update(appearance=appearance,baked_pixels=old);exec(source,namespace);color,normal=namespace['fur_atlas']([('WOLF_BODY_R',lod)]);color.name='NativePremium_ContinuousFur';normal.name='NativePremium_ContinuousFurNormal';npix=np.array(normal.pixels[:],dtype=np.float32).reshape(2048,2048,4);v=old_normal[:,:,:3]*2-1;w=npix[:,:,:3]*2-1;combined=np.stack([v[:,:,0]*.8+w[:,:,0]*.6,v[:,:,1]*.8+w[:,:,1]*.6,v[:,:,2]*w[:,:,2]],axis=2);combined/=np.maximum(.001,np.linalg.norm(combined,axis=2))[:,:,None];npix[:,:,:3]=combined*.5+.5;normal.pixels.foreach_set(npix.ravel())
for image in [color,normal]:image.filepath_raw=str(O/(image.name+'.png'));image.save();image.pack()
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=color;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=normal;normal_node.inputs['Strength'].default_value=.75;mat.node_tree.links.new(n.outputs['Color'],normal_node.inputs['Color']);shader.inputs['Roughness'].default_value=.93
# The original crotch had a sharp pelvis/thigh discontinuity. The new trousers
# use a continuous anatomical blend there, never an unrelated arm/hand donor.
groups={n:obj.vertex_groups[n] for n in ['Bip01 Pelvis','Bip01 L Thigh','Bip01 R Thigh']};changed=0
for vertex in obj.data.vertices:
 x,y,z=vertex.co
 if not (48<y<78 and abs(x)<18):continue
 influence=base.common.smooth((18-abs(x))/6)*base.common.smooth((y-48)/4)*base.common.smooth((78-y)/4);pelvis=base.common.smooth((y-52)/22);left=.5+.5*math.tanh(x/3);target={'Bip01 Pelvis':pelvis,'Bip01 L Thigh':(1-pelvis)*left,'Bip01 R Thigh':(1-pelvis)*(1-left)};value={obj.vertex_groups[g.group].name:g.weight*(1-influence) for g in vertex.groups}
 for name,w in target.items():value[name]=value.get(name,0)+w*influence
 for group in obj.vertex_groups:group.remove([vertex.index])
 top=sorted(value.items(),key=lambda v:-v[1])[:4];total=sum(w for _,w in top)
 for name,w in top:
  if w>1e-7:obj.vertex_groups[name].add([vertex.index],w/total,'REPLACE')
 changed+=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True);e.OUT=O;report=e.build('wolf',{'modelType':'power42','wardrobeOrigin':'original_authored_on_selected_body','nativeMouthGeometry':True,'nativeJawBone':'Bip01 Ponytail2','mouthGeometryOrigin':'selected native jaw, teeth and oral geometry','bodyGeometryOrigin':'selected native body with refined native skin and new trouser hip falloff','originalAppearanceSource':'01a18823-7e5f-7422-8ae2-b27a15865086','appearanceMethod':'Cycles original-production PBR bake plus continuous photographic reference fur','sourceClothingTexturesUsed':False,'fittedPants':True,'longHangingPanels':False,'nativeLocomotion':{'quadClip':'T_WallDash','walkStrideMeters':2.8942126751800683,'runStrideMeters':2.5106097294977214}},body_source=BODY,motion_source=MOTION);report['trouser_hip_vertices_refined']=changed;(R/'docs/premium-wolf-01/native-final-finish.json').write_text(json.dumps(report,indent=2));print('NATIVE_FINISH',report)
