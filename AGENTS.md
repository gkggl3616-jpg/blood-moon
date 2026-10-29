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
