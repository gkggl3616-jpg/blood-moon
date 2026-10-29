"""Fit original generated meshes to immutable native skeletons, without authoring motion.
Exports static skin; attach_native_clips.py supplies unchanged native keys separately.
"""
import bpy,bmesh,sys,types,importlib,json,math,statistics
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
OUT=R/'art/characters/bilge-original/working';OUT.mkdir(parents=True,exist_ok=True)
SOURCES={'wolf':'20261028_200509_bilge-original-wolf_01a1841d','human':'20261028_200757_bilge-original-human_01a1841f'}
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def bary(p,a,b,c):
 u=b-a;v=c-a;w=p-a;den=u.dot(u)*v.dot(v)-u.dot(v)**2
 if abs(den)<1e-12:return [1,0,0]
 y=(v.dot(v)*w.dot(u)-u.dot(v)*w.dot(v))/den;z=(u.dot(u)*w.dot(v)-u.dot(v)*w.dot(u))/den;co=[max(0,1-y-z),max(0,y),max(0,z)];return [a/sum(co) for a in co]
def surface(body):
 vertices=[];faces=[];weights=[]
 for p in body.pieces:
  if p.name.lower().startswith('tattoo'):continue
  lod=p.lods[0];off=len(vertices);vertices += [v.location.copy() for v in lod.vertices];faces += [tuple(off+c.vertex_index for c in f.vertices) for f in lod.faces];weights += [{w.node_index:w.bias for w in v.weights} for v in lod.vertices]
 return vertices,faces,weights,BVHTree.FromPolygons(vertices,faces,all_triangles=True)
