'use strict';
sounds.roar = new Audio('media/roar.mp3');
const wolfBodyProfiles={basibozuk:{body:'Atletik • dar bel',width:1,height:1,color:'#91bac4'},kul:{body:'Çevik • ince bel • uzun uzuv',width:.85,height:1.03,color:'#b3a29b'},ayaz:{body:'Geniş omuz • yoğun yele',width:1.13,height:.98,color:'#80c5dc'},bilge:{body:'Uzun gövde • örgülü yele • kağan tasması',width:.94,height:1.12,color:'#d2b367'},kultigin:{body:'Kısa, kaslı omuz • dar bel • omuzluk',width:1.28,height:.94,color:'#db6977'},alparslan:{body:'Ağır göğüs • dar bel • bronz boyunluk',width:1.42,height:1.06,color:'#d5a565'},konuralp:{body:'İnce akıncı • uzun kollar • deri kayışlar',width:.82,height:1.09,color:'#77d3c6'}};
let wolfEquipment={skill:'none',run:false,roll:false,accessory:'none'};
const rollItems=[{id:'normal',title:'KURT TAKLASI',price:450,rarity:'STANDART',desc:'Yalnızca takla atmayı açar. Dört ayak koşu vermez; takla ek hasar vermez.'},{id:'legendary',title:'EFSANEVİ KURT TAKLASI',price:1200,rarity:'EFSANEVİ',desc:'Dört ayak üzerinde koşu ve taklayı birlikte açar. Standart takla ayrıca takılmaz.'}];
const ownedRollSkills=new Set();
try{const saved=JSON.parse(localStorage.getItem('rogue-roll-items'));if(Array.isArray(saved))for(const id of saved)if(['normal','legendary'].includes(id))ownedRollSkills.add(id);}catch(_){}
let wolfLoadouts={};
try{const saved=JSON.parse(localStorage.getItem('rogue-wolf-loadouts'));if(saved&&typeof saved==='object')wolfLoadouts=saved;}catch(_){}
let wolfTattoos={back:'dragon',left:'runes',right:'runes'};
function loadWolfLoadout(){const e=wolfLoadouts[collectionState.equipped];const skill=ownedRollSkills.has(e?.skill)?e.skill:'none';wolfEquipment={skill,run:skill==='legendary',roll:skill!=='none',accessory:['collar','shoulder','charm'].includes(e?.accessory)?e.accessory:'none'};wolfTattoos={back:['dragon','phoenix','lion','pegasus','spider','bull','dice','unicorn','reaper','none'].includes(e?.tattoos?.back)?e.tattoos.back:'dragon',left:['runes','dragon','phoenix','reaper','none'].includes(e?.tattoos?.left)?e.tattoos.left:'runes',right:['runes','dragon','phoenix','reaper','none'].includes(e?.tattoos?.right)?e.tattoos.right:'runes'};}
const ROAR_DURATION=20000;
let roarUntil=0,previewTimer;
function wolfStats(now=Date.now()){
 const c=roster.find(c=>c.id===collectionState.equipped);const active=now<roarUntil;const baseDamage=100+c.beast[0][1],baseDefense=100+c.beast[1][1];
 return {active,remaining:Math.max(0,roarUntil-now),speed:Math.min(180,100*(wolfEquipment.run?1.15:1)*(active?1.20:1)),damage:Math.min(180,baseDamage*(active?1.15:1)),defense:Math.min(180,baseDefense*(active?1.30:1))};
}
function openWolfEquipment(){loadWolfLoadout();screen('wolfGear');renderRollEquipment();$('wolfAccessory').value=wolfEquipment.accessory;renderWolfEquipment();$('tattooBack').value=wolfTattoos.back;$('tattooLeft').value=wolfTattoos.left;$('tattooRight').value=wolfTattoos.right;window.refreshWolf3D?.();}
$('openWolfGear').onclick=openWolfEquipment;
function renderWolfEquipment(){const c=roster.find(c=>c.id===collectionState.equipped),p=wolfBodyProfiles[c.id];$('wolfBodyName').textContent=p.body;$('wolfFigureName').textContent=c.wolf;$('wolfShape').style.transform=`translate(${120*(1-p.width)}px,${170*(1-p.height)}px) scale(${p.width},${p.height})`;$('wolfFigure').style.setProperty('--tattoo',p.color);const decorations={none:'',collar:'<path d="M91 108L120 120L149 108L146 124L120 137L94 124Z" fill="#9d8753"/><circle cx="120" cy="126" r="7" fill="#c9b26b"/>',shoulder:'<path d="M145 109L171 119L180 153L150 149Z" fill="#575f6b" stroke="#9b7475" stroke-width="3"/>',charm:'<path d="M95 110L137 182" stroke="#665445" stroke-width="5"/><path d="M130 166L146 171L141 194L128 186Z" fill="#c6b99b"/>'};$('accessoryDrawing').innerHTML=decorations[wolfEquipment.accessory];updateRoar();window.refreshWolf3D?.();}
$('wolfAccessory').onchange=e=>{wolfEquipment.accessory=e.target.value;renderWolfEquipment();};
$('saveWolfGear').onclick=()=>{try{wolfLoadouts[collectionState.equipped]={...wolfEquipment,tattoos:{...wolfTattoos}};localStorage.setItem('rogue-wolf-loadouts',JSON.stringify(wolfLoadouts));localStorage.setItem('rogue-wolf-equipment',JSON.stringify(wolfEquipment));toast('Kurt donanımı kaydedildi.');}catch(_){toast('Cihaz kaydı kullanılamıyor.');}};
$('runPreview').onclick=()=>window.playWolfMotion?.('WolfRunQuad');
$('rollPreview').onclick=()=>window.playWolfMotion?.('WolfRoll');
$('activateRoar').onclick=()=>{if(wolfStats().active)return;roarUntil=Date.now()+ROAR_DURATION;playSound('roar');updateRoar();};
window.getWolf3DState=()=>({character:collectionState.equipped,accessory:wolfEquipment.accessory,tattoos:wolfTattoos,roaring:wolfStats().active});
for(const [id,key] of [['tattooBack','back'],['tattooLeft','left'],['tattooRight','right']])$(id).onchange=e=>{wolfTattoos[key]=e.target.value;window.refreshWolf3D?.();};
$('viewWolfFront').onclick=()=>window.wolf3DView?.(true);$('viewWolfBack').onclick=()=>window.wolf3DView?.(false);
function updateRoar(){if(currentScreen!=='wolfGear')return;const s=wolfStats();window.refreshWolf3D?.();$('wolfFigure').classList.toggle('roaring',s.active);$('activateRoar').disabled=s.active;$('roarRemaining').textContent=s.active?(s.remaining/1000).toFixed(1)+' sn':'HAZIR';$('roarProgress').style.width=(s.remaining/ROAR_DURATION*100)+'%';$('wolfLiveStats').innerHTML=[['Hız',s.speed],['Hasar',s.damage],['Savunma',s.defense]].map(([name,value])=>`<div class="bonus-row"><span>${name}</span><strong>${value.toFixed(1)} / 180</strong></div>`).join('');$('roarStatus').textContent=s.active?'Kükreme etkin • dövmeler parlıyor.':'Kükreme kapalı • temel donanım değerleri.';}
setInterval(updateRoar,100);
const shopBlueprints={weapons:[['AR-01','Saldırı tüfeği'],['SR-01','Keskin nişancı tüfeği']],grenades:[['PARÇA-01','Parça tesirli el bombası'],['SİS-01','Duman bombası']],knives:[['KAMA-01','Yakın dövüş bıçağı']]};
window.renderCatalog=(key)=>{const items=shopBlueprints[key];$('collectionCount').textContent=items.length+' TASLAK';$('collectionCards').innerHTML=items.map(([name,type])=>`<div class="blueprint-item"><span>＋</span><strong>${name}</strong><p>${type}</p><small>MODEL VE OYNANIŞ EKLENECEK</small></div>`).join('');$('collectionDetail').innerHTML='<span class="eyebrow">KATALOG ALANI</span><h2>'+({weapons:'SİLAHLAR',grenades:'BOMBALAR',knives:'BIÇAKLAR'}[key])+'</h2><p>Bu kategorinin modelleri ve savaş özellikleri sonraki aşamada eklenecek. Şimdilik satın alınabilir eşya yok.</p>';};


