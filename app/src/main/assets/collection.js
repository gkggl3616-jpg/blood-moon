'use strict';
const roster = [
 {id:'basibozuk',name:'BAŞIBOZUK',wolf:'GECE AVCISI',role:'DENGELİ',price:0,color:'#607d89',human:[['Hareket',0],['Şarjör değişimi',0]],beast:[['Hareket',0],['Dayanıklılık',0]],desc:'Dengeli başlangıç operatörü. Temel insan ve kurt değerleriyle oynanış referansı.'},
 {id:'kul',name:'KÜL',wolf:'KÜL PENÇESİ',role:'İZCİ',price:750,color:'#be8b72',human:[['Hareket',4],['Dayanıklılık',-3]],beast:[['Hareket',5],['Dayanıklılık',-4]],desc:'Çeviklik odaklı izci. Daha hızlı hareket karşılığında daha düşük dayanıklılık.'},
 {id:'ayaz',name:'AYAZ',wolf:'AYAZ MUHAFIZI',role:'SAVUNMA',price:1200,color:'#72a7b5',human:[['Dayanıklılık',5],['Hareket',-3]],beast:[['Dayanıklılık',6],['Hareket',-4]],desc:'Alan savunmasına odaklı ağır operatör. Dayanıklılık avantajı, hareket hızı bedeliyle dengelenir.'}
];
let collectionState={credits:2500,owned:['basibozuk'],equipped:'basibozuk'};
try{const v=JSON.parse(localStorage.getItem('rogue-collection'));if(v){collectionState.credits=Number.isFinite(v.credits)?Math.max(0,v.credits):2500;collectionState.owned=roster.filter(c=>v.owned?.includes(c.id)).map(c=>c.id);if(!collectionState.owned.includes('basibozuk'))collectionState.owned.push('basibozuk');collectionState.equipped=collectionState.owned.includes(v.equipped)?v.equipped:'basibozuk';}}catch(_){}
let libraryMode='inventory',category='characters',selectedCharacter='basibozuk',previewForm='human';
function saveCollection(){try{localStorage.setItem('rogue-collection',JSON.stringify(collectionState));}catch(_){toast('Cihaz kaydı kullanılamıyor.');}}
function bonusRows(rows){return rows.map(([label,value])=>`<div class="bonus-row"><span>${label}</span><strong class="${value>0?'positive':value<0?'negative':''}">${value>0?'+':''}${value}%</strong></div>`).join('');}
window.refreshCharacter=()=>{const c=roster.find(c=>c.id===collectionState.equipped);$('operatorName').textContent=gearForm==='human'?c.name:c.wolf;$('operatorRole').textContent=c.role+' • Temsilî görsel';$('gearRole').textContent=c.role;};
window.openCollection=(mode='inventory')=>{libraryMode=mode;screen('collection');renderCollection();};
function renderCollection(){
 $('collectionTitle').textContent=libraryMode==='shop'?'MAĞAZA':'ENVANTER';$('walletAmount').textContent=collectionState.credits.toLocaleString('tr');
 $('inventoryMode').classList.toggle('active',libraryMode==='inventory');$('shopMode').classList.toggle('active',libraryMode==='shop');
 document.querySelectorAll('[data-category]').forEach(b=>b.classList.toggle('active',b.dataset.category===category));
 const labels={characters:'KARAKTERLER',wolves:'KURT FORMLARI',equipment:'EKİPMAN',cosmetics:'GÖRÜNÜMLER'};
 $('categoryTitle').textContent=labels[category];
 const list=libraryMode==='shop'?roster:roster.filter(c=>collectionState.owned.includes(c.id));
 $('collectionCount').textContent=(['characters','wolves'].includes(category)?list.length:category==='cosmetics'?1:0)+' KAYIT';
 if(['characters','wolves'].includes(category)){
  if(!list.some(c=>c.id===selectedCharacter))selectedCharacter=list[0].id;
  $('collectionCards').innerHTML=list.map(c=>`<button class="character-card ${selectedCharacter===c.id?'active':''}" data-character="${c.id}" style="--character-color:${c.color}"><span class="character-mark">${category==='wolves'?'◈':c.name[0]}</span><small>${c.role}</small><strong>${category==='wolves'?c.wolf:c.name}</strong><span class="ownership">${collectionState.equipped===c.id?'SEÇİLİ':collectionState.owned.includes(c.id)?'ENVANTERDE':c.price+' DENEME KREDİSİ'}</span></button>`).join('');
  document.querySelectorAll('[data-character]').forEach(b=>b.addEventListener('click',()=>{playSound();selectedCharacter=b.dataset.character;renderCollection();}));renderCharacter();
 }else{
  $('collectionCards').innerHTML=category==='equipment'?'<div class="empty-collection"><b>＋</b><h3>EKİPMAN ALANI HAZIR</h3><p>Silahlar ve ekipman modelleri sonraki aşamada eklenecek.</p></div>':'<div class="cosmetic-card"><span>◈</span><h3>STANDART GÖRÜNÜM</h3><p>Başlangıç görünümü • Envanterde</p></div>';
  $('collectionDetail').innerHTML='<span class="eyebrow">KOLEKSİYON BİLGİSİ</span><h2>'+labels[category]+'</h2><p>Karakter ve kurt formunu teçhizat ekranından birlikte kullanabileceksin.</p><button class="primary" id="backToGear">TEÇHİZATA DÖN →</button>';$('backToGear').onclick=()=>screen('gear');
 }
}
function renderCharacter(){const c=roster.find(c=>c.id===selectedCharacter);const owned=collectionState.owned.includes(c.id);
 $('collectionDetail').innerHTML=`<span class="eyebrow">${c.role} / KARAKTER DETAYI</span><h2>${previewForm==='human'?c.name:c.wolf}</h2><div class="collection-form"><button id="previewHuman" class="${previewForm==='human'?'active':''}">İNSAN</button><button id="previewWolf" class="${previewForm==='wolf'?'active':''}">KURT</button></div><p>${c.desc}</p><h4>FORM BONUSLARI</h4>${bonusRows(previewForm==='human'?c.human:c.beast)}<p class="balance-note">Örnek denge değerleri. Mevcut APK’da savaş istatistiğini değiştirmez.</p><button class="primary" id="characterAction">${owned?(collectionState.equipped===c.id?'SEÇİLİ KARAKTER':'TEÇHİZATA SEÇ'):c.price+' KREDİYLE DENE'} →</button><p class="collection-note">${owned?'Tercihin cihazda kaydedilir.':'Sadece deneme kredisi kullanılır; ödeme yapılmaz.'}</p>`;
 $('previewHuman').onclick=()=>{previewForm='human';playSound();renderCharacter();};$('previewWolf').onclick=()=>{previewForm='wolf';playSound();renderCharacter();};
 $('characterAction').onclick=()=>{playSound();if(!owned){if(collectionState.credits<c.price){toast('Deneme kredisi yetersiz.');return;}collectionState.credits-=c.price;collectionState.owned.push(c.id);toast(c.name+' deneme envanterine eklendi.');}else{collectionState.equipped=c.id;toast(c.name+' teçhizata seçildi.');}saveCollection();renderGear();renderCollection();};
}
$('inventoryMode').onclick=()=>{libraryMode='inventory';renderCollection();};$('shopMode').onclick=()=>{libraryMode='shop';renderCollection();};
for(const b of document.querySelectorAll('[data-category]'))b.onclick=()=>{playSound();category=b.dataset.category;renderCollection();};
$('openInventory').onclick=()=>window.openCollection();
const abilities=[{id:'claw',title:'PENÇE',key:'01',range:2.5,damage:30,cooldown:1.5,desc:'Yakın mesafeye kısa saldırı.'},{id:'pounce',title:'SIÇRAMA',key:'02',range:5,damage:20,cooldown:5,desc:'İleri atılma ve yaklaşma.'},{id:'pulse',title:'ŞOK DALGASI',key:'03',range:4,damage:15,cooldown:8,desc:'Yakındaki hedefe alan etkisi.'},{id:'track',title:'İZ SÜRME',key:'04',range:10,damage:0,cooldown:10,desc:'Menzildeki hedefi kısa süre belirginleştir.'}];
let targetDistance=2;const cooldowns={};let effectTimer;
window.openAbilities=()=>{screen('abilities');renderAbilities();};
$('openAbilities').onclick=window.openAbilities;$('collectionAbilities').onclick=window.openAbilities;
function renderAbilities(){$('abilityCards').innerHTML=abilities.map(a=>`<button class="ability-card" data-ability="${a.id}"><span>${a.key}</span><div><strong>${a.title}</strong><p>${a.desc}</p><small>${a.range} m • ${a.cooldown} sn • ${a.damage? a.damage+' hasar':'Algılama'}</small></div><b id="cooldown-${a.id}">DENE</b></button>`).join('');document.querySelectorAll('[data-ability]').forEach(b=>b.onclick=()=>useAbility(b.dataset.ability));updateCooldowns();}
function setDistance(d){targetDistance=d;$('nearTarget').classList.toggle('active',d===2);$('farTarget').classList.toggle('active',d===8);$('targetToken').classList.toggle('far',d===8);}
$('nearTarget').onclick=()=>setDistance(2);$('farTarget').onclick=()=>setDistance(8);
function useAbility(id){const a=abilities.find(a=>a.id===id);if((cooldowns[id]||0)>Date.now())return;cooldowns[id]=Date.now()+a.cooldown*1000;playSound();clearTimeout(effectTimer);$('abilityEffect').className='';$('wolfToken').className='';void $('abilityEffect').offsetWidth;$('abilityEffect').className='effect-'+id;$('wolfToken').className=id==='pounce'?'pouncing':'';const hit=targetDistance<=a.range;$('targetToken').classList.toggle('detected',id==='track'&&hit);$('damageText').textContent=hit?(a.damage?'-'+a.damage:'TESPİT'):'MENZİL DIŞI';$('damageText').className='damage-pop';$('abilityResult').textContent=hit?a.title+': '+(a.damage?a.damage+' örnek hasar.':'Hedef algılandı.') :a.title+': hedef menzil dışında; hasar verilmedi.';effectTimer=setTimeout(()=>{$('abilityEffect').className='';$('wolfToken').className='';$('targetToken').classList.remove('detected');$('damageText').className='';},1500);updateCooldowns();}
function updateCooldowns(){if(currentScreen!=='abilities')return;for(const a of abilities){const remaining=Math.max(0,((cooldowns[a.id]||0)-Date.now())/1000);const b=document.querySelector('[data-ability="'+a.id+'"]');if(b){b.disabled=remaining>0;$('cooldown-'+a.id).textContent=remaining>0?remaining.toFixed(1)+' sn':'DENE';}}}
setInterval(updateCooldowns,200);renderGear();
