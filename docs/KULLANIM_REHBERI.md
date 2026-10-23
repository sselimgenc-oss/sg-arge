# Eldeki 3 strateji: gerçekte ne getirir? (lider, 2026-10-23)

Kapsam: Geçti C07, R01 ve Koşullu A6-010, eşit ağırlıklı.

**Yöntem:**
- Motorun kendi risk ayarı yalnız katsayıyla değiştirildi: işlem başına risk %0,5 × k, toplam açık risk %2 × k. Strateji kurallarına dokunulmadı. Kaldıraç yok; brüt pozisyon özkaynağı aşmıyor.
- **"+ nakit faizi":** Stratejinin kullanmadığı para, o gün dolar faizinde (yıllık %4) duruyor sayıldı.
- **Faiz uyarısı:** 2020–2021'de dolar faizi ~%0'dı. Bu yüzden IS satırında faiz katkısı abartılı. OOS dönemi (2024-10 → bugün) için %4 gerçekçi.

## Sonuçlar (dolar bazında)

| Risk ayarı | Dönem | Yalnız strateji, yıllık | + nakit faizi, yıllık | En büyük düşüş |
|---|---|---:|---:|---:|
| **1x (şu anki, temkinli)** | OOS (~2 yıl) | %3,6 | **%6,9** | %2,0 |
| | IS (2020–2024/09) | %4,1 | %7,4 | %3,2 |
| **2x (orta)** | OOS | %8,8 | **%11,3** | %4,3 |
| | IS | %8,2 | %10,6 | %7,1 |
| **3x (agresif)** | OOS | %12,3 | **%14,2** | %6,2 |
| | IS | %10,9 | %12,9 | %10,1 |

3x ayarda bile en büyük düşüş %15 portföy sınırının altında kalıyor (IS %10,1; OOS %6,2).

## 5.000 $ ile, bir yılda (OOS dönemine göre, faiz dahil)

| Ayar | Beklenen kazanç | En kötü anda düşüş |
|---|---:|---:|
| Yalnız dolar mevduatı / hazine bonosu | ~200 $ | 0 |
| 1x | ~345 $ | ~100 $ |
| 2x | ~565 $ | ~215 $ |
| 3x | ~710 $ | ~310 $ |

## TL mevduatıyla kıyas
- **Formül:** TL getirisi ≈ (1 + dolar getirisi) × (1 + kur artışı) − 1.
- **Örnek:** Kur yılda %25 artarsa 3x ayarın TL karşılığı ≈ 1,142 × 1,25 − 1 ≈ **%43**. Bu %40 TL mevduatıyla **aşağı yukarı başa baş**; kur artışı daha düşük olursa mevduatın altında kalır.
- **Dürüst sonuç:** Bu sistem TL mevduatını açıkça yenmiyor. Sağladığı şey dolar bazında, mevduatın 2–3 katı getiri ve TL'den bağımsız bir çeşitlendirme. Bunun karşılığı düşüş riski ve günlük işlem takibi.

## Uyarılar
- **Geçmiş garanti değil.** OOS dönemi yalnız ~2 yıl.
- **Gerçek işlemde ek maliyetler:**
  - aracı kurum komisyonu;
  - kesirli hisse gereği;
  - 25 ABD hissesi ve emtia ETF'lerinde günlük emir takibi.
- **Ayar seçimi:** Ayar artırılırsa bir yılın zararla kapanma olasılığı da artar. 3x ayarda kötü bir yılda %5–10 zarar mümkündür.
