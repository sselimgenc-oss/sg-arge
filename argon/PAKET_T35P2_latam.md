# Argon paketi T35 parti 2: Güney Amerika + Afrika (ikinci parti)

Merhaba Argon. İlk partin kabul edildi. Kullanıcı iki kaydını (Gap Trap WDO, JSE pairs) kaynağında kontrol etti, rakamlar birebir tuttu. Teşekkürler. QuantBrasil en verimli kaynak çıktı.
**Ekran görüntüsü alma. Yalnız metin ve kod oku.**

## Amaç (değişmedi)
Yazarının **rakamla** kârlı olduğunu iddia ettiği stratejileri, yazarın kendi piyasasıyla kaydetmek. Backtest yok.

## Hedef: 15 kayıt
1. **QuantBrasil'de devam: 8-10 kayıt.** İlk partide aldıkların:
   - Saudade de Casa
   - IFR2 + SMA50
   - Estocástico Lento
   - Máximas e Mínimas
   - Candle Pavio
   - Gap Trap

   Bunları **tekrar alma**. Özellikle WIN/WDO vadeli gün içi (scalp/day) yazılarını öncelikle.
2. **Yeni ülkeler: 5-7 kayıt.**
   - Meksika (BMV, IPC)
   - Kolombiya (BVC)
   - Şili (IPSA)
   - Peru
   - Afrika: Mısır EGX30, Nijerya NGX, Kenya NSE. Yalnız rakamlı ve kurallı kaynaklar.

## Kayıt kapısı (değişmedi)
1. En az bir performans rakamı (PF, kazanma oranı, getiri, Sharpe, max düşüş) **ve** test dönemi yazılı.
2. Strateji açıklanmış ya da kodu var. Kurs, sinyal ya da bot satışı girmez.

## Yeni kurallar
- **Connors RSI2 / IFR2 ailesinden** yeni kayıt alma. Bu aile bizde zaten var.
- **`iddia_pf` yalnız profit factor.** Ortalama kazanç/kayıp, beklenen değer gibi başka metrikleri `not` alanına birimiyle yaz.
- **Al-tut kıyası:** Yazar al-tut ya da endeks getirisini veriyorsa `not`'a yaz. Strateji al-tutun altındaysa `kirmizi_bayrak`'a `al_tut_altinda` ekle.
- Uydurma yok. Kaynakta olmayan alanı boş bırak.

## Çıktı biçimi
İlk partiyle aynı: sekmeyle ayrılmış tablo ya da CSV, aynı sütunlar:

`id | ad | ad_orijinal | tur | ulke | dil | platform | url | yazar | yayin_tarihi | piyasa | enstruman | veri_kodu | zaman_dilimi | ozet | giris | cikis | stop | orijinal_alinti | kod_dili | kod_link | kural_tam | iddia_donem | iddia_islem | iddia_wr | iddia_pf | iddia_getiri | iddia_mdd | iddia_sharpe | iddia_turu | maliyet_dahil | referans_turu | dogrulama | kanit_notu | erisim | kirmizi_bayrak | not`

- `id` numaraları kaldığın yerden devam etsin: `SA-008`..., `AF-002`...
- Tablonun altına kısa bir not ekle:
  - açılamayan siteler;
  - kapıdan dönen yaklaşık kayıt sayısı ve en sık dönme nedeni.
