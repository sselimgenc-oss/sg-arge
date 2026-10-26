# Faz 2 durum

## İş 3 — dört doğrulama

- TV-2 Pine yorumlayıcısı ve mevcut gerçekçi maliyet ayarlarıyla çalışacak `backtests/faz2_dogrulama.py` eklendi.
- Coinbase sayfalama, perp funding işareti ve MNQ back-adjust için ağsız birim testleri eklendi.
- MNQ doğrulamasında emülatöre kontrat puan değeri tanımı eklendi (`$2`, `0,25` tick); varsayılan değer 1 olduğundan mevcut strateji sonuçlarını değiştirmez.
- `paper/` dizinine dokunulmadı.

## Açık durum

- Tam ağlı koşu denendi; ortam vekili `api.exchange.coinbase.com` için `403 Forbidden` verdi. Bu nedenle doğrulama verisi indirilemedi ve sayısal sonuç CSV'si üretilmedi; uydurma sonuç yazılmadı. Erişim sağlandığında `python -m backtests.faz2_dogrulama` tüm satırları üretir.
