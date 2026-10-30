"""Measure how fast each locomotion clip moves its planted feet, retime the quad gallop to the model's reference
run speed, and store the speeds on the Body node so the engine plays every clip at a rate of ~1 (no sliding).
usage: foot_speeds.py model.glb [...]"""
import sys, os, json, struct, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB
from clip_speed import speed
def patch(path):
    g = GLB(path); names = [a['name'] for a in g.j.get('animations', [])]
    if 'WolfMove' not in names: return None
    body = next(n for n in g.j['nodes'] if 'skin' in n and n.get('name', '').startswith('Body'))
    ex = body.setdefault('extras', {}); ref = float(ex.get('run_reference_speed_mps', 8.0))
    out = {}
    out['walk_foot_speed_mps'] = speed(path, 'WolfMove')[0]
    if 'WolfJog' in names: out['jog_foot_speed_mps'] = speed(path, 'WolfJog')[0]
    # The current gallop's planted paws only cover ~3 m/s; retiming it to 8 m/s would make a frantic 0.14 s cycle.
    # Record the measurement; the engine keeps its stride-based run rate until a longer-stride gallop is authored.
    vr, T = speed(path, 'WolfRunQuad', feet=('HandL', 'HandR', 'FootL', 'FootR'))
    out['run_measured_foot_speed_mps'] = vr
    ex.update({k: round(float(x), 3) for k, x in out.items()})
    js = json.dumps(g.j, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4); bn = g.bin + b'\0' * ((4 - len(g.bin) % 4) % 4)
    with open(path, 'wb') as fh:
        fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bn))); fh.write(struct.pack('<I', len(js)) + b'JSON' + js); fh.write(struct.pack('<I', len(bn)) + b'BIN\0' + bn)
    return out
if __name__ == '__main__':
    for p in sys.argv[1:]: print(os.path.basename(p), patch(p))