def fit_and_skin(mesh,body,T,form):
 # Mesh landmarks move toward the fixed native bind skeleton; bones never move.
 h=2.4 if form=='wolf' else 1.85
 src=[Vector((.34,-.12,1.84)),Vector((.52,-.12,1.61)),Vector((.68,-.12,1.35)),Vector((.64,-.12,1.10))] if form=='wolf' else [Vector((.21,-.075,1.45)),Vector((.32,-.11,1.21)),Vector((.445,-.205,.985)),Vector((.435,-.21,.84))]
 # Art is centered on its own pelvis; native mesh has an offset in depth.
 depth=-.12 if form=='wolf' else -.035
 index={n.name:i for i,n in enumerate(body.nodes)};anchor_names=['UpperArm','Forearm','Hand','Finger11']
 for name in ['original_arm_mix','original_arm_progress','original_arm_side']:mesh.data.attributes.new(name=name,type='FLOAT',domain='POINT')
 for vertex in mesh.data.vertices:
  co=T@vertex.co;co.y+=depth;sign=1 if co.x>=0 else -1
  if abs(co.x)>(.23 if form=='wolf' else .17) and (h*.36<co.z<h*.83) and (co.z>h*.58 or abs(co.x)>h*.23):
   point=Vector((abs(co.x),co.y,co.z));nearest=None
   for j in range(3):
    a,b=src[j:j+2];u=max(0,min(1,(point-a).dot(b-a)/(b-a).length_squared));distance=(point-a.lerp(b,u)).length
    if nearest is None or distance<nearest[0]:nearest=(distance,j,u)
   distance,j,u=nearest
   mix=1-smooth((distance-(.08 if form=='human' else .11))/(.08 if form=='human' else .14))
   mesh.data.attributes['original_arm_mix'].data[vertex.index].value=mix
   mesh.data.attributes['original_arm_progress'].data[vertex.index].value=j+u
   mesh.data.attributes['original_arm_side'].data[vertex.index].value=sign
   side='R' if sign>0 else 'L';target=[T@body.nodes[index['Bip01 '+side+' '+name]].bind_matrix.to_translation() for name in anchor_names]
   a,b=src[j:j+2];a=a.copy();b=b.copy();a.x*=sign;b.x*=sign;origin=a.lerp(b,u);goal=target[j].lerp(target[j+1],u)
   rotation=(b-a).rotation_difference(target[j+1]-target[j]);radial=co-origin;result=goal+radial
   fade=smooth((abs(co.x)-(.23 if form=='wolf' else .17))/(.16 if form=='wolf' else .13));fade*=mix
   co=co.lerp(result,fade)
  vertex.co=T.inverted()@co
 mesh.data.update();verts,faces,weights,tree=surface(body);groups=[mesh.vertex_groups.new(name=n.name) for n in body.nodes];values=[];distances=[]
 lower_ids={i for i,n in enumerate(body.nodes) if n.name in ['Bip01','Bip01 Pelvis','Bip01 Spine'] or any(part in n.name for part in [' Thigh',' Calf',' Foot',' Toe'])};lower_faces=[f for f in faces if all(sum(w for i,w in weights[v].items() if i in lower_ids)>.5 for v in f)];lower_tree=BVHTree.FromPolygons(verts,lower_faces,all_triangles=True)
 arm_segments=[]
 for side in ['L','R']:
  chain=[T@body.nodes[index['Bip01 '+side+' '+name]].bind_matrix.to_translation() for name in ['UpperArm','Forearm','Hand','Finger1','Finger11']]
  arm_segments += list(zip(chain,chain[1:]))
 def arm_distance(co):
  return min((co-a.lerp(b,max(0,min(1,(co-a).dot(b-a)/(b-a).length_squared)))).length for a,b in arm_segments)
 for vertex in mesh.data.vertices:
  p,normal,face,distance=tree.find_nearest(vertex.co);distances.append(distance);triangle=faces[face];factors=bary(p,*(verts[i] for i in triangle));weights_out={}
  for vi,factor in zip(triangle,factors):
   for i,w in weights[vi].items():weights_out[i]=weights_out.get(i,0)+w*factor
  co=T@vertex.co
  # Reject hand/arm donors for lower clothing. A nearby glove is not a coat bone.
  if mesh.data.attributes['original_arm_mix'].data[vertex.index].value<.01 and co.z<h*.57 and abs(co.x)<h*.35 and not(abs(co.x)>h*.26 and arm_distance(co)<.10):
   weights_out={i:w for i,w in weights_out.items() if i in lower_ids}
   if sum(weights_out.values())<.01:
    lp,ln,lf,ld=lower_tree.find_nearest(vertex.co);triangle=lower_faces[lf];factors=bary(lp,*(verts[i] for i in triangle));weights_out={}
    for vi,factor in zip(triangle,factors):
     for i,w in weights[vi].items():
      if i in lower_ids:weights_out[i]=weights_out.get(i,0)+w*factor
   total=sum(weights_out.values());weights_out={i:w/total for i,w in weights_out.items()}
  # Garment front panels follow pelvis, not an unrelated knee or hand.
  if mesh.data.attributes['original_arm_mix'].data[vertex.index].value<.01 and co.z<h*.5 and co.z>h*.25 and abs(co.x)<h*.045 and co.y<(-.23 if form=='wolf' else -.12):
   pelvis=index['Bip01 Pelvis'];influence=smooth((h*.52-co.z)/(h*.15));weights_out={i:w*(1-influence) for i,w in weights_out.items()};weights_out[pelvis]=weights_out.get(pelvis,0)+influence
  values.append(weights_out)
 # UV seam duplicates share weights; smooth native transfer across anatomical surface.
 weld={};ids=[]
 for vertex in mesh.data.vertices:ids.append(weld.setdefault(tuple(round(v,3) for v in vertex.co),len(weld)))
 W=[{} for _ in weld];counts=[0]*len(weld);adj=[set() for _ in weld]
 for value,wi in zip(values,ids):
  counts[wi]+=1
  for i,w in value.items():W[wi][i]=W[wi].get(i,0)+w
 for i in range(len(W)):W[i]={g:w/counts[i] for g,w in W[i].items()}
 for edge in mesh.data.edges:
  a,b=[ids[i] for i in edge.vertices]
  if a!=b:adj[a].add(b);adj[b].add(a)
 for _ in range(12):
  new=[]
  for i,neighbors in enumerate(adj):
   value={g:w*.5 for g,w in W[i].items()}
   for j in neighbors:
    for g,w in W[j].items():value[g]=value.get(g,0)+w*.5/max(1,len(neighbors))
   new.append(value if neighbors else W[i])
  W=new
 for vertex,wi in zip(mesh.data.vertices,ids):
  top=sorted(W[wi].items(),key=lambda x:-x[1])[:4];total=sum(w for _,w in top);assert total>0
  for i,w in top:
   if w>1e-7:groups[i].add([vertex.index],w/total,'REPLACE')
 return {'max_native_distance':max(distances),'p95_native_distance':sorted(distances)[int(.95*(len(distances)-1))],'unweighted':sum(not v.groups for v in mesh.data.vertices)}
