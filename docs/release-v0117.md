# Rogue: Blood Moon v0.1.17 — karakter ve fizik onarımı

Bu prerelease, v0.1.16 kaynak hareketlerini altı kurtun kendi deform rig'ine yeniden bake eder. WolfIdle artık kaynak `Ui_idle` klibinden gelir; yürüyüş/koşu hedef rig'in güvenli pozu ile sınırlı harmanlanır; taklada kaynak süre ve hareket kimliği korunurken kol/el zinciri hedefin penetrasyonsuz pozunda tutulur. Root yatay hareketi ve yaw kliplerden kaldırılmıştır.

Altı insanın idle pelvis dönüşü ve yatay sürüklenmesi kaldırıldı; Chest üzerinde 3,2 saniyelik doğal nefes eklendi. Kuyruk, saç ve pelerinler AnimationMixer sonrasında sabit 1/60 adımlı secondary solver kullanır. Kral insan pelerinine mevcut armature içinde Cape1–3 eklendi ve yalnız arka pelerin ağırlıkları yumuşatıldı.

Şarjör değiştirme sırasında 1,4 saniyelik CC0 gerçek kayıt bir kez çalar; form değişiminde veya arena çıkışında durur. Kaynak: SpringySpringo, “Gun Reload Sounds”, OpenGameArt, CC0 1.0; ayrıntılar `THIRD_PARTY_AUDIO.md` dosyasındadır.

Birinci şahıs `fp_arms.glb`, silah GLB'leri, işaretli FP hand/viewmodel kod blokları, kamera mesafeleri ve kontrol sistemi korunmuştur. DTX dosyaları değiştirilmedi. APK çevrimdışıdır ve ek veri paketi istemez.

Otomatik kabul: bütün model kliplerinde CPU skin/deformasyon, normalize ağırlık/joint, root drift, quaternion, runtime fixed-step 30/60/120, reload tek başlangıç/iptal, UI, arena, referans hareket ve 6 karakter FP grip testleri. Fiziksel Android cihazda kurulum veya performans testi yapılmamıştır.
