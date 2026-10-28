# Native çift — inceleme sürümü

Kaynaklar: kullanıcının `wt_new_wolf_ch.ltb` (42 düğüm/72 klip) ve `wt_new_man_ch.ltb` (47/569). Hash ve ayrıntılı kayıt kök a.md içinde. Orijinaller değiştirilmedi.

Bu dosyalar nihai sanat kalitesi onayı almamış gerçek 3B çalışma modelleridir. Kurt 14.865, insan 3.926 üçgen; gömülü dokular, skin ve klipler GLB içinde. BLEND içinde de dokular paketli. Yeni ücretli üretim yok.

Oyun: Envanter → YENİ ÇİFT · DENEME, yeniden açılan menüde Bilge Kağan'ı seç. İnsan/kurt önizlemesi ve düz test alanı. ESKİ MODELE DÖN varsayılan modeli açar. Krediler/satın almalar/donanım kayıtları değiştirilmez. Uygulama baştan açılınca varsayılan model gelir.

Doğrulanan yükleme/oynanış sonuçları runtime-check.json, geometrik kusurlar geometry-check.json içinde. Sanat kalite onayı **yok**. Kol deformasyonu ve ayak teması hâlâ düzeltilecek. LRF iki ayak koşu, T_Bodyatk gövde saldırısı; dört ayak koşu/takla diye kabul edilmedi. Bu hareketler yeni çiftte kapalı; eski modellerde korunur. Çene/yüz tam animasyonu, gerçek morph, silah uyumu, telefon performansı tamamlanmadı.

Üretim: tools/build_native_character_pair.py; native okuyucu MelissaAutumn/io_scene_lithtech commit 495372d59d00e019a7143c961d94f05df2cc5c72. Blender 4.3.2. Script kaynak LTB'lerin ve mevcut dokulu kaynak GLB'lerin yerel kopyalarını gerektirir; ham kullanıcı kaynakları repo yayınında yok.

Önceki `wolf-run-*` ve `wolf-roll-*` görüntüleri ilk yanlış eşleme teşhis kareleridir; bunlar tamamlanmış dört ayak koşu/takla kanıtı değildir. Güncel model GLB ve runtime görüntüleridir.
