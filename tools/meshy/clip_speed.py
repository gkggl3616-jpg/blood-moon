"""Estimate the ground speed an in-place locomotion clip implies (feet sliding backward during stance)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB, sample_trs, world_with
def speed(path, clip, feet=('FootL', 'FootR', 'ToeL', 'ToeR')):
    g = GLB(path); a = next(x for x in g.j['animations'] if x['name'] == clip); nm = {n.get('name'): i for i, n in enumerate(g.j['nodes'])}
    T = max(g.acc(s['input']).max() for s in a['samplers']); ts = np.linspace(0, T, int(T * 60) + 1); pos = {f: [] for f in feet if f in nm}
    for t in ts:
        W = world_with(g, sample_trs(g, a, t))
        for f in pos: pos[f].append(W[nm[f]][:3, 3])
    v = []
    for f, P in pos.items():
        P = np.array(P); vel = np.gradient(P, ts, axis=0); low = P[:, 1] < P[:, 1].min() + .04
        v += list(np.abs(vel[low, 2]))
    return float(np.median(v)), float(T)
if __name__ == '__main__':
    for c in sys.argv[2:]: print(c, 'speed %.2f m/s, %.2fs' % speed(sys.argv[1], c))
