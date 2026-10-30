"""Retarget Mixamo FBX clips onto the engine wolf skeleton by world-space rotation deltas."""
import math, sys
import numpy as np
sys.path.insert(0, '../wolfgen')
from fbxread import load_anim, rot_xyz

MAP = {'Hips': 'Hips', 'Spine': 'Spine', 'Chest': 'Spine2', 'Neck': 'Neck', 'Head': 'Head',
       'ClavL': 'LeftShoulder', 'UpperArmL': 'LeftArm', 'ForearmL': 'LeftForeArm', 'HandL': 'LeftHand',
       'ThighL': 'LeftUpLeg', 'ShinL': 'LeftLeg', 'FootL': 'LeftFoot',
       'ClavR': 'RightShoulder', 'UpperArmR': 'RightArm', 'ForearmR': 'RightForeArm', 'HandR': 'RightHand',
       'ThighR': 'RightUpLeg', 'ShinR': 'RightLeg', 'FootR': 'RightFoot'}
def rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg)); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
CB = {}
for b in ('UpperArm', 'Forearm', 'Hand'): CB[b + 'L'] = rz(90); CB[b + 'R'] = rz(-90)

def mat_to_quat(R):
    t = np.trace(R)
    if t > 0: s = math.sqrt(t + 1) * 2; q = [(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, s / 4]
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]: s = math.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2; q = [s / 4, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s, (R[2, 1] - R[1, 2]) / s]
    elif R[1, 1] > R[2, 2]: s = math.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2; q = [(R[0, 1] + R[1, 0]) / s, s / 4, (R[1, 2] + R[2, 1]) / s, (R[0, 2] - R[2, 0]) / s]
    else: s = math.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2; q = [(R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, s / 4, (R[1, 0] - R[0, 1]) / s]
    q = np.array(q); return q / np.linalg.norm(q)

def sample(curves, t, default):
    out = []
    for ax, d in zip('XYZ', default):
        c = curves.get(ax)
        out.append(float(np.interp(t, c[0], c[1])) if c else d)
    return out

def retarget(path, skel, fps=30, t0=0.0, t1=None):
    """returns list of (pose{bone:quat}, hips_dy_scaled) per frame between t0..t1 at the source rate."""
    bones, anim = load_anim(path)
    names = {n.split(':')[-1]: m for n, m in ((m['name'], m) for m in bones.values())}
    def parent_chain(n):
        p = names[n]['parent_name']; return p
    def rest_local(n):
        m = names[n]; return rot_xyz(*m['PreRotation']) @ rot_xyz(*m['Lcl Rotation'])
    def anim_local(n, t):
        m = names[n]; a = anim.get(n, {}).get('Lcl Rotation')
        r = sample(a, t, m['Lcl Rotation']) if a else m['Lcl Rotation']
        return rot_xyz(*m['PreRotation']) @ rot_xyz(*r)
    order = []
    def visit(n):
        if n in order: return
        p = parent_chain(n)
        if p in names: visit(p)
        order.append(n)
    for n in names: visit(n)
    wrest = {}
    for n in order:
        p = parent_chain(n); wrest[n] = (wrest[p] if p in wrest else np.eye(3)) @ rest_local(n)
    dur = max(c[0][-1] for a in anim.values() for cs in a.values() for c in cs.values())
    t1 = dur if t1 is None else t1
    hips_rest = names['Hips']['Lcl Translation']; hy_scale = skel.pos[skel.idx('Hips')][1] / max(hips_rest[1], 1e-6)
    frames = []
    for t in np.arange(t0, t1 + 1e-6, 1.0 / fps):
        W = {}
        for n in order:
            p = parent_chain(n); W[n] = (W[p] if p in W else np.eye(3)) @ anim_local(n, t)
        Wd = {n: W[n] @ wrest[n].T for n in W}
        pose = {}; mine = {'Root': np.eye(3)}
        for b, src in MAP.items():
            mine[b] = Wd[src] @ CB.get(b, np.eye(3))
        for b in MAP:
            par = skel.names[skel.parent[skel.idx(b)]]
            while par not in mine: par = skel.names[skel.parent[skel.idx(par)]]
            local = mine[par].T @ mine[b]; pose[b] = tuple(mat_to_quat(local))
        ht = anim.get('Hips', {}).get('Lcl Translation')
        dy = (sample(ht, t, hips_rest)[1] - hips_rest[1]) * hy_scale if ht else 0.0
        frames.append((pose, dy))
    return frames, t1 - t0
