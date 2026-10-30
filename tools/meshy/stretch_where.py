"""Show where triangles stretch: per clip, the dominant bones of the worst stretched edges."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB, sample_trs, world_with, skin
def run(path, clips=None, ratio=3.0, absm=.2):
    g = GLB(path); N = g.j['nodes']; mi = next(i for i, n in enumerate(N) if 'skin' in n)
    p = g.j['meshes'][N[mi]['mesh']]['primitives'][0]; J = g.acc(p['attributes']['JOINTS_0']).astype(int); Wt = g.acc(p['attributes']['WEIGHTS_0'])
    names = [N[j]['name'] for j in g.j['skins'][N[mi]['skin']]['joints']]
    R, I = skin(g, world_with(g, {}), mi); T = I.reshape(-1, 3)
    E = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1), axis=0); L0 = np.linalg.norm(R[E[:, 0]] - R[E[:, 1]], axis=1)
    res = {}
    for a in g.j['animations']:
        if clips and a['name'] not in clips: continue
        Tm = g.acc(a['samplers'][0]['input']).max(); cnt = {}
        for t in np.linspace(0, Tm, 16):
            Q, _ = skin(g, world_with(g, sample_trs(g, a, t)), mi); L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1)
            bad = np.where((L > L0 * ratio) & (L - L0 > absm))[0]
            for e in bad:
                for v in E[e]:
                    key = names[J[v, np.argmax(Wt[v])]]; cnt[key] = cnt.get(key, 0) + 1
        res[a['name']] = sorted(cnt.items(), key=lambda x: -x[1])[:6]
    return res
if __name__ == '__main__':
    for k, v in run(sys.argv[1], sys.argv[2:] or None).items(): print(k, v)
