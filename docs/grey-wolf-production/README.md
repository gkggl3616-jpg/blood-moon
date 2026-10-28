# Referansa sadık yeni kurt — üretim hazırlığı

**Hazır:** [ayrıntılı Türkçe ana prompt](MASTER-PROMPT-TR.md), yaklaşık 1.845 sözcük; [İngilizce modelleme brifi](../../art/characters/grey-wolf-production/MODEL-PROMPT-EN.txt); [negatif prompt](../../art/characters/grey-wolf-production/NEGATIVE-PROMPT.txt); desteklenen sınırda ayrı doku promptu; son onaylı tasarımdan türetilmiş [tam boy A-pozu](../../art/characters/grey-wolf-production/fullbody-a-pose.png).

Bu görsel 2B üretim referansıdır. Ayaklar ve alt bacaklar, ilk referans kadrajında bulunmadıkları için aynı görsel dilde tamamlandı. Henüz oyun modeli veya animasyon teslimi değildir.

**Hazırlanan işlem:** bir adet Smart Topology kurt, 15.000 üçgen hedefi, A pozu, PBR, 2K doku, GLB. Desteklenen tam CLI argümanları, kaynak görüntü hash'i ve kapsam [prepared-job.json](prepared-job.json) içindedir. Uzun ana prompt yalnız bir API metin parametresi değildir; üretim, Blender düzenlemesi ve kabul testlerinin talimatıdır. Image-to-3D genel geometri promptu kabul etmediği için görsel + desteklenen seçenekler + en fazla 600 karakter doku promptu kullanılır.

