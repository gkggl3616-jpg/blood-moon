# Rogue: Blood Moon — güncel çalışma, kalite ve hata kaydı

29 Ekim 2026. Bu belge yayımlanmış yeni APK raporu değildir. Son teslim edilmiş sürüm v0.1.17'dir. Bu turdaki kod değişiklikleri yerel çalışma ağacındadır; Karahan'ın görsel kalitesi kabul edilmediği için yeni APK yayımlanmadı. Yeni ücretli Meshy görevi başlatılmadı; bu tur üretim kredi harcaması sıfırdır.

## Kullanıcının güncel kararı

Karahan ayrı karakterdir; Bilge Kağan/Buz Kurdu'nun yerine yazılmaz. Bütün gelecek insan/kurt modellerinde doğal anatomi, kaliteli kürk ve kostüm, kontrollü yara/kuru kan, yıpranmış/yırtık pantolon ve gerçek PBR katmanları gerekir. Shader tek başına kalite çözümü değildir. Kalıcı tam prompt `docs/KALICI-KARAKTER-KALITE-PROMPTU-TR.md`, aynı metin kök `a.md` içindedir. `AGENTS.md` sonraki proje oturumlarını bu kurala yönlendirir. Bu, hesap genelinde otomatik hafıza garantisi değildir.

## Gerçekten yapılan kod düzeltmeleri

- `tools/viewer/arena.js`: fizik 60 Hz, görüntü daha yüksek yenilemede çalışırken fizik adımı olmayan karelerde `moving=false` üretiliyordu. Koşu/duruş arasında tekrar tekrar sıçrama oluşuyordu. Son fizik adımının gerçek yatay hızı saklanıyor; animasyon temposu görüntü karesindeki 0/değişken yer değiştirmeden hesaplanmıyor.
- Sıçrama, takla, dönüşüm, koşu, kükreme ve iz sürme eylemleri doğrudan `pointerdown` kullanıyor. Uyumluluk `click` olayına dayanmak, yönü tutan ilk parmak varken ikinci parmağı kaçırıyordu. Klavye/erişilebilirlik tıklaması korunuyor; tek dokunuş iki eylem üretmiyor.
- Kükreme HTMLAudio yeniden oynatmasından tek, önceden çözülmüş WebAudio sesine taşındı. Sesin başlama komutu ve poz süresi ortak. Pozdan sonra geciken ikinci ses kuyruğu yok; önceki ses durduruluyor. Karakter/sahne değişiminde ve arka plana geçişte kesiliyor. Kükreme sırasında giriş onay sesiyle üst üste binme engellendi.
- `prepare_roar_voice.py`: mevcut sesin 0–1,36 sn hazırlığı ve 1,80–3,11 sn güçlü kükremesi korunuyor; aradaki boşluk kaldırılıp perdeyi koruyan zaman sıkıştırması uygulanıyor. Yalnız sessiz hazırlığı kesip ana sesi atmak yanlış bir ilk denemeydi; son dosya o deneme değildir. Son tampon yaklaşık 1,319 sn, tepe 0,620; çalışma zamanı poz süresine uyarlar ve ayrıca ses düzeyi payı bırakır.
- Menü kükremesi de gerçek model klibinin süresini aynı ses yoluna gönderir. Hareket ve ses değişiklikleri yeni model üretiminden bağımsızdır.

## Kısa test — ne geçti, ne anlama gelmez

`refresh-touch-audio-test.json` ve `tools/verify_refresh_touch_audio.py`:

- Aynı gerçek arena güncellemesini 60/90/120/144 Hz adımlarla sürme: başlangıçtan sonra dört durumda da yalnız `WolfRunQuad`; tempo sabit 1,78331. Bu, farklı fiziksel telefonlarda FPS ölçümü değildir.
- Buz Kurdu pasifiyle fizik hızı 8,4 m/sn. 8 m/sn temel hız ile +%5 karakter hızı uygulanır.
- Chrome CDP gerçek çoklu dokunma olaylarıyla ilk parmak ileri basılıyken ikinci parmak sıçrama ve takla: geçti. Sıçrama tepe yatay hızı 8,4; çift hız eklenmedi.
- Kısa takla 2,01258 m; yön tuşunu bırakmadan koşuya döndü.
- İleri basılıyken kükremede yatay hareket durdu.
- Tek ses başlangıcı, 1,333 sn poz/ses süresi eşleşmesi; son ölçümde başlangıç komutu gecikmesi raporda kayıtlıdır. Dijital tepe payı kontrol edildi; gerçek telefon hoparlörü/algılanan ses kalitesi denenmedi.
- Tarayıcı JS hatası yok. Bütün oyun arayüzü, mağaza veya bütün dövme motifleri yeniden taranmadı.

