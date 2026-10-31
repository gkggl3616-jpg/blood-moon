# v0.1.17 görsel ve teknik doğrulama

`before/` v0.1.16, `after/` v0.1.17 çalışma zamanı GLB'lerinden Blender 4.3.2 ile aynı kamera ve kare oranında üretilmiştir. Altı kurt için BindRest, WolfIdle, WolfMove, WolfRunQuad ve WolfRoll; altı insan için BindRest, HumanIdle, HumanWalk ve HumanRun ön/yan/arka görüntüleri bulunur.

Hızlı karşılaştırmalar:

- `compare-wolf-idle.png`
- `compare-wolf-run.png`
- `compare-wolf-roll.png`
- `compare-human-idle.png`

Otomatik raporlar CI Release varlığı olarak yayımlanır:

- `character-rig-topology-audit.json`
- `human-kral-cape-repair.json`
- `dtx-checksums.json`
- `v0117-runtime-verification.json`

Görüntüler fiziksel Android cihaz testi değildir. Runtime secondary motion için oyun içi WebGL testi ve sabit-adım testi kullanılmıştır.
