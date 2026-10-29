"""Post-APK study: identify the exact horned gait body and its native contract.
Create untextured proportion references only; never call these a new game model.
"""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));import export_bilge_native_basis as e
D=R/'docs/horned-pair';O=R/'art/characters/horned-pair';D.mkdir(exist_ok=True);O.mkdir(exist_ok=True)
pairs=[('wolf','art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_king_behamah.ltb','art/3d/source/wolfteam-archive/full-selected/wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb',2.6),('human','art/3d/source/pedro-native/main/pedro.ltb','art/3d/source/pedro-native/new-motion/wt_new_man_ch.ltb',1.85)];report=[]
for form,bodypath,motionpath,height in pairs:
 body=e.Reader().from_file(str(R/bodypath));motion=e.Reader().from_file(str(R/motionpath));assert [n.name for n in body.nodes]==[n.name for n in motion.nodes];error=max(abs(a.bind_matrix[i][j]-b.bind_matrix[i][j]) for a,b in zip(body.nodes,motion.nodes) for i in range(4) for j in range(4));jaw=next((i for i,n in enumerate(body.nodes) if n.name=='Bip01 Ponytail2'),None);jaw_vertices=sum(any(w.node_index==jaw and w.bias>.5 for w in v.weights) for p in body.pieces for v in p.lods[0].vertices) if jaw is not None else 0
 roles=['T_Dash','T_cry','T_CRY_old','T_Specialatk','T_Dash_JJ','T_Dash_JT','T_Dash_JL'] if form=='wolf' else ['UI_Default_Idle','LWF','LRF'];catalog={a.name:{'duration_ms':a.keyframes[-1].time,'keys':len(a.keyframes),'events':[{'ms':k.time,'text':k.string} for k in a.keyframes if k.string]} for a in motion.animations};frozen_clips={name:catalog[name] for name in roles if name in catalog}
 bpy.ops.wm.read_factory_settings(use_empty=True);points=[v.location for p in body.pieces for v in p.lods[0].vertices];lo=min(p.y for p in points);scale=height/(max(p.y for p in points)-lo);T=Matrix(((-scale,0,0,0),(0,0,scale,0),(0,scale,0,-lo*scale),(0,0,0,1)));mat=bpy.data.materials.new('ReferenceClayOnly');mat.diffuse_color=(.30,.34,.38,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.30,.34,.38,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.83
 for piece in body.pieces:
  if 'tattoo' in piece.name.lower():continue
  lod=piece.lods[0];mesh=bpy.data.meshes.new(piece.name);mesh.from_pydata([T@v.location for v in lod.vertices],[],[tuple(c.vertex_index for c in f.vertices) for f in lod.faces]);obj=bpy.data.objects.new(piece.name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(mat)
  for p in mesh.polygons:p.use_smooth=True
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=800;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('ReferenceWorld');s.world.color=(.20,.20,.20);s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
 for location,power in [((3,-4,5),800),((-3,-2,4),600),((0,3,4),700)]:
  bpy.ops.object.light_add(type='AREA',location=location);bpy.context.object.data.energy=power;bpy.context.object.data.size=4
 bpy.ops.object.camera_add(location=(0,-6,height*.55));cam=bpy.context.object;s.camera=cam;target=Vector((0,0,height*.52));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(height*1.3,(max(p.x for p in points)-min(p.x for p in points))*scale/.8*1.13);s.render.filepath=str(O/(form+'-native-proportions.png'));bpy.ops.render.render(write_still=True)
 selected=frozen_clips;report.append({'form':form,'source_body':bodypath,'source_motion':motionpath,'source_body_sha256':hashlib.sha256((R/bodypath).read_bytes()).hexdigest(),'source_motion_sha256':hashlib.sha256((R/motionpath).read_bytes()).hexdigest(),'bones':len(body.nodes),'native_clips':len(motion.animations),'max_source_bind_error':error,'source_jaw_weighted_vertices':jaw_vertices,'triangles':sum(len(p.lods[0].faces) for p in body.pieces),'clips':selected,'reference_only':True,'runtime_added':False});print('HORNED_SOURCE',form,error,jaw_vertices,flush=True)
(D/'source-contract.json').write_text(json.dumps(report,indent=2));print('HORNED_STUDY_STARTED')
