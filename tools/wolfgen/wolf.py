"""Original werewolf: skeleton + skinned mesh for three variants (ice, fire, king)."""
import math
import numpy as np
from core import *

VARIANTS = {
    'ice': dict(fur=(0.86, 0.90, 0.95), fur_dark=(0.58, 0.64, 0.72), belly=(0.97, 0.98, 1.0), cloth=(0.55, 0.58, 0.64),
                eye=(0.35, 0.8, 1.0), claw=(0.82, 0.88, 0.95)),
    'fire': dict(fur=(0.10, 0.07, 0.08), fur_dark=(0.03, 0.02, 0.03), belly=(0.32, 0.07, 0.09), cloth=(0.12, 0.07, 0.08),
                 eye=(1.0, 0.25, 0.1), claw=(0.25, 0.1, 0.1)),
    'king': dict(fur=(0.30, 0.25, 0.22), fur_dark=(0.12, 0.10, 0.10), belly=(0.46, 0.40, 0.34), cloth=(0.14, 0.10, 0.10),
                 eye=(1.0, 0.62, 0.15), claw=(0.2, 0.18, 0.16)),
}


def build_skeleton(variant):
    s = Skeleton()
    s.add('Root', None, (0, 0, 0))
    s.add('Hips', 'Root', (0, .95, -.02))
    s.add('Spine', 'Hips', (0, 1.12, 0))
    s.add('Chest', 'Spine', (0, 1.32, .02))
    s.add('Neck', 'Chest', (0, 1.52, .06))
    s.add('Head', 'Neck', (0, 1.64, .1))
    s.add('Jaw', 'Head', (0, 1.6, .2))
    for sx, L in ((1, 'L'), (-1, 'R')):
        s.add('Clav' + L, 'Chest', (.16 * sx, 1.44, .03))
        s.add('UpperArm' + L, 'Clav' + L, (.30 * sx, 1.45, .02))
        s.add('Forearm' + L, 'UpperArm' + L, (.35 * sx, 1.10, .02))
        s.add('Hand' + L, 'Forearm' + L, (.36 * sx, .80, .10))
        s.add('Thigh' + L, 'Hips', (.15 * sx, .93, -.02))
        s.add('Shin' + L, 'Thigh' + L, (.18 * sx, .55, .12))
        s.add('Foot' + L, 'Shin' + L, (.17 * sx, .20, -.04))
    s.add('Tail1', 'Hips', (0, .95, -.15))
    s.add('Tail2', 'Tail1', (0, .90, -.45))
    s.add('Tail3', 'Tail2', (0, .80, -.75))
    if variant == 'king':
        s.add('Cape1', 'Chest', (0, 1.50, -.12))
        s.add('Cape2', 'Cape1', (0, 1.18, -.20))
        s.add('Cape3', 'Cape2', (0, .84, -.24))
        s.add('Cape4', 'Cape3', (0, .50, -.24))
    return s


def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)


def path_weights(path, bones, blend=.07):
    """bones: [(name, start_arclength)] ordered; boundaries blend smoothly."""
    path = np.asarray(path, float)
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])

    def proj(p):
        best, bs = 1e9, 0
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]; d = b - a
            t = np.clip(np.dot(p - a, d) / (np.dot(d, d) + 1e-9), 0, 1)
            dist = np.linalg.norm(p - (a + d * t))
            if dist < best: best, bs = dist, cum[i] + t * seg[i]
        return bs

    def fn(i, p):
        s = proj(p); w = {}
        for k, (name, st) in enumerate(bones):
            en = bones[k + 1][1] if k + 1 < len(bones) else 1e9
            lo = smooth((s - (st - blend)) / (2 * blend)) if k > 0 else 1.0
            hi = 1 - smooth((s - (en - blend)) / (2 * blend)) if k + 1 < len(bones) else 1.0
            if lo * hi > 1e-3: w[name] = lo * hi
        return w or {bones[0][0]: 1.0}
    fn.cum = cum
    return fn


