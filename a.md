# Pedro — alınan native LTB dosyaları

Kayıt tarihi: 2026-10-28 (Europe/Istanbul).

Kullanıcıdan **36 LTB** alındı; tamamı indirildi, toplam **610,858 bayt**. Orijinaller değiştirilmeden `art/3d/source/pedro-native/` altında saklandı. Her dosyanın boyutu ve SHA-256 değeri aşağıda; ayrıntılı yerel manifest aynı klasörde `manifest.json`. Kaynak klasörü mevcut Git dışlama kuralı kapsamındadır; bu kayıt dosyaların dış servise yayımlandığı anlamına gelmez.

## Kullanıcının model ve varyant ayrımı

- Oyunda birden fazla Pedro sürümü var; insan ve kurt formları ayrı ele alınacak.
- Numaralı `01/02/03/04/05/06` dosyaları ile `deops` grubu otomatik olarak aynı karaktere atanmayacak. Varyant kimliği eşya/model kaydı veya kaynak bağlantısı ile doğrulanacak.
- `_wolf` taşıyan 6 dosya kurt ekipmanı adayı; `deops` taşıyan 6 dosya ayrı ekipman grubu adayı; kalan 24 dosyanın formu adından kesinleşmiyor.
- `_l` ve `_r` sol/sağ parça ayrımı korunacak. Eksik eşler otomatik üretilmiş veya tamamlanmış sayılmayacak.

## Dosya adlarından görülen kapsam ve açık işler

Bu yüklemenin isimleri çanta, gözlük, kask/şapka, maske, yelek, dirsek ve diz koruyucuları gösteriyor. Bunlar 36 ayrı tam karakter olarak sayılmıyor. Ana insan/kurt gövdesi bu dosyalar arasında henüz doğrulanmadı. Ekipman dosyasının da node, kemik veya hareket verisi taşıması mümkündür; yalnız adından tam iskelet/animasyon var veya yok sonucu çıkarılmadı.

**Yapıldı:** 36/36 indirme, değişmeden yerel kopya, boyut/SHA-256 kaydı, dosya adı üzerinden geçici parça sınıflandırması.

**Henüz yapılmadı:** LTB ayrıştırma, Blender mesh/armature importu, doku eşleştirme, kemik/skin/klip raporu, Pedro varyant eşleştirmesi, GLB dönüşümü veya oyun entegrasyonu. Bu yüklemede DTX dokusu gelmedi.

**Sonraki gerekli kontrol:** Ana Pedro insan ve kurt gövdelerini kaynak klasör/listeden saptamak; ilgili LTB ve bağlı DTX dosyalarını almak. `pedro.ltb`, `pedro_wolf.ltb` gibi adlar yalnız arama örnekleridir, mevcut arşiv yolu olarak doğrulanmış değildir. Kullanıcının eski rehberindeki sayılar/yollar bu dosyaların kanıtı sayılmaz.

## Envanter

| Dosya | Bayt | Adına göre parça | Geçici grup | SHA-256 |
|---|---:|---|---|---|
| `pedro_deops_elbow_r.ltb` | 10171 | Dirsek koruyucu | DEOPS ekipmanı adayı | `72be9a1a049d50d06fc7d75381d85323f4bad99f4ac9569bd2acd6962ce34bd8` |
| `pedro_bag01.ltb` | 7577 | Çanta | Pedro ekipmanı adayı; formu doğrulanmadı | `da7daa51d282902328c0a48c485745f12150b68ac8d75d9030685315ea2724a6` |
| `pedro_deops_goggle01.ltb` | 8755 | Gözlük | DEOPS ekipmanı adayı | `91dea2a0b11ece2968a88bf238c8b309d36d4a36169a20d3b9a39740fed1f7ad` |
| `pedro_bag02.ltb` | 9209 | Çanta | Pedro ekipmanı adayı; formu doğrulanmadı | `31f72f2d0952baad3c32aa7d25893b34c2ae8b61698e604487475c3690fb0f1e` |
| `pedro_deops_knee.ltb` | 10197 | Diz koruyucu | DEOPS ekipmanı adayı | `18ebb2c24dd72c436a8a538fa871150d1b7249ea3d7f3778a06cb5de0da42482` |
| `pedro_deops_helmet01.ltb` | 5863 | Kask | DEOPS ekipmanı adayı | `85bc623ce7dea9d60052051e8342528ee79d1af70fe054efe5d9cee259e8ec13` |
| `pedro_deops_mask01.ltb` | 6839 | Maske | DEOPS ekipmanı adayı | `a779471f42abb561f8dff6f5d50f475c11c2ff41c1a11b328e144c334c48f6d9` |
| `pedro_elbowprotector_wolf_l.ltb` | 7053 | Dirsek koruyucu | Kurt ekipmanı adayı (_wolf) | `7d2251c846dde91a72bcae39b8d8433ae7b638a4fa25e7de80461a384c56131f` |
| `pedro_elbowprotector_wolf_r.ltb` | 7053 | Dirsek koruyucu | Kurt ekipmanı adayı (_wolf) | `0ef5957a02fe13ddf7f0653364aeb201b0114a3a80d04fcfbf72db8756e735fc` |
| `pedro_deops_vest01.ltb` | 118397 | Yelek | DEOPS ekipmanı adayı | `4d974804cc5fc7909464c89ba95f96eded1b9e73b0cbe53edade415c3b7dfc3f` |
| `pedro_elbowprotector01_r.ltb` | 6846 | Dirsek koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `1a158a1f30b01cd9988f74ca60709cf2a2e85fe518b3f2f7bedef2b18decef21` |
| `pedro_elbowprotector03_r.ltb` | 5748 | Dirsek koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `991550c3cb65c4ec8a3fae4290a1813f472e9dd0316c19825b4fef3047e2d8a1` |
| `pedro_elbowprotector01_l.ltb` | 6846 | Dirsek koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `4d5c04bb45efc6b447900445ac2cf3cf7f7079550a6b635af083481a5a63aab9` |
| `pedro_elbowprotector04_l.ltb` | 7484 | Dirsek koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `c0b8ab0e2487a95361af5a15b82b217c4b5edf0aea6369a9a05f0cd80af73081` |
| `pedro_goggles01.ltb` | 2720 | Gözlük | Pedro ekipmanı adayı; formu doğrulanmadı | `b272d19c66f8ab465d8f8f2dab9d23dc785a79c3c612c18fe10a099ca6f6d5bc` |
| `pedro_elbowprotector05_l.ltb` | 7847 | Dirsek koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `a5b3f65b2f4bf602e143b73cecb7be79c22805f8b8fc8b7939c18a8c9ead30aa` |
| `pedro_elbowprotector05_r.ltb` | 7847 | Dirsek koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `822e00de9bde202bffbfaf489dc9ef2cc97c59932923c823ba049d7a31b21f6e` |
| `pedro_goggles02.ltb` | 5876 | Gözlük | Pedro ekipmanı adayı; formu doğrulanmadı | `b7ba9998b6db523ff66a77c12c85ec41111b1a419a481edd9ef5dcd2a54e359c` |
| `pedro_helmet01.ltb` | 7799 | Kask | Pedro ekipmanı adayı; formu doğrulanmadı | `83076f525c9f1d8a34226c93ad03d5df740dc2ff8023c48c7f24cb12d05d756f` |
| `pedro_goggles05.ltb` | 15730 | Gözlük | Pedro ekipmanı adayı; formu doğrulanmadı | `c0a5ae9ef5e97bd0a70c4d5cc76e86cd080b92007a3b3c415ce99bb4f696ba16` |
| `pedro_helmet_wolf.ltb` | 9002 | Kask | Kurt ekipmanı adayı (_wolf) | `bb6ed63be28f23db24d6885b2754f96f2a2576fdc44ff2b92db92534d95c0f08` |
| `pedro_helmet06.ltb` | 75711 | Kask | Pedro ekipmanı adayı; formu doğrulanmadı | `b9fbce9515e6af18b6b372cdbe780c98c971a0a9f5274fe8273a4d5879875b1a` |
| `pedro_helmet02.ltb` | 7303 | Kask | Pedro ekipmanı adayı; formu doğrulanmadı | `45459fad9722e63ddb382f9e0bb16749356dc962521ca49bde15d7aead3e6465` |
| `pedro_kneeprotector_wolf_l.ltb` | 9368 | Diz koruyucu | Kurt ekipmanı adayı (_wolf) | `7258ece9f848c92a3d63edff5009ee247b2ec2bae9452a22ab8888fdf77d4ad3` |
| `pedro_junglehat01.ltb` | 13668 | Şapka | Pedro ekipmanı adayı; formu doğrulanmadı | `bdac9e9488f3ab3996e51cbe2a97c468a6f5e290c43ff5adaab01d9378717ad3` |
| `pedro_junglehat04.ltb` | 14270 | Şapka | Pedro ekipmanı adayı; formu doğrulanmadı | `a2de89676459594818867c699ce42bf2cc5f522492cb69aa6e1c9d6e907ce66f` |
| `pedro_kneeprotector01_l.ltb` | 6409 | Diz koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `50ae1af2891073fd3d86874887866fb897903308cb917c63bc36bb81d6a02031` |
| `pedro_kneeprotector01_r.ltb` | 6409 | Diz koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `cae612c4cded0246e951e43552b14596ca016fa981e265aafaf4fdd8d0b00963` |
| `pedro_kneeprotector05_r.ltb` | 9010 | Diz koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `0c673aef149a42bb21051743120af0423608d5b4f919ecfa0fc5064063b1d10a` |
| `pedro_mask_wolf.ltb` | 9232 | Maske | Kurt ekipmanı adayı (_wolf) | `6e533af83d7412a74b326158df20f8bdf0912e383d4d26d2836e4e6c0366d0d4` |
| `pedro_kneeprotector05_l.ltb` | 9010 | Diz koruyucu | Pedro ekipmanı adayı; formu doğrulanmadı | `cebec0b0a4179bb958eb26b7df70d9aa4cdda77efbd0e3c20655f3de2577a032` |
| `pedro_vest_wolf.ltb` | 35216 | Yelek | Kurt ekipmanı adayı (_wolf) | `d0cdf7c561446b9cbaaab480b6e8a529e33491b75ed5165ddf9dd6a810d9b807` |
| `pedro_vest02.ltb` | 22698 | Yelek | Pedro ekipmanı adayı; formu doğrulanmadı | `3e721126ba54ad9cfd7740eb494838a53fed7d4b165510cf301cf343a1172b0b` |
| `pedro_vest01.ltb` | 8643 | Yelek | Pedro ekipmanı adayı; formu doğrulanmadı | `a629b9aab8fb4a85c213e7cdfaf2702dc4a4e69ea6a702ea94b73fc0b9dc1a27` |
| `pedro_vest05.ltb` | 92725 | Yelek | Pedro ekipmanı adayı; formu doğrulanmadı | `c1cd8301342a0533b8f151f535e1a79455a90537755f385fd9bf5b13fd85f9e5` |
| `pedro_vest03.ltb` | 16327 | Yelek | Pedro ekipmanı adayı; formu doğrulanmadı | `2d2eaf59eb7baa731b787db6d4ebd20eb26f85886b21acc8b608bae89ff3575a` |

