# Kapı v3.0 — DONDURULDU (2026-10-26)

**Onay:** kullanıcı (şartlı: "Sol tamam derse") + Sol 6.1 ("şu değişikliklerle onay": üç sınıf, sıfır-kenar
yanlış-geçme kalibrasyonu, tam boru hattı güç testi, q ≤ 0,10). Değişiklikler işlendi → dondu.
Kaynak: `docs/kapi_degerlendirme.md` (7 yapay zekâ + lider), `docs/sol_kapi_gorus.md`, `docs/kapi_kontrol.md`,
`results/plasebo.csv`, `results/kapi_kontrol_13.csv`.

**Kural:** eşikler ve §3'teki kalibrasyon kuralı sonuçlara bakılarak değiştirilmez. Sonradan bulunan istisna yeni
sürüm (v3.1) olur; önceki sonuçlarla birleştirilmez. Güç testinde §3 dışında alternatif eşik denenmez.

## 0. Pilot ölçüm (dondurmadan önce)
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

## 2. Sonuç sınıfları ve adımlar
Üç sınıf: **Geçti / Yetersiz / Kaldı.** "Yetersiz" = henüz yeterli kanıt yok (kötü strateji demek değil); kısa
örneklem doğrudan "Kaldı" olmaz.

| # | Adım | Şart | Şart sağlanmazsa |
|---|---|---|---|
| 0 | Kayıt | Aile, veri, maliyet, eşikler bu belgede; deneme sayısı (ham N) ve N_eff (korelasyon ≥ 0,9 kümeleri) | — |
| 1 | Nedensellik | Mevcut kesim testi + `lookahead_on`/repaint taraması | **Kaldı** |
| 2 | Asgari kanıt | Sınama ≥ 1 yıl **ve** ≥ 50 işlem; sepette ≥ 52 bağımsız aktif hafta | **Yetersiz** |
| 3 | Ekonomik | 1x maliyette net > 0; **1 bar gecikmeli dolumda** net > 0 | **Kaldı** |
| 3b | Kırılganlık | 2x maliyette net ≤ 0 | **"kırılgan"** etiketi |
| 4 | Plasebo | **Motor tabanlı** rastgele giriş (aynı çıkış kuralları, sembol, dönem, yön, işlem sayısı), 1.000 tekrar; tek yönlü p ≤ 0,05 | §2.1 |
| 5 | Alfa | Maruziyet eşleşmiş kıyas (piyasada kalınan oran × piyasa + nakit); yıllık alfa > 0, tek yönlü NW t ≥ t* (§3) **ve** blok bootstrap %90 alt sınırı > 0 | §2.1 |
| 6 | Çoklu test | Ailedeki **tüm test edilenlerin** (yalnız geçenler değil) plasebo p-değerlerine BHY, **q ≤ 0,10** (değişmez) | §2.1 |
| 7 | Kısa liste | Önceden kilitli kısa listeye Hansen SPA (maruziyet kıyasına karşı) | rapor; p > 0,10 → şerh |
| 8 | Portföy | Hiyerarşik kümeleme (ρ ≤ 0,5), her kümeden en yüksek alfa-t; risk bütçesi | seçim |
| 9 | Paper | 26 hafta **icra doğrulaması** + sağlık matrisi; alfa kanıtı sayılmaz | — |

### 2.1 Adım 4–6'da kalan
- Alfa nokta tahmini ≤ 0 ya da plasebo yüzdeliği ≤ %50 → **Kaldı**.
- Aksi hâlde (yön doğru, kanıt yetmiyor): stratejinin hücresinde (§3) SR 1,0'daki güç t* ile hâlâ < %50 ise
  **Yetersiz**, değilse **Kaldı**.

### 2.2 Seyrek stratejiler
Eşik kaldırılmaz. İstisna yalnız önceden kayda geçirilmiş çoklu varlık sepetiyle: yeterli bağımsız aktif hafta
(≥ 52) ve sepet üzerinde ortak test. Böyle bir sepet yoksa **Yetersiz** kalır.

