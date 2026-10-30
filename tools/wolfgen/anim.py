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
    H, S_, C_ = 62 + 5 * math.sin(2 * ph), 26 + 5 * math.sin(2 * ph + .8), 12
    add(p, 'Hips', H); add(p, 'Spine', S_); add(p, 'Chest', C_)
    add(p, 'Neck', -(H + S_ + C_) * .66 - 4 * math.sin(2 * ph)); add(p, 'Head', -8)
    tilt = H + S_ + C_
    for s, L, da, dl in ((1, 'L', 0.0, math.pi), (-1, 'R', .55, math.pi + .55)):
        sa = math.sin(ph + da)
        add(p, 'UpperArm' + L, -(tilt) - 36 * sa + 6, 0, -s * 3)       # reach forward / pull back
        add(p, 'Hand' + L, 12 * sa - 4)
        sl = math.sin(ph + dl)
        th = -H - 34 * sl - 8; sh = 30 + 46 * max(0.0, -math.sin(ph + dl + .7))
        add(p, 'Thigh' + L, th); add(p, 'Shin' + L, sh); add(p, 'Foot' + L, -(H + th + sh) + 18 * sl)
    add(p, 'Tail1', 6, 0, 5 * math.sin(ph)); add(p, 'Tail2', 6, 0, 10 * math.sin(ph - .7)); add(p, 'Tail3', 8, 0, 14 * math.sin(ph - 1.4))
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
    p = {}
    pre = sm(t / .16) * (1 - sm((t - .16) / .08))          # coil forward, claws down
    up = sm((t - .18) / .12) * (1 - sm((t - .84) / .16)); hold = up
    shake = math.sin(t * TAU * 13) * up * (1 if .3 < t < .85 else .3)
    add(p, 'Hips', 10 * pre - 6 * hold); add(p, 'Spine', 22 * pre - 18 * hold); add(p, 'Chest', 14 * pre - 20 * hold)
    add(p, 'Neck', 10 * pre - 28 * hold + 2.5 * shake); add(p, 'Head', 8 * pre - 38 * hold + 3.5 * shake)
    add(p, 'Jaw', 42 * hold + 10 * math.sin(t * TAU * 10) * hold)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'Clav' + L, 0, 0, s * 10 * hold); add(p, 'UpperArm' + L, -20 * pre - 12 * hold, 0, s * 115 * hold + s * 2 * shake)
        add(p, 'Forearm' + L, -30 * pre, 0, s * 100 * hold); add(p, 'Hand' + L, 0, 0, -s * 8 * hold)
        add(p, 'Thigh' + L, -(30 * pre + 38 * hold)); add(p, 'Shin' + L, 44 * pre + 62 * hold); add(p, 'Foot' + L, -(14 * pre - 20 * hold))
    add(p, 'Tail1', 12 * hold); add(p, 'Tail2', 14 * hold); add(p, 'Tail3', 16 * hold)
    return p, 'feet'


def roll(t):
    p = {}
    dive = sm(t / .22); rise = sm((t - .78) / .22)
    ang = 360 * sm((t - .12) / .72)
    add(p, 'Hips', ang)
    tuck = sm((t - .05) / .2) * (1 - sm((t - .8) / .2))
    add(p, 'Spine', 50 * tuck); add(p, 'Chest', 34 * tuck); add(p, 'Neck', 26 * tuck); add(p, 'Head', 14 * tuck)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, -105 * tuck, 0, -s * 10 * tuck); add(p, 'Forearm' + L, -110 * tuck)
        add(p, 'Thigh' + L, -(100 * tuck + 30 * (1 - tuck) * 0)); add(p, 'Shin' + L, 135 * tuck); add(p, 'Foot' + L, -25 * tuck)
    add(p, 'Tail1', 14 * tuck); add(p, 'Tail2', 20 * tuck); add(p, 'Tail3', 22 * tuck)
    return p, 'roll'


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
    'WolfRoar': (roar, 1.2, False), 'WolfRoll': (roll, .8, False), 'WolfClaw': (claw, .62, False), 'WolfTransform': (transform, 1.0, False),
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
        elif mode == 'roll':
            tuck = math.sin(math.pi * min(1, t * 1.15)) ** .8; root = (0, .52 + .08 * math.sin(math.pi * t) - .12 * 0 + 0 * tuck, 0)
        else: root = (0, 0, 0)
        frames.append((pose, root))
    return dict(duration=dur, frames=frames)


# ----------------------------------------------------------------------------- Mixamo-retargeted clips (baked JSON)
import json, os
BAKED = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'retarget', 'baked')
MIX = {'WolfIdle': ('idle', 6.0, True), 'WolfRoar': ('roar', 1.2, False), 'WolfClaw': ('clawR', .65, False), 'WolfJump': ('jump', .9, False)}


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
