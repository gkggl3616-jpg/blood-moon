"""Orthographic, textured side view of a static GLB with a labelled grid, used to locate grip / trigger / sight /
magazine / muzzle sockets by eye. usage: side_view.py model.glb out.png [axis: x|z (horizontal axis)]"""
import sys, os, io, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'meshy')); from glbio import GLB
def load(path):
    g = GLB(path); W, _ = g.node_world(); Ps, Is, Cs = [], [], []; off = 0
    for i, n in enumerate(g.j['nodes']):
        if 'mesh' not in n: continue
        for pr in g.j['meshes'][n['mesh']]['primitives']:
            A = pr['attributes']; P = g.acc(A['POSITION']).astype(float); P = (np.c_[P, np.ones(len(P))] @ W[i].T)[:, :3]
            UV = g.acc(A['TEXCOORD_0']) if 'TEXCOORD_0' in A else np.zeros((len(P), 2)); I = g.acc(pr['indices']).reshape(-1, 3) + off
            col = np.full((len(P), 3), .6)
            try:
                ti = g.j['materials'][pr.get('material', 0)]['pbrMetallicRoughness']['baseColorTexture']['index']
                tex = np.asarray(Image.open(io.BytesIO(g.view_bytes(g.j['images'][g.j['textures'][ti]['source']]['bufferView']))).convert('RGB'), np.float32) / 255
                th, tw = tex.shape[:2]; col = tex[np.clip((UV[:, 1] * th).astype(int), 0, th - 1), np.clip((UV[:, 0] * tw).astype(int), 0, tw - 1)]
            except Exception: pass
            Ps.append(P); Is.append(I); Cs.append(col); off += len(P)
    return np.vstack(Ps), np.vstack(Is), np.vstack(Cs)
def render(P, I, C, out, hax=0, vax=1, dax=2, W=1400, H=700, grid=.05):
    lo = P.min(0); hi = P.max(0); span = max((hi[hax] - lo[hax]) / (W * .9), (hi[vax] - lo[vax]) / (H * .85))
    X = lambda v: (v - lo[hax]) / span + W * .05; Y = lambda v: H * .92 - (v - lo[vax]) / span
    im = Image.new('RGB', (W, H), (245, 245, 245)); d = ImageDraw.Draw(im)
    g0 = np.floor(lo / grid) * grid
    x = g0[hax]
    while x <= hi[hax] + grid:
        d.line([(X(x), 0), (X(x), H)], fill=(205, 205, 215)); d.text((X(x) + 2, 2), '%.2f' % x, fill=(90, 90, 160)); x += grid
    y = g0[vax]
    while y <= hi[vax] + grid:
        d.line([(0, Y(y)), (W, Y(y))], fill=(205, 205, 215)); d.text((2, Y(y) - 10), '%.2f' % y, fill=(160, 90, 90)); y += grid
    T = P[I]; n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    sh = .55 + .45 * np.abs(n[:, dax]); col = C[I].mean(1) * sh[:, None]
    for t in np.argsort(T[:, :, dax].mean(1)):
        d.polygon([(X(T[t, k, hax]), Y(T[t, k, vax])) for k in range(3)], fill=tuple(int(255 * min(1, c)) for c in col[t]))
    im.save(out); return lo, hi
if __name__ == '__main__':
    P, I, C = load(sys.argv[1]); lo, hi = P.min(0), P.max(0); ext = hi - lo
    hax = int(np.argmax([ext[0], -1, ext[2]])) if len(sys.argv) < 4 else {'x': 0, 'z': 2}[sys.argv[3]]
    dax = 2 if hax == 0 else 0
    print('bbox', lo.round(3), hi.round(3), 'horizontal axis', 'xyz'[hax], 'tris', len(I))
    render(P, I, C, sys.argv[2], hax, 1, dax)
