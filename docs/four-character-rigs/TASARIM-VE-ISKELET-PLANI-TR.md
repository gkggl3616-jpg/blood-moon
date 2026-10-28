# Dört karakter / dört kurt iskeleti

28 Ekim 2026. Kullanıcının son kararı: dört farklı iskelete göre karakter tasarlanacak; **şu aşamada animasyonlara kesinlikle dokunulmayacak**. Önceki ortak koşu/takla veya yeni hareket üretme talepleri bu turda uygulanmaz. Ücretli üretim başlatılmadı.

## Kesin seçim

| Karakter | Kaynak kurt | Düğüm/kemik | Kaynak üçgeni* | Ayırt edici yapı | Tasarım yönü |
|---|---|---:|---:|---|---|
| Bilge Kağan | `wt_wolf_ice_r.ltb` | 40 | 5.790 | Ice gövdesi, farklı önkol ve boyun oranı | Buz komutanı; lacivert, mat altın, kırık beyaz |
| Kül Tigin | `r1_wolf.ltb` | 54 | 6.192 | `L_Twist`, `R_Twist`, önkol burulma ve ek boyun kemikleri | Kan savaşçısı; kömür siyahı, kızıl, koyu çelik |
| Alp Arslan | `wt_wolf_power_r.ltb` | 42 | 4.776 | Power omuz/gövde yapısı, klasik 42 düğümlü zincir | Köz muhafızı; sıcak gri, deri, bronz |
| Konuralp | `wt_wolf_wraith.ltb` | 58 | 5.097 | İki önkol burulma kemiği ve altı parçalı kuyruk zinciri | Gölge avcısı; antrasit, koyu mor, soluk gümüş |

* Kaynak LOD0, varsa kuşanılmamış dövme yüzeyleri dahil. Bunlar bitmiş yeni tasarımın poligon sayıları değildir.

Dört iskeletin ad/parent hiyerarşisi imzaları birbirinden farklı. Seçim yalnız kemik sayısını değiştirerek yapılmadı. Yeni özel karakter modelleri henüz tamamlanmış değil; seçilen kaynak gövdeler tasarımın hareket sınırlarını belirleyen tabanlar.

## Animasyon kilidi

- Kaynak LTB ve hareket dosyaları değişmeden tutulur; altı benzersiz dosyanın SHA-256 değerleri `selection.json` içinde.
- Yeni keyframe, klip kesme/uzatma, hız değiştirme, yeniden rigleme, retarget veya başka karakterin hareketini aktarma yapılmaz.
- Kemik isimleri, parent yapısı, bind matrisleri ve kemik oranları değiştirilmez.
- Modelin mevcut pozlarına göre gövde/kostüm tasarlanır; eklem merkezleri ve bükülme boşlukları korunur.
- Kaynak gövdenin mevcut ağırlıkları başlangıç referansıdır; yeni kostüm parçaları mevcut kemiklere bağlanabilir, bu işlem yeni hareket üretme izni değildir.
- Tasarım önizlemeleri statik bind pozlarıdır. Koşu/kükreme/takla oynatımı bu turda yapılmaz. Orijinal hareketler kaynak dosyada durur; görsel çalışma dosyasına taşınmamış olmaları silindikleri anlamına gelmez.
- Oyundaki mevcut klipler, hareket kodu ve efekt zamanlaması değiştirilmez.

Hareket bağlantıları: Ice → `wt_wolf_ice_ch.ltb`; Power gövdesinin kendi child kaydı → `WT_NEW_WOLF_CH.ltb`; R1 ve Wraith hareketleri kendi LTB'lerinde. Seçim bu kaynakları ortaklaştırmaz.

## Bilge Kağan — Ice / 40

Dik ve otoriter silüet. Göğüs geniş; bel dar fakat aşırı uzun değil. Kafa-boyun-omuz ayrı okunmalı. Yele ense boyunca kısa, düzenli kümeler halinde; omuz eklemini örtmemeli. Doğal yarı kapalı eller ve ağır pençeler korunacak.

Buz, önkolun dış hattında kontrollü plakalar halinde çalışmalı. Dirsek içi ve bilek hareket alanı boş kalmalı. Kristaller rastgele sivri levhalar gibi serpiştirilmeyecek. Lacivert bel kuşağı ve ince mat altın komutan motifleri; sırtın dövme alanı açık.

İnsan eşinin kimliği: lacivert-altın komutan kıyafeti, kısa kontrollü kürk yakası, olgun yüz ve sade saç. Kumaş panelleri kalça/diz hareket alanını daraltmayacak. Bu belge yeni bir insan iskeleti seçildiği iddiası değildir.

## Kül Tigin — R1 / 54

Atik, savaşçı, köşeli zırh silüeti. Bilge'den daha dar ve çevik gövde; katmanlı omuzluk ve kısaltılmış bel etekleri. Kızıl deri bağlar ile koyu çelik parçalar; yüz okunurluğunu kapatmayan kısa yele.

