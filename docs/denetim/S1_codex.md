# S1 denetimi — TV-2 ilk beş geçen strateji

Denetim tarihi: 2026-10-25

## Kapsam ve yöntem

İlk beş `gecti` satırı, `results/tv2/satirlar/*.json` içindeki sonuç sırasından
alındı: `3UcIwSrE`, `627VbHkS`, `GjZOz8Pu`, `KUyDNRyQ`, `QPIGo8hs`.
Her birinin açık Pine kaynağı, `arastirma/tv2_surumler.csv` içindeki PUB
kimliği kullanılarak TradingView Pine facade `last` kaynağından okundu. Motor
karşılaştırması `backtests/tv2.py` içindeki `PineStrateji` akışı ve
`engine/pine/yorumlayici.py` içindeki emir/security/ayar çağrılarına göre
yapıldı. Sonuçlardaki kararlar değiştirilmedi.

## Karşılaştırma

| ID | Pine kaynağındaki giriş/çıkış | Boyut ve maliyet | `security` | Yorumlayıcı karşılaştırması |
|---|---|---|---|---|
| `3UcIwSrE` | Pivot high/low teyidinden sonra, `rsi[rightBars]` filtresiyle sırasıyla `stop=hprice+mintick` long veya `stop=lprice-mintick` short (`strategy.entry`, kaynak satırları 16–48). Kaynakta `close/exit` yok; pozisyon ters sinyal veya emülatör sonuna kadar açık kalabilir. | `strategy()` içinde özel boyut, komisyon veya kayma yok; v4 varsayılanı kullanılır. Girişte miktar belirtilmediği için motor varsayılan miktarı uygular. | Yok. | `strategy.entry` stop emri ve iki yön, `mintick`, varsayılan ayarlar ve çıkışsız pozisyon davranışı yorumlayıcıda destekleniyor. Kaynakta olmayan bir stop-loss/TP eklenmemiş. |
| `627VbHkS` | `st.d < 0 && medianValue > 0` long, `st.d > 0 && medianValue < 0` short. Ters pozisyon önce `strategy.close`, sonra yeni `strategy.entry`. Açık pozisyonda üçer kademeli limit TP (`qty_percent`) var; sabit stop-loss yok (kaynak satırları 237–277). | `percent_of_equity`, %10, başlangıç 10.000 USD; komisyon %0,1 ve slippage 1. | Yok. | `strategy.close`, ters giriş ve `strategy.exit` kademeleri yorumlayıcı çağrılarına karşılık geliyor. Kaynakta olmayan sabit stop veya ek risk kapısı görülmedi. |
| `GjZOz8Pu` | İki SuperTrend aynı yöndeyse ve VIX filtresi uygunsa long/short; trend tersine dönünce `strategy.close`. Varsayılan `use4StepTP=true` ile dört kademeli limit+stop çıkış; alternatif standart/trailing/ATR yolları input’a bağlı (kaynak satırları 146–257). | `percent_of_equity`, %10, başlangıç 10.000 USD; komisyon %0,1, slippage 1. | `request.security(vixSymbol, "D", close, lookahead=barmerge.lookahead_off)` (kaynak satır 96). | Aynı sembol dışı üst zaman dilimi verisi için yorumlayıcı veri sağlayıcısını kullanıyor; `lookahead_off` korunuyor. Giriş/close ve dört kademeli `strategy.exit` çağrıları mevcut. Denetim riski kaynakta `vixSymbol` varsayılanının `VIX` olması ve sağlayıcı eşlemesinin veri bağımlı olmasıdır; bu satırda karar değişikliği yapılmadı. |
| `KUyDNRyQ` | HMA, grafik fiyatı ve günlük `s2` ilişkisiyle long/short `strategy.order`; `strategy.openprofit < SL` veya `> TP` olunca `strategy.close_all` (kaynak satırları 4–23). | `percent_of_equity`, %1, başlangıç 1 BTC; komisyon %0,25, slippage 1. | `security(syminfo.tickerid, timeframe.period, ..., lookahead_off)` ve günlük `security(..., "D", ..., lookahead_off)` (kaynak satırları 9–10). | `strategy.order`, `close_all`, açık kâr ve aynı sembol/HTF security yorumlayıcıda destekleniyor. `SL` negatif açık kâr eşiği ve `TP` pozitif eşik olarak kaynakta ne yazıyorsa öyle bırakılmış; bunlar fiyat stop/limit emri değildir. |
| `QPIGo8hs` | `vwap_smooth` EVWMA’yı yukarı kesince long, aşağı kesince short; iki `strategy.entry` dışında çıkış çağrısı yok (kaynak satırları 8–22). | `strategy()` içinde özel boyut, komisyon veya kayma yok; v4 varsayılanı. | Yok. | `crossover/crossunder` koşulları ve iki yönlü `strategy.entry` yorumlayıcı akışıyla uyumlu. Kaynakta olmayan çıkış, maliyet veya boyut varsayımı rapora eklenmedi. |

## Bulgular

1. Beş kaynağın giriş, yön ve açıkça yazılmış çıkış emirleri yorumlayıcının
   desteklediği çağrı yüzeyiyle eşleşiyor. Kaynakta çıkış olmayan üç stratejiye
   (`3UcIwSrE`, `QPIGo8hs` ve açık pozisyon süresince `627VbHkS`'nin stop yolu)
   sonradan çıkış kuralı eklenmemiş.
2. Boyut, komisyon ve kayma `strategy()` bildiriminden alınmış; özellikle
   `627VbHkS`, `GjZOz8Pu`, `KUyDNRyQ` için sonuçta görülen maliyet/pozisyon
   ayarları kaynakla uyumlu.
3. `KUyDNRyQ` günlük `security` çağrısını, `GjZOz8Pu` ise başka sembol ve
   günlük VIX çağrısını kullanıyor. Her ikisinde de kaynak `lookahead_off`
   istiyor. `GjZOz8Pu` için dış VIX veri eşlemesi ayrıca izlenmesi gereken bir
   veri bağımlılığıdır; bu gözlem karar veya eşik değişikliği değildir.

## Kaynak kimlikleri

- `3UcIwSrE`: `PUB;purCQAHAasps9PmtDqur8gYaumgoZcc7`
- `627VbHkS`: `PUB;34aa06ef9de446228afd25540ad36700`
- `GjZOz8Pu`: `PUB;9ef3d684e78c47fcb4568d4501089313`
- `KUyDNRyQ`: `PUB;da4x6yqpEKXrvBPKlqH3QKx0S7lyhhJN`
- `QPIGo8hs`: `PUB;A6WdofrgI0Q9dXSHuJIgyxy2LNyuQ2Ar`

