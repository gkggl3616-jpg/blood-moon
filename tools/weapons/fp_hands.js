/* First-person hands on the CC0 finger-rigged arms (models/fp_arms.glb, tools/weapons/build_fp_arms.py).
   Every bone points along its local +Y. The hand hangs from HandCtrl (not from the forearm), so the arm is solved here:
   two-bone IK for upper arm + forearm onto the wrist, the hand placed and oriented from the weapon's grip sockets,
   fingers curled bone by bone (index finger solved onto the trigger). */
var FPSKIN={bilge:0xf1d8c6,ates:0xd7a07c,kral:0xc8946f,ay:0xf6e2d8,hellgate:0x7a5149,zeynos:0xfde6dc};
var FH={v:Array.from({length:12},()=>new B.Vector3),q:new B.Quaternion,q2:new B.Quaternion,m:new B.Matrix4,m2:new B.Matrix4};
var FCH=["Index","Middle","Ring","Pinky","Thumb"];
function FpRigInit(f,s){f.updateMatrixWorld(!0);let id=Zw[s]||"bilge";f.traverse(o=>{o.isMesh&&o.material&&(o.material.color.setHex(FPSKIN[id]||16777215),o.material.roughness=.6)});let rig={};
 for(let L of["L","R"]){let up=f.getObjectByName("UpperArm"+L),fo=f.getObjectByName("Forearm"+L),ha=f.getObjectByName("Hand"+L);if(!up||!fo||!ha)continue;let W=n=>f.getObjectByName(n)?.getWorldPosition(new B.Vector3),pu=W("UpperArm"+L),pf=W("Forearm"+L),ph=W("Hand"+L),hs=ha.getWorldScale(new B.Vector3).x,inv=new B.Matrix4().copy(ha.matrixWorld).invert(),loc=v=>v.clone().applyMatrix4(inv);
  let kn=["Index","Middle","Ring","Pinky"].map(c=>loc(W(c+L+"1"))),fl=kn[1].clone().normalize(),side=kn[0].clone().sub(kn[3]),nl=new B.Vector3().crossVectors(side,fl).multiplyScalar(L==="R"?1:-1);nl.addScaledVector(fl,-nl.dot(fl)).normalize();
  let bl=new B.Vector3().crossVectors(fl,nl),Ml=new B.Matrix4().makeBasis(fl,nl,bl),avg=kn.reduce((a,b)=>a.add(b),new B.Vector3).multiplyScalar(.25),pc=avg.multiplyScalar(.5).addScaledVector(nl,.011/hs);
  let ch={};for(let c of FCH){let bs=[1,2,3].map(k=>f.getObjectByName(c+L+k)).filter(Boolean);if(bs.length<3)continue;let rest=bs.map(b=>b.quaternion.clone()),tip=()=>{let a=bs[2].getWorldPosition(new B.Vector3),b=bs[1].getWorldPosition(new B.Vector3);return a.addScaledVector(a.clone().sub(b),.85)};
   /* curl axis/sign: the local axis whose rotation moves the tip toward the palm (for the thumb: toward the palm centre) */
   let nw=nl.clone().transformDirection(ha.matrixWorld),pcw=pc.clone().applyMatrix4(ha.matrixWorld),t0=tip(),best=null;for(let ax of[[1,0,0],[0,0,1]])for(let sg of[1,-1]){let a=new B.Vector3(...ax).multiplyScalar(sg);bs.forEach((b,i)=>b.quaternion.copy(rest[i]).multiply(new B.Quaternion().setFromAxisAngle(a,.35)));bs[0].updateMatrixWorld(!0);let t=tip(),sc=c==="Thumb"?t0.distanceTo(pcw)-t.distanceTo(pcw):t.clone().sub(t0).dot(nw);(!best||sc>best[0])&&(best=[sc,a.clone()]);bs.forEach((b,i)=>b.quaternion.copy(rest[i]));bs[0].updateMatrixWorld(!0)}
   ch[c]={bs,rest,ax:best[1],tip}}
  rig[L]={l1:pu.distanceTo(pf),l2:pf.distanceTo(ph),Ml,pc,ch,hs,kn0:kn[0].clone()}}
 f.userData.rig=rig}
