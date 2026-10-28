"""Fit existing textured bodies to supplied native skeletons; retain source motion.
No external generation. Source LTBs and original GLBs are never overwritten.
"""
import bpy,bmesh,sys,types,importlib,json,math,bisect,statistics
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
ADDON=Path('/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech')
pkg=types.ModuleType('native_lithtech');pkg.__path__=[str(ADDON)];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
OUT=ROOT/'art/3d/native-pair';OUT.mkdir(parents=True,exist_ok=True)
FPS=30

def canon(name):
    if name=='Scene Root':return 'Root'
    if name=='Bip01':return 'Hips'
    for side in ['L','R']:
        prefix='Bip01 '+side+' '
        if name.startswith(prefix):return name[len(prefix):].replace(' ','')+side
    return name.removeprefix('Bip01 ').replace(' ','')

def rest_locals(model):
    return [n.parent.bind_matrix.inverted()@n.bind_matrix if n.parent else n.bind_matrix.copy() for n in model.nodes]

def sample(animation,index,seconds):
    times=[k.time/1000 for k in animation.keyframes];t=times[0]+min(max(0,seconds),times[-1]-times[0])
    j=min(len(times)-1,max(0,bisect.bisect_right(times,t)-1));k=min(len(times)-1,j+1)
    a=animation.node_keyframe_transforms[index][j];b=animation.node_keyframe_transforms[index][k]
    u=(t-times[j])/max(1e-9,times[k]-times[j])
    return a.location.lerp(b.location,u),a.rotation.normalized().slerp(b.rotation.normalized(),u)

def bary(point,a,b,c):
    v0=b-a;v1=c-a;v2=point-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
    if abs(den)<1e-12:return (1,0,0)
    v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den
    values=[max(0,1-v-w),max(0,v),max(0,w)];total=sum(values)
    return tuple(v/total for v in values)

def native_surface(model):
    vertices=[];faces=[];weights=[]
    for piece in model.pieces:
        if piece.name.startswith('Tattoo'):continue
        lod=piece.lods[0];start=len(vertices)
        vertices.extend(v.location.copy() for v in lod.vertices)
        weights.extend({w.node_index:w.bias for w in v.weights} for v in lod.vertices)
        faces.extend(tuple(start+c.vertex_index for c in face.vertices) for face in lod.faces)
    return vertices,faces,weights,BVHTree.FromPolygons(vertices,faces,all_triangles=True)

