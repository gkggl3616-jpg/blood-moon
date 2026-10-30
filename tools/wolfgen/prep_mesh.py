"""Extract one wolf from a Higgsfield/Meshy multi-copy GLB, normalise to 1.85 m, feet on y=0, facing +z."""
import json, struct, io, sys
import numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from PIL import Image


def load_glb(path):
    b = open(path, 'rb').read()
    jl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + jl]); bin_ = b[20 + jl + 8:]

    def acc(i):
        a = j['accessors'][i]; v = j['bufferViews'][a['bufferView']]
        ct = {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[a['componentType']]; n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
        off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        arr = np.frombuffer(bin_, ct, a['count'] * n, off)
        return arr.reshape(-1, n) if n > 1 else arr
    pr = j['meshes'][0]['primitives'][0]; at = pr['attributes']
    v = j['bufferViews'][j['images'][0]['bufferView']]
    tex = Image.open(io.BytesIO(bin_[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']])).convert('RGB')
    return acc(at['POSITION']).astype(float), acc(at['NORMAL']).astype(float), acc(at['TEXCOORD_0']).astype(float), acc(pr['indices']).reshape(-1, 3).astype(int), tex


def extract(path, pick_x_rank=2, out='/tmp/wolf_prep.npz', height=1.85):
    P, N, UV, T, tex = load_glb(path)
    key = np.round(P / 1e-4).astype(np.int64); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.reshape(-1)
    n = inv.max() + 1; I = inv[T]
    r = np.concatenate([I[:, 0], I[:, 1], I[:, 2]]); c = np.concatenate([I[:, 1], I[:, 2], I[:, 0]])
    k, lab = connected_components(sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)), directed=False); lab = lab[inv]
    sizes = np.bincount(lab); big = [i for i in np.argsort(-sizes) if sizes[i] > 5000]
    big.sort(key=lambda i: P[lab == i, 0].mean())          # left->right
    comp = big[pick_x_rank]
    vm = lab == comp; ids = np.where(vm)[0]; remap = -np.ones(len(P), int); remap[ids] = np.arange(len(ids))
    tm = vm[T].all(1); Tn = remap[T[tm]]
    Q = P[ids].copy(); Q[:, 0] -= Q[:, 0].mean(); Q[:, 2] -= (Q[:, 2].min() + Q[:, 2].max()) / 2
    Q[:, 1] -= Q[:, 1].min(); s = height / Q[:, 1].max(); Q *= s
    np.savez(out, P=Q, N=N[ids], UV=UV[ids], T=Tn)
    tex.resize((1024, 1024), Image.LANCZOS).save(out.replace('.npz', '_tex.jpg'), quality=88)
    print('wolf', comp, 'verts', len(Q), 'tris', len(Tn), 'bbox', Q.min(0).round(2), Q.max(0).round(2))


if __name__ == '__main__':
    extract(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 2)
