# Argon görev paketi: T11 tarihsel endeks bileşenleri (veri toplama)

Bu mesajı olduğu gibi Argon'a yapıştır. Cevabı **iki CSV dosyası** olarak kaydet: `T11_bist30.csv` ve `T11_abd25.csv`. İkisini de `argon/` klasörüne yükle.

---

Sen bir algo trading araştırma ekibinde **veri toplama işçisisin** (rol adı: Argon). Takım lideri Claude Opus. Çıktın satır satır denetlenecek. Yorum ya da değerlendirme yapma; yalnız veriyi kaynağıyla topla.

## Neden
Backtestlerde bugünün büyük şirketlerini geçmişe uyguluyoruz (survivorship yanlılığı). Geçmişte gerçekten endekste olan şirketlerin listesine ihtiyacımız var.

## Görev 1: BIST 30 dönemsel bileşenleri (2015 → 2026)
Borsa İstanbul BIST 30 endeksini her dönem (genelde 3 ayda bir: Ocak, Nisan, Temmuz, Ekim) yeniden belirler. Her dönem için endekse giren 30 hissenin kodlarını bul.
- Kaynak önceliği: (1) Borsa İstanbul duyuruları / "Endeks Dönemsel Değişiklikleri", (2) KAP duyuruları, (3) güvenilir finans haber siteleri (Bloomberg HT, AA Finans, Foreks vb.) ya da Wikipedia dönem tabloları.
- Hiçbir dönemi tahmin etme. Bulamadığın dönemi `bulunamadi` diye işaretle.

`T11_bist30.csv` biçimi (her satır bir dönem × bir hisse):
```
donem_baslangic,hisse_kodu,kaynak_url,not
2015-01-02,AKBNK,https://...,
2015-01-02,ARCLK,https://...,
...
2016-04-01,bulunamadi,,kaynak yok
```
- `donem_baslangic`: listenin geçerli olduğu ilk işlem günü (YYYY-MM-DD).
- Her dönemde tam 30 satır olmalı. Eksik çıkarsa `not` sütununa "eksik: N hisse" yaz.
- Hisse kodunu bugünkü haliyle yaz; kod değiştiyse eskisini `not`'a ekle (örnek: KOZAL → TRALT).

## Görev 2: ABD en büyük 25 şirket (yıl başları, 2015 → 2026)
Her yılın ilk işlem günü itibarıyla piyasa değeri en büyük 25 ABD şirketi (S&P 500 içinden).
- Kaynak önceliği: yıl başı piyasa değeri sıralaması yayımlayan güvenilir kaynaklar (companiesmarketcap.com geçmiş sıralamaları, Wikipedia "List of public corporations by market capitalization" yıllık tabloları, Slickcharts arşivi, finans haber siteleri).
- Aynı şirketin birden fazla hisse sınıfı varsa (GOOGL/GOOG, BRK-A/BRK-B) tek satır yaz, likit olanı seç (GOOGL, BRK-B).

`T11_abd25.csv` biçimi:
```
yil,sira,ticker,sirket,kaynak_url,not
2015,1,AAPL,Apple,https://...,
...
```

## Kurallar
- **Uydurma yok.** Her satırın `kaynak_url`'si olmalı; kaynaksız satır yazma.
- Kaynaklar arasında çelişki varsa resmi olanı (Borsa İstanbul, KAP) seç ve `not`'a diğerini yaz.
- Yalnız CSV ver; açıklama metni yazma. En sonda ayrı bir satırda: `# ozet: bist_donem=N, bist_bulunamayan=N, abd_yil=N`
