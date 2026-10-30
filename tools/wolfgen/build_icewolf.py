import sys, json, io
import numpy as np
from core import *
from rig import *
from anim import *
from PIL import Image

def fix_stretch(S, P, Jn, Wn, T, rigid, rounds=40, ratio=2.4, slack=.08, poses=None):
    """Permanent anti-stretch pass: skin the mesh through every clip, find edges that grow past `ratio`x rest
    length (+slack m) and diffuse the bone weights over the 2-ring around them until no edge tears."""
    import scipy.sparse as sp
    nb = len(S.names); n = len(P)
    Wd = np.zeros((n, nb))
    for k in range(4): np.add.at(Wd, (np.arange(n), np.asarray(Jn)[:, k]), np.asarray(Wn)[:, k])
    E = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1), axis=0)
    _, inv = np.unique(np.round(P, 4), axis=0, return_inverse=True); inv = inv.ravel()      # weld seams
    A = sp.coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
    G = sp.coo_matrix((np.ones(n), (np.arange(n), inv)), shape=(n, inv.max() + 1)).tocsr(); A = (A + G @ G.T).tocsr(); A.data[:] = 1
    deg = np.asarray(A.sum(1)).ravel(); E0 = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1)
    cnt = np.asarray(G.sum(0)).ravel()
    def weld(W):   # vertices sharing a position (UV seams) must share weights, or the seam opens into long triangles
        return G @ ((G.T @ W) / np.maximum(cnt, 1)[:, None])
    Wd = weld(Wd)
    rest = S.fk({}); inv_rest = [np.linalg.inv(m) for m in rest]; Ph = np.c_[P, np.ones(n)]
    if poses is None:
        poses = []
        for name in CLIPS:
            fr = bake(S, name)['frames']; poses += [fr[i] for i in range(0, len(fr), 2)]
    free = ~np.asarray(rigid, bool)
    for it in range(rounds):
        bad = np.zeros(len(E), bool); worst = 0
        for pose, root in poses:
            mats = S.fk(pose, root); sk = [m @ i for m, i in zip(mats, inv_rest)]; Q = np.zeros((n, 3))
            for b in range(nb):
                w = Wd[:, b]; m = w > 1e-4
                if m.any(): Q[m] += w[m, None] * (Ph[m] @ sk[b].T)[:, :3]
            L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1); b_ = (L > E0 * ratio) & (L - E0 > slack); bad |= b_
            worst = max(worst, float(np.max(np.where(b_, L - E0, 0))))
        print('stretch round', it, 'bad edges', int(bad.sum()), 'worst +%.3fm' % worst)
        if not bad.any(): break
        for a_, b_ in E[bad]:                                                    # first: make the torn pair move together
            if free[a_] == free[b_]: Wd[a_] = Wd[b_] = (Wd[a_] + Wd[b_]) / 2
            elif free[a_]: Wd[a_] = Wd[b_]
            elif free[b_]: Wd[b_] = Wd[a_]
        sel = np.zeros(n, bool); sel[E[bad].ravel()] = True
        for _ in range(2): sel = sel | (A @ sel.astype(float) > 0)            # grow to the 2-ring
        sel &= free
        for _ in range(3):                                                     # weight diffusion on the region
            Wn_ = (A @ Wd) / np.maximum(deg, 1)[:, None]
            Wd[sel] = .4 * Wd[sel] + .6 * Wn_[sel]
        Wd = weld(Wd)
    top = np.argsort(-Wd, 1)[:, :4]; w = np.take_along_axis(Wd, top, 1); w /= np.maximum(w.sum(1, keepdims=True), 1e-9)
    return top.astype(np.uint16).tolist(), w.astype(np.float32).tolist()


def ICE_MASK(c):
    return ((c[..., 2] - c[..., 0]) > .10) & (c[..., 2] > .55)


def make_mesh(prep='/tmp/wolf_prep.npz', texpath='/tmp/wolf_prep_tex.jpg'):
    d = np.load(prep); P = d['P']; Nn = d['N']; UV = d['UV']; T = d['T']
    S = build_skeleton(); Jn, Wn, _ = compute_weights(S, P, T=T)
    M = Mesh(S); M.material('Fur_icewolf', (1, 1, 1), roughness=.9, textured=True, double=True)
    tex = Image.open(texpath).convert('RGB'); tarr = np.array(tex)
    u = (UV[:, 0] % 1 * (tarr.shape[1] - 1)).astype(int); v = (UV[:, 1] % 1 * (tarr.shape[0] - 1)).astype(int)
    col = tarr[v, u] / 255.0
    # rigid ice: blue crystal vertices follow a single bone so the shards never stretch
    ice = ICE_MASK(col)
    for i in np.where(ice)[0]:
        L = 'L' if P[i, 0] >= 0 else 'R'; sx = 1 if L == 'L' else -1
        el = S.pos[S.idx('Forearm' + L)].copy(); kn = np.array([J['Shin'][0] * sx, J['Shin'][1], J['Shin'][2]])
        if np.linalg.norm(P[i] - el) < .17: Jn[i] = [S.idx(('UpperArm' if P[i, 1] > el[1] + .03 else 'Forearm') + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]   # shards above the elbow ride the upper arm
        elif np.linalg.norm(P[i] - kn) < .17: Jn[i] = [S.idx('Shin' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
        else: ice[i] = False
    print('rigid ice verts', int(ice.sum()))
    Jn, Wn = fix_stretch(S, P, Jn, Wn, T, ice)
    M.P = [p for p in P]; M.N = [n for n in smooth_normals(P, T)]; M.J = list(Jn); M.W = list(Wn)
    M.C = [list(c) + [1.0] for c in col]; M.M = ['Fur_icewolf'] * len(P)
    M.tris = [t.tolist() + ['Fur_icewolf'] for t in T]
    M.UV = UV; M.texture = open(texpath, 'rb').read()
    # emissive mask: only the ice-blue texels glow (elbow crystals + knee shards)
    t = tarr.astype(float) / 255.0; mask = ICE_MASK(t)
    from scipy.ndimage import binary_dilation
    mask = binary_dilation(mask, iterations=1)
    em = (t * mask[..., None] * 255).astype(np.uint8); buf = io.BytesIO(); Image.fromarray(em).save(buf, 'PNG', optimize=True); M.emissive_tex = buf.getvalue()
    M.materials['Fur_icewolf']['emissive'] = [.35, .35, .35]
    return S, M

if __name__ == '__main__':
    S, M = make_mesh()
    clips = {n: bake(S, n) for n in CLIPS}
    extras = dict(source_kind='new_ice', clawProfile='standard', previewHeight=1.85, run_stride_m=3.2, run_reference_speed_mps=8.0)
    write_glb('/tmp/icewolf_rigged.glb', S, M, clips, 'Body_bilge', extras=extras)
    import os; print('glb', os.path.getsize('/tmp/icewolf_rigged.glb'))
