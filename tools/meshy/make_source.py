"""Turn a fresh Meshy rig of a NEW character into a 'source' model in the game's conventions, so tools/meshy/build_game.py
can finish it exactly like the older characters:
  - joints renamed to the engine's names, rest = Meshy bind pose
  - spring bones added and skinned from the geometry: Tail1-3 (tail island behind the hips) and Hair1-3 (hair found by
    its colour in the base-colour texture, hanging below the skull)
  - the approved custom clips (quad run, flip attack, roar, claws, jump, transform, FP ready pose) retargeted from a
    finished donor character with a per-bone rest-direction correction (T-pose model vs. arms-down donor)
usage (python): make_source(rigged, donor, out, body_name, tail=True, hair=True, clips=[...])"""
import sys, os, re, colorsys, io, numpy as np
from PIL import Image
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__))
from glbio import GLB, sample_trs, world_with, skin, _q2m
import build_game as bg
def orth(M): return bg.orth(M)
def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = float(np.dot(a, b))
    if c < -0.9999:
        ax = np.cross(a, [1, 0, 0]); ax = ax if np.linalg.norm(ax) > 1e-3 else np.cross(a, [0, 1, 0]); ax /= np.linalg.norm(ax)
        return 2 * np.outer(ax, ax) - np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
def components(I, sel, wid):
    """Connected components (welded) of the sub-mesh formed by triangles whose 3 vertices are all selected."""
    T = I.reshape(-1, 3); T = T[sel[T].all(1)]; W = wid[T]
    par = {}
    def f(x):
        while par.get(x, x) != x: par[x] = par.get(par[x], par[x]); x = par[x]
        return x
    for a, b, c in W:
        for u, v in ((a, b), (b, c)):
            ru, rv = f(u), f(v)
            if ru != rv: par[ru] = rv
    lab = {}
    for v in np.unique(W): lab.setdefault(f(v), []).append(v)
    return sorted(lab.values(), key=len, reverse=True)
def chain_weights(P, idx, pts, root_bone, chain, joint_names, Wd, blend_top=.15):
    """Skin vertices idx along polyline pts (root..tip) onto bones chain[0..n-1] (bone k spans pts[k]..pts[k+1])."""
    seg = np.diff(pts, axis=0); L = np.linalg.norm(seg, axis=1); cum = np.r_[0, np.cumsum(L)]
    for v in idx:
        best = None
        for k in range(len(seg)):
            t = np.clip(np.dot(P[v] - pts[k], seg[k]) / (L[k] ** 2 + 1e-12), 0, 1); d = np.linalg.norm(P[v] - (pts[k] + t * seg[k]))
            if best is None or d < best[0]: best = (d, k, t)
        _, k, t = best; s = (cum[k] + t * L[k]) / cum[-1]
        w = np.zeros(Wd.shape[1])
        f = s * len(chain) - .5; k0 = int(np.clip(np.floor(f), 0, len(chain) - 1)); k1 = min(k0 + 1, len(chain) - 1); a = np.clip(f - k0, 0, 1)
        w[joint_names.index(chain[k0])] += 1 - a; w[joint_names.index(chain[k1])] += a
        if s < blend_top:   # root of the chain blends into the body bone so the seam does not tear
            r = 1 - s / blend_top; w *= (1 - r); w[joint_names.index(root_bone)] += r
        Wd[v] = w
