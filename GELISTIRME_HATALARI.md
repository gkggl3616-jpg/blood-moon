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

## Bilge kükreme çalışması 01 — APK öncesi inceleme

Kol hedeflerini tekrar ayarlamak, referans hareketin gücünü üretmedi; kullanıcı sonucu yeniden reddetti. Ayrı bir düzenlenebilir FK çalışma klibi kuruldu. Geniş kol açılışının ön görünüşü, ön kol ağırlıklarının bel/kıyafete sızdığını gösterdi: eski el/parmak odaklı test bunu yakalamıyordu. Yeni çalışma içinde 415 merkez bölge köşesi düzeltildi; özgün bind geometrisi değişmedi. Çene işareti ön görünüşte kontrol edilip aşağı açılacak şekilde düzeltildi. Bunlar henüz çalışma zamanı modellerine taşınmadı. Hareket/renk/teknik testlerin geçmesi görsel kabul değildir. Ayrıntı ve videolar: docs/bilge-roar-study-01/README.md.

- Çalışma 01 karşılaştırmasının kaynak kesiti kullanıcıya göre kükremenin sonunu erken kesiyordu. Sonraki 08-04-29 kaydı tam ana referans oldu. Karşılaştırma yeni kaydın tamamını ve 38 kareyi kullanır; dar kadraj kaldırıldı, erken tekrar engellendi. Mevcut 1,2 sn çalışma sağ panelde eski çalışma olarak etiketlidir; yeni süreyle eşleştiği iddia edilmez.

- Tam kaynak düzeltmesinin uygulaması çalışma 02 içinde: 1,7 sn eylem, yeni görünür ilk açık kol pozu ve tamamlanan toparlanma. Önceki çalışma 01 karşılaştırması tarihî yanlış kesit olarak işaretlendi; güncel video 02 kullanılır.

- Ön kol sınıflandırmasının kaynak hatası bulundu: büyük/küçük harfe duyarlı `Arm` araması `ForearmL/R` kemiklerini kapsamıyordu. `name.lower()` ile kol zincirinin tamamı kapsandı. Mevcut GLB/çalışma kollarının düzeldiği iddia edilmez; ağırlıkların yeniden üretilmesi ve gerçek deformasyon kontrolü gerekir. Kullanıcı çalışma 02’yi de reddetti.

## 29 Ekim 2026 — güncel hata kaydı / bu bölüm eski tamamlandı ifadelerinin önündedir

Aşağıdaki kayıt; kullanıcının son bilek, ağız, giysiye taşan dövme, koşu ve kükreme şikâyetlerini kapsar. “Kodlandı”, “otomatik test geçti”, “görsel kabul” ve “telefonda doğrulandı” aynı şey değildir. Bu tur yeni APK yayımlanmadı.

