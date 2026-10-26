# Kapı v3 — TASLAK (kullanıcı onayı bekliyor)

Kaynak: `docs/kapi_degerlendirme.md` (7 yapay zekâ + lider), `docs/sol_kapi_gorus.md` (Sol 6.1), `docs/kapi_kontrol.md` ve
`results/plasebo.csv` / `results/kapi_kontrol_13.csv` (pilot ölçüm, 2026-10-26). **Onaylanınca eşikler dondurulur;
sonuçlara bakılarak değiştirilmez.** Sonradan bulunan istisna yeni sürüm (v3.1) olur, önceki sonuçlarla birleştirilmez.

## 0. Pilot ölçüm (dondurmadan önce kalibrasyon — Sol §1 "Tüm evren" madde 3)
Getiri serisi blok plasebosu (yaklaşık; motor tabanlı değil):
- Eski kapıyı ("net > 0") **rastgele girişlerin %67'si (TV-2) / %99,6'sı (U7)** geçerdi → kapı istatistiksel olarak boştu.
- 13 paper kitabından maruziyet eşleşmiş kıyasa göre alfa NW t ≥ 2: yalnız TV-zoY9DmsF (2,16) ve yhoK9cH4 (3,06; yalnız
  12 hafta). Sınırda: TV-dpkq3n4O 1,65, TV-71yKm18B 1,59. Geçen 181 stratejiden DSR ≥ 0,95: 3.
- U7 sepetlerinde maruziyet ~%90–100 → blok plasebosu ayırt edemiyor; orada alfa testi esas.

## 1. Aileler (önceden ayrılır; çoklu test aile içinde)
- **A — TV-2 yayımlı:** yazarın sembolü/tf/kodu, sınama = sürüm tarihi sonrası (gerçek örneklem dışı).
- **B — U7 sepet:** TradingView kuralları + kendi hipotezlerimiz, 25'lik sepet, sınama 2023+. **Gerçek örneklem dışı
  değil** (dönem bilinerek kuruldu) → aynı eşikler + "B ailesi" şerhi.
- **C — yeni:** radar, copy trade, ML (her biri ayrı aile; deneme defteri zorunlu).

## 2. Adımlar ve eşikler
| # | Adım | Şart | Sonuç |
|---|---|---|---|
| 0 | Kayıt | Aile, veri, maliyet, eşikler bu belgede; deneme sayısı (ham N) ve N_eff (korelasyon ≥ 0,9 kümeleri) | — |
| 1 | Nedensellik | Mevcut kesim testi + `lookahead_on`/repaint taraması | ihlal → **Red** |
| 2 | Asgari kanıt | Sınama ≥ 1 yıl **ve** ≥ 50 işlem; sepette ≥ 52 aktif hafta | altı → **Yetersiz** (geçti değil) |
| 3 | Ekonomik | 1x maliyette net > 0; **1 bar gecikmeli dolumda** net > 0 | değilse **Red** |
| 3b | Kırılganlık | 2x maliyette net ≤ 0 | **"kırılgan"** etiketi |
| 4 | Plasebo | **Motor tabanlı** rastgele giriş (aynı çıkış kuralları, sembol, dönem, işlem sayısı), 1.000 tekrar; p ≤ 0,05 | değilse **Red** |
| 5 | Alfa | Maruziyet eşleşmiş kıyas (piyasada kalınan oran × piyasa + nakit); yıllık alfa > 0, NW t ≥ 2 **ve** blok bootstrap %90 alt sınırı > 0 | değilse **Red** |
| 6 | Çoklu test | Ailedeki **tüm test edilenlerin** (yalnız geçenler değil) plasebo p-değerlerine BHY, q ≤ 0,10 | değilse **Red** |
| 7 | Kısa liste | Önceden kilitli kısa listeye Hansen SPA (maruziyet kıyasına karşı) | rapor; p > 0,10 → şerh |
| 8 | Portföy | Hiyerarşik kümeleme (ρ ≤ 0,5), her kümeden en yüksek alfa-t; risk bütçesi | seçim |
| 9 | Paper | 26 hafta **icra doğrulaması** + sağlık matrisi; alfa kanıtı sayılmaz | — |

Bilgi sütunları (eleme yapmaz): DSR (N_eff ile), PSR, p10, PF, parametre ±%20 duyarlılığı (Pine girdileri
hesaplanabildiğinde), eski huni null sonucu.

**Kaldırılanlar:** "tek enstrümanda yılda < 30 işlem" (yerini adım 2 aldı), elle "hata şüphesi" (yerini adım 1 ve
otomatik kontroller aldı), sonuç görüldükten sonra konan p10/PF eşikleri.

## 3. Uygulama sırası (Sol)
1. Bu taslak onaylanır → eşikler dondurulur.
2. Motor tabanlı plasebo ve 1 bar gecikme koşucusu yazılır (mevcut `asama2a.random_entry_signals` + TV-2 emülatörü).
3. Yorumlayıcı paritesi: katmanlı örneklemle (her aile/tf'den) TradingView çıktısıyla karşılaştırma.
4. A ailesinin tüm test edilenleri (~530) ve B ailesinin 119'u Actions'ta koşulur.
5. Sonuç tablosu → kullanıcı kararı (paper'da kim kalır/girer/çıkar).

## 4. Kullanıcı kararları
1. Taslak bu hâliyle onay mı?
2. Paper bu süreçte aynen sürsün mü (önerim: evet; v3 sonucu gelince tek seferde karar)?
