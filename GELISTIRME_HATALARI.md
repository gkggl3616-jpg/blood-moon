# Geliştirme hataları ve düzeltme kaydı

Bu dosya bu konuşmada tespit edilen hataları, bunların sonucunu ve gerçek durumlarını kaydeder. Yeni hatalar bu kayda eklenecek. Bir prototip veya tarayıcı testi, gerçek telefonda/3B savaşta doğrulama yerine geçmez.

## Teslim ve iletişim

1. **Görseller görünmeden teslim edilmiş gibi konuştum.** Higgsfield widget'ları, uzak URL'ler ve yerel `sandbox:` bağlantıları kullanıcıda çalışmadı. Aynı yöntemi tekrarlamak zaman kaybettirdi. Düzeltme: görsel verisini doğrudan görsel eki yöntemiyle sunmak; APK için başarılı GitHub Actions çıktısı vermek. Kullanıcının cihazında görünürlüğü kendim doğrulayamadığımı açıkça belirtmek.
2. **Ağ izni bekleyen komutta uzun süre sessiz kaldım.** Android araçlarını indirirken ilerleyemedim ve zamanında açıklama vermedim. Düzeltme: kaynağı bağımsız hazırlamak, durum bildirmek ve kullanıcı istediğinde GitHub Actions ile derlemek.
3. **İlk APK planıyla tam oyun arasındaki sınırı her yerde yeterince açık tutmadım.** Mevcut proje bir Android WebView menü prototipidir; Unity/FPS, çarpışma ve ağ maçı yoktur. v0.1.7'de donanım ekranına gerçek iskelet animasyonu önizlemeleri eklendi; bunlar maç oynanışı değildir. Sonraki açıklamalarda uygulanmış hesap/arayüz ile planlanan oynanış ayrılıyor.

## Açılış ve ekran

4. **İlk açılış videosu otomatik değildi; bitince menüye geçmiyordu.** Düzeltildi: native otomatik medya izni, otomatik oynatma, `ended` ile lobi geçişi, atlama ve hata durumunda menüye dönüş.
5. **Sabit 1280x720 sahne ve `innerWidth` ölçeklemesi Android ekranında kırpıldı.** Düzeltildi: sabit sınırlandırılmış viewport, gerçek `clientWidth/clientHeight`, resize gözlemi ve native WebView viewport ayarları.
6. **Kırpmayı düzeltirken yanlarda geniş boşluk bıraktım.** Düzeltildi: 720 tasarım yüksekliğini koruyup tasarım genişliğini ekran oranına göre açmak. Video oranını korumak ayrı bir davranıştır.
7. **Native dialog/top-layer menünün ölçeğini paylaşmadı.** Ayarlar ve etkinliklerde dev yazılar, düğmeler ve kaydırma oluştu. Düzeltildi: aynı sahnede ölçeklenen modal katmanı, küçük ölçüler ve farklı ekranlarda sığma kontrolleri.
8. **Çentik ve sistem çubuklarını başlangıçta hesaba katmadım.** Düzeltildi: Android WindowInsets güvenli alanları; yine de fiziksel cihaz doğrulaması gerekir.
9. **İlk etkinlik ve teçhizat pencereleri fazla sade kaldı.** Düzeltildi: görev/avantaj kartları, setler, form seçimi, slotlar ve envanter/mağaza sayfaları.

## Tasarım ve kullanıcı yönlendirmesi

