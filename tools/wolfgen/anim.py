"""Procedural clips for the engine skeleton.  Pose = {bone: (rx,ry,rz) degrees}, rest = world-aligned axes.
+rx on a limb hanging down swings it BACKWARD; -rx swings it forward.  +rx on an upright spine leans FORWARD."""
import math
import numpy as np
from core import *

FPS = 30
TAU = 2 * math.pi


def sm(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t


def add(pose, bone, rx=0, ry=0, rz=0):
    o = pose.get(bone, (0, 0, 0)); pose[bone] = (o[0] + rx, o[1] + ry, o[2] + rz)


def ground_lock(skel, pose, base_y=0.0, hand_off=.10, foot_off=.10):
    jw = skel.joint_world(pose)
    low = min(jw['HandL'][1] - hand_off, jw['HandR'][1] - hand_off, jw['FootL'][1] - foot_off, jw['FootR'][1] - foot_off)
    return (0, base_y - low, 0)


def feet_lock(skel, pose, foot_off=.10):
    jw = skel.joint_world(pose)
    return (0, -(min(jw['FootL'][1], jw['FootR'][1]) - foot_off), 0)


def idle(t):
    p = {}; b = math.sin(t * TAU)
    add(p, 'Hips', 10); add(p, 'Spine', 16 + 1.5 * b); add(p, 'Chest', 8 + 1.2 * b); add(p, 'Neck', -14 - .8 * b); add(p, 'Head', -6 - .5 * b)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, -16 + 2 * b, 0, s * 10 + s * b); add(p, 'Forearm' + L, -26 - 3 * b); add(p, 'Hand' + L, 8); add(p, 'Clav' + L, 0, 0, s * 3)
        add(p, 'Thigh' + L, -34); add(p, 'Shin' + L, 52); add(p, 'Foot' + L, -(10 - 34 + 52))
    add(p, 'Tail1', 8 + 3 * b); add(p, 'Tail2', 6 + 5 * math.sin(t * TAU - .6)); add(p, 'Tail3', 8 + 8 * math.sin(t * TAU - 1.2), 4 * math.sin(t * TAU))
    return p, 'feet'


def walk(t):
    p = {}; ph = t * TAU
    add(p, 'Hips', 4 + 2 * abs(math.sin(ph)), 5 * math.sin(ph)); add(p, 'Spine', 4, -3 * math.sin(ph)); add(p, 'Chest', 3, -3 * math.sin(ph)); add(p, 'Neck', -6); add(p, 'Head', -4)
    for s, L, o in ((1, 'L', 0), (-1, 'R', math.pi)):
        sw = math.sin(ph + o)
        add(p, 'Thigh' + L, -26 * sw - 4, 0, 0); add(p, 'Shin' + L, 14 + 30 * max(0, -math.sin(ph + o + 1.1)))
        add(p, 'Foot' + L, 10 * sw - 6 - 0.3 * 30 * max(0, -math.sin(ph + o + 1.1)))
        add(p, 'UpperArm' + L, 24 * sw, 0, -s * 3); add(p, 'Forearm' + L, -14 - 14 * max(0, -sw))
    add(p, 'Tail1', 8, 0, 6 * math.sin(ph)); add(p, 'Tail2', 8, 0, 9 * math.sin(ph - .6)); add(p, 'Tail3', 10, 0, 12 * math.sin(ph - 1.2))
    return p, 'feet'


def run_quad(t):
    """Wolf gallop: forelegs reach and plant (hand on ground), hind legs push; hand height solved in bake()."""
    p = {}; ph = t * TAU
    H, S_, C_ = 58 + 5 * math.sin(2 * ph), 24 + 8 * math.sin(2 * ph + .8), 14 - 6 * math.sin(2 * ph + .8)
    add(p, 'Hips', H); add(p, 'Spine', S_); add(p, 'Chest', C_)
    add(p, 'Neck', -(H + S_ + C_) * .66 - 4 * math.sin(2 * ph)); add(p, 'Head', -8)
    tilt = H + S_ + C_
    for s, L, da, dl in ((1, 'L', 0.0, math.pi), (-1, 'R', .55, math.pi + .55)):
        sa = math.sin(ph + da)
        add(p, 'UpperArm' + L, -(tilt) - 34 * sa - 14, 0, -s * 3)       # reach forward / pull back
        add(p, 'Hand' + L, 12 * sa - 4)
        sl = math.sin(ph + dl)
        th = -H - 46 - 34 * sl; sh = 62 + 50 * max(0.0, -math.sin(ph + dl + .7))
        add(p, 'Thigh' + L, th); add(p, 'Shin' + L, sh); add(p, 'Foot' + L, -(H + th + sh) + 18 * sl)
    add(p, 'Tail1', -22, 0, 5 * math.sin(ph)); add(p, 'Tail2', -8, 0, 10 * math.sin(ph - .7)); add(p, 'Tail3', -4, 0, 14 * math.sin(ph - 1.4))
    return p, 'quad'


