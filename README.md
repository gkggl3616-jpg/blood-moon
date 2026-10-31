# Rogue: Blood Moon — Android prototip (v0.1.15)

Yatay ekranlı Android için insan ↔ kurt dönüşümlü FPS/TPS prototipi. Oyun bir WebView içinde çalışan three.js
uygulamasıdır; bütün çalışma zamanı dosyaları APK'nın içindedir (ek indirme yok).

- **APK:** her `main` push'unda GitHub Actions derler ve
  [Releases](https://github.com/gkggl3616-jpg/blood-moon/releases) altına `prototype-v0.1.15-<çalıştırma no>` olarak koyar.
- **Kurallar ve bütçeler:** [`PROJE_KURALLARI.md`](PROJE_KURALLARI.md), [`docs/uretim-standardi.md`](docs/uretim-standardi.md)
- **Hata günlüğü ve dersler:** [`GELISTIRME_HATALARI.md`](GELISTIRME_HATALARI.md)
- **Birinci şahıs silah sistemi:** [`docs/fps-viewmodel.md`](docs/fps-viewmodel.md)
- **Sürüm notları:** `docs/release-v0*.md` (son: [`docs/release-v0115.md`](docs/release-v0115.md))

---

## 1. Klasör haritası

```
app/src/main/
  java/…                    Android kabuğu (WebView, tam ekran, ses)
  assets/                   OYUNUN KENDİSİ (APK'ya giren her şey)
    index.html              tüm ekranlar (açılış, lobi, envanter, mağaza, arena)
    app.js                  ekran geçişleri, ayarlar, ses
    collection.js           karakter kataloğu (ad, kurt adı, rol, güçler, açıklama)
    gear-system.js          eşyalar (silah/bomba/bıçak/dövme/takla), bonus hesabı, kuşanma
    inventory.js / .css     envanter ve mağaza arayüzü
    wolf.js / wolf.css      kurt donanım ekranı (3B önizleme)
    wolf3d.js               3B motor: three.js + arena + kurt/insan kontrolü + efektler (tek paket dosya)
    arena.css               arena arayüzü
    media/                  açılış videosu, karakter kart görselleri, sesler
    models/                 oyunun 3B modelleri (aşağıda ayrıntılı)
art/                        kaynak sanat (APK'ya girmez)
  characters/<id>/          onaylı tasarım görselleri + not (ör. art/characters/zeynos/)
  3d/meshy/source/<id>.glb  her karakterin kaynak gövdesi (Meshy çıktısı, düzenlenmiş)
  3d/meshy/rigs/<id>/       Meshy iskeleti (rigged.glb) ve Meshy animasyon paketleri (anim_a.glb, anim_b.glb)
  3d/weapons/src/*.glb      silah/bomba kaynak modelleri (Higgsfield Tripo image-to-3D)
  3d/weapons/sockets.json   silah tutuş noktaları (kabza, tetik, el kundağı, nişangah, namlu, şarjör)
  3d/fp_arms/               CC0 parmak kemikli FP kol modeli (Blender dışa aktarımı + deri dokusu)
docs/                       üretim standardı, viewmodel raporu, sürüm notları, video analizleri
tools/                      derleme ve test araçları (aşağıda)
.github/workflows/android-apk.yml   CI: test + APK + release
```

## 2. Karakterler ve dosyaları

Her karakterin iki formu vardır: **insan** (`models/human-<id>.glb`) ve **kurt** (`models/<id>.glb`).
Kimlikler motor/dosya adıdır; oyundaki adlar `collection.js` içindedir.

| id | İnsan adı | Kurt adı | Kurt modeli | İnsan modeli | Kaynak gövde / iskelet | FP eli (aksesuar) |
|---|---|---|---|---|---|---|
| `bilge` | Bilge Kağan | Boz Kağan | `models/bilge.glb` (6.785 üçgen) | `models/human-bilge.glb` (23.636) | `art/3d/meshy/source/bilge.glb`, `rigs/bilge/` | taktik parmaksız eldiven |
| `ates` | Köz Bey | Köz Kağan | `models/ates.glb` (6.780) | `models/human-ates.glb` (32.249) | `source/ates.glb`, `rigs/ates/` | kırmızı bez bilek sargısı |
| `kral` | Kara Han | Kurt Kral | `models/kral.glb` (8.123; boynuz+pelerin elle) | `models/human-kral.glb` (30.044) | `source/kral.glb`, `rigs/kral/` | deri zırhlı kolluk |
| `ay` | Aysel | Ay Kurdu | `models/ay.glb` (16.979) | `models/human-ay.glb` (18.382) | `source/ay.glb`, `rigs/ay/` | siyah dantel parmaksız eldiven |
| `hellgate` | Zebani | Hellgate Kurdu | `models/hellgate.glb` (19.792) | `models/human-hellgate.glb` (27.167) | `source/hellgate.glb`, `rigs/hellgate/` | kömürleşmiş deri, lav çatlakları |
| `zeynos` | Zeynoş | Ak Yürek | `models/zeynos.glb` (20.466) | `models/human-zeynos.glb` (36.446 = gövde 33.459 + kol kesiti) | `source/zeynos.glb`, `rigs/zeynos/`, `art/characters/zeynos/` | kalp oyuklu siyah deri eldiven |

Eski kurgu karakterler (`basibozuk`, `kul`, `ayaz`, `kultigin`, `alparslan`, `konuralp`) Bilge'nin modelini kullanır
(`wolf3d.js` → `Zw` eşlemesi).

### 2.1 Kurt animasyonları (her kurt GLB'sinin içinde)

| Klip | Kaynak | Ne zaman oynar |
|---|---|---|
| `WolfIdle` | Meshy `Combat_Stance` (anim_a #0) | dururken |
| `WolfMove` | Meshy `Quick_Walk` (anim_b #2), adım hızına göre yeniden zamanlanır | yürürken (`WalkBlend` ile `WolfJog` karışır) |
| `WolfJog` | Meshy `Run_02` (anim_b #0) | hızlı yürüyüş |
| `WolfRunQuad` | eski elle yapılmış dört ayak koşu (önceki rig'den aktarılır) | dört ayak koşu (ileri ×2) |
| `WolfJump` | eski rig'den aktarılır | sıçrama |
| `WolfRoar` | eski rig'den aktarılır | kükreme |
| `WolfRoll` | eski rig'den aktarılır | takla |
| `WolfClaw`, `WolfClawR` | eski rig'den aktarılır | sol / sağ pençe |
| `WolfTransform` | eski rig'den aktarılır | dönüşüm |

Ayak hızları (`walk_foot_speed_mps`, `jog_foot_speed_mps`, `run_measured_foot_speed_mps`) gövde düğümünün `extras`
alanına yazılır (`tools/meshy/foot_speeds.py`); motor klibi bu hızla oynatır, ayak kaymaz.
Kuyruk ve pelerin motor içinde yay fiziğiyle sallanır (`TailSpring`, `TailCollide`, `CapeCollide`).

### 2.2 İnsan animasyonları (her `human-<id>.glb` içinde)

| Klip | Kaynak | Kullanım |
|---|---|---|
| `HumanIdle` | Meshy `Idle` | üçüncü şahıs bekleme |
| `HumanWalk` | Meshy `Casual_Walk` | üçüncü şahıs yürüme |
| `HumanRun` | Meshy `Run_02` | üçüncü şahıs koşu / sprint |
| `HumanCombat` | Meshy `Combat_Stance` | havadayken |
| `HumanReload` | Meshy `Standing_Reload` | (yedek) |
| `HumanReady` | eski rig | eski FP kolu için hazır duruş |

Üçüncü şahısta kollar IK ile silahın kabza soketlerine yerleştirilir (`TpTick`).

### 2.3 Birinci şahıs kolları ve silahlar

| Dosya | İçerik |
|---|---|
| `models/fp_arms.glb` | CC0 parmak kemikli kol (omuz, dirsek, bilek, parmak başına 3 kemik), 8.152 üçgen |
| `models/fp/<id>_c.jpg`, `<id>_r.jpg` | karaktere göre ten rengi + eldiven/aksesuar (renk ve pürüzlülük) |
| `models/weapons/rifle.glb` | AR-01 saldırı tüfeği (0,86 m, 28.704 üçgen, şarjör ayrı) |
| `models/weapons/sniper.glb` | SR-01 keskin nişancı (1,18 m, 28.098) |
| `models/weapons/pistol.glb` | P-01 tabanca (0,19 m, 17.783) |
| `models/weapons/knife.glb` | KAMA-01 bıçak (0,33 m, 11.646) |
| `models/weapons/frag.glb`, `smoke.glb` | parça ve sis bombası (6.228 / 6.096) |

Silah GLB'lerinin kök düğümü `extras.sockets` taşır: `grip_r`, `grip_l`, `trigger`, `sight`, `muzzle`, `ring`, `grip_dir`.

## 3. Motor içindeki önemli bölümler (`app/src/main/assets/wolf3d.js`)

`wolf3d.js` derlenmiş bir paket dosyasıdır; elle yazılan bölümler işaretlerle ayrılmıştır ve `tools/weapons/*.js`
kaynaklarından yamalanır:

| İşaret / fonksiyon | Kaynak dosya | Görev |
|---|---|---|
| `/*VIEWMODEL-BEGIN*/ … END` | `tools/weapons/viewmodel.js` | silah profilleri, ADS, geri tepme, bob, nefes, sprint pozu, inceleme, bıçak saldırıları |
| `/*FPHANDS-BEGIN*/ … END` | `tools/weapons/fp_hands.js` | kol IK, elin kabzaya yerleşmesi, parmak sarma, tetik parmağı, deri dokuları |
| `WeapLoad`, `WGP/WGR` | (paket içinde) | silah modellerini yükler, şarjörü bulur |
| `TpBody`, `TpTick`, `TpToggle` | (paket içinde) | insan üçüncü şahıs |
| `FpFit`, `FPK` | (paket içinde) | FP kollarının ölçek/yerleşimi |
| `WalkBlend`, `TailSpring`, `CapeCollide` | (paket içinde) | kurt hareket karışımı, kuyruk/pelerin fiziği |
| `EnvLight`, `ArenaDress` | (paket içinde) | gece gökyüzü ışığı (IBL), arena görünümü |

Yamaları yeniden uygulamak için: `python3 tools/weapons/patch_fp_hands.py && python3 tools/weapons/patch_viewmodel.py`.

## 4. Kontroller (arena)

| Eylem | Dokunmatik | Klavye / fare |
|---|---|---|
| Hareket | sol yön düğmeleri | WASD |
| Bakış | sağ ekranı sürükle | fare sürükle |
| Ateş / pençe | ATEŞ | F |
| Nişan al (insan) / ağır bıçak | NİŞAN (kurtta İZ SÜR) | T veya sağ tık |
| İncele (insan) | İNCELE (kurtta TAKLA) | Q |
| Sprint (insan) / dört ayak koşu (kurt) | ileri ×2 | W ×2 |
| Şarjör / kükreme | DOLDUR / KÜKRE | R |
| Dönüşüm | KURT / İNSAN | E |
| 1. / 3. şahıs (insan) | 3. ŞAHIS | V |
| Silah seçimi | 1 ANA · 2 İKİNCİ · 3 BIÇAK · 4 BOMBA | 1–4 |

## 5. Araçlar (`tools/`)

| Araç | Ne yapar |
|---|---|
| `meshy/build_all.py <rigs> [ad…]` | Meshy iskelet + animasyonlardan oyun GLB'lerini kurar (`SRC_DIR=art/3d/meshy/source INSTALL=1`) |
| `meshy/build_game.py` | ağırlık aktarımı, delik kapatma, uzama düzeltme, FP kesiti, doku sıkıştırma |
| `meshy/make_source.py` | yeni karakter için kaynak: kuyruk/saç kemikleri, parmak kemiği |
| `meshy/foot_speeds.py` | yürüme/koşu ayak hızlarını ölçer, GLB'ye yazar |
| `weapons/build_weapons.py` | silah kaynaklarını gerçek boya, silah çerçevesine ve soketlere çevirir |
| `weapons/side_view.py` | yandan ortografik görünüm (soket okumak için) |
| `weapons/build_fp_arms.py` | CC0 kol modelini oyun dosyasına çevirir |
| `weapons/paint_fp_skins.py` | karaktere özel kol dokuları: eldiven, sargı, kolluk, ten |
| `weapons/patch_*.py` | `wolf3d.js` içine viewmodel / el kodlarını yamalar |
| `verify_models.py` | poligon bütçesi, uzayan üçgen, yeni delik, pelerin/kuyruk ağırlığı, FP kolu, silah soketleri |
| `verify_fp.py` | 6 karakter × tüfek/tabanca × düz/yukarı/aşağı: avuçlar kabzada; üçüncü şahıs tüfek |
| `verify_ui.py`, `verify_arena.py`, `verify_reference_arena.py` | arayüz, oynanış, kükreme/koşu |
| `build_apk.py` | APK derler, içeriği ve model bütçelerini denetler |

Bilgisayardaki Blender iş kuyruğu: `Desktop\rbm-blender\` (`sunucu.py` Blender'da çalışır; `jobs\*.py` sırayla işlenir,
günlük `out\`). Meshy anahtarı yalnız bu işler tarafından dosyadan okunur, depoya yazılmaz.

## 6. Üretim promptları (kullanılanlardan örnekler)

Bütçe ve kurallar: [`docs/uretim-standardi.md`](docs/uretim-standardi.md) (insan 35.000, kurt 30.000, silah 35.000,
bomba 10.000 üçgen). Aşağıdakiler projede gerçekten gönderilmiş promptlardır (bilgisayardaki plan dosyalarından):

**Silah görseli (AR-01) — görüntü modeli `gpt-image-2`, sonra Higgsfield Tripo image-to-3D:**
```text
AR-01 assault rifle: modern military carbine, dark gunmetal and matte black polymer, long M-LOK style handguard with
a vertical foregrip underneath, curved 30-round magazine, clear pistol grip behind the trigger guard with visible
trigger, adjustable stock, flip-up iron sights plus a compact red-dot sight on the top rail, worn edges. Original
fictional design for the game Rogue Blood Moon, no real-world brand, no logos, no text. Single object only, exact
orthographic side view, muzzle/blade pointing to the RIGHT, whole object in frame, centered, plain pure white
background, soft even studio lighting, photorealistic PBR materials, ultra-detailed 4K game asset.
```

**Bıçak görseli (KAMA-01):**
```text
KAMA-01 combat knife: Turkic-inspired fighting knife with a long slightly curved steel blade with a fuller, brass
guard, wrapped dark leather grip with finger grooves, wolf-head pommel. Original fictional design for the game Rogue
Blood Moon, no real-world brand, no logos, no text. Single object only, exact orthographic side view, muzzle/blade
pointing to the RIGHT, whole object in frame, centered, plain pure white background, soft even studio lighting,
photorealistic PBR materials, ultra-detailed 4K game asset.
```

**Eldiven görseli (taktik, birinci şahıs için):**
```text
A single RIGHT human hand and forearm wearing a black-and-dark-grey tactical combat glove with reinforced knuckles
and a short sleeve cuff at the forearm, palm facing DOWN, viewed exactly from above (top-down orthographic), fingers
straight, fully extended and clearly SPREAD apart with visible gaps between every finger, thumb pointing out to the
side at 45 degrees, forearm cut cleanly at mid-forearm, centered, plain pure white background, soft even lighting,
photorealistic PBR 3D game asset, no text, no logos.
```

**Zeynoş (Higgsfield, onaylı):** iş kimlikleri insan `1c264348-9f01-4ccf-8fd0-e940696ed0fd`, kurt
`c5371cef-5156-48a1-9737-a9ca4847b441`. Bu iki işin prompt metni depoya kaydedilmemiş; onaylı tasarım tarifi
`art/characters/zeynos/README.md` içindedir. Yeni karakterlerde prompt metni de karakter klasörüne yazılır.
Yeni karakter için şablon: `docs/uretim-standardi.md` § 2 (T-poz, açık gri fon, karaktere özel eldiven/kol aksesuarı,
kurtta kol ve sırt parlama bölgeleri).

## 7. CI ve APK

`.github/workflows/android-apk.yml` her `main` push'unda sırayla şunları çalıştırır: `verify_models` → `verify_ui` →
`verify_arena` → `verify_reference_arena` → `verify_fp` → `build_apk`. Bunlardan biri başarısız olursa APK çıkmaz.
APK geliştirme imzasıyla imzalanır ve `prototype-v0.1.15-<no>` sürümüne yüklenir. Geliştirme `wip/*` dallarında yapılır.

## 8. Bilinen eksikler (v0.1.15)

- Kurtlar Meshy'nin insan iskeletiyle kurulu; dört ayaklı hareketler eski elle yapılmış kliplerden aktarılıyor.
  Gerçek dört ayaklı iskelet + elle keyframe'lenmiş kurt animasyonları yapılmadı.
- Birinci şahıs silah animasyonları kodla üretilir (yordamsal); Blender'da keyframe'lenmiş FP animasyonu yoktur.
- FP kol modeli tüm karakterlerde aynı geometri; fark dokuda (ten, eldiven, aksesuar).
- Boz Kağan, Köz Kağan ve Kurt Kral bütçenin çok altında (7–8 bin üçgen); yeniden üretim kredi bekliyor.
- Fiziksel Android cihaz performans ölçümü yapılmadı.

Lisanslar: `app/src/main/assets/licenses/`. FP kol modeli CC0 (opengameart.org/content/fps-arms-rigged-only,
MakeHuman tabanlı).
