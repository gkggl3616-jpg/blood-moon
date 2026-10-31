# v0.1.16 — modelleri koruyan animasyon aktarımı

Kullanıcının sağladığı kaynak hareket setleri mevcut altı kurt / altı insan iskeletine uyarlandı. Ana şablonlar bütün kurtlarda ortak: dört ayak koşu T_WallDash, takla T_Specialatk. Normal yürüyüş/koşu, kükreme ve pençe vücut grubuna göre eşlendi. 54 klip güncellendi; Zeynoş sağ pençesi deri sınırı nedeniyle eski uyumlu klibi korur.

Model geometri/indeks/UV/doku/skin/bind/rest verileri, birinci şahıs fp_arms ve silahlar, kamera/kontrol/fizik kodu değişmez. İnsan formunda yalnız üçüncü şahıs HumanIdle/Walk/Run değişir. Eski HumanReady/Combat/Reload klipleri korunur. Görünüşü düzeltmek için ağırlık değiştirme veya yüzey kesme yapılmaz.

Aktarım, kaynak ve hedefin bakış/yatay eksenini eşler; kol/bacak segment yönlerini mevcut kemik uzunluklarıyla çözer. Omuz/yele, dirsek/el ve iki bacak arasında karma ağırlık taşıyan sınırlarda hareket bükülmesi uyarlanır. Hiçbir kemik uzatılmaz; yalnız kalça dikey hareketi ve eklem dönüşleri yazılır. Ortak koşu 0.4 sn, takla 1.2 sn; mevcut hareket, temas hasarı ve kamera sistemi kullanılır.

Güncelleme aşaması: tools/animation_transfer/apply.py. Çalışma zamanı GLB'lerinin özgün binary verisi byte-for-byte ön ek olarak kalır. verify.py model tanımlarını, korunmuş klipleri ve birinci şahıs/kamera/arayüz dosya özetlerini karşılaştırır. verify_models, üçüncü şahıs insan yürüme/koşusunu da sınar.

Android sürüm kodu 17. Tek APK; ek veri paketi veya internet gerektirmez. Önceki yayımlanmış sertifika SHA-256 değeri CI'da zorlanır. Fiziksel Android cihazda performans ve kullanıcı görsel kabulü yapılmış değildir; tarayıcı oyun ve kaynak kontrolleri bunların yerine sunulmaz.
