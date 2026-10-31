"""Build a game-ready character GLB from:
  - the current game GLB (mesh, materials, textures, spring bones such as Tail/Cape/Hair/Jaw/Fingers),
  - the Meshy auto-rig (standard humanoid skeleton + skin weights),
  - Meshy animation GLBs (clips baked on that exact skeleton, so no retarget error),
  - optional transfer of approved clips from the old skeleton (world-space rotation deltas; rest poses coincide).
Output keeps the engine's bone names (Hips, Spine, Chest, Neck, Head, ClavL, UpperArmL, ForearmL, HandL, ThighL, ShinL, FootL...)."""
import sys, os, re, json, struct, numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB, sample_trs, world_with, _q2m, skin
REN = {'Hips': 'Hips', 'Spine02': 'Spine', 'Spine01': 'Spine1', 'Spine': 'Chest', 'neck': 'Neck', 'Head': 'Head', 'head_end': 'HeadEnd', 'headfront': 'HeadFront'}
for s, S in (('Left', 'L'), ('Right', 'R')):
    REN.update({s + 'Shoulder': 'Clav' + S, s + 'Arm': 'UpperArm' + S, s + 'ForeArm': 'Forearm' + S, s + 'Hand': 'Hand' + S,
                s + 'UpLeg': 'Thigh' + S, s + 'Leg': 'Shin' + S, s + 'Foot': 'Foot' + S, s + 'ToeBase': 'Toe' + S})
EXTRA = re.compile(r'^(Tail|Cape|Hair|Jaw|Ear|Fingers)')
OLDMAP = ['Hips', 'Spine', 'Chest', 'Neck', 'Head'] + [b + s for s in 'LR' for b in ('Clav', 'UpperArm', 'Forearm', 'Hand', 'Thigh', 'Shin', 'Foot')]
class J:  # tiny json holder usable by world_with
    def __init__(self, nodes): self.j = {'nodes': nodes}
def orth(M):
    R = M[:3, :3] / np.linalg.norm(M[:3, :3], axis=0, keepdims=True); u, _, vt = np.linalg.svd(R); return u @ vt
def m2q(R):
    t = np.trace(R)
    if t > 0: s = np.sqrt(t + 1) * 2; q = [(R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s, .25 * s]
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]: s = np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2]) * 2; q = [.25 * s, (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s, (R[2, 1] - R[1, 2]) / s]
    elif R[1, 1] > R[2, 2]: s = np.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2]) * 2; q = [(R[0, 1] + R[1, 0]) / s, .25 * s, (R[1, 2] + R[2, 1]) / s, (R[0, 2] - R[2, 0]) / s]
    else: s = np.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1]) * 2; q = [(R[0, 2] + R[2, 0]) / s, (R[1, 2] + R[2, 1]) / s, .25 * s, (R[1, 0] - R[0, 1]) / s]
    q = np.array(q); return q / np.linalg.norm(q)
def qfix(Q):  # keep quaternion hemisphere continuous
    for i in range(1, len(Q)):
        if np.dot(Q[i], Q[i - 1]) < 0: Q[i] = -Q[i]
    return Q
def parents(nodes):
    p = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): p[c] = i
    return p
def skinned_mesh(g, ni):
    n = g.j['nodes'][ni]; pr = g.j['meshes'][n['mesh']]['primitives'][0]; A = pr['attributes']
    return pr, A