function FpCurl(c,a){if(!c)return;c.bs.forEach((b,i)=>b.quaternion.copy(c.rest[i]).multiply(FH.q.setFromAxisAngle(c.ax,a[i])));c.bs[0].updateMatrixWorld(!0)}
/* two-bone arm: upper arm and forearm point their +Y at the elbow and at the wrist target T */
function FpArmIK(up,fo,T,pole,l1,l2){let[S,E,D,P,X,A]=FH.v;up.getWorldPosition(S);D.copy(T).sub(S);let d=B.MathUtils.clamp(D.length(),Math.abs(l1-l2)+.002,l1+l2-.002);D.normalize();let a=(l1*l1-l2*l2+d*d)/(2*d),h=Math.sqrt(Math.max(0,l1*l1-a*a));P.copy(pole).addScaledVector(D,-pole.dot(D)).normalize();X.copy(S).addScaledVector(D,a).addScaledVector(P,h);fo.getWorldPosition(E);IKturn(up,A.copy(E).sub(S),FH.v[6].copy(X).sub(S));up.updateMatrixWorld(!0);fo.getWorldPosition(E);let y=FH.v[7].set(0,1,0).transformDirection(fo.matrixWorld);IKturn(fo,y,FH.v[8].copy(S).addScaledVector(D,d).sub(E));fo.updateMatrixWorld(!0);return fo.getWorldPosition(E).addScaledVector(FH.v[7].set(0,1,0).transformDirection(fo.matrixWorld),l2)}
/* world rotation of the hand bone for a wanted finger direction fw and palm normal nw */
function FpHandQ(r,fw,nw,out){let b=FH.v[9].crossVectors(fw,nw);FH.m.makeBasis(fw,nw,b);FH.m2.copy(r.Ml).transpose();FH.m.multiply(FH.m2);return out.setFromRotationMatrix(FH.m)}
function FpSetHand(ha,pos,q,ws){ha.parent.updateMatrixWorld(!0);FH.m.compose(pos,q,FH.v[10].setScalar(ws));FH.m2.copy(ha.parent.matrixWorld).invert().multiply(FH.m);FH.m2.decompose(ha.position,ha.quaternion,ha.scale);ha.updateMatrixWorld(!0)}
// palm normal n and thumb-side axis z of each hand in the weapon frame (gd: z = up the pistol grip), grip radius r,
// finger wrap per finger [index, middle, ring, pinky] (radians per joint), thumb [base, curl]
var GloveGrip={rifle:{R:{n:[-1,0,-.3],gd:1,r:.016,w:[0,1.2,1.25,1.3],t:[.5,.7]},L:{n:[1,0,-.15],z:[0,1,0],r:.017,w:[1.15,1.25,1.3,1.35],t:[.5,.7]}},
 sniper:{R:{n:[-1,0,-.3],gd:1,r:.016,w:[0,1.2,1.25,1.3],t:[.5,.7]},L:{n:[0,1,0],z:[0,0,-1],r:.024,w:[.9,.95,1,1.05],t:[.4,.4]}},
 pistol:{R:{n:[-1,0,-.3],gd:1,r:.014,w:[0,1.25,1.3,1.35],t:[.5,.7]},L:{n:[.8,.6,0],z:[0,.35,-1],r:.034,w:[1,1.05,1.1,1.15],t:[.3,.4]}},
 knife:{R:{n:[-1,.35,0],z:[0,0,-1],r:.013,w:[1.25,1.3,1.35,1.4],t:[.5,.8]}},
 frag:{R:{n:[-1,0,-.3],z:[0,1,0],r:.027,w:[.95,1,1.05,1.1],t:[.45,.55]}},
 smoke:{R:{n:[-1,0,-.3],z:[0,1,0],r:.022,w:[1.05,1.1,1.15,1.2],t:[.45,.6]}}};
