# Animasyon yöntemi, araç seçimi ve kol deformasyonu

**Güncelleme:** Bu ilk kontrol yalnız eklenti kataloğuyla sınırlıydı. Sonraki kapsamlı web/kurulum araştırmasında MCP for Blender, Codex entegrasyonu ve Cascadeur’un resmî yerel MCP sunucusu bulundu. Güncel bulgular ve gerçek protokol testi [MCP araştırmasında](mcp-research/README.md).

Kullanıcı çalışma 02'nin de yetersiz olduğunu ve kolların bozulduğunu belirtti; referanstaki hareket ve efektlerin çok daha yakın olmasını istiyor. Önceki görsel çalışmalar kabul edilmiş değildir.

## Doğrulanan mevcut yöntem

Blender 4.3.2 kurulu. Önceki iskelet, poz anahtarları ve renderlar Blender'ın Python arayüzüyle üretildi. Bu, arayüzde insan animatörün yaptığı ayrıntılı sanatçı cilasının tamamlandığı anlamına gelmez. FK çalışma dosyaları düzenlenebilir, ancak kullanıcı tarafından yeterli bulunmadı.

İskelet ağırlık üretiminde somut hata: `['Arm', 'Hand', 'Clavicle', 'Digits']` ad eşlemesi `ForearmL/R` isimlerini büyük/küçük harf yüzünden kol zinciri saymıyordu. Bu kemikler gövde filtre koluna düşüyordu. Eşleme küçük harfe normalize edilerek düzeltildi. Sözdizimi kontrolü geçti. Bu kaynak düzeltmesiyle henüz GLB/APK yeniden üretilmedi; mevcut kolların tamamen düzeldiği iddia edilmez. Genel yakınlıkla ağırlık üretimi de tek başına kaliteli omuz ve dirsek deformasyonu sağlamaz.

## Araç kontrolü

- Plugin Management ile Blender, Rigify, Auto-Rig Pro, Cascadeur, Rokoko, DeepMotion ve Mixamo bağlantıları arandı. Bu adlarla uygun bir ChatGPT bağlantısı bulunmadı; dizin araması bütün eklentilerin yokluğu anlamına gelmez.
- Blender içindeki ücretsiz Rigify modülü kurulu fakat kapalıydı. Etkinleştirildi, tercihler kaydedildi; yeni Blender sürecinde `addon_utils.check('rigify') == (True, True)` doğrulandı. Henüz Bilge için yeni Rigify kontrol iskeleti tamamlanmış değildir.
- Rigify bir Blender eklentisidir. IK/FK kontrolleri için başlangıç aracıdır; bozuk ağırlıkları ve kötü omuz topolojisini otomatik olarak bitmiş sanatçı işine dönüştürmez.
- Auto-Rig Pro ücretli bir Blender eklentisidir; rig/animasyon aktarımı iş akışında değerlendirilebilir. Bu kurulumda doğrulanmadı, satın alma yapılmadı.
- Cascadeur ayrı bir animasyon programıdır; bu oturumda kullanılabilir kontrol bağlantısı doğrulanmadı. Doğrudan kurulu ChatGPT eklentisi gibi sunulmaz.
- Meshy mevcut yeteneklerde bulunuyor. Belgesine göre otomatik humanoid rig, katalog animasyonları ve ayrı FBX/BVH iskelet hareketi üretebilir. MP4'ü otomatik olarak aynı kurt iskeletine birebir aktardığı iddia edilmez. Yeni ücretli üretim yapılmadı.

## Uygulama sırası ve kabul

1. Omuz/üst kol/ön kol/bilek eksenleri, uzunluk ve bükülme düzeni; düzgün deformasyon iskeleti ve kontrollü ağırlıklar. Gerekirse omuz/dirsek topolojisi ve sınırlı yardımcı deformasyon kemikleri değerlendirilir. Kaynak şekil ve mobil üçgen bütçesi korunur.
2. Kol kaldırma, dirsek bükme, bilek çevirme ve farklı üst kol dönüşlerinde bütün deri yüzeyinin kontrolü. Kontrolün başarı ölçütü yalnız kemik uzunluğu değildir. Blender önizlemesi ve oyundaki GLB aynı deformasyonla değerlendirilir.
3. Tam 08-04-29 referansına göre ağırlık aktarımı ve hareket yayları; düzenlenebilir animasyon ve gerçek zamanlı karşılaştırma. Yeni ücretli hareket kaynağı gerekirse gerçek maliyet ayrıca açıklanır.
4. Son kullanıcı talebiyle efektli bir önizleme de hazırlanacak: el kemiğine bağlı alev, dövme/gövde parlaması, tepe vurgusu ve sönüş ortak zaman çizelgesine bağlanır. Karakter rengi ayrı parametredir. Sahnedeki başka aktörlerin etkileri ana oyuncuya otomatik mal edilmez. Bu efektli yeni önizleme henüz yapılmadı; önceki çalışmalar bilinçli olarak efeksizdi.
5. İskelet/hareket ve efektler tamamlanınca oyun geçişleri, gerçek kol deformasyonu ve telefon maliyeti kontrol edilerek tek APK teslim edilir. Bu aşama tamamlanmış değildir.

Yeni eklenti bir kalite garantisi değildir. Bu oturumda tamamlanan iş: araç araştırması, Rigify'nin etkinleştirilmesi ve somut ön kol sınıflandırma hatasının kaynakta düzeltilmesi. Profesyonel görsel kalite, referansla birebirlik ve yeni efekt teslimi iddia edilmez.

## Uygulama güncellemesi — çalışma 03

Kullanıcı ilk öneriyi seçtikten sonra Blender MCP canlı GUI bağlantısı, Bilge için Rigify üretimi, gerçek Rokoko retarget ve efektli Three.js oynatımı tamamlandı. Önceki "henüz iskelet tamamlanmadı" notu araştırma anını anlatır. Güncel kanıtlar, sınırlamalar ve tamamlanmayan işler [çalışma 03](bilge-roar-study-03/README.md) içindedir. Bu bir yeni Android sürümü değildir; ana çalışma zamanı modeli korunur. Referans kareleri elle yorumlandı; otomatik MP4 mocap'i iddia edilmez.