def build(old_path, rig_path, anim_specs, out_path, transfer=(), scale_wrap=None, report=print, rigid=('Head',), destretch_skip=(), fp_arms=False, old_from=None):
    old = GLB(old_path); mr = GLB(rig_path); Wo, _ = old.node_world(); Wm, _ = mr.node_world()
    on = old.j['nodes']; oname = {n.get('name'): i for i, n in enumerate(on)}
    k = scale_wrap if scale_wrap is not None else (on[oname['WolfScale']]['scale'][0] if 'WolfScale' in oname else 1.0)
    # ---------- Meshy re-centres the model (x/z bbox centre) and rescales it to height_meters: undo that ----------
    _mm = next(i for i, n in enumerate(mr.j['nodes']) if 'skin' in n); _Pm, _Im = skin(mr, Wm, _mm)
    _om = next(i for i, n in enumerate(on) if 'skin' in n and n.get('name', '').startswith('Body')); _Po, _Io = skin(old, Wo, _om)
    _Pm = _Pm[_Im]; _Po = _Po[_Io]
    sm_ = (_Po[:, 1].max() - _Po[:, 1].min()) / (_Pm[:, 1].max() - _Pm[:, 1].min())
    cm_ = np.array([(_Pm[:, 0].max() + _Pm[:, 0].min()) / 2, _Pm[:, 1].min(), (_Pm[:, 2].max() + _Pm[:, 2].min()) / 2])
    co_ = np.array([(_Po[:, 0].max() + _Po[:, 0].min()) / 2, _Po[:, 1].min(), (_Po[:, 2].max() + _Po[:, 2].min()) / 2])
    Tm2o = np.eye(4); Tm2o[:3, :3] *= sm_; Tm2o[:3, 3] = co_ - sm_ * cm_
    tr_ = cKDTree(_Po)
    for _ in range(8):   # refine (scale + offset) on matched points; robust to parts that changed since rigging
        Q = _Pm * Tm2o[0, 0] + Tm2o[:3, 3]; d_, nn_ = tr_.query(Q); ok_ = d_ < max(np.percentile(d_, 80) * 2, 1e-4)
        A_, B_ = _Pm[ok_], _Po[nn_[ok_]]; ma, mb = A_.mean(0), B_.mean(0)
        sc_ = ((A_ - ma) * (B_ - mb)).sum() / ((A_ - ma) ** 2).sum()
        Tm2o = np.eye(4); Tm2o[:3, :3] *= sc_; Tm2o[:3, 3] = mb - sc_ * ma
    sm_ = Tm2o[0, 0]
    report('  Meshy frame -> game frame: scale %.4f, offset %s' % (sm_, np.round(Tm2o[:3, 3], 4)))
    Wm = [Tm2o @ w for w in Wm]
    # ---------- skeleton: Meshy armature subtree, renamed ----------
    mn = mr.j['nodes']; mname = {n.get('name'): i for i, n in enumerate(mn)}
    arm = mname['Armature']; mpar = parents(mn)
    keep = [arm]; stack = list(mn[arm].get('children', []))
    while stack:
        i = stack.pop(0)
        if 'mesh' in mn[i]: continue
        keep.append(i); stack += mn[i].get('children', [])
    newidx = {}; nodes = [{'name': 'WolfScale', 'scale': [k, k, k], 'children': []}]
    for i in keep:
        n = {kk: vv for kk, vv in mn[i].items() if kk in ('translation', 'rotation', 'scale', 'matrix')}
        n['name'] = REN.get(mn[i].get('name'), mn[i].get('name')); newidx[i] = len(nodes); nodes.append(n)
    for i in keep:
        ch = [newidx[c] for c in mn[i].get('children', []) if c in newidx]
        if ch: nodes[newidx[i]]['children'] = ch
    A0 = nodes[newidx[arm]]; Aw = Wm[arm] / 1.0   # already includes Tm2o; express under WolfScale(k)
    Al = np.diag([1 / k, 1 / k, 1 / k, 1]) @ Aw; asc = np.linalg.norm(Al[:3, :3], axis=0); Ar = Al[:3, :3] / asc
    for kk in ('matrix', 'rotation'): A0.pop(kk, None)
    A0['scale'] = asc.tolist(); A0['translation'] = Al[:3, 3].tolist()
    if not np.allclose(Ar, np.eye(3), atol=1e-6): A0['rotation'] = m2q(Ar).tolist()
    nodes[0]['children'].append(newidx[arm])
    byname = {n['name']: i for i, n in enumerate(nodes)}
    # put every joint's rest TRS at its bind pose (Meshy node defaults are not always the bind pose)
    mskin0 = mr.j['skins'][0]; MIB = mr.acc(mskin0['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
    bind = {newidx[j]: Tm2o @ np.linalg.inv(MIB[q]) for q, j in enumerate(mskin0['joints'])}
    npar0 = parents(nodes)
    order0 = []; st0 = [0]
    while st0:
        i = st0.pop(0); order0.append(i); st0 += nodes[i].get('children', [])
    Wcur = world_with(J(nodes), {})
    for i in order0:
        if i not in bind: continue
        p_ = npar0[i]; Wp_ = Wcur[p_] if p_ not in bind else bind[p_]
        L = np.linalg.inv(Wp_) @ bind[i]; R = L[:3, :3]; sc_ = np.linalg.norm(R, axis=0); R = R / sc_
        u_, _, vt_ = np.linalg.svd(R); R = u_ @ vt_
        nd = nodes[i]; nd.pop('matrix', None); nd['translation'] = L[:3, 3].tolist(); nd['rotation'] = m2q(R).tolist(); nd['scale'] = sc_.tolist()
        if np.allclose(sc_, 1, atol=1e-3): nd.pop('scale')
    # ---------- spring / extra bones from the old rig ----------
    oskin_node = next(i for i, n in enumerate(on) if 'skin' in n and n.get('name', '').startswith('Body'))
    ojoints = old.j['skins'][on[oskin_node]['skin']]['joints']; opar = parents(on)
    extras = [on[j]['name'] for j in ojoints if EXTRA.match(on[j].get('name', ''))]
    for e in extras:
        oi = oname[e]; pn = on[opar[oi]]['name']; pn = pn if pn in byname else 'Hips'
        Wn = world_with(J(nodes), {}); Wp = Wn[byname[pn]]
        loc = np.linalg.inv(Wp) @ np.r_[Wo[oi][:3, 3], 1]
        nodes.append({'name': e, 'translation': loc[:3].tolist()}); byname[e] = len(nodes) - 1
        nodes[byname[pn]].setdefault('children', []).append(byname[e])
    Wn = world_with(J(nodes), {})
    msk = mr.j['skins'][0]; mjoints = msk['joints']
    joint_names = [REN.get(mn[j]['name'], mn[j]['name']) for j in mjoints] + extras
    jidx = [byname[n] for n in joint_names]
    # ---------- weights: nearest Meshy vertex, spring bones blended back in ----------
    mmesh = next(i for i, n in enumerate(mn) if 'skin' in n); mpr, mA = skinned_mesh(mr, mmesh)
    Pm = skin(mr, Wm, mmesh)[0]   # Wm already carries Tm2o
    Jm = mr.acc(mA['JOINTS_0']).astype(int); Wtm = mr.acc(mA['WEIGHTS_0']).astype(float)
    tree = cKDTree(Pm); nJ = len(joint_names); out_meshes = []
    ojnames = [on[j]['name'] for j in ojoints]
    for ni, n in enumerate(on):
        if 'mesh' not in n or 'skin' not in n: continue
        if n.get('name', '').startswith('FPArms'): continue   # rebuilt below from the full body
        pr, A = skinned_mesh(old, ni)
        fullI = old.acc(pr['indices']).reshape(-1, 3).astype(np.int64)
        for n2 in on:   # humans keep forearms/hands in a separate mesh over the same vertices: merge into one full body
            if 'mesh' in n2 and n2.get('name', '').startswith('FPArms'):
                p2 = old.j['meshes'][n2['mesh']]['primitives'][0]
                if p2['attributes']['POSITION'] == A['POSITION']:
                    T2 = np.concatenate([fullI, old.acc(p2['indices']).reshape(-1, 3).astype(np.int64)])
                    fullI = T2[np.sort(np.unique(np.sort(T2, 1), axis=0, return_index=True)[1])]
        P = old.acc(A['POSITION']).astype(float); Nn = old.acc(A['NORMAL']).astype(float)
        Pw, Nw = skin(old, Wo, ni, normals=True)
        d, nn = tree.query(Pw); report('  %s: %d verts, nearest Meshy vertex max %.4f m, p99 %.4f' % (n['name'], len(P), d.max(), np.percentile(d, 99)))
        Wd = np.zeros((len(P), nJ))
        for c in range(4): np.add.at(Wd, (np.arange(len(P)), Jm[nn, c]), Wtm[nn, c])
        Jo = old.acc(A['JOINTS_0']).astype(int); Wto = old.acc(A['WEIGHTS_0']).astype(float)
        Eo = np.zeros((len(P), nJ))
        for c in range(4):
            nm_ = [ojnames[x] for x in Jo[:, c]]
            for v in range(len(P)):
                if nm_[v] in extras: Eo[v, joint_names.index(nm_[v])] += Wto[v, c]
        e = Eo.sum(1, keepdims=True); Wd = Wd / (Wd.sum(1, keepdims=True) + 1e-9) * (1 - np.clip(e, 0, 1)) + Eo
        # cloth / tail / hair vertices: their body share comes only from torso bones (Meshy only knows a humanoid and
        # would otherwise hang a cape corner or tail tip on an arm or a leg)
        limb = np.array([bool(re.match(r'^(UpperArm|Forearm|Hand|Fingers|Thigh|Shin|Foot|Toe)', x)) for x in joint_names])
        exv = e[:, 0] > 1e-3
        if exv.any():
            Mt = Wd[exv].copy(); Mt[:, limb] = 0; Mt[:, [joint_names.index(x) for x in extras]] = 0
            z = Mt.sum(1) < 1e-6; Mt[z, joint_names.index('Hips')] = 1
            Mt /= Mt.sum(1, keepdims=True); Wd[exv] = Mt * (1 - np.clip(e[exv], 0, 1)) + Eo[exv]
        # hand-built attachments appended after the generated body (King's horns + cloak) keep their tuned old weights
        if old_from is not None and len(P) > old_from:
            Om = np.zeros((len(P) - old_from, nJ))
            for c in range(4):
                for q, v in enumerate(range(old_from, len(P))):
                    nm_ = ojnames[Jo[v, c]]; nm_ = 'Hips' if nm_ == 'Root' else nm_
                    if Wto[v, c] > 0 and nm_ in joint_names: Om[q, joint_names.index(nm_)] += Wto[v, c]
            Wd[old_from:] = Om / (Om.sum(1, keepdims=True) + 1e-9)
        # rigid attachments (horns, skull plates) that were 100% on one bone stay 100% on that bone
        for bn in rigid:
            if bn not in ojnames or bn not in joint_names: continue
            hit = ((Jo == ojnames.index(bn)) & (Wto >= .999)).any(1)
            if hit.any(): Wd[hit] = 0; Wd[hit, joint_names.index(bn)] = 1
        # a vertex may belong to an arm or to a leg, never to both (fused hand/thigh in generated meshes)
        grp0 = np.array([1 if re.match(r'^(UpperArm|Forearm|Hand|Fingers)', x) else 2 if re.match(r'^(Thigh|Shin|Foot|Toe)', x) else 0 for x in joint_names])
        for sd in 'LR':
            a_ = np.array([g_ == 1 and x.endswith(sd) for g_, x in zip(grp0, joint_names)]); l_ = np.array([g_ == 2 and x.endswith(sd) for g_, x in zip(grp0, joint_names)])
            wa, wl = Wd[:, a_].sum(1), Wd[:, l_].sum(1); both = (wa > 0) & (wl > 0)
            Wd[np.ix_(both & (wa >= wl), l_)] = 0; Wd[np.ix_(both & (wa < wl), a_)] = 0
        if fp_arms:   # humans (posed by arm IK in third person): forearm/hand never shares a vertex with the hips or either leg
            a_ = np.array([bool(re.match(r'^(Forearm|Hand|Fingers)', x)) for x in joint_names]); l_ = np.array([bool(re.match(r'^(Hips|Thigh|Shin|Foot|Toe)', x)) for x in joint_names])
            wa, wl = Wd[:, a_].sum(1), Wd[:, l_].sum(1); both = (wa > 0) & (wl > 0)
            # decide by geometry, not by the (often wrong) transferred weights: a vertex close to the forearm/hand/finger
            # line belongs to the arm even if it touched the thigh in the rest pose (else finger pieces stay at the hips)
            Wn_ = world_with(J(nodes), {}); Hs = np.ptp(Pw[:, 1]) / 1.78; isa = np.zeros(len(Pw), bool)
            def _seg(p0, p1):
                v = p1 - p0; t = np.clip(((Pw - p0) @ v) / (v @ v + 1e-12), 0, 1); return np.linalg.norm(Pw - (p0 + t[:, None] * v), axis=1)
            for sd in 'LR':
                h = Wn_[byname['Hand' + sd]][:3, 3]; fo = Wn_[byname['Forearm' + sd]][:3, 3]; tip = h + (h - fo) * .75
                dt = np.minimum(_seg(Wn_[byname['Thigh' + sd]][:3, 3], Wn_[byname['Shin' + sd]][:3, 3]), _seg(Wn_[byname['Thigh' + ('R' if sd == 'L' else 'L')]][:3, 3], Wn_[byname['Shin' + ('R' if sd == 'L' else 'L')]][:3, 3]))
                dh = _seg(h, tip); df = _seg(fo, h); mine = ((dh < .09 * Hs) | (df < .06 * Hs)) & (np.minimum(dh, df) < dt - .045 * Hs)
                orphan = mine & (wa < 1e-6); Wd[orphan] = 0; Wd[orphan, joint_names.index('Hand' + sd)] = 1; isa |= mine
            wa = Wd[:, a_].sum(1); both = (wa > 0) & (wl > 0)
            Wd[np.ix_(both & isa, l_)] = 0; Wd[np.ix_(both & ~isa, a_)] = 0
            low_ = Wd[:, l_].sum(1) / (Wd.sum(1) + 1e-9)
        top = np.argsort(-Wd, 1)[:, :4]; tw = np.take_along_axis(Wd, top, 1); tw /= tw.sum(1, keepdims=True) + 1e-9
        # Generated meshes often fuse the hanging hand to the thigh. Triangles bridging an arm and a leg tear open
        # as soon as the arm moves, so they are dropped (the two surfaces only touched in the rest pose).
        I_ = fullI
        grp = np.zeros(nJ, int)
        for q, nm_ in enumerate(joint_names):
            if re.match(r'^(UpperArm|Forearm|Hand|Fingers)', nm_): grp[q] = 1 if nm_.endswith('L') else 2
            if re.match(r'^(Thigh|Shin|Foot|Toe)', nm_): grp[q] = 3 if nm_.endswith('L') else 4
        armw = np.stack([Wd[:, grp == g_].sum(1) for g_ in (1, 2, 3, 4)], 1)
        dom = np.where(armw.max(1) > .15, armw.argmax(1) + 1, 0)
        exw = Wd[:, [joint_names.index(x) for x in extras]].sum(1) if extras else np.zeros(len(Wd)); dom[exw > .3] = 0   # cloth/tail follow their own bones
        G = dom[I_]; arm_ = (G == 1) | (G == 2); leg_ = (G == 3) | (G == 4); lr_ = (G == 1) | (G == 3)
        bridge = (arm_.any(1) & leg_.any(1)) | ((G == 1).any(1) & (G == 2).any(1))
        if fp_arms:   # also cut forearm/hand surfaces fused to the hips (hands resting on the hips in the rest pose)
            fh = np.array([bool(re.match(r'^(Forearm|Hand|Fingers)', x)) for x in joint_names]); fw = Wd[:, fh].sum(1) / (Wd.sum(1) + 1e-9)
            hipb = (fw[I_] > .5).any(1) & (low_[I_] > .5).any(1); bridge |= hipb; dom = np.where(fw > .5, np.where(dom > 0, dom, 1), np.where(low_ > .5, np.where(dom > 0, dom, 3), dom))
        caps = cap_holes(I_[~bridge], I_, dom, weld_ids(Pw)) if bridge.any() else np.zeros((0, 3), np.int64)
        if bridge.any(): report('  %s: split %d arm-leg bridging triangles, closed both sides with %d cap triangles' % (n['name'], bridge.sum(), len(caps)))
        idx_keep = np.concatenate([I_[~bridge], caps]).reshape(-1)
        out_meshes.append(dict(name=n['name'], extras=n.get('extras'), P=Pw.astype(np.float32), N=(Nw / (np.linalg.norm(Nw, axis=1, keepdims=True) + 1e-9)).astype(np.float32),
                               UV=old.acc(A['TEXCOORD_0']).astype(np.float32), I=idx_keep.astype(np.uint32), J=top.astype(np.uint16), W=tw.astype(np.float32), mat=pr.get('material', 0), Wd=Wd, ncap=len(caps)))
    if fp_arms and out_meshes:   # humans: thumb / index / other-finger bones so the hands can really grip and pull triggers
        split_fingers(nodes, byname, joint_names, jidx, out_meshes[0], report)
        Wn = world_with(J(nodes), {})
    IB = [np.linalg.inv(Wn[j]) for j in jidx]
    # ---------- animations ----------
    clips = []
    hips = byname['Hips']; armn = byname[REN.get('Armature', 'Armature')] if 'Armature' in byname else newidx[arm]
    for path, specs in anim_specs:
        ga = GLB(path); gn = ga.j['nodes']; anims = ga.j.get('animations', [])
        for ai, (cname, opts) in enumerate(specs):
            if cname is None or ai >= len(anims): continue
            a = anims[ai]; T = max(ga.acc(s['input']).max() for s in a['samplers']); fac = opts.get('duration', T) / T
            ch = []
            for c in a['channels']:
                nm = REN.get(gn[c['target']['node']].get('name'), gn[c['target']['node']].get('name'))
                if nm not in byname or c['target']['path'] == 'scale': continue
                s = a['samplers'][c['sampler']]; t = ga.acc(s['input']).reshape(-1) * fac; v = ga.acc(s['output']).astype(np.float32)
                if c['target']['path'] == 'translation':
                    if nm != 'Hips': continue
                    v = v.copy()
                    if opts.get('inplace', True):
                        for ax in (0, 2): v[:, ax] -= np.interp(t, [t[0], t[-1]], [v[0, ax] - v[0, ax], v[-1, ax] - v[0, ax]])
                        if opts.get('center', True): v[:, 0] -= v[:, 0].mean() - v[0, 0] * 0; v[:, 2] -= v[:, 2].mean()
                ch.append((byname[nm], c['target']['path'], t.astype(np.float32), v))
            clips.append((cname, ch)); report('  clip %s <- %s #%d (%.2fs -> %.2fs)' % (cname, os.path.basename(path), ai, T, T * fac))
    # transfer approved clips from the old rig (rest poses are identical, so world deltas carry over exactly)
    restR = {i: orth(Wn[i]) for i in range(len(nodes))}; npar = parents(nodes)
    order = []; st = [0]
    while st:
        i = st.pop(0); order.append(i); st += nodes[i].get('children', [])
    srcmap = {byname[n]: oname[n] for n in OLDMAP + extras if n in byname and n in oname}
    oldrest = {oi: orth(Wo[oi]) for oi in srcmap.values()}
    for cname, src_name, opts in transfer:
        a = next(x for x in old.j['animations'] if x['name'] == src_name)
        T = max(old.acc(s['input']).max() for s in a['samplers']); fps = 30; ts = np.linspace(0, T, int(round(T * fps)) + 1)
        rot = {i: [] for i in order if i in jidx}; tra = []
        for t in ts:
            Wt = world_with(old, sample_trs(old, a, t)); Rw = {}
            for i in order:
                p = npar.get(i); Rp = Rw[p] if p is not None else np.eye(3)
                if i in srcmap:
                    oi = srcmap[i]; R = orth(Wt[oi]) @ oldrest[oi].T @ restR[i]
                else:
                    R = Rp @ (restR[p].T @ restR[i] if p is not None else restR[i])
                Rw[i] = R
                if i in rot: rot[i].append(m2q(Rp.T @ R))
            oh = oname['Hips']; dpos = Wt[oh][:3, 3] - Wo[oh][:3, 3]
            tra.append((np.linalg.inv(Wn[npar[hips]]) @ np.r_[Wn[hips][:3, 3] + dpos, 1])[:3])
        ch = [(i, 'rotation', ts.astype(np.float32), qfix(np.array(q)).astype(np.float32)) for i, q in rot.items()]
        ch.append((hips, 'translation', ts.astype(np.float32), np.array(tra, np.float32)))
        clips.append((cname, ch)); report('  clip %s <- old %s (%.2fs, transferred)' % (cname, src_name, T))
    for m in out_meshes:
        m['joint_names'] = joint_names; m['separate_arms'] = fp_arms
        destretch(m, nodes, clips, jidx, IB, report, skip_clips=destretch_skip)
    if fp_arms:   # first-person arms: everything from the collarbones outward, cut from the finished full body
        b = out_meshes[0]; T3 = b['I'].reshape(-1, 3)
        armset = np.array([bool(re.match(r'^(UpperArm|Forearm|Hand|Fingers)', x)) for x in joint_names])
        chain = np.array([bool(re.match(r'^(Clav|UpperArm|Forearm|Hand|Fingers)', x)) for x in joint_names])
        aw = (b['W'] * armset[b['J'].astype(int)]).sum(1)
        # keep only skin that hugs the arm bones: coat flaps, capes and long hair that merely touch the arm would
        # float in front of the camera once the arm is lifted into the aiming pose
        Wn0 = world_with(J(nodes), {}); jp = lambda nm: Wn0[byname[nm]][:3, 3]
        hgt = b['P'][:, 1].max() - b['P'][:, 1].min(); R = .11 * hgt / 1.78; segs = []
        for sd in 'LR':
            c_, u_, f_, h_ = jp('Clav' + sd), jp('UpperArm' + sd), jp('Forearm' + sd), jp('Hand' + sd)
            segs += [(c_, u_), (u_, f_), (f_, h_), (h_, h_ + (h_ - f_) * .75)]
        Pb = b['P'].astype(float); dmin = np.full(len(Pb), 1e9)
        for a_, c2 in segs:
            v_ = c2 - a_; t_ = np.clip(((Pb - a_) @ v_) / (v_ @ v_ + 1e-12), 0, 1); dmin = np.minimum(dmin, np.linalg.norm(Pb - (a_ + t_[:, None] * v_), axis=1))
        near = dmin < R
        keep = ((aw[T3] > .45) & near[T3]).all(1)
        # The first-person arms get their OWN weights: arm chain only. In first person the torso stays where the body
        # was while IK throws the hands forward, so any torso influence would smear a vertex across the screen.
        Jb = b['J'].astype(int); Wb = b['W'] * chain[Jb]; Wb[Wb.sum(1) < 1e-6, 0] = 1
        Wb /= Wb.sum(1, keepdims=True)
        fp = dict(b); fp['name'] = 'FPArms_human'; fp['extras'] = None; fp['I'] = T3[keep].reshape(-1).astype(np.uint32)
        fp['W'] = Wb.astype(np.float32)
        used = np.unique(fp['I']); remap = np.full(len(b['P']), -1, np.int64); remap[used] = np.arange(len(used))   # only the arm vertices
        for key in ('P', 'N', 'UV', 'J', 'W'): fp[key] = fp[key][used]
        fp['I'] = remap[fp['I']].astype(np.uint32)
        out_meshes.append(fp); report('  FPArms_human: %d triangles' % keep.sum())
    nodes, clips, IB = normalize(nodes, clips, jidx, k)
    write(out_path, old, nodes, jidx, IB, out_meshes, clips)
    return dict(nodes=nodes, joints=joint_names)
def open_edges(T):
    """Directed edges of triangles T that have no opposite edge (boundary of the surface)."""
    d = {}
    for a, b, c in T:
        for u, v in ((a, b), (b, c), (c, a)): d[(u, v)] = d.get((u, v), 0) + 1
    return [(u, v) for (u, v) in d if (v, u) not in d]
def split_fingers(nodes, byname, joint_names, jidx, m, report):
    """Generated hands have no finger joints. Classify the hand's vertices into thumb, index finger and the other three
    fingers (spread runs along the model's forward axis in both arms-down and T-pose rests; the thumb sticks forward
    near the wrist, the index is the forward-most finger) and give each group its own bone under the hand."""
    P = m['P'].astype(float); Wd = m['Wd']; Wn = world_with(J(nodes), {})
    for sd in 'LR':
        h = Wn[byname['Hand' + sd]][:3, 3]; f = Wn[byname['Forearm' + sd]][:3, 3]; d = (h - f) / np.linalg.norm(h - f); L = np.linalg.norm(h - f) * .45
        cols = [joint_names.index(x) for x in ('Hand' + sd, 'Fingers' + sd) if x in joint_names]
        hand = Wd[:, cols].sum(1) > .5; along = (P - h) @ d
        z = P[:, 2]; zc = np.median(z[hand & (along > .3 * L)]) if (hand & (along > .3 * L)).sum() > 10 else h[2]
        zs = np.percentile(z[hand], 95) - np.percentile(z[hand], 5) + 1e-6
        thumb = hand & (along > .05 * L) & (along < .75 * L) & (z > zc + .32 * zs)
        fing = hand & (along > .42 * L) & ~thumb
        index = fing & (z > zc + .08 * zs)
        rest = fing & ~index
        if thumb.sum() < 8 or index.sum() < 8 or rest.sum() < 8:
            report('  hand %s: finger split skipped (%d/%d/%d)' % (sd, thumb.sum(), index.sum(), rest.sum())); continue
        for nm, sel, pivot in (('Thumb' + sd, thumb, h + d * .15 * L + np.array([0, 0, .25 * zs])), ('Index' + sd, index, h + d * .45 * L), ('Fingers' + sd, rest, h + d * .45 * L)):
            if nm not in byname:
                Wp = Wn[byname['Hand' + sd]]; loc = np.linalg.inv(Wp) @ np.r_[pivot, 1]
                nodes.append({'name': nm, 'translation': loc[:3].tolist()}); byname[nm] = len(nodes) - 1
                nodes[byname['Hand' + sd]].setdefault('children', []).append(byname[nm]); joint_names.append(nm); jidx.append(byname[nm])
                m['Wd'] = Wd = np.c_[Wd, np.zeros(len(Wd))]
            k = joint_names.index(nm); tot = Wd[sel][:, cols + [k]].sum(1)
            ramp = np.clip((along[sel] - (.05 if nm.startswith('Thumb') else .42) * L) / (.25 * L), 0, 1)
            row = Wd[sel]; row[:, cols] = 0; row[:, k] = 0
            row[:, joint_names.index('Hand' + sd)] += tot * (1 - ramp); row[:, k] += tot * ramp; Wd[sel] = row
        m['Wd'] = Wd; report('  hand %s: thumb %d, index %d, other fingers %d vertices' % (sd, thumb.sum(), index.sum(), rest.sum()))
def weld_ids(P):
    """Vertices split along UV seams share a position: give every vertex the id of its first twin."""
    key = np.round(np.asarray(P, float) / 1e-5).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    return first[inv.reshape(-1)]
def cap_holes(kept, full, dom, wid=None):
    """Close the holes left where arm-leg bridging triangles were removed. Each new boundary loop is split into its
    arm run and its body/leg run and each run is closed on its own with a fan, so neither side stays open."""
    if wid is not None: kept, full = wid[kept], wid[full]
    old_open = set(open_edges(full)); new_open = [e for e in open_edges(kept) if e not in old_open]
    nxt = {}
    for u, v in new_open: nxt.setdefault(u, []).append(v)
    used = set(); caps = []
    side = lambda v: int(dom[v])
    for u0, v0 in new_open:
        if (u0, v0) in used: continue
        loop = [u0]; cur = v0; used.add((u0, v0)); guard = 0
        while cur != u0 and guard < 5000:
            loop.append(cur); cand = [w for w in nxt.get(cur, []) if (cur, w) not in used]
            if not cand: break
            used.add((cur, cand[0])); cur = cand[0]; guard += 1
        if len(loop) < 3: continue
        lab = [side(v) for v in loop]
        if len(set(lab)) == 1: runs = [loop]
        else:   # rotate so a run starts at index 0, then cut into same-side runs
            k = next(i for i in range(len(loop)) if lab[i] != lab[i - 1]); loop = loop[k:] + loop[:k]; lab = lab[k:] + lab[:k]
            runs = []; cur_run = [loop[0]]
            for v, l, lp in zip(loop[1:], lab[1:], lab[:-1]):
                if l == lp: cur_run.append(v)
                else: runs.append(cur_run); cur_run = [v]
            runs.append(cur_run)
        for r in runs:
            for i in range(1, len(r) - 1): caps.append((r[0], r[i + 1], r[i]))   # opposite winding to the open edges
    return np.array(caps, np.int64).reshape(-1, 3)
def clip_over(chans, t):
    from glbio import _slerp
    over = {}
    for node, pth, ts, v in chans:
        tt = min(max(t, ts[0]), ts[-1]); i = int(np.clip(np.searchsorted(ts, tt, side='right') - 1, 0, len(ts) - 1)); j2 = min(i + 1, len(ts) - 1)
        f = 0 if ts[j2] <= ts[i] else (tt - ts[i]) / (ts[j2] - ts[i])
        val = _slerp(v[i].astype(float), v[j2].astype(float), f) if pth == 'rotation' else v[i] * (1 - f) + v[j2] * f
        over.setdefault(node, {})[pth] = np.asarray(val, float)
    return over
def skin_dense(Wd, M, Ph):
    """Linear blend skinning with dense weights (N x nJ) and joint matrices M (nJ x 3 x 4)."""
    A = np.einsum('nj,jab->nab', Wd.astype(np.float32), M)   # per-vertex blended 3x4
    return np.einsum('nab,nb->na', A, Ph.astype(np.float32))
def destretch(m, nodes, clips, jidx, IB, report, frames=24, ratio=2.4, absm=.12, rounds=160, skip_clips=()):
    """Anti-stretch pass on the final weights: sample every clip, find edges that grow too long, and pull the weights of
    both end vertices (and their 1-ring) toward each other until no edge tears. Same idea as tools/wolfgen fix_stretch."""
    P = m['P'].astype(float); I = m['I'].reshape(-1, 3); Wd = m['Wd'].copy(); nJ = Wd.shape[1]
    E = np.unique(np.sort(np.concatenate([I[:, [0, 1]], I[:, [1, 2]], I[:, [2, 0]]]), 1), axis=0)
    Ph = np.c_[P, np.ones(len(P))]; L0 = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1)
    poses = []
    for name, chans in clips:
        if not chans or name in skip_clips: continue
        T = max(float(c[2][-1]) for c in chans)
        for t in np.linspace(0, T, frames):
            W = world_with(J(nodes), clip_over(chans, t)); M = np.stack([W[j] @ IB[q] for q, j in enumerate(jidx)])
            poses.append(M[:, :3].astype(np.float32))   # joint matrices only: skinning is redone per round (low memory)
    nb = [[] for _ in range(len(P))]
    for a, b in E: nb[a].append(b); nb[b].append(a)
    jn = m.get('joint_names') or []
    cloth = np.array([x.startswith(('Cape', 'Tail', 'Hair')) for x in jn]) if jn else None
    remap = {}
    for k, x in enumerate(jn):   # a limb's share on a cloth vertex goes to the torso bone the limb hangs from
        if x.startswith(('UpperArm', 'Forearm', 'Hand', 'Fingers', 'Thumb', 'Index')): remap[k] = jn.index('Clav' + x[-1]) if ('Clav' + x[-1]) in jn else jn.index('Chest')
        elif x.startswith(('Thigh', 'Shin', 'Foot', 'Toe')): remap[k] = jn.index('Hips')
    armc = np.array([x.startswith(('Forearm', 'Hand', 'Fingers', 'Thumb', 'Index')) for x in jn]) if jn else np.zeros(0, bool)
    legc = np.array([x.startswith(('Hips', 'Thigh', 'Shin', 'Foot', 'Toe')) for x in jn]) if jn else np.zeros(0, bool)
    def top4(Wx):   # evaluate exactly what ships: 4 influences per vertex, cloth never follows a limb
        Wx = Wx.copy()
        if cloth is not None and cloth.any():
            cv = Wx[:, cloth].sum(1) > .03
            for k, t in remap.items(): Wx[cv, t] += Wx[cv, k]; Wx[cv, k] = 0
        if m.get('separate_arms') and armc.any():   # humans: a vertex follows either the forearm/hand or the hips/legs, never both
            aw = Wx[:, armc].sum(1); lw = Wx[:, legc].sum(1); both = (aw > .02) & (lw > .02)
            Wx[np.ix_(both & (aw >= lw), np.nonzero(legc)[0])] = 0; Wx[np.ix_(both & (aw < lw), np.nonzero(armc)[0])] = 0
        t = np.argsort(-Wx, 1)[:, 4:]; np.put_along_axis(Wx, t, 0, 1); return Wx / (Wx.sum(1, keepdims=True) + 1e-9)
    Wd = top4(Wd)
    for r in range(rounds):
        badv = set(); worst = 0
        for X in poses:
            Q = skin_dense(Wd, X, Ph); L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1)
            bad = (L > L0 * ratio) & (L - L0 > absm)
            if bad.any(): worst = max(worst, float((L - L0)[bad].max())); badv.update(E[bad].reshape(-1).tolist())
        if not badv:
            report('  %s: no stretched edges after %d anti-stretch rounds' % (m['name'], r)); break
        if r >= 20:   # persistent tears: weld the weights of both ends of every still-stretched edge
            for X in poses:
                Q = skin_dense(Wd, X, Ph); L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1)
                for a, b in E[(L > L0 * ratio) & (L - L0 > absm)]: avg = .5 * (Wd[a] + Wd[b]); Wd[a] = avg; Wd[b] = avg
        bv = np.array(sorted(badv)); ring = set(bv.tolist())
        for v in bv: ring.update(nb[v])
        ring = np.array(sorted(ring)); newW = Wd.copy()
        for v in ring:
            nbs = nb[v]
            if nbs: newW[v] = .5 * Wd[v] + .5 * Wd[nbs].mean(0)
        Wd = top4(newW)
        if r % 10 == 0: report('  %s: anti-stretch round %d, %d vertices, worst +%.2f m' % (m['name'], r, len(bv), worst))
    else:
        report('  %s: WARNING stretched edges remain (worst +%.2f m)' % (m['name'], worst))
        # a hole-cap triangle that spans a bending joint cannot be smoothed: drop just those caps
        nc = m.get('ncap', 0)
        if nc:
            badE = set()
            for X in poses:
                Q = skin_dense(Wd, X, Ph); L = np.linalg.norm(Q[E[:, 0]] - Q[E[:, 1]], axis=1)
                for a, b in E[(L > L0 * ratio) & (L - L0 > absm)]: badE.add((a, b))
            T = m['I'].reshape(-1, 3); capT = T[-nc:]
            drop = np.array([any(tuple(sorted(x)) in badE for x in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))) for t in capT])
            if drop.any():
                m['I'] = np.concatenate([T[:-nc], capT[~drop]]).reshape(-1).astype(np.uint32); m['ncap'] = int((~drop).sum())
                report('  %s: removed %d cap triangles that spanned a bending joint' % (m['name'], drop.sum()))
    Wd = top4(Wd); top = np.argsort(-Wd, 1)[:, :4]; tw = np.take_along_axis(Wd, top, 1); tw /= tw.sum(1, keepdims=True) + 1e-9
    m['J'] = top.astype(np.uint16); m['W'] = tw.astype(np.float32)
