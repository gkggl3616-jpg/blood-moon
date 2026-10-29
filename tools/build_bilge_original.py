"""LEGACY generated-pair repair only; future production follows MODEL-URETIM-STANDARDI-TR.md.
Fit original generated meshes to immutable native skeletons, without authoring motion.
Exports static skin; attach_native_clips.py supplies unchanged native keys separately.
"""
import bpy,bmesh,sys,types,importlib,json,math,statistics
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
OUT=R/'art/characters/bilge-original/working';OUT.mkdir(parents=True,exist_ok=True)
GEOMETRY_CAGE_SKINS={}
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
def fit_geometry_with_anatomical_cage(mesh,body,T,form,landmarks=None):
 # Temporary geometry-only cage fits the generated bind shape to native joints.
 # It is discarded; native skeleton and animation data are not modified.
 from mathutils.kdtree import KDTree
 h=2.4 if form=='wolf' else 1.85;depth=-.12 if form=='wolf' else -.035
 arm=[Vector((.34,-.12,1.84)),Vector((.52,-.12,1.61)),Vector((.68,-.12,1.35)),Vector((.64,-.12,1.10))] if form=='wolf' else [Vector((.21,-.075,1.45)),Vector((.32,-.11,1.21)),Vector((.445,-.205,.985)),Vector((.435,-.21,.84))]
 heights=[1.14,1.25,1.48,1.72,1.98,2.15,2.38] if form=='wolf' else [.94,1.05,1.20,1.38,1.55,1.68,1.83]
 labels=['Pelvis','Spine','Spine1','Spine2','Neck','Head','Top'];own={'Bip01 '+n:Vector((0,depth,z)) for n,z in zip(labels,heights)};links={}
 for a,b in zip(labels,labels[1:]):links['Bip01 '+a]='Bip01 '+b
 for side,sign in [('L',-1),('R',1)]:
  prefix='Bip01 '+side+' ';own[prefix+'Clavicle']=Vector((sign*.08,depth,heights[3]));links[prefix+'Clavicle']=prefix+'UpperArm'
  for name,p in zip(['UpperArm','Forearm','Hand','Fingertip'],arm):own[prefix+name]=Vector((sign*p.x,p.y,p.z))
  for a,b in [('UpperArm','Forearm'),('Forearm','Hand'),('Hand','Fingertip')]:links[prefix+a]=prefix+b
  for name,p in [('Thigh',(.16 if form=='wolf' else .11,depth,heights[0])),('Calf',(.24 if form=='wolf' else .13,depth,.57 if form=='wolf' else .52)),('Foot',(.25 if form=='wolf' else .13,depth,.13 if form=='wolf' else .10)),('Toe0',(.25 if form=='wolf' else .13,depth-.15,.04)),('Toetip',(.25 if form=='wolf' else .13,depth-.23,.03))]:own[prefix+name]=Vector((sign*p[0],p[1],p[2]))
  for a,b in [('Thigh','Calf'),('Calf','Foot'),('Foot','Toe0'),('Toe0','Toetip')]:links[prefix+a]=prefix+b
 if landmarks:own.update({name:Vector(value) for name,value in landmarks.items()})
 native={n.name:n.bind_matrix.to_translation() for n in body.nodes};target={n:p.copy() for n,p in native.items()};target['Bip01 Top']=native['Bip01 Head']+Vector((0,(heights[-1]-heights[-2])/abs(T.to_scale().x),0))
 for side in ['L','R']:
  prefix='Bip01 '+side+' ';target[prefix+'Fingertip']=native[prefix+'Finger11'];target[prefix+'Toe0']=native.get(prefix+'Toe0',native[prefix+'Foot']+Vector((0,-2,-8)));target[prefix+'Toetip']=target[prefix+'Toe0']+Vector((0,0,-5))
  if prefix+'Toe0' not in native:
   foot_id=next(i for i,n in enumerate(body.nodes) if n.name==prefix+'Foot');samples=[v.location for p in body.pieces for v in p.lods[0].vertices if sum(w.bias for w in v.weights if w.node_index==foot_id)>.7]
   if samples:
    floor=min(p.y for p in samples);front=min(p.z for p in samples if p.y<floor+3);x=native[prefix+'Foot'].x;target[prefix+'Toe0']=Vector((x,floor+1,front+2));target[prefix+'Toetip']=Vector((x,floor+.5,front))

 for v in mesh.data.vertices:
  p=T@v.co;p.y+=depth;v.co=T.inverted()@p
 helper_mesh=mesh.copy();helper_mesh.data=mesh.data.copy();bpy.context.collection.objects.link(helper_mesh);bm=bmesh.new();bm.from_mesh(helper_mesh.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.015);bm.to_mesh(helper_mesh.data);bm.free();helper_mesh.vertex_groups.clear();armdata=bpy.data.armatures.new('GeometryFitOnly');helper=bpy.data.objects.new('GeometryFitOnly',armdata);bpy.context.collection.objects.link(helper);bpy.context.view_layer.objects.active=helper;helper.select_set(True);bpy.ops.object.mode_set(mode='EDIT');matrices={}
 for name,end in links.items():
  a=T.inverted()@own[name];b=T.inverted()@own[end];bone=armdata.edit_bones.new(name);bone.head=a;bone.tail=b;ta=target[name];tb=target[end];u=(b-a).normalized();v=(tb-ta).normalized();rotation=u.rotation_difference(v).to_matrix().to_4x4();ratio=(tb-ta).length/(b-a).length;stretch=Matrix.Identity(4)
  for row in range(3):
   for col in range(3):stretch[row][col]+=(ratio-1)*u[row]*u[col]
  matrices[name]=Matrix.Translation(ta)@rotation@stretch@Matrix.Translation(-a)
 bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.object.select_all(action='DESELECT');helper_mesh.select_set(True);helper.select_set(True);bpy.context.view_layer.objects.active=helper;bpy.ops.object.parent_set(type='ARMATURE_AUTO');values=[{helper_mesh.vertex_groups[g.group].name:g.weight for g in v.groups} for v in helper_mesh.data.vertices];assert all(values),'Geometry fitting cage contains unweighted vertices';tree=KDTree(len(helper_mesh.data.vertices))
 for v in helper_mesh.data.vertices:tree.insert(v.co,v.index)
 tree.balance()
 bound_weights=[]
 for v in mesh.data.vertices:
  value=dict(sorted(values[tree.find(v.co)[1]].items(),key=lambda item:-item[1])[:4]);total=sum(value.values());value={name:w/total for name,w in value.items()};bound_weights.append(value);v.co=sum(((matrices[name]@v.co)*w for name,w in value.items()),Vector())
 GEOMETRY_CAGE_SKINS[mesh.name]=bound_weights
 bpy.data.objects.remove(helper_mesh,do_unlink=True);bpy.data.objects.remove(helper,do_unlink=True);mesh.data.update();return {'method':'temporary_own_anatomical_heat_cage','native_bones_changed':False,'guide_bones':len(links)}

