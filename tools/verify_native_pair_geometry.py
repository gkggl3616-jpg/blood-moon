"""Sample exported native-motion GLBs and report actual skin and timing bounds."""
import bpy,sys,json,math,statistics
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];reports=[]
for form in ['wolf','human']:
 bpy.ops.wm.read_factory_settings(use_empty=True);source=ROOT/'art/3d/native-pair'/('guardian-'+form+'.glb');bpy.ops.import_scene.gltf(filepath=str(source))
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
 for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
 mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Body'))
 rig.data.pose_position='REST';bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();base=mesh.evaluated_get(deps).to_mesh();vertices=[v.co.copy() for v in base.vertices];edges=[tuple(e.vertices) for e in base.edges];lengths=[(vertices[a]-vertices[b]).length for a,b in edges];mesh.evaluated_get(deps).to_mesh_clear();rig.data.pose_position='POSE'
 report={'form':form,'skin_bones':len(rig.data.bones),'clips':[],'body_vertices':len(vertices),'unweighted_body_vertices':sum(not v.groups for v in mesh.data.vertices),'finite':True}
 for action in bpy.data.actions:
  rig.animation_data.action=action;entry={'name':action.name,'duration_s':(action.frame_range[1]-action.frame_range[0])/bpy.context.scene.render.fps,'samples':[]}
  for phase in [0,.125,.25,.375,.5,.625,.75,.875,1]:
   frame=action.frame_range[0]+phase*(action.frame_range[1]-action.frame_range[0]);bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();evaluated=mesh.evaluated_get(deps);geo=evaluated.to_mesh();coords=[mesh.matrix_world@v.co for v in geo.vertices]
   ratios=sorted((geo.vertices[a].co-geo.vertices[b].co).length/length for (a,b),length in zip(edges,lengths) if length>.45)
   finite=all(all(math.isfinite(c) for c in v) for v in coords)
   entry['samples'].append({'phase':phase,'min_z':min(v.z for v in coords),'max_z':max(v.z for v in coords),'edge_stretch_p99':ratios[int(.99*(len(ratios)-1))],'edge_stretch_max':max(ratios),'finite':finite,'head':list(rig.matrix_world@rig.pose.bones['Head'].head),'left_foot':list(rig.matrix_world@rig.pose.bones['FootL'].head),'right_foot':list(rig.matrix_world@rig.pose.bones['FootR'].head)})
   report['finite'] &= finite;evaluated.to_mesh_clear()
  report['clips'].append(entry)
 reports.append(report)
Path(ROOT/'docs/native-pair-review/geometry-check.json').write_text(json.dumps(reports,indent=2))
for r in reports:print('GEOMETRY_CHECK',r['form'],r['skin_bones'],r['unweighted_body_vertices'],r['finite'],[(c['name'],round(max(s['edge_stretch_p99'] for s in c['samples']),2),round(min(s['min_z'] for s in c['samples']),2)) for c in r['clips']])