| Hata / yanlış yaklaşım | Düzeltme ve gerçek durum |
|---|---|
| Rastgele üretilmiş gövdeyi sonradan farklı oranlı bir iskelete zorlamak | Yeni üretim onaylı gövdeyle başlıyor. Ice40 adayında kaynak gövde üçgenleri ve skin ağırlıkları dışa aktarımda karşılaştırılıyor. Eski Bilge test geometrisinin bütün kalite sorunları kapanmış sayılmaz. |
| El/önkol ağırlıklarının bel ve kıyafet köşeleriyle karışması; bilekten uzayan üçgenler | Doğrudan native koordinat dışa aktarımı ve geometrinin kendi ağırlık kılavuzu eklendi. Yeni insanın ön görüntüsünde uzun bilek çıkıntısı görülmedi; bütün pozlar için final kabul verilmedi. Yeni gövdede kaynak ağırlıkları korunuyor. |
| Uzun etek/kaftan şeritlerinin dört ayak pozlarında kötü deformasyonu | Yeni kurt şablonunda pantolon ve gövdeye yakın alt giysi zorunlu. Eski oyundaki uzun paneller yeni seri için kabul edilmiyor; yeni pantolonlu aday henüz çalışma zamanı modelinin yerine geçirilmedi. |
| Kırmızı oval ağız içinin yüzün dışında görünmesi | Dış kapalı ağız küresi kaldırıldı; eski test çiftinde içeri alınan ağız boşluğu, yeni temelde kaynak çene/diş geometrisi kullanılıyor. Yeni adayın kükreme yakın planı alındı; yüz/malzeme ayrıntıları hâlâ kalite konusu. |
| Kol dövmesinin bind pozuna göre yerleştirilip gerçekte önde görünmesi | Yerleşim gerçek LSt+UMSt bekleme pozunun arka yüzünde hesaplanıp bind uzayına geri taşınıyor. Ön/arka kontrolü zorunlu. |
| Sırt dövmesinin düşükte kalıp pantolona/kemere taşması | İlk anchor Spine1/pelvis bölgesine fazla yakındı. Yeni anchor Spine2–Neck; kullanıcının ikinci düzeltmesiyle ayrıca 5,5 cm yükseltiliyor. Bel alt sınırı ve giysi malzemesi dışlama eklendi. Her motif aynı yamayı kullanır; eski düşük yerleşim kabul edilmez. |
| Seyrek düz dövme ızgarasının eğri gövdenin içine girmesi | Gövdenin gerçek üçgenlerinden kesilmiş skin yüzeyi kullanılıyor. Native adayda nötr poz yüzey mesafesi yaklaşık 0,85 mm; bütün hareket pozları ayrıca denetlenir. |
| Normal durumda dövmenin fazla parlaması / poz bitince yüksek parlaklığın buff süresince sürmesi | Ortak politika: normal 0,025, kükreme tepe 1,05; poz bitince düşük değere dönülür. Kükremenin 20 saniyelik oyun bonusu değiştirilmez. Dört ailede normal/tepe/toparlanma testi ekleniyor. |
| Yalnız kemik adlarının eşitliğini uyum sanmak | Behamah T_Dash ile Ice40 uzuv oranları farklı bulundu. Türetilmiş uyarlama ayrı kliptir. Ardından Ice40'ın kendi T_WallDash döngüsü bulundu; yeni temel bunu özgün anahtarlarla kullanır. Kaynaklar korunur. |
| “Ice40'ta dört ayak kaynak yok” ifadesinin araştırma ilerleyince yanlış kalması | T_WallDash 533 ms; yeni temel üzerinde tüm döngü inceleniyor. Eski durum belgelerindeki yok ifadesi tarihîdir. Yürüyüş/koşu fizik hızı ile ayak temasından ölçülen tempo ayrı tutulur. |
| Kükreme referansını hareket bitmeden kesmek | Önceki yanlış kesit kayıtta tutuluyor. Tam video ve toparlanma korunmalı. Güncel native klipler ayrıca kendi tam süre/olay bilgileriyle kaydedilir; kısa kesit tam kükreme diye sunulmaz. |
| Efekti salt renk değişimiyle tamamlanmış saymak | ClientFX grupları ve 32 bağımlılık çözüldü; dört farklı grup bağlandı. Buz eşleşmesi kaynak yapılandırmada doğrulandı; diğer aile eşleşmeleri tasarım seçimi olarak açıkça kayıtlı. Başka motorun birebir renderı iddia edilmez. |
| İnce uzun çizgiyi görmeden tek nedene bağlamak | Skin üçgenleri, bind dönüşümü, ağız geometri sınırı ve FX modelleri ayrı denetleniyor. “Süs kemiği bozuyor” tek başına teşhis değildir. Eski sürümdeki çizginin bütün durumlarda kalktığı henüz beyan edilmez. |
| Ateş tuşuna basılıyken aynı parmakla nişan döndürememek | Ateş pointer capture ile sürükleme nişanı döndürüyor; ikinci parmak hareketi, iptal, odak kaybı ve bırakma testleri eklendi. |
| Kamera hazır olmadan stopArena çağrısında hata | Kamera erişimi hazır olma kontrolüne alındı. Başlangıç ve giriş testleri yeniden çalıştırılıyor. |
| İnceleme sahnesinin BLEND dövme malzemesinde depthWrite=false bırakması | Dövme doğru yerdeyken incelemede gövdenin arkasında göründü. İnceleme malzemesi çalışma zamanıyla aynı alphaTest/depthWrite ayarına getirildi. Bu, ürün hatasıyla test sahnesi hatasını ayırmadan karar vermemem gerektiğini gösterdi. |
| Arşiv klasörü adındaki “wolfteam” yüzünden gereksiz LTB adaylarını seçmek | Seçim basename üzerinden daraltıldı; gereksiz staging kopyaları temizlendi. Tam kaynak arşivi korunuyor. |
| Otomatik test başarısını kullanıcı görsel kabulü ve hatasız APK saymak | Bu sürümde yapılmayacak. Son görüntü, kaynak hash'i, test zamanı ve açık işler birlikte kaydedilir. Fiziksel Android testi yapılmadan FPS/çökmez/kurulum garantisi verilmez. |

Son testlerde geniş envanter testi karakter kartına tıklarken zaman aşımına uğradı. Önceki PASS logları bu yeni çalışmanın sonucu diye kullanılmayacak; tek başına tekrar ve hata incelemesi sürüyor. Güncel kanıtlar `docs/full-archive-review/` ve `docs/ice40-production/` altında.