def fit_and_skin(mesh,body,T,form):
 geometry_fit=fit_geometry_with_anatomical_cage(mesh,body,T,form)
 h=2.4 if form=='wolf' else 1.85;index={n.name:i for i,n in enumerate(body.nodes)}
 for name in ['original_arm_mix','original_arm_progress','original_arm_side']:mesh.data.attributes.new(name=name,type='FLOAT',domain='POINT')
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
 return {'geometry_fit':geometry_fit,'max_native_distance':max(distances),'p95_native_distance':sorted(distances)[int(.95*(len(distances)-1))],'unweighted':sum(not v.groups for v in mesh.data.vertices)}
def bind_own_cage_skin(mesh,body):
 values=GEOMETRY_CAGE_SKINS[mesh.name];mesh.vertex_groups.clear();groups={n.name:mesh.vertex_groups.new(name=n.name) for n in body.nodes}
 for v,value in zip(mesh.data.vertices,values):
  merged={}
  for name,w in value.items():
   if name not in groups and name.endswith(' Toe0'):name=name[:-4]+'Foot'
   assert name in groups,name
   merged[name]=merged.get(name,0)+w
  total=sum(merged.values())
  for name,w in merged.items():groups[name].add([v.index],w/total,'REPLACE')
 return {'method':'own_geometry_cage_weights','unweighted':sum(not v.groups for v in mesh.data.vertices),'native_bone_count':len(body.nodes),'max_influences':4}

