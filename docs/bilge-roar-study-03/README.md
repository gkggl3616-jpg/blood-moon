# Bilge kükreme 03 — Blender MCP, Rigify, Rokoko ve gerçek oyun görünümü

İlk seçilen ücretsiz araç zinciri kuruldu ve kullanıldı. Bu çalışma, Bilge'nin onaylanan beyaz modelini değiştirmeden yeni kontrol iskeleti, yeniden düzenlenen deri ağırlıkları, tam referans zamanlaması ve efektli oyun önizlemesi sağlar. **Bu bir inceleme çalışmasıdır; yayımlanmış Android oyununa henüz uygulanmadı.**

- [Tam referansla karşılaştırma](comparison.mp4): kaynağın bütün kadrajı ve 38 karesi, iki normal / bir yarım hız tekrar. Son toparlanma kesilmez.
- [Ön / yan, efektli tam klip](front-side.mp4).
- [Efektsiz ön](deformation-front.jpg) ve [efektsiz yan](deformation-side.jpg): alev olmadan eklem kontrolü.
- [Kare çizelgesi](reference-frames.md), [kaynak ana pozları](reference-poses.jpg), [yeni ana pozlar](key-poses.jpg).
- Düzenlenebilir gerçek kaynak: `art/3d/animation-studies/bilge-roar-study-03.blend`.
- Dışa aktarılan gerçek oyun modeli: `art/3d/animation-studies/bilge-roar-study-03.glb`.

## Yapılanlar

**Araç bağlantısı:** Blender MCP 2.2.4 kuruldu, Codex MCP kaydı eklendi, Blender 4.3.2 GUI sahnesiyle yerel bağlantı doğrulandı. Sahne bilgisi, görüntü ve sahne düzenleme gerçekten MCP üzerinden yapıldı. Rigify etkin; resmî Rokoko 1.4.3 yerel retarget işlemi `FINISHED` döndü. Ayrıntılar [araç notlarında](../../tools/mcp/README.md), gerçek yanıt [MCP raporunda](audits/mcp-native-status.json). Yeni ücretli üretim/abonelik veya kredi harcaması yapılmadı.

**Kare çalışması:** Ana kaynak kullanıcının tam `08-04-29-656.mp4` kaydıdır. 38 görüntü, 1,671792 sn konteyner süresi; son gerçek görüntü zamanı 1,522 sn. Açılma → yükseliş → tepe/tutuş → indirme → toparlanma → son duruş ayrı anahtarlandı. Klip 30 kare/sn, 0–51, 1,7 sn. Eski kısa video seçimi kullanılmadı. Kayıt zaten kollar açılmışken başladığı için görünmeyen hazırlık kaynaktan ölçülmüş gibi sunulmaz.

Pozlar bütün kareler incelenerek **elle yorumlanan 3B tahminlerdir**. MCP veya Rokoko'nun MP4'ten otomatik, kesin kurt mocap'i çıkardığı iddia edilmez. Kamera hareketi, uzak kolun örtülmesi ve tek görüşte derinlik belirsizliği vardır. Kaynak ve hedef kameraları tam kalibre değildir.

**İskelet ve ağırlıklar:** Bilge eklem merkezlerine oturtulmuş Rigify iskeleti 237 toplam kemik / 40 deformasyon kemiği içerir. Omuz, kol, ön kol, el, parmak, boyun/baş ve gerçek alt çene ayrı kontrol edilir. Kollar FK, ayaklar destek için IK; kol/bacak esnetmesi kapalı. Orijinal gövde köşe koordinatları ve UV'leri değişmedi. Renkli bir konsept görseli 3B model yerine kullanılmadı.

Keskin gövde/ön kol ağırlık sınırları, komşu yüzeyleri farklı kemiklere atayarak uzun şeritler üretiyordu. Anatomik bölgeler yumuşatıldı, yakındaki parçalı yüzeyler arasında ağırlık alanı düzeltildi. Oyun için dört pozitif etkiyle dokuz örnek poza uyan bir ağırlık uyarlaması yapıldı. Yeni poligon eklenmedi. Dört etkiye indirgeme kusursuz değildir: gövdede yumuşak çalışma alanına göre en büyük fark yaklaşık **17,3 mm**, %99 dilimi yaklaşık **4 mm**; kolların dövmelerinde yerel hata yaklaşık **15 mm'ye kadar** çıkabilir. Bunlar yeni oyunun referansla eşleşme ölçümü değildir; ağırlık yaklaşımının sınırıdır.

**Aktarım:** Blender'a özgü B-Bone/preserve-volume davranışına dayanılmadı. Yalnız 40 sıradan deformasyon eklemi, örneklenmiş yerel dönüşlerle GLB'ye aktarıldı. Kontrol iskeleti .blend içinde kalır. Dışa aktarılan eklemler, miras alınan kayma matrislerini önlemek için düz bir kök düzeninde örneklenir; düzenlenebilir kontrol zinciri yerine oyun oynatma verisidir. İçe aktarma yardımcısı olan kemik gösterim küresi ve Rigify widget'ları modelden ayrıldı. GLB'de yalnız **WolfRoar / 1,7 sn** bulunur; diğer hareket klipleri henüz yeni iskelete geçirilmedi.

