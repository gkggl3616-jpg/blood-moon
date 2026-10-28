# XFS Gezgini 0.1.0

Wolfteam'in Xenesis XFS arşivlerini salt okunur tarayan Windows masaüstü aracı.

## Kullanım

`XFS-Gezgini.exe` dosyasını açın. `XFS Aç` ile arşivi seçin. Ad/klasör aramasını ve dosya türünü birlikte kullanın. LTB, DTX ve arşivde bulunan diğer uzantılar listelenir. Ctrl/Shift ile birden fazla kayıt seçip `Seçilenleri Dışa Aktar` ile ayrı klasöre çıkarın. Arşivdeki klasör yapısı korunur. Filtrenin bütün sonuçlarını çıkarmak için ayrı düğme vardır. Liste CSV olarak da kaydedilebilir.

Sonuçlar 200 kayıtlık sayfalarla gösterilir. Sayfa değişince önceki sayfadaki seçim korunmaz; bütün filtre sonuçları için ilgili toplu çıkarma düğmesini kullanın. Mevcut çıktı dosyaları atlanır, üzerine yazılmaz. Arşiv açıldıktan sonra başka program tarafından değiştirilirse çıkarma reddedilir.

## Yanıt verme ve sınırlar

- Arşivin tamamı belleğe yüklenmez; yalnız sıkıştırılmış dosya tablosu açılır.
- Tablo okuma, filtreleme, önizleme ve çıkarma arka planda çalışır. Arama 250 ms gecikmeyle birleştirilir; eski işlerin sonuçları iptal edilir.
- Arayüzde en fazla 200 dosya satırı vardır. İlerleme mesajları seyreltilir; iptal düğmesi bloklar arasında kontrol edilir.
- Metin önizleme 256 KiB ile sınırlı; ikili dosyalarda ilk 1.024 bayt hex gösterilir. Daha büyük dosyalarda yalnız metadata gösterilir.
- XFS 1 (`XFS `) / XFS2 (`XFS2`) okuyucusu ve 4 GiB üzeri adresler desteklenir. Dosya tablosu limiti 128 MiB; kayıt limiti 1 milyon.
- 3B LTB/DTX görüntüleyicisi, model dönüştürme, repack, import ve oyun dosyası düzenleme bu sürümde yoktur. Orijinal arşive yazılmaz.
- Disk/donanım hatalarında veya desteklenmeyen paketlerde hatasız çalışma garantisi verilmez. Kullanıcının gerçek 4 GB arşivi henüz bu okuyucuyla test edilmedi.
- Windows için tek dosyalı EXE PyInstaller ile paketlenir; kod imzası yoktur. Antivirüs veya Windows güvenlik özelliklerini kapatmak gerekmez ve önerilmez.

## Geliştirme / doğrulama

Python 3.12+ ve Tkinter; uygulama üçüncü taraf Python paketi gerektirmez. Kaynaktan çalıştırma:

```
python app.py
python -m unittest discover -s . -v
```

Windows EXE üretme:

```
python -m pip install pyinstaller==6.16.0
python -m PyInstaller --clean --noconfirm --onefile --windowed --name XFS-Gezgini app.py
```

Testler sentetik ama ikili formatı doğru XFS/XFS2 arşivlerinde zlib/raw blokları, 4 GiB üzeri seyrek dosya, tablo sonu 4.881 sıfır bayt padding, path traversal/Windows geçersiz adları, symlink kaçışı, iptal, değişmiş arşiv ve mevcut dosyaları korumayı denetler. Grafik oturumundaki test 40.000 kayıt açılırken arayüz kalp atışını, filtre/paging ve önizlemeyi kontrol eder. Sentetik testler gerçek Wolfteam paket sürümünün uyumluluk kanıtı değildir.

Format araştırması: [Luigi Auriemma — xenesis.bms](https://mirror.aluigi.org/bms/xenesis.bms), [QuickBMS](https://mirror.aluigi.org/quickbms.htm). Okuyucu bu belgelenmiş paket düzenini bağımsız Python koduyla uygular; QuickBMS yürütülebilirini çalıştırmaz veya içermez.
