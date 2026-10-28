"""Inspect and render the actual downloaded mesh, never substitute a concept.
Usage: blender -b -t 2 --python tools/inspect_generated_character.py -- INPUT.glb OUTPUT_DIR
"""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]).resolve();out=Path(args[1]).resolve();out.mkdir(parents=True,exist_ok=True)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(source));s=bpy.context.scene
# Imported bone widgets are helpers; generated source geometry is identified by actual mesh users.
meshes=[o for o in s.objects if o.type=='MESH' and not o.name.startswith(('WGT-','IcosphereHelper')) and not any(c.name=='glTF_not_exported' for c in o.users_collection)]
report={'source':str(source),'meshes':[],'total_triangles':0,'has_armature':any(o.type=='ARMATURE' for o in s.objects),'visual_review':'PENDING','rigging_and_animation':'NOT established by this static inspection'}
points=[]
for ob in meshes:
 me=ob.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me);remaining=set(bm.verts);components=[]
 while remaining:
  stack=[remaining.pop()];n=0
  while stack:
   v=stack.pop();n+=1
   for e in v.link_edges:
    other=e.other_vert(v)
    if other in remaining:remaining.remove(other);stack.append(other)
  components.append(n)
 mats=[]
 for mat in me.materials:
  images=[]
  if mat and mat.use_nodes:images=[{'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file)} for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
  mats.append({'name':mat.name if mat else None,'images':images})
 entry={'name':ob.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'quads':sum(len(p.vertices)==4 for p in me.polygons),'has_uv':bool(me.uv_layers),'loose_vertices':sum(not v.link_faces for v in bm.verts),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_nonboundary_edges':sum(not e.is_manifold and not e.is_boundary for e in bm.edges),'component_sizes':sorted(components,reverse=True),'materials':mats};bm.free();report['meshes'].append(entry);report['total_triangles']+=entry['triangles'];points.extend(ob.matrix_world@v.co for v in me.vertices)
 if any(o.type=='ARMATURE' for o in s.objects):ob.hide_render=False
if not points:raise RuntimeError('No source geometry found')
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=(lo+hi)/2;size=hi-lo;report['bounds']={'min':list(lo),'max':list(hi),'size':list(size)};report['budget_15000_pass']=report['total_triangles']<=15000
(out/'mesh-inspection.json').write_text(json.dumps(report,indent=2));print('MESH_CHECK',json.dumps({'triangles':report['total_triangles'],'meshes':len(meshes),'dimensions':list(size),'budget_pass':report['budget_15000_pass']}))
# Render only the real source. No automatic sculpt/topology/colour "repair" here.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.cycles.device='CPU';s.world.color=(.045,.045,.045);s.view_settings.view_transform='AgX';s.render.resolution_x=960;s.render.resolution_y=1080;s.render.resolution_percentage=100
height=max(.1,size.z);bpy.ops.mesh.primitive_plane_add(size=height*200,location=(center.x,center.y,lo.z-.004*height));floor=bpy.context.object;mat=bpy.data.materials.new('InspectionFloor');mat.diffuse_color=(.09,.105,.12,1);floor.data.materials.append(mat)
for vec,energy,width in [((1.4,-1.8,2),550,1.5),((-1.5,-.8,1.3),250,1.5),((.2,1.5,1.8),400,1)]:
 co=center+Vector(vec)*height;bpy.ops.object.light_add(type='AREA',location=co);o=bpy.context.object;o.data.energy=energy*height*height/4;o.data.size=width*height;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
for name,offset in {'front':(0,-3,.12),'back':(0,3,.12),'side':(3,0,.12),'three-quarter':(2,-3,.18)}.items():
 cam.location=center+Vector(offset)*height;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 # Fit projected vertices, not just height: A-pose hands must stay in frame.
 local=[cam.rotation_euler.to_matrix().transposed()@(p-center) for p in points];width=max(p.x for p in local)-min(p.x for p in local);view_height=max(p.y for p in local)-min(p.y for p in local);aspect=s.render.resolution_x/s.render.resolution_y;cam.data.ortho_scale=max(view_height,width/aspect)*1.12
 s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('ACTUAL_MESH_PREVIEWS_READY')