## Koruma ve aktarım kuralları

XFS salt okunur kalacak; repack/yeni kayıt ekleme yok. Orijinal isimler ve model varyantları korunacak. İnsan/kurt formları ve ekipmanlar birbirinin üzerine yazılmayacak. Kaynak iskelet ve varsa özgün animasyonlar önce beraber denenecek; eski bozuk rig üzerine doğrudan uygulanmayacak. Model ve animasyon doğrulanmadan oyuna hazır kabul edilmeyecek.


## XFS Studio Pro videosunda görülen ana model adayları

2026-10-28 tarihli 60,496 saniyelik, 1920×992 ekran kaydı incelendi. Önce 3 saniye aralıklarla görüntüler, model listelerinin hızla geçtiği 16–32 saniye bölümü için ayrıca 0,5 saniye aralıklı görüntüler çıkarıldı. OCR'den sonra aşağıdaki önemli adlar görüntü üzerinde elle okundu. Bu, dosya içeriği/iskelet/animasyon doğrulaması değildir; dosyalar henüz alınmadı.

İlk inceleme için istenen üç LTB:

| Geçici rol | Videoda görülen tam yol | Görünen açılmış boyut | Kanıt |
|---|---|---:|---|
| Pedro insan ana gövde adayı | `Root\wt_chars\newchars\pedro_red\pedro.ltb` | 154.764 bayt | [Yaklaşık 26. saniye](docs/pedro-native-video/files-21.png) |
| Pedro kurt ana gövde adayı | `Root\wt_chars\newchars\pedro_wolf\pedro_wolf.ltb` | 246.086 bayt | [Yaklaşık 30. saniye](docs/pedro-native-video/files-28.png) |
| Aynı kurt klasöründeki ek LTB; içeriği incelenecek | `Root\wt_chars\newchars\pedro_wolf\wt_wolf_ch.ltb` | 1.649.151 bayt | [Aynı görüntü](docs/pedro-native-video/files-28.png) |

`wt_wolf_ch.ltb` boyutu veya adı tek başına animasyon içerdiğinin kanıtı değildir. Üç dosya mevcut rig/klip/bağlantılarla birlikte çözümlenecek. İnsan ve kurt adaylarının oyun içindeki aynı varyant çifti olduğu henüz model/eşya kaydıyla doğrulanmadı.

