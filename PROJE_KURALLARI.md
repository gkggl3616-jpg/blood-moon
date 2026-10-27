# Rogue: Blood Moon — kullanıcının kalıcı çalışma kuralları

- Kısa mesajları önceki kararlarla birlikte ayrıntılı görev olarak yorumla; rutin ayrıntıları kullanıcıya tekrar sordurma. Eksik veya belirsiz noktaları makul oyun tasarım kararlarıyla tamamla. Kullanıcı son mesajlarıyla işi genişlettiğinde önceki hedefleri bırakma.
- Android öncelikli. Kurulum teslimi tek, bağımsız `.apk` ve doğrudan indirme bağlantısı olmalı. ZIP, kaynak modelleri veya ek veri paketlerini kurulumun parçası gibi sunma. Tüm çalışma zamanı dosyaları APK'da bulunmalı.
- Referanslar: Wolfteam insan/kurt duruşları, sert yüz ve diş yapısı, ayrıntılı kıyafet/zırh, farklı yele/silüet, buzlu el-dirsek geometrisi, kükremede mor el alevi. Yalnız renk ve boy değiştirerek farklı model tamamlandı deme.
- Bilge Kağan, Kül Tigin, Alp Arslan ve Konuralp için birbirine uyan insan ve kurt tasarımları. Yavuz Selim görselleri tarihî kıyafet ve iki formun ortak kimliği için referans.
- Kurtlar geniş omuz/göğüs, belirgin kas, dar bel; göbekli görünüm istemiyor. Model/efektler düşük poligonlu ve mobil belleğe uygun olacak. Performans ölçülmeden 'çökmez' denmez.
- Envanterin hedef yerleşimi 11473.jpg: solda büyük ve duruşu belirgin karakter, sağda üst kategori ve alt filtreler, üç sütun eşya ızgarası, altta seçili eşya görseli ve açıklama/özellikler. Harf kartları hedef görünüm değil.
- İz sürme korunacak. Sıçrama doğal ileri sıçrama; yerde hedef/alan halkası yok. Yetenek laboratuvarı yok.
- Standart Kurt Taklası mağazadan alınır ve yalnız takla açar. Efsanevi Kurt Taklası dört ayak koşu ve takla açar. Kurt başına kuşanma. Son kullanıcı düzeltmesi: takla temas hasarı verir; aynı hedef tek taklada yalnız bir kez vurulur, siper arkasına hasar geçmez.
- Koşu ve takla bütün kurtlarda aynı hareket şablonu, tempo ve süreyi kullanır. Pençe hareketi ve izi karakter/gövde tipine göre farklı. Kükreme 20 saniye +%20 hız, +%15 hasar, +%30 savunma; dövmeler ve eller parlar. Ortak 100 tabanındaki toplam değer tavanı 180; en güçlü kurt diğerlerine en fazla %80 fark atabilir.
- Şimdi düz bir test haritası isteniyor: dokunmatik/klavye hareket, insan birinci şahıs, kurt üçüncü şahıs, insan–kurt dönüşümü, koşu, takla, sıçrama, pençe vuruşu/izleri, mor alev ve test hedeflerinde vuruş kontrolü. Sonra harita ayrıntılandırılacak.
- Tespit edilen hatalar ve gerçek düzeltme durumu GELISTIRME_HATALARI.md dosyasında tutulur. Konsept çizimi, 3B geometri, animasyon önizlemesi, oynanış ve fiziksel Android testi birbirinin yerine sunulmaz.

- Son kontrol tercihi: joystick yerine dört yön düğmesi. İleriye 330 ms içinde iki ayrı basış, efsanevi özellik varsa ortak kurt koşusunu açar. Sağ eylemler yuvarlak, arka planlı ve uluma/pençe/sıçrama/takla simgeli. Gölge gerçek karakter geometrisinden yumuşak olarak yere düşer. İnsan ve kurt bakışı aynı yönde çalışır: yukarı sürükle yukarı bak; aşağı sürükle aşağı bak.

- Son hareket/netlik düzeltmesi: takla kısa mesafe (~2m) olacak; koşarken sıçrama ve takla mümkün, kükremede karakter durur. Koşu/duruş uzuvları germemeli; yere basma, ağırlık aktarımı ve geçişler görsel olarak kontrol edilir. Dikey/yatay hassasiyet ekran boyutundan bağımsız ve ayarlanabilir; başlangıç hassasiyeti artırılır. Yüksek yoğunluklu telefonda düşük çözünürlük hissi giderilecek; Net varsayılanı ve Dengeli seçeneği bulunur. Netlik kazanımı, telefonda ölçülmeden yüksek FPS/çökmez garantisi sayılmaz.
