# Sanal havuz taslağı

Bu belge bir **öneri taslağıdır**. Gölge kitaba aday eklemez, herhangi bir
karar/kapı/eşik değiştirmez ve gerçek para için talimat değildir.

## TV-2 sonuç anlık görüntüsü

Kaynak, `origin/codex/tv2-kosu` dalındaki
`8b5ac099b20a7e1a7aec9d22f2aecd665a790442` commit'inin
`results/tv2/siralama.csv` dosyasıdır. Dosyada 19 sıralı satır ve 15 küme
temsilcisi vardır. Aşağıdaki değerler ham sonuç değerleridir; burada yeni
filtre veya sıralama uygulanmadı.

| Sıra | Kimlik | Sembol / zaman dilimi | Sınama işlem | Ölçekli yıllık getiri | Haftalık p10 | PF | MDD |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | wcegMOXj | BINANCE:ETHBTC / 360 | 257 | 14.43% | 0.127% | 2.193 | 1.13% |
| 2 | 3UcIwSrE | KRAKEN:ETHUSD / 60 | 2,988 | 4.45% | 0.016% | 1.081 | 2.40% |
| 3 | VQjItUaK | BITFINEX:XRPUSD / 60 | 2,902 | 4.63% | -0.003% | 1.110 | 0.00% |
| 4 | j9rq1wQq | BINANCE:QTUMUSDT / 12H | 221 | 3.23% | -0.021% | 1.371 | 0.01% |
| 5 | mXygJWkv | BINANCE:BTCUSDT / 60 | 638 | 2.68% | -0.026% | 1.057 | 34.76% |
| 6 | zFKRj4Gi | BITFINEX:BTCUSD / 480 | 117 | 5.27% | -0.026% | 1.307 | 5.13% |
| 7 | 627VbHkS | BITFINEX:BTCUSD / 360 | 42 | 6.86% | -0.027% | 1.570 | 4.35% |
| 8 | QPIGo8hs | BINANCE:ETHBTC / 120 | 899 | 3.33% | -0.028% | 1.116 | 0.00% |
| 9 | YqnWtjnn | BITFINEX:BTCUSD / 360 | 126 | 8.96% | -0.031% | 1.605 | 1.77% |
| 10 | KUyDNRyQ | BITSTAMP:ETHBTC / 60 | 620 | 3.28% | -0.032% | 1.656 | 16.95% |
| 11 | hLZPT7it | BITFINEX:BTCUSD / 480 | 38 | 6.30% | -0.032% | 1.221 | 7.71% |
| 12 | XJfWHHEc | BITFINEX:BTCUSD / 360 | 36 | 5.54% | -0.032% | 1.578 | 5.13% |
| 13 | warXbPtA | BITFINEX:BTCUSD / 480 | 49 | 5.61% | -0.037% | 1.438 | 4.58% |
| 14 | lncoD9BX | BITFINEX:BTCUSD / 480 | 47 | 4.06% | -0.082% | 1.345 | 3.99% |
| 17 | VHbRaeUe | BITFINEX:BTCUSD / 360 | 79 | 1.80% | -0.112% | 1.111 | 9.03% |

## U7 sonuç anlık görüntüsü

U7 sıralaması analiz dalında, `origin/codex/u7-tum-stratejiler`
`aaefebbde7aecdf7b0262b39efd6abb3e3518b32` kaynak verisinden türetildi.
85 sıralı varyant ve 72 küme temsilcisi vardır. Aşağıdaki ilk 12 temsilci
yalnız kaynak/sıralama görünürlüğü içindir; TV-2 ile birleştirilmiş kitap
listesi değildir.

| Sıra | Varyant | Piyasa / zaman dilimi | Sınama işlem | Ölçekli yıllık getiri | Haftalık p10 |
|---:|---|---|---:|---:|---:|
| 1 | TV-zoY9DmsF | ABD25 / 1D | 119 | 13.24% | 0.157% |
| 2 | TV-sPNx5Z74 | ABD25 / 1D | 23 | 11.05% | 0.116% |
| 3 | TV-DUCODGjC | ABD25 / 1D | 295 | 10.59% | 0.107% |
| 4 | TV-IMKs0OPw | ABD25 / 1D | 211 | 9.71% | 0.101% |
| 5 | TV-71yKm18B | KRIPTO25 / 4H | 226 | 13.48% | 0.098% |
| 6 | TV-dpkq3n4O | ABD25 / 1D | 150 | 9.94% | 0.092% |
| 7 | TV-70PkIvTL | ABD25 / 1D | 126 | 10.75% | 0.091% |
| 8 | TV-bZ815rmw | ABD25 / 1D | 26 | 9.52% | 0.081% |
| 9 | TV-KO7Qe4Xb | EMTIA / 1D | 76 | 8.13% | 0.069% |
| 10 | TV-3Q75d98D | KRIPTO25 / 1D | 307 | 12.42% | 0.069% |
| 11 | TV-3BXWqwnF | KRIPTO25 / 1D | 94 | 12.32% | 0.068% |
| 12 | TV-Q9OQye4C | KRIPTO25 / 1D | 285 | 11.22% | 0.064% |

## Öneri olarak sonraki adım

- TV-2 ve U7 aynı kaynak anlık görüntüsünde birlikte değerlendirilmeden aday
  havuzu oluşturulmasın.
- Bu önkoşul sağlandığında mevcut prosedür uygulanır: önce birleşik sıralamada
  en yüksek 12 küme temsilcisi, sonra onlarla en düşük ortalama korelasyonlu
  4 çeşitlendirici ve kalan uygun temsilcilerden sabit tohumla 4 kura adayı.
  Ortak günlük getiri kesişimi ve seçim kaydı olmadan bu 20 aday yazılmaz.
- Birleştirme yapılırsa, yalnız `docs/TEST_YAPISI.md` içindeki mevcut
  prosedür ve kayıt gereklilikleri kullanılsın; bu taslak yeni sayı ya da
  terfi kararı üretmez.
- Veri vekilliği olan satırlar (örneğin Kraken/Bitfinex/Bitstamp sembollerinin
  Binance verisiyle çalıştırılması) sanal izlemede kaynak notuyla korunmalı;
  bunlar canlı uygulanabilirlik kanıtı değildir.
