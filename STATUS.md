# v0.1.16 animasyon aktarımı durumu

- Yerel yan yana kurulabilen test APK'sı üretildi: `dist/Rogue-Blood-Moon-v0.1.16-Animasyon-Test.apk`.
- Test paket kimliği `com.roguebloodmoon.animationtest`; mevcut oyunun kurulumunu ve kayıtlarını değiştirmez.
- Altı kurtta ortak dört ayak koşusu ve takla saldırısı kullanılır. Yürüyüş, hafif koşu, kükreme ve pençe klipleri uyumlu kaynak gövde grubundan aktarılır.
- İnsanlarda üçüncü şahıs yürüyüş ve koşu aktarılmıştır. Zeynoş'un üçüncü şahıs silah tutuşu için tek omuz duruş kanalı düzeltilmiştir.
- Model geometrisi, indeks, UV, doku, skin, bind/rest verileri; birinci şahıs kol/silah varlıkları; kamera, giriş ve fizik kodu korunmuştur.
- 54 animasyon yuvası güncellendi. Çalışma zamanı modelleri doğrulandı; FPS/TPS silah tutuşu, arena hareketleri, dönüşüm, koşu, takla, hasar, arayüz ve referans koşu testi geçti.
- APK imzası doğrulandı ve APK içindeki 13 GLB'nin yerel doğrulanmış modellerle byte eşitliği kontrol edildi. Fiziksel Android cihazda kurulum testi yapılmadı.
- Kaynak katalog 795 tekil animasyon, beş kategori ve 65 tam kurt hareket seti içerir; bütün GLB'ler Khronos doğrulamasından hatasız geçti.
- Ortak kaynak hareketler ayrıca üç tekil, geometrisiz GLB olarak teslim edildi: koşu, takla saldırısı ve yürüyüş. Rogue: Blood Moon'un önceki animasyonları bu küçük pakete eklenmedi.
- Genel GitHub deposuna yükleme ve mevcut uygulamayla aynı imzayı kullanan güncelleme APK'sı, açık dış yükleme onayı bekliyor.
