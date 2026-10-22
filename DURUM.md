# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-22 19:15 UTC, lider (Opus)

## Özet (kullanıcı için)
- **İlk Geçti:** tarihsel evrenle (PIT) C07 ve R01 tüm paper kapılarını geçti.
- **Aşama 2b (son eleme) bitti:** 29 satır, **7 Koşullu**, 22 Reddedildi. Ayrıntı: `results/asama2b_ozet.md`.
  - Güçlü (ABD): **C07** kanal+ADX, **R01**, **G011** PowerX, **M038**. Tek şerh survivorship.
  - Zayıf: **C04** BIST, **A6-010** Emtia, **M015** ABD. Hepsinde ön dönem negatif.
- **T11 (Argon) geldi:** ABD 2015-2026 ve BIST30 2020-2026 tarihsel listeleri tam. BIST 2015-2019 bulunamadı (T11b ile ikinci deneme). Koşullu adaylar tarihsel evrenle (`--evren pit`) yeniden koşuluyor. ABD'de survivorship kalkınca adaylar **Geçti** olabilir.
- T16: 50 eksik kartın hiçbiri tamamlanamadı; sinyal kuralı kaynakta yok. Doğrulanamaz kalıyorlar.
- **Rotasyon (T22) taraması:** 13 kart, 12 satır Aşama 1'i geçti. Çoğu kaldıraçlı ETF stratejisinde MDD %40-80. MDD'si %15 altındakiler: A6-004 ABD (%8), M017 ABD (%12). Aşama 2 bağlantısı T23'te.
- Gün içi kripto taraması: veri tam (25 coin, 30m/15m/5m), tarama koşuyor.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Sonnet | **T23: rotasyon kartlarını Aşama 2a/2b + portföye bağla** (`docs/GOREV_T23.md`) | Atandı | "Görev geldi" |
| Codex | **T24: gün içi Aşama 2b + saat/gün ilkelleri (A6-019)** (`docs/GOREV_T24.md`), model **Sol** | Atandı | "Görev geldi" |
| Argon | **T11b: BIST30 2015-2019 değişiklik tabloları** (küçültülmüş paket `argon/PAKET_T11b_bist_2015_2019.md`) | Limit 22:22'de açılır | Yeni paketi yapıştır; CSV'yi `argon/`a yükle |
| Lider | Gün içi kripto taraması (1H/30m/15m/5m, veri tam) | Koşuyor | Yok |

## Tamamlananlar (son)
- T17 (Codex, PR #82): gün içi Aşama 2a null testi (`--tf`, `--isci`). Günlük null sonuçları ve işlem paritesi birebir.
- T22 (Sonnet, PR #80): `engine/rotasyon.py` + D12; 13 kart taşındı, Composer paritesi korelasyon 1,0000. Pytest 247, motor paritesi birebir. A6-021 short fazına.
- T21 (Sonnet, PR #78): 7 kart taşındı (A3-002a/f/h/i, A3-010b, O1-039, P3-008); 13 kart Argon T19'a. Parite birebir.
- T20 (Sonnet, PR #75): 5 kart taşındı (A3-002b/c, M013, M010, M027), O1-070 kapsam dışı, 16 kart gerekçeyle kaldı. Motor paritesi birebir.
- T18 (Sonnet, PR #72): portföy + korelasyon kodu; gerçek koşu lider.
- **PIT yeniden koşu** (`results/asama2b_pit_ozet.md`): C07 ve R01 (ABD) **Geçti**; C04, G011, M015, M038 Reddedildi.
- **Portföy** (`results/portfoy.md`): C07 + R01 + A6-010, eşit risk. OOS +%7,5, MDD %2,9, korelasyon 0,20.
- T16 (Sonnet, PR #70): 50 kart incelendi, terfi 0.
- T11 (Argon): tarihsel endeks listeleri. Eksik veri: SODA/TRKCM (2020'de SISE'ye birleşti; Yahoo'da veri yok).
- T12 (Sonnet, PR #67): gün içi tarama, roi_tablosu, motor hızlandırma #2. C01/C09 gerçek veri paritesi birebir.
- asama2b: R01 EndeksYok düzeltmesi; PIT evrenle koşulunca ABD'de survivorship şerhi kalkar, BIST'te "2015-2019 PIT yok" şerhi kalır.

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
