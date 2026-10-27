# v0.1.13 — üç video sonrası koşu / ortak kükreme

Kullanıcının “tamam başla kodlamaya” onayıyla önceki inceleme uygulandı. Kaynakların tamamı, kare sayıları ve ağır çekim teşhisi [inceleme dosyasında](uc-video-kosu-kukreme-analizi-20261028.md). Yeni ücretli Meshy üretimi veya kredi harcaması yok.

## Uygulanan değişiklikler

- `reference_motion.py`: ön uzanma, ön destek, gövde altına toplanma, arka destek/itiş ve süzülme fazlarından oluşan ortak koşu. Sağ/sol uzuvlar hafif faz farkıyla çalışır. Gövde, boyun ve baş birlikte yönlenir; kaynak kemik uzunlukları ölçeklenmez.
- 8 m/sn temel hız, 0,53333 sn klip ve 4,26667 m çevrim mesafesi. Bunlar yerel oyun ayarlarıdır; videodan ölçülmüş dünya mesafeleri değildir. Kayıt 2'nin yavaş oynatımı doğrudan oyun temposuna çevrilmedi.
- Eski `8/5.6` çarpanı kaldırıldı. Arena animasyon zamanı = gerçek alınan mesafe / çevrim mesafesi. Menü de aynı klip/mesafe sözleşmesini kullanır. Başlangıç +%5 hız rünüyle 8,4 m/sn ve ortalama 1,05 klip hızı beklenir; eski 1,5 çarpanı yoktur.
- Kaynak kol oranları farklı kurtlara aynı fazlar uyarlanır. Kısa kollu kaynaklarda kemik uzatmak yerine gövde eğimi ve göğüs yüksekliği ayarlanır. Dört pençe için gerçek deforme yüzeyden taban yüksekliği kalibre edilir.
- Destek sırasında avuç ve parmak tabanı ön kolun dönüşüyle ezilmez. İki parmak grubu/el ve bilek dönüşü eklenir; mevcut geometri korunur. El ağırlıkları etek/kumaştan dışlanır. Dövme ağırlıkları gövdeden barycentrik aktarılır.
- 30 Hz anahtarların arasındaki FK ara değerleme pençeyi birkaç santimetre aşağı sarkıtıyordu. 60 Hz dışa aktarım bu hatayı azaltır; süreler değişmez. Bu bir telefon FPS garantisi değildir.
- Ortak 1,2 sn kükreme: kısa hazırlık/çökme → kolları açma → iki eli başın üzerine kaldırma ve pençeleri açma → göğüs/baş kaldırma → kontrollü geri dönüş. Alt çene gerçek kemikle açılır; dört kurtta da ağız içi ve diş geometrisi vardır. Son üç modelde ek iç ağızlar toplam 320 üçgendir.
- Efekt hareketi, yayılımı ve ana patlama fazı ortak; yalnız karakter rengi farklıdır. Bilge `#70dfff`, Kül Tigin `#ff354d`, Alp Arslan `#ffae36`, Konuralp `#af65ff`. Eski sabit mor istek bu son kararla değişmiştir. En fazla 72 el parçacığı ve mevcut kısa pençe izi havuzu korunur. Ana patlama fazı kükremede yalnız bir kez tetiklenir; gövde parlaması düşük tutulur.
- Kükremede basılı yön tuşu yatay hareket üretmez. 20 saniyelik hız ×1,20 / hasar ×1,15 / savunma ×1,30 hesabı değişmez. Klip bitişi gerçek klip süresinden alınır.
- Özgün beyaz Bilge gövdesi, yüzü, kürkü, kıyafeti, buz şekli ve UV'si korunur. Reddedilen koyu/düz gövde yeniden kullanılmadı. Menü ve arena aynı çalışma zamanı GLB'sini açar.

## Korunan sistemler

Yaklaşık 2 m / 0,8 sn takla ve tek hedefe tek temas hasarı; siper engeli; koşudan sıçrama ve havada takla; insan FPS/kurt TPS dönüşümü; yön düğmeleri, ileriye çift basma ve simgeli yuvarlak aksiyonlar; bakış yönü/hassasiyet; gerçek gölge, Net/Dengeli çözünürlük; iz sürme; satın alma, insan/kurt donanımı, sürükle-bırak, gerçek dövme bonusu ve eski kayıtların göçü.

Dövme hesabı hâlâ `temel × (1 + karakter/100 + uygulanabilir dövmeler toplamı/100) × aktif çarpan`. Bağımsız +%240 dövme, 100 tabanda 340 verir; +%20 pasifle 360 ve hasar kükremesiyle 414. Genel 180 tavanı yoktur. Eşya tablosu önceki [uygulama kaydında](guncelleme-v012.md) geçerlidir; bu sürüm yeni eşya eklemez veya sahipliği silmez.

## Ölçüm ve kabul kontrolleri

