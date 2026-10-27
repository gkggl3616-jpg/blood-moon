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
  const scale = Math.min(width / 1280, height / 720);
  stage.style.transform = `translate(${(width - 1280 * scale) / 2}px,${(height - 720 * scale) / 2}px) scale(${scale})`;
}
addEventListener('resize', fit);
addEventListener('orientationchange', fit);
if (window.visualViewport) window.visualViewport.addEventListener('resize', fit);
if (window.ResizeObserver) new ResizeObserver(fit).observe(viewport);
fit();
function saveSettings() { try { localStorage.setItem('rogue-settings', JSON.stringify({ audio: audioEnabled, volume })); } catch (_) {} updateSound(); }
function updateSound() { $('openingSound').textContent = audioEnabled ? 'SES AÇIK' : 'SES KAPALI'; intro.muted = !audioEnabled; intro.volume = volume; }
function playSound(type = 'click') { if (!audioEnabled || document.hidden) return; const a = sounds[type]; if (!a) return; a.volume = volume; a.currentTime = 0; a.play().catch(() => {}); }
function screen(name) { if (name !== 'opening') { intro.pause(); intro.classList.remove('playing'); } for (const el of document.querySelectorAll('.screen')) { const active = el.id === name; el.classList.toggle('active', active); el.inert = !active; } currentScreen = name; }
function toast(text) { $('toast').textContent = text; $('toast').classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').classList.remove('show'), 3500); }
function showModal(title, html, label = 'ROGUE: BLOOD MOON') { $('modalTitle').textContent = title; $('modalBody').innerHTML = html; $('modalLabel').textContent = label; if (!modal.open) modal.showModal(); }
function closeModal() { playSound('back'); modal.close(); }
$('closeModal').addEventListener('click', closeModal);
$('modalOk').addEventListener('click', closeModal);
modal.addEventListener('click', e => { if (e.target === modal) { const r = modal.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeModal(); } });

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
  screen('map');
});
const eventContent = {
  moon: ['KANLI AY', '<p>Kanlı ay yükseldiğinde tesisin kontrolü için savaş.</p><ul><li>Önerilen mod: gece takım savaşı.</li><li>İnsan ve kurt formları arasında taktiksel geçiş.</li><li>Görüşü koruyan kırmızı acil durum ışıkları.</li></ul>'],
  hunt: ['İLK AV', '<p>İlk operasyonuna hazırlan. Kontrolleri öğren, silahını tanı ve içindeki avcıyı keşfet.</p><ul><li>Hareket ve nişan alma eğitimi.</li><li>İnsan–kurt dönüşümünü öğrenme.</li><li>İlk pençe saldırısı ve çatı rotası.</li></ul>'],
  pack: ['SÜRÜ KAPIŞMASI', '<p>Altı oyuncu, iki takım, tek av sahası.</p><ul><li>Önerilen format: 3’e 3 takım savaşı.</li><li>Silah menzili ve kurt hareketliliğini birlikte kullan.</li><li>Avlu, yan koridorlar ve çatılarda takımını destekle.</li></ul>']
};
const eventNote = '<p class="modal-note">Planlanan etkinlik konsepti. Görev, ödül ve canlı etkinlik sistemi bu sürümde uygulanmadı.</p>';
document.querySelectorAll('[data-event]').forEach(b => b.addEventListener('click', () => { playSound(); const [title, body] = eventContent[b.dataset.event]; showModal(title, body + eventNote, 'ETKİNLİK KONSEPTİ'); }));

function mapInfo() { playSound(); showModal('SIĞINAK 07', '<p>Terk edilmiş askerî araştırma tesisi. İlk 3’e 3 haritamız için görsel ve rota konsepti.</p><ul><li><strong>Avlu:</strong> siperli merkez çatışma alanı.</li><li><strong>Laboratuvar:</strong> kuzeyden geçen kapalı yan rota.</li><li><strong>Bakım:</strong> güneyde yükleme alanına bağlanan rota.</li><li><strong>Çatılar:</strong> kurtlar için önerilen zıplama kestirmeleri.</li></ul><p class="modal-note">Görsel bir konsepttir; henüz 3B sahne, çarpışma veya hareket sistemi yok.</p>', 'HARİTA • 3 ROTA'); }
$('mapInfo').addEventListener('click', mapInfo);
$('mapDetails').addEventListener('click', () => { playSound(); document.querySelector('.map-image').classList.add('expanded'); toast('Kapatmak için haritaya dokun.'); });
document.querySelector('.map-image').addEventListener('click', e => { e.currentTarget.classList.remove('expanded'); });

