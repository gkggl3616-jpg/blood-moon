# v0.1.17 rig, animasyon ve secondary physics raporu

## Animasyon eşleme

| Hedef | Idle | Yürüyüş | Hafif koşu | Ortak koşu | Takla |
|---|---|---|---|---|---|
| Bilge kurt | `wt_wolf_ch / Ui_idle` | `wt_wolf_ch / LWF` | `wt_wolf_ch / LRF` | `wt_wolf_ch / T_WallDash` | `wt_wolf_ch / T_Specialatk` |
| Ateş kurt | ortak Ui_idle | `wt_wolf_smart_ch / LWF` | `wt_wolf_smart_ch / LRF` | ortak T_WallDash | ortak T_Specialatk |
| Kral kurt | ortak Ui_idle | `wt_wolf_guardian_ch / LWF` | `wt_wolf_guardian_ch / LRF` | ortak T_WallDash | ortak T_Specialatk |
| Hellgate kurt | ortak Ui_idle | `wt_wolf_berserker_ch / LWF` | `wt_wolf_berserker_ch / LRF` | ortak T_WallDash | ortak T_Specialatk |
| Ay kurt | ortak Ui_idle | `wt_wolf_woman_b_ch / LWF` | `wt_wolf_woman_b_ch / LRF` | ortak T_WallDash | ortak T_Specialatk |
| Zeynoş kurt | ortak Ui_idle | `wt_wolf_woman_r_ch / LWF` | `wt_wolf_woman_r_ch / LRF` | ortak T_WallDash | ortak T_Specialatk |
| Altı insan | hedef HumanIdle + yaw/XZ kilidi + Chest nefesi | v0.1.16 LWF; Kral eski güvenli klip | v0.1.16 LRF; Kral eski güvenli klip | — | — |

Kaynak hareket önce kanonik segment yönlerine çözülür, sonra her hedefin ayrı rest matrisi ve mevcut kemik uzunluğuyla bake edilir. Hareket klibinde yalnız joint rotation ve Hips Y yazılır. Hips X/Z ve yaw sabittir. `Tail*`, `Hair*`, `Cape*` ana klipten sürülmez.

## Mesh ve skin onarımı

On iki karakterde UV seam ikizleri konuma göre kaynaklandıktan sonra boundary edge/loop envanteri `character-rig-topology-audit.json` içindedir. Bilinçli ağız, göz, pençe, kıyafet ve FP kol açıklıkları model bazındaki mutlak component listesinde tutulur. Yeni model üretimi, remesh, double-sided materyal veya parça silme yapılmadı.

Kral insan pelerini kaynakta ayrı obje değildi ve arka pelerin yüzeyi `Thigh/Shin` ağırlığı taşıyordu. `Cape1–3` mevcut skin'e eklendi. Position, normal, UV, indeks, material, image ve texture değişmeden pelerin bölgesine en fazla %35 Cape etkisi verildi; 160 mesh-komşuluk yumuşatma turu sınır deformasyonunu giderdi. Sonuç bütün HumanIdle/Walk/Run karelerinde uzayan kenar testini geçer.

## Secondary physics ayarları

| Zincir | Etki | Frekans | Damping | Açı sınırı |
|---|---:|---:|---:|---:|
| Tail1 / 2 / 3 | 0.035 / 0.045 / 0.055 | 13 / 12 / 11 | 7.5 / 7 / 6.5 | 0.25 / 0.30 / 0.35 rad |
| Cape1 / 2 / 3 | 0.06 / 0.09 / 0.12 | 10 / 8 / 7 | 6 / 5 / 4.5 | 0.35 / 0.45 / 0.55 rad |
| Hair1 / 2 / 3 | 0.08 / 0.11 / 0.14 | 11 / 9 / 8 | 5 / 4 / 3.5 | 0.45 / 0.55 / 0.65 rad |

Solver sabit `1/60 s` accumulator kullanır. AnimationMixer'dan sonra çalışır. Sadece Tail/Hair/Cape/Ear local rotation değerini değiştirir; teleport, sahne/form değişimi, `dt > 0.1 s` veya 2 metreden büyük konum sıçramasında resetlenir. 30/60/120 FPS matematiksel sonucu aynıdır; runtime NaN ve açı sınırı testi bulunur.

## Koruma ve checksum

- `fp_arms.glb`: `80d3b033857ea0b2225b054b135d6bbd9c3952445b881e6b6a081d2a30212f68`
- FP hands marker: `1c441cc1b0b4b706e5534c4d95468c610508af9f134c70cce7c8ffa29165bab9`
- Viewmodel marker: `bb80701ab625359d5dc7070842ec701d0f31f912074b8f667b704df0cbbce7ae`
- 2.859 kaynak DTX dosyasının SHA-256 listesi `dtx-checksums.json` içindedir; hiçbir DTX yazılmadı.
- GLB image/texture/material/UV tanımları animasyon aktarımında aynı; Kral pelerin onarımında da bu tanımlar ve buffer bölgeleri korunur.

## Doğrulama sınırı

Tarayıcı WebGL, Blender kareleri, CPU skin ve APK içerik testleri çalıştırıldı. Fiziksel Android telefona kurulum ve gerçek cihaz performansı bu ortamda yapılmadı.

Onarılan 12 karakter GLB'si Khronos glTF Validator'da sıfır hata ve sıfır uyarı verir. Byte düzeyinde korunması zorunlu `fp_arms.glb` içinde kaynak dosyadan kalan bir `NODE_SKINNED_MESH_NON_ROOT` uyarısı, değiştirilmesi yasak silah GLB'lerinde de kaynak dosyadan kalan tangent-space uyarıları vardır. `gltf-validator-report.json` bunları onarılan karakter sonuçlarından ayrı kaydeder; koruma kuralı nedeniyle bu dosyalar değiştirilmedi.
