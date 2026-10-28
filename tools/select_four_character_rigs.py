"""Record four distinct native skeletons and freeze all selected source motion.
Reads source files only; does not rewrite models, motion or gameplay.
"""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];reports={x['file']:x for x in json.loads((R/'docs/native-pair-review/archive-rig-inspection.json').read_text())};base=R/'art/3d/source/wolfteam-archive/selected'
choices=[('bilge','Bilge Kağan','wt_wolf_ice_r.ltb',base/'wt_wolf_ice_ch.ltb','Buz; lacivert-altın komutan; kontrollü buz önkolu'),('kultigin','Kül Tigin','r1_wolf.ltb',base/'r1_wolf.ltb','Kan; kömür siyahı-kızıl savaşçı; parçalı hafif zırh'),('alparslan','Alp Arslan','wt_wolf_power_r.ltb',R/'art/3d/source/pedro-native/new-motion/wt_new_wolf_ch.ltb','Köz; geniş göğüs/omuz; bronz deri kemer ve omuzluk'),('konuralp','Konuralp','wt_wolf_wraith.ltb',base/'wt_wolf_wraith.ltb','Gölge; ince çevik silüet; mor işaretler ve doğal kuyruk')]
records=[];frozen={}
for key,name,filename,motion,design in choices:
 row=reports[filename];source=base/filename;hierarchy=[(n['name'],n['parent']) for n in row['nodes']]
 for f in [source,motion]:frozen[str(f.relative_to(R))]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 records.append({'id':key,'character':name,'form':'wolf','source':str(source.relative_to(R)),'motion_source':str(motion.relative_to(R)),'nodes':row['node_count'],'hierarchy_sha256':hashlib.sha256(json.dumps(hierarchy).encode()).hexdigest(),'source_triangles':sum(p['lods'][0]['triangles'] for p in row['pieces']),'native_pieces':[p['name'] for p in row['pieces']],'design_direction':design,'animations_locked':True})
assert len({r['hierarchy_sha256'] for r in records})==4
out=R/'docs/four-character-rigs';out.mkdir(exist_ok=True);(out/'selection.json').write_text(json.dumps({'scope':'Four distinct wolf rigs; human partners retain matching identity, human skeleton selection not asserted here','characters':records,'frozen_source_files':frozen,'runtime_changed':False,'animation_edits_permitted':False},ensure_ascii=False,indent=2))
print([(r['character'],r['nodes'],r['source_triangles']) for r in records])
