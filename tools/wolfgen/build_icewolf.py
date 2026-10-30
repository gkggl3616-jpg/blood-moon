import sys, json, io
import numpy as np
from core import *
from rig import *
from anim import *
from PIL import Image

def make_mesh(prep='/tmp/wolf_prep.npz', texpath='/tmp/wolf_prep_tex.jpg'):
    d = np.load(prep); P = d['P']; Nn = d['N']; UV = d['UV']; T = d['T']
    S = build_skeleton(); Jn, Wn, _ = compute_weights(S, P)
    M = Mesh(S); M.material('Fur_icewolf', (1, 1, 1), roughness=.9, textured=True)
    tex = Image.open(texpath).convert('RGB'); tarr = np.array(tex)
    u = (UV[:, 0] % 1 * (tarr.shape[1] - 1)).astype(int); v = (UV[:, 1] % 1 * (tarr.shape[0] - 1)).astype(int)
    col = tarr[v, u] / 255.0
    # rigid ice: blue crystal vertices follow a single bone so the shards never stretch
    ice = ((col[:, 2] - col[:, 0]) > .10) & (col[:, 2] > .55)
    for i in np.where(ice)[0]:
        L = 'L' if P[i, 0] >= 0 else 'R'; sx = 1 if L == 'L' else -1
        el = np.array([J['Forearm'][0] * sx, J['Forearm'][1], J['Forearm'][2]]); kn = np.array([J['Shin'][0] * sx, J['Shin'][1], J['Shin'][2]])
        if np.linalg.norm(P[i] - el) < .17: Jn[i] = [S.idx('Forearm' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
        elif np.linalg.norm(P[i] - kn) < .17: Jn[i] = [S.idx('Shin' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
        else: ice[i] = False
    print('rigid ice verts', int(ice.sum()))
    M.P = [p for p in P]; M.N = [n for n in normalize(Nn)]; M.J = Jn.tolist(); M.W = Wn.tolist()
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
    extras = dict(source_kind='new_ice', clawProfile='standard', previewHeight=1.85, run_stride_m=4.8, run_reference_speed_mps=8.0)
    write_glb('/tmp/icewolf_rigged.glb', S, M, clips, 'Body_bilge', extras=extras)
    import os; print('glb', os.path.getsize('/tmp/icewolf_rigged.glb'))
