"""Minimal GLB reader/writer helpers (numpy only)."""
import json, struct, numpy as np
CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
class GLB:
    def __init__(self, path):
        b = open(path, 'rb').read(); jl = struct.unpack('<I', b[12:16])[0]
        self.j = json.loads(b[20:20 + jl]); off = 20 + jl
        self.bin = b[off + 8: off + 8 + struct.unpack('<I', b[off:off + 4])[0]] if off < len(b) else b''
    def acc(self, i):
        a = self.j['accessors'][i]; v = self.j['bufferViews'][a.get('bufferView', 0)]
        dt = np.dtype(CT[a['componentType']]); n = NC[a['type']]; o = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        st = v.get('byteStride', 0)
        if st and st != dt.itemsize * n:
            raw = np.frombuffer(self.bin, np.uint8, count=st * a['count'], offset=o).reshape(a['count'], st)
            arr = raw[:, :dt.itemsize * n].copy().view(dt).reshape(a['count'], n)
        else:
            arr = np.frombuffer(self.bin, dt, count=a['count'] * n, offset=o).reshape(a['count'], n).copy()
        if a.get('normalized') and dt != np.float32: arr = arr.astype(np.float32) / np.iinfo(dt).max
        return arr
    def view_bytes(self, i):
        v = self.j['bufferViews'][i]; o = v.get('byteOffset', 0); return self.bin[o:o + v['byteLength']]
    def node_world(self):
        """World matrices for every node (column-vector convention)."""
        N = self.j['nodes']; W = [None] * len(N); par = {}
        for i, n in enumerate(N):
            for c in n.get('children', []): par[c] = i
        def local(n):
            if 'matrix' in n: return np.array(n['matrix'], float).reshape(4, 4).T
            t = np.array(n.get('translation', [0, 0, 0]), float); r = n.get('rotation', [0, 0, 0, 1]); s = np.array(n.get('scale', [1, 1, 1]), float)
            x, y, z, w = r
            R = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
            M = np.eye(4); M[:3, :3] = R * s; M[:3, 3] = t; return M
        def get(i):
            if W[i] is None: W[i] = (get(par[i]) if i in par else np.eye(4)) @ local(N[i])
            return W[i]
        for i in range(len(N)): get(i)
        return W, par

def _q2m(q):
    x, y, z, w = q / (np.linalg.norm(q) + 1e-12)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def _slerp(a, b, t):
    d = np.dot(a, b)
    if d < 0: b = -b; d = -d
    if d > .9995: r = a + t * (b - a); return r / np.linalg.norm(r)
    th = np.arccos(d); return (np.sin((1 - t) * th) * a + np.sin(t * th) * b) / np.sin(th)
def sample_trs(g, anim, t):
    """Return {node: {'translation'|'rotation'|'scale': value}} sampled at time t (seconds, clamped)."""
    out = {}
    for ch in anim['channels']:
        s = anim['samplers'][ch['sampler']]; T = g.acc(s['input']).reshape(-1); V = g.acc(s['output'])
        tt = min(max(t, T[0]), T[-1]); k = int(np.searchsorted(T, tt, side='right') - 1); k = min(max(k, 0), len(T) - 1)
        path = ch['target']['path']
        if path == 'weights': continue
        if k + 1 < len(T) and T[k + 1] > T[k]:
            f = (tt - T[k]) / (T[k + 1] - T[k])
            v = _slerp(V[k].astype(float), V[k + 1].astype(float), f) if path == 'rotation' else V[k] * (1 - f) + V[k + 1] * f
        else: v = V[k]
        out.setdefault(ch['target']['node'], {})[path] = np.asarray(v, float)
    return out
def world_with(g, over):
    N = g.j['nodes']; par = {}
    for i, n in enumerate(N):
        for c in n.get('children', []): par[c] = i
    W = [None] * len(N)
    def local(i):
        n = N[i]; o = over.get(i, {})
        if 'matrix' in n and not o: return np.array(n['matrix'], float).reshape(4, 4).T
        t = o.get('translation', np.array(n.get('translation', [0, 0, 0]), float)); r = o.get('rotation', np.array(n.get('rotation', [0, 0, 0, 1]), float)); s = o.get('scale', np.array(n.get('scale', [1, 1, 1]), float))
        M = np.eye(4); M[:3, :3] = _q2m(np.asarray(r, float)) * s; M[:3, 3] = t; return M
    def get(i):
        if W[i] is None: W[i] = (get(par[i]) if i in par else np.eye(4)) @ local(i)
        return W[i]
    for i in range(len(N)): get(i)
    return W
def skin(g, W, mesh_node=None, normals=False):
    """Linear-blend-skin the first skinned mesh with node world matrices W. Returns (P, I)."""
    N = g.j['nodes']; mi = mesh_node if mesh_node is not None else next(i for i, n in enumerate(N) if 'skin' in n)
    p = g.j['meshes'][N[mi]['mesh']]['primitives'][0]; A = p['attributes']
    P = g.acc(A['POSITION']).astype(float); J = g.acc(A['JOINTS_0']).astype(int); Wt = g.acc(A['WEIGHTS_0']).astype(float)
    sk = g.j['skins'][N[mi]['skin']]; IB = g.acc(sk['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
    M = np.stack([W[j] @ IB[k] for k, j in enumerate(sk['joints'])])
    Ph = np.c_[P, np.ones(len(P))]; out = np.zeros((len(P), 3))
    for k in range(4): out += Wt[:, k:k + 1] * np.einsum('nij,nj->ni', M[J[:, k]], Ph)[:, :3]
    if normals:
        Nn = g.acc(A['NORMAL']).astype(float); on = np.zeros_like(Nn)
        for k in range(4): on += Wt[:, k:k + 1] * np.einsum('nij,nj->ni', M[J[:, k]][:, :3, :3], Nn)
        return out, on / (np.linalg.norm(on, axis=1, keepdims=True) + 1e-9)
    return out, g.acc(p['indices']).reshape(-1)
