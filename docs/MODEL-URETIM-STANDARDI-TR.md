# Kalıcı üretim standardı — onaylı gövde, kontrollü varyant

Güncelleme: 29 Ekim 2026. Kullanıcının son talimatıdır; önce rastgele karakter üretip sonra mevcut iskelete zorla uydurma yaklaşımının önüne geçer.

## Gövde önce gelir

İlk seri Buz Kurdu / Ice40 gövde ailesi üzerinden ilerler. Aynı doğrulanmış gövde, iskelet, bind pozu, skin ve hareket paketi üzerinde 3–4 kontrollü kurt varyantı hazırlanır. Bu seri kabul edilmeden başka anatomik aileye genişlenmez. Sonraki aile adayı güçlü/zırhlı Power42 / Köz Kurdu'dur. İnsan eşleri de doğrulanmış insan gövdesi/iskeleti üzerinde geliştirilir; kurt iskeleti insanın iskeleti sayılmaz.

Aileler: Ice40=Buz Kurdu; R1_54=Kan Kurdu; Power42=Köz Kurdu; Wraith58=Gölge Kurdu. Bilge Kağan vb. insan/karakter kimlikleri bu model ailelerinden ayrıdır.

Kaynak modeller ve DTX görselleri birlikte incelenir. Üretimde kullanılan kaynak geometri ile yeni modelleme/doku değişikliklerinin kökeni açıkça kaydedilir. Kaynak DTX kıyafetleri yeni özgün kıyafet diye sunulmaz; önceki reference-only kıyafet kuralı korunur. Kaynak varlıklar silinmez.

## Kostüm ve dekorasyon

- Bundan sonraki bütün kurtlarda pantolon veya aynı işlevi gören, anatomiyi izleyen alt giysi bulunur.
- Bilge'deki gibi uzun sarkan etek/kaftan panelleri, büyük bel süsleri ve uzun uçuşan şeritler yeni kurtlarda kullanılmaz. Mevcut sorunlu parçalar yeni standarda göre yeniden ele alınır.
- Küçük kemer, arma, kısa kürk detayı ve gövdeye yakın zırh kullanılabilir. Ana gövdeden taşma sınırlı kalır; eklem hareketini engellemez.
- Eklem yerleri, uzuv uzunlukları, bind matrisi ve kemik hiyerarşisi dekorasyona uydurulmaz.
- El/kolluk, kıyafet ve pelvis ağırlıkları birbirine karışmaz. Otomatik rig/weight başlangıçtır; görsel kabul değildir.
- Varyantlar yalnız rastgele renk değildir; aynı güvenilir gövdede kontrollü yüz/kürk, malzeme ve küçük donanım farklarıdır.

Süsler tek başına kemiği değiştirmez. Uzayan üçgenlerin nedenleri geometri, skin ağırlıkları, bind/koordinat dönüşümü ve hareket uyumunda ayrı ayrı araştırılır. Hata dekorasyon, ışık veya efektle örtülmez.

## Ağız ve yüz — zorunlu kalite kapısı

Dışarı taşan kırmızı yuvarlak/oval, dudak gibi görünen ağız içi, havada duran dişler ve yanlış çene pivotu kabul edilmez. Ağız içi çenenin içinde kalır; üst dişler başı, alt dişler alt çeneyi izler. Kapalı ağız ve kükremenin bütün evreleri yakından ön/yan/üç çeyrek açılardan kontrol edilir. Yapılmamış yüz hareketi tamamlandı sayılmaz.

## Dövme, hareket, efekt, ses

Sırt dövmesi sırtta; sol/sağ kol dövmeleri üst kolun arka yüzünde olmalıdır. Yerleşim yalnız bind pozunda değil gerçek bekleme pozunda da doğrulanır. Deriyi izler; kart gibi ayrılmaz veya titreşmez. Bonus ve sahiplik kayıtları korunur.

Kükreme efekti model ailesine bağlıdır. Kaynak olay zamanı, efekt geometrisi/sprite, renk-ölçek eğrileri ve sönme süresi korunarak taşınır; yalnız renk değişikliği farklı efekt sayılmaz. Kükreme daha tok/korkutucu sesle desteklenir; dijital kırpılma olmaz. Hafif, kısa kamera titreşimi eklenir; güçlü/zırhlı gövdede biraz daha belirgin olabilir. Titreşim kalıcı nişan yönünü değiştirmez.

Koşudan sıçrama, takla ve insana dönüş girişleri, yön tuşunu bırakmak gerekmeksizin çalışır. Yatay sıçrama hızı iki kez eklenmez; takla kısa ve tek-hedef/tek-vuruş hasarlı kalır. Koşu uyarlaması kullanıcı tarafından “en iyi şekilde yap” yanıtıyla onaylanmıştır. Orijinal kaynak dosyalar korunur; türetilen klip ayrı ad ve kökenle kaydedilir. İskelet/rest uzunlukları korunur; uyarlama izni başka klipleri gelişigüzel değiştirme izni değildir.

