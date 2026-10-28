"""Fingerprint existing native roar clips; no resampling or writes to animation."""
import types,importlib,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];pkg=types.ModuleType('native_lithtech');pkg.__path__=['/workspace/research/lithtech-source/io_scene_lithtech-495372d59d00e019a7143c961d94f05df2cc5c72/src/io_scene_lithtech'];import sys;sys.modules[pkg.__name__]=pkg
Reader=importlib.import_module('native_lithtech.reader_ltb_pc').PCLTBModelReader
selection=json.loads((R/'docs/four-character-rigs/selection.json').read_text());rows=[]
for item in selection['characters']:
 model=Reader().from_file(str(R/item['motion_source']));clip=next(a for a in model.animations if a.name=='T_CRY');h=hashlib.sha256()
 for n in model.nodes:h.update(n.name.encode()+b'\0')
 for k in clip.keyframes:h.update(struct.pack('<i',k.time));h.update(k.string.encode('utf-8')+b'\0')
 for transforms in clip.node_keyframe_transforms:
  for t in transforms:h.update(struct.pack('<7f',*t.location,*t.rotation))
 rows.append({'model_type':{'bilge':'ice40','kultigin':'r1_54','alparslan':'power42','konuralp':'wraith58'}[item['id']],'initial_character':item['id'],'source':item['motion_source'],'source_clip':'T_CRY','keyframes':len(clip.keyframes),'first_key_ms':clip.keyframes[0].time,'last_key_ms':clip.keyframes[-1].time,'duration_ms':clip.keyframes[-1].time-clip.keyframes[0].time,'native_transform_sha256':h.hexdigest(),'native_key_events':[{'time_ms':k.time,'raw_asset_event':k.string} for k in clip.keyframes if k.string],'reuse_rule':'Characters using this same model type reuse this native roar. Different model types do not share a forced generic roar.','animation_edit_allowed':False,'fx_reference':'Previously supplied full roar videos; hand flame + tattoo pulse + decay, aligned to this unmodified clip; visual verification pending','character_DTX_runtime_use':False})
for name,x in selection['frozen_source_files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==x['sha256']
(R/'docs/four-character-rigs/roar-model-profiles.json').write_text(json.dumps({'profiles':rows,'source_files_unchanged':True,'runtime_wired':False,'timing_or_animation_edits':False},ensure_ascii=False,indent=2));print([(r['model_type'],r['duration_ms'],r['keyframes']) for r in rows])
