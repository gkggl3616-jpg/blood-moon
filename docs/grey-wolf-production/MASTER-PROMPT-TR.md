# Rogue: Blood Moon — referansa sadık yeni kurt ve animasyon üretim talimatı

## 1. Yetkili görsel yön ve kapsam

Bu işin hedefi, kullanıcının son gönderdiği koyu gri Wolfteam kurt görselini esas alan, güçlü anatomili ve animasyona uygun gerçek bir 3B oyun karakteridir. Onaylanan kimlik görseli: `art/characters/reference/grey-wolf-faithful-large.png`. Son el/ayak duruşu düzeltmesi: `art/characters/grey-wolf-production/fullbody-natural-pose.png`.

Açık renk, pürüzsüz, oyuncak veya insan mankenine benzeyen son yerel prototip kullanıcı tarafından reddedildi. Onun kafa, yüz, kostüm ve silüetini yeni karakterin temeli yapma. Referansı yalnız renk paleti olarak yorumlama. Referansın karakter oranları, yüzü, silüeti, kürkü, kıyafetleri ve el biçimi birlikte hedef alınacak.

İlk üretim yalnız **bir kurt** içindir. Bilge Kağan insanı, diğer insan/kurt çiftleri ve yeni ücretli varyantlar bu tek model işiyle tamamlandı sayılmaz. Son kurt referansında bulunmayan buz zırhı, lacivert kaftan, taç, yeni dövme veya büyülü uzuv ekleme. Oyundaki kuşanılabilir dövme ve element efektleri ayrı sistem olarak korunacak; temel bedenin yüzeyine kalıcı olarak çizilmeyecek.

## 2. Modelin görsel kimliği

### Silüet ve anatomi

- İki ayak üzerinde savaşabilen, koşuda dört uzvunu da kullanabilen kaslı kurt-insan anatomisi kur.
- Göğüs ve üst sırt geniş; omuzlar güçlü ve yuvarlak hacimli; bel belirgin biçimde dar olsun. Gövde bir kutu, ters üçgen levha veya şişirilmiş küre gibi görünmesin.
- Pektoral, deltoid, trapez, latissimus, karın ve oblik kasların yönleri kürkün altında okunabilsin. Kasları birbirinden ayrılan zırh plakaları gibi modelleme.
- Baş, boyun ve omuzların sınırları önden, yandan ve arkadan ayrı seçilsin. Boynu saklayan dev bir yele yapma.
- Üst kol ve ön kol dolgun; ön kollar referanstaki gibi iri ve uzun; bilek geçişi güçlü fakat hareket edebilir olsun. Dirsekleri yanlara fırlayan sürekli bir kanat duruşu oluşturma.
- Elleri referanstaki gibi büyük ve tehditkâr tasarla. Parmak boğumları, avuç, karşılayan başparmak ve fildişi pençeler okunabilsin. Parmaklar birbirine kaynamasın, birbirini kesmesin veya ince çubuklara dönüşmesin. Oyun bekleme duruşunda eller tam açık ve parmaklar yelpaze gibi ayrık olmasın: ağır eller hafif çukur, yarı kapalı ve doğal kıvrımlı dursun. Başparmak kıvrık işaret parmağına karşı gelsin; yüzük ve küçük parmak biraz daha bükülü, bilek ön kolun doğal devamı olsun.
- Uyluk ve baldırlar güçlü; diz ve ayak bileği yönleri tutarlı olsun. Tam boy kaynakta görünmeyen alt bacaklar aynı anatomik dili sürdürsün: kamuflaj pantolondan çıkan koyu kürklü alt bacaklar ve geniş pençeli kurt ayakları. Bu bölümün ilk görselde ölçülmediğini kaydet.
- Başlangıç çalışma ölçeği yaklaşık 2,4 metre olsun; bu yerel sanat/oyun ayarıdır, referanstan ölçülmüş boy değildir. Daha büyük önizleme isteğini yalnız dünya ölçeğini artırıp kamerayı kırparak çözme; karakter ekranda büyük ve tam görünmeli.

### Kurt yüzü