def heat_skin_original_geometry(mesh,body,T,form):
 # Temporary weighting guides use anatomical joint segments. They are removed;
 # the delivered skeleton still has the exact native matrices and bone count.
 allowed=[n for n in body.nodes if n.name.startswith('Bip01 ') and n.name not in ['Bip01 Ponytail1','Bip01 Ponytail11']]
 original=mesh;mesh=mesh.copy();mesh.data=original.data.copy();bpy.context.collection.objects.link(mesh);mesh.name='TemporaryWeldedWeightSurface';bm=bmesh.new();bm.from_mesh(mesh.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.015);bm.to_mesh(mesh.data);bm.free();print('HEAT_WELD',len(original.data.vertices),len(mesh.data.vertices));native={n.name:i for i,n in enumerate(body.nodes)};lookup={n.name:n for n in body.nodes};backup=[{original.vertex_groups[g.group].name:g.weight for g in v.groups} for v in original.data.vertices]
 arm=bpy.data.armatures.new('TemporaryHeatGuides');helper=bpy.data.objects.new('TemporaryHeatGuides',arm);bpy.context.collection.objects.link(helper);bpy.context.view_layer.objects.active=helper;helper.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in allowed:
  bone=arm.edit_bones.new(n.name);bone.head=n.bind_matrix.to_translation();suffix=n.name.split(' ')[-1];target={'Pelvis':'Bip01 Spine','Spine':'Bip01 Spine1','Spine1':'Bip01 Spine2','Spine2':'Bip01 Neck','Neck':'Bip01 Head'}.get(suffix)
  if n.name.startswith(('Bip01 L ','Bip01 R ')):
   prefix=n.name[:8];target=prefix+{'Clavicle':'UpperArm','UpperArm':'Forearm','Forearm':'Hand','Hand':'Finger1','Thigh':'Calf','Calf':'Foot','Foot':'Toe0'}.get(suffix,'')
   if suffix.startswith('Finger') and len(suffix)==7:target=prefix+suffix+'1'
  if target and target in lookup:bone.tail=lookup[target].bind_matrix.to_translation()
  elif n.name=='Bip01 Head':bone.tail=bone.head+Vector((0,8,0))
  elif n.name=='Bip01 Ponytail2':bone.tail=bone.head+Vector((0,-2,-4))
  elif n.parent:
   direction=bone.head-n.parent.bind_matrix.to_translation();bone.tail=bone.head+direction.normalized()*max(2,min(5,direction.length*.5))
  else:bone.tail=bone.head+Vector((0,3,0))
  if (bone.tail-bone.head).length<.05:bone.tail=bone.head+Vector((0,2,0))
  if n.parent and n.parent.name in arm.edit_bones:bone.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT');mesh.vertex_groups.clear();bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);helper.select_set(True);bpy.context.view_layer.objects.active=helper
 try:bpy.ops.object.parent_set(type='ARMATURE_AUTO')
 except RuntimeError:pass
 values=[{mesh.vertex_groups[g.group].name:g.weight for g in v.groups} for v in mesh.data.vertices];unweighted=sum(not v for v in values)
 if not unweighted:
  from mathutils.kdtree import KDTree
  tree=KDTree(len(mesh.data.vertices))
  for v in mesh.data.vertices:tree.insert(v.co,v.index)
  tree.balance();values=[values[tree.find(v.co)[1]] for v in original.data.vertices]
 else:values=backup
 if form=='human':values=backup
 bpy.data.objects.remove(mesh,do_unlink=True);bpy.data.objects.remove(helper,do_unlink=True);mesh=original;mesh.vertex_groups.clear()
 groups={n.name:mesh.vertex_groups.new(name=n.name) for n in body.nodes}
 h=2.4 if form=='wolf' else 1.85
 segments=[]
 for side in ['L','R']:
  chain=[T@lookup['Bip01 '+side+' '+name].bind_matrix.to_translation() for name in ['Forearm','Hand','Finger1','Finger11']]
  segments+=list(zip(chain,chain[1:]))
 def hand_distance(co):
  return min((co-a.lerp(b,max(0,min(1,(co-a).dot(b-a)/(b-a).length_squared)))).length for a,b in segments)
 for v,value in zip(mesh.data.vertices,values):
  co=T@v.co
  mix=mesh.data.attributes['original_arm_mix'].data[v.index].value
  progress=mesh.data.attributes['original_arm_progress'].data[v.index].value
  side='R' if mesh.data.attributes['original_arm_side'].data[v.index].value>0 else 'L'
  if mix>0 and form!='human':
   target={}
   if progress<.8:target={'Bip01 '+side+' UpperArm':1}
   elif progress<1.2:
    blend=smooth((progress-.8)/.4);target={'Bip01 '+side+' UpperArm':1-blend,'Bip01 '+side+' Forearm':blend}
   elif progress<1.8:target={'Bip01 '+side+' Forearm':1}
   elif progress<2.2:
    blend=smooth((progress-1.8)/.4);target={'Bip01 '+side+' Forearm':1-blend,'Bip01 '+side+' Hand':blend}
   else:target={'Bip01 '+side+' Hand':1}
   value={name:w*(1-mix) for name,w in value.items()}
   for name,w in target.items():value[name]=value.get(name,0)+w*mix
  # The original hand shape is retained; wrong finger donors cannot pull a cuff.
  collapsed={}
  for name,w in value.items():
   name=name[:8]+'Hand' if ' Finger' in name else name
   collapsed[name]=collapsed.get(name,0)+w
  value=collapsed
  if form!='human' and co.z<h*.59 and mix<1:
   lower={name:w for name,w in value.items() if name in ['Bip01','Bip01 Pelvis','Bip01 Spine'] or any(part in name for part in [' Thigh',' Calf',' Foot',' Toe'])}
   total=sum(lower.values());lower={name:w/total for name,w in lower.items()} if total>.01 else {'Bip01 Pelvis':1}
   influence=(1-mix)*smooth((h*.59-co.z)/(h*.05))
   value={name:w*(1-influence) for name,w in value.items()}
   for name,w in lower.items():value[name]=value.get(name,0)+w*influence
  top=sorted([(name,w) for name,w in value.items() if name in native],key=lambda x:-x[1])[:4];total=sum(w for _,w in top);assert total>0
  for name,w in top:
   if w>1e-7:groups[name].add([v.index],w/total,'REPLACE')
 return {'method':('native_surface_transfer' if form=='human' else 'anatomical_heat_guides' if not unweighted else 'native_transfer_fallback'),'heat_unweighted_vertices':unweighted}