Diğer görülen seçenekler: `pedro_nano_wolf\pedro_nano_wolf.ltb`, `pedro_re\pedro_re.ltb`, `pedro_re_wolf\pedro_re_wolf.ltb`, `pedro_action\pedro_action.ltb`, `pedro_christmas\pedro_christmas.ltb`, `pedro_soccer\pedro_soccer.ltb`. Bunlar `Root\wt_chars\newchars\` altında farklı varyant adayları; şimdilik birbirine karıştırılmayacak. Örnek [RE insan modeli görüntüsü](docs/pedro-native-video/files-16.png).

Doku ayrımı: `Root\wt_interface\item\character\...` ve `killsystemmessage` kayıtları arayüz/kart/mesaj görseli adaylarıdır; model kaplaması diye eşlenmez. Öncelik seçilen modelin `wt_chars\newchars\...` klasöründeki DTX'ler ve ekipmanlar için `wt_charparts\skins\...` dosyalarıdır. Videoda `pedro_nano_wolf_fur.dtx`, `pedro_re_body.dtx`, `pedro_re_head.dtx` gibi model dokuları da görülüyor. Tam doku eşleştirmesi LTB içeriğiyle kontrol edilecek.

Kullanıcı işlemi: arama kutusuna üç dosya adını sırayla yaz → tam yolu doğrula → kaydı seç → üstteki `Seçili Dışa Aktar` → çıkan LTB'yi yükle. Bu videonun alınması önceki 36 ekipman dosyasının tamamlanmış karakter olduğu anlamına gelmez.

## Üç ana LTB alındı ve ayrıştırıldı — 2026-10-28

Dosyalar indirildi; orijinaller değiştirilmeden `art/3d/source/pedro-native/main/` altında saklandı. Native PC LTB okuyucusuyla (MelissaAutumn/io_scene_lithtech, commit `495372d59d00e019a7143c961d94f05df2cc5c72`) üçü de v25 olarak ayrıştırıldı. Aşağıdaki sayılar artık dosya içeriğinden ölçülüdür.

| Dosya | Bayt | İskelet düğümü | Üçgen (mevcut LOD) | Klip | SHA-256 |
|---|---:|---:|---:|---|---|
| `pedro.ltb` | 154764 | 47 | 3204 | Yalnız tek karelik @figure | `ef1111e1bf1804da63de457551ff48a13882dcd34e71e1d0924fd6130b34535a` |
| `pedro_wolf.ltb` | 246086 | 42 | 4244 | Yalnız tek karelik @figure | `9f27a26f19d5174523e1c9a273afd5d23bc6b837d360992c5d3419f797698c2b` |
| `wt_wolf_ch.ltb` | 2016341 | 42 | 4616 | 70 | `e86bf17b460b0654c2e3893087014412808caa2e3c3227046aecbc19d099a441` |

**Gerçek bağlantılar:** `pedro.ltb` → `..\..\Models\WT_NEW_MAN_CH.ltb`; `pedro_wolf.ltb` → `..\..\Models\WT_NEW_WOLF_CH.ltb`. Bu iki dosya henüz gelmedi. `wt_wolf_ch.ltb` 42 düğümlü ve 70 klipli farklı bir kaynak olarak korunuyor; beklenen `WT_NEW_WOLF_CH.ltb` ile aynı olduğu varsayılmıyor. Gelen `wt_wolf_ch.ltb` boyutu 2.016.341 bayt; videoda görünen 1.649.151 bayttan farklı. Kaynak/sürüm uyumluluğu kontrol edilmeli.

**Blender sonucu:** Üç model de kendi armature ve skin gruplarıyla içe aktarıldı. `pedro.blend` (47 kemik), `pedro_wolf.blend` (42 kemik), `wt_wolf_ch.blend` (42 kemik, 70 Action) kaynak çalışma klasörüne kaydedildi. Tüm Action kayıtları Blender dosyası kapatılınca kaybolmamaları için fake-user ile korundu. Model aynalama, bind/rest matrisleri, kliplerin görsel doğruluğu ve başka gövdeye uyarlaması henüz onaylanmadı. DTX dokuları henüz yok; oyun entegrasyonu ve yeni APK yapılmadı.

**İçe aktarıcı UV düzeltmesi:** Pedro kurtta materyal indeksleri 10/14/18 bulundu. Upstream importer her materyal için UV katmanı oluşturup materyal indeksiyle katman seçiyordu; Blender katman sınırı bu düzeni karşılamıyor. Yerel kopya her mesh için tek UV katmanı kullanacak, materyal slotlarını ve yüz köşesi UV verisini ayrı koruyacak şekilde düzeltildi. Patch: [lithtech-uv.patch](docs/pedro-native-video/lithtech-uv.patch). Kaynak LTB değiştirilmedi; vertex birleştirme devre dışı bırakıldı.

**Klipler:** `T_CRY` 22 kaynak kare / 1.333 ms; `LRF` 17 kare / 733 ms; `LWF` 20 kare / 933 ms; `T_Bodyatk`, `T_BodyatkL`, `T_BodyatkR` 28 kare / 900 ms. İsimlere göre kükreme/koşu/yürüme/saldırı adayıdırlar; görsel inceleme yapılmadan kesin hareket eşlemesi sayılmaz. Bütün 70 klibin süreleri, kemik hiyerarşileri, parçalar, socket ve child-model bağlantıları [ltb-inspection.json](docs/pedro-native-video/ltb-inspection.json) içinde. Blender veri raporu: [blender-import-report.json](docs/pedro-native-video/blender-import-report.json).

**Sonraki gerekli girdiler:** arşivde `WT_NEW_WOLF_CH.ltb` ve `WT_NEW_MAN_CH.ltb` aranıp dışarı alınmalı. Doku eşleştirmesi için karakter DTX dosyaları ve mümkünse modellerin texture slot eşlemesini tutan `ModelButes.txt` kaydı gerekli. Anahtar/hesap bilgisi veya tüm XFS istenmez.

### Gelen wt_wolf_ch.ltb içindeki klip listesi

| Native ad | Kaynak kare | Süre (ms) |
|---|---:|---:|
| `LSt` | 12 | 866 |
| `LC` | 12 | 866 |
| `LCWR` | 20 | 1266 |
| `LCWB` | 27 | 1400 |
| `LCWF` | 24 | 1400 |
| `LCWL` | 22 | 1266 |
| `LCWFR` | 24 | 1400 |
| `LCWFL` | 24 | 1400 |
| `LCWBL` | 27 | 1400 |
| `LCWBR` | 27 | 1400 |
| `LJJ` | 5 | 133 |
| `LJL` | 9 | 366 |
| `LJT` | 3 | 67 |
| `LRF` | 17 | 733 |
| `LRR` | 23 | 733 |
| `LRL` | 23 | 733 |
| `LRFR` | 17 | 733 |
| `LRFL` | 17 | 733 |
| `LWR` | 18 | 733 |
| `LWB` | 24 | 933 |
| `LWF` | 20 | 933 |
| `LWL` | 14 | 733 |
| `LWFR` | 20 | 933 |
| `LWFL` | 21 | 933 |
| `LWBL` | 24 | 933 |
| `LWBR` | 24 | 933 |
| `UMC` | 12 | 866 |
| `UMJJ` | 5 | 133 |
| `UMJL` | 9 | 366 |
| `UMJT` | 3 | 67 |
| `UMRF` | 23 | 733 |
| `UMRR` | 23 | 733 |
| `UMRL` | 22 | 733 |
| `UMWR` | 18 | 733 |
| `UMWF` | 20 | 933 |
| `UMWB` | 24 | 933 |
| `UMWL` | 14 | 733 |
| `UMCWR` | 20 | 1266 |
| `UMCWB` | 27 | 1400 |
| `UMCWF` | 24 | 1400 |
| `UMCWL` | 22 | 1266 |
| `UMSt` | 12 | 866 |
| `UMTr` | 3 | 733 |
| `T_WallRide` | 13 | 533 |
| `T_wallRide2` | 27 | 866 |
| `T_DFHS1` | 54 | 2733 |
| `T_DFBS1` | 36 | 1866 |
| `T_DFBB1` | 19 | 967 |
| `Twitch` | 5 | 166 |
| `T_DBBS1` | 41 | 1900 |
| `T_DBBB1` | 20 | 1000 |
| `T_DBHS1` | 35 | 2133 |
| `T_CRY` | 22 | 1333 |
| `T_BITE` | 17 | 1166 |
| `T_DFBF1` | 32 | 1033 |
| `T_DBBF1` | 38 | 1233 |
| `LJA` | 18 | 1200 |
| `UMFi3` | 14 | 600 |
| `UMFi2` | 10 | 400 |
| `UMFi1` | 10 | 333 |
| `Ui_idle` | 41 | 1333 |
| `T_Specialatk` | 31 | 1000 |
| `T_Bodyatk` | 28 | 900 |
| `T_BodyatkL` | 28 | 900 |
| `T_BodyatkR` | 28 | 900 |
| `T_WallDash` | 17 | 533 |
| `T_WallDashL` | 17 | 533 |
| `T_WallDashR` | 17 | 533 |
| `UMDe` | 41 | 1333 |
| `T_WallDashAtk` | 34 | 900 |

## Ayrı XFS masaüstü aracı başlatıldı

Kullanıcının filtreleme ve donma sorununu çözme isteğiyle `desktop/xfs_browser/` altında salt okunur bir XFS tarayıcısı geliştirildi. Uzantı/ad/yol filtresi, sayfalama, çoklu seçim, arka planda çıkarma, iptal, metin/hex ve CSV var. Kaynak arşiv değiştirilmez. 3B önizleme ve repack yok; gerçek kullanıcı XFS paketiyle henüz denenmedi. Ayrıntılı yapılan/test edilen/açık iş kaydı: [docs/xfs-browser/README.md](docs/xfs-browser/README.md). Bu araç çalışması Pedro'nun oyun entegrasyonunun tamamlandığı anlamına gelmez.

## İstenen yeni hareket paketleri alındı — 2026-10-28

İki native PC LTB v25 dosyası indirildi ve içerikleri ayrıştırıldı. Bunlar yürütülebilir kod değil, model/iskelet/hareket verisi paketleridir. Kaynaklar değiştirilmeden `art/3d/source/pedro-native/new-motion/` altında saklanıyor.

| Dosya | Bayt | Düğüm | Klip | SHA-256 |
|---|---:|---:|---:|---|
| `wt_new_wolf_ch.ltb` | 2088235 | 42 | 72 | `c06e7e9347968a1987126450bdb7ba3d37353ac97c414ace261bfca9873bbfc4` |
| `wt_new_man_ch.ltb` | 20579112 | 47 | 569 | `f026978087746f5b44df7cf90a8927a189d2596f2660e01f369518a209fbd950` |

### Uyum sonucu

- Kurt: 42 düğümün isimleri ve parent hiyerarşisi Pedro kurt gövdesiyle eşleşti. En büyük bind-matris eleman farkı yaklaşık 0,000403 kaynak birimi.
- İnsan: 47 düğümün isimleri ve parent hiyerarşisi eşleşti; bind pozu birebir aynı değil (en büyük eleman farkı 6,31433 kaynak birimi). Doğrudan farklı rest-poza klip bağlamak yerine rest farkına göre dönüşüm yapılıyor; segment uzunlukları korunuyor.
- Kaynak `Upper` ve `Lower` ağırlık setleri ayrı. Yürüme/koşuda yalnız alt veya yalnız üst gövde klibini kullanmak yerine iki katman birleştiriliyor.
- Kurt paketindeki 72 klip, önceki `wt_wolf_ch.ltb` dosyasındaki 70 kliple aynı paket olarak sayılmıyor. Gerçek model bağı bu yeni dosyayı gösteriyor.
- Kaynakların tamamı ve klip isim/süreleri [new-motion-inspection.json](docs/pedro-native-video/new-motion-inspection.json); karşılaştırma [native-compatibility.json](docs/pedro-native-video/native-compatibility.json) içinde.

### Tasarım ve uygulama çalışması

Mevcut onaylı koyu gri, kamuflaj pantolonlu kurt görünüşü ve mevcut dokulu insan tasarımının görünüşü, native iskeletlere uyarlanıyor. Ortak turkuaz/bronz bileklikler ve kemer mührü ekleniyor. Yeni ücretli üretim yapılmadı. Bu bir sıfırdan yeni ücretli model üretimi değil; eldeki dokulu geometri ve native hareketlerden türetilen uyarlamadır.

İlk testte hatalı kök yönü ve Blender edit-bone matrisinin sıfır uzunlukta kemiğe atanması nedeniyle poz bozulması görüldü; kemik önce sıfır olmayan uzunlukla oluşturulup native bind matrisinin korunduğu assert ile denetleniyor. Native kliplerin oynama yönü 180° sabit kalibrasyonla oyun ileri yönüne hizalanıyor. Kesirli son karelerin dışa aktarımda kırpılmaması için klip süresi üst tam kareye taşınıyor ve kaynak son poz korunuyor.

İlk insan denemesinde uzun etek panelinin bacağa bağlanması kötü deformasyon verdi. Bu deneme kabul edilmedi. İnsan gövdesi native topoloji/orijinal ağırlıklarla yeniden kurulup mevcut görünüş seçili-kaynak → hedef UV aktarımıyla 2K renk/normal/pürüzlülük haritalarına taşınıyor. Modelin görünüşü ve bütün klipleri henüz onaylanmış değildir.

Yeni çalışma dosyaları: `art/3d/native-pair/guardian-wolf.blend`, `.glb`, `guardian-human.blend`, `.glb`. Yapım raporu `art/3d/native-pair/build-report.json`. Başlangıç çalışma raporu: kurt 14.865, insan 3.256 üçgen; 42/47 kemik. Aktarım mesafeleri ve kalibrasyonlar teknik kontrol verisidir; sanat kalitesi onayı değildir.

**Açık işler:** yeni dosyaların son görsel kontrolü, koşu/takla/pençe/jump eşlemelerinin bütün döngüsü, ayak teması, ağırlık deformasyonu, runtime testleri, oyuna entegrasyon ve kullanıcıya son varlık dosyalarının teslimi. `WolfTransform` çalışma klibi henüz gerçek insan-kurt morph animasyonu değil, dönüşüm sırasında kullanılan bekleme pozu yer tutucusudur. `HumanFire` ve `HumanReload` üst/alt gövde denemeleri gerçek silah modeliyle henüz eşlenmedi.

## Native çift denemesi — son kontrol, 28 Ekim 2026

**Yapıldı:** 42 kemikli / 14.865 üçgen kurt ve 47 kemikli / 3.926 üçgen insan üretildi; GLB ve dokuları paketlenmiş BLEND dosyaları hazırlandı. Kurtun UV dikişlerinde aynı konumdaki vertex ağırlıkları birleştirildi, komşuluk boyunca 18 geçiş yumuşatıldı ve en fazla 4 etki korundu. Dirsek gerilmesi azaldı; tamamen çözülmüş kabul edilmedi. İnsan native gövde topolojisi ve ağırlıkları korunup mevcut Bilge görünüşü 2K PBR haritalarına aktarıldı; dokulu baş ayrı korunuyor. Beklemede zemin hizası düzeltildi. Ücretli üretim yok.

**Önemli eşleme düzeltmesi:** Görsel inceleme LRF+UMRF'nin iki ayaklı koşu olduğunu, T_Bodyatk'nin de tam takla olmadığını gösterdi. Önceki çalışma isimleri yanlıştı. Gerçek isimler artık `WolfRunNative` ve `WolfBodyAttack`. Bu hareketleri dört ayak koşu/takla diye sunmuyoruz. Doğru animasyon kaynakları henüz bulunmadı. Bu iki hareket yeni çiftin oynanışında kapalı; varsayılan eski modellerin koşu/taklası değişmedi.

**Oyuna ekleme:** Envanterde `YENİ ÇİFT · DENEME` seçeneği `?nativePair=1` açar. Bilge Kağan seçildiğinde yalnız model kaynağı yeni çifte yönlendirilir. Menü ve arena aynı GLB'yi kullanır. Eski modele dönme düğmesi vardır. Sahiplik, kredi, ekipman şeması ve varsayılan modeller korunur. Bu değişiklik sanat kalitesi tamamlandı anlamına gelmez.

**Test edildi:** Gerçek WebGL oyun motorunda yeni kurt ve insanın yüklenmesi, 1,333333 saniyelik T_CRY kükremesi, 2 ele bağlı alev parçacıkları, sağ/sol pençe sırası ve hazır olmayan koşu/taklanın reddi geçti; sayfa JS hatası yok. İskelette ağırlıksız gövde vertex'i yok, örneklenen koordinatlar sonlu. İki mevcut pençe/yürüyüş sözleşme testi geçti. Rapor: `docs/native-pair-review/runtime-check.json`.

**Kalite testi sonucu / açık işler:** `geometry-check.json` 9 faz örnekli ölçümüdür. En az 0,45 native birim uzunluğundaki kenarlar değerlendirilir; kurtun anlamlı kenarlarında P99 gerilme hâlâ klibe göre yaklaşık 1,64–2,42 kat, insanda 1,48–2,31 kat. Bunlar kalite geçişi değildir. Bazı kliplerde ara kare zemin sapması 1–7 cm kalıyor; sıçrama pozunun kaynak eşlemesi ayrıca incelenmeli. Parmak/dirsek/omuz skin ince ayarı, bağımsız çene/ağız içi hareketi, insan doku dikişleri, silahla ateş/doldurma uyumu ve gerçek dört ayak koşu/takla açık. `WolfTransform` gerçek morph değil. Adım mesafesi metadatası 3,6/8 m/sn başlangıç temposuna göre kurulmuştur; yer temasıyla ölçülmüş stride değildir. Telefon FPS/çökmezlik garantisi verilmedi.

**Teslim biçimi:** Yeni çift deneme APK'sının tüm GLB/dokuları APK içinde; model düzenleme için ayrıca GLB/BLEND paketi verilir, APK kurulumu bu pakete bağlı değildir. v0.1.15 / sürüm kodu 16 için eski yayımlanan sertifika SHA-256 kontrolü CI içinde zorunlu. Yayın bağlantısı ve CI sonucu doğrulandıktan sonra bu kayda eklenir.

### Yeni XFS arama videosu — 58,6 saniye

`20261028-1657-23.0142458.mp4` (918×618, 18.569.538 bayt) alındı. 5 saniye aralıkla 12 kare çıkarılıp OCR ve görüntüyle kontrol edildi; bu aralıklı örnekleme hızla geçen her dosyanın tespit edildiği iddiası değildir. Kareler `docs/native-pair-review/search-video/` altında.

İlk bölüm `wt_interface/item/...special...` DTX kartları; yaklaşık 27,5 saniye `cherokee_axe_runes` balta UI/PV/HH LTB ve dokuları; yaklaşık 32,5 saniye `Root/wt_attributes/wolfvars.dat`, `aiwolfdata.dat`, `wolfsound.dat`, `wolfparts.dat`; sonra harita/path ve `wt_charparts/models` ekipmanları, pençe LTA/LTB ve ekipman DTX'leri görünüyor. Bu kayıtta gerçek dört ayak koşu/takla dosyası doğrulanmadı. Balta modeli veya özel paket kartı animasyon diye içe aktarılmayacak. Kullanıcıdan boş ad filtresi + `.ltb` uzantısı ile `Filtre Listesini CSV Kaydet` çıktısı istendi; tüm XFS'yi yüklemesi gerekmiyor.

## Yayımlanan deneme dosyaları ve aktarım engeli

- Android CI `40732213876` başarılı: arayüz, düz arena, mevcut referans hareket testleri, tek APK derleme ve imza doğrulaması geçti.
- APK: https://github.com/gkggl3616-jpg/blood-moon/releases/download/prototype-v0.1.15-21/Rogue-Blood-Moon-v0.1.15.apk
- Model GLB + düzenlenebilir BLEND paketi: https://github.com/gkggl3616-jpg/blood-moon/releases/download/native-pair-preview-01/Bilge-Native-Cift-DENEME.zip
- Yayımlanan arşiv ve APK tekrar indirildi. Arşiv içindeki SHA-256 değerleri, APK CRC'si, yeni GLB'lerin paketle byte eşitliği ve eski yayımlanan sertifika kontrol edildi. Ayrıntı `docs/native-pair-review/delivery.json`. Fiziksel telefon testi yapılmadı. Sanat/animasyon açık işleri önceki bölümdeki gibi duruyor.

Kullanıcının `wt models, wt charts ,models.rar` dosyası (`file_000000009eac820aa20a3e4c2cdaa8e6`) alıntısı geldi. İndirme aracı **file exceeds the executor transfer limit of 32 MiB** hatası verdi. Yerel çalışma alanında bu arşivin kopyası bulunmadı; dolayısıyla içindekiler henüz listelenemedi veya doğrulanamadı. Kullanıcıdan indirmeye açık bağlantı veya 30 MB WinRAR ciltleri istendi. Eksiksiz arşiv gelince ana gövde/hareket/doku ayrımı, native klip adaylarının incelenmesi ve doğru dört ayak koşu/takla eşlemesi sürdürülecek. Arşiv adı tüm ihtiyaçların bulunduğunun teknik doğrulaması sayılmadı.

### Drive bağlantısı ve seçici içe aktarım kararı

Kullanıcı aynı arşivi `https://drive.google.com/file/d/1feaeVe0-F5OkB130x3jM631UmWOYfRMD/view` ile paylaştı. Genel Drive ve doğrudan usercontent indirme denemeleri oturum açma sayfasına yönlendi; view isteği 401 verdi. Son yeniden denemede de RAR yerine `Google Drive: Sign-in` HTML'i döndü. Arşiv henüz indirilmedi, içeriği listelenmedi.

