import assert from 'node:assert/strict';
import {ClawCombo,armSide,ensureClawClips} from './viewer/claw-combo.js';
const combo=new ClawCombo();assert.equal(combo.next,'right');assert.deepEqual([combo.accept(),combo.accept(),combo.accept()],['right','left','right']);assert.equal(combo.count,3);combo.reset();assert.equal(combo.accept(),'right');
for(const [name,side] of [['HandL.quaternion','left'],['ForearmR.position','right'],['DEF-upper_armR.quaternion','right'],['Chest.quaternion',null],['FootL.position',null]])assert.equal(armSide(name),side);
const base={name:'WolfClaw',tracks:['Chest.quaternion','UpperArmR.quaternion','HandR.quaternion','UpperArmL.quaternion','HandL.quaternion'].map(name=>({name})),clone(){return {...this,tracks:[...this.tracks]};}};
const actor={userData:{motionClips:[base]}};assert(ensureClawClips(actor));assert(ensureClawClips(actor));assert.equal(actor.userData.motionClips.length,3);
for(const [name,side] of [['WolfClawRight','right'],['WolfClawLeft','left']]){const clip=actor.userData.motionClips.find(c=>c.name===name);assert(clip.tracks.some(t=>armSide(t.name)===side));assert(clip.tracks.every(t=>!armSide(t.name)||armSide(t.name)===side));}
assert.equal(ensureClawClips({userData:{motionClips:[]}}),false);console.log('Claw alternation and one-arm clip masks PASS');
