// Session-only review variant: ownership, equipment and credits are untouched.
(()=>{const button=document.getElementById('nativePairToggle');if(!button)return;
const active=new URLSearchParams(location.search).get('nativePair')==='1';
button.textContent=active?'ESKİ MODELE DÖN':'YENİ ÇİFT · DENEME';
button.title='Bilge Kağan insan/kurt uyarlaması. Dört ayak koşu ve tam takla bu çiftte henüz hazır değil.';
button.onclick=()=>{const url=new URL(location.href);if(active)url.searchParams.delete('nativePair');else url.searchParams.set('nativePair','1');location.href=url.href;};
})();
