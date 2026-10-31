"""First-person arms with real finger bones, from the CC0 "FPS arms rigged" pack (opengameart.org/content/fps-arms-rigged-only,
MakeHuman base). The .blend is exported to GLB in Blender (job 40_arms_export.py); this script turns that export into the
game file app/src/main/assets/models/fp_arms.glb:
  metres (x0.1), facing +Z like the character models (the engine turns it to face the camera), engine bone names
  (ClavL/R, UpperArmL/R, ForearmL/R, HandL/R; finger bones keep f_index.01.R ... thumb.03.L), mesh named FPArms_human,
  skin texture embedded (1K JPEG), rest-pose clip dropped.
usage: build_fp_arms.py exported.glb diffuse.png"""
import sys, os, io, json, struct
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'meshy')); from glbio import GLB
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src, tex = sys.argv[1], sys.argv[2]; out = os.path.join(ROOT, 'app/src/main/assets/models/fp_arms.glb')
g = GLB(src); j = g.j; binb = bytearray(g.bin)
REN = {'clavicle': 'Clav', 'upper_arm': 'UpperArm', 'forearm': 'Forearm', 'hand': 'Hand'}
for n in j['nodes']:
    nm = n.get('name', '')
    base, _, sd = nm.rpartition('.')
    if base in REN and sd in 'LR': n['name'] = REN[base] + sd
    # dots are stripped from node names by three.js: give every finger bone a plain name (IndexR1, ThumbL3, PalmIndexR ...)
    for k, v in (('f_index', 'Index'), ('f_middle', 'Middle'), ('f_ring', 'Ring'), ('f_pinky', 'Pinky'), ('thumb', 'Thumb')):
        if nm.startswith(k + '.0') and nm[-1] in 'LR': n['name'] = v + nm[-1] + nm[len(k) + 2]
    if nm.startswith('palm_') and nm[-1] in 'LR': n['name'] = 'Palm' + nm[5:-2].capitalize() + nm[-1]
    if nm.startswith('deltoid.'): n['name'] = 'Deltoid' + nm[-1]
    if nm.startswith('hand.') and nm.endswith('.control'): n['name'] = 'HandCtrl' + nm[5]
    if nm == 'caucasian_male_1': n['rotation'] = [0, 0, 0, 1]; n['scale'] = [.1, .1, .1]; n['translation'] = [0, 0, 0]; n['name'] = 'FPArmsRig'
    if nm == 'caucasian_male_1:Body': n['name'] = 'FPArms_human'
j['meshes'][0]['name'] = 'FPArms_human'
j.pop('animations', None)
im = Image.open(tex).convert('RGB'); im.thumbnail((1024, 1024)); b = io.BytesIO(); im.save(b, 'JPEG', quality=90); raw = b.getvalue()
while len(binb) % 4: binb.append(0)
j['bufferViews'].append(dict(buffer=0, byteOffset=len(binb), byteLength=len(raw))); binb.extend(raw)
j['images'] = [dict(bufferView=len(j['bufferViews']) - 1, mimeType='image/jpeg')]
j['samplers'] = [dict(magFilter=9729, minFilter=9987)]; j['textures'] = [dict(source=0, sampler=0)]
j['materials'] = [dict(name='FPSkin', doubleSided=False, pbrMetallicRoughness=dict(baseColorTexture=dict(index=0), metallicFactor=0, roughnessFactor=.62))]
while len(binb) % 4: binb.append(0)
j['buffers'] = [dict(byteLength=len(binb))]
js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
open(out, 'wb').write(struct.pack('<4sII', b'glTF', 2, 28 + len(js) + len(binb)) + struct.pack('<I4s', len(js), b'JSON') + js + struct.pack('<I4s', len(binb), b'BIN\0') + bytes(binb))
print('written', out, os.path.getsize(out))