def split_native_jaw(mesh,T):
 # Open a real mouth seam on the new mesh; retain the existing source jaw bone.
 bm=bmesh.new();bm.from_mesh(mesh.data);plane=T.inverted()@Vector((0,0,2.145));normal=(T.to_3x3().transposed()@Vector((0,0,1))).normalized()
 faces=[f for f in bm.faces if (lambda p: abs(p.x)<.14 and p.y<-.27 and 2.03<p.z<2.3)(T@f.calc_center_median())]
 geom=set(faces)
 for f in faces:geom.update(f.edges);geom.update(f.verts)
 result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.0001,plane_co=plane,plane_no=normal,clear_outer=False,clear_inner=False)
 edges=[e for e in result['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and all((T@v.co).y<-.285 for v in e.verts)]
 if edges:bmesh.ops.split_edges(bm,edges=edges)
 bm.to_mesh(mesh.data);bm.free();mesh.data.update();jaw=mesh.vertex_groups.get('Bip01 Ponytail2');head=mesh.vertex_groups.get('Bip01 Head');neighbors=[[] for v in mesh.data.vertices]
 for f in mesh.data.polygons:
  z=sum((T@mesh.data.vertices[i].co).z for i in f.vertices)/len(f.vertices)
  for i in f.vertices:neighbors[i].append(z)
 count=0
 for v in mesh.data.vertices:
  co=T@v.co;mouth=abs(co.x)<.12 and co.y<-.27 and 2.025<co.z<2.28
  jaw_weight=next((g.weight for g in v.groups if g.group==jaw.index),0)
  if mouth:
   low=co.z<2.1449 or (abs(co.z-2.145)<.0002 and neighbors[v.index] and sum(neighbors[v.index])/len(neighbors[v.index])<2.145)
   for group in mesh.vertex_groups:group.remove([v.index])
   (jaw if low else head).add([v.index],1,'REPLACE');count+=1
  elif jaw_weight:
   jaw.remove([v.index]);old=next((g.weight for g in v.groups if g.group==head.index),0);head.add([v.index],old+jaw_weight,'REPLACE')
 return {'seam_edges':len(edges),'mouth_vertices':count,'jaw_bone':'Bip01 Ponytail2'}
def mouth_geometry(rig,T):
 materials={}
 for name,color,roughness in [('Mouth_original',(.035,.009,.016,1),.8),('Teeth_original',(.72,.67,.5,1),.52)]:
  m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=roughness;materials[name]=m
 def finish(obj,name,bone,mat):
  obj.name=name
  bpy.context.view_layer.update();transform=obj.matrix_world.copy()
  for v in obj.data.vertices:v.co=T.inverted()@(transform@v.co)
  obj.matrix_world=Matrix.Identity(4);obj.parent=rig;obj.matrix_basis=Matrix.Identity(4);obj.matrix_parent_inverse=Matrix.Identity(4);g=obj.vertex_groups.new(name=bone);g.add(list(range(len(obj.data.vertices))),1,'REPLACE');mod=obj.modifiers.new('NativeSkin','ARMATURE');mod.object=rig;obj.data.materials.append(materials[mat])
 for lower in [False,True]:
  bone='Bip01 Ponytail2' if lower else 'Bip01 Head'
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(0,-.355,2.14 if lower else 2.15));o=bpy.context.object;o.scale=(.071,.066,.019);finish(o,'Mouth_inner_lower' if lower else 'Mouth_inner_upper',bone,'Mouth_original')
  for i in range(9):
   x=(i-4)*.015;y=-.395+abs(i-4)*.006;length=.04 if i in [1,7] else .023
   bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.007,radius2=0,depth=length,location=(x,y,2.145+(length/2 if lower else -length/2)))
   o=bpy.context.object
   if not lower:o.rotation_euler.x=math.pi
   finish(o,f'Teeth_{"lower" if lower else "upper"}_{i}',bone,'Teeth_original')

