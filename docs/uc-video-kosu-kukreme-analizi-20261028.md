# Üç yeni video — koşu ve ortak kükreme incelemesi

Tarihî inceleme kaydı; sonraki kodlama onayının uygulaması [v0.1.13 kaydında](guncelleme-v013.md). Aşağıdaki durum incelemenin yapıldığı anı anlatır.

Bu inceleme turundaki istek: üç kaydın incelenmesi ve aynı hareketlerin oyuna nasıl aktarılacağının açıklanması. **Oyun kodu, GLB’ler ve yayımlanmış v0.1.12 APK değiştirilmedi. Yeni ücretli üretim yapılmadı.** Aşağıdaki uygulama adımları henüz yapılmış iş değildir.

## Kaynaklar ve inceleme

| Video | Kullanıcının anlamı | Konteyner süresi | İncelenen görüntü kareleri | Son görüntü zamanı |
|---|---|---:|---:|---:|
| 1 · 00-19-31-640 | Bizim oyundaki koşu | 2,693 sn | 62 | 2,517 sn |
| 2 · 00-22-55-291 | Hedef koşu | 7,152 sn | 170 | 6,988 sn |
| 3 · 00-28-44-891 | Bütün karakterlere ortak kükreme | 2,949 sn | 69 | 2,808 sn |

Üç videonun toplam 301 görüntü karesi çıkarıldı ve zaman etiketli 20 sayfada incelendi. Konteyner süreleri görüntü son zamanından farklıdır; ses/paket kuyruğu hareket süresine katılmadı. İnceleme görsel poz ve efekt üzerinedir; ses tasarımı onaylanmış sayılmaz. Kaynak kimlikleri: [sources.json](review-20261028/sources.json). Tüm kareler ve sayfalar çalışma alanında `/workspace/reference-review/20261028-run-roar/` altında tutulur.

Kanıt şeritleri: [bizim koşu](review-20261028/current-run.jpg), [hedef koşu](review-20261028/target-run.jpg), [hedef kükreme](review-20261028/target-roar.jpg), [hedef kaydın sayacı](review-20261028/target-timer.jpg).

## Video 1 — somut sorunlar

- Kül Tigin’in koşusu tepeden görülüyor. Omuz/baş silüeti, gövdenin öne uzanmasından daha baskın; ön kol/ellerin destek ve toparlama hareketleri kısa ve birbirine yakın fazlarda gerçekleşiyor. Hızlı, küçük salınım baskın; ağırlık aktarımı okunmuyor.
- Arka bacakların gövde altına toplanması ve geriye itmesi hedefteki kadar geniş ve belirgin değil. Sırt/kalça/baş ilişkisi bir bütün halinde çalışmıyor. Kuyruk arka bacakları kısmen örtüyor; kuyruk hareketi koşu ritmini gölgeliyor.
- Bu kayıttaki kamera açısı teması gizliyor. Bu, varsayılan kameranın her durumda yanlış olduğunun kanıtı değildir; kullanıcı bakışı da açıyı değiştirebilir. Karşılaştırmada kamera eğimi, mesafe, modelin ekrandaki büyüklüğü eşitlenmeli.
- Görselde her pençenin her anda yerle temasını kesin çıkaramıyoruz. Doğrulama için aynı klibin yan görünümü ve taban işaretleri gerekir. “Hiç basmıyor” veya “bütün döngü kayıyor” diye ölçülmemiş kesinlik kullanılmayacak.

## Video 2 — alınacak hareket ve yavaş oynatım kanıtı