- Uzunluğu ve genişliği referansa uyan sivri kurt burnu; siyah burun ucu; güçlü üst çene, gerçek alt çene ve net yanak yapısı kullan.
- Göz çukurları derin, gözler dar ve buz mavisi; kaş çıkıntısı sert ve saldırgan olsun. Büyük yuvarlak oyuncak gözler veya yüzeyden çıkan siyah gözlük benzeri parçalar yapma.
- Yanaklarda gri-beyaz kürk, küçük açık renk çene tutamı; kısa, arkaya taranan koyu baş kürkü; iki sivri ve ölçülü kurt kulağı olsun.
- Tehditkâr ifade korunsun. Kükreme ağız animasyonunda alt çene menteşesi doğru yerde açılsın; alt dişler alt çeneyi izlesin. Üst dişler başa bağlı kalsın.
- Ağız içinde gerçek karanlık boşluk, damak ve dil hacmi olsun. Ağız açıldığında başın içinden arka plan görülmesin. Dişler açık veya kapalı pozda birbirine girmesin.
- Otomatik yüz rig'i yoksa varmış gibi sunma; geometri ve çene hareketini ayrı doğrula.

### Kürk ve yüzeyler

- Ana kürk koyu antrasit/gri, kas yönlerini izleyen daha açık gri geçişlerle işlenmeli. Göğüs ve karın daha açık; ön kollar daha koyu; eller ve çene çevresi daha açık gri olsun.
- Yoğun ama kısa yönlü kürk etkisi kullan. Yüz ve omuz çevresinde kontrollü küçük kümeler olabilir; rastgele uzun sivri kartlar, kâğıt saçaklar ve metal kırığı gibi parlayan kürk kullanma.
- Küçük tüy ayrıntıları renk/normal/pürüzlülük dokularında çözülsün. Her tüyü geometri olarak ekleme. Ana silüeti değiştiren az sayıda kontrollü küme geometri olabilir.
- Kürk mat, deri orta pürüzlü, metal tokalar kontrollü yansımalı olsun. Bütün malzemeler aynı plastik yüzey gibi görünmesin.

### Kıyafet

- Referanstaki yeşil/kahverengi kamuflaj pantolon, koyu taktik kemer ve uyluk kayışlı siyah kılıf düzenini koru.
- Görüntünün sağındaki ön kolda kahverengi deri sarım bulunsun. Bu parçayı yanlışlıkla karşı kola taşıma; dosyada hangi anatomik kola karşılık geldiğini açıkça işaretle.
- Pantolon ve kayışlarda ölçülü dikiş, kat ve aşınma ayrıntıları olsun. Kumaş cilde kaynamasın; hareket esnasında kalça, diz ve kasık kıvrımları düzgün çalışsın.
- Referansta bulunmayan dev omuzluk, buz kılıfı, pelerin, kraliyet süsü veya yeni silah ekleme.

## 3. Animasyona uygun modelleme ve topoloji

Önce teknik nötr A duruşunda oranları, eklemleri ve silüeti kur. Bu teknik iskelet pozu, oyun beklemesinde parmakları tamamen açma veya bacakları robot gibi kilitleme talimatı değildir. Görsel hedef doğal yarı kapalı eller ve yere ağırlık veren organik duruştur. Omuzdan dirseğe kadar yüzeyi tesadüfî üçgenlerle doldurma; bükülme çevresinde düzenli yüzey halkaları kullan.

- Ana deri yüzeyi bağlı, temiz ve yönleri tutarlı olsun. Omuz–kol bağlantısı birbiri içine sokulmuş kopuk küre ve silindirlerden ibaret olmasın.
- Omuzun kol kaldırma ve öne uzanma hareketleri için deltoid, koltuk altı, köprücük ve kürek kemiği çevresinde yeterli yüzey akışı bulunmalı.
- Dirsek, bilek, kalça, diz ve ayak bileğinde bükülme halkaları kur. Eklemin tam orta çizgisine bütün ağırlığı yığma.
- Parmakların en az iki bükülme bölgesi ve başparmağın ayrı hareketi olsun. Pençe uçları distal kemiğe doğru bağlı kalsın.
- Gereksiz iç yüzeyleri, sıfır alanlı yüzleri, üst üste çift yüzleri ve gevşek köşeleri temizle. Deri üzerinde açık yarık veya ters normal bırakma.
- Göz, diş, alt çene, giysi ve kayışlar gerektiği yerde ayrı kapalı parçalar olabilir. Bunları ana gövdenin kopuk topolojisiyle karıştırma.
- Dört uzuv üzerinde yere basarken omuz hacmi çökmemeli; kollar tüy/deri şeritlerine dönüşmemeli. Kükremede başın üstüne çıkan eller gövdeyi sürüklememeli.

## 4. İskelet ve ağırlıklar

