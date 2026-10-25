# Asama 2a: piyasa betasi testleri (T6a/T17)

BIST USD bazinda; rastgele giris (null) testi: PF ve ortalama R, null dagiliminin %95 yuzdeligini gecmeli.
Donem: gunluk ve kripto gun ici 2020-01-01 -> 2024-09-30; yfinance 1H arsivinin ilk 2/3'u (OOS ve on donem kullanilmadi).

Kart: 3 | T6b'ye gecen: 0 | elenen/dogrulanamaz: 3

## Satir sonuclari

| Kart | Piyasa | Para | Islem | PF | ortR | null PF p95 | null ortR p95 | p(PF) | p(ortR) | Tekrar | Karar |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| RD-01 | ABD25 | yerel | 1591 | 1.25 | 0.025 | 1.66 | 0.123 | 0.995 | 1.000 | 200 | Reddedildi (piyasa betasi): PF p=0.995, ortR p=1.000 (esik 0.05) |
| RD-02 | ABD25 | yerel | 373 | 1.34 | 0.060 | 1.81 | 0.246 | 0.826 | 1.000 | 200 | Reddedildi (piyasa betasi): PF p=0.826, ortR p=1.000 (esik 0.05) |
| RD-03 | ABD25 | yerel | 30 | 2.48 | 0.059 | 2.34 | 0.137 | 0.040 | 0.438 | 200 | Reddedildi (piyasa betasi): PF p=0.040, CAGR p=0.438 (esit 0.05) |

## Karar ozeti

- T6b'ye gecen kartlar: -
- Elenen kartlar (hicbir piyasada gecmedi): RD-01, RD-02, RD-03

## Notlar

- Null model: ayni cikis kurallari ve portfoy limitleri; sembol basina ayni giris sayisi (rastgele barlar), toplam islem sayisini kartinkine yaklastirmak icin giris sayisi pilot kosuyla olceklenir; `null_islem_ort` ve `tutma_*` kontrol icindir.
- Sinir bolgedeki satirlar (p 0,03-0,10) daha cok tekrarla yeniden kosulur.
- Rotasyon kartlari (T23, `metrik: PF+CAGR`): islem basina stop/R yok; null modelde takvim, N, maliyet ve yurutme kartinki, yalniz secim rastgele (kesitsel/sirali: rastgele siralama, filtre ve rejim kapisi ayni; gecis: ayni gecis tarihlerinde agacin enstrumanlarindan biri). PF ve CAGR null %95'inin ustunde olmali; `ort_r`, `null_ortr_*`, `p_ortr` sutunlari bu satirlarda CAGR tasir.
- Gun ici arsivleri `--veri-kok` altindan okunur; BIST 1H veri kalitesi duzelene kadar null testine alinmaz.
- BIST: USD fiyat = TL fiyat / ayni gun USDTRY kapanisi. TL sonucu `PF_1x_tl`, `net_1x_tl` sutunlarinda yalniz bilgi.
