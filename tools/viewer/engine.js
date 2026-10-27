import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
export {THREE};
const loader=new GLTFLoader(),cache=new Map(),pending=new Map();
let renderer,active,env,lastTime=0,pins=new Set();
export const modelIds={basibozuk:'kultigin',kul:'konuralp',ayaz:'alparslan',bilge:'bilge',kultigin:'kultigin',alparslan:'alparslan',konuralp:'konuralp'};
export const identity={bilge:{name:'BOZ KAĞAN',element:'BUZ',color:0x70dfff,claws:3,tilt:-.35},kultigin:{name:'KARA TİGİN',element:'KAN',color:0xff354d,claws:2,tilt:.65},alparslan:{name:'BOZ ARSLAN',element:'KÖZ',color:0xffae36,claws:3,tilt:-.8},konuralp:{name:'UÇ AVCISI',element:'GÖLGE',color:0xaf65ff,claws:4,tilt:.25}};
export function keyFor(id,form='wolf'){const key=modelIds[id]||'kultigin';return form==='human'?'human-'+key:key;}
export function getRenderer(){
 if(renderer)return renderer;
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.25));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
 renderer.domElement.style.cssText='width:100%;height:100%;display:block;touch-action:none';
 const pmrem=new THREE.PMREMGenerator(renderer);env=pmrem.fromScene(new RoomEnvironment(),.08).texture;pmrem.dispose();
 renderer.setAnimationLoop(time=>{
  const dt=Math.min(.12,lastTime?(time-lastTime)/1000:0);lastTime=time;
  if(!active||document.hidden)return;
  const r=active.host.getBoundingClientRect();if(r.width<2||r.height<2)return;
  const w=Math.round(r.width),h=Math.round(r.height);
  if(active.width!==w||active.height!==h){renderer.setSize(w,h,false);active.camera.aspect=w/h;active.camera.updateProjectionMatrix();active.width=w;active.height=h;}
  active.update?.(dt,time/1000);renderer.render(active.scene,active.camera);
 });
 return renderer;
}
export function takeStage(name,host,scene,camera,update){const r=getRenderer();host.prepend(r.domElement);scene.environment=env;active={name,host,scene,camera,update};lastTime=0;r.setClearColor(name==='arena'?0x101c26:0x08131a,name==='arena'?1:0);return r;}
export function isStage(name){return active?.name===name;}
export function pauseStage(name){if(active?.name===name)active=null;}
export function pinAssets(keys){pins=new Set(keys);trimCache();}
function disposeAsset(object){const geo=new Set(),mats=new Set(),textures=new Set();object.traverse(o=>{if(o.geometry)geo.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])if(m){mats.add(m);for(const v of Object.values(m))if(v?.isTexture)textures.add(v);}});geo.forEach(g=>g.dispose());mats.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());}
function trimCache(){for(const [key,value] of cache){if(cache.size<=2)break;if(!pins.has(key)){cache.delete(key);disposeAsset(value.scene);}}}
export function cachedAsset(key,object){return cache.get(key)?.scene===object;}
export async function loadCharacter(key){
 if(cache.has(key)){const v=cache.get(key);cache.delete(key);cache.set(key,v);return v;}
 if(pending.has(key))return pending.get(key);
 const promise=loader.loadAsync('models/'+key+'.glb').then(gltf=>{gltf.scene.userData.motionClips=gltf.animations;cache.set(key,gltf);trimCache();return gltf;}).finally(()=>pending.delete(key));pending.set(key,promise);return promise;
}
const rects={dragon:[0,0,426,431],phoenix:[428,0,847,430],lion:[848,0,1274,431],pegasus:[0,431,428,826],spider:[429,431,845,826],bull:[846,431,1274,826],dice:[0,827,427,1234],unicorn:[428,827,846,1234],reaper:[847,827,1274,1234],runes:[428,0,847,430]};
export function configureCharacter(object,state={}){
 if(!object)return;
 const slots=state.tattoos||{back:'dragon',left:'runes',right:'runes'};
 object.traverse(o=>{
  if(o.name.startsWith('Tattoo_')){
   const slot=['back','left','right'].find(s=>o.name.startsWith('Tattoo_'+s+'_'));
   if(slot){const motif=slots[slot]||'none';o.visible=motif!=='none'&&(o.name.includes('_surface')||o.name.startsWith('Tattoo_'+slot+'_'+motif+'_'));if(o.name.includes('_surface')&&o.material){
    const rect=rects[motif]||rects.dragon,base=o.userData.atlas_uv_base,uv=o.geometry.attributes.uv;
    if(base&&uv&&o.userData._atlasMotif!==motif){
     if(!o.userData._normalizedUV){const original=new Float32Array(uv.array.length);for(let i=0;i<uv.count;i++){original[i*2]=(uv.getX(i)-base[0])/base[2];original[i*2+1]=(uv.getY(i)-base[1])/base[3];}o.userData._normalizedUV=original;}
     const original=o.userData._normalizedUV;for(let i=0;i<uv.count;i++)uv.setXY(i,rect[0]/1274+original[i*2]*(rect[2]-rect[0])/1274,1-rect[3]/1234+original[i*2+1]*(rect[3]-rect[1])/1234);uv.needsUpdate=true;o.userData._atlasMotif=motif;
    }
   }}
  }
  if(o.name.startsWith('Accessory_')){const name=o.name.replace(/\.\d+$/,'');o.visible=name==='Accessory_'+state.accessory||(name==='Accessory_cross_strap'&&state.accessory==='charm');}
  for(const mat of Array.isArray(o.material)?o.material:[o.material]){
   if(!mat)continue;
   if(mat.name.startsWith('Fur_')){mat.metalness=0;mat.roughness=.78;mat.normalScale?.set(.4,.4);}
   if(mat.name.startsWith('Tattoo_')){mat.emissiveIntensity=state.roaring?3:.15;mat.alphaTest=.3;mat.transparent=false;mat.depthWrite=true;mat.polygonOffset=true;mat.polygonOffsetFactor=-1;mat.polygonOffsetUnits=-1;}
  }
 });
}
export function engineInfo(){return {contexts:renderer?1:0,stage:active?.name||null,cacheKeys:[...cache.keys()],triangles:renderer?.info.render.triangles||0,drawCalls:renderer?.info.render.calls||0,textures:renderer?.info.memory.textures||0};}
window.rogueEngineInfo=engineInfo;
