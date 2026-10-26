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

## Sonuç (Actions koşusu 40395868133, 2026-10-26) — lider yorumu

| Kimlik | Veri | Sınama | İşlem | Net % | PF | MDD % | Kaldıraç | TV-2 ilk net % | Kapı |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| QCkIgf3z | Coinbase ETH-USD 15dk | 03-12 → 10-26 | 287 | 4,90 | 3,14 | 0,2 | 0,10 | 22,60 | geçti |
| BR74LOKo | Binance UM perp 15dk + funding | 06-07 → 09-30 | 200 | 1,54 | 1,94 | 2,3 | 0,02 | 1,87 | geçti |
| zuEOEYPK | Binance UM perp 3s + funding | 04-03 → 09-30 | 43 | 0,46 | 1,85 | 0,3 | 0,10 | 1,05 | geçti |
| 9u8pzF0I | MNQ=F geri-düzeltilmiş 2s | 04-10 → 10-26 | 84 | 729 | 3,31 | 3,2 | 112 | 541 | geçti |
| 9u8pzF0I | QQQ 2s (yalnız seans) | 04-10 → 10-26 | 29 | 0,81 | 1,13 | 5,3 | 1,3 | 541 | geçti |

- Dördü de tek kapıyı (gerçekçi maliyetle sınama net > 0) asıl piyasaya yakın veriyle de geçti.
- QCkIgf3z: Coinbase'de net Binance'in ~1/5'i (4,9 / 22,6). Sonuç veri kaynağına duyarlı; PF 3,1 ve MDD %0,2 olağandışı iyi.
- BR74LOKo / zuEOEYPK: funding etkisi küçük (pozisyon sermayenin %2 / %10'u); getiriler küçük, sınama 4–6 ay.
- 9u8pzF0I: yazar 4.500 USD ile 8 MNQ (~112x nominal kaldıraç). 1x eşdeğeri ≈ %6,5 / 6,5 ay. Devir düzeltmesi
  sonucu az değiştiriyor (tespit sezgisel). QQQ'da (gece seansı yok) PF 1,13'e düşüyor: kenar büyük ölçüde
  Globex gece seansında. Paper'da kitap sermayesine ölçeklenir (kaldıraç olmaz).
- Hepsinin sınaması < 1 yıl: kanıt zayıf. Paper'a alınıp alınmaması kullanıcı kararı.
