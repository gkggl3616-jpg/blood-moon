'use strict';
sounds.roar=new Audio('media/roar.mp3');
const ROAR_DURATION=20000;let roarUntil=0,roarCooldownUntil=0;
const wolfBodyProfiles=Object.fromEntries(roster.map(c=>[c.id,{body:c.body,width:1,height:1,color:c.color}]));
let wolfEquipment={},wolfTattoos={};
const ownedRollSkills=new Set();
function loadWolfLoadout(){const e=RogueGear.current(collectionState.equipped);wolfEquipment={skill:e.skill?.replace('skill-','')||'none',run:e.skill==='skill-legendary',roll:!!e.skill,accessory:RogueGear.items[e.accessory]?.accessory||'none'};wolfTattoos=Object.fromEntries(['back','left','right'].map(s=>[s,RogueGear.items[e[s]]?.motif||'none']));for(const i of RogueGear.catalog.filter(i=>i.type==='skill'&&RogueGear.owns(i.id)))ownedRollSkills.add(i.id.replace('skill-',''));}
function wolfStats(now=Date.now()){const active=now<roarUntil;return {active,remaining:Math.max(0,roarUntil-now),...RogueGear.stats(collectionState.equipped,'wolf',active).values};}
window.getArenaStats=(id,form='wolf',roaring=false)=>RogueGear.stats(id,form,roaring);
window.getArenaConfig=(id,trial='equipped')=>{
 const c=roster.find(c=>c.id===id)||roster[0],e=RogueGear.current(c.id),s=RogueGear.stats(c.id).values;
 const skill=trial==='equipped'?(e.skill?.replace('skill-','')||'none'):trial;
 return {id:c.id,name:c.name,wolf:c.wolf,power:c.power,...s,accessory:RogueGear.items[e.accessory]?.accessory||'none',tattoos:Object.fromEntries(['back','left','right'].map(slot=>[slot,RogueGear.items[e[slot]]?.motif||'none'])),claw:RogueGear.items[e.claw]?.profile||'standard',humanLoadout:RogueGear.current(c.id,'human'),run:skill==='legendary',roll:['normal','legendary'].includes(skill),trial:trial!=='equipped'};
};
window.saveInventoryTattoo=(id,slot,motif)=>{const result=RogueGear.equip(id,'wolf',slot,motif==='none'?null:`tattoo-${motif}-${slot}`);toast(result.message);window.refreshWolf3D?.();return result.ok;};
window.getWolf3DState=()=>({...window.getArenaConfig(collectionState.equipped),character:collectionState.equipped,roaring:wolfStats().active});
window.getWolfMotionAccess=()=>{const skill=RogueGear.current(collectionState.equipped).skill;return {roll:['skill-normal','skill-legendary'].includes(skill)&&RogueGear.owns(skill),run:skill==='skill-legendary'&&RogueGear.owns(skill)};};
function renderRollEquipment(){loadWolfLoadout();for(const o of $('equipRollTier').options)o.disabled=o.value!=='none'&&!RogueGear.owns('skill-'+o.value);$('equipRollTier').value=wolfEquipment.skill;$('runPreview').disabled=!wolfEquipment.run;$('rollPreview').disabled=!wolfEquipment.roll;$('rollTierInfo').textContent=wolfEquipment.run?'Efsanevi: dört ayak koşu + temas hasarlı takla.':wolfEquipment.roll?'Standart: kısa ve temas hasarlı takla.':'Takla özelliğini envanterden bu kurda kuşan.';window.checkWolfMotionAccess?.();}
function renderWolfEquipment(){loadWolfLoadout();const c=roster.find(c=>c.id===collectionState.equipped);$('wolfBodyName').textContent=c.body;$('wolfFigureName').textContent=c.wolf;$('wolfShape').style.transform='';$('wolfFigure').style.setProperty('--tattoo',c.color);$('wolfAccessory').value=wolfEquipment.accessory;for(const [node,slot] of [['tattooBack','back'],['tattooLeft','left'],['tattooRight','right']]){const select=$(node);select.innerHTML='<option value="none">Dövme yok</option>'+RogueGear.catalog.filter(i=>i.type==='tattoo'&&i.slot===slot&&RogueGear.owns(i.id)).map(i=>`<option value="${i.motif}">${i.name}</option>`).join('');select.value=wolfTattoos[slot];}for(const o of $('wolfAccessory').options)o.disabled=o.value!=='none'&&!RogueGear.owns('accessory-'+o.value);updateRoar();window.refreshWolf3D?.();}
function openWolfEquipment(){screen('wolfGear');renderRollEquipment();renderWolfEquipment();}
$('openWolfGear').onclick=openWolfEquipment;
$('equipRollTier').onchange=e=>{toast(RogueGear.equip(collectionState.equipped,'wolf','skill',e.target.value==='none'?null:'skill-'+e.target.value).message);renderRollEquipment();updateRoar();};
$('wolfAccessory').onchange=e=>{toast(RogueGear.equip(collectionState.equipped,'wolf','accessory',e.target.value==='none'?null:'accessory-'+e.target.value).message);renderWolfEquipment();};
for(const [node,slot] of [['tattooBack','back'],['tattooLeft','left'],['tattooRight','right']])$(node).onchange=e=>{window.saveInventoryTattoo(collectionState.equipped,slot,e.target.value);updateRoar();};
$('saveWolfGear').onclick=()=>{RogueGear.save();loadWolfLoadout();try{localStorage.setItem('rogue-wolf-equipment',JSON.stringify(wolfEquipment));}catch(_){}toast('Donanım kaydedildi.');};
$('runPreview').onclick=()=>window.playWolfMotion?.('WolfRunQuad');$('rollPreview').onclick=()=>window.playWolfMotion?.('WolfRoll');
$('activateRoar').onclick=()=>{if(Date.now()<roarCooldownUntil)return;roarCooldownUntil=Date.now()+3000;roarUntil=Date.now()+ROAR_DURATION;playSound('roar');window.playWolfMotion?.('WolfRoar');updateRoar();};
$('viewWolfFront').onclick=()=>window.wolf3DView?.(true);$('viewWolfBack').onclick=()=>window.wolf3DView?.(false);
function updateRoar(){if(currentScreen!=='wolfGear')return;const s=wolfStats();window.refreshWolf3D?.();$('wolfFigure').classList.toggle('roaring',s.active);$('activateRoar').disabled=Date.now()<roarCooldownUntil;$('roarRemaining').textContent=s.active?(s.remaining/1000).toFixed(1)+' sn':'HAZIR';$('roarProgress').style.width=s.remaining/ROAR_DURATION*100+'%';$('wolfLiveStats').innerHTML=[['Hız',s.speed],['Hasar',s.damage],['Savunma',s.defense],['Can',s.health]].map(([n,v])=>`<div class="bonus-row"><span>${n}</span><strong>${v.toFixed(1)}</strong></div>`).join('');$('roarStatus').textContent='Temel + karakter + dövme; kükreme etkinse ayrıca çarpılır. Genel 180 tavanı yok.';}
setInterval(updateRoar,100);
$('openRollShop').onclick=()=>{category='skills';window.openCollection('shop');};
window.addEventListener('rogue-gear-changed',()=>{if(currentScreen==='wolfGear'){renderRollEquipment();renderWolfEquipment();}});
