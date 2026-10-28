"""Render native source poses without transferring skin or inventing clip labels."""
import bpy,sys,types,importlib,math,json,bisect
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
O=R/'docs/native-pair-review/motion-candidates';O.mkdir(exist_ok=True);records=[]
for filename,clipname in [('wt_wolf_wraith','LRF2'),('wt_wolf_wraith','LRF'),('r1_wolf','LRF'),('wt_wolf_smart_ch','LRF'),('wt_wolf_ice_ch','LRF'),('wt_wolf_wraith','T_Specialatk'),('wt_wolf_wraith','T_Bodyatk')]:
 bpy.ops.wm.read_factory_settings(use_empty=True);m=Reader().from_file(str(R/'art/3d/source/wolfteam-archive/selected'/(filename+'.ltb')));clip=next((a for a in m.animations if a.name==clipname),None)
 if not clip:continue
 arm=bpy.data.armatures.new('Native');rig=bpy.data.objects.new('Native',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n in m.nodes:
  b=arm.edit_bones.new(n.name);b.head=(0,0,0);b.tail=(0,2,0);b.matrix=n.bind_matrix
  if n.parent:b.parent=arm.edit_bones[n.parent.name]
 bpy.ops.object.mode_set(mode='OBJECT')
 verts=[];faces=[];weights=[]
 for p in m.pieces:
  if p.name.startswith('Tattoo'):continue
  l=p.lods[0];offset=len(verts);verts.extend(v.location.copy() for v in l.vertices);weights.extend([{w.node_index:w.bias for w in v.weights} for v in l.vertices]);faces.extend([tuple(offset+c.vertex_index for c in f.vertices) for f in l.faces])
 low=min(v.y for v in verts);scale=2.4/(max(v.y for v in verts)-low);T=Matrix(((-scale,0,0,0),(0,0,scale,0),(0,scale,0,-low*scale),(0,0,0,1)));rig.matrix_world=Matrix.Rotation(math.pi,4,'Z')@T
 data=bpy.data.meshes.new('NativeBody');data.from_pydata(verts,[],faces);obj=bpy.data.objects.new('NativeBody',data);bpy.context.collection.objects.link(obj);obj.parent=rig
 for i,n in enumerate(m.nodes):
  g=obj.vertex_groups.new(name=n.name)
  for vi,w in enumerate(weights):
   if w.get(i,0)>0:g.add([vi],w[i],'REPLACE')
 mod=obj.modifiers.new('OriginalSkin','ARMATURE');mod.object=rig
 for p in data.polygons:p.use_smooth=True
 mat=bpy.data.materials.new('UntexturedDiagnostic');mat.diffuse_color=(.3,.36,.41,1);data.materials.append(mat)
 overname='UM'+clipname[1:] if clipname.startswith('L') else None;over=next((a for a in m.animations if a.name==overname),None);upper=next((w.node_weights for w in m.weight_sets if w.name=='Upper'),[0]*len(m.nodes))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=False;s.render.resolution_x=480;s.render.resolution_y=480;s.world=bpy.data.worlds.new('World');s.world.color=(.13,.13,.13)
 center=Vector((0,0,1.1))
 for loc,energy in [((3,-4,5),900),((-3,0,3),700)]:
  bpy.ops.object.light_add(type='AREA',location=loc);b=bpy.context.object;b.data.energy=energy;b.data.size=4;b.rotation_euler=(center-b.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(3,-5,2.6));camera=bpy.context.object;s.camera=camera;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.5
 for phase in [.15,.4,.65,.85]:
  for i,n in enumerate(m.nodes):
   a=over if over and upper[i]>0 else clip;times=[key.time for key in a.keyframes];t=times[0]+phase*(times[-1]-times[0]);j=max(0,bisect.bisect_right(times,t)-1);k=min(len(times)-1,j+1);u=(t-times[j])/max(1,times[k]-times[j]);x=a.node_keyframe_transforms[i][j];y=a.node_keyframe_transforms[i][k];loc=x.location.lerp(y.location,u);rot=x.rotation.slerp(y.rotation,u);rest=n.parent.bind_matrix.inverted()@n.bind_matrix if n.parent else n.bind_matrix;basis=rest.inverted()@Matrix.LocRotScale(loc,rot,Vector((1,1,1)));rig.pose.bones[n.name].matrix_basis=basis
  bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());geo=evaluated.to_mesh();coords=[obj.matrix_world@v.co for v in geo.vertices];lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));center=(lo+hi)/2;evaluated.to_mesh_clear();camera.location=center+Vector((3,-5,1.5));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=max(3.0,(hi-lo).length*1.15);s.render.filepath=str(O/f'{filename}-{clipname}-{phase}.png');bpy.ops.render.render(write_still=True);records.append({'model':filename,'lower':clipname,'upper':overname if over else None,'phase':phase,'image':Path(s.render.filepath).name})
(O/'frames.json').write_text(json.dumps(records,indent=2))