function FpIK(){let f=hn?.userData.fp;if(!f||!hn.visible)return;let w=hn.userData.weapon,A=FPA[w];hn.updateMatrixWorld(!0);if(!A){f.visible=!1;return}f.visible=!0;let rig=f.userData.rig;if(!rig)return;
 let k=f.userData.fit?.k||1,gp=hn.userData.groups?.[w],M=gp?.userData.model,SK=gp?.userData.sock,cf=GloveGrip[w],T=IKv[8],Pl=IKv[9];M&&M.updateMatrixWorld(!0);
 for(let L of["L","R"]){let r=rig[L],up=f.getObjectByName("UpperArm"+L),fo=f.getObjectByName("Forearm"+L),ha=f.getObjectByName("Hand"+L);if(!r||!up||!fo||!ha)continue;
  let s=L==="L"?-1:1,c=cf?.[L],sk=L==="R"?"grip_r":"grip_l",S=M&&SK&&c&&SK[sk]?new B.Vector3().fromArray(SK[sk]).applyMatrix4(M.matrixWorld):null,ws=r.hs/k*1.05,hv=A["h"+L]||(L==="L"?[.2,1,.1]:[-1,-.25,0]),q=new B.Quaternion,Tw=new B.Vector3,el=new B.Vector3;
  Pl.fromArray(A["p"+L]).transformDirection(hn.matrixWorld);
  /* free / reloading hand: the fixed reach targets, palm by hint */
  T.fromArray(A[L]);L==="L"&&RL.k>0&&T.lerp(RL.tgt,RL.k);T.applyMatrix4(hn.matrixWorld);
  let freeQ=()=>{let E=FpArmIK(up,fo,T,Pl,r.l1,r.l2);up.getWorldPosition(el);let fw=fo.getWorldPosition(new B.Vector3);fw=E.clone().sub(fw).normalize();let nw=new B.Vector3().fromArray(hv).transformDirection(hn.matrixWorld);nw.addScaledVector(fw,-nw.dot(fw)).normalize();return[E,FpHandQ(r,fw,nw,new B.Quaternion)]};
  if(S){let z=new B.Vector3,n=new B.Vector3;c.gd?z.fromArray(SK.grip_dir).negate():z.fromArray(c.z);z.transformDirection(M.matrixWorld);n.fromArray(c.n).transformDirection(M.matrixWorld);n.addScaledVector(z,-n.dot(z)).normalize();let n0=n.clone(),fw=new B.Vector3,trig=L==="R"&&SK.trigger&&["rifle","sniper","pistol"].includes(w)?new B.Vector3().fromArray(SK.trigger).applyMatrix4(M.matrixWorld):null;
   for(let it=0;it<3;it++){fw.crossVectors(n,z).multiplyScalar(s).normalize();FpHandQ(r,fw,n,q);Tw.copy(S).addScaledVector(n,-c.r*.55).sub(r.pc.clone().multiplyScalar(ws).applyQuaternion(q));
    if(trig){let kw=Tw.clone().add(r.kn0.clone().multiplyScalar(ws).applyQuaternion(q));Tw.addScaledVector(z,B.MathUtils.clamp(trig.clone().sub(kw).dot(z),-.05,.05))}
    FpArmIK(up,fo,Tw,Pl,r.l1,r.l2);fo.getWorldPosition(el);let fd=el.sub(Tw);fd.addScaledVector(z,-fd.dot(z));if(fd.lengthSq()<1e-8)break;fd.normalize();let nx=new B.Vector3().crossVectors(fd,z).multiplyScalar(s);if(n0.angleTo(nx)>1.05){let ax=new B.Vector3().crossVectors(n0,nx).normalize();nx.copy(n0).applyAxisAngle(ax,1.05)}n.copy(nx)}
   fw.crossVectors(n,z).multiplyScalar(s).normalize();FpHandQ(r,fw,n,q);Tw.copy(S).addScaledVector(n,-c.r*.55).sub(r.pc.clone().multiplyScalar(ws).applyQuaternion(q));if(trig){let kw=Tw.clone().add(r.kn0.clone().multiplyScalar(ws).applyQuaternion(q));Tw.addScaledVector(z,B.MathUtils.clamp(trig.clone().sub(kw).dot(z),-.05,.05))}
   let rk=L==="L"?RL.k:0;if(rk>0){let[,qa]=freeQ();q.slerp(qa,rk);Tw.lerp(T,rk)}
   let E=FpArmIK(up,fo,Tw,Pl,r.l1,r.l2);FpSetHand(ha,E,q,ws);if(L==="R"){let nh=r.Ml.elements,nl=new B.Vector3(nh[4],nh[5],nh[6]).applyQuaternion(ha.getWorldQuaternion(new B.Quaternion));hn.userData.probe={S:S.toArray(),n:n.toArray(),z:z.toArray(),wrist:E.toArray(),handPalm:nl.toArray()}}ha.userData.sockErr=E.distanceTo(Tw)+(rk>0?0:0);
   /* wrap: each finger closes until its tip touches the grip surface (cylinder along z, or a ball for grenades) */
   let ball=w==="frag"||w==="smoke",dS=t=>{let v=t.clone().sub(S);ball||v.addScaledVector(z,-v.dot(z));return v.length()};
   for(let i=0;i<4;i++){if(i===0&&trig)continue;let ch=r.ch[FCH[i]],best=null;for(let a=.2;a<=1.65;a+=.05){FpCurl(ch,[a,a*1.1,a*.85]);let d=Math.abs(dS(ch.tip())-c.r-.002);(!best||d<best[0])&&(best=[d,a])}FpCurl(ch,[best[1],best[1]*1.1,best[1]*.85])}FpCurl(r.ch.Thumb,[c.t[0]*.5,c.t[1],c.t[1]*.8]);
   if(trig){let ch=r.ch.Index,b=null;if(!r.ic||r.icw!==w||(r.icn=(r.icn||0)+1)%15===0){for(let a=-.2;a<=1.6;a+=.08)for(let e=0;e<=1.8;e+=.08){FpCurl(ch,[a,e,e*.7]);let d=ch.tip().distanceTo(trig);(!b||d<b[0])&&(b=[d,a,e])}r.ic=b;r.icw=w}b=r.ic;FpCurl(ch,[b[1],b[2],b[2]*.7]);ha.userData.trig=ch.tip().distanceTo(trig)}else ha.userData.trig=null}
  else{let[E,qf]=freeQ();FpSetHand(ha,E,qf,ws);ha.userData.sockErr=null;ha.userData.trig=null;for(let i=0;i<4;i++)FpCurl(r.ch[FCH[i]],[.3,.35,.25]);FpCurl(r.ch.Thumb,[.15,.2,.15])}}}
