// Shared model contracts: character identity and wardrobe are independent of rig type.
import {AnimationClip} from 'three';
import {normalizedBoneName} from './rig-bones.js';
export const MODEL_TYPES=Object.freeze({ice40:{bones:40,roar:'T_CRY'},power42:{bones:42,roar:'T_CRY'},r1_54:{bones:54,roar:'T_CRY'},wraith58:{bones:58,roar:'T_CRY'},human47:{bones:47}});
export const nativeModel=actor=>!!(actor?.userData.nativeSourceKeyPreserved&&MODEL_TYPES[actor.userData.modelType]);
const wolf={WolfClaw:['LSt','UMFi1','upper'],WolfIdle:['LSt','UMSt'],WolfMove:['LWF','UMWF'],WolfWalk:['LWF','UMWF'],WolfRunQuad:['LRF','UMRF'],WolfRoar:['T_CRY'],WolfRoll:['T_Specialatk'],WolfClawRight:['LSt','UMFi1','upper'],WolfClawLeft:['LSt','UMFi2','upper'],WolfJump:['LJJ','UMJJ'],WolfJumpAir:['LJT','UMJT'],WolfLand:['LJL','UMJL'],WolfTransform:['LSt','UMSt']};
const human={HumanIdle:['UI_Default_Idle'],HumanMove:['LWF','URi1WF'],HumanWalk:['LWF','URi1WF'],HumanRun:['LRF','URi1RF'],HumanFire:['URi1Fi'],HumanReload:['URi1Re']};
const trackBone=track=>normalizedBoneName(track.name.slice(0,track.name.lastIndexOf('.')).replace(/^.*\[([^\]]+)\]$/,'$1'));
export function motionClip(actor,role){
 const clips=actor?.userData.motionClips||[];if(!nativeModel(actor))return clips.find(c=>c.name===role)||clips.find(c=>c.name==='WolfIdle'||c.name==='HumanIdle');
 const cache=actor.userData.nativeRoleCache||(actor.userData.nativeRoleCache=new Map());if(cache.has(role))return cache.get(role);
 const recipe=(actor.userData.modelType==='human47'?human:wolf)[role];if(!recipe)return clips.find(c=>c.name===role)||null;
 const base=clips.find(c=>c.name===recipe[0]),upper=clips.find(c=>c.name===recipe[1]);if(!base)return null;
 let tracks=base.tracks,duration=base.duration;
 if(upper){const mask=new Set((actor.userData.nativeUpperBoneNames||[]).map(normalizedBoneName));tracks=[...base.tracks.filter(t=>!mask.has(trackBone(t))),...upper.tracks.filter(t=>mask.has(trackBone(t)))];duration=recipe[2]==='upper'?upper.duration:Math.max(base.duration,upper.duration);}
 // Track times/values are referenced unchanged: only native upper/lower selection.
 const clip=new AnimationClip(role,duration,tracks);cache.set(role,clip);return clip;
}
export function nativeRoar(actor){const clip=motionClip(actor,'WolfRoar');const duration=clip?.duration||1.2;const events=actor?.userData.nativeClipEvents?.T_CRY||[];const event=events.find(e=>/create_attachfx|FX ChangeCharEffect/i.test(e.event));return {modelType:actor?.userData.modelType||'legacy27',clip:clip?.name,duration,eventTime:event?event.timeMs/1000:null,peakPhase:event?Math.min(.95,Math.max(.05,event.timeMs/1000/duration)):.49};}
export function motionDuration(actor,role,fallback){return motionClip(actor,role)?.duration||fallback;}
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
