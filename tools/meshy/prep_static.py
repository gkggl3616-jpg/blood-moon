"""Export each game character as a static, textured A-pose GLB for Meshy auto-rigging.
Arms are swung 45 degrees outward with the existing skin weights so pose estimation sees a clear A-pose."""
import sys, os, json, struct, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB
def rotz(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])
def apose(path, ang=0.0):
    g = GLB(path); W, par = g.node_world(); N = g.j['nodes']; nm = {n.get('name'): i for i, n in enumerate(N)}
    body = next(i for i, n in enumerate(N) if 'mesh' in n and n.get('name', '').startswith('Body'))
    m = g.j['meshes'][N[body]['mesh']]; p = m['primitives'][0]; A = p['attributes']
    P = g.acc(A['POSITION']).astype(float); Nn = g.acc(A['NORMAL']).astype(float); UV = g.acc(A['TEXCOORD_0'])
    J = g.acc(A['JOINTS_0']).astype(int); Wt = g.acc(A['WEIGHTS_0']).astype(float); I = g.acc(p['indices']).reshape(-1)
    # humans keep forearms/hands in a separate FPArms mesh over the same vertex buffer: rig the whole body
    for n2 in N:
        if 'mesh' in n2 and n2.get('name', '').startswith('FPArms'):
            p2 = g.j['meshes'][n2['mesh']]['primitives'][0]
            if p2['attributes']['POSITION'] == A['POSITION']:
                T = np.concatenate([I.reshape(-1, 3), g.acc(p2['indices']).reshape(-1, 3)]); T = np.unique(np.sort(T, 1), axis=0, return_index=True)[1]
                I = np.concatenate([I.reshape(-1, 3), g.acc(p2['indices']).reshape(-1, 3)])[np.sort(T)].reshape(-1)
    sk = g.j['skins'][N[body]['skin']]; joints = sk['joints']
    def desc(root):
        out = {root}; ch = True
        while ch:
            ch = False
            for c, pp in par.items():
                if pp in out and c not in out: out.add(c); ch = True
        return out
    D = [np.eye(4) for _ in joints]
    for side, sgn in (('L', 1), ('R', -1)):
        ua = nm['UpperArm' + side]; piv = W[ua][:3, 3]; R = rotz(sgn * ang); M = np.eye(4); M[:3, :3] = R; M[:3, 3] = piv - R @ piv
        for k, ji in enumerate(joints):
            if ji in desc(ua): D[k] = M
    # mesh vertices are in the body node's space; joints world. Body node world:
    Bw = W[body]; Bi = np.linalg.inv(Bw)
    Ph = np.c_[P, np.ones(len(P))] @ Bw.T
    out = np.zeros_like(P); outn = np.zeros_like(Nn)
    for k in range(4):
        Mk = np.stack([D[j] for j in J[:, k]])
        out += Wt[:, k:k + 1] * np.einsum('nij,nj->ni', Mk, Ph)[:, :3]
        outn += Wt[:, k:k + 1] * np.einsum('nij,nj->ni', Mk[:, :3, :3], Nn @ Bw[:3, :3].T)
    outn /= np.linalg.norm(outn, axis=1, keepdims=True) + 1e-9
    # pick base color image
    mat = g.j['materials'][p.get('material', 0)]; ti = mat['pbrMetallicRoughness']['baseColorTexture']['index']
    img = g.j['images'][g.j['textures'][ti]['source']]; imgb = g.view_bytes(img['bufferView'])
    return out.astype(np.float32), outn.astype(np.float32), UV.astype(np.float32), I.astype(np.uint32), imgb, img.get('mimeType', 'image/png')
def write_static(path, P, Nn, UV, I, imgb, mime):
    chunks = []; views = []; accs = []
    def add(arr, typ, ctype, target=None, mm=False):
        o = sum(len(c) for c in chunks); b = arr.tobytes(); chunks.append(b + b'\0' * ((4 - len(b) % 4) % 4))
        v = dict(buffer=0, byteOffset=o, byteLength=len(b)); target and v.update(target=target); views.append(v)
        if typ is None: return len(views) - 1
        a = dict(bufferView=len(views) - 1, componentType=ctype, count=len(arr), type=typ)
        if mm: a.update(min=arr.min(0).tolist(), max=arr.max(0).tolist())
        accs.append(a); return len(accs) - 1
    ap = add(P, 'VEC3', 5126, 34962, True); an = add(Nn, 'VEC3', 5126, 34962); au = add(UV, 'VEC2', 5126, 34962)
    ai = add(I, 'SCALAR', 5125, 34963); iv = add(np.frombuffer(imgb, np.uint8), None, None)
    j = dict(asset=dict(version='2.0'), scene=0, scenes=[dict(nodes=[0])], nodes=[dict(name='Body', mesh=0)],
             meshes=[dict(primitives=[dict(attributes=dict(POSITION=ap, NORMAL=an, TEXCOORD_0=au), indices=ai, material=0)])],
             materials=[dict(pbrMetallicRoughness=dict(baseColorTexture=dict(index=0), metallicFactor=0, roughnessFactor=.8))],
             textures=[dict(source=0)], images=[dict(bufferView=iv, mimeType=mime)], accessors=accs, bufferViews=views,
             buffers=[dict(byteLength=sum(len(c) for c in chunks))])
    js = json.dumps(j).encode(); js += b' ' * ((4 - len(js) % 4) % 4); bn = b''.join(chunks)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bn))); f.write(struct.pack('<I', len(js)) + b'JSON' + js); f.write(struct.pack('<I', len(bn)) + b'BIN\0' + bn)
if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    for n in (sys.argv[3:] or ['bilge', 'ates', 'kral', 'ay', 'hellgate', 'human-bilge', 'human-ates', 'human-kral', 'human-ay', 'human-hellgate']):
        P, Nn, UV, I, imgb, mime = apose(os.path.join(src, n + '.glb'))
        write_static(os.path.join(dst, n + '.glb'), P, Nn, UV, I, imgb, mime)
        print(n, len(P), len(I) // 3, 'h=%.2f' % (P[:, 1].max() - P[:, 1].min()), 'zface', round(float(P[:, 2].max()), 2), round(float(P[:, 2].min()), 2), os.path.getsize(os.path.join(dst, n + '.glb')) // 1024, 'KB')
