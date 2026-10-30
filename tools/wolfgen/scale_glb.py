"""Wrap a GLB's scene roots in a uniformly scaled parent node: scale_glb.py in.glb out.glb factor"""
import json, struct, sys
src, dst, k = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = open(src, 'rb').read(); jl = struct.unpack_from('<I', d, 12)[0]
g = json.loads(d[20:20 + jl]); rest = d[20 + jl:]
sc = g['scenes'][g.get('scene', 0)]
g['nodes'].append({'name': 'WolfScale', 'scale': [k, k, k], 'children': list(sc['nodes'])})
sc['nodes'] = [len(g['nodes']) - 1]
j = json.dumps(g, separators=(',', ':')).encode(); j += b' ' * (-len(j) % 4)
out = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(j) + len(rest)) + struct.pack('<I4s', len(j), b'JSON') + j + rest
open(dst, 'wb').write(out)