def expose_original_back(mesh,T):
 data=mesh.data;data.calc_loop_triangles();triangles=list(data.loop_triangles);tree=BVHTree.FromPolygons([v.co for v in data.vertices],[tuple(t.vertices) for t in triangles],all_triangles=True);uv=data.uv_layers.active;original=[v.uv.copy() for v in uv.data];count=0
 for polygon in data.polygons:
  center=T@(sum((data.vertices[i].co for i in polygon.vertices),Vector())/len(polygon.vertices))
  if not(abs(center.x)<.205 and 1.48<center.z<1.96 and center.y>.005):continue
  for li in polygon.loop_indices:
   co=T@data.vertices[data.loops[li].vertex_index].co;z=1.73+(co.z-1.72)*.3;origin=T.inverted()@Vector((co.x*.3,-1.5,z));direction=(T.inverted().to_3x3()@Vector((0,1,0))).normalized();point,normal,face,distance=tree.ray_cast(origin,direction,200)
   if point is not None:
    tri=triangles[face];factors=bary(point,*(data.vertices[i].co for i in tri.vertices));value=sum((original[i]*w for i,w in zip(tri.loops,factors)),Vector((0,0)));uv.data[li].uv=value
  count+=1
 mesh['back_fur_uses_original_generated_chest_atlas']=True;mesh['back_fur_faces']=count