Kök, pelvis, bel, göğüs, boyun ve baş için ayrı kontrol; iki omuz/köprücük; üst kol, ön kol, el; ayrı parmaklar ve başparmak; uyluk, baldır, ayak ve gerekli parmak/pençe uçları kur. Çeneyi gerçek menteşe etrafında ayrı kontrol et.

- Dinlenme pozu referansın tehditkâr hissini taşısın; üretim A pozu ve oyun bekleme pozu ayrı tutulabilir.
- Kol uzunlukları dört ayak koşusuna ve yukarı kaldırılan kükreme pozuna yetecek şekilde modelleme sırasında değerlendirilsin. Hedefe yetiştirmek için kemik uzatma açılmasın.
- IK/FK kontrolleri düzenlenebilir olsun. Destek ayaklarını sabitlemek ve bilek yönünü kontrol etmek mümkün olsun.
- Oyun köşesi başına en fazla dört normalize kemik etkisi hedefle. Ağırlıksız köşe, karşı kola bağlı deri ve kola bağlı pantolon bırakma.
- Ağırlık geçişleri keskin coğrafi sınırlarla komşu köşeleri farklı organlara ayırmasın. Kürk kümeleri ve giysi yüzeyleri kendi anatomik bölgesini izlesin.
- Blender'ın yalnız kendi görüntüleyicisinde çalışan B-Bone veya preserve-volume görünümüne güvenme. GLB'de kullanılan sıradan kemikler, ağırlıklar ve klipler yeniden yüklenerek kontrol edilsin.
- Gerekirse eklem destek/twist kemikleri kullan; yüksek bükülmede hacim korunmasını gerçekten incele. Destek kemiği eklenmiş olmasını düzgün deformasyon kanıtı sayma.

## 5. Hareketlerin üretim tarifi

### Bekleme

Ayaklar dengeli, dizler hafif esnek, eller ağır, dirsekler hafif bükülü. İki ayak robot gibi kusursuz paralel ve özdeş konumda olmasın: birkaç derece dışa yönelim, bir ayakta küçük ilerilik ve hafif 55/45 ağırlık dağılımı olabilir. Ayak parmakları da mekanik bir yelpaze gibi açılmasın; pençeli kurt ayağı korunurken yük taşıması doğal olsun. Gövde hafif öne hazır; baş tek başına düşürülmüş kambur görünüm yok. Nefes küçük ve kontrollü; ayak kayması veya sürekli havada kalan bacak yok.

### Kükreme

Ana zaman referansı kullanıcının tam `Screenrecorder-2026-10-28-08-04-29-656.mp4` dosyasıdır: 38 gerçek görüntü, 1,671792 sn konteyner, son görüntü 1,522 sn. Eski erken kesilmiş parça kullanılmayacak.

Açılma, yükseliş, ellerin tepeye varması, kısa tutuş, kolların indirilmesi ve baş/gövde toparlanması ayrı aşamalar olsun. Referans zaten hareket başlamışken açıldığı için beklemeden ilk poza giriş ayrıca doğal biçimde yazılsın; bu girişin videodan ölçüldüğü iddia edilmesin. Bütün toparlanma korunmalı; döngü sıfırlaması hareketi erken bitirmemeli.

Omuzlar, göğüs, boyun ve baş birlikte çalışsın. Parmaklar tepeye varırken açılsın. Alt çene ve ağız içi gerçekten hareket etsin. İleri tuşu basılı olsa bile kükreme pozu süresince yatay hareket durmalı.

### Dört ayak koşusu

İlk yerel hız ayarı yaklaşık 8 m/sn; bu referans oyundan ölçülmüş kesin hız değildir. Bütün kurtlar aynı ana hareket şablonu ve tempoyu kullanmalı; gövde oranları uygun şekilde uyarlanmalı.

Ön destek, emilim, arka uzuvların toplanması, arka itiş, havada toparlanma ve yeni temas fazlarını kur. Gerçek ilerleme hızı, adım açıklığı ve yere basma süresi birlikte eşleşsin. Sadece klibi hızlandırma. Destekte dünya üzerindeki ayak kaymasını mesafe/zamanla ölç. Baş aşırı sallanmasın; bacaklar makas gibi birbirinden geçmesin; eklemler uzayıp kısalmasın.

### Takla, sıçrama ve pençe

Takla yaklaşık 2 metrelik kısa oynanış ilerlemesini korusun; ileri hareket iki kez eklenmesin. Gövde, kollar ve bacaklar taklada toplanabilsin; baş veya omuz zemine gömülmesin. Takla teması hasar versin; aynı hedef aynı taklada bir kez vurulsun ve siper arkasına hasar geçmesin.

