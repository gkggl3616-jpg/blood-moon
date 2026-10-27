# v0.1.12 — donanım, gerçek bonuslar ve kaynak modele sadık aktarım

## Son görsel kararı

İlk beş SS: 11496 referans duruş; 11492/11494 hatalı mevcut menü/arena; 11497 sol donanım–sağ eşya envanteri; 11498 insan silah donanımı. Referansta omuzlar geniş, bel dar, kollar gövdeye yakın. Mevcut bekleme animasyonu dirsekleri dışa itiyor ve baş/omuz ayrımını bozuyordu. Envanter referansları yalnız renk teması olarak değerlendirilmedi: sol yuvalar, bağımsız setler, sağ üç sütun ve alt açıklama uygulandı.

**Daha yeni 11513–11517 talebi önceliklidir:** kullanıcı özgün beyaz Bilge modelini korumamızı istedi. Koyu, düz gövdeyle yapılan deney reddedildi; APK’ya alınmadı. Kaynak modelin sırtı, yelesi, yüzü, kıyafeti, buz kolları, UV ve 11.999 gövde üçgeni korunur. Genel dirsek hedefleri yerine kaynağın omuz–dirsek–bilek noktaları beklemede aynen kullanılır. Küçük nefes hareketi üst zinciri birlikte taşır. Menü ve arena aynı GLB/iskeleti yükler.

`verify_source_fidelity.py` özgün statik kaynak ile teslim edilen modelin gerçek deforme köşelerini karşılaştırır. Dinlenme pozu yaklaşık 0,0000014 m; nefes döngüsü en fazla yaklaşık 0,00204 m sapar. Bu, sanatsal kalite garantisi değil; aktarımda kolların yeniden biçimlenmediğini doğrulayan geometri kontrolüdür. Kaynak kürkün kendi köşeli dokusu/topolojisi korunmuştur.

## Uygulanan sistemler

- Dört kayıtlı donanım seti; karakter ve insan/kurt formu başına ayrı yuvalar. İnsan: ana silah, ikinci silah, bıçak, bomba. Kurt: sırt/sol/sağ dövme, özellik, aksesuar ve pençe.
- Sağ ızgaradan sol yuvaya gerçek fare/dokunma sürüklemesi. Sahiplik ve uyumluluk kontrolü; dolu slotta kayıpsız değişim; iptal, pencere dışı, arka plan/blur temizliği; dokunarak seç–Kuşan alternatifi. Liste kaydırma ve 3B döndürme farklı alanlarda.
- Eski koleksiyon, krediler, satın alınan karakterler, dövmeler ve takla özellikleri v2 kaydına taşınır; eski anahtarlar silinmez. Kuşanma sahipliği ya da bombayı tüketmez.
- Satın alınan SR-01 arenada 67 hasar / 5 mermi; AR-01 23 / 30, P-01 18 / 12. Bıçak yakın mesafe ve siper kontrolü; parça bombası yarıçap/mesafe/siper hesabı, sis bombası süreli görsel hacim. 1–4 veya ekran tuşlarıyla seçilir. İnsan el/silahları gerçek, hafif prosedürel 3B geometridir; taranmış yüksek ayrıntılı silah varlığı değildir.
- Kurt temel dört ayak koşusu 8 m/sn; sol başlangıç rünü +%5 ile 8,4. Klip temposu gerçek hızla birlikte değişir. Gerçek mesafe/zaman ölçümü `dist/run-speed.json` dosyasındadır. Takla hareketi hız bonusundan bağımsız ~1,98 m; temas hasarı, hedef başına bir kez ve siper kontrolü korunur.
- Koşu→sıçrama→iniş/koşu, havada takla, koşu→takla; sıçramada yatay hız bir kez taşınır. Kalkış/iniş mesafesi ayrıca kaydedilir.
- Kükreme pozu boyunca ileri basılı olsa da yatay hareket sıfır. 20 sn hız ×1,20, hasar ×1,15, savunma ×1,30; mor el alevleri ve yüzey dövmesi parlama. Bilge’de gerçek Jaw kemiği, kaynak alt çene ağırlıkları, içeride ağız boşluğu ve üst/alt dişler var. Jaw dönüşü yaklaşık 0,60 radyan. Diğer üç kurtta yeni yüz/çene cilası tamamlanmış sayılmaz.
- Gerçek can, azami can ve savunma hesabı. İsteğe bağlı hedef karşı ateşi bu değerleri kullanır. Savunma bir derecelendirmedir: alınan hasar = ham hasar × 100 / savunma; +%240 savunma doğrudan %240 hasar azaltma değildir. Form değişiminde can oranı korunur.
- Yön düğmeleri, ileri çift basış, yuvarlak simgeli eylemler, doğru dikey bakış, ayarlanabilir hassasiyet, Net/Dengeli, gerçek karakter gölgesi, iz sürme ve tek WebGL bağlamı/iki varlık önbelleği korunur. Laboratuvar ve sıçrama halkası yoktur.

