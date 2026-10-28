# Bilge kükreme çalışması 02 — tam referans ve toparlanma

Kullanıcı, çalışma 01 karşılaştırmasının kükreme bitmeden kesildiğini belirtti: önceki seçime yaklaşık 0,5 saniye daha eklenmeliydi. Ardından `Screenrecorder-2026-10-28-08-04-29-656.mp4` dosyasını tam sürüm olarak gönderdi. Bu son dosya yeni ana referanstır. Önceki 1,320–2,438 sn kaynak seçimi kullanımdan kaldırıldı.

## Referansın korunması

Yeni dosya 1,671792 sn; 38 görüntü karesi, son gerçek görüntü zamanı 1,522 sn. Kaydın başı/sonu ve bütün kadrajı korunur. Son görüntü ses/konteyner kuyruğu boyunca tutulur; olmayan yeni hareket kareleri üretilmez. [Özgün dosya](reference-full/original.mp4) yüklemeyle bayt bayt aynıdır. [H.264 uyumlu kopya](reference-full/full-frame-h264.mp4) 38 kareyi, sesini ve en-boy oranını korur.

`comparison.mp4` bütün 38 kareyi içerir. Normal hız iki tekrar, yarım hız bir tekrar; etiketler görünürdür. Karşılaştırma sessizdir. Referansın başka karakterleri ve yeşil efekti kaynak görüntünün parçasıdır; Bilge çalışmasına eklenmedi. İlk çalışma gibi dar bir zaman seçimi veya karakter kırpması yoktur. Kaydın gerçek zaman damgaları kullanılır; pozları eşlenmiş göstermek için zaman bükülmez.

## Bilge çalışmasındaki düzeltme

- Klip 1,2 sn yerine 1,7 sn, 0–51 kare aralığına alındı. Son toparlanma ve yerleşme artık döngü sıfırlamasıyla kesilmiyor.
- Yeni kayıt kollar zaten açılmışken başlıyor. Bu nedenle çalışma aynı görünür pozdan başlar; kayıtta görünmeyen bir hazırlık bölümü kaydın parçasıymış gibi eklenmez. Oyunda beklemeden bu ilk poza geçiş ayrıca ele alınacak açık iştir.
- Poz zamanları yeni kayda göre düzenlendi: açık kollar → yükseliş → kükreme tepesi/tutuş → indirme → uzun toparlanma → son duruş. Son bölüm yalnız videoyu son karede dondurarak uzatılmadı; düzenlenebilir Blender eylemi 51. kareye kadar anahtarlandı. Son pozun yerleşmesinden sonra kısa duruş bulunur.
- Omuz/ön kol FK dönüşleri ve ayrı bilek/parmak gecikmeleri korunur. Bel/kıyafetteki 415 köşenin kol ağırlığı düzeltmesi ve gerçek alt çene hareketi korunur. Özgün gövde, UV, kıyafet/kürk/buz geometrisi değişmedi. Efekt eklenmedi.

Dosya: `art/3d/animation-studies/bilge-roar-study-02.blend`; eylem `BilgeRoarStudy02_FK`. Ön/yan görünüşte de aynı 1,7 saniyelik eylemin tamamı gösterilir. Sabit önizleme kameraları kullanılır; referans kamera açısı yalnız görsel olarak yaklaştırılmıştır, tam kalibrasyon değildir.

## Durum

**Yapıldı:** yeni tam kaydın 38 karesinin incelenmesi; kırpmasız kaynak ve doğrulama; çalışmanın yeni görünür başlangıca ve tam son bölüme zamanlanması; efeksiz karşılaştırma ve tam ön/yan video.

**Test edildi:** kaynak kopyasının SHA-256 eşitliği, bütün kaynak karelerin karşılaştırmada bulunması, klibin 1,7 sn olması, merkez kıyafet bölgesinde kol zinciri ağırlığının sıfır olması, çenenin aşağı açılması ve ayak desteğinin örneklenmesi. Ayrıntılar JSON raporlarındadır. Bunlar görsel kabul değildir.

**Açık:** kullanıcının hareket ritmi/pozları için görsel değerlendirmesi, omuz ve bilek ağırlık cilası, oyunda bekleme geçişi, diğer kurtlara aktarım ve gerçek oynanış testleri. Çalışma zamanı GLB/APK değişmedi; yeni ücretli üretim yapılmadı. Telefon performansı ölçülmedi.

Üretim:

```sh
blender -b -t 3 --python art/3d/animation-studies/build_roar_study.py -- --study02 --stills
blender -b -t 3 --python art/3d/animation-studies/render_roar_study.py -- --study02
python art/3d/animation-studies/compose_roar_study.py --study02
```

## Dışa aktarılan videonun son kare kontrolü

İki video H.264, 30 kare/sn, 267 kare / 8,9 saniye (iki normal ve bir yarım hız tekrar); bütün kareler çözümlendi. Eski 1,2 sn kesimin ötesinde, kaynak zamanı 1,533 sn olan çıktı karesi 55 yeniden çözümlendi. Sol panelin 38. kaynak görüntüsüyle ortalama piksel farkı yaklaşık 1,80/255: son kare gerçekten videoda, yalnız süre sayacı uzatılmış değil. `video-verification.json` bu kontrolü içerir.
