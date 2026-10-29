"""Production body first: preserve selected native skin/jaw and source motion.
The new paid reference model supplies original fur and trouser appearance only.
No source DTX clothing textures, random rest-fit cage or generated mouth patch.
"""
import bpy,bmesh,sys,json,math,inspect,numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import build_ice40_family as base;import export_bilge_native_basis as exporter
O=R/'art/characters/premium-wolf-01/native-final';O.mkdir(parents=True,exist_ok=True);D=R/'docs/premium-wolf-01';BODY='art/3d/source/wolfteam-archive/selected/wt_wolf_power_r.ltb';MOTION='art/3d/source/pedro-native/new-motion/wt_new_wolf_ch.ltb';body=base.common.Reader().from_file(str(R/BODY));lod=next(p for p in body.pieces if p.name=='WOLF_BODY_R').lods[0];parts=base.components(lod);pts=[v.location for p in body.pieces for v in p.lods[0].vertices];low=min(p.y for p in pts);scale=2.4/(max(p.y for p in pts)-low);T=Matrix(((-scale,0,0,0),(0,0,scale,0),(0,scale,0,-low*scale),(0,0,0,1)))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'art/characters/premium-wolf-01/v2/mobile-2k.glb'));donor=next(o for o in bpy.context.scene.objects if o.type=='MESH');points=[donor.matrix_world@v.co for v in donor.data.vertices];lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));points=[(p-center)*2.4/(hi.z-lo.z) for p in points];donor.data.calc_loop_triangles();tris=list(donor.data.loop_triangles);uv=[v.uv.copy() for v in donor.data.uv_layers.active.data];image=next(n.image for n in donor.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.colorspace_settings.name=='sRGB');pixels=np.array(image.pixels[:],dtype=np.float32).reshape(image.size[1],image.size[0],4).copy();mapped={};sample_trees={};sample_colors={}
for kind in ['Fur','Pants']:
 eligible=[t for t in tris if (lambda p:1.30<p.z<1.84 if kind=='Fur' else .26<p.z<1.23)(sum((points[i] for i in t.vertices),Vector())/3)];tree=BVHTree.FromPolygons(points,[tuple(t.vertices) for t in eligible],all_triangles=True);values=[]
 for v in lod.vertices:
  p=T@v.location;p.y+=.12;point,normal,fi,distance=tree.find_nearest(p);t=eligible[fi];factors=base.common.bary(point,*(points[i] for i in t.vertices));values.append(sum((uv[i]*w for i,w in zip(t.loops,factors)),Vector((0,0))))
 mapped[kind]=np.array(values)
 # Sample color and 3D position together on each donor triangle. UVs from
 # separate islands must never be interpolated across a receiver triangle.
 samples=[];colors=[]
 for t in eligible:
  for ai in range(6):
   for bi in range(6-ai):
    weights=[ai/5,bi/5,1-(ai+bi)/5];q=sum((points[i]*w for i,w in zip(t.vertices,weights)),Vector());tex=sum((uv[i]*w for i,w in zip(t.loops,weights)),Vector((0,0)));ix=int(np.clip(tex.x*(pixels.shape[1]-1),0,pixels.shape[1]-1));iy=int(np.clip(tex.y*(pixels.shape[0]-1),0,pixels.shape[0]-1));samples.append(q);colors.append(pixels[iy,ix,:3])
 kd=KDTree(len(samples))
 for i,point in enumerate(samples):kd.insert(point,i)
 kd.balance();sample_trees[kind]=kd;sample_colors[kind]=np.array(colors)

bpy.ops.wm.read_factory_settings(use_empty=True);base.model=body;base.OUT=O
# Separate appearance atlases prevent cloth pixels leaking into bare fur even
# where nearest donor UV islands differ. Reject colored non-fur pixels explicitly.
source=inspect.getsource(base.make_atlas).replace('def make_atlas(surface):','def make_paid_atlas(surface):')
old='rgb,h=appearance(points,normals,region(piece,lod,face,parts));color'
new="""rgb,h=appearance(points,normals,kind);sample=sample_colors[kind][[sample_trees[kind].find(Vector((-x*scale,z*scale+.12,(y-low)*scale)))[1] for x,y,z in points]]
   if kind=='Fur':
    gray=sample.mean(1);valid=(sample.max(1)-sample.min(1)<.14)&(sample[:,2]<sample[:,0]*1.12+.015)&(gray>.12);rgb[valid]=sample[valid]*.9+rgb[valid]*.1
   else:
    valid=(sample[:,2]>sample[:,0]*1.04)&(sample.mean(1)<.48);rgb[valid]=sample[valid]*.85+rgb[valid]*.15
   color"""
assert old in source;source=source.replace(old,new);maps={}
for kind in ['Fur','Pants']:
 namespace=dict(base.__dict__);namespace.update(kind=kind,mapped=mapped,pixels=pixels,sample_trees=sample_trees,sample_colors=sample_colors,scale=scale,low=low);exec(source,namespace);maps[kind]=namespace['make_paid_atlas']([('WOLF_BODY_R',lod)])
 for image in maps[kind]:
  image.name='Premium_'+kind+'_'+image.name;image.filepath_raw=str(O/(image.name+'.png'));image.save()
