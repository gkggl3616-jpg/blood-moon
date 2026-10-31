"""Build the game weapon models from the generated sources + art/3d/weapons/sockets.json.

usage: python3 tools/weapons/build_weapons.py [source_dir]   (default art/3d/weapons/src)

Every output (app/src/main/assets/models/weapons/<kind>.glb) is in the first-person weapon frame:
  metres, +Y up, barrel along -Z (muzzle forward), origin = palm centre of the shooting hand on the grip (grip_r).
The magazine (or pistol floor plate) is split into its own mesh "Mag" so the reload can drop it. The root node carries
the sockets in extras: grip_r, grip_l, trigger, sight, muzzle, ring, grip_dir, palm_l (support-hand palm direction).
Budgets (docs/uretim-standardi.md): guns <= 35000 triangles, grenades <= 10000. Textures: guns base colour 2K, normal and
metal/rough 1K; knife and grenades 1K."""
import sys, os, io, json, struct, numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'meshy')); from glbio import GLB
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'art/3d/weapons/src')
OUT = os.path.join(ROOT, 'app/src/main/assets/models/weapons')
SOCK = json.load(open(os.path.join(ROOT, 'art/3d/weapons/sockets.json')))
KIND = {'ar01': 'rifle', 'sr01': 'sniper', 'p01': 'pistol', 'kama01': 'knife', 'frag': 'frag', 'smoke': 'smoke'}
BUDGET = {'frag': 10000, 'smoke': 10000}
# support-hand palm direction in the weapon frame: vertical foregrip -> palm faces the gun (+X); handguard -> palm up
PALM_L = {'ar01': [1, .15, 0], 'sr01': [.2, 1, .1], 'p01': [.6, .8, 0], 'kama01': [.2, 1, .1], 'frag': [.2, 1, .1], 'smoke': [.2, 1, .1]}
MAG_BOX = {'p01': [[-0.08, -0.345, 0.15], [0.08, -0.29, 0.42]]}   # pistol: only the floor plate shows below the grip

def frame(spec):
    """source -> weapon frame rotation (3x3) and scale."""
    if spec['axis'] == 'z':   # Tripo guns: long axis Z, muzzle at -Z, +Y up already
        R = np.eye(3)
    else:                     # grenades: long axis X with the fuse/ring at +X -> stand the grenade up (fuse +Y)
        R = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1.]])
    return R