def bake_native_human(source,body):
    # Keep the native body topology and weights; transfer the existing authored
    # appearance by selected-to-active UV baking rather than deforming a long coat.
    vertices=[];faces=[];weights=[];face_parts=[]
    for piece in body.pieces:
        if piece.name=='Head':continue
        lod=piece.lods[0];offset=len(vertices)
        vertices.extend(v.location.copy() for v in lod.vertices)
        weights.extend({w.node_index:w.bias for w in v.weights} for v in lod.vertices)
        faces.extend(tuple(offset+c.vertex_index for c in f.vertices) for f in lod.faces)
        face_parts.extend([piece.name]*len(lod.faces))
    head=source.copy();head.data=source.data.copy();bpy.context.collection.objects.link(head);head.name='GuardianHumanHead'
    bm=bmesh.new();bm.from_mesh(head.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,97,0),plane_no=(0,1,0),clear_inner=True,clear_outer=False);bm.to_mesh(head.data);bm.free();head.vertex_groups.clear()
    hg=head.vertex_groups.new(name='Head');ng=head.vertex_groups.new(name='Neck')
    for vertex in head.data.vertices:
        t=max(0,min(1,(vertex.co.y-97)/8));hg.add([vertex.index],t,'REPLACE');ng.add([vertex.index],1-t,'REPLACE')
    head['native_weights_exact']=True
    data=bpy.data.meshes.new('GuardianHumanNative');data.from_pydata(vertices,[],faces);mesh=bpy.data.objects.new('Body_human_bilge',data);bpy.context.collection.objects.link(mesh)
    for poly in data.polygons:poly.use_smooth=True
    for index,node in enumerate(body.nodes):
        group=mesh.vertex_groups.new(name=canon(node.name))
        for vi,w in enumerate(weights):
            if w.get(index,0)>0:group.add([vi],w[index],'REPLACE')
    bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
    mat=bpy.data.materials.new('GuardianHuman_BakedPBR');mat.use_nodes=True;data.materials.append(mat);shader=mat.node_tree.nodes.get('Principled BSDF')
    bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.context.scene.cycles.use_denoising=False
    bpy.context.scene.render.bake.use_selected_to_active=True
    bpy.ops.object.select_all(action='DESELECT');source.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
    results=[]
    for suffix,kind in [('color','DIFFUSE'),('normal','NORMAL'),('roughness','ROUGHNESS')]:
        image=bpy.data.images.new('GuardianHuman_'+suffix,width=2048,height=2048,alpha=False)
        if suffix!='color':image.colorspace_settings.name='Non-Color'
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.nodes.active=tex
        bpy.ops.object.bake(type=kind,pass_filter={'COLOR'} if kind=='DIFFUSE' else set(),use_clear=True,margin=12,cage_extrusion=18,max_ray_distance=40)
        image.filepath_raw=str(OUT/('guardian-human-'+suffix+'.png'));image.file_format='PNG';image.save();image.pack();results.append((suffix,tex))
    for suffix,tex in results:
        if suffix=='color':mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
        elif suffix=='roughness':mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Roughness'])
        else:
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65;mat.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    data.materials.append(material('Guardian_DarkGloves',(.035,.045,.055),.05,.78));data.materials.append(material('Guardian_LeatherBoots',(.045,.035,.025),0,.75))
    for polygon,part in zip(data.polygons,face_parts):polygon.material_index=1 if part=='Hand' else 2 if part=='Shoes' else 0
    bpy.data.objects.remove(source,do_unlink=True)
    mesh['source_asset']='native Pedro body; PBR baked from existing authored Bilge human appearance'
    mesh['source_kind']='new_native_exact_skin';mesh['native_weights_exact']=True
    return mesh

def make_rig(body,T):
    arm=bpy.data.armatures.new('NativeArmature');rig=bpy.data.objects.new('NativeRig',arm);bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for node in body.nodes:
        bone=arm.edit_bones.new(canon(node.name));bone.head=(0,0,0);bone.tail=(0,2,0);bone.matrix=node.bind_matrix.copy()
        if node.parent:bone.parent=arm.edit_bones[canon(node.parent.name)]
    bpy.ops.object.mode_set(mode='OBJECT')
    error=max(abs(arm.bones[canon(n.name)].matrix_local[i][j]-n.bind_matrix[i][j]) for n in body.nodes for i in range(4) for j in range(4))
    if error>.001:raise RuntimeError(f'Native bind matrix changed: {error}')
    rig['max_bind_matrix_error']=error
    rig.matrix_world=T;rig.show_in_front=True
    rig['native_bone_names']=json.dumps({canon(n.name):n.name for n in body.nodes})
    return rig