materials={}
for name in ['Fur','Pants','Eyes','Nose','Teeth','Mouth','Claws']:
 m=bpy.data.materials.new('NativePremium_'+name);m.use_nodes=True;shader=m.node_tree.nodes['Principled BSDF'];shader.inputs['Metallic'].default_value=0;shader.inputs['Roughness'].default_value=.91 if name=='Fur' else .84 if name=='Pants' else .5
 if name in maps:
  color,normal=maps[name];tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=color;m.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=normal;convert=m.node_tree.nodes.new('ShaderNodeNormalMap');convert.inputs['Strength'].default_value=.5;m.node_tree.links.new(n.outputs['Color'],convert.inputs['Color']);m.node_tree.links.new(convert.outputs['Normal'],shader.inputs['Normal'])
 else:shader.inputs['Base Color'].default_value={'Eyes':(.08,.42,.5,1),'Nose':(.008,.012,.015,1),'Teeth':(.74,.69,.55,1),'Mouth':(.008,.003,.005,1),'Claws':(.025,.03,.035,1)}[name]
 materials[name]=m
arm=bpy.data.armatures.new('ImmutablePower42');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n in body.nodes:
 bone=arm.edit_bones.new(n.name);bone.head=(0,0,0);bone.tail=(0,2,0);bone.matrix=n.bind_matrix
 if n.parent:bone.parent=arm.edit_bones[n.parent.name]
bpy.ops.object.mode_set(mode='OBJECT');mesh=bpy.data.meshes.new('NativePremiumBody');mesh.from_pydata([v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new('Body_bilge',mesh);bpy.context.collection.objects.link(obj);obj.parent=rig
for m in materials.values():mesh.materials.append(m)
layer=mesh.uv_layers.new(name='BodyUV');normals=[]
def region(face):
 ids=[c.vertex_index for c in face.vertices];p=sum((lod.vertices[i].location for i in ids),Vector())/3;count,c=parts[ids[0]]
 if c.y>129 and -16<c.z<-11 and 2.5<abs(c.x)<4 and count==10:return 'Eyes'
 if c.y>120 and c.z<-13 and count<=15:return 'Teeth'
 normal=sum((lod.vertices[i].normal for i in ids),Vector())/3
 if abs(p.x)<4.5 and p.z<-12 and ((p.y>124 and normal.y<-.3) or (119<p.y<125 and normal.y>.3)):return 'Mouth'
 if count==13 and c.y<120 and c.z<-13:return 'Mouth'
 if p.z<-21 and p.y>127.5 and abs(p.x)<3:return 'Nose'
 if p.y<6 or p.y<75 and abs(p.x)>46:return 'Claws'
 return 'Fur'
for f,source_face in zip(mesh.polygons,lod.faces):
 f.use_smooth=True;f.material_index=list(materials).index(region(source_face))
 for li,c in zip(f.loop_indices,source_face.vertices):layer.data[li].uv=(c.texcoord[0],1-c.texcoord[1]);normals.append(lod.vertices[c.vertex_index].normal)
mesh.normals_split_custom_set(normals)
for i,n in enumerate(body.nodes):
 group=obj.vertex_groups.new(name=n.name)
 for vi,v in enumerate(lod.vertices):
  for w in v.weights:
   if w.node_index==i:group.add([vi],w.bias,'REPLACE')
# Split actual geometry at the waistband and cuffs, so the boundary is smooth.
bm=bmesh.new();bm.from_mesh(mesh)
for height in [76,13]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,height,0),plane_no=(0,1,0),clear_inner=False,clear_outer=False)
for f in bm.faces:
 p=f.calc_center_median()
 if 13<p.y<76 and abs(p.x)<25:f.material_index=list(materials).index('Pants')
bm.to_mesh(mesh);bm.free();mesh.update();bpy.context.view_layer.objects.active=obj;obj.select_set(True)
# Simple subdivision interpolates the proven native weights without inventing
# a new rest skeleton; retain the original head, jaw, teeth and limb lengths.
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.subdivide_edges(bm,edges=[e for e in bm.edges if all(v.co.y<117 for v in e.verts)],cuts=1,use_grid_fill=True);bm.to_mesh(mesh);bm.free();mesh.update()
obj.modifiers.new('NativeSkin','ARMATURE').object=rig;rig.matrix_world=T;base.common.tattoos(obj,rig,body,T,motion_source=MOTION);rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@T;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'wolf-static.blend'));bpy.ops.export_scene.gltf(filepath=str(O/'wolf-static.glb'),export_format='GLB',export_animations=False,export_extras=True);exporter.OUT=O;report=exporter.build('wolf',{'modelType':'power42','wardrobeOrigin':'original_authored_on_selected_body','nativeMouthGeometry':True,'nativeJawBone':'Bip01 Ponytail2','mouthGeometryOrigin':'native oral geometry and original weights; no external mouth patches','bodyGeometryOrigin':'selected Power42 topology with interpolated source skin refinement','originalAppearanceSource':'01a18823-7e5f-7422-8ae2-b27a15865086','sourceClothingTexturesUsed':False,'fittedPants':True,'longHangingPanels':False,'nativeLocomotion':{'quadClip':'T_WallDash','walkStrideMeters':2.8942126751800683,'runStrideMeters':2.5106097294977214}},body_source=BODY,motion_source=MOTION);report.update(native_skin_refinement='SIMPLE subdivision of original native weights',generated_mesh_forced_onto_skeleton=False,source_dtx_pixels_used=False,paid_original_appearance_task='01a18823-7e5f-7422-8ae2-b27a15865086');(D/'native-final-build.json').write_text(json.dumps(report,indent=2));print('NATIVE_PREMIUM_FINAL',report)