10. **Kurtları yeterince farklılaştırmadım.** Benzer yele, gövde ve aksesuarlar aynı görünmelerine neden oldu. Düzeltme: v0.1.6'da dört gerçek gövde oranı, modüler aksesuar ve dövme rengi uygulandı. Yedi karakter şimdilik bu dört geometriyi paylaşır; ayrı yele ve karaktere özel pençe animasyonları tamamlanmadı.
11. **Bazı Higgsfield çıktıları dört ayaklı kurt üretti.** İki ayaklı pençe kullanan tasarıma uymadı. Düzeltildi: iki ayaklı insansı anatomiyi açıkça isteyen referans düzenlemesi; eski görseller `prototypes/archive/` altında tutuluyor.
12. **Sıçrama konseptine hedef/iniş halkası koydum.** Kullanıcının doğal ileri sıçrama isteğine aykırıydı. Kural düzeltildi: yerde hedef alanı yok; doğal ileri sıçrama. Gerçek 3B sıçrama henüz yok.
13. **Kullanıcı istemeden yetenek laboratuvarı ekledim.** Kullanıcı kaldırılmasını istedi. Kaldırıldı. Sonraki donanım sayfası bir envanter ekranıdır; arena/laboratuvar yoktur.
14. **Pençe animasyonu/izi ve gövde uyumu başta ortak kaldı.** Düzeltme: her karakter için ayrı hareket ve iz tanımı. Gerçek animasyon klipleri/rig'ler üretilecek; mevcut kartlarda tarif gösteriliyor.
15. **Örnek görsel ve koddaki denge değerleri aynı değildi.** Görseller kesin oyun verisi değildir. Çalışan prototipin verisi kodda tutulur; sayılar testle doğrulanır.
16. **Kükreme eklenince pasif +%80 üstüne bonus koymak toplam tavanı aşacaktı.** Önlenerek düzeltildi: ortak 100 tabanı, 180 toplam tavanı, pasiflerde kükremeye pay, 20 saniyelik %20 hız/%15 hasar/%30 savunma çarpanları. Aksesuarlar kozmetiktir. v0.1.7 kuralı: tek takla yuvası; standart yalnızca takla, efsanevi koşu ve takla açar.

## Derleme ve testler

17. **Yereldeki tarayıcı ile GitHub Chromium'un medya desteğini aynı varsaydım.** İlk CI video testi takıldı. Düzeltildi: codec destekli Chrome kanalı ve gerçek video başlangıç/bitiş testi.
18. **CI'da mevcut Chrome'u yeniden kurmaya çalıştım.** Gereksiz bekleme oluştu. Düzeltildi: kurulu Chrome'u kullan, yalnızca yoksa kur.
19. **Resize sonrası yerleşimi hemen ölçtüm.** Asenkron güncelleme CI'da yanlış başarısızlık verdi. Düzeltildi: ölçümden önce sınırların güncellenmesini beklemek.
20. **Playwright string ifadesi CSP ile çakıştı.** Düzeltildi: fonksiyon şeklindeki test ifadeleri; ürün CSP'si gevşetilmedi.
21. **Yeni sayfalarda aynı CSS sınıfını seçen test strict-mode hatası verdi.** Düzeltildi: ilgili ekranı belirten selector kullanmak.
22. **JRE içindeki derleyiciyi ve `--release` desteğini başlangıçta doğru değerlendirmedim.** Düzeltildi: mevcut JDK compiler modülü ile uyumlu source/target derlemesi; APK imzası ve arşivi kontrol ediliyor.
23. **Her temiz CI çalışmasında yeni geliştirme imzası üretiliyor.** Durum: hâlâ açık. Eski APK üzerine kurulum reddedilebilir; eski test sürümünü kaldırmak gerekir. Kalıcı üretim/test anahtarı ayrıca güvenli şekilde yapılandırılmalı. Anahtar depoya eklenmedi.
24. **GitHub artifact yönlendirmesini CLI üzerinden indirme bazı ağlarda reddedildi.** Düzeltme: GitHub artifact bağlantısı ve gerektiğinde connector'ın artifact indirme aracı. Başarılı CI çıktısını doğrulamadan tamamlandı denmiyor.

25. **Koşu/takla donanımını ilk uygulamada bütün kurtlar için ortak tuttum.** Yayınlamadan önce düzeltildi: her seçili karakter/kurt için ayrı kayıt anahtarı var; bir kurda takılan özellik diğerine otomatik geçmez. Bu geçiş test ediliyor.

26. **Meshy CLI ilk bağlantısında Node proxy ayarı eksikti.** Düzeltildi: resmî CLI mevcut ağ proxy’sini ve sistem CA güvenini kullanıyor; cihaz onayıyla giriş doğrulandı.
27. **3B gövde dokusu ilk WebGL kontrolde siyah/metalik, sonra beyaz göründü.** Kök neden: GLB içindeki blob dokuları CSP connect-src ile engelleniyordu. Yerel blob erişimi açıldı, metaliklik ve normal etkisi ayarlandı; dokunun gerçekten yüklendiği test ediliyor.
28. **Blender renderında mevcut olmayan denoiser varsayıldı.** Düzeltildi: desteklenmeyen denoising kapatıldı, CPU Cycles renderı üretildi.

