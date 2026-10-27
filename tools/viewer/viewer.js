import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const host=document.getElementById('wolfModelViewport');
let renderer,model,controls,requested='',loaded='',loadToken=0;
let mixer,activeAction,currentMotion='WolfIdle',resumeMotion='WolfIdle';
const motionClock=new THREE.Clock();
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(34,1,.05,40);
const loader=new GLTFLoader();
const cache=new Map();
function setStatus(s){document.getElementById('modelStatus').textContent=s;}
function initRenderer(){if(renderer)return true;
try{
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0x08131a,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.35;
 host.prepend(renderer.domElement);
 const pmrem=new THREE.PMREMGenerator(renderer);scene.environment=pmrem.fromScene(new RoomEnvironment(),.04).texture;pmrem.dispose();
 controls=new OrbitControls(camera,renderer.domElement);controls.enablePan=false;controls.minDistance=2.4;controls.maxDistance=7;controls.minPolarAngle=.55;controls.maxPolarAngle=2;controls.target.set(0,1.15,0);
 camera.position.set(.2,4.7,2.0);controls.update();
 scene.add(new THREE.HemisphereLight(0xc2dfed,0x32333b,2.5));
 const key=new THREE.DirectionalLight(0xe6f3ff,3);key.position.set(2,4,4);scene.add(key);
 const rim=new THREE.DirectionalLight(0x87cddc,2.5);rim.position.set(-2,-3,3);scene.add(rim);
 const floor=new THREE.Mesh(new THREE.CircleGeometry(1.1,48),new THREE.MeshBasicMaterial({color:0x2b6777,transparent:true,opacity:.13,side:THREE.DoubleSide}));floor.rotation.x=-Math.PI/2;floor.position.y=.008;scene.add(floor);
 function resize(){const r=host.getBoundingClientRect();if(r.width<2||r.height<2)return;renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();}
 new ResizeObserver(resize).observe(host);resize();
 renderer.setAnimationLoop(()=>{if(document.hidden||!document.getElementById('wolfGear').classList.contains('active'))return;const delta=Math.min(.06,motionClock.getDelta());mixer?.update(delta);controls.update();renderer.render(scene,camera);});
 host.dataset.webgl='ready';return true;
}catch(e){host.dataset.webgl='failed';setStatus('Bu cihazda 3B görüntü açılamadı. Donanım seçimi kullanılabilir.');return false;}
}
const modelIds={basibozuk:'kultigin',kul:'konuralp',ayaz:'alparslan',bilge:'bilge',kultigin:'kultigin',alparslan:'alparslan',konuralp:'konuralp'};
function updateParts(state){if(!model)return;const tattoos=state.tattoos||{};model.traverse(o=>{
 if(o.name.startsWith('Tattoo_back_'))o.visible=o.name.startsWith('Tattoo_back_'+(tattoos.back||'dragon')+'_');
 if(o.name.startsWith('Tattoo_left_'))o.visible=o.name.startsWith('Tattoo_left_'+(tattoos.left||'runes')+'_');
 if(o.name.startsWith('Tattoo_right_'))o.visible=o.name.startsWith('Tattoo_right_'+(tattoos.right||'runes')+'_');
 if(o.name.startsWith('Accessory_')){const name=o.name.replace(/\.\d+$/,'');o.visible=name==='Accessory_'+state.accessory||(name==='Accessory_cross_strap'&&state.accessory==='charm');}
 if(o.isMesh){const mats=Array.isArray(o.material)?o.material:[o.material];for(const mat of mats){if(mat?.name.startsWith('Fur_')){mat.metalness=0;mat.roughness=.78;mat.normalScale?.set(.35,.35);}
 if(mat?.name.startsWith('Tattoo_')){mat.emissiveIntensity=state.roaring?3:.15;mat.alphaTest=.3;mat.transparent=false;mat.depthWrite=true;mat.polygonOffset=true;mat.polygonOffsetFactor=-1;mat.polygonOffsetUnits=-1;}}}
 });
}
window.refreshWolf3D=async()=>{
 if(!renderer&&!initRenderer())return;
 const state=window.getWolf3DState?.();if(!state)return;
 const id=modelIds[state.character]||'kultigin';requested=id;
 if(id===loaded){if(host.dataset.loading&&host.dataset.loading!==id){++loadToken;host.dataset.loading='';}host.dataset.modelReady='true';host.dataset.model=id;updateParts(state);setStatus('Döndürmek için sürükle • Yakınlaştırmak için iki parmak');return;}
 if(host.dataset.loading===id)return;
 const token=++loadToken;host.dataset.loading=id;host.dataset.modelReady='false';setStatus('3B model yükleniyor…');
 try{
  let object=cache.get(id);
  if(!object){const gltf=await loader.loadAsync('models/'+id+'.glb');object=gltf.scene;object.userData.motionClips=gltf.animations;cache.set(id,object);}
  if(token!==loadToken||requested!==id)return;
  if(model)scene.remove(model);mixer?.stopAllAction();model=object;scene.add(model);loaded=id;
  mixer=new THREE.AnimationMixer(model);activeAction=null;currentMotion='WolfIdle';
  mixer.addEventListener('finished',event=>{if(event.action.getClip().name==='WolfRoll')startMotion(resumeMotion==='WolfRunQuad'&&window.getWolfMotionAccess?.().run?'WolfRunQuad':'WolfIdle');});
  startMotion('WolfIdle');
  // glTF uses Y-up. Camera starts at the back so the tattoo is visible.
  const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3());
  controls.target.set(center.x,center.y,center.z);camera.position.set(center.x+.25,center.y+.5,center.z-4.5);controls.update();
  host.dataset.modelReady='true';host.dataset.model=id;host.dataset.loading='';updateParts(window.getWolf3DState());setStatus('Döndürmek için sürükle • Yakınlaştırmak için iki parmak');
 }catch(e){if(token===loadToken){host.dataset.loading='';setStatus('Model yüklenemedi. Yeniden denemek için farklı kurt seç.');host.dataset.error=String(e);}}
};
window.wolf3DView=(front)=>{if(!model||!controls)return;camera.position.set(controls.target.x+.15,controls.target.y+.45,controls.target.z+(front?4.5:-4.5));controls.update();};
window.wolf3DInfo=()=>{const meshes=[],tattoos=[];model?.traverse(o=>{if(o.isMesh&&o.name.startsWith('Body')){const m=o.material;meshes.push({name:o.name,color:m.color?.toArray(),metalness:m.metalness,roughness:m.roughness,emissive:m.emissive?.toArray(),emissiveIntensity:m.emissiveIntensity,map:!!m.map,normal:!!m.normalMap});}if(o.isMesh&&o.name.startsWith('Tattoo_'))tattoos.push({name:o.name,visible:o.visible,map:!!o.material.map,emissiveMap:!!o.material.emissiveMap,alphaTest:o.material.alphaTest,glow:o.material.emissiveIntensity});});return {loaded,meshes,tattoos,motion:currentMotion,clips:model?.userData.motionClips?.map(c=>c.name)||[],skinned:!!model?.getObjectByProperty('isSkinnedMesh',true),actionTime:activeAction?.time||0};};

