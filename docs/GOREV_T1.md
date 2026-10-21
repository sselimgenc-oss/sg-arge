# T1 - Veri katmani ve Codex Algo 21 portfoyunun bagimsiz yeniden uretimi

Sahip: codex-worker (GPT-5.6 Sol). Moderator: claude-moderator.

## Amac
Kanit seviyesi A satirlarinin (docs/KATALOG.csv, C01-C21) rakamlarinin bagimsiz olarak tekrar uretilebildigini dogrula.

## Yapilacaklar
1. `data/fetch.py`: yfinance (BIST30 *.IS, ABD hisse, emtia ETF) ve Binance/ccxt (kripto) ile 2020-01-01'den gunluk veri cek, `data/*.parquet` olarak sakla. Evren: Codex_Algo_21 PDF s.2 (28 BIST30, 25 ABD, 25 kripto, 6 emtia ETF).
2. `strategies/`: 11 stratejinin her biri icin ayri modul (PDF'teki Al/Sat kriterlerini birebir uygula; kodlar: wd_pullback_risk vb.). Ortak kurallar: 1W yon filtresi (tamamlanmis hafta), sinyal gunluk kapanis, emir ertesi acilis, long-only, islem basi risk %0,5 ATR14x3 stop, toplam acik risk %2, brut %100, komisyon varsayimi PDF'tekiyle ayni.
3. `backtests/run_codex21.py`: PF, Sharpe, MDD, islem sayisi, OOS (baslangic 03.10.2024), 2x/3x maliyet, +1 bar gecikme ciktilari -> `results/codex21.csv`.
4. `results/codex21_karsilastirma.md`: PDF rakamlari ile bizimkileri yan yana koy, sapmasi >%25 olanlari isaretle.

## Kabul kriteri
- Kod tekrar calistirilabilir (`python backtests/run_codex21.py`), seed/veri tarihi kayitli.
- Sapma nedenleri (veri kaynagi, kurumsal aksiyon, tarih) not edilmis.
- Bitince `state.json` icinde T1 `done`, turn `claude-moderator` yapilir; issue'da `@claude-moderator` etiketlenir.

## Yapmayacagi seyler
Parametre optimizasyonu yok; PDF kurali neyse o. Eksik kural varsa tahmin etme, issue'ya soru yaz.
