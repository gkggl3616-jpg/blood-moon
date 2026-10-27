# Yüklenen hareket videosu — inceleme ve v0.1.11

## İncelenen dosya

`Screenrecorder-2026-10-27-20-54-17-670.mp4`: toplam 5.015 saniye, görüntü 4.910 saniye, 1220×2712, 119 HEVC kare. Bütün görüntü kareleri 0.000–4.869 saniye arasında zaman sırasıyla çözüldü ve dört temas sayfasında incelendi. Son karedeki görüntü akışın sonuna kadar sürer. Bu yüklenen kısa kaydın tamamıdır; kaynak YouTube videosunun geri kalanı değildir. Telefon/YouTube arayüzünü içeren özgün dosya depoya veya APK'ya eklenmedi.

## Zaman sıralı gözlemler

| Aralık | Görüntüde seçilen hareket | Oyuna etkisi |
|---|---|---|
| 0.00–0.12 | Öne toplanmış/alçak gövde, ellerde mor ışık, ardından doğrulma | Koşuda gövde öne yatmalı, baş dengeli kalmalı; yalnızca normal duruşu hızlandırmak yeterli değil. Bu kısa bölüm tam bir sürekli dört ayak koşu devrini ölçmeye yetmez. |
| 0.12–0.54 | Omuz/kollar açılıyor; eller çevresinde mor/mavi enerji, gövde tekrar aşağı toplanıyor | Kükreme için hazırlık–açılma–tutma–toparlanma ve el kemiğine bağlı efekt. Bonus yüzdeleri bu karelerden ölçülemez. |
| 0.54–0.78 | Kollarda kısa yaylar ve saldırıdan sonra dönüş | Pençe izi kısa ömürlü kalmalı; her kare kalıcı geometri oluşturulmamalı. |
| 0.78–1.44 | Dizler bükülü, öne eğilmiş hazır duruş; kollar gövdeden açık | A-pose yerine ağırlığı aşağı alınmış kurt duruşu, kaslı gövde ve okunur el silüeti. |
| 1.44–1.98 | Gövde ilerlerken ayaklar sırayla hareket ediyor, kamera dönüyor | Duruş, normal hareket ve koşu ayrı klipler; kamera hedef yüksekliği alçak koşuya uyum sağlamalı. |
| 1.98–2.60 | Kol yukarı açılıyor, kısa iz, eller tekrar aşağı alınıyor | Saldırı ve toparlanma pozları ayrı zamanlanır; saldırı animi bütün süre boyunca aynı poz değildir. |
| 2.60–3.30 | Öne toplanmış gövdeyle ilerleme, bacak uzanması/toplanması | İtme, yerle temas ve geri toplama fazları; uzuvları fiziksel uzunluğundan fazla germe. |
| 3.30–3.75 | Dizler esnek, kollar açık, kısa yer değiştirme ve kamera yönü değişimi | Hareket geçişlerinde sabit kafaya, gövde dengesine ve iyi hassasiyete ihtiyaç var. |
| 3.75–4.25 | Baş/gövde aşağı toplanıyor, ayaklar dönüp yukarı geliyor, tekrar doğruluyor | Kısa takla. Dünya metreleri bu perspektifli/kurgulu kayıttan ölçülemez; uzun ileri atılma istenmediği kullanıcı tarafından açıklandı. |
| 4.25–4.91 | Ayakta toparlanma, ellerde mor enerji, kameranın yön değiştirmesi | Takla bitişinde duruşa/harekete geri dönüş; efekt ve kamera hareketi karakter animasyonundan ayrı ele alınır. |

Renkli parlamalar, sağlık artısı simgeleri ve ekran izleri görüntüyü kısmen örtüyor. Kaynak oyunun gerçek FPS'i, dünyadaki hız/mesafe, hasar değeri ve yetenek bonusu bu kayıttan sayısal olarak doğrulanamaz. Aşağıdaki sayılar yerel oyun ayarıdır.

## Kök nedenler ve düzeltmeler

**Koşu ve duruş:** Önceki pozlar bilek/diz hedeflerini kaynak kol/bacak uzunluklarına göre sınırlamıyordu; düz sinüs hareketi ve uzun 0.8 sn koşu döngüsü, uzuvların gerilip süzülmesine neden oluyordu. Ortak `wolf-shared-v3` iki kemikli IK kullanır; dört kurtta aynı fazlar ve tempo, kaynak gövde oranına göre eklem yerleşimi vardır. Ön/arka pençe temasları ve geri toplama fazları ayrıldı, sağ-sol küçük faz farkı eklendi, başın dikey salınımı azaltıldı. Gerçek pençe tabanı yüksekliği eklem merkezinden ayrılır. Normal hareket 0.667 sn, dört ayak koşu 0.533 sn; yürüyüş/koşu hızları 3.6 / 5.6 m/sn. Kükreme hız bonusu, ilerleme hızı ile hareket klibinin temposuna birlikte uygulanır. Yüz/çene hareketi hâlâ yoktur; yeni model üretildi diye sunulmaz.