Koşudan sıçrama, koşudan takla ve havada taklaya geçiş çalışsın. İnişte basılı yönde doğal harekete dönülsün. Sıçramada yatay hız iki kez toplanmasın. Pençe saldırısında omuz–gövde dönüşü ve gerçek el yolu uyumlu olsun; vuruş izi eli izlesin.

## 6. Efekt ve dövme uyumu

Mor el alevi, karakter paletine göre renklendirilebilen ortak efekt yapısı; tepe anında ölçülü patlama; kuşanılan dövmede kontrollü parlama; kısa ömürlü pençe izi kullan. Efekt kemiğe bağlı, küçük ve sınırlı havuzlu olsun. Modeli ışık topuyla kapatma.

Efektler kapalıyken de eklem ve silüet kontrolü yapılmalı. Dövme desenleri deriyi izlesin; havada kart, kalın kabartma veya titreyen çift yüzey gibi durmasın. Üç dövme yuvası ayrı; bonus hesabı karakter pasifinden bağımsız mevcut güncel kurala bağlı kalsın. Yeni karakterin temel görünüşünü üretmek bu sistemi yeniden yazma veya kayıtları silme gerekçesi değildir.

## 7. Mobil varlık bütçesi

Başlangıç hedefi kurt için toplam yaklaşık 15.000 üçgen; ana gövde, baş, eller, dişler, kıyafet ve aksesuarları birlikte say. İnsan modeli ileride ayrıca yaklaşık 12.000 üçgen bütçede ele alınacak. Yüksek ayrıntılı kaynak çalışma modeli gerekiyorsa ayrıntıları oyun topolojisine ve dokulara aktar; milyonlarca yüzü APK'ya koyma.

Renk, normal ve pürüzlülük dokuları hazırlanmalı; gerektiği yerde metalik kanal kullanılmalı. Oyun için başlangıç 2K doku atlası; gerekirse kaynakta 4K, cihaz ölçümüne göre 1K/2K teslim seçeneği. UV yoğunluğu yüzde ve ellerde yeterli; görünür dikiş, ters normal, aşırı parlama ve saydam kürk hatası olmamalı. LOD gerekiyorsa aynı modelden türetilsin; ayrı ücretli karakter tekrar üretimi sayılmasın.

Net görüntü varsayılanı, ayarlanabilir bakış hassasiyeti, yumuşak gerçek gölge, yön düğmeleri, ileriye çift basarak koşu ve yuvarlak simgeli aksiyon tuşları korunsun. Telefon üzerinde ölçüm yapılmadan sabit FPS veya çökmezlik garantisi verme.

## 8. Üretim sırası ve kabul kapıları

1. Son onaylı görsele sadık tam boy A-pozu referansı hazırla. Mevcut görsel üst bacakta kesiliyor; eksik ayak/alt bacak ayrıntısını görünür biçimde tamamla. Farklı karakterlere ait tutarsız ön/yan/arka görselleri aynı modelin ölçüsü gibi kullanma.
2. Tek bir model için gerçek üretim seçeneği, maliyet kaynağı ve kapsamı kaydet. Eski ücretli üretim bütçesi yeni deneme izni değildir. Onaylanmayan ek ücret veya başarısız sonuç üzerine otomatik ücretli tekrar yapma.
3. Önce nötr, efektsiz ön/yan/arka/üç çeyrek görünüşte yüz, oran ve silüeti karşılaştır. Temel benzerlik yoksa ışık ve efektle tamamlandı deme.
4. Oyun topolojisi/UV/PBR ve iskelet hazırlığını yap; omuz kaldırma, 120° dirsek, bilek yönleri, çömelme ve çene açılmasını test et.
5. Tam kükreme, koşu, takla, sıçrama ve pençe kliplerini üret. Tüm döngüleri örnekle; yalnız iyi bir kare seçme.
6. Gerçek GLB'yi oyunun Three.js görüntüleyicisinde yeniden aç. Blender ve GLB arasındaki konum/deformasyon farkını ölç. Menü ve arena aynı gerçek varlığı kullansın.
7. Koşu hızını mesafe/zamanla; yere basmayı dünya konumuyla; taklanın ilerlemesini, temas hasarını ve kükremede durmayı gerçek oynanışta doğrula.
8. Görsel kabulü, teknik test geçişinden ayrı raporla. Yapılan/test edilen/açık işleri MD dosyalarına yaz. Konsept görselini rigli oyun modeli yerine teslim etme.
9. Entegrasyon bittiğinde mevcut kayıtları, sahipliği ve kredileri koru. Son APK ayrıca önceki imza/sürüm uyumuyla kontrol edilecek; bütün varlıkları içeren tek, imzalı kurulabilir APK gerekir. Bu prompt hazırlanmış olması APK'nın hazır olduğu anlamına gelmez.

