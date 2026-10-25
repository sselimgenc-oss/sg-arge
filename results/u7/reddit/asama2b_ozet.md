# Asama 2b tam dogrulama (T6b/T24)

OOS, on donem, 2x/3x/+1 bar stres, kaynak merkezli parametre platosu, 20 gunluk block bootstrap ve DSR birlikte raporlanir.
DSR paper trading icin bilgi; canliya geciste kotumser (5N) deger icin 0,95 kapisi uygulanir.

Satir: 0 | 

| ID | Piyasa | OOS islem/ortR | 2x PF | 3x net | +1 net | Plato + | Boot MDD95 | DSR 5N | Karar | Gerekce |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|

## Yontem notlari

- Rotasyon kartlari (T23, `metrik: PF+CAGR`): ortR yerine CAGR; `oos_ort_r`/`on_ort_r` sutunlari donem CAGR'i tasir. Asama 2'de dolum ertesi acilistir (Composer kartlarinin kapanis dolumu yalniz Asama 1 bilgisidir). Plato: `rotasyon:` blogu ve kullandigi gostergelerin her sayisal parametresi (pencere, esik, N) tek tek +-%20; hucre = PF>1 ve getiri>0. `evren: enstruman` = adli ETF'ler (survivorship notu yok).
- BIST fiyatlari USDTRY ile ayni gun USD'ye cevrilir.
- Plato merkezleri kaynak sinyal degerleridir; en iyi hucre secilmez ve stratejiye geri yazilmaz.
- DSR N = kaynak denemesi (yoksa 1) + tarama.csv satirlari + 21 Codex satiri.
- Gun ici platoda her sayisal parametre merkez etrafinda tek tek -%20/+%20 denenir; stres ve plato `--isci` ile paraleldir.
- Gun ici bootstrap/DSR oncesinde ozkaynak UTC gun sonu degerlerine indirgenir; block uzunlugu 20 gundur. Gun ici DSR N tum gun ici kart-piyasa-tf tarama satirlarini kapsar.
- DSR'da denemeler arasi SR varyansi bilinmedigi icin stratejinin kendi SR standart hatasi kullanildi (yaklasim).
- BIST/ABD guncel evrenleri survivorship yanliligi nedeniyle en fazla `Kosullu` olabilir; `--evren pit` (T11) ile ABD tam, BIST 2020 sonrasi duzeltilir.