29. **İlk koşu/takla rig denemesinde kemikler global yukarı eksenine göre yeniden yönlendirildi.** Baş/gövde dönmesi ve bükülmeler görüldü. Düzeltme: her kemiğin rest-pose yönü ve roll ekseni korunuyor; taklanın bütünsel dönüşü ayrı uygulanıyor. Animasyonlar önizleme aşamasında, deformasyon cilası hâlâ gerekli.

30. **Hızlı karakter değişiminde yüklü modele dönülünce yükleme durumu yanlışlıkla açık kalabiliyordu.** Düzeltildi: bekleyen farklı model yüklemesi geçersiz kılınıyor, mevcut model hazır duruma alınıyor. Kurtlar arasında hızlı geçiş akışı test ediliyor.

31. **Ağır kurtlarda bel ve karın derinliğini de büyüttüm.** Göğüs/omuz ağırlığı yerine kalın bir bel silüeti oluştu; kullanıcı referansları atletik ve dar bel istiyordu. Düzeltme: dört gövdede bel ve karın ayrı biçimlendirildi, omuz hacmi korundu. İlk düzeltme taslağındaki aşırı daralma yayınlamadan yumuşatıldı. Ön kollar/eller gövde daraltma alanından çıkarıldı; ön ve yan görünüm kontrol ediliyor.
32. **İlk dövmeler ayrıntılı desen yerine kaba çizgi geometrisi olarak kaldı.** İstenen görsel kaliteyi karşılamadı. Düzeltme: dokuz ayrıntılı özgün renkli alfa/emisyon dövmesi, bağımsız kol seçimleri ve yüzeye oturan UV patch'leri eklendi. Zar, tekboynuz ve ölüm temaları da var; örnek oyunun doku dosyaları kopyalanmadı.
33. **Dövme rig ağırlıklarını gövdeden bağımsız hesapladım.** Eklem bükülmesinde yüzeyden ayrılma riski vardı. Düzeltme: her dövme köşesine en yakın gövde üçgeninin gerçek iskelet ağırlıkları ara değerlemeyle aktarılır. Bu yöntem deformasyon cilası ve fiziksel cihaz kontrolünün yerini almaz.
34. **Boyunluk fazla geniş, deri kayış ise düz bir çubuk gibi gövdeden uzaktaydı.** Yakın model kontrolünde görüldü. Düzeltme: boyunluk boyun çevresine küçültüldü; kayış gövde önüne oturan yassı deri şeridi oldu ve yalnız tılsımlı görünümde gösterilir. Kaba raycast ızgarasının kürk çıkıntılarında köprü kurması da giderildi: dövmeler artık gerçek gövde üçgenlerini izler.

## Açık sınırlar

- Fiziksel Android cihaz ve gerçek 3B savaş testi yapılmadı.
- Mağaza sahipliği, kurt başına takla kuşanması ve kükreme hesabı çalışır. Donanım ekranında gerçek 3B model, ayrı emisif dövmeler ve üç ilk iskelet animasyonu bulunur. Rig ağırlıklarında elle deformasyon cilası gerekir; gerçek 3B savaş hareketi, çarpışma ve hasar testi yoktur.
- Yeni silah/bomba/bıçak kategorileri katalog taslağıdır; modelleri, atış veya hasar fiziği yoktur.
- Tarihî esinli karakter görselleri kurgu konseptleridir; tarihsel portre doğruluğu iddiası yoktur.