Kullanıcı yalnız gerekli varlıkların alınmasını istedi. Erişim açılınca önce arşiv dizini listelenecek; uygun birkaç kurt iskeleti, karşılık gelen gövdeler, gerekli hareket paketleri ve yalnız bağlı dokular seçilecek. Kurt geometri oranlarına göre iskelet uyumu karşılaştırılacak. Bütün arşiv oyuna veya APK'ya eklenmeyecek. Paket listesi ve seçilen/reddedilen dosya gerekçeleri kaydedilecek. Şu aşamada hangi ek iskeletlerin bulunduğu doğrulanmış değildir.

## Drive erişimi açıldı — seçici arşiv incelemesi

Son `usp=sharing` bağlantısında indirme başarılı oldu. RAR5 imzası doğrulandı; arşiv **133.326.447 bayt**. SHA-256 ve tam dizin listesi `docs/native-pair-review/archive-index.json` içinde. 974 kayıt: **553 LTB dosyası ve 421 dizin**; bu arşivde DTX dosyası yok. İçeriğin açılmış toplam boyutu 469.570.615 bayt. Yalnız seçilen **13 dosya / 23.296.957 bayt** `art/3d/source/wolfteam-archive/selected/` altına çıkarıldı; geri kalan dosyalar oyuna aktarılmadı. Ham RAR ve seçili kaynaklar Git dışında tutuluyor.