## 9. Kesin ret nedenleri

Referanstan uzak oyuncak yüz; yuvarlak gözler; kısa/şişkin burun; aşırı iri yele; kâğıt gibi sivri levha kürk; kopuk kürelerden oluşan deri; yana taşan dirsekler; eriyen koltuk altı; esneyen kemikler; avuçtan ayrılan parmaklar; kumaşı sürükleyen kol ağırlıkları; sahte ağız açıklığı; zeminden kopan destek ayakları; kayarak ilerleme; uzun ileri fırlatan takla; hareketi erken kesen döngü; efektsiz bakıldığında bozulan gövde; yalnız renk değiştirip yeni model tamamlandı deme; 2B renderı gerçek 3B teslim gibi sunma.

## 10. Güncel ek kapsam — insan formu, doğal yürüyüş ve dönüşümlü pençe

### Aynı karakterin insan formu

Bu kurtla eşleşen bir insan formu da gereklidir. Görsel tasarım referansı `art/characters/grey-wolf-production/human-counterpart-reference.png`; bu 2B referans, tamamlanmış 3B insan modeli değildir. Yetişkin, güçlü ve gerçekçi oranlı bir erkek savaşçı; koyu kısa saç, ölçülü gri şakak, köşeli yüz ve kısa sakal; normal gri/mavi gözler. Koyu antrasit taktik gömlek, aynı kamuflaj pantolon, aynı kemer, aynı uyluk kılıfı ve görüntünün sağındaki aynı deri kol bağı iki formun kimliğini bağlasın. İnsan elleri beş parmaklı, normal insan anatomisinde; ayaklarda işlevsel botlar olsun. Kurt tırnağı, parlayan göz veya yeni kraliyet kostümü ekleme.

İnsan ve kurt ayrı doğru oranlı mesh/iskelet varlıklarıdır. İnsanı kurdun derisini renklendirerek üretme. İnsan için toplam yaklaşık 12.000, kurt için yaklaşık 15.000 üçgen hedefi geçerlidir. İki forma da aynı fiziksel boy veya aynı omuz genişliğini zorla uygulama; poz aktarımında oran uyarlaması yap. İnsan birinci şahıs görünümü, dönüşüm ve envanterdeki tam beden önizleme aynı donanım verilerini paylaşmalı. İnsan formunun ayrı ücretli 3B üretimi bu yeni isteğin gereğidir; önceki tek kurt üretim onayına otomatik eklenmiş sayılmaz.

### Yürüyüş — yalnız koşuyu yavaşlatma

İnsan ve kurt için ayrı doğal iki ayak yürüyüşü üret. Kurdun dört ayak koşusu bundan ayrı kliptir. Yeni kaynakta `HumanWalk` ve `WolfWalk` adları kullanılabilir; eski `HumanMove` / `WolfMove` adları için açık uyumluluk eşlemesi yap. Yürüyüşü dört ayak koşu klibinin hızını düşürerek oluşturma.