Fiziksel Android kurulumu, görsel kullanıcı kabulü ve yeni APK imza doğrulaması bu tur yapılmadı. Önceki v0.1.17 imzası değiştirilmeyecek.

## Bilge Kağan'ın yerini alma kontrolü

Son v0.1.17 APK içindeki dosyalarla çalışma ağacındakiler birebir karşılaştırıldı:

- `models/bilge.glb`: SHA-256 `1b08c712bdbe96d9dd607da6a61c3dfd8b4ef3f2ab440d27a35369806354ef71`.
- `models/human-bilge.glb`: SHA-256 `754233f0a108e69cb3167f0b842936ce520b19a4ce17c7f57c451bcbd7b72e7a`.

Bu iki model bu tur değiştirilmedi. Bu, önceki sürümün görsel kalitesinin kabul edildiği anlamına gelmez. Karahan adayları `art/characters/karahan` altındadır; canlı karakter listesine eksik dosya bağlanmadı. Bir denemede Karahan'ı listenin başına eklemek varsayılan geri dönüş kimliğini etkileyebilirdi; bu geçici kayıt çıkarıldı. Yeni karakter yayıma hazır olduğunda kendi `karahan` / `human-karahan` dosyaları, kayıtları ve ayrı kartıyla eklenir.

## Modelleme nasıl yapılıyor — gerçek zincir

Mevcut Buz Kurdu: seçili Power42 gövdesi, 42 kemik, kaynak çene/dişler, 72 kaynak klip. Ücretli özgün üretimden görünüş aktarımı ve sürekli referans kürkü; kontrollü yeni pantolon ağırlıkları. Bu tur yeni Buz geometrisi üretilmedi.

Karahan kurt adayı: Behamah kaynak anatomisi, 40 kemik, 74 ham çocuk klibi; tam kükreme `T_cry` 1,933 sn, `T_Dash` 533 ms. Kısa `T_CRY_old` kullanılmaz. Kaynak eklem uzunlukları korunuyor. İki küçük başa bağlı boynuz, pantolon ve sınırlı kolluk; uzun bel süsleri kaldırılıyor. Ayrıntılar yüzey dokusuyla üretilmeli; kaynakta olmayan yeni rastgele gövdeyi sonradan iskelete zorlamak kullanılmayacak.

İnsan adayı: tamamı birbiriyle uyumlu Human47 gövde/baş temeli üzerinden ilerlemeli. Bilge'nin yüzünü kopyalayıp kıyafeti belden kesmek kötü sonuç verdi ve reddedildi. Karahan'ın insanı ayrı görünüş taşımalı. Tam native insan anatomisi doku girdisi olarak hazırlandı; bu yalnız hazırlıktır.

Araçlar: Blender 4.3.2, yerel Python üreticileri, kaynak LTB okuyucu, kaynak anahtarları doğrudan GLB'ye aktaran `export_bilge_native_basis.py`, ortak `apply_tattoo_policy.py`, Three.js gerçek çalışma zamanı. Blender kullanılması tek başına profesyonel görsel kalite garantisi değildir. İskelet/ham animasyon, statik geometri, UV/PBR, dövme ve FX ayrı aşamalar olarak tutulur.

## Bu tur bulunan ve önceki önemli hatalar

