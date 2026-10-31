# v0.1.17 çalışma durumu

- Dal: `character-repair-v0.1.17`
- Motor: Three.js + Android WebView.
- Model görünüşü: position/normal/UV/material/image/texture korunur; yalnız Human Kral pelerin bölgesinde sınırlı skin ağırlığı ve Cape1–3 eklenmiştir.
- Korunanlar: `fp_arms.glb`, silah GLB'leri, FP el ve viewmodel işaret blokları, kamera mesafeleri ve kontrol davranışı.
- Animasyon: altı kurt için Ui_idle/LWF/LRF/T_WallDash/T_Specialatk hedef rig üzerinde ayrı bake; altı insan için yaw kilitli nefes idle.
- Fizik: Tail/Hair/Cape sabit 1/60 secondary solver; 30/60/120 matematiksel tutarlılık testi.
- Ses: CC0 gerçek reload kaydı, APK içinde çevrimdışı.
- Otomatik test: model deformasyonu, runtime ses/fizik, UI, arena, referans arena, FP grip ve APK içerik/imza kontrolü.
- Fiziksel Android cihaz testi yapılmadı; Release APK'sı bu ortamda gerçek telefona kurulmuş sayılmaz.