function renderRollEquipment(){
 const select=$('equipRollTier');for(const option of select.options)option.disabled=option.value!=='none'&&!ownedRollSkills.has(option.value);
 select.value=wolfEquipment.skill||'none';
 $('rollTierInfo').textContent=wolfEquipment.skill==='legendary'?'Efsanevi takılı: dört ayak koşu ve takla açık.':wolfEquipment.skill==='normal'?'Standart takla takılı: yalnızca takla açık.':'Özelliği mağazadan alıp bu yuvaya tak.';
 $('runPreview').disabled=!wolfEquipment.run;$('rollPreview').disabled=!wolfEquipment.roll;
 window.checkWolfMotionAccess?.();
}
$('equipRollTier').onchange=e=>{const skill=e.target.value;if(skill!=='none'&&!ownedRollSkills.has(skill)){renderRollEquipment();return;}wolfEquipment.skill=skill;wolfEquipment.run=skill==='legendary';wolfEquipment.roll=skill!=='none';renderRollEquipment();updateRoar();};
window.getWolfMotionAccess=()=>({roll:wolfEquipment.roll&&ownedRollSkills.has(wolfEquipment.skill),run:wolfEquipment.run&&wolfEquipment.skill==='legendary'&&ownedRollSkills.has('legendary')});
function openRollShop(){category='skills';window.openCollection('shop');}
$('openRollShop').onclick=openRollShop;
window.renderRollShop=()=>{
 const list=libraryMode==='shop'?rollItems:rollItems.filter(item=>ownedRollSkills.has(item.id));
 $('collectionCount').textContent=list.length+' ÖZELLİK';
 $('collectionCards').innerHTML=list.length?list.map(item=>`<article class="roll-item ${item.id}"><span>${item.rarity}</span><div class="roll-symbol">${item.id==='legendary'?'◈':'↻'}</div><h3>${item.title}</h3><p>${item.desc}</p><strong>${ownedRollSkills.has(item.id)?'ENVANTERDE':item.price+' DENEME KREDİSİ'}</strong><button class="primary" data-buy-roll="${item.id}" ${ownedRollSkills.has(item.id)?'disabled':''}>${ownedRollSkills.has(item.id)?'ALINDI':'SATIN AL'} →</button></article>`).join(''):'<div class="empty-collection"><h3>KURT ÖZELLİĞİ YOK</h3><p>Standart veya efsanevi taklayı mağazadan alabilirsin.</p></div>';
 $('collectionDetail').innerHTML='<span class="eyebrow">KUŞANMA KURALI</span><h2>TEK TAKLA YUVASI</h2><p><strong>Standart:</strong> yalnızca takla.</p><p><strong>Efsanevi:</strong> dört ayak koşu + takla.</p><p>Önce satın al, sonra seçili kurdun takla yuvasına tak. İki özellik aynı anda üst üste eklenmez.</p><button id="goWolfEquip" class="primary">KURDA TAK →</button><p class="collection-note">Deneme kredisi kullanılır. Gerçek ödeme yapılmaz.</p>';
 $('goWolfEquip').onclick=openWolfEquipment;
 document.querySelectorAll('[data-buy-roll]').forEach(button=>button.onclick=()=>{const item=rollItems.find(item=>item.id===button.dataset.buyRoll);if(ownedRollSkills.has(item.id))return;if(collectionState.credits<item.price){toast('Deneme kredisi yetersiz.');return;}collectionState.credits-=item.price;ownedRollSkills.add(item.id);saveCollection();try{localStorage.setItem('rogue-roll-items',JSON.stringify([...ownedRollSkills]));}catch(_){toast('Özellik bu oturumda alındı; cihaz kaydı başarısız.');}renderCollection();toast(item.title+' envantere eklendi. Kurda takmayı unutma.');});
};

