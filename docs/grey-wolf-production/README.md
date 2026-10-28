# Referansa sadık yeni kurt — üretim hazırlığı

**Hazır:** [ayrıntılı Türkçe ana prompt](MASTER-PROMPT-TR.md), yaklaşık 1.845 sözcük; [İngilizce modelleme brifi](../../art/characters/grey-wolf-production/MODEL-PROMPT-EN.txt); [negatif prompt](../../art/characters/grey-wolf-production/NEGATIVE-PROMPT.txt); desteklenen sınırda ayrı doku promptu; son onaylı tasarımdan türetilmiş [tam boy A-pozu](../../art/characters/grey-wolf-production/fullbody-a-pose.png).

Bu görsel 2B üretim referansıdır. Ayaklar ve alt bacaklar, ilk referans kadrajında bulunmadıkları için aynı görsel dilde tamamlandı. Henüz oyun modeli veya animasyon teslimi değildir.

**Hazırlanan işlem:** bir adet Smart Topology kurt, 15.000 üçgen hedefi, A pozu, PBR, 2K doku, GLB. Desteklenen tam CLI argümanları, kaynak görüntü hash'i ve kapsam [prepared-job.json](prepared-job.json) içindedir. Uzun ana prompt yalnız bir API metin parametresi değildir; üretim, Blender düzenlemesi ve kabul testlerinin talimatıdır. Image-to-3D genel geometri promptu kabul etmediği için görsel + desteklenen seçenekler + en fazla 600 karakter doku promptu kullanılır.

**Ücret:** CLI `make --dry-run` standart dokulu görsel üretimi için 30 kredi tahmin etti; kayıt [cost-plan.json](cost-plan.json). Ardından 2026-10-28 tarihinde resmî [fiyat tablosu](https://docs.meshy.ai/en/api/pricing) kontrol edildi: CLI yardımının Smart Topology için belirttiği **meshy-t2 + 2K doku 15 kredi** olarak listeleniyor. İlk seçenek bu 15 kredilik tek üretimdir. Bu bir tahmindir; gerçek tüketim, sonuçtaki `consumed_credits` alanından raporlanacak. Ücretli otomatik rigging, ikinci varyant, yeniden üretim ve başka ücretli aşama bu kapsamda yoktur.

**Hesap durumu:** CLI 0.4.0 ve Node 24.19.0 çalışıyor, API adresleri resmî Meshy adresleri. Kayıtlı OAuth oturumu süresi dolmuş ve yenileme başarısız olmuş. Geçmişte bildirilen bakiye güncel bakiye sayılmadı; şimdiki bakiye bilinmiyor. Kimlik bilgileri okunmadı veya mesaja yazılmadı. Üretim onayı geldiğinde CLI cihaz oturumu açılmalı, aynı oturum tamamlanana kadar beklenmeli ve bakiye yeniden doğrulanmalı.

**Başlatılmayan:** yeni ücretli 3B görev; bu iş için görev ID'si ve gerçek tüketim henüz yok. Kullanıcının önceki ana kapsamındaki "yeni ücretli üretim gerekiyorsa kapsam ve gerçek maliyeti belirt; eski bütçeyi sınırsız yeni üretim izni sayma" talebi nedeniyle bu yeni harcama ayrıca onaylanacak.

Sonraki uygulama sırası: onay → gerekirse cihaz girişi ve bakiye kontrolü → tek asenkron üretim → sonucu ve gerçek maliyeti kaydetme → model ve önizleme indirme → referans benzerliği ve gerçek yüzey/UV kontrolü → Blender'da topoloji/çene/parmak/iskelet düzeltmeleri → tam hareket ve yeniden yüklenen GLB testleri → oyuna entegrasyon. Teknik veya görsel kalite geçmezse model tamamlandı diye sunulmayacak; otomatik ücretli tekrar yapılmayacak.