### Seçilen ve karşılaştırılan kaynaklar

Manifest: `archive-selection.json`; tam geometri/iskelet/klip raporu: `archive-rig-inspection.json`; mevcut Pedro ile isim/parent/bind karşılaştırması: `archive-rig-comparison.json` (üçü de `docs/native-pair-review/` altında).

| Grup | Kemik | Sonuç |
|---|---:|---|
| `wt_wolf_r`, `wt_wolf_ch`, `wt_wolf_power_r`, `wt_wolf_power_ch` | 42 | Pedro ile 42 ortak düğüm ve aynı parent yapısı; paylaşılan bind matrisi farkı raporda yaklaşık sıfır. İlk uyarlama için tercih. |
| Ice, Guardian | 40 | 40 ortak düğüm; bind pozları farklı. İlgili gövde ve kendi klibi birlikte değerlendirilmeli. |
| Smart | 40 | Daha büyük bind-pozu farkı; mevcut gövdeye doğrudan takılmayacak. |
| R1, Hacker | 54 | Yalnız 39 ortak isim ve farklı parent ilişkileri. Ayrı retarget gerekir. |
| Wraith | 58 | 38 ortak isim ve farklı parent ilişkileri; ek kemikler nedeniyle doğrudan rig değişimi kabul edilmedi. |

Kaynak poz incelemeleri dokusuz teşhis render'larıdır; bitmiş karakter tasarımı değildir. `motion-candidates/` karelerinde Wraith `LRF2/UMRF2` dahil koşu adayları örneklendi. İkinci set de dört ayak koşu olarak doğrulanmadı. `T_Specialatk` hareketinde havada dönüş görülüyor; yalnız isminden veya birkaç pozdan hedeflenen kısa takla kabul edilmedi. `T_Bodyatk` hâlâ tam takla olarak doğrulanmış değil. Hazır olmayan eşlemeler oyuna eklendi diye sunulmuyor.

### Kullanıcının yeni aktarım tercihi

Kullanıcı tüm oyun veya tüm LTB/DTX'leri gönderebileceğini belirtti. Gerekli uzantı **LTB** olarak açıklandı. Mevcut 553 LTB'nin yeniden yüklenmesi istenmedi; öncelik ilgili insan/kurt modellerinin DTX dokuları ve varsa ModelButes gibi model–doku eşleştirme kayıtları. Klasör yapısı korunacak; gereksiz tüm oyun dosyaları alınmayacak. Doku slotları LTB içinde sayısal; yalnız bu slotlardan kesin DTX dosya yolu çıkarılamıyor. Doğru kaplama eşlemesi için doku/kayıt incelemesi açık. Mevcut oyun modelleri bu arşiv incelemesi sırasında değiştirilmedi.

## Güncel LTB + DTX arşivi alındı — 28 Ekim 2026

Aynı Drive kimliğindeki dosya güncellendi. Son arşiv **2.145.027.885 bayt**, SHA-256 **769306e95c928eee7623085ca7f27234b97b2e0cc503c50a0d21a0d93ca50394**. İlk indirme 60 saniye sınırında 1.951.580.160 baytta kaldı; HTTP Range ile kalan bölüm tamamlandı ve beklenen toplam boyut doğrulandı. RAR5 dizini sonuna kadar hatasız okundu. Bu, çıkarılmayan bütün dosyaların CRC kontrolü yapıldı anlamına gelmez.

`updated-archive-index.json`: 37.892 kayıt, **36.879 dosya: 3.255 LTB + 33.624 DTX**, 1.013 dizin. Açılmış toplam boyut 8.723.184.832 bayt. Arşivin tamamı APK'ya veya çalışma klasörüne açılmadı. Bazı girdiler `wolfteam kurtları/Root/wt_guns/` altında silah dosyaları; yalnız üst klasör adındaki “wolf” nedeniyle kurt animasyonu sayılmadı.

### Seçici doku aktarımı

Önceki 13 LTB/23.296.957 bayt adayına ek olarak **17 DTX / 3.013.348 bayt** çıkarıldı. Klasör yapısı korundu, her dosyanın SHA-256 değeri `texture-selection.json` içinde.

- Pedro kurt üst/alt/kürk için 3 gerçek model atlası.
- Pedro insan üst/baş, alt, eldiven01 ve bot01 için 4 atlas. Baş UV'si üst gövde atlasında bulunuyor; ayrı baş dokusu icat edilmedi. Bot/eldiven varyantının kesin oyun kayıt bağı bu pakette ModelButes olmadığı için ayrıca doğrulanmış değil; 01 başlangıç adayı.
- Standart/Power/Ice/Guardian/Smart karşılaştırmaları için 6 doku adayı. `helmet.dtx` yalnız eşleme adayı; özgün ekipman bağı kesinleşmiş sayılmadı.
- Mor el alevi, mor pençe izi, çizik izi ve önkol parlaması için 4 efekt dokusu adayı. Dosya adının eşleşmesi, videodaki efekt zamanlamasının birebir çözüldüğü anlamına gelmez.

17/17 DTX, v-5 başlığı doğrulanarak DXT3/DXT5'ten PNG'ye çözüldü. Alfa kanalı korundu; örneğin 512×128 izler ve 256×128 omuz dokusu kareye çevrilmedi. Çözüm raporu/piksel hash'leri `texture-decode.json`. Kaynak DTX'ler değiştirilmedi. Araç: `tools/decode_selected_dtx.py`.

### Gerçek gövdede UV kontrolü

Özgün LTB geometri, UV, iskelet ve deri ağırlıkları korunarak dokulu Pedro insan/kurt referansları hazırlandı. Modellerde uydurma kabartma/normal dokusu kullanılmadı; özgün renk atlasları ve sabit pürüzlülük var. Kuşanılmamış dövme yüzeyleri referansta gizli: kurt **3.876 üçgen / 42 kemik**, insan **3.204 üçgen / 47 kemik**. Bu sayılar önceki özel Guardian tasarımının 14.865/3.926 üçgen sayılarıyla karıştırılmayacak.

Ön/yan/arka GLB yeniden içe aktarım render'ları `docs/native-pair-review/textured-reference/` içinde. Üst/alt/kürk, insan yüz/gövde ve el/ayak UV eşleşmesi görsel olarak kontrol edildi. Kaynak pozu/floor kalibrasyonu ve saç/yelenin tek yüzlü yüzeyleri hâlâ inceleme konusu; özellikle insan referansında zeminden ayrılma görülüyor. Referans yalnız tek başlangıç bekleme pozu taşır; tamamlanmış yürüyüş, koşu, takla veya kükreme paketi değildir.

Yerel çalışma dosyaları `art/3d/source/wolfteam-archive/textured-references/{wolf,human}.{blend,glb}` altında; dokular dosyalara gömülü. Ham RAR/LTB/DTX ve kaynak referans dosyaları Git dışında. Yapım/eşleme raporu `textured-native-reference.json`. Bu turda oyun çalışma zamanı modeli değiştirilmedi ve yeni APK yayımlanmadı. Yeni ücretli üretim yok. Kullanıcıdan bu aşama için tekrar aynı kaynakların yüklenmesi istenmiyor.

## Kullanıcının yeni kararı: 4 karakter / 4 farklı kurt iskeleti, animasyonlar kilitli

Bilge Kağan → Ice 40; Kül Tigin → R1 54; Alp Arslan → Power 42; Konuralp → Wraith 58 seçildi. R1'in ek kol burulma ve boyun kemikleri, Wraith'in kuyruk zinciri tasarımda korunacak. Dört kaynak hiyerarşisinin SHA-256 imzası farklı. Ayrıntılı tablo ve karakter/insan eşi tasarım briefleri: `docs/four-character-rigs/TASARIM-VE-ISKELET-PLANI-TR.md`.

