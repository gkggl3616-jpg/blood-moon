"""Apply the narrow v0.1.17 runtime patch without rebuilding the protected FPS bundle.

The repository's readable viewer sources predate several production FPS/TPS patches.
Rebundling them would remove those changes, so this script replaces only the existing
secondary-motion function and the reload sound hooks in the reviewed production bundle.
The first-person hand and viewmodel marker blocks are hashed before/after.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'app/src/main/assets/wolf3d.js'


def block(text, begin, end):
    a = text.index(begin)
    b = text.index(end, a) + len(end)
    return text[a:b]


def replace_once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'expected one runtime anchor, found {count}: {old[:90]}')
    return text.replace(old, new, 1)


def main():
    text = BUNDLE.read_text()
    before = {
        'fp_hands': hashlib.sha256(block(text, '/*FPHANDS-BEGIN*/', '/*FPHANDS-END*/').encode()).hexdigest(),
        'viewmodel': hashlib.sha256(block(text, '/*VIEWMODEL-BEGIN*/', '/*VIEWMODEL-END*/').encode()).hexdigest(),
    }
    start = text.index('var PH={')
    end = text.index('function TailCollide', start)
    replacement = r'''var PH={};var PHC={Tail1:[.035,13,7.5,.25],Tail2:[.045,12,7,.3],Tail3:[.055,11,6.5,.35],Cape1:[.06,10,6,.35],Cape2:[.09,8,5,.45],Cape3:[.12,7,4.5,.55],Hair1:[.08,11,5,.45],Hair2:[.11,9,4,.55],Hair3:[.14,8,3.5,.65],EarL:[.03,18,7,.25],EarR:[.03,18,7,.25]};
function TailSpring(m,dt,mode=Ws){if(!m||!(dt>0)||!m.visible)return;let S=m.userData.secondaryMotion,g=n=>m.getObjectByName(n);if(!S){let bones=[];m.traverse(o=>{o.isBone&&PHC[o.name]&&bones.push(o)});S=m.userData.secondaryMotion={acc:0,bones,states:new Map,last:new B.Vector3,now:new B.Vector3,velocity:new B.Vector3,steps:0,resets:0};m.getWorldPosition(S.last)}PH.st=S.states;m.getWorldPosition(S.now);let jump=S.now.distanceTo(S.last),reset=dt>.1||jump>2||!Number.isFinite(dt);S.velocity.subVectors(S.now,S.last).divideScalar(Math.max(dt,1/240));S.last.copy(S.now);if(reset){S.acc=0;S.velocity.set(0,0,0);for(let st of S.states.values())st.x=st.z=st.vx=st.vz=0;S.resets++}S.acc=Math.min(.2,S.acc+Math.min(dt,.1));let fixed=1/60,run=mode==="WolfRunQuad"||mode==="HumanRun",walk=mode==="WolfMove"||mode==="HumanWalk",drive=run?1:walk?.45:0;for(;S.acc>=fixed;S.acc-=fixed){for(let o of S.bones){let k=PHC[o.name],st=S.states.get(o);if(!st){st={x:0,z:0,vx:0,vz:0};S.states.set(o,st)}let max=k[3],tx=B.MathUtils.clamp(-S.velocity.z*k[0]*drive,-max,max),tz=B.MathUtils.clamp(S.velocity.x*k[0]*drive,-max,max);if(o.name.startsWith("Cape"))tx=B.MathUtils.clamp(tx+.035,-max,max);st.vx+=((tx-st.x)*k[1]*k[1]-2*k[2]*st.vx)*fixed;st.vz+=((tz-st.z)*k[1]*k[1]-2*k[2]*st.vz)*fixed;st.x=B.MathUtils.clamp(st.x+st.vx*fixed,-max,max);st.z=B.MathUtils.clamp(st.z+st.vz*fixed,-max,max);if(!Number.isFinite(st.x+st.z+st.vx+st.vz))st.x=st.z=st.vx=st.vz=0}S.steps++}for(let o of S.bones){let st=S.states.get(o);if(st){o.rotation.x+=st.x;o.rotation.z+=st.z;o.updateMatrixWorld(!0)}}CapeCollide(g);TailCollide(g);S.debug={fixedStep:fixed,steps:S.steps,resets:S.resets,bones:S.bones.map(o=>o.name),finite:[...S.states.values()].every(s=>Number.isFinite(s.x+s.z+s.vx+s.vz)),maxAngle:Math.max(0,...[...S.states.values()].map(s=>Math.max(Math.abs(s.x),Math.abs(s.z))))}}
'''
    text = text[:start] + replacement + text[end:]
    text = replace_once(text, 'TP.mix.update(dt);\n let A=TP.aim;', 'TP.mix.update(dt);TailSpring(m,dt,cl);\n let A=TP.aim;')
    text = replace_once(text, r'Ln=1.4,Kn("\u015Earj\xF6r de\u011Fi\u015Ftiriliyor.",1.4)', r'Ln=1.4,window.roguePlaySound?.("reload"),Kn("\u015Earj\xF6r de\u011Fi\u015Ftiriliyor.",1.4)')
    text = replace_once(text, 'Xm=pt==="human"?"wolf":"human",ai=.6', 'window.rogueStopSound?.("reload"),Xm=pt==="human"?"wolf":"human",ai=.6')
    text = replace_once(text, 'function hx(){++km,jm(),Yi=!1', 'function hx(){window.rogueStopSound?.("reload"),++km,jm(),Yi=!1')
    text = replace_once(text, 'effects:qs?.info(),render:Lm()', 'effects:qs?.info(),secondary:(pt==="wolf"?yt:TP.m)?.userData.secondaryMotion?.debug||null,render:Lm()')
    after = {
        'fp_hands': hashlib.sha256(block(text, '/*FPHANDS-BEGIN*/', '/*FPHANDS-END*/').encode()).hexdigest(),
        'viewmodel': hashlib.sha256(block(text, '/*VIEWMODEL-BEGIN*/', '/*VIEWMODEL-END*/').encode()).hexdigest(),
    }
    if after != before:
        raise SystemExit('protected first-person marker block changed')
    BUNDLE.write_text(text)
    report = {'bundle': str(BUNDLE.relative_to(ROOT)), 'protected_blocks_unchanged': True,
              'protected_block_sha256': after, 'fixed_secondary_timestep_seconds': 1/60,
              'reload_sound_hook': True, 'reload_cancel_hooks': ['form change', 'arena exit']}
    (ROOT / 'dist').mkdir(exist_ok=True)
    (ROOT / 'dist/runtime-patch-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
