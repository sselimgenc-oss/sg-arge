# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-21 ~23:00 UTC, lider (Opus)

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Codex | T1b: kalan 9 aile (15 satır) | **Sırada; limit açılınca** | Limit açılınca "görev geldi" |
| Sonnet | T10: Argon parti 6'nın 40 kartını standarda getir (T7+T8 kuralları) | Atandı | "Görev geldi" |
| Argon | Parti 7 (40 kart) | Sırada | `argon/PAKET_T2_parti7.md`'yi yapıştır; cevabı `argon/T2_parti7.yaml` adıyla yükle |
| Veri arşivi | Saatlik arşiv | **Tamam** (4. koşu): 62 dosya, 8,5 MB; haftalık otomatik | Yok |

## İlk sonuçlar (T1a, ayrıntı `tartisma/004_t1a_lider_degerlendirme.md`)
2015-2019 (raporu yazanın görmediği dönem) testinde: C01 BIST Geri Çekilme PF 1,76, C02 BIST CCI PF 1,89, C09 ABD CCI PF 1,50 güçlü. C19 Emtia Geri Çekilme negatif. Henüz nihai karar değil; tam test seti T6'da.

## Kullanıcı bilgisayarında
| — | T9 iptal: okunamayan 47 kaynak **Doğrulanamaz (kaynak erişilemedi)** olarak raporlanacak | Kapandı | Yok |

## Sırada bekleyen (açılmadı)
- Argon: partiler 7, 8, 9
- Argon yeniden okuma 2 kabul edildi: 36 kart, 26'i çözüldü
- Codex: T5b (hızlı tarama). T1b'den sonra. **Ek:** BIST saatlik verisinde hisse başına ~727 seans dışı ve ~385 sıfır hacimli bar var (`results/veri_kalitesi_1h.md`). Yahoo 09:30 etiketi ve kapanış seansı olabilir. BIST 1H/4H testlerinden önce çözülecek.
- T5a kabul edildi (PR #22). T7 kabul edildi (PR #26): `tam` kartlarda 0 sözdizimi hatası; taramaya hazır 26 tam + 7 dakikalık kart. T8 tamamlandı (PR #33, #35): hazır kart **49 tam + 11 dakikalık**; göstergeler TA-Lib ile 1e-7 içinde doğrulandı.

## İlerleme
- Kart: 243 / ~316. Taramaya hazır: 49 tam + 11 dakikalık (Argon parti 6 standarda getirilince artacak). Doğrulanamaz (kaynak erişilemedi): 71
- Backtest: 6 / 21 Codex Algo satırı (T1a)
