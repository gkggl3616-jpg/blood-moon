# Birinci şahıs silah tutuş sistemi (viewmodel) — durum raporu

## Tespit edilen teknik nedenler
- Eski FP kolu karakter gövdesinden kesiliyordu; Meshy iskeletinde parmak kemiği yok. El tek kemikle bükülünce parmaklar pençe gibi açılıyordu.
- Silahlar kod içinde kutulardan çiziliyordu; kabza ve tetik yeri yoktu.
- Kol ölçeği tek ayardı. Sol kolun ön tutamağa uzanması için kollar 1,5–2 kat büyütülmüştü; sol kol dümdüz ve uzun görünüyordu.

## Mimari
| Katman | Dosya | Görev |
|---|---|---|
| Silah modeli | `models/weapons/*.glb` (`tools/weapons/build_weapons.py`) | Gerçek boy; kabza (grip_r), destek eli (grip_l), tetik, nişangah, namlu soketleri silahın yerel koordinatında; şarjör ayrı parça |
| FP kolları | `models/fp_arms.glb` (`tools/weapons/build_fp_arms.py`) | CC0 "FPS arms rigged" (MakeHuman): omuz, dirsek, bilek, parmak başına 3 kemik; ten rengi karaktere göre |
| El IK + parmak pozu | `tools/weapons/fp_hands.js` | İki kemikli kol IK; el yönü kabza soketinden (avuç normali + kabza ekseni). Bilek ön kola göre kabza ekseni çevresinde döner, kırık bilek oluşmaz. Her parmak kabza yüzeyine değene kadar kapanır, işaret parmağı tetiğe çözülür |
| Viewmodel profili ve animasyon | `tools/weapons/viewmodel.js` | Silaha göre omuz yerleşimi/ölçeği (sağ dirsek ~%72, sol ~%84 uzanım: bükülü), kalça pozu, nişan pozu, geri tepme, yürüme sallanması, nefes, inceleme, bıçak saldırıları |

Bütün animasyonlar silahı hareket ettirir; iki el her karede kabza soketlerine yeniden çözülür. Bu yüzden eller silahın üzerinde kaymaz.

## Animasyon durumları
| Durum | Durum açıklaması |
|---|---|
| Idle / nefes | Var: yavaş dikey + eğim salınımı |
| Walk | Var: hıza bağlı bob ve yalpa. **Sprint yok**: insan formunda koşu mekaniği bulunmuyor, bob hızla ölçekleniyor |
| ADS | Var: NİŞAN düğmesi / T / farenin sağ tuşu; nişangah soketi kamera eksenine hizalanır, FOV daralır (tüfek 55, keskin nişancı 28, tabanca 60), nişangah artısı gizlenir |
| Fire / Recoil | Var: silaha özel geri itme + yukarı kalkma + küçük yan sapma; hızlı toparlanma, eller birlikte tepki verir |
| Reload | Var: şarjör ayrı parça olarak düşer, sol el yeni şarjörü takar (tüfek); tabancada taban plakası |
| Equip / Unequip | Var: silah değiştirmede aşağıdan kalkma hareketi |
| Inspect | Var: İNCELE düğmesi / Q (insan formunda); silah yan yüzünü gösterip geri döner |
| Bıçak | Hafif saldırı = ATEŞ (saplama); ağır saldırı = NİŞAN düğmesi / sağ tuş (geniş kesme, 1,9× hasar) |

## Eksik / açık raporlanan
- Kol modeli tüm karakterlerde aynı; yalnız ten rengi değişiyor. Karaktere özel eldiven/kolluk henüz boyanmadı.
- Silah ve kol animasyonları elle keyframe'lenmiş değil, yordamsal (kod) eğrilerdir. Gerçek AAA kalitesi için Blender'da keyframe animasyon gerekir.
- Sprint mekaniği insan formunda yok.
