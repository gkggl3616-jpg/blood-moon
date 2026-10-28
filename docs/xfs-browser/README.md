# XFS Gezgini — uygulama ve doğrulama kaydı

2026-10-28. Kullanıcı donan XFS Studio Pro yerine LTB/DTX ve diğer türlerde filtreleme, arama ve akıcı kullanım istedi. Android oyununa dokunmadan ayrı `desktop/xfs_browser/` uygulaması geliştirildi. Windows dağıtımı ayrı `tools/xfs-browser` dalında üretildi; Android sürümü veya imzası değiştirilmedi.

## Yapılanlar

- Salt okunur XFS 1/XFS2 tablo okuyucusu, 48-bit konumlar / 4 GiB üzeri dosya desteği; zlib ve ham bloklardan seçerek çıkarma.
- Dosya uzantısı filtresi: arşivde bulunan bütün uzantılar. Tam yol/ad araması; birden fazla kelime birlikte eşleşir, büyük/küçük harf duyarsız.
- 200 satırlık sayfalama; bütün 40.000 kayıt için arayüz bileşeni oluşturulmaz.
- Arka plan işleri, 250 ms arama gecikmesi, eski sonuçları reddetme, ilerleme ve iptal.
- Ctrl/Shift ile çoklu seçim; seçilenleri veya filtredeki bütün sonuçları çıkarma; CSV dosya listesi kaydetme.
- Metadata, sınırlı metin/hex önizleme. Orijinal klasör yapısı korunur; mevcut dosyalar atlanır.
- Bozuk dosya/boyut/yol sınırları, Windows geçersiz adları ve çıktı klasöründen kaçan yollar reddedilir.
- Kapatırken aktif çıkarma iptal edilir; yarım dosya temizliği tamamlanmadan arayüz kapanmaz.
- Python gerektirmeyen tek Windows EXE paketi ve paketlenmiş uygulamayı açıp kapatan derleme testi.

## Doğrulananlar

Yerel grafik oturumunda 14 test geçti: XFS/XFS2, üç blok biçimi, çok bloklu 1,5 MiB model, boş dosya, 4 GiB üzeri seyrek arşiv, 4.881 sıfır bayt tablo padding, bozuk zlib, aşırı açılmış boyut, iptal, değişmiş arşiv, mevcut dosya koruma, geçersiz yollar/symlink, CSV, önizleme sınırı, filtre/sayfalama/arayüz kalp atışı.

Son yerel örnek: 40.000 kaydın tablo okuması 142,8 ms; LTB filtresi 105,0 ms; arayüzde en fazla 200 satır; en büyük kalp atışı aralığı 52 ms. Bunlar ölçüm örneğidir, süre garantisi değildir. İlk Windows CI ölçümü: tablo 222,8 ms, filtre 114,0 ms, arayüz kalp atışı en büyük aralık 63 ms. Windows symlink testi yetki gerektirdiğinden atlanır; GUI testi Windows'ta çalışır.

Ek aktif kapatma denemesinde worker gerçekten dosya çıkarırken pencere kapatıldı: iptal edildi, `.part` ve bitmemiş hedef dosya kalmadı. `test-active-close.py` bu denemenin kaydıdır; çalıştırmak için içindeki kaynak yolu uyarlanabilir.

## Açık kalanlar / kapsam sınırı

Kullanıcının gerçek yaklaşık 4 GB `wolf.xfs` dosyası henüz alınmadı ve yeni okuyucuyla denenmedi. Test arşivleri format araştırmasına göre sentetik üretildi; uyumluluk bütün paket sürümleri için garanti değildir. Gerçek arşivden önce bir LTB çıkarılıp mevcut yüklenen LTB'nin SHA-256 değeriyle karşılaştırılmalı. Performans kullanıcının bilgisayarında ölçülmedi.

3B LTB/DTX önizleme, model dönüşümü, düzenleme/import/repack ve kaynak uygulamanın bütün özellikleri henüz yok. Bu sürüm, filtreleme/inceleme/çıkarma içindir. EXE kod imzalı değildir; güvenlik özelliklerini kapatmaya yönelik talimat yoktur.

Kod: [uygulama](../../desktop/xfs_browser/app.py), [okuyucu](../../desktop/xfs_browser/xfs_core.py), [kullanım](../../desktop/xfs_browser/README.md). Windows CI: `.github/workflows/xfs-browser.yml`.

## Teslim

[Windows EXE indir](https://github.com/gkggl3616-jpg/blood-moon/releases/download/xfs-browser-v0.1.0/XFS-Gezgini.exe). Boyut: 11.409.927 bayt. Yerel indirilen EXE'nin SHA-256 değeri Windows paket kaydıyla eşleşti: `de6cd9bf52959f06927dd3be55ef22739339a04c4dec47c9bbc2cdc7de41b0a5`.

Son Windows derlemesi ve paketlenmiş EXE açılış testi: [40719305472](https://github.com/gkggl3616-jpg/blood-moon/actions/runs/40719305472), başarılı. Sürüm [0.1.0](https://github.com/gkggl3616-jpg/blood-moon/releases/tag/xfs-browser-v0.1.0) ön sürüm olarak yayımlandı; Android yayınları değiştirilmedi. Doğrulanan kaynak commit'i `2099d747cfbd841ef58d78134e179307ee01a6f3`. Ayrıntılı teslim kaydı `release.json`.
