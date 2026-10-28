# Blender canlı bağlantısı — çalışma 03

Bu ortamda `mcp-for-blender==2.2.4` kuruldu, GUI Blender 4.3.2 ile 127.0.0.1:9876 üzerinden gerçek bağlantı kuruldu. Sahne okuma, görüntü alma, Rigify üretimi, Rokoko retarget ve efekt sahnesi yazımı `execute_blender_code` üzerinden çalıştırıldı. CLI yalnız protokol taklidiyle sınanmadı. Telemetri kapalı; uzak üretim sağlayıcıları kullanılmadı.

Codex kaydı:

```sh
codex mcp add blender --env DISABLE_TELEMETRY=true --env BLENDER_HOST=127.0.0.1 --env BLENDER_PORT=9876 -- uvx --from mcp-for-blender==2.2.4 mcp-for-blender
codex mcp get blender
```

Blender MCP arka plan (`-b`) kipinde sunucu açmaz. Bu ortamda yerel Xorg dummy ekranı `:99` ve GUI Blender kullanıldı. Headless render/export ayrı Blender süreçleridir. Bağlantı, Blender ve yerel sunucu çalışırken kullanılabilir; sonraki oturumda GUI yeniden açılmalıdır.

Yerel MCP istemcisi (konuşmanın doğrudan araç listesine yeni araç enjekte edildiği iddiası yok):

```sh
mkdir -p dist/mcp-proof
uv run --no-project --with mcp-for-blender==2.2.4 python tools/mcp/blender_live.py get_addon_status '{}'
uv run --no-project --with mcp-for-blender==2.2.4 python tools/mcp/blender_live.py execute-file art/3d/animation-studies/build_rigify_roar.py
```

Rigify Blender ile gelen sürümdür. Resmî Rokoko eklentisi 1.4.3, kaynak commit `b031e5a001b3d87e62359d18159c4e4ab479c732` kullanıldı. `rsl.retarget_animation` gerçek Bilge kontrol iskeletine aktarımda `FINISHED` döndü. Kaynak, videodan elle yorumlanan iskelet animasyonudur; hazır insan mocap'i veya otomatik MP4 hareket çıkarımı değildir.

Dağıtımda eksik olan Python 3.13 `ensurepip` modülü CPython v3.13.5 resmî kaynaklarından Blender kullanıcı modüllerine eklendi. Rokoko'nun tekrar özel kemik eşlemesi kaydederken verdiği `KeyError` için bu dizindeki tek satırlık yama uygulandı; bu bir yerel uyumluluk düzeltmesidir. Rokoko hesap/Live bağlantısı ve isteğe bağlı `boto3` hesap bağımlılıkları bu işte kullanılmadı. Yerel retarget çalışması doğrulandı; bütün Rokoko özellikleri doğrulandı denmez.

Yalnız kendi ürettiğimiz güvenilen .blend dosyalarını ayrı süreçte render ederken `--enable-autoexec` kullanılır; Rigify kontrol sürücüleri yüklenir. Rastgele dış .blend dosyalarına genel güven ayarı açılmadı.

Bu araçlar tek başına iyi animasyon üretmez. Ağırlık, topoloji, poz ve zamanlama ayrıca kontrol edilmelidir; görsel kabul ile teknik bağlantı testi ayrı tutulur.