def normalize(nodes, clips, jidx, k):
    """Make every bone world-aligned at rest, in metres (like the engine's original rig): rest rotations become identity,
    the 0.01 armature scale is folded into translations, animation rotations are re-expressed so the motion is unchanged."""
    W = world_with(J(nodes), {}); par = parents(nodes)
    sub = set(); st = list(nodes[0].get('children', []))
    while st:
        i = st.pop(); sub.add(i); st += nodes[i].get('children', [])
    Rw = {i: orth(W[i]) for i in sub}; Rw[0] = np.eye(3)
    pos = {i: W[i][:3, 3] for i in sub}; pos[0] = np.zeros(3)
    arm = [i for i in nodes[0]['children'] if i in sub][0]; s_arm = np.linalg.norm(W[arm][:3, 0]) / k
    for i in sub:
        nd = nodes[i]; p = par[i]
        for kk in ('rotation', 'scale', 'matrix'): nd.pop(kk, None)
        nd['translation'] = ((pos[i] - pos[p]) / k).tolist()
    newclips = []
    for name, chans in clips:
        nc = []
        for node, pth, t, v in chans:
            if node not in sub: continue
            if pth == 'rotation':
                Rp = Rw[par[node]]; Rj = Rw[node]
                q = [m2q(Rp @ _q2m(np.asarray(x, float)) @ Rj.T) for x in v]
                nc.append((node, pth, t, qfix(np.array(q)).astype(np.float32)))
            elif pth == 'translation' and par[node] == arm:
                nc.append((node, pth, t, (np.asarray(v, float) @ Rw[arm].T * s_arm).astype(np.float32)))
        newclips.append((name, nc))
    W2 = world_with(J(nodes), {}); IB = [np.linalg.inv(W2[j]) for j in jidx]
    return nodes, newclips, IB
