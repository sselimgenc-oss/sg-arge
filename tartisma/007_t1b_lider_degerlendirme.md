# T1b lider değerlendirmesi (Codex Algo, 21 satırın tamamı)

PR #49 kabul edildi. 141 test geçti; ilk 6 satır (T1a) bit-bit aynı; motor dosyasına dokunulmadı. Örnek kontrol: `wd_reversion_risk` (C13) PDF s.20 kurallarıyla birebir.

## 2015-2019 ön dönem (raporun görmediği dönem), 1x maliyet
| Grup | Satırlar |
|---|---|
| **Güçlü** (PF ≥ 1,5 ve ≥ 100 işlem) | C01 BIST Geri Çekilme 1,76 · C02 BIST CCI 1,89 · C03 BIST Hacim Akışı 1,58 · C07 ABD ADX Kırılım 1,65 · C08 ABD Çift Momentum 1,73 · C09 ABD CCI 1,50 · C10 ABD Kırılım 1,56 · C11 ABD Momentum 2,05 · C12 ABD Ichimoku 1,86 |
| Pozitif ama zayıf ya da az örnek | C05, C06, C13, C17, C18, C20, C21 |
| **Negatif** | C04 BIST Ichimoku 0,75 · C14 Kripto Kırılım 0,53 (9 işlem) · C16 Emtia Çift Momentum 0,90 · C19 Emtia Geri Çekilme 0,62 |
| Ölçülemedi (çok az işlem) | C15 Kripto CCI (9 işlem) |

## Uyarılar
- **ABD satırlarında survivorship etkisi ön dönemde en güçlü:** evren bugünün en büyük 25 şirketi (NVDA, AVGO, LLY…). 2015-2019'da bunları seçmek mümkün değildi. ABD'deki güçlü sonuçlar bu yüzden iyimser okunmalı; rastgele giriş testi (T6a/T6b) bunu kısmen ayıklar.
- Henüz nihai karar değil. Bu satırlar da T6b'de rastgele giriş, OOS, stres, plato ve DSR testlerinden geçecek.
