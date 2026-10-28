# v0.1.14 — reddedilen kükremenin düzeltilmesi

Son video **bizim oyunun hatalı kükremesidir**, hedef değildir. `Screenrecorder-2026-10-28-07-19-41-357.mp4`: 1,811 saniye, 41 çözümlenen görüntü karesi incelendi. Hedef önceki üçüncü videodaki, yaklaşık 1,32–2,44 saniye arasındaki tam kükremedir. Referans dosyaları ve önceki inceleme korunur.

v0.1.13'te yalnız iki eli başın üstüne çıkaran bir hedef kurmuştum. Kollar fazla düz ve dar yükseliyor, bilek–dirsek–omuz silüeti hedefteki güçlü bükülmeyi taşımıyordu. Küçük hazırlık hareketi ve genel el yüksekliği testi bu sorunu yakalamadı. Önceki test başarısı hedef animasyonun kabul edildiği anlamına gelmez; kullanıcı bu sonucu reddetti.

## Değişiklik

- Hazırlık kalça alçalması boyun %1,2'sinden %4'üne çıkarıldı; dizler sabit ayak hedeflerine göre bükülür. Bu kaynak mesh veya kemik ölçeğini değiştirmez.
- Dirsek kutupları dışarı taşındı. Baş üstü el hedefi artık neredeyse düz kolun %91 uzanması yerine yaklaşık %73 kol mesafesine kurulur; kısa kollu modellerde baş üstü sınırı ve gövdeye uzaklık birlikte değerlendirilir.
- Ön kollar içe eğilir, pençe doğrultusu da hafif içe döner. Eller gövdeden gereksiz uzağa, öne uzanmaz. Göğüs ve boyun geriye açılır; yalnız başı yatırma kullanılmaz.
- Poz ve efekt fazları bütün kurtlarda ortak, süre yine 1,2 saniye. 20 saniyelik bonus ve karakter renkleri korunur. Geometri, UV, kaynak bekleme duruşu, koşu ve takla değiştirilmedi; yeni ücretli üretim yok.
- Yeni kontroller gerçek dışa aktarılmış GLB ve gerçek WebGL oyununda dirsek bükülmesinin 65 dereceden fazla olmasını ve dirseğin bilekten dışarıda kalmasını arar. Eski düz kol çözümü bu kontrolden geçmez. Kemik uzunluğu, kaynak biçimi, ağız, taban ve koşu kontrolleri de sürer.

## Kanıt ve sınırlar

[Kullanıcının reddettiği poz](verification-v014/user-rejected-v013.jpg), [yeni arka poz](verification-v014/WolfRoar-50-back.png), [yeni yan poz](verification-v014/WolfRoar-50-side.png). Açılar ve görüntüleme ortamları farklıdır; bu resimler piksel ölçümü veya birebir eşleşme kanıtı değildir. Hazırlık, açılma ve toparlanma kareleri de aynı klasörde tutulur.

Bu çalışma görünen hareketi yeniden kurar; referans oyunun özgün animasyon dosyaları elimizde değildir. Matematiksel kabul sınırları tek başına sanatsal kaliteyi kanıtlamaz. Kullanıcının onayı yerine geçecek bir “aynısı oldu” iddiası yoktur. Diğer insan modellerinin önceki açık işleri bu odaklı düzeltmeyle tamamlanmış sayılmaz. Fiziksel telefon testi yapılmadı.

Yerel kaynak/mesh/klip kontrolleri geçti. Dört kurtta gerçek oyun testi de geçti: bükülü/dışarıdaki dirsekler, baş üstü eller, hareket kilidi, efekt renkleri ve bonuslar kontrol edildi. [Gerçek oyun görüntüsü](verification-v014/actual-game-bilge.png). Temiz yayın testleri ayrıca kaydedilir. Teslim v0.1.14, versionCode 15; önceki sertifika korunarak tek APK üretilir.

## Yayın doğrulaması

[TEK APK v0.1.14](https://github.com/gkggl3616-jpg/blood-moon/releases/download/prototype-v0.1.14-20/Rogue-Blood-Moon-v0.1.14.apk). [Temiz yayın çalışması](https://github.com/gkggl3616-jpg/blood-moon/actions/runs/40632494108) başarılı: envanter, genel arena, dört kurt için yeni kol pozu/koşu/efekt ve paket testleri geçti. Yayımlanan dosya yeniden indirildi; sürüm kodu 15, CRC sağlam, 52 çalışma zamanı dosyası kaynakla birebir aynı, sertifika v0.1.13 ile aynı. [Paket raporu](verification-v014/published-apk.json). Görsel birebirlik kullanıcı tarafından henüz kabul edilmedi; fiziksel telefon testi yapılmadı.
