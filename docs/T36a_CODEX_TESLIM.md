# T36a Codex teslim notu

Tarih: 2026-10-23

## Yapılanlar

- `data/dukascopy.py` tamamlandı.
- BID/ASK bi5 LZMA dosyaları UTC 1 dakikalık orta fiyat ve spread olarak işleniyor.
- 429/5xx tekrar denemesi, istekler arasında 0,75 saniye bekleme ve yıllık Parquet checkpoint/resume eklendi.
- `tests/test_dukascopy.py` eklendi.
- `.github/workflows/dukascopy.yml` ile doğrudan erişim olmayan ortamlar için GitHub Actions fallback’i eklendi.
- `results/veri_kalitesi_dukascopy.md` kalite raporu oluşturuldu.

## Doğrulama

Tam test sonucu: **318 passed, 4 skipped**.

T36a testleri: **4 passed**.

## Sınırlamalar

Bu cloud runtime’da `datafeed.dukascopy.com` erişimi `CONNECT tunnel ... 403` ile engellendi; bu nedenle Parquet veri dosyaları henüz indirilemedi. Ortam yapılandırma taslağına alan adı erişimi ve kurulum/start talimatları kaydedildi; publish/reconnect sonrasında doğrudan indirme yeniden denenebilir. Alternatif olarak `.github/workflows/dukascopy.yml` çalıştırılmalıdır.

GitHub REST/GraphQL API de `403 Forbidden` verdi. Bu nedenle PR otomatik oluşturulamadı. Hazır branch:

`codex/t36a-dukascopy-1m`

PR oluşturma bağlantısı:

https://github.com/sselimgenc-oss/sg-arge/pull/new/codex/t36a-dukascopy-1m

Commit: `8b22501 [T36a] Dukascopy 1 dk veri`