def plant_hands(skel, pose, t, hand_off=.10):
    """Solve Forearm bend so the hand touches the ground while the foreleg is in stance and lifts in swing."""
    ph = t * TAU; root = feet_lock(skel, pose)
    for L, da in (('L', 0.0), ('R', .55)):
        sa = math.sin(ph + da)                      # >0 = arm pulled back (stance), <0 = reaching/swing
        lift = .30 * max(0.0, -sa) ** .8
        target = hand_off + lift
        lo, hi = -125.0, 0.0
        for _ in range(26):
            mid = (lo + hi) / 2; q = dict(pose); q['Forearm' + L] = (mid, 0, 0)
            y = skel.joint_world(q, root)['Hand' + L][1]
            if y > target: hi = mid          # too high -> bend more (more negative)... keep monotone search
            else: lo = mid
        # choose the bend giving hand height closest to target
        best = min((abs(skel.joint_world({**pose, 'Forearm' + L: (r, 0, 0)}, root)['Hand' + L][1] - target), r) for r in np.linspace(-125, 20, 59))[1]
        pose['Forearm' + L] = (best, 0, 0)
    return pose


def jump(t):
    p = {}
    crouch = sm(t / .22) * (1 - sm((t - .22) / .12)); air = sm((t - .24) / .12) * (1 - sm((t - .8) / .15)); land = sm((t - .8) / .08) * (1 - sm((t - .95) / .05))
    add(p, 'Spine', 20 * crouch - 6 * air + 10 * land); add(p, 'Chest', 12 * crouch + 6 * land); add(p, 'Neck', -8 * crouch - 8 * air); add(p, 'Head', -6 * air)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'Thigh' + L, -(40 * crouch + 55 * air + 38 * land)); add(p, 'Shin' + L, 60 * crouch + 85 * air + 70 * land); add(p, 'Foot' + L, -(20 * crouch - 25 * air))
        add(p, 'UpperArm' + L, 35 * crouch - 70 * air - 20 * land, 0, -s * (6 + 28 * air)); add(p, 'Forearm' + L, -(15 + 50 * air))
    add(p, 'Tail1', -10 * air + 10 * crouch); add(p, 'Tail2', -12 * air); add(p, 'Tail3', -14 * air)
    return p, 'jump'


def roar(t):
    """Ice Rage Roar, 5 s: prep 0-.8 (crouch, head down), build .8-1.6 (fists, chest swells), roar 1.6-2.5 (head snaps
    45-60 deg up, chest out, back arched, arms open to the sides, palms up/forward, wide stance with the right leg
    forward), blast 2.5-3.5 (held, trembling), calm 3.5-5 (back to the ready stance)."""
    T = t * 5.0; p = {}
    def env(a, b, c, d): return sm((T - a) / max(b - a, 1e-6)) * (1 - sm((T - c) / max(d - c, 1e-6)))
    prep = env(0, .6, 1.4, 1.75)            # crouch / head down
    build = env(.8, 1.55, 1.6, 1.85)        # fists, chest swells
    R = env(1.6, 1.92, 3.5, 4.7)            # main roar pose (fast in, slow out)
    tr = math.sin(T * TAU * 2.3) * (env(2.0, 2.3, 3.4, 3.7) * 1.0 + build * .4)   # muscle tremble
    # torso
    add(p, 'Hips', 10 * prep + 4 * build - 6 * R)
    add(p, 'Spine', 20 * prep + 6 * build - 14 * R + .6 * tr)
    add(p, 'Chest', 10 * prep - 6 * build - 18 * R + .8 * tr)
    add(p, 'Neck', 16 * prep + 6 * build - 28 * R + 1.2 * tr, 0, 3 * R)
    add(p, 'Head', 12 * prep - 4 * build - 30 * R + 2 * tr)
    add(p, 'Jaw', 10 * build + 46 * R + 4 * math.sin(T * TAU * 6) * R)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'Clav' + L, 0, -s * 8 * prep, s * (-4 * prep + 6 * build + 4 * R))
        add(p, 'UpperArm' + L, -14 * prep + 6 * build + 6 * R, -s * 14 * R, s * (6 * prep + 18 * build + 46 * R) + s * 1.2 * tr)
        add(p, 'Forearm' + L, -26 * prep - 58 * build - 28 * R, -s * 20 * R, s * 6 * R)
        add(p, 'Hand' + L, 18 * build - 24 * R, -s * 30 * R, -s * (14 * build - 6 * R))
    # legs: wider than shoulders, knees bent; right leg reaches forward/out, left leg carries the weight
    add(p, 'ThighL', -(22 * prep + 10 * build + 18 * R), 0, 8 * build + 16 * R); add(p, 'ShinL', 34 * prep + 18 * build + 40 * R); add(p, 'FootL', -(12 * prep + 8 * build + 22 * R), 0, -16 * R)
    add(p, 'ThighR', -(22 * prep + 10 * build + 42 * R), 0, -(8 * build + 22 * R)); add(p, 'ShinR', 34 * prep + 18 * build + 34 * R); add(p, 'FootR', -(12 * prep + 8 * build) + 8 * R, 0, 22 * R)
    sw = math.sin(T * TAU * .9)
    add(p, 'Tail1', 6 * prep - 14 * R, 0, 14 * R + 4 * sw * R); add(p, 'Tail2', -6 * R, 0, 12 * R + 7 * sw * R); add(p, 'Tail3', 6 * R, 0, 10 * R + 10 * sw * R)
    return p, 'feet'