| Hata | Neden / karar | Gerçek durum |
|---|---|---|
| Koşunun ayakta duruşa sıçraması | Fizik adımı olmayan görüntü karesi hareketsiz sayılıyordu | Kod düzeltildi; dört yenileme oranı kontrolü geçti |
| Koşarken ikinci parmak sıçrama/takla çalışmaması | Android çoklu dokunmada uyumluluk click olayına güvenildi | Pointerdown ve CDP çoklu dokunma kontrolü geçti |
| Geciken/patlayan kükreme | Uzun HTMLAudio, pozdan geç gelen ana ses ve üst üste oynatma | Tek önceden çözülmüş ses, tam ifade/süre ve seviye payı; telefon ses kabulü açık |
| Yalnız hazırlığı ses diye kırpmak | Güçlü kükreme 1,8 sn sonrasındaydı | Tam ifade yeniden işlendi; ilk kısaltma kullanılmıyor |
| Bind farkından otomatik uyarlama çıkarmak | Yerel bind farkı tek başına retarget gerekçesi sayıldı | Deneme kaldırıldı. Aynı gövdenin kendi AI kükremesi ile çocuk T_cry anahtarları eşleşiyor; ham hareket korunuyor |
| Uzayan kasık/omuz/boğaz üçgenleri | Kaynak skin süreksizlikleri ve denenen uygunsuz ağırlık geçişleri | Karahan'da hâlâ açık; birkaç pozu geçmesi tamamlandı sayılmıyor |
| Tekrarlayan mermer/zebra kürk | Küçük fotoğraf örneğini tüm gövdeye fazla tekrarlama, aşırı normal şiddeti | Reddedildi; mevcut aday son kaplama değildir |
| Yamalı beyaz/siyah 3B doku aktarımı | Donor eşleşmesindeki boşluklar ve farklı renk bölgeleri | Reddedildi; yayıma alınmadı |
| Geçersiz normal bake pikselleri | Alpha=1 olması geçerli normal demek sanıldı | Yöntem tek başına kullanılmaz; normal vektörü ve dikiş kontrolü gerekir |
| Düz blok insan giysisi / ayrık kürk yaka | Zayıf elle kaplama ve uyumsuz parça birleştirme | Reddedildi |
| Kesilmiş zikzak insan kıyafet kenarı | Yüzleri yalnız yükseklikle silerek kısa kostüm yapma | Reddedildi; tam anatomik/kostüm temeli kullanılacak |
| Bilge ile Karahan kimliğinin karışması | Aynı insan yüzü/kostümü yeni karakter diye kullanma ve liste geri dönüş riski | Ayrı kimlik şartı kaydedildi; aday henüz canlı listede değil |
| Sırt dövmesinin giysiye/ön kola taşması | Düşük anchor, yön/baz ve yanlış gövde seçimi | Ortak deri yaması politikası; çok parçalı gövdede açık `tattooProjectionBodyName` kullanılır |
| Sadece ilk Body meshini projeksiyona almak | Çok parçalı modelde pantolon da Body adını taşıyabilir | Hedef gövde adı seçimi eklendi; kıyafete dövme basılmaz |
| Sürekli güçlü dövme parlaması | 20 sn güçlendirme ile kısa kükreme pozu karıştırıldı | Normal 0,025 / poz tepe 1,05 politikası korunuyor |
| Kırmızı dış ağız ovali / yüzün yanlış kesilmesi | Tahmini dünya koordinatıyla ağız ve çene üretme | Kullanılmayacak; gerçek kaynak ağız/çene korunur |
| Bilekten çıkan ince şeritler | Dekor/giysi geometrisi ve uzak kemiğe yanlış ağırlık | Kaynak ve yeni geometride ayrı kontrol; Karahan insanı tamamlandı denmiyor |
| UV adalarını karıştıran renk aktarımı | En yakın UV'leri bir üçgende enterpole etme | Önceki yöntem reddedildi; kaynak kıyafetleri özgün tasarım diye kopyalanmaz |
| Gerçek 3B yerine konsept teslimi | Pafta ile runtime varlığını aynı sayma | Pafta, geometri, entegrasyon ve görsel kabul ayrı yazılır |

## Dövme, FX ve kaynak arşiv gerçeği

Sırt ve iki üst kol yaması aynı ortak politikayı kullanır; giysi malzemeleri dışlanır. Motif değişince skin/yerleşim değişmez. Yeni Karahan'da son görsel kontrol tamamlanmadı. Dövme bonus hesabı değiştirilmedi: temel × [1 + karakter pasifi/100 + uygun dövme toplamı/100] × aktif yetenek çarpanı. +%240 tek başına 100'ü 340 yapar; eski 180 tavanına dönülmez.

73.019 girdilik arşiv indeksi ve seçili kaynaklar yereldedir; 4,7 GB yeniden indirilmedi. `modelbutes.txt` içindeki Behamah `ClientFXOnce3="cryguardian"` bağlantısı bulundu. Bu grubun gerçek içeriği **CamJitter**'dır; görsel ateş/sprite paketi değildir. CamJitter türü okuyucuya eklendi. Kaynakta bulunmayan bir parçacık efekti bulundu denmez. Oyunun mevcut el alevi ve dövme parlaması ayrı katmandır. AI kükreme olayındaki FIRE_KEY komutu oyuncuya hasar olarak çalıştırılmaz.