## Tek hesap kaynağı

`gear-system.js` menü, kayıt ve arenanın ortak eşya tablosu / hesaplayıcısıdır.

`Sonuç = Temel × (1 + Karakter/100 + uygulanabilir dövmeler toplamı/100) × Aktif yetenek çarpanı`

Set bonusu bu sürümde **yoktur**. Setler yalnız bağımsız donanım kayıtlarıdır. Aynı ID yalnız bir kez sayılır ve her dövme yalnız tanımlı sırt/sol/sağ yuvasına uygundur. Pasif temel veriye yazılmaz. Eski 180 tavanı kaldırıldı. Örnekler: 100 +%240 = 340; karakter +%20 ile 360; hasar kükremesiyle 414. Gerçek Başıbozuk + Ölüm sırt = 340; gerçek Bilge +%45 + Ölüm sırt +%240 = 385.

| Sırt dövmesi | Bağımsız bonus | Kredi |
|---|---|---:|
| Ejder | Hasar +%60, savunma +%20 | 650 |
| Anka | Can +%100, hasar +%20 | 900 |
| Aslan | Savunma +%120, can +%40 | 1000 |
| Kanatlı At | Hız +%40, can +%20 | 850 |
| Örümcek | Savunma +%60, hız +%20 | 600 |
| Boğa | Can +%160, savunma +%40 | 1100 |
| Kader Zarı | Hasar +%80, hız +%15 | 850 |
| Tekboynuz | Can +%240, savunma +%20 | 1800 |
| Ölüm | Hasar +%240 | 1800 |

| Kol dövmesi | Sol kol | Sağ kol | Her biri kredi |
|---|---|---|---:|
| Ejder | Hasar +%20 | Hasar +%20 | 300 |
| Anka | Can +%35 | Can +%35 | 300 |
| Ölüm | Hasar +%60 | Savunma +%60 | 650 |
| Gök Yazısı | Hız +%5 | Savunma +%15 | 150 |

Farklı uygun yuvaların bonusları toplanır. Aksesuarlar ve pençe izleri kozmetiktir. En güçlü dövmenin hasar veya can bonusu karakter olmadan da +%240’tır; bütün özelliklere birden +%240 verilmez. Başlangıçta eski kuşanılmış Ejder/Gök Yazısı sahipliği korunur.

## Doğrulananlar

