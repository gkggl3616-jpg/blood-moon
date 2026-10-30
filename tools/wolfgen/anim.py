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
    add(p, 'Spine', 2 + 1.2 * b); add(p, 'Chest', 1.5 * b); add(p, 'Neck', -1 - .8 * b); add(p, 'Head', -.5 * b)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, 2 * b, 0, -s * (1 + b)); add(p, 'Forearm' + L, -4 - 2 * b); add(p, 'Clav' + L, 0, 0, s * .8 * b)
        add(p, 'Thigh' + L, -3); add(p, 'Shin' + L, 6); add(p, 'Foot' + L, -3)
    add(p, 'Tail1', 6 + 3 * b); add(p, 'Tail2', 6 + 5 * math.sin(t * TAU - .6)); add(p, 'Tail3', 8 + 8 * math.sin(t * TAU - 1.2), 4 * math.sin(t * TAU))
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
    p = {}; ph = t * TAU
    H, S_, C_ = 56 + 4 * math.sin(2 * ph), 22 + 5 * math.sin(2 * ph + .8), 10
    add(p, 'Hips', H); add(p, 'Spine', S_); add(p, 'Chest', C_)
    add(p, 'Neck', -(H + S_ + C_) * .62 - 4 * math.sin(2 * ph)); add(p, 'Head', -10)
    tilt = H + S_ + C_
    for s, L, da, dl in ((1, 'L', 0.0, math.pi), (-1, 'R', .55, math.pi + .55)):
        sa = math.sin(ph + da)
        add(p, 'Clav' + L, -tilt * .0); add(p, 'UpperArm' + L, -(tilt) - 30 * sa + 16, 0, -s * 4)
        add(p, 'Forearm' + L, -(8 + 38 * max(0.0, math.sin(ph + da + 1.0)))); add(p, 'Hand' + L, 14 * sa - 4)
        sl = math.sin(ph + dl)
        th = -H - 34 * sl - 6; sh = 26 + 42 * max(0.0, -math.sin(ph + dl + .7))
        add(p, 'Thigh' + L, th); add(p, 'Shin' + L, sh); add(p, 'Foot' + L, -(H + th + sh) + 18 * sl)
    add(p, 'Tail1', 6, 0, 5 * math.sin(ph)); add(p, 'Tail2', 6, 0, 10 * math.sin(ph - .7)); add(p, 'Tail3', 8, 0, 14 * math.sin(ph - 1.4))
    return p, 'quad'


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
    up = sm(t / .26) * (1 - sm((t - .82) / .18)); hold = up
    shake = math.sin(t * TAU * 11) * up * (1 if .3 < t < .85 else .2)
    add(p, 'Hips', -4 * hold); add(p, 'Spine', -12 * hold); add(p, 'Chest', -14 * hold); add(p, 'Neck', -22 * hold + 2 * shake); add(p, 'Head', -34 * hold + 3 * shake)
    add(p, 'Jaw', 36 * hold + 8 * math.sin(t * TAU * 9) * hold)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'Clav' + L, 0, 0, s * 8 * hold); add(p, 'UpperArm' + L, -12 * hold, 0, s * 115 * hold); add(p, 'Forearm' + L, 0, 0, s * 100 * hold); add(p, 'Hand' + L, 0, 0, -s * 8 * hold)
        add(p, 'Thigh' + L, -6 * hold); add(p, 'Shin' + L, 12 * hold); add(p, 'Foot' + L, -4 * hold)
    add(p, 'Tail1', 12 * hold); add(p, 'Tail2', 14 * hold); add(p, 'Tail3', 16 * hold)
    return p, 'feet'


def roll(t):
    p = {}
    ang = 360 * sm(t * 1.0)
    add(p, 'Hips', ang)
    tuck = math.sin(math.pi * min(1, t * 1.15)) ** .8
    add(p, 'Spine', 32 * tuck); add(p, 'Chest', 22 * tuck); add(p, 'Neck', 14 * tuck); add(p, 'Head', 12 * tuck)
    for s, L in ((1, 'L'), (-1, 'R')):
        add(p, 'UpperArm' + L, -70 * tuck, 0, -s * 14 * tuck); add(p, 'Forearm' + L, -105 * tuck)
        add(p, 'Thigh' + L, -85 * tuck); add(p, 'Shin' + L, 120 * tuck); add(p, 'Foot' + L, -20 * tuck)
    add(p, 'Tail1', 12 * tuck); add(p, 'Tail2', 18 * tuck); add(p, 'Tail3', 20 * tuck)
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
    fn, dur, loop = CLIPS[name]; n = max(2, int(round(dur * fps)) + (0 if loop else 1)); frames = []
    for k in range(n):
        t = k / (n if loop else n - 1)
        pose, mode = fn(t)
        if mode == 'quad': root = ground_lock(skel, pose)
        elif mode == 'feet': root = feet_lock(skel, pose)
        elif mode == 'jump':
            root = feet_lock(skel, pose); air = sm((t - .24) / .12) * (1 - sm((t - .8) / .15)); root = (0, root[1] + .55 * air, 0)
        elif mode == 'roll':
            tuck = math.sin(math.pi * min(1, t * 1.15)) ** .8; root = (0, .52 + .08 * math.sin(math.pi * t) - .12 * 0 + 0 * tuck, 0)
        else: root = (0, 0, 0)
        frames.append((pose, root))
    return dict(duration=dur, frames=frames)
