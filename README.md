# Rogue: Blood Moon — Android Prototype 0.1.11

Yatay Android ekranı için menü ve harita konsepti prototipi.

v0.1.3: Açılış videosu otomatik başlar ve bitince lobiye geçer. Görünür ekran alanına göre ölçekleme, sabit viewport ve Android çentik/sistem çubuğu güvenli alanları eklendi.

## v0.1.4 — karakter ve mekanik yönü

- Envanter, deneme mağazası, insan/kurt bonus karşılaştırması ve kalıcı karakter seçimi.
- Bilge Kağan, Kül Tigin, Alp Arslan ve Konuralp’ten esinlenen kurgu karakter kartları.
- Kurt güç endeksi 100–180; kurt bonusları 0–%80 ile sınırlanır. Bunlar taslak değerlerdir.
- Her gövde tipi için ayrı pençe hareketi ve iz tarifi tutulur; 3B animasyon uygulanmadı.
- İz sürme korunur; ileri sıçrama için hedef alanı göstergesi kullanılmaz.
- Yetenek laboratuvarı kaldırıldı. Yeni 3B mekanikler hâlâ tasarım aşamasındadır.
- Higgsfield konseptleri prototypes/ klasöründedir; oyun içi kartlar henüz temsilîdir.

## v0.1.5

Kurt donanımında koşu ve takla ayrı kuşanılır; kozmetik aksesuar seçimi kaydedilir. Kükreme 20 saniye boyunca %20 hız, %15 hasar, %30 savunma sağlar; 2B dövme şeması parlar. Pasif değerler kükreme dahil toplam 180 tavanına göre ayarlanır. Koşu önizlemesi %15 koşu bonusu kullanır. Bunlar henüz 3B savaş animasyonları değildir. Silah, bomba ve bıçak katalog kategorileri eklendi. Bilinen hata kaydı: GELISTIRME_HATALARI.md.

## v0.1.6 — İlk gerçek 3B kurtlar

Meshy text-to-3D kaynak modelinden Blender’da dört gövde varyantı oluşturuldu. Donanım ekranı solda sürükleyerek dönen model, sağda dövme/ekipman listesi şeklindedir. Sırtta altı özgün motif, sağ ve sol kollarda ayrı çizgi katmanları, aksesuar seçimi ve kükreme emisif malzemesi vardır. Motifler final UV dövme sanatı değil, düzenlenebilir başlangıç çizgi geometrileridir.

Blender dosyası: `art/3d/wolves-modular.blend`. GLB dosyaları: `app/src/main/assets/models/`. Gerçek üçgen sayıları: `art/3d/model-report.json`. Meshy görevleri ve gerçek tüketim: `art/3d/task-trail.json` (toplam 30 kredi). Modeller A-pozunda; rig/koşu/takla/savaş animasyonu tamamlanmadı.

TikTok sayfası ve kapak karesi incelendi; video akışı 403 döndüğü için tamamı izlendiği iddia edilmez. Yüklenen dövme örneğinin yerleşimi referans alındı; oyun varlıkları kopyalanmadı.

## v0.1.7 — Mağazadan alınan takla özellikleri

- **Kurt Taklası:** 450 deneme kredisi, yalnızca takla. Dört ayak koşu açmaz; takla temas hasarı verir (v0.1.10 kuralı).
- **Efsanevi Kurt Taklası:** 1.200 deneme kredisi, dört ayak koşu ve takla birlikte. Tek takla yuvası kullanır.
- Mağaza → Kurt Özellikleri bölümünden satın alındıktan sonra Kurt Donanımı → Takla Yuvası bölümünde kuşanılır ve kaydedilir. Her kurdun seçimi ayrı tutulur; satın alma otomatik kuşanma yapmaz. Bu sürüm önceki ücretsiz koşu/takla kutularının yerini alır.
- Mevcut dört Meshy/Blender gövdesine Blender’da 22 kemikli başlangıç rig’i ve `WolfIdle`, `WolfRoll`, `WolfRunQuad` klipleri eklendi. Düğmeler tüm modelin CSS dönüşünü değil, GLB içindeki iskelet animasyonunu oynatır. Koşu döngüsü durdurulabilir; takla bitince önceki uygun duruşa döner.
- Düzenlenebilir kaynak: `art/3d/wolves-rigged.blend`; üretim betiği: `art/3d/scripts/animate_wolves.py`; klip/kemik kaydı: `art/3d/animation-report.json`. Bu aşamada yeni Meshy üretimi ve kredi tüketimi yoktur.

Bu hareketler donanım ekranındaki ilk 3B önizlemelerdir. Ağırlıklar geometrik yöntemle atanmıştır; özellikle omuz, kalça ve kürkte elle deformasyon düzeltmesi gerekir. Haritada ilerleme, çarpışma, saldırı ve çevrimiçi maç henüz uygulanmadı. Tarayıcı testi satın alma/kuşanma ayrımını, kalıcı kaydı ve klip oynatmayı doğrular; fiziksel Android cihazda oynanış testi değildir.

## v0.1.8 — Atletik gövdeler ve ayrıntılı dövmeler

Dört gerçek gövdenin beli ve karın derinliği yeniden biçimlendirildi. Ağır varyantların hacmi omuz/göğüste korunur. Bel daraltması yalnızca gövde bölgesine uygulanır; ön kolları ve elleri sıkıştırmaz. Her varyantın oranları, boyu ve ölçülen gövde kesitleri `art/3d/model-report.json` içindedir. Kaynak Meshy modeli korunarak Blender'da düzenlendi; yeni Meshy üretimi ve kredi tüketimi yoktur.

