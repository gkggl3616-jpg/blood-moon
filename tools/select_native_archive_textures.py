"""Extract only an explicit allowlist; retain native archive-relative paths."""
import json,hashlib
from pathlib import Path,PurePosixPath
import libarchive
R=Path(__file__).resolve().parents[1];SRC=R/'art/3d/source/wolfteam-archive/updated-download';OUT=R/'art/3d/source/wolfteam-archive/textures'
paths={
'wt_chars/newchars/pedro_wolf/pedro_wolf_upper.dtx':'wolf upper UV atlas',
'wt_chars/newchars/pedro_wolf/pedro_wolf_lower.dtx':'wolf lower UV atlas',
'wt_chars/newchars/pedro_wolf/pedro_wolf_hair.dtx':'wolf fur UV atlas',
'wt_chars/newchars/pedro_red/pedro_r_upperbody.dtx':'human torso/head UV atlas candidate',
'wt_chars/newchars/pedro_red/pedro_r_lowerbody.dtx':'human lower UV atlas',
'wt_chars/newchars/pedro_red/pedro_gloves01.dtx':'human base glove candidate',
'wt_chars/newchars/pedro_red/pedro_boots01.dtx':'human base boot candidate',
'wt_chars/skins/wt_wolf_r.dtx':'standard 42-bone wolf body comparison',
'wt_chars/skins/helmet.dtx':'standard wolf object material candidate',
'wt_chars/skins/wt_wolf_powershoulder_r.dtx':'Power 42-bone shoulder comparison',
'wt_chars/skins/wt_icewolf_r.dtx':'Ice 40-bone body comparison',
'wt_chars/skins/wt_wolf_guardian_r.dtx':'Guardian 40-bone body comparison',
'wt_chars/skins/wt_wolf_smart_r.dtx':'Smart 40-bone body comparison',
'wt_fx/glow/purplefire_ptcle_1.dtx':'purple hand flame sprite candidate',
'wt_fx/swingtrail/swingtrail_purplefire.dtx':'short purple claw trail candidate',
'wt_fx/swingtrail/swingtrail_special_gm_scratch.dtx':'scratch trail comparison',
'wt_fx/wolf_arm_glow/wolf_arm_glow.dtx':'wolf forearm glow candidate'}
report=[]
with libarchive.file_reader(str(SRC)) as arc:
 for e in arc:
  if e.pathname not in paths:continue
  rel=PurePosixPath(e.pathname);assert not rel.is_absolute() and '..' not in rel.parts and not e.isdir and 0<e.size<8_000_000
  target=OUT.joinpath(*rel.parts);target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('wb') as f:
   for block in e.get_blocks():f.write(block)
  report.append({'path':e.pathname,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'purpose':paths[e.pathname]})
assert {e['path'] for e in report}==set(paths),'Missing selected files'
(R/'docs/native-pair-review/texture-selection.json').write_text(json.dumps(report,indent=2));print('extracted',len(report),'bytes',sum(e['bytes'] for e in report))
