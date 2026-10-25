# Oturum A durumu

Tarih: 2026-10-25 (Europe/Istanbul)
Dal: `codex/kripto-disi`

- 4.1 TAMAMLANDI — Dukascopy yükleyicisi FX, XAU/XAG ve endeks CFD sembol ölçekleriyle birleştirildi; sahte indirme testleri geçti (19 test).
- 4.2 TAKILDI: `vnstock` paketi ortamda yok (`ModuleNotFoundError`); vnstock dalı çalıştırılmadı.
- 4.3 TAMAMLANDI — `arastirma/tv2_veri_eslesme.csv` oluşturuldu: 636 kripto-dışı strateji; Dukascopy 214, yfinance 422.
- 4.4 TAMAMLANDI — `results/tv2/kuyruk_kripto_disi.txt` oluşturuldu; sürüm tarihi 2026 öncesi 72 öğe önce sıralandı, toplam 636 öğe.
- 4.5 HAZIR, KOŞU KULLANICIDAN BEKLENİYOR — `codex/tv2-kosu` birleştirildi; `.github/workflows/tv2.yml` içindeki `kuyruk` girdisi varsayılan olarak `results/tv2/kuyruk_kripto_disi.txt` seçiyor. Kullanıcı workflow’u başlatabilir.

Son doğrulama: `./.venv/bin/python -m pytest -q tests/` → 1328 geçti, 4 atlandı.

## Ek iş havuzu

- E3 TAMAMLANDI — 31 `veri_yok` satırı için OKX ikinci kaynak fallback’i eklendi ve Bybit/OKX sorguları denendi. Bybit çalışma bölgesinden HTTP 403 ile engelli; OKX’te bu 31 sembol için kullanılabilir veri bulunamadı; yeniden koşulacak satır çıkmadı.
- E5 TAMAMLANDI — 11 `islem_yok` satırı kaynak okumasıyla sınıflandırıldı: brMq1l1s, CFOy39oC, 2lGyzYkC ve XIJrNXQc harici `input.source` bağlayıcısı bekliyor; KHBR2H0R, IvMdQJNW, 8N8DT3Pv, sxo2gPSm, Bz7isFiX, 7VqlwJsL ve 6MsOzaoy kaynakta/koşuda sinyal üretmedi.
- E4 TAMAMLANDI — 12 desteklenmiyor satırı gruplandı: 9 `request.security` dış sembol verisi yok, 2 çizim nesnesi `get_y1/get_top`, 1 footprint verisi yok. İlk grup veri erişimi, ikinci grup yorumlayıcı semantiği, üçüncü grup ücretli veri kapsamı olduğundan karar değiştiren varsayımsal uygulama yapılmadı.
- E8 TAKILDI — Resmî TradingView belgesi `ticker.renko()`nun yalnız bir sentetik ticker kimliği ürettiğini, bunun `request.security()` ile okunacağını ve örnekte ATR parametresini açıklar; Renko barlarının düşük zaman dilimi fiyatından yalnız yaklaşık üretildiğini de belirtir. Traditional/ATR tuğla oluşumu, kapanış tabanı, ters-dönüş eşiği ve zaman eşleme algoritması tanımlanmadığından sadık bir yorumlayıcı uygulanmadı. Kaynak: https://www.tradingview.com/pine-script-docs/concepts/non-standard-charts-data/
- Koşu izleme (2026-10-25) — GitHub Actions API’sinde `codex/kripto-disi` üzerinde TV-2 run görünmüyor. Görünen tek etkin TV-2 run `40213846730`, `codex/tv2-kosu` dalında; bu nedenle kripto-dışı sonuç/artifact kurtarma işlemi güvenle başlatılamadı.
- Çizim nesneleri — `line.get_y1` ve `box.get_top` için mevcut yorumlayıcı erişicileri, koordinat güncellemesi ve `na` kimliği testi `tests/test_pine_yorumlayici.py::test_drawing_coordinates_can_be_read_back` ile doğrulandı (41/41 Pine testi). Yeniden koşuda `UUHabgvo` `gecti`; `hlOgflm1` artık `get_top` değil, sonraki bağımsız eksik `wave1_0_500` liste özniteliğinde `desteklenmiyor`.

## Gece planı

- 01:44 — A1 — `40226355510` run’ının 0–6 artifact’ları doğrulandı (8/8 job başarılı). Kurtarma betiği varsayılan kripto kuyruğunu kullandığı için kripto-dışı satırları sahiplenmiyordu; `tv2.yml` artık seçilen `kuyruk` girdisini `--queue` ile kurtarıcıya geçiriyor. İlgili testler: 16 geçti.
- 01:44 — A1 TAKILDI: Artifact ZIP indirmesi GitHub’ın yönlendirdiği Actions blob adresinde ortam proxy’sinden HTTP 403 alıyor; `gh run download` ise bu ortamda yetkili değil. 0–6 satırları indirilemedi; erişim sağlanınca `scripts/tv2_artifact_kurtar.py <artifact> --part N --queue results/tv2/kuyruk_kripto_disi.txt` ile kurtarılacak.
- 01:44 — A2 — Kapsam raporu `docs/denetim/kripto_disi_kapsam.md` yazıldı: 636 kuyruktan 80 satır dalda, 556 artifact/checkpoint kaybı nedeniyle yok.
- 01:44 — A3 — `results/tv2/kuyruk_kripto_disi_kalan.txt` oluşturuldu (556 kimlik). KOSU_ISTEGI: `codex/kripto-disi`, `results/tv2/kuyruk_kripto_disi_kalan.txt`, parça `0-7`; B bu kuyruğu matriste başlatmalı.
- 01:44 — A5 — Dış sembol eşlemesi: `CME:BTC1!` yfinance `BTC=F` ile yeniden koşuldu (`cFY26Qg8`: kaldı); `DXY` yfinance ile çözüldü ancak iki stratejide sonraki eksik sembol `XAUAUD` çıktı. Öneksiz `BTCUSD` artık Binance `BTCUSDT` eşdeğerine yönleniyor (testli); `XsQ38Pkh` için 1 dakikalık yeniden koşu gerekir. `CRYPTOCAP:USDT.D`, `CRYPTOCAP:TOTAL`, `GLASSNODE:BTC_MARKETCAP` ve `BTCUSDT.P.P_OI` mevcut üç kaynağın OHLCV verisiyle eşlenemez; `XAUAUD` için de Dukascopy çaprazının iki arşivi henüz yok. KOSU_ISTEGI: `codex/kripto-disi`, tekil `XsQ38Pkh`, `--dakikalik`, uzun süre sınırı.
- 01:44 — A6 — Yfinance’ın 1-30 dakikalık 7/60 günlük penceresiyle gelen sonuçlara yalnız bilgi sütunu `veri_kisa=true` ekleniyor; kapı, eşik ve karar kodu değişmedi. Testler: 18 geçti.
