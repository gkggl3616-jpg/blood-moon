"""Rebuild every shipped character model from source with the anti-stretch pass, then install it."""
import os, subprocess, sys
M = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'app', 'src', 'main', 'assets', 'models')
def sh(*a): subprocess.run([sys.executable, *a], check=True, cwd=os.path.dirname(os.path.abspath(__file__)), stdout=subprocess.DEVNULL)
def scale(src, name, k): sh('scale_glb.py', src, os.path.join(M, name), str(k))
sh('build_icewolf.py'); scale('/tmp/icewolf_rigged.glb', 'bilge.glb', 1.4)
sh('build_variant.py', 'fire', 'king', 'hell')
scale('/tmp/wolf_fire.glb', 'ates.glb', 1.4); scale('/tmp/wolf_king.glb', 'kral.glb', 1.55); scale('/tmp/wolf_hell.glb', 'hellgate.glb', 1.45)
sh('build_aywolf.py'); scale('/tmp/aywolf_rigged.glb', 'ay.glb', 1.3)
import build_human as bh
for tex, name in (('/tmp/human_prep_tex.jpg', 'human-bilge'), ('/tmp/human_tex_fire.jpg', 'human-ates'), ('/tmp/human_tex_king.jpg', 'human-kral')):
    S, Mm = bh.make(texpath=tex); bh.write_glb(os.path.join(M, name + '.glb'), S, Mm, bh.bake_human(S), 'Body_human', extras=dict(previewHeight=1.78), parts={'Body_human': ['Human_body'], 'FPArms_human': ['Human_arms']})
default_mask = bh.ICE_MASK
bh.ICE_MASK = lambda c: (c[..., 0] > .5) & (c[..., 1] < .4) & (c[..., 2] < .12) & ((c[..., 0] - c[..., 1]) > .3)
S, Mm = bh.make(texpath='/tmp/human_tex_hell.jpg'); bh.write_glb(os.path.join(M, 'human-hellgate.glb'), S, Mm, bh.bake_human(S), 'Body_human', extras=dict(previewHeight=1.78), parts={'Body_human': ['Human_body'], 'FPArms_human': ['Human_arms']})
bh.ICE_MASK = default_mask
sh('build_aysel.py'); import shutil; shutil.copy('/tmp/aysel_rigged.glb', os.path.join(M, 'human-ay.glb'))
print('all models rebuilt')
