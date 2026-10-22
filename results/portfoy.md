# Portfoy analizi: Gecti + Kosullu adaylar (T18)

Kaynak: `results/asama2b.csv + asama2b_pit.csv` (evren: pit) | Adaylar (3): A6-010:EMTIA, C07:ABD25, R01:ABD25

> **Secim yanliligi uyarisi:** adaylar IS sonuclarina bakilarak secildi. Asil kanit **OOS** bloktur (2024-10-01 sonrasi, secime girmedi); IS rakamlari yalniz baglam icindir. Agirlik optimizasyonu yapilmadi: her aday 1/N.

## Birlesik portfoy (esit risk, 1/N sermaye)

| Donem | Gun | Getiri | CAGR | PF (gunluk) | MDD | Bootstrap MDD %95 | Bootstrap CAGR p05 | MDD kapisi (<=%15) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **OOS** | 516 | 7.5% | 3.6% | 1.20 | 2.9% | 4.7% | 0.4% | gecti |
| **IS** | 1193 | 21.1% | 4.1% | 1.24 | 4.6% | 6.7% | 1.3% | gecti |

Portfoy genelinde IS'te en yuksek acik baslangic riski (islemlerin `initial_risk` toplami / ozkaynak): **2.16%**. Her kitap motorun %2 toplam risk tavaniyla calisir; 1/N agirlikla portfoy riski kitaplarin ortalamasidir, dolayisiyla tek kitabin tavanini asamaz.

## Adaylar ayri ayri

| Aday | OOS getiri | OOS MDD | IS getiri | IS MDD |
|---|---:|---:|---:|---:|
| A6-010:EMTIA | 7.9% | 4.2% | 12.4% | 6.3% |
| C07:ABD25 | 13.0% | 3.8% | 30.6% | 4.7% |
| R01:ABD25 | 1.6% | 4.4% | 20.0% | 9.2% |

## Korelasyon (gunluk getiri; piyasa kapali gun = 0)

| Donem | Tum gunler ort. cift korelasyonu | Stres gunleri (piyasanin en kotu %5'i) |
|---|---:|---:|
| OOS | 0.20 | 0.22 (n=26 gun) |
| IS | 0.24 | 0.27 (n=60 gun) |

Tam matrisler: `results/portfoy_korelasyon.csv`.

## Yontem notlari

- Getiri serileri `tarama.prepare(...).run()` / `asama2b.prepare_codex(...).run()` ile uretilir; BIST USD bazinda. Her kitap bagimsiz sermaye ile calisir; portfoy getirisi gunluk getirilerin ortalamasidir (gunluk yeniden dengeleme).
- Takvimler farkli piyasalardan gelir: birlesik tarih ekseni, bir piyasanin kapali gunu 0 getiri sayilir. Bu, korelasyonlari asagi ceker.
- Stres gunleri: aday piyasalarindaki tum sembollerin esit agirlikli gunluk getirisinin (BIST USD) piyasalar arasi ortalamasinin en kotu %5'lik gunleri. BIST/emtia icin tek bir endeks serisi yok.
- Bootstrap: 20 gunluk dairesel block, `asama2b.block_bootstrap`. OOS ornegi kisadir; OOS bootstrap'i gevsek okunmalidir.
- PF gunluk getirilerden hesaplanir (islem bazli PF degil).
- Acik risk islem listesinden turetilir; veri sonunda acik kalan pozisyonlar listede yoktur ve gunluk ozkaynak degisimi orani oynatir (tavan giris aninda motorda uygulanir).
