// Shared model contracts: character identity and wardrobe are independent of rig type.
import {AnimationClip,Vector3} from 'three';
import {normalizedBoneName} from './rig-bones.js';
export const MODEL_TYPES=Object.freeze({behamah40:{bones:40,roar:'T_cry'},ice40:{bones:40,roar:'T_CRY'},power42:{bones:42,roar:'T_CRY'},r1_54:{bones:54,roar:'T_CRY'},wraith58:{bones:58,roar:'T_CRY'},human47:{bones:47}});
export const nativeModel=actor=>!!(actor?.userData.nativeSourceKeyPreserved&&MODEL_TYPES[actor.userData.modelType]);
const wolf={WolfClaw:['LSt','UMFi1','upper'],WolfIdle:['LSt','UMSt'],WolfMove:['LWF','UMWF'],WolfWalk:['LWF','UMWF'],WolfRunQuad:['LRF','UMRF'],WolfRoar:['T_CRY'],WolfRoll:['T_Specialatk'],WolfClawRight:['LSt','UMFi1','upper'],WolfClawLeft:['LSt','UMFi2','upper'],WolfJump:['LJJ','UMJJ'],WolfJumpAir:['LJT','UMJT'],WolfLand:['LJL','UMJL'],WolfTransform:['LSt','UMSt']};
const human={HumanIdle:['UI_Default_Idle'],HumanMove:['LWF','URi1WF'],HumanWalk:['LWF','URi1WF'],HumanRun:['LRF','URi1RF'],HumanFire:['URi1Fi'],HumanReload:['URi1Re']};
const trackBone=track=>normalizedBoneName(track.name.slice(0,track.name.lastIndexOf('.')).replace(/^.*\[([^\]]+)\]$/,'$1'));
export function motionClip(actor,role){
 const clips=actor?.userData.motionClips||[];if(role==='WolfRunQuad'){const chosen=actor?.userData.nativeLocomotion?.quadClip;const quad=clips.find(c=>c.name===(chosen||'DerivedQuadRun'));if(quad){const cache=actor.userData.nativeRoleCache||(actor.userData.nativeRoleCache=new Map());if(!cache.has('WolfRunQuad'))cache.set('WolfRunQuad',new AnimationClip('WolfRunQuad',quad.duration,quad.tracks));return cache.get('WolfRunQuad');}}if(!nativeModel(actor))return clips.find(c=>c.name===role)||clips.find(c=>c.name==='WolfIdle'||c.name==='HumanIdle');
 const cache=actor.userData.nativeRoleCache||(actor.userData.nativeRoleCache=new Map());if(cache.has(role))return cache.get(role);
 const recipe=actor.userData.nativeRoleRecipes?.[role]||(actor.userData.modelType==='human47'?human:wolf)[role];if(!recipe)return clips.find(c=>c.name===role)||null;
 const base=clips.find(c=>c.name===recipe[0]),upper=clips.find(c=>c.name===recipe[1]);if(!base)return null;
 let tracks=base.tracks,duration=base.duration;
 if(upper){const mask=new Set((actor.userData.nativeUpperBoneNames||[]).map(normalizedBoneName));tracks=[...base.tracks.filter(t=>!mask.has(trackBone(t))),...upper.tracks.filter(t=>mask.has(trackBone(t)))];duration=recipe[2]==='upper'?upper.duration:Math.max(base.duration,upper.duration);}
 // Track times/values are referenced unchanged: only native upper/lower selection.
 const clip=new AnimationClip(role,duration,tracks);cache.set(role,clip);return clip;
}
export function nativeRoar(actor){const clip=motionClip(actor,'WolfRoar');const duration=clip?.duration||1.2;const events=actor?.userData.nativeClipEvents?.[actor?.userData.nativeRoleRecipes?.WolfRoar?.[0]||MODEL_TYPES[actor?.userData.modelType]?.roar||'T_CRY']||[];const event=events.find(e=>/create_attachfx|FX ChangeCharEffect/i.test(e.event));return {modelType:actor?.userData.modelType||'legacy27',clip:clip?.name,duration,eventTime:event?event.timeMs/1000:null,peakPhase:event?Math.min(.95,Math.max(.05,event.timeMs/1000/duration)):.49};}
export function motionDuration(actor,role,fallback){return motionClip(actor,role)?.duration||fallback;}
// Correct only measured mesh penetration; retain the source gait's aerial phases.
export function placeNativeLocomotion(actor,role,clipTime){
 const samples=actor?.userData.nativeLocomotionClearance?.[role];if(!samples?.length)return;
 let i=1;while(i<samples.length-1&&samples[i][0]<clipTime)i++;
 const a=samples[i-1],b=samples[i],u=Math.max(0,Math.min(1,(clipTime-a[0])/Math.max(.0001,b[0]-a[0])));actor.position.y+=a[1]+(b[1]-a[1])*u;actor.updateMatrixWorld(true);
}
// Physics owns travel; compensate embedded horizontal motion without editing tracks.
export function placeNativeRoll(actor,clipTime){
 if(!nativeModel(actor))return;
 const base=actor.userData.nativeClipRootStarts?.T_Specialatk;
 const samples=actor.userData.nativeRollClearance;
 if(!base||!samples?.length)return;
 let root;actor.traverse(o=>{if(o.isBone&&normalizedBoneName(o.name)==='bip01')root=o;});
 if(!root)return;
 actor.updateMatrixWorld(true);const p=root.getWorldPosition(actor.position.clone());actor.worldToLocal(p);p.x-=base[0];p.y=0;p.z-=base[2];p.applyQuaternion(actor.quaternion);actor.position.sub(p);
 let i=1;while(i<samples.length-1&&samples[i][0]<clipTime)i++;
 const a=samples[i-1],b=samples[i],u=Math.max(0,Math.min(1,(clipTime-a[0])/Math.max(.0001,b[0]-a[0])));actor.position.y+=a[1]+(b[1]-a[1])*u;actor.updateMatrixWorld(true);
}

