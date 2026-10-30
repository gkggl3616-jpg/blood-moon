"""Render N frames of every animation in a GLB (front + side) into one sheet."""
import sys, os, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__)); from glbio import GLB, sample_trs, world_with, skin
from preview import draw
def frames(path, n=5, size=220, side=True, clips=None):
    g = GLB(path); rows = []
    anims = g.j.get('animations', []) or [None]
    for a in anims:
        if a is not None and clips and a.get('name') not in clips: continue
        T = max(g.acc(s['input']).max() for s in a['samplers']) if a else 0
        ims = []
        for k in range(n):
            t = T * k / max(1, n - 1) if a else 0; W = world_with(g, sample_trs(g, a, t) if a else {}); P, I = skin(g, W)
            im = draw(P, I, size, side=False); ims.append(im)
            if side: ims.append(draw(P, I, size, side=True))
        row = Image.new('RGB', (size * len(ims), size + 14), (18, 18, 22)); [row.paste(im, (size * i, 14)) for i, im in enumerate(ims)]
        ImageDraw.Draw(row).text((4, 1), '%s  %s  %.2fs' % (os.path.basename(os.path.dirname(path)) + '/' + os.path.basename(path), a.get('name') if a else 'rest', T), fill=(255, 220, 120)); rows.append(row)
    return rows
if __name__ == '__main__':
    out = sys.argv[1]; rows = []
    for p in sys.argv[2:]: rows += frames(p)
    S = Image.new('RGB', (max(r.width for r in rows), sum(r.height for r in rows))); y = 0
    for r in rows: S.paste(r, (0, y)); y += r.height
    S.save(out); print(out, S.size)
