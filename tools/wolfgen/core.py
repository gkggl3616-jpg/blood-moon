"""Original procedural character toolkit: skeleton, skinned mesh builders, glTF writer,
forward-kinematics posing and a tiny numpy preview rasteriser.  No third-party game data."""
import json, math, struct
import numpy as np


# ----------------------------------------------------------------------------- math
def normalize(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-9)


def quat_from_euler(rx, ry, rz):
    """Degrees, intrinsic XYZ -> (x,y,z,w)."""
    rx, ry, rz = [math.radians(a) * .5 for a in (rx, ry, rz)]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return np.array([sx * cy * cz + cx * sy * sz, cx * sy * cz - sx * cy * sz,
                     cx * cy * sz + sx * sy * cz, cx * cy * cz - sx * sy * sz])


def quat_to_mat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def slerp(a, b, t):
    d = float(np.dot(a, b))
    if d < 0: b = -b; d = -d
    if d > .9995:
        r = a + t * (b - a); return r / np.linalg.norm(r)
    th = math.acos(d); return (math.sin((1 - t) * th) * a + math.sin(t * th) * b) / math.sin(th)


def hash_noise(p, scale=1.0, seed=0):
    p = np.asarray(p, float) * scale
    i = np.floor(p); f = p - i; f = f * f * (3 - 2 * f)

    def h(ix, iy, iz):
        n = (ix * 127.1 + iy * 311.7 + iz * 74.7 + seed * 19.19)
        return (np.sin(n) * 43758.5453) % 1.0
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * h(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz)
    return out


# ----------------------------------------------------------------------------- skeleton
class Skeleton:
    def __init__(self):
        self.names, self.parent, self.pos = [], [], []

    def add(self, name, parent, pos):
        self.names.append(name); self.parent.append(None if parent is None else self.names.index(parent))
        self.pos.append(np.array(pos, float)); return len(self.names) - 1

    def idx(self, name): return self.names.index(name)

    def local_offset(self, i):
        p = self.parent[i]
        return self.pos[i] if p is None else self.pos[i] - self.pos[p]

    def fk(self, pose, root_t=(0, 0, 0)):
        """pose: {bone: (rx,ry,rz) degrees}. returns world 4x4 per bone."""
        mats = []
        for i, n in enumerate(self.names):
            M = np.eye(4)
            M[:3, :3] = quat_to_mat(quat_from_euler(*pose.get(n, (0, 0, 0))))
            M[:3, 3] = self.local_offset(i) + (np.array(root_t) if self.parent[i] is None else 0)
            mats.append(M if self.parent[i] is None else mats[self.parent[i]] @ M)
        return mats

    def joint_world(self, pose, root_t=(0, 0, 0)):
        return {n: m[:3, 3] for n, m in zip(self.names, self.fk(pose, root_t))}