def tattoos(mesh,rig,body,T):
 data=mesh.data;data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in data.vertices],[tuple(f.vertices) for f in data.loop_triangles],all_triangles=True);triangles=[tuple(f.vertices) for f in data.loop_triangles]
 atlas=bpy.data.images.load(str(R/'art/3d/textures/tattoo-atlas.png'),check_existing=True);atlas.pack()
 for slot in ['back','left','right']:
  vertices=[];uvs=[];faces=[];weights=[];cols=6;rows=8
  if slot=='back':center=Vector((0,1.72,.2));width=.36;height=.43;axis=2
  else:
   side='L' if slot=='left' else 'R';a=T@next(n.bind_matrix.to_translation() for n in body.nodes if n.name=='Bip01 '+side+' UpperArm');b=T@next(n.bind_matrix.to_translation() for n in body.nodes if n.name=='Bip01 '+side+' Forearm');center=a.lerp(b,.45);width=.13;height=.22;axis=2
  # Coordinates are first assembled in Blender world, then raycast in native space.
  for row in range(rows+1):
   for col in range(cols+1):
    u=col/cols;v=row/rows
    world=Vector(((u-.5)*width,1.72+(v-.5)*height,0)) if slot=='back' else Vector((center.x+(u-.5)*width,center.z+(v-.5)*height,0))
    co=Vector((world.x,1.0,world.y)) if slot=='back' else Vector((world.x,-1.0,world.y));direction=Vector((0,-1,0)) if slot=='back' else Vector((0,1,0));origin=T.inverted()@co;native_dir=(T.inverted().to_3x3()@direction).normalized();hit,normal,face,distance=tree.ray_cast(origin,native_dir,200)
    if hit is None:vertices.append(None);weights.append({});uvs.append((u,v));continue
    point=hit+normal*.05;vertices.append(point);uvs.append((u,v));inds=triangles[face];factors=bary(hit,*(data.vertices[i].co for i in inds));value={}
    for vi,factor in zip(inds,factors):
     for g in data.vertices[vi].groups:value[g.group]=value.get(g.group,0)+g.weight*factor
    weights.append(value)
  for row in range(rows):
   for col in range(cols):
    a=row*(cols+1)+col;b=a+1;c=a+cols+2;d=a+cols+1
    if all(vertices[i] is not None for i in [a,b,c,d]):faces.extend([(a,c,b),(a,d,c)] if slot=='back' else [(a,b,c),(a,c,d)])
  if not faces:continue
  used=sorted({i for f in faces for i in f});remap={i:n for n,i in enumerate(used)};geo=bpy.data.meshes.new('TattooSkin');geo.from_pydata([vertices[i] for i in used],[],[tuple(remap[i] for i in f) for f in faces]);obj=bpy.data.objects.new('Tattoo_'+slot+'_surface',geo);bpy.context.collection.objects.link(obj);obj.parent=rig
  # Initial atlas cell: top-left dragon, renderer can replace motif while retaining UVs.
  rect=[0,0,426,431];base=(rect[0]/1274,1-rect[3]/1234,(rect[2]-rect[0])/1274,(rect[3]-rect[1])/1234);layer=geo.uv_layers.new(name='TattooAtlas')
  for loop in geo.loops:
   u,v=uvs[used[loop.vertex_index]];layer.data[loop.index].uv=(base[0]+u*base[2],base[1]+v*base[3])
  obj['atlas_uv_base']=list(base)
  for i,n in enumerate(body.nodes):
   group=obj.vertex_groups.new(name=n.name)
   for vi,original in enumerate(used):
    if weights[original].get(i,0)>1e-7:group.add([vi],weights[original][i],'REPLACE')
  modifier=obj.modifiers.new('NativeSkin','ARMATURE');modifier.object=rig
  mat=bpy.data.materials.new('Tattoo_'+slot);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],shader.inputs['Alpha']);shader.inputs['Roughness'].default_value=.9;geo.materials.append(mat)
def merge_mouth_geometry():
 parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Mouth_','Teeth_'))]
 if not parts:return
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();bpy.context.object.name='Mouth_original_surface'