- `tools/verify_ui.py`: gerçek tarayıcı; satın alma → owned ızgarası → fare/dokunma → uygun slot → gerçek stat → arena hasarı; yanlış slot ve sahip olunmayan eşya reddi, dolu slot değişimi, çıkar/tak, dört set, 800×360 dokunma, yeniden yükleme, eski kayıt/kredi göçü. 340/360/414 örnekleri ve karakter pasifi olmadan gerçek 340 hasar derecesi.
- `tools/verify_arena.py`: ateş/şarjör, siper/çarpışma, dönüşüm, normal/efsanevi kapıları, çift ileri, ölçülmüş koşu, kısa tek-vuruş takla, havada takla, koşu sıçraması, basılı yönle durarak kükreme, bonus süresi, pençe/VFX, tek bağlam ve sınırlı önbellek, yüksek DPI ve ayar kaydı.
- `verify_motion.py`: dört kurtta beş klibin 25’er örneği; sınır, yer seviyesi, uzuv uzunluğu, döngü dikişi. `capture_model_review.py`: gerçek teslim GLB’sinin ön/yan/arka/üç çeyrek, koşu döngüsü ve takla aşamaları.
- `verify_source_fidelity.py`: özgün Bilge gövde aktarımı ve gerçek çene dönüşü. Klip/UV/iskelet/üçgen bütçeleri APK içinden de okunarak kontrol edilir.

## Açık kalite sınırları

- Kullanıcının son kararı gereği özgün modeldeki yele/kıyafet korunur. Önceki koyu gövde denemesi bir iyileştirme olarak sunulmaz. Kaynağın kürk kümelerinde ve kıyafetinde hâlâ köşeli, üretim kaynaklı yüzeyler bulunur. Tam elle retopoloji ve final sanatçı cilası yapılmış değildir.
- Bilge insanı gerçek 3B, tarihî lacivert/altın kimlikli kaynaktır; malzeme ayrımı ve uzunluğu koruyan rig vardır. Diğer üç insan formu menüde açıkça 2B konsepttir; yeni insan modelleri üretilmedi. Diğer üç kurt kendi mevcut geometrilerini ve ortak koşu/takla sistemini korur.
- Otomatik uzuv kontrolü, her hareketin insan tarafından kusursuz bulunduğu anlamına gelmez. Yüz/diş kapanışı ve ileri deformasyon cilası, özellikle diğer kurtlarda, açık kalır.
- Fiziksel Android telefonunda FPS, bellek/ısınma ve uzun süreli dokunma testi yapılmadı. Performans veya çökmez garantisi verilmez.
- Yeni ücretli üretim ve Meshy harcaması: **0**. Önceki bütçe sınırsız üretim izni sayılmadı.

## Paket

Sürüm 0.1.12, versionCode 13, paket `com.roguebloodmoon.prototype`. Tüm çalışma zamanı dosyaları imzalı tek APK içindedir. ZIP, model paketi veya OBB kurulmaz. Önceki v0.1.11 APK sertifikasıyla SHA-256 karşılaştırması yapılır; yayınlanan varlık ayrıca indirilerek kaynak dosyalar ve imza kontrol edilir.

## Son doğrulama kaydı

Yerel UI ve arena testleri geçti; parça bombası patlama hasarı, bıçak hasarı ve sahipliğin tüketilmemesi de UI akışında doğrulandı. Ölçülen fizik hızı 8,400 m/sn; render-zamanı ölçümü 8,366 m/sn (8 temel +%5 rün). Bilge toplam 14.457, gövde 11.999 üçgen; diğer kurtlar 9.598 / 9.595 / 9.653, Bilge insan 9.000 üçgen.

Görsel ve makine kontrol kayıtları: [oyun envanteri](review-v012/inventory-wolf.png), [insan envanteri](review-v012/inventory-human.png), [özgün biçimi koruyan ön](review-v012/model-front.png), [arka](review-v012/model-back.png), [yan](review-v012/model-side.png), [kaynak aktarımı ölçümü](review-v012/source-fidelity.json), [hareket örnekleri](review-v012/motion-verification.json), [hız ölçümü](review-v012/run-speed.json).

Yerel anahtar önceki yayın sertifikasından farklı çıktı; yerel imzalı dosya kullanıcıya teslim edilmiyor. Yayın CI’si kalıcı anahtar cache’ini kullanır ve v0.1.11 sertifikasının `af43be4b6ee4d5b2e1feca6da3df36805a7b10bbb56b1f884136054ef7f98633` SHA-256 değeriyle eşleşmeyen APK’yı yayımlamaz. Yayımlanan APK ayrıca indirilerek karşılaştırılacak.
