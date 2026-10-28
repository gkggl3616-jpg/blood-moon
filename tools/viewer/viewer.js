import {THREE,takeStage,pauseStage,isStage,loadCharacter,keyFor,pinAssets,cachedAsset,configureCharacter,setRoarGlow} from './engine.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {WolfEffects} from './effects.js';
import {motionProfile,runRate,motionJoints} from './motion.js';
const host=document.getElementById('wolfModelViewport'),status=document.getElementById('modelStatus');
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(34,1,.05,40);
let model,loaded='',requested='',token=0,mixer,activeAction,currentMotion='WolfIdle',resumeMotion='WolfIdle',controls,fx,preview=null;
const reference=document.createElement('img');reference.id='modelReference';reference.alt='Karakter tasarım konsepti';reference.style.cssText='position:absolute;inset:0;width:100%;height:100%;object-fit:contain;display:none;pointer-events:none';host.prepend(reference);
scene.add(new THREE.HemisphereLight(0xc2dfed,0x32333b,2.5));const keyLight=new THREE.DirectionalLight(0xe6f3ff,3);keyLight.position.set(2,4,4);scene.add(keyLight);const rim=new THREE.DirectionalLight(0x87cddc,2.5);rim.position.set(-2,-3,3);scene.add(rim);
const floor=new THREE.Mesh(new THREE.CircleGeometry(1.0,40),new THREE.MeshBasicMaterial({color:0x2b6777,transparent:true,opacity:.13,side:THREE.DoubleSide}));floor.rotation.x=-Math.PI/2;floor.position.y=.008;floor.visible=false;scene.add(floor);
function inInventory(){return document.getElementById('collection').classList.contains('active');}
function state(){const base=window.getWolf3DState?.()||{};if(inInventory()&&preview){const settings=window.getArenaConfig?.(preview.id,'equipped')||{};return {...base,...settings,character:preview.id,form:preview.form,roaring:false};}return {...base,form:'wolf'};}
function statusText(s){status.textContent=s;}
function mount(){const target=inInventory()?document.getElementById('inventoryModelHost'):document.querySelector('#wolfGear .wolf-showcase');if(target&&host.parentElement!==target)target.prepend(host);}
function stage(){
 mount();
 if(!controls){const renderer=takeStage('viewer',host,scene,camera,tick);controls=new OrbitControls(camera,renderer.domElement);controls.enablePan=false;controls.minDistance=2.2;controls.maxDistance=6.5;controls.minPolarAngle=.55;controls.maxPolarAngle=2;fx=new WolfEffects(scene);}
 else if(!isStage('viewer'))takeStage('viewer',host,scene,camera,tick);
 controls.enabled=true;host.querySelector('canvas').style.visibility='visible';reference.style.display='none';host.dataset.webgl='ready';
}
window.fitWolfPreview=()=>{if(!model||!controls)return;const box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3()),rect=host.getBoundingClientRect(),aspect=Math.max(.2,rect.width/Math.max(1,rect.height));const dist=Math.max(size.y,size.x/aspect)/(2*Math.tan(34*Math.PI/360))*1.10;controls.maxDistance=Math.max(7,dist*1.4);controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(.06,.12,(inInventory()?1:-1)*dist));controls.update();};new ResizeObserver(()=>window.fitWolfPreview()).observe(host);
function tick(dt){if(!document.getElementById('wolfGear').classList.contains('active')&&!inInventory())return;const s=state();if(activeAction&&currentMotion==='WolfRunQuad'){const speed=window.getArenaStats?.(s.character,'wolf',!!s.roaring).values.speed||100;activeAction.setEffectiveTimeScale(runRate(model,8*speed/100));}mixer?.update(dt);controls?.update();const phase=currentMotion==='WolfRoar'?Math.min(1,(activeAction?.time||0)/motionProfile(model).roarDuration):null;setRoarGlow(model,!!s.roaring,phase);fx?.update(dt,s.roaring||false,s.form!=='human',phase);}
window.previewCharacter3D=(id,form='wolf')=>{preview={id,form};return window.refreshWolf3D();};
window.refreshWolf3D=async()=>{
 mount();const s=state(),id=keyFor(s.character,s.form);requested=id;
 if(s.form==='human'&&id!=='human-bilge'){
  ++token;host.dataset.loading='';host.dataset.modelReady='concept';controls&&(controls.enabled=false);pauseStage('viewer');const canvas=host.querySelector('canvas');if(canvas)canvas.style.visibility='hidden';reference.src='media/characters/'+keyFor(s.character)+'-human.webp';reference.style.display='block';statusText('İnsan formu • 2B tasarım konsepti');return;
 }
 try{stage();}catch(e){host.dataset.webgl='failed';statusText('Bu cihazda 3B görüntü açılamadı.');return;}
 if(id===loaded&&cachedAsset(id,model)){
  model.visible=true;
  if(host.dataset.loading&&host.dataset.loading!==id){++token;host.dataset.loading='';}
  if(model.parent!==scene){model.position.set(0,0,0);model.rotation.set(0,0,0);scene.add(model);startMotion(s.form==='human'?'HumanIdle':'WolfIdle');}
  host.dataset.modelReady='true';host.dataset.model=id;configureCharacter(model,s);statusText('Döndürmek için sürükle • İki parmakla yakınlaştır');return;
 }
 if(host.dataset.loading===id)return;
 const request=++token;host.dataset.loading=id;host.dataset.modelReady='false';statusText('3B model yükleniyor…');
 try{
  const gltf=await loadCharacter(id);if(request!==token||requested!==id)return;
  if(model)scene.remove(model);mixer?.stopAllAction();model=gltf.scene;model.visible=true;model.position.set(0,0,0);model.rotation.set(0,0,0);scene.add(model);loaded=id;pinAssets([id]);
  mixer=new THREE.AnimationMixer(model);activeAction=null;currentMotion='';mixer.addEventListener('finished',event=>{if(['WolfRoll','WolfClaw','WolfRoar'].includes(event.action.getClip().name))startMotion(resumeMotion==='WolfRunQuad'&&window.getWolfMotionAccess?.().run?'WolfRunQuad':s.form==='human'?'HumanIdle':'WolfIdle');});
  startMotion(s.form==='human'?'HumanIdle':'WolfIdle');fx.bind(model,keyFor(s.character));
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3());model.userData.previewHeight=box.getSize(new THREE.Vector3()).y;controls.target.set(center.x,center.y,center.z);camera.position.set(center.x+.12,center.y+.25,center.z+(inInventory()?3.8:-4.0));controls.update();window.fitWolfPreview();
  host.dataset.modelReady='true';host.dataset.model=id;host.dataset.loading='';configureCharacter(model,state());statusText('Döndürmek için sürükle • İki parmakla yakınlaştır');
 }catch(e){if(request===token){host.dataset.loading='';host.dataset.error=String(e);statusText('Model açılamadı. Farklı karakter seçip tekrar dene.');}}
};
function startMotion(name){if(!model||!mixer)return false;const clip=model.userData.motionClips?.find(c=>c.name===name)||model.userData.motionClips?.find(c=>c.name==='WolfIdle'||c.name==='HumanIdle');if(!clip)return false;const next=mixer.clipAction(clip);if(activeAction&&activeAction!==next)activeAction.fadeOut(.14);next.reset().setEffectiveTimeScale(1).setEffectiveWeight(1).fadeIn(.14);const once=['WolfRoll','WolfClaw','WolfRoar','WolfJump'].includes(name);next.setLoop(once?THREE.LoopOnce:THREE.LoopRepeat,once?1:Infinity);next.clampWhenFinished=once;next.play();activeAction=next;currentMotion=name;if(controls){const h=model.userData.previewHeight||2.25;controls.target.y=h*(name==='WolfRunQuad'?.30:name==='WolfRoar'?.57:.5);controls.update();}document.getElementById('runPreview').textContent=name==='WolfRunQuad'?'KOŞUYU DURDUR':'DÖRT AYAK KOŞ';host.dataset.motion=name;return true;}
window.playWolfMotion=name=>{if(['WolfRunQuad','WolfRoll'].includes(name)&&!model?.userData.motionClips?.some(c=>c.name===name)){statusText('Yeni çiftte bu hareket henüz hazır değil.');return false;}const access=window.getWolfMotionAccess?.()||{};if((name==='WolfRoll'&&!access.roll)||(name==='WolfRunQuad'&&!access.run)){statusText(name==='WolfRunQuad'?'Dört ayak koşu için efsanevi takla kuşan.':'Takla özelliğini önce kuşan.');return false;}if(currentMotion==='WolfRoll')return false;if(name==='WolfRunQuad'&&currentMotion==='WolfRunQuad')return startMotion('WolfIdle');resumeMotion=currentMotion;const ok=startMotion(name);if(ok){const d=name==='WolfRoar'?3.7:3.1;camera.position.set(controls.target.x+d,controls.target.y+.5,controls.target.z-d);controls.update();}return ok;};
window.checkWolfMotionAccess=()=>{const a=window.getWolfMotionAccess?.()||{};if(currentMotion==='WolfRunQuad'&&!a.run||currentMotion==='WolfRoll'&&!a.roll)startMotion('WolfIdle');};
window.stopWolfMotion=()=>{++token;host.dataset.loading='';if(mixer)startMotion('WolfIdle');if(controls)controls.enabled=false;pauseStage('viewer');};
window.wolf3DView=front=>{if(!controls||!model)return;const d=camera.position.distanceTo(controls.target);camera.position.set(controls.target.x+(front==='side'?d:.12),controls.target.y+.25,controls.target.z+(front==='side'?0:front?d:-d));controls.update();};
window.wolf3DInfo=()=>{const meshes=[],tattoos=[];model?.traverse(o=>{if(o.isMesh&&o.name.startsWith('Body')){const m=Array.isArray(o.material)?o.material[0]:o.material;meshes.push({name:o.name,color:m.color?.toArray(),metalness:m.metalness,roughness:m.roughness,emissive:m.emissive?.toArray(),emissiveIntensity:m.emissiveIntensity,map:!!m.map,normal:!!m.normalMap});}if(o.isMesh&&o.name.startsWith('Tattoo_'))tattoos.push({name:o.name,visible:o.visible,map:!!o.material.map,emissiveMap:!!o.material.emissiveMap,alphaTest:o.material.alphaTest,glow:o.material.emissiveIntensity});});return {loaded,visible:!!model?.visible&&model?.parent===scene,meshes,tattoos,motion:currentMotion,actionRate:activeAction?.getEffectiveTimeScale(),motionProfile:motionProfile(model),joints:motionJoints(model),clips:model?.userData.motionClips?.map(c=>c.name)||[],skinned:!!model?.getObjectByProperty('isSkinnedMesh',true),actionTime:activeAction?.time||0,effects:fx?.info()};};
