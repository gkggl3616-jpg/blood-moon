# Bilge Kağan + dört iskelet ailesi — yalnız karakter dosyaları

Bu ZIP oyun kodu, JS, Python, shader kaynak dosyası, APK veya hazır Godot projesi içermez. Model, doku, iskelet/animasyon ve statik Blender çalışma sahneleri içerir. Karahan modeli bu pakette yoktur.

## Bilge Kağan

- `BilgeKagan/Kurt.glb`: güncel oyun kurdu; 42 kemik, 72 kaynak klip; kaplamalar gömülü.
- `BilgeKagan/Insan.glb`: güncel oyun insanı; 47 kemik, 11 kullanılan klip; kaplamalar gömülü.
- `BilgeKagan/Dokular`: güncel GLB'lerden ayrıca çıkarılan görüntüler. GLB'nin açılması için ayrıca bağlamak gerekmez.
- `BilgeKagan/Calisma`: statik Blender çalışma dosyaları; tüm kliplerin Blender sahnesine kurulmuş olduğu iddia edilmez. Animasyonlu son kopyalar GLB'lerdir.
- `BilgeKagan/Kaynak`: Bilge'nin kaynak model/hareket LTB dosyaları ve kaynak DTX referansları. Güncel özgün Bilge görünüşü DTX değil GLB içine gömülü görüntülerdir; kaynak DTX giysisiyle karıştırma.
- `BilgeKagan/Dovme` ve `BilgeKagan/Ses`: dövme atlası/politikası ve mevcut kükreme sesi. Bunlar oyun kodu değildir.

## Seçtiğimiz dört ayrı kaynak iskelet

| Klasör | Kemik | Ham klip | Dosyalar |
|---|---:|---:|---|
| `DortModel/Buz-40` | 40 | 68 | `Model.glb`, `Govde.ltb`, `Hareketler.ltb` |
| `DortModel/Kan-54` | 54 | 76 | `Model.glb`, `Govde.ltb`; hareketler aynı LTB içinde |
| `DortModel/Koz-42` | 42 | 72 | `Model.glb`, `Govde.ltb`, `Hareketler.ltb` |
| `DortModel/Golge-58` | 58 | 83 | `Model.glb`, `Govde.ltb`; hareketler aynı LTB içinde |

Dört GLB, gerçek kaynak geometri/UV/skin/kemik ve ham animasyonları taşır. Malzemeleri nötr gri anatomi önizlemesidir; dört yeni kostümlü karakter üretildiği iddia edilmez. Kaynak dövme kartları bu dört anatomi önizlemesine takılı değildir. Bilge'nin güncel oyun modelleri kendi gerçek kaplamalarını korur.

Godot/Blender'a GLB'leri aktar. LTB ve DTX standart Godot içe aktarıcısının doğrudan desteklediği biçimler değildir. Alt/üst gövde kliplerini birleştirme, fiziksel ilerleme, yer teması ve FX oynatma modellerin dışında bir uygulama gerektirir; kullanıcı oyun kodu istemediği için bu pakete konulmadı. Ham tek bir klip, oyun davranışının tamamı değildir. Tek anahtarlı hareketler statik poz olabilir.

## Köken ve bütünlük

Dosya/klasör adları okunabilir şekilde sadeleştirildi; kaynak içerik bize ait özgün üretimmiş gibi gösterilmedi. Dört referans gövdenin ve kaynak hareketlerin kökeni kullanıcının sağladığı üçüncü taraf Wolfteam varlıklarıdır. Özgün görünüş çalışması ve kaynak geometri/animasyon ayrı şeylerdir. Kaynak karşılıklar `DortModel/KOKEN-VE-ANIMASYONLAR.json` içindedir. İsim değişikliği sahiplik/lisans sağlamaz.

`DOSYA-MANIFESTOSU.json` her dosyanın boyutunu ve SHA-256 değerini içerir. Bu teslim için yeni ücretli üretim veya oyun/APK değişikliği yapılmadı.
