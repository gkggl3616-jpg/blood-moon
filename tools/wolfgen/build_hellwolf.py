"""Hellgate Kurdu from the approved Higgsfield design (Tripo mesh): shared skeleton/clips, lava-vein emissive mask,
normal + roughness maps for the fur/muscle relief. The mesh already carries the horns and the growing spine spikes."""
import os
import numpy as np
import rig, build_icewolf as bi
from core import write_glb, attach_detail_maps

rig.J.update(Hips=(0, 1.0, .02), Spine=(0, 1.15, 0), Chest=(0, 1.33, -.01), Neck=(0, 1.55, -.02), Head=(0, 1.68, .02), Jaw=(0, 1.62, .15),
             Clav=(.10, 1.47, -.01), UpperArm=(.26, 1.45, -.01), Forearm=(.40, 1.16, -.03), Hand=(.34, .86, .05),
             Thigh=(.13, .98, .04), Shin=(.16, .60, .02), Foot=(.23, .15, -.12),
             Tail1=(0, .90, -.55), Tail2=(0, .80, -.65), Tail3=(0, .70, -.72))     # the design has no tail: keep tail bones clear of the body
rig.JR = {}; rig.HAND_TIP_R = rig.HAND_TIP = (.36, .70, .07)
rig.HEAD_TIP = (0, 1.60, .34); rig.TOE_TIP = (.25, .0, .12); rig.TAIL_TIP = (0, .62, -.78)
bi.ICE_MASK = lambda c: (c[..., 0] > .6) & (c[..., 1] > .12) & (c[..., 1] < .55) & (c[..., 2] < .25) & ((c[..., 0] - c[..., 1]) > .25)   # glowing lava veins

if __name__ == '__main__':
    S, M = bi.make_mesh('/tmp/hgwolf_prep.npz', '/tmp/hgwolf_prep_tex.jpg')
    M.materials['Fur_icewolf']['emissive'] = [.45, .45, .45]
    attach_detail_maps(M, '/tmp/hgwolf_prep')
    clips = {n: bi.bake(S, n) for n in bi.CLIPS}
    extras = dict(source_kind='new_hellgate', clawProfile='standard', previewHeight=1.9, run_stride_m=3.2, run_reference_speed_mps=8.0)
    write_glb('/tmp/hgwolf_rigged.glb', S, M, clips, 'Body_hellgate', extras=extras)
    print('glb', os.path.getsize('/tmp/hgwolf_rigged.glb'), 'tris', len(M.tris))
