"""Compare open (boundary) edges of a built model with its pre-rig source, welding UV-seam twins by position."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB, skin
import build_game as b
def tris(g, body_only=True):
    N = g.j['nodes']; out = []; P = None
    for i, n in enumerate(N):
        if 'mesh' not in n or 'skin' not in n: continue
        if body_only and n.get('name', '').startswith('FPArms') and P is not None and False: continue
        pr = g.j['meshes'][n['mesh']]['primitives'][0]
        if P is None: P = g.acc(pr['attributes']['POSITION'])
        out.append(g.acc(pr['indices']).reshape(-1, 3).astype(int))
    return P, out
def new_holes(model, source):
    g = GLB(model); s = GLB(source)
    P, Tg = tris(g); _, Ts = tris(s)
    body = Tg[0]   # Body mesh (FPArms is an intentional open subset)
    w = b.weld_ids(P); src_all = np.concatenate(Ts)
    so = set(b.open_edges(w[src_all])); no = [e for e in b.open_edges(w[body]) if e not in so]
    # trace the new open edges into loops; a real hole has a large vector area, a closed seam has (almost) none
    nxt = {}
    for u, v in no: nxt.setdefault(u, []).append(v)
    used = set(); areas = []
    for u0, v0 in no:
        if (u0, v0) in used: continue
        loop = [u0]; cur = v0; used.add((u0, v0))
        while cur != u0:
            loop.append(cur); c = [x for x in nxt.get(cur, []) if (cur, x) not in used]
            if not c: break
            used.add((cur, c[0])); cur = c[0]
        Q = P[loop].astype(float); A = 0.5 * np.linalg.norm(np.cross(Q, np.roll(Q, -1, 0)).sum(0)); areas.append(A)
    return len(no), sorted(areas, reverse=True)[:5]
if __name__ == '__main__':
    print(new_holes(sys.argv[1], sys.argv[2]))