## Dokunmatik ateş ve nişan

Ateş tuşuna basılı tutarken aynı parmağı sağ/sol/yukarı/aşağı sürüklemek nişanı döndürür. Ateş kesilmeden yön değişir; boş ekrana ikinci bir basış gerekmez. Diğer parmak yön düğmelerini kullanabilir. Pointer iptali, ekran dışına sürükleme, uygulamanın arka plana alınması ve odak kaybı takılı ateş/nişan bırakmaz.

## Kabul ve kayıt

Her yeni gövde ve varyant; menü ve arenada ön/yan/arka görünüm, yürüyüş, koşu döngüsü, sıçrama/iniş, takla, pençe, dönüşüm ve kükremeyi geçer. Uzayan yüzey, yerden kopma, ayak kayması, yanlış dövme yüzü ve dışarı taşan ağız ayrıca incelenir. Otomatik oynanış testleri görsel kabul yerine geçmez.

“Üretildi”, “oyuna bağlandı”, “otomatik test geçti”, “görsel kabul geçti” ve “telefonda doğrulandı” ayrı kaydedilir. Kusurlu test sürümü hatasız diye sunulmaz. Ücretli üretim gerekiyorsa yeni kapsam/maliyet ayrıca belirtilir. Telefon ölçümü olmadan FPS/çökmez garantisi verilmez.

Bu dosya çalışma standardıdır; 3–4 yeni varyantın üretildiği veya açık hataların tamamının kapandığı beyanı değildir.

## 29 Ekim — bütün dövmeler ve seri üretim için bağlayıcı ek

Kullanıcı önce dövmenin giysiye taştığını, ardından biraz daha yükselmesi gerektiğini belirtti. Eski alt sırt/pelvis odaklı yerleşim geçersizdir. Ortak ayar `art/characters/model-families/tattoo-policy.json` içindedir; tek tek motifler veya varyantlar bu kuralı aşamaz.

- Sırt alanı Spine2–Neck arasından hesaplanır; 2,4 m modelde ek 5,5 cm yukarı taşınır. Başka boyda orantılı uygulanır. Alt sınır bel hattından ayrıca uzak tutulur.
- Bütün motifler aynı doğrulanmış gövde yamasını kullanır. Motif değiştirmek yerleşimi veya ağırlıkları değiştirmez.
- Pantolon/kumaş/deri/zırh/giysi olarak işaretli yüzeyler projeksiyona alınmaz. Dövme kıyafete basılmaz. Kol dövmeleri üst kolun arkasındadır.
- Seyrek, düz ve havada duran bir kart yerine gerçek eğri gövde üçgenleri kullanılır. Yüzey mesafesi ve animasyonda deriyi izleme denetlenir.
- Normal emissive şiddeti 0,025; kükreme tepe değeri 1,05'tir. Bunlar oynanış bonusu veya yüzde değildir. Poz bitince düşük değere döner; 20 saniyelik hız/hasar/savunma bonusu ayrıca sürer.

“Fabrika gibi” üretim, doğrulanmış ortak şablonun tekrarlanmasıdır. Bir gövde ailesinin kaynak hash'i, kemik hiyerarşisi, bind matrisleri, skin ve klip sözleşmesi sabitlenir. Yeni varyant yalnız izinli malzeme/doku ve küçük donanım değişiklikleri yapar. Aynı üretim aracı ve aynı kontrol listesi kullanılır; her model için sıfırdan rastgele rig aktarımı yapılmaz.

Üretim sırası: ortak gövde → kaynak bütünlük testi → bütün dövmelerin giysi sınırı testi → ön/yan/arka ve tam hareket döngüsü → normal/kükreme/toparlanma parlama testi → efekt/ses/oynanış → Android paket kontrolü. Bir kontrolün başarısız olması o modeli tamamlandı saymayı engeller. İlk gövdenin görsel kalite sorunları kapanmadan seri varyantlar bitmiş diye listelenmez.

Bilinen hatalar ve açık durumlar `GELISTIRME_HATALARI.md` dosyasının son bölümündedir. Yeni bir hata bulunduğunda neden, etkilenen çıktı, düzeltme ve doğrulama ayrı yazılır.

Mevcut eski Bilge gövdesinin korse üst sınırı 1,55 m'dir; bu sınır yalnız o geometri profiline aittir. Yeni pantolonlu native gövdeye rastgele kopyalanmaz. Aynı “yalnız gövde yüzeyi” kuralı, farklı gövdelerde bir kez doğrulanmış anatomik/giysi sınırıyla uygulanır. Varyant veya motif seçimi bu sınırı aşamaz.

