# Rogue Blood Moon — üretim standardı ve kalıcı önlemler

Bu dosya her yeni model, animasyon ve silah işinden önce okunur. Buradaki sayılar ve kurallar
`tools/verify_models.py` tarafından CI'da zorlanır: kurala uymayan model APK'ya giremez.

## 1. Poligon bütçesi (sabit, 31.10.2026 kullanıcı kararı)

| Varlık | Üst sınır (üçgen) | Üretim hedefi | Not |
|---|---|---|---|
| İnsan gövdesi (`Body_human`) | 35.000 | 30.000–35.000 | Birinci şahıs kol kesiti (`FPArms_human`) gövdenin alt kümesidir, ayrıca sayılır |
| Kurt gövdesi (`Body_<kurt>`) | 30.000 | 25.000–30.000 | Boynuz, pelerin vb. eklentiler dahil |
| Silah (tüfek, tabanca, bıçak) | 35.000 | 20.000–35.000 | Şarjör ayrı parça olsa da toplam sayılır |
| Bomba (parça, sis) | 10.000 | 6.000–10.000 | Pim halkası dahil |
| Birinci şahıs eldiveni (karaktere özel) | 12.000 / el | 6.000–10.000 | Parmak kemikli; gövde bütçesinden ayrı |

- Bütçeyi aşan model **inceltilir**, kesilip atılmaz. İndirgeme yalnız saç ve kafa arkasına uygulanır.
  Yüz, eller, gövde ve giysi korunur; yüzün UV'si bozulursa ifade dağılır. Bu durum Zeynoş'ta ölçüldü ve
  yüz kutusu korumaya alındı. Araç: Blender Decimate (Collapse), korunan köşeler ağırlık grubuyla dışarıda
  tutulur. Sonra ağırlık ve normal en yakın özgün köşeden aktarılır, açık kenar sayısı karşılaştırılır.
- Meshy gövdelerinde el başına ~400 üçgen var. Birinci şahısta görünen ayrıntı karaktere özel
  eldivenden gelir (aşağıdaki satır). Gövde indirgemesi elleri asla azaltmaz.
- Dokular 4K üretilir, oyuna 2K JPEG/PNG olarak girer.

## 2. Üretim promptu (yeni karakter / silah için ana talimat)

```text
GÖREV: Rogue Blood Moon için yeni varlık üret (karakter: insan+kurt, ya da silah/bomba).

KAYNAK VE TASARIM
- Yalnız kullanıcının onayladığı görselin birebir aynısı. WolfTeam'e ait hiçbir şey kullanılmaz.
  Başka oyunların ekran görüntüleri yalnız genel kamera/kavrama fikri içindir.
- Karakter görselleri T-pozda, düz açık gri arka plan, tam boy, ön görünüş.
- Kollar ve eller boş bırakılmaz: her insan formunda karaktere özel bir kol/el aksesuarı modelin parçası
  olarak üretilir (31.10.2026 kullanıcı kararı). Eldiven aksesuardır, ayrı parça olarak sonradan eklenmez:
  Zeynoş: kalp oyuklu siyah deri eldiven; Aysel: siyah dantel parmaksız eldiven; Bilge Kağan: taktik
  parmaksız eldiven (sert eklem korumalı); Köz Bey, Kara Han, Zebani: eldivensiz ama bileklik / sargı /
  zırhlı kolluk gibi karaktere uygun bir kol aksesuarı. Parmaklar eldivenin içinden ayrı ayrı okunmalı.
- Kurt formlarında kollar ve sırttaki parlayan bölgeler korunur (buz, köz, lav, ay ışığı, kalp kristali):
  yeniden üretimde eski modeldeki parlama yerleri ve renkleri aynen istenir.
- Silah görselleri tam yandan ortografik, namlu/bıçak SAĞA bakar, beyaz arka plan, marka/logo/yazı yok.

POLİGON (zorunlu)
- İnsan 35.000, kurt 30.000, silah 35.000, bomba 10.000 üçgen üst sınır.
- Meshy: target_polycount = insan 33000, kurt 28000, silah 30000, bomba 8000; should_remesh=true,
  enable_pbr=true, texture_resolution=4k. Tripo: face_limit aynı değerler, texture_quality=detailed.
- Üretimden sonra üçgen sayısı ölçülür; aşan model Blender Decimate ile hedefe indirilir.

KREDİ
- Higgsfield: her istekten önce get_cost; karakter başına ~15 kredi.
- Meshy: toplu işten önce /balance okunur, maliyet hesaplanır, istekler sırayla gönderilir.
- Her bilgisayar işi KENDİ ADINDA ayrı plan dosyası okur; iş başlamadan önce plan dosyası
  bilgisayarda açılıp içeriği doğrulanır.

İSKELET VE AĞIRLIK (tools/meshy hattı)
- Meshy otomatik iskelet + build_game.py. Kemik adları motorun adlarıdır.
- Kol ile bacak (veya iki kol) arasında köprü üçgeni varsa silinip BIRAKILMAZ: iki yan ayrı kapatılır.
- Pelerin / kuyruk / saç köşeleri gövde payını yalnız gövde kemiklerinden (Hips, Spine, Chest,
  Neck, Head, Clav) alır; kol ve bacak kemiklerinden ağırlık ALAMAZ.
- Elle eklenen sert parçalar (boynuz, kolye, plaka) tek kemiğe %100 kilitlidir ve yüzeye 2 cm gömülür.
- Birinci şahıs kolu: yalnız Clav/UpperArm/Forearm/Hand/parmak ağırlığı; kol kemiğinden uzak deri girmez.
- İnsan gövdesi üçüncü şahısta kol IK'sı ile silaha yerleştirilir: ön kol/el köşesi aynı anda kalça veya
  bacak kemiğine bağlı olamaz (yoksa el kalçaya lastik gibi uzar). build_game bunu uygular, test yakalar.
- Uzama testi her köşede en fazla 4 etkiyle (sevk edilen ağırlıkla) yapılır.

SİLAH
- Her silah için yandan görünümden okunan noktalar art/3d/weapons/sockets.json'a yazılır:
  kabza (grip_r) ve kabza yönü, tetik, el kundağı/tutamak (grip_l), nişangah hattı, namlu ucu,
  şarjör kutusu (ayrı parçaya bölünür), bombalarda pim halkası.
- Sağ el kabzayı kavrar, işaret parmağı tetikte; sol el el kundağını/tutamağı kavrar.

KABUL (hepsi geçmeden teslim yok)
- tools/verify_models.py: bütçe, uzayan üçgen, yeni delik, pelerin/kuyruk/saç ağırlığı, FP kolu.
- tools/verify_fp.py: 6 karakter × tüfek/tabanca × düz/yukarı/aşağı; eller kabzada.
- verify_ui / verify_arena / verify_reference_arena.
- Kullanıcıya oyun içi görüntü gösterilir; onay olmadan APK yok. APK çıkınca dosya + release linki.
```