- Yaklaşık 0,7 sn civarında gövde/arka bacaklar geriye uzamış, 0,9–1,2 civarında gövde toplanmaya başlamış, 1,3–1,5 civarında dizler açılarak ayaklar gövde altına alınmış, 1,6–1,9 civarında itiş/uzama yeniden oluşuyor. Bunlar kayıt zamanlarıdır; kesin temas anları tek arkadan açıyla tam görülemiyor.
- Belirgin toplanma pozu yaklaşık 0,4 / 1,4 / 2,4 / 3,4 / 4,4 / 5,4 kayıt saniyelerinde tekrarlanıyor: görünen döngü yaklaşık 1 sn. Koşu gövdeyi uzatıp topluyor; el ve ayak hareketleri yalnız küçük aşağı-yukarı salınım değil.
- Yaklaşık 6,16’da ayakta beklemeye, 6,82’de yeniden koşuya geçiliyor. Kayıtta koşu, durma ve yeniden başlama birlikte var.
- **Kayıt gerçek zamanla aynı hızda görünmüyor:** sayaç ilk karede 02:59, yaklaşık 0,99’da 02:58, 2,73’te 02:57, 4,47’de 02:56, 6,45’te 02:55. Ardışık tam sayaç aralıkları yaklaşık 1,7–2 görüntü saniyesi sürüyor. Kaydın yavaşlatılmış/yeniden zamanlanmış olması güçlü olasılık; tam oynatım katsayısı kesinleştirilmedi.
- Dolayısıyla görünen 1 saniyelik döngü oyuna doğrudan “referansın gerçek koşu süresi 1 sn” diye konamaz. Oyun dünyasındaki m/sn hızı da bu perspektifli görüntüden kesin ölçülemez.

## Video 3 — kükreme ve karıştırılmaması gereken efektler

- Kayıt ilk karede zaten etkin yeşil ışık/bulut ve yükselmiş bir el içeren hareketin ortasından başlıyor. Bu ilk kısmı tam kükreme başlangıcı diye varsaymıyoruz.
- Yaklaşık 1,32–1,61: karakter belirgin biçimde yükleniyor; dizler/kalça esnek, kollar yana açılmaya başlıyor.
- Yaklaşık 1,69–2,10: **iki el başın üzerine çıkıyor**, dirsekler bükülü, parmak/pençeler açık; göğüs ve baş yukarı taşınıyor. Bu, mevcut kükreme klibimizin elleri göğüs hizasında öne/yanlara açmasından farklıdır.
- Yaklaşık 2,15–2,44: kollar aşağı inerken gövde toparlanıp beklemeye dönüyor. İki kolun hareketi tamamen simetrik robot dönüşü değildir; küçük doğal farklar var.
- Yüz arkadan görüldüğü için bu kayıttan kesin ağız açıklığı, diş kapanışı veya çene eğrisi ölçülemez; önden ayrıca kontrol gerekir.
- Öndeki büyük yeşil patlama ilk karede zaten vardır ve başka karakterlerin yanında görünür. İkinci belirgin baş-üstü kol hareketi sırasında bu bulutun önemli bölümü sönüyor. Bu nedenle sahnedeki bütün yeşil bulutu veya sonradan geçen ışınları oyuncunun kendi kükreme efektine mal etmek doğru değil. Kullanıcının işaret ettiği ana karakter pozu alınır; efekt sahipliği net olmayan alan saldırısı kükremeye otomatik eklenmez.

## Mevcut kod neden aynı sonucu vermiyor?