# ----------------------------------------------------------------------------- mesh
class Mesh:
    def __init__(self, skel):
        self.skel = skel
        self.P, self.N, self.C, self.J, self.W, self.M, self.tris = [], [], [], [], [], [], []
        self.materials = {}   # name -> dict(color, emissive, roughness, metallic)

    def material(self, name, color=(1, 1, 1), emissive=(0, 0, 0), roughness=.8, metallic=0, emissive_strength=1.0, double=False):
        self.materials[name] = dict(color=list(color), emissive=list(emissive), roughness=roughness, metallic=metallic, double=double)
        return name

    def _weights(self, wd):
        items = sorted(wd.items(), key=lambda kv: -kv[1])[:4]
        tot = sum(w for _, w in items) or 1.0
        j = [self.skel.idx(b) for b, _ in items] + [0] * (4 - len(items))
        w = [x / tot for _, x in items] + [0.0] * (4 - len(items))
        return j, w

    def add_part(self, P, tris, weight_fn, color_fn, material, smooth=True):
        P = np.asarray(P, float); tris = np.asarray(tris, int)
        base = len(self.P)
        N = np.zeros_like(P)
        fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
        for k in range(3): np.add.at(N, tris[:, k], fn)
        N = normalize(N)
        for i, p in enumerate(P):
            wd = weight_fn(i, p) if callable(weight_fn) else weight_fn
            j, w = self._weights(wd)
            self.P.append(p); self.N.append(N[i]); self.J.append(j); self.W.append(w)
            col = color_fn(p, N[i]) if callable(color_fn) else color_fn
            self.C.append(list(col)[:3] + [1.0]); self.M.append(material)
        for t in tris: self.tris.append((t + base).tolist() + [material])
        return base

    # --- primitives -----------------------------------------------------------
    def tube(self, path, radii, weight_fn, color_fn, material, sides=10, cap_start=True, cap_end=True, ref=(1, 0, 0), twist=0.0, jitter=None, shift=None):
        path = np.asarray(path, float); n = len(path)
        radii = [r if isinstance(r, (tuple, list)) else (r, r) for r in radii]
        verts = []; ref = np.asarray(ref, float)
        for i in range(n):
            T = normalize(path[min(i + 1, n - 1)] - path[max(i - 1, 0)])
            u = ref - T * np.dot(ref, T)
            if np.linalg.norm(u) < 1e-4: u = np.array([0, 0, 1.0]) - T * T[2]
            u = normalize(u); v = np.cross(T, u)
            ru, rv = radii[i]
            for s in range(sides):
                a = 2 * math.pi * s / sides + twist
                k = 1.0 if jitter is None else jitter(i, s)
                off = T * shift(i, s) if shift is not None else 0
                verts.append(path[i] + off + (u * math.cos(a) * ru + v * math.sin(a) * rv) * k)
        tris = []
        for i in range(n - 1):
            for s in range(sides):
                a, b = i * sides + s, i * sides + (s + 1) % sides
                c, d = (i + 1) * sides + s, (i + 1) * sides + (s + 1) % sides
                tris += [(a, c, b), (b, c, d)]
        if cap_start or cap_end:
            if cap_start:
                verts.append(path[0]); ci = len(verts) - 1
                tris += [(ci, (s + 1) % sides, s) for s in range(sides)]
            if cap_end:
                verts.append(path[-1]); ci = len(verts) - 1
                o = (n - 1) * sides
                tris += [(ci, o + s, o + (s + 1) % sides) for s in range(sides)]
        # orientation fix: make triangles face outward
        V = np.array(verts); tris = np.array(tris)
        cen = V.mean(0)
        fnrm = np.cross(V[tris[:, 1]] - V[tris[:, 0]], V[tris[:, 2]] - V[tris[:, 0]])
        mid = V[tris].mean(1)
        # tube centreline based test is more robust than global centre
        flip = 0
        sample = tris[len(tris) // 3]
        nn = np.cross(V[sample[1]] - V[sample[0]], V[sample[2]] - V[sample[0]])
        ctr = path[min(len(path) - 1, int(sample[0] // sides))]
        if np.dot(nn, V[sample].mean(0) - ctr) < 0: tris = tris[:, ::-1]
        return self.add_part(V, tris, weight_fn, color_fn, material)

    def ellipsoid(self, c, r, weight_fn, color_fn, material, rot=None, seg=14, rings=10):
        verts = []
        for i in range(rings + 1):
            th = math.pi * i / rings
            for j in range(seg):
                ph = 2 * math.pi * j / seg
                verts.append([math.sin(th) * math.cos(ph) * r[0], math.cos(th) * r[1], math.sin(th) * math.sin(ph) * r[2]])
        V = np.array(verts)
        if rot is not None: V = V @ quat_to_mat(quat_from_euler(*rot)).T
        V = V + np.asarray(c, float)
        tris = []
        for i in range(rings):
            for j in range(seg):
                a, b = i * seg + j, i * seg + (j + 1) % seg
                c2, d = (i + 1) * seg + j, (i + 1) * seg + (j + 1) % seg
                tris += [(a, b, c2), (b, d, c2)]
        tris = np.array(tris)
        n = np.cross(V[tris[:, 1]] - V[tris[:, 0]], V[tris[:, 2]] - V[tris[:, 0]])
        if np.mean(np.einsum('ij,ij->i', n, V[tris].mean(1) - np.asarray(c, float))) < 0: tris = tris[:, ::-1]
        return self.add_part(V, tris, weight_fn, color_fn, material)

    def cone(self, base, tip, radius, weight_fn, color_fn, material, sides=6, curve=None):
        base, tip = np.asarray(base, float), np.asarray(tip, float)
        pts = [base, base + (tip - base) * .5 + (np.asarray(curve, float) if curve is not None else 0), tip]
        return self.tube(pts, [radius, radius * .55, 0.0], weight_fn, color_fn, material, sides=sides, cap_start=True, cap_end=False)

    def crystal(self, c, axis, length, width, weight_fn, color_fn, material, sides=6, flat=1.0):
        """Faceted pointed crystal / blade: bipyramid-ish prism along axis."""
        axis = normalize(axis); c = np.asarray(c, float)
        ref = np.array([0, 1.0, 0]) if abs(axis[1]) < .9 else np.array([1.0, 0, 0])
        u = normalize(ref - axis * np.dot(ref, axis)); v = np.cross(axis, u)
        verts = [c - axis * length * .25]
        ring_t = [(.0, .75), (.35, 1.0), (.7, .62)]
        for t, w in ring_t:
            for s in range(sides):
                a = 2 * math.pi * s / sides
                verts.append(c + axis * (t * length - length * .25) + (u * math.cos(a) * width * w + v * math.sin(a) * width * w * flat))
        verts.append(c + axis * length * .75)
        tris = []
        for s in range(sides): tris.append((0, 1 + (s + 1) % sides, 1 + s))
        for r in range(2):
            for s in range(sides):
                a, b = 1 + r * sides + s, 1 + r * sides + (s + 1) % sides
                c2, d = 1 + (r + 1) * sides + s, 1 + (r + 1) * sides + (s + 1) % sides
                tris += [(a, b, c2), (b, d, c2)]
        top = len(verts) - 1
        for s in range(sides): tris.append((top, 1 + 2 * sides + s, 1 + 2 * sides + (s + 1) % sides))
        V = np.array(verts); tris = np.array(tris)
        n = np.cross(V[tris[:, 1]] - V[tris[:, 0]], V[tris[:, 2]] - V[tris[:, 0]])
        if np.mean(np.einsum('ij,ij->i', n, V[tris].mean(1) - c)) < 0: tris = tris[:, ::-1]
        return self.add_part(V, tris, weight_fn, color_fn, material)

    def sheet(self, grid, weight_fn, color_fn, material):
        """grid: (rows, cols, 3) surface, rendered double-sided by material."""
        grid = np.asarray(grid, float); R, C = grid.shape[:2]
        V = grid.reshape(-1, 3); tris = []
        for i in range(R - 1):
            for j in range(C - 1):
                a, b, c, d = i * C + j, i * C + j + 1, (i + 1) * C + j, (i + 1) * C + j + 1
                tris += [(a, c, b), (b, c, d)]
        return self.add_part(V, np.array(tris), weight_fn, color_fn, material)

    # --- export ---------------------------------------------------------------
    def arrays(self):
        return (np.array(self.P, np.float32), np.array(self.N, np.float32), np.array(self.C, np.float32),
                np.array(self.J, np.uint16), np.array(self.W, np.float32))


def blend(a, b, t):
    t = np.clip(t, 0, 1); return tuple(np.array(a) * (1 - t) + np.array(b) * t)


def chain_weights(skel_bones):
    """skel_bones: list of (bone, y_or_param_center). returns fn(param)->weights using smooth blend."""
    def fn(param):
        ws = {}
        for k in range(len(skel_bones) - 1):
            (b0, p0), (b1, p1) = skel_bones[k], skel_bones[k + 1]
            if (p0 <= param <= p1) or (p1 <= param <= p0):
                t = (param - p0) / (p1 - p0 + 1e-9); t = t * t * (3 - 2 * t)
                ws[b0] = ws.get(b0, 0) + 1 - t; ws[b1] = ws.get(b1, 0) + t
        if not ws: ws[skel_bones[0][0] if param < skel_bones[0][1] else skel_bones[-1][0]] = 1.0
        return ws
    return fn


# ----------------------------------------------------------------------------- glTF
def _pad(b, ch=b'\0'):
    return b + ch * ((4 - len(b) % 4) % 4)


def write_glb(path, skel, mesh, clips, node_name, extras=None, scene_extras=None, fps=30):
    """clips: {name: dict(duration, frames=[(pose dict, root_t)])}"""
    bin_chunks, views, accessors = [], [], []

    def add(arr, target=None, ctype=5126, typ='SCALAR', minmax=False):
        arr = np.ascontiguousarray(arr)
        data = arr.tobytes(); off = sum(len(_pad(c)) for c in bin_chunks)
        bin_chunks.append(data)
        views.append(dict(buffer=0, byteOffset=off, byteLength=len(data), **({'target': target} if target else {})))
        acc = dict(bufferView=len(views) - 1, componentType=ctype, count=int(arr.shape[0]), type=typ)
        if minmax: acc['min'] = arr.min(0).tolist() if arr.ndim > 1 else [float(arr.min())]; acc['max'] = arr.max(0).tolist() if arr.ndim > 1 else [float(arr.max())]
        accessors.append(acc); return len(accessors) - 1

    P, N, C, J, W = mesh.arrays()
    a_pos = add(P, 34962, 5126, 'VEC3', True); a_nrm = add(N, 34962, 5126, 'VEC3')
    a_col = add(C, 34962, 5126, 'VEC4'); a_j = add(J, 34962, 5123, 'VEC4'); a_w = add(W, 34962, 5126, 'VEC4')
    mats = list(mesh.materials.keys())
    prims = []
    for mi, mname in enumerate(mats):
        idx = np.array([t[:3] for t in mesh.tris if t[3] == mname], np.uint32).reshape(-1)
        if len(idx) == 0: continue
        prims.append(dict(attributes=dict(POSITION=a_pos, NORMAL=a_nrm, COLOR_0=a_col, JOINTS_0=a_j, WEIGHTS_0=a_w),
                          indices=add(idx, 34963, 5125, 'SCALAR'), material=mi, mode=4))
    ibm = []
    for i in range(len(skel.names)):
        M = np.eye(4); M[:3, 3] = -skel.pos[i]; ibm.append(M.T.reshape(-1))
    a_ibm = add(np.array(ibm, np.float32), None, 5126, 'MAT4')

    nodes = [dict(name='Armature', children=[])]
    jn = {}
    for i, n in enumerate(skel.names):
        nodes.append(dict(name=n, translation=skel.local_offset(i).tolist(), rotation=[0, 0, 0, 1]))
        jn[i] = len(nodes) - 1
    for i, p in enumerate(skel.parent):
        parent_node = 0 if p is None else jn[p]
        nodes[parent_node].setdefault('children', []).append(jn[i])
    mesh_node = dict(name=node_name, mesh=0, skin=0)
    if extras: mesh_node['extras'] = extras
    nodes.append(mesh_node); mesh_idx = len(nodes) - 1

    animations = []
    for cname, clip in clips.items():
        frames = clip['frames']; n = len(frames); times = np.arange(n, dtype=np.float32) / (fps)
        samplers, channels = [], []
        t_acc = add(times, None, 5126, 'SCALAR', True)
        for i, bname in enumerate(skel.names):
            rq = np.array([quat_from_euler(*fr[0].get(bname, (0, 0, 0))) for fr in frames], np.float32)
            # keep quaternion continuity
            for k in range(1, n):
                if np.dot(rq[k], rq[k - 1]) < 0: rq[k] = -rq[k]
            if np.abs(rq - np.array([0, 0, 0, 1], np.float32)).max() > 1e-6:
                samplers.append(dict(input=t_acc, output=add(rq, None, 5126, 'VEC4'), interpolation='LINEAR'))
                channels.append(dict(sampler=len(samplers) - 1, target=dict(node=jn[i], path='rotation')))
        # root translation on Hips
        hips = skel.idx('Hips')
        tr = np.array([skel.local_offset(hips) + np.array(fr[1]) for fr in frames], np.float32)
        samplers.append(dict(input=t_acc, output=add(tr, None, 5126, 'VEC3'), interpolation='LINEAR'))
        channels.append(dict(sampler=len(samplers) - 1, target=dict(node=jn[hips], path='translation')))
        animations.append(dict(name=cname, samplers=samplers, channels=channels))

    gl_mats = []
    for m in mats:
        d = mesh.materials[m]
        gl_mats.append(dict(name=m, pbrMetallicRoughness=dict(baseColorFactor=d['color'] + [1.0], metallicFactor=d['metallic'], roughnessFactor=d['roughness']),
                            emissiveFactor=d['emissive'], doubleSided=bool(d['double'])))
    gltf = dict(asset=dict(version='2.0', generator='bloodmoon-wolfgen (original)'),
                scene=0, scenes=[dict(nodes=[0, mesh_idx], **({'extras': scene_extras} if scene_extras else {}))],
                nodes=nodes, meshes=[dict(name=node_name, primitives=prims)],
                skins=[dict(inverseBindMatrices=a_ibm, joints=[jn[i] for i in range(len(skel.names))], skeleton=0)],
                materials=gl_mats, animations=animations, accessors=accessors, bufferViews=views,
                buffers=[dict(byteLength=sum(len(_pad(c)) for c in bin_chunks))])
    jsb = _pad(json.dumps(gltf, separators=(',', ':')).encode(), b' ')
    binb = b''.join(_pad(c) for c in bin_chunks)
    with open(path, 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(jsb) + 8 + len(binb)))
        f.write(struct.pack('<I4s', len(jsb), b'JSON')); f.write(jsb)
        f.write(struct.pack('<I4s', len(binb), b'BIN\0')); f.write(binb)


# ----------------------------------------------------------------------------- preview renderer
def skin_vertices(skel, mesh, pose, root_t=(0, 0, 0)):
    P, N, C, J, W = mesh.arrays()
    mats = skel.fk(pose, root_t)
    skin = []
    for i in range(len(skel.names)):
        B = np.eye(4); B[:3, 3] = -skel.pos[i]; skin.append(mats[i] @ B)
    skin = np.array(skin)
    Ph = np.concatenate([P, np.ones((len(P), 1), np.float32)], 1)
    out = np.zeros((len(P), 3)); outn = np.zeros((len(P), 3))
    for k in range(4):
        M = skin[J[:, k]]
        out += W[:, k:k + 1] * np.einsum('nij,nj->ni', M, Ph)[:, :3]
        outn += W[:, k:k + 1] * np.einsum('nij,nj->ni', M[:, :3, :3], N)
    return out, normalize(outn)


def render(skel, mesh, pose, root_t=(0, 0, 0), yaw=30, pitch=8, size=(700, 800), center=None, dist=None, scale=None,
           glow=0.0, bg=(30, 34, 42), ground=True, ss=2):
    from PIL import Image
    V, Nn = skin_vertices(skel, mesh, pose, root_t)
    W_, H_ = size[0] * ss, size[1] * ss
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]); Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    R = Rx @ Ry
    c = V.mean(0) if center is None else np.asarray(center)
    Vc = (V - c) @ R.T; Nc = Nn @ R.T
    ext = np.abs(Vc[:, :2]).max() if scale is None else scale
    s = min(W_, H_) * .46 / ext
    X = Vc[:, 0] * s + W_ / 2; Y = -Vc[:, 1] * s + H_ / 2; Z = Vc[:, 2]
    img = np.zeros((H_, W_, 3), np.float32); img[:] = np.array(bg, np.float32)
    zb = np.full((H_, W_), 1e9, np.float32)
    L = normalize(np.array([-.5, .8, .6])); L2 = normalize(np.array([.6, .2, -.5]))
    cols = np.array(mesh.C)[:, :3]
    for t in mesh.tris:
        a, b, c3 = t[0], t[1], t[2]
        mat = mesh.materials[t[3]]
        x0, x1, x2 = X[a], X[b], X[c3]; y0, y1, y2 = Y[a], Y[b], Y[c3]
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-6: continue
        if area > 0 and not mat['double']: continue   # back-face (screen y is flipped)
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2)) + 1, W_ - 1)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2)) + 1, H_ - 1)
        if minx > maxx or miny > maxy: continue
        gx, gy = np.meshgrid(np.arange(minx, maxx + 1) + .5, np.arange(miny, maxy + 1) + .5)
        w0 = ((x1 - gx) * (y2 - gy) - (x2 - gx) * (y1 - gy)) / area
        w1 = ((x2 - gx) * (y0 - gy) - (x0 - gx) * (y2 - gy)) / area
        w2 = 1 - w0 - w1
        m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not m.any(): continue
        z = w0 * Z[a] + w1 * Z[b] + w2 * Z[c3]
        sub = zb[miny:maxy + 1, minx:maxx + 1]
        m &= z < sub
        if not m.any(): continue
        nrm = (w0[..., None] * Nc[a] + w1[..., None] * Nc[b] + w2[..., None] * Nc[c3]); nrm = nrm / np.maximum(np.linalg.norm(nrm, axis=-1, keepdims=True), 1e-6)
        if mat['double']: nrm = np.where((nrm[..., 2:3] < 0), -nrm, nrm)
        lum = np.clip(nrm @ (R @ L) * .8 + .28, 0, 1.2)[..., None] + np.clip(nrm @ (R @ L2), 0, 1)[..., None] * .22
        base = (w0[..., None] * cols[a] + w1[..., None] * cols[b] + w2[..., None] * cols[c3]) * np.array(mat['color'])
        em = np.array(mat['emissive']) * (1 + glow * 1.5)
        rgb = base * lum + em * .9
        sub[m] = z[m]
        img[miny:maxy + 1, minx:maxx + 1][m] = (np.clip(rgb[m], 0, 1) * 255)
    im = Image.fromarray(img.astype(np.uint8))
    return im.resize(size, Image.LANCZOS) if ss > 1 else im