Bilgi sütunları (eleme yapmaz): DSR (N_eff ile), PSR, p10, PF, parametre ±%20 duyarlılığı (Pine girdileri
hesaplanabildiğinde), eski huni null sonucu.

**Kaldırılanlar:** "tek enstrümanda yılda < 30 işlem" (yerini adım 2 aldı), elle "hata şüphesi" (yerini adım 1 ve
otomatik kontroller aldı), sonuç görüldükten sonra konan p10/PF eşikleri. q = 0,20 kullanılmaz.

## 3. Güç ve yanlış-geçme kalibrasyonu (gerçek sonuçlardan ÖNCE koşulur)
- **Senaryolar:** sentetik kenarlı strateji, yıllık Sharpe **0 (null), 0,5, 1,0, 1,5**. Gerçek stratejilerin
  sembol, dönem, frekans, maruziyet, yön ve tutma süresi dağılımı korunur; kenar, işlem getirilerine eklenen sabit
  kaymayla verilir.
- **Tam boru hattı:** adım 2–6 birlikte (plasebo, NW alfa, BHY aile içinde, 1 bar gecikme dahil); kümeleme raporlanır.
- **Hücreler:** aile × piyasa (ABD / kripto / emtia / forex) × tf (≤ 1s / 4s / 1G+) × sınama uzunluğu (1–2 / 2–4 / 4+ yıl).
  Hücre başına ≥ 1.000 simülasyon; geçme oranları **Wilson %95 güven aralığıyla**.
- **Hedefler:** SR 0'da yanlış geçme ≤ %5 (güven aralığı üst ucu ≤ %10); SR 1,0'da güç ≥ %50.
- **Önceden dondurulmuş tek gevşetme:** t* = 2,00. Bir hücrede SR 1,0 gücü < %50 ise o hücrede t* = **1,65** (tek yönlü).
  Başka bir eşik denenmez. 1,65 ile SR 0 yanlış geçme hedefi bozuluyorsa o hücre t* = 2,00'da kalır.
- **SR 0 hedefi t* = 2,00'da da tutmuyorsa:** v3.0 o hücrede geçersiz sayılır, sonuç "Yetersiz" yazılır ve kullanıcıya
  raporlanır (v3.1 kararı kullanıcının).

## 4. Uygulama sırası
1. ✅ Taslak onaylandı, eşikler donduruldu (bu belge).
2. Motor tabanlı plasebo + 1 bar gecikme koşucusu (`asama2a.random_entry_signals` + TV-2 emülatörü).
3. §3 kalibrasyonu → hücre başına t* tablosu (`results/kapi_v3/kalibrasyon.csv`); gerçek sonuçlara bakılmadan.
4. Yorumlayıcı paritesi: katmanlı örneklemle (her aile/tf'den) TradingView çıktısıyla karşılaştırma.
5. A ailesinin tüm test edilenleri (~530) ve B ailesinin 119'u Actions'ta.
6. Sonuç tablosu → kullanıcı kararı (paper'da kim kalır/girer/çıkar). Paper bu süreçte aynen sürer (kullanıcı 2026-10-26).

## Sürüm 3.1 (geriye dönük kayıt, 2026-10-29)
- 2026-10-27 kullanıcı kararı: kârlı ay eşiği %60 → aşama 1'de %44 (`asama1_min_karli_ay_orani`), adım 4'te %49
  (`adim4_min_karli_ay_orani`). Karar o günkü sonuçlar görülerek verildi; bu yüzden ayrı sürümdür. v3.0 sonuçlarıyla birleştirilmez
  (hesap sürümü `v1.1-2026-10-27d` bunu zaten ayırır).
- Uygulamadaki pencere: mum ve kopya defteri `mum_pencere_gun` = 200 gün; adım 6 alfası da fiilen bu 200 günlük veriden hesaplanır
  (`alfa_pencere_gun` 365 üst sınırdır). Adım 2'nin "≥ 1 yıl" şartı geçmiş uzunluğuna (`min_history_days`) değil, sınama verisine
  bakar; bu fark bilinçli kabul edildi ve raporlarda belirtilir.
