# Faz 2 — dört piyasa-verisi doğrulaması

Bu çalışma TV-2'nin Pine yorumlayıcısını, dolum semantiğini, gerçekçi maliyetini ve tek karar kapısını değiştirmez: uygulanabilir sınama neti `> 0` ise geçer. Yalnız vekil fiyatlar asıl piyasaya daha yakın ücretsiz kaynaklarla değiştirilir. Ayrıntılı sayısal sonuçlar `results/faz2_dogrulama.csv` içindedir.

| Kimlik | Doğrulama | Not |
|---|---|---|
| QCkIgf3z | Coinbase ETH-USD 15dk | Exchange API anahtarsızdır; 300 mum sınırında `start`/`end` ile sayfalanır. |
| BR74LOKo | Binance USDⓈ-M BTCUSDT perp 15dk | Bybit ABD IP'de erişilemediğinde kabul edilmiş ücretsiz vekil; funding'li ve funding'siz metrikler ayrı yazılır. |
| zuEOEYPK | Binance USDⓈ-M BTCUSDT perp 1s → 3s | BingX için aynı vekil ve 00/08/16 UTC funding uygulanır. |
| 9u8pzF0I | MNQ=F ve QQQ 60dk → 120dk | MNQ'da 0,25 tick ve puan başına 2 USD kullanılır. MNQ=F devir boşlukları üçüncü Cuma öncesindeki pencerede bulunur; tarihçe boşluk kadar geri-düzeltilir, devir sonrası fiyatlar sabit kalır. QQQ yalnız normal seanstır; CME Globex'in 23 saatlik seansı değildir. |

Funding, ödeme anında açık olan işlem için `-yön × adet × perp_kapanışı × oran` nakit akışıdır: pozitif oranda uzun öder, kısa alır. Raporlanan `fundingli_*` sütunları bu akışı özkaynağa ve nete uygular; `funding_nakit` toplam etkidir.

MNQ sürekli kontratta stratejinin adet/`default_qty` seçimi Pine kaynağından aynen gelir. Emülatörde kontrat PnL'i artık `adet × puan farkı × $2` ile hesaplanır; bu, yalnız MNQ koşusuna verilen kontrat tanımıdır. MNQ ham satırındaki `devir_acik_pnl_puan`, saptanan devir anında açık olan işlemlere yazılan hayalî puan PnL'ini ayrıca raporlar.
