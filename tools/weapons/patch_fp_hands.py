"""Insert tools/weapons/fp_hands.js into wolf3d.js (replacing FpIK) and load the finger-rigged arms (idempotent)."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = os.path.join(ROOT, 'app/src/main/assets/wolf3d.js'); s = open(P).read()
code = open(os.path.join(os.path.dirname(__file__), 'fp_hands.js')).read().strip() + '\n'
A, Z = '/*FPHANDS-BEGIN*/', '/*FPHANDS-END*/'
if A in s: s = s[:s.index(A)] + 'function FpIK(){}' + s[s.index(Z) + len(Z):]
i = s.index('function FpIK(){'); j = s.index('function HandAim', i)
s = s[:i] + A + code + Z + s[j:]
old = 'let r=await Kw.loadAsync("models/"+Xr(s,"human")+".glb"),f=r.scene,a=0;'
if old in s: s = s.replace(old, 'let r=await Kw.loadAsync("models/fp_arms.glb"),f=r.scene,a=0;')
old = 'FpFit(f),hn.add(f),hn.userData.fp=f;'
if old in s: s = s.replace(old, 'FpFit(f),FpRigInit(f,s),hn.add(f),hn.userData.fp=f;')
old = 'r["sock"+L]=h?.userData.sockErr??null}'
if old in s and 'r["trig"+L]' not in s: s = s.replace(old, old[:-1] + ';r["trig"+L]=h?.userData.trig??null}')
open(P, 'w').write(s); print('patched')