function startMotion(name){
 if(!mixer||!model)return false;
 const clip=model.userData.motionClips?.find(c=>c.name===name);if(!clip){setStatus('Bu modelde hareket klibi yok.');return false;}
 const next=mixer.clipAction(clip);
 if(activeAction&&activeAction!==next)activeAction.fadeOut(.18);
 next.reset().setEffectiveTimeScale(1).setEffectiveWeight(1).fadeIn(.18);
 next.setLoop(name==='WolfRoll'?THREE.LoopOnce:THREE.LoopRepeat,name==='WolfRoll'?1:Infinity);next.clampWhenFinished=name==='WolfRoll';next.play();activeAction=next;currentMotion=name;
 document.getElementById('runPreview').textContent=name==='WolfRunQuad'?'KOŞUYU DURDUR':'DÖRT AYAK KOŞ';
 host.dataset.motion=name;return true;
}
window.playWolfMotion=(name)=>{
 const access=window.getWolfMotionAccess?.()||{};
 if((name==='WolfRoll'&&!access.roll)||(name==='WolfRunQuad'&&!access.run)){setStatus(name==='WolfRunQuad'?'Dört ayak koşu için efsanevi takla kuşan.':'Takla özelliğini önce kuşan.');return false;}
 if(currentMotion==='WolfRoll')return false;
 if(name==='WolfRunQuad'&&currentMotion==='WolfRunQuad')return startMotion('WolfIdle');
 resumeMotion=currentMotion;
 const ok=startMotion(name);if(ok){camera.position.set(controls.target.x+3.4,controls.target.y+.6,controls.target.z-3.4);controls.update();}
 return ok;
};
window.checkWolfMotionAccess=()=>{const access=window.getWolfMotionAccess?.()||{};if((currentMotion==='WolfRunQuad'&&!access.run)||(currentMotion==='WolfRoll'&&!access.roll))startMotion('WolfIdle');};
window.stopWolfMotion=()=>{if(mixer)startMotion('WolfIdle');};
