# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-21 ~23:00 UTC, lider (Opus)

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Codex | T1b: kalan 9 aile (15 satır) | **Sırada; limit açılınca** | Limit açılınca "görev geldi" |
| Sonnet | T5a birleştirme: `engine/indicators.py` çakışması | Atandı | "Görev geldi" |
| Argon | `PAKET_T2_yeniden2.md` (36 kart) | Gönderildi; limitte | Cevabı `argon/T2_yeniden2.yaml` olarak yükle |
| Veri arşivi | Saatlik arşiv | 2. koşu boyut sınırına takıldı (kripto dahil 59 MB). Düzeltildi: kripto arşivlenmez | Actions → "Hourly market data archive" → Run workflow (bir kez daha) |

## İlk sonuçlar (T1a, ayrıntı `tartisma/004_t1a_lider_degerlendirme.md`)
2015-2019 (raporu yazanın görmediği dönem) testinde: C01 BIST Geri Çekilme PF 1,76, C02 BIST CCI PF 1,89, C09 ABD CCI PF 1,50 güçlü. C19 Emtia Geri Çekilme negatif. Henüz nihai karar değil; tam test seti T6'da.

## Sırada bekleyen (açılmadı)
- Argon: partiler 6, 7, 8, 9
- Codex: T5b (hızlı tarama). T1b ve T5a'dan sonra.
- Sonnet: kart sözdizimi düzeltmeleri (19 `tam` kartta hata). T5a'dan sonra.

## İlerleme
- Kart: 203 / ~316. `tam` 58, `dakikalik` 41, `eksik` 88. Yeniden okunacak 73 (13'ü TradingView, okunamıyor)
- Backtest: 6 / 21 Codex Algo satırı (T1a)
