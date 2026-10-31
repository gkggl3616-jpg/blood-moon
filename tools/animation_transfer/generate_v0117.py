"""Bake the reviewed Wolfteam motions onto each shipped deform rig.

This generator is intentionally offline: it reads the user supplied LTB archive and the
unchanged pre-transfer GLBs, then writes compact animation-only payloads.  Geometry,
skin joints, inverse bind matrices, materials, images, UVs and source DTX files are not
rewritten.  Each target keeps its own rest pose and bone lengths.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('/workspace/extracted/wt_chars/models')
BASELINE = Path('/workspace/model-baseline')
CATALOG = Path('/workspace/catalog')
sys.path.insert(0, str(CATALOG))
sys.path.insert(0, str(ROOT / 'tools/meshy'))
from animation_reader import read  # noqa: E402
from export_animations import decode  # noqa: E402
from glbio import GLB, skin, world_with, sample_trs, _slerp  # noqa: E402

OUT = ROOT / 'tools/animation_transfer/data'
OUT.mkdir(parents=True, exist_ok=True)
VARIANTS = {
    'bilge': 'wt_wolf_ch', 'ates': 'wt_wolf_smart_ch',
    'kral': 'wt_wolf_guardian_ch', 'hellgate': 'wt_wolf_berserker_ch',
    'ay': 'wt_wolf_woman_b_ch', 'zeynos': 'wt_wolf_woman_r_ch',
}
MAP = {'Hips': 'Bip01 Pelvis', 'Spine': 'Bip01 Spine', 'Spine1': 'Bip01 Spine1',
       'Chest': 'Bip01 Spine2', 'Neck': 'Bip01 Neck', 'Head': 'Bip01 Head'}
for side in 'LR':
    for target, source in [('Clav', 'Clavicle'), ('UpperArm', 'UpperArm'),
                           ('Forearm', 'Forearm'), ('Hand', 'Hand'),
                           ('Thigh', 'Thigh'), ('Shin', 'Calf'),
                           ('Foot', 'Foot'), ('Toe', 'Toe0')]:
        MAP[target + side] = f'Bip01 {side} {source}'

CHILD = {'Spine': 'Spine1', 'Spine1': 'Chest', 'Chest': 'Neck', 'Neck': 'Head'}
for side in 'LR':
    for parent, child in [('Clav', 'UpperArm'), ('UpperArm', 'Forearm'),
                          ('Forearm', 'Hand'), ('Thigh', 'Shin'),
                          ('Shin', 'Foot'), ('Foot', 'Toe')]:
        CHILD[parent + side] = child + side

_CACHE = {}


def source(stem, clip):
    key = (stem, clip)
    if key in _CACHE:
        return _CACHE[key]
    path = ARCHIVE / f'{stem}.ltb'
    data = read(path, True)
    animation = next((a for a in data['animations'] if a['name'] == clip), None)
    if animation is None:
        fallback = 'wt_wolf_ch' if 'wolf' in stem else 'wt_man_ch'
        return source(fallback, clip)
    _, _, samples, bind, _ = decode({'nodes': data['nodes'], 'animation': animation})
    reference = [bind[0] if i == 0 else bind[0] @ matrix for i, matrix in enumerate(bind)]
    _CACHE[key] = data, animation, samples, reference, path
    return _CACHE[key]


def align(a, b):
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    axis = np.cross(a, b)
    length = np.linalg.norm(axis)
    dot = np.clip(a @ b, -1, 1)
    if length < 1e-8:
        if dot > 0:
            return np.eye(3)
        axis = np.cross(a, [1, 0, 0] if abs(a[0]) < .8 else [0, 1, 0])
        axis /= np.linalg.norm(axis)
        return R.from_rotvec(axis * np.pi).as_matrix()
    return R.from_rotvec(axis / length * np.arctan2(length, dot)).as_matrix()


def ortho(matrix):
    u, _, v = np.linalg.svd(matrix[:3, :3])
    result = u @ v
    if np.linalg.det(result) < 0:
        u[:, -1] *= -1
        result = u @ v
    return result


def continuous(quaternions, loop=False):
    values = np.asarray(quaternions, dtype=float)
    if loop:
        values[-1] = values[0]
    for frame in range(1, len(values)):
        values[frame] /= max(np.linalg.norm(values[frame]), 1e-12)
        if values[frame] @ values[frame - 1] < 0:
            values[frame] *= -1
    values[0] /= max(np.linalg.norm(values[0]), 1e-12)
    return values.astype('float32')


def human_idle(g, old, nodes, bone_names):
    """Keep the compatible idle, remove yaw/XZ drift and add a subtle 3.2 s breath."""
    clip = old['HumanIdle']
    duration = 3.2
    frames = 97
    times = np.linspace(0, duration, frames, dtype='float32')
    hips = bone_names['Hips']
    chest = bone_names['Chest']
    channels = []
    hip_t, hip_q, chest_q = [], [], []
    first = sample_trs(g, clip, 0)
    neutral_t = np.array(first.get(hips, {}).get('translation', nodes[hips].get('translation', [0, 0, 0])), float)
    neutral_q = np.array(first.get(hips, {}).get('rotation', nodes[hips].get('rotation', [0, 0, 0, 1])), float)
    for t in times:
        pose = sample_trs(g, clip, float(t % max(duration, 1e-6)))
        tr = np.array(pose.get(hips, {}).get('translation', neutral_t), float)
        tr[0] = neutral_t[0]
        tr[2] = neutral_t[2]
        hip_t.append(tr)
        # A stationary pelvis prevents the unrelated side-to-side turn.
        hip_q.append(neutral_q)
        base = np.array(pose.get(chest, {}).get('rotation', nodes[chest].get('rotation', [0, 0, 0, 1])), float)
        breath = R.from_rotvec([np.deg2rad(1.15) * np.sin(2 * np.pi * t / duration), 0, 0]).as_quat()
        chest_q.append((R.from_quat(base) * R.from_quat(breath)).as_quat())
    hip_t[-1] = hip_t[0]
    channels.append({'node': hips, 'path': 'translation', 'times': times.tolist(),
                     'values': np.asarray(hip_t, dtype='float32').tolist()})
    channels.append({'node': hips, 'path': 'rotation', 'times': times.tolist(),
                     'values': continuous(hip_q, True).tolist()})
    channels.append({'node': chest, 'path': 'rotation', 'times': times.tolist(),
                     'values': continuous(chest_q, True).tolist()})
    return {'name': 'HumanIdle', 'mode': 'override_channels', 'duration': duration, 'loop': True,
            'source': {'file': 'original target HumanIdle', 'clip': 'yaw-locked + 3.2s chest breath',
                       'duration': duration, 'matched_bones': 2}, 'channels': channels}


def build_target(key, form):
    name = key if form == 'wolf' else f'human-{key}'
    path = BASELINE / f'{name}.glb'
    g = GLB(path)
    world, parent = g.node_world()
    nodes = g.j['nodes']
    bone_names = {node.get('name'): i for i, node in enumerate(nodes)}
    joints = set(g.j['skins'][0]['joints'])
    hips = bone_names['Hips']
    rest_rotation = [ortho(matrix) for matrix in world]
    order = []

    def visit(index):
        order.append(index)
        for child in nodes[index].get('children', []):
            visit(child)
    for index in range(len(nodes)):
        if index not in parent:
            visit(index)

    old = {animation['name']: animation for animation in g.j['animations']}
    duration_of = lambda clip: float(max(g.acc(s['input']).max() for s in old[clip]['samplers']))
    if form == 'wolf':
        variant = VARIANTS[key]
        specs = [
            ('WolfIdle', 'wt_wolf_ch', 'Ui_idle', 1.333, True),
            ('WolfMove', variant, 'LWF', .933, True),
            ('WolfJog', variant, 'LRF', .7, True),
            ('WolfRunQuad', 'wt_wolf_ch', 'T_WallDash', .533, True),
            ('WolfRoll', 'wt_wolf_ch', 'T_Specialatk', 1.2, False),
            ('WolfRoar', variant, 'T_CRY', 1.4, False),
            ('WolfClaw', variant, 'UMFi1', duration_of('WolfClaw'), False),
            ('WolfClawR', variant, 'UMFi2', duration_of('WolfClawR'), False),
        ]
    else:
        donor = 'wt_new_woman_ch' if key in ('ay', 'zeynos') else 'wt_man_ch'
        # Kara Han's cloak is joined to the lower body in the source mesh.  Its reviewed
        # target walk/run are retained so the new cloak attachment is not pulled by a
        # second leg retarget; only the broken idle is replaced for this character.
        specs = [] if key == 'kral' else [('HumanWalk', donor, 'LWF', .933, True),
                 ('HumanRun', donor, 'LRF', .7, True)]

    body = next(i for i, node in enumerate(nodes)
                if node.get('name', '').startswith('Body') and 'skin' in node)
    bind_positions, _ = skin(g, world, body)
    ground = float(bind_positions[:, 1].min())
    clips = []
    for destination, stem, source_clip, duration, loop in specs:
        if name == 'zeynos' and destination == 'WolfClawR':
            continue
        data, animation, samples, reference, source_path = source(stem, source_clip)
        source_names = {node['name']: i for i, node in enumerate(data['nodes'])}
        mapped = {bone_names[target]: source_names[source_name] for target, source_name in MAP.items()
                  if target in bone_names and source_name in source_names}
        assert len(mapped) >= 20
        source_leg = reference[source_names['Bip01 L Thigh']][:3, 3] - reference[source_names['Bip01 Pelvis']][:3, 3]
        target_leg = world[bone_names['ThighL']][:3, 3] - world[hips][:3, 3]
        angle = np.arctan2(target_leg[0], target_leg[2]) - np.arctan2(source_leg[0], source_leg[2])
        axis_fix = R.from_rotvec([0, angle, 0]).as_matrix()
        frame_count = len(samples)
        times = np.array(animation['times'], float) / 1000
        times = (times - times[0]) / (times[-1] - times[0]) * duration
        tracks = {index: [] for index in joints}
        translations = []
        source_hips = source_names['Bip01 Pelvis']
        source_hip_rest = reference[source_hips][:3, 3]
        target_hip_rest = world[hips][:3, 3]
        height_ratio = abs(target_hip_rest[1]) / max(abs(source_hip_rest[1]), .1)
        neutral_hip_q = np.array(sample_trs(g, old[destination], 0).get(hips, {}).get(
            'rotation', nodes[hips].get('rotation', [0, 0, 0, 1])), float)
        for frame in range(frame_count):
            current = {}
            overrides = {}
            original_pose = sample_trs(g, old[destination], duration_of(destination) * frame / max(frame_count - 1, 1))
            for index in order:
                parent_index = parent.get(index)
                parent_rotation = current[parent_index] if parent_index is not None else np.eye(3)
                if index in mapped:
                    source_index = mapped[index]
                    world_rotation = axis_fix @ ortho(samples[frame, source_index]) @ ortho(reference[source_index]).T @ axis_fix.T @ rest_rotation[index]
                    bone = nodes[index].get('name', '')
                    child = CHILD.get(bone)
                    source_child = MAP.get(child)
                    if child in bone_names and source_child in source_names:
                        target_direction = world[bone_names[child]][:3, 3] - world[index][:3, 3]
                        source_direction = axis_fix @ (samples[frame, source_names[source_child], :3, 3] - samples[frame, source_index, :3, 3])
                        world_rotation = align(target_direction, source_direction) @ rest_rotation[index]
                    if bone.startswith('Hand') and parent_index is not None:
                        world_rotation = parent_rotation @ (rest_rotation[parent_index].T @ rest_rotation[index])
                else:
                    world_rotation = parent_rotation @ (rest_rotation[parent_index].T @ rest_rotation[index] if parent_index is not None else rest_rotation[index])
                bone = nodes[index].get('name', '')
                old_q = np.array(original_pose.get(index, {}).get('rotation', nodes[index].get('rotation', [0, 0, 0, 1])), float)
                if bone == 'Hips' and destination in ('WolfIdle', 'WolfMove', 'WolfJog', 'WolfRunQuad'):
                    world_rotation = parent_rotation @ R.from_quat(neutral_hip_q).as_matrix()
                # The source and target have different anatomy.  The canonical source supplies
                # phase/direction while each target retains most of its compatible deform pose.
                blend = .50 if destination in ('WolfMove', 'WolfJog') else .65 if destination == 'WolfRunQuad' else .35 if destination == 'WolfIdle' else 1.0
                if destination in ('WolfMove', 'WolfJog', 'WolfRunQuad', 'WolfIdle') and index in joints and index != hips:
                    new_q = R.from_matrix(parent_rotation.T @ world_rotation).as_quat()
                    world_rotation = parent_rotation @ R.from_quat(_slerp(old_q, new_q, blend)).as_matrix()
                keep_human = form == 'human' and not bone.startswith(('Thigh', 'Shin', 'Foot', 'Toe'))
                keep_roll_arm = destination == 'WolfRoll' and bone.startswith(('Clav', 'UpperArm', 'Forearm', 'Hand'))
                keep_secondary = bone.startswith(('Tail', 'Hair', 'Cape', 'Ear'))
                keep_zeynos = name == 'zeynos' and destination.startswith('WolfClaw') and bone in ('Spine', 'Spine1', 'Chest', 'Neck', 'Head', 'ClavL', 'ClavR')
                if keep_human or keep_roll_arm or keep_secondary or keep_zeynos:
                    world_rotation = parent_rotation @ R.from_quat(old_q).as_matrix()
                elif destination == 'WolfRoll' and index in joints and index != hips:
                    new_q = R.from_matrix(parent_rotation.T @ world_rotation).as_quat()
                    world_rotation = parent_rotation @ R.from_quat(_slerp(old_q, new_q, .32)).as_matrix()
                current[index] = world_rotation
                if index in tracks:
                    q = R.from_matrix(parent_rotation.T @ world_rotation).as_quat()
                    tracks[index].append(q)
                    overrides.setdefault(index, {})['rotation'] = q
            delta = samples[frame, source_hips, :3, 3] - source_hip_rest
            delta[[0, 2]] = 0
            parent_matrix = world[parent[hips]] if hips in parent else np.eye(4)
            translation = (np.linalg.inv(parent_matrix) @ np.r_[target_hip_rest + delta * height_ratio, 1])[:3]
            overrides.setdefault(hips, {})['translation'] = translation
            posed = world_with(g, overrides)
            deformed, _ = skin(g, posed, body)
            correction = ground - float(deformed[:, 1].min())
            translation += (np.linalg.inv(parent_matrix) @ np.array([0, correction, 0, 0]))[:3]
            if form == 'human':
                translation = np.array(original_pose.get(hips, {}).get('translation', nodes[hips].get('translation', [0, 0, 0])), float)
                translation[[0, 2]] = np.array(nodes[hips].get('translation', [0, 0, 0]))[[0, 2]]
            translations.append(translation)
        channels = []
        for index, values in tracks.items():
            channels.append({'node': index, 'path': 'rotation', 'times': times.astype('float32').tolist(),
                             'values': continuous(values, loop).tolist()})
        translations = np.asarray(translations)
        if loop:
            translations[-1] = translations[0]
        translations[:, 0] = translations[0, 0]
        translations[:, 2] = translations[0, 2]
        channels.append({'node': hips, 'path': 'translation', 'times': times.astype('float32').tolist(),
                         'values': translations.astype('float32').tolist()})
        clips.append({'name': destination, 'duration': duration, 'loop': loop,
                      'source': {'file': str(source_path.relative_to(ARCHIVE.parent.parent)),
                                 'clip': source_clip, 'duration': animation['duration'],
                                 'matched_bones': len(mapped)}, 'channels': channels})
    if form == 'human':
        clips.append(human_idle(g, old, nodes, bone_names))
    payload = {'target': path.name, 'base_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'version': 2, 'clips': clips}
    if form == 'wolf':
        payload['metrics'] = {'run_stride_m': 8.0 * .533, 'run_reference_speed_mps': 8.0}
    raw = json.dumps(payload, separators=(',', ':')).encode()
    (OUT / f'{name}.json.gz').write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    return {'target': path.name, 'base_sha256': payload['base_sha256'],
            'clips': [{key: clip[key] for key in ('name', 'duration', 'source')} for clip in clips]}


if __name__ == '__main__':
    selected = set(sys.argv[1:])
    reports = []
    for character in VARIANTS:
        for target_form in ('wolf', 'human'):
            target = character if target_form == 'wolf' else f'human-{character}'
            if selected and target not in selected:
                continue
            reports.append(build_target(character, target_form))
            print('generated', target, flush=True)
    (ROOT / 'tools/animation_transfer/mapping.json').write_text(
        json.dumps(reports, indent=2, ensure_ascii=False) + '\n')
