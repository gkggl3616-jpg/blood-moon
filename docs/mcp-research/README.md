# Animasyon araçları ve MCP araştırması — 28 Ekim 2026

Kullanıcı, çalışma animasyonlarının hâlâ yetersiz olduğunu söyleyerek profesyonel eklenti/MCP araştırması istedi. Önceki yalnız eklenti kataloğuna dayalı arama eksikti. Katalogda bulunmamak, dışarıda uygun bir MCP bulunmadığı anlamına gelmez. Bu tur oyun/GLB/animasyon dosyaları değiştirilmedi; yeni ücretli üretim ya da hesap satın alma yapılmadı.

## Sonuç ve önerilen sıra

1. **MCP for Blender (ahujasid): ilk kurulacak bağlantı.** Canlı Blender Python kontrolü, sahne/mesh/rig/ağırlık bilgisi, çok açılı görüntü ve animasyon şeridi inceleme sunar. Bu, görsel düzeltme döngüsüne yardımcı olur. Hareketi yine AI/Python veya kaynak animasyon belirler; otomatik profesyonel animatör değildir. Rigify mevcut kurulumda önceki turda etkinleştirildi. İyi kaynak animasyonun doğru iskelete aktarımı yeni iş akışının parçası olmalı.
2. **Rokoko Blender retargeting:** kaynak FBX/BVH hareketini karaktere aktarmak için ücretsiz seçenek. Resmî yardım, retargeting için premium hesap gerekmediğini belirtiyor. İskelet eşlemesi ve rest-pose kontrolü gerekir; kendiliğinden kaynak hareket oluşturmaz. Bu tur kurulmadı ve Bilge üzerinde denenmedi.
3. **Cascadeur ve kendi yerel MCP sunucusu:** profesyonel hareket düzeltme/AutoPhysics değerlendirmesi için güçlü aday. Resmî Scripts Menu belgesinde MCP → Start script server var. Bu, ayrıca bulunan bağımsız `gprethesh/cascadeur-mcp` projesiyle aynı sunucu değildir. Yerel/native sunucunun bağlantı ayrıntıları, çalışacak uygulama sürümü ve istemciyle gerçek uyumu bu ortamda henüz test edilmedi.
4. **Auto-Rig Pro:** ücretli Blender rig/skin/retarget/export aracı; satın alma sayfası kontrol edildi. Önce ücretsiz bağlantı ve kaynak-animasyon aktarımı denemesi, ardından gerekirse lisans kararı. Satın alınmadı ve kurulu olarak doğrulanmadı.

## Cascadeur için doğrulanan ayrımlar

- AutoPhysics, hazırlanmış animasyona fizik temelli düzeltmeler önerir. Doğru rig/center-of-mass kurulumu gerekir; her hareketi tek tıkla bitirmez.
- Mocap (Alpha), görüntü/video pozlarından sahnedeki karakter için taslak oluşturur. Tek aktör sınırlaması ve tek kamera açısından karmaşık pozları eksik çözme ihtimali resmî belgede var. Kullanıcının efektli kurt kaydında sonucu denenmedi; birebir çıkaracağı iddia edilmez.
- Güncel plan sayfası Free için yalnız `.casc` ve ticari olmayan kullanım bildiriyor. Oyun için FBX dışa aktarımı ücretli planda; quadruped AutoPosing Pro özellikleri arasında listeleniyor. Kesin satın alma tutarı hesap/bölge/plan üzerinden tekrar kontrol edilmeli; bu tur abonelik başlatılmadı.
- Bağımsız `gprethesh/cascadeur-mcp`, Codex/Claude/Cursor için animasyon, parmak, rig incelemesi, keyframe ve fizik komutları tanımlıyor. Kendi Known limits kısmı rig üretimi, mocap, AI motion ve retargeting kalitesini doğrulanmış özellik diye sunmuyor; menü komutu göndermek başarılı işlem kanıtı değildir. Native Python video export testinde çökme raporlanmış. İlk tercih olarak doğrulanmadan üretime konmamalı.

## Doğrulanan yerel MCP testi

