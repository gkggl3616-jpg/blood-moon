import {THREE,takeStage,getRenderer,pauseStage,isStage,loadCharacter,keyFor,pinAssets,configureCharacter,engineInfo,identity} from './engine.js';
import {WolfEffects} from './effects.js';
import {humanView} from './human-view.js';
const $=id=>document.getElementById(id),host=$('arenaCanvas');
let releaseDirections=()=>{};
let initialized=false,active=false,scene,camera,actor,mixer,fx,viewmodel,action,config,loadToken=0;
let form='human',character='bilge',trial='legendary',motion='',yaw=0,pitch=0;
const ROLL={duration:.8,windup:.08,impactEnd:.60,speed:3.2,damage:38,radius:.95};
const rollHitTargets=new Set(),rollFrom=new THREE.Vector3(),rollStart=new THREE.Vector3();let rollYaw=0,roarPoseTime=0,rollDistance=0;
let groundVX=0,groundVZ=0,cameraTargetHeight=1.3,health=100,maxHealth=100,weaponSlot='primary',counterTime=0;
let simulationTime=0;let magazines={},grenadeTime=0,jumpDistance=0,jumpPeakSpeed=0;const jumpOrigin=new THREE.Vector3();const projectiles=[];
const stats=()=>window.getArenaStats(character,form,form==='wolf'&&roarTime>0);
const weapon=()=>window.RogueGear.items[config?.humanLoadout?.[weaponSlot]];
function syncHealth(){const next=stats().values.health;health=maxHealth?health/maxHealth*next:next;maxHealth=next;}
function selectWeapon(slot){if(form!=='human'||!['primary','secondary','knife','grenade'].includes(slot)||!config?.humanLoadout?.[slot])return false;weaponSlot=slot;reloadTime=0;ammo=magazines[weapon().id]??weapon().weapon.capacity??0;viewmodel.setWeapon(weapon().weapon.kind);updateHUD();return true;}
function receiveDamage(amount){const defense=stats().values.defense;const taken=Math.max(0,amount)*100/Math.max(1,defense);health=Math.max(0,health-taken);if(health===0){health=maxHealth;player.set(0,0,8);velocity.set(0,0,0);notice('Yeniden doğdun.',2);}return taken;}
const player=new THREE.Vector3(0,0,8),velocity=new THREE.Vector3();
let grounded=true,run=false,rollTime=0,jumpTime=0,attackTime=0,attackHit=false,transformTime=0,pendingForm='',roarTime=0,trackTime=0,ammo=30,reloadTime=0,hits=0,elapsed=0,fireHeld=false,nextFire=0,hitFlash=0,noticeTime=0,fps=60,hudTime=0;
const keys={},stick={x:0,y:0},blocks=[],targets=[],shootable=[];
const raycaster=new THREE.Raycaster(),aim=new THREE.Vector2(),forward=new THREE.Vector3(),desiredCam=new THREE.Vector3(),camQuaternion=new THREE.Quaternion();
const fixedStep=1/60;let accumulator=0;
function notice(text,duration=3){$('arenaNotice').textContent=text;$('arenaNotice').hidden=false;noticeTime=duration;}
function box(w,h,d,color,x,y,z){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color,roughness:.88,metalness:.05}));m.position.set(x,y,z);scene.add(m);return m;}
function init(){
 if(initialized)return;initialized=true;
 scene=new THREE.Scene();scene.background=new THREE.Color(0x101c26);scene.fog=new THREE.Fog(0x101c26,22,65);camera=new THREE.PerspectiveCamera(67,1,.06,100);
 scene.environmentIntensity=.35;scene.add(new THREE.HemisphereLight(0xd4e8f3,0x303f43,1.6));const sun=new THREE.DirectionalLight(0xf3e8cf,2.3);sun.position.set(-8,15,6);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-5,right:5,top:5,bottom:-5,near:.5,far:35});sun.shadow.normalBias=.025;sun.shadow.bias=-.0001;sun.shadow.radius=3;scene.add(sun);scene.add(sun.target);scene.userData.sun=sun;const renderer=getRenderer();renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 const rim=new THREE.DirectionalLight(0x709fc5,1.1);rim.position.set(10,5,-6);scene.add(rim);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(64,64),new THREE.MeshStandardMaterial({color:0x23383f,roughness:1}));ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;scene.add(ground);
 const grid=new THREE.GridHelper(64,32,0x536d75,0x344b52);grid.position.y=.003;scene.add(grid);
 for(const [x,z,w,d] of [[-32,0,.4,64],[32,0,.4,64],[0,-32,64,.4],[0,32,64,.4]])box(w,1.2,d,0x3a4d54,x,.6,z);
 for(const b of [{x:-5,z:-3,w:2.5,d:2.5,h:1.2},{x:6,z:-6,w:3,d:2,h:1.6},{x:-8,z:-13,w:3,d:1.6,h:1.05},{x:9,z:5,w:3,d:3,h:1.1}]){const mesh=box(b.w,b.h,b.d,0x56636a,b.x,b.h/2,b.z);b.box=new THREE.Box3(new THREE.Vector3(b.x-b.w/2,0,b.z-b.d/2),new THREE.Vector3(b.x+b.w/2,b.h,b.z+b.d/2));blocks.push(b);shootable.push(mesh);}
 for(const [i,x,z] of [[0,0,-8],[1,-10,-17],[2,10,-20]]){
  const target={id:i,hp:100,respawn:0,flash:0,group:new THREE.Group(),position:new THREE.Vector3(x,0,z),meshes:[]};target.group.position.copy(target.position);scene.add(target.group);
  const torso=new THREE.Mesh(new THREE.BoxGeometry(.75,.95,.4),new THREE.MeshStandardMaterial({color:0xb76b51,roughness:.8}));torso.position.y=1.2;torso.userData.target=i;torso.userData.part='body';target.group.add(torso);
  const head=new THREE.Mesh(new THREE.SphereGeometry(.24,10,8),new THREE.MeshStandardMaterial({color:0xdab28a,roughness:.8}));head.position.y=1.98;head.userData.target=i;head.userData.part='head';target.group.add(head);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.11,.15,.75,8),new THREE.MeshStandardMaterial({color:0x344048}));stem.position.y=.375;target.group.add(stem);
  const health=new THREE.Mesh(new THREE.PlaneGeometry(.9,.07),new THREE.MeshBasicMaterial({color:0x70d7ab,side:THREE.DoubleSide}));health.position.set(0,2.38,0);target.group.add(health);target.health=health;
  target.meshes=[torso,head];shootable.push(torso,head);targets.push(target);
 }
 fx=new WolfEffects(scene);createViewmodel();
 bindControls();
}
function createViewmodel(){viewmodel=humanView(scene);}
function reset(){releaseDirections();player.set(0,0,8);velocity.set(0,0,0);yaw=0;pitch=0;grounded=true;run=false;rollTime=jumpTime=attackTime=transformTime=roarTime=roarPoseTime=trackTime=reloadTime=0;rollHitTargets.clear();rollDistance=0;groundVX=groundVZ=0;cameraTargetHeight=1.3;form='human';simulationTime=0;weaponSlot='primary';magazines={};grenadeTime=0;for(const p of projectiles)scene.remove(p.mesh);projectiles.length=0;health=maxHealth=100;ammo=30;hits=0;nextFire=0;elapsed=0;fireHeld=false;Object.keys(keys).forEach(k=>keys[k]=false);stick.x=stick.y=0;for(const t of targets){t.hp=100;t.respawn=0;t.group.visible=true;t.health.scale.x=1;}motion='';}
function play(name,once=false){
 if(!mixer||!actor||motion===name)return;
 const clips=actor.userData.motionClips||[],clip=clips.find(c=>c.name===name)||clips.find(c=>c.name==='WolfIdle');if(!clip)return;
 const next=mixer.clipAction(clip);action?.fadeOut(.12);next.reset().setEffectiveWeight(1).setEffectiveTimeScale(1).fadeIn(.12).setLoop(once?THREE.LoopOnce:THREE.LoopRepeat,once?1:Infinity);next.clampWhenFinished=once;next.play();action=next;motion=name;
}
async function setCharacter(id){
 character=id;config=window.getArenaConfig(character,trial);syncHealth();if(!config.humanLoadout[weaponSlot])weaponSlot=Object.keys(config.humanLoadout).find(s=>config.humanLoadout[s])||'primary';if(form==='human'&&!selectWeapon(weaponSlot)){viewmodel.setWeapon('none');ammo=0;reloadTime=0;}$('arenaLoad').hidden=false;$('arenaLoad').textContent='Karakter yükleniyor…';const token=++loadToken;
 try{const key=keyFor(id);const data=await loadCharacter(key);if(token!==loadToken||!active)return;if(actor)scene.remove(actor);mixer?.stopAllAction();actor=data.scene;actor.position.set(0,0,0);actor.rotation.set(0,0,0);scene.add(actor);mixer=new THREE.AnimationMixer(actor);motion='';fx.bind(actor,key);configureCharacter(actor,config);pinAssets([key]);actor.traverse(o=>{if(o.isMesh){o.castShadow=o.name.startsWith('Body');o.receiveShadow=false;}});actor.visible=form==='wolf';$('arenaLoad').hidden=true;updateHUD();}
 catch(e){$('arenaLoad').textContent='Model açılamadı. Farklı karakter seçebilir veya lobiye dönebilirsin.';$('arenaLoad').style.pointerEvents='none';notice('3B model yüklenemedi.');console.warn('arena character load:',String(e));}
}
function applyConfig(){config=window.getArenaConfig(character,trial);if(!config.run)run=false;syncHealth();if(form==='human'&&!selectWeapon(weaponSlot)){viewmodel.setWeapon('none');ammo=0;reloadTime=0;}configureCharacter(actor,config);updateHUD();}
export async function openArena(){
 try{init();active=true;window.rogueOpenScreen('arena');reset();character=$('arenaCharacter').value||'bilge';trial=$('arenaTrial').value;takeStage('arena',host,scene,camera,update);await setCharacter(character);notice('Deneme donanımı açık. Dönüş, koşu, takla ve hedef vuruşlarını burada dene.',6);}
 catch(e){notice('Bu cihazda test alanı açılamadı.');$('arenaLoad').textContent='WebGL açılamadı. Lobiye dönüp tekrar dene.';console.warn(String(e));}
}
export function stopArena(){++loadToken;releaseDirections();active=false;fireHeld=false;run=false;Object.keys(keys).forEach(k=>keys[k]=false);stick.x=stick.y=0;mixer?.stopAllAction();pauseStage('arena');}
function allowed(){return active&&config&&actor&&transformTime<=0&&roarPoseTime<=0;}
function transform(){if(!allowed()||rollTime>0)return false;pendingForm=form==='human'?'wolf':'human';transformTime=.6;attackTime=0;run=false;fireHeld=false;$('arenaFlash').classList.remove('active');void $('arenaFlash').offsetWidth;$('arenaFlash').classList.add('active');fx.burst(player.clone().add(new THREE.Vector3(0,1.1,0)),0x9b6bff);notice(pendingForm==='wolf'?'Kurt formuna dönüşüyorsun.':'İnsan formuna dönüşüyorsun.',1.5);return true;}
function toggleRun(){if(!allowed())return false;if(form!=='wolf'){notice('Dört ayak koşu kurt formunda kullanılır.');return false;}if(!config.run){notice('Dört ayak koşu için efsanevi takla kuşan veya deneme donanımını seç.');return false;}run=!run;updateHUD();return true;}
function roll(){if(!allowed()||form!=='wolf'||rollTime>0)return false;if(!config.roll){notice('Takla özelliği takılı değil.');return false;}rollTime=ROLL.duration;rollYaw=yaw;rollStart.copy(player);rollDistance=0;rollHitTargets.clear();attackTime=jumpTime=0;fireHeld=false;velocity.x=velocity.z=0;play('WolfRoll',true);notice('Kısa takla • temas hasarı',1);return true;}
function jump(){if(!allowed()||!grounded||rollTime>0)return false;grounded=false;velocity.y=6.8;jumpTime=.85;jumpOrigin.copy(player);jumpDistance=jumpPeakSpeed=0;const moving=Math.hypot(groundVX,groundVZ)>.1;velocity.x=moving?groundVX:-Math.sin(yaw)*(form==='wolf'?4.2:.5);velocity.z=moving?groundVZ:-Math.cos(yaw)*(form==='wolf'?4.2:.5);play('WolfJump',true);return true;}
function roar(){if(!allowed()||rollTime>0)return false;if(form==='human'){const cap=weapon()?.weapon.capacity;if(cap&&reloadTime<=0&&ammo<cap){reloadTime=1.4;notice('Şarjör değiştiriliyor.',1.4);return true;}return false;}if(roarTime>0)return false;roarTime=20;roarPoseTime=1.2;run=false;fireHeld=false;velocity.x=velocity.z=groundVX=groundVZ=0;window.roguePlaySound?.('roar');configureCharacter(actor,{...config,roaring:true});play('WolfRoar',true);attackTime=0;notice('20 sn: hız +%20, hasar +%15, savunma +%30. Mor alevler etkin.',4);return true;}
function track(){if(!allowed()||form!=='wolf')return false;trackTime=8;notice('İz sürme: eğitim hedefleri 8 sn vurgulanıyor.',3);return true;}
function damage(t,amount,critical=false,kind='claw'){if(t.hp<=0)return;t.hp=Math.max(0,t.hp-amount);t.flash=.16;t.health.scale.x=Math.max(.01,t.hp/100);hits++;hitFlash=.18;$('arenaDamage').textContent=(kind==='roll'?'TAKLA ':critical?'KRİTİK ':'')+Math.round(amount);fx.burst(t.position.clone().add(new THREE.Vector3(0,1.3,0)),critical?0xffc45c:0x84ddff);if(t.hp===0){t.respawn=3;t.group.visible=false;notice('Hedef devrildi. 3 saniye sonra yenilenir.',2);}}
function fire(){
 if(!allowed()||rollTime>0||elapsed<nextFire)return false;
 if(form==='human'){
  const item=weapon(),w=item?.weapon;if(!w||reloadTime>0)return false;
  if(w.kind==='knife'){nextFire=elapsed+w.interval;viewmodel.userData.recoil=-.15;const facing=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw));for(const t of targets){const delta=t.position.clone().sub(player);if(t.hp>0&&delta.length()<w.range&&delta.normalize().dot(facing)>.6&&clearSight(player,t.position)){damage(t,w.damage*stats().values.damage/100);break;}}}
  else if(w.kind==='frag'||w.kind==='smoke'){if(grenadeTime>0)return false;grenadeTime=w.interval;nextFire=elapsed+.5;const mesh=new THREE.Mesh(new THREE.IcosahedronGeometry(.075,1),new THREE.MeshStandardMaterial({color:0x557955}));mesh.position.copy(player).add(new THREE.Vector3(0,1.5,0));scene.add(mesh);const direction=camera.getWorldDirection(new THREE.Vector3());direction.y=Math.max(.25,direction.y);projectiles.push({mesh,velocity:direction.multiplyScalar(9),time:1.1,weapon:w});viewmodel.userData.recoil=-.12;}
  else{if(ammo<=0){roar();return false;}ammo--;magazines[weapon().id]=ammo;nextFire=elapsed+w.interval;viewmodel.userData.recoil=.07;
   raycaster.setFromCamera(aim,camera);scene.updateMatrixWorld(true);const intersections=raycaster.intersectObjects(shootable,false);const hit=intersections.find(h=>h.object.visible&&h.object.parent.visible);
   if(hit&&hit.object.userData.target!==undefined){const target=targets[hit.object.userData.target],critical=hit.object.userData.part==='head';damage(target,w.damage*(critical?1.5:1)*stats().values.damage/100,critical);}
  }
  updateHUD();return true;
 }
 nextFire=elapsed+.65;attackTime=.65;attackHit=false;play('WolfClaw',true);fx.claw(player,yaw);return true;
}
function clearSight(a,b){const origin=a.clone();origin.y+=1;const end=b.clone();end.y+=1;const d=end.sub(origin),length=d.length();if(length<.001)return true;const ray=new THREE.Ray(origin,d.normalize());return !blocks.some(b=>{const p=ray.intersectBox(b.box,new THREE.Vector3());return p&&p.distanceTo(origin)<length;});}
function updateProjectiles(dt){for(let i=projectiles.length-1;i>=0;i--){const p=projectiles[i];p.time-=dt;if(p.weapon.kind==='cloud'){p.mesh.material.opacity=.35*Math.min(1,p.time);if(p.time>0)continue;scene.remove(p.mesh);p.mesh.geometry.dispose();p.mesh.material.dispose();projectiles.splice(i,1);continue;}p.velocity.y-=12*dt;const next=p.mesh.position.clone().addScaledVector(p.velocity,dt);if(next.y<.08){next.y=.08;p.velocity.y=Math.abs(p.velocity.y)*.3;p.velocity.x*=.65;p.velocity.z*=.65;}if(blocks.some(b=>b.box.containsPoint(next))){p.velocity.multiplyScalar(-.25);next.copy(p.mesh.position);next.y=Math.max(.08,next.y);}p.mesh.position.copy(next);if(p.time>0)continue;
 if(p.weapon.damage)for(const t of targets){const dist=t.position.distanceTo(p.mesh.position);if(dist<p.weapon.radius&&clearSight(p.mesh.position,t.position))damage(t,p.weapon.damage*(1-dist/p.weapon.radius*.6)*stats().values.damage/100);}
 fx.burst(p.mesh.position.clone(),p.weapon.damage?0xffad62:0x9ba5af);if(!p.weapon.damage){const smoke=new THREE.Mesh(new THREE.SphereGeometry(1,12,8),new THREE.MeshBasicMaterial({color:0x7b8790,transparent:true,opacity:.35,depthWrite:false}));smoke.position.copy(p.mesh.position);smoke.position.y+=1;smoke.scale.setScalar(p.weapon.radius*.6);scene.add(smoke);projectiles.push({mesh:smoke,velocity:new THREE.Vector3(),time:5,weapon:{damage:0,kind:'cloud'}});}
 scene.remove(p.mesh);p.mesh.geometry.dispose();p.mesh.material.dispose();projectiles.splice(i,1);
 }}
