'use strict';
let powerFilter='all',selectedPower=null;
const tattooNames={dragon:'Ejder',phoenix:'Anka',lion:'Aslan',pegasus:'Kanatlı At',spider:'Örümcek',bull:'Boğa',dice:'Kader Zarı',unicorn:'Tekboynuz',reaper:'Ölüm'};
const tattooTiles={dragon:[0,0],phoenix:[1,0],lion:[2,0],pegasus:[0,1],spider:[1,1],bull:[2,1],dice:[0,2],unicorn:[1,2],reaper:[2,2]};
const tattooItems=Object.keys(tattooNames).flatMap(motif=>(['dragon','phoenix','reaper'].includes(motif)?['back','left','right']:['back']).map(slot=>({id:motif+'-'+slot,motif,slot,title:tattooNames[motif]+' Dövmesi ('+({back:'Sırt',left:'Sol',right:'Sağ'}[slot])+')'})));
function tileStyle(motif){const [x,y]=tattooTiles[motif]||[0,0];return 'background-position:'+x*50+'% '+y*50+'%';}
function isTattooEquipped(item){return window.getArenaConfig(selectedCharacter,'equipped').tattoos[item.slot]===item.motif;}
function renderPowerDetail(item){
 if(item.type==='claw'){
  const c=roster.find(c=>c.id===item.character);$('collectionDetail').innerHTML=`<div class="detail-art"><img src="media/characters/${item.character}-wolf.webp" alt="${c.wolf}"></div><div class="detail-copy"><span class="eyebrow">KARAKTERİN İMZA PENÇESİ</span><h2>${item.title}</h2><div class="detail-scroll"><p>${c.claw}</p><p>${c.trail}</p><p>Koşu ve takla tüm kurtlarda ortaktır. Pençe hareketi ve ışık izi gövdeye göre değişir.</p></div><button id="tryClaw" class="primary">TEST ALANINDA DENE →</button></div>`;
  $('tryClaw').onclick=()=>{$('arenaCharacter').value=item.character;window.openArena?.();};return;
 }
 const equipped=isTattooEquipped(item);
 $('collectionDetail').innerHTML=`<div class="detail-art"><span class="tattoo-thumb" style="${tileStyle(item.motif)}"></span><small>${item.title}</small></div><div class="detail-copy"><span class="eyebrow">AÇIKLAMA / ÖZELLİK</span><h2>${item.title}</h2><div class="detail-scroll"><p>Kurtlar için ${item.slot==='back'?'sırt':item.slot==='left'?'sol kol':'sağ kol'} dövmesi. Kükremede parlar.</p><p>Kozmetik eşya; ek güç veya hasar vermez. Sürekli kullanım.</p><p>${equipped?'Seçili kurt üzerinde kullanılıyor.':'Bu yuvaya kuşanılabilir.'}</p></div><button id="equipTattooItem" class="primary">${equipped?'BIRAK':'KUŞAN'} →</button></div>`;
 $('equipTattooItem').onclick=()=>{if(!collectionState.owned.includes(selectedCharacter)){toast('Bu karakteri önce deneme envanterine ekle.');return;}window.saveInventoryTattoo(selectedCharacter,item.slot,equipped?'none':item.motif);renderCollection();};
}
const oldPowerRenderer=window.renderRollShop;
window.renderRollShop=()=>{
 oldPowerRenderer();
 const oldHTML=$('collectionCards').innerHTML;
 const tattoos=['all','tattoos'].includes(powerFilter)?tattooItems:[];
 const claws=['all','claws'].includes(powerFilter)?[{character:'bilge',title:'Buz Kıran Pençe'},{character:'kultigin',title:'Kızıl Çapraz'},{character:'alparslan',title:'Köz Vuruşu'},{character:'konuralp',title:'Gölge Yırtığı'}]:[];
 const rollHTML=['all','skills'].includes(powerFilter)&&oldHTML.includes('data-buy-roll')?oldHTML:'';
 $('collectionCards').innerHTML=tattoos.map(item=>`<button class="power-item ${selectedPower?.id===item.id?'active':''}" data-tattoo-item="${item.id}"><span class="tattoo-thumb" style="${tileStyle(item.motif)}"></span><strong>${item.title}</strong><small class="${isTattooEquipped(item)?'used':''}">${isTattooEquipped(item)?'Kullanılıyor':'Sürekli Kullanım'}</small></button>`).join('')+claws.map(item=>`<button class="power-item" data-claw-item="${item.character}"><img src="media/characters/${item.character}-wolf.webp" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 24%;opacity:.45"><strong>${item.title}</strong><small>Karaktere özel iz</small></button>`).join('')+rollHTML;
 $('collectionCount').textContent=$('collectionCards').children.length+' EŞYA';
 if(!$('collectionCards').children.length)$('collectionCards').innerHTML='<div class="empty-collection"><h3>BU FİLTREDE EŞYA YOK</h3><p>Mağazaya geçerek takla özelliklerini alabilirsin.</p></div>';
 document.querySelectorAll('[data-tattoo-item]').forEach(b=>b.onclick=()=>{selectedPower=tattooItems.find(x=>x.id===b.dataset.tattooItem);renderCollection();});
 document.querySelectorAll('[data-claw-item]').forEach(b=>b.onclick=()=>{selectedPower={type:'claw',id:b.dataset.clawItem,character:b.dataset.clawItem,title:claws.find(x=>x.character===b.dataset.clawItem).title};renderPowerDetail(selectedPower);});
 // The original shop renderer owns purchase actions; restore them after grid composition.
 document.querySelectorAll('[data-buy-roll]').forEach(button=>button.onclick=()=>{const item=rollItems.find(item=>item.id===button.dataset.buyRoll);if(ownedRollSkills.has(item.id))return;if(collectionState.credits<item.price){toast('Deneme kredisi yetersiz.');return;}collectionState.credits-=item.price;ownedRollSkills.add(item.id);saveCollection();try{localStorage.setItem('rogue-roll-items',JSON.stringify([...ownedRollSkills]));}catch(_){toast('Cihaz kaydı kullanılamıyor.');}renderCollection();toast(item.title+' envantere eklendi. Kurda takmayı unutma.');});
 if(selectedPower)renderPowerDetail(selectedPower);
 else{
  $('collectionDetail').innerHTML='<div class="detail-art"><span class="tattoo-thumb" style="background-position:0 0"></span></div><div class="detail-copy"><span class="eyebrow">DONANIM BİLGİSİ</span><h2>KURT ÖZELLİKLERİ</h2><div class="detail-scroll"><p>Dövme ve pençeleri incelemek için eşya seç.</p><p>Standart takla: yalnızca takla. Efsanevi: dört ayak koşu ve takla.</p><p>Önce satın al, sonra seçili kurdun tek takla yuvasına tak. Gerçek ödeme yapılmaz.</p></div><button id="goWolfEquip" class="primary">KURDA TAK →</button></div>';$('goWolfEquip').onclick=openWolfEquipment;
 }
 updateInventoryCharacter();
};
for(const button of document.querySelectorAll('[data-power-filter]'))button.onclick=()=>{powerFilter=button.dataset.powerFilter;selectedPower=null;category='skills';document.querySelectorAll('[data-power-filter]').forEach(b=>b.classList.toggle('active',b===button));renderCollection();};
