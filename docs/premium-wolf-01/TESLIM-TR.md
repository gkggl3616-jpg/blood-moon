# v0.1.17 — tek çalışan kurt zinciri

Kullanıcı aynı kapsamda tekrar tekrar onay sorulmadan devam edilmesini ve tam APK istedi. Yeni görselden üretim + remesh tamamlandı: 30 + 5 = 35 kredi. Önceki reddedilen metinden üretim 45 krediydi; bu iki denemenin toplamı 80 kredi. Yeni ücretli iskelet/animasyon üretilmedi.

## Oyuna gerçekten eklenen

- Bilge/Buz Kurdu: seçilen Power42 gövdesi, 42 kaynak kemik ve 72 kaynak klip. Yeni Meshy gövdesi bu iskelete zorla uydurulmadı. Yüz, çene, diş ve ağız içi temel geometrisi kaynak gövdeden; görünüş ve yeni pantolon özgün üretimden yüzeye aktarıldı. DTX kıyafet pikselleri kullanılmadı.
- Yaklaşık 14,2 bin üçgen; bütün renk/normal dokuları GLB içinde. Kürk ayrıntısı Cycles PBR yüzey aktarımı ve onaylı gri kurt referansından sürekli fotoğrafik kürk malzemesiyle işlendi. Kaynak animasyon anahtarları ve eklem ölçüleri korunuyor.
- Pantolonun bel/paça sınırında gerçek geometri kesişimi var; kıyafeti rastgele üçgen merkezine göre boyayan eski yöntem kaldırıldı. Yeni giysinin kasık bölgesinde keskin pelvis/uyluk ağırlık değişimi yumuşatıldı.
- Üç ayrı dövme yaması cilde bağlı. Sırt alanı giysiden yukarıda; üst kol yamaları arkada. Tek ortak politika bütün motiflerde kullanılır. Normal parlama 0,025; kükremede belirginleşir. Ağız ve diş malzemeleri gövde parlamasına alınmaz.
- Dört ayak koşu `T_WallDash`: 0,533 sn, kaynak temasından ölçülen adım 2,5106 m. Fiziksel koşu temel 8 m/sn; test donanımıyla 8,4 m/sn.
- Kükreme bu gövdenin `T_CRY` klibidir: 1,333 sn, kaynak olay 0,633 sn. Kaynak efekt, mor el alevleri, toklaştırılmış ses ve kısa kamera titreşimi korunur. Takla kısa ve hasarlıdır; hasar/siper kuralları aynı.
- Animasyonlar karışırken temas için az sayıda gerçek yüzey noktası kullanılır. Önceki hareketten beklemeye geçişte 18,9 cm gömülme giderildi. Fizik konumu ve nişan değiştirilmez.
- Ateş düğmesine basılı sürükleyerek nişan; koşudan sıçrama/takla/dönüşüm; yön düğmeleri ve çift ileri korunur.
- Android uygulaması güncel APK varlıklarını önbellekten eski sürüme düşmeden okur. DOM storage, satın alınmış eşyalar ve sahiplik silinmez.

## Yerel doğrulama

Gerçek WebGL: dört ana poz, sabit kol uzunlukları, ağır yüzey uzaması ve temas kontrolü geçti. Gerçek arena: donanımla 8,4 m/sn, kısa takla yaklaşık 2 m, ileri basılıyken kükremede durma, doğru kaynak süre/olay ve el alevleri geçti. Yedi hareket geçişi, koşu→sıçrama/iniş, takla ve hareketten beklemeye dönüşte yere gömülme kontrolü geçti. Bütün motifler tek tek yeniden taranmadı.

İmzalı sürümden önce CI; envanter/kayıt/bonus, temel arena, kaynak efekt/koşu, varlık ve Android paket kontrollerini aynı yayımlanacak dosyalar üzerinde çalıştırır. Sonuç ve APK sertifika/ZIP doğrulaması ayrıca kaydedilir.

## Hatalar ve gerçek sınırlar

- Yeni üretilen başı kaynak çeneye doğrudan aktarma denemeleri gerilen ağız yüzeyleri üretti. Elle tahmini koordinatla açılan ağız denemesi de hatalıydı. Bu dosyalar APK'ya alınmadı; seçilen anatomik gövdeye dönüldü.
- Ayrı donor UV adaları arasındaki koordinatları karıştırmak kürke giysi şeritleri taşıdı. Bu yanlış aktarım kullanılmadı. Gerçek yüzey aktarımı ve sürekli kürk malzemesi kullanıldı.
- İlk kısa testin bekleme koşulunda henüz tanımlanmamış JS globali okunuyordu; test yardımcı kodu düzeltildi. Başarısız testler geçti diye kaydedilmedi.
- Diğer üç kurdun yeni özgün üretimleri tamamlanmadı; mevcut prototipler korunuyor. İnsan modeli bu tur sıfırdan yeniden üretilmedi; mevcut 47 kemikli/11 klipli sürüm paketlenir.
- Bu, kullanıcının görsel kaliteyi kabul ettiği veya fiziksel Android telefonda test edildiği anlamına gelmez. Belirli FPS veya hatasızlık garantisi verilmez.