`tools/apply_tattoo_policy.py` bütün modeli yeniden riglemez: üç dövme yüzeyini değiştirir; gövde, inverse bind matrisleri ve animasyon nesnelerini aynı bırakır. Önce bütün partiyi doğrular, sonra çalışma zamanı dosyalarını değiştirir. Aynı politika hash'iyle tekrar çalıştırmak dosyaları büyütmez veya yeniden dönüştürmez. APK paketleyici eski politika hash'ini kabul etmez. Bu araç seri üretimde ortak normalleştirme adımıdır; yeni gövdenin görsel kontrolünü kaldırmaz.

## Son talimat — yeniden tasarım ve kısa kontrol

Kullanıcı kurdun yeniden tasarlanmasını ve uzun test tekrarlarının azaltılmasını istedi. Her dövmeyi tek tek deneme zorunluluğu bu tur için kaldırıldı. Tek örnek dövmede gövde teması/parlama; bir kükreme ve efekt; kısa yürüyüş/koşu/takla kontrolü yeterlidir. Görsel tasarım açıkça hatalıyken geniş regresyon veya 36 motif taraması tekrarlanmaz. Sayısal testleri geçmesi, reddedilen modeli kabul edilir yapmaz.

Ice40'ın uzun boğazlı tasarımı yeniden üretimin temeli değildir. Daha önce seçilmiş Power42 gövdesi, kendi WT_NEW_WOLF_CH hareket paketiyle yeni tasarım adayı olarak hazırlanıyor. Kaynak iskelet/klipler korunur. Kendi önceki özgün modelimizin ayrıntılı kürk dokusu yeni gövdeye aktarılır; kaynak DTX kıyafetleri kullanılmaz. Yeni ücretli üretim yoktur. Bu, adayın tamamlandığı veya oyuna geçirildiği beyanı değildir.

## 29 Ekim — yeni ücretli kurt üretimi, eski kaplama yönteminin reddi

Kullanıcı yeni ücretli üretimi açıkça istedi. Tek kurt için 4K geometri + 8K PBR + mobil remesh tahmini 45 kredi; başlangıç bakiyesi 905. Geometri görevi `01a1878d-a5b3-72ac-9098-ccc4a0306a66` başarılı, gerçekleşen 25 kredi. Kaplama görevi `01a18814-08b2-747b-b5ba-1ce9d5c2c6b5` sürüyor. Tekrar gönderim yapılmadı; önceki kabul yerel işlem günlüğünden kurtarıldı.

Önceki Power42 adayında en yakın UV ile eski modelden renk aktarmak kürke giysi/metal desenleri yaydı. Bu yöntem reddedildi; aday oyuna kurulmadı ve tamamlanmış model değildir. Ice40 diz üçgenleri ve uzun boğaz sorunu da kapanmış sayılmaz. Yeni model doğal kürk, ayrı kumaş pantolon ve küçük buz bileklikleriyle üretiliyor. Kaynak animasyonların korunması ve yeni geometri uyumu henüz doğrulanmadı. Kuyruk, ağız/çene ve eklem uyumu özellikle kontrol edilecek. Kalitesiz gövdeyi yeniden zorla uydurup bitmiş sayma yöntemi tekrarlanmayacak. Test kapsamı kısa hareket, bir kükreme/efekt ve tek örnek dövme; bütün motifleri yeniden tarama yok.

## v0.1.17 — seçili gövdeye dönüş ve çalışan zincir

Yeni görselden üretim/remesh 35 krediyle tamamlandı. Üretilen geometriyi Power42 çenesine zorlayan baş/çene denemeleri bozuldu; tahmini ağız kesimi de yanlıştı. Bu adaylar oyuna alınmadı. Kaynak Power42 gövde, gerçek çene/dişler ve 72 kaynak klip korunarak özgün kürk/pantolon görünüşü Cycles ile aktarıldı. Yanlış UV adaları arasındaki renk karışımı giysi desenlerini kürke taşıyordu; bu yöntem kaldırıldı. Sürekli referans kürkü ve yeni giysinin yumuşak kasık ağırlıkları kullanıldı. 42 kemik, yaklaşık 14,2 bin üçgen. Yerel dört poz, gerçek koşu/takla/kükreme ve yedi geçiş kontrolü geçti. Telefon/görsel kullanıcı kabulü henüz yok. Diğer üç yeni özgün kurt tamamlanmış sayılmaz. Ayrıntı `docs/premium-wolf-01/TESLIM-TR.md`. Tek imzalı APK için CI aşamasına geçiliyor.
