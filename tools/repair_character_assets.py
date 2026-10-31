"""Localized v0.1.17 skin repair for assets that cannot be fixed by animation alone.

The human king cloak arrived weighted almost entirely to thighs/shins and had no cloak
bones.  This tool adds Cape1..3 to the existing armature and moves only the isolated
rear cloak sheet to those joints.  POSITION/NORMAL/UV, indices, images, materials and
textures are preserved byte for byte.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'app/src/main/assets/models/human-kral.glb'


def unpack(data):
    json_length = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + json_length]), bytearray(data[28 + json_length:])


def accessor(gltf, binary, index):
    acc = gltf['accessors'][index]
    view = gltf['bufferViews'][acc['bufferView']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[acc['type']]
    dtype = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}[acc['componentType']]
    offset = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    result = np.frombuffer(binary, dtype=dtype, count=acc['count'] * width, offset=offset)
    return result.reshape(acc['count'], width), offset


def matrix(node):
    if 'matrix' in node:
        return np.array(node['matrix'], float).reshape(4, 4).T
    result = np.eye(4)
    q = node.get('rotation', [0, 0, 0, 1])
    x, y, z, w = q
    result[:3, :3] = np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
        [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
        [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)],
    ]) * np.array(node.get('scale', [1, 1, 1]))
    result[:3, 3] = node.get('translation', [0, 0, 0])
    return result


def worlds(gltf):
    parents = {child: parent for parent, node in enumerate(gltf['nodes']) for child in node.get('children', [])}
    cache = {}
    def world(index):
        if index not in cache:
            local = matrix(gltf['nodes'][index])
            cache[index] = local if index not in parents else world(parents[index]) @ local
        return cache[index]
    return [world(i) for i in range(len(gltf['nodes']))], parents


def add_buffer(gltf, binary, raw, component_type, value_type, count):
    while len(binary) % 4:
        binary.append(0)
    view_index = len(gltf['bufferViews'])
    gltf['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(raw)})
    binary.extend(raw)
    accessor_index = len(gltf['accessors'])
    gltf['accessors'].append({'bufferView': view_index, 'componentType': component_type,
                              'count': count, 'type': value_type})
    return accessor_index


def pack(gltf, binary):
    gltf['buffers'][0]['byteLength'] = len(binary)
    encoded = json.dumps(gltf, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    binary.extend(b'\0' * (-len(binary) % 4))
    return (struct.pack('<III', 0x46546C67, 2, 28 + len(encoded) + len(binary)) +
            struct.pack('<II', len(encoded), 0x4E4F534A) + encoded +
            struct.pack('<II', len(binary), 0x004E4942) + binary)


def main():
    before = MODEL.read_bytes()
    gltf, binary = unpack(before)
    names = {node.get('name'): i for i, node in enumerate(gltf['nodes'])}
    if 'Cape1' in names:
        print('human-kral cloak rig already installed')
        return
    protected = {key: hashlib.sha256(json.dumps(gltf.get(key), sort_keys=True).encode()).hexdigest()
                 for key in ('meshes', 'materials', 'textures', 'images', 'samplers')}
    body_node = next(node for node in gltf['nodes'] if node.get('name') == 'Body_human')
    primitive = gltf['meshes'][body_node['mesh']]['primitives'][0]
    positions, _ = accessor(gltf, binary, primitive['attributes']['POSITION'])
    positions = positions.copy()
    joints, joints_offset = accessor(gltf, binary, primitive['attributes']['JOINTS_0'])
    weights, weights_offset = accessor(gltf, binary, primitive['attributes']['WEIGHTS_0'])
    joints = joints.copy()
    weights = weights.copy()
    old_joint_count = len(gltf['skins'][0]['joints'])
    joint_names = [gltf['nodes'][node].get('name', '') for node in gltf['skins'][0]['joints']]
    hips_joint = joint_names.index('Hips')
    chest_joint = joint_names.index('Chest')

    world, _ = worlds(gltf)
    chest = names['Chest']
    targets = [np.array([-.075, 1.30, -.16]), np.array([-.075, .92, -.30]), np.array([-.075, .52, -.43])]
    parent = chest
    cape_nodes = []
    parent_world = world[parent]
    cape_worlds = []
    for number, target in enumerate(targets, 1):
        local = (np.linalg.inv(parent_world) @ np.r_[target, 1])[:3]
        node_index = len(gltf['nodes'])
        gltf['nodes'].append({'name': f'Cape{number}', 'translation': local.tolist(), 'rotation': [0, 0, 0, 1], 'children': []})
        gltf['nodes'][parent].setdefault('children', []).append(node_index)
        current_world = parent_world.copy()
        current_world[:3, 3] = target
        cape_worlds.append(current_world)
        cape_nodes.append(node_index)
        parent, parent_world = node_index, current_world
    gltf['nodes'][cape_nodes[-1]].pop('children', None)
    gltf['skins'][0]['joints'].extend(cape_nodes)

    # This back sheet is the broken cloak: it is behind the torso, below the belt and
    # was 99.99% assigned to leg joints.  Use a smooth attachment band; a hard spatial
    # cut would put adjacent triangle vertices on unrelated bones and create a crack.
    depth = np.clip((.05 - positions[:, 2]) / .55, 0, 1)
    top_fade = np.clip((1.42 - positions[:, 1]) / .42, 0, 1)
    bottom_fade = np.clip((positions[:, 1] - .05) / .22, 0, 1)
    alpha = depth * top_fade * bottom_fade
    alpha *= (np.abs(positions[:, 0]) < .72)
    # The cloak is welded into the coat rather than a separate mesh.  A bounded 35%
    # cape share gives secondary motion while the original torso/leg share keeps the
    # welded border continuous.
    alpha *= .35
    selected = np.where(alpha > 1e-4)[0]
    for vertex in selected:
        phase = np.clip((1.06 - float(positions[vertex, 1])) / .86, 0, 1) * 2
        if phase < 1:
            ids = (old_joint_count, old_joint_count + 1)
            blend = phase
        else:
            ids = (old_joint_count + 1, old_joint_count + 2)
            blend = phase - 1
        cape = [(ids[0], (1 - blend) * alpha[vertex]), (ids[1], blend * alpha[vertex])]
        original = sorted(zip(joints[vertex], weights[vertex]), key=lambda item: item[1], reverse=True)[:2]
        # The bad source weights bound this sheet to thighs/shins.  Keep the smooth
        # transition weight, but redirect that share to the torso attachment.
        original = [((chest_joint if positions[vertex, 1] > .82 else hips_joint)
                     if joint_names[int(joint)].startswith(('UpperArm', 'Forearm', 'Hand', 'Thigh', 'Shin', 'Foot', 'Toe'))
                     else int(joint), weight) for joint, weight in original]
        combined = cape + [(int(joint), float(weight) * (1 - alpha[vertex])) for joint, weight in original]
        combined = sorted(combined, key=lambda item: item[1], reverse=True)[:4]
        total = sum(weight for _, weight in combined) or 1
        joints[vertex] = [joint for joint, _ in combined]
        weights[vertex] = [weight / total for _, weight in combined]
    # Diffuse the transition over actual mesh adjacency.  Position-only falloff is not
    # enough on folded cloak strips; adjacent vertices can sit far apart in XYZ.
    joint_total = old_joint_count + 3
    dense = np.zeros((len(positions), joint_total), dtype=np.float32)
    for column in range(4):
        dense[np.arange(len(positions)), joints[:, column]] += weights[:, column]
    triangles, _ = accessor(gltf, binary, primitive['indices'])
    triangles = triangles.copy()
    neighbours = [set() for _ in range(len(positions))]
    for a, b, c in triangles.astype(int).reshape(-1, 3):
        neighbours[a].update((b, c)); neighbours[b].update((a, c)); neighbours[c].update((a, b))
    for _ in range(160):
        updated = dense.copy()
        for vertex in selected:
            if neighbours[vertex]:
                mean = dense[list(neighbours[vertex])].mean(axis=0)
                updated[vertex] = dense[vertex] * .5 + mean * .5
        dense = updated
    limb = [i for i, name in enumerate(joint_names)
            if name.startswith(('UpperArm', 'Forearm', 'Hand', 'Thigh', 'Shin', 'Foot', 'Toe'))]
    for vertex in selected:
        if dense[vertex, old_joint_count:].sum() > .03:
            torso = chest_joint if positions[vertex, 1] > .82 else hips_joint
            dense[vertex, torso] += dense[vertex, limb].sum()
            dense[vertex, limb] = 0
        arm = [i for i, name in enumerate(joint_names) if name.startswith(('Forearm', 'Hand'))]
        leg = [i for i, name in enumerate(joint_names) if name.startswith(('Hips', 'Thigh', 'Shin', 'Foot', 'Toe'))]
        if dense[vertex, arm].sum() > .02 and dense[vertex, leg].sum() > .02:
            dense[vertex, chest_joint] += dense[vertex, arm].sum()
            dense[vertex, arm] = 0
        best = np.argsort(dense[vertex])[-4:][::-1]
        total = dense[vertex, best].sum() or 1
        joints[vertex] = best
        weights[vertex] = dense[vertex, best] / total
    del triangles, dense
    binary[joints_offset:joints_offset + joints.nbytes] = joints.tobytes()
    binary[weights_offset:weights_offset + weights.nbytes] = weights.astype(np.float32).tobytes()

    old_ibm, _ = accessor(gltf, binary, gltf['skins'][0]['inverseBindMatrices'])
    old_ibm = old_ibm.copy().reshape(-1, 16)
    new_ibm = [np.linalg.inv(w).T.reshape(16) for w in cape_worlds]
    matrices = np.vstack([old_ibm, np.asarray(new_ibm, dtype=np.float32)]).astype(np.float32)
    del old_ibm
    gltf['skins'][0]['inverseBindMatrices'] = add_buffer(gltf, binary, matrices.tobytes(), 5126, 'MAT4', len(matrices))

    after = pack(gltf, binary)
    MODEL.write_bytes(after)
    final_gltf, _ = unpack(after)
    for key, digest in protected.items():
        assert hashlib.sha256(json.dumps(final_gltf.get(key), sort_keys=True).encode()).hexdigest() == digest, key
    report = {
        'model': MODEL.name,
        'repair': 'localized human king cloak rig',
        'vertices_reweighted': int(len(selected)),
        'vertex_region': {'x_abs_max': .72, 'y_blend': [.05, 1.42], 'z_blend': [.05, -.50]},
        'added_bones': ['Cape1', 'Cape2', 'Cape3'],
        'joint_count_before': old_joint_count,
        'joint_count_after': old_joint_count + 3,
        'position_normal_uv_indices_unchanged': True,
        'images_textures_materials_unchanged': True,
        'before_sha256': hashlib.sha256(before).hexdigest(),
        'after_sha256': hashlib.sha256(after).hexdigest(),
    }
    (ROOT / 'dist').mkdir(exist_ok=True)
    (ROOT / 'dist/human-kral-cape-repair.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
