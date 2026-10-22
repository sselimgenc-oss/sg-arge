# T14 ve T15 (Codex) — lider, 2026-10-22

## T14 — Point-in-time evren (survivorship duzeltmesi) — **Onerilen model: Terra**
Argon T11 ile iki CSV toplayacak (`argon/T11_bist30.csv`, `argon/T11_abd25.csv`; bicim `argon/PAKET_T11_tarihsel_evren.md`). Altyapiyi simdi kur; veri gelince lider baglar.
1. `data/evren_pit.py`: CSV'leri okur → `(tarih, piyasa) -> o tarihte gecerli sembol kumesi`. BIST: `donem_baslangic`'tan bir sonrakine kadar gecerli; ABD: `yil` boyunca gecerli. `bulunamadi` donemleri: onceki gecerli liste tasinir ve uyari loglanir.
2. Motor entegrasyonu (`engine/portfolio.py`'ye dokunmadan, ince sarmalayici): bir sembolde **yeni giris** yalniz o tarihte evrende ise acilir; evrenden cikan sembolde acik pozisyon kendi cikis kuraliyla kapanir (zorla kapatma yok).
3. Veri: evrene girip `data/evren.csv`'de olmayan semboller icin `data/fetch.py` ile gunluk veri indirilebilsin (`data/evren_pit_semboller.csv` uretilir). Delist olmus BIST/ABD sembolleri yfinance'ta bulunamazsa `eksik` olarak raporla.
4. `backtests/run_codex21.py`, `tarama.py`, `asama2b.py` icin `--evren pit` secenegi (varsayilan: mevcut sabit evren; sonuclar bit-bit ayni kalmali).
5. Testler: sentetik PIT CSV ile giris filtresi; varsayilan modda T1a paritesi.
PR: `[Codex-Sol] T14 point-in-time evren`.

## T15 — Motor: bekleyen emir (stop/limit giris) destegi — **Onerilen model: Sol** (cekirdek motor)
T14'ten sonra. 10 `tam` kart `ozel_kod_nedeni: bekleyen_emir` nedeniyle taranamiyor.
- Kart semasi: `giris_emri: {tip: stop|limit, seviye: "<ifade>", gecerlilik_bar: k}`; seviye sinyal barinda hesaplanir, sonraki k bar icinde fiyat seviyeye degerse dolum (stop: high >= seviye → max(open, seviye); limit: low <= seviye → min(open, seviye)). Ayni barda stop ve giris olursa kotumser kural (A3).
- `engine/portfolio.py` degisikligi geriye uyumlu; T1a ve tarama paritesi bit-bit ayni.
- 10 karti yeni alanla ifade et (`ozel_kod: false`), D8 anlamini EVRENSEL_KURALLAR'a yaz.
PR: `[Codex-Sol] T15 bekleyen emir`.
