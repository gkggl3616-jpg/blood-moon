# Kalıcı insan/kurt üretim promptu — güncel ana kalite şartı

29 Ekim 2026. Kullanıcının son kalite düzeltmesi. Yeni karakterler ve mevcut karakter düzeltmeleri için bağlayıcıdır. Teknik kontrolün geçmesi görsel kabul değildir.

## Görev

Rogue: Blood Moon için mevcut, doğrulanmış gövde/iskelet ailesini kullanarak ayrıntılı, doğal ve tehditkâr insan/kurt çifti üret. Sonucu gerçek oyun GLB'si, malzemeleri, skin ağırlıkları, kaynak animasyonları, dövme yüzeyleri ve model ailesinin kükreme efektiyle birlikte hazırla. Konsept görseli gerçek 3B teslim sayılmaz. Rastgele üretilmiş anatomiyi sonradan başka iskelete zorlama.

## Karakter kimliklerini koru

Bilge Kağan `bilge`, Buz Kurdu onun kurt formudur. Karahan `karahan` kimliğiyle ayrı eklenir. Karahan'ın insanı veya kurdu Bilge'nin dosya yoluna, kayıt kimliğine ya da ekipman profiline yazılmaz. Eski sahiplik, kredi ve donanımlar korunur. Aynı insan gövde ailesinin kullanılması, iki karakterin aynı yüz/kostümle tamamlanmış sayılması değildir. Ortak yüz/gövde kullanılan adayda bu sınırlama açıkça belirtilir.

## Görsel kalite

- Geniş omuz ve göğüs, anlaşılır kas yapısı, dar bel, güçlü kalça/bacak. Baş-boyun-omuz silüeti ayrı okunur. El ve ayaklar doğal, parmaklar hafif kıvrık; robot gibi açık avuç yok.
- Kürk, metal ve desenli kumaş gibi görünmez. Büyük tekrarlayan dalgalar, zebra/mermer desenleri, kâğıt levhalar ve rastgele sivri üçgenler kabul edilmez. Kürk akışı anatomiyi takip eder; yalnız yüzey gürültüsü ayrıntı sayılmaz.
- PBR renk, tangent-space normal ve pürüzlülük haritaları kullan. Gerçek olmayan boyalı ışık/parlama yerine ışığa tutarlı tepki ver. Kürk/deri/kumaş metal değildir; metal yalnız gerçek zırh parçalarındadır. Her malzemenin pürüzlülüğü ayrı ayarlanır. Bir shader kaliteyi sihirli biçimde artırmaz.
- Ana ayrıntıda 2K, yüz/yakın çekim gerektiriyorsa uygun 4K atlas değerlendir. Çözünürlük sayısı tek başına kalite kanıtı değildir. Mip haritaları, UV dikişleri ve anizotropik filtre birlikte kontrol edilir. Telefon belleği ölçülmeden sınırsız 4K/8K yükleme yapma.
- Geometri bütçesi yaklaşık kurt 15 bin, insan 12 bin üçgendir. Silüeti etkileyen parça geometridir; küçük saç/kürk/dikiş/çizik ayrıntısı dokudur. Kareli/çok köşeli eklem, ters normal ve kötü gölgelendirmeyi düşük poligon gerekçesiyle kabul etme.
- Kurt pantolon/eşdeğer alt giysi giyer. Kumaşta dokuma, dikiş, kıvrım ve kontrollü yıpranma olsun. Küçük yırtıkların altında uygun deri/kürk görünür; karanlık boşluk veya uzayan üçgen oluşmaz. Yırtık için eklem yüzeyini rastgele silme. Uzun etek, sallanan bel süsü ve büyük kemer kıvrımı ekleme.
- Az sayıda iyileşmiş pençe yarası ve sınırlı koyu/kuru kan izi eklenebilir. Yaralar omuz, göğüs veya kol üzerinde anatomiyi izler; desen tüm gövdeye döşenmez. Çizik, kan, giysi kirlenmesi ve dövme farklı katmanlardır. Kan normal durumda emissive değildir.
- İnsan ayrıntılı yüz/saç/kaş/sakal, okunur gözler, doğru el ve kaliteli kısa kostüm taşır. Düz siyah blok gömlek veya kaplaması eksik kahverengi omuz, tamamlanmış zırh diye sunulmaz.

## Ağız, iskelet ve animasyon

Kaynak baş/çene ve dişler korunur. Üst diş başı, alt diş alt çeneyi izler. Dış kırmızı oval, havada diş, çenede delik ve uzayan boğaz yok. Kaynak bind ile hareket bind'i ölçülür; yalnız kemik adı/sayısı eşleşmesi yeterli değildir. Gerekli bağlama uyarlaması türetilmiş katmanda yapılır; ham kaynak anahtarlar saklanır. Boynuz/zırh gibi küçük parçalar uygun mevcut kemiğe bağlanır; yeni süs için kemik oranı değiştirilmez.

Yürüme/koşma temposu gerçek sabit fizik adımındaki ilerleme hızından hesaplanır. Fizik adımı olmayan yüksek yenileme kareleri karakteri boşta duruşa döndürmez. Koşarken ikinci parmakla sıçrama/takla ve insana dönüş çalışır. Takla kısa kalır, yatay hız iki kez eklenmez. Kısa kontrol: bir yürüyüş/koşu döngüsü, sıçrama, takla ve tam kükreme. Her motif ve bütün oyun arayüzü yeniden taranmaz.

## Dövme ve FX/ses

Üç ortak deri yaması: üst sırt, sol üst kol arkası, sağ üst kol arkası. Giysi/zırha taşma yok. Eğri yüzeyi ve skin ağırlığını izler; havada kart değildir. Motif değişimi aynı yerleşimi kullanır. Normal parlama 0,025; kükremede tepe 1,05. Eşya bonusları karakter pasifinden bağımsız gerçek hesapla uygulanır; +%240, 100 tabanda 340 demektir.

Modelin kendi kaynak kükreme klibi ve efekt bağlantısı çözülsün; yalnız renk değiştirmek başka efekt sayılmaz. Olay zamanı, efekt geometrisi/sprite/ölçek/sönme eğrileri korunur. AI hasar komutları oyuncuya taşınmaz. Ses önceden çözülür, tek ses kanalı ve pay bırakılmış seviye kullanılır; animasyon bittikten sonra geç başlama veya üst üste ses patlaması yok. Hafif kamera titreşimi nişanı kalıcı kaydırmaz.

## Teslim ve dürüst kayıt

Ön/yan/arka gerçek oyun görüntüsüyle kontrol et. Ağır uzama veya açık ağız hatası varken modeli yayıma hazır sayma. Yalnız test edildiği kadarını söyle. Yapılan, otomatik kontrol edilen, görsel olarak incelenen, kullanıcı tarafından kabul edilen ve fiziksel telefonda deneneni ayrı yaz. Yeni ücretli görev gerekiyorsa gerçek kapsam/maliyet açık olmalı; geçmiş bütçe sınırsız izin değildir. Kurulum tek imzalı APK, belgeler ayrı güncel MD bağlantısıdır.
