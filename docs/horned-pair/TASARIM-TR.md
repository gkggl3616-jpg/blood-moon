# Güncel karar: Karahan — 29 Ekim 2026

İnsan ve kurt kimliği Karahan olarak adlandırıldı; aşağıdaki Demir Han/Kara Boynuz adları eski çalışma adlarıdır. Karahan Bilge Kağan'ın yerini almaz. Yeni görüntü denemeleri yeterli bulunmadı; canlı model listesine eklenmedi. Kalıcı güncel prompt `../KALICI-KARAKTER-KALITE-PROMPTU-TR.md`, ayrıntılı gerçek durum `../karahan-v0118/GUNCEL-RAPOR-TR.md` içindedir.

Ek bind düzeltmesi denemesi reddedildi: aynı Behamah gövdesinin AI `T_Explosion` kükreme anahtarları, çocuk dosyanın `T_cry` anahtarlarıyla aynıdır. Farklı bind kayıtları tek başına ek dönüştürme gerekçesi değildir. Ham hareket anahtarları korunur. Kaynak cilt/giysi ağırlıklarında kalan uzamalar ayrıca düzeltilmelidir; doku üretimi bunları otomatik çözmez.

---

# Demir Han / Kara Boynuz — tasarım başlangıcı

Bu çalışma v0.1.17 APK gönderildikten sonra başladı. Bu çift o APK'nın içinde değildir. İsimler çalışma adıdır: insan **Demir Han**, kurt **Kara Boynuz**.

## Kaynak ve hareket

Koşu görselindeki gövde `wolf_king_behamah.ltb` kaynağıdır. Gövdenin ilan ettiği çocuk hareket dosyası `Wolf_kingAsmon_CH.ltb` olarak çözüldü. Benzer isimli `wt_wolfrush_behamah_ch.ltb` dosyasını yalnız kemik adları eşleştiği için körlemesine bağlama.

Kaynakta 40 kemik, gerçek çene etkisi olan 271 ağırlıklı vertex ve 4.484 üçgen bulundu. `T_Dash` 533 ms; tam kükreme `T_cry` 1933 ms. `T_CRY_old` 1133 ms eski kliptir ve tam kükremenin yerine alınmaz. Ses/efekt olayları gerçek dosyadan okunur. `T_Dash_JJ`, `T_Dash_JT` ve `T_Dash_JL` koşudan sıçrama için ayrıca vardır; yeni hareket yazmadan önce bunlar değerlendirilir.

Bind karşılaştırması fark gösterdi; yalnız kemik sayısı veya isimlerin eşleşmesi yeterli değildir. Ayrıntılar `source-contract.json`, `resolved-sources.json`, `bind-details.json` içindedir. Kök/pelvis çerçeveleri, ağırlıklı uzuvların yerel bind ölçüleri ve çocuk animasyon bağlama kuralı çözülmeden bu gövde oyuna kurulmaz. 271 jaw vertex bulunması kükremenin görsel kabulünün tamamlandığı anlamına gelmez.

İnsan için ilk oran referansı Pedro47'dir. Kaynak hareket dosyasıyla bind farkları ayrıca görülmüştür; bu da çözülmeden yeni insan modeli tamamlandı sayılmaz. Şimdilik ham kaynaklar korunur; kaynak anahtarlar yeniden yazılmadı. Nötr gri görseller yalnız anatomi/oran referansıdır, yeni özgün karakter teslimi değildir.

## Görsel kimlik

Kara Boynuz, Buz Kurdu'nun renk varyantı olmayacak. Aynı Behamah gövdesinin iri göğüs/omuz, dar bel, uzun önkol ve geniş pençe fiziği korunacak. Kömür grisi kısa kürk, hafif gümüş kenarlar, küçük mat bronz bağlantılar ve sıcak kehribar göz yönü seçildi. Kürk metal/kumaş gibi parlamaz. Donanım siyah çelik ve eskitilmiş bronz; pantolon koyu dokuma/deri, esnek diz ve düzgün paça.