def skin(mesh,body,rig,surface):
    if mesh.get('native_weights_exact'):
        mod=mesh.modifiers.new('NativeSkin','ARMATURE');mod.object=rig;mesh.parent=rig;mesh.matrix_parent_inverse=Matrix.Identity(4);mesh.matrix_basis=Matrix.Identity(4)
        return {'method':'original native vertex weights','unweighted_vertices':0}
    verts,faces,source_weights,tree=surface;groups=[mesh.vertex_groups.new(name=canon(n.name)) for n in body.nodes];distances=[]
    for vertex in mesh.data.vertices:
        point,normal,face,distance=tree.find_nearest(vertex.co)
        if face is None:raise RuntimeError('No native skin surface')
        distances.append(distance)
        triangle=faces[face];coefs=bary(point,*(verts[i] for i in triangle));weights={}
        for source_vertex,amount in zip(triangle,coefs):
            for node,weight in source_weights[source_vertex].items():weights[node]=weights.get(node,0)+weight*amount
        top=sorted(weights.items(),key=lambda x:-x[1])[:4];total=sum(w for _,w in top)
        if total<=0:raise RuntimeError('Unweighted fitted vertex')
        for node,weight in top:
            if weight>1e-7:groups[node].add([vertex.index],weight/total,'REPLACE')
    if mesh.name=='Body_bilge':
        def smooth(x):
            x=max(0,min(1,x));return x*x*(3-2*x)
        hi=next(i for i,n in enumerate(body.nodes) if n.name=='Bip01 Head');ni=next(i for i,n in enumerate(body.nodes) if n.name=='Bip01 Neck');ji=next(i for i,n in enumerate(body.nodes) if n.name=='Bip01 Ponytail2')
        for vertex in mesh.data.vertices:
            co=rig.matrix_world@vertex.co
            influence=smooth((co.z-1.73)/.35)*smooth((.48-abs(co.x))/.16)
            if influence<=0:continue
            existing={g.group:g.weight for g in vertex.groups}
            t=smooth((co.z-1.78)/.26)
            jaw=smooth((-.16-co.y)/.08)*smooth((2.04-co.z)/.07)*smooth((co.z-1.82)/.08)*smooth((.15-abs(co.x))/.05)
            desired={hi:t*(1-jaw),ni:(1-t)*(1-jaw),ji:jaw}
            combined={i:existing.get(i,0)*(1-influence)+desired.get(i,0)*influence for i in set(existing)|set(desired)}
            top=sorted(combined.items(),key=lambda p:-p[1])[:4];total=sum(w for _,w in top)
            for group in groups:group.remove([vertex.index])
            for i,w in top:
                if w>1e-7:groups[i].add([vertex.index],w/total,'REPLACE')
    if mesh.name=='Body_bilge':
        # Diffuse transferred weights across welded topology. UV seams must use
        # identical influences; nearest-triangle transfer alone creates tearing.
        welded={};vid=[]
        for vertex in mesh.data.vertices:
            key=tuple(round(c,3) for c in vertex.co)
            vid.append(welded.setdefault(key,len(welded)))
        adj=[set() for _ in welded];values=[{} for _ in welded];counts=[0]*len(welded)
        for vertex,w in zip(mesh.data.vertices,vid):
            counts[w]+=1
            for g in vertex.groups:values[w][g.group]=values[w].get(g.group,0)+g.weight
        for i in range(len(values)):values[i]={g:w/counts[i] for g,w in values[i].items()}
        for edge in mesh.data.edges:
            a,b=(vid[i] for i in edge.vertices)
            if a!=b:adj[a].add(b);adj[b].add(a)
        for iteration in range(18):
            updated=[]
            for i,near in enumerate(adj):
                result={g:w*.45 for g,w in values[i].items()}
                for j in near:
                    for g,w in values[j].items():result[g]=result.get(g,0)+w*.55/max(1,len(near))
                updated.append(result if near else values[i])
            values=updated
        for vertex,weld in zip(mesh.data.vertices,vid):
            top=sorted(values[weld].items(),key=lambda p:-p[1])[:4];total=sum(w for _,w in top)
            for group in groups:group.remove([vertex.index])
            for i,w in top:
                if w>1e-7:groups[i].add([vertex.index],w/total,'REPLACE')
        mesh['skin_smoothing_iterations']=18
    if mesh.name=='Body_human_bilge':
        pelvis=groups[next(i for i,n in enumerate(body.nodes) if n.name=='Bip01 Pelvis')]
        for vertex in mesh.data.vertices:
            co=rig.matrix_world@vertex.co
            if .46<co.z<1.04 and abs(co.x)<.34 and co.y<-.055:
                for group in groups:group.remove([vertex.index])
                pelvis.add([vertex.index],1,'REPLACE')
    mod=mesh.modifiers.new('NativeSkin','ARMATURE');mod.object=rig;mesh.parent=rig;mesh.matrix_parent_inverse=Matrix.Identity(4);mesh.matrix_basis=Matrix.Identity(4)
    return {'maximum_native_distance_units':max(distances),'p95_native_distance_units':sorted(distances)[int(.95*(len(distances)-1))],'unweighted_vertices':0,'max_influences':4}

