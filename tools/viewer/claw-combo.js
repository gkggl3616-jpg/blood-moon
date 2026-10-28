// Alternation advances only when a strike is accepted, never on a blocked input.
export class ClawCombo {
 constructor(){this.reset();}
 reset(){this.next='right';this.last=null;this.count=0;}
 accept(){const side=this.next;this.last=side;this.next=side==='right'?'left':'right';this.count++;return side;}
}
export function armSide(trackName){
 const bone=trackName.slice(0,trackName.lastIndexOf('.')).replace(/[^a-z0-9]/gi,'').toLowerCase();
 if(!/(clavicle|shoulder|upperarm|forearm|hand|digits|digit|thumb)/.test(bone))return null;
 if(/(right|r)$/.test(bone))return 'right';if(/(left|l)$/.test(bone))return 'left';return null;
}
// Keep authored side-specific clips. Existing bilateral legacy clips get an arm
// mask; this is a compatibility step, not a claim of newly polished animation.
export function ensureClawClips(actor){
 const clips=actor?.userData.motionClips;if(!clips)return false;
 if(['WolfClawRight','WolfClawLeft'].every(n=>clips.some(c=>c.name===n)))return true;
 const base=clips.find(c=>c.name==='WolfClaw');if(!base)return false;
 if(!['left','right'].every(side=>base.tracks.some(t=>armSide(t.name)===side)))return false;
 for(const side of ['right','left']){
  const name=side==='right'?'WolfClawRight':'WolfClawLeft';if(clips.some(c=>c.name===name))continue;
  const clip=base.clone();clip.name=name;clip.tracks=clip.tracks.filter(t=>!armSide(t.name)||armSide(t.name)===side);clips.push(clip);
 }
 actor.userData.clawClipSource='legacy arm mask; authored side clips preferred';return true;
}
