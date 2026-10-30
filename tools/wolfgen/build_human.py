"""Rig the generated human (ice warrior) with the engine skeleton, split a first-person arms mesh, bake HumanIdle/HumanReady."""
import io, math
import numpy as np
from core import *
from anim import add, sm
from PIL import Image
from scipy.ndimage import binary_dilation

HJ = dict(Hips=(0, .95, -.01), Spine=(0, 1.10, -.01), Chest=(0, 1.28, 0), Neck=(0, 1.52, .0), Head=(0, 1.62, .02),
          Clav=(.08, 1.46, -.01), UpperArm=(.20, 1.46, -.02), Forearm=(.28, 1.18, -.07), Hand=(.355, .955, .03),
          Thigh=(.10, .94, -.01), Shin=(.12, .56, .03), Foot=(.12, .10, -.04))
HAND_TIP = (.37, .785, .06); KNUCKLE = (.372, .872, .045); TOE = (.12, .02, .14); HEAD_TIP = (0, 1.78, .03)


def skeleton():
    s = Skeleton(); s.add('Root', None, (0, 0, 0)); s.add('Hips', 'Root', HJ['Hips']); s.add('Spine', 'Hips', HJ['Spine']); s.add('Chest', 'Spine', HJ['Chest'])
    s.add('Neck', 'Chest', HJ['Neck']); s.add('Head', 'Neck', HJ['Head'])
    for sx, L in ((1, 'L'), (-1, 'R')):
        m = lambda p: (p[0] * sx, p[1], p[2])
        s.add('Clav' + L, 'Chest', m(HJ['Clav'])); s.add('UpperArm' + L, 'Clav' + L, m(HJ['UpperArm'])); s.add('Forearm' + L, 'UpperArm' + L, m(HJ['Forearm'])); s.add('Hand' + L, 'Forearm' + L, m(HJ['Hand'])); s.add('Fingers' + L, 'Hand' + L, m(KNUCKLE))
        s.add('Thigh' + L, 'Hips', m(HJ['Thigh'])); s.add('Shin' + L, 'Thigh' + L, m(HJ['Shin'])); s.add('Foot' + L, 'Shin' + L, m(HJ['Foot']))
    return s


def segs(s):
    p = {n: s.pos[i] for i, n in enumerate(s.names)}
    out = {'Hips': (p['Hips'], p['Spine'], .19), 'Spine': (p['Spine'], p['Chest'], .19), 'Chest': (p['Chest'], p['Neck'], .22), 'Neck': (p['Neck'], p['Head'], .09), 'Head': (p['Head'], np.array(HEAD_TIP), .16)}
    for sx, L in ((1, 'L'), (-1, 'R')):
        m = lambda q: np.array((q[0] * sx, q[1], q[2]))
        out['Clav' + L] = (p['Clav' + L], p['UpperArm' + L], .10); out['UpperArm' + L] = (p['UpperArm' + L], p['Forearm' + L], .09)
        out['Forearm' + L] = (p['Forearm' + L], p['Hand' + L], .08); out['Hand' + L] = (p['Hand' + L], p['Fingers' + L], .07); out['Fingers' + L] = (p['Fingers' + L], m(HAND_TIP), .05)
        out['Thigh' + L] = (p['Thigh' + L], p['Shin' + L], .13); out['Shin' + L] = (p['Shin' + L], p['Foot' + L], .09); out['Foot' + L] = (p['Foot' + L], m(TOE), .08)
    return out


def weights(S, P, sharp=2.4):
    from rig import seg_dist
    sg = segs(S); names = list(sg)
    D = np.stack([seg_dist(P, *sg[n][:2]) / sg[n][2] for n in names], 1)
    for k, n in enumerate(names):
        if n.endswith('L'): D[:, k] += np.where(P[:, 0] < -.03, 3.0, 0)
        if n.endswith('R'): D[:, k] += np.where(P[:, 0] > .03, 3.0, 0)
    W = np.exp(-(D ** 2) * sharp); W /= np.maximum(W.sum(1, keepdims=True), 1e-9)
    idx = np.argsort(-W, 1)[:, :4]; w = np.take_along_axis(W, idx, 1); w /= w.sum(1, keepdims=True)
    return np.array([[S.idx(names[i]) for i in r] for r in idx], np.uint16), w.astype(np.float32)


