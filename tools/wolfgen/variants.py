"""Texture variants of the original ice-wolf mesh: 'fire' (evil twin, black/red/burgundy, burning forearms, chest claw scars)
and 'king' (war-worn wolf king: dark fur, blood, scars). Position-aware painting via the UV position map."""
import numpy as np
from PIL import Image, ImageFilter

SWATCH = {'horn': (592, 288, 32), 'cape': (624, 288, 32), 'capein': (592, 320, 32), 'gold': (624, 320, 32)}   # free texel blocks


def seg_d(p, a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(p - (a + t[..., None] * ab), axis=-1)


def noise(shape, seed, blur):
    r = np.random.default_rng(seed).random(shape).astype(np.float32)
    im = Image.fromarray((r * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur)); a = np.asarray(im, np.float32) / 255
    return (a - a.min()) / (a.max() - a.min() + 1e-6)


def paint(kind, tex_path='/tmp/wolf_prep_tex.jpg', pm='/tmp/wolf_posmap.npz'):
    t = np.asarray(Image.open(tex_path).convert('RGB'), np.float32) / 255; d = np.load(pm); pos, cov = d['pos'], d['cov']
    H = t.shape[0]; L = t.mean(2); ice = ((t[..., 2] - t[..., 0]) > .10) & (t[..., 2] > .55)
    x, y, z = pos[..., 0], pos[..., 1], pos[..., 2]
    pants = cov & (y > .5) & (y < 1.03) & (np.abs(x) < .27) & ~ice
    claws = L < .22
    out = np.zeros_like(t); em = np.zeros_like(t)
    n1 = noise(L.shape, 1, 3); n2 = noise(L.shape, 2, 9)
    if kind == 'fire':
        fur = np.stack([.055 + .16 * L ** 1.4, .045 + .085 * L ** 1.6, .05 + .085 * L ** 1.6], -1)
        # warmer ember-red undertone deeper in the fur and toward the forearms
        heat = np.clip(1 - np.minimum(seg_d(pos, (.30, 1.17, .10), (.30, .90, .24)), seg_d(pos, (-.27, 1.16, -.08), (-.28, .88, .03))) / .22, 0, 1) * cov
        fur = fur + heat[..., None] * np.array([.25, .05, .0]) * (.4 + .6 * n1[..., None])
        pa = np.stack([.095 * (.4 + .8 * L), .08 * (.4 + .8 * L), .08 * (.4 + .8 * L)], -1)   # charcoal torn shorts
        out = np.where(pants[..., None], pa, fur)
        # crimson mane: head/neck crest, a stripe down the spine and the tail, like the design sheet
        mane = cov & (((y > 1.56) & (z < .06) & (n1 > .3)) | ((np.abs(x) < .035) & (z < -.08) & (y > 1.05) & (y < 1.58)) | ((z < -.2) & (y < .8) & (y > .35) & (np.abs(x) < .09) & (n1 > .25)))
        mc = np.stack([.26 + .26 * L, .025 + .04 * L, .035 + .04 * L], -1) * (.6 + .5 * n1[..., None])
        out = np.where(mane[..., None], mc, out)
        out = np.where(claws[..., None], np.array([.55, .12, .03]) * (.6 + .4 * n1[..., None]), out)
        em = em + (claws & cov)[..., None] * np.array([.35, .07, .0])
        ember = np.stack([1.0 * np.ones_like(L), .38 + .35 * L, .08 + .1 * L], -1)
        out = np.where(ice[..., None], ember * .9, out); em = np.where(ice[..., None], ember, em)
        em = em + (heat * (n1 > .55))[..., None] * np.array([.6, .16, .02])
        # three claw-mark scars across the chest centre (glow when roaring)
        sc = np.zeros(L.shape, bool)
        for k in range(3):
            o = (k - 1) * .045
            dd = seg_d(pos, (-.09 + o, 1.43, .19), (.07 + o, 1.20, .21))
            sc |= cov & (dd < .010 + .004 * (1 - abs(k - 1))) & (z > .08) & (np.abs(x) < .2)
        out[sc] = [.55, .03, .03]; em[sc] = [.9, .12, .04]
    elif kind == 'moon':
        fur = np.stack([.70 + .28 * L, .70 + .26 * L, .76 + .22 * L], -1) * (.92 + .1 * n2[..., None])
        stripes = cov & (np.sin(y * 38 + np.abs(x) * 22 + n2 * 4) > .78) & ~pants
        fur = np.where(stripes[..., None], np.array([.55, .48, .78]) * (.8 + .3 * L[..., None]), fur)
        pa = np.stack([.12 * (.4 + .8 * L), .11 * (.4 + .8 * L), .12 * (.4 + .8 * L)], -1)
        out = np.where(pants[..., None], pa, fur); out = np.where(claws[..., None], t * .35, out)
        moon = np.stack([.78 + .2 * L, .62 + .2 * L, 1.0 + 0 * L], -1)
        out = np.where(ice[..., None], moon * .85, out); em = np.where(ice[..., None], moon * .9, em)
    else:  # king
        fur = np.stack([.16 + .30 * L ** 1.1, .13 + .25 * L ** 1.15, .11 + .19 * L ** 1.2], -1)   # gray-brown, like the sheet
        pa = np.stack([.12 * (.4 + .8 * L), .085 * (.4 + .8 * L), .07 * (.4 + .8 * L)], -1)
        out = np.where(pants[..., None], pa, fur)
        out = np.where(claws[..., None], t * .4, out)
        # dried blood: on claws/hands, forearms, muzzle and chest splatter
        hands = np.minimum(seg_d(pos, (.30, .95, .2), (.30, .76, .30)), seg_d(pos, (-.28, .95, .02), (-.27, .72, .04)))
        mouth = seg_d(pos, (0, 1.6, .26), (0, 1.62, .36))
        blood = cov & (((hands < .09) & (n1 > .35)) | ((mouth < .06) & (n1 > .4)) | ((z > .1) & (y > 1.1) & (y < 1.45) & (n2 > .78)))
        bc = np.array([.32, .02, .025]) * (.6 + .5 * n1[..., None])
        out = np.where(blood[..., None], out * .25 + bc * .9, out)
        # pale scars: a few long slashes on chest, shoulder and thigh
        sc = np.zeros(L.shape, bool)
        for a_, b_ in (((-.15, 1.42, .17), (.05, 1.22, .21)), ((.18, 1.40, .05), (.27, 1.22, .12)), ((-.2, .95, .1), (-.12, .72, .14)), ((.02, 1.38, .2), (.12, 1.30, .2))):
            sc |= cov & (seg_d(pos, a_, b_) < .007)
        out[sc] = out[sc] * .4 + np.array([.62, .5, .48]) * .6
        crys = np.stack([.16 + .12 * L, .11 + .08 * L, .09 + .06 * L], -1)   # the shards become dark bone spurs
        out = np.where(ice[..., None], crys, out); em = np.where(ice[..., None], np.array([.18, .02, .02]) * (.5 + .5 * L[..., None]), em)
    out = np.where(cov[..., None], out, t * .3); em = em * cov[..., None]   # keep unused texels dark (mip bleeding)
    for k, (cx, cy, s) in SWATCH.items():
        col = {'horn': (.30, .25, .2), 'cape': (.075, .07, .07), 'capein': (.05, .045, .045), 'gold': (.55, .52, .45)}[k]
        out[cy:cy + s, cx:cx + s] = col
    return (np.clip(out, 0, 1) * 255).astype(np.uint8), (np.clip(em, 0, 1) * 255).astype(np.uint8)


def swatch_uv(name, size):
    cx, cy, s = SWATCH[name]; return ((cx + s / 2) / (size - 1), (cy + s / 2) / (size - 1))
