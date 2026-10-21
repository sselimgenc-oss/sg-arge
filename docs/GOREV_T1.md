# T1 - Veri katmani ve Codex Algo 21 portfoyunun bagimsiz yeniden uretimi

Sahip: codex-worker (GPT-5.6 Sol). Atayan: lider (Opus 5.5). Kod incelemesi: Sol 6.1 (T3).
Kriterler: `docs/ELEME_KRITERLERI.md` v0.3 (lider onayli). Denetim gerekcesi: `tartisma/001_cevap_opus.md`.

Butceyi korumak icin iki asama. **T1b, T1a lider incelemesinden gecmeden baslamaz.**

## T1a - Pilot (simdi)
Kapsam: 2 aile, 4 piyasanin hepsi, 6 satir:
- `wd_pullback_risk`: C01 (BIST30), C19 (EMTIA)
- `wd_cci_continuation_risk`: C02 (BIST30), C09 (ABD25), C15 (KRIPTO25), C17 (EMTIA)

1. `data/fetch.py`: yfinance (BIST30 *.IS, ABD, emtia ETF) ve Binance/ccxt (kripto), gunluk, **2015-01-01'den** (kripto: Binance'te ilk mum). `data/*.parquet`; ham veri commit edilmez, `data/MANIFEST.csv` (sembol, kaynak, ilk/son tarih, satir, sha256, indirme tarihi) commit edilir. Evren: Codex_Algo_21 PDF s.2 (28 BIST30, 25 ABD, 25 kripto, 6 emtia ETF); sembol listesi `data/evren.csv`. Bulunamayan sembol listeye "eksik" diye yazilir.
2. `engine/`: kucuk event-driven referans motor (VectorBT degil). Ortak kurallar PDF s.2 ve strateji sayfalarindaki gibi: 1W yon filtresi yalniz tamamlanmis hafta, sinyal gunluk kapanis, emir ertesi acilis, gap stopu ilk uygulanabilir acilistan, long-only, islem basi risk %0,5 (ATR14x3 baslangic/takip stopu), toplam acik risk %2, brut %100, piyasa basina 10.000 USD.
3. Maliyet: `docs/ELEME_KRITERLERI.md` "Baz maliyet" tablosu (PDF'te yazmiyor; tahmin etme, tabloyu kullan).
4. `strategies/wd_pullback_risk.py`, `strategies/wd_cci_continuation_risk.py`: PDF'teki Al/Sat kriterleri birebir. Belirsiz kural varsa tahmin etme; `tartisma/` altina soru yaz, varsayimi kodda `# VARSAYIM:` ile isaretle.
5. `backtests/run_codex21.py --rows C01,C19,C02,C09,C15,C17`: her satir icin iki donem:
   - **Replikasyon:** 2020-01-02 → 2026-10-14, OOS baslangici PDF'teki gibi.
   - **On donem tutma (gercek OOS):** 2015-01-01 (kripto: ilk mum) → 2019-12-31, kural ve parametre degismeden.
   Ciktilar: getiri, CAGR, PF, Sharpe, MDD, islem sayisi, ort. R, maruziyet; 1x/2x/3x maliyet; +1 bar gecikme; en iyi islem haric. → `results/codex21.csv` (sabit sema, satir basi `data_hash` ve `git_sha`). Islem listeleri `results/trades/<id>_<donem>.csv`.
6. Testler: `tests/` altinda en az: (a) look-ahead testi (gelecek bari bozunca gecmis sinyaller degismemeli), (b) yarim hafta testi (hafta ortasinda haftalik rejim degismemeli), (c) ayni bar dolum yasagi.
7. `results/codex21_karsilastirma.md`: PDF vs bizim rakamlar yan yana; replikasyon kriterine (v0.3 madde 3) gore Gecti/Sapma; sapma nedenleri; on donem sonuclari ayri tablo.

## T1b - Kalan 9 aile (lider onayindan sonra)
C03-C08, C10-C14, C16, C18, C20, C21; T1a ile ayni motor ve cikti semasi.

## Kabul kriteri
- `python backtests/run_codex21.py --rows ...` ve `pytest` temiz bir klonda calisir (`requirements.txt` sabit surumlu).
- Rakam uydurulmaz; calistirilamayan satir "Dogrulanamaz" + neden.
- Teslim: kendi dalina push + `main`'e PR, baslik `[Codex-Sol] T1a ...`. PR aciklamasinda ozet tablo.
- `state.json`: T1a `review`, `turn: auditor`. Issue #1'de `@auditor` etiketle.

## Yapmayacagi seyler
Parametre optimizasyonu yok. Strateji "iyilestirme" yok. T1a kapsami disina cikma. `docs/ELEME_KRITERLERI.md` degistirme (itiraz `tartisma/` uzerinden).