def make(prep='/tmp/human_prep.npz', texpath='/tmp/human_prep_tex.jpg'):
    d = np.load(prep); P = d['P']; Nn = d['N']; UV = d['UV']; T = d['T']
    S = skeleton(); Jn, Wn = weights(S, P)
    tex = Image.open(texpath).convert('RGB'); ta = np.array(tex)
    u = (UV[:, 0] % 1 * (ta.shape[1] - 1)).astype(int); v = (UV[:, 1] % 1 * (ta.shape[0] - 1)).astype(int); col = ta[v, u] / 255.0
    ice = ((col[:, 2] - col[:, 0]) > .10) & (col[:, 2] > .55)
    for i in np.where(ice)[0]:
        L = 'L' if P[i, 0] >= 0 else 'R'; sx = 1 if L == 'L' else -1
        el = np.array([HJ['Forearm'][0] * sx, HJ['Forearm'][1], HJ['Forearm'][2]]); kn = np.array([HJ['Shin'][0] * sx, HJ['Shin'][1], HJ['Shin'][2]])
        if np.linalg.norm(P[i] - el) < .15: Jn[i] = [S.idx('Forearm' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
        elif np.linalg.norm(P[i] - kn) < .17: Jn[i] = [S.idx('Shin' + L), 0, 0, 0]; Wn[i] = [1, 0, 0, 0]
    # first-person arms: triangles whose three vertices are driven mainly by upper/forearm/hand bones
    arm_ids = {S.idx(n + L) for n in ('UpperArm', 'Forearm', 'Hand', 'Fingers') for L in 'LR'}
    dom = Jn[:, 0]; armv = np.array([d_ in arm_ids for d_ in dom]) & (P[:, 1] < 1.42)
    armt = armv[T].all(1)
    M = Mesh(S); M.material('Human_body', (1, 1, 1), roughness=.85, textured=True); M.material('Human_arms', (1, 1, 1), roughness=.85, textured=True)
    M.P = [p for p in P]; M.N = [n for n in normalize(Nn)]; M.J = Jn.tolist(); M.W = Wn.tolist(); M.C = [list(c) + [1.0] for c in col]; M.M = ['Human_body'] * len(P)
    M.tris = [t.tolist() + ['Human_arms' if a else 'Human_body'] for t, a in zip(T, armt)]
    M.UV = UV; M.texture = open(texpath, 'rb').read()
    t = ta.astype(float) / 255.0; mask = binary_dilation(((t[..., 2] - t[..., 0]) > .10) & (t[..., 2] > .55), iterations=1)
    buf = io.BytesIO(); Image.fromarray((t * mask[..., None] * 255).astype(np.uint8)).save(buf, 'PNG', optimize=True); M.emissive_tex = buf.getvalue()
    for k in ('Human_body', 'Human_arms'): M.materials[k]['emissive'] = [.35, .35, .35]
    print('arm tris', int(armt.sum()), 'of', len(T))
    return S, M


def human_idle(t):
    p = {}; b = math.sin(t * 2 * math.pi)
    add(p, 'Spine', 1.0 + .6 * b); add(p, 'Chest', .8 * b); add(p, 'Neck', -.5 * b)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, 2 * b, 0, -s * .8 * b); add(p, 'Forearm' + L, -5 - 1.5 * b)
    return p


FP_SCALE = 1.3; FP_OFF = np.array([0, 0, -.25])
TARGET = {'R': np.array([.21, -.31, -.50]), 'L': np.array([.04, -.36, -.82])}   # wrist targets in viewmodel (camera) space


def cam_to_model(p, head):
    q = (np.asarray(p) - FP_OFF) / FP_SCALE            # undo offset/scale
    return np.array([-q[0], q[1], -q[2]]) + np.asarray(head)   # undo Ry(pi) then re-centre on the head joint


def solve_arm(S, L, sx):
    sh = S.pos[S.idx('UpperArm' + L)]; el = S.pos[S.idx('Forearm' + L)]; ha = S.pos[S.idx('Hand' + L)]
    l1 = np.linalg.norm(el - sh); l2 = np.linalg.norm(ha - el)
    tgt = cam_to_model(TARGET[L], S.pos[S.idx('Head')])
    v = tgt - sh; d = np.linalg.norm(v); u = v / d; d = min(d, l1 + l2 - 1e-3)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = np.sqrt(max(l1 * l1 - a * a, 0))
    pole = np.array([sx * .9, -.2, -.5]); pole = pole - u * np.dot(pole, u); pole /= np.linalg.norm(pole)
    elbow = sh + u * a + pole * h; wrist = sh + u * d
    qu = qrot_between(el - sh, elbow - sh); qf = qrot_between(ha - el, wrist - elbow)
    return qu, qmul(qinv(qu), qf)


def human_ready(t):
    S_ = human_ready.S; p = {}; b = math.sin(t * 2 * math.pi)
    for sx, L in ((1, 'L'), (-1, 'R')):
        qu, qf = solve_arm(S_, L, sx); p['UpperArm' + L] = tuple(qu); p['Forearm' + L] = tuple(qf)
        add(p, 'Hand' + L, -8 + 2 * b, 0, sx * -10)
        add(p, 'Fingers' + L, 0, 0, -sx * (68 + 3 * b))   # curl around the weapon grip / handguard
    add(p, 'Spine', 1 + .4 * b)
    return p


def human_ready_old(t):
    """FPS stance: both forearms raised forward, hands at lower-centre of the screen, slight breathing sway."""
    p = {}; b = math.sin(t * 2 * math.pi)
    add(p, 'Spine', 3 + .5 * b); add(p, 'Chest', 1 + .5 * b)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'Clav' + L, 0, 0, s * -4); add(p, 'UpperArm' + L, -38 + 1.5 * b, 14 * s, -s * 4); add(p, 'Forearm' + L, -78 - 1.5 * b, 8 * s, -s * 8); add(p, 'Hand' + L, -10, 0, s * 4)
    return p


def bake_human(S, fps=30):
    human_ready.S = S; clips = {}
    for name, fn, dur in (('HumanIdle', human_idle, 2.4), ('HumanReady', human_ready, 2.4)):
        n = int(dur * fps); fr = []
        for k in range(n):
            pose = fn(k / n); jw = S.joint_world(pose)
            fr.append((pose, (0, -(min(jw['FootL'][1], jw['FootR'][1]) - .10) + .0, 0)))
        clips[name] = dict(duration=dur, frames=fr)
    return clips


if __name__ == '__main__':
    S, M = make(); clips = bake_human(S)
    write_glb('/tmp/human_rigged.glb', S, M, clips, 'Body_human', extras=dict(previewHeight=1.78), parts={'Body_human': ['Human_body'], 'FPArms_human': ['Human_arms']})
    import os; print('glb', os.path.getsize('/tmp/human_rigged.glb'))
