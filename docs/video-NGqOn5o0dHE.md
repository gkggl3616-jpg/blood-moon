# NGqOn5o0dHE referansı ve v0.1.10 uygulama kaydı

## Kaynakların ayrımı

- Kullanıcının yeni bağlantısı: https://youtube.com/shorts/NGqOn5o0dHE?si=DP-cPaTOSk4vZcOR . 27 Ekim 2026'da yt-dlp ile sayfa ve oynatıcı API erişimi denendi. Ortam ağ geçidi `Tunnel connection failed: 403 Forbidden` döndürdü. Video, ses, süre ve tek bir karesi dahi bu bağlantıdan alınamadı; tamamı izlenmedi. Zaman kodlu içerik dökümü bekliyor. Bu belge yeni videonun izlenmiş analizi değildir.
- Kullanıcıdan doğrudan doğrulanan yeni kural: **takla hasar verir**. Eski hasarsız takla kararı geçersizdir. Diğer açık hata: dikey bakış insan/kurt formlarında ters algılanıyor.
- Önceki erişilebilir video kareleri yeniden kontrol edildi: `/workspace/reference-review/roll-motion.jpg`, `roar.jpg`, `movement.jpg`. Bunlar yeni YouTube videosuna atfedilmeyecek.

## Erişilebilir eski karelerde görülenler

- `roll-motion.jpg`, 1.6–2.2 saniye aralığı: gövde küçülüp toplanıyor, ileri yönde dönüş ve ardından ayakta toparlanma var; ellerde parlak izler seçiliyor. Bu seyrek karelerden gerçek klip süresi veya gerçek oyunun hasar değeri ölçülemez.
- `movement.jpg`, 1.4 saniye: öne alçalmış ilerleme; 4.4–6.4 ve 10.4 saniye: açık kol silüeti ve kısa parlak pençe izleri; 11.4 saniye: toplanmış ileri hareket pozu. Edit kesmeleri yüzünden bunlar kesintisiz hareket kaydı sayılmaz.
- `roar.jpg`, 10.6 saniye: eller çevresinde belirgin renkli enerji; sırt işareti ve koyu gövde birbirinden okunuyor. Karelerden bonus yüzdesi/süresi çıkarılmaz; oyundaki bonuslar kullanıcının önceki açık kurallarındandır.

## Şimdi uygulanan oyun davranışı

- İnsan ve kurt aynı bakış anlamını kullanır: yukarı sürükle → yukarı bak, aşağı sürükle → aşağı bak. İnsan Euler pitch ile kurt yörünge yüksekliği aynı işareti kullanınca ters sonuç oluşuyordu; kurt yörüngesinde `elevation = .22 - pitch` ile giderildi. Kamera zeminin altına girmeyecek şekilde sınırlandırılır. Klavye yukarı/aşağı da aynı semantiği kullanır.
- Standart ve efsanevi takla temas hasarı verir. Koşu kilidi değişmedi: dört ayak koşu efsanevi özellik ile açılır. Her kurdun kuşanması ayrıdır; geçici test donanımı sahiplik kazandırmaz.
- Takla: 1.4 saniye; ilk 0.12 saniye hazırlık, 0.12–1.15 saniye temas penceresi, sonra yavaşlayarak toparlanma. Yön başlangıçta sabitlenir; kamera serbesttir. Vuruş pençe saldırısını iptal eder. Süpürülen gövde mesafesiyle temas aranır; her hedef aynı taklada bir kez hasar alır. Siper çarpışması ve görüş hattı kontrolü hasarın duvardan geçmesini önler.
- Taban takla hasarı **38**, temas yarıçapı **0.95 m**: bunlar prototip için seçilmiş yerel denge değerleridir, Wolfteam veya yeni videodan ölçülmüş sayılar değildir. Gerçek hasar `38 × min(180, karakterHasarı × kükremeÇarpanı) / 100`; bonusları iki kere ekleme yoktur. İsabet ve hasar bildirimi mevcuttur.
- Ortak `wolf-shared-v2`: bütün kurtlarda aynı 0.8 saniyelik dört ayak koşu ve 1.4 saniyelik takla şablonu. Takla açısı doğrusal başlayıp gövdeyi hazırlıksız çevirmek yerine, hazırlık → toplanma → 360 derece dönüş → iniş/toparlanma şeklinde zamanlandı. Karakter oranlarına göre aynı hareket uygulanır.
- Kükreme pozu 1.2 saniye: hazırlık → kolları/göğsü açma → kısa tutma → toparlanma. Poz süresince hareket/saldırı/takla klibi kesemez; bakış kontrolü açıktır. Mor el parçacıkları gerçek el kemiklerine bağlıdır. 20 saniyelik hız +%20, hasar +%15, savunma +%30 ve toplam 180 tavanı korunur. Pençe hareketleri karaktere özel kalır.