- `art/3d/scripts/animate_wolves.py`: `WolfRunQuad` referanstan hazırlanmış sanatçı klibi değil; faz fonksiyonları ve hedef eklem noktalarıyla üretilen prosedürel bir döngü. `fit_limbs` kol/bacak uzunluğunu korur, ancak anatomik poz, doğru destek, avuç yönü ve omuz–gövde deformasyon kalitesi sağlamaz. Gövde/boyun segmentleri de ayrıca kontrol edilmeli.
- Kaynak koşu 16/30 ≈ **0,533 sn**. `tools/viewer/arena.js` bunu `8/5.6 × hız_derecesi/100` ile hızlandırıyor. Başlangıç +%5 ründe çarpan 1,5; görünen döngü yaklaşık **0,356 sn** oluyor. Önceki hız artışı klip temposunu da çok sıklaştırmış. Bu, hedefteki pozlara uymayan bir döngüyü daha hızlı oynatıyor.
- Menü `tools/viewer/viewer.js` içinde klip hızı 1 iken arena koşuya farklı çarpan uyguluyor. Menü ve arena aynı GLB’yi kullansa da aynı hızda animasyon izlenmiyor. Ortak hareket/temas ayarı gerekli.
- Mevcut `WolfRoar` el hedefleri yaklaşık 0,64 × karakter boyu düzeyindedir; bu baş üstü poz değildir. Yalnız klibin süresini uzatmak veya efekt eklemek referans hareketini üretmez.
- `tools/viewer/effects.js` kükreme el parçacıkları için sabit `0xa849ff` kullanıyor. Mevcut karakter paleti otomatik olarak kükremeye uygulanmıyor.
- Son kaynak-model sadakati testinin başarısı bekleme pozunu koruduğumuzu gösterir. Koşunun veya kükremenin referansın sanatsal hareketini yakaladığının kanıtı değildir.

## Aktarım yöntemi

1. **Mevcut onaylı modeli koru.** Gövdeyi yeniden üretme, yeleyi başka gövdeyle değiştirme, eklemleri geometriyi esneterek hedefe götürme. Rest-pose ve kaynak-köşe farkı kontrolünü koru.
2. **Bir ana kurt üzerinde Blender’da pozları kur.** Uzama → ön destek/yük alma → arka bacakların toplanması → arka itiş → kısa uçuş/uzama fazlarını referansla eşleştir. Omuz, göğüs, bel, kalça, baş, bilek ve ayak tabanı birlikte çalışsın. Önce efeksiz silüet, sonra yüzey görüntüsü onaylanır.
3. **Rig ve ağırlıkları elle düzelt.** Omuz/dirsek/bilek ve diz kutupları doğru yere oturtulur; destek fazında ön/arka pençe hedefleri sabitlenir. Avuç yönü için bilek dönmesi, ayak tabanı devrilmesi ve gereken pençe/parmak açılması anahtarlanır. Kemik sayısı tek başına sorun değildir; kontrol kemikleri Blender’da kalabilir. Gereken birkaç deformasyon kemiği parmak/ayak hareketini sağlar, poligon sayısını artırmaz. Eski 23 kemik sayısı kalite hedefi sayılmaz.
4. **Önce aynı kayıt hızında karşılaştır, sonra gerçek zamana uyarla.** Yavaşlatılmış referansın pozları bu hızda eşlenir; sonra sayaç kanıtına uygun gerçek zaman ayarı yapılır. 8 m/sn yerel hareket hedefiyle adım mesafesi ve destek süresi birlikte ele alınır. Süre veya bacak ölçeğiyle tek başına sorun gizlenmez.
5. **Hareketi tek kez uygula.** Sanatçı ana klibi hareket eden sanal kökle hazırlayabilir; oyun için klip yerinde oynayan biçime çevrilir ve kök yer değiştirme bilgisi ayrı tutulur. Gerçek yer değiştirmeyi mevcut karakter kontrolcüsü yapar; animasyon kökü ikinci yatay hız eklemez. Faz ilerlemesi/adım mesafesi gerçek gidilen mesafeyle eşleşir; destek sırasında pençeler zeminde kaymaz. Düz haritada Blender IK sonucunu klibe bake etmek yeterli olabilir; canlı IK ancak gerekli olduğunda eklenir.
6. **Ayrı, ortak bir kükreme klibi yap.** Yüklenme → kolları açma → iki eli baş üstüne kaldırma/avuçları açma → göğüs/baş/çene tepe pozu → kolları indirme/toparlanma. Kullanıcının 3. videosundaki sıralama esas alınır. Ağız, çene ve diş geometrisi her gerçek kurt varlığında hazırlanıp önden kontrol edilir; Bilge’deki çene tek başına diğer kurtların yüz işini bitirmiş sayılmaz.
7. **Tüm kurtlara aynı hareketi oranlarına göre aktar.** Aynı faz/süre ve ortak animasyon kimliği korunur. Mutlak eklem noktalarını başka boydaki kurda kopyalamak yerine rest uzunluklarını koruyan uyarlama kullanılır. Model/kıyafet/silüet kimlikleri değişmez. Menü ve arena aynı tempo ayarını kullanır.
8. **Efekti ayrı katmanda ve tek renk parametresiyle kur.** El kemiğine bağlı ışık/alev, geçici dövme/gövde emisyonu, tepe vurgusu ve sönüş aynı olay çizelgesine bağlanır. Aynı hareket ve efekt biçimi bütün kurtlarda ortaktır; yalnız renk karakter paletinden gelir. Kullanıcı aksini belirleyene kadar mevcut motor paleti kullanılır: Bilge buz turkuazı `#70dfff`, Kül Tigin kızıl `#ff354d`, Alp Arslan köz/kehribar `#ffae36`, Konuralp mor `#af65ff`. Bu, karakterin kalıcı temel dokusunu boyamak değildir.
9. **Klip ile yetenek süresini ayır.** Durdurma kilidi yeni kükreme klibinin süresinden okunur; ileri basılı tutulsa da poz boyunca yatay hareket sıfırdır. Mevcut 20 sn hız +%20 / hasar +%15 / savunma +%30 ayrı kalır. Güçlü tepe efekti kısa; kalıcı bonus göstergesi/sönük el alevi model ayrıntısını örtmez. Kükremenin video boyu kadar 20 sn sürmesi gerekmez.

