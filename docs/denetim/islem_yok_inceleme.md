# TV-2 `islem_yok` kaynak denetimi (E5)

2026-10-26. `results/tv2/sonuclar.csv` içindeki 11 satır, kaynak metni ve
tam geçmişte yazar/uygulanabilir işlem sayıları birlikte incelendi. Her
satırda her iki sayacın da sıfır olması, yorumlayıcının yalnız maliyet
uygularken işlem kaybetmediğini gösterir.

| ID | Yazarın sembolü / tf | Kaynak bulgusu | Sonuç |
|---|---|---|---|
| 2lGyzYkC | BTCUSDT / 60 | `input.source` ile dış gösterge sinyali bekliyor | Gerçek sinyal yok: varsayılan `close` ±1 üretmez |
| CFOy39oC | BTCUSDT / 1 | `input.source` ile dış gösterge sinyali bekliyor | Gerçek sinyal yok: dış gösterge bağlanmadan test edilemez |
| XIJrNXQc | BTCUSDT / 60 | `input.source` ile dış gösterge sinyali bekliyor | Gerçek sinyal yok: dış gösterge bağlanmadan test edilemez |
| brMq1l1s | BTCUSDT / 30 | `input.source` ile dış gösterge sinyali bekliyor | Gerçek sinyal yok: dış gösterge bağlanmadan test edilemez |
| 6MsOzaoy | BTCUSDT / 60 | 2 `strategy.entry`, kaynak içi koşullar | Bu sürüm çok yeni; gözlenen geçmişte sinyal yok |
| 7VqlwJsL | BTCUSD / 1 | 2 `strategy.entry`, kaynak içi koşullar | Test penceresinde sinyal yok |
| 8N8DT3Pv | HYPEUSDT.P / 15 | 1 `strategy.entry`, kaynak içi koşul | Kısa enstrüman geçmişinde sinyal yok |
| Bz7isFiX | BTCUSD / 60 | 2 `strategy.entry`, kaynak içi koşullar | Test penceresinde sinyal yok |
| IvMdQJNW | XMRUSDT.P / 15 | 1 `strategy.entry`, kaynak içi koşul | Bu sürüm çok yeni; gözlenen geçmişte sinyal yok |
| KHBR2H0R | BTCUSD / 480 | 8 `strategy.entry`, kaynak içi koşullar | Bu sürüm çok yeni; gözlenen geçmişte sinyal yok |
| sxo2gPSm | BTCUSDT.P / 15 | 2 `strategy.entry`, kaynak içi koşullar | Bu sürüm çok yeni; gözlenen geçmişte sinyal yok |

## Sonuç

Yorumlayıcı hatasını işaretleyen `PineHatasi`/`Desteklenmiyor` sonucu veya
işlem sayacı uyuşmazlığı görülmedi. Dört dış-gösterge şablonu ancak yazarın
bağladığı kaynak seriyle yeniden üretilebilir; kalan yedi satır için kaynak
emir içeriyor fakat mevcut tarih/veri penceresinde tetik yok. Bu turda kod ya
da karar kapısı değiştirilmedi.
