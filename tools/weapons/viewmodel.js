/* Viewmodel layer (tools/weapons/patch_viewmodel.py inserts it into wolf3d.js).
   Per-weapon profile: arm fit (shoulder placement/yaw/scale chosen so the elbows stay bent: right ~72 %, left ~84 % of
   full reach), hip pose, aim-down-sights pose (sight socket on the camera axis), recoil, bob. Every animation moves the
   WEAPON; both hands are re-solved onto its grip sockets each frame (fp_hands.js), so they never slide off it. */
var VMP={
 rifle:{fpk:{reach:.72,kmax:1.45,x:.06,y:-.22,z:-.1,yaw:-.75},hip:{p:[.25,-.215,-.42],r:[.03,0,0]},ads:{d:.36,fov:55},rec:{z:.04,p:.045,y:.012},bob:1},
 sniper:{fpk:{reach:.72,kmax:1.45,x:.06,y:-.22,z:-.1,yaw:-.75},hip:{p:[.25,-.205,-.44],r:[.025,.01,0]},ads:{d:.19,fov:28},rec:{z:.075,p:.09,y:.008},bob:1},
 pistol:{fpk:{reach:.595,kmax:1.25,x:.02,y:-.18,z:-.04,yaw:-.15},hip:{p:[.13,-.16,-.4],r:[.05,.02,0]},ads:{d:.34,fov:60},rec:{z:.035,p:.11,y:.014},bob:1.1},
 knife:{fpk:{reach:.524,kmax:1.1,x:.04,y:-.26,z:-.04,yaw:-.05},hip:{p:[.2,-.21,-.4],r:[.12,.05,.1]},bob:1.2},
 frag:{fpk:{reach:.524,kmax:1.1,x:.04,y:-.26,z:-.04,yaw:-.05},hip:{p:[.17,-.19,-.36],r:[0,.2,0]},bob:1.2},
 smoke:{fpk:{reach:.524,kmax:1.1,x:.04,y:-.26,z:-.04,yaw:-.05},hip:{p:[.17,-.19,-.36],r:[0,.2,0]},bob:1.2}};