def roll(t):
    """Attack shoulder-roll: dive low, tuck into a tight ball that tumbles along the ground, come up on all fours."""
    p = {}
    tuck = sm(t / .16) * (1 - sm((t - .72) / .2))
    ang = 360 * sm((t - .1) / .66)
    rise = sm((t - .74) / .26)
    add(p, 'Hips', ang + 30 * rise * (1 - sm((t - .92) / .08)))
    add(p, 'Spine', 58 * tuck + 14 * rise); add(p, 'Chest', 44 * tuck); add(p, 'Neck', 40 * tuck - 10 * rise); add(p, 'Head', 26 * tuck)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, -120 * tuck - 30 * rise, 0, -s * 18 * tuck); add(p, 'Forearm' + L, -125 * tuck - 30 * rise)
        add(p, 'Thigh' + L, -125 * tuck - 40 * rise); add(p, 'Shin' + L, 150 * tuck + 70 * rise); add(p, 'Foot' + L, -30 * tuck)
    add(p, 'Tail1', 40 * tuck); add(p, 'Tail2', 40 * tuck); add(p, 'Tail3', 30 * tuck)
    return p, 'roll'


def ball_lock(skel, pose, pad=.2):
    """keep the lowest joint of the tumbling body on the ground so the roll never floats."""
    jw = skel.joint_world(pose)
    return (0, pad - min(v[1] for k, v in jw.items() if not k.startswith('Tail') and k != 'Root'), 0)


def claw(t):
    p = {}
    wind = sm(t / .28) * (1 - sm((t - .32) / .06)); strike = sm((t - .28) / .12) * (1 - sm((t - .62) / .38))
    add(p, 'Hips', 6 * strike, -14 * strike + 12 * wind); add(p, 'Spine', 8 * strike, -22 * strike + 18 * wind); add(p, 'Chest', 6 * strike, -18 * strike + 14 * wind)
    add(p, 'Neck', -4 * strike); add(p, 'Head', -8 * strike, 8 * strike)
    # right arm: raise high & back, slash down-across
    add(p, 'ClavR', 0, 0, -8 * wind); add(p, 'UpperArmR', -160 * wind + 20 * strike + (-40) * (1 - 0) * strike * 0, 0, 55 * wind - 20 * strike)
    add(p, 'UpperArmR', -50 * strike, 0, 0); add(p, 'ForearmR', -30 * wind - 18 * strike); add(p, 'HandR', 0, 0, 12 * strike)
    add(p, 'UpperArmL', 8 * wind, 0, 6); add(p, 'ForearmL', -20)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'Thigh' + L, -12 * (wind + strike)); add(p, 'Shin' + L, 22 * (wind + strike)); add(p, 'Foot' + L, -8 * (wind + strike))
    add(p, 'Tail1', 6, 0, 10 * strike); add(p, 'Tail2', 6, 0, 14 * strike)
    return p, 'feet'


def transform(t):
    p = {}
    c = math.sin(math.pi * t); sh = math.sin(t * TAU * 8) * c
    add(p, 'Hips', 10 * c); add(p, 'Spine', 26 * c, 0, 3 * sh); add(p, 'Chest', 18 * c, 0, -3 * sh); add(p, 'Neck', -10 * c); add(p, 'Head', 8 * c, 4 * sh)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, -34 * c, 0, -s * 12 * c); add(p, 'Forearm' + L, -56 * c)
        add(p, 'Thigh' + L, -28 * c); add(p, 'Shin' + L, 52 * c); add(p, 'Foot' + L, -10 * c)
    add(p, 'Tail1', 10 * c); add(p, 'Tail2', 12 * c); add(p, 'Tail3', 12 * c)
    return p, 'feet'


