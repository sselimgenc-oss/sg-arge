# `lookahead_on` bağlam denetimi

Kaynak: `results/tv2/lookahead_listesi.csv` ve Pine Facade’dan okunan dokuz
kaynak. Bu belge karar etiketi değiştirmez; canlı/sanal aday incelemesinde
kullanılacak risk işaretidir.

| Kimlik | Kaynak bağlamı | Sınıf | Mevcut sonuç |
|---|---|---|---|
| zwR6q7AL | Günlük pivot için `close/high/low[1]`; kaynak bunu “previous day values” diye adlandırıyor. | önceki HTF barı, düşük risk | izle |
| TgXEkOq4 | H1/H4 önceki mumun açık/kapanışı (`[1]`). | önceki HTF barı, düşük risk | izle |
| 6ve1ax1D | Günlük pivot bileşenleri `[high[1], low[1], close[1], ...]`; diğer security çağrıları `lookahead_off`. | önceki HTF barı, düşük risk | veri ücretli |
| u4g3IrXS | Giriş/çıkış RSI’si `[1]` ile HTF’den alınıyor. | önceki HTF barı, düşük risk | veri yok |
| fqS79J4w | HTF destek/direnç `high[1]`, `low[1]`. | önceki HTF barı, düşük risk | veri yok |
| asmZOvXE | Pivot hesaplaması önceki HTF yüksek/düşük/kapanıştan. | önceki HTF barı, düşük risk | izle |
| w45uet8E | HTF iki hareketli ortalama geri kaydırmasız; doğrudan `macro_bull_raw`a akıyor. | ileri bakma riski, kaynak incelemesi zorunlu | izle |
| XsQ38Pkh | Çoklu `security(..., src, lookahead_on)` geri kaydırmasız; günlük `open` da aynı biçimde kullanılıyor. | ileri bakma riski, kaynak incelemesi zorunlu | desteklenmiyor |
| 0VIgV9kM | Varsayılanı `true` olan `lookaheadMTF`, geri kaydırmasız `f_count()` sonucunu sinyal hesabına alıyor. | ileri bakma riski, kaynak incelemesi zorunlu | zaman aşımı |

## Sonuç

`[1]` kalıbı önceki tamamlanmış yüksek zaman dilimi barını hedeflediği için
tek başına gelecek sızıntısı kanıtı değildir. `w45uet8E`, `XsQ38Pkh` ve
`0VIgV9kM` ise geri kaydırmasız olduklarından ayrı kaynak/sonuç karşılaştırması
olmadan sanal ya da canlı aday seçimine girmemelidir. Bu belge yeni eleme
kuralı oluşturmaz.
