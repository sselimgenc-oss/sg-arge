# T5 - YAML yorumlayici ve asama 1 hizli tarama

Atayan: lider. Iki parca:
- **T5a (Sonnet, simdi):** madde 1-3 (sema denetleyici, ifade ayristirici, gosterge kutuphanesi) + testler. Internet gerektirmez.
- **T5b (Codex, T1a onayindan sonra):** madde 4-6 (tarama, parite testi, cikti). `ozel_kod` kartlarinin elle kodlanmasi T5c (sonra).
Hedef: `docs/HEDEF.md`. Kurallar ve kart semasi: `docs/EVRENSEL_KURALLAR.md`.

## Yapilacaklar
1. `engine/spec.py`: `docs/spec/*.yaml` okuyup dogrulayan sema denetleyicisi.
2. `engine/expr.py`: giris/cikis ifade dili icin guvenli ayrıştırıcı (Python `eval` YOK; beyaz liste AST). Desteklenenler: karsilastirma, and/or/not, cross_over/cross_under, `[k]` gecikme, `mtf(...)`.
3. `engine/indicators.py`: bolum D + D2 + D4 gosterge/ilkel listesi (ott, pmax, rvol, stdev, var, rrs, atr_ratio, takvim ilkelleri dahil). Her biri icin bilinen referans degerle birim testi (TA-Lib varsa onunla karsilastir; yoksa elle hesaplanmis kucuk ornek). Pine/TradingView tanimiyla uyum esas (ornegin RSI = RMA tabanli).
3b. `engine/spec.py --kontrol docs/spec/`: tum kartlari dogrular. Ayrıştırılamayan giris/cikis ifadelerini, tanimsiz gosterge adlarini ve `tam` olup ifadesi bos kartlari `results/kart_kontrol.md`'ye listeler. Kartlari degistirmez.
4. `backtests/tarama.py`: VectorBT ile asama 1. Evrensel kurallar A1-A9, 4 piyasa, IS donemi, 1x ve 2x maliyet. `ozel_kod: true` kartlari atla, raporla.
5. **Parite testi:** C01 ve C02'yi hem T1a motoruyla hem YAML + tarama ile calistir. Islem listeleri %95+ ortusmeli. Ortusmuyorsa tarama sonucuna guvenilmez.
6. Cikti `results/tarama.csv`: id, piyasa, tf, islem, PF_1x, PF_2x, net_1x, net_2x, sharpe, mdd, maruziyet, asama2_aday (bool), neden.

## Asama 1 → 2 gecis kurali (lider karari)
En az bir piyasada IS'de: islem >= 30, 1x PF >= 1,1 ve 2x net pozitif. Gecemeyen → **Reddedildi (asama 1)**, nedeniyle.

## Kabul kriteri
- `pytest` yesil; parite testi gecer; temiz klonda calisir.
- PR basligi `[Codex-Sol] T5 ...`. `@auditor` etiketle.

## T5a teslim notu (lider, PR #22)
Kart gosterge kutuphanesi `engine/gosterge.py` (Pine uyumlu, kanonik). `engine/indicators.py` T1a'nin referans fonksiyonlari olarak degismeden kalir. T5b taramasi `engine/gosterge.py` + `engine/expr.py` + `engine/spec.py` kullanir; parite testi (madde 5) iki kutuphane arasindaki farki da gosterir.

## T5b ek madde (lider)
7. BIST saatlik veri temizliği: `results/veri_kalitesi_1h.md`'de hisse başına ~727 seans dışı ve ~385 sıfır hacimli bar var. Nedenini bul (yfinance 09:30 bar etiketi, kapanış seansı, tatil). Seansa hizalı temiz 1H/4H serisi üret (`engine/resample.py`). BIST gün içi kartları bu düzeltme olmadan taranmaz.

## T5b yeniden atama ve kapsam (lider, 2026-10-21)
**Sahip: claude-moderator (Sonnet).** Codex T1b ve T6'da kalir. Gerekce: yorumlayiciyi Sonnet yazdi; tarama kritik yol.

**Mimari karari: VectorBT yok.** Tarama, T1a'nin event-driven motorunu (`engine/portfolio.py`) kullanir; sinyaller YAML karttan (`engine/expr.py` + `engine/gosterge.py`) gelir. Boylece motor tek, parite sorunu yok.

**T5b-1 (ilk teslim): yalniz gunluk/haftalik kartlar** (`tf` 1D/1W, `tam`, `ozel_kod: false`).
1. `backtests/tarama.py --kartlar docs/spec/ --tf 1D`: kart → sinyal → `engine/portfolio.py`. EVRENSEL_KURALLAR A1-A9 + D2-D4: `dolum: kapanis` iki varyant, `piyasa_kisiti`, `stop`/`hedef`/`iz_suren`/`zaman_stop`/`kismi_kar`/`roi_tablosu`. Motorun desteklemedigi bir alan varsa karti atla ve `neden: motor_destegi_yok:<alan>` yaz; sessizce yok sayma.
2. **Parite testi:** C01 ve C02 icin YAML kart yaz (`docs/spec/C01.yaml`, `C02.yaml`; kurallar `strategies/*.py` ile birebir). Ayni motor ve veriyle T1a islem listeleri birebir (%100) cikmali. Test sentetik veride `pytest` icinde; gercek veride Actions'ta.
3. Donem: IS 2020-01-01 → 2024-09-30. Maliyet 1x ve 2x (baz tablo). 4 piyasa (`piyasa_kisiti` varsa yalniz o).
4. Cikti: `results/tarama.csv` (madde 6 semasi + `kart_yazari`, `piyasa_kisiti`) ve `results/tarama_ozet.md` (gecen/kalan sayilari, nedenler).
5. `.github/workflows/tarama.yml` (`workflow_dispatch`): gunluk veriyi ceker, taramayi calistirir, `results/`a commit eder (push oncesi `git pull --rebase`, codex21.yml gibi).
6. Gecis kurali: yukaridaki "Asama 1 → 2" kurali. **Bu asamada OOS ve 2015-2019 verisine bakilmaz** (yalniz IS); onlar asama 2'de (T6) kullanilacak, gormeden tutulur.

T5b-2 (sonra): gun ici kartlar (kripto 1m-1H, BIST/ABD/emtia 1H; madde 7 BIST temizligi dahil).