`verify_reference_motion.py` gerçek dışa aktarılmış GLB'leri yeniden açar. Dört kurtta kaynak gövde farkını, kumaşa yanlış el ağırlığını, destek fazındaki gerçek mesh tabanlarını, sanal kök hareketiyle temas kaymasını, sabit gövde/uzuv uzunluklarını, baş üstü elleri, parmak/çene hareketlerini ve ağız geometrisini denetler. Örneklenen destek noktalarında kayma 0,00066–0,00275 m; taban yüksekliği −0,00633–+0,00785 m aralığında. Bunlar belirli faz örnekleridir; bütün telefonlarda sıfır hata iddiası değildir.

Kaynak Bilge gövdesinin bekleme başlangıcında en yüksek koordinat farkı yaklaşık 0,0000014 m; kontrollü nefes sırasında yaklaşık 0,00208 m. Koşunun 33 örneğinde gövde/uzuv uzunluk farkı oranı 0,000008'in altında. Dört kurtta kükreme tepesinde el kemikleri baş kemiğinin 0,17–0,32 m üstünde, çene açılması yaklaşık 0,60 radyandır.

`verify_motion.py` bütün koşu/takla/sıçrama/kükreme/bekleme kliplerinin deforme mesh sınırlarını ve döngü dikişini kontrol eder. `verify_source_fidelity.py` kaynak beyaz Bilge gövdesini ve bekleme/çeneyi ayrıca doğrular. `capture_model_review.py` gerçek GLB'den ön/yan/arka/üç çeyrek bekleme, sekiz koşu fazı, yedi takla fazı ve üç kükreme pozu üretir.

`verify_reference_arena.py` gerçek WebGL oyununda dört karakterin mesafe/zamanını, çevrim fazı/mesafe eşleşmesini, baş üstü ellerini, yayılan parçacığın gerçek RGB rengini, tek ana patlamayı, basılı yönde duruşu, bonus katmanlarını ve menü temposunu test eder. Genel `verify_arena.py` ve `verify_ui.py` de geriye dönük kontrollerdir. Yerel kontrollerin tamamı geçti: genel arena, gerçek dört karakterli hareket/efekt ve envanter/kayıt/satın alma/fare–dokunma sürüklemesi. Ölçümler [doğrulama klasöründe](verification-v013/README.md). Yayın paketinin imza/varlık kontrolü ayrıca kaydedilir.

## Bütçe ve açık işler

| Model | Toplam üçgen | Kemik |
|---|---:|---:|
| Bilge kurt | 14.457 | 27 |
| Kül Tigin kurt | 9.918 | 27 |
| Alp Arslan kurt | 9.915 | 27 |
| Konuralp kurt | 9.973 | 27 |
| Bilge insan | 9.000 | 27 |

Hareket videodaki ana pozlardan yeniden yazıldı; referans oyunun orijinal animasyon dosyaları çıkarılmadı. Piksel piksel aynı hareket veya final sinema kalitesi iddia edilmez. Mevcut kürk kümeleri, kıyafet yüzeyleri, yüz ağırlıkları ve geçişlerin elle sanatçı cilası hâlâ yapılabilir; bunlar efektle gizlenmiş “bitmiş yeni model” olarak sunulmaz. Diğer üç insan formu hâlâ 2B konsepttir. Fiziksel Android kurulumu, GPU profili, ısınma ve FPS bu ortamda ölçülmedi.

Teslim hedefi v0.1.13 / versionCode 14, tek imzalı bağımsız APK. Yayın CI'sı önceki sürümün `af43be4b…98633` sertifikasını zorunlu tutar; farklı yerel anahtarla üretilmiş paket teslim edilmez. Yayın bağlantısı ve indirilmiş dosyanın kontrolleri ayrıca kaydedilir.

## Yayın sonucu

[TEK APK v0.1.13](https://github.com/gkggl3616-jpg/blood-moon/releases/download/prototype-v0.1.13-19/Rogue-Blood-Moon-v0.1.13.apk) — 62.292.240 bayt, versionCode 14. [Temiz CI çalışması](https://github.com/gkggl3616-jpg/blood-moon/actions/runs/40596165659) başarılı; envanter, genel arena, yeni dört karakterli hareket/efekt kontrolleri ve imzalama geçti.

Yayımlanmış dosya yeniden indirildi: ZIP CRC sağlam; 52 çalışma zamanı dosyasının her biri kaynakla bayt bayt aynı; dört kurt ve Bilge insan GLB’leri içeride. Sertifika v0.1.12 ile aynı: `af43be4b6ee4d5b2e1feca6da3df36805a7b10bbb56b1f884136054ef7f98633`. APK SHA-256: `8ea24111d90fef1fcea9aee83e09c5f0771d43332d6b7ebf48c10976599d3bdd`. [Paket raporu](verification-v013/published-apk.json). Fiziksel telefon testi açık kalır.
