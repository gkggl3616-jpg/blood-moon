# Rogue: Blood Moon — Android Prototype 0.1.7

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

- **Kurt Taklası:** 450 deneme kredisi, yalnızca takla. Dört ayak koşu veya ek saldırı hasarı vermez.
- **Efsanevi Kurt Taklası:** 1.200 deneme kredisi, dört ayak koşu ve takla birlikte. Tek takla yuvası kullanır.
- Mağaza → Kurt Özellikleri bölümünden satın alındıktan sonra Kurt Donanımı → Takla Yuvası bölümünde kuşanılır ve kaydedilir. Her kurdun seçimi ayrı tutulur; satın alma otomatik kuşanma yapmaz. Bu sürüm önceki ücretsiz koşu/takla kutularının yerini alır.
- Mevcut dört Meshy/Blender gövdesine Blender’da 22 kemikli başlangıç rig’i ve `WolfIdle`, `WolfRoll`, `WolfRunQuad` klipleri eklendi. Düğmeler tüm modelin CSS dönüşünü değil, GLB içindeki iskelet animasyonunu oynatır. Koşu döngüsü durdurulabilir; takla bitince önceki uygun duruşa döner.
- Düzenlenebilir kaynak: `art/3d/wolves-rigged.blend`; üretim betiği: `art/3d/scripts/animate_wolves.py`; klip/kemik kaydı: `art/3d/animation-report.json`. Bu aşamada yeni Meshy üretimi ve kredi tüketimi yoktur.

Bu hareketler donanım ekranındaki ilk 3B önizlemelerdir. Ağırlıklar geometrik yöntemle atanmıştır; özellikle omuz, kalça ve kürkte elle deformasyon düzeltmesi gerekir. Haritada ilerleme, çarpışma, saldırı ve çevrimiçi maç henüz uygulanmadı. Tarayıcı testi satın alma/kuşanma ayrımını, kalıcı kaydı ve klip oynatmayı doğrular; fiziksel Android cihazda oynanış testi değildir.