Koşu pozunda boynuz gibi görünen kaynak kıvrımlı parçalar nötr pozda bel dekorundadır. Kullanıcının önceki büyük bel süsü yasağı korunur: bunlar yeni tasarıma taşınmaz. Yeni boynuz görünüşü başa bağlı iki kontrollü, kısa ve geriye yönelen ayrı keratin parça olarak ele alınır. Baş/çene geometrisi kesilmez; yeni kemik eklenmez, boynuz başı izler. Büyük omuz/dirsek çıkıntısı ve uzun sarkan etek yok.

Demir Han aynı kimliğin insanıdır: güçlü, yorgun komutan yüzü, kısa koyu saç/sakal, siyah çelik ve eskitilmiş bronz göğüs zırhı, kısa bel düzeni, koyu pantolon. İnsan yüzüne veya eline metal desenleri taşınmaz. Uzun bilek süsleri, avuçtan taşan ince şeritler ve kart gibi giysi yüzeyleri yok. Giysi görseli kaynak DTX'den kopyalanmaz.

Dövme tasarıma kalıcı basılmaz. Sırt/sol üst kol/sağ üst kol yaması ayrı skin sistemiyle gelir; normalde kısık, yalnız kükreme pozunda parlak. Eşya bonusu karakter pasifinden ayrıdır. Pasif/denge değerleri bu tasarım başlangıcında oyuna eklenmedi.

## Ağız, efekt ve kısa kabul

Kaynak yüz, gerçek alt çene, üst/alt diş geometrisi ve ağırlıkları temel alınır. Üst diş başı, alt diş çeneyi izler. Tahmini dünya yüksekliğiyle ağız kesilmez. Boyalı ağız içi diş yerine sunulmaz. Ağız/diş/dil gövde parlamasına alınmaz.

Kükremede ham olay metni çalıştırılmaz; yalnız tanımlı ses ve efekt eşlemesi yapılır. `T_Explosion` gibi AI saldırı olayları yeni oyuncu kükremesine hasar olarak taşınmaz. Modelin kendi efekt bağlantısı ayrıca çözülecek; sıcak metal tozu ve ölçülü şok dalgası tasarım yönüdür, tamamlanmış FX beyanı değildir. Ses tok, kısa kamera titreşimi nişan yönünden bağımsız olur.

Kontrol kapsamı yalnız insan/kurt, dört ana hareket pozu, tek örnek dövme ve bir tam kükreme/FX çevrimidir. Her karakter eklemede mağaza, tüm arayüz veya bütün dövme motifleri tekrar taranmaz. Yeni çiftin rig/görsel kabulü ve oyun entegrasyonu henüz tamamlanmadı; yeni ücretli Meshy görevi başlatılmadı.

## İlk pafta hazır

`art/characters/horned-pair/design-board-v1.png` insan/kurt görsel yönünü gösterir. Kaynak gövdelerin nötr oran görüntüleriyle oluşturulmuş **2B tasarım paftasıdır**. Gerçek oyun geometrisi, skin, animasyon veya FX teslimi değildir. Özellikle baş/el oranları ve zırh kalınlıkları, kaynak 3B sınırları üzerinden tekrar ele alınmadan resimdeki her ayrıntı doğrudan geometri diye kullanılmaz. Mevcut v0.1.17 APK dosyaları bu çalışmada değiştirilmedi.

Paftadaki kol açıları ve baş/el ölçeği nötr kaynak pozundan sapabilir. Bu nedenle pafta doğrudan yeni gövde üretip sonra rig'e zorlamak için kullanılmaz; öncelikle malzeme, giysi ve kimlik hedefidir. 3B boynuz ve donanım, mevcut kemiklere bağlı küçük parçalar olarak oluşturulur; kaynak eklem merkezleri ve çene korunur.
