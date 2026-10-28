import assert from 'node:assert/strict';
import {motionProfile,walkRate,runRate} from './viewer/motion.js';
function close(a,b){assert(Math.abs(a-b)<1e-10,`${a} != ${b}`);}
function actor(clips,data={}){return {userData:{motionClips:clips},traverse(fn){fn({userData:data});}};}
const fresh=actor([{name:'WolfWalk',duration:.8},{name:'WolfRunQuad',duration:.5}],{walk_stride_m:1.2,run_stride_m:4,run_reference_speed_mps:8});assert.equal(motionProfile(fresh).walkClip,'WolfWalk');close(walkRate(fresh,1.5),1);close(walkRate(fresh,3),2);assert.equal(walkRate(fresh,0),0);assert.equal(runRate(fresh,8),1);
const old=actor([{name:'WolfMove',duration:20/30}]);assert.equal(motionProfile(old).walkClip,'WolfMove');assert.equal(motionProfile(old).walkCalibrated,false);assert(Math.abs(walkRate(old,4.3)-4.3/3.6)<1e-12);
const human=actor([{name:'HumanWalk',duration:1}],{walk_stride_m:1.4});assert.equal(motionProfile(human).walkClip,'HumanWalk');assert.equal(walkRate(human,1.4),1);console.log('Walk clip selection, stride calibration and legacy compatibility PASS');
