# Sanal havuz taslağı

Bu belge `docs/TEST_YAPISI.md` Adım 4'ün önceden yazılmış yürütme
taslağıdır. Bir aday listesi ya da gölge kitap değişikliği değildir; liste,
TV-2 ve U7 sonuçları birleştirildikten sonra aynı kuralla tek seferde üretilir.

## Girdi ve uygunluk

- Kaynaklar: `results/tv2/` ile `results/u7/` sonuçları ve günlük net getiri
  serileri. Her satır kaynak commit'i ve hesaplama zamanıyla kaydedilir.
- Adaylar: Adım 0'ı geçen; Adım 2 `Geçti` olanların tamamı ile `İzle`
  olanların tamamı. Koruma listesi ayrıca etiketlenir; sessiz eleme yapılmaz.
- Sıralama, `backtests/tv2_sirala.py` / U7 eşdeğerinin ortak %10 yıllık
  oynaklık, blok bootstrap p10 ve kopya kümeleri çıktısını kullanır. Yazarın
  bildirdiği getiri, kart sırası veya elle seçilmiş sembol kullanılmaz.

## 20 gölge kitap adayı

Liste, aynı sonuç snapshot'ında aşağıdaki sırayla ve yinelenebilir biçimde
oluşturulur:

1. Kopya kümelerinin en yüksek sıralı **12** temsilcisi `guclu` olarak alınır.
2. Kalan temsilcilerden mevcut 12'ye ortalama günlük-getiri korelasyonu en
   düşük olan **4** aday `cesitlendirici` olarak alınır. Aynı sembol + aynı yön
   için en çok üç kitap kuralı uygulanır.
3. Kalan uygun temsilciler arasından sabit tohum **20261024** ile örneklenen
   **4** aday `kura` olarak alınır. Evren, tohum, örnekleme algoritması ve
   adayların sıralanmadan önceki kimlik sırası sonuç dosyasına yazılır.

Yeterli temsilci yoksa eksik yer doldurulmaz; sayı ve neden açıkça yazılır.
Bu aşama yeni eşik üretmez, bir sıralama sonucunu değiştirmez ve kart
parametresine dokunmaz.

## Paper yürütmesi

- Her aday kendi yazar mantığı ve zaman diliminde, kapanmış bar sonrasında
  hesaplanır; maliyet bizim gerçekçi maliyet varsayımımızdır.
- Ortak karşılaştırma ölçeği yıllık %10 oynaklıktır. Her kitap 5.000 USD
  başlangıç sanal sermayesiyle, birbirinden ve ana portföyden ayrı izlenir.
- Sanal havuzun kitap sayısı sınırsızdır. Yalnız seçilen 20 aday gölge kitap
  önerisidir; bu belge hiçbirini `paper/`e eklemez.
- Her giriş/çıkış/değiştirme `results/canli/denemeler.csv` içinde kitap,
  strateji, kaynak sonuç snapshot'ı, tarih, neden ve önceki/sonraki adayla
  kalıcı biçimde kaydedilir. Satır silinmez.

## Canlı değerlendirme sınırı

Bir kitabın başlangıç sermayesinden %10 düşmesi, yalnız o kitabı durdurur;
yerine gelecek temsilci yukarıdaki kayıtla belirlenir. Aylık değerlendirme,
en az 26 canlı hafta ve 10 işlem haftasından önce gerçek para adayı üretmez.
Olasılık eşiği ve yanlış-terfi kalibrasyonu TEST_YAPISI'nda önceden yazılan
prosedürden alınır; bu taslakta değiştirilmez.

## Üretilecek kayıt

Seçim yapıldığında `results/canli/sanal_havuz_adaylari.csv` şu alanları taşır:
`sira, strateji_id, aile, grup, kaynak_snapshot, kategori, kume_id,
bootstrap_p10, ort_korelasyon, tohum, secim_nedeni`. Böylece lider kararı
öncesi 20 adayın neden ve hangi sonuçla seçildiği denetlenebilir.

## G1 ön önerisi — 2026-10-26

Bu yalnız `results/tv2/siralama.csv` içindeki mevcut kripto snapshot’ının
tekrar üretilebilir okumasıdır. Kripto dışı koşunun 0–6 artifact’ları henüz
geri alınamadığından nihai havuz değildir ve hiçbir `paper/` dosyasını
değiştirmez.

| Kategori | Sıra | Strateji | Sembol | TF | Neden |
| --- | ---: | --- | --- | --- | --- |
| güçlü | 1 | wcegMOXj | BINANCE:ETHBTC | 360 | sıralama küme temsilcisi |
| güçlü | 2 | 3UcIwSrE | KRAKEN:ETHUSD | 60 | sıralama küme temsilcisi |
| güçlü | 3 | VQjItUaK | BITFINEX:XRPUSD | 60 | sıralama küme temsilcisi |
| güçlü | 4 | j9rq1wQq | BINANCE:QTUMUSDT | 12H | sıralama küme temsilcisi |
| güçlü | 5 | mXygJWkv | BINANCE:BTCUSDT | 60 | sıralama küme temsilcisi |
| güçlü | 6 | zFKRj4Gi | BITFINEX:BTCUSD | 480 | sıralama küme temsilcisi |
| güçlü | 7 | 627VbHkS | BITFINEX:BTCUSD | 360 | sıralama küme temsilcisi |
| güçlü | 8 | QPIGo8hs | BINANCE:ETHBTC | 120 | sıralama küme temsilcisi |
| güçlü | 9 | YqnWtjnn | BITFINEX:BTCUSD | 360 | sıralama küme temsilcisi |
| güçlü | 10 | KUyDNRyQ | BITSTAMP:ETHBTC | 60 | sıralama küme temsilcisi |
| güçlü | 11 | hLZPT7it | BITFINEX:BTCUSD | 480 | sıralama küme temsilcisi |
| güçlü | 12 | XJfWHHEc | BITFINEX:BTCUSD | 360 | sıralama küme temsilcisi |
| çeşitlendirici | 13 | VHbRaeUe | BITFINEX:BTCUSD | 360 | ilk 12’ye en düşük ortalama mutlak günlük korelasyon (0.215) |
| çeşitlendirici | 14 | lncoD9BX | BITFINEX:BTCUSD | 480 | aynı ölçütte 0.282 |
| çeşitlendirici | 15 | warXbPtA | BITFINEX:BTCUSD | 480 | aynı ölçütte 0.314 |

Snapshot yalnız 15 küme temsilcisi içerdiği için 4. çeşitlendirici ve 4 kura
adayı üretilemedi. Eksik beş yer doldurulmaz; kripto dışı sonuçların tam
birleştirilmesinden sonra 20 aday kuralı yeniden uygulanır.