def load_body(form,T,height):
    source=ROOT/('art/characters/grey-wolf-production/working/grey-wolf-working.glb' if form=='wolf' else 'art/3d/source/pedro-native/inputs/human-bilge-before-native.glb')
    bpy.ops.import_scene.gltf(filepath=str(source))
    oldrigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    for o in oldrigs:o.data.pose_position='REST'
    bpy.context.view_layer.update()
    candidates=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('Body') or form=='wolf')]
    if len(candidates)!=1:raise RuntimeError(f'Expected one textured body: {[o.name for o in candidates]}')
    mesh=candidates[0];world=[mesh.matrix_world@v.co for v in mesh.data.vertices]
    low=Vector(tuple(min(v[i] for v in world) for i in range(3)));high=Vector(tuple(max(v[i] for v in world) for i in range(3)))
    center=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z));factor=height/(high.z-low.z)
    inverse=T.inverted();oldmatrix=mesh.matrix_world.copy();normals=[n.vector.copy() for n in mesh.data.corner_normals]
    normal_rotation=inverse.to_3x3()@oldmatrix.to_3x3()
    for vertex,co in zip(mesh.data.vertices,world):vertex.co=inverse@((co-center)*factor)
    mesh.parent=None;mesh.matrix_world=Matrix.Identity(4)
    mesh.data.normals_split_custom_set([(normal_rotation@n).normalized() for n in normals])
    for mod in list(mesh.modifiers):mesh.modifiers.remove(mod)
    mesh.vertex_groups.clear()
    mesh.name='Body_bilge' if form=='wolf' else 'Body_human_bilge'
    mesh['source_kind']='new_native_compatible_textured_body';mesh['source_asset']=str(source.relative_to(ROOT))
    for other in list(bpy.context.scene.objects):
        if other!=mesh:bpy.data.objects.remove(other,do_unlink=True)
    for action in list(bpy.data.actions):bpy.data.actions.remove(action)
    if form=='wolf':
        # Fit anatomical rest landmarks before skin transfer. The native wrist
        # sits higher than the generated art wrist; weights alone cannot fix it.
        anchors=[Vector((.42,0,1.86)),Vector((.65,0,1.57)),Vector((.91,0,1.18)),Vector((1.02,0,.96))]
        target_names=['UpperArm','Forearm','Hand','Finger11']
        body_for_fit=Reader().from_file(str(ROOT/'art/3d/source/pedro-native/main/pedro_wolf.ltb'))
        for vertex in mesh.data.vertices:
            co=T@vertex.co;sign=1 if co.x>=0 else -1
            if abs(co.x)<.27 or not .85<co.z<1.99:continue
            reference=Vector((abs(co.x),co.y,co.z));best=None
            for j in range(len(anchors)-1):
                a,b=anchors[j:j+2];u=max(0,min(1,(reference-a).dot(b-a)/(b-a).length_squared));distance=(reference-a.lerp(b,u)).length
                if best is None or distance<best[0]:best=(distance,j,u)
            _,j,u=best;side='R' if sign>0 else 'L'
            targets=[T@next(n.bind_matrix.to_translation() for n in body_for_fit.nodes if n.name=='Bip01 '+side+' '+name) for name in target_names]
            desired=targets[j].lerp(targets[j+1],u);origin=anchors[j].lerp(anchors[j+1],u);origin.x*=sign
            fade=max(0,min(1,(abs(co.x)-.27)/.20));fade=fade*fade*(3-2*fade)
            co+=(desired-origin)*fade;vertex.co=T.inverted()@co
        mesh.data.update()
    return mesh

