"""Per-character first-person arm textures for models/fp_arms.glb.

Every triangle of the arm mesh is rasterised in UV space with its bind-pose 3D position, bone and side (palm/back)
interpolated per pixel, so gloves and arm accessories are drawn ON the hand surface (they follow the fingers exactly):
  bilge    : tactical fingerless glove (knuckle armour, padded back, velcro wrist strap)
  ay       : black floral lace fingerless glove with a scalloped cuff (Aysel)
  zeynos   : black leather gloves with a heart-shaped cut-out on the back of the hand and a wrist snap
  ates     : bare hands, red cloth wrist wraps
  kral     : bare hands, dark leather bracers with metal studs
  hellgate : charred skin with glowing lava cracks
Writes app/src/main/assets/models/fp/<id>_c.jpg (colour) and <id>_r.jpg (roughness in G, glTF convention).
usage: python3 tools/weapons/paint_fp_skins.py"""
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'meshy')); from glbio import GLB
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'app/src/main/assets/models/fp'); os.makedirs(OUT, exist_ok=True)
S = 1024
g = GLB(os.path.join(ROOT, 'app/src/main/assets/models/fp_arms.glb')); j = g.j; Wn, _ = g.node_world(); nm = {n['name']: i for i, n in enumerate(j['nodes'])}
pr = j['meshes'][0]['primitives'][0]
UV = g.acc(pr['attributes']['TEXCOORD_0']).astype(float); I = g.acc(pr['indices']).reshape(-1, 3)
J = g.acc(pr['attributes']['JOINTS_0']); Wt = g.acc(pr['attributes']['WEIGHTS_0'])
# rest-pose skinned positions (the mesh's own coordinates are in bind space, not next to the bones)
P0 = np.c_[g.acc(pr['attributes']['POSITION']).astype(float), np.ones(len(J))]; IB = g.acc(j['skins'][0]['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
SM = np.stack([Wn[k] @ IB[q] for q, k in enumerate(j['skins'][0]['joints'])]); P = np.zeros((len(J), 3))
for c in range(4): P += Wt[:, c:c + 1] * np.einsum('nij,nj->ni', SM[J[:, c]], P0)[:, :3]
jn = [j['nodes'][k]['name'] for k in j['skins'][0]['joints']]
dom = [jn[J[i][Wt[i].argmax()]] for i in range(len(P))]
sof = lambda n: n[-2] if n[-1].isdigit() else n[-1]
B = lambda k: Wn[nm[k]][:3, 3]
base = np.asarray(Image.open(os.path.join(ROOT, 'art/3d/fp_arms/new_diff.png')).convert('RGB').resize((S, S)), float) / 255
# ---- per-vertex attributes in each hand's frame ---------------------------------------------------------------------
side = np.array([1.0 if sof(d) == 'L' else -1.0 for d in dom])   # +1 left arm
lev = np.array([int(d[-1]) if d[-1].isdigit() else 0 for d in dom]); isthumb = np.array([d.startswith('Thumb') for d in dom])
isfinger = np.array([d.startswith(('Index', 'Middle', 'Ring', 'Pinky')) for d in dom])
ishand = np.array([d.startswith(('Hand', 'Palm', 'Index', 'Middle', 'Ring', 'Pinky', 'Thumb')) for d in dom])
A = np.zeros((len(P), 4))   # u = along fingers from the wrist (m), w = across (index +), s = palm side (+) / back (-), d = up the forearm from the wrist (m)
for L in 'LR':
    sel = np.array([sof(d) == L for d in dom]); h = B('Hand' + L); f = B('Middle' + L + '1') - h; f /= np.linalg.norm(f)
    sd = B('Index' + L + '1') - B('Pinky' + L + '1'); n = np.cross(sd, f) * (1 if L == 'R' else -1); n -= f * (n @ f); n /= np.linalg.norm(n)
    w_ = np.cross(n, f); w_ *= np.sign(w_ @ sd)
    fa = B('Forearm' + L) - h; fa /= np.linalg.norm(fa)
    q = P[sel] - h; A[sel, 0] = q @ f; A[sel, 1] = q @ w_; A[sel, 2] = q @ n; A[sel, 3] = q @ fa
# ---- rasteriser: per pixel attributes ---------------------------------------------------------------------------------
attr = np.full((S, S, 8), np.nan, np.float32)   # u w s d lev thumb finger hand
vals = np.c_[A, lev, isthumb, isfinger, ishand].astype(np.float32)
for t in I:
    uv = UV[t] * S; x0, y0 = np.floor(uv.min(0)).astype(int); x1, y1 = np.ceil(uv.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, S - 1), min(y1, S - 1)
    if x1 < x0 or y1 < y0: continue
    gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
    (ax, ay), (bx, by), (cx, cy) = uv; den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-12: continue
    l0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den; l1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den; l2 = 1 - l0 - l1
    m = (l0 >= -.02) & (l1 >= -.02) & (l2 >= -.02)
    if not m.any(): continue
    v = l0[..., None] * vals[t[0]] + l1[..., None] * vals[t[1]] + l2[..., None] * vals[t[2]]
    v[..., 4:] = np.maximum(np.maximum(vals[t[0], 4:], vals[t[1], 4:]), vals[t[2], 4:]) * (v[..., 4:] > .34)   # categorical: majority-ish
    blk = attr[y0:y1 + 1, x0:x1 + 1]; blk[m] = v[m]
# dilate into the gutters so mip-mapping never shows the skin colour along UV seams
for _ in range(6):
    miss = np.isnan(attr[..., 0])
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        sh = np.roll(np.roll(attr, dy, 0), dx, 1); fill = miss & ~np.isnan(sh[..., 0]); attr[fill] = sh[fill]
u, w, s, d, lv, th, fi, ha = [attr[..., k] for k in range(8)]
valid = ~np.isnan(u); u, w, s, d = [np.nan_to_num(x) for x in (u, w, s, d)]; lv, th, fi, ha = [np.nan_to_num(x) > .5 for x in (lv, th, fi, ha)]
lv = np.nan_to_num(attr[..., 4])
rng = np.random.default_rng(7); noise = np.asarray(Image.fromarray((rng.random((128, 128)) * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC), float) / 255
def tone(rgb, var=.06):
    c = base / base[valid].mean(0) * np.array(rgb) / 255; return np.clip(c * (1 - var / 2 + var * noise[..., None]), 0, 1)
def mix(a, b, m): m = np.clip(m, 0, 1)[..., None]; return a * (1 - m) + b * m
def fabric(rgb, scale=180, amp=.12):
    yy, xx = np.mgrid[0:S, 0:S]; weave = (np.sin(xx * np.pi * 2 / 3.0) * np.sin(yy * np.pi * 2 / 3.0)) * .5 + .5
    c = np.array(rgb, float) / 255; return np.clip(c[None, None] * (1 - amp + amp * weave[..., None]) * (.9 + .2 * noise[..., None]), 0, 1)
def sm(e0, e1, x): t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
hand = valid & (ha | (d < .0)) & (d < .02)          # palm + fingers (+ the wrist crease)
wrist = valid & ~ha & (d >= -.01)                    # forearm, measured from the wrist
def write(id_, col, rough):
    Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, id_ + '_c.jpg'), quality=90)
    r = np.zeros((S, S, 3), np.uint8); r[..., 1] = (np.clip(rough, 0, 1) * 255).astype(np.uint8); r[..., 0] = 255
    Image.fromarray(r).resize((512, 512)).save(os.path.join(OUT, id_ + '_r.jpg'), quality=90); print('written', id_)
def finger_tip_cut(level):   # fingerless glove: covers the hand and the fingers up to `level` (1 = first segment)
    return ha & ((~fi & ~th) | (fi & (lv <= level)) | (th & (lv <= level)))
# ---- bilge: tactical fingerless ------------------------------------------------------------------------------------
skin = tone((236, 205, 186)); col = skin.copy(); rough = np.full((S, S), .62)
cover = valid & (finger_tip_cut(1) | (~ha & (d < .055)))
cloth = fabric((34, 36, 38)); col = mix(col, cloth, cover); rough[cover] = .85
back = cover & ha & (s < -.004) & ~fi & ~th
knuck = back & (u > .092) & (u < .128); plates = knuck & (np.sin(w * 2 * np.pi / .021) > -.55)
col = mix(col, fabric((52, 54, 58), amp=.04) * (.8 + .4 * sm(.092, .128, u))[..., None], plates); rough[plates] = .38
pad = cover & fi & (lv == 1) & (s < -.003); col = mix(col, fabric((58, 60, 64), amp=.05), pad); rough[pad] = .45
strap = valid & ~ha & (d > .015) & (d < .045); col = mix(col, fabric((22, 23, 25), amp=.25), strap); rough[strap] = .9
logo = back & (u > .03) & (u < .06) & (np.abs(w) < .016); col = mix(col, fabric((70, 74, 80), amp=.08), logo)
write('bilge', col, rough)
# ---- ay (Aysel): black floral lace, fingerless, scalloped cuff --------------------------------------------------------
skin = tone((246, 226, 216)); col = skin.copy(); rough = np.full((S, S), .6)
ang = np.arctan2(s, w); cuff_edge = .095 + .006 * np.sin(ang * 9)
lace_area = valid & ((ha & ~fi & ~th) | (ha & th & (lv <= 1)) | (~ha & (d < cuff_edge)))
lace_area &= ~(ha & ~fi & ~th & (u > .1 + .004 * np.sin(w * 2 * np.pi / .02)))     # scallops at the knuckles
X, Y = (w + 2 * d) * 1.0, (u + 2 * d - s) * 1.0
net = (np.abs(np.sin(X * 2 * np.pi / .007)) < .16) | (np.abs(np.sin(Y * 2 * np.pi / .007)) < .16)
cx_, cy_ = np.mod(X, .034) - .017, np.mod(Y, .034) - .017; rr = np.hypot(cx_, cy_); th_ = np.arctan2(cy_, cx_)
petal = rr < .012 * (.5 + .5 * np.abs(np.cos(th_ * 2.5)))
flower = petal & ~(rr < .0028); ring = np.abs(rr - .0145) < .0011
thread = (flower | ring | net) & lace_area
col = mix(col, np.full_like(col, .05), thread * .92); col = mix(col, skin * .55, lace_area & ~thread)
border = valid & ~ha & (np.abs(d - cuff_edge) < .004); col = mix(col, np.full_like(col, .04), border); rough[lace_area] = .7
write('ay', col, rough)
# ---- zeynos: black leather gloves, heart cut-out on the back of the hand -------------------------------------------
skin = tone((253, 232, 222)); col = skin.copy(); rough = np.full((S, S), .6)
glove = valid & (ha | (~ha & (d < .06)))
hx = (w) / .032; hy = (u - .062) / .032
heart = ((hx ** 2 + (hy - .35 * np.sqrt(np.abs(hx))) ** 2 * 1.25) < .55) & (s < -.004) & ha & ~fi & ~th
leather = np.clip(np.array([24, 20, 22]) / 255 * (1.0 + .25 * noise[..., None]), 0, 1) * np.ones((S, S, 1))
col = mix(col, leather, glove & ~heart); rough[glove & ~heart] = .32
stitch = glove & ~ha & (np.abs(d - .052) < .0018) & (np.sin(np.arctan2(s, w) * 40) > 0); col = mix(col, np.full_like(col, [.75, .45, .55]), stitch)
heart_edge = ((hx ** 2 + (hy - .35 * np.sqrt(np.abs(hx))) ** 2 * 1.25) < .7) & ~heart & (s < -.004) & ha & ~fi & ~th
col = mix(col, np.full_like(col, [.55, .12, .25]), heart_edge)
snap = valid & ~ha & (np.hypot(d - .03, w - .0) < .006) & (s < 0); col = mix(col, np.full_like(col, .55), snap); rough[snap] = .2
write('zeynos', col, rough)
# ---- ates: bare hands, red cloth wrist wraps -----------------------------------------------------------------------
skin = tone((222, 170, 132)); col = skin.copy(); rough = np.full((S, S), .6)
wrap = valid & ~ha & (d > .0) & (d < .11 + .01 * np.sin(np.arctan2(s, w) * 3)); bands = np.sin((d + .006 * np.arctan2(s, w)) * 2 * np.pi / .018)
cloth = fabric((128, 22, 18), amp=.2) * (.75 + .25 * (bands > -.6))[..., None]; col = mix(col, cloth, wrap); rough[wrap] = .88
handwrap = valid & ha & ~fi & ~th & (u < .05); col = mix(col, cloth, handwrap); rough[handwrap] = .88
write('ates', col, rough)
# ---- kral: bare hands, dark leather bracers with studs ---------------------------------------------------------------
skin = tone((206, 158, 124)); col = skin.copy(); rough = np.full((S, S), .62)
brace = valid & ~ha & (d > .025) & (d < .19)
leather = np.clip(np.array([48, 32, 24]) / 255 * (.9 + .3 * noise[..., None]), 0, 1) * np.ones((S, S, 1)); col = mix(col, leather, brace); rough[brace] = .45
straps = brace & ((np.abs(d - .05) < .006) | (np.abs(d - .165) < .006)); col = mix(col, np.full_like(col, .07), straps)
stud = brace & (np.hypot(np.mod(d, .03) - .015, np.mod(np.arctan2(s, w) * .035, .03) - .015) < .0045) & (d > .07) & (d < .15)
col = mix(col, np.full_like(col, [.62, .55, .42]), stud); rough[stud] = .2
write('kral', col, rough)
# ---- hellgate (Zebani): charred skin, lava cracks ---------------------------------------------------------------------
yy, xx = np.mgrid[0:S, 0:S] / S
cr = np.abs(np.sin(xx * 37 + np.sin(yy * 23) * 2.1) * np.sin(yy * 41 + np.sin(xx * 19) * 1.7)); crack = valid & (cr < .045)
char = tone((70, 58, 56), .35); col = mix(char, np.full_like(char, [1, .45, .1]), crack * .9); rough = np.full((S, S), .8); rough[crack] = .4
write('hellgate', col, rough)
