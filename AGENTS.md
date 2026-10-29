# Rogue: Blood Moon — proje belleği

Bu depoda işe başlarken `PROJE_KURALLARI.md`, `docs/MODEL-URETIM-STANDARDI-TR.md` ve `a.md` içindeki son çalışma kayıtlarını okuyun. Kullanıcının yeni talimatları eski kararların önüne geçer.

- Onaylı gövde/iskelet/hareket paketi önce gelir; rastgele üretilmiş modeli sonradan iskelete zorlamayın.
- İlk doğrulanmış gövdeden 3–4 kontrollü varyant; sonra başka gövde ailesi. Kurtlarda pantolon veya eşdeğer alt giysi; uzun sarkan süs/etek panelleri yok.
- Ağızda kırmızı dış oval, uzayan bilek yüzeyleri, yanlış dövme yönü ve kesilen efektler kabul edilmez. Hataları gizlemeyin; açık durumu belgeleyin.
- Kaynak dosyaları ve kullanıcı kayıtlarını koruyun. Yeni ücretli üretim için eski bütçeyi sınırsız izin saymayın.
- Animasyon kaynağı ile türetilmiş uyarlamayı ayrı tutun. Kullanıcı koşu uyarlamasına izin verdi; iskelet/rest uzunlukları korunur.
- Otomatik test, görsel kabul ve fiziksel Android testi farklıdır. Yapılmamış işi tamamlandı demeyin.

Bu dosyalar bu proje deposunda sonraki oturumlar için kalıcı kayıttır; hesap genelinde veya başka projelerde otomatik bellek garantisi değildir.

Dövme ortak politikası `art/characters/model-families/tattoo-policy.json` içindedir. Bütün motifler gövde yamasını paylaşır; kıyafete taşma yasaktır. Kaynak geometriye göre doğrulanmış gövde sınırı kullanılır (eski Bilge'de yüksek korse sınırı ayrıca tanımlıdır). Normal parlama düşük, yalnız kükreme pozunda belirgindir. Yeni wolf GLB'leri `tools/apply_tattoo_policy.py` ve uygun rig/görsel kontrollerden geçirilir. APK paketleyici güncel politika hash'ini doğrular. Politika değiştiğinde bütün modeller güncellenip motif/normal/tepe/toparlanma testleri çalıştırılmadan sürüm çıkarılmaz.

Son kullanıcı önceliği: kurt yeniden tasarlanacak. Testler kısa tutulacak; her dövmeyi tek tek test etmek istenmiyor. Bu yeni talimat yukarıdaki bütün motifleri her seferinde tarama kuralının önündedir. Tasarım turunda üç ana poz ve tek örnek dövme/efekt kontrolü; geniş regresyon yalnız son entegrasyonda veya somut yeni hata gerekçesiyle.

v0.1.17 için geçerli gövde yolu: `build_native_premium_wolf.py` → `bake_native_premium_appearance.py` → `finish_native_premium.py` → `premium_native_contract.py --asset ...` → `apply_tattoo_policy.py`. Kaynak Power42 bind ölçüleri, çene/dişler ve 72 klip korunur; yeni giysinin kasık ağırlık geçişi ayrıca düzenlenmiştir. `build_premium_wolf_v2.py`, `repair_premium_mouth.py` ve eski UV yakınlık denemeleri reddedilen araştırmalardır; yeni karakter üretiminin temeli yapılmaz. Ücretli donor 3B modelin özgün görünüşü Cycles ile aktarılır; kaynak DTX kıyafetleri kopyalanmaz. Runtime sözleşmesi `app/src/main/assets/models/native-contracts.json` içindedir. Gerçek fiziksel telefon ve kullanıcı görsel kabulü henüz yoktur.

Son kalite talimatı: `docs/KALICI-KARAKTER-KALITE-PROMPTU-TR.md` okunur. Karahan ayrı `karahan`; Bilge Kağan/Buz Kurdu `bilge` kimliği ve modelleri korunur. Düz siyah blok giysi, ayrık yaka ve tekrarlayan mermer/zebra kürk desenleri görsel kabul değildir. PBR shader tek başına modelleme ve doku kalitesinin yerine geçmez.

Karahan/Behamah40 ayrı kimliktir; Bilge/Buz dosyalarıyla karıştırılmaz. Son görünüş: özgün yan boynuzlar, belirgin yırtık kapri, kan/pençe yaraları. `docs/karahan-v0118/GUNCEL-RAPOR-TR.md` gerçek üretim/hata kaydıdır. 74 ham kaynak klip + ayrı DerivedBehamahRoar korunur. Gövdeyle klipteki yerel uzunluk farkları yalnız bu ailede rest uzunluklarına uyarlanır. Son PBR albedo verisinin gerçekten GLB içine gömüldüğü doğrulanır; bağlantının varlığı yeterli değildir. Fiziksel cihaz testi ve kullanıcı görsel kabulü hâlâ ayrıdır.
