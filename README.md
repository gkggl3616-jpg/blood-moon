# Rogue: Blood Moon — Android Prototype 0.1.2

Yatay Android ekranı için menü ve harita konsepti prototipi.

v0.1.2: Açılış videosu otomatik başlar ve bitince lobiye geçer. Görünür ekran alanına göre ölçekleme, sabit viewport ve Android çentik/sistem çubuğu güvenli alanları eklendi.

## v0.1.2 değişiklikleri

- Ekranın genişliğine yayılan lobi; yan boşluklar kaldırıldı.
- Menüyle aynı ölçekte, tek sayfaya sığan ayarlar penceresi.
- Sekmeli etkinlik merkezi: görevler, örnek kredi ödülleri, deneyim bonusları ve kozmetik avantajlar.
- Teçhizat ekranı: üç set, insan/kurt önizlemesi ve dört boş ekipman yuvası.
- Set ve form tercihleri cihazda saklanır. Silahlar ve gerçek ödül sistemi bu prototipte yoktur.

## Bu sürüm

- Asker/kurt açılış görseli ve isteğe bağlı özgün 5 saniyelik Higgsfield animasyonu.
- Sesli lobi, örnek etkinlik kartları ve oda seçimi.
- Kanlı Ay, İlk Av ve Sürü Kapışması etkinlik açıklamaları.
- Sığınak 07 harita konsepti, üstten rota planı ve büyütme.
- Ses açma/kapatma ve kalıcı ses düzeyi ayarı.
- Android 8.0 ve üzeri; yatay tam ekran; internet izni gerektirmez.

Bu APK bir menü prototipidir. 3B harita, FPS kontrolleri, dönüşüm, çevrimiçi maç,
hesap, ödül veya satın alma sistemi içermez. Oda dolulukları ve etkinlikler örnektir.
İleride oynanış Unity projesinde geliştirilebilir; mevcut arayüz akışı onun referansıdır.

## GitHub Actions ile APK

`main` dalına gönderim veya **Actions → Android APK → Run workflow** derlemeyi başlatır.
İş bitince **Rogue-Blood-Moon-v0.1.2-APK** çıktısını indirin, ZIP içindeki
`Rogue-Blood-Moon-v0.1.2-debug.apk` dosyasını Android telefonda açın.
Gerekirse dosyayı açan uygulama için "Bu kaynaktan izin ver" seçeneğini etkinleştirin.
Bu geliştirme imzalı APK Google Play sürümü değildir.

## Yerel derleme

Java 21, Python 3 ve ilk araç indirmesi için internet gerekir:

```sh
python tools/bootstrap_android.py
python tools/build_apk.py
```

Google SDK arşivleri resmî depo manifestindeki SHA-1 ile doğrulanır.
Derleme sonunda Android imzası doğrulanır, APK SHA-256 özeti kaydedilir.
Yerel geliştirme anahtarı projenin üst klasöründe oluşturulur ve depoya eklenmez.
GitHub Actions her temiz çalışmada yeni bir geliştirme anahtarı üretir; farklı
çalışmaların APK'ları arasında güncelleme için eski sürümü kaldırmak gerekebilir.
Üretim imzası gelecek sürümlerde ayrıca yapılandırılmalıdır.

```sh
python -m pip install playwright==1.58.0
python -m playwright install chromium
python tools/verify_ui.py
```

Testler lobi geçişini, etkinlikleri, harita seçimini, geri gezinmeyi, kalıcı ses
ayarlarını ve farklı ekran oranlarını gerçek Chromium içinde kontrol eder.
Fiziksel Android cihaz testi ayrıca yapılmalıdır.

Görseller, açılış videosu ve giriş sesi bu proje için Higgsfield üzerinden üretilmiştir.
Kısa menü tıklama ve geri sesleri özgün sentezlenmiş WAV dosyalarıdır.