def build(form):
 bpy.ops.wm.read_factory_settings(use_empty=True);source=R/'meshy_output'/SOURCES[form]/'source.glb';bpy.ops.import_scene.gltf(filepath=str(source));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1;mesh=meshes[0];coords=[mesh.matrix_world@v.co for v in mesh.data.vertices];low=Vector(tuple(min(v[i] for v in coords) for i in range(3)));high=Vector(tuple(max(v[i] for v in coords) for i in range(3)));height=2.4 if form=='wolf' else 1.85;factor=height/(high.z-low.z);center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
 body=Reader().from_file(str(R/('art/3d/source/wolfteam-archive/selected/wt_wolf_ice_r.ltb' if form=='wolf' else 'art/3d/source/pedro-native/main/pedro.ltb')));points=[v.location for p in body.pieces for v in p.lods[0].vertices];native_low=min(v.y for v in points);scale=height/(max(v.y for v in points)-native_low);T=Matrix(((-scale,0,0,0),(0,0,scale,0),(0,scale,0,-native_low*scale),(0,0,0,1)))
 for vertex,co in zip(mesh.data.vertices,coords):vertex.co=T.inverted()@((co-center)*factor)
 mesh.parent=None;mesh.matrix_world=Matrix.Identity(4);mesh.name='Body_bilge' if form=='wolf' else 'Body_human_bilge';mesh.vertex_groups.clear()
 for modifier in list(mesh.modifiers):mesh.modifiers.remove(modifier)
 # Recompute smooth normals after local bind fitting rather than keeping unwarped normals.
 for poly in mesh.data.polygons:poly.use_smooth=True
 mesh.data.normals_split_custom_set([(0,0,0)]*len(mesh.data.loops))
 stats=fit_and_skin(mesh,body,T,form);stats.update(heat_skin_original_geometry(mesh,body,T,form))
 if form=='wolf':stats['mouth']=split_native_jaw(mesh,T)
 arm=bpy.data.armatures.new('ImmutableNativeSkeleton');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in body.nodes:
  bone=arm.edit_bones.new(n.name);bone.head=(0,0,0);bone.tail=(0,2,0);bone.matrix=n.bind_matrix
  if n.parent:bone.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT');error=max(abs(arm.bones[n.name].matrix_local[i][j]-n.bind_matrix[i][j]) for n in body.nodes for i in range(4) for j in range(4));assert error<.001
 rig.matrix_world=T;mesh.parent=rig;mesh.matrix_basis=Matrix.Identity(4);mesh.matrix_parent_inverse=Matrix.Identity(4);modifier=mesh.modifiers.new('NativeSkin','ARMATURE');modifier.object=rig
 mesh['model_type']='ice40' if form=='wolf' else 'human47';mesh['source_kind']='new_original_bilge';mesh['texture_origin']='original_authored_meshy';mesh['walk_stride_m']=4.3*.933 if form=='wolf' else 3.6;mesh['run_stride_m']=8*.733 if form=='wolf' else 0;mesh['stride_origin']='runtime_speed_contract_not_measured_foot_contact';mesh['run_reference_speed_mps']=8
 if form=='wolf':expose_original_back(mesh,T);tattoos(mesh,rig,body,T);mouth_geometry(rig,T);merge_mouth_geometry()
 rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@T
 for image in bpy.data.images:
  if image.size[0]>2048 or image.size[1]>2048:
   image.scale(min(2048,image.size[0]),min(2048,image.size[1]));image.pack()
 bpy.ops.file.pack_all();bpy.context.scene['native_animation_edit_permitted']=False;out=OUT/(form+'-static');bpy.ops.wm.save_as_mainfile(filepath=str(out.with_suffix('.blend')));bpy.ops.export_scene.gltf(filepath=str(out.with_suffix('.glb')),export_format='GLB',export_animations=False,export_extras=True)
 triangles=0
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 return {'form':form,'source':str(source.relative_to(R)),'bones':len(body.nodes),'triangles':triangles,'bind_matrix_error':error,'skin':stats,'animation_edits':False}
forms=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['wolf','human'];report=[build(form) for form in forms];(R/'docs/bilge-original-complete/static-build.json').write_text(json.dumps(report,indent=2));print('ORIGINAL_STATIC_BUILD',json.dumps(report))