**Efektler:** Bilge için camgöbeği el alevleri, mor kenar vurguları, tepe anında parçacık patlaması ve deriyi izleyen dövme parlaması eklendi. Oyunun mevcut 72 parçacık havuzu ve altı küçük alev yüzeyi kullanılır; parıltı tüm gövdeyi örtmez. Renk parametresi ortak hareketi değiştirmez. Blender çalışma sahnesinde ayrıca geç enerji çizgisi taslağı vardır; Three.js önizlemesi el alevi, patlama ve dövme parlamasını gösterir. Kaynaktaki diğer oyuncu ve geniş yeşil bulutun tamamı öznenin el efektiymiş gibi kopyalanmadı.

## Test edilenler

- Üç kamera açısından **156 gerçek Three.js karesi**; shader/JavaScript hata listesi boş. Görüntü tamponu 960×960. El kemikleri bulunuyor, altı alev yüzeyi çalışıyor; parçacık sayısı 72 sınırını aşmıyor.
- Klip süresi yeniden yüklenen GLB'de yaklaşık 1,70000005 sn. Kaynak .blend ile sade deformasyon iskeleti arasındaki örneklenmiş gövde farkı yaklaşık 0,003 mm'den az.
- **GLB yeniden içe alındığında**, 11 örnek karede en büyük gövde sapması yaklaşık **0,266 mm**. Bu uyumluluk testidir; görsel kalite onayı değildir. Testte içe aktarmadan önce 30 kare/sn ayarlanır.
- Ayak bileği desteği örneklenir; üst kol/ön kol uzunluk değişimi çok küçük sayısal tolerans içindedir. Son rapor [poz denetiminde](audits/pose-audit.json).
- Her iki MP4 H.264 / 30 kare/sn / 267 kare / 8,9 sn, bütün kareleri çözümlendi. 38. kaynak görüntünün eski kesim sonrasında gerçekten bulunduğu piksel karşılaştırmasıyla doğrulandı: [video testi](video-verification.json).
- Aynı model ve iskelet ön, yan, arka üç çeyrek görüntülerde kullanıldı. [Tarayıcı raporu](audits/browser-audit.json), [ağırlık yaklaşımı](audits/four-weight-fit.json), [dışa aktarım](audits/export-audit.json), [yeniden yükleme](audits/roundtrip-audit.json).

## Henüz tamamlanmayanlar

Görsel olarak birebir eşleşme veya profesyonel son kalite iddia edilmiyor. Orijinal modelin parçalı/sivri kürk ve omuz topolojisi korunmuştur; bunun kendisi temiz yeniden topolojiye dönüşmedi. Koltuk altı/omuz hacmi, bilek/parmak biçimi, baş-boyun yaylanması ve dövmenin yerel yüzey uyumu hâlâ sanatçı düzeltmesi gerektirir. İyileşen aktarım bu kusurları otomatik çözmez. Efektsiz resimler bu yüzden eklendi.

Beklemeden ilk açık poza giriş, kükremeden koşu/sıçramaya dönüş, diğer hareketlerin yeni iskelete taşınması, diğer kurtlara oran uyarlaması, ana oyuna yerleştirme ve Android cihaz testi açıktır. Mevcut insan/kurt dönüşümü ve envanter kayıtları değiştirilmedi. Çalışma, kullanıcının ana kapsamındaki bütün envanter/model işleri tamamlandı anlamına gelmez.

Bu inceleme dalında APK üretilmedi veya yayımlanmadı. Telefon FPS'i ve çökmezlik garantisi verilmez. Yeni ücretli üretim gerekirse ayrı, somut kapsam/maliyet belirtilmelidir; eski bütçe yeniden kullanılmaz.

## Yeniden üretim / etkileşimli inceleme

GUI Blender ve MCP sunucusu açıkken, depo kökünden:

```sh
uv run --no-project --with mcp-for-blender==2.2.4 python tools/mcp/blender_live.py execute-file art/3d/animation-studies/build_rigify_roar.py
uv run --no-project --with mcp-for-blender==2.2.4 python tools/mcp/blender_live.py execute-file art/3d/animation-studies/optimize_game_weights.py
uv run --no-project --with mcp-for-blender==2.2.4 python tools/mcp/blender_live.py execute-file art/3d/animation-studies/add_roar_effects.py
blender --enable-autoexec -b -t 2 --python art/3d/animation-studies/export_rigify_roar.py
cp dist/roar-study-03/bilge-roar-study-03.glb art/3d/animation-studies/bilge-roar-study-03.glb
tools/viewer/node_modules/.bin/esbuild tools/viewer/study03.js --bundle --format=esm --outfile=dist/roar-study-03/player.js
python tools/capture_roar_study03.py
python art/3d/animation-studies/compose_rigify_roar.py
blender --enable-autoexec -b -t 2 --python art/3d/animation-studies/verify_roar_glb.py
python art/3d/animation-studies/verify_full_reference_comparison.py --study03
```

Kare karşılaştırma araçları bu oturumdaki `/workspace/reference-review/roar-full-080429` çıkarımlarını kullanır; kaynak özgün MP4 önceki çalışma 02'nin `reference-full/original.mp4` dosyasında korunur. Eksik çıkarımlar tam kaynaktan yeniden, bütün kareler ve zaman damgalarıyla hazırlanmalıdır.

`python -m http.server 8000` ile depo kökünü açıp `/tools/viewer/study03.html` adresinde oynat/duraklat, zaman sürgüsü, kamera ve efekt anahtarları kullanılabilir. Bu inceleme sayfası Android oyuna eklenen bir laboratuvar değildir. Yeni bir ortamda önce `tools/viewer` bağımlılıkları kurulup esbuild adımı çalıştırılmalıdır.
