# Bilge Kağan — özgün insan/kurt entegrasyonu

Güncel çalışma kaydı, 29 Ekim 2026. Bu dosya bitmiş kalite veya hatasız APK beyanı değildir.

## Uygulananlar

- Meshy ile iki özgün geometrik model üretildi. 60 kredi onayına karşı gerçek tüketim 30 kredi (15+15). Yeni ücretli rig/animasyon üretimi yapılmadı.
- Kurt Ice40, insan Human47 kaynak iskeletine bağlandı. Kemik adları, hiyerarşi ve bind dönüşümleri korunuyor. Kaynak dosyalar değiştirilmiyor.
- Kurt 68, insan 11 kaynak klibi taşır. Kaynak anahtar zamanları yeniden örneklenmez. glTF için koordinat dönüşümü ve birim quaternion normalizasyonu uygulanır; geri dönüş hata ölçümü `native-conversion.json` içindedir.
- Menü ve arena aynı `models/bilge.glb` dosyasını kullanır. İnsan önizlemesi `models/human-bilge.glb` dosyasını kullanır. Eski opt-in çift düğmesi kaldırıldı.
- Model tipi karakter kimliğinden bağımsızdır. Diğer üç model tipi henüz yeni özgün geometriyle tamamlanmış değildir.
- Kaynak kükreme T_CRY: 1,933 sn. Kaynak `create_attachfx` olayı: 0,933 sn. El alevleri ve dövme parlaması bu olaya göre zamanlanır. Efekt yeniden oluşturulmuştur; kaynak oyunun özgün efekt dosyasının birebir çözüldüğü iddia edilmez.
- Kaynak T_Specialatk: 1 sn; yaklaşık 2 m fiziksel hareket, mevcut tek-hedef/tek-vuruş ve siper kontrolü korunur. Kaynak yatay root hareketi fiziğe ikinci kez eklenmez. Zemine temas düzeltmesi yeni modelin örneklenmiş alt sınırından hesaplanır; kaynak klip anahtarları değişmez.
- Ayrı sırt/sol/sağ dövme yüzeyleri gövdeyle aynı ağırlıklara sahiptir; mevcut sahiplik, kayıt, kuşanma ve bonus hesabı korunur.
- Kaynak kıyafet DTX'leri yeni dokulara aktarılmadı. Yeni modeller kendi üretilmiş renk/normal/pürüzlülük dokularını içerir.
- Gerçek çene ayrımı, ağız içi ve diş geometrisi eklendi; mevcut çene kemiğini kullanır.

## Doğrulama ve açık kalite kapısı

`static-build.json`, `native-conversion.json`, `grounding.json` teknik ölçümleri tutar. `views/` gerçek GLB renderlarıdır; konsept görseli değildir. Test logları aynı dizindedir. Başarısız test ve görsel deformasyonlar çözülmeden sürüm tamamlandı olarak yayımlanmayacak.

Kol/kıyafet ağırlıkları üzerinde görsel kalite kontrolü sürmektedir. Kaynak koşu bu modelde iki ayaklıdır; dört ayak koşu tamamlandı diye sunulmaz. Telefon performansı, APK imza uyumluluğu ve cihaz kurulumu bu çalışma için henüz doğrulanmadı. Yeni APK yayımlanmadı.

## Dövme hesap sözleşmesi

Temel × [1 + pasif/100 + uygulanabilir dövme bonusları toplamı/100] × aktif yetenek çarpanı. Örnek: 100, +%20 pasif, +%240 dövme = 360; +%15 hasar kükremesiyle 414. Aynı eşya iki kere sayılmaz. Kükreme 20 sn +%20 hız / +%15 hasar / +%30 savunmadır. Savunma değeri doğrudan yüzde hasar azaltma olarak kullanılmaz. Gerçek eşya tablosu `app/src/main/assets/gear-system.js` içindedir.

### Test güncellemesi

İlk gerçek tarayıcı kontrollerinde envanter/kayıt/bonus/silah zinciri PASS; bağımsız Bilge testi PASS; dört karakter koşu/efekt regresyonu PASS. Bu sonuçlar test JSON/loglarındaki asset hash'leriyle ilişkilidir. Sonraki geometri değişiklikleri için yeniden doğrulama gerekir. Görsel insan bilek/kıyafet çekilmesi hâlâ kalite engeli; sürüm yayımlanmadı. Kullanılmayan eski Guardian deneme modelleri ve opt-in yükleme kodu APK varlıklarından çıkarıldı; referanslar `art/` altında korunuyor.

### Son doğrulama / yayımlama kararı

Geniş arena testi tek başına tekrarda PASS oldu: havada takla ve iniş, kısa tek-hedef hasarı, siper, dönüşüm, bakış yönü, çift basış, sıçrama, kükremede durma, bonus süresi, gölge ve tek WebGL bağlamı doğrulandı. İlk zaman aşımı yoğun eşzamanlı yerel yükte gözlendi; kalıcı fizik hatası olarak yeniden üretilemedi.

Son özgün insan modelinin bilek/kıyafet ağırlıklarında gözle görülür çekilme devam ediyor. Bu yüzden **üretim kabulü başarısız / APK yayımlama kapalı**. Kullanıcının “her şeyi tamamlamadan atma” talimatına göre bu çalışma için APK indirme bağlantısı verilmeyecek. Mevcut APK önceki sürümdür ve bu değişiklikleri içeriyor diye sunulamaz.

Kaynak anahtarları korunuyor; küçük yüzey ayrıntıları yeni PBR atlaslarından geliyor. Native gait için temel oynatma hızının 1 olması hedeflendi; çalışma zamanı stride sözleşmesi fiziksel 8 m/sn koşu ve 4,3 m/sn yürüyüşe göre tanımlıdır. Ayak temasından ölçülmüş bir stride kalibrasyonu olarak sunulmaz. Telefon için hatasızlık/FPS garantisi yoktur.
