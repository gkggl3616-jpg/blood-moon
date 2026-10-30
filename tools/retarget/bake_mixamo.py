"""One-off: retarget the Mixamo FBX clips onto the wolf skeleton and store compact JSON (tools/retarget/baked)."""
import json, sys
sys.path.insert(0, '../wolfgen'); sys.path.insert(0, '.')
from build_icewolf import build_skeleton
from retarget import retarget
A = sys.argv[1]
SRC = {'idle': ('Orc_Idle.fbx', 0, 6.0), 'roar': ('Zombie_Scream.fbx', .4, 2.4), 'clawR': ('Standing_Melee_Attack_Horizontal.fbx', 0, None),
       'clawL': ('Standing_Melee_Attack_Horizontal_1.fbx', 0, None), 'jump': ('Mutant_Jumping.fbx', 0, None), 'runjump': ('Standing_Melee_Run_Jump_Attack_1.fbx', 0, None)}
import glob
S = build_skeleton()
for k, (fn, t0, t1) in SRC.items():
    path = glob.glob(f'{A}/*{fn}')[0]; fr, dur = retarget(path, S, t0=t0, t1=t1)
    json.dump({'duration': dur, 'frames': [{'q': {b: [round(float(x), 5) for x in q] for b, q in p.items()}, 'dy': round(float(dy), 4)} for p, dy in fr]}, open(f'baked/{k}.json', 'w'), separators=(',', ':'))
    print(k, dur, len(fr))
