# Gun ici / dakikalik tarama ozeti (T12)

Donem: kripto IS 2020-01-01 -> 2024-09-30; BIST/ABD/emtia 1H (yfinance ~2 yil) ilk 2/3 IS, son 1/3 gorulmez. Maliyet 1x ve 2x (ELEME_KRITERLERI baz tablosu). Gun ici kartlarda kapanis dolumu istisnasi yok.
Gecis kurali: en az bir piyasada islem >= 30, 1x PF >= 1.1, 2x net > 0.

Kart: 3 | Reddedildi (asama 1): 3

## Karar tablosu

| Kart | Karar | Ayrinti |
|---|---|---|
| A3-010a | Reddedildi (asama 1) | KRIPTO25: PF_1x<1.1,net_2x<=0 |
| A3-010b | Reddedildi (asama 1) | KRIPTO25: PF_1x<1.1,net_2x<=0 |
| A3-010c | Reddedildi (asama 1) | KRIPTO25: PF_1x<1.1,net_2x<=0 |

## Atlanan / dogrulanamayan satirlar

| Neden | Satir sayisi |
|---|---:|
| dakikalik_veri_yok | 9 |

## Notlar

- Evren gunumuzun buyuk sirketleridir (survivorship yanliligi); BIST/ABD sonuclari en fazla Kosullu sayilir.
- BIST30 ve EMTIA icin endeks serisi yok: `endeks_close` kullanan kartlar bu piyasalarda Dogrulanamaz.
- Cikis alan anlamlari: docs/EVRENSEL_KURALLAR.md D5.
- 1H altindaki kartlar yalniz kriptoda (Binance) test edilir; diger piyasalar `dakikalik_veri_yok` (Dogrulanamaz).
- BIST 1H verisinde seans disi/sifir hacimli bar sorunu cozulmedigi icin BIST 1H satirlari `veri_kalitesi` (Dogrulanamaz).
- Gercek (OOS) sonuclar ve 2018-2019 kripto donemi bu taramada gorulmez.
