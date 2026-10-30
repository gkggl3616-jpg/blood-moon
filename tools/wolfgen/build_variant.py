"""Build the Fire Wolf (ates) and Wolf King (kral) from the original ice-wolf mesh/rig: same skeleton and clips,
new painted textures; the king also gets horns and a skinned cape on its own 3-bone chain (driven by engine spring physics)."""
import io, math, sys
import numpy as np
from PIL import Image
from build_icewolf import make_mesh, bake, CLIPS, write_glb
from variants import paint, swatch_uv


def tube(M, pts, r0, r1, uv, bone_w, sides=8):
    base = len(M.P); pts = np.asarray(pts, float); n = len(pts)
    for i, p in enumerate(pts):
        t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]; t /= np.linalg.norm(t)
        a = np.cross(t, [0, 0, 1.0]);
        if np.linalg.norm(a) < 1e-3: a = np.cross(t, [1.0, 0, 0])
        a /= np.linalg.norm(a); b = np.cross(t, a); r = r0 + (r1 - r0) * i / (n - 1)
        for k in range(sides):
            ang = 2 * math.pi * k / sides; nrm = a * math.cos(ang) + b * math.sin(ang)
            M.P.append(p + nrm * r); M.N.append(nrm); add_v(M, uv, bone_w)
    for i in range(n - 1):
        for k in range(sides):
            a0 = base + i * sides + k; a1 = base + i * sides + (k + 1) % sides; b0 = a0 + sides; b1 = a1 + sides
            M.tris += [[a0, b0, a1, M.tris[0][3]], [a1, b0, b1, M.tris[0][3]]]


def add_v(M, uv, bone_w):
    j = [b for b, _ in bone_w] + [0] * (4 - len(bone_w)); w = [x for _, x in bone_w] + [0] * (4 - len(bone_w))
    M.J.append(j); M.W.append(w); M.C.append([1, 1, 1, 1]); M.M.append(M.M[0]); M._uv.append(uv)


def build(kind, out, scale_note):
    S, M = make_mesh()
    tex, em = paint(kind); size = tex.shape[0]
    b = io.BytesIO(); Image.fromarray(tex).save(b, 'JPEG', quality=90); M.texture = b.getvalue()
    b = io.BytesIO(); Image.fromarray(em).save(b, 'PNG', optimize=True); M.emissive_tex = b.getvalue()
    M._uv = []
    if kind == 'king':
        head = S.idx('Head'); horn_uv = swatch_uv('horn', size)
        for sx in (1, -1):
            pts = [(sx * .065, 1.73, .11), (sx * .11, 1.81, .09), (sx * .16, 1.88, .04), (sx * .19, 1.92, -.04), (sx * .19, 1.93, -.12), (sx * .16, 1.91, -.18)]
            tube(M, pts, .034, .004, horn_uv, [(head, 1.0)])
        # cape bones (Chest -> Cape1 -> Cape2 -> Cape3)
        S.add('Cape1', 'Chest', (0, 1.40, -.19)); S.add('Cape2', 'Cape1', (0, 1.08, -.27)); S.add('Cape3', 'Cape2', (0, .76, -.35))
        ch, c1, c2, c3 = (S.idx(n) for n in ('Chest', 'Cape1', 'Cape2', 'Cape3'))
        cu = swatch_uv('cape', size); rows, cols = 10, 9; base = len(M.P)
        for r in range(rows + 1):
            s = r / rows; yv = 1.44 - s * 1.0; half = .22 + .13 * s
            for c in range(cols + 1):
                u = c / cols * 2 - 1; xv = u * half; zv = -.17 - .27 * s - .05 * (1 - u * u) - .02 * math.sin(u * 7) * s
                M.P.append(np.array([xv, yv, zv])); M.N.append(np.array([0, 0, -1.0]))
                if yv >= 1.40: bw = [(ch, 1.0)]
                elif yv >= 1.08: k = (1.40 - yv) / .32; bw = [(c1, 1 - k * .5), (c2, k * .5)]
                elif yv >= .76: k = (1.08 - yv) / .32; bw = [(c2, 1 - k * .5), (c3, .5 * k + 0)] if k > 0 else [(c2, 1.0)]
                else: bw = [(c3, 1.0)]
                tot = sum(x for _, x in bw); bw = [(i, x / tot) for i, x in bw]
                add_v(M, (cu[0] + (c / cols - .5) * .02, cu[1] + (s - .5) * .02), bw)
        for r in range(rows):
            for c in range(cols):
                a = base + r * (cols + 1) + c; b_ = a + 1; d = a + cols + 1; e = d + 1
                M.tris += [[a, d, b_, M.tris[0][3]], [b_, d, e, M.tris[0][3]]]
    if M._uv: M.UV = np.concatenate([np.asarray(M.UV), np.asarray(M._uv)], 0)
    clips = {n: bake(S, n) for n in CLIPS}
    extras = dict(source_kind='new_' + kind, clawProfile='standard', previewHeight=1.85, run_stride_m=3.2, run_reference_speed_mps=8.0)
    write_glb(out, S, M, clips, 'Body_' + ('ates' if kind == 'fire' else 'kral'), extras=extras)
    import os; print(kind, 'glb', os.path.getsize(out), 'joints', len(S.names), 'tris', len(M.tris))


if __name__ == '__main__':
    for k in sys.argv[1:]: build(k, f'/tmp/wolf_{k}.glb', None)
