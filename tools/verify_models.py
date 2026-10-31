"""Skin every shipped character GLB on the CPU through every animation clip and fail if any triangle edge
stretches beyond its rest length (the 'long triangles' artefact). Runs in CI before the APK is built.
usage: verify_models.py [models...]   (default: every models/*.glb)"""
import json, struct, sys, math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]; MODELS = ROOT / 'app/src/main/assets/models'
MAX_RATIO, MIN_ABS = 3.0, .20          # visible tearing: an edge grows past 3x its rest length and by more than 20 cm (in-game units)


def load(path):
    d = path.read_bytes(); jl = struct.unpack_from('<I', d, 12)[0]; g = json.loads(d[20:20 + jl]); b = d[28 + jl:]
    def acc(i):
        a = g['accessors'][i]; v = g['bufferViews'][a['bufferView']]; n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
        dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
        off = v.get('byteOffset', 0) + a.get('byteOffset', 0); cnt = a['count'] * n
        arr = np.frombuffer(b, dt, cnt, off).astype(np.float64 if dt == np.float32 else np.int64)
        if a.get('normalized') and dt == np.uint8: arr = arr / 255.0
        return arr.reshape(a['count'], n) if n > 1 else arr
    return g, acc


def quat_mat(q):
    x, y, z, w = q; return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def local(n, ov=None):
    ov = ov or {}; M = np.eye(4)
    t = ov.get('translation', n.get('translation', [0, 0, 0])); r = ov.get('rotation', n.get('rotation', [0, 0, 0, 1])); s = n.get('scale', [1, 1, 1])
    M[:3, :3] = quat_mat(r) * np.array(s); M[:3, 3] = t; return M


PER = {}
def check(path):
    PER.clear(); g, acc = load(path); nodes = g['nodes']; parent = {c: i for i, n in enumerate(nodes) for c in n.get('children', [])}
    skin = g['skins'][0]; joints = skin['joints']; ibm = acc(skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
    worst = (0, 0, '', 0)
    for mi, n in enumerate(nodes):
        if 'mesh' not in n or 'skin' not in n: continue
        for prim in g['meshes'][n['mesh']]['primitives']:
            P = acc(prim['attributes']['POSITION']); J = acc(prim['attributes']['JOINTS_0']); W = acc(prim['attributes']['WEIGHTS_0'])
            T = acc(prim['indices']).reshape(-1, 3)
            E = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1), axis=0)
            Ph = np.c_[P, np.ones(len(P))]
            def skinned(ov):
                world = {}
                def wm(i):
                    if i in world: return world[i]
                    m = local(nodes[i], ov.get(i)); p = parent.get(i); world[i] = m if p is None else wm(p) @ m; return world[i]
                S = np.stack([wm(j) @ ibm[k] for k, j in enumerate(joints)])
                out = np.zeros((len(P), 3))
                for c in range(4): out += W[:, c, None] * np.einsum('nij,nj->ni', S[J[:, c]], Ph)[:, :3]
                return out
            R = skinned({}); L0 = np.linalg.norm(R[E[:, 0]] - R[E[:, 1]], axis=1)
            mname = nodes[mi].get('name', '')
            for an in g.get('animations', []):
                if mname.startswith('Body_human') and an['name'] != 'HumanIdle': continue   # the human body is only seen idling; first-person poses show the arms mesh
                ch = an['channels']; sm = an['samplers']; tin = acc(sm[0]['input']).ravel()
                for f in range(0, len(tin), 2):
                    ov = {}
                    for c in ch:
                        v = acc(sm[c['sampler']]['output']); ov.setdefault(c['target']['node'], {})[c['target']['path']] = list(v[min(f, len(v) - 1)])
                    Q = skinned(ov); L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1)
                    bad = (L > L0 * MAX_RATIO) & (L - L0 > MIN_ABS)
                    if bad.any():
                        k = int(np.argmax(np.where(bad, L - L0, 0)))
                        if L[k] - L0[k] > worst[0]: worst = (float(L[k] - L0[k]), int(bad.sum()), an['name'], f)
                        PER[an['name']] = max(PER.get(an['name'], 0), float(L[k] - L0[k]))
    return worst


