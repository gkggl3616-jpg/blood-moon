# Karahan — güncel model, animasyon ve hata kaydı

29 Ekim 2026. v0.1.18 / sürüm kodu 19 yayımlandı. Bu belge önceki “üretim başlamadı / bütçe bekleniyor” durumunun yerine geçer. Fiziksel Android ve kullanıcı görsel kabulü yapılmadı.

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

### Bu sürümde tamamlanan kısa Karahan sonucu

Karahan kimliğiyle 60/90/120/144 Hz hareket örneklerinde yalnız koşu durumu görüldü; tempo 2,179411, donanımla yatay hız 8,4 m/sn. Çoklu dokunma sıçrama/takla geçti; takla 2,01258 m. Yön tuşu basılı kükremede yatay hareket durdu. Tek ses 1,93299997 sn; son yerel ölçümde komut gecikmesi yaklaşık 3,9 ms. Bu değer hoparlör akustik gecikmesi değildir. Bilge iki dosyasının SHA-256 değerleri önceki APK ile aynı kaldı.

### Son kurt üretiminde kullanılan gerçek Meshy istemi

```text
Savage battle-hardened werewolf Karahan. Keep supplied BEHAMAH side horns exactly: curved dark ridged keratin, not upright spikes. Natural charcoal fur, amber eyes, ivory fangs, dark inner mouth. UNMISTAKABLE faded brown-olive COMBAT CAPRI trousers: leather waistband, pockets, seams, ragged below-knee hems, large frayed tears exposing grey fur. Distinct cloth from fur, not black leggings. VISIBLE dark red blood streaks on chest, shoulders, forearms and hands. Three large claw-slash scars with fresh red edges, bruises, dirt. Scarred black steel bracers, worn bronze edges. Brutal war-game veteran, NOT clean, soft, polished or elegant. Detailed realistic PBR. No tattoos, logos, glow or baked lighting. Preserve anatomy.
```

İstenen koyu kürke rağmen üretim göğüs/kollarda daha sıcak çıplak deri yorumu verdi. Bu sapma saklanmaz; gerçek görünüş önizlemelerdeki gibidir. Yeni ücretli tekrar açılmadı.

## Gerçek APK teslimi ve son kontrol