## Bu modeller ve animasyonlar nasıl üretilir?

1. Aynı karakterin insan/kurt silüeti, yüzü, kostümü ve elementini ortak tasarım referansında belirle. Bilge çiftinin mevcut Meshy üretimi kullanılır; diğer altı yeni modele bu turda kredi harcanmadı.
2. Büyük şekilleri düşük poligonlu gövdede tut; kas, kürk ve süs detayını renk/normal dokusunda taşı. Mevcut Bilge insan 9.000, kurt 13.773 üçgen; diğer üç kurt 10 binin altında. Buz ve dirsek silüeti uzaktan okunmalı. Doku sınırları renk 2K, normal 1K, skaler haritalar en fazla 512px.
3. Blender'da omuz/dirsek/el, bel/diz/ayak dönüşlerine uygun ağırlıklar ve ortak iskelet kullan. Mevcut 22 kemikli rig geometrik ağırlıklıdır; eklem cilası manuel kontrol ister. Dövme ağırlıkları gövdeden aktarılır. A-pose'u hareket klibi gibi sunma.
4. Ana pozları zamanlayıp ara hareketleri düzenle. Koşu/takla ortak; pençe karaktere özel. Yer değiştirmeyi oyun fiziği, beden hareketini GLB klibi yönetir; böylece görsel ileri hareket iki kez uygulanmaz. El izleri ve alevler ayrı, sınırlı ömürlü efektlerdir.
5. Kükremenin ağız açma/yüz ifadesi için çene ve yüz topolojisi ile ağırlıkları ayrıca hazırlanmalı. Mevcut rig'de **çene kemiği ve dudak animasyonu yok**; bu turda tamamlandı denmez. Aynı şekilde final retopoloji, kürk katmanı ve el/ayak basma cilası hâlâ gerekir.
6. Klipleri GLB'ye aktar; tek renderer, en fazla iki model cache'i ve 72 parçacık sınırını koru. Animasyon, temas hasarı ve kamera yönünü oyunda test et. Telefon performansı/çökme güvenilirliği fiziksel cihazla ayrıca ölçülür.

## Doğrulama

Tarayıcıda iki formda gerçek sürükleme, takla başına tek hasar, siper çarpışması, koşu donanımı, kükreme kilidi/bonus bitişi, pençe, model değişimi ve tek WebGL context kontrol edilir. APK içerik ve imza kontrolü ayrıca yapılır. Fiziksel Android testi yapılmadı. Yeni YouTube videosunun bütününü inceleme işi erişilebilir dosya gelene kadar açık kalır; bu eksik, mevcut hata düzeltmelerinin teslimini durdurmaz.

27 Ekim yerel sonuçları: `tools/verify_arena.py` ve `tools/verify_ui.py` geçti; 15 pozdan oluşan yerel GLB animasyon sayfası oluşturulup görsel olarak kontrol edildi (`dist/motion-v0110-review.jpg`, bu oyunun çıktısıdır). `tools/build_apk.py` APK içerik/imza/üçgen bütçesi kontrolünden geçti. Bunlar yeni YouTube videosuna erişildiği anlamına gelmez.

## Sonraki yükleme

Kullanıcı `Screenrecorder-2026-10-27-20-54-17-670.mp4` adlı yaklaşık 5 saniyelik yerel kayıt sağladı. Bu dosyanın 119 görüntü karesi incelendi; gözlem ve sonraki uygulama kaydı `docs/video-screenrecorder-20261027.md` dosyasındadır. Önceki bağlantı erişim hatası geçmiş kaydıdır; artık yüklenen kısmın görsel analizi mevcuttur.