def material(name,color,metal=0,rough=.5,glow=0):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=glow
    return mat

def decorations(rig,body,T,form):
    # Small articulated forearm cuffs and matching gold seal; do not cover elbows.
    gold=material('Guardian_BrushedBronze',(.34,.20,.065),.75,.34)
    blue=material('Guardian_ObsidianTurquoise',(.018,.13,.17),.5,.28,.12)
    inverse=T.inverted();objects=[]
    for side in ['L','R']:
        a=T@next(n.bind_matrix.to_translation() for n in body.nodes if n.name=='Bip01 '+side+' Forearm')
        b=T@next(n.bind_matrix.to_translation() for n in body.nodes if n.name=='Bip01 '+side+' Hand')
        axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u).normalized()
        radius=.072 if form=='wolf' else .052;points=[];faces=[]
        for ring,t in enumerate([.36,.48,.65]):
            center=a.lerp(b,t);r=radius*(1.1 if ring==1 else 1)
            for j in range(5):points.append(inverse@(center+r*(u*math.cos(j*math.tau/5)+v*math.sin(j*math.tau/5))))
        for ring in range(2):
            for j in range(5):faces.append((ring*5+j,ring*5+(j+1)%5,(ring+1)*5+(j+1)%5,(ring+1)*5+j))
        data=bpy.data.meshes.new('GuardianCuff');data.from_pydata(points,[],faces);obj=bpy.data.objects.new('GuardianCuff'+side,data);bpy.context.collection.objects.link(obj);data.materials.append(blue);data.materials.append(gold)
        for face in data.polygons:face.material_index=1 if face.index%5==0 else 0
        group=obj.vertex_groups.new(name=canon('Bip01 '+side+' Forearm'));group.add(list(range(len(points))),1,'REPLACE');mod=obj.modifiers.new('NativeSkin','ARMATURE');mod.object=rig;obj.parent=rig;objects.append(obj)
    # Low-profile commander seal on the belt, shared by both forms.
    pelvis=T@next(n.bind_matrix.to_translation() for n in body.nodes if n.name=='Bip01 Pelvis')
    center=pelvis+Vector((0,-.155 if form=='wolf' else -.12,.035))
    points=[inverse@center]
    for j in range(12):points.append(inverse@(center+Vector((math.cos(j*math.tau/12)*.05,0,math.sin(j*math.tau/12)*.05))))
    faces=[(0,j+1,(j+1)%12+1) for j in range(12)]
    data=bpy.data.meshes.new('GuardianSeal');data.from_pydata(points,[],faces);obj=bpy.data.objects.new('GuardianSeal',data);bpy.context.collection.objects.link(obj);data.materials.append(gold)
    group=obj.vertex_groups.new(name='Pelvis');group.add(list(range(len(points))),1,'REPLACE');mod=obj.modifiers.new('NativeSkin','ARMATURE');mod.object=rig;obj.parent=rig;objects.append(obj)
    return objects

