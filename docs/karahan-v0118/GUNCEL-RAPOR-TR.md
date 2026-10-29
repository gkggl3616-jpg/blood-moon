# Karahan — güncel model, animasyon ve hata kaydı

29 Ekim 2026. Bu belge önceki “üretim başlamadı / bütçe bekleniyor” durumunun yerine geçer. Fiziksel Android ve kullanıcı görsel kabulü yapılmadı. APK teslim bilgileri aşağıdaki doğrulama kaydında ayrıca belirtilir.

## Son tasarım talimatı ve sonuç

Kullanıcı son olarak yalnız kurdun Meshy ile yeniden işlenmesini istedi: Behamah'taki yana kıvrılan boynuzlar, belirgin yırtık pantolon/kapri, kan ve pençe yaraları; yumuşak temiz tasarım istemiyor. Son tur yalnız kurt için yapıldı. İnsan için ikinci ücretli iş açılmadı.

Karahan kendi `karahan` kimliğiyle karakter listesinin sonuna eklendi. `human-karahan` onun insanıdır. Bilge Kağan/Buz Kurdu'nun kimliği ve iki model dosyası değiştirilmedi. Eski krediler ve seçili karakter korunur; Karahan güncelleme hediyesi olarak sahip olunan listeye eklenir. Bu bir mağaza harcaması değildir.

Gerçek kurt modeli: seçilmiş Behamah anatomisi, 40 kemik, 74 ham kaynak klip. Boynuzlar kaynak modelin yan boynuzlarıdır; sonradan çizilmiş dik sivri boynuzlar kaldırıldı. Alt giysi ayrı, gövdeye yakın kapri kabuğudur; yırtıkların altında gövde korunur. Uzun etek/kaftan sarkıtları yoktur. Son model 11.631 üçgen; insan 3.204 üçgen/47 kemik/11 kaynak klip. Küçük ayrıntılar PBR dokudadır. İnsan, Bilge'nin başını kopyalamaz; tam Human47 gövdesinin ayrı kaplamasıdır.

Meshy yeni iskelet veya yeni animasyon üretmedi. Retexture çıktısındaki UV ve PBR verisi mevcut gerçek modele aktarıldı; kaynak rig ve ağırlıklar ayrı korundu. Albedo 4K, normal 2K, paketlenmiş pürüzlülük/metal katmanı 1K kullanılır. Deri/kürk kumaş ve keratin ayrı malzeme gruplarındadır. Görsel kontrol dosyaları bu klasördeki `WolfIdle-front.png`, `WolfIdle-back.png`, `WolfRunQuad-side.png`, `WolfRoar-three.png`, `karahan-human-front.png` dosyalarıdır; konsept değil gerçek GLB/Three.js görüntüleridir.

## Ücretli üretim — gerçek kullanım

İlk onay: insan+kurt 4K PBR toplam 20 kredi. İlk kurt görünüşü kullanıcı tarafından fazla temiz/yumuşak bulundu. Kullanıcı yalnız kurdu yeniden istedi; 10 ek krediyle tek tekrar yapıldı. Toplam bu çalışma 30 kredi; sınırsız tekrar izni yoktur.

| Görev | Kimlik | Gerçek kredi | Durum |
|---|---|---:|---|
| İlk kurt PBR | 01a188ef-e682-76a7-b177-d2ea1c3cb7dd | 10 | Son görünüş olarak kullanılmadı |
| İnsan PBR | 01a188f0-3489-71d1-bfe1-dd7fff0337cd | 10 | Korundu; tekrar üretilmedi |
| Savaş yaralı kurt PBR | 01a188fc-2079-766d-b337-6759221b5482 | 10 | Güncel kurt kaplaması |

800 karakter sınırını aşan iki istem görev kabulünden önce hata verdi; bunlara kabul edilmiş görev kimliği/kredi tüketimi kaydı yoktur. Kabul edilen üç görevin `consumed_credits` alanları 10'ar kredidir.

## Animasyon ve iskelet: hangi veri korundu, ne uyarlandı?

Kaynak `wolf_king_behamah.ltb`, hareket çocuğu `wolf_kingasmon_ch.ltb`. Dört ayak koşusu `T_Dash`: 0,533 sn. Tam kükreme `T_cry`: 1,933 sn/59 anahtar; efekt olayı 0,866 sn. Kısa `T_CRY_old` seçilmedi. Ham 74 kaynak klip saklanır.

