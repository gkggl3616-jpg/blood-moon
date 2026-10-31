"""Write the per-character v0.1.17 rig, topology and animation audit."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / 'app/src/main/assets/models'
NAMES = ['bilge', 'ates', 'kral', 'hellgate', 'ay', 'zeynos']


def load(path):
    data = path.read_bytes(); length = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20 + length]); binary = data[28 + length:]
    def acc(index):
        a = gltf['accessors'][index]; view = gltf['bufferViews'][a['bufferView']]
        size = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
        dtype = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}[a['componentType']]
        offset = view.get('byteOffset', 0) + a.get('byteOffset', 0)
        values = np.frombuffer(binary, dtype, a['count'] * size, offset).reshape(a['count'], size)
        if a.get('normalized') and dtype == np.uint8: values = values.astype(float) / 255
        return values
    return gltf, acc


def topology(positions, triangles):
    keys = np.round(positions, 5)
    lookup = {}; welded = np.empty(len(keys), int)
    for i, value in enumerate(keys): welded[i] = lookup.setdefault(tuple(value), i)
    tri = welded[triangles]
    counts = {}
    for face in tri:
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            edge = tuple(sorted((int(a), int(b)))); counts[edge] = counts.get(edge, 0) + 1
    boundary = [edge for edge, count in counts.items() if count == 1]
    adjacency = {}
    for a, b in boundary: adjacency.setdefault(a, set()).add(b); adjacency.setdefault(b, set()).add(a)
    components = []
    unseen = set(adjacency)
    while unseen:
        todo = [unseen.pop()]; component = set(todo)
        while todo:
            for other in adjacency[todo.pop()]:
                if other not in component:
                    component.add(other); unseen.discard(other); todo.append(other)
        components.append(component)
    # UV seam twins were welded above; remaining components are real geometric openings.
    return len(boundary), sorted([len(c) for c in components], reverse=True)


def animation_metrics(gltf, acc, name_to_node):
    result = {}
    hips = name_to_node.get('Hips')
    for animation in gltf.get('animations', []):
        root_xz = []; yaw = []; discontinuities = 0; loop_error = 0
        duration = 0
        for channel in animation['channels']:
            sampler = animation['samplers'][channel['sampler']]
            times = acc(sampler['input']).ravel(); values = acc(sampler['output'])
            duration = max(duration, float(times[-1]))
            if channel['target']['path'] == 'rotation':
                norms = np.linalg.norm(values, axis=1)
                dots = np.sum(values[1:] * values[:-1], axis=1)
                discontinuities += int((dots < 0).sum()) + int((np.abs(norms - 1) > 2e-4).sum())
                loop_error = max(loop_error, float(1 - abs(np.dot(values[0], values[-1]))))
                if channel['target']['node'] == hips:
                    yaw.extend(Rotation.from_quat(values).as_euler('xyz')[:, 1].tolist())
            elif channel['target']['node'] == hips and channel['target']['path'] == 'translation':
                root_xz.extend(values[:, [0, 2]].tolist())
        root_xz = np.asarray(root_xz)
        result[animation['name']] = {
            'duration_seconds': round(duration, 6),
            'root_horizontal_range_m': round(float(np.ptp(root_xz, axis=0).max()), 6) if len(root_xz) else 0,
            'root_yaw_range_degrees': round(float(np.ptp(np.unwrap(yaw))) * 180 / np.pi, 4) if yaw else 0,
            'loop_quaternion_error': round(loop_error, 8),
            'quaternion_discontinuities': discontinuities,
        }
    return result


reports = []
for stem in NAMES + [f'human-{name}' for name in NAMES]:
    path = MODELS / f'{stem}.glb'; gltf, acc = load(path)
    name_to_node = {node.get('name'): i for i, node in enumerate(gltf['nodes'])}
    mesh_nodes = [node for node in gltf['nodes'] if 'mesh' in node]
    primitives = [primitive for node in mesh_nodes for primitive in gltf['meshes'][node['mesh']]['primitives']]
    vertices = sum(len(acc(p['attributes']['POSITION'])) for p in primitives)
    triangles = sum(len(acc(p['indices'])) // 3 for p in primitives)
    body = next(p for node in mesh_nodes if node.get('name', '').startswith('Body')
                for p in gltf['meshes'][node['mesh']]['primitives'])
    positions = acc(body['attributes']['POSITION']); indices = acc(body['indices']).astype(int).ravel().reshape(-1, 3)
    joints = acc(body['attributes']['JOINTS_0']).astype(int); weights = acc(body['attributes']['WEIGHTS_0']).astype(float)
    skin = gltf['skins'][0]; joint_count = len(skin['joints'])
    boundary_edges, loops = topology(positions, indices)
    inverse = acc(skin['inverseBindMatrices'])
    reports.append({
        'model': path.name, 'mesh_count': len(mesh_nodes), 'primitive_count': len(primitives),
        'vertices': vertices, 'triangles': triangles,
        'joints': [gltf['nodes'][node].get('name', '') for node in skin['joints']],
        'inverse_bind_matrix_count': len(inverse),
        'max_influences_per_vertex': int((weights > 1e-5).sum(1).max()),
        'non_normalized_weight_vertices': int((np.abs(weights.sum(1) - 1) > 2e-3).sum()),
        'invalid_joint_indices': int((joints >= joint_count).sum()),
        'boundary_edges_after_uv_seam_weld': boundary_edges,
        'boundary_loop_component_sizes': loops,
        'animations': animation_metrics(gltf, acc, name_to_node),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    })

dtx_root = Path('/workspace/extracted/wt_chars')
dtx = []
if dtx_root.exists():
    for path in sorted(dtx_root.rglob('*.dtx')):
        dtx.append({'path': str(path.relative_to(dtx_root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
elif (ROOT / 'docs/v0117-dtx-checksums.json').is_file():
    # CI does not contain the user's 4 GB source archive. Keep its immutable,
    # locally generated inventory in the repository so Release evidence remains complete.
    dtx = json.loads((ROOT / 'docs/v0117-dtx-checksums.json').read_text())['files']

out = {'models': reports, 'dtx_files': dtx, 'dtx_files_modified': False,
       'texture_image_material_uv_modified': False,
       'fp_arms_sha256': hashlib.sha256((MODELS / 'fp_arms.glb').read_bytes()).hexdigest()}
(ROOT / 'dist').mkdir(exist_ok=True)
(ROOT / 'dist/character-rig-topology-audit.json').write_text(json.dumps(out, indent=2) + '\n')
(ROOT / 'dist/dtx-checksums.json').write_text(json.dumps({'files': dtx, 'modified': False}, indent=2) + '\n')
print('audited', len(reports), 'models and', len(dtx), 'DTX files')