def tattoo_surfaces(mesh,rig,body,T):
    # Project a small skin grid onto the real body and interpolate its exact weights.
    # Texture alpha supplies the outline; the surface follows the same skeleton.
    mesh.data.calc_loop_triangles()
    native_vertices=[v.co.copy() for v in mesh.data.vertices]
    native_faces=[tuple(t.vertices) for t in mesh.data.loop_triangles]
    native_weights=[{g.group:g.weight for g in v.groups} for v in mesh.data.vertices]
    world_vertices=[T@v for v in native_vertices]
    world_tree=BVHTree.FromPolygons(world_vertices,native_faces,all_triangles=True)
    native_tree=BVHTree.FromPolygons(native_vertices,native_faces,all_triangles=True)
    surface=(native_vertices,native_faces,native_weights,native_tree)
    atlas=bpy.data.images.load(str(ROOT/'art/3d/textures/tattoo-atlas.png'),check_existing=True)
    atlas.pack();inverse=T.inverted()
    rectangles={'back':(0,0,426,431),'left':(428,0,847,430),'right':(428,0,847,430)}
    regions={'back':(-.20,.20,1.25,1.77,4,5),'left':(.53,.76,1.19,1.43,2,3),'right':(-.76,-.53,1.19,1.43,2,3)}
    for slot,(xmin,xmax,zmin,zmax,columns,rows) in regions.items():
        points=[];uvs=[];valid=[];faces=[]
        for row in range(rows+1):
            for column in range(columns+1):
                u=column/columns;v=row/rows;x=xmin+(xmax-xmin)*u;z=zmin+(zmax-zmin)*v
                if slot!='back':
                    group=mesh.vertex_groups['Forearm'+('L' if slot=='left' else 'R')].index
                    chosen=[world_vertices[i] for i,w in enumerate(native_weights) if w.get(group,0)>.65]
                    if chosen:
                        center=sum(chosen,Vector())/len(chosen);sign=1 if center.x>0 else -1
                        axis=Vector((sign*.65,0,-.76));cross=Vector((.76,0,sign*.65))
                        point=center+axis*((v-.5)*.18)+cross*((u-.5)*.09);x,z=point.x,point.z
                hit,normal,face,distance=world_tree.ray_cast(Vector((x,2,z)),Vector((0,-1,0)),4)
                valid.append(hit is not None)
                points.append(inverse@(hit+normal*.0012) if hit is not None else Vector((0,0,0)))
                uvs.append((u,v))
        for row in range(rows):
            for column in range(columns):
                a=row*(columns+1)+column;b=a+1;c=a+columns+2;d=a+columns+1
                if all(valid[i] for i in (a,b,c,d)):faces.extend([(a,c,b),(a,d,c)])
        if not faces:continue
        used=sorted({i for f in faces for i in f});remap={old:new for new,old in enumerate(used)}
        data=bpy.data.meshes.new('TattooSkinGrid');data.from_pydata([points[i] for i in used],[],[tuple(remap[i] for i in f) for f in faces]);obj=bpy.data.objects.new('Tattoo_'+slot+'_surface',data);bpy.context.collection.objects.link(obj)
        rect=rectangles[slot];base=(rect[0]/1274,1-rect[3]/1234,(rect[2]-rect[0])/1274,(rect[3]-rect[1])/1234)
        uv=data.uv_layers.new(name='TattooAtlas')
        for loop in data.loops:
            u,v=uvs[used[loop.vertex_index]];uv.data[loop.index].uv=(base[0]+u*base[2],base[1]+v*base[3])
        mat=bpy.data.materials.new('Tattoo_'+slot);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas
        mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);mat.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.08;p.inputs['Roughness'].default_value=.85
        data.materials.append(mat);obj['atlas_uv_base']=list(base);skin(obj,body,rig,surface)