function meleeImpact(){
 const facing=new THREE.Vector3(-Math.sin(yaw),0,-Math.cos(yaw)),power=stats().values.damage;
 for(const t of targets){if(t.hp<=0)continue;const delta=t.position.clone().sub(player);const dist=delta.length();if(dist>2.6||Math.abs(player.y)>1.8||delta.normalize().dot(facing)<.55)continue;
  const origin=player.clone().add(new THREE.Vector3(0,1.3,0)),end=t.position.clone().add(new THREE.Vector3(0,1.3,0)),direction=end.clone().sub(origin),length=direction.length();const ray=new THREE.Ray(origin,direction.normalize());if(blocks.some(b=>{const point=ray.intersectBox(b.box,new THREE.Vector3());return point&&point.distanceTo(origin)<length;}))continue;damage(t,28*power/100);break;
 }
}
function rollImpact(from,to){
 const age=ROLL.duration-rollTime;if(age<ROLL.windup||age>ROLL.impactEnd)return;
 const segment=new THREE.Line3(from,to),closest=new THREE.Vector3();
 const power=stats().values.damage;
 for(const t of targets){
  if(t.hp<=0||rollHitTargets.has(t.id)||Math.abs(t.position.y-player.y)>1.6)continue;
  // At a wall (or during recovery) the sweep can have zero length. Projecting
  // onto that segment divides by zero; use a point contact instead.
  if(from.distanceToSquared(to)<1e-10)closest.copy(to);
  else segment.closestPointToPoint(t.position,true,closest);
  if(Math.hypot(closest.x-t.position.x,closest.z-t.position.z)>ROLL.radius)continue;
  const origin=closest.clone();origin.y=player.y+1;
  const end=t.position.clone();end.y+=1;const direction=end.clone().sub(origin),distance=direction.length();
  if(distance>.001){const ray=new THREE.Ray(origin,direction.normalize());if(blocks.some(b=>{const hit=ray.intersectBox(b.box,new THREE.Vector3());return hit&&hit.distanceTo(origin)<distance;}))continue;}
  rollHitTargets.add(t.id);damage(t,ROLL.damage*power/100,false,'roll');
 }
}
function simulate(dt){simulationTime+=dt;
 const oldY=player.y,rollingStep=rollTime>0;rollFrom.copy(player);velocity.y-=16*dt;
 if(rollingStep)rollTime=Math.max(0,rollTime-dt);
 let x=stick.x+(keys.KeyD?1:0)-(keys.KeyA?1:0),z=stick.y+(keys.KeyS?1:0)-(keys.KeyW?1:0);const n=Math.hypot(x,z);if(n>1){x/=n;z/=n;}
 let speed=(form==='wolf'?(run&&config.run?8:4.3):4.1)*stats().values.speed/100;if(transformTime>0)speed*=.2;if(roarPoseTime>0)speed=0;
 const sin=Math.sin(yaw),cos=Math.cos(yaw);let dx=(x*cos+z*sin)*speed*dt,dz=(-x*sin+z*cos)*speed*dt;
 if(!grounded){if(n>.07&&roarPoseTime<=0&&rollTime<=0){const turn=Math.min(1,dt*1.5);velocity.x+=(dx/dt-velocity.x)*turn;velocity.z+=(dz/dt-velocity.z)*turn;}dx=dz=0;}
 if(roarPoseTime>0){dx=dz=0;velocity.x=velocity.z=0;}
 if(rollingStep){const age=ROLL.duration-rollTime,factor=age<ROLL.windup?0:age>ROLL.impactEnd?Math.max(0,rollTime/(ROLL.duration-ROLL.impactEnd)):1;dx=-Math.sin(rollYaw)*ROLL.speed*factor*dt;dz=-Math.cos(rollYaw)*ROLL.speed*factor*dt;}
 if(grounded&&rollTime<=0){groundVX=dx/dt;groundVZ=dz/dt;velocity.x=velocity.z=0;}
 if(!grounded)jumpPeakSpeed=Math.max(jumpPeakSpeed,Math.hypot(dx/dt+velocity.x,dz/dt+velocity.z));player.x+=dx+velocity.x*dt;player.z+=dz+velocity.z*dt;velocity.x*=Math.exp(-.12*dt);velocity.z*=Math.exp(-.12*dt);player.y+=velocity.y*dt;
 const radius=.37,height=form==='wolf'?2.05:1.78;let ground=0;
 for(const b of blocks){const minX=b.x-b.w/2-radius,maxX=b.x+b.w/2+radius,minZ=b.z-b.d/2-radius,maxZ=b.z+b.d/2+radius;if(player.x<minX||player.x>maxX||player.z<minZ||player.z>maxZ)continue;
  if(oldY>=b.h-.08&&velocity.y<=0){ground=Math.max(ground,b.h);continue;}if(player.y>=b.h||player.y+height<=0)continue;
  const sides=[player.x-minX,maxX-player.x,player.z-minZ,maxZ-player.z],side=sides.indexOf(Math.min(...sides));if(side===0)player.x=minX;else if(side===1)player.x=maxX;else if(side===2)player.z=minZ;else player.z=maxZ;
 }
 player.x=THREE.MathUtils.clamp(player.x,-31.3,31.3);player.z=THREE.MathUtils.clamp(player.z,-31.3,31.3);
 if(player.y<=ground&&velocity.y<=0){if(!grounded)jumpDistance=Math.hypot(player.x-jumpOrigin.x,player.z-jumpOrigin.z);player.y=ground;velocity.y=velocity.x=velocity.z=0;grounded=true;}else grounded=false;
 if(rollingStep){rollImpact(rollFrom,player);rollDistance=Math.hypot(player.x-rollStart.x,player.z-rollStart.z);}
 return Math.hypot(player.x-rollFrom.x,player.z-rollFrom.z)>.0005;
}
function update(dt,time){
 if(!active||!config)return;elapsed+=dt;fps+=(1/Math.max(.005,dt)-fps)*.05;
 if(keys.ArrowLeft)yaw+=dt*1.7;if(keys.ArrowRight)yaw-=dt*1.7;if(keys.ArrowUp)pitch+=dt;if(keys.ArrowDown)pitch-=dt;pitch=THREE.MathUtils.clamp(pitch,-1.15,1.1);
 if(transformTime>0){const before=transformTime;transformTime=Math.max(0,transformTime-dt);if(before>.3&&transformTime<=.3){form=pendingForm;nextFire=elapsed;syncHealth();if(form==='human')selectWeapon(weaponSlot);attackTime=0;rollTime=0;motion='';if(form==='wolf')play('WolfTransform',true);updateHUD();}}
 roarPoseTime=Math.max(0,roarPoseTime-dt);jumpTime=Math.max(0,jumpTime-dt);attackTime=Math.max(0,attackTime-dt);if(attackTime>0&&attackTime<.42&&!attackHit){attackHit=true;meleeImpact();}
 if(roarTime>0){roarTime=Math.max(0,roarTime-dt);if(roarTime===0)configureCharacter(actor,config);}trackTime=Math.max(0,trackTime-dt);
 if(reloadTime>0){reloadTime=Math.max(0,reloadTime-dt);if(reloadTime===0){ammo=weapon()?.weapon.capacity||0;magazines[weapon().id]=ammo;}}
 grenadeTime=Math.max(0,grenadeTime-dt);updateProjectiles(dt);counterTime-=dt;if($('arenaCounterfire').checked&&counterTime<=0){counterTime=1;const t=targets.find(t=>t.hp>0&&t.position.distanceTo(player)<20&&clearSight(t.position,player));if(t)receiveDamage(12);}
 let moving=false;accumulator=Math.min(.18,accumulator+dt);while(accumulator>=fixedStep){moving=simulate(fixedStep);accumulator-=fixedStep;}
 if(fireHeld)fire();
 if(actor){actor.visible=form==='wolf';actor.position.copy(player);actor.rotation.set(0,(rollTime>0?rollYaw:yaw)+Math.PI,0);
  if(form==='wolf'){if(transformTime>0)play('WolfTransform',true);else if(rollTime>0)play('WolfRoll',true);else if(roarPoseTime>0)play('WolfRoar',true);else if(attackTime>0)play('WolfClaw',true);else if(!grounded)play('WolfJump',true);else if(moving)play(run?'WolfRunQuad':'WolfMove');else play('WolfIdle');if(action)action.setEffectiveTimeScale(motion==='WolfRunQuad'?8/5.6*stats().values.speed/100:motion==='WolfMove'?4.3/3.6*stats().values.speed/100:1);mixer?.update(dt);}
 }
 const sin=Math.sin(yaw),cos=Math.cos(yaw);
 if(form==='human'){desiredCam.set(player.x,player.y+1.66,player.z);camQuaternion.setFromEuler(new THREE.Euler(pitch,yaw,0,'YXZ'));camera.position.lerp(desiredCam,Math.min(1,dt*22));camera.quaternion.slerp(camQuaternion,Math.min(1,dt*22));}
 else{cameraTargetHeight+=((run&&moving&&grounded&&rollTime<=0?.88:1.3)-cameraTargetHeight)*Math.min(1,dt*8);const distance=rollTime>0?4.0:3.8,elevation=.22-pitch;desiredCam.set(player.x+sin*distance*Math.cos(elevation),Math.max(player.y+.25,player.y+cameraTargetHeight+Math.sin(elevation)*distance),player.z+cos*distance*Math.cos(elevation));camera.position.lerp(desiredCam,Math.min(1,dt*11));camera.lookAt(player.x-sin*.8,player.y+cameraTargetHeight,player.z-cos*.8);}
 camera.fov+=( (run&&form==='wolf'?70:67)-camera.fov)*Math.min(1,dt*6);camera.updateProjectionMatrix();
 viewmodel.visible=form==='human';viewmodel.position.copy(camera.position);viewmodel.quaternion.copy(camera.quaternion);viewmodel.userData.recoil*=Math.exp(-14*dt);viewmodel.translateZ(viewmodel.userData.recoil);if(moving){viewmodel.translateY(Math.sin(elapsed*12)*.01);viewmodel.translateX(Math.cos(elapsed*6)*.009);}if(reloadTime>0)viewmodel.rotateZ(Math.sin((1.4-reloadTime)/1.4*Math.PI)*-.55);
 const sun=scene.userData.sun;sun.position.set(player.x-8,15,player.z+6);sun.target.position.set(player.x,0,player.z);
 for(const t of targets){t.health.lookAt(camera.position);if(t.respawn>0){t.respawn-=dt;if(t.respawn<=0){t.hp=100;t.group.visible=true;t.health.scale.x=1;}}t.flash=Math.max(0,t.flash-dt);for(const m of t.meshes){m.material.emissive.setHex(t.flash>0?0xff6633:trackTime>0?0x196959:0);m.material.emissiveIntensity=t.flash>0?1:trackTime>0?.5:0;}}
 fx.update(dt,roarTime>0,form==='wolf');hitFlash=Math.max(0,hitFlash-dt);$('arenaHit').classList.toggle('active',hitFlash>0);if(hitFlash===0)$('arenaDamage').textContent='';
 if(noticeTime>0){noticeTime-=dt;if(noticeTime<=0)$('arenaNotice').hidden=true;}
 hudTime+=dt;if(hudTime>.12){hudTime=0;updateHUD();}
}
function updateHUD(){if(!config)return;const wolf=form==='wolf',w=weapon()?.weapon;$('arenaFire').disabled=transformTime>0||roarPoseTime>0||(!wolf&&!w);$('arenaHealth').textContent=Math.ceil(health)+' / '+Math.round(maxHealth)+' HP';$('arenaWeapons').hidden=wolf;document.querySelectorAll('[data-weapon-slot]').forEach(b=>{b.disabled=!config.humanLoadout[b.dataset.weaponSlot];b.classList.toggle('active',b.dataset.weaponSlot===weaponSlot);});$('arenaName').textContent=wolf?config.wolf:config.name;$('arenaMode').textContent=wolf?'KURT • ÜÇÜNCÜ ŞAHIS':'İNSAN • BİRİNCİ ŞAHIS · '+(weapon()?.name||'SİLAH YOK');$('arenaTransform').querySelector('.action-label').textContent=wolf?'İNSAN':'KURT';$('arenaFire').querySelector('.action-label').textContent=wolf?'PENÇE':'ATEŞ';$('arenaRun').disabled=!wolf||!config.run;$('arenaRoll').disabled=!wolf||!config.roll;$('arenaRun').classList.toggle('active',run);$('arenaRoarButton').querySelector('.action-label').textContent=wolf?'KÜKRE':'DOLDUR';$('arenaRoarButton').disabled=wolf?roarTime>0:reloadTime>0||!w?.capacity||ammo===w.capacity;$('arenaTrack').disabled=!wolf;$('arenaRoar').hidden=roarTime<=0;$('arenaRoarTimer').textContent=roarTime.toFixed(1)+' sn';$('arenaRoarBar').style.width=(roarTime/20*100)+'%';$('arenaTargets').textContent='İSABET '+hits+(wolf?'':w?.capacity?' · '+ammo+'/'+w.capacity:grenadeTime>0?' · '+grenadeTime.toFixed(1)+' sn':'');$('arenaAction').textContent=transformTime>0?'DÖNÜŞÜM':rollTime>0?'TAKLA':roarPoseTime>0?'KÜKREME':attackTime>0?'PENÇE VURUŞU':!grounded?'HAVADA':run?'DÖRT AYAK KOŞU':'HAZIR';$('arenaPerformance').textContent=Math.round(fps)+' FPS';}
function bindControls(){
 document.querySelectorAll('[data-weapon-slot]').forEach(b=>b.onclick=()=>selectWeapon(b.dataset.weaponSlot));window.addEventListener('rogue-gear-changed',()=>{if(active)applyConfig();});
 $('arenaExit').onclick=()=>{stopArena();window.rogueOpenScreen('lobby');};$('arenaTransform').onclick=transform;$('arenaRun').onclick=toggleRun;$('arenaRoll').onclick=roll;$('arenaJump').onclick=jump;$('arenaRoarButton').onclick=roar;$('arenaTrack').onclick=track;
 $('arenaCharacter').onchange=()=>{roarTime=roarPoseTime=0;run=false;rollTime=0;attackTime=0;setCharacter($('arenaCharacter').value);};$('arenaTrial').onchange=()=>{trial=$('arenaTrial').value;applyConfig();};
 $('arenaFire').addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();fireHeld=true;fire();e.currentTarget.setPointerCapture?.(e.pointerId);});for(const name of ['pointerup','pointercancel','lostpointercapture'])$('arenaFire').addEventListener(name,()=>fireHeld=false);
 $('arenaFire').addEventListener('click',e=>{if(e.detail===0)fire();});
 const heldDirections=new Map();let lastForward=-Infinity;
 const syncDirections=()=>{const dirs=new Set(heldDirections.values());stick.x=(dirs.has('right')?1:0)-(dirs.has('left')?1:0);stick.y=(dirs.has('back')?1:0)-(dirs.has('forward')?1:0);document.querySelectorAll('[data-move]').forEach(b=>b.classList.toggle('pressed',dirs.has(b.dataset.move)));};
 for(const button of document.querySelectorAll('[data-move]')){
  button.addEventListener('pointerdown',e=>{e.preventDefault();if(!active)return;const direction=button.dataset.move;heldDirections.set(e.pointerId,direction);button.setPointerCapture(e.pointerId);if(direction==='forward'){const now=performance.now();if(now-lastForward<=330&&form==='wolf'&&!run)toggleRun();lastForward=now;}syncDirections();});
  for(const name of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(name,e=>{heldDirections.delete(e.pointerId);syncDirections();});
 }
 const releaseStick=()=>{heldDirections.clear();lastForward=-Infinity;syncDirections();};releaseDirections=releaseStick;
 let lookPointer=null,lx=0,ly=0;host.addEventListener('contextmenu',e=>e.preventDefault());host.addEventListener('pointerdown',e=>{if(!active)return;lookPointer=e.pointerId;lx=e.clientX;ly=e.clientY;host.setPointerCapture(e.pointerId);e.preventDefault();});host.addEventListener('pointermove',e=>{if(e.pointerId!==lookPointer)return;const sensitivity=(window.getRoguePreferences?.().lookSensitivity||1.45)*Math.PI*2/Math.max(1,host.getBoundingClientRect().width);yaw-=(e.clientX-lx)*sensitivity;pitch-=(e.clientY-ly)*sensitivity*.8;lx=e.clientX;ly=e.clientY;});for(const name of ['pointerup','pointercancel','lostpointercapture'])host.addEventListener(name,()=>lookPointer=null);
 window.addEventListener('keydown',e=>{if(!active||/SELECT|INPUT/.test(e.target.tagName))return;keys[e.code]=true;if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();if(e.repeat)return;({Digit1:()=>selectWeapon('primary'),Digit2:()=>selectWeapon('secondary'),Digit3:()=>selectWeapon('knife'),Digit4:()=>selectWeapon('grenade'),KeyE:transform,KeyQ:roll,Space:jump,KeyR:roar,KeyT:track,KeyF:fire,ShiftLeft:toggleRun,ShiftRight:toggleRun})[e.code]?.();});window.addEventListener('keyup',e=>{keys[e.code]=false;});window.addEventListener('blur',()=>{fireHeld=false;Object.keys(keys).forEach(k=>keys[k]=false);releaseStick();});
}
window.openArena=openArena;window.stopArena=stopArena;
window.arenaDebug={state:()=>({active,time:elapsed,simulationTime,ready:!!actor,character,form,camera:camera?.position.toArray(),position:player.toArray(),yaw,pitch,velocity:velocity.toArray(),grounded,canAct:allowed(),attackCooldown:Math.max(0,nextFire-elapsed),run,jumpDistance,jumpPeakSpeed,rollTime,rollDistance,roarTime,roarPoseTime,attackTime,ammo,hits,rollHitTargets:[...rollHitTargets],lookDirection:camera?.getWorldDirection(new THREE.Vector3()).toArray(),targets:targets.map(t=>({hp:t.hp,position:t.position.toArray(),respawn:t.respawn})),motion,stats:stats().values,statLayers:stats(),health,maxHealth,weaponSlot,weapon:weapon()?.id,grenadeTime,projectiles:projectiles.length,effects:fx?.info(),render:engineInfo(),shadow:{type:'PCFSoft',resolution:1024},input:{...stick}}),action:name=>({transform,run:toggleRun,roll,jump,roar,track,fire})[name]?.(),place:(x,z,angle=0,lookPitch=0)=>{player.set(x,0,z);yaw=angle;pitch=lookPitch;velocity.set(0,0,0);},aimAt:id=>{const p=targets[id].position.clone();p.y=1.3;const d=p.sub(player.clone().add(new THREE.Vector3(0,1.66,0)));yaw=Math.atan2(-d.x,-d.z);pitch=Math.atan2(d.y,Math.hypot(d.x,d.z));},expireRoar:()=>{roarTime=0;configureCharacter(actor,config);},setCharacter,selectWeapon,receiveDamage};
