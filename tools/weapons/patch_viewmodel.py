"""Insert tools/weapons/viewmodel.js into wolf3d.js and route fire/recoil, FOV, buttons and keys through it (idempotent)."""
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = os.path.join(ROOT, 'app/src/main/assets/wolf3d.js'); s = open(P).read()
code = open(os.path.join(os.path.dirname(__file__), 'viewmodel.js')).read().strip() + '\n'
A, Z = '/*VIEWMODEL-BEGIN*/', '/*VIEWMODEL-END*/'
if A in s: s = s[:s.index(A)] + s[s.index(Z) + len(Z):]
s = s.replace('/*FPHANDS-BEGIN*/', A + code + Z + '/*FPHANDS-BEGIN*/', 1)
def rep(a, b):
    global s
    if b in s: return
    assert s.count(a) == 1, a[:80]; s = s.replace(a, b)
rep('hn.userData.recoil*=Math.exp(-14*s),hn.translateZ(hn.userData.recoil),n&&(hn.translateY(Math.sin(li*12)*.01),hn.translateX(Math.cos(li*6)*.009)),FpReload(s),KnifeStab(s),FpIK()',
    'hn.userData.recoil*=Math.exp(-14*s),FpReload(s),VmTick(s,n,s>0?Math.hypot(ve.x-t.x,ve.z-t.z)/s:0),FpIK()')
rep('Gs=li+e.interval,hn.userData.recoil=.07,', 'Gs=li+e.interval,VmKick(hn.userData.weapon),')
rep('cn.fov+=((dn&&pt==="wolf"?70:67)-cn.fov)*Math.min(1,s*6)',
    'cn.fov+=((dn&&pt==="wolf"?70:pt==="human"&&!TPV&&VM.ads>0?67+((VMP[hn.userData.weapon]?.ads?.fov||67)-67)*VM.ads:67)-cn.fov)*Math.min(1,s*(VM.ads>0?14:6))')
rep('Fe("arenaRoll").onclick=Zm,', 'Fe("arenaRoll").onclick=()=>pt==="human"?VmInspect():Zm(),')
rep('Fe("arenaTrack").onclick=$m,', 'Fe("arenaTrack").onclick=()=>pt==="human"?VmAds():$m(),')
rep('KeyQ:Zm,Space:Jm,KeyR:Od,KeyT:$m,', 'KeyQ:()=>pt==="human"?VmInspect():Zm(),Space:Jm,KeyR:Od,KeyT:()=>pt==="human"?VmAds():$m(),')
rep('$r.addEventListener("contextmenu",a=>a.preventDefault()),',
    '$r.addEventListener("contextmenu",a=>a.preventDefault()),$r.addEventListener("mousedown",a=>{a.button===2&&Yi&&pt==="human"&&VmAds(hn.userData.weapon==="knife"?void 0:!0)}),$r.addEventListener("mouseup",a=>{a.button===2&&Yi&&pt==="human"&&hn.userData.weapon!=="knife"&&VmAds(!1)}),')
rep('Fe("arenaRoll").disabled=!s||!At.roll,', 'Fe("arenaRoll").disabled=s?!At.roll:!1,')
rep('Fe("arenaTrack").disabled=!s,',
    'Fe("arenaTrack").disabled=!1,Fe("arenaRoll").querySelector(".action-label")&&(Fe("arenaRoll").querySelector(".action-label").textContent=s?"TAKLA":"\\u0130NCELE"),Fe("arenaTrack").querySelector(".action-label")&&(Fe("arenaTrack").querySelector(".action-label").textContent=s?"\\u0130Z S\\xDCR":hn?.userData.weapon==="knife"?"A\\u011EIR":"N\\u0130\\u015EAN"),Fe("arenaTrack").classList.toggle("active",!s&&VM.adsOn),')
rep('fire:Jc,view:TpToggle}', 'fire:Jc,view:TpToggle,ads:VmAds,inspect:VmInspect,heavy:VmHeavy}')
rep('selectWeapon:_s,', 'selectWeapon:_s,vm:()=>({weapon:hn?.userData.weapon,ads:VM.ads,adsOn:VM.adsOn,inspect:VM.insp,heavy:VM.heavy,kick:VM.kz,fov:cn?.fov,fit:hn?.userData.fp?.userData.fit}),')
rep('let La=(uL.distanceTo(eL)+eL.distanceTo(hL)+uR.distanceTo(eR)+eR.distanceTo(hR))/2,', 'let La=f.userData.La0||(f.userData.La0=(uL.distanceTo(eL)+eL.distanceTo(hL)+uR.distanceTo(eR)+eR.distanceTo(hR))/2),')
# human sprint: double-tap forward (button or W) while in human form; fire / aim / reload end it
rep('function Zc(){return Ys()?pt!=="wolf"?(Kn("D\\xF6rt ayak ko\\u015Fu kurt formunda kullan\\u0131l\\u0131r."),!1):', 'function Zc(){return Ys()?pt!=="wolf"?(TPV||Ln>0||VM.ads>.3?!1:(dn=!dn,VM.adsOn=!1,eo(),!0)):')
rep('let o=(pt==="wolf"?dn&&At.run?8:4.3:4.1)', 'let o=(pt==="wolf"?dn&&At.run?8:4.3:dn?6.3:4.1)')
rep('h-e<=330&&pt==="wolf"&&!dn&&Zc()', 'h-e<=330&&!dn&&Zc()')
rep('h-KW<=330&&pt==="wolf"&&!dn&&Zc()', 'h-KW<=330&&!dn&&Zc()')
rep('if(pt==="human"){let s=wi(),e=s?.weapon;if(!e||Ln>0)return!1;', 'if(pt==="human"){let s=wi(),e=s?.weapon;if(!e||Ln>0)return!1;dn&&(dn=!1,eo());')
open(P, 'w').write(s); print('patched')