**Son kullanıcı talimatı önceki hareket işlerinin önüne geçer: şu aşamada animasyonlara kesinlikle dokunulmaz.** Yeni keyframe/retarget/klip kesme veya hız değişikliği yapılmayacak. Statik tasarım ve gövde/kostüm, kaynak bind hiyerarşisi ve eklem oranlarına göre yapılacak. Kaynaklar silinmeyecek. `selection.json` içinde seçili gövde ve hareket kaynaklarının hash'leri donduruldu. Bu karar dört insan iskeletinin de birbirinden farklı seçildiği anlamına gelmez; dört ayrı iskelet seçimi burada kurt formları içindir. Dört insan eşinde karakter kimliği aynı briefte planlandı.

Bu tur oyun hareket kodu ve klipleri değiştirilmedi; ücretli üretim yapılmadı. Yeni karakter tasarımları tamamlandı diye sunulmadı.

Dört kaynak gövdenin statik nötr poz görüntüleri hazırlandı; kemik/mesh grupları orijinal isimlerle referans BLEND dosyalarına alındı. Hiçbir animation action oluşturulmadı. İşlem sonunda seçili altı benzersiz kaynak dosyanın SHA-256 değeri başlangıçla birebir eşleşti (`docs/four-character-rigs/preview-check.json`). Bu tur `app/` çalışma zamanı dosyalarında değişiklik yapılmadı. Görüntüler nihai karakter tasarımı olarak sunulmaz.

## Özgün tasarım şartı ve model bazında kükreme

Kullanıcı kaynak iskelet/kemik sayısı/animasyonların korunmasını, buna karşılık Wolfteam görünüşü ve DTX giysilerinin kopyalanmamasını istedi. Karakter DTX'leri **reference-only**: yeni giysiye bake/kaplama yapılmaz, kaynak giysi mesh'i yeni model olarak sunulmaz. `art/characters/original-roster/asset-policy.json` ve dört model planı bu kuralla güncellendi.

Dört kurt + dört insan eşi için `design-board-v1.png` özgün konsept paftası oluşturuldu; kaynak DTX'ler görsel üretimine verilmedi. İlk üç modelin iskeletinde olmayan konsept kuyrukları düzeltildi; yalnız Wraith/Konuralp kuyruğu kalır. Bu 2B konsepttir; gerçek 3B karakter üretimi/skin/oyun entegrasyonu tamamlandı iddiası değildir. Ana kadro dört; kullanıcının verdiği 6–7'ye çıkma izni zorunlu yeni model üretimi sayılmadı.

**Kükreme karakter başına değil model türüne göre ayrılır.** `T_CRY` kaynakları doğrudan okunup olaylar ve hareket verisi hash'lendi: Ice40 1933 ms/23 anahtar, R1_54 1500 ms/46, Power42/WT_NEW 1333 ms/41, Wraith58 1500 ms/55. Native efekt olayları sırasıyla 933, 500, 633 ve 1111 ms'de kaydedildi. Ham metinler asset verisidir, çalıştırılmadı. Aynı model türünü kullanan karakterler aynı kükremeyi paylaşır; bütün model türleri tek klibe zorlanmaz. Kaynak klip ve iskeletlere dokunulmadı. Kükreme efektinin önceki tam video referansı ve el alevi/dövme/sönme aşamaları korunacak; yeni zaman eşlemesi henüz oyuna bağlanmadı.

Mevcut oyun GLB'lerindeki 23 görüntü, seçili 13 karakter DTX atlasının piksel hash'iyle kontrol edildi; eşleşme bulunmadı. Test yalnız seçili atlasları kapsar. Yeni Meshy ücretli işi başlatılmadı; ücretsiz CLI planlayıcısı 30 kredi/model tahmini verdi, bakiye OAuth süresi dolduğu için doğrulanamadı. Yeni maliyet onayı olmadan yeniden üretim yapılmayacak. Üretim sahnesine source giysi sokulmadı, bu tur APK değiştirilmedi.


## 29 Ekim — Bilge özgün çift entegrasyonu / sürüm kalite kapısı

60 yeni kredi onaylandı; iki özgün geometrinin gerçekleşen maliyeti toplam 30 kredi oldu. Üretim görevleri ve kaynak hash'leri `art/characters/bilge-original/production.json` içinde. Kaynak kıyafet dokuları yeni üretimde kullanılmadı. Yeni ücretli animasyon/rig yapılmadı.

Ice40 kurt / Human47 insan GLB'leri Bilge model yollarına eklendi. Kaynak kemik ve animasyon anahtarları korunarak format dönüşümü yapıldı. Kükreme 1933 ms, efekt olayı 933 ms; kısa takla klibi 1000 ms. Ağız/diş, üç ayrı skin dövme yüzeyi ve ele bağlı pençe izi eklendi. Eski opt-in düğmesi kaldırıldı. Ayrıntı ve açık işler `docs/bilge-original-complete/DURUM-TR.md` dosyasında.

İlk WebGL testi: gerçek koşu 8.400000000000064 m/sn (8 temel +%5 donanım), kısa takla 2.0125786163522097 m, kükremede ileri basılıyken durma, 1.933 sn kükreme ve 0.933 sn kaynak efekt olayı geçti. Envanter testi dokunma/fare, +%240 bağımsız bonus, kayıt/preset, satın alma ve silah oynanışını geçti. Test kayıtları ilgili dizinde. Geniş arena testinin ilk çalışması havada takla/iniş beklemesinde zaman aşımına uğradı; tek başına tekrar kontrol ediliyor. Son geometri değişikliklerinden sonra kontroller yeniden geçmeli.

Kıyafet/kol deformasyonu ve zemine temas kalite kapıları sürüyor. Yeni APK henüz yayımlanmadı; cihaz performansı/kurulum/imza doğrulaması henüz yapılmadı. Bu kayıt tamamlandı beyanı değildir. Dört genel model tipinden yalnız Bilge'nin yeni özgün çiftinin entegrasyonu üzerinde çalışıldı. Kaynak Ice40 koşusu iki ayaklıdır; dört ayak koşu tamamlandı denmez.

Son durum: geniş arena testi tek başına PASS; önceki havada takla/iniş zaman aşımı yeniden oluşmadı. Buna karşın insan bilek/kıyafet deformasyonu açık. `production.json` release_ready=false olarak işaretlendi. Bu çalışma için yeni APK yayımlanmadı.

## v0.1.16 test APK teslimi doğrulandı

Kullanıcının son APK talebiyle test sürümü yayımlandı. GitHub Actions 40825318025 SUCCESS: envanter/kayıt/bonus/silah, geniş arena, dört karakter hareket/efekt ve Bilge kaynak-klip/efekt kontrolleri geçti. APK indirildikten sonra ZIP bütünlüğü ve 52 çalışma zamanı dosyasının çalışma ağacındaki içerikle birebir eşleşmesi doğrulandı. Paket com.roguebloodmoon.prototype, sürüm 0.1.16 / kod 17, 74.334.480 bayt. Önceki sürümün sertifika SHA-256 değeriyle eşleşiyor. Ayrı veri/model kurulumu gerekmiyor. Fiziksel telefonda kurulup test edildiği iddia edilmez.

Doğrudan APK: https://github.com/gkggl3616-jpg/blood-moon/releases/download/prototype-v0.1.16-22/Rogue-Blood-Moon-v0.1.16.apk

Doğrulama: docs/bilge-original-complete/apk-v0116-verification.json. İnsan bilek/kıyafet deformasyonu devam eder; bu test sürümü tam görsel kabul değildir. Sonraki sıra docs/sonraki-adimlar-v0116.md içinde: telefon testi → Bilge skin düzeltmesi → kaynak dört ayak klip/temas/efekt kabulü → cihaz ölçümü → diğer özgün model tipleri → harita.

## 29 Ekim — onaylı gövde önce / kalıcı model standardı ve yeni kontroller

Kullanıcı bir güvenilir gövdeden 3–4 küçük varyant, sonra başka gövde ailesi istedi. Yeni kurtlarda pantolon/eşdeğer alt giysi zorunlu; Bilge'deki uzun sarkan paneller ve büyük süsler tekrarlanmayacak. İnsan eşleri de onaylı anatomik temel üzerinden yapılacak. Kaynak DTX görselleri kontrol edilir; kıyafet dokuları yeni özgün kostüm diye kopyalanmaz. Kalıcı standart `docs/MODEL-URETIM-STANDARDI-TR.md`, proje başlangıç yönergesi kök `AGENTS.md` ve `PROJE_KURALLARI.md` içine eklendi. Bu depo için kalıcı kayıttır; hesap geneli bellek iddiası değildir.

Ateş tuşu basılı sürüklenirken nişan dönüyor. Fare ve gerçek iki-parmak dokunma, pointer iptali/odak kaybı, koşudan sıçrama/takla/insana dönüş testleri geçti. Kükremede bir defalık, sınırlı kamera titreşimi var; hedef yaw/pitch ve oyuncu konumu değişmiyor. Güçlü/zırhlı Köz ailesinde biraz daha belirgin. Daha tok ses mevcut sesin perde/ton/eko düzenlemesiyle `roar-deep.mp3` olarak hazırlandı; kullanıcı ses ayarlarına uyar. Kanıt `docs/full-archive-review/fire-drag-roar-verification.json`.

