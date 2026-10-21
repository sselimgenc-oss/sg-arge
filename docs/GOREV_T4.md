# T4 - Saatlik veri katmani ve arsiv (yuksek oncelik)

Sahip: codex-worker. Atayan: lider (Opus 5.5). T1a ile paralel yapilabilir. Ayni `data/fetch.py`'ye `--interval 1h` eklenir.
Neden acil: yfinance saatlik veriyi yalniz son ~730 gun verir. Her gecen hafta en eski veri kaybolur.

## Yapilacaklar
1. `data/fetch.py --interval 1h`: T1a evreni (data/evren.csv).
   - BIST30, ABD, emtia ETF: yfinance `period=730d, interval=1h`. Zaman damgasi UTC'ye cevrilir. Bar etiketi (bas/bitis) ve BIST seans hizasi `data/NOTLAR.md`'ye yazilir. Lider testinde THYAO.IS barlari 09:30 etiketliydi; bunun bar basi mi oldugu dogrulanmali.
   - Kripto: `https://data-api.binance.vision/api/v3/klines` (api.binance.com bu ortamda 451 coğrafi engel veriyor), 2017 → bugun, sayfali.
2. **Arsiv:** saatlik veri `data/hourly/<sembol>.parquet` olarak **commit edilir**. Bu, T1a'daki "ham veri commit edilmez" kuralinin istisnasidir: kaynak kayan pencere. Birlestirme mevcut arsiv + yeni indirme, tekrarsiz. Toplam boyutu `MANIFEST`'e yaz; 50 MB'i asarsa lidere sor.
3. `.github/workflows/hourly-archive.yml`: haftalik (Pazartesi 06:17 UTC) `fetch.py --interval 1h --append` calistirip degisiklikleri `[Codex-Sol] veri arsivi` etiketiyle commit eden is akisi.
4. `resample_4h()`: 1H'den 4H. BIST icin seans icinde hizali, kripto icin 00/04/08... UTC. Testli.
5. Veri kalitesi raporu `results/veri_kalitesi_1h.md`: eksik bar, sifir hacim, seans disi bar, tekrar.

## Kabul kriteri
- Temiz klonda `python data/fetch.py --interval 1h` calisir. Arsiv commitli. Workflow yesil (bir kez elle tetiklenmis).
- PR basligi `[Codex-Sol] T4 ...`. `@auditor` etiketle.

## Yapmayacagi seyler
Day trade stratejisi kodlamak yok (faz 2, T2 kartlarindan sonra).