## 3. Kalıcı önlemler — pelerin ve kurt gövdesindeki boşluklar

### 3.1 Kurtlardaki boşluklar (şeffaf delikler)
- **Kök neden:** Üretilen modellerde el uyluğa yapışık geliyordu. Yırtılmayı önlemek için aradaki
  köprü üçgenleri silindi, yerleri kapatılmadı. Kurt Kral'da 194, diğer kurtlarda ~90 delik oluştu.
- **Önlem 1 — kapatma:** `build_game.cap_holes` silinen bölgenin açık kenar halkasını kol tarafı ve
  bacak/gövde tarafı olarak ayırır, her tarafı kendi kemiğine bağlı yamayla kapatır.
  UV dikişlerinde ayrılmış köşeler konumla birleştirilerek (weld) gerçek topoloji üzerinde çalışılır.
- **Önlem 2 — test:** `verify_models.py` her modeli kaynağıyla (`art/3d/meshy/source`) karşılaştırır;
  kaynakta olmayan ve alanı 300 cm²'yi aşan bir açık halka varsa derleme DURUR.
- **Önlem 3 — hat kuralı:** Hiçbir adım üçgen silip yerini boş bırakamaz; silen her fonksiyon aynı
  adımda kapatmak zorundadır.

### 3.2 Pelerin hataları
- **Kök neden 1:** Meshy yalnız insan iskeleti bilir; pelerin köşelerine kol ve bacak ağırlığı verdi.
  Kol veya bacak hareket edince pelerin şerit şerit yırtıldı.
- **Kök neden 2:** Silinen köprü üçgenleri pelerinde de çizgi çizgi boşluk bıraktı.
- **Kök neden 3:** Pelerin gövdeyle çarpışmıyordu; koşarken bacakların ve göğsün içine giriyordu.
- **Önlem 1 — ağırlık:** Pelerin köşeleri gövde payını yalnız gövde kemiklerinden alır. `build_game.destretch`
  son 4-etki ağırlığını yazarken pelerin/kuyruk/saç köşesindeki her kol payını o kolun bağlı olduğu Clav
  kemiğine, her bacak payını Hips'e taşır. Kural modelin sevk edilen ağırlığında uygulanır, hiçbir model
  bunu atlayamaz. 31.10.2026'da ates, ay, bilge, kral ve zeynos bu kuralla yeniden derlendi.
- **Önlem 2 — çarpışma:** Motor her karede `CapeCollide` ile pelerin uçlarını göğsün arkasında tutar;
  kuyruk için `TailCollide` uyluk kapsüllerini kullanır.
- **Önlem 3 — test:** `verify_models.py` Cape/Tail/Hair kemiğine ağırlığı olan bir köşenin kol veya
  bacak kemiğinden ağırlık almasını yasaklar. Delik testi pelerini de kapsar.

### 3.3 Birinci şahıs kolları
- Kök neden: kollar gövde/saç/pelerin kemiklerine de bağlıydı; kamera önünde dev düz üçgenler oluştu.
- Önlem: FP kolu ayrı köşelerle, yalnız kol zinciri ağırlığıyla kurulur; testler hem ağırlığı hem
  kemiğe uzaklığı hem de ellerin kabzaya ulaştığını ölçer.

## 4. İş akışı kuralları
- Bir hata bulunduğunda önce `GELISTIRME_HATALARI.md`'ye kök nedeni yazılır, sonra düzeltme ile birlikte
  onu yakalayan otomatik test eklenir. Testi olmayan düzeltme tamamlanmış sayılmaz.
- Teknik testlerin geçmesi kullanıcı onayı yerine geçmez.
