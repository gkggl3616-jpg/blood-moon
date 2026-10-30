import numpy as np, sys
from core import *
from PIL import Image, ImageDraw
d = np.load('/tmp/wolf_prep.npz'); P = d['P']; T = d['T']; UV = d['UV']
tex = np.array(Image.open('/tmp/wolf_prep_tex.jpg')); u = (UV[:, 0] % 1 * (tex.shape[1] - 1)).astype(int); v = (UV[:, 1] % 1 * (tex.shape[0] - 1)).astype(int)
col = tex[v, u] / 255.0
S = Skeleton(); S.add('Root', None, (0, 0, 0)); M = Mesh(S); M.material('m', (1, 1, 1))
M.add_part(P, T, {'Root': 1.0}, (1, 1, 1), 'm'); M.C = [list(c) + [1.0] for c in col]
def views(pose=None, root_t=(0, 0, 0), size=(560, 760), ss=1):
    return [render(S, M, pose or {}, root_t, yaw=y, pitch=0, size=size, ss=ss, center=np.array([0, .93, 0]), scale=1.0) for y in (0, 90)]
if __name__ == '__main__':
    a, b = views()
    W, H = a.size; s = min(W, H) * .46 / 1.0
    for im in (a, b):
        dr = ImageDraw.Draw(im)
        for y in np.arange(0, 2.0, .1):
            Y = -(y - .93) * s + H / 2; dr.line([(0, Y), (W, Y)], fill=(80, 90, 60) if abs(y * 10 % 5) > .01 else (160, 160, 60), width=1)
            if round(y * 10) % 2 == 0: dr.text((2, Y - 10), f'{y:.1f}', fill=(255, 255, 0))
        for x in np.arange(-.6, .61, .1):
            X = x * s + W / 2; dr.line([(X, 0), (X, H)], fill=(60, 80, 90), width=1)
            if round(x * 10) % 2 == 0: dr.text((X + 2, H - 14), f'{x:.1f}', fill=(120, 220, 255))
    im = Image.new('RGB', (1120, 760)); im.paste(a, (0, 0)); im.paste(b, (560, 0)); im.save('/tmp/prep_grid.png')