- PyPI `mcp-for-blender` sürümü kontrol anında **2.2.4**, Python ≥3.10; kaynak `pyproject.toml` MIT lisansı bildiriyor.
- İzole `uvx --from mcp-for-blender==2.2.4 mcp-for-blender --help` çalıştı.
- `addon-paths`, `/home/agent/.config/blender/4.3/scripts/addons` yolunu buldu; dizin henüz yok.
- İzole MCP stdio oturumunda `initialize` ve `tools/list` başarılı. Dokuz araç bildirildi: `get_addon_status`, `disable_telemetry`, `get_scene_info`, `execute_blender_code`, `record_trajectory_feedback`, `look`, `generate_3d`, `search_assets`, `import_asset`.
- Paket sürümü 2.2.4 olarak sabitlendi; dönen `serverInfo.version` alanında 1.29.0 vardı. Bu iki sürüm alanı birbirine karıştırılmamalı.
- **Blender addon bağlantısı, canlı ekran görüntüsü, sahne düzenleme ve Bilge animasyon kalitesi bu testte doğrulanmadı.** Test yalnız MCP protokolünü ve araç listesini kanıtlar. Aktif sohbetin araç listesine bağlı olduğu iddia edilmez.
- Testte telemetri kapalı, Blender hedefi localhost, hiçbir ücretli model üretimi çağrılmadı. Global Codex ayarı yazılmadı, Blender MCP addon kurulmadı.
- Mevcut Codex CLI'da `mcp add` ve `plugin marketplace add` komutlarının bulunduğu yardım çıktısıyla kontrol edildi. Depoda `integrations/codex/.agents` ve `integrations/codex/plugins` dizinleri doğrulandı.

Örnek ayar: `tools/mcp/blender-config.example.toml`. İzole testi yeniden çalıştırma:

```sh
uv run --no-project --with mcp-for-blender==2.2.4 python tools/mcp/probe_blender_protocol.py
```

Kurulum kararı verildiğinde doğrulanacak iki parça: Blender içindeki addon ve MCP istemcisindeki sunucu kaydı. Blender soketi, Blender'ın gerçekten çalıştığı makineye gitmelidir. Başka bilgisayardaki localhost'a bağlanmış görünmek geçerli kurulum değildir. Canlı bağlantı, sahne bilgisi ve bir görüntü alınmadan “kuruldu ve çalışıyor” denmez.

## Kaynak hareket seçimi

Adobe'nun resmî Mixamo sayfası profesyonel oyunculardan motion-capture animasyon kütüphanesi tanımlar. FAQ ücretsiz Adobe ID erişimi ve oyunlarda kullanımı açıklar; auto-rig ve kütüphane biped humanoid içindir. Bu nedenle insansı kükreme için kaynak aday olabilir, dört ayak kurt koşusuna otomatik uygun sayılmaz. Bu tur hesap girişi veya belirli bir hareketin indirilmesi yapılmadı. Uygun kaynak, lisansı ve karakter oranları görülerek seçilmeli; ham kütüphane dosyaları herkese açık depoya gelişigüzel konmamalı.

DeepMotion capture guidelines, insan hareketi için tasarlandığını ve cartoon/abstract karakterli videolardan kaçınılmasını belirtiyor. Kullanıcının efektli kurt ekran kaydı için doğrudan güvenilir video-to-motion çözümü diye önerilmez. Bir insanın benzer hareketi temiz çekimde yapması ayrı bir seçenek olur; böyle bir kayıt henüz mevcut değil.

Efektler (el alevi, dövme parlaması, tepe vurgusu, sönüş) ayrı oyun/Blender katmanıdır. Animasyon MCP bağlantısı bu efektleri kendiliğinden tamamlamaz. Son kullanıcı bunların da referansa yakın olmasını istiyor; bu tur efekt teslimi yoktur.

## İncelenen birincil kaynaklar

- [MCP for Blender, kurulum/Codex/araçlar](https://github.com/ahujasid/mcp-for-blender)
- [Paket metadatası](https://pypi.org/project/mcp-for-blender/)
- [Cascadeur native MCP, Scripts Menu](https://cascadeur.com/help/category/320)
- [Cascadeur AutoPhysics](https://cascadeur.com/help/tools/physics_tools/autophysics)
- [Cascadeur Mocap Alpha](https://cascadeur.com/help/category/203)
- [Cascadeur güncel planları](https://cascadeur.com/plans)
- [Bağımsız Cascadeur MCP ve sınırlamaları](https://github.com/gprethesh/cascadeur-mcp)
- [Rokoko ücretsiz Blender retargeting](https://support.rokoko.com/hc/en-us/articles/4410463481489-Retarget-an-animation-in-Blender)
- [Rokoko Blender addon kaynağı](https://github.com/Rokoko/rokoko-studio-live-blender)
- [Auto-Rig Pro](https://www.lucky3d.fr/tools_auto_rig_pro.php), [Remap](https://www.lucky3d.fr/auto-rig-pro/doc/remap_doc.html), [satış sayfası](https://artell.gumroad.com/l/autorigpro)
- [Adobe Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html), [Mixamo resmî tanıtım](https://mixamo-mini.adobe.io/)
- [DeepMotion capture guidelines](https://www.deepmotion.com/article/capture-guidelines-quick-guide)
