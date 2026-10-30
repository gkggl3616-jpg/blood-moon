import sys, json, io
import numpy as np
from core import *
from rig import *
from anim import *
from PIL import Image

def fix_stretch(S, P, Jn, Wn, T, rigid, rounds=16):
    """Find edges that tear apart (posed length >> rest length) over all clips and pull their end-point weights together."""
    nb = len(S.names); n = len(P)
    Wd = np.zeros((n, nb)); 
    for k in range(4): np.add.at(Wd, (np.arange(n), Jn[:, k]), Wn[:, k])
    E = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1), axis=0)
    E0 = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1)
    rest = S.fk({}); inv = [np.linalg.inv(m) for m in rest]; Ph = np.c_[P, np.ones(n)]
    poses = []
    for name in ('WolfRunQuad', 'WolfRoar', 'WolfClaw', 'WolfClawR', 'WolfJump', 'WolfRoll', 'WolfIdle'):
        fr = bake(S, name)['frames']; poses += [fr[i] for i in range(0, len(fr), 2)]
    for it in range(rounds):
        top = np.argsort(-Wd, 1)[:, :4]; bad = np.zeros(len(E), bool); worst = 0
        for pose, root in poses:
            mats = S.fk(pose, root); sk = [m @ i for m, i in zip(mats, inv)]; Q = np.zeros((n, 3))
            for b in range(nb):
                w = Wd[:, b]; m = w > 1e-4
                if m.any(): Q[m] += w[m, None] * (Ph[m] @ sk[b].T)[:, :3]
            L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1); b_ = (L > E0 * 2.2 + .06); bad |= b_; worst = max(worst, float((L - E0).max()))
        print('stretch round', it, 'bad edges', int(bad.sum()), 'worst +%.2fm' % worst)
        if not bad.any(): break
        for a, b in E[bad]:
            if rigid[a] and rigid[b]: continue
            if rigid[a]: Wd[b] = Wd[a]
            elif rigid[b]: Wd[a] = Wd[b]
            else: Wd[a] = Wd[b] = (Wd[a] + Wd[b]) / 2
    top = np.argsort(-Wd, 1)[:, :4]; w = np.take_along_axis(Wd, top, 1); w /= w.sum(1, keepdims=True)
    return top.astype(np.uint16).tolist(), w.astype(np.float32).tolist()


def make_mesh(prep='/tmp/wolf_prep.npz', texpath='/tmp/wolf_prep_tex.jpg'):
    d = np.load(prep); P = d['P']; Nn = d['N']; UV = d['UV']; T = d['T']
    S = build_skeleton(); Jn, Wn, _ = compute_weights(S, P, T=T)
    M = Mesh(S); M.material('Fur_icewolf', (1, 1, 1), roughness=.9, textured=True, double=True)
    tex = Image.open(texpath).convert('RGB'); tarr = np.array(tex)
    u = (UV[:, 0] % 1 * (tarr.shape[1] - 1)).astype(int); v = (UV[:, 1] % 1 * (tarr.shape[0] - 1)).astype(int)
    col = tarr[v, u] / 255.0
    # rigid ice: blue crystal vertices follow a single bone so the shards never stretch
    ice = ((col[:, 2] - col[:, 0]) > .10) & (col[:, 2] > .55)
    for i in np.where(ice)[0]:
        L = 'L' if P[i, 0] >= 0 else 'R'; sx = 1 if L == 'L' else -1
        el = S.pos[S.idx('Forearm' + L)].copy(); kn = np.array([J['Shin'][0] * sx, J['Shin'][1], J['Shin'][2]])
        if np.linalg.norm(P[i] - el) < .17: Jn[i] = [S.idx('Forearm' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
        elif np.linalg.norm(P[i] - kn) < .17: Jn[i] = [S.idx('Shin' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
        else: ice[i] = False
    print('rigid ice verts', int(ice.sum()))
    Jn, Wn = fix_stretch(S, P, Jn, Wn, T, ice)
    M.P = [p for p in P]; M.N = [n for n in smooth_normals(P, T)]; M.J = list(Jn); M.W = list(Wn)
    M.C = [list(c) + [1.0] for c in col]; M.M = ['Fur_icewolf'] * len(P)
    M.tris = [t.tolist() + ['Fur_icewolf'] for t in T]
    M.UV = UV; M.texture = open(texpath, 'rb').read()
    # emissive mask: only the ice-blue texels glow (elbow crystals + knee shards)
    t = tarr.astype(float) / 255.0; mask = ((t[..., 2] - t[..., 0]) > .10) & (t[..., 2] > .55)
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