Gövde LOD'si 18.000'den 28.000 üçgene çıkarıldı. Dokuz ayrıntılı, özgün sırt dövmesi: ejder, anka, aslan, kanatlı at, örümcek, boğa, kader zarı, tekboynuz ve ölüm. Kaynak sayfa `art/3d/textures/tattoo-atlas.png`, UV bölmeleri aynı klasördeki JSON dosyasıdır. Dövmeler görüntü üretimiyle hazırlanan şeffaf renk/emisyon dokularını kullanır; referans oyundan doku dosyası alınmadı. Her dövme gerçek gövde yüzey üçgenlerini izleyen ayrı bir mesh'tir. Sol ve sağ kol bağımsız olarak kanat şeridi, ejder, anka veya ölüm deseni seçer. Kükreme bu renkli mürekkepleri parlatır.

Dövme iskelet ağırlıkları gövdenin en yakın üçgeninden ara değerleme ile aktarılır. İlk rig ve üç hareket klibi korunur; final üretim topolojisi, yüz ifadesi ve deformasyon cilası henüz tamamlanmadı. Bu bir kalite geliştirme geçişidir; nihai AAA model iddiası yoktur. Yedi karakter hâlâ dört temel geometriyi paylaşır.

## v0.1.9 — oynanabilir düz test alanı

Yeni Bilge Kağan insan/kurt çifti Meshy image-to-3D ile üretildi; onaylanan ve tüketilen toplam 60 kredi. Diğer altı insan/kurt referansı 2B konsepttir, yeni ücretli üretimleri yapılmadı. Bilge bu geliştirme sürümünde başlangıç envanterine dahildir. Oyun LOD'ları insan 9.000, Bilge kurt 13.773 üçgen; diğer üç kurt 10 bin üçgenden az. İnsan FPS, kurt TPS, dönüşüm, ileri sıçrama, ortak dört ayak koşu/takla, pençe klipleri ve vuruş efektleri düz alanda denenir. Hedeflerin canı azalır ve 3 saniyede yenilenir. Deneme donanımı mağaza sahipliğini değiştirmez.

Sol dört yön düğmesi; ileriye 330 ms içinde iki basış efsanevi özellik takılıysa koşuyu açar. Sağda simgeli yuvarlak eylemler. Klavye WASD, E dönüşüm, Q takla, Shift koşu, Space sıçrama, F saldırı, R kükreme/şarjör, T iz sürme. Sağ ekranı sürüklemek bakışı değiştirir. Kükreme 20 saniye, mor el alevleri ve dövme parlaması; 180 tavanı korunur. Tek WebGL context, iki kayıtla sınırlı model cache'i, 72 parçacık havuzu, karakterden düşen 1024 PCF gölge kullanılır.

Tek APK release varlığı bütün çalışma zamanı dosyalarını içerir; ek model/OBB/ZIP kurulumu yoktur. Actions imza sırrı yazma yetkisi 403 verdiği için geliştirme imzası cache ile korunur; üretim imzası kurulmuş değildir. Fiziksel Android testi ve çevrimiçi maç yoktur. Deformasyon ve yüz cilası geliştirme aşamasındadır. TikTok sayfalarına erişildi, yeni akış 403 verdi; yüklenen yerel referans videolarının kareleri incelendi.

## v0.1.10 — takla teması ve bakış düzeltmesi

Takla temas hasarı verir: 38 taban hasar, karakter hasar değeri/kükreme çarpanı ve 180 tavanıyla ölçeklenir. Bu yerel denge ayarıdır; yeni YouTube videosundan ölçülmüş değer değildir. Süpürülen gövde teması, hedef başına taklada bir vuruş, siper engeli, sabit takla yönü kullanılır. Koşu/takla dört kurtta ortak v2 şablonu; taklada hazırlık–toplanma–360 dönüş–iniş, kükremede hazırlık–açılma–tutma–toparlanma vardır. Çene kemiği/yüz animasyonu henüz yoktur. İnsan ve kurt dikey sürüklemesi aynı yönde düzeltilmiştir.

Yeni video `https://youtube.com/shorts/NGqOn5o0dHE` ortam ağ geçidinde 403 ile engellendi; tamamı izlenmedi. Zaman kodlu içerik analizi bekliyor. Önceki erişilebilir referanslar ile kullanıcı düzeltmesi ayrı kaynak olarak kaydedildi: `docs/video-NGqOn5o0dHE.md`. Yeni ücretli model üretimi yok; mevcut düşük poligonlu modeller ve yerel Blender rig'i düzenlendi.

## v0.1.11 — yüklenen hareket kaydı ve görüntü netliği

Yüklenen 4.91 saniyelik videonun 119 karesi zaman sırasıyla incelendi. Ayrıntılı gözlemler ve uygulama kararları `docs/video-screenrecorder-20261027.md` içinde. Ortak v3 koşu/duruş iki kemikli IK ile kol/bacak uzunluklarını korur; yere basma ve toparlanma fazları, daha sabit baş ve kısa döngü kullanır. Takla 0.8 saniye / yaklaşık 2m; temas hasarı korunur. Koşarken sıçrama/takla, havada taklaya geçiş ve kükremede durma test edilir. Sıçramada koşu hızına ikinci bir yatay hız eklenmez.

1.25 DPR sınırı kaldırıldı. Net varsayılanı ekran piksel yoğunluğunu 4.2M piksel bütçesi içinde izler; Dengeli 2M bütçe kullanır. Kenar yumuşatma ve 8x'e kadar doku filtreleme korunur, aşırı parlak ışık azaltılır. Hassasiyet ekran genişliğine göre normalize edilir; varsayılan 1.45x, ayarlardan 0.60–2.40x. Tercihler kalıcıdır. Poligon ve parçacık bütçeleri değişmez; fiziksel telefon performansı henüz ölçülmedi. Yeni Meshy kredisi harcanmadı.
