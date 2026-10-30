'use strict';
const roster = [
 {id:'bilge',name:'BİLGE KAĞAN',wolf:'BOZ KAĞAN',role:'KOMUTAN',price:0,power:145,color:'#c3b17c',human:[['Dayanıklılık',3],['Hareket',-2]],beast:[['Hasar',45],['Dayanıklılık',45]],body:'Uzun ve geniş gövdeli',claw:'Gövde dönüşüyle ağır yatay darbe',trail:'Mat altın • üç geniş yatay yay',desc:'Göktürk hükümdarı Bilge Kağan’dan esinlenen kurgu komutan. Tarihî bir portre iddiası taşımaz.'}

];
let collectionState={credits:2500,owned:['bilge'],equipped:'bilge'};
try{const v=JSON.parse(localStorage.getItem('rogue-collection'));if(v){collectionState.credits=Number.isFinite(v.credits)?Math.max(0,v.credits):2500;collectionState.owned=roster.filter(c=>v.owned?.includes(c.id)).map(c=>c.id);if(!collectionState.owned.includes('bilge'))collectionState.owned.push('bilge');collectionState.equipped=collectionState.owned.includes(v.equipped)?v.equipped:'bilge';}}catch(_){}
let libraryMode='inventory',category='characters',selectedCharacter='bilge',previewForm='wolf';
function saveCollection(){try{localStorage.setItem('rogue-collection',JSON.stringify(collectionState));}catch(_){toast('Cihaz kaydı kullanılamıyor.');}}
function bonusRows(rows){return rows.map(([label,value])=>`<div class="bonus-row"><span>${label}</span><strong class="${value>0?'positive':value<0?'negative':''}">${value>0?'+':''}${Number(value.toFixed(1))}%</strong></div>`).join('');}
window.refreshCharacter=()=>{const c=roster.find(c=>c.id===collectionState.equipped);$('operatorName').textContent=gearForm==='human'?c.name:c.wolf;$('operatorRole').textContent=c.role+' • Temsilî görsel';$('gearRole').textContent=c.role;$('operatorPortrait').style.backgroundImage='url(media/characters/'+characterModelId(c.id)+'-'+gearForm+'.webp)';$('operatorPortrait').style.backgroundSize='contain';$('operatorPortrait').style.backgroundPosition='center';};
window.openCollection=(mode='inventory')=>{libraryMode=mode;selectedCharacter=collectionState.equipped;screen('collection');renderCollection();};
function renderCollection(){}
function renderCharacter(){const c=roster.find(c=>c.id===selectedCharacter);const owned=collectionState.owned.includes(c.id);
 $('collectionDetail').innerHTML=`<div class="detail-art"><img src="media/characters/${characterModelId(c.id)}-${previewForm}.webp" alt="${c.name} tasarım referansı"><small>TASARIM REFERANSI</small></div><div class="detail-copy"><span class="eyebrow">${c.role} / ${previewForm==='human'?'İNSAN':'KURT'}</span><h2>${previewForm==='human'?c.name:c.wolf}</h2><div class="detail-scroll"><p>${c.desc}</p>${bonusRows(previewForm==='human'?c.human:c.beast)}<div class="signature-details"><strong>KARAKTER GÜCÜ ${c.power}</strong><p>${c.body} · ${c.claw}<br>İz: ${c.trail}</p><small>İz sürme korunur. Sıçrama düz ileriye; yerde alan göstergesi yok.</small></div><p class="balance-note">Karakter pasifi ve kuşanılan dövme bonusları ayrı hesaplanır. Koşu ve takla bütün kurtlarda aynı şablondadır.</p></div><button class="primary" id="characterAction">${owned?(collectionState.equipped===c.id?'SEÇİLİ KARAKTER':'TEÇHİZATA SEÇ'):c.price+' KREDİYLE DENE'} →</button></div>`;
 $('characterAction').onclick=()=>{playSound();if(!owned){if(collectionState.credits<c.price){toast('Deneme kredisi yetersiz.');return;}collectionState.credits-=c.price;collectionState.owned.push(c.id);toast(c.name+' deneme envanterine eklendi.');}else{collectionState.equipped=c.id;toast(c.name+' teçhizata seçildi.');}saveCollection();renderGear();renderCollection();};
 updateInventoryCharacter();
}
function characterModelId(id){return 'bilge';}
window.rogueModelId=characterModelId;
function updateInventoryCharacter(){}
$('previewHuman').onclick=()=>{previewForm='human';renderCollection();};$('previewWolf').onclick=()=>{previewForm='wolf';renderCollection();};
$('inventoryBackView').onclick=()=>window.wolf3DView?.(false);
$('inventoryTestArea').onclick=()=>{$('arenaCharacter').value=selectedCharacter;window.openArena?.();};
$('inventoryMode').onclick=()=>{libraryMode='inventory';renderCollection();};$('shopMode').onclick=()=>{libraryMode='shop';renderCollection();};
for(const b of document.querySelectorAll('[data-category]'))b.onclick=()=>{playSound();category=b.dataset.category;renderCollection();};
$('openInventory').onclick=()=>window.openCollection();
renderGear();
