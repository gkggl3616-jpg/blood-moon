# Bilge kükreme — görsel inceleme çalışması 01

Son karar: önce yalnız Bilge üzerinde gerçek düzenlenebilir animasyon ve efeksiz karşılaştırma; görsel kontrolün ardından diğer kurtlara aktarım ve oyun paketi. Bu dosyalar APK yayını değildir. Çalışma zamanı GLB'leri ve v0.1.14 APK değiştirilmedi.

## Hazırlanan çalışma

Blender dosyası: `art/3d/animation-studies/bilge-roar-study-01.blend`. Eylem: `BilgeRoarStudy01_FK`. 30 kare/sn, 0–36 ana zaman aralığı, 1,2 saniye. Dokuz elle belirlenen poz: dinlenme, hazırlık, açılma, yükselme, tepe, tutuş, indirme, toparlanma, dinlenme. Omuz/ön kol yönleri ayrı FK dönüş anahtarlarıyla yazılır; elin dünya yüksekliğine yönelik eski kol IK hedefi kullanılmaz. Bilek ve parmak varışları ayrı gecikir; eğriler Blender'da düzenlenebilir. Ayak desteği için bacak IK hesabı korunur.

Özgün beyaz model, kürk, kıyafet, buz şekli ve UV korunur. Silüeti değiştiren yeni gövde üretilmedi. Bütün kaynak gövde köşeleri mevcut modelle aynı: bind şekil farkı 0 metre. Efekt, el alevi, geçici parlama ve yeni ses eklenmedi. Blender ışığı ve sade bir yer düzlemi kullanılır. Görüntüdeki gren düşük örnekli CPU renderıdır; telefon performansı veya gerçek oyun çözünürlüğü ölçümü değildir.

## Bulunan ağırlık sorunu

Geniş kol açılmasında kıyafetin yanları yukarı kalkıyordu. Eski kontrol el/parmak gruplarını tarıyordu; ön kol bağlantılarını yakalamıyordu. Bu çalışmanın bel/kıyafet/üst bacak bölgesindeki 415 köşesinden kol zinciri katkısı çıkarılıp mevcut kalça/bacak katkıları normalize edildi. En yüksek çıkarılan kol katkısı yaklaşık %36,84. Gerçek el ve kürk kümelerini yanlışlıkla sabitleyen geniş maske denemesi geri alındı; dar, elle belirlenen merkez bölge kullanıldı. Son ön görünüşte uzun kıyafet perdeleri yoktur. Yerel düzeltme henüz çalışma zamanı modellerine taşınmadı.

## Videoları okuma

- `comparison.mp4`: solda kullanıcının önceki üçüncü videosundaki hedef kükreme, sağda bu gerçek Blender eylemi. İlk iki tekrar 1×, son tekrar 0,5×; hız ekranda yazılıdır. Her tekrarın başında ve sonunda kısa bekleme eklenir.
- Kaynak karelerin gerçek zaman damgaları kullanılır: önceki üçüncü videonun 33.–60. kareleri (yaklaşık 1,320–2,438 sn). Pozları eşleşmiş göstermek için ayrı bir zaman bükme uygulanmaz. Referans hareket bitince son kare tutulur. Sessizdir.
- Referanstaki başka karakterler ve yeşil efekt kaynak görüntünün parçasıdır; yeni modele eklenmedi.
- Referans kamerası, sahne verileri elimizde olmadığı için görünür perspektife göre elle yaklaştırıldı. Tam kamera kalibrasyonu veya piksel piksel eşleşme iddiası değildir. Görüntü yalnız ana karaktere sabit bir kırpma uygular; geometriyi uzatıp kısaltmaz.
- `front-side.mp4`: aynı eylemin bütün zaman aralığı önden ve yandan. Bükülme, boyun/çene, bel ve ayak desteği bu videodan ayrıca incelenir.
- `key-poses.jpg`: hızlı inceleme için altı zaman örneği; videonun yerine geçmez.

## Kontroller ve açık işler

Gövde bind köşeleri değişmedi. İncelenen merkez kıyafet bölgesinde bütün kol zinciri ağırlığı sıfır. 37 zaman örneğinde ayak bileği kontrol noktalarının en yüksek konum sapması yaklaşık 5,64 mm; bu bütün taban köşelerinin sıfır kaydığı iddiası değildir. Alt çene kontrolü, başın dönüşü çıkarılarak ayrıca ölçülür: tepe pozunda çene ucunun aşağı açılması yaklaşık 8,9 cm; bu yüzün sanatsal olarak tamamlandığı iddiası değildir. Teknik veriler `study-audit.json`, `weight-paint.json`, `bind-shape-audit.json`, `authored-keys.json` dosyalarında.

**Hazır:** Bilge için düzenlenebilir FK çalışma eylemi, yerel kıyafet ağırlık düzeltmesi, tam hareketin üç açıdan efeksiz görüntüsü ve gerçek zamanlı referans karşılaştırması.

**Görsel kabul bekliyor:** kol yayının genişliği ve ritmi, göğüs/başın güç hissi, tepe pozunun süresi ve toparlanmanın doğallığı. Sayısal kontroller bu kabulün yerine geçmez. Omuz/koltuk altı ve bilek yüzeyinin yakın plan ağırlık cilası da değerlendirmeye açıktır; bütün iskeletin sanatçı düzeyinde bitirildiği iddia edilmez. Yele nedeniyle baş/boyun arkadan hâlâ kısmen örtülür; onaylı model geometrisi korunmaktadır. Parmaklar mevcut iki grup/el iskeletiyle hareket eder; ayrı her parmak eklemi yapılmış sayılmaz.

**Sonraki aşama:** değerlendirmeye göre poz/eğri/ağırlık cilası, sonra aynı hareketin diğer oranlara aktarımı, gerçek oyunda geçiş/etkileşim kontrolleri ve tek APK. Bunlar bu çalışma tesliminde tamamlandı diye sunulmaz. Yeni ücretli Meshy işlemi yoktur.

Üretim:

```sh
blender -b -t 3 --python art/3d/animation-studies/build_roar_study.py -- --stills
blender -b -t 3 --python art/3d/animation-studies/render_roar_study.py
python art/3d/animation-studies/compose_roar_study.py
```

Karşılaştırmayı yeniden üretmek için çalışma alanındaki önceki video kareleri ve zaman damgası manifesti gerekir. Özgün video ve bütün kareler çalışma alanında korunur; karşılaştırmada ilgili özgün kareler zaten görünür.