### Son dövme düzeltmesinin kontrol sonucu

- Kullanıcının ikinci yükseltme isteği ortak politikaya +5,5 cm olarak eklendi. Eski Bilge'nin yüksek korse üst sınırı ayrıca 1,55 m: salt pelvis yüksekliği bu modelde yeterli değildi. Bu geometri profili kaydedildi; yeni pantolonlu kaynak gövdeyle karıştırılmaz.
- Bütün dört çalışma zamanı modelinin üç dövme yüzeyi ortak araçtan geçirildi. Gövde verisi, skin/inverse-bind ve animasyon nesneleri değişmedi. 36 motif/model birleşimi gerçek WebGL testinde geçti; sırf motif değiştirmek geometriyi değiştirmiyor.
- Dört ailede test anındaki normal parlama 0,025; kükreme örnekleri yaklaşık 0,73–0,96 aralığında. Eğrinin tepe tanımı 1,05. Toparlanma sonunda 0,025'e dönüş test edildi; aktif 20 saniye bonus dövmeyi yüksek parlaklıkta kilitlemiyor.
- Envanter testi tek başına tekrarda PASS oldu. İlk kart tıklama zaman aşımının kalıcı bir ürün hatası olduğu yeniden üretilemedi; önceki log bunun yerine kullanılmadı.
- İnceleme aracı önce bütün isteğe bağlı aksesuarları aynı anda gösterdi. Bu görüntü gerçek kuşanma durumu değildi. İnceleme `default_visible` ve aksesuar görünürlüğünü gerçek kullanım gibi uygulayacak şekilde düzeltildi. Ürünle aynı görünürlük/derinlik ayarları olmadan görsel kabul verilmez.
- Yeni üreticide ortak dövme işlevinin import takma adı yanlış çağrıldığı için bir yerel üretim durdu. İşlev adı düzeltildi; kaynak bütünlük/inceleme zinciri yeniden çalıştırılıyor. Bu başarısız çalışma tamamlandı diye kaydedilmedi.
- Tek yönden ışınla bakıldığında bir dövme köşesinin başka gövde üçgeni tarafından örtülmesi, kendi derisinin içine girdiğinin kanıtı değildir. Yerel yüzey mesafesi ve görüş yönündeki doğal örtülme ayrı tanı verileridir. Önceki görünmezlik teşhisinin bir kısmı inceleme sahnesinin depthWrite ayarındandı; geometriyi değiştirerek bunu gizlemek doğru değildi. Eski seyrek yüzeyin yerine gerçek gövde üçgenleri kullanılması ayrıca yüzeye uyum önlemidir.

Yeni ücretli üretim yapılmadı. Yeni pantolonlu gövdenin tam oyun içi değişimi, uzun eski giysi panellerinin tamamen emekliye ayrılması, bütün yüz/malzeme ayrıntıları ve fiziksel Android kabulü hâlâ ayrı açık işlerdir. Bu testler hatasız APK veya seri üretilmiş yeni karakterler teslim edildiği anlamına gelmez.

## Kullanıcının son görsel reddi — seri üretim ve yayın durduruldu

Kullanıcı dizlerin iki yanındaki sivri/uzayan üçgenleri, kükremede boğazın uzun bir şerit gibi görünmesini ve genel model kalitesini reddetti. Hazır kaynak modelinin kendi ağırlıklarını korumak iyi görsel sonucu garanti etmedi. Sayısal iskelet testleri geçmesine rağmen bu modeli çalışma zamanına geçirmek erkendi; görsel kalite kapısını ben kaçırdım.

- Dizlerde kaynak dizlik/kürk geometrisinin üzerine düz bir yükseklik eşiğiyle pantolon boyamak sivri koyu kenarlar oluşturdu. Odaklı denemede kumaş sınırı dizliğin üstüne çekiliyor; bunun görsel kabulü henüz verilmedi.
- Boğaz/üst göğüs ağırlıkları ve uzayan kürk görünümü ayrıca ele alınıyor. Kemik uzunlukları sabit olduğu için “kemik uzamıyor, sorun yok” sonucuna varmak yanlıştı. Yerel boyun/üst göğüs ağırlığı düzeltmesi deneme aşamasında; kaynak ağırlıklarıyla artık birebir eşitmiş gibi kaydedilmiyor. Kaynak dosya ve önceki aday saklandı.
- Son gerçek geçiş testi hareketten beklemeye dönüşte yaklaşık 19 cm zemin ihlali buldu. Diğer altı geçişin geçmesi bu hatayı kapatmaz. Açık sürüm engelidir.
- Testleri uzun ve geniş döngüler halinde tekrarlamak iki saatlik süreci gereksiz uzattı. Yeni sıra: yalnız sorunlu üç pozun hızlı görsel karşılaştırması → kabul edilen değişikliğin ilgili hareket testi → en sonda tek geniş regresyon. Görsel hata açıkken bütün test paketleri tekrar çalıştırılmayacak.
- Yeni APK ve seri varyant üretimi bu reddedilen adayla yapılmayacak. `production.json` ve gövde sözleşmesi yayın/seri üretime kapalıdır.

