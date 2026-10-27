# v0.1.13 doğrulama kanıtları

Bu klasör gerçek dışa aktarılmış varlıkların ve gerçek WebGL oyununun ölçümlerini içerir. Fiziksel telefon testi değildir.

- `source-fidelity.json`: onaylı Bilge gövdesi / çalışma zamanı bekleme pozu koordinat farkı.
- `motion-verification.json`: dört kurtta klipler, deforme mesh sınırları, uzuv uzunlukları ve döngü birleşimi.
- `reference-motion-verification.json`: dört kurtta destek taban yüksekliği, sanal köke göre destek kayması, gövde/uzuv uzunlukları, kumaş–el ağırlığı ayrımı, baş üstü eller ve gerçek çene/ağız.
- `reference-arena-verification.json`: gerçek oyun mesafe/zamanı, adım–mesafe eşleşmesi, yayılan parçacığın RGB'si, kükremede hareketsizlik ve menü temposu.
- `run-speed.json`: genel arena regresyonunun bağımsız hız ölçümü.
- `published-apk.json` ve `apk-badging.txt`: yayımlanmış dosya yeniden indirilerek imza/sürüm/52 varlık doğrulaması; eski APK ile aynı sertifika.
- `test-status.json`: yapılmış kontroller ve açık fiziksel cihaz testi.
- `review13-collage.jpg`: çalışma zamanı Bilge modelinin ön/arka bekleme, koşu, kükreme ve takla örnekleri.
- `four-runs13.jpg`: dört çalışma zamanı GLB'sinde aynı koşu fazları.
- `four-roars13.jpg`: üst sırada gerçek GLB, alt sırada gerçek oyunun karakter renkli el efektleri. Alt görüntüler farklı kare yakalama zamanlarıdır; zaman serisi karşılaştırması değildir.

Üretim/test komutları (Blender 4.3.2; Python Playwright 1.58.0 ve Chromium):

```sh
blender -b -t 2 --python art/3d/scripts/animate_wolves.py
blender -b -t 2 --python art/3d/scripts/verify_source_fidelity.py
blender -b -t 2 --python art/3d/scripts/verify_motion.py
blender -b -t 2 --python art/3d/scripts/verify_reference_motion.py
npm run build --prefix tools/viewer
python tools/verify_reference_arena.py
python tools/verify_arena.py
python tools/verify_ui.py
```

İlk komut, eksik yerel statik girdileri depodaki onaylı sahneler / mevcut GLB bağlama geometrisinden yeniden oluşturur. Kaynak yedekleri tek başına APK'nın bir parçası değildir; gerekli çalışma zamanı GLB'leri APK'nın içindedir. Raporlardaki faz örnekleri sınırlıdır; sıfır hata veya belirli telefon FPS'i garantisi verilmez.
