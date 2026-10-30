"""Rebuild every shipped character from the Meshy rigs: python3 tools/meshy/build_all.py <meshy_out dir> [names...]
Wolves: Meshy idle/locomotion + the approved custom clips (quad run, flip attack, roar, claws, jump, transform)
carried over from the previous rig. Humans: Meshy idle + the first-person ready pose; FP arms cut from the full body."""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(__file__)); import build_game as bg
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); MODELS = os.path.join(ROOT, 'app/src/main/assets/models')
WOLF_A = ['Combat_Stance', 'Monster_Walk', 'RunFast', 'Basic_Jump', 'Idle', 'Slow_Orc_Walk', 'Zombie_Scream']
WOLF_B = ['Run_02', 'Run_03', 'Quick_Walk', 'Walk_Fight_Forward']
# WolfMove = Meshy Quick_Walk (anim_b #2), retimed so its feet move at 3.6 m/s at timescale 1 (the engine scales it to the
# wolf's actual speed); durations measured per model with clip_speed.py so the feet do not slide.
OLD_FROM = {'kral': 13588}   # vertices after the generated body: horns + cloak built in tools/wolfgen/build_variant.py
WALK = {'bilge': 1.948, 'ates': 1.891, 'kral': 2.076, 'ay': 1.743, 'hellgate': 1.814, 'zeynos': 1.719}
def wolf(name, U, src=None):
    d = os.path.join(U, name); specs = [(os.path.join(d, 'anim_a.glb'), [('WolfIdle', {}), None, None, None, None, None, None])]
    transfer = [('WolfRunQuad', 'WolfRunQuad', {}), ('WolfJump', 'WolfJump', {}), ('WolfRoar', 'WolfRoar', {}), ('WolfRoll', 'WolfRoll', {}),
                ('WolfClaw', 'WolfClaw', {}), ('WolfClawR', 'WolfClawR', {}), ('WolfTransform', 'WolfTransform', {})]
    if name in WALK and os.path.exists(os.path.join(d, 'anim_b.glb')):
        specs.append((os.path.join(d, 'anim_b.glb'), [('WolfJog', {}), None, ('WolfMove', {'duration': WALK[name]}), None]))
    else:
        transfer.insert(0, ('WolfMove', 'WolfMove', {}))
    specs = [(p, [x if x else (None, {}) for x in l]) for p, l in specs]
    out = os.path.join('/tmp', name + '_meshy.glb')
    bg.build(src or os.path.join(MODELS, name + '.glb'), os.path.join(d, 'rigged.glb'), specs, out, transfer=transfer, old_from=OLD_FROM.get(name))
    import foot_speeds; print('  foot speeds:', foot_speeds.patch(out))
    return out
def human(name, U, src=None):
    d = os.path.join(U, name)
    specs = [(os.path.join(d, 'anim_a.glb'), [('HumanIdle', {}), (None, {}), (None, {}), (None, {}), (None, {})])]
    out = os.path.join('/tmp', name + '_meshy.glb')
    bg.build(src or os.path.join(MODELS, name + '.glb'), os.path.join(d, 'rigged.glb'), specs, out, transfer=[('HumanReady', 'HumanReady', {})], fp_arms=True)
    return out
if __name__ == '__main__':
    U = sys.argv[1]; names = sys.argv[2:] or ['bilge', 'ates', 'kral', 'ay', 'hellgate', 'zeynos', 'human-bilge', 'human-ates', 'human-kral', 'human-ay', 'human-hellgate', 'human-zeynos']
    src_dir = os.environ.get('SRC_DIR')
    for n in names:
        print('==', n); src = os.path.join(src_dir, n + '.glb') if src_dir else None
        out = (human if n.startswith('human-') else wolf)(n, U, src)
        if os.environ.get('INSTALL'): shutil.copy(out, os.path.join(MODELS, n + '.glb'))