Arşiv indeksindeki sesler arasında karakter kükremesi bulunmadı. Bu yüzden ses mevcut proje sesinden düzenlendi; arşivden özgün ses alındı denmez. Diğer modellerin Howling_Ice/Fire/Wraith/Reboot grupları önceki runtime kaynak paketinde bulunur. Bütün kurtlara yeni FX görsel kabulü yapıldığı iddia edilmez.

## Yeni doku üretimi için somut hazırlık ve maliyet

Hazır, henüz kaplanmamış girişler:

- `art/characters/karahan/texture-inputs/wolf-texture-input.glb` (yaklaşık 221 KB).
- `art/characters/karahan/texture-inputs/human-texture-input.glb` (yaklaşık 126 KB).

Öneri: mevcut geometrilere **yalnız 4K PBR Retexture**, bir insan + bir kurt. Yeni rig, yeni animasyon, yeniden geometri üretimi veya remesh satın alınmayacak. Çıktıdan yalnız uygun UV/PBR verisi alınır; kaynak iskelet ve animasyon verisi korunur. Modelde kalan skin/geometri sorunlarını doku görevi düzeltmez; bunlar bağımsız yerel iş olarak açık kalır. Doku sonucu kötü çıkarsa otomatik ücretli tekrar yapılmaz.

29 Ekim 2026'da okunan resmî fiyat tablosu: <https://docs.meshy.ai/en/api/pricing>. Retexture 2K/4K = model başına tahmini 10 kredi; iki model **20 yeni kredi**. CLI bakiye kontrolü **825 kredi**. Yeni 20 kredi henüz onaylanmadı/harcanmadı; gerçekleşen tutar ancak görev bittikten sonraki `consumed_credits` ile bilinir. Önceki Bilge üretim bütçesi sınırsız yeniden deneme izni sayılmaz.

Kurt doku yönü: anatomiyi takip eden kömür grisi doğal kürk, daha açık kontrollü göğüs/çene, gerçek keratin boynuz/pençe, içeri çekilmiş koyu ağız, doğal fildişi diş, kehribar göz ve belirgin koyu gözbebeği. Mat siyah dokuma pantolon; sınırlı yırtık, altında kürk; dikiş/kıvrım/yıpranma. Küçük bronz donanım. Az sayıda iyileşmiş pençe yarası ve koyu kuru kan. Kalıcı dövme veya parlayan yara dokuya basılmaz. Metalik kürk, mermer/zebra desen, bütün gövde kanı ve boyalı ışık yok.

İnsan doku yönü: Bilge'den ayrı sert komutan yüzü, koyu kısa saç/sakal, küçük eski yanak yarası; siyah çelik/eskitilmiş bronz kısa zırh, gerçek deri kayış ve dokuma pantolon. Ten/saç/kumaş/metal ayrı PBR tepkisi; ten üzerinde metal desen veya kâğıt kürk yaka yok. Wolfteam DTX kıyafet pikselleri kullanılmaz.

## Kalan işler ve teslim koşulu

1. Karahan'ın uzayan skin yüzeylerini gerçekten düzeltmek; boğaz/omuz/kasık kusurları kapanmadan tamamlandı dememek.
2. İki özgün kaliteli doku/malzeme üretimi; yeni ücretli işlem için yeni bütçe kararını almak.
3. Tek örnek dövme, tam kükreme ve model FX/ses çevrimiyle kısa görsel kontrol. Her motif veya tüm oyun arayüzünü tekrar taramamak.
4. Karahan'ı kendi kimliği ve iki dosyasıyla gerçekten oyuna bağlamak; Bilge'nin kimliğini/kayıtlarını korumak.
5. Sürüm kodunu artırmak, önceki imzayla tek bağımsız APK üretmek; APK'nın tüm runtime dosyalarını içerdiğini ve imzayı doğrulayıp APK + güncel MD bağlantısını teslim etmek.

Bu maddeler henüz tamamlanmış değildir. Şu anki kusurlu adaylar "hatasız son sürüm" diye kullanıcıya gönderilmedi.
