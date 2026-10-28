# Orijinal karakter ve animasyon dosyasıyla aktarım

Kullanıcının 2026-10-28 tarihli önerisi: orijinal Wolfteam karakter dosyalarıyla doğrudan çalışmak. Bu, yeni ücretli üretim talimatı değildir. Elde olmayan içerik tamamlanmış sayılmaz.

## En yararlı dosyalar

1. **FBX, GLB/GLTF veya BLEND**: gerçek mesh, iskelet, skin ağırlıkları, bind/rest pozu.
2. **Özgün animasyonlar**: bekleme, yürüme, dört ayak koşu, tam kükreme, kısa takla, sıçrama ve pençe. Klipler ayrı dosyalardaysa özgün isimleriyle korunmalı.
3. **Dokular**: renk/albedo, normal, pürüzlülük ve varsa metal/maske/ışıldama. Dosya klasörleri korunmalı. GLTF için `.bin` ve bağlı görseller de gerekli.
4. İnsan formu için aynı içerik; birinci şahıs kol/silah modeli ayrıca varsa ayrı tutulmalı.

Çok dosya ZIP ile birlikte taşınabilir. OBJ yalnız geometri/UV/malzeme taşıyabilir; tek başına iskelet, skin ağırlığı veya animasyon sağlamaz. Oyuna özel biçimlerde ilk iş uzantıyı, dosya başlığını ve desteklenen içeriği belirlemektir; dosyayı FBX diye yeniden adlandırmak dönüşüm değildir.

## İlk kontrol

- Orijinallerin hash'i alınır, çalışma kopyası açılır. Orijinal dosya değiştirilmez.
- Kaynak iskelet, kemik isimleri/hiyerarşisi, birim, eksen ve rest/bind matrisleri korunur.
- Model ilk önce **kendi iskeleti ve özgün klipleriyle** oynatılır. Eski oyunumuzun bozuk olabilen animasyonları hemen üstüne uygulanmaz.
- Üçgen/UV/malzeme, eksik doku, ağırlıksız veya aşırı etkili köşeler ve GPU kemik sınırları kontrol edilir.
- Her klibin tam başlangıç/bitişi, kare/saniye oranı, root hareketi ve döngü dikişi ölçülür. Tam kükremenin toparlanma sonu kesilmez.
- Omuz/dirsek/bilek, parmaklar, çene/dişler ve bacaklar önden, yandan, arkadan ve hareket boyunca incelenir.
- Mesh kaynakta düzgün, oyunda bozuksa rest/bind dönüşümleri, eksen/ölçek, root hareketi, animasyon katmanları ve oynatma karışımı araştırılır. Animasyonda kemik ölçeği uygulanıyorsa bunun gerekçesi doğrulanır.

## Oyuna taşıma

İlk deneme dışa aktarılmış GLB yeniden içe alınarak yapılır. Kaynak ile yeniden açılan modelde aynı poz/zaman karşılaştırılır. Ardından gerçek Three.js oynatıcısında, sonra Android çalışma zamanında kontrol edilir. Önizleme ile arena aynı gerçek dosyayı kullanır.

Animasyonun görsel hareketi ile oynanış kuralları ayrı ayarlanır: ortak dört ayak koşu başlangıç ayarı yaklaşık 8 m/sn; takla yaklaşık 2 m ve aynı hedefe bir kez hasar; kükremede hareket kilidi; koşudan sıçrama/takla geçişleri. Kaynak klipte root hareketi varsa ayrıca oyun hızına eklenip iki kez ilerleme üretilmez.

Doğru özgün rig gelirse yeni oluşturulan rig üzerine körlemesine retarget yapılmaz. Diğer kurtlara ortak hareket gerektiğinde hedef oranlarına uygun retarget, ayak teması ve eklem testleri yapılır. Efektler el kemiğine bağlı, kısa ömürlü ve karakter paletine uygun kalır; bozuk eklemleri ışıkla gizlemek kabul değildir.

Sahiplik, satın alınmış eşyalar, krediler ve kayıtlar korunur. Son teslim yine gerekli bütün çalışma zamanı varlıklarını içeren tek imzalı APK'dır; geliştirme için ZIP kaynak almak APK'yı parçalara bölmek anlamına gelmez.
