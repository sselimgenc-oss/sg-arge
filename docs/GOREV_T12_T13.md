# T12 (Sonnet) ve T13 (Codex) — lider, 2026-10-22

## T12 — Kripto gun ici / dakikalik tarama (Sonnet)
On adim: Argon parti 11 kartlarindaki 4 `tam` hatasini T10 kurallariyla duzelt.
1. Motor: `roi_tablosu` destegi (Freqtrade zaman bazli ROI; G003, G012, A3-010/011). D5'e anlami yaz. T1a paritesi bozulmamali.
2. `backtests/tarama.py --tf 1m,5m,15m,30m,1H` destegi: veri Binance `data-api.binance.vision` (gerekirse `data/fetch.py`'ye `--interval 5m/15m/30m` ekle; 1H arsivi zaten var). Kripto disi piyasalarda 1H alti kart → `Dogrulanamaz (dakikalik veri yok)`. 1H kartlar 4 piyasada (BIST/ABD/emtia 1H yfinance arsivi ~2 yil: IS = ilk 2/3, OOS = son 1/3; EVRENSEL_KURALLAR C).
3. Kripto donem: IS 2020-01-01 → 2024-09-30 (2018-2019 ve OOS gorulmez).
4. Cikti: `results/tarama.csv`'ye ek satirlar (`tf` sutunu ile), `results/tarama_gunici_ozet.md`. Is akisi: `.github/workflows/tarama.yml` `tf` girdisiyle.
5. BIST 1H temizligi (`GOREV_T5.md` madde 7): seans disi/sifir hacimli barlar ayiklanmadan BIST 1H taranmaz; ya temizle ya da BIST 1H satirlarini `Dogrulanamaz (veri kalitesi)` yaz.
PR: `[Claude-Mod] T12 gun ici tarama`.

## T13 — Sonuc raporu ureticisi (Codex) — **Onerilen model: Terra** (mekanik)
`backtests/sonuc_raporu.py`: tum ciktilari birlestirip kullaniciya teslim edilecek listeyi uretir. Hesap yapmaz, yalniz birlestirir.
Girdiler: `docs/spec/INDEKS.csv`, `docs/spec/YENIDEN.csv`, kart YAML'lari (`spec_durumu`, `ozel_kod_nedeni`, `piyasa_kisiti`), `results/tarama.csv`, `results/asama2a.csv`, `results/asama2b.csv`, `results/codex21.csv`.
Her strateji (kart id; Codex Algo icin C01-C21) icin tek nihai durum, oncelik sirasiyla:
1. `asama2b` karari varsa: Gecti / Kosullu / Reddedildi (+ gerekce)
2. `asama2a` reddi: Reddedildi (piyasa betasi | BIST USD)
3. tarama reddi: Reddedildi (asama 1: neden)
4. Dogrulanamaz alt nedenleri: kaynak erisilemedi (YENIDEN), kural eksik (`eksik`), gizli, ihtiyari, ozel kod (`ozel_kod_nedeni`), piyasa ozgu, dakikalik veri yok, motor destegi yok, orneklem
5. Kapsam disi / sadece short / kaldirac fazina ertelendi
Piyasa bazli satirlar varsa strateji durumu "en iyi piyasa"dir; piyasa kirilimi ayri tabloda.
Ciktilar:
- `results/sonuc.csv`: id, ad, kaynak, tarz, tf, nihai_durum, alt_neden, en_iyi_piyasa, piyasa_ayrintisi (json)
- `results/SONUC.md`: Turkce. (a) Ozet sayilar, (b) **Gecti ve Kosullu** tablosu (en uste), (c) Reddedilenler (nedene gore gruplu), (d) Dogrulanamaz (nedene gore gruplu), (e) Yontem ve uyarilar (survivorship, BIST USD, rastgele giris bulgusu: `tartisma/008`).
- `tests/test_sonuc_raporu.py`: kucuk sentetik girdilerle oncelik kurallarinin testi.
Rapor eksik girdi dosyasinda calismaya devam eder ("henuz yok" yazar).
PR: `[Codex-Sol] T13 sonuc raporu`.