4,74 GB arşiv indeksi ve kaynak efekt bağlantıları `docs/full-archive-review/` altında. Buz/kan/köz/gölge kaynak efekt grupları ayrı bileşenlerle bağlandı; salt renk değişikliği değil. Kaynak geometri, sprite kareleri ve renk/ölçek eğrileri kullanılıyor; başka motorun tam birebir renderı iddia edilmez. Koşu uyarlamasına kullanıcı “en iyi şekilde yap bozuk hiçbir şey istemiyorum” yanıtıyla izin verdi. Orijinaller korunur; türetilmiş koşu ayrı kliptir. Araştırma ve görsel kabul sürüyor. Yeni 3–4 varyant üretilmiş veya bütün model hataları kapanmış sayılmaz; bu çalışma için yeni APK yayımlanmadı.

## 29 Ekim — kullanıcı dövme yerleşimini iki kez düzeltti

İlk sırt dövmesi pantolona taşıyordu. Spine1 odaklı düşük anchor yanlıştı. Spine2–Neck arası anchor ve kullanıcının “birazcık daha üstte” düzeltmesi için ek 5,5 cm yükseltme ortak `tattoo-policy.json` dosyasına alındı. Bel sınırı ve kıyafet malzemesi dışlama bütün motiflerde zorunlu. Normal parlama 0,025; kükreme tepe 1,05; poz bitince normale döner. Aynı politika üretici ve çalışma zamanı tarafından okunur. Kullanıcı gelecekte kurtların hızlı, standart ve hatasız üretilmesini istedi: önce güvenilir gövde ve ortak kontrol, sonra seri varyant. Bilinen bütün bu tur hataları `GELISTIRME_HATALARI.md` son tablosunda durumlarıyla kayıtlı; tamamlanmamış işlere tamamlandı denmez.

## Son yeniden tasarım talimatı

Kullanıcı düşük model kalitesini reddetti; kurdun yeniden tasarlanmasını, testlerin azaltılmasını ve dövmelerin tek tek denenmemesini istedi. Ice40 görünüşüne yama eklemek yerine seçilmiş Power42 gövdesi ve kendi 42 kemikli WT_NEW_WOLF_CH paketi üzerinden yeni aday hazırlanıyor. Kendi özgün Meshy kurt modelinin detaylı kürk renkleri yeni native gövdeye bake ediliyor; DTX kıyafetleri aktarılmıyor. Büyük bel aksesuarları çıkarılıyor, pantolon ve sınırlı omuz zırhı korunuyor. Araç tools/build_power_redesign.py. Yeni ücretli iş yok. Yeni aday görsel olarak incelenmeden çalışma zamanı modeli değiştirilmeyecek.

## 29 Ekim — yeni ücretli kurt üretimi, eski kaplama yönteminin reddi

Kullanıcı yeni ücretli üretimi açıkça istedi. Tek kurt için 4K geometri + 8K PBR + mobil remesh tahmini 45 kredi; başlangıç bakiyesi 905. Geometri görevi `01a1878d-a5b3-72ac-9098-ccc4a0306a66` başarılı, gerçekleşen 25 kredi. Kaplama görevi `01a18814-08b2-747b-b5ba-1ce9d5c2c6b5` sürüyor. Tekrar gönderim yapılmadı; önceki kabul yerel işlem günlüğünden kurtarıldı.

Önceki Power42 adayında en yakın UV ile eski modelden renk aktarmak kürke giysi/metal desenleri yaydı. Bu yöntem reddedildi; aday oyuna kurulmadı ve tamamlanmış model değildir. Ice40 diz üçgenleri ve uzun boğaz sorunu da kapanmış sayılmaz. Yeni model doğal kürk, ayrı kumaş pantolon ve küçük buz bileklikleriyle üretiliyor. Kaynak animasyonların korunması ve yeni geometri uyumu henüz doğrulanmadı. Kuyruk, ağız/çene ve eklem uyumu özellikle kontrol edilecek. Kalitesiz gövdeyi yeniden zorla uydurup bitmiş sayma yöntemi tekrarlanmayacak. Test kapsamı kısa hareket, bir kükreme/efekt ve tek örnek dövme; bütün motifleri yeniden tarama yok.

### Premium üretim sonucu: başarısız görsel kabul

Üç yeni Meshy görevi başarılı; toplam gerçek maliyet 45 kredi. Yüksek model 1.369.346, oyun adayı 15.586 üçgen. Ancak gerçek ön/yan/arka renderlar gövde kürkünün kumaş gibi, yelenin sivri levhalı kaldığını ve desteksiz kuyruk üretildiğini gösterdi. Ücret harcanmış olması kabul nedeni yapılmadı. Aday oyuna kurulmadı, rig/animasyon/efekt/dövme tamamlandı denmedi. İkinci ücretli tekrar yok. Ayrıntı `docs/premium-wolf-01/README-TR.md`.

## Yeni yetki — tekrar tekrar sormadan tamamla

Kullanıcı görselden yeni üretime devam edilmesini ve tek çalışan kurt + tam APK teslimini açıkça istedi. Yeni 35 kredi tahminli üretim zinciri onaylandı; tamamlandı. Kaynak `01a18823-7e5f-7422-8ae2-b27a15865086`, remesh `01a18825-b1ec-7227-8e88-c5062cd205d2`. Aynı kapsam için tekrar bütçe onayı istenmeyecek. Öncelik tek kurdun tüm zincirini tamamlamak; seri varyant üretimi henüz yok.

## v0.1.17 — seçili gövdeye dönüş ve çalışan zincir

Yeni görselden üretim/remesh 35 krediyle tamamlandı. Üretilen geometriyi Power42 çenesine zorlayan baş/çene denemeleri bozuldu; tahmini ağız kesimi de yanlıştı. Bu adaylar oyuna alınmadı. Kaynak Power42 gövde, gerçek çene/dişler ve 72 kaynak klip korunarak özgün kürk/pantolon görünüşü Cycles ile aktarıldı. Yanlış UV adaları arasındaki renk karışımı giysi desenlerini kürke taşıyordu; bu yöntem kaldırıldı. Sürekli referans kürkü ve yeni giysinin yumuşak kasık ağırlıkları kullanıldı. 42 kemik, yaklaşık 14,2 bin üçgen. Yerel dört poz, gerçek koşu/takla/kükreme ve yedi geçiş kontrolü geçti. Telefon/görsel kullanıcı kabulü henüz yok. Diğer üç yeni özgün kurt tamamlanmış sayılmaz. Ayrıntı `docs/premium-wolf-01/TESLIM-TR.md`. Tek imzalı APK için CI aşamasına geçiliyor.

## Son sıralama — APK önce, boynuzlu çift sonra

Kullanıcı mevcut kurtla APK'nın önce gönderilmesini; sonra koşu referansında görülen boynuzlu gövde için yeni insan/kurt çiftine başlanmasını istedi. Bu yeni çiftin tasarımı APK tesliminden önce başlatılmaz. Ağız/diş, iskelet uyumu, dövme ve efekt hataları tekrar edilmez. Kontrol kapsamı karakter, insan, animasyon, dövme ve efektlerle sınırlanır; her karakter eklemede bütün arayüz/mağaza testleri yeniden taranmaz. Manuel CI varsayılanı `character`, gerekirse ayrı `full` seçeneğidir. Açılışı geçmek karaktere ulaşma hazırlığıdır; Atla düğmesi bu kapsamda test edilmez. Mevcut CI'de arayüz kontrolleri kullanıcı bu sınırlamayı iletmeden önce bitmişti; bunlar yeniden başlatılmadı.

## v0.1.17 APK gerçekten teslim edildi

CI 40906762220 başarılı; sürüm 0.1.17/kod 18, 75.029.377 bayt. İmza önceki v0.1.16 ile aynı: af43be4b6ee4d5b2e1feca6da3df36805a7b10bbb56b1f884136054ef7f98633. İndirilen APK CRC/bütünlük ve 81 çalışma zamanı dosyasının birebir eşleşme kontrolünü geçti. İnsan tek bekleme pozunda ölçülen ağır bilek uzaması yok. Tek örnek dövme/ortak yama, kaynak kükreme/FX ve geçişler kontrol edildi. Telefon veya kullanıcı görsel kabulü yapılmadı. Doğrudan bağlantı ve hash: docs/premium-wolf-01/apk-v0117-verification.json.

APK gönderildikten sonra boynuzlu kaynak gövde için Demir Han / Kara Boynuz çiftinin tasarım başlangıcı açıldı. Ayrıntı docs/horned-pair/TASARIM-TR.md. Bu yeni çift mevcut APK'ya eklenmedi. Bind eşleşmesindeki farklar çözülmeden rastgele yeni mesh üretip iskelete zorlanmayacak.

## 29 Ekim — son kalite itirazı ve kimlik koruması