def heat_skin_original_geometry(mesh,body,T,form):
 # Temporary weighting guides use anatomical joint segments. They are removed;
 # the delivered skeleton still has the exact native matrices and bone count.
 allowed=[n for n in body.nodes if n.name.startswith('Bip01 ') and n.name not in ['Bip01 Ponytail1','Bip01 Ponytail11'] and ' Finger' not in n.name]
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
 from mathutils.kdtree import KDTree
 tree=KDTree(len(mesh.data.vertices))
 for v in mesh.data.vertices:tree.insert(v.co,v.index)
 tree.balance();values=[values[tree.find(v.co)[1]] or backup[i] for i,v in enumerate(original.data.vertices)]

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
  # Keep the welded anatomical heat solution; no pelvis/hand region gates.
  collapsed={}
  for name,w in value.items():
   name=name[:8]+'Hand' if ' Finger' in name else name
   collapsed[name]=collapsed.get(name,0)+w
  value=collapsed
  top=sorted([(name,w) for name,w in value.items() if name in native],key=lambda x:-x[1])[:4];total=sum(w for _,w in top);assert total>0
  for name,w in top:
   if w>1e-7:groups[name].add([v.index],w/total,'REPLACE')
 return {'method':('anatomical_heat_guides' if not unweighted else 'anatomical_heat_with_local_native_fallback'),'heat_unweighted_vertices':unweighted}

def regularize_skin(mesh,iterations=8):
 # Smooth abrupt donor changes across the actual surface and UV seam copies.
 weld={};ids=[]
 for v in mesh.data.vertices:ids.append(weld.setdefault(tuple(round(x,3) for x in v.co),len(weld)))
 values=[{} for _ in weld];counts=[0]*len(weld);adj=[set() for _ in weld]
 for v,i in zip(mesh.data.vertices,ids):
  counts[i]+=1
  for g in v.groups:values[i][g.group]=values[i].get(g.group,0)+g.weight
 for i in range(len(values)):values[i]={g:w/counts[i] for g,w in values[i].items()}
 for edge in mesh.data.edges:
  a,b=[ids[i] for i in edge.vertices]
  if a!=b:adj[a].add(b);adj[b].add(a)
 for _ in range(iterations):
  new=[]
  for i,neighbors in enumerate(adj):
   value={g:w*.5 for g,w in values[i].items()}
   for j in neighbors:
    for g,w in values[j].items():value[g]=value.get(g,0)+w*.5/max(1,len(neighbors))
   new.append(value if neighbors else values[i])
  values=new
 for v,i in zip(mesh.data.vertices,ids):
  top=sorted(values[i].items(),key=lambda x:-x[1])[:4];total=sum(w for _,w in top)
  for group in mesh.vertex_groups:group.remove([v.index])
  for g,w in top:
   if w>1e-7:mesh.vertex_groups[g].add([v.index],w/total,'REPLACE')
 return {'iterations':iterations,'welded_vertices':len(weld),'max_influences':4}