35. **Ortak baş ve kürk yapısı karakterleri benzer bıraktı.** Kullanıcının son onayıyla yalnız Bilge Kağan insan/kurt çifti yeni kaynaklardan üretildi (30+30 kredi). Diğer altı yeni model konsept olarak hazır, ücretli üretimleri onaylanmadı. Koşu/takla ortak; pençe şablonları farklıdır.
36. **APK indirmesini ZIP ve model paketi bağlantılarıyla karıştırdım.** Yeni teslim doğrudan tek `.apk` release varlığıdır; bütün modeller ve veriler içinde bulunur. Kaynak modeller ayrı kurulum paketi değildir.
37. **Blender'da yeniden boyutlanan packed dokunun kopyası piksel verisini kaybetti.** Dışa aktarma durdu. Düzeltme: küçültülen dokuyu gerçek PNG'ye kaydedip yeniden yükleyerek paketlemek; yeni Meshy görevi açılmadı.
38. **GitHub bağlantısının imza sırrı yazma yetkisini varsaydım.** API 403 döndü. Özel anahtar depoya konmadı. Geliştirme anahtarı Actions cache'inde korunur; kalıcı üretim sırrı ayrıca kurulmalıdır. Cache kaybolursa imza sürekliliği garanti edilmez.
39. **İlk test alanında gölge sert daire, hareket kontrolü joystick ve eylemler köşeliydi.** Kullanıcı düzeltmesi: karakterden düşen 1024 PCF yumuşak gölge, dört yön düğmesi, ileriye iki basışta koşu, simgeli yuvarlak eylemler.

40. **İnsan kamerasından envantere dönünce paylaşılan model gizli kalıyordu.** Düzeltildi: önizleme sahipliği devralınca kök görünürlüğü sıfırlanır. Test artık yalnız yükleme bayrağını değil, görünür modeli ve gerçek çizilen üçgenleri de kontrol eder.

41. **Kurt üçüncü şahıs dikey bakışı, insan birinci şahıs bakışının tersine çalışıyordu.** Kök neden: aynı pozitif pitch insan kamerasını yukarı çevirirken kurt yörüngesini yukarı taşıyıp aşağı baktırıyordu. Kurt yörünge yüksekliği ters işaretle düzeltildi; iki formda gerçek pointer sürüklemesiyle doğrulanır.
42. **Taklayı hasarsız bırakan eski kural artık geçerli değil.** Kullanıcı açıkça taklanın hasar verdiğini belirtti. Temas süpürmesi, hedef başına taklada tek isabet, siper çarpışması ve hasar/mağaza açıklamaları birlikte güncellendi. 38 taban hasar yerel denge tercihidir; erişilemeyen videodan çıkarıldığı iddia edilmez.
43. **Yeni YouTube referansı bu ortamda engellendi.** `NGqOn5o0dHE` için sayfa/API isteği ağ geçidinden 403 aldı. Video izlenmedi; zaman kodlu yeni video analizi açık. Gözlenen eski kareler, kullanıcı beyanı ve uygulama tercihleri `docs/video-NGqOn5o0dHE.md` içinde ayrı kaynaklar olarak kaydedildi.
44. **Kükreme pozu yeni bir eylemle kesilebiliyordu; takla anında dönüşe başlıyordu.** Kükremeye 1.2 sn poz kilidi, taklaya hazırlık/toplanma/dönüş/iniş fazları eklendi. Dört kurt aynı koşu/takla şablonunu korur. Çene/yüz animasyonu hâlâ tamamlanmadı.
45. **Yeni takla teması testinde sıfır uzunluklu hareket parçası uzak hedefleri vurabiliyordu.** Duvara dayanıp duran oyuncuda doğru parçasına izdüşüm sıfıra bölünerek NaN üretiyordu. Düzeltildi: durağan adımda oyuncu konumu ile nokta teması hesaplanır; mesafe/görüş hattı kontrolleri korunur. Siper önünde durma ve uzak hedeflerin hasar almaması testi bunu yakalar.
46. **Görüntü bütün telefonlarda 1.25 DPR ile sınırlandırılıyordu.** DPR3 ekranda görüntü piksel sayısı ekranın yaklaşık %17'siydi. Düzeltme: cihaz DPR'sini izleyen Net / 4.2M piksel ve Dengeli / 2M piksel bütçeleri, framebuffer ölçümü, kenar yumuşatma ve doku filtreleme. Gerçek telefon FPS'i ölçülmüş değildir.
47. **Koşu uzuv hedefleri kaynak kol/bacak uzunluklarını korumuyordu; pozlar esneyip dengesiz görünüyordu.** Ortak v3 IK, ayrı temas/toparlanma fazları, kısa koşu döngüsü, daha sabit baş, hazır duruş ve pençe tabanı yüksekliği eklendi. Dört gerçek GLB'de deforme mesh sınırları, eklem uzunlukları ve döngü dikişi test edilir.
48. **Taklada 180 derece yakınındaki quaternion işaretleri, Blender ara değerlemesinde gövdeyi bir kare yukarı fırlatıyordu.** Ardışık quaternion yarımküreleri eşitlendi. GLB klipleri 0.033 saniye yerine sıfırda başlatıldı; gerçek klip süresi ve döngü uçları doğrulanır.
49. **Takla çok uzağa gidiyordu; koşu sıçramasına ikinci yatay hız ekleniyordu.** Takla 0.8 sn / yaklaşık 2m oldu, hasarı korundu. Takla zamanı sabit fizik adımında ilerler; mesafe render FPS'ine bağlı hesaplanmaz. Koşu sıçraması tek yatay hızı taşır, havada takla geçişi ve koşu moduna dönüş vardır. Kükremede yatay hız tamamen sıfırlanır.
50. **Yeni ayar alanları eklenince test eski iki alanlı kayıt şemasını bekliyordu.** Beklenti hassasiyet ve görüntü tercihini kapsayacak şekilde güncellendi; eski ses/volume kayıtları varsayılanlarla okunur. Hassasiyet ekran genişliğine göre normalize ve kalıcıdır.