Kullanıcı insan/kurt dokularının ve genel görünümün çok kalitesiz, kareli göründüğünü belirtti. Sadece shader/parlaklık/renk değişikliği kabul edilmiyor. Güncel bağlayıcı prompt: `docs/KALICI-KARAKTER-KALITE-PROMPTU-TR.md`. Anatomik kürk akışı, gerçek PBR katmanları, kontrollü pençe yaraları/kuru kan, yıpranmış/yırtık pantolon, doğru ağız ve ayrı kimlik şartları yazıldı. Karahan `karahan` olarak ayrı karakterdir; Bilge Kağan `bilge` ve onun Buz Kurdu dosyaları değiştirilerek Karahan yapılmaz. Yeni insan adayı düz blok gömlek ve ayrık kürk yaka nedeniyle reddedildi; bu aday görsel olarak tamamlandı diye sunulmayacak. Teknik olarak çalışan düşük kaliteli kaplama da kabul değildir. Kükreme sesi arşiv indeksinde bulunmadı; kaynak efekt bulundu. Ses kaynağı konusunda bunlar karıştırılmayacak.


<!-- KALICI_KALITE_PROMPTU_20261029 -->
# Kalıcı insan/kurt üretim promptu — güncel ana kalite şartı

29 Ekim 2026. Kullanıcının son kalite düzeltmesi. Yeni karakterler ve mevcut karakter düzeltmeleri için bağlayıcıdır. Teknik kontrolün geçmesi görsel kabul değildir.

## Görev

Rogue: Blood Moon için mevcut, doğrulanmış gövde/iskelet ailesini kullanarak ayrıntılı, doğal ve tehditkâr insan/kurt çifti üret. Sonucu gerçek oyun GLB'si, malzemeleri, skin ağırlıkları, kaynak animasyonları, dövme yüzeyleri ve model ailesinin kükreme efektiyle birlikte hazırla. Konsept görseli gerçek 3B teslim sayılmaz. Rastgele üretilmiş anatomiyi sonradan başka iskelete zorlama.

## Karakter kimliklerini koru

Bilge Kağan `bilge`, Buz Kurdu onun kurt formudur. Karahan `karahan` kimliğiyle ayrı eklenir. Karahan'ın insanı veya kurdu Bilge'nin dosya yoluna, kayıt kimliğine ya da ekipman profiline yazılmaz. Eski sahiplik, kredi ve donanımlar korunur. Aynı insan gövde ailesinin kullanılması, iki karakterin aynı yüz/kostümle tamamlanmış sayılması değildir. Ortak yüz/gövde kullanılan adayda bu sınırlama açıkça belirtilir.

## Görsel kalite

- Geniş omuz ve göğüs, anlaşılır kas yapısı, dar bel, güçlü kalça/bacak. Baş-boyun-omuz silüeti ayrı okunur. El ve ayaklar doğal, parmaklar hafif kıvrık; robot gibi açık avuç yok.
- Kürk, metal ve desenli kumaş gibi görünmez. Büyük tekrarlayan dalgalar, zebra/mermer desenleri, kâğıt levhalar ve rastgele sivri üçgenler kabul edilmez. Kürk akışı anatomiyi takip eder; yalnız yüzey gürültüsü ayrıntı sayılmaz.
- PBR renk, tangent-space normal ve pürüzlülük haritaları kullan. Gerçek olmayan boyalı ışık/parlama yerine ışığa tutarlı tepki ver. Kürk/deri/kumaş metal değildir; metal yalnız gerçek zırh parçalarındadır. Her malzemenin pürüzlülüğü ayrı ayarlanır. Bir shader kaliteyi sihirli biçimde artırmaz.
- Ana ayrıntıda 2K, yüz/yakın çekim gerektiriyorsa uygun 4K atlas değerlendir. Çözünürlük sayısı tek başına kalite kanıtı değildir. Mip haritaları, UV dikişleri ve anizotropik filtre birlikte kontrol edilir. Telefon belleği ölçülmeden sınırsız 4K/8K yükleme yapma.
- Geometri bütçesi yaklaşık kurt 15 bin, insan 12 bin üçgendir. Silüeti etkileyen parça geometridir; küçük saç/kürk/dikiş/çizik ayrıntısı dokudur. Kareli/çok köşeli eklem, ters normal ve kötü gölgelendirmeyi düşük poligon gerekçesiyle kabul etme.
- Kurt pantolon/eşdeğer alt giysi giyer. Kumaşta dokuma, dikiş, kıvrım ve kontrollü yıpranma olsun. Küçük yırtıkların altında uygun deri/kürk görünür; karanlık boşluk veya uzayan üçgen oluşmaz. Yırtık için eklem yüzeyini rastgele silme. Uzun etek, sallanan bel süsü ve büyük kemer kıvrımı ekleme.
- Az sayıda iyileşmiş pençe yarası ve sınırlı koyu/kuru kan izi eklenebilir. Yaralar omuz, göğüs veya kol üzerinde anatomiyi izler; desen tüm gövdeye döşenmez. Çizik, kan, giysi kirlenmesi ve dövme farklı katmanlardır. Kan normal durumda emissive değildir.
- İnsan ayrıntılı yüz/saç/kaş/sakal, okunur gözler, doğru el ve kaliteli kısa kostüm taşır. Düz siyah blok gömlek veya kaplaması eksik kahverengi omuz, tamamlanmış zırh diye sunulmaz.

## Ağız, iskelet ve animasyon

Kaynak baş/çene ve dişler korunur. Üst diş başı, alt diş alt çeneyi izler. Dış kırmızı oval, havada diş, çenede delik ve uzayan boğaz yok. Kaynak bind ile hareket bind'i ölçülür; yalnız kemik adı/sayısı eşleşmesi yeterli değildir. Gerekli bağlama uyarlaması türetilmiş katmanda yapılır; ham kaynak anahtarlar saklanır. Boynuz/zırh gibi küçük parçalar uygun mevcut kemiğe bağlanır; yeni süs için kemik oranı değiştirilmez.

Yürüme/koşma temposu gerçek sabit fizik adımındaki ilerleme hızından hesaplanır. Fizik adımı olmayan yüksek yenileme kareleri karakteri boşta duruşa döndürmez. Koşarken ikinci parmakla sıçrama/takla ve insana dönüş çalışır. Takla kısa kalır, yatay hız iki kez eklenmez. Kısa kontrol: bir yürüyüş/koşu döngüsü, sıçrama, takla ve tam kükreme. Her motif ve bütün oyun arayüzü yeniden taranmaz.

## Dövme ve FX/ses

Üç ortak deri yaması: üst sırt, sol üst kol arkası, sağ üst kol arkası. Giysi/zırha taşma yok. Eğri yüzeyi ve skin ağırlığını izler; havada kart değildir. Motif değişimi aynı yerleşimi kullanır. Normal parlama 0,025; kükremede tepe 1,05. Eşya bonusları karakter pasifinden bağımsız gerçek hesapla uygulanır; +%240, 100 tabanda 340 demektir.

Modelin kendi kaynak kükreme klibi ve efekt bağlantısı çözülsün; yalnız renk değiştirmek başka efekt sayılmaz. Olay zamanı, efekt geometrisi/sprite/ölçek/sönme eğrileri korunur. AI hasar komutları oyuncuya taşınmaz. Ses önceden çözülür, tek ses kanalı ve pay bırakılmış seviye kullanılır; animasyon bittikten sonra geç başlama veya üst üste ses patlaması yok. Hafif kamera titreşimi nişanı kalıcı kaydırmaz.

## Teslim ve dürüst kayıt

Ön/yan/arka gerçek oyun görüntüsüyle kontrol et. Ağır uzama veya açık ağız hatası varken modeli yayıma hazır sayma. Yalnız test edildiği kadarını söyle. Yapılan, otomatik kontrol edilen, görsel olarak incelenen, kullanıcı tarafından kabul edilen ve fiziksel telefonda deneneni ayrı yaz. Yeni ücretli görev gerekiyorsa gerçek kapsam/maliyet açık olmalı; geçmiş bütçe sınırsız izin değildir. Kurulum tek imzalı APK, belgeler ayrı güncel MD bağlantısıdır.

## Son somut durum — kalite promptu sonrası

`docs/karahan-v0118/GUNCEL-RAPOR-TR.md` bütün bu tur hatalarını, gerçek model üretim zincirini, kısa test sonuçlarını, kaynak FX/ses gerçeğini ve açık işleri bir arada içerir. Hareket/ses kodu kısa kontrolden geçti; Bilge insan/kurt GLB'leri son APK ile aynı. Karahan'ın yeni doku ve skin kalitesi kabul edilmedi, canlı modele eklenmedi. İki doku girdisi hazır. 29 Ekim resmî fiyat listesinde 4K Retexture model başına 10; insan+kurt 20 yeni kredi önerisi, bakiye 825; yeni ücretli görev başlatılmadı. Kaynak skin uzamaları ayrıca düzeltilmeden yayıma hazır sayılmaz. Sonraki oturum testleri en baştan tekrarlamak yerine bu açık durumdan devam eder. Yeni tek APK ve güncel MD teslimi hâlâ bekliyor.
