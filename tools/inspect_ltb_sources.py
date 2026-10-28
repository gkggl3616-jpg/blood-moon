"""Read native PC LTB using a pinned external LithTech reader, without conversion.
blender --factory-startup -b --python tools/inspect_ltb_sources.py -- ADDON_DIR INPUT_DIR OUTPUT.json
"""
import sys,types,importlib,json,hashlib,traceback
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
package=types.ModuleType('native_lithtech');package.__path__=[str(Path(args[0]).resolve())];sys.modules[package.__name__]=package
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
reports=[]
for path in sorted(Path(args[1]).glob('*.ltb')):
 report={'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 try:
  model=Reader().from_file(str(path))
  report.update(parsed=True,version=model.version,node_count=len(model.nodes),nodes=[{'name':n.name,'index':n.index,'parent':n.parent.name if n.parent else None} for n in model.nodes],children=[c.name for c in model.child_models],command_string=model.command_string,sockets=[{'name':s.name,'node_index':s.node_index} for s in model.sockets],pieces=[{'name':p.name,'material_index':p.material_index,'lods':[{'vertices':len(l.vertices),'triangles':len(l.faces),'texture_slots':l.textures,'vertices_with_weights':sum(bool(v.weights) for v in l.vertices)} for l in p.lods]} for p in model.pieces],animations=[{'name':a.name,'frames':len(a.keyframes),'duration_ms':a.keyframes[-1].time-a.keyframes[0].time if a.keyframes else 0,'compression':a.compression_type,'transform_nodes':len(a.node_keyframe_transforms)} for a in model.animations])
 except Exception as e:
  report.update(parsed=False,error=repr(e),traceback=traceback.format_exc())
 reports.append(report)
 print('LTB_REPORT',json.dumps({k:v for k,v in report.items() if k not in ['nodes','pieces','animations','traceback']},ensure_ascii=False))
Path(args[2]).parent.mkdir(parents=True,exist_ok=True)
Path(args[2]).write_text(json.dumps(reports,indent=2,ensure_ascii=False)+'\n')
