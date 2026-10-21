# T5 - YAML yorumlayici ve asama 1 hizli tarama

Sahip: codex-worker. Atayan: lider. **Baslangic: T1a lider onayi + T2 parti 1 onayi sonrasi.**
Hedef: `docs/HEDEF.md`. Kurallar ve kart semasi: `docs/EVRENSEL_KURALLAR.md`.

## Yapilacaklar
1. `engine/spec.py`: `docs/spec/*.yaml` okuyup dogrulayan sema denetleyicisi.
2. `engine/expr.py`: giris/cikis ifade dili icin guvenli ayrıştırıcı (Python `eval` YOK; beyaz liste AST). Desteklenenler: karsilastirma, and/or/not, cross_over/cross_under, `[k]` gecikme, `mtf(...)`.
3. `engine/indicators.py`: bolum D'deki gosterge listesi; her biri icin TA-Lib veya referans degerle birim testi.
4. `backtests/tarama.py`: VectorBT ile asama 1. Evrensel kurallar A1-A9, 4 piyasa, IS donemi, 1x ve 2x maliyet. `ozel_kod: true` kartlari atla, raporla.
5. **Parite testi:** C01 ve C02'yi hem T1a motoruyla hem YAML + tarama ile calistir. Islem listeleri %95+ ortusmeli. Ortusmuyorsa tarama sonucuna guvenilmez.
6. Cikti `results/tarama.csv`: id, piyasa, tf, islem, PF_1x, PF_2x, net_1x, net_2x, sharpe, mdd, maruziyet, asama2_aday (bool), neden.

## Asama 1 → 2 gecis kurali (lider karari)
En az bir piyasada IS'de: islem >= 30, 1x PF >= 1,1 ve 2x net pozitif. Gecemeyen → **Reddedildi (asama 1)**, nedeniyle.

## Kabul kriteri
- `pytest` yesil; parite testi gecer; temiz klonda calisir.
- PR basligi `[Codex-Sol] T5 ...`. `@auditor` etiketle.