CLIPS = {  # name: (fn, duration_s, loop)
    'WolfIdle': (idle, 2.4, True), 'WolfMove': (walk, 1.0, True), 'WolfRunQuad': (run_quad, .62, True), 'WolfJump': (jump, 1.0, False),
    'WolfRoar': (roar, 5.0, False), 'WolfRoll': (roll, .8, False), 'WolfClaw': (claw, .62, False), 'WolfTransform': (transform, 1.0, False), 'WolfClawR': (claw, .65, False),
}


def bake(skel, name, fps=FPS):
    if name in MIX: return bake_mixamo(skel, name, fps)
    fn, dur, loop = CLIPS[name]; n = max(2, int(round(dur * fps)) + (0 if loop else 1)); frames = []
    for k in range(n):
        t = k / (n if loop else n - 1)
        pose, mode = fn(t)
        if mode == 'quad': pose = plant_hands(skel, pose, t); root = ground_lock(skel, pose)
        elif mode == 'feet': root = feet_lock(skel, pose)
        elif mode == 'jump':
            root = feet_lock(skel, pose); air = sm((t - .24) / .12) * (1 - sm((t - .8) / .15)); root = (0, root[1] + .55 * air, 0)
        elif mode == 'roll': root = ball_lock(skel, pose)
        else: root = (0, 0, 0)
        frames.append((pose, root))
    return dict(duration=dur, frames=frames)


# ----------------------------------------------------------------------------- Mixamo-retargeted clips (baked JSON)
import json, os
BAKED = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'retarget', 'baked')
MIX = {'WolfIdle': ('idle', 6.0, True), 'WolfClaw': ('clawR', .65, False), 'WolfJump': ('jump', .9, False), 'WolfClawR': ('clawR', .65, False)}


def _nlerp(a, b, u):
    a = np.asarray(a); b = np.asarray(b)
    if np.dot(a, b) < 0: b = -b
    q = a * (1 - u) + b * u; return q / np.linalg.norm(q)


def bake_mixamo(skel, name, fps=FPS):
    key, dur, loop = MIX[name]; d = json.load(open(os.path.join(BAKED, key + '.json'))); src = d['frames']; m = len(src)
    n = max(2, int(round(dur * fps)) + (0 if loop else 1)); frames = []
    for k in range(n):
        u = (k / (n if loop else n - 1)) * (m - 1); i = min(int(u), m - 2); f = u - i
        pose = {b: tuple(_nlerp(src[i]['q'][b], src[i + 1]['q'][b], f)) for b in src[0]['q']}
        if name == 'WolfClawR':   # the supplied slash is left-handed: mirror it across the sagittal plane for the right arm
            sw = lambda b: b[:-1] + ('R' if b.endswith('L') else 'L') if b[-1] in 'LR' and b not in ('Hips',) else b
            pose = {sw(b): (q[0], -q[1], -q[2], q[3]) for b, q in pose.items()}
        dy = src[i]['dy'] * (1 - f) + src[i + 1]['dy'] * f
        t = k / (n if loop else n - 1); ph = t * TAU
        if name == 'WolfRoar':
            op = math.sin(math.pi * min(1, max(0, (t - .12) / .7))) ; pose['Jaw'] = (38 * op ** .6 + 7 * math.sin(t * TAU * 10) * op, 0, 0)
        add(pose, 'Tail1', 6, 0, 5 * math.sin(ph)); add(pose, 'Tail2', 8, 0, 9 * math.sin(ph - .7)); add(pose, 'Tail3', 10, 0, 13 * math.sin(ph - 1.4))
        frames.append([pose, dy])
    if loop:   # crossfade the tail of the loop into its first frame so it repeats seamlessly
        X = 24
        for k in range(X):
            w = (k + 1) / X; w = w * w * (3 - 2 * w); j = n - X + k
            frames[j][0] = {b: (tuple(_nlerp(frames[j][0][b], frames[0][0][b], w)) if len(frames[j][0][b]) == 4 else frames[j][0][b]) for b in frames[j][0]}
            frames[j][1] = frames[j][1] * (1 - w) + frames[0][1] * w
    out = []
    base = None
    for pose, dy in frames:
        if name == 'WolfJump':
            if base is None: base = feet_lock(skel, pose)[1]
            root = (0, base + dy, 0)
        else: root = feet_lock(skel, pose)
        out.append((pose, root))
    return dict(duration=dur, frames=out)
