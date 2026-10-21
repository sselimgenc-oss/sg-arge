# T1a lider değerlendirmesi (Codex Algo pilotu, 6 satır)

Kaynak: `results/codex21_karsilastirma.md`, `results/codex21.csv` (PR #23). Kod incelendi: haftalık rejim yalnız tamamlanmış haftayı kullanıyor (look-ahead yok); 17 test geçti.

## Karar 1: Replikasyon tanımı (işlem listesi yayımlanmamışsa)
PDF işlem tarihlerini vermediği için "giriş tarihlerinin >= %70 örtüşmesi" ölçülemez. Bu durumda replikasyon yalnız metrik ölçütlerine göre değerlendirilir: işlem sayısı ±%15, işaret aynı, PF ±%25. Sonuç **"Geçti (metrik)"** olarak işaretlenir. Bu karar `ELEME_KRITERLERI.md` madde 3'e işlenir.
- C01, C09, C15 → Geçti (metrik)
- C02, C17, C19 → Sapma. Rapor rakamı zaten kanıt sayılmadığı için strateji bizim sonuçlarımızla değerlendirilmeye devam eder. Sapma raporun sorunudur, stratejinin değil.

## Karar 2: Ön dönem (2015-2019) gerçek OOS sonuçları
| Satır | Piyasa | PF | İşlem | Getiri | Lider yorumu |
|---|---|---:|---:|---:|---|
| C01 Geri Çekilme | BIST30 | 1,76 | 279 | +%27,1 | **Güçlü.** Görülmemiş dönemde de çalışıyor |
| C02 CCI Devam | BIST30 | 1,89 | 250 | +%29,2 | **Güçlü** |
| C09 CCI Devam | ABD | 1,50 | 347 | +%19,8 | **Güçlü.** Ancak 2024-10 sonrası OOS -%2,7: izlenecek |
| C17 CCI Devam | Emtia | 1,71 | 41 | +%5,2 | Pozitif ama örneklem küçük (<60) |
| C19 Geri Çekilme | Emtia | 0,62 | 48 | -%3,6 | **Negatif → Koşullu** (yarım ağırlık kuralı) |
| C15 CCI Devam | Kripto | 1,34 | 9 | +%0,4 | **Yetersiz örneklem.** Test edilemedi sayılır; ayrıca OOS -%1,9 ve MDD -%12 (PDF -%5,5) |

**Not:** Bunlar henüz nihai "Geçti" kararı değildir. Maliyet stresi (2x/3x) ve +1 bar sonuçları elde; walk-forward, plato, bootstrap ve DSR (testler 5-8) T6'da uygulanacak. Survivorship yanlılığı (bugünün BIST30/ABD listesi) hepsi için geçerli; ön dönemde etkisi daha büyük. Sonuçlar bu yüzden iyimser okunmalı.

## Karar 3: Sıradaki
- T1b (kalan 9 aile, 15 satır) Codex'e. Codex'in limiti açıldığında başlar.
- T3 (Sol 6.1 kod incelemesi) aktif bir Sol 6.1 kanalı olmadığı için lider incelemesiyle kapatıldı.
