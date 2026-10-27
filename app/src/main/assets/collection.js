'use strict';
const roster = [
 {id:'basibozuk',name:'BAŞIBOZUK',wolf:'GECE AVCISI',role:'DENGELİ',power:100,body:'Dengeli gövde',claw:'Kısa çapraz savuruş',trail:'Soluk çelik • üç kısa çizgi',price:0,color:'#607d89',human:[['Hareket',0],['Şarjör değişimi',0]],beast:[['Hasar',0],['Dayanıklılık',0]],desc:'Dengeli başlangıç operatörü. Temel insan ve kurt değerleriyle oynanış referansı.'},
 {id:'kul',name:'KÜL',wolf:'KÜL PENÇESİ',role:'İZCİ',power:112,body:'İnce ve çevik',claw:'Hızlı ters el serisi',trail:'Kül grisi • iki dar kavis',price:750,color:'#be8b72',human:[['Hareket',4],['Dayanıklılık',-3]],beast:[['Hasar',12],['Dayanıklılık',12]],desc:'Çeviklik odaklı izci. Daha hızlı hareket karşılığında daha düşük dayanıklılık.'},
 {id:'ayaz',name:'AYAZ',wolf:'AYAZ MUHAFIZI',role:'SAVUNMA',power:118,body:'Geniş omuzlu',claw:'Ağır üstten savuruş',trail:'Buz mavisi • geniş tek yay',price:1200,color:'#72a7b5',human:[['Dayanıklılık',5],['Hareket',-3]],beast:[['Hasar',18],['Dayanıklılık',18]],desc:'Alan savunmasına odaklı ağır operatör. Dayanıklılık avantajı, hareket hızı bedeliyle dengelenir.'} ,
 {id:'bilge',name:'BİLGE KAĞAN',wolf:'BOZ KAĞAN',role:'KOMUTAN',price:900,power:145,color:'#c3b17c',human:[['Dayanıklılık',3],['Hareket',-2]],beast:[['Hasar',45],['Dayanıklılık',45]],body:'Uzun ve geniş gövdeli',claw:'Gövde dönüşüyle ağır yatay darbe',trail:'Mat altın • üç geniş yatay yay',desc:'Göktürk hükümdarı Bilge Kağan’dan esinlenen kurgu komutan. Tarihî bir portre iddiası taşımaz.'},
 {id:'kultigin',name:'KÜL TİGİN',wolf:'KARA TİGİN',role:'SAVAŞÇI',price:1400,power:180,color:'#b55260',human:[['Dayanıklılık',4],['Hareket',-3]],beast:[['Hasar',80],['Dayanıklılık',80]],body:'Kaslı ve atletik',claw:'Omuzdan başlayan iki çapraz güçlü darbe',trail:'Koyu kızıl • iki kalın çapraz iz',desc:'Göktürk komutanı Kül Tigin’den esinlenen savaşçı. Kurt gücü tasarım tavanı olan 180 endeksindedir.'},
 {id:'alparslan',name:'ALP ARSLAN',wolf:'BOZ ARSLAN',role:'ÖNCÜ',price:1250,power:165,color:'#c3945e',human:[['Dayanıklılık',5],['Hareket',-4]],beast:[['Hasar',65],['Dayanıklılık',65]],body:'Ağır, geniş göğüslü',claw:'Ağırlık aktarımıyla alttan yukarı ağır darbe',trail:'Kehribar • üç derin yükselen yay',desc:'Selçuklu hükümdarı Alp Arslan’dan esinlenen kurgu öncü. Ağır gövdesi için daha geniş saldırı hareketleri planlanır.'},
 {id:'konuralp',name:'KONURALP',wolf:'UÇ AVCISI',role:'AKINCI',price:1000,power:150,color:'#6ea8a2',human:[['Hareket',4],['Dayanıklılık',-3]],beast:[['Hasar',50],['Dayanıklılık',50]],body:'İnce, uzun uzuvlu',claw:'Kısa adımla üç hızlı pençe',trail:'Soluk turkuaz • üç ince paralel iz',desc:'Osmanlı uç beyi Konuralp’ten esinlenen kurgu akıncı. Hafif gövde için dar ve hızlı savuruşlar planlanır.'}

];
for (const c of roster) { c.power=Math.max(100,Math.min(180,c.power)); const t=(c.power-100)/80; c.beast=[['Hasar',Math.floor(t*(180/1.15-100)*1000)/1000],['Dayanıklılık',Math.floor(t*(180/1.30-100)*1000)/1000]]; }
let collectionState={credits:2500,owned:['basibozuk'],equipped:'basibozuk'};
try{const v=JSON.parse(localStorage.getItem('rogue-collection'));if(v){collectionState.credits=Number.isFinite(v.credits)?Math.max(0,v.credits):2500;collectionState.owned=roster.filter(c=>v.owned?.includes(c.id)).map(c=>c.id);if(!collectionState.owned.includes('basibozuk'))collectionState.owned.push('basibozuk');collectionState.equipped=collectionState.owned.includes(v.equipped)?v.equipped:'basibozuk';}}catch(_){}
let libraryMode='inventory',category='characters',selectedCharacter='basibozuk',previewForm='human';
function saveCollection(){try{localStorage.setItem('rogue-collection',JSON.stringify(collectionState));}catch(_){toast('Cihaz kaydı kullanılamıyor.');}}
function bonusRows(rows){return rows.map(([label,value])=>`<div class="bonus-row"><span>${label}</span><strong class="${value>0?'positive':value<0?'negative':''}">${value>0?'+':''}${Number(value.toFixed(1))}%</strong></div>`).join('');}
window.refreshCharacter=()=>{const c=roster.find(c=>c.id===collectionState.equipped);$('operatorName').textContent=gearForm==='human'?c.name:c.wolf;$('operatorRole').textContent=c.role+' • Temsilî görsel';$('gearRole').textContent=c.role;};
window.openCollection=(mode='inventory')=>{libraryMode=mode;screen('collection');renderCollection();};
function renderCollection(){
 $('collectionTitle').textContent=libraryMode==='shop'?'MAĞAZA':'ENVANTER';$('walletAmount').textContent=collectionState.credits.toLocaleString('tr');
 $('inventoryMode').classList.toggle('active',libraryMode==='inventory');$('shopMode').classList.toggle('active',libraryMode==='shop');
 document.querySelectorAll('[data-category]').forEach(b=>b.classList.toggle('active',b.dataset.category===category));
 const labels={skills:'KURT ÖZELLİKLERİ',weapons:'SİLAHLAR',grenades:'BOMBALAR',knives:'BIÇAKLAR',characters:'KARAKTERLER',wolves:'KURT FORMLARI',equipment:'EKİPMAN',cosmetics:'GÖRÜNÜMLER'};
 $('categoryTitle').textContent=labels[category];
 const list=libraryMode==='shop'?roster:roster.filter(c=>collectionState.owned.includes(c.id));
 $('collectionCount').textContent=(['characters','wolves'].includes(category)?list.length:category==='cosmetics'?1:0)+' KAYIT';
 if(['characters','wolves'].includes(category)){
  if(!list.some(c=>c.id===selectedCharacter))selectedCharacter=list[0].id;
  $('collectionCards').innerHTML=list.map(c=>`<button class="character-card ${selectedCharacter===c.id?'active':''}" data-character="${c.id}" style="--character-color:${c.color}"><span class="character-mark">${category==='wolves'?'◈':c.name[0]}</span><small>${c.role}</small><strong>${category==='wolves'?c.wolf:c.name}</strong><span class="ownership">${collectionState.equipped===c.id?'SEÇİLİ':collectionState.owned.includes(c.id)?'ENVANTERDE':c.price+' DENEME KREDİSİ'}</span></button>`).join('');
  document.querySelectorAll('[data-character]').forEach(b=>b.addEventListener('click',()=>{playSound();selectedCharacter=b.dataset.character;renderCollection();}));renderCharacter();
 }else if(category==='skills'){window.renderRollShop();
 }else if(['weapons','grenades','knives'].includes(category)){ window.renderCatalog(category);
 }else{
  $('collectionCards').innerHTML=category==='equipment'?'<div class="empty-collection"><b>＋</b><h3>EKİPMAN ALANI HAZIR</h3><p>Silahlar ve ekipman modelleri sonraki aşamada eklenecek.</p></div>':'<div class="cosmetic-card"><span>◈</span><h3>STANDART GÖRÜNÜM</h3><p>Başlangıç görünümü • Envanterde</p></div>';
  $('collectionDetail').innerHTML='<span class="eyebrow">KOLEKSİYON BİLGİSİ</span><h2>'+labels[category]+'</h2><p>Karakter ve kurt formunu teçhizat ekranından birlikte kullanabileceksin.</p><button class="primary" id="backToGear">TEÇHİZATA DÖN →</button>';$('backToGear').onclick=()=>screen('gear');
 }
}
function renderCharacter(){const c=roster.find(c=>c.id===selectedCharacter);const owned=collectionState.owned.includes(c.id);
 $('collectionDetail').innerHTML=`<span class="eyebrow">${c.role} / KARAKTER DETAYI</span><h2>${previewForm==='human'?c.name:c.wolf}</h2><div class="collection-form"><button id="previewHuman" class="${previewForm==='human'?'active':''}">İNSAN</button><button id="previewWolf" class="${previewForm==='wolf'?'active':''}">KURT</button></div><p>${c.desc}</p><h4>FORM BONUSLARI</h4>${bonusRows(previewForm==='human'?c.human:c.beast)}<div class="signature-details"><strong>GÜÇ ENDEKSİ ${c.power} / 180</strong><p>${c.body}<br>${c.claw}<br>İz: ${c.trail}</p><small>İz sürme korunur. Sıçrama düz ileriye; yerde alan göstergesi yok.</small></div><p class="balance-note">Kükreme dahil toplam güç en fazla 180. Pasif bonuslar kükremeye pay bırakır. Animasyonlar gövdeye göre üretilecek.</p><button class="primary" id="characterAction">${owned?(collectionState.equipped===c.id?'SEÇİLİ KARAKTER':'TEÇHİZATA SEÇ'):c.price+' KREDİYLE DENE'} →</button><p class="collection-note">${owned?'Tercihin cihazda kaydedilir.':'Sadece deneme kredisi kullanılır; ödeme yapılmaz.'}</p>`;
 $('previewHuman').onclick=()=>{previewForm='human';playSound();renderCharacter();};$('previewWolf').onclick=()=>{previewForm='wolf';playSound();renderCharacter();};
 $('characterAction').onclick=()=>{playSound();if(!owned){if(collectionState.credits<c.price){toast('Deneme kredisi yetersiz.');return;}collectionState.credits-=c.price;collectionState.owned.push(c.id);toast(c.name+' deneme envanterine eklendi.');}else{collectionState.equipped=c.id;toast(c.name+' teçhizata seçildi.');}saveCollection();renderGear();renderCollection();};
}
$('inventoryMode').onclick=()=>{libraryMode='inventory';renderCollection();};$('shopMode').onclick=()=>{libraryMode='shop';renderCollection();};
for(const b of document.querySelectorAll('[data-category]'))b.onclick=()=>{playSound();category=b.dataset.category;renderCollection();};
$('openInventory').onclick=()=>window.openCollection();
renderGear();
