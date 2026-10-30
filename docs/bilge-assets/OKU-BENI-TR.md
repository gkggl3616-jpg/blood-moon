# Bilge Kağan / Buz Kurdu — dosya paketi

30 Ekim 2026. Bu paket yayımlanmış v0.1.18 APK içindeki Bilge Kağan insan/kurt çiftine aittir. Karahan değildir. Yeni üretim veya oyun güncellemesi yapılmadı.

## Nereden başlamalısın?

- `Oyun/Modeller/bilge.glb`: güncel kurt. 42 kemik / Power42, 72 ham kaynak klip. Model, iskelet, ağırlıklar, UV, dokular ve animasyonlar gömülüdür.
- `Oyun/Modeller/human-bilge.glb`: güncel insan. Human47 / 47 kemik, gereken 11 kaynak insan klibi. Dokular ve animasyonlar gömülüdür.
- `Oyun/Dokular`: bu GLB'lere gömülü gerçek güncel görüntülerin ayrıca çıkarılmış kopyaları. GLB'yi açmak için ayrıca bağlaman gerekmez. Görüntü numarası GLB `images` diziniyle aynıdır; malzeme/doku bağları GLB içinde korunur.
- `ANIMASYON-LISTESI.json`: tam klip adları, süreleri ve runtime meta verisi. İnsan kaynak LTB'si 569 klip içerir; oyunun GLB'sinde yalnız kullanılan 11 klip vardır.
- `Kaynak/Animasyonlar/wt_new_wolf_ch.ltb`: kurt hareket kaynağı. `T_WallDash` koşu, `T_CRY` 1,333 sn kükreme, `T_Specialatk` takla, `UMFi1` / `UMFi2` pençe, `LWF` / `UMWF` yürüyüş. Kükreme FX olayı 0,633 sn. Tam liste JSON'dadır.
- `Kaynak/Animasyonlar/wt_new_man_ch.ltb`: insan hareket kaynağı; kurt dosyası değildir.
- `Kaynak/Modeller/wt_wolf_power_r.ltb`: kurt gövde/iskelet kaynağı. `pedro.ltb`: insan temeli için kaynak referans. Bu kaynakların görünüşü oyundaki özgün Bilge kostümü değildir.
- `Kaynak/DTX`: kaynak referans dokuları. `wt_wolf_r.dtx` gövde; `wt_wolf_powershoulder_r.dtx` omuzluk; Pedro üst/alt/el/ayakkabı dosyaları insan referansıdır. Kaynak DTX kıyafetleri güncel özgün Bilge kaplaması diye sunulmaz. **Güncel Bilge kaplamaları DTX değil, GLB içine gömülü PNG/JPEG görüntüleridir.**
- `Blender/*-static.blend`: düzenlenebilir statik çalışma sahneleri. Son runtime GLB'sindeki kliplerin tamamını içeren bitmiş animasyonlu Blender teslimi değildir. Son animasyonlu durumu görmek için GLB'yi Blender'a aktar.
- `Kaynak/FX`: seçilmiş efektlerin orijinal LTB/DTX/sprite bağımlılıkları; ortak paket olduğundan diğer ailelerin bağımlılıkları da bulunabilir.
- `Oyun/fx/native`: mevcut oyunun ortak kaynak FX paketi; Bilge `Howling_Ice_1` grubunu kullanır. Paylaşılan JSON bağımlılıklarını kırpmamak için diğer gruplar da korunmuştur; hepsi Bilge'ye ait denmez.
- `Oyun/Ses/roar-voice.wav`: oyunun düzenlenmiş kükreme sesi; arşivde bulunmuş özgün karakter sesi değildir.
- `Oyun/Dovme`: ortak dövme atlası ve yerleşim/parlama politikası.
- `Entegrasyon-Referansi`: hareket birleştirme, hız, yer teması ve FX olayları için mevcut Three.js kaynak referansı. Bunlar tek başına çalışan Godot eklentisi değildir.

## Godot / Blender notu

Godot'a esas olarak `.glb` dosyalarını aktar. `.ltb` / `.dtx` kaynak biçimleridir; standart Godot içe aktarıcısı bunları doğrudan oyun modeli olarak açmaz. Kaynak kemik adları, bind pozları ve ağırlıklar korunmalıdır. Alt/üst gövde hareketlerinin birleştirilmesi, yere temas düzeltmesi, fiziksel ilerleme ve FX zamanlaması oyunun runtime katmanında yapılır; yalnız bir ham klibi seçmek oyunla birebir aynı davranışı garanti etmez. Karakter pasifi, dövme bonusu ve sahiplik oyunun verisidir; model geometrisinin özelliği değildir.

Bu paket üçüncü taraf kaynak gövde/iskelet/animasyon verisi içerir; dosya adları ve kökeni korundu. Bu dosyaların adını değiştirmek bunlara yeni sahiplik/lisans sağlamaz. Gövde kaynağı ile üretilen görünüş ayrı tutulmuştur.

Bu bir APK veya Godot projesi değildir. Güncel oyun model kopyaları yayımlanmış APK ile aynı hash'e sahiptir. Fiziksel telefon/Godot testinin yapıldığı iddia edilmez. `DOSYA-MANIFESTOSU.json` her dosyanın boyutunu ve SHA-256 değerini içerir.