var VM={ads:0,adsOn:!1,insp:0,heavy:0,kz:0,kp:0,ky:0,bob:0,amp:0,br:0,w:"",v:new B.Vector3,e:new B.Euler};
var VSm=x=>x*x*(3-2*x),VEnv=(t,a,b,c,d)=>t<a||t>d?0:t<b?VSm((t-a)/(b-a)):t<=c?1:1-VSm((t-c)/(d-c));
function VmFit(w){let f=hn?.userData.fp,P=VMP[w];if(!f||!P?.fpk)return;let k0=f.userData.fit?.k||1;Object.assign(FPK,P.fpk);let pa=f.parent;pa?.remove(f);FpFit(f);pa?.add(f);let k1=f.userData.fit?.k||1,rig=f.userData.rig;if(rig&&k0>0)for(let L in rig){let r=rig[L],q=k1/k0;r.l1*=q;r.l2*=q;r.hs*=q}}
function VmCanAds(){return pt==="human"&&!TPV&&["rifle","sniper","pistol"].includes(hn?.userData.weapon)&&Ln<=0&&!(hn.userData.swap>0)}
function VmAds(on){if(!Ys()||pt!=="human")return!1;let w=hn.userData.weapon;if(w==="knife")return VmHeavy();if(!VmCanAds())return!1;VM.adsOn=on===void 0?!VM.adsOn:!!on;VM.insp=0;eo();return!0}
function VmInspect(){if(!Ys()||pt!=="human"||VM.ads>.05||Ln>0)return!1;VM.insp=2.4;return!0}
function VmKick(w){let R=VMP[w]?.rec;if(!R)return;let a=1-.45*VM.ads;VM.kz+=R.z*a;VM.kp+=R.p*a;VM.ky+=(Math.random()-.5)*2*R.y;VM.insp=0}
/* heavy knife attack: wide right-to-left slash, more damage and reach than the stab */
function VmHeavy(){if(!Ys()||pt!=="human"||li<Gs||VM.heavy>0)return!1;let e=wi()?.weapon;if(!e||e.kind!=="knife")return!1;Gs=li+1.05;VM.heavy=.75;VM.insp=0;window.roguePlaySound?.("swap");let t=new B.Vector3(-Math.sin(Gt),0,-Math.cos(Gt));setTimeout(()=>{for(let n of Ei){let i=n.position.clone().sub(ve);if(n.hp>0&&i.length()<e.range*1.15&&i.normalize().dot(t)>.35&&ig(ve,n.position)){th(n,e.damage*1.9*Ti().values.damage/100);break}}eo()},280);return!0}
function VmTick(dt,moving,speed){let w=hn.userData.weapon,P=VMP[w],M=hn.userData.groups?.[w]?.userData.model;if(VM.w!==w){VM.w=w;VM.adsOn=!1;VM.heavy=0;VM.insp=0;VmFit(w)}if(!P||!M)return;
 let can=VmCanAds();can||(VM.adsOn=!1);VM.ads+=((VM.adsOn?1:0)-VM.ads)*(1-Math.exp(-dt*13));let A=VM.ads;
 /* recoil: fast kick, exponential recovery */
 let d=Math.exp(-dt*16);VM.kz*=d;VM.kp*=Math.exp(-dt*12);VM.ky*=Math.exp(-dt*10);
 /* bob (walk) and breathing (idle) */
 let sp=moving?B.MathUtils.clamp(speed/4.1,0,1.6):0;VM.amp+=(sp-VM.amp)*(1-Math.exp(-dt*8));VM.bob+=dt*(5.5+3*VM.amp)*(VM.amp>.02?1:0);VM.br+=dt;
 let ba=VM.amp*(P.bob||1)*(1-.75*A),bx=Math.cos(VM.bob)*.011*ba,by=-Math.abs(Math.sin(VM.bob))*.013*ba,brY=Math.sin(VM.br*1.7)*.0022*(1-.6*A),brP=Math.sin(VM.br*1.7+.6)*.0045*(1-.6*A);
 /* hip <-> aim down sights: sight socket on the camera axis, weapon level */
 let hp=P.hip.p,hr=P.hip.r,ap=hp,ar=hr,sk=hn.userData.groups[w].userData.sock;if(P.ads&&sk?.sight){ap=[-sk.sight[0],-sk.sight[1],-P.ads.d-sk.sight[2]];ar=[0,0,0]}
 let px=hp[0]+(ap[0]-hp[0])*A,py=hp[1]+(ap[1]-hp[1])*A,pz=hp[2]+(ap[2]-hp[2])*A,rx=hr[0]+(ar[0]-hr[0])*A,ry=hr[1]+(ar[1]-hr[1])*A,rz=hr[2]+(ar[2]-hr[2])*A;
 /* inspect: turn the weapon to show its side, then back */
 if(VM.insp>0){VM.insp=Math.max(0,VM.insp-dt);let t=1-VM.insp/2.4,e=VEnv(t,0,.22,.78,1),e2=VEnv(t,.3,.45,.6,.78);ry+=.95*e-.5*e2;rz+=.35*e;rx+=.15*e2;px-=.07*e;py+=.04*e;pz+=.06*e}
 /* knife: light stab (hn.userData.stab, set by the attack) and heavy slash */
 if(w==="knife"){let U=hn.userData;U.stab=Math.max(0,(U.stab||0)-dt);let t=U.stab>0?1-U.stab/.38:1,e=t<.18?-.25*VSm(t/.18):t<.4?-.25+1.25*VSm((t-.18)/.22):t<.6?1:1-VSm((t-.6)/.4);px-=.05*e;py+=.05*e;pz-=.3*e;rx-=.3*Math.max(0,e);ry-=.08*e;
  if(VM.heavy>0){VM.heavy=Math.max(0,VM.heavy-dt);let h=1-VM.heavy/.75,wind=VEnv(h,0,.25,.3,.42),sw=h<.3?0:h<.55?VSm((h-.3)/.25):1,back=VEnv(h,.55,.62,.7,1);let s2=sw*(1-back);px+=.12*wind-.32*s2;py+=.06*wind-.02*s2;pz+=-.05*wind-.16*s2;rz+=.9*wind-1.4*s2;ry+=.4*wind-.7*s2;rx+=.1*wind}}
 M.position.set(px+bx,py+by+brY,pz+VM.kz);M.rotation.set(rx+brP+VM.kp,ry+VM.ky,rz+Math.cos(VM.bob)*.02*ba);
 let ch=document.querySelector(".arena-crosshair");ch&&(ch.style.opacity=String(1-A))}