**Ücret:** CLI `make --dry-run` standart dokulu görsel üretimi için 30 kredi tahmin etti; kayıt [cost-plan.json](cost-plan.json). Ardından 2026-10-28 tarihinde resmî [fiyat tablosu](https://docs.meshy.ai/en/api/pricing) kontrol edildi: CLI yardımının Smart Topology için belirttiği **meshy-t2 + 2K doku 15 kredi** olarak listeleniyor. İlk seçenek bu 15 kredilik tek üretimdir. Bu bir tahmindir; gerçek tüketim, sonuçtaki `consumed_credits` alanından raporlanacak. Ücretli otomatik rigging, ikinci varyant, yeniden üretim ve başka ücretli aşama bu kapsamda yoktur.

**Hesap durumu:** CLI 0.4.0 ve Node 24.19.0 çalışıyor, API adresleri resmî Meshy adresleri. Kayıtlı OAuth oturumu süresi dolmuş ve yenileme başarısız olmuş. Geçmişte bildirilen bakiye güncel bakiye sayılmadı; şimdiki bakiye bilinmiyor. Kimlik bilgileri okunmadı veya mesaja yazılmadı. Üretim onayı geldiğinde CLI cihaz oturumu açılmalı, aynı oturum tamamlanana kadar beklenmeli ve bakiye yeniden doğrulanmalı.

**Başlatılmayan:** yeni ücretli 3B görev; bu iş için görev ID'si ve gerçek tüketim henüz yok. Kullanıcının önceki ana kapsamındaki "yeni ücretli üretim gerekiyorsa kapsam ve gerçek maliyeti belirt; eski bütçeyi sınırsız yeni üretim izni sayma" talebi nedeniyle bu yeni harcama ayrıca onaylanacak.

Sonraki uygulama sırası: onay → gerekirse cihaz girişi ve bakiye kontrolü → tek asenkron üretim → sonucu ve gerçek maliyeti kaydetme → model ve önizleme indirme → referans benzerliği ve gerçek yüzey/UV kontrolü → Blender'da topoloji/çene/parmak/iskelet düzeltmeleri → tam hareket ve yeniden yüklenen GLB testleri → oyuna entegrasyon. Teknik veya görsel kalite geçmezse model tamamlandı diye sunulmayacak; otomatik ücretli tekrar yapılmayacak.

## Son el ve ayak düzeltmesi

Kullanıcı tam açık parmakları ve mekanik ayak duruşunu reddetti. Yeni [doğal duruş referansı](../../art/characters/grey-wolf-production/fullbody-natural-pose.png) bu noktada önceki tam boy A-pozu görselinin yerini alır. Eller yarı kapalı, parmaklar kademeli kıvrık, bilekler doğal; dizler esnek ve ağırlık dağılımı hafif asimetriktir. A-pozu teknik iskelet gereksinimi olarak kalabilir, ancak açık mekanik eller görsel hedef değildir. Ana prompt, İngilizce brif, negatif prompt ve henüz gönderilmemiş üretim kaydı güncellendi. Yeni ücretli 3B görev başlatılmadı.

## İnsan formu, yürüyüş ve tek kollu saldırı ek kapsamı

Kullanıcı iki form için doğal yürüyüş/salınım, bu kurdun insan karşılığı ve her vuruşta değişen tek saldıran kol istedi. Ana promptun 10. bölümü bu hareketleri, fazları, geçişleri ve testlerini ayrıntılandırır. [İnsan görünüş referansı](../../art/characters/grey-wolf-production/human-counterpart-reference.png) ve [insan üretim brifi](../../art/characters/grey-wolf-production/HUMAN-PROMPT-EN.txt) kaydedildi; bunlar henüz rigli 3B insan varlığı değildir.

Oyunun kaynak kodunda sağ/sol saldırı sırası, sadece kabul edilmiş vuruşta ilerleme ve tarafa göre pençe izi eklendi. Mevcut eski çift kollu klip için taraf maskesi oluşturulur; yeni varlıkta özel `WolfClawRight/Left` varsa onlar korunur. Bu uyumluluk katmanı yeni karakterin tamamlanmış profesyonel saldırı animasyonu olarak sunulmaz. Yeni yürüyüş klipleri, insan 3B modeli ve yeni karaktere özel saldırı klipleri henüz üretilmedi. Yeni ücretli Meshy görevi gönderilmedi; önceki tek kurt iş kaydı otomatik olarak iki karakterlik onay sayılmaz.

### Bu turdaki uygulama ve doğrulama

- `tools/viewer/claw-combo.js`: kabul edilen vuruşlarda sağ/sol sırası; geçersiz basış sırayı ilerletmez. Yeni modele ait özel taraf klipleri korunur; eski `WolfClaw` için karşı kol izleri klipten çıkarılan bir uyumluluk maskesi oluşturulur.
- Arena, vuruş tarafına uygun klibi ve pençe izi yönünü kullanır. Mevcut tek temas/tek hasar ve siper kontrolü korunur.
- `motion.js`, yeni `WolfWalk/HumanWalk` kliplerini ve `walk_stride_m` verisini okuyabilir; gerçek ilerleme hızına göre klip hızını ayarlar. Eski klipler için mevcut 3,6 m/sn kalibrasyon varsayımı uyumluluk olarak kalır; bu eski kliplerin yeni gerçekçi yürüyüş olduğu anlamına gelmez. Yeni kliplerde gerçek adım mesafesi kaydedilmelidir.
- İnsan birinci şahıs el/silah salınımı artık yalnız geçen zamana göre ilerlemez: yerde kat edilen mesafeden faz alır, duruşta ve havada yumuşakça söner. Bu, tam bedenin pelvis/göğüs animasyonunun yerine geçmez.
- `node tools/test_walk_contract.mjs`: yeni yürüyüş seçimi, mesafe/süre kalibrasyonu, eski klip uyumluluğu geçti.
- `node tools/test_claw_combo.mjs`: sıra ve tek etkin kol maskeleri geçti.
- `python tools/verify_claw_combo.py`: gerçek arena üzerinde sağ/sol, reddedilen basış, basılı tutmada sağ/sol/sağ, ilk saldırıda tek hasar, sol el izi ve insan salınımının duruşta sönmesi geçti. JavaScript hata listesi boş. Kanıt: [claw-combo-test.json](claw-combo-test.json).
- Web varlık paketi yeniden derlendi. Yeni APK yayımlanmadı. İnsan görünüş referansı 2B'dir; yeni iki formun gerçek mesh/iskeletleri ve doğal tam beden yürüyüş/özel saldırı klipleri açık iştir.
