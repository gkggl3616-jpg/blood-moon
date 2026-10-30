"""Rasterise a mesh into its UV space: per-texel 3D position (+coverage). Used to paint position-aware texture variants."""
import numpy as np

def position_map(P, UV, T, size):
    H = W = size; pos = np.zeros((H, W, 3), np.float32); cov = np.zeros((H, W), bool)
    U = UV[:, 0] % 1 * (W - 1); V = UV[:, 1] % 1 * (H - 1)
    for tri in T:
        x = U[tri]; y = V[tri]
        x0, x1 = int(np.floor(x.min())), int(np.ceil(x.max())); y0, y1 = int(np.floor(y.min())), int(np.ceil(y.max()))
        if x1 - x0 > W / 2 or y1 - y0 > H / 2: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-9: continue
        a = ((y[1] - y[2]) * (xs - x[2]) + (x[2] - x[1]) * (ys - y[2])) / d
        b = ((y[2] - y[0]) * (xs - x[2]) + (x[0] - x[2]) * (ys - y[2])) / d
        c = 1 - a - b; m = (a >= -.02) & (b >= -.02) & (c >= -.02)
        if not m.any(): continue
        p = a[m, None] * P[tri[0]] + b[m, None] * P[tri[1]] + c[m, None] * P[tri[2]]
        yy, xx = np.clip(ys[m], 0, H - 1), np.clip(xs[m], 0, W - 1)
        pos[yy, xx] = p; cov[yy, xx] = True
    return pos, cov
