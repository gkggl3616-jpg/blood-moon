"""Ay Kurdu (female moon wolf): rig the Tripo mesh with the shared engine skeleton and bake the shared clips."""
import os
import numpy as np
import rig, build_icewolf as bi
from core import write_glb

rig.J.update(Hips=(0, .95, .04), Spine=(0, 1.10, .05), Chest=(0, 1.28, .06), Neck=(0, 1.48, .06), Head=(0, 1.60, .07), Jaw=(0, 1.58, .15),
             Clav=(.08, 1.42, .05), UpperArm=(.18, 1.42, .06), Forearm=(.23, 1.12, .08), Hand=(.28, .88, .14),
             Thigh=(.10, .92, .06), Shin=(.15, .50, .06), Foot=(.19, .12, .06),
             Tail1=(0, .97, -.14), Tail2=(.05, .80, -.30), Tail3=(.20, .58, -.38))
rig.JR = {}; rig.HAND_TIP_R = rig.HAND_TIP = (.30, .74, .13)
rig.HEAD_TIP = (0, 1.60, .33); rig.TOE_TIP = (.20, .01, .19); rig.TAIL_TIP = (.36, .42, -.44)
bi.ICE_MASK = lambda c: (c[..., 2] > .78) & (c[..., 0] > .5) & ((c[..., 2] - c[..., 1]) > .16) & (c[..., :3].mean(-1) > .6)   # glowing violet moon marks

if __name__ == '__main__':
    S, M = bi.make_mesh('/tmp/aywolf_prep.npz', '/tmp/aywolf_prep_tex.jpg')
    M.materials['Fur_icewolf']['emissive'] = [.5, .5, .5]
    # braid physics chain (engine spring bones Hair1-3): the braid hangs from the right side of the head over the shoulder
    S.add('Hair1', 'Head', (-.15, 1.62, .06)); S.add('Hair2', 'Hair1', (-.24, 1.45, .12)); S.add('Hair3', 'Hair2', (-.29, 1.28, .14))
    P = np.asarray(M.P); h = [S.idx(n) for n in ('Head', 'Hair1', 'Hair2', 'Hair3')]
    braid = ((P[:, 0] < -.17) & (P[:, 1] > 1.47) & (P[:, 1] < 1.66)) | ((P[:, 0] < -.265) & (P[:, 1] > 1.1) & (P[:, 1] <= 1.47) & (P[:, 2] > .04))
    for i in np.where(braid)[0]:
        y = P[i, 1]
        if y > 1.56: w = [(h[0], .6), (h[1], .4)]
        elif y > 1.45: k = (1.56 - y) / .11; w = [(h[1], 1 - .5 * k), (h[2], .5 * k)]
        elif y > 1.28: k = (1.45 - y) / .17; w = [(h[2], 1 - .5 * k), (h[3], .5 * k)]
        else: w = [(h[3], 1.0)]
        M.J[i] = [b for b, _ in w] + [0] * (4 - len(w)); M.W[i] = [x for _, x in w] + [0] * (4 - len(w))
    print('braid verts', int(braid.sum()))
    clips = {n: bi.bake(S, n) for n in bi.CLIPS}
    extras = dict(source_kind='new_ay', clawProfile='standard', previewHeight=1.85, run_stride_m=3.2, run_reference_speed_mps=8.0)
    write_glb('/tmp/aywolf_rigged.glb', S, M, clips, 'Body_ay', extras=extras)
    print('glb', os.path.getsize('/tmp/aywolf_rigged.glb'), 'tris', len(M.tris))
