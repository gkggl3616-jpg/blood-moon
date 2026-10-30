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
    n_body = len(M.P)
    if kind == 'king':
        head = S.idx('Head'); horn_uv = swatch_uv('horn', size)
        for sx in (1, -1):
            # ram horn: rises from the temple, curls back, down and forward around the ear
            pts = []
            for i in range(16):
                t = i / 15; th = math.pi * 1.55 * t; R = .085 * (1 - .4 * t)
                pts.append((sx * (.075 + .085 * t), 1.745 + R * math.cos(th) + .02 * (1 - t), .05 - R * math.sin(th) - .04 * t))
            tube(M, pts, .046, .01, horn_uv, [(head, 1.0)], sides=10)
        # cape bones (Chest -> Cape1 -> Cape2 -> Cape3)
        S.add('Cape1', 'Chest', (0, 1.38, -.17)); S.add('Cape2', 'Cape1', (0, 1.12, -.21)); S.add('Cape3', 'Cape2', (0, .88, -.23))
        ch, c1, c2, c3 = (S.idx(n) for n in ('Chest', 'Cape1', 'Cape2', 'Cape3'))
        # tattered cloak draped over both shoulders (design sheet): wraps the back from shoulder to shoulder,
        # widens toward the calves, irregular moth-eaten holes and a long jagged hem; metal clasp on the left chest.
        cu, ci = swatch_uv('cape', size), swatch_uv('capein', size); rows, cols = 16, 22; base = len(M.P)
        sp_, hp_ = S.idx('Spine'), S.idx('Hips'); cl = {1: S.idx('ClavL'), -1: S.idx('ClavR')}
        rng = np.random.default_rng(7)
        for r in range(rows + 1):
            s_ = r / rows; yv = 1.48 - s_ * .98
            A = math.radians(118 - 22 * s_); R = .21 + .13 * s_; zc = .03 - .05 * s_
            for c in range(cols + 1):
                a = -A + 2 * A * c / cols
                Rr = R + .018 * math.sin(a * 7 + s_ * 2.5) * s_ + (.03 if s_ < .08 else 0)
                xv = Rr * math.sin(a); zv = zc - Rr * math.cos(a); yy = yv - .07 * (abs(math.sin(a)) ** 2) * (1 - s_)
                M.P.append(np.array([xv, yy, zv])); M.N.append(np.array([math.sin(a), 0, -math.cos(a)]))
                side = 1 if xv > 0 else -1; front = abs(math.sin(a))
                body = ch if yy >= 1.26 else sp_ if yy >= 1.06 else hp_
                chain = c1 if yy >= 1.15 else c2 if yy >= .9 else c3
                if s_ < .1: bw = [(ch, 1 - .5 * front), (cl[side], .5 * front)]
                else:
                    k = min(1.0, (s_ - .1) * 1.3) * (1 - .55 * front)
                    bw = [(body, 1 - .6 * k), (chain, .6 * k)]
                uvc = cu if (c + r) % 3 else ci
                add_v(M, (uvc[0] + (c / cols - .5) * .02, uvc[1] + (s_ - .5) * .02), bw)
        hem = [rows - int(rng.integers(0, 4)) - (2 if rng.random() < .25 else 0) for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                a = base + r * (cols + 1) + c; b_ = a + 1; d = a + cols + 1; e = d + 1
                if r >= hem[c]: continue
                hole = 3 <= r < rows - 3 and rng.random() < .07
                if not hole or rng.random() < .5: M.tris.append([a, d, b_, M.tris[0][3]])
                if not hole: M.tris.append([b_, d, e, M.tris[0][3]])
        # clasp ring on the left chest
        gu = swatch_uv('gold', size); ring = []
        for k in range(13):
            t = 2 * math.pi * k / 12; ring.append((.13 + .035 * math.cos(t), 1.38 + .035 * math.sin(t), .17))
        tube(M, ring, .009, .009, gu, [(ch, 1.0)], sides=6)
    if kind == 'hell':
        head = S.idx('Head'); hu = swatch_uv('horn', size)
        for sx in (1, -1):   # short swept-back black horns
            pts = [(sx * (.06 + .03 * t), 1.75 + .07 * t - .04 * t * t, .06 - .16 * t) for t in np.linspace(0, 1, 8)]
            tube(M, pts, .03, .004, hu, [(head, 1.0)], sides=8)
        # bone spikes in one line down the spine, smallest at the lower back, growing toward the neck
        horn_uv = swatch_uv('horn', size)
        back = [(1.05, -.07), (1.13, -.055), (1.19, -.05), (1.25, -.065), (1.31, -.12), (1.37, -.145), (1.43, -.157), (1.49, -.166), (1.55, -.157)]
        ys, zs = zip(*back); n = 10
        for k in range(n):
            u = k / (n - 1); y0 = 1.05 + u * .50; z0 = float(np.interp(y0, ys, zs)) + .012
            L = .035 + .14 * u ** 1.3; r0 = .011 + .026 * u
            d = np.array([0, math.sin(math.radians(32)), -math.cos(math.radians(32))])
            pts = [np.array([0, y0, z0]) + d * L * t for t in np.linspace(0, 1, 6)]
            bone = S.idx('Hips') if y0 < 1.12 else S.idx('Spine') if y0 < 1.30 else S.idx('Chest') if y0 < 1.50 else S.idx('Neck')
            tube(M, pts, r0, .0015, horn_uv, [(bone, 1.0)], sides=7)
    if M._uv: M.UV = np.concatenate([np.asarray(M.UV), np.asarray(M._uv)], 0)
    if len(M.P) > n_body:   # horns / cape / spikes were added after skinning: give the whole mesh one more anti-stretch pass
        from build_icewolf import fix_stretch
        P_ = np.asarray(M.P); T_ = np.array([t[:3] for t in M.tris]); rig_ = np.zeros(len(P_), bool); rig_[n_body:] = True
        rig_[n_body:] = np.array([w[0] >= .999 for w in M.W[n_body:]])   # single-bone horns/spikes/clasp stay rigid, cloth may blend
        Jl, Wl = fix_stretch(S, P_, np.asarray(M.J), np.asarray(M.W), T_, rig_); M.J = list(Jl); M.W = list(Wl)
    U = np.asarray(M.UV); px = (U[:, 0] % 1 * (size - 1)).astype(int); py = (U[:, 1] % 1 * (size - 1)).astype(int)
    M.C = [list(c) + [1.0] for c in tex[py, px] / 255.0]   # vertex colours from the painted texture (offline previews)
    build.last = (S, M)
    clips = {n: bake(S, n) for n in CLIPS}
    extras = dict(source_kind='new_' + kind, clawProfile='standard', previewHeight=1.85, run_stride_m=3.2, run_reference_speed_mps=8.0)
    write_glb(out, S, M, clips, 'Body_' + {'fire': 'ates', 'king': 'kral', 'moon': 'ay', 'hell': 'hellgate'}[kind], extras=extras)
    import os; print(kind, 'glb', os.path.getsize(out), 'joints', len(S.names), 'tris', len(M.tris))


if __name__ == '__main__':
    for k in sys.argv[1:]: build(k, f'/tmp/wolf_{k}.glb', None)
