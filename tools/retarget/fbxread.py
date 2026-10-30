"""Minimal binary-FBX (7.x) reader: skeleton rest pose + per-bone animated rotations (Mixamo exports)."""
import struct, zlib, math
import numpy as np

class N:
    __slots__ = ('name', 'props', 'kids')
    def __init__(s, name): s.name = name; s.props = []; s.kids = []
    def find(s, name): return [k for k in s.kids if k.name == name]
    def first(s, name):
        r = s.find(name); return r[0] if r else None

def parse(path):
    d = open(path, 'rb').read(); ver = struct.unpack_from('<I', d, 23)[0]; big = ver >= 7500; pos = 27
    def rec(pos):
        if big: end, npr, plen, nl = struct.unpack_from('<QQQB', d, pos); pos += 25
        else: end, npr, plen, nl = struct.unpack_from('<IIIB', d, pos); pos += 13
        if end == 0: return None, pos
        n = N(d[pos:pos + nl].decode('latin1')); pos += nl
        for _ in range(npr):
            t = chr(d[pos]); pos += 1
            if t in 'YCIFDL':
                fmt = {'Y': '<h', 'C': '<?', 'I': '<i', 'F': '<f', 'D': '<d', 'L': '<q'}[t]; v = struct.unpack_from(fmt, d, pos)[0]; pos += struct.calcsize(fmt)
            elif t in 'fdlib':
                ln, enc, cl = struct.unpack_from('<III', d, pos); pos += 12
                raw = d[pos:pos + cl]; pos += cl
                if enc: raw = zlib.decompress(raw)
                v = np.frombuffer(raw, dtype={'f': '<f4', 'd': '<f8', 'l': '<i8', 'i': '<i4', 'b': 'u1'}[t])
            elif t in 'SR':
                ln = struct.unpack_from('<I', d, pos)[0]; pos += 4; v = d[pos:pos + ln]; pos += ln
                if t == 'S': v = v.decode('latin1')
            else: raise ValueError(t)
            n.props.append(v)
        while pos < end:
            k, pos = rec(pos)
            if k is None: break
            n.kids.append(k)
        return n, end
    root = N('root')
    while pos < len(d) - 30:
        k, pos = rec(pos)
        if k is None: break
        root.kids.append(k)
    return root

TICKS = 46186158000.0

def rot_xyz(rx, ry, rz):
    """FBX EulerXYZ: R = Rz * Ry * Rx (degrees in)."""
    a, b, c = map(math.radians, (rx, ry, rz)); ca, sa, cb, sb, cc, sc = math.cos(a), math.sin(a), math.cos(b), math.sin(b), math.cos(c), math.sin(c)
    Rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]]); Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]]); Rz = np.array([[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def load_anim(path):
    root = parse(path); obj = root.first('Objects'); conn = root.first('Connections')
    models = {}; curvenodes = {}; curves = {}
    for o in obj.kids:
        if o.name == 'Model':
            uid, nm = o.props[0], o.props[1].split('\x00')[0]; pr = {'Lcl Translation': (0, 0, 0), 'Lcl Rotation': (0, 0, 0), 'PreRotation': (0, 0, 0), 'RotationOrder': 0}
            p70 = o.first('Properties70')
            if p70:
                for p in p70.kids:
                    if p.props[0] in pr: pr[p.props[0]] = tuple(p.props[4:7]) if len(p.props) >= 7 else p.props[4]
            models[uid] = dict(name=nm.split(':')[-1], **pr, parent=None, kind=o.props[2])
        elif o.name == 'AnimationCurveNode': curvenodes[o.props[0]] = dict(name=o.props[1].split('\x00')[0], curves={}, target=None, prop=None)
        elif o.name == 'AnimationCurve':
            curves[o.props[0]] = (np.asarray(o.first('KeyTime').props[0], float) / TICKS, np.asarray(o.first('KeyValueFloat').props[0], float))
    for c in conn.kids:
        if c.props[0] != 'OO' and c.props[0] != 'OP': continue
        ch, par = c.props[1], c.props[2]
        if c.props[0] == 'OO' and ch in models and par in models: models[ch]['parent'] = par
        elif c.props[0] == 'OP' and ch in curves and par in curvenodes: curvenodes[par]['curves'][c.props[3].split('|')[-1]] = curves[ch]
        elif c.props[0] == 'OP' and ch in curvenodes and par in models: curvenodes[ch]['target'] = par; curvenodes[ch]['prop'] = c.props[3]
    anim = {}
    for cn in curvenodes.values():
        if cn['target'] in models and cn['prop'] in ('Lcl Rotation', 'Lcl Translation') and cn['curves']:
            anim.setdefault(models[cn['target']]['name'], {})[cn['prop']] = cn['curves']
    bones = {m['name']: m for m in models.values() if m['kind'] in ('LimbNode', 'Null', 'Root') or True}
    byid = {u: m['name'] for u, m in models.items()}
    for m in models.values(): m['parent_name'] = byid.get(m['parent'])
    return bones, anim