function settings() {
  showModal('AYARLAR', `<p>Düğme seslerini ve video sesini buradan ayarla.</p><div class="setting"><span>Ses efektleri</span><button id="soundToggle" class="toggle ${audioEnabled ? '' : 'off'}">${audioEnabled ? 'AÇIK' : 'KAPALI'}</button></div><label class="setting"><span>Ses düzeyi</span><input id="volume" type="range" min="0" max="100" value="${Math.round(volume * 100)}" aria-label="Ses düzeyi"></label><button id="testSound" class="toggle">DÜĞME SESİNİ DENE</button><p class="modal-note" style="margin-top:20px">Rogue: Blood Moon v0.1.1<br>Çevrimdışı menü ve harita konsepti prototipi.</p>`, 'TERCİHLER');
  $('soundToggle').addEventListener('click', e => { audioEnabled = !audioEnabled; e.currentTarget.textContent = audioEnabled ? 'AÇIK' : 'KAPALI'; e.currentTarget.classList.toggle('off', !audioEnabled); saveSettings(); playSound(); });
  $('volume').addEventListener('input', e => { volume = Number(e.target.value) / 100; saveSettings(); });
  $('testSound').addEventListener('click', () => { if (!audioEnabled) toast('Sesi denemek için ses efektlerini aç.'); else playSound('confirm'); });
}
document.querySelectorAll('[data-nav]').forEach(b => b.addEventListener('click', () => {
  playSound();
  switch (b.dataset.nav) {
    case 'lobby': screen('lobby'); break;
    case 'events': showModal('ETKİNLİKLER', '<div class="event-details"><strong>KANLI AY</strong><br>Gece operasyonu.</div><div class="event-details"><strong>İLK AV</strong><br>Başlangıç ve dönüşüm eğitimi.</div><div class="event-details"><strong>SÜRÜ KAPIŞMASI</strong><br>3’e 3 takım mücadelesi.</div>' + eventNote, 'PLANLANAN İÇERİKLER'); break;
    case 'settings': settings(); break;
    case 'gear': showModal('TEÇHİZAT', '<p>İlk oynanış sürümü için planlanan başlangıç seti:</p><ul><li>Bir saldırı tüfeği.</li><li>Bir keskin nişancı tüfeği.</li><li>Temel kurt formu ve pençe saldırısı.</li></ul><p class="modal-note">Henüz silah seçimi, satın alma veya envanter sistemi bulunmuyor.</p>', 'GELİŞTİRME PLANI'); break;
    case 'clan': showModal('KLAN', '<p>Kendi sürünü kur. Takım kimliği, klan etiketi ve arkadaşlarla oda kurma gelecek sürümler için planlanıyor.</p><p class="modal-note">Bu sürümde hesap veya klan sunucusu bulunmuyor.</p>', 'SOSYAL • PLANLANAN'); break;
  }
}));
window.goBack = () => { if (modal.open) closeModal(); else if (document.querySelector('.map-image.expanded')) document.querySelector('.map-image').classList.remove('expanded'); else if (currentScreen === 'map') { playSound('back'); screen('lobby'); } else if (currentScreen === 'opening') screen('lobby'); else toast('Uygulamadan çıkmak için ana ekran hareketini kullan.'); };
window.pauseApp = () => { intro.pause(); Object.values(sounds).forEach(a => a.pause()); };
window.resumeApp = () => { if (currentScreen === 'opening' && !intro.ended) startIntro(false); };
document.addEventListener('visibilitychange', () => { if (document.hidden) window.pauseApp(); else window.resumeApp(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.open) window.goBack(); });
updateSound();
startIntro();