## v0.1.12 — güncel düzeltme

- Genel 180 tavanı ve kozmetik dövme kararı son kapsamla geçersiz; RogueGear temel/pasif/dövme/aktif katmanlarını ayrı hesaplar. Gerçek hasar, can, hız ve savunma bu hesabı kullanır.
- Kaynak modeli iyileştirmeye çalışırken beyaz kürkü düz/koyu bir gövdeyle değiştirdim. Kullanıcı 11513–11517 SS ile bunu reddetti. Deneme tamamen geri alındı; özgün gövde/UV korunur.
- Genel bekleme dirsek hedefleri kaynağın neredeyse düz A-poz kollarını dışa büküyordu. Kaynak omuz/dirsek/bilek noktaları ve uzunlukları beklemede korunur; kaynak–teslim geometri farkı otomatik ölçülür (yaklaşık 2 mm nefes hareketi).
- Eski teçhizat ekranının kaydı yeni gerçek donanıma bağlı değildi. Teçhizat menüsü artık gerçek sol yuva/sağ ızgara ekranını açar.
- Koşu hızı arttığında test, iniş sonrasında basılı kalan tuşla gidilen mesafeyi de sıçrama sayıyordu. Fizik kalkış/iniş mesafesini ve tepe yatay hızı ayrıca kaydeder.
- #23 tarihî imza sorunu: kalıcı cache anahtarı kullanılır; bu sürümün sertifikası yayımlanmış v0.1.11 ile ayrıca karşılaştırılır. Eski kayıtları silmek için uygulamayı kaldırmak istenmez.
- Ayrıntılı güncel durum, eşya tablosu ve açık kalite işleri: docs/guncelleme-v012.md.

- Yayın testinde hızlı SR-01 atışı → kurt dönüşümü → pençe vuruşu akışı takıldı: insan silahının 0,95 sn atış kilidi kurt formuna sızıyordu. Yerel yavaş yazılım renderı bu yarışı görünmez kılmıştı. Form değişiminde atış kilidi sıfırlandı; dönüşüm/kükreme sırasında ateş düğmesi kilitli görünür, test gerçek eylem-hazır durumunu bekler ve sıfır taşınmış atış kilidini doğrular.

## Yeni üç video incelemesi — henüz uygulanmadı

- Kaynak modelin bekleme biçimini korumak, koşu animasyonunun hedef harekete benzediğini kanıtlamadı. Video 1’de kısa/hızlı salınım ve zayıf ağırlık aktarımı sürüyor. Prosedürel koşu hedef videonun uzama/toparlanma/destek pozlarına göre yeniden kurulmalı.
- Koşu klibi 0,533 sn iken arena çarpanı başlangıç rünüyle 1,5, etkin döngü ~0,356 sn. Menü farklı tempoda oynatıyor. Hız, adım mesafesi ve faz birlikte ayarlanmalı. Hedef kayıt sayacı yavaş oynatımı gösteriyor; görünen ~1 sn döngüyü doğrudan gerçek oyun süresi saymak yanlış.
- Mevcut kükreme el hedefi göğüs hizasında; yeni videoda iki el baş üstüne kaldırılıyor. Aynı poz/süre bütün kurtlara aktarılmalı; efekt yalnız karakter rengiyle farklılaşmalı. Sabit mor el parçacığı güncellenecek.
- Sahnedeki başka oyuncuların/belirsiz kaynaklı yeşil patlamaların tamamı ana oyuncunun kükremesi diye kopyalanmayacak. Aşamalar ve inceleme kanıtları `docs/uc-video-kosu-kukreme-analizi-20261028.md` içinde. Bu maddeler teşhistir, tamamlanmış düzeltme değildir.