1. Sol topuk/ayak tabanı temas → ağırlığı kabul → tek ayak üzerinde taşıma → diğer bacağın geçişi → itiş → karşı ayak temas fazlarını kur. İki taraf arasında doğal ama kontrollü küçük farklar olabilir.
2. Kalça taşıyan ayağa doğru hafifçe yer değiştirsin. Pelviste küçük dönme ve yana eğilme; göğüste buna karşı hafif dönüş bulunsun. Gövde tek parça yana sallanan direk gibi olmasın.
3. Baş ve bakış hedefi gövde hareketini yumuşakça dengelesin. Omuz ve baş her adımda aynı açıyla mekanik biçimde dönmesin. Büyük kafa sallanması veya mide bulandıran kamera hareketi yok.
4. Başlangıç sanat ayarı olarak pelvis yana hareketi yaklaşık 1–2 cm, dikey hareket 1–3 cm; pelvis dönüşü 2–4°, göğüs karşı dönüşü 1–3°, serbest kol salınımı 8–15° denenebilir. Bunlar ölçülmüş referans değerleri veya sabit zorunlu sınırlar değildir; model boyuna ve görüntüye göre ayarlanır.
5. Sağ bacak öne giderken sol kol, sol bacak öne giderken sağ kol doğal karşı salınım yapsın. Dirsek ve bilekte küçük gecikme olsun; el parmakları gevşek yarı kıvrık kalsın. İnsan silahı iki eliyle tutuyorsa serbest kol salınımını silahın üzerine zorla bindirme; üst beden nişan katmanı ile alt beden yürüyüşünü ayır.
6. Destek tabanı dünya üzerinde kaymasın; sallanan ayak yeterince yerden ayrılsın. Diz yönü ayakla uyumlu olsun; dizler birbirinin içinden geçmesin, bacak boyları değişmesin.
7. Gerçek ilerleme hızı, adım boyu ve klip süresi birlikte ayarlansın: tam döngü mesafesi / döngü süresi = referans oynanış hızı. Karakter boyu farklıysa mesafeyi ve süreyi açıkça yeniden değerlendir. İleri yürüyüş yanında geri ve yan hareketlerin gereksinimi de kaydedilsin; ileri yürüyüşü yanlış yönde kaydırarak tamamlandı deme.
8. Bekleme→ilk adım, yürüme→durma, yön değiştirme ve yürüme→koşu geçişleri ayağın o anki destek fazını korusun. Tek karelik poz sıçraması veya ani kamera zıplaması olmasın.
9. İnsan birinci şahısta silah/ellerde hafif, adımla uyumlu sallanma olabilir. Kamera etkisi küçük ve ayarlanabilir olsun; nişangâhı büyük dairelerde gezdirme. Mobil bakış yönü ve hassasiyet düzeltmeleri korunur.
10. Yürüyüş kliplerini tam döngüde ön, yan ve arka açılardan izle. Başlangıç/son dikişi, destek ayağının dünya konum hatası, topuk/ayak ucu yerden açıklığı ve gerçek mesafe/zaman ayrı ölçülsün.

### Pençe — her vuruşta yalnız bir saldıran kol

Başlangıç sırası sağ → sol → sağ → sol olsun. Her kabul edilmiş saldırı bir sonraki kolu belirlesin. Bekleme süresinde, kükremede, dönüşümde veya geçersiz durumda reddedilen düğme basışı sırayı ilerletmesin. Yeni doğuşta veya karakter değişiminde başlangıç sağ kola dönebilir; bu davranış açıkça tanımlansın.

`WolfClawRight` ve `WolfClawLeft` ayrı kliplerdir. Saldıran kol hazırlık, hızlanma, temas ve toparlanma yayını tamamlar. Diğer kol büyük bir saldırı savurmaz; denge/koruma pozunda kalır, gövde aktarımından küçük doğal hareket alabilir. Omuz, kürek kemiği, göğüs ve pelvis vuruşla uyumlu dönsün. Animasyon sırf bütün karakteri aynalayarak üretilmesin; deri sarımı ve kılıf karşı kola taşınmasın.

İlk zamanlama denemesi olarak yaklaşık 0,65 sn vuruş içinde 0–0,12 hazırlık, 0,12–0,30 hızlanma/temas ve kalan bölüm toparlanma kullanılabilir. Bunlar yerel başlangıç ayarıdır. Temas penceresi son klibin el yoluna göre düzenlenir. Hasar bir saldırı kimliği için tek kez uygulanır; her karede veya her pençe parçasında tekrar tekrar sayılmaz. Mevcut siper görüş/temas kontrolü korunur. Sağ/sol için sırf animasyon değişti diye farklı hasar veya erişim uydurma.

Pençe izi saldıran elin tarafını ve gerçek el yolunu izlemeli; sol vuruşta sağ kolun önünde görünmemeli. Hazırlıkta erken iz başlatma; toparlanma sonunda iz kısa sürede sönsün. Alev/dövme katmanı vuruşun iskeletini ve temas anını örtmesin.

Testler: art arda dört vuruş sağ/sol/sağ/sol; bekleme süresindeki ek basışın sırayı etkilememesi; basılı tuş ile aynı sıra; tek vuruş/tek hasar; siper arkasına hasar geçmemesi; vuruş sırasında yalnız etkin kolun saldırı yayı; doğru tarafta iz; karakter değişiminde sıfırlama; yeni rigde kemik adlarının eşlenmesi. Eski iki kollu klibi maskelemek bir uyumluluk çözümüdür; yeni karakterin özel sol/sağ animasyonlarının tamamlandığı anlamına gelmez.