**Takla:** Önceki ~8m ilerleyen hareket 0.8 sn / yaklaşık 2m olacak şekilde kısaltıldı. Başlangıç 0.08 sn, temas sonu 0.60 sn, ardından yavaşlama. Gövdedeki ileri offset ve dikey sıçrama da azaltıldı. 38 taban temas hasarı, kükreme/karakter çarpanı, hedef başına tek isabet, siper kontrolü korunur. Koşu modu takla yüzünden silinmez; basılı hareketle iniş sonrası koşuya dönülür. Koşudan veya havadayken kısa taklaya geçilebilir.

**Dönüş hatası:** 180 dereceyi geçerken quaternion işaretleri farklı yarımküreye geçiyordu. Blender bileşen eğrileri sıfırdan geçip ara pozda kök dönüşünü bozuyor; gövde bir karede yukarı fırlıyordu. Ardışık quaternion işaretleri süreklileştirildi. Klipler 0.033 sn yerine sıfırda başlatıldı; koşu döngüsünün ilk/son pozu ve gerçek klip süresi eşitlendi.

**Koşarken sıçrama:** Koşu açık kalır, sıçrama klibi oynar, yere inince basılı yön tuşuyla koşuya dönülür. Önceki ayrı sıçrama itkisinin üstüne koşu hızı ekleniyordu. Havada tek yatay hız taşınır ve sınırlı yönlendirme uygulanır; koşu ve sıçrama hızları üst üste toplanmaz. Zemine basınca taşınan hız sıfırlanır.

**Kükreme:** Basınca koşu kapanır ve yatay hız sıfırlanır. İleri tuşu basılı olsa da 1.2 sn poz süresince karakter ilerlemez. Bakış açık kalır; saldırı/sıçrama/takla pozu kesemez. Poz bitince basılı yön tuşu normal hareketi sürdürür. 20 saniyelik mor el alevi ve önceki bonus/tavan kuralları devam eder.

**Netlik:** Renderer bütün cihazlarda en fazla 1.25 DPR kullanıyordu. DPR=3 telefonda, aynı CSS alanında ekranın gerçek piksel sayısının yaklaşık %17'si çiziliyordu. Bu sınır kaldırıldı. Varsayılan **Net**, cihaz piksel yoğunluğunu en fazla 4.2 milyon piksel bütçesi ve GPU boyut sınırı içinde kullanır. **Dengeli** bütçesi 2 milyon pikseldir. Bunlar gerçek framebuffer boyutlarıyla test edilir; 800×360 CSS / DPR3 örneğinde Net 2400×1080 çizer. Yumuşatma, 8x'e kadar doku filtreleme korunur; fazla parlak pozlama azaltıldı. Düşük poligon/doku bütçesi değişmedi. Bu kayıt Wolfteam referansıdır; kullanıcının kendi APK ekranındaki netlik artışı fiziksel telefonda ayrıca görülmelidir.

**Hassasiyet/kamera:** Yatay sürükleme ekran genişliğine göre normalize edilir; varsayılan 1.45×, ayarlar 0.60–2.40×. Böylece küçük telefon CSS alanında eski sabit piksel katsayısından daha hızlı ve ekranlar arasında tutarlı dönüş olur. Tercih kaydedilir. İki formda yukarı/aşağı bakış yönü korunur. Kurt kamerası biraz yaklaştırıldı; koşuda bakılan yükseklik yumuşakça alçalır, aşırı geniş FOV azaltıldı.

## Üretim ve doğrulama

Mevcut GLB'ler ve Blender kaynak sahnesi güncellendi; **yeni Meshy harcaması 0**. Geometri/üçgen sınırları, tek WebGL context, iki model cache'i ve 72 parçacık havuzu korunur. Düz test haritası kullanılmaya devam eder.

- `art/3d/scripts/verify_motion.py`: her kurt için GLB'den okunan duruş/hareket/koşu/takla/kükreme kliplerinde 25 poz örneği; gerçek deforme gövde sınırları, uzuv uzunluğu ve döngü dikişi kontrolü.
- `tools/verify_arena.py`: takla mesafesi/hasarı/siper, koşu→sıçrama→koşu, koşu→takla, havada takla, ileri basılı kükremede durma, iki formda bakış, yüksek DPI framebuffer ve ayar kalıcılığı.
- `tools/verify_ui.py`: beş mobil oran, menü/ayar/mağaza/kuşanma ve model geçişleri.
- APK imzası, arşivi, klipleri ve üçgen bütçesi kontrol edilir. Fiziksel Android performans testi yapılmadı; bütün cihazlarda belirli FPS veya çökmez garantisi yoktur.