## v0.1.13 — üç video teşhisinin uygulanması

- Eski hız çarpanı kaldırıldı; gerçek mesafe/çevrim sözleşmesi menü ve arena arasında ortak. Koşu ana fazları yeniden yazıldı.
- Kükreme artık baş üstü poz, bilek/parmak hareketi ve gerçek çene kullanır. Aynı efekt biçimi karakter rengine boyanır.
- Yeni parmak kemiklerine en yakın mesafeyle ağırlık atamak etek köşelerini ellere çekiyordu. El/kol bölgeleri anatomik sınırlarla ayrıldı; gerçek kaynak etek köşelerinde el ağırlığı sıfır olarak doğrulandı.
- Sabit IK destek hedefi tek başına mesh temasını garanti etmedi. Avuç bağları, gerçek mesh tabanı kalibrasyonu ve 60 Hz FK aktarımıyla ara kare çökmesi giderildi; test gerçek dışa aktarılmış deri köşelerini ve destek kaymasını ölçer.
- Ayrıntılar, ölçüm sınırları ve açık kalite işleri: docs/guncelleme-v013.md.

## v0.1.14 — kullanıcı kükreme sonucunu reddetti

v0.1.13 baş üstü el testi, fazla düz/dar kol duruşunu yakalamadı. Bu sonuç referans kabulü sayılmamalıydı. Yeni poz; dışarıda bükülü dirsek, içe eğimli ön kol, göğüs/boyun açılması ve belirgin hazırlık kullanır. Kısa kollu kurtlarda öne uzak el hedefi yeniden düzleşme üretiyordu; uzaklık düzeltildi. Gerçek GLB ve WebGL dirsek ölçümleri eklendi. Ayrıntı: docs/kukreme-duzeltmesi-v014.md.

## v0.1.15 hazırlığı — Meshy hattı, birinci şahıs ve kredi hataları (31.10.2026)

