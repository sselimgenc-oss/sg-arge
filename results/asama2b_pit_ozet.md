# Asama 2b tam dogrulama (T6b)

OOS, on donem, 2x/3x/+1 bar stres, kaynak merkezli parametre platosu, 20 gunluk block bootstrap ve DSR birlikte raporlanir.
DSR paper trading icin bilgi; canliya geciste kotumser (5N) deger icin 0,95 kapisi uygulanir.

Satir: 6 | Gecti: 2 | Reddedildi: 4

| ID | Piyasa | OOS islem/ortR | 2x PF | 3x net | +1 net | Plato + | Boot MDD95 | DSR 5N | Karar | Gerekce |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| C04 | BIST30 | 25/-0.148 | 2.42 | 11.4% | 14.0% | 96% | 5.9% | 0.144 | Reddedildi | null |
| C07 | ABD25 | 102/0.237 | 2.05 | 27.1% | 26.2% | 100% | 10.1% | 0.186 | Gecti | paper kapilari gecti; DSR canli oncesi degerlendirilmeli |
| R01 | ABD25 | 114/0.128 | 1.32 | 11.4% | 13.5% | 100% | 13.8% | 0.033 | Gecti | paper kapilari gecti; DSR canli oncesi degerlendirilmeli |
| G011 | ABD25 | 215/-0.052 | 1.50 | 14.3% | 20.2% | 84% | 8.6% | 0.106 | Reddedildi | OOS ortR<=0 |
| M015 | ABD25 | 130/0.060 | 1.19 | 1.3% | 5.5% | 100% | 6.0% | 0.011 | Reddedildi | 2x PF<1.2 |
| M038 | ABD25 | 627/0.075 | 1.16 | 5.1% | 21.7% | 100% | 13.9% | 0.110 | Reddedildi | 2x PF<1.2 |

## Yontem notlari

- BIST fiyatlari USDTRY ile ayni gun USD'ye cevrilir.
- Plato merkezleri kaynak sinyal degerleridir; en iyi hucre secilmez ve stratejiye geri yazilmaz.
- DSR N = kaynak denemesi (yoksa 1) + tarama.csv satirlari + 21 Codex satiri.
- DSR'da denemeler arasi SR varyansi bilinmedigi icin stratejinin kendi SR standart hatasi kullanildi (yaklasim).
- BIST/ABD guncel evrenleri survivorship yanliligi nedeniyle en fazla `Kosullu` olabilir; `--evren pit` (T11) ile ABD tam, BIST 2020 sonrasi duzeltilir.
