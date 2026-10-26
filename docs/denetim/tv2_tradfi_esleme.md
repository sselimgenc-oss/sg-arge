# TV-2 TradFi perp eşleme denetimi

Denetim tarihi: 2026-10-26. Bu kayıt karar kapısını değiştirmez; yalnız veri
kaynağı/eşdeğerlik denetimidir.

| TV-2 kimliği | Yayın sembolü | Denetim sonucu | İşlem |
|---|---|---|---|
| `jLKPS0lF` | `BYBIT:NVDAXUSDT` | `NVDAXUSDT` Pionex xStock adıdır. Binance USD-M'deki `NVDAUSDT` başka sözleşmedir; önceki genel USDT fallback'i Binance'te bulunmayan `NVDAXUSDT`yi sorguluyordu. | Satır `veri_yok` kaldı; neden `sembol eşlemesi yanlış` olarak düzeltildi. `NVDAUSDT` ile yeniden koşu yapılmadı. |
| `83hmaEOQ` | `OKX:XAUUSDT.P` | Kaynak borsa OKX; Binance'e eşdeğer sayılmadı. | Mevcut `veri_yok` korunur. |
| `cXpZ682G`, `7T0JUDc6`, `ip7Wyl0i`, `fN6SvWLZ` | `BINANCE:XAUUSDT.P` | Sembol Binance USD-M kaynağında ayrıca denendi; satırlar veri gelmediğini kaydediyor. Bu, başka sözleşmeye ad değiştirme gerekçesi değildir. | Mevcut `veri_yok` korunur. |
| `ununtjrx`, `Z8eVxEaX` | `PIONEX:XAGUSDT.P` | Pionex sözleşmesi Binance eşdeğeri değildir. | Mevcut `veri_yok` korunur. |

`NVDAUSDT` ancak yayınlanan sembolün gerçekten o sözleşme olduğuna dair kaynak
kanıtı gelirse ayrı bir eşleme olarak eklenip yeniden koşturulur; bu denetim
öyle bir ikame yapmaz.
