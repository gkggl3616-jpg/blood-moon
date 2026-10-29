# v0.1.16 sonrası çalışma sırası

Bu sürüm oynanabilir test paketidir. İnsan bilek/kıyafet deformasyonu ve tam dört ayak koşusu tamamlanmış kabul edilmez.

1. **Telefonda kısa kabul turu.** Önceki APK üzerine güncellemeyi dene; uygulama verisini silmeden sahiplik/kredi/kuşanmayı kontrol et. Bilge insan/kurt, koşu→sıçrama→takla→iniş ve ileri basılıyken kükremeyi dene. Telefon modeli ve karşılaşılan sorunun kısa ekran kaydı test kanıtı olarak tutulur.
2. **Bilge insan ağırlıklarını düzelt.** Kıyafet, bilek, parmak ve gövde grupları yeni geometri üzerinde ayrılır. Aynı kaynak anahtarlarıyla ön/yan/arka ve bütün hareket evrelerinde çekilme/ince uzuv/kopuk yüzey kontrol edilir. Salt efekt veya ışıkla kapatılmaz. Yeni model üretimine kredi harcamadan mevcut geometri ve skin düzeltilir.
3. **Bilge kurt hareket ve efekt kabulü.** Kaynak kemikler/anahtarlar korunur. Dört ayak koşu kaynağı arşivde ayrıca tespit edilir; Ice40'ın iki ayaklı koşusu dört ayaklı diye adlandırılmaz. Uyumlu kaynak yoksa iskelet/animasyon değiştirme kararı açıkça yeniden değerlendirilir; gizli retarget yapılmaz. Ayak temasından stride ölçülür. Takla/zemin, çene, gerçek ele bağlı alev/pençe izi ve üç dövme yüzeyi birlikte kontrol edilir.
4. **Cihaz performansı ve görsel netlik.** Tek tek kalite profilleri, uzun oturum, karakter değiştirme ve arka plana alma ölçülür. CPU/GPU/bellek/draw-call kanıtıyla iyileştirme yapılır; test edilmemiş FPS/çökmez garantisi verilmez.
5. **Genel model tiplerini yay.** Bilge kabul edilince Kül Tigin, Alp Arslan ve Konuralp sırayla özgün silüet/kıyafet/elementleriyle uygulanır. Model türü karakter kimliğinden ayrı kalır; her tipe kendi kaynak kükremesi/efekt olayı bağlanır. Source DTX giysileri oyuna taşınmaz. Yeni ücretli üretim gerçek fiyatı belirtilip ayrıca onaylanır.
6. **Haritayı genişlet.** Düz test alanı hareket ve temas kabulü bitene kadar korunur. Sonra tek küçük oynanış haritası yapılır; yeni harita performans ve siper/hasar testlerini yeniden geçer. Envanter ve kayıt gerilemeleri her sürümde kontrol edilir.

Her aşama MD kayıtları, aynı GLB'nin menü/arena kanıtı ve gerektiğinde yeni imzalı tek APK ile kapanır. Bir sonraki aşamaya geçmek öncekinin açık kalite kusurunu tamamlandı saymaz.
