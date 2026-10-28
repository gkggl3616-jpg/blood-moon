// One timing/stride contract for inventory previews and actual movement.
export function motionProfile(actor){
 if(actor?.userData.motionProfile)return actor.userData.motionProfile;
 let data;actor?.traverse(o=>{if(o.userData.run_stride_m||o.userData.walk_stride_m)data=o.userData;});
 const clips=actor?.userData.motionClips||[];
 const walk=clips.find(c=>c.name==='WolfWalk'||c.name==='HumanWalk')||clips.find(c=>c.name==='WolfMove'||c.name==='HumanMove');
 const walkStride=data?.walk_stride_m||((walk?.name==='WolfMove'||walk?.name==='HumanMove')?walk.duration*3.6:null);
 const profile={walkClip:walk?.name||'WolfMove',walkDuration:walk?.duration||0,walkStride,walkCalibrated:!!data?.walk_stride_m,runDuration:clips.find(c=>c.name==='WolfRunQuad')?.duration||16/30,runStride:data?.run_stride_m||8*16/30,runSpeed:data?.run_reference_speed_mps||8,roarDuration:clips.find(c=>c.name==='WolfRoar')?.duration||1.2,roarPeak:.49};
 if(actor)actor.userData.motionProfile=profile;return profile;
}
export function walkRate(actor,metersPerSecond){const p=motionProfile(actor);return p.walkStride>0?Math.max(0,metersPerSecond)*p.walkDuration/p.walkStride:1;}
export function runRate(actor,metersPerSecond){const p=motionProfile(actor);return metersPerSecond*p.runDuration/p.runStride;}

export function motionJoints(actor){
 if(!actor)return {};actor.updateMatrixWorld(true);const result={};
 for(const name of ['Head','HandL','HandR','FootL','FootR','UpperArmL','UpperArmR','ForearmL','ForearmR']){const b=actor.getObjectByName(name);if(b){const e=b.matrixWorld.elements;result[name]=[e[12],e[13],e[14]];}}return result;
}