Önemli gerçek hata: aynı adları taşıyan kaynak kliplerde bazı yerel kemik öteleme uzunlukları gövdeyle aynı değil. Üst kol gövdede 21,946 kaynak birimi, bekleme/koşuda 17,838, kükremede 21,946; ön kol 25,443'e karşı 20,942. Doğrudan oynatmak uzuv oranını klipler arasında değiştiriyordu. Karahan için türetilmiş çalışma zamanı klipleri, yerel öteleme yönünü/zamanını koruyarak uzunluğu gövdenin rest uzunluğuna sabitler. Kök ve pelvisin hareketi bu işlemden hariçtir. Diğer karakterlere bu yeni kural uygulanmaz.

Kükreme için ayrıca `DerivedBehamahRoar` adında açıkça türetilmiş klip eklendi. Kaynak dönüşler ve 59 zaman anahtarı korunur; uzunluk uyarlaması ve tek düzeltici şekil kanalı vardır. Kükreme tepesinde baş/çene/diş/boynuz birlikte yaklaşık 25 cm aşağı toparlanır; boyun geçişi ağırlıklı yumuşar. Bu bir mesh düzeltmesidir; “bütün çıktı animasyonları hiç değişmedi” denmez. Ham 74 klip değişmeden ayrıca mevcuttur. Çene ve ağız gerçek kaynak geometrisidir; kırmızı dış oval eklenmedi.

Uzunluk uyarlaması yer temasını değiştirdiği için Karahan'da 25 örnekle gerçek Three.js deformasyonu üzerinden bekleme/yürüyüş/kükreme zemin eğrileri ölçüldü. Koşuda tek taban düzeltmesi kullanılır; doğal havalanma fazları her kare yere yapıştırılmaz. Bekleme ve kükremenin incelenen örneklerinde taban zeminden yaklaşık 8 mm yüksektedir. Bu tam ayak IK sistemi değildir.

## Dövme ve efekt

Sırt, sol ve sağ kol ayrı üç yüzey yaması kullanır. Kaynak gövde üzerinde barycentrik bind yüzeyi ve aynı skin ağırlıkları kullanılır; giysi yüzleri hariçtir. Önce nötr pozu ters skin matrisiyle geri çözmek kıvrık kolda hatalı noktalar üretmişti; Karahan'da bu yol yerine doğrudan gövde yüzeyi kullanılır. Bütün motifler aynı üç yama üzerinden çalışır; bu tur her motif tek tek denenmedi. Normal parlama düşük, kükreme parlaklığı ortak politika değeridir. Bonus hesabı/sahiplik katmanları değiştirilmedi.

Meshy'nin kendiliğinden bastığı sabit omuz damgaları istenmiyordu; yerel doku temizliği yapıldı. Kuşanılan dövmeler ayrı kalır. Savaş yaraları kozmetik doku ayrıntısıdır, yeni bonus veya hasar türü değildir.

Karahan'ın arşivdeki `cryguardian` grubu kaynak kamera titreşimi içerir; bu grubun içinde kaynak parçacık/şok dalgası bulunmadı. Mevcut özgün el alevleri ve dövme parlaması buna eşlik eder. Kaynakta olmayan bir parçacık efekti “arşivden aynen alındı” diye sunulmaz. Diğer ailelerin mevcut kaynak Howling efektleri korunur. Arşiv ses indeksinde karakter kükremesi bulunmadı; ses mevcut proje kaydından düzenlendi.

## Gerçek kod hataları ve düzeltmeler

