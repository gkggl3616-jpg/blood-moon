"""Quick flat-shaded front/side preview of a static or skinned GLB (painter's algorithm)."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB
def draw(P, I, size=360, side=False):
    T = P[I.reshape(-1, 3)]; x = T[..., 2] if side else T[..., 0]; y = T[..., 1]; z = -T[..., 0] if side else T[..., 2]
    lo = np.array([P[:, 2 if side else 0].min(), P[:, 1].min()]); span = max(np.ptp(P[:, 1]), np.ptp(P[:, 2 if side else 0])) * 1.05
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    L = np.array([.4, .5, .77]) if not side else np.array([.77, .5, -.4]); sh = np.clip(np.abs(nrm @ L), .15, 1)
    im = Image.new('RGB', (size, size), (30, 32, 38)); d = ImageDraw.Draw(im)
    for t in np.argsort(z.mean(1)):
        pts = [((x[t, k] - lo[0]) / span * size + size * .02, size - (y[t, k] - lo[1]) / span * size - size * .02) for k in range(3)]
        c = int(60 + 190 * sh[t]); d.polygon(pts, fill=(c, c, int(c * .95)))
    return im
def sheet(items, out):
    ims = []
    for name, P, I in items:
        a = draw(P, I); b = draw(P, I, side=True); c = Image.new('RGB', (720, 380), (20, 20, 24)); c.paste(a, (0, 20)); c.paste(b, (360, 20))
        ImageDraw.Draw(c).text((6, 4), name, fill=(255, 220, 120)); ims.append(c)
    cols = 2; rows = (len(ims) + 1) // 2; S = Image.new('RGB', (720 * cols, 380 * rows))
    for k, im in enumerate(ims): S.paste(im, ((k % cols) * 720, (k // cols) * 380))
    S.save(out)
if __name__ == '__main__':
    d = sys.argv[1]; items = []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.glb'): continue
        g = GLB(os.path.join(d, f)); p = g.j['meshes'][0]['primitives'][0]
        items.append((f, g.acc(p['attributes']['POSITION']), g.acc(p['indices'])))
    sheet(items, sys.argv[2])
