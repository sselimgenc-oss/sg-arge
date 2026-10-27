# Pano Faz 1 — kabul kanıtı

## Kayma altın örnekleri

Kayma, referans fiyata göre hesaplanır. Referans, aynı coindeki son `acilis`/`buyutme` olayı; yoksa pozisyon girişidir.
Eşikler: intraday `%0,5`, swing `%1,5`.

| Senaryo | Hesap | Beklenen rozet |
|---|---|---|
| Long, intraday | Referans `100`, şimdi `100,60`: `(100,60 − 100) / 100 = +%0,60`; long için aleyhte ve `%0,5` üstü | `Geç kaldın · +%0,60` |
| Short, intraday | Referans `100`, şimdi `99,20`: `(100 − 99,20) / 100 = +%0,80`; short için aleyhte ve `%0,5` üstü | `Geç kaldın · +%0,80` |

Bu rozet bilgi amaçlıdır; emir veya borsa bağlantısı oluşturmaz.

## Canlı kontrol

28 Ekim 2026 TSİ’de `0x8bae3527e5a33fa0cf184f37bc112d071463ab6d` adresi kontrol edildi. Tarayıcıdaki Hyperliquid sorgusu ve Hyperdash adres sayfası aynı sekiz açık pozisyonu gösterdi: BTC, DOGE, BSV, TNSR, kNEIRO, `xyz:GOOGL`, `xyz:SKHX`, `xyz:SKHY`.