## Kabul ve sınırlar

- Aynı açı/ekran büyüklüğünde referans ve oyun görüntüsü yan yana; ayrıca yan, ön, arka ve üç çeyrek.
- Tam koşu döngüsünde tüm pençeler için destek/uçuş, bilek–avuç yönü, itiş, toplanma, gövde/boyun uzunluğu, zemin ve ilk/son kare sürekliliği. Yalnız kemik uzunluğu testi yeterli değil.
- Tüm kurtlarda aynı faz ve kükreme zamanlaması; renk değişimi dışında klip/efekt davranışı aynı. İlk olarak ana kurt doğrulanır, sonra oranları farklı kurtlara aktarılır.
- Koşu→durma, sıçrama→iniş/koşu, takla→koşu ve ileri tuşu basılıyken kükreme kontrol edilir. Önceki ~2 m takla/tek hedefe tek temas hasarı ve siper kontrolü korunur.
- Aynı iskelete gerçekten uyan orijinal animasyon dosyaları varsa doğrudan aktarım en doğru yoldur. Bu üç MP4 yalnız görüntü içerir; FBX/GLB animasyon kanalları/kemik eğrileri çıkarılamaz. Orijinal veri olmadan hedef, görüntüde görünen hareketi yüksek benzerlikle yeniden kurmaktır; gizlenen eklem açıları veya piksel piksel aynılık garanti edilemez. Bu sınırlama çalışmayı durdurmayı gerektirmez.
- Bu düzeltme için yeni ücretli karakter üretimi zorunlu değildir. Mevcut model, UV, üçgen bütçesi ve ortak iskelet korunup düzeltilerek çalışılabilir. Gerekli ek yüz/el topolojisi karakter başına ayrıca ölçülür; telefon performansı görülmeden garanti verilmez.

## Bu turdaki durum

**Yapıldı:** üç videonun bütün görüntü karelerinin çıkarılması/incelenmesi, yavaş oynatım kanıtı, mevcut kodla karşılaştırma, ortak kükreme/renk kararının kaydı, uygulama ve kabul yöntemi.

**Yapılmadı:** yeni koşu veya kükreme klibinin üretilmesi, rig/ağırlık düzeltmesi, oyun entegrasyonu, yeni test veya APK. Bu belge uygulama tamamlandı iddiası değildir.