Native twist kemiklerinin olduğu üst kol/önkol bölgelerine kalın, tek parça sert zırh yapıştırılmayacak. Dirsek boşluğu ve bilek dönüşü açık bırakılacak. Sırt ve kolların dövme alanı zırhın altında kaybolmayacak. Kan yönü yalnız yüzey malzemesi ve motif tasarımıdır; yeni efekt/animasyon bu turda yok.

İnsan eşi: hareketli süvari komutanı, parçalı lamel zırh, kızıl kuşak, kollarda esnek deri. Aynı bağ ve metal motifleri iki formda tekrar eder.

## Alp Arslan — Power / 42

Dördünün en tok göğüs ve omuz hissi. Power gövdesinin oranları korunur; diğer üç karakterin yalnız şişirilmiş kopyası yapılmaz. Omuzluklar gövdeden bağımsız okunmalı, kolu tek bir iri kütleye dönüştürmemeli.

Sıcak gri kürk, bronz tokalar, koyu kahve deri. Köz çatlakları yüzey dokusunda ölçülü; göğsü kapatan ışık küresi veya yoğun çıkıntı yok. Alt gövde pratik deri/metal parçalarla dengelenir. Pençeler ve ayak tabanı biçimi kaynak eklem merkezlerine göre korunur.

İnsan eşi: Selçuklu esintili komutan; bronz miğfer, belirgin bıyık/sakal, deri ve zırh katmanları. Tarihî esin kullanılır; arkeolojik doğruluk iddiası verilmez.

## Konuralp — Wraith / 58

Uzun ve çevik avcı silüeti; omuzlar güçlü ama Alp Arslan kadar blok değil. Wraith'in kuyruk zinciri korunur; kuyruk silinerek başka iskelet gibi gösterilmez. Kuyruk kökü çevresinde kostümün kesim ve bind boşluğu buna göre tasarlanır.

Antrasit kürk, sınırlı mor işaretler, ince gümüş bağlantılar. Hafif çapraz deri donanımı; uzun, okunabilir pençeler. Boyun ve başın çizgisi belirgin; yüzü örten aşırı tüy veya kask yok. Kuyruk ve önkol twist kemiklerine yeni hareket yazılmayacak.

İnsan eşi: hafif sınır savaşçısı/izci; antrasit deri, koyu mor kuşak, sade gümüş toka. Uzun ve sert bir pelerin yerine hareket alanını açık tutan kısa parçalar.

## Ortak kalite sınırları

Hedef kurt başına yaklaşık 15 bin, insan başına 12 bin üçgen üst bütçesi korunur. Bu bir telefon FPS garantisi değildir. Küçük işlemeler dokuya; silüet ayrıntıları ölçülü geometriye aktarılır. Her karakter yalnız renk değişimiyle ayrı tasarım sayılmaz.

Kürk mat, metal kontrollü parlak, deri ve kumaş ayrı pürüzlülükte olmalı. Dövmeler bedenin derisini izlemeli; havada kart gibi durmamalı. Tüm yeni yüzeyler kaynak iskelete göre tasarlanır. Tasarım sırasında eklem yapısını saklamak için efekt kullanılmaz.

## Bu turdaki sonuç

**Yapıldı:** dört ayrı kaynak iskelet seçimi; hiyerarşi/hash kaydı; karakter kimliği ve kostüm briefleri; animasyona dokunmama kuralının kaydı.

**Statik inceleme:** `*-front.png` ve `*-three.png` dosyaları kaynakların nötr pozunu karşılaştırır. Bunlar bitmiş tasarım veya oyun içi bekleme animasyonu değildir.

**Henüz yapılmadı:** dört yeni nihai mesh/kostüm/doku tasarımı, dört yeni insan iskeleti seçimi, oyuna bu dört yeni tasarımın geçirilmesi veya yeni APK. Önceki oyundaki karakterler değiştirilmedi.

## Güncel özgünlük ve kaynak kullanım kararı

Kullanıcının son düzeltmesi: modeller Wolfteam'in birebir kopyası olmayacak. Kaynak iskeletin kemik sayısı, isimleri, parent bağlantıları, bind matrisi ve animasyonları aynı kalacak; **yeni gövde/yüz/kürk, kostüm, donanım ve giysi dokuları özgün tasarlanacak**. Kaynak kıyafeti yalnız yeniden boyamak ayrı tasarım sayılmaz. Kaynak giysi mesh'i de yeni kostümün yerine konulmaz.

**Karakter DTX'leri yalnız kontrol içindir.** UV/slot eşlemesini ve eski modelin neden bozulduğunu incelemeye yarar; giysi atlasları yeni karaktere bake edilmez, yeniden renklendirilip kullanılmaz, yeni APK'ya taşınmaz. Önceki `textured-references` çalışmaları bu nedenle teknik inceleme klasöründe kalır. Yeni üretim ilkesi `art/characters/original-roster/asset-policy.json` içinde.