def sanitize_anatomical_influences(mesh,T,form):
 h=2.4 if form=='wolf' else 1.85;changed=0
 for v in mesh.data.vertices:
  co=T@v.co;value={mesh.vertex_groups[g.group].name:g.weight for g in v.groups};filtered=value
  if abs(co.x)>h*.21 and h*.36<co.z<h*.79:
   side='R' if co.x>0 else 'L';prefix='Bip01 '+side+' '
   filtered={n:w for n,w in value.items() if n.startswith(prefix) and any(x in n for x in ['Clavicle','UpperArm','Forearm','Hand','Finger'])}
   if not filtered:filtered={prefix+'Hand':1}
  elif abs(co.x)<h*.20 and co.z>h*.52:
   filtered={n:w for n,w in value.items() if not any(x in n for x in [' Thigh',' Calf',' Foot',' Toe'])}
   if not filtered:filtered={'Bip01 Pelvis':1}
  if filtered==value:continue
  total=sum(filtered.values())
  for group in mesh.vertex_groups:group.remove([v.index])
  for name,w in filtered.items():mesh.vertex_groups[name].add([v.index],w/total,'REPLACE')
  changed+=1
 return {'vertices_with_rejected_cross_region_donors':changed}

def reject_distant_donors(mesh,body,T):
 # Use distance to actual anatomical segments, never an abrupt x/z region gate.
 lookup={n.name:n for n in body.nodes};segments={};scale=T.to_scale().x;radius=.10/abs(scale)
 for n in body.nodes:
  a=n.bind_matrix.to_translation();suffix=n.name.split(' ')[-1];target={'Pelvis':'Bip01 Spine','Spine':'Bip01 Spine1','Spine1':'Bip01 Spine2','Spine2':'Bip01 Neck','Neck':'Bip01 Head'}.get(suffix)
  if n.name.startswith(('Bip01 L ','Bip01 R ')):
   prefix=n.name[:8];target=prefix+{'Clavicle':'UpperArm','UpperArm':'Forearm','Forearm':'Hand','Hand':'Finger1','Thigh':'Calf','Calf':'Foot','Foot':'Toe0'}.get(suffix,'')
  b=lookup[target].bind_matrix.to_translation() if target in lookup else a+Vector((0,4,0));segments[n.name]=(a,b)
 for v in mesh.data.vertices:
  values=[]
  for g in v.groups:
   name=mesh.vertex_groups[g.group].name;a,b=segments[name];d=b-a;u=max(0,min(1,(v.co-a).dot(d)/max(.000001,d.length_squared)));distance=(v.co-a.lerp(b,u)).length;values.append((g.group,g.weight,distance))
  minimum=min(d for _,_,d in values);r=max(radius,minimum*.7);hip=(T@lookup['Bip01 Pelvis'].bind_matrix.to_translation()).z;z=(T@v.co).z
  weighted=[]
  for i,w,d in values:
   name=mesh.vertex_groups[i].name;leg_fade=smooth((hip+.08-z)/.16) if any(part in name for part in [' Thigh',' Calf',' Foot',' Toe']) else 1
   weighted.append((i,w*math.exp(-.5*((d-minimum)/r)**2)*leg_fade))
  total=sum(w for _,w in weighted)
  if total<1e-12:weighted=[(mesh.vertex_groups['Bip01 Pelvis'].index,1)];total=1
  for group in mesh.vertex_groups:group.remove([v.index])
  for i,w in weighted:
   if w/total>1e-7:mesh.vertex_groups[i].add([v.index],w/total,'REPLACE')
 return {'physical_distance_radius_m':.10,'hard_region_gates':False}

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
def mouth_geometry(rig,T,body_mesh):
 materials={}
 for name,color,roughness in [('Mouth_original',(.004,.002,.003,1),.9),('Teeth_original',(.72,.67,.5,1),.52)]:
  m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=roughness;materials[name]=m
 def finish(obj,name,bone,mat):
  obj.name=name
  bpy.context.view_layer.update();transform=obj.matrix_world.copy()
  for v in obj.data.vertices:v.co=T.inverted()@(transform@v.co)
  obj.matrix_world=Matrix.Identity(4);obj.parent=rig;obj.matrix_basis=Matrix.Identity(4);obj.matrix_parent_inverse=Matrix.Identity(4);g=obj.vertex_groups.new(name=bone);g.add(list(range(len(obj.data.vertices))),1,'REPLACE');mod=obj.modifiers.new('NativeSkin','ARMATURE');mod.object=rig;obj.data.materials.append(materials[mat])
 samples=[T@v.co for v in body_mesh.data.vertices if abs((T@v.co).x)<.075 and 2.12<(T@v.co).z<2.17 and (T@v.co).y<-.20]
 front=min((p.y for p in samples),default=-.38);opening=front+.018;throat=front+.10;verts=[];faces=[];rings=6;slices=20
 for row in range(rings+1):
  u=row/rings;r=.055*u;y=throat+(opening-throat)*u*u
  for col in range(slices):
   angle=2*math.pi*col/slices;verts.append((r*math.cos(angle),y,2.145+.018*u*math.sin(angle)))
 for row in range(rings):
  for col in range(slices):
   a=row*slices+col;b=row*slices+(col+1)%slices;c=b+slices;d=a+slices;faces.extend([(a,b,c),(a,c,d)])
 geo=bpy.data.meshes.new('RecessedMouthCavity');geo.from_pydata(verts,[],faces);obj=bpy.data.objects.new('Mouth_recessed_cavity',geo);bpy.context.collection.objects.link(obj);finish(obj,'Mouth_recessed_cavity','Bip01 Head','Mouth_original');head=obj.vertex_groups['Bip01 Head'];jaw=obj.vertex_groups.new(name='Bip01 Ponytail2')
 for i,point in enumerate(verts):
  w=smooth((2.15-point[2])/.01);head.remove([i])
  if w<1:head.add([i],1-w,'REPLACE')
  if w>0:jaw.add([i],w,'REPLACE')
 obj['recessed_from_muzzle_m']=.018;obj['solid_external_mouth_spheres']=False
 for lower in [False,True]:
  bone='Bip01 Ponytail2' if lower else 'Bip01 Head'
  for i in range(9):
   x=(i-4)*.015;y=opening+.006+abs(i-4)*.006;length=.04 if i in [1,7] else .023
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