def make_source(rigged, donor, out, body_name, tail=True, hair=True, clips=(), report=print, extras=None, fingers_bones=False):
    mr = GLB(rigged); Wm, _ = mr.node_world(); mn = mr.j['nodes']; mname = {n.get('name'): i for i, n in enumerate(mn)}
    arm = mname['Armature']; keep = [arm]; st = list(mn[arm].get('children', []))
    while st:
        i = st.pop(0)
        if 'mesh' in mn[i]: continue
        keep.append(i); st += mn[i].get('children', [])
    newidx = {}; nodes = [{'name': 'WolfScale', 'scale': [1, 1, 1], 'children': []}]
    for i in keep:
        n = {kk: vv for kk, vv in mn[i].items() if kk in ('translation', 'rotation', 'scale', 'matrix')}; n['name'] = bg.REN.get(mn[i].get('name'), mn[i].get('name'))
        newidx[i] = len(nodes); nodes.append(n)
    for i in keep:
        ch = [newidx[c] for c in mn[i].get('children', []) if c in newidx]
        if ch: nodes[newidx[i]]['children'] = ch
    nodes[0]['children'].append(newidx[arm]); byname = {n['name']: i for i, n in enumerate(nodes)}
    mi = next(i for i, n in enumerate(mn) if 'skin' in n); pr = mr.j['meshes'][mn[mi]['mesh']]['primitives'][0]; A = pr['attributes']
    P, Nn = skin(mr, Wm, mi, normals=True); I = mr.acc(pr['indices']).reshape(-1).astype(np.int64); UV = mr.acc(A['TEXCOORD_0']).astype(np.float32)
    Jm = mr.acc(A['JOINTS_0']).astype(int); Wtm = mr.acc(A['WEIGHTS_0']).astype(float); mj = mr.j['skins'][0]['joints']
    joint_names = [bg.REN.get(mn[j]['name'], mn[j]['name']) for j in mj]
    Wn = world_with(bg.J(nodes), {}); pos = lambda nm: Wn[byname[nm]][:3, 3]
    h = P[:, 1].max() - P[:, 1].min(); wid = bg.weld_ids(P)
    extra_specs = []
    if tail:
        hz = pos('Hips')[2]; sel = (P[:, 2] < hz - .06 * h) & (P[:, 1] < pos('Hips')[1] + .05 * h) & (P[:, 1] > .08 * h)
        comps = components(I, sel, wid)
        if comps:
            isl = np.isin(wid, comps[0]); idx = np.where(isl)[0]
            top = P[idx][np.argmax(P[idx, 1] + -P[idx, 2] * 0)]; tip = P[idx][np.argmin(P[idx, 1])]
            root = np.array([0, pos('Hips')[1] - .02 * h, P[idx, 2].max()])
            pts = np.array([root + (tip - root) * f for f in (0, .3, .62, 1.0)])
            extra_specs.append(('Tail', 'Hips', pts, idx)); report('  tail island: %d vertices, tip %s' % (len(idx), np.round(tip, 2)))
    if hair:
        mat = mr.j['materials'][pr.get('material', 0)]; ti = mat['pbrMetallicRoughness']['baseColorTexture']['index']
        img = mr.j['images'][mr.j['textures'][ti]['source']]; tex = np.asarray(Image.open(io.BytesIO(mr.view_bytes(img['bufferView']))).convert('RGB'), np.float32) / 255
        th, tw = tex.shape[:2]; px = tex[np.clip((UV[:, 1] * th).astype(int), 0, th - 1), np.clip((UV[:, 0] * tw).astype(int), 0, tw - 1)]
        hsv = np.array([colorsys.rgb_to_hsv(*c) for c in px])
        red = (hsv[:, 0] > .03) & (hsv[:, 0] < .11) & (hsv[:, 1] > .55) & (hsv[:, 2] > .42)   # copper hair; leather is darker, skin and fur paler
        neck = pos('Neck')[1]; head = pos('Head')
        long_hair = red & (P[:, 1] < neck + .02 * h) & (P[:, 1] > pos('Chest')[1] - .2 * h) & (np.abs(P[:, 0]) < .35 * h)
        idx = np.where(long_hair)[0]
        if len(idx) > 50:
            low = P[idx][np.argmin(P[idx, 1])]; root = np.array([0, neck + .02 * h, head[2] - .04 * h]); tipp = np.array([0, low[1], P[idx, 2].min() * .5 + root[2] * .5])
            pts = np.array([root + (tipp - root) * f for f in (0, .35, .7, 1.0)])
            extra_specs.append(('Hair', 'Head', pts, idx)); report('  hair below the skull: %d vertices down to y=%.2f' % (len(idx), low[1]))
    fingers = []
    if fingers_bones:   # Meshy hands have no finger joints: add one curl bone per hand (first-person grip)
        for sd in 'LR':
            hnd = pos('Hand' + sd); fa = pos('Forearm' + sd); d = (hnd - fa) / np.linalg.norm(hnd - fa)
            hi = joint_names.index('Hand' + sd); domh = Wtm[np.arange(len(P)), 0] * 0
            for c in range(4): domh = domh + Wtm[:, c] * (Jm[:, c] == hi)
            along = (P - hnd) @ d; L_h = np.linalg.norm(hnd - fa) * .45
            lat = np.linalg.norm((P - hnd) - along[:, None] * d[None], axis=1)   # the thumb sticks out sideways: leave it on the hand
            idx = np.where((domh > .4) & (along > L_h * .45) & (lat < L_h * .42))[0]
            if len(idx) > 20: fingers.append(('Fingers' + sd, 'Hand' + sd, hnd + d * L_h * .35, idx, along[idx], L_h))
    for nm_, par_, p_, idx_, al_, L_ in fingers:
        Wp = world_with(bg.J(nodes), {})[byname[par_]]; loc = np.linalg.inv(Wp) @ np.r_[p_, 1]
        nodes.append({'name': nm_, 'translation': loc[:3].tolist()}); byname[nm_] = len(nodes) - 1; nodes[byname[par_]].setdefault('children', []).append(byname[nm_]); joint_names.append(nm_)
    for base, parent, pts, idx in extra_specs:
        par = parent
        for k in range(3):
            Wp = world_with(bg.J(nodes), {})[byname[par]]; loc = np.linalg.inv(Wp) @ np.r_[pts[k], 1]
            nm = '%s%d' % (base, k + 1); nodes.append({'name': nm, 'translation': loc[:3].tolist()}); byname[nm] = len(nodes) - 1
            nodes[byname[par]].setdefault('children', []).append(byname[nm]); par = nm; joint_names.append(nm)
    nJ = len(joint_names); Wd = np.zeros((len(P), nJ))
    for c in range(4): np.add.at(Wd, (np.arange(len(P)), Jm[:, c]), Wtm[:, c])
    for nm_, par_, p_, idx_, al_, L_ in fingers:
        f_ = np.clip((al_ - L_ * .45) / (L_ * .3), 0, 1)   # knuckles blend, finger tips fully on the curl bone
        Wd[idx_] *= (1 - f_)[:, None]; Wd[idx_, joint_names.index(nm_)] += f_
    for base, parent, pts, idx in extra_specs:
        chain_weights(P, idx, pts, parent, ['%s1' % base, '%s2' % base, '%s3' % base], joint_names, Wd)
    top = np.argsort(-Wd, 1)[:, :4]; tw_ = np.take_along_axis(Wd, top, 1); tw_ /= tw_.sum(1, keepdims=True) + 1e-9
    Wn = world_with(bg.J(nodes), {}); jidx = [byname[n] for n in joint_names]; IB = [np.linalg.inv(Wn[j]) for j in jidx]
    # ---------- retarget the approved clips from the donor (rest-direction corrected) ----------
    dn = GLB(donor); dname = {n.get('name'): i for i, n in enumerate(dn.j['nodes'])}; Wd0 = world_with(dn, {})
    tpar = bg.parents(nodes); dpar = bg.parents(dn.j['nodes'])
    child_of = {'Hips': 'Spine', 'Spine': 'Spine1' if 'Spine1' in byname else 'Chest', 'Chest': 'Neck', 'Neck': 'Head',
                'Tail1': 'Tail2', 'Tail2': 'Tail3', 'Hair1': 'Hair2', 'Hair2': 'Hair3'}
    for sd in 'LR': child_of.update({'Clav' + sd: 'UpperArm' + sd, 'UpperArm' + sd: 'Forearm' + sd, 'Forearm' + sd: 'Hand' + sd, 'Thigh' + sd: 'Shin' + sd, 'Shin' + sd: 'Foot' + sd})
    mapped = [n for n in bg.OLDMAP + ['Tail1', 'Tail2', 'Tail3', 'Hair1', 'Hair2', 'Hair3', 'Fingers' + 'L', 'FingersR', 'Jaw'] if n in byname and n in dname]
    C = {}
    for n in mapped:
        c = child_of.get(n)
        if c and c in byname and c in dname:
            td = Wn[byname[c]][:3, 3] - Wn[byname[n]][:3, 3]; dd = Wd0[dname[c]][:3, 3] - Wd0[dname[n]][:3, 3]
            C[n] = rot_between(td, dd)   # maps the target's rest bone direction onto the donor's
    for n in mapped:
        if n not in C: C[n] = C.get(next((k for k, v in child_of.items() if v == n), ''), np.eye(3))
    restR = {i: orth(Wn[i]) for i in range(len(nodes))}; dRest = {n: orth(Wd0[dname[n]]) for n in mapped}
    order = []; st = [0]
    while st:
        i = st.pop(0); order.append(i); st += nodes[i].get('children', [])
    hip_ratio = (pos('Hips')[1]) / max(1e-6, Wd0[dname['Hips']][1, 3])
    out_clips = []
    for cname in clips:
        a = next((x for x in dn.j['animations'] if x['name'] == cname), None)
        if a is None: continue
        T = max(dn.acc(s['input']).max() for s in a['samplers']); ts = np.linspace(0, T, int(round(T * 30)) + 1)
        rot = {i: [] for i in order if i in jidx}; tra = []
        for t in ts:
            Wt = world_with(dn, sample_trs(dn, a, t)); Rw = {}
            for i in order:
                p = tpar.get(i); Rp = Rw[p] if p is not None else np.eye(3); nm = nodes[i]['name']
                if nm in mapped:
                    Dw = orth(Wt[dname[nm]]) @ dRest[nm].T   # donor's world rotation away from its rest
                    R = Dw @ C[nm] @ restR[i]
                else: R = Rp @ (restR[p].T @ restR[i] if p is not None else restR[i])
                Rw[i] = R
                if i in rot: rot[i].append(bg.m2q(Rp.T @ R))
            dpos = (Wt[dname['Hips']][:3, 3] - Wd0[dname['Hips']][:3, 3]) * hip_ratio
            tra.append((np.linalg.inv(Wn[tpar[byname['Hips']]]) @ np.r_[pos('Hips') + dpos, 1])[:3])
        ch = [(i, 'rotation', ts.astype(np.float32), bg.qfix(np.array(q)).astype(np.float32)) for i, q in rot.items()]
        ch.append((byname['Hips'], 'translation', ts.astype(np.float32), np.array(tra, np.float32)))
        out_clips.append((cname, ch)); report('  retargeted %s from %s (%.2fs)' % (cname, os.path.basename(donor), T))
    mesh = dict(name=body_name, extras=extras, P=P.astype(np.float32), N=Nn.astype(np.float32), UV=UV, I=I.astype(np.uint32), J=top.astype(np.uint16), W=tw_.astype(np.float32), mat=pr.get('material', 0))
    bg.write(out, mr, nodes, jidx, IB, [mesh], out_clips)
    return extra_specs
