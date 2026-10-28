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