window.getArenaConfig=(id,trial='equipped')=>{
 const c=roster.find(c=>c.id===id)||roster[0],e=wolfLoadouts[c.id]||{};
 const skill=trial==='equipped'?(ownedRollSkills.has(e.skill)?e.skill:'none'):trial;
 return {id:c.id,name:c.name,wolf:c.wolf,power:c.power,damage:100+c.beast[0][1],defense:100+c.beast[1][1],accessory:e.accessory||'none',tattoos:e.tattoos||{back:'dragon',left:'runes',right:'runes'},run:skill==='legendary',roll:['normal','legendary'].includes(skill),trial:trial!=='equipped'};
};
window.saveInventoryTattoo=(id,slot,motif)=>{
 if(!collectionState.owned.includes(id)||!['back','left','right'].includes(slot))return false;
 const old=wolfLoadouts[id]||{};const tattoos={back:'dragon',left:'runes',right:'runes',...old.tattoos,[slot]:motif};wolfLoadouts[id]={...old,tattoos};
 try{localStorage.setItem('rogue-wolf-loadouts',JSON.stringify(wolfLoadouts));}catch(_){toast('Cihaz kaydı kullanılamıyor.');}
 if(id===collectionState.equipped)loadWolfLoadout();window.refreshWolf3D?.();toast(motif==='none'?'Dövme bırakıldı.':'Dövme kuşanıldı.');return true;
};
