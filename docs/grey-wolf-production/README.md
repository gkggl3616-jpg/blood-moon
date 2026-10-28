# Referansa sadık yeni kurt — gerçek kaynak modeli

## Güncel durum — 2026-10-28

Kullanıcının yüklediği `MASTER-PROMPT-TR.md` depo kopyasıyla aynı içerikte doğrulandı. "Promptu oku ve Başla" talimatıyla daha önce fiyatı belirtilen **15 kredilik tek kurt** üretimi başlatıldı ve tamamlandı. Ayrı insan modeli, ücretli rigging, animasyon, varyant veya ücretli tekrar başlatılmadı.

- Kaynak görsel: [doğal el/ayak referansı](../../art/characters/grey-wolf-production/fullbody-natural-pose.png). Önceki açık parmaklı tam boy A-pozu kabul edilmiş hedef değildir.
- İşlem: `image-to-3d`, görev `01a18237-eaff-7570-ada6-a9738305ab6b`.
- Gerçek tüketim **15 kredi**; doğrulanan bakiye **950 → 935**. Kayıt: [balance-check.json](balance-check.json).
- Gerçek sonuç: **14.749 üçgen**, UV, 2K PBR; **iskelet ve animasyon yok**. Menü/arena entegrasyonu henüz tamamlanmadı.
- [İndirilen gerçek GLB](../../art/characters/grey-wolf-production/grey-wolf-source.glb) değişmeden korunuyor. SHA256: `1be2ec0d973881cdd8c3d7f459e348f063bcdb8e909c82e308fb0c37ce89ac6b`.
- [Düzenlenebilir Blender çalışma dosyası](../../art/characters/grey-wolf-production/working/grey-wolf-working.blend) ve [çalışma GLB'si](../../art/characters/grey-wolf-production/working/grey-wolf-working.glb) hazırlandı. Bunlar tamamlanmış animasyonlu oyun varlığı değildir.
- Ayrıntılı görev/kapsam kaydı: [prepared-job.json](prepared-job.json). Ham Meshy görev JSON'ları imzalı indirme adresleri içerdiğinden yayımlanmaz.

## Yapılan hazırlık ve teknik doğrulama

`tools/prepare_character_source.py`, orijinali değiştirmeden çalışma kopyası oluşturur. Yalnız tam çakışan aktarım köşeleri birleştirildi: Blender mesh köşeleri 13.885 → 9.640; **bütün 14.749 üçgen ve 44.247 yüz köşesinin UV/malzeme verisi korundu**, kaynak köşe konumları değişmedi. Bu sayı GPU'da aynı köşe sayısı kullanılacağı anlamına gelmez; GLB, UV ve normal sınırlarında yeniden bölebilir.

Daha geniş `1e-5` birleştirme denemesi küçük bir üçgeni kaldırdığı için çalışma kopyasına uygulanmadı. Yüzeyler körlemesine kapatılmadı. Ham GLB'deki açık kenar sayısının tamamı gerçek delik sayılamaz: UV/normal sınırları ve ayrı kürk/ağız parçaları vardır. Daha geniş tanısal birleştirme sonucu yalnız inceleme raporunda tutulur.

Özel yüz köşesi normalleri aktarıldı; Blender'ın yeniden kodlamasındaki en büyük vektör sapması `0.00294` (yaklaşık 0,17°). Çalışma modeli **2,4 m**, ayak tabanı **Z=0**, ön yön **-Y** olacak şekilde düzenlendi. Dokular `.blend` içine paketlendi. GLB dışa aktarılıp yeniden açıldı: boy `2.400000095 m`, taban `0`, UV ve dokulu malzeme mevcut. İskeletten/animasyondan yoksun olduğu kontrol edilip raporda açıkça işaretlendi.

Kanıt: [preparation-report.json](../../art/characters/grey-wolf-production/working/preparation-report.json). Tekrar üretilebilir komut:

```sh
blender --factory-startup -b -t 2 --python-exit-code 1 \
  --python tools/prepare_character_source.py -- \
  art/characters/grey-wolf-production/grey-wolf-source.glb \
  art/characters/grey-wolf-production/working
```

`tools/inspect_generated_character.py` gerçek GLB'yi açıp ön/arka/yan/üç çeyrek görüntüleri üretir; konsept görseli render yerine kullanılmaz. Kamera yalnız boya göre değil, görünen bütün köşelere göre ayarlanır; açık kollar ve eller kadrajdan kesilmez. [Çalışma modeli inceleme görüntüleri](../../art/characters/grey-wolf-production/working/review) aynı dışa aktarılmış dosyadan oluşturulur.

## Görsel olarak açık kalan işler

Gerçek modelin ön ve yan görüntüleri incelendi. Yüz, kaslı gövde, gri kürk, kamuflaj pantolon, kemer, kılıf ve kahverengi sargı onaylı yönle önceki beyaz prototipten daha uyumlu. Bu karşılaştırma modelin nihai kabulü değildir.

- Teknik A-pozunda eller hâlâ fazla açık. Doğal yarı kapalı bekleme pozu ve parmak kontrolü hazırlanmalı.
- Yele özellikle yan silüette hâlâ iri ve sivri; kontrollü kürk kümelerine indirilmeli.
- Gövdenin yanındaki küçük açıklıklar, ağız/diş parçaları ve gerçek çene ayrımı incelenmeli. Ayrı çene hareketi henüz yapılmadı.
- Omuz, dirsek, bilek, kalça ve diz bükülmeleri için yeni iskelet, ağırlıklar ve hareket testleri yapılmadı.
- `WolfIdle`, `WolfWalk`, `WolfRunQuad`, `WolfRoar`, `WolfRoll`, `WolfJump`, `WolfClawRight/Left` yeni modele ait hazır klipler değildir.
- Menü ve arena aynı son rigli GLB'yi kullanmalı; dört açı ve hareketin tüm fazları kontrol edilmeli.
- Yeni APK yayımlanmadı; mevcut yayımlanan sürüm değiştirilmedi.

## Orijinal karakter dosyalarıyla devam etme

Kullanıcı orijinal Wolfteam karakter dosyalarını yüklemeyi önerdi. İskeleti, kemik ağırlıkları ve özgün klipleri içeren kaynak dosyalar, video karelerinden yeniden hareket tahmininden çok daha doğrudan bir çalışma zemini sağlar. Dosya gelmeden içeriği veya sorunsuz aktarılacağı varsayılmaz. Yeni ücretli üretim bu öneriyle otomatik olarak yetkilendirilmiş sayılmaz.

Tercih edilen içerik ve aktarım sırası [ORIGINAL-ASSET-IMPORT-TR.md](ORIGINAL-ASSET-IMPORT-TR.md) içinde kaydedildi. İlk denemede model, özgün iskelet/ağırlık/klipleriyle beraber açılacak; kolları bozan eski rig veya elle yazılmış pozlar üzerine hemen bindirilmeyecek. Yerel model doğru, oyun görünümü bozuksa koordinat, bind/rest matrisleri, animasyon karışımı ve GLB aktarımı incelenecek.

## Korunan oyun kodu ve mevcut doğrulamalar

Bu kaynak model hazırlığı oyun içi donanım, sahiplik, kredi veya kayıt verilerini değiştirmez. Önceki turda yapılan ortak sistem işleri:

- `tools/viewer/claw-combo.js`: yalnız kabul edilen vuruşlarda sağ/sol sırası ilerler. Yeni modelin özel sağ/sol klipleri korunur. Eski çift kollu `WolfClaw` için karşı kol izlerini çıkartan uyumluluk maskesi vardır; yeni profesyonel klip yerine geçmez.
- Arena uygun tarafın klibini ve pençe izini kullanır; tek temas/tek hasar ve siper kontrolü korunur.
- `motion.js`: `WolfWalk/HumanWalk` ve `walk_stride_m` desteklenir; gerçek ilerleme hızıyla klip süresi ilişkilendirilir. Eski 3,6 m/sn kalibrasyon uyumluluğu yeni gerçekçi yürüyüş sayılmaz.
- İnsan birinci şahıs el/silah salınımı yerde kat edilen mesafeden faz alır; duruşta/havada söner. Bu, tam beden yürüyüşü değildir.
- `node tools/test_walk_contract.mjs`, `node tools/test_claw_combo.mjs` ve gerçek arena üzerinde `python tools/verify_claw_combo.py` geçti. [claw-combo-test.json](claw-combo-test.json) eski varlıklarla ortak davranışları doğrular; yeni Meshy kurdunun animasyon onayı değildir.

## Brifler, insan formu ve bütçe sınırı

[Ana Türkçe prompt](MASTER-PROMPT-TR.md), [İngilizce model brifi](../../art/characters/grey-wolf-production/MODEL-PROMPT-EN.txt), [negatif prompt](../../art/characters/grey-wolf-production/NEGATIVE-PROMPT.txt) ve ayrı 600 karakterlik doku promptu üretim/kabul kapsamını taşır. Image-to-3D genel geometri promptu almadığından bütün metin bir API parametresiymiş gibi sunulmaz.

[İnsan karşılığı referansı](../../art/characters/grey-wolf-production/human-counterpart-reference.png) ve [brifi](../../art/characters/grey-wolf-production/HUMAN-PROMPT-EN.txt) hazırdır; **2B konsepttir, rigli 3B insan değildir**. Ayrı ücretli üretimi başlatılmadı.

İlk istek `remove_lighting` seçeneğinin Smart Topology'de desteklenmemesi nedeniyle HTTP 400 ile reddedildi; görev oluşturulmadı, bakiye 950 kaldı. Aynı işlem anahtarıyla farklı gövde reddedildikten sonra, yalnız desteklenmeyen seçenek çıkarılarak ayrı düzeltilmiş işlem kaydıyla tek faturalı görev oluşturuldu. Gerçek tüketim 15'tir. CLI cihaz oturumu `NODE_USE_ENV_PROXY=1` ile mevcut proxy/CA güveni korunarak tamamlandı; kimlik bilgileri okunmadı veya yayımlanmadı.
