'use strict';
const $ = (id) => document.getElementById(id);
const stage = $('stage');
const viewport = $('viewport');
const intro = $('intro');
const modal = $('modal');
const sounds = { click: new Audio('media/click.wav'), confirm: new Audio('media/enter.mp3'), back: new Audio('media/back.wav') };
let audioEnabled = true;
let volume = 0.65;
let selectedRoom = 'bunker';
let currentScreen = 'opening';
let toastTimer;
try { const saved = JSON.parse(localStorage.getItem('rogue-settings')); if (saved) { audioEnabled = saved.audio !== false; volume = Math.max(0, Math.min(1, Number(saved.volume) || 0)); } } catch (_) {}

function fit() {
  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  if (!width || !height) return;
  const scale = height / 720;
  stage.style.width = `${width / scale}px`;
  stage.style.transform = `scale(${scale})`;
}
addEventListener('resize', fit);
addEventListener('orientationchange', fit);
if (window.visualViewport) window.visualViewport.addEventListener('resize', fit);
if (window.ResizeObserver) new ResizeObserver(fit).observe(viewport);
fit();
function saveSettings() { try { localStorage.setItem('rogue-settings', JSON.stringify({ audio: audioEnabled, volume })); } catch (_) {} updateSound(); }
function updateSound() { $('openingSound').textContent = audioEnabled ? 'SES AÇIK' : 'SES KAPALI'; intro.muted = !audioEnabled; intro.volume = volume; }
function playSound(type = 'click') { if (!audioEnabled || document.hidden) return; const a = sounds[type]; if (!a) return; a.volume = volume; a.currentTime = 0; a.play().catch(() => {}); }
function screen(name) { if(name!=='arena')window.stopArena?.(); if(name!=='wolfGear'&&name!=='collection')window.stopWolfMotion?.(); if (name !== 'opening') { intro.pause(); intro.classList.remove('playing'); } for (const el of document.querySelectorAll('.screen')) { const active = el.id === name; el.classList.toggle('active', active); el.inert = !active; } currentScreen = name; }
function toast(text) { $('toast').textContent = text; $('toast').classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').classList.remove('show'), 3500); }
function showModal(title, html, label = 'ROGUE: BLOOD MOON') { modal.classList.remove('events-modal','settings-modal'); $('modalTitle').textContent = title; $('modalBody').innerHTML = html; $('modalLabel').textContent = label; document.getElementById(currentScreen).inert = true; modal.hidden = false; modal.open = true; modal.setAttribute('open', ''); $('closeModal').focus(); }
function closeModal() { playSound('back'); modal.hidden = true; modal.open = false; modal.removeAttribute('open'); document.getElementById(currentScreen).inert = false; }
$('closeModal').addEventListener('click', closeModal);
$('modalOk').addEventListener('click', closeModal);
modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
modal.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); closeModal(); } if (e.key === 'Tab') { const items = Array.from(modal.querySelectorAll('button,input')).filter(el => !el.disabled); const first=items[0], last=items[items.length-1]; if (e.shiftKey && document.activeElement===first) { e.preventDefault(); last.focus(); } else if (!e.shiftKey && document.activeElement===last) { e.preventDefault(); first.focus(); } } });

$('skipIntro').addEventListener('click', () => screen('lobby'));
$('openingSound').addEventListener('click', () => { audioEnabled = !audioEnabled; saveSettings(); playSound(); });
async function startIntro(restart = true) {
  screen('opening');
  if (restart) intro.currentTime = 0;
  $('startIntro').hidden = true;
  updateSound(); intro.classList.add('playing');
  try { await intro.play(); }
  catch (error) {
    if (currentScreen !== 'opening' || document.hidden) return;
    if (error.name === 'NotAllowedError') $('startIntro').hidden = false;
    else { screen('lobby'); toast('Açılış videosu oynatılamadı. Menü açıldı.'); }
  }
}
$('startIntro').addEventListener('click', () => startIntro(false));
intro.addEventListener('ended', () => { if (currentScreen === 'opening') screen('lobby'); });
intro.addEventListener('error', () => { if (currentScreen === 'opening') { screen('lobby'); toast('Açılış videosu yüklenemedi. Menü açıldı.'); } });