51. **Uzayan üçgen yerine şeffaf delik ürettim.** El-uyluk köprü üçgenlerini silip yerini kapatmadım; Kurt Kral'da 194, diğer kurtlarda ~90 delik kaldı, pelerin şerit şerit göründü. Düzeltme: iki yan ayrı ayrı kapatılıyor; `verify_models.py` kaynağa göre 300 cm²'den büyük yeni açık halka bulursa derleme durur.
52. **Pelerin/kuyruk/saç köşelerine Meshy'nin kol-bacak ağırlıkları karıştı.** Bu köşeler artık gövde payını sadece gövde kemiklerinden alır; Kral'ın elle yapılmış boynuz+pelerini eski ayarlı ağırlıklarını korur.
53. **Uzama testi 4 etki sınırını dikkate almıyordu.** Sevk edilen model her köşede en fazla 4 kemik kullanır; uzama döngüsü artık tam bu kesilmiş ağırlıkları dener.
54. **Birinci şahıs kolları gövde/saç/pelerin kemiklerine de bağlıydı.** Kamera önünde dev düz üçgenler ve havada uçan ceket/saç parçaları oluştu (kullanıcı Zeynoş SS'i). Kalıcı önlem: FP kolu yalnız Clav/UpperArm/Forearm/Hand/Fingers ağırlığı alır, kol kemiğine uzak deri FP'ye girmez; `verify_models.py` ikisini de denetler, `verify_fp.py` 6 karakter × 2 silah × 3 bakış açısında ellerin kabzaya ulaştığını CI'da ölçer.
55. **Karakterleri çok düşük poligonla ürettim; eller parmak ayrılamayacak kadar kaba.** Mobil bütçe için gövdeyi indirgemek ellerin de 20–60 köşeye düşmesine yol açtı; işaret parmağı tetiğe konamaz. Ders: birinci şahısta görülen eller/eldivenler gövdeden ayrı, yüksek detaylı ve parmak kemikli üretilir (karaktere özel eldiven). Gövde düşük poligon kalabilir, eller kalamaz.
56. **Meshy kredisini yanlış iş tükettti.** Silah görselleri için plan dosyasını güncelledim sanırken bilgisayardaki eski Gökçe planı okundu; 6 gereksiz görsel (~54 kredi) üretildi. Ders: her iş kendi adıyla ayrı plan dosyası okur; işi başlatmadan önce plan dosyasının içeriği bilgisayarda doğrulanır.
57. **6 eşzamanlı 4K görselden-3D isteği "yetersiz kredi" aldı.** Bakiye kontrol edilmeden toplu iş başlatıldı. Ders: toplu Meshy işinden önce `/balance` okunur, maliyet hesaplanır, istekler sırayla gönderilir.
58. **Dört ayak koşusunun adımı kısa.** Yere basan pençeler ~3 m/sn gidiyor, oyun 8 m/sn koşuyor; hızlandırmak 0,14 sn'lik telaşlı döngü yapar. Açık iş: daha uzun adımlı gallop.
59. **Pelerin/kuyruk/saç kuralı kaynakta vardı ama sevk edilen ağırlıkta yoktu.** Yeni test (`verify_models.py`: kumaş köşesi aynı anda kol/bacak kemiğine >%5 bağlı olamaz) ates 15, ay 28, bilge 19, kral 11, zeynos 1222, human-zeynos 2620 ihlal buldu. Sebep: ağırlık aktarımı ve uzama düzeltmesi kuralı sonradan bozuyordu. Kalıcı çözüm: `destretch` son 4-etki ağırlığını yazarken kumaş köşesindeki kol payını Clav'a, bacak payını Hips'e taşır; altı model yeniden derlendi, hepsi geçti.
60. **Poligon bütçesi yazılı değildi, Zeynoş insan formu 61.980 üçgendi.** Bütçe sabitlendi (insan 35k, kurt 30k, silah 35k, bomba 10k; `docs/uretim-standardi.md`) ve hem `verify_models.py` hem `build_apk.py` zorlar. Zeynoş Blender Decimate ile 33.459 üçgene indirildi. İlk denemede yüz de indirgendi ve ifade bozuldu. Ders: indirgeme yalnız saç/kafa arkasına uygulanır; yüz, eller, gövde ve giysi korunur, sonuç görsel olarak karşılaştırılmadan kabul edilmez.
61. **Kodla çizilmiş eldiven ele oturmadı.** Kapsül parmaklı eldiven çok büyük kaldı, bilekte gri bir halka göründü ve elin yönü ön kolla uyuşmadı (kullanıcı SS'i). Ders: eldiven sonradan eklenen ayrı parça olmaz. Karakter üretiminde aksesuar olarak modelin parçası istenir (`docs/uretim-standardi.md`). Kodla üretilen eldiven kaldırıldı.
62. **Üçüncü şahısta el kalçaya lastik gibi uzadı.** Meshy, kalçaya değen ön kol ve el köşelerine bacak ağırlığı da verdi; IK kolu kaldırınca deri gerildi. Kalıcı çözüm: insan gövdesinde bir köşe ya kol tarafına ya bacak tarafına ait olur. Karar aktarılan ağırlığa göre değil, kol ve bacak kemik çizgisine uzaklığa göre verilir; aradaki köprü üçgenleri iki yandan kapatılır. `verify_models.py` aynı anda iki tarafa bağlı köşeyi yakalar.
63. **Birinci şahıs elleri parmak kemiği olmayan gövdeden kesiliyordu.** Meshy iskeletinde parmak kemiği yok; tek kemikle bükülen el pençe gibi açılıyordu (kullanıcı SS'i). Araştırma: FPS oyunları birinci şahısta karakter gövdesini değil, parmak kemikli ayrı bir kol modelini kullanır. Çözüm: CC0 "FPS arms rigged" (MakeHuman tabanlı, parmak başına 3 kemik) `models/fp_arms.glb` oldu (`tools/weapons/build_fp_arms.py`). El, silahın kabza soketine göre yerleştirilir; her parmak kabza yüzeyine değene kadar kapanır, işaret parmağı tetiğe çözülür. Ten rengi karaktere göre boyanır. `verify_fp.py` soket mesafesini 2 cm altında ister.
