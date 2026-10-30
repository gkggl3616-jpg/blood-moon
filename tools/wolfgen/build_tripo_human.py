"""Rig any A-pose Tripo human with the shared human skeleton: joints are placed from anthropometric heights and the
mesh's own limb cross-sections, then the shared human clips / first-person arms / anti-stretch pass are applied.
usage: build_tripo_human.py src.glb out.glb mask(lava|ember|none)"""
import sys, os
import numpy as np
import build_human as bh
from prep_tripo import prep
from core import attach_detail_maps

H = 1.785                     # shoulders end up at Bilge's height so the first-person arm placement matches
MASKS = {'lava': lambda c: (c[..., 0] > .6) & (c[..., 1] > .12) & (c[..., 1] < .55) & (c[..., 2] < .25) & ((c[..., 0] - c[..., 1]) > .25),
         'ember': lambda c: (c[..., 0] > .75) & (c[..., 1] > .25) & (c[..., 1] < .6) & (c[..., 2] < .25),
         'none': lambda c: np.zeros(c.shape[:-1], bool)}


def centroid(P, y, cond, band=.025):
    m = (np.abs(P[:, 1] - y) < band) & cond
    return P[m].mean(0) if m.sum() > 4 else None


def fit(P):
    J = {}
    for name, f in (('Hips', .53), ('Spine', .61), ('Chest', .71), ('Neck', .855), ('Head', .9)):
        c = centroid(P, f * H, np.abs(P[:, 0]) < .12); J[name] = (0, f * H, float(c[2]) if c is not None else 0)
    sh = .818 * H; front = P[:, 2] > -.06                          # capes/mantles hang behind: look at the front half only
    tw = np.percentile(np.abs(P[(np.abs(P[:, 1] - .72 * H) < .02) & front & (np.abs(P[:, 0]) < .3), 0]), 85)
    def arm(f):
        c = centroid(P, f * H, (P[:, 0] > tw + .02) & front)
        if c is None: c = centroid(P, f * H, (P[:, 0] > tw - .02) & front)
        return c
    up, el, wr = arm(.80), arm(.63), arm(.485); tip = arm(.40)
    J['Clav'] = (.07, sh - .02, J['Chest'][2]); J['UpperArm'] = (float(up[0]) - .01, sh - .03, float(up[2]))
    J['Forearm'] = tuple(float(v) for v in el); J['Hand'] = tuple(float(v) for v in wr)
    leg = lambda f: centroid(P, f * H, (P[:, 0] > .03) & (P[:, 0] < .3))
    th, kn, an = leg(.5), leg(.285), leg(.06)
    J['Thigh'] = (float(th[0]) - .02, .515 * H, float(th[2])); J['Shin'] = tuple(float(v) for v in kn); J['Foot'] = tuple(float(v) for v in an)
    tips = dict(HAND_TIP=tuple(float(v) for v in (tip if tip is not None else wr - [0, .12, 0])),
                KNUCKLE=tuple(float(v) for v in ((np.asarray(wr) + (tip if tip is not None else wr - [0, .12, 0])) / 2)),
                TOE=(float(an[0]), .01, float(an[2]) + .14), HEAD_TIP=(0, H - .04, J['Head'][2]))
    return J, tips


if __name__ == '__main__':
    src, out, mask = sys.argv[1], sys.argv[2], sys.argv[3]; cell = float(sys.argv[4]) if len(sys.argv) > 4 else .011
    pre = '/tmp/' + os.path.basename(src).replace('.glb', '') + '_prep'
    prep(src, pre + '.npz', H, cell)
    P = np.load(pre + '.npz')['P']; J, tips = fit(P)
    for k, v in J.items(): print(f'  {k:9s}', np.round(v, 3))
    bh.HJ.update(J); [setattr(bh, k, v) for k, v in tips.items()]
    bh.ICE_MASK = MASKS[mask]
    bh.ARM_TOP = J['UpperArm'][1] - .1
    from rig import seg_dist
    def _excl(Q):   # first-person arms = the arm itself: drop capes / hair / cloth that merely touch it
        d = np.full(len(Q), 9.0)
        for sx in (1, -1):
            m = lambda p: np.array([p[0] * sx, p[1], p[2]])
            pts = [m(J['UpperArm']), m(J['Forearm']), m(J['Hand']), m(tips['HAND_TIP'])]
            for a_, b_ in zip(pts[:-1], pts[1:]): d = np.minimum(d, seg_dist(Q, a_, b_))
        return ((Q[:, 2] < -.07) & (np.abs(Q[:, 0]) < .24)) | (d > .1)
    bh.ARM_EXCLUDE = _excl
    S, M = bh.make(pre + '.npz', pre + '_tex.jpg'); attach_detail_maps(M, pre)
    bh.write_glb(out, S, M, bh.bake_human(S), 'Body_human', extras=dict(previewHeight=H), parts={'Body_human': ['Human_body'], 'FPArms_human': ['Human_arms']})
    print(out, os.path.getsize(out), 'tris', len(M.tris))
