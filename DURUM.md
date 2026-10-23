# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-23, lider (Opus) — **FAZ 1 KAPANDI** (`docs/FAZ1_SONUC_RAPORU.md`). **Yeni iş: U1, kendi stratejilerimiz (kripto gün içi)** (`docs/GOREV_U1.md`)

## Özet (kullanıcı için) — Faz 1 nihai
- **Geçti 2:** C07, R01 (ABD günlük, PIT evrenle).
- **Koşullu 3:** A6-010 (emtia günlük), T8-07 ve V2B (emtia 1H).
- **Reddedildi 132**, **Doğrulanamaz 273**, **Test edilmedi 5** (dakikalık kartlar), Ertelendi/Kapsam dışı 7. Toplam 422.
- **Önerilen portföy** (C07 + R01 + A6-010, eşit ağırlık): OOS getiri %7,5, MDD %2,9.
- **Kıl payı denetimi:** gözden kaçan strateji yok.
- Ayrıntı: `docs/FAZ1_SONUC_RAPORU.md`. Faz 2 planı: `docs/FAZ2_NOTLAR.md`.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
**Kapsam: yalnız kripto** (kullanıcı kararı, 2026-10-23; BIST/ABD/emtia/FX iptal, Dukascopy çalışması kapsam dışı). **U1: Kendi stratejilerimiz, kripto gün içi** (`docs/GOREV_U1.md`, revize 2026-10-23: swing iptal, 1 saat kurulum + 15/5 dk giriş, Hat 0 = T8-07/V2B kriptoda). **Hedef:** yılda %20-30 net, MDD ≤ %15.

