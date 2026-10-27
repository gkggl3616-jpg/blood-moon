# Kurt modelleme başlangıcı

İlk kaynak: Meshy text-to-3D, A-pose, Kül Tigin tipi kısa/kaslı iki ayaklı kurt.
Görsel dil: özgün, karanlık askerî kurt; başka oyunun model/dövme dosyaları kullanılmaz.

## Varyantlar

- Bilge Kağan: uzun gövde, daha ince bel, uzun yele, bronz tılsım.
- Kül Tigin: kısa, kaslı omuzlar, asimetrik omuz zırhı, kızıl iz.
- Alp Arslan: ağır göğüs, kalın boyun, bronz halka ve kumaş kemer.
- Konuralp: ince ve uzun uzuvlar, deri çapraz kayış, kemik tılsım.

## Parçalar

Gövde ve aksesuarlar ayrı Blender nesneleridir. Dövmeler sırtta, sağ kolda, sol kolda ayrı emisif malzeme ve geometri olarak tutulur. Motifler: ejder, anka, aslan, kanatlı at, örümcek ve boğa temalarından özgün çizgiler. Gerçek UV cilt baskısı için model üzerindeki görünür deri yüzeyleri kontrol edilir; başlangıç decal/çizgi geometrisi ayrı tutulur.

## Teslim sınırları

GLB gerçek geometri dosyasıdır; Blender sahnesi ayrıca saklanır. Bu ilk modelleme çalışması final retopoloji, animasyon rig'i veya savaş fiziği tamamlandı anlamına gelmez. Kaynak Meshy görevleri ve tüketilen kredi ayrı kayıt edilir. Meshy bağlantısı kurulmadan üretildiği iddia edilmez.

İlk çıktı tamamlandı: kaynak 1.040.602 yüz, Blender gövde LOD taslağı 18.000 yüz; ayrı aksesuar/dövme nesneleriyle toplam sayı model-report.json içindedir. Retopoloji ve rig için elle kontrol gerekir.

## Takla ve dört ayak koşu önizlemesi — v0.1.7

İlk rig ve üç GLB klibi eklendi: `WolfIdle`, `WolfRoll`, `WolfRunQuad`. Her modelde 22 kemik bulunur. `wolves-rigged.blend` düzenlenebilir animasyon kaynağıdır; `wolves-modular.blend` ilk statik kaynağı korur. Yeniden üretim: `blender -b --python art/3d/scripts/animate_wolves.py`. Betik statik yedekler yoksa bunları `wolves-modular.blend` kaynağından çıkarır; rig'li GLB'yi yeniden rig'lemez.

Standart takla yalnızca `WolfRoll` erişimi verir. Efsanevi takla `WolfRoll` ve `WolfRunQuad` erişimi verir. Her ikisi mağaza sahipliği ve seçili kurdun tek takla yuvasıyla denetlenir. Takla ek hasar vermez. Klipler yerinde oynar; harita root motion/çarpışma uygulanmadı. Geometrik deri ağırlıkları ve geçişler üretim kalitesine ulaşmak için elle düzeltilmelidir. Bu adımın ek Meshy maliyeti sıfırdır.

## Atletik silüet ve mürekkep — v0.1.8

Yeni referanslarda geniş omuz/göğüs, dar bel, belirgin karın, uzun kollar ve ayrıntılı mürekkep ortak yön olarak alındı. Ağır kurtlarda bel ve karın derinliğini birlikte büyütme kaldırıldı; merkez gövdede kontrollü daralma uygulanır. Ağır/hafif gövde farkı omuz ölçeği, göğüs derinliği ve boyla korunur. Her varyantın gerçek ölçüleri rapordadır; referans fotoğrafından kesin anatomik ölçü elde edildiği iddia edilmez.

Gövde LOD'si 28.000 üçgen. Dokuz sırt motifi ve bağımsız kol motifleri alfa kesmeli renk/emisyon dokusunu kullanır. Görüntü üretimiyle hazırlanan atlasın pikselleri değiştirilmez; UV koordinatları gerekli bölmeyi seçer. Desenin altı bel formuna uyacak şekilde daraltılır. Yüzey patch'i doğrudan gövdenin yüzey üçgenlerinden çıkarılır, deri ağırlıkları gövde üçgenlerinden barycentric yöntemle aktarılır. Kaynak `wolves-modular.blend`, hareketli kaynak `wolves-rigged.blend` ve atlas birlikte teslim edilir. Ham Meshy GLB'si yerelde `meshy_output/wolf-textured.glb` yolundadır; bu ham dosya Git'e eklenmez. Statik kaynak sahneden rig yeniden kurulabilir.