if __name__ == '__main__':
    files = [Path(a) for a in sys.argv[1:]] or sorted(MODELS.glob('*.glb'))
    failed = []
    sys.path.insert(0, str(ROOT / 'tools' / 'meshy'))
    SRC = ROOT / 'art/3d/meshy/source'; MAX_HOLE = .03   # m^2: an open loop larger than this is a see-through hole
    for f in files:
        src = SRC / f.name.replace('_meshy', '')
        if src.exists():
            from holes import new_holes
            n_open, areas = new_holes(str(f), str(src))
            if areas and areas[0] > MAX_HOLE:
                print(f'FAIL {f.name}  new hole in the surface: {areas[0] * 1e4:.0f} cm2 (limit {MAX_HOLE * 1e4:.0f})'); failed.append(f.name); continue
        g_, acc_ = load(f); names_ = [g_['nodes'][j].get('name', '') for j in g_['skins'][0]['joints']]; bad_fp = False
        for n_ in g_['nodes']:   # first-person arms may only follow the arm chain (torso influence smears them across the screen)
            if 'mesh' in n_ and n_.get('name', '').startswith('FPArms'):
                pr_ = g_['meshes'][n_['mesh']]['primitives'][0]; J_ = acc_(pr_['attributes']['JOINTS_0']).astype(int); W_ = acc_(pr_['attributes']['WEIGHTS_0'])
                used = np.unique(acc_(pr_['indices']).astype(int)); off = {names_[j] for j in np.unique(J_[used][W_[used] > 1e-4]) if not names_[j].startswith(('Clav', 'UpperArm', 'Forearm', 'Hand', 'Fingers'))}
                if off: print(f'FAIL {f.name}  first-person arms follow non-arm bones: {sorted(off)}'); bad_fp = True
                # and every first-person vertex must hug an arm bone (no coat flaps / hair floating in front of the camera)
                from glbio import GLB as _G, world_with as _ww
                _g = _G(str(f)); _W = _ww(_g, {}); _nm = {n.get('name'): i for i, n in enumerate(_g.j['nodes'])}
                _P = acc_(pr_['attributes']['POSITION'])[used]; _bm = next(m for m in g_['nodes'] if 'mesh' in m and m.get('name', '').startswith('Body')); _h = np.ptp(acc_(g_['meshes'][_bm['mesh']]['primitives'][0]['attributes']['POSITION'])[:, 1])   # body height
                _d = np.full(len(_P), 1e9)
                for sd in 'LR':
                    pts = [_W[_nm[b + sd]][:3, 3] for b in ('Clav', 'UpperArm', 'Forearm', 'Hand')]; pts.append(pts[-1] + (pts[-1] - pts[-2]) * .75)
                    for a, c in zip(pts[:-1], pts[1:]):
                        v = c - a; t = np.clip(((_P - a) @ v) / (v @ v + 1e-12), 0, 1); _d = np.minimum(_d, np.linalg.norm(_P - (a + t[:, None] * v), axis=1))
                if _d.max() > .14 * _h / 1.78: print(f'FAIL {f.name}  first-person arm vertex {_d.max():.2f} m away from the arm bones'); bad_fp = True
        if bad_fp: failed.append(f.name); continue
        w = check(f); ok = w[1] == 0
        print(('OK   ' if ok else 'FAIL ') + f.name + ('' if ok else f'  {w[1]} stretched edges, worst +{w[0]:.2f} m in {w[2]} frame {w[3]}; clips: ' + ', '.join(f'{k} +{v:.2f}' for k, v in PER.items())))
        if not ok: failed.append(f.name)
    if failed: raise SystemExit('model checks failed (stretched triangles or holes): ' + ', '.join(failed))
    print('PASS: no stretched triangles in any clip')
