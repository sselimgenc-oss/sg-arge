# Argon paketi T35: Afrika + Güney Amerika strateji toplama (ilk parti)

Merhaba Argon. Beyin fırtınasındaki önerilerin kabul edildi. Şimdi ilk deneme partisini topluyoruz.
**Ekran görüntüsü alma. Yalnız metin ve kod oku.**

## Amaç
Yazarının **rakamla** kârlı olduğunu iddia ettiği trading stratejilerini, yazarın kendi piyasasıyla birlikte kaydetmek. Backtest yapma; yalnız bul ve kaydet.

## Hedef
**8-12 kayıt.** Sayıyı doldurmak için zayıf kayıt ekleme. 6 iyi kayıt, 12 zayıf kayıttan iyidir. Mümkünse scalp, day ve swing karışık olsun.

## Kaynaklar (senin listen)
QuantBrasil, B3 odaklı GitHub depoları (Portekizce), ADVFN Brasil Forum, Rankia (İspanya/LatAm), Rava Foros (Arjantin), ArabicTrader Forum, MyBroadband forum. Başka güçlü kaynak bulursan ekleyebilirsin.
**Kullanma:** Nairaland, Kenya grupları, Moneyweb, investing.com forumları. Faz 1'de taranan TradingView, ProRealCode, MQL5, ForexFactory, QuantifiedStrategies, NinjaTrader, Collective2, Elite Trader, QuantConnect, Matriks da kullanılmaz.

## Kayıt kapısı: kayıt yalnız şu durumda girer
1. En az bir performans rakamı (PF, kazanma oranı, getiri, Sharpe, max düşüş) **ve** test dönemi yazılı. İşlem sayısı yoksa kayıt yine girer, kırmızı bayrağa `islem_sayisi_yok` yazılır.
2. Strateji açıklanmış: en az bir paragraf ya da kod. Kurs, sinyal ya da bot satışı reklamı girmez.

Giriş gerektiren ya da ücretli kaynak atılmaz, işaretlenir. Kırmızı bayraklar da atılmaz, işaretlenir: `islem_sayisi_yok`, `az_islem(<30)`, `pf_gt_4`, `maliyet_yok`, `kisa_donem(<1yil)`, `yalniz_ekran_goruntusu`.

## Kurallar
- **Uydurma yok.** Kaynakta yazmayan alanı boş bırak. Rakamları yazarın verdiği gibi yaz.
- Aynı strateji farklı piyasada ya da parametreyle ayrı sonuç vermişse ayrı satır aç: `SA-003a`, `SA-003b`.
- Giriş/çıkış kuralını orijinal dilde kısa alıntıyla da ver (`orijinal_alinti`).

## Çıktı biçimi
Markdown tablo **ya da** CSV. Sütunlar şunlar; uymayanı boş bırak:

`id | ad | ad_orijinal | tur | ulke | dil | platform | url | yazar | yayin_tarihi | piyasa | enstruman | veri_kodu | zaman_dilimi | ozet | giris | cikis | stop | orijinal_alinti | kod_dili | kod_link | kural_tam | iddia_donem | iddia_islem | iddia_wr | iddia_pf | iddia_getiri | iddia_mdd | iddia_sharpe | iddia_turu | maliyet_dahil | referans_turu | dogrulama | kanit_notu | erisim | kirmizi_bayrak | not`

Değer listeleri:
- `id`: Güney Amerika `SA-001`..., Afrika `AF-001`...
- `tur`: scalp (1 saatin altı) / day / swing / belirsiz
- `kural_tam`: evet / kismen / hayir
- `iddia_turu`: backtest / canli / forward / karisik
- `maliyet_dahil`: evet / hayir / belirtilmemis
- `referans_turu`: forum / blog / kod_deposu / platform_raporu / canli_hesap / makale
- `dogrulama`: platform_dogrulamali / yazar_beyani
- `erisim`: acik / giris_gerekli / ucretli
- `veri_kodu`: biliyorsan B3 için `WIN$`, `PETR4.SA`, JSE için `NPN.JO` gibi.

Tablonun altına kısa bir not ekle:
- açamadığın siteler;
- kapıdan dönen yaklaşık kayıt sayısı ve en sık dönme nedeni.
