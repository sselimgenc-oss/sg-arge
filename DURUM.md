# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-22 gece, lider (Opus)

## Sabah özeti (kullanıcı için)
- **İlk geniş tarama yapıldı.** 42 günlük/haftalık strateji 4 piyasada test edildi: 35'i ikinci aşamaya kaldı, 4'ü elendi, 3'ü motor desteği eksik olduğu için beklemede. Ayrıntı: `results/tarama_ozet.md`, değerlendirme: `tartisma/005_tarama1_lider_degerlendirme.md`.
- **Önemli uyarı:** 2020-2024'te BIST (TL) medyan +%1.037, kripto +%332 yükseldi. Bu ortamda uzun pozisyonla trend izleyen her strateji iyi görünüyor. "35 strateji geçti" sonucu henüz bir şey kanıtlamıyor.
- **Lider kararı:** İkinci aşamaya iki sert test eklendi: BIST USD bazında test edilecek, ve her strateji "rastgele giriş" sınamasını geçmek zorunda. Bu sınamada strateji, aynı çıkış kurallarıyla rastgele zamanlarda girmekten belirgin şekilde iyi olmalı; değilse kârı piyasanın yükselişinden geliyordur. Görev tanımı: `docs/GOREV_T6.md` (Codex, T1b'den sonra).

## Bugün ilk yapılacaklar
1. Codex limiti açıldıysa: "görev geldi" (T1b), Issue #1'deki son Codex görevi.
2. ~~Argon~~ kart işi bitti.
3. ~~Sonnet limiti~~ yenilendi → T6a verildi.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Codex | **T13: sonuç raporu üreticisi** (`SONUC.md`). Model: Terra | Atandı | "Görev geldi" |
| Sonnet | **T12: kripto gün içi/dakikalık tarama** + roi_tablosu + parti 11 düzeltme | Atandı | "Görev geldi" |
| Argon | **T11: tarihsel endeks bileşenleri** (BIST30 dönemsel, ABD en büyük 25; survivorship düzeltmesi için) | Atandı | `argon/PAKET_T11_tarihsel_evren.md`'yi yapıştır; iki CSV'yi `argon/`a yükle |
| Veri arşivi | Saatlik arşiv | **Tamam** (4. koşu): 62 dosya, 8,5 MB; haftalık otomatik | Yok |

## İlk sonuçlar (T1a, ayrıntı `tartisma/004_t1a_lider_degerlendirme.md`)
2015-2019 (raporu yazanın görmediği dönem) testinde: C01 BIST Geri Çekilme PF 1,76, C02 BIST CCI PF 1,89, C09 ABD CCI PF 1,50 güçlü. C19 Emtia Geri Çekilme negatif. Henüz nihai karar değil; tam test seti T6'da.

## Aşama 2a sonucu (`tartisma/008`)
125 satırdan **3'ü** rastgele giriş testini geçti: A6-010 Emtia, P3-011 Kripto, R01 ABD (Qullamaggie). Giriş sinyalleri genel olarak rastgele girişten ayırt edilemiyor; kâr piyasa yönü ve çıkış yapısından geliyor. Sırada T6b (lider koşusu).

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