Kullanıcı 6–7 model seçilmesine izin verdi; bu zorunlu artış sayılmadı. İlk kadro dört ayrı iskeletle devam eder. Yeni bir model ancak ayrı anatomi/iskelet/kostüm yönü kazandırırsa eklenir; aynı modelin palet değişimi yeni iskelet gibi sayılmaz.

### Özgün tasarım paftası

`art/characters/original-roster/design-board-v1.png`: dört kurt + dört insan eşi için özgün konsept. Kaynak DTX görselleri bu görsel üretimine verilmedi; giysiler aktarılmadı. Görselin ilk sürümünde ilk üç kurtta iskeletlerinde bulunmayan kuyruklar oluştu; düzeltildi. Son sürümde yalnız Wraith/Konuralp kuyruğu korunur. Konuralp insanının yüz yönü de Kül Tigin'den ayrıldı.

Pafta gerçek 3B mesh, UV, skin veya iskelet uyumu kanıtı değildir. Çizimdeki oranlar nihai mesh'te kaynak bind eklemlerine uyarlanacak; paftaya uydurmak için kemikler taşınmayacak. Dirsek içi, bilek, kalça ve diz çevresinde kostüm boşluğu korunacak. Görseldeki süslemeler mobil bütçeye göre sadeleştirilecek; bütün nakışlar geometri olmayacak.

### Kükreme sahibi karakter adı değil model türüdür

Kullanıcının düzeltmesine göre yeni veri ayrımı `model_type` üzerinden: `ice40`, `r1_54`, `power42`, `wraith58`. Aynı model türünü kullanan farklı karakterler aynı native kükremeyi paylaşır; ayrı model türleri tek bir genel kükremeye zorlanmaz. Bu turda mevcut oyun klibi veya oynama hızı değiştirilmedi.

`roar-model-profiles.json` yalnız okunarak çıkarılan kaynak sözleşmesidir:

| Model | T_CRY süresi | Kaynak anahtar | LTB'de görülen efekt olayı |
|---|---:|---:|---|
| Ice40 | 1.933 ms | 23 | 933 ms: `create_attachfx 3` |
| R1_54 | 1.500 ms | 46 | 0 ms: dört attachfx gösterimi; 500 ms: `create_attachfx 3` |
| Power42 / WT_NEW | 1.333 ms | 41 | 633 ms: `create_attachfx 3` |
| Wraith58 | 1.500 ms | 55 | 1.111 ms: `FX ChangeCharEffect` |

Bütün kliplerde 0 ms'de `WolfCrySnd` kaydı var. Bunlar kaynak asset olay metinleridir; kabuk komutu olarak çalıştırılmaz. Sayısal attachfx kimliği tek başına hangi emitter/doku ayarının kullanılacağını kanıtlamaz. Hareket, olay metni ve anahtar zamanlarının hash'leri kaydedildi; kaynak LTB'ler değişmedi.

**Power/WT_NEW kükremesi 41 anahtar içerir**; önceki eski paket tablosundaki 22 anahtar bu yeni paketin sayısı değildir. Güncel sözleşme doğrudan kaynak dosyadan doğrulandı.

Daha önce gelen tam kükreme videosundaki el alevleri, dövme parlaması, sönme ve geç izler efekt referansı olmaya devam eder. Var olan `reference-roar-fx.js` ve `effects.js` çalışmalarının sahneye bağlanma durumları aynı değildir; eski çalışma raporundaki efekt `runtime_installed:false` kaydı tamamlandı diye değiştirilmeyecek. Yeni modelde efekt bağlanması, doğru el kemiği, kendi native olay zamanı, özgün video ve modelin gerçek oynanışı birlikte kontrol edilerek yapılacak. Genel 1,2/1,7 saniyelik zamanla bütün klipler kesilmeyecek. Efekt kimlik rengi değişebilir; bunun için animasyon yeniden üretilmez.

### Bu tur kontrol sonucu

- Seçili kaynak gövde/hareket dosyalarının hash'leri değişmedi.
- Kükreme klipleri yalnız okundu; kesme, retarget, keyframe düzenleme veya yeniden örnekleme yok.
- Seçili 13 karakter DTX atlasının piksel hash'i mevcut oyun GLB'lerindeki 23 gömülü görüntüyle karşılaştırıldı: eşleşme yok. Bu dar kapsamlı bir aktarım kontrolüdür; tüm 33.624 DTX'nin yokluğu veya tam görsel özgünlük garantisi değildir. Rapor `reference-texture-audit.json`.
- Pafta dışında yeni nihai 3B karakter üretilmedi. Yeni ücretli Meshy işi başlatılmadı. CLI ücretsiz planlayıcısı görüntüden dokulu model başına 30 kredi tahmini verdi; bu tablo paftası üretime gönderilmedi. Bilge insan/kurt için olası iki yeni üretim 60 kredi tahminidir; yeni bütçe onayı ve temiz tek-figür üretim referansları olmadan gönderilmeyecek. Bakiye sorgusunda OAuth süresi dolmuş olduğundan güncel bakiye doğrulanamadı. Eski bakiye güncel gibi sunulmaz.
