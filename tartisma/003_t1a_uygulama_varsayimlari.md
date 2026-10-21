# T1a uygulama varsayımları

PDF sinyal kurallarını açık biçimde veriyor; aşağıdaki iki ayrıntıyı tanımlamıyor. Replikasyon farklarının izlenebilmesi için kodda `# VARSAYIM:` ile işaretlendiler.

1. **Haftalık mum sınırı:** BIST/ABD/emtia ETF için cuma kapanışı (`W-FRI`), Binance spot için pazar UTC kapanışı (`W-SUN`) kullanılır. Haftalık rejim ancak bu kapanıştan sonraki günlük hesaplarda kullanılabilir.
2. **CCI negatif bakış penceresi:** “CCI20 son 10 gün içinde negatif bölgeyi gördükten sonra +100 seviyesini yukarı keserse” ifadesi, kesişim barından önceki 10 tamamlanmış günlük bar olarak uygulanır.
3. **ATR takip stopu:** Başlangıç stopu giriş fiyatı eksi sinyal barındaki `ATR14×3`; takip stopu her kapanıştan sonra `max(eski stop, kapanış − ATR14×3)` olur ve ancak sonraki barda etkinleşir. PDF “ATR14×3 başlangıç/takip stopu” der fakat takip referans fiyatını ayrıca belirtmez.

Bu varsayımlar strateji iyileştirmesi değildir. Lider farklı tanım verirse aynı dalda değiştirilip replikasyon yeniden çalıştırılmalıdır.
