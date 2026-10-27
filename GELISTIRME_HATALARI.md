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
