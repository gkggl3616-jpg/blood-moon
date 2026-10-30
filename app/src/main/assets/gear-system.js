'use strict';
// One owned-item ledger and stat calculator for menus, saved presets and combat.
window.RogueGear=(()=>{
 const slotNames={back:'Sırt dövmesi',left:'Sol kol dövmesi',right:'Sağ kol dövmesi',skill:'Takla / koşu',accessory:'Aksesuar',claw:'Pençe',primary:'Ana silah',secondary:'İkinci silah',knife:'Bıçak',grenade:'Bomba'};
 const motifs={dragon:['Ejder',{damage:60,defense:20},650],phoenix:['Anka',{health:100,damage:20},900],lion:['Aslan',{defense:120,health:40},1000],pegasus:['Kanatlı At',{speed:40,health:20},850],spider:['Örümcek',{defense:60,speed:20},600],bull:['Boğa',{health:160,defense:40},1100],dice:['Kader Zarı',{damage:80,speed:15},850],unicorn:['Tekboynuz',{health:240,defense:20},1800],reaper:['Ölüm',{damage:240},1800]};
 const catalog=[];
 for(const [motif,[name,bonus,price]] of Object.entries(motifs)){
  catalog.push({id:`tattoo-${motif}-back`,type:'tattoo',slot:'back',name:`${name} · Sırt`,motif,bonus,price});
  if(['dragon','phoenix','reaper'].includes(motif))for(const side of ['left','right'])catalog.push({id:`tattoo-${motif}-${side}`,type:'tattoo',slot:side,name:`${name} · ${side==='left'?'Sol':'Sağ'} kol`,motif,bonus:motif==='reaper'?{[side==='left'?'damage':'defense']:60}:motif==='phoenix'?{health:35}:{damage:20},price:motif==='reaper'?650:300});
 }
 for(const side of ['left','right'])catalog.push({id:`tattoo-runes-${side}`,type:'tattoo',slot:side,name:`Gök Yazısı · ${side==='left'?'Sol':'Sağ'} kol`,motif:'runes',bonus:side==='left'?{speed:5}:{defense:15},price:150});
 catalog.push(
  {id:'skill-normal',type:'skill',slot:'skill',name:'Kurt Taklası',price:450,bonus:{},description:'Kısa ve temas hasarlı takla.'},
  {id:'skill-legendary',type:'skill',slot:'skill',name:'Efsanevi Kurt Taklası',price:1200,bonus:{},description:'Dört ayak koşu + kısa, temas hasarlı takla.'},
  {id:'accessory-collar',type:'accessory',slot:'accessory',name:'Kağan Tasması',price:200,bonus:{},accessory:'collar'},
  {id:'accessory-shoulder',type:'accessory',slot:'accessory',name:'Tigin Omuzluğu',price:250,bonus:{},accessory:'shoulder'},
  {id:'accessory-charm',type:'accessory',slot:'accessory',name:'Uç Tılsımı',price:180,bonus:{},accessory:'charm'},
  {id:'claw-standard',type:'claw',slot:'claw',name:'Çelik Pençe',price:0,bonus:{},profile:'standard'},
  {id:'rifle-ar01',type:'weapon',slot:'primary',name:'AR-01 · Saldırı Tüfeği',price:0,bonus:{},weapon:{kind:'rifle',damage:23,interval:.17,capacity:30}},
  {id:'rifle-sr01',type:'weapon',slot:'primary',name:'SR-01 · Keskin Nişancı',price:550,bonus:{},weapon:{kind:'sniper',damage:67,interval:.95,capacity:5}},
  {id:'pistol-p01',type:'weapon',slot:'secondary',name:'P-01 · Tabanca',price:0,bonus:{},weapon:{kind:'pistol',damage:18,interval:.26,capacity:12}},
  {id:'knife-k01',type:'knife',slot:'knife',name:'KAMA-01',price:0,bonus:{},weapon:{kind:'knife',damage:34,interval:.55,range:1.9}},
  {id:'grenade-frag',type:'grenade',slot:'grenade',name:'PARÇA-01 · Parça Bombası',price:200,bonus:{},weapon:{kind:'frag',damage:65,interval:3.5,radius:3.5}},
  {id:'grenade-smoke',type:'grenade',slot:'grenade',name:'SİS-01 · Duman Bombası',price:250,bonus:{},weapon:{kind:'smoke',damage:0,interval:5,radius:3}}
 );
 for(const [model,name] of [['bilge','Buz Kıran']])catalog.push({id:'claw-'+model,type:'claw',slot:'claw',name:name+' Pençe',price:0,bonus:{},model,profile:model});
 const items=Object.fromEntries(catalog.map(i=>[i.id,i]));
 const empty=()=>({wolf:{back:null,left:null,right:null,skill:null,accessory:null,claw:'claw-standard'},human:{primary:'rifle-ar01',secondary:'pistol-p01',knife:'knife-k01',grenade:null}});
 let data={version:2,owned:['rifle-ar01','pistol-p01','knife-k01','claw-standard'],profiles:{},active:{}};
 let loaded=false;
 try{const v=JSON.parse(localStorage.getItem('rogue-gear-v2'));if(v?.version===2&&v.profiles&&v.active&&Array.isArray(v.owned)){data=v;data.owned=[...new Set(v.owned.filter(id=>items[id]))];loaded=true;}}catch(_){}
 const owns=id=>data.owned.includes(id);
 function ensure(id){if(!data.profiles[id])data.profiles[id]=Array.from({length:4},empty);while(data.profiles[id].length<4)data.profiles[id].push(empty());if(!Number.isInteger(data.active[id])||data.active[id]<0||data.active[id]>3)data.active[id]=0;for(const p of data.profiles[id]){p.wolf={...empty().wolf,...p.wolf};p.human={...empty().human,...p.human};}return data.profiles[id];}
 const grant=id=>{if(items[id]&&!owns(id))data.owned.push(id);};
 if(!loaded){
  let old={},skills=[];try{old=JSON.parse(localStorage.getItem('rogue-wolf-loadouts'))||{};skills=JSON.parse(localStorage.getItem('rogue-roll-items'))||[];}catch(_){}
  for(const tier of skills)grant('skill-'+tier);
  for(const c of roster){const p=ensure(c.id)[0],e=old[c.id]||{};const tattoos={back:'dragon',left:'runes',right:'runes',...e.tattoos};
   for(const slot of ['back','left','right']){const id=`tattoo-${tattoos[slot]}-${slot}`;if(items[id]){grant(id);p.wolf[slot]=id;}}
   if(skills.includes(e.skill))p.wolf.skill='skill-'+e.skill;
   if(items['accessory-'+e.accessory]){grant('accessory-'+e.accessory);p.wolf.accessory='accessory-'+e.accessory;}
  }
 }
 function syncOwnedCharacters(){for(const id of collectionState.owned){ensure(id);const claw='claw-'+characterModelId(id);grant(claw);if(!data.profiles[id][0]._clawInitialized){data.profiles[id][0].wolf.claw=claw;data.profiles[id][0]._clawInitialized=true;}}}
 syncOwnedCharacters();
 function save(){try{localStorage.setItem('rogue-gear-v2',JSON.stringify(data));return true;}catch(_){toast('Cihaz kaydı kullanılamıyor; bu oturumdaki donanım korunuyor.');return false;}}
 save();
 function profile(id,index=data.active[id]||0){return ensure(id)[index];}
 function current(id,form='wolf'){return profile(id)[form];}
 function compatible(item,slot,form,id){return !!item&&item.slot===slot&&(form==='wolf'?!['weapon','knife','grenade'].includes(item.type):['weapon','knife','grenade'].includes(item.type))&&(!item.model||item.model===characterModelId(id));}
 function notify(){window.dispatchEvent(new Event('rogue-gear-changed'));}
 function equip(id,form,slot,itemId){
  if(!collectionState.owned.includes(id))return {ok:false,message:'Önce karakteri envantere ekle.'};
  const item=items[itemId];if(itemId!==null&&(!owns(itemId)||!compatible(item,slot,form,id)))return {ok:false,message:'Bu eşya bu yuvaya uygun değil veya sahip değilsin.'};
  if(!slotNames[slot]||!(slot in current(id,form)))return {ok:false,message:'Geçersiz donanım yuvası.'};
  current(id,form)[slot]=itemId;save();notify();return {ok:true,message:itemId?item.name+' kuşanıldı.':'Eşya çıkarıldı.'};
 }
 function buy(itemId){const i=items[itemId];if(!i||owns(itemId))return {ok:false,message:'Bu eşya zaten envanterde.'};if(i.model&&!collectionState.owned.some(id=>characterModelId(id)===i.model))return {ok:false,message:'Bu pençe ilgili karakterle birlikte açılır.'};if(collectionState.credits<i.price)return {ok:false,message:'Deneme kredisi yetersiz.'};collectionState.credits-=i.price;grant(itemId);saveCollection();save();notify();return {ok:true,message:i.name+' envantere eklendi.'};}
 function aggregate(base,character,tattoo,roaring=false){const multipliers={damage:roaring?1.15:1,defense:roaring?1.30:1,speed:roaring?1.20:1,health:1};const values={};for(const k of ['damage','defense','speed','health'])values[k]=base[k]*(1+(character[k]||0)/100+(tattoo[k]||0)/100)*multipliers[k];return {base,character,tattoo,active:multipliers,values};}
 function stats(id,form='wolf',roaring=false){const c=roster.find(c=>c.id===id)||roster[0],character={damage:0,defense:0,speed:0,health:0},tattoo={damage:0,defense:0,speed:0,health:0};
  if(form==='wolf'){character.damage=c.beast[0][1];character.defense=c.beast[1][1];const seen=new Set();for(const slot of ['back','left','right']){const item=items[current(c.id)[slot]];if(!item||!owns(item.id)||seen.has(item.id)||item.slot!==slot)continue;seen.add(item.id);for(const [key,value] of Object.entries(item.bonus))tattoo[key]+=value;}}
  else{for(const [key,value] of c.human){if(key==='Hareket')character.speed=value;if(key==='Dayanıklılık')character.health=value;}}
  return aggregate({damage:100,defense:100,speed:100,health:100},character,tattoo,roaring);
 }
 return {catalog,items,slotNames,owns,profile,current,compatible,equip,buy,aggregate,stats,save,ensure,syncOwnedCharacters,
  preset:id=>data.active[id]||0,setPreset:(id,n)=>{if(!Number.isInteger(n)||n<0||n>3)return false;ensure(id);data.active[id]=n;save();notify();return true;},snapshot:()=>JSON.parse(JSON.stringify(data))};
})();