- 60 Hz fizik/90–144 Hz görüntü farkında adım olmayan kareler hareketi sıfırlıyordu. Son fizik adımının gerçek yatay hızı saklanır; animasyon temposu değişken görüntü yer değiştirmesinden hesaplanmaz.
- Yönü tutan parmak varken ikinci parmakla sıçrama/takla/dönüşüm kaçıyordu. Eylemler doğrudan `pointerdown` üzerinden çalışır; tek dokunuş çift eylem üretmez.
- Kükreme sesindeki hazırlık/boşluk ana sesi geciktiriyordu. Hazırlık ve ana kükreme birlikte korunup ara boşluk kaldırıldı. Tek, önceden çözülmüş WebAudio sesi poz süresine uyarlanır; tepe yaklaşık 0,620, ek oynatma payı vardır. Kükreme sırasında onay sesiyle üst üste binme engellendi. Sahne/karakter değişimi ve arka plan sesi durdurur.
- Shader ile bozuk geometriyi örtmek kalite çözümü değildir. PBR yalnız yüzey tepkisini sağlar.
- Geniş kör ağırlık yumuşatma, göğse baş/çene ağırlığı taşıdı; reddedildi. Üst gövdede kaynak skin ağırlıkları yeniden yüzeye aktarıldı. Tam bind farkı çarpımıyla kör retarget da kullanılmadı.
- Ağız malzemesini geniş boyun alanına sürmek ve çene ağırlığını göğse taşımak yanlış denemeydi; üretim zincirinden çıkarıldı.
- Meshy normalizasyonu UV aktarımını kaydırıyordu. Model sınır kutusuyla ölçülü kayıt ve üçgen bazında UV aktarımı yapıldı. Kurt en büyük kayıt hatası yaklaşık 1,52 mikrometre; insan 0,764 mikrometre. Nonplanar giysi dörtgenlerinde farklı üçgenleme yüzey karşılaştırmasını yaklaşık 1,07 mm etkiliyor; bu gövdeyi yeniden üretme değildir.
- Blender'daki tembel JPEG yükleme yüzünden albedo bağlantısı var görünse de GLB'ye gömülmüyor, model beyaz çıkıyordu. Görüntü açıkça çıkarılıp okunarak paketlendi; APK kapısı Karahan malzemelerinde gerçek albedo ve dış dosya bağımlılığı olmamasını doğrular.
- İlk sürümde özgün yan boynuzları kaldırıp dik boynuz çizmek kullanıcı talebine aykırıydı; kaynak boynuzlar geri getirildi.
- Testte gizli arena seçim kutusunu görünür öğe gibi seçmek zaman aşımı verdi; test hazırlığı düzeltilerek tekrar çalıştırıldı. Bu oyun hatası değildir.

## Kısa doğrulama ve sınırlar

`refresh-touch-audio-test.json`: Buz Kurdu'nun 60/90/120/144 Hz hareket sürekliliği, gerçek CDP çoklu dokunma sıçrama/takla, yaklaşık 2 m takla, hareket tuşu basılı kükremede durma ve tek ses sınandı. Yeni Karahan karşılığı `karahan-touch-audio-test.json` dosyasına yazılır. Bunlar fiziksel telefon testi değildir.

`karahan-first-review.json`: bekleme ön/arka, koşu yan, tam kükremenin örnek pozu ve takla; `karahan-grounding.json`: gerçek deformasyon yer teması ölçümü. Beş poz örneği bütün hareket boyunca kusursuzluk garantisi değildir. Kaynak gövdenin omuz/kürk sınırlarında sert yüzey geçişleri ve koşu/kükremede az sayıda yüksek oransal kenar büyümesi hâlâ kalite riski taşır. Bunları “hatasız model” diye saklamıyoruz. Telefon performansı, hoparlör ve kullanıcı estetik kabulü açık kalır.

## Tekrar kullanılacak üretim kuralı

Önce doğrulanmış gövde/rig/çene paketi seçilir. Aynı ailede kontrollü yeni görünüş ve küçük, eklemden uzak geometri hazırlanır. Rastgele vücut üretip sonra kırparak iskelete zorlanmaz. Kurtlarda belirgin pantolon/kapri; yırtığın altında gerçek gövde; kontrollü kan/pençe izi; kuşanılabilir dövme için açık deri alanı bulunur. Boynuz, ağız, diş ve pençe silüeti kaynak hareketle birlikte tasarlanır. Albedo/normal/pürüzlülük ayrı hazırlanır; kumaş kürk gibi, kürk metal gibi parlamaz. Tam boyutlu dokular görsel netliği artırır ama telefon bellek/performance ölçümünün yerine geçmez.

Güncel kurt zinciri: son PBR malzemeli `wolf-static.blend` → kaynak üst gövde skin onarımı/native export/ortak dövme politikası → açıkça türetilmiş kükreme düzelticisi → ölçülü uzunluk uyarlamalı gait ölçümü → gerçek WebGL yer teması meta verisi → ayrı `models/karahan.glb`. Eski reddedilmiş oral/skin denemeleri yeniden çalıştırılmaz. `docs/KALICI-KARAKTER-KALITE-PROMPTU-TR.md` genel standart olmaya devam eder.