document.querySelectorAll('[data-action]').forEach(b => b.addEventListener('click', () => { playSound('back'); if (b.dataset.action === 'opening') startIntro(); else screen(b.dataset.action); }));
const rooms = { bunker: ['SIĞINAK 07', "3'e 3 • Harita konsepti hazır"], foundry: ['DÖKÜMHANE', 'Harita henüz tasarım aşamasında'], quarantine: ['KARANTİNA', 'Harita henüz tasarım aşamasında'] };
document.querySelectorAll('[data-room]').forEach(b => b.addEventListener('click', () => {
  playSound(); selectedRoom = b.dataset.room;
  document.querySelectorAll('[data-room]').forEach(row => { const active = row === b; row.classList.toggle('selected', active); row.setAttribute('aria-pressed', String(active)); });
  $('selectedName').textContent = rooms[selectedRoom][0]; $('selectedHint').textContent = rooms[selectedRoom][1];
}));
$('join').addEventListener('click', () => {
  playSound('confirm');
  if (selectedRoom !== 'bunker') { showModal(rooms[selectedRoom][0], '<p>Bu harita ileriki sürümler için ayrıldı. İlk prototipte <strong>Sığınak 07</strong> konseptini inceleyebilirsin.</p><p class="modal-note">Bu sürümde çevrimiçi oda ve oynanabilir maç bulunmuyor.</p>', 'HARİTA • TASARIM AŞAMASINDA'); return; }
  if(window.openArena)window.openArena();else toast('Test alanı hazırlanıyor…');
});
const eventData = {
 moon: {title:'KANLI AY', tag:'GECE OPERASYONU', description:'Dolunay altında Sığınak 07 kontrolünü ele geçir. Açık alanlarda insan formunu, çatı rotalarında kurdunu kullan.', tasks:['3 gece operasyonuna katıl','Takımınla 2 galibiyet kazan','İnsan ve kurt formunda 5’er eleme yap'], benefits:['+%25 deneyim bonusu','Kanlı Ay profil çerçevesi','750 kredi görev ödülü'], goal:'0 / 3 operasyon', tone:'moon'},
 hunt: {title:'İLK AV', tag:'BAŞLANGIÇ GÖREVLERİ', description:'İlk dönüşümün, ilk avın. Temel eğitim görevlerini tamamlayıp kendi muharebe düzenini oluştur.', tasks:['Hareket ve nişan eğitimini bitir','İlk insan–kurt dönüşümünü yap','Çatı parkurunu tamamla'], benefits:['Başlangıç görünüm seti','500 kredi eğitim ödülü','İlk Av oyuncu unvanı'], goal:'0 / 3 eğitim', tone:'hunt'},
 pack: {title:'SÜRÜ KAPIŞMASI', tag:'HAFTALIK TAKIM HEDEFİ', description:'Sürünü bir araya getir. 3’e 3 çatışmalarda takımınla ilerle, ortak hedefleri tamamla.', tasks:['Takımınla 5 maça katıl','Toplam 20 asist yap','3 takım galibiyeti kazan'], benefits:['Özel sürü arması','1.000 kredi takım ödülü','Takım maçlarında +%15 deneyim'], goal:'0 / 5 takım maçı', tone:'pack'}
};
let chosenEvent = 'moon';
function showEvents(key = 'moon') {
 chosenEvent=key;
 const e=eventData[key];
 const tabs=Object.entries(eventData).map(([id,v])=>`<button class="event-tab ${id===key?'active':''}" data-event-tab="${id}">${v.title}</button>`).join('');
 showModal('ETKİNLİK MERKEZİ', `<div class="event-tabs">${tabs}</div><div class="event-sheet"><div class="event-story ${e.tone}"><span class="eyebrow">${e.tag}</span><h3>${e.title}</h3><p>${e.description}</p><div class="event-progress"><span>${e.goal}</span><span>PLANLANAN</span></div><div class="progress-track"><i></i></div></div><div class="event-objectives"><h4>GÖREVLER</h4>${e.tasks.map((t,i)=>`<div class="task-row"><span>0${i+1}</span><p>${t}</p><b>○</b></div>`).join('')}<h4>AVANTAJLAR & ÖDÜLLER</h4><div class="reward-grid">${e.benefits.map(t=>`<div class="reward"><span>◇</span><strong>${t}</strong></div>`).join('')}</div></div></div><p class="concept-note">Örnek etkinlik tasarımıdır. Bonuslar, görev ilerlemesi ve ödüller henüz aktif değil.</p>`, 'SEZON 00 • OPERASYONLAR');
 modal.classList.add('events-modal');
 modal.querySelectorAll('[data-event-tab]').forEach(b=>b.addEventListener('click',()=>{playSound();showEvents(b.dataset.eventTab);}));
}
document.querySelectorAll('[data-event]').forEach(b=>b.addEventListener('click',()=>{playSound();showEvents(b.dataset.event);}));

function mapInfo() { playSound(); showModal('SIĞINAK 07', '<p>Terk edilmiş askerî araştırma tesisi. İlk 3’e 3 haritamız için görsel ve rota konsepti.</p><ul><li><strong>Avlu:</strong> siperli merkez çatışma alanı.</li><li><strong>Laboratuvar:</strong> kuzeyden geçen kapalı yan rota.</li><li><strong>Bakım:</strong> güneyde yükleme alanına bağlanan rota.</li><li><strong>Çatılar:</strong> kurtlar için önerilen zıplama kestirmeleri.</li></ul><p class="modal-note">Görsel bir konsepttir; henüz 3B sahne, çarpışma veya hareket sistemi yok.</p>', 'HARİTA • 3 ROTA'); }
$('mapInfo').addEventListener('click', mapInfo);
$('mapDetails').addEventListener('click', () => { playSound(); document.querySelector('.map-image').classList.add('expanded'); toast('Kapatmak için haritaya dokun.'); });
document.querySelector('.map-image').addEventListener('click', e => { e.currentTarget.classList.remove('expanded'); });

