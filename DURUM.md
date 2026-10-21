# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-21 ~23:00 UTC, lider (Opus)

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Codex | T1b: kalan 9 aile (15 satır) | **Sırada; limit açılınca** | Limit açılınca "görev geldi" |
| Sonnet | T7: son 5 kart (yeni Argon kartları) | Atandı (PR #26 açık) | "Görev geldi" |
| Argon | Parti 6 (40 kart) | Çalışıyor | Cevabı `argon/T2_parti6.yaml` olarak yükle |
| Veri arşivi | Saatlik arşiv | 3. koşuda veri indirildi ama push reddedildi (koşu sırasında main ilerledi). Düzeltildi: push öncesi rebase | Run workflow (4. kez) |

## İlk sonuçlar (T1a, ayrıntı `tartisma/004_t1a_lider_degerlendirme.md`)
2015-2019 (raporu yazanın görmediği dönem) testinde: C01 BIST Geri Çekilme PF 1,76, C02 BIST CCI PF 1,89, C09 ABD CCI PF 1,50 güçlü. C19 Emtia Geri Çekilme negatif. Henüz nihai karar değil; tam test seti T6'da.

## Sırada bekleyen (açılmadı)
- Argon: partiler 7, 8, 9
- Argon yeniden okuma 2 kabul edildi: 36 kart, 26'i çözüldü
- Codex: T5b (hızlı tarama). T1b ve T5a'dan sonra.
- T5a kabul edildi (PR #22, 86 test).

## İlerleme
- Kart: 203 / ~316. `tam` 73, `dakikalik` 48, `eksik` 68. Yeniden okunacak 47 (çoğu TradingView/prorealcode/ninjatrader, okunamıyor)
- Backtest: 6 / 21 Codex Algo satırı (T1a)
