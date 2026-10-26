# `calc_on_order_fills` bağlam denetimi

299 sonuçlanmış TV-2 Pine kaynağı tarandı. `calc_on_order_fills=false` ve
değişken ataması içeren, değeri kaynak satırından belirlenemeyen kullanımlar
aktif `true` sayılmadı.

| Sonuç | Açıkça `true` olan kimlikler |
|---|---|
| geçti | yok |
| izle | PIOU52P5, pcoISSiu |
| kaldı | 95cOZIj1, oMfpXSzp, txpk2ji5, xZufQuxX |
| zaman aşımı | ANBc7bkF, CYBNhBGG, Hen8I4To, ISy4P1JB, JeRCEqWU, gftlucA4 |
| desteklenmiyor | QzkRRL0T, XsQ38Pkh, t8Bp5gcx |

`calc_on_order_fills=true` geçmiş barda dolumdan sonra ek hesaplama
yaptırabileceğinden, TradingView bunu tarihsel sonuçlarda iyimserleştirebilir.
Bu nedenle açıkça `true` olan bir kaynak sonuçlansa bile yazar sonucu yalnız
bilgi sayılmalı; uygulanabilir sonuç kapanmış bar ve sonraki-açılış dolum
kurallarıyla karşılaştırılmalıdır. Mevcut TV-2 kararı veya maliyet varsayımı
değiştirilmedi.