// A small set of actual body vertices follows the blended pose. Clip-only floor
// curves cannot cover the intermediate pose when two animations cross-fade.
const supportDirections=[new Vector3(1,0,0),new Vector3(-1,0,0),new Vector3(0,1,0),new Vector3(0,-1,0),new Vector3(0,0,1),new Vector3(0,0,-1),...[-1,1].flatMap(x=>[-1,1].flatMap(y=>[-1,1].map(z=>new Vector3(x,y,z))))];
const supportPoint=new Vector3(),supportCache=new WeakMap();
function contactProbes(actor){
 const meshes=[];actor.traverse(mesh=>{if(!mesh.isSkinnedMesh||!mesh.name.startsWith('Body'))return;const p=mesh.geometry.attributes.position,si=mesh.geometry.attributes.skinIndex,sw=mesh.geometry.attributes.skinWeight,buckets=new Map();
  for(let i=0;i<p.count;i++){let dominant=0;for(let j=1;j<4;j++)if(sw.array[i*4+j]>sw.array[i*4+dominant])dominant=j;const bone=si.array[i*4+dominant];let extremes=buckets.get(bone);if(!extremes){extremes=supportDirections.map(()=>({value:-Infinity,index:0}));buckets.set(bone,extremes);}supportPoint.fromBufferAttribute(p,i);for(let j=0;j<supportDirections.length;j++){const value=supportPoint.dot(supportDirections[j]);if(value>extremes[j].value)extremes[j]={value,index:i};}}
  meshes.push({mesh,indices:[...new Set([...buckets.values()].flatMap(values=>values.map(v=>v.index)))]});
 });actor.userData.groundContactProbeCount=meshes.reduce((sum,p)=>sum+p.indices.length,0);return meshes;
}
export function keepNativeBodyAboveGround(actor,groundY=0){
 if(!nativeModel(actor))return 0;let probes=supportCache.get(actor);if(!probes){probes=contactProbes(actor);supportCache.set(actor,probes);}actor.updateMatrixWorld(true);let floor=Infinity;
 for(const {mesh,indices} of probes){if(!mesh.visible)continue;for(const i of indices){supportPoint.fromBufferAttribute(mesh.geometry.attributes.position,i);mesh.applyBoneTransform(i,supportPoint).applyMatrix4(mesh.matrixWorld);floor=Math.min(floor,supportPoint.y);}}
 const correction=Number.isFinite(floor)?Math.max(0,groundY+.008-floor):0;if(correction>0){actor.position.y+=correction;actor.updateMatrixWorld(true);}return correction;
}