| Ajan | Görev |
|---|---|
| Lider | Codex'in U1c PR'ını denetler, sonra `results/U1_SONUC.md` |
| Sonnet | U1d bitti (PR #152). **Şimdi U2a** (`docs/GOREV_U2.md`): kripto short motoru (PR #136'dan), funding maliyeti ve verisi → PR. **Sırada U3** (`docs/GOREV_U3.md`): dünya genelinde 4s/1s kurulum + 15dk/5dk giriş stratejileri, en az 100 kayıt, backtest yok |
| Argon | **U-A1** (`argon/PAKET_UA1_uc_enstruman.md`, Gemini 3.8): XU030 endeks kontratı, SPX, XAUUSD için veri kaynakları, kontrat/maliyet, 128 kartın uygunluk ayrımı, yöntem denetimi. Yalnız araştırma; kapsam kripto kalır, test/kod açılmaz (kullanıcı kararı, 2026-10-23) |
| Codex | **U1c** (`docs/GOREV_U1c_CODEX.md`): 14 coin 1s/15dk/5dk verisi + U1 hunisinin gerçek koşusu → PR (kullanıcı kararı, 2026-10-23: Codex geri döndü) |

## T35/T36 kapanış özeti
- **T35 (bölgesel strateji toplama):** 80 kayıt (`arastirma/TUM_KAYITLAR.csv`), 4 kol, 2 parti. Kullanıcı örneklem doğrulamaları tuttu. Argon'un türetilmiş PF değerleri temizlendi. Değerlendirmeler: `tartisma/010`, `tartisma/011`. Kısa liste: `tartisma/011`.
- **T36 (kısa liste testi):** Kapatıldı.
  - Ücretsiz dakikalık veri yalnız USDJPY/Nasdaq için Dukascopy'de var. İndirici hazır (`data/dukascopy.py`), indirme yapılmadı.
  - Çin/WDO/Nifty adayları veri yokluğundan Doğrulanamaz.
- **Lider değerlendirmesi:** Paper'a en sağlam adaylar hâlâ Faz 1'in C07 + R01 (+ A6-010) üçlüsü. Yeni listeden en umutlu olanlar JP-005 ve JP-004 (USDJPY); test edilmedi.

## Tamamlananlar (son)
- **T32 (Codex/Terra) tamam:** 2H/4H mumlar (D16) ve FX8 piyasası + pip stop. Gerçek koşu: M013 (FX8 4H, PF 0.79) ve O2-005 (FX8 1H, PF 0.62) Aşama 1’de Reddedildi. Not: lider ilk tahmini (~80 kart) yanlıştı; bu piyasalara bağlı kartların çoğu kural eksik/özel kod. SONUC: Geçti 2, Koşullu 3, Reddedildi 132, Bekliyor 5.
- **Kıl payı denetimi (`results/denetim_kil_payi.md`, ön kayıtlı):** 2a'da elenen 147 satıra risk testi → BH sonrası 0 keşif (ham p<0.05: 7, şans beklentisi 7.4); yalnız OOS ile elenen 2 satır OOS'ta gerçekten bozulmuş. Eleme iyi strateji kaçırmamış; SONUC değişmedi.
- **Bekleyen 15 stratejiden 9'u sonuçlandı (lider, düzeltilmiş motorla, PR #104 sonrası):** hepsi Reddedildi. A6-019 ve M016 Aşama 1'de; A1-025, A6-003, M008, M010, O1-039 ve A2-002/A2-021 (1H) rastgele giriş testinde (piyasa betası); M036 ABD sabit evrende Koşullu iken tarihsel evrende (PIT) 2x maliyette PF<1,2 ve 3x maliyette net≤0 ile Reddedildi; P3-008 kripto OOS ortR≤0. Nihai liste değişmedi: Geçti 2 (C07, R01), Koşullu 3. Kalan Bekliyor 6: A3-002a/c ve O1-064 (1m veri yok), A3-002d/f (T30 bellek), M013 (4H desteklenmiyor). Not: Codex C10 yeni veriyle sınırda (p 0,052→0,050) karar değiştiriyor; sağlam değil, main'deki Reddedildi korundu.
- **Lider motor düzeltmesi (bekleyen emir, D8):** bar içinde dolan limit/stop girişte motor aynı barın açılışıyla `gap_target` çıkışı yapıyordu (açılış girişten önce: look-ahead) ve aynı barda hedefe dokunmayı kâr sayıyordu (bar içi sıra bilinmez). Artık bar içi dolumda o bar yalnız stop kontrol edilir; hedef ertesi bardan. Etki: A1-025 ve M016 (One Percent a Week) PF 3-5'ten ~1'e düştü. Etkilenen kartlar (giris_emri olan 10 kart) yeniden taranıyor. Test eklendi.
- **Gün içi huni (lider, gerçek koşu):** 1H/30m/15m/5m tarama. Kripto 30m/15m/5m'de aday yok. 1H'de 9 aday (ABD/EMTIA, yfinance ~2 yıl) → 2a'da 3 geçti (O1-004, T8-07, V2B; hepsi EMTIA) → 2b: **T8-07 ve V2B Koşullu** (OOS +%5,8 / +%3,1, bootstrap MDD95 %7,9 / %8,3; şerh: 1H ön dönem verisi yok), O1-004 Reddedildi. A3-001/A3-002d/A3-002f 5m taraması bellek yetersizliğinden koşulamadı (T30).
- **T11b (Argon):** BIST30 2015-2019, 20 çeyrek × 30 hisse, Borsa İstanbul duyurularıyla. Lider denetimi: tekrar yok, çeyrek değişiklikleri zincirleme tutarlı, 2019-Q4 listesi 2020-Q1 listesine bağlanıyor (yalnız KOZAL→TRALT, KOZAA→TRMET kod değişikliği). `data/evren_pit.py` iki listeyi birleştirir; asama2b'de BIST PIT şerhi kalktı. Nihai listeye etkisi yok (tek BIST adayı C04 IS null testinde elenmişti).
- T27 (Sonnet, PR #99): paper altyapısı (`paper/`: günlük sinyal, sanal defter, parite, RAPOR, panel `data.json`, `paper.yml`). Lider doğrulaması: pytest 294, gerçek veri parite birebir (292 işlem), motor değişikliği eski sonuçları değiştirmedi. **Paper Faz 2 (kullanıcı kararı):** tüm stratejiler bitince toplu başlar. `paper.yml` zamanlaması kapalı; `PANEL_TOKEN` eklendi, hazır bekliyor.
- T29 (Codex, PR #97): `huni.yml` uçtan uca huni (veri → tarama → 2a → 2b sabit/PIT → portföy → SONUC) ve sonuçları PR olarak açar; mevcut 4 iş akışı da artık main'e doğrudan push etmez, PR açar. Kullanıcı ayarı: Actions'ın PR açma izni açık.
- T28 (Codex, PR #92): `.github/workflows/ci.yml`. Her PR'da pytest + spec kontrolü + main/PR gerçek veri paritesi (C01/C09/G011/M015/C07/R01 tarama, R01/C07 asama2b). `[parite-farki-bekleniyor]` etiketiyle bilinçli fark.
- **Rotasyon Aşama 2 (gerçek koşu, lider):** 2a'da 12 satırdan 7'si null'u geçti (A4-002, A6-004 ABD, M017, M020a ABD/KRİPTO, O2-025, O2-027). 2b'de 7'si de **Reddedildi**: bootstrap MDD95 > %15 (A6-004 %15,8 en yakını; diğerleri %29-92). Kaldıraçlı ETF stratejileri yüksek getiri ama kabul edilemez düşüş. `SONUC.md` yeniden üretildi.
- Lider düzeltmesi: `asama2a.py --kart-ids` koşulmayan kartların satırlarını siliyordu; artık yalnız seçilen kartlar değişir (test eklendi).
- T26 (Codex, PR #89): BIST 1H saat etiketi normalize edildi (Yahoo :30 → tam saat). Açılış barlarında fiyatı değişen sıfır hacim (%5-7) uydurmadan düzeltilemez; kalite kapısı kapalı, BIST 1H Doğrulanamaz kalır (veri düzelirse otomatik açılır).
- T25 (Sonnet, PR #88): `results/SONUC.md` + `SONUC.csv` başarılı/başarısız listesi (Geçti: C07, R01; Koşullu: A6-010).
- T24 (Codex, PR #85): gün içi Aşama 2b + saat ilkeleri (D14), A6-019 taşındı. Lider: main ile çakışma çözüldü, `--kart-ids` satır silme hatası düzeltildi.
- T23 (Sonnet, PR #84): rotasyon kartları Aşama 2a (PF+CAGR null) / 2b / portföye bağlandı. T17 ile çakışmayı lider çözdü; günlük 2a/2b ve işlem paritesi birebir.
- **Lider düzeltmesi:** T17 sonrası `asama2b` Codex satırları (C01-C21) `trusted_inputs` hatasıyla çöküyordu; `CodexPrepared.run` hızlı null yoluna uyarlandı, regresyon testi eklendi. C04/C07 sonuçları eskisiyle birebir.
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
