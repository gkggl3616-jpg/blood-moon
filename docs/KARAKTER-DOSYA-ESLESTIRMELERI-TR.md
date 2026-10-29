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
