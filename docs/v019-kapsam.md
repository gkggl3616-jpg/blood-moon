# v0.1.9 uygulama kapsamı ve kabul ölçütleri

## Referans ve yeni istekler

Son kullanıcı mesajları aynı görevi genişletiyor; hepsi birlikte uygulanacak. Kart tasarımını kopyalamak zorunlu değil; envanter yerleşimi ise son referansa çok yakın isteniyor. Referans görsellerindeki büyük yüz/çene/diş, katmanlı yele, kostüm ve dirsek-bilek silüeti esas alınır. Yeni videolar: https://vt.tiktok.com/ZSgquwp3Q/ ve https://vt.tiktok.com/ZSgqba4vb/ . Erişilemeyen video izlendi diye yazılmaz; erişim durumu kayıt edilir.

## Karakter yönleri

| Karakter | İnsan | Kurt | Öğe/iz |
|---|---|---|---|
| Bilge Kağan | Lacivert-altın lamel zırh, olgun yüz, taç/turkuaz | Uzun boz yele, iri keskin çene, düz komutan duruşu | Buzlu dirsek ve eller, açık mavi geniş pençe |
| Kül Tigin | Kara-kızıl asimetrik savaş zırhı, toplu saç | Kısa, kuvvetli üst beden, sivri kara yele, yara izleri | Kızıl zırhlı ön kol, çift çapraz iz |
| Alp Arslan | Bronz miğfer, ağır deri/metal öncü zırhı | Kalın kahverengi yele, ağır omuz ve çene, dar bel | Kehribar çatlak/köz, ağır yükselen iz |
| Konuralp | Hafif deri akıncı, turkuaz kuşak, ince uzun gövde | Uzun kollar, öne eğilen avcı, ince ve sivri yele | Mor enerji bilekleri, üç dar hızlı kavis |

## Oynanabilir düz test alanı

- Çevrimdışı düz zemin, sınırlar, birkaç siper ve canı azalan eğitim hedefleri. Tam oyun/çevrimiçi maç olduğu iddia edilmez.
- Sol dört yön düğmesiyle hareket, sağ sürükleme ile bakış; klavyede WASD ve ok/sağ fare, telefon yatay yerleşim.
- İnsan kamerası birinci şahıs, görünür eller ve geçici silah ile atış/geri tepme. Kurt kamerası arkadan üçüncü şahıs; gerçek iskelet klipleri.
- İnsan–kurt dönüşümü, ileri sıçrama ve düşüş/yere basma, normal hareket, dört ayak koşu, ileri takla. Takla saldırı hasarı üretmez.
- Pençe klibi ve kısa ömürlü ışık izleri; yakın mesafe/ön koni içinde hedef hasarı; insan atışı engellerle kesilir.
- Kükreme ve 20 saniyelik bonuslar, ellerde mor alev, dövme parlaması; pasif/aktif toplam 180 tavanı.
- Envanter kuşanması oyuna aktarılır. Test modu geçici deneme donanımı kullanıyorsa açıkça belirtilir ve mağaza sahipliği değiştirilmez.

## Mobil bütçe ve teslim

- Tek etkin sahne/karakter; kullanılmayan WebGL kaynaklarını bırak. Dinamik efektlerde sınırlı parçacık/iz sayısı; her kare yeni geometri oluşturma.
- Yeni modeller için hedef görünür kurt <=15 bin, insan <=12 bin üçgen. Yakın menü LOD'si ve oyun LOD'si rapor edilir. Doku çözünürlüklerini mobil kullanım için sınırla.
- Tarayıcıda gerçek hareket, çarpışma/sınırlar, dönüşüm, animasyon ve hasar/efekt ömrü testleri. Android APK derleme, içerik ve imza doğrulaması.
- Sabit geliştirme imzası, GitHub Actions üzerinden tek APK; doğrudan `.apk` release varlığı. Kullanıcıya ZIP açtırma veya iki paket kurdurma.

## Yeni Meshy maliyeti

CLI 0.4.0 image-to-3D dry-run, 27 Ekim 2026: dokulu model başına tahmini 30 kredi; istek yapılmadı. Doğrulanan bakiye 1010. Dört insan + dört ayrı kurt = tahmini 240 kredi; yerel Blender optimizasyonu ücretsizdir. Ücretli yeniden üretim henüz başlatılmadı; yeni maliyet onayı ayrı beklenir. Üretim açılırsa görev kimlikleri ve gerçek tüketim kayıt edilir.

## Son kullanıcı onayı ve öncelik

Kullanıcı önce yalnız Bilge Kağan insan + kurt çiftini üretmeyi onayladı: yaklaşık 60 Meshy kredisi. Diğer altı yeni model için ücretli üretim başlatılmayacak. Hazırlanan diğer karakter görselleri konsept referansı olarak kalır. Bilge çifti oyuna ve düz test alanına entegre edilecek. Koşu/takla bütün kurtlarda aynı klip şablonu ve tempoda olacak; pençe hareketi/izi farklı kalacak.