function settings() {
  showModal('AYARLAR', `<p class="settings-intro">Ses tercihleri</p><div class="setting"><span>Ses efektleri</span><button id="soundToggle" class="toggle ${audioEnabled ? '' : 'off'}">${audioEnabled ? 'AÇIK' : 'KAPALI'}</button></div><label class="setting"><span>Ses düzeyi</span><input id="volume" type="range" min="0" max="100" value="${Math.round(volume * 100)}" aria-label="Ses düzeyi"></label><button id="testSound" class="toggle">DÜĞME SESİNİ DENE</button><p class="settings-version">ROGUE: BLOOD MOON • v0.1.10</p>`, 'TERCİHLER'); modal.classList.add('settings-modal');
  $('soundToggle').addEventListener('click', e => { audioEnabled = !audioEnabled; e.currentTarget.textContent = audioEnabled ? 'AÇIK' : 'KAPALI'; e.currentTarget.classList.toggle('off', !audioEnabled); saveSettings(); playSound(); });
  $('volume').addEventListener('input', e => { volume = Number(e.target.value) / 100; saveSettings(); });
  $('testSound').addEventListener('click', () => { if (!audioEnabled) toast('Sesi denemek için ses efektlerini aç.'); else playSound('confirm'); });
}
document.querySelectorAll('[data-nav]').forEach(b => b.addEventListener('click', () => {
  playSound();
  switch (b.dataset.nav) {
    case 'lobby': screen('lobby'); break;
    case 'events': showEvents(); break;
    case 'settings': settings(); break;
    case 'inventory': window.openCollection('inventory'); break;
    case 'shop': window.openCollection('shop'); break;
    case 'gear': screen('gear'); break;
    case 'clan': showModal('KLAN', '<p>Kendi sürünü kur. Takım kimliği, klan etiketi ve arkadaşlarla oda kurma gelecek sürümler için planlanıyor.</p><p class="modal-note">Bu sürümde hesap veya klan sunucusu bulunmuyor.</p>', 'SOSYAL • PLANLANAN'); break;
  }
}));
window.goBack = () => { if (modal.open) closeModal(); else if (document.querySelector('.map-image.expanded')) document.querySelector('.map-image').classList.remove('expanded'); else if (['map','gear','collection','wolfGear','arena'].includes(currentScreen)) { playSound('back'); screen('lobby'); } else if (currentScreen === 'opening') screen('lobby'); else toast('Uygulamadan çıkmak için ana ekran hareketini kullan.'); };
window.pauseApp = () => { intro.pause(); Object.values(sounds).forEach(a => a.pause()); };
window.resumeApp = () => { if (currentScreen === 'opening' && !intro.ended) startIntro(false); };
document.addEventListener('visibilitychange', () => { if (document.hidden) window.pauseApp(); else window.resumeApp(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.open) window.goBack(); });

let gearSet = '1';
let gearForm = 'human';
try { const saved=JSON.parse(localStorage.getItem('rogue-loadout')); if(saved) {gearSet=['1','2','3'].includes(saved.set)?saved.set:'1';gearForm=saved.form==='wolf'?'wolf':'human';} } catch(_) {}
function renderGear() {
 document.querySelectorAll('[data-loadout]').forEach(b=>b.classList.toggle('active',b.dataset.loadout===gearSet));
 document.querySelectorAll('[data-form]').forEach(b=>b.classList.toggle('active',b.dataset.form===gearForm));
 $('loadoutName').textContent=$('loadoutFooter').textContent='SET 0'+gearSet;
 $('operatorPortrait').className='operator-portrait '+gearForm;
 $('operatorName').textContent=gearForm==='human'?'BAŞIBOZUK':'GECE AVCISI';
 $('operatorRole').textContent=gearForm==='human'?'Taktik operatör • Görsel önizleme':'Kurt formu • Görsel önizleme';
 $('gearRole').textContent=gearForm==='human'?'TAKTİK OPERATÖR':'YAKIN MESAFE AVCISI';
 if(window.refreshCharacter) window.refreshCharacter();
}
document.querySelectorAll('[data-loadout]').forEach(b=>b.addEventListener('click',()=>{playSound();gearSet=b.dataset.loadout;renderGear();}));
document.querySelectorAll('[data-form]').forEach(b=>b.addEventListener('click',()=>{playSound();gearForm=b.dataset.form;renderGear();}));
document.querySelectorAll('[data-slot]').forEach(b=>b.addEventListener('click',()=>{playSound();document.querySelectorAll('[data-slot]').forEach(s=>s.classList.toggle('selected',s===b));$('slotName').textContent=b.dataset.slot.toLocaleUpperCase('tr');$('slotHelp').textContent='Bu yuva hazır. Silah ve ekipmanlar sonraki aşamada eklenecek.';}));
$('saveLoadout').addEventListener('click',()=>{playSound('confirm');try {localStorage.setItem('rogue-loadout',JSON.stringify({set:gearSet,form:gearForm}));toast('Set düzeni kaydedildi.');}catch(_){toast('Bu cihazda tercihler kaydedilemedi.');}});
renderGear();

updateSound();
startIntro();

window.rogueOpenScreen=screen;window.roguePlaySound=playSound;
