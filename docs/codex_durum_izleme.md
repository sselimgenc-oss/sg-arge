# Codex durum — izleme

- Kapsam: yalnız İş A. İş B / Telegram başlatılmadı; anahtar ve emir yok.
- `main` güncellendi ve `codex/izleme` içine birleştirildi (`53b69ec`).
  `copytrade/kapi.delayed_copy` bağımlılığı artık mevcut.
- Liderin `copytrade/izleme_listesi.yaml` dosyası aynen kullanılıyor:
  iki test trader'ı, `izlemede`, t0 `2026-10-28`; kopyalama kararı değil.
- Komut: `source .venv/bin/activate` ardından `python -m copytrade.izleme_motoru --root . --output /tmp/izleme`.
  Actions çıktısı `copytrade-izleme` dalındaki `izleme/` dizinine gider; `main` içine canlı çıktı yazılmaz.
- Motor: kalıcı trader imleciyle artımlı dolumlar, ana/HIP-3 hesap pozisyonları, kalıcı olay kimlikleri ve son 200 olay.
  `perpDexs` listesindeki her benzersiz dex, `dex` parametresiyle ayrı sorgulanır; `xyz:CL` gibi coin adları korunur.
- Sanal defter: 1.000 USD, 30 dk, `delayed_copy` maliyeti ve funding; geçmiş yürütme mumları arşivlenir.
  Tam yürütme mumu yoksa ya da arşivsiz geçmiş 5.000 dakika dışındaysa koşu hata verir.
- Sağlık: mevcut blok bootstrap ve CUSUM yeniden kullanılır; kaldıraç brüt pozisyon / hesap değeridir.
- İş akışı: saatlik `23 * * * *`, elle tetikleme, yetim veri dalı ve üç rebase/push denemesi. `kararlar.jsonl` korunur.
- Önceki kabul: `python -m pytest -q` — **80 başarılı, 112 uyarı**; iki gerçek test trader'ı için canlı çıktı ve HIP-3
  pozisyonları doğrulandı. PR: https://github.com/sselimgenc-oss/sg-arge/pull/277.
- Ortam taslağı: `install_script` ve `start_skill` kaydedildi; canlı doğrulama yeni görevde yeniden yapılmalıdır.

## İzleme/Worker düzeltmeleri — 2026-10-28

Dal: `codex/izleme-duzeltme`. Başlangıç: `main` `452b70e`.

- [x] Emir bazlı sanal sonuç: kalan miktar, toplam maliyet ve gerçekleşen K/Z
- [x] Sağlık paydasını t0'da sabitle; `veri_zamani` ve `gecerli` yayımla
- [x] Worker Atladım → neden akışı ve yeniden basma
- [x] Başarısız Telegram gönderimini yeniden dene; yinelenen bildirimi engelle
- [x] Sorgulara bölünen `oid` için D1 biriktirme ve motorla aynı olay
- [x] Karar gizliliği: `bakiye_yok` dönüşümü, tarih, izinli `not`
- [x] Sözleşme v1.4 ve altın örnek kabul testleri
- [x] Tam Python ve Worker testleri; PR çıktı özeti — Python: 94 başarılı (153 uyarı), Worker: 9 başarılı. Canlı Telegram kabulü kullanıcıda bekliyor; bu PR dağıtım yapmaz.