def tattoos(mesh,rig,body,T,motion_source=None):
 policy=json.loads((R/'art/characters/model-families/tattoo-policy.json').read_text());back_policy=policy['back'];height_scale=abs(T.to_scale().x)*(max(v.location.y for p in body.pieces for v in p.lods[0].vertices)-min(v.location.y for p in body.pieces for v in p.lods[0].vertices))/2.4
 # Reuse the actual curved body triangles, not a coarse floating grid.
 # Project in the composed native neutral pose, then inverse-skin edge clips.
 motion=Reader().from_file(str(R/(motion_source or 'art/3d/source/wolfteam-archive/selected/wt_wolf_ice_ch.ltb')));clips={a.name:a for a in motion.animations};indices={n.name:i for i,n in enumerate(body.nodes)};pose=[]
 for i,n in enumerate(body.nodes):
  parent=n;upper=False
  while parent:
   if parent.name=='Bip01 Spine1':upper=True
   parent=parent.parent
  t=clips['UMSt' if upper else 'LSt'].node_keyframe_transforms[i][0];m=Matrix.LocRotScale(t.location,t.rotation.normalized(),Vector((1,1,1)));pose.append(pose[indices[n.parent.name]]@m if n.parent else m)
 skin=[p@n.bind_matrix.inverted() for p,n in zip(pose,body.nodes)];data=mesh.data;data.calc_loop_triangles();triangles=[tuple(f.vertices) for f in data.loop_triangles];posed=[sum(((skin[g.group]@v.co)*g.weight for g in v.groups),Vector()) for v in data.vertices];world=[T@v for v in posed];tree=BVHTree.FromPolygons(posed,triangles,all_triangles=True);atlas=bpy.data.images.load(str(R/'art/3d/textures/tattoo-atlas.png'),check_existing=True);atlas.pack();zero=Matrix([[0.0]*4 for _ in range(4)]);direction=(T.inverted().to_3x3()@Vector((0,1,0))).normalized()
 def clip_polygon(poly,axis,edge,lower):
  out=[]
  for current,previous in zip(poly,poly[-1:]+poly[:-1]):
   p,pw=previous;q,qw=current;ip=p[axis]>=edge if lower else p[axis]<=edge;iq=q[axis]>=edge if lower else q[axis]<=edge
   if ip!=iq:
    t=(edge-p[axis])/(q[axis]-p[axis]);out.append((p.lerp(q,t),pw.lerp(qw,t)))
   if iq:out.append(current)
  return out
 for slot in ['back','left','right']:
  if slot=='back':center=T@pose[indices[back_policy['anchor_lower']]].translation.lerp(pose[indices[back_policy['anchor_upper']]].translation,back_policy['anchor_mix']);center.z+=back_policy['raise_m_at_2_4m_height']*height_scale;width=back_policy['width_m_at_2_4m_height']*height_scale;height=back_policy['height_m_at_2_4m_height']*height_scale
  else:
   side='L' if slot=='left' else 'R';a=T@pose[indices['Bip01 '+side+' UpperArm']].translation;b=T@pose[indices['Bip01 '+side+' Forearm']].translation;center=a.lerp(b,policy['arms']['anchor_mix']);width=policy['arms']['width_m_at_2_4m_height']*height_scale;height=policy['arms']['height_m_at_2_4m_height']*height_scale
  requested_height=height
  left,right=center.x-width/2,center.x+width/2;bottom,top=center.z-height/2,center.z+height/2
  if slot=='back':
   # A back tattoo must clear the waistband, including its transparent margins.
   waist=T@pose[indices['Bip01 Pelvis']].translation;bottom=max(bottom,waist.z+back_policy['minimum_above_pelvis_m_at_2_4m_height']*height_scale);height=top-bottom;assert height>.15
  if slot=='back' and back_policy['preserve_patch_aspect_when_clipped']:
   width*=height/requested_height;left,right=center.x-width/2,center.x+width/2
  vertices=[];weights=[];uvs=[];faces=[]
  for face,inds in enumerate(triangles):
   material=data.materials[data.loop_triangles[face].material_index]
   if any(token in material.name.lower() for token in policy['excluded_material_tokens']) or material.name.lower().rsplit('_',1)[-1] in policy['excluded_material_regions']:continue
   points=[world[i] for i in inds]
   if min(p.x for p in points)>right or max(p.x for p in points)<left or min(p.z for p in points)>top or max(p.z for p in points)<bottom:continue
   mid=sum(points,Vector())/3;origin=T.inverted()@Vector((mid.x,-1.5,mid.z));hit,normal,visible,distance=tree.ray_cast(origin,direction,200)
   if hit is None or visible!=face:continue
   if normal.dot(direction)>0:normal.negate()
   poly=[(point,Vector(tuple(int(k==j) for k in range(3)))) for j,point in enumerate(points)]
   for axis,edge,lower in [(0,left,True),(0,right,False),(2,bottom,True),(2,top,False)]:
    if not poly:break
    poly=clip_polygon(poly,axis,edge,lower)
   if len(poly)<3:continue
   offset=len(vertices)
   for point,factors in poly:
    value={}
    for vi,factor in zip(inds,factors):
     for g in data.vertices[vi].groups:value[g.group]=value.get(g.group,0)+g.weight*factor
    blended=sum((skin[i]*w for i,w in value.items()),zero.copy());native=T.inverted()@point+normal*policy['surface_offset_native_units'];vertices.append(blended.inverted_safe()@native);weights.append(value);uvs.append(((point.x-left)/width,(point.z-bottom)/height))
   for j in range(1,len(poly)-1):faces.append((offset,offset+j,offset+j+1))
  assert faces,('Tattoo patch missed actual body',slot)
  geo=bpy.data.meshes.new('TattooSkin');geo.from_pydata(vertices,[],faces);obj=bpy.data.objects.new('Tattoo_'+slot+'_surface',geo);bpy.context.collection.objects.link(obj);obj.parent=rig;base=(0,1-431/1234,426/1274,431/1234);layer=geo.uv_layers.new(name='TattooAtlas')
  for loop in geo.loops:
   u,v=uvs[loop.vertex_index];layer.data[loop.index].uv=(base[0]+u*base[2],base[1]+v*base[3])
  obj['atlas_uv_base']=list(base);obj['placement_reference']='actual_neutral_body_triangles_back_inverse_skin';obj['surface_offset_native_units']=policy['surface_offset_native_units'];obj['tattoo_policy_version']=policy['version'];obj['clothing_faces_excluded']=True;obj['neutral_min_height_m']=bottom;obj['neutral_max_height_m']=top
  for i,n in enumerate(body.nodes):
   group=obj.vertex_groups.new(name=n.name)
   for vi,value in enumerate(weights):
    if value.get(i,0)>1e-7:group.add([vi],value[i],'REPLACE')
  modifier=obj.modifiers.new('NativeSkin','ARMATURE');modifier.object=rig;mat=bpy.data.materials.new('Tattoo_'+slot);mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas;mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],shader.inputs['Alpha']);shader.inputs['Roughness'].default_value=.9;geo.materials.append(mat)

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
 stats=fit_and_skin(mesh,body,T,form);stats.update(bind_own_cage_skin(mesh,body));stats['regularization']=regularize_skin(mesh,2)
 if form=='wolf':stats['mouth']=split_native_jaw(mesh,T)
 arm=bpy.data.armatures.new('ImmutableNativeSkeleton');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in body.nodes:
  bone=arm.edit_bones.new(n.name);bone.head=(0,0,0);bone.tail=(0,2,0);bone.matrix=n.bind_matrix
  if n.parent:bone.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT');error=max(abs(arm.bones[n.name].matrix_local[i][j]-n.bind_matrix[i][j]) for n in body.nodes for i in range(4) for j in range(4));assert error<.001
 rig.matrix_world=T;mesh.parent=rig;mesh.matrix_basis=Matrix.Identity(4);mesh.matrix_parent_inverse=Matrix.Identity(4);modifier=mesh.modifiers.new('NativeSkin','ARMATURE');modifier.object=rig
 mesh['model_type']='ice40' if form=='wolf' else 'human47';mesh['source_kind']='new_original_bilge';mesh['texture_origin']='original_authored_meshy';mesh['walk_stride_m']=4.3*.933 if form=='wolf' else 3.6;mesh['run_stride_m']=8*.733 if form=='wolf' else 0;mesh['stride_origin']='runtime_speed_contract_not_measured_foot_contact';mesh['run_reference_speed_mps']=8
 if form=='wolf':expose_original_back(mesh,T);tattoos(mesh,rig,body,T);mouth_geometry(rig,T,mesh);merge_mouth_geometry()
 rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@T
 for image in bpy.data.images:
  if image.size[0]>2048 or image.size[1]>2048:
   image.scale(min(2048,image.size[0]),min(2048,image.size[1]));image.pack()
 bpy.ops.file.pack_all();bpy.context.scene['native_animation_edit_permitted']=False;out=OUT/(form+'-static');bpy.ops.wm.save_as_mainfile(filepath=str(out.with_suffix('.blend')));bpy.ops.export_scene.gltf(filepath=str(out.with_suffix('.glb')),export_format='GLB',export_animations=False,export_extras=True)
 triangles=0
 for o in bpy.context.scene.objects:
  if o.type=='MESH':o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 return {'form':form,'source':str(source.relative_to(R)),'bones':len(body.nodes),'triangles':triangles,'bind_matrix_error':error,'skin':stats,'animation_edits':False}
if __name__=='__main__':
 forms=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['wolf','human'];report=[build(form) for form in forms];(R/'docs/bilge-original-complete/static-build.json').write_text(json.dumps(report,indent=2));print('ORIGINAL_STATIC_BUILD',json.dumps(report))
