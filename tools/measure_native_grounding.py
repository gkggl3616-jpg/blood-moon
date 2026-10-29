"""Measure shipped mesh grounding/root motion without modifying native key tracks."""
import bpy,json,struct,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=R/'art/characters/bilge-original/working/wolf.glb';raw=P.read_bytes();jsize=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jsize]);end=20+jsize;binary=raw[end+8:end+8+struct.unpack_from('<I',raw,end)[0]]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=next(o for o in bpy.context.scene.objects if o.name=='Body_bilge');[rig.animation_data.nla_tracks.remove(t) for t in list(rig.animation_data.nla_tracks)];scene=bpy.context.scene;scene.render.fps=24;dep=bpy.context.evaluated_depsgraph_get();report={};starts={}
for name in ['LSt','UMSt','LWF','LRF','T_CRY','T_Specialatk','LJJ','LJT','LJL']:
 a=next(a for a in bpy.data.actions if a.name.startswith(name+'_'));rig.animation_data.action=a;duration=a.frame_range[1]/24;records=[]
 for i in range(61):
  t=duration*i/60;f=t*24;scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();root=rig.matrix_world@rig.pose.bones['Bip01'].head
  if i==0:starts[name]=[root.x,root.z,-root.y]
  minimum=min((body.matrix_world@v.co).z for v in body.evaluated_get(dep).data.vertices)
  records.append([round(t,6),round(max(0,.008-minimum),6)])
 report[name]={'duration':duration,'max_floor_correction_m':max(r[1] for r in records),'clearance':records}
extras=g['scenes'][g.get('scene',0)].setdefault('extras',{});extras['nativeClipRootStarts']=starts;extras['nativeRollClearance']=report['T_Specialatk']['clearance'];extras['nativeRootPlacementPolicy']='Physics drives horizontal roll travel; unchanged native vertical arc retained with measured floor clearance. Native animation accessors unchanged.'
text=json.dumps(g,separators=(',',':')).encode();text+=b' '*((-len(text))%4);P.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(text)+len(binary))+struct.pack('<II',len(text),0x4E4F534A)+text+struct.pack('<II',len(binary),0x004E4942)+binary)
(R/'docs/bilge-original-complete/grounding.json').write_text(json.dumps(report,indent=2));print('GROUNDING',[(n,r['max_floor_correction_m']) for n,r in report.items()])