def author_clips(body,motion,rig,form):
    native={a.name:a for a in motion.animations};upper=next(w.node_weights for w in motion.weight_sets if w.name=='Upper')
    if form=='wolf':
        recipes={'WolfIdle':('LSt','UMSt',None),'WolfWalk':('LWF','UMWF',None),'WolfRunNative':('LRF','UMRF',None),'WolfRoar':('T_CRY',None,None),'WolfBodyAttack':('T_Bodyatk',None,.8),'WolfClawRight':('LSt','UMFi1',.65),'WolfClawLeft':('LSt','UMFi2',.65),'WolfJump':('LJA','UMJJ',.9),'WolfTransform':('Ui_idle',None,.6)}
    else:recipes={'HumanIdle':('UI_Default_Idle',None,None),'HumanWalk':('LWF','URi1WF',None),'HumanRun':('LRF','URi1RF',None),'HumanFire':('LSt','URi1Fi',None),'HumanReload':('LSt','URi1Re',None)}
    target_local=rest_locals(body);source_local=rest_locals(motion);rig.animation_data_create();reports=[]
    ref_globals=[]
    for i,n in enumerate(motion.nodes):
        ref=native['UMSt'] if form=='wolf' and upper[i]>0 else native['LSt'] if form=='wolf' else native['UI_Default_Idle']
        q=sample(ref,i,0)[1];parent=motion.nodes.index(n.parent) if n.parent else None;ref_globals.append(ref_globals[parent]@q if parent is not None else q)
    rootindex=next(i for i,n in enumerate(body.nodes) if n.name=='Bip01');ratio=body.nodes[rootindex].bind_matrix.to_translation().y/motion.nodes[rootindex].bind_matrix.to_translation().y
    for name,(lower_name,upper_name,override) in recipes.items():
        lower=native[lower_name];over=native[upper_name] if upper_name else None
        lower_duration=(lower.keyframes[-1].time-lower.keyframes[0].time)/1000
        upper_duration=(over.keyframes[-1].time-over.keyframes[0].time)/1000 if over else 0
        duration=math.ceil((override or max(lower_duration,upper_duration))*FPS-1e-6)/FPS;count=max(2,round(duration*FPS)+1)
        action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
        for frame in range(count):
            seconds=duration*frame/(count-1);raw_globals=[];pose_globals=[]
            for index,node in enumerate(body.nodes):
                clip=over if over and upper[index]>0 else lower
                original=(clip.keyframes[-1].time-clip.keyframes[0].time)/1000
                t=seconds/max(duration,1e-9)*original
                loc,rot=sample(clip,index,t)
                inactive = (name=='WolfClawRight' and node.name.startswith('Bip01 L ')) or (name=='WolfClawLeft' and node.name.startswith('Bip01 R '))
                if inactive:loc,rot=sample(native['UMSt'],index,0)
                parent_index=body.nodes.index(node.parent) if node.parent else None
                raw_global=raw_globals[parent_index]@rot if parent_index is not None else rot;raw_globals.append(raw_global)
                rotation_delta=source_local[index].to_quaternion().inverted()@rot
                if canon(node.name) in (['Head','Neck','Ponytail2'] if form=='wolf' else ['Head','Neck']):
                    neutral=native['UMSt' if form=='wolf' else 'UI_Default_Idle']
                    rotation_delta=sample(neutral,index,0)[1].inverted()@rot
                if canon(node.name)=='Head':
                    goal=Quaternion((0,1,0),math.pi)@node.bind_matrix.to_quaternion()@(ref_globals[index].inverted()@raw_global)
                    parent_pose=pose_globals[parent_index] if parent_index is not None else Quaternion()
                    rotation_delta=target_local[index].to_quaternion().inverted()@parent_pose.inverted()@goal
                local_pose=target_local[index].to_quaternion()@rotation_delta;pose_globals.append(pose_globals[parent_index]@local_pose if parent_index is not None else local_pose)
                desired=target_local[index].to_quaternion()@rotation_delta
                bone=rig.pose.bones[canon(node.name)];bone.rotation_mode='QUATERNION';bone.rotation_quaternion=rotation_delta
                # Preserve target segment lengths. Only the native locomotion root translates.
                offset=Vector((0,0,0))
                if index==rootindex:
                    delta=(loc-source_local[index].to_translation())*ratio
                    start=sample(clip,index,0)[0];end=sample(clip,index,original)[0]
                    for axis in [0,2]:delta[axis]-=(end[axis]-start[axis])*(t/max(original,1e-9))*ratio
                    offset=target_local[index].to_3x3().inverted()@delta
                bone.location=offset;bone.scale=(1,1,1)
                bone.keyframe_insert('location',frame=frame);bone.keyframe_insert('rotation_quaternion',frame=frame)
        # Correct export-space floor penetration without erasing jump/flight.
        body_mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Body'))
        hips=rig.pose.bones['Hips'];vertical=rig.matrix_world.inverted().to_3x3()@Vector((0,0,1))
        vertical=hips.bone.matrix_local.to_3x3().inverted()@vertical
        idle_offset=None
        for frame in range(count):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            deps=bpy.context.evaluated_depsgraph_get();ev=body_mesh.evaluated_get(deps);geo=ev.to_mesh()
            minimum=min((body_mesh.matrix_world@v.co).z for v in geo.vertices);ev.to_mesh_clear()
            if idle_offset is None:idle_offset=-minimum if name in ['WolfIdle','HumanIdle'] else 0
            lift=idle_offset if name in ['WolfIdle','HumanIdle'] else max(0,-minimum)
            if name=='WolfJump':lift=0
            hips.location+=vertical*lift;hips.keyframe_insert('location',frame=frame)
        for fc in action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
        action['native_lower']=lower_name;action['native_upper']=upper_name or '';action['duration_s']=duration
        reports.append({'name':name,'native_lower':lower_name,'native_upper':upper_name,'duration_s':duration,'frames':count})
    rig.animation_data.action=bpy.data.actions.get('WolfIdle' if form=='wolf' else 'HumanIdle');bpy.context.scene.frame_set(0)
    return reports

