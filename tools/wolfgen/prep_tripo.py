"""Prepare a dense Tripo/Higgsfield GLB for rigging: vertex-cluster decimation that keeps UV charts apart
(no texture smearing) but snaps every chart to the same cluster position (no cracks), then normalise
(+z forward, feet on y=0, given height). Usage: prep_tripo.py in.glb out.npz height cell"""
import sys
import numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from PIL import Image
from prep_mesh import load_glb


def decimate(P, UV, T, cell):
    n = len(P); r = np.concatenate([T[:, 0], T[:, 1], T[:, 2]]); c = np.concatenate([T[:, 1], T[:, 2], T[:, 0]])
    _, chart = connected_components(sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)), directed=False)
    g = np.floor((P - P.min(0)) / cell).astype(np.int64); dims = g.max(0) + 1
    cid = (g[:, 0] * dims[1] + g[:, 1]) * dims[2] + g[:, 2]
    _, cinv = np.unique(cid, return_inverse=True); cinv = cinv.ravel(); nc = cinv.max() + 1
    cpos = np.zeros((nc, 3)); np.add.at(cpos, cinv, P); cpos /= np.bincount(cinv, minlength=nc)[:, None]
    key = cinv.astype(np.int64) * (chart.max() + 1) + chart
    _, kinv = np.unique(key, return_inverse=True); kinv = kinv.ravel(); nk = kinv.max() + 1
    d = np.linalg.norm(P - cpos[cinv], axis=1); order = np.lexsort((d, kinv)); first = np.ones(n, bool); first[1:] = kinv[order][1:] != kinv[order][:-1]
    rep = np.zeros(nk, int); rep[kinv[order[first]]] = order[first]
    NP = cpos[cinv[rep]]; NUV = UV[rep]
    NT = kinv[T]; ok = (NT[:, 0] != NT[:, 1]) & (NT[:, 1] != NT[:, 2]) & (NT[:, 0] != NT[:, 2]); NT = NT[ok]
    NT = np.unique(np.sort(NT, 1), axis=0, return_index=True)[1]; NT = kinv[T][ok][np.sort(NT)]
    return NP, NUV, NT


def prep(src, out, height, cell):
    P, N, UV, T, tex = load_glb(src)
    Q, U, Tn = decimate(P, UV, T, cell)
    Q = Q.copy(); Q[:, 0] -= Q[:, 0].mean(); Q[:, 2] -= (Q[:, 2].min() + Q[:, 2].max()) / 2
    Q[:, 1] -= Q[:, 1].min(); Q *= height / Q[:, 1].max()
    Q = np.stack([-Q[:, 2], Q[:, 1], Q[:, 0]], 1)              # generated characters face +x; engine is +z
    a, b, c = Q[Tn[:, 0]], Q[Tn[:, 1]], Q[Tn[:, 2]]; fn = np.cross(b - a, c - a)
    Nn = np.zeros_like(Q); [np.add.at(Nn, Tn[:, k], fn) for k in range(3)]; Nn /= np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-12
    np.savez(out, P=Q, N=Nn, UV=U, T=Tn)
    tex.convert('RGB').resize((1024, 1024), Image.LANCZOS).save(out.replace('.npz', '_tex.jpg'), quality=90)
    print(out, 'verts', len(Q), 'tris', len(Tn), 'bbox', Q.min(0).round(2), Q.max(0).round(2))


if __name__ == '__main__':
    prep(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
