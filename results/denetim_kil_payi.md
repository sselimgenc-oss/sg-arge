# Kil payi denetimi

On kayit: `docs/DENETIM_KIL_PAYI.md`. Mevcut kararlar degismez.

## A. Risk testi (getiri/|MDD| vs rastgele giris; BH q=0.1)

- Test edilen satir: 151; ham p<0.05: 7; BH sonrasi kesif: 0

En dusuk p'li 20 satir:

| id | piyasa | tf | islem | getiri | MDD | oran | null p95 | p | BH |
|---|---|---|---|---|---|---|---|---|---|
| A3-009a | BIST30 | 1D | 149 | 0.227 | -0.055 | 4.10 | 3.05 | 0.010 | hayir |
| P3-002 | ABD25 | 1D | 369 | 0.262 | -0.043 | 6.08 | 4.68 | 0.012 | hayir |
| P3-008 | ABD25 | 1D | 888 | 0.230 | -0.043 | 5.37 | 4.83 | 0.028 | hayir |
| T8-02 | KRIPTO25 | 1D | 303 | 0.269 | -0.061 | 4.41 | 3.60 | 0.030 | hayir |
| O3-003 | EMTIA | 1D | 143 | 0.036 | -0.019 | 1.95 | 1.74 | 0.037 | hayir |
| O1-039 | BIST30 | 1D | 125 | 0.383 | -0.076 | 5.07 | 4.93 | 0.045 | hayir |
| C01 | KRIPTO25 | 1D | 231 | 0.333 | -0.083 | 4.01 | 3.99 | 0.050 | hayir |
| R01 | KRIPTO25 | 1D | 221 | 0.743 | -0.137 | 5.43 | 6.01 | 0.071 | hayir |
| O1-039 | KRIPTO25 | 1D | 157 | 0.382 | -0.070 | 5.44 | 6.01 | 0.081 | hayir |
| C02 | EMTIA | 1D | 103 | 0.142 | -0.037 | 3.87 | 4.52 | 0.087 | hayir |
| P3-001 | KRIPTO25 | 1D | 109 | 0.917 | -0.166 | 5.53 | 6.08 | 0.091 | hayir |
| A3-007 | KRIPTO25 | 1D | 281 | 0.590 | -0.098 | 6.04 | 6.73 | 0.094 | hayir |
| M036 | KRIPTO25 | 1D | 429 | 0.090 | -0.037 | 2.43 | 3.12 | 0.095 | hayir |
| T8-05 | KRIPTO25 | 1D | 271 | 0.460 | -0.080 | 5.78 | 6.72 | 0.104 | hayir |
| A2-002 | EMTIA | 1H | 436 | 0.205 | -0.064 | 3.20 | 3.72 | 0.104 | hayir |
| M015 | EMTIA | 1D | 47 | 0.019 | -0.012 | 1.57 | 2.81 | 0.109 | hayir |
| B3-010 | EMTIA | 1D | 169 | 0.039 | -0.019 | 2.09 | 2.77 | 0.114 | hayir |
| P3-002 | KRIPTO25 | 1D | 588 | 0.395 | -0.108 | 3.66 | 4.58 | 0.114 | hayir |
| O1-003 | EMTIA | 1H | 439 | 0.265 | -0.097 | 2.73 | 3.66 | 0.117 | hayir |
| R05 | KRIPTO25 | 1D | 581 | 0.627 | -0.152 | 4.11 | 5.07 | 0.124 | hayir |

## B. OOS gucu (Welch tek yonlu, alfa=0.05)

| id | piyasa | IS islem | IS ortR | OOS islem | OOS ortR | OOS %95 aralik | p | karar |
|---|---|---|---|---|---|---|---|---|
| P3-011 | KRIPTO25 | 404.0 | 0.317 | 169.0 | -0.112 | [-0.278, 0.076] | 0.000 | Reddedildi (OOS IS'ten anlamli kotu) |
| P3-008 | KRIPTO25 | 740.0 | 0.127 | 361.0 | -0.019 | [-0.091, 0.060] | 0.004 | Reddedildi (OOS IS'ten anlamli kotu) |

## Lider notu
- **Şans beklentisi:** 147 geçerli testte p<0.05 olan satır sayısı 7. Hiçbir gerçek kenar olmasa bile şansla beklenen sayı 147 × 0.05 ≈ 7.4. Yani dağılım tamamen şansla uyumlu. Benjamini–Hochberg sonrası keşif yok.
- **Test edilemeyen 4 satır (A4-003, A4-005, A6-004 KRIPTO, B3-014):** Bunlar rotasyon kartı; rastgele giriş modelleri farklı olduğu için bu betikte koşmadı. Dördünün de IS MDD'si %41–55. %15 sınırının çok üstünde olduklarından Aşama 2b'de elenirlerdi; karar değişmez.
- **B bölümü:** P3-011 ve P3-008 (kripto) OOS'ta IS'ten anlamlı ölçüde kötü. "Kısa pencere şansı" değil, gerçek bozulma.
- **Sonuç:** Denetim, mevcut elemenin iyi bir stratejiyi kaçırdığına dair kanıt bulmadı. `SONUC.*` değişmez.