- [Tek, bağımsız APK v0.1.18](https://github.com/gkggl3616-jpg/blood-moon/releases/download/prototype-v0.1.18-25/Rogue-Blood-Moon-v0.1.18.apk); sürüm kodu 19.
- Boyut 133278989 bayt (yaklaşık 133,3 MB). SHA-256 `32075e6f9a9e1551c355599bbdbf85c271be2699a32efdca5450e4421e33f7dd`.
- Önceki sürümle aynı imza sertifikası: `af43be4b6ee4d5b2e1feca6da3df36805a7b10bbb56b1f884136054ef7f98633`. Paket `com.roguebloodmoon.prototype`; önceki sürüm kodu 18 idi. İmza/sürüm uyumluluğu doğrulandı; gerçek cihazda kurulum denenmedi.
- Yayımlanan APK yeniden indirildi; ZIP bütünlüğü ve 86 çalışma zamanı dosyasının her biri yerel güncel dosyayla bayt bayt aynı bulundu. Modeller, PBR dokular, FX ve ses APK içinde. Ek veri kurulumu yok.
- CI 40941336513 başarılı; kaynak commit `796bd9c350fe73497d0185ffceb75bd77acb7a2a`. Buz kaynak sözleşmesi/temas geçişleri ve Karahan çoklu dokunma/ses testi geçti. Karahan kaynak efekt grubu `cryguardian` bulundu ve desteklenmeyen bileşen kaydı çıkmadı.
- [İsteğe bağlı kurt GLB dosyası](https://github.com/gkggl3616-jpg/blood-moon/releases/download/prototype-v0.1.18-25/Karahan-Wolf.glb). Bu, APK kurulumu için gerekmez. Uzunluk uyarlaması/zemin sözleşmesi oyunun runtime katmanındadır; genel bir GLB oynatıcı ham klipleri doğrudan seçerse aynı sonuç garanti edilmez.

Açık işler: omuz/kürk sınırlarındaki yüzey kalitesi, bazı pozlardaki kaynak deformasyonları ve istenen koyu kürke karşı üretimin sıcak deri yorumu. Yeni ücretli üretim açılmadı. Bu aday, görsel kullanıcı kabulü veya bütün karakterlerin tamamlandığı anlamına gelmez. Sonraki düzenleme aynı gövde üzerinde bu somut sorunlara odaklanmalı; bütün oyun ve dövme motifleri tekrar taranmamalı.

## Ek — güncel dosya eşleştirme rehberi

# Hangi dosya hangi karaktere ait?

Güncel durum: 29 Ekim 2026, yayımlanmış APK v0.1.18 / kod 19. Kullanıcı son mesajında koşunun doğru çalıştığını doğruladı; bu bildirim üzerine koşu kodunda yeni değişiklik yapılmadı. Telefonda bizim tarafımızdan test yapıldığı anlamına gelmez.

## GitHub'da nerede?

Güncelleme dalı: `animation/bilge-roar-study-01`. GitHub varsayılan `main` dalına bakmak bu çalışma dosyalarını göstermeyebilir.

- Oyun kaynakları: `app/src/main/assets/`.
- Gerçek paketlenmiş modeller: `app/src/main/assets/models/`.
- Güncel rapor: `docs/karahan-v0118/GUNCEL-RAPOR-TR.md`.
- İndirilebilir APK/model/rapor: <https://github.com/gkggl3616-jpg/blood-moon/releases/tag/prototype-v0.1.18-25>.

## Oyun içinde kullanılan gerçek dosyalar

| Oyundaki ad | Kod kimliği | Kurt dosyası | İnsan dosyası | Güncel gerçek iskelet durumu |
|---|---|---|---|---|
| Karahan | `karahan` | `models/karahan.glb` | `models/human-karahan.glb` | Kurt Behamah40; insan Human47 |
| Bilge Kağan / Buz Kurdu | `bilge` | `models/bilge.glb` | `models/human-bilge.glb` | Güncel kurt Power42; insan Human47. “Buz” görünüş/karakter adıdır; güncel rig Ice40 değildir. |
| Kül Tigin / Kan Kurdu | `kultigin` | `models/kultigin.glb` | O model için ayrı tamamlanmış native insan GLB'si yok | APK'daki mevcut kurt eski 27 kemikli model; seçilen R1_54 ailesinin tam aktarımı tamamlanmış değildir. |
| Alp Arslan / Köz Kurdu | `alparslan` | `models/alparslan.glb` | Ayrı tamamlanmış native insan GLB'si yok | APK'daki mevcut kurt eski 27 kemikli model; Power42 seçim kaydı bu dosyanın tamamlandığını göstermez. |
| Konuralp / Gölge Kurdu | `konuralp` | `models/konuralp.glb` | Ayrı tamamlanmış native insan GLB'si yok | APK'daki mevcut kurt eski 27 kemikli model; Wraith58 aktarımı tamamlanmış değildir. |

Başıbozuk→Kül Tigin, Kül→Konuralp, Ayaz→Alp Arslan görsel dosyasına eşlenir. Bunlar bağımsız yeni gövde ailesi sayılmaz. İnsan formunda gerçek ayrı model bulunmayan karakterlerin mevcut oyun davranışı, tamamlanmış yeni insan modeli diye sunulmaz.

**Karahan adıyla yeni bir `.ltb` üretilmedi.** Oyun dosyası `karahan.glb`'dir. Kaynak LTB'nin adı hâlâ `wolf_king_behamah.ltb`'dir; kaynak dosyanın adını Karahan yaparak kökeni gizlemiyoruz.

## LTB model / iskelet / animasyon eşleştirmesi

Dosya uzantısı **`.ltb`**; “ldb/lbt” yazımları burada aynı dosya türü anlamında kullanılmamalıdır. LTB, kaynağa göre geometri, iskelet, ağırlık ve/veya animasyon içerir. `_ch` dosyası genellikle hareket çocuğudur; her modelde aynı adlı kemik olması uyum garantisi değildir.

| Aile / kullanım | Kaynak gövde LTB | Kaynak hareket LTB | Not |
|---|---|---|---|
| Karahan / Behamah40 | `wt_chars/newchars/wolf_king/wolf_king_behamah.ltb` | `wt_chars/newchars/wolf_king/wolf_kingasmon_ch.ltb` | 40 kemik, 74 ham klip. `T_Dash` 533 ms; tam `T_cry` 1933 ms; takla `T_Specialatk` 1000 ms. `DerivedBehamahRoar` bizim açıkça türetilmiş düzelticimizdir. |
| Güncel Bilge / Power42 | `wt_wolf_power_r.ltb` | `wt_new_wolf_ch.ltb` | 42 kemik, 72 ham klip; koşu `T_WallDash`, kükreme `T_CRY` 1333 ms. Hareketin asıl yerel dosyası `art/3d/source/pedro-native/new-motion/wt_new_wolf_ch.ltb`. |
| Ice40 / ilk Buz ailesi seçimi | `wt_wolf_ice_r.ltb` | `wt_wolf_ice_ch.ltb` | 40 kemik; eski seçim. Güncel `bilge.glb` bununla karıştırılmaz. |
| R1_54 / Kan ailesi seçimi | `r1_wolf.ltb` | `r1_wolf.ltb` | 54 kemik; gövde ve hareket aynı dosyada. Seçilmiş kaynak, güncel 27 kemikli Kül Tigin dosyasıyla aynı şey değildir. |
| Power42 / Köz ailesi seçimi | `wt_wolf_power_r.ltb` | `wt_new_wolf_ch.ltb` | Seçilmiş aile; güncel `alparslan.glb` henüz native42 aktarımı değildir. |
| Wraith58 / Gölge ailesi seçimi | `wt_wolf_wraith.ltb` | `wt_wolf_wraith.ltb` | 58 kemik; gövde ve hareket aynı dosyada. |
| Karahan insan temeli | `pedro.ltb` | `wt_new_man_ch.ltb` | 47 kemik; APK'da gereken 11 insan klibi seçildi. Kaynağın bütün 569 klibi APK'ya konulmadı. |
| Bilge insan hareketi | Ayrı özgün Bilge görünüşü / Human47 temeli | `wt_new_man_ch.ltb` | İnsan/kurt aynı iskeleti paylaşmaz; görsel kimlik eşleşir. |

Seçilmiş dört eski aile için yerel model kökü `art/3d/source/wolfteam-archive/selected/`. Karahan için `art/3d/source/wolfteam-archive/full-selected/` + tabloda belirtilen arşiv yolu. İnsan kaynağı `art/3d/source/pedro-native/main/pedro.ltb`.

Behamah AI `wt_wolfrush_behamah_type_ai.ltb` + `ai/ch/wt_wolfrush_behamah_ch.ltb` başka kaynak çifttir. Benzer isim nedeniyle Karahan'ın Wolf King gövdesine körlemesine bağlanmaz.

## DTX: doğrulanmış kaynak doku eşleştirmeleri

DTX, doku/görünüş dosyasıdır; tek başına iskelet veya animasyon değildir. Aşağıdaki kıyafet dokuları **kaynak incelemesi içindir**. Kullanıcının talimatıyla kaynak giysileri yeni özgün kostüm diye APK'ya kopyalamıyoruz. Güncel Karahan, Meshy PBR görüntülerini GLB içine gömülü kullanır; ayrı DTX kurulumu istemez.

Aşağıdaki Behamah, Power ve Ice bağlantıları kaynak `Root/attributes/modelbutes.txt` içindeki `ModelFile`/`Skin` alanlarından doğrulandı; yalnız ad benzerliğiyle tahmin edilmedi.

| Kaynak model | DTX / diğer kaynak görünüş dosyası | Bölüm / güven durumu |
|---|---|---|
| Wolf King Behamah | `wt_chars/newchars/wolf_king/wolf_king_behamah_upper.dtx` | Üst gövde, Skin0; doğrulandı |
| Wolf King Behamah | `wt_chars/newchars/wolf_king/wolf_king_behamah_lower.dtx` | Alt gövde, Skin1; doğrulandı |
| Power R | `wt_chars/skins/wt_wolf_r.dtx` | Skin0; doğrulandı |
| Power R | `wt_chars/skins/wt_man_r.dtx` | Skin1; kaynak yardımcı malzeme, yeni insan kostümü değildir |
| Power R | `wt_chars/skins/wt_pv_mark2.dtx` | Skin2; kaynak kayıt |
| Power R | `wt_chars/skins/wt_wolf_powershoulder_r.dtx` | Omuzluk, Skin3; doğrulandı |
| Ice R | `wt_chars/skins/wt_icewolf_r.dtx` | Skin0; doğrulandı |
| Ice R | `wt_fx/wolflight/wolflightice.spr` | Skin2 sprite; DTX değil, efekt katmanı |
| Bu üç kaynak model | `wt_chars/skins/helmet.dtx` | Kaynak Skin4 kaydı; yeni karaktere otomatik takılacak aksesuar anlamına gelmez |
| Pedro insan / üst gövde ve baş | `wt_chars/newchars/pedro_red/pedro_r_upperbody.dtx` | Kaynak UV/görünüş incelemesi |
| Pedro insan / alt gövde | `wt_chars/newchars/pedro_red/pedro_r_lowerbody.dtx` | Kaynak UV/görünüş incelemesi |
| Pedro insan / el | `wt_chars/newchars/pedro_red/pedro_gloves01.dtx` | Kaynak UV/görünüş incelemesi |
| Pedro insan / ayakkabı | `wt_chars/newchars/pedro_red/pedro_boots01.dtx` | Kaynak UV/görünüş incelemesi |
| Pedro kurt / üst | `wt_chars/newchars/pedro_wolf/pedro_wolf_upper.dtx` | Pedro kurt kaynağı; Karahan/Behamah dokusu değildir |
| Pedro kurt / alt | `wt_chars/newchars/pedro_wolf/pedro_wolf_lower.dtx` | Aynı ayrım |
| Pedro kurt / kürk | `wt_chars/newchars/pedro_wolf/pedro_wolf_hair.dtx` | Aynı ayrım |
| R1_54 | Kesin gövde/DTX bağlama kaydı henüz doğrulanmadı | Benzer adlı Reboot dokuları kesin eşleşme diye atanmaz |
| Wraith58 | Kesin gövde/DTX bağlama kaydı henüz doğrulanmadı | Arayüzdeki Wraith kart DTX'leri model ten dokusu değildir |

Behamah'ın `balrog`, `destroyer`, `dreadnought` alt/üst DTX dosyaları da vardır; bunlar ayrı kaynak görünüş varyantlarıdır. Hepsi aynı anda Karahan'ın kaplaması değildir.

## Dövme ve FX dosyaları

- Güncel dövme atlası `art/3d/textures/tattoo-atlas.png`; oyunda gerekli görüntü/model içine aktarılır. Kaynak örnek `wt_chars/skinstattoo/tattoo_icewolf_dragon.dtx` gibi dosyalar motif referansıdır, rig değildir.
- Ortak yerleşim/parlama politikası `art/characters/model-families/tattoo-policy.json`.
- Runtime kaynak FX paketi `app/src/main/assets/fx/native/native-roar-assets.json`; doku alt klasörü `fx/native/wt_fx/`.
- Karahan kaynak FX grubu `cryguardian`: kaynak kamera titreşimi. Bu grupta kaynak parçacık/şok dalgası bulunmadı; el alevi/dövme parlaması projedeki ayrı efekt katmanıdır.
- Diğer mevcut gruplar: Bilge `Howling_Ice_1`, Kül Tigin `Howling_Reboot_1_Red`, Alp Arslan `Howling_Fire_1`, Konuralp `Howling_Wraith_1`. Efekt ailesi, gövdenin güncel kemik sayısı veya karakter adından ayrı bir seçimdir.
- Projedeki güncel ses `app/src/main/assets/media/roar-voice.wav`. Arşivden özgün karakter kükremesi bulunduğu iddia edilmez.

## Karahan'a oyundan ulaşma

v0.1.18'de Envanter → Karakterler / Kurt Formları → KARAHAN. Sol karakter açılır listesinden de seçilebilir. Test alanı → KARAKTER açılır listesi → Karahan. Yeni karakter otomatik sahip olunanlar listesine eklenir; Bilge'nin seçimini ve kredileri değiştirmez. Bu belge için yeni model üretimi veya APK değişikliği yapılmadı.