### Hızlı üç poz denemesinin sonucu

Üç gerçek pozla yapılan odaklı denemede dizdeki koyu sivri kumaş sınırı kaldırıldı; giysi sınırı kaynak dizlik formunun üstüne taşındı. Buna karşılık 80 boyun/üst göğüs köşesini yeniden ağırlıklandırma denemesi boyun görünümünü yeterince düzeltmedi. Bu deneme reddedildi ve çalışma BLEND dosyasında kaynak ağırlıklarına geri dönüldü. Yeni ağırlıklar oyuna aktarılmadı. Deneysel GLB yalnız reddedilmiş karşılaştırma çıktısıdır. Boyun/üst göğüs topolojisi ve kaplama kalitesi çözülmüş sayılmaz. Aynı başarısız adayın geniş testlerini tekrar çalıştırmak durduruldu.

## 29 Ekim — yeni ücretli kurt üretimi, eski kaplama yönteminin reddi

Kullanıcı yeni ücretli üretimi açıkça istedi. Tek kurt için 4K geometri + 8K PBR + mobil remesh tahmini 45 kredi; başlangıç bakiyesi 905. Geometri görevi `01a1878d-a5b3-72ac-9098-ccc4a0306a66` başarılı, gerçekleşen 25 kredi. Kaplama görevi `01a18814-08b2-747b-b5ba-1ce9d5c2c6b5` sürüyor. Tekrar gönderim yapılmadı; önceki kabul yerel işlem günlüğünden kurtarıldı.

Önceki Power42 adayında en yakın UV ile eski modelden renk aktarmak kürke giysi/metal desenleri yaydı. Bu yöntem reddedildi; aday oyuna kurulmadı ve tamamlanmış model değildir. Ice40 diz üçgenleri ve uzun boğaz sorunu da kapanmış sayılmaz. Yeni model doğal kürk, ayrı kumaş pantolon ve küçük buz bileklikleriyle üretiliyor. Kaynak animasyonların korunması ve yeni geometri uyumu henüz doğrulanmadı. Kuyruk, ağız/çene ve eklem uyumu özellikle kontrol edilecek. Kalitesiz gövdeyi yeniden zorla uydurup bitmiş sayma yöntemi tekrarlanmayacak. Test kapsamı kısa hareket, bir kükreme/efekt ve tek örnek dövme; bütün motifleri yeniden tarama yok.

### Premium üretim sonucu: başarısız görsel kabul

Üç yeni Meshy görevi başarılı; toplam gerçek maliyet 45 kredi. Yüksek model 1.369.346, oyun adayı 15.586 üçgen. Ancak gerçek ön/yan/arka renderlar gövde kürkünün kumaş gibi, yelenin sivri levhalı kaldığını ve desteksiz kuyruk üretildiğini gösterdi. Ücret harcanmış olması kabul nedeni yapılmadı. Aday oyuna kurulmadı, rig/animasyon/efekt/dövme tamamlandı denmedi. İkinci ücretli tekrar yok. Ayrıntı `docs/premium-wolf-01/README-TR.md`.

## v0.1.17 — seçili gövdeye dönüş ve çalışan zincir

Yeni görselden üretim/remesh 35 krediyle tamamlandı. Üretilen geometriyi Power42 çenesine zorlayan baş/çene denemeleri bozuldu; tahmini ağız kesimi de yanlıştı. Bu adaylar oyuna alınmadı. Kaynak Power42 gövde, gerçek çene/dişler ve 72 kaynak klip korunarak özgün kürk/pantolon görünüşü Cycles ile aktarıldı. Yanlış UV adaları arasındaki renk karışımı giysi desenlerini kürke taşıyordu; bu yöntem kaldırıldı. Sürekli referans kürkü ve yeni giysinin yumuşak kasık ağırlıkları kullanıldı. 42 kemik, yaklaşık 14,2 bin üçgen. Yerel dört poz, gerçek koşu/takla/kükreme ve yedi geçiş kontrolü geçti. Telefon/görsel kullanıcı kabulü henüz yok. Diğer üç yeni özgün kurt tamamlanmış sayılmaz. Ayrıntı `docs/premium-wolf-01/TESLIM-TR.md`. Tek imzalı APK için CI aşamasına geçiliyor.
