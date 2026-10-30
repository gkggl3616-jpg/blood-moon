"""Fit the engine skeleton to a prepared (normalised, +z facing) wolf mesh and compute skin weights."""
import numpy as np
from core import *

# joint positions measured from the prepared ice-wolf mesh (metres, y up, +z forward, +x = character's left)
J = dict(
    Hips=(0, .98, -.01), Spine=(0, 1.12, 0), Chest=(0, 1.30, .02), Neck=(0, 1.50, .07), Head=(0, 1.62, .10), Jaw=(0, 1.62, .20),
    Clav=(.12, 1.42, .03), UpperArm=(.25, 1.40, .02), Forearm=(.31, 1.17, .10), Hand=(.30, .90, .24),
    Thigh=(.12, .96, .0), Shin=(.13, .52, .10), Foot=(.12, .12, -.04),
    Tail1=(0, .95, -.12), Tail2=(0, .75, -.28), Tail3=(0, .55, -.34),
)
# the generated mesh is asymmetric: its right arm hangs straight down at z~0 while the left reaches forward
JR = dict(UpperArm=(.25, 1.38, -.02), Forearm=(.27, 1.16, -.08), Hand=(.28, .88, .03)); HAND_TIP_R = (.27, .72, .04)
HEAD_TIP = (0, 1.64, .36); HAND_TIP = (.30, .76, .30); TOE_TIP = (.12, .02, .22); TAIL_TIP = (0, .40, -.38)


def build_skeleton(extra_cape=False):
    s = Skeleton()
    s.add('Root', None, (0, 0, 0)); s.add('Hips', 'Root', J['Hips']); s.add('Spine', 'Hips', J['Spine']); s.add('Chest', 'Spine', J['Chest'])
    s.add('Neck', 'Chest', J['Neck']); s.add('Head', 'Neck', J['Head']); s.add('Jaw', 'Head', J['Jaw'])
    for sx, L in ((1, 'L'), (-1, 'R')):
        m = lambda p: (p[0] * sx, p[1], p[2]); JJ = J if sx == 1 else {**J, **JR}
        s.add('Clav' + L, 'Chest', m(J['Clav'])); s.add('UpperArm' + L, 'Clav' + L, m(JJ['UpperArm']))
        s.add('Forearm' + L, 'UpperArm' + L, m(JJ['Forearm'])); s.add('Hand' + L, 'Forearm' + L, m(JJ['Hand']))
        s.add('Thigh' + L, 'Hips', m(J['Thigh'])); s.add('Shin' + L, 'Thigh' + L, m(J['Shin'])); s.add('Foot' + L, 'Shin' + L, m(J['Foot']))
    s.add('Tail1', 'Hips', J['Tail1']); s.add('Tail2', 'Tail1', J['Tail2']); s.add('Tail3', 'Tail2', J['Tail3'])
    return s


def segments(skel):
    """bone -> (a, b, radius): capsule used for weighting."""
    p = {n: skel.pos[i] for i, n in enumerate(skel.names)}
    seg = {'Hips': (p['Hips'], p['Spine'], .20), 'Spine': (p['Spine'], p['Chest'], .20), 'Chest': (p['Chest'], p['Neck'], .24),
           'Neck': (p['Neck'], p['Head'], .13), 'Head': (p['Head'], np.array(HEAD_TIP), .20), 'Jaw': (p['Jaw'], np.array(HEAD_TIP) + (0, -.04, 0), .06),
           'Tail1': (p['Tail1'], p['Tail2'], .14), 'Tail2': (p['Tail2'], p['Tail3'], .14), 'Tail3': (p['Tail3'], np.array(TAIL_TIP), .14)}
    for sx, L in ((1, 'L'), (-1, 'R')):
        m = lambda q: np.array((q[0] * sx, q[1], q[2]))
        seg['Clav' + L] = (p['Clav' + L], p['UpperArm' + L], .12); seg['UpperArm' + L] = (p['UpperArm' + L], p['Forearm' + L], .12)
        seg['Forearm' + L] = (p['Forearm' + L], p['Hand' + L], .12); seg['Hand' + L] = (p['Hand' + L], m(HAND_TIP if sx == 1 else HAND_TIP_R), .09)
        seg['Thigh' + L] = (p['Thigh' + L], p['Shin' + L], .17); seg['Shin' + L] = (p['Shin' + L], p['Foot' + L], .13)
        seg['Foot' + L] = (p['Foot' + L], m(TOE_TIP), .10)
    return seg


def seg_dist(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-9), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def compute_weights(skel, P, sharp=2.2, T=None):
    seg = segments(skel); names = list(seg)
    D = np.stack([seg_dist(P, *seg[n][:2]) / seg[n][2] for n in names], 1)   # normalised distance
    if T is not None:   # arm bones use surface (geodesic) distance so a hanging hand never grabs the hip/pants it touches
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import dijkstra
        _, inv = np.unique(np.round(P, 4), axis=0, return_inverse=True); inv = inv.ravel(); n = inv.max() + 1
        Q = np.zeros((n, 3)); Q[inv] = P
        E = inv[np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])]; w = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1) + 1e-6
        G = coo_matrix((w, (E[:, 0], E[:, 1])), shape=(n, n)).tocsr()
        for k, nm in enumerate(names):
            if not any(nm.startswith(b) for b in ('UpperArm', 'Forearm', 'Hand')): continue
            a_, b_, r = seg[nm]; dq = seg_dist(Q, a_, b_); seeds = np.argsort(dq)[:12]
            gd = dijkstra(G, directed=False, indices=seeds, min_only=True) + 0
            D[:, k] = np.maximum(D[:, k], gd[inv] / r * .55)
    # side guard: left-side bones never drive right-side vertices (and vice versa) away from the midline
    for k, n in enumerate(names):
        if n.endswith('L'): D[:, k] += np.where(P[:, 0] < -.04, 3.0, 0)
        if n.endswith('R'): D[:, k] += np.where(P[:, 0] > .04, 3.0, 0)
    W = np.exp(-(D ** 2) * sharp)
    W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
    idx = np.argsort(-W, 1)[:, :4]; out_w = np.take_along_axis(W, idx, 1); out_w /= out_w.sum(1, keepdims=True)
    return np.array([[skel.idx(names[i]) for i in row] for row in idx], np.uint16), out_w.astype(np.float32), names