def write(path, old, nodes, jidx, IB, meshes, clips):
    bufs = []; views = []; accs = []
    def blob(b, target=None):
        o = sum(len(x) for x in bufs); pad = b'\0' * ((4 - len(b) % 4) % 4); bufs.append(b + pad)
        v = dict(buffer=0, byteOffset=o, byteLength=len(b)); target and v.update(target=target); views.append(v); return len(views) - 1
    def acc(arr, typ, ct, target=None, mm=False):
        arr = np.ascontiguousarray(arr); a = dict(bufferView=blob(arr.tobytes(), target), componentType=ct, count=len(arr), type=typ)
        if mm: a.update(min=np.atleast_1d(arr.min(0)).tolist(), max=np.atleast_1d(arr.max(0)).tolist())
        accs.append(a); return len(accs) - 1
    j = dict(asset=dict(version='2.0', generator='rbm meshy pipeline'), scene=0, scenes=[dict(nodes=[0])], nodes=[dict(n) for n in nodes])
    # images / textures / materials copied verbatim from the old game model
    imgs = []
    for im in old.j.get('images', []):
        raw = old.view_bytes(im['bufferView']); mime = im.get('mimeType', 'image/png')
        if len(raw) > 1_500_000:   # Meshy ships 2k PNG maps: 1k JPEG keeps the APK small and looks the same on a phone
            from PIL import Image as _I; import io as _io
            pic = _I.open(_io.BytesIO(raw))
            if pic.mode in ('RGBA', 'LA') and pic.getextrema()[-1][0] < 250: pic = None   # real transparency: keep PNG
            if pic is not None:
                pic = pic.convert('RGB'); pic.thumbnail((1024, 1024), _I.LANCZOS); b = _io.BytesIO(); pic.save(b, 'JPEG', quality=88); raw = b.getvalue(); mime = 'image/jpeg'
        imgs.append(dict(bufferView=blob(raw), mimeType=mime))
    j['images'] = imgs; j['textures'] = old.j.get('textures', []); j['samplers'] = old.j.get('samplers', []); j['materials'] = old.j.get('materials', [])
    j['skins'] = [dict(joints=jidx, inverseBindMatrices=acc(np.array([m.T.reshape(-1) for m in IB], np.float32), 'MAT4', 5126), skeleton=jidx[0])]
    j['meshes'] = []
    for m in meshes:
        attrs = dict(POSITION=acc(m['P'], 'VEC3', 5126, 34962, True), NORMAL=acc(m['N'], 'VEC3', 5126, 34962), TEXCOORD_0=acc(m['UV'], 'VEC2', 5126, 34962),
                     JOINTS_0=acc(m['J'], 'VEC4', 5123, 34962), WEIGHTS_0=acc(m['W'], 'VEC4', 5126, 34962))
        j['meshes'].append(dict(name=m['name'], primitives=[dict(attributes=attrs, indices=acc(m['I'], 'SCALAR', 5125, 34963), material=m['mat'])]))
        nd = dict(name=m['name'], mesh=len(j['meshes']) - 1, skin=0); m['extras'] and nd.update(extras=m['extras'])
        j['nodes'].append(nd); j['nodes'][0]['children'].append(len(j['nodes']) - 1)
    j['animations'] = []
    from glbio import _slerp
    def resample(chans, fps=30):
        T = max(float(t[-1]) for _, _, t, _ in chans); ts = np.linspace(0, T, max(2, int(round(T * fps)) + 1)).astype(np.float32); out = []
        for node, pth, t, v in chans:
            if len(t) == len(ts) and np.allclose(t, ts, atol=1e-4): out.append((node, pth, ts, v)); continue
            idx = np.clip(np.searchsorted(t, ts, side='right') - 1, 0, len(t) - 1); nx = np.minimum(idx + 1, len(t) - 1)
            f = np.where(t[nx] > t[idx], (ts - t[idx]) / np.maximum(t[nx] - t[idx], 1e-9), 0).clip(0, 1)
            if pth == 'rotation': vv = np.array([_slerp(v[a].astype(float), v[b].astype(float), c) for a, b, c in zip(idx, nx, f)], np.float32)
            else: vv = (v[idx] * (1 - f[:, None]) + v[nx] * f[:, None]).astype(np.float32)
            out.append((node, pth, ts, vv))
        return out
    clips = [(n, resample(c)) for n, c in clips if c]
    for name, chans in clips:
        samp = []; chs = []; tin = acc(chans[0][2].reshape(-1, 1), 'SCALAR', 5126, None, True)
        for node, pth, t, v in chans:
            samp.append(dict(input=tin, output=acc(v, 'VEC4' if pth == 'rotation' else 'VEC3', 5126), interpolation='LINEAR'))
            chs.append(dict(sampler=len(samp) - 1, target=dict(node=node, path=pth)))
        j['animations'].append(dict(name=name, samplers=samp, channels=chs))
    bn = b''.join(bufs); j['buffers'] = [dict(byteLength=len(bn))]; j['bufferViews'] = views; j['accessors'] = accs
    js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bn))); f.write(struct.pack('<I', len(js)) + b'JSON' + js); f.write(struct.pack('<I', len(bn)) + b'BIN\0' + bn)