def build(form):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    base=ROOT/'art/3d/source/pedro-native'
    body=Reader().from_file(str(base/'main'/('pedro_wolf.ltb' if form=='wolf' else 'pedro.ltb')))
    motion=Reader().from_file(str(base/'new-motion'/('wt_new_wolf_ch.ltb' if form=='wolf' else 'wt_new_man_ch.ltb')))
    if [n.name for n in body.nodes]!=[n.name for n in motion.nodes]:raise RuntimeError('Native hierarchy mismatch')
    points=[v.location for p in body.pieces for v in p.lods[0].vertices]
    low=min(v.y for v in points);native_height=max(v.y for v in points)-low;height=2.4 if form=='wolf' else 1.85;scale=height/native_height
    T=Matrix((( -scale,0,0,0),(0,0,scale,0),(0,scale,0,-low*scale),(0,0,0,1)))
    mesh=load_body(form,T,height)
    if form=='man':mesh=bake_native_human(mesh,body)
    rig=make_rig(body,T);stats=skin(mesh,body,rig,native_surface(body))
    for extra in list(bpy.context.scene.objects):
        if extra.type=='MESH' and extra!=mesh and extra.get('native_weights_exact'):skin(extra,body,rig,None)
    decorations(rig,body,T,form)
    if form=='wolf':tattoo_surfaces(mesh,rig,body,T)
    clips=author_clips(body,motion,rig,form)
    # Native clips face opposite the art neutral pose; align the played forward axis.
    rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@rig.matrix_world
    rig['native_forward_alignment_degrees']=180
    mesh['walk_stride_m']=3.6*next(a['duration_s'] for a in clips if a['name'].endswith('Walk'))
    mesh['run_reference_speed_mps']=8.0;mesh['run_stride_m']=8*next(a['duration_s'] for a in clips if a['name'] in ['WolfRunNative','HumanRun'])
    bpy.context.scene.render.fps=FPS;bpy.context.scene['native_motion_status']='PREVIEW_REQUIRES_VISUAL_AND_RUNTIME_REVIEW';bpy.ops.file.pack_all()
    out=OUT/('guardian-wolf' if form=='wolf' else 'guardian-human')
    bpy.ops.wm.save_as_mainfile(filepath=str(out.with_suffix('.blend')))
    bpy.ops.export_scene.gltf(filepath=str(out.with_suffix('.glb')),export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_frame_range=False,export_extras=True,export_skins=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];triangles=0
    for o in meshes:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
    return {'form':form,'source_body':mesh['source_asset'],'native_bones':len(body.nodes),'triangles':triangles,'height_m':height,'transfer':stats,'clips':clips,'visual_approval':False}

if __name__ == '__main__':
    forms=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['wolf','man']
    reports=[build(form) for form in forms]
    if (OUT/'build-report.json').exists() and len(forms)<2:
        reports += [r for r in json.loads((OUT/'build-report.json').read_text()) if r['form'] not in forms]
    (OUT/'build-report.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('NATIVE_PAIR_BUILD',json.dumps(reports))
