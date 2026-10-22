# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-22 15:10 UTC, lider (Opus)

## Özet (kullanıcı için)
- **Aşama 2b (son eleme) 1. koşu bitti:** 24 satır, **3 Koşullu**, 21 Reddedildi. Ayrıntı: `results/asama2b_ozet.md`.
  - **C07 ABD (kanal+ADX):** en güçlü aday. OOS 94 işlem, 3x maliyette +%37. Tek şerh survivorship; T11 sonrası PIT evrenle yeniden koşulacak.
  - **C04 BIST** ve **A6-010 Emtia:** zayıf. Ön dönem negatif, C04'te OOS örneği az.
- BIST/ABD güncel evrenle en fazla Koşullu olabilir (kural). "Geçti" için T11 (Argon) tarihsel evren gerekli.
- **2. koşu sürüyor:** R01 Koşullu, G011 Koşullu, G007 Reddedildi; M015, M038, O3-003 bekliyor.
- Gün içi kripto taraması: veri (30m/15m/5m) lider ortamında iniyor.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Sonnet | **T16: eksik kart triyajı** (47 kart, `docs/GOREV_T16_T17.md`) | Atandı | "Görev geldi" |
| Codex | **T17: gün içi null testi** (`docs/GOREV_T16_T17.md`), model **Sol** | Atandı | Limit 21:10'da açılınca "görev geldi" |
| Argon | **T11: tarihsel endeks bileşenleri** (BIST30 dönemsel, ABD en büyük 25) | Atandı | `argon/PAKET_T11_tarihsel_evren.md`; iki CSV'yi `argon/`a yükle |
| Lider | Aşama 2b 2. koşu + gün içi kripto taraması | Koşuyor | Yok |

## Tamamlananlar (son)
- T12 (Sonnet, PR #67): gün içi tarama, roi_tablosu, motor hızlandırma #2. C01/C09 gerçek veri paritesi birebir.
- T15 (Codex, PR #66): bekleyen giriş emirleri. T14 (PR #65): PIT evren. T13 (PR #63): SONUC raporu.
- asama2b: endeks serisi evren dışından okunur (R01 EndeksYok düzeltmesi, lider).

## İlk sonuçlar (T1a, ayrıntı `tartisma/004_t1a_lider_degerlendirme.md`)
2015-2019 (raporu yazanın görmediği dönem) testinde: C01 BIST Geri Çekilme PF 1,76, C02 BIST CCI PF 1,89, C09 ABD CCI PF 1,50 güçlü. C19 Emtia Geri Çekilme negatif. Henüz nihai karar değil; tam test seti T6'da.

## Aşama 2a sonucu (`tartisma/008`)
146 satırdan **8'i** rastgele giriş testini geçti: A6-010 Emtia, P3-011 Kripto, R01 ABD, G007 Kripto, G011 ABD (PowerX), M015 ABD (Connors Cumulative RSI), M038 ABD, O3-003 ABD. Uyarı: şansla ~7 yanlış pozitif beklenir; T6b belirleyici.

## Sırada bekleyen (açılmadı)
- Argon parti 11 (28 kaynak, md listeleri) ve parti 12 (13 strateji: güncellenmiş liste PDF'i + Trend Trigger). Envanter: `tartisma/006_pdf_envanteri.md` (repoda toplam ≈392 strateji).
- **Kullanıcıdan:** repoda olmayan strateji PDF'leri (Paper_Test_8'in "256 stratejilik 3 PDF" dediği kaynaklar dahil) `kaynak_pdf/` klasörüne yüklenmeli.
- T5b-2: dakikalık ve gün içi kartların kripto taraması (Binance). Kullanıcı kararı: dakikalıklar yalnız kriptoda test edilir, elenmez.
- Argon: tüm partiler tamam (parti 8: 22 gizli, 10 okunamadı)
- Argon yeniden okuma 2 kabul edildi: 36 kart, 26'i çözüldü
- Codex: T1b, sonra T6 (tam doğrulama, `docs/GOREV_T6.md`). T5b Sonnet'e geçti. **Ek:** BIST saatlik verisinde hisse başına ~727 seans dışı ve ~385 sıfır hacimli bar var (`results/veri_kalitesi_1h.md`). Yahoo 09:30 etiketi ve kapanış seansı olabilir. BIST 1H/4H testlerinden önce çözülecek.
- T5a kabul edildi (PR #22). T7 kabul edildi (PR #26): `tam` kartlarda 0 sözdizimi hatası; taramaya hazır 26 tam + 7 dakikalık kart. T8 tamamlandı (PR #33, #35): hazır kart **49 tam + 11 dakikalık**; göstergeler TA-Lib ile 1e-7 içinde doğrulandı.

## İlerleme
- Kart aşaması **tamamlandı**: 326 kart (324 strateji + C01/C02 parite). tam 99, dakikalık 57, eksik 123, gizli 29, ihtiyari 14. Doğrulanamaz (kaynak erişilemedi): 93. İlk tarama: 42 kart, 35 aşama 2 adayı (`tartisma/005`).
- Backtest: Codex Algo 21/21 satır (T1a+T1b, `tartisma/007`). İlk tarama 42 kart + P02/R01. T6a (rastgele giriş + BIST USD) lider ortamında koşuyor.
