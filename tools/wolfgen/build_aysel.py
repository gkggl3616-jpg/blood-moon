"""Aysel (Ay Kurdu human form): rig the Tripo mesh with the shared human skeleton/clips and first-person arms."""
import os
import build_human as bh
k = 1.794 / 1.72   # prepared at Bilge's shoulder height so the first-person arm placement matches
J = dict(Hips=(0, .93, 0), Spine=(0, 1.08, 0), Chest=(0, 1.26, 0), Neck=(0, 1.46, -.01), Head=(0, 1.56, 0),
         Clav=(.07, 1.41, -.02), UpperArm=(.17, 1.40, -.03), Forearm=(.23, 1.10, -.01), Hand=(.25, .88, .06),
         Thigh=(.10, .90, 0), Shin=(.15, .50, 0), Foot=(.20, .10, -.03))
bh.HJ.update({n: tuple(v * k for v in p) for n, p in J.items()})
bh.HAND_TIP = tuple(v * k for v in (.24, .72, .06)); bh.KNUCKLE = tuple(v * k for v in (.245, .80, .07))
bh.TOE = tuple(v * k for v in (.20, .02, .13)); bh.HEAD_TIP = tuple(v * k for v in (0, 1.72, 0))
bh.ICE_MASK = lambda c: (c[..., 2] > .82) & (c[..., 0] > .55) & ((c[..., 2] - c[..., 1]) > .2) & (c[..., :3].mean(-1) > .62)   # glowing crescent marks only, not the lavender hair
import numpy as np
bh.ARM_EXCLUDE = lambda P: (P[:, 2] < -.08) & (np.abs(P[:, 0]) < .2)   # ponytail hanging behind the shoulders
if __name__ == '__main__':
    S, M = bh.make('/tmp/aysel_prep.npz', '/tmp/aysel_prep_tex.jpg'); clips = bh.bake_human(S)
    bh.write_glb('/tmp/aysel_rigged.glb', S, M, clips, 'Body_human', extras=dict(previewHeight=1.79), parts={'Body_human': ['Human_body'], 'FPArms_human': ['Human_arms']})
    print('glb', os.path.getsize('/tmp/aysel_rigged.glb'), 'tris', len(M.tris))