def fur_color(pal, seed=0, blotch=None):
    base, dark, belly = [np.array(pal[k]) for k in ('fur', 'fur_dark', 'belly')]

    def fn(p, n):
        up = np.clip(n[1] * .5 + .5, 0, 1)
        c = base * (1 - .35 * (1 - up)) + belly * .35 * (1 - up)
        v = hash_noise(np.array(p), 9.0, seed) * .6 + hash_noise(np.array(p), 31.0, seed + 3) * .4
        c = c * (.82 + .3 * v) + dark * .25 * (hash_noise(np.array(p), 4.0, seed + 8) > .62)
        if blotch is not None: c = blotch(p, n, c)
        return tuple(np.clip(c, 0, 1))
    return fn


def build_wolf(variant):
    pal = VARIANTS[variant]
    S = build_skeleton(variant)
    M = Mesh(S)
    M.material('Fur_' + variant, (1, 1, 1), roughness=.92)
    M.material('Cloth_' + variant, (1, 1, 1), roughness=.96, double=True)
    M.material('Claw_' + variant, pal['claw'], roughness=.4)
    M.material('Eye_' + variant, pal['eye'], emissive=[c * .9 for c in pal['eye']], roughness=.3)
    M.material('Mouth_' + variant, (.25, .05, .06), roughness=.6)
    M.material('Teeth_' + variant, (.95, .93, .86), roughness=.4)
    if variant == 'ice':
        M.material('Glow_Ice', (.62, .88, 1.0), emissive=[.25, .55, .8], roughness=.15)
    if variant == 'fire':
        M.material('Glow_Flame', (1.0, .45, .1), emissive=[1.0, .35, .05], roughness=.5, double=True)
        M.material('Glow_Scar', (1.0, .25, .1), emissive=[.9, .15, .04], roughness=.5)
    if variant == 'king':
        M.material('Horn_king', (.12, .1, .09), roughness=.45)
        M.material('Glow_Blood', (.45, .02, .03), emissive=[.0, .0, .0], roughness=.35)
    if variant != 'ice':
        pass

    def blotch(p, n, c):
        return c
    if variant == 'king':
        scars = [((.10, 1.42, .17), (.22, 1.22, .20)), ((.06, 1.40, .18), (.17, 1.20, .21)), ((-.12, 1.30, .20), (-.02, 1.12, .20)),
                 ((.05, 1.70, .20), (.10, 1.60, .22)), ((.30, 1.38, .06), (.37, 1.2, .10))]

        def blotch(p, n, c):
            p = np.array(p)
            blood = hash_noise(p, 7.0, 21) * .7 + hash_noise(p, 19.0, 5) * .3
            m = np.clip((blood - .66) * 6, 0, 1) * (1 if p[1] > .6 else .3)
            c = c * (1 - m * .85) + np.array([.34, .02, .03]) * m * .85
            for a, b in scars:
                a, b = np.array(a), np.array(b); d = b - a
                t = np.clip(np.dot(p - a, d) / np.dot(d, d), 0, 1); dist = np.linalg.norm(p - (a + d * t))
                if dist < .014: c = c * .35 + np.array([.55, .12, .12]) * .35
            return c
    fur = fur_color(pal, seed={'ice': 1, 'fire': 2, 'king': 3}[variant], blotch=blotch if variant == 'king' else None)
    FUR = 'Fur_' + variant
    cloth_col = lambda p, n: tuple(np.clip(np.array(pal['cloth']) * (.75 + .5 * hash_noise(np.array(p), 17.0, 4)), 0, 1))
    claw_col = pal['claw']
    one = lambda b: (lambda i, p: {b: 1.0})

    # --- torso --------------------------------------------------------------
    spine_path = [(0, .92, -.05), (0, 1.10, 0), (0, 1.32, .03), (0, 1.50, .07)]
    M.tube(spine_path, [(.17, .15), (.18, .16), (.27, .20), (.19, .16)], path_weights(spine_path, [('Hips', 0), ('Spine', .18), ('Chest', .40)], .1), fur, FUR, sides=14)
    # chest ruff
    M.ellipsoid((0, 1.38, .09), (.23, .17, .17), one('Chest'), lambda p, n: tuple(np.array(pal['belly']) * .95), FUR)
    # --- neck / head --------------------------------------------------------
    neck_path = [(0, 1.48, .05), (0, 1.60, .11)]
    M.tube(neck_path, [(.11, .11), (.10, .10)], path_weights(neck_path, [('Neck', 0)]), fur, FUR, sides=10, cap_start=False)
    M.ellipsoid((0, 1.67, .10), (.125, .115, .15), one('Head'), fur, FUR)
    snout = [(0, 1.655, .19), (0, 1.63, .30), (0, 1.615, .39)]
    M.tube(snout, [(.08, .062), (.058, .045), (.036, .03)], one('Head'), fur, FUR, sides=10)
    M.ellipsoid((0, 1.63, .41), (.03, .024, .028), one('Head'), lambda p, n: (.04, .04, .05), FUR)
    jaw = [(0, 1.58, .17), (0, 1.57, .28), (0, 1.58, .37)]
    M.tube(jaw, [(.06, .035), (.045, .03), (.025, .02)], one('Jaw'), lambda p, n: tuple(np.array(pal['belly']) * .9), FUR, sides=8)
    for sx in (1, -1):
        M.ellipsoid((.055 * sx, 1.70, .21), (.022, .02, .014), one('Head'), lambda p, n: pal['eye'], 'Eye_' + variant, seg=8, rings=6)
        # ears
        M.cone((.075 * sx, 1.76, .06), (.11 * sx, 1.90, .02), .045, one('Head'), fur, FUR, sides=6, curve=(0, .01, -.01))
        # brow ridge
        M.ellipsoid((.06 * sx, 1.73, .20), (.045, .014, .03), one('Head'), fur_color(pal, 9), FUR, rot=(0, 0, 20 * sx), seg=8, rings=6)
    # teeth (fangs)
    for sx in (1, -1):
        M.cone((.03 * sx, 1.605, .34), (.032 * sx, 1.555, .35), .009, one('Head'), lambda p, n: (.95, .93, .86), 'Teeth_' + variant, sides=5)
        M.cone((.028 * sx, 1.575, .33), (.03 * sx, 1.62, .335), .008, one('Jaw'), lambda p, n: (.95, .93, .86), 'Teeth_' + variant, sides=5)
    # --- arms ---------------------------------------------------------------
    for sx, L in ((1, 'L'), (-1, 'R')):
        M.ellipsoid((.24 * sx, 1.46, .03), (.13, .11, .12), one('Clav' + L), fur, FUR)
        arm = [(.30 * sx, 1.45, .02), (.33 * sx, 1.27, .02), (.35 * sx, 1.10, .02), (.355 * sx, .95, .06), (.36 * sx, .80, .10)]
        wf = path_weights(arm, [('UpperArm' + L, 0), ('Forearm' + L, .35), ('Hand' + L, .65)], .06)
        M.tube(arm, [(.085, .085), (.082, .082), (.075, .075), (.062, .062), (.048, .048)], wf, fur, FUR, sides=10)
        palm = (.365 * sx, .73, .12)
        M.ellipsoid(palm, (.05, .075, .06), one('Hand' + L), fur, FUR)
        for k, off in enumerate((-.032, 0.0, .032)):
            f0 = np.array([palm[0] + off * sx * .6, .68, .14 + off * 0]); f1 = f0 + np.array([off * .6 * sx, -.07, .035])
            M.tube([f0, f1], [.017, .012], one('Hand' + L), fur, FUR, sides=6, cap_start=False)
            M.cone(f1, f1 + np.array([off * .2 * sx, -.075, .045]), .012, one('Hand' + L), lambda p, n: claw_col, 'Claw_' + variant, sides=5, curve=(0, 0, .012))
        # thumb
        M.cone((palm[0] - .045 * sx, .72, .15), (palm[0] - .06 * sx, .66, .21), .015, one('Hand' + L), lambda p, n: claw_col, 'Claw_' + variant, sides=5)
    # --- legs + pants --------------------------------------------------------
    rng = np.random.default_rng(7)
    for sx, L in ((1, 'L'), (-1, 'R')):
        leg = [(.15 * sx, .93, -.02), (.17 * sx, .74, .05), (.18 * sx, .55, .12), (.175 * sx, .38, .04), (.17 * sx, .20, -.04)]
        wf = path_weights(leg, [('Thigh' + L, 0), ('Shin' + L, .42)], .08)
        M.tube(leg, [(.12, .12), (.105, .105), (.075, .075), (.058, .058), (.045, .045)], wf, fur, FUR, sides=10)
        foot = [(.17 * sx, .20, -.04), (.17 * sx, .06, .03), (.17 * sx, .035, .13)]
        M.tube(foot, [(.045, .045), (.04, .05), (.032, .045)], path_weights(foot, [('Foot' + L, 0)]), fur, FUR, sides=8)
        for k, off in enumerate((-.03, 0, .03)):
            t0 = np.array([.17 * sx + off, .03, .17]); M.cone(t0, t0 + np.array([off * .3, -.012, .08]), .014, one('Foot' + L), lambda p, n: claw_col, 'Claw_' + variant, sides=5)
        # capri pants: ragged hem at mid-shin
        pant = [(.15 * sx, 1.0, -.02), (.15 * sx, .88, -.02), (.17 * sx, .70, .06), (.18 * sx, .55, .12), (.178 * sx, .44, .08), (.176 * sx, .36, .05)]
        hem = rng.uniform(-.06, .07, size=16)
        M.tube(pant, [(.135, .135), (.135, .135), (.118, .118), (.092, .092), (.09, .09), (.088, .088)], path_weights(pant, [('Hips', 0), ('Thigh' + L, .1), ('Shin' + L, .46)], .08),
               cloth_col, 'Cloth_' + variant, sides=16, cap_start=False, cap_end=False,
               shift=lambda i, s: (hem[s % 16] if i == len(pant) - 1 else 0), jitter=lambda i, s: 1.0 + (.06 if (i == len(pant) - 1 and s % 2) else 0))
    waist = [(0, .86, -.03), (0, 1.0, -.03)]
    M.tube(waist, [(.19, .17), (.18, .165)], path_weights(waist, [('Hips', 0)]), cloth_col, 'Cloth_' + variant, sides=16, cap_start=False, cap_end=False)
    # --- tail ---------------------------------------------------------------
    tail = [(0, .95, -.12), (0, .92, -.32), (0, .86, -.55), (0, .76, -.78), (0, .64, -.97)]
    M.tube(tail, [.07, .09, .095, .075, 0.0], path_weights(tail, [('Tail1', 0), ('Tail2', .25), ('Tail3', .55)], .08), fur, FUR, sides=10, cap_start=False, cap_end=False)

    # === variant features =====================================================
    if variant == 'ice':
        ice = lambda p, n: (.75, .93, 1.0)
        for sx, L in ((1, 'L'), (-1, 'R')):
            e = np.array([.35 * sx, 1.10, .02])
            for k, (ax, ln, wd) in enumerate([((.9 * sx, .35, -.55), .2, .035), ((.5 * sx, .9, -.35), .15, .03), ((.7 * sx, -.2, -.8), .13, .027), ((.95 * sx, .15, .1), .11, .025)]):
                M.crystal(e + np.array([0, .01 * k, -.045]), ax, ln, wd, one('Forearm' + L), ice, 'Glow_Ice')
            kn = np.array([.18 * sx, .56, .19])
            M.crystal(kn + np.array([0, -.04, .0]), (.18 * sx, .75, .65), .30, .028, one('Shin' + L), ice, 'Glow_Ice', sides=4, flat=.35)
            M.crystal(kn + np.array([.035 * sx, .01, .0]), (.5 * sx, .55, .5), .11, .02, one('Shin' + L), ice, 'Glow_Ice', sides=4, flat=.4)
    if variant == 'fire':
        for sx, L in ((1, 'L'), (-1, 'R')):
            # flames: wrist -> elbow, outer side of the forearm
            for k in range(7):
                t = k / 6.0
                base = np.array([(.36 - .01 * t) * sx + .05 * sx, .82 + .27 * t, .09 - .07 * t])
                height = .20 * (1 - .55 * t) + .05
                lean = np.array([.05 * sx, 0, -.05]) * (1 - t)
                tip = base + np.array([0, height, 0]) + lean
                M.cone(base, tip, .035 * (1 - .3 * t), one('Forearm' + L), lambda p, n: (1.0, .5, .12), 'Glow_Flame', sides=5, curve=(.012 * sx, 0, -.01))
                if k % 2 == 0:
                    b2 = base + np.array([.03 * sx, 0, .04]); M.cone(b2, b2 + np.array([.02 * sx, height * .65, .01]), .026, one('Forearm' + L), lambda p, n: (1.0, .35, .08), 'Glow_Flame', sides=5)
        # three claw slashes on chest centre
        for k, xo in enumerate((-.055, 0.0, .055)):
            pts = []
            for u in np.linspace(0, 1, 7):
                x = xo + (u - .5) * .07; y = 1.46 - u * .26 - abs(xo) * .0
                z = .02 + .2 * math.sqrt(max(0.0, 1 - (x / .27) ** 2 - ((y - 1.32) / .21) ** 2 * .6)) + .008
                pts.append((x, y, z))
            M.tube(pts, [.0, .008, .011, .012, .011, .008, .0], one('Chest'), lambda p, n: (1.0, .3, .1), 'Glow_Scar', sides=6)
    if variant == 'king':
        horn_col = lambda p, n: (.13, .11, .1)
        for sx, L in ((1, 'L'), (-1, 'R')):
            hp = [(.075 * sx, 1.745, .045), (.14 * sx, 1.86, .0), (.19 * sx, 1.99, -.06), (.17 * sx, 2.12, -.04)]
            M.tube(hp, [.04, .034, .022, .0], one('Head'), horn_col, 'Horn_king', sides=8, cap_start=False, cap_end=False)
            # shoulder spikes
            M.cone((.30 * sx, 1.54, .0), (.38 * sx, 1.74, -.08), .04, one('Clav' + L), horn_col, 'Horn_king', sides=6)
        # cape: sheet hanging from shoulders, static weights along the Cape chain
        cb = [('Chest', 1.5), ('Cape1', 1.5), ('Cape2', 1.18), ('Cape3', .84), ('Cape4', .5)]
        rows, cols = 9, 7
        grid = np.zeros((rows, cols, 3)); rag = np.random.default_rng(3).uniform(-.07, .07, cols)
        for r in range(rows):
            tt = r / (rows - 1)
            y = 1.52 - tt * 1.12 + (rag[(r * 3) % cols] * (tt > .85))
            for c in range(cols):
                u = c / (cols - 1) * 2 - 1
                w = .24 + .2 * tt
                grid[r, c] = (u * w, y + (abs(u) * .04) * (tt < .1) - (rag[c] if r == rows - 1 else 0), -.15 - .1 * tt - abs(u) * .04)
        capw = chain_weights([('Cape1', 1.5), ('Cape2', 1.18), ('Cape3', .84), ('Cape4', .5)])
        M.sheet(grid, lambda i, p: capw(p[1]), lambda p, n: tuple(np.clip(np.array((.30, .04, .05)) * (.7 + .5 * hash_noise(np.array(p), 11.0, 2)), 0, 1)), 'Cloth_king')
    return S, M