def tex(raw, size, normal=False):
    im = Image.open(io.BytesIO(raw)); im = im.convert('RGB')
    if max(im.size) > size: im = im.resize((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=92 if normal else 88); return b.getvalue()

def write(path, parts, mat, images, extras):
    bufs = bytearray(); views = []; accs = []
    def blob(b, target=None):
        while len(bufs) % 4: bufs.append(0)
        views.append(dict(buffer=0, byteOffset=len(bufs), byteLength=len(b), **({'target': target} if target else {}))); bufs.extend(b); return len(views) - 1
    def acc(a, typ, ct, target, mm=False):
        a = np.ascontiguousarray(a); d = dict(bufferView=blob(a.tobytes(), target), componentType=ct, count=len(a), type=typ)
        if mm: d.update(min=a.min(0).tolist(), max=a.max(0).tolist())
        accs.append(d); return len(accs) - 1
    j = dict(asset=dict(version='2.0', generator='rbm weapons'), scene=0, scenes=[dict(nodes=[0])],
             nodes=[dict(name='Weapon', children=[], extras=extras)], meshes=[], materials=[mat], textures=[], images=[], samplers=[dict(magFilter=9729, minFilter=9987, wrapS=10497, wrapT=10497)])
    for raw in images:
        j['images'].append(dict(bufferView=blob(raw), mimeType='image/jpeg')); j['textures'].append(dict(source=len(j['images']) - 1, sampler=0))
    for name, P, N, UV, I, t in parts:
        attrs = dict(POSITION=acc(P.astype(np.float32), 'VEC3', 5126, 34962, True), NORMAL=acc(N.astype(np.float32), 'VEC3', 5126, 34962), TEXCOORD_0=acc(UV.astype(np.float32), 'VEC2', 5126, 34962))
        j['meshes'].append(dict(name=name, primitives=[dict(attributes=attrs, indices=acc(I.reshape(-1).astype(np.uint32), 'SCALAR', 5125, 34963), material=0)]))
        j['nodes'].append(dict(name=name, mesh=len(j['meshes']) - 1, translation=[float(x) for x in t])); j['nodes'][0]['children'].append(len(j['nodes']) - 1)
    while len(bufs) % 4: bufs.append(0)
    j['buffers'] = [dict(byteLength=len(bufs))]; j['bufferViews'] = views; j['accessors'] = accs
    jb = json.dumps(j, separators=(',', ':')).encode(); jb += b' ' * ((4 - len(jb) % 4) % 4)
    open(path, 'wb').write(struct.pack('<4sII', b'glTF', 2, 28 + len(jb) + len(bufs)) + struct.pack('<I4s', len(jb), b'JSON') + jb + struct.pack('<I4s', len(bufs), b'BIN\0') + bytes(bufs))

def build(name):
    spec = SOCK[name]; g = GLB(os.path.join(SRC, spec['src'])); Wm, _ = g.node_world()
    ni = next(i for i, n in enumerate(g.j['nodes']) if 'mesh' in n); pr = g.j['meshes'][g.j['nodes'][ni]['mesh']]['primitives'][0]
    A = pr['attributes']; P = g.acc(A['POSITION']).astype(float); P = (np.c_[P, np.ones(len(P))] @ Wm[ni].T)[:, :3]
    N = g.acc(A['NORMAL']).astype(float) @ Wm[ni][:3, :3].T; N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    UV = g.acc(A['TEXCOORD_0']); I = g.acc(pr['indices']).reshape(-1, 3).astype(np.int64)
    ext = P.max(0) - P.min(0); ax = 'xyz'.index(spec['axis']); s = spec['length_m'] / ext[ax]
    R = frame(spec); o = np.array(spec['grip_r'], float)
    tf = lambda x: ((np.asarray(x, float) - o) @ R.T) * s
    Pw = tf(P); Nw = N @ R.T
    box = MAG_BOX.get(name, spec.get('mag'))
    parts = []
    if box:
        lo, hi = np.array(box[0]), np.array(box[1]); inb = ((P >= lo) & (P <= hi)).all(1); mt = inb[I].all(1)
        groups = [('Body', I[~mt]), ('Mag', I[mt])]
    else:
        groups = [('Body', I)]
    for nm, T in groups:
        used = np.unique(T); remap = -np.ones(len(P), np.int64); remap[used] = np.arange(len(used))
        c = Pw[used].mean(0) if nm == 'Mag' else np.zeros(3)
        parts.append((nm, Pw[used] - c, Nw[used], UV[used], remap[T], c))
    tris = len(I); lim = BUDGET.get(name, 35000)
    assert tris <= lim, (name, tris, lim)
    mat = g.j['materials'][pr['material']]; pbr = mat.get('pbrMetallicRoughness', {})
    gun = spec['axis'] == 'z' and name != 'kama01'
    raw = lambda k: g.view_bytes(g.j['images'][g.j['textures'][k]['source']]['bufferView'])
    images = [tex(raw(pbr['baseColorTexture']['index']), 2048 if gun else 1024)]
    m2 = dict(name=name, pbrMetallicRoughness=dict(baseColorTexture=dict(index=0), metallicFactor=1.0, roughnessFactor=1.0))
    if 'metallicRoughnessTexture' in pbr:
        images.append(tex(raw(pbr['metallicRoughnessTexture']['index']), 1024)); m2['pbrMetallicRoughness']['metallicRoughnessTexture'] = dict(index=len(images) - 1)
    if 'normalTexture' in mat:
        images.append(tex(raw(mat['normalTexture']['index']), 1024, True)); m2['normalTexture'] = dict(index=len(images) - 1)
    def pt(k): return [round(float(v), 5) for v in tf(spec[k])] if k in spec else None
    gd = np.asarray(spec['grip_dir'], float) @ R.T; gd /= np.linalg.norm(gd)
    pl = np.asarray(PALM_L[name], float) @ R.T if spec['axis'] == 'z' else np.asarray(PALM_L[name], float)
    extras = dict(kind=KIND[name], source=spec['src'], length_m=spec['length_m'], triangles=int(tris),
                  sockets=dict(grip_r=[0, 0, 0], grip_l=pt('grip_l'), trigger=pt('trigger'), sight=pt('sight'), muzzle=pt('muzzle_pt'), ring=pt('ring'),
                               grip_dir=[round(float(v), 4) for v in gd], palm_l=[round(float(v), 4) for v in pl / np.linalg.norm(pl)]))
    os.makedirs(OUT, exist_ok=True); path = os.path.join(OUT, KIND[name] + '.glb'); write(path, parts, m2, images, extras)
    print('%-7s -> %-14s %6d tris  mag %s  %.0f KB  scale %.4f' % (name, KIND[name] + '.glb', tris, len(parts) > 1 and len(parts[1][4]), os.path.getsize(path) / 1024, s))
    return extras

if __name__ == '__main__':
    for n in [k for k in SOCK if not k.startswith('_')]: build(n)
