# Karşılaştırma — bağımsız trader seçimi (lider, 2026-10-27)

9 cevap (beamfree, big pickle, deepseek, nemotron + 5 adsız md). **Uyarı:** 7'si bizim `sonuc.csv`'den çalıştı; aynı
adreslerde birleşmeleri bağımsız doğrulama değildir. Kendi verisiyle çalışanlar: `deepseek.txt` (canlı API, 120 adres) ve
`hyperliquid_elle_kopya_aday_analizi.md` (Hyperdash/Hydromancer vb.). Toplam 92 benzersiz adres.

## En çok anılan adresler (bizim kapı değerleriyle)
| Kaç cevapta | Adres | Kapı (eski koşu) |
|---|---|---|
| 8 | 0x8bae…3ab6d | 3+4 Geçti; swing 81 sa; 30dk +%21,7; kârlı ay %100; t 3,74 (izleme listesinde T1) |
| 8 | 0x9312…6663 | 3 Geçti, 4 Kaldı; swing 125 sa; 2sa +%125; t 2,43 |
| 7 | 0x4c92…42db | 3 Geçti, 4 Kaldı; 3,2 sa; kaldıraç 0,07x; t 5,17 |
| 7 | 0xe573…4e55 | 3 Geçti, 4 Kaldı; 19,6 sa; 30dk +%70; t 3,12 |
| 7 | 9 adım-5 adayı (0x09d7, 0x3ea0, 0x3e68, 0x2975, 0x69b0, 0x3f96, 0x79bf, 0x1404*, …) | 3+4 Geçti; plasebo bekleniyor |
\* 0x1404 adım 4'te Kaldı; deepseek kendi 190 günlük hesabında gecikmeli kopyayı **−%22,6** buldu (bizde +%22) → doğrulanacak.

## Bizim görmediğimiz, doğru bulunan kör noktalar
1. **Adım 7 (BHY) çözünürlüğü yetersiz.** 1000 tekrarla en küçük p ≈ 0,001; tek başına en güçlü aday için BHY tabanı
   p·m·c(m): m=30 → 0,12, m=60 → 0,28. (Düzeltme, Sol 6.1: BHY sıralı bir yöntemdir; birden çok küçük p birlikte
   geçebilir; "kimse geçemez" ifadesi yanlıştı.) Çözüm: 10.000 tekrar — çözünürlüğü iyileştirir, anlamlılık üretmez.
   Test ailesi önceden tanımlı: adım 1–4'ü geçen herkes (`m`); "geçene kadar tekrar artırma" yok.
2. **Gece penceresi.** Intraday trader TSİ 01–08 arasında açıp kapatıyorsa sabit 30 dk testi kârlı gösterir ama
   kullanıcı uyurken kopyalanamaz. Ölçüt: "TSİ gece açılıp sabah 09'dan önce kapanan işlem payı".
3. **Son 90 gün aktiflik/form yok.** Durmuş hesaplar (ör. 0x19e9… 90 günde 0 işlem) listeye girebiliyor. İzleme
   ışığında "30 gün işlem yok" var, kapıda yok.
4. **Gecikmeli kopya en fazla ~200 gün.** 1 saatlik mum sınırı (5.000 mum); "12 ay" iddiası gecikme için geçerli değil.
   Raporda açıkça yazılmalı.
5. **Parçalı kapanış / TP1.** Medyan tutma, kısmi kâr alan swing trader'ı kısa gösterebilir. Ağırlıklı (büyüklükle)
   tutma süresi daha doğru olabilir. Bizde round-trip düz-düz (flat-to-flat) birleşik; etkisi ölçülmeli.
6. **Düşüş derinliği ve toparlanma süresi** kapı ölçütü değil (yalnız 1. aşamada). Elle kopyalayan en çok uzun
   düşüşte bırakır.

## Kapsam
deepseek kapının hiç bakmadığı 54 adresten 4'ünü listesine aldı → kapsam eksikliği (%66) gerçek; Sonnet'in işinde.

## Kararlar (2026-10-27, kullanıcı + Sol 6.1)
- 10.000 tekrar; test ailesi = adım 1–4'ü geçen herkes; tekrar sayısı bir daha değişmez.
- **Aktiflik eklenir:** son 90 günde kapanmış döngü intraday ≥ 20, swing ≥ 5; son işlem ≤ 30 gün önce. Kâr şartı yok.
- **Gece penceresi: kapı ölçütü değil** (kullanıcı: "kasma"); yalnız raporda gece açılan işlem payı bilgi olarak.
- 0x1404 farkı aynı aralık/maliyet/payda ile mutabık kılınır; modellerin kayıtsız "canlı API" beyanları doğrulanmış sayılmaz.
- Kurallar bu turdan sonra **dondurulur**; asıl kanıt sonraki 3 ay ileriye dönük sanal izleme.
- Bilinen sınır: coin başına plasebo, coinler arası eşzamanlılığı ve toplam kaldıracı tam korumaz.

## İlk lider önerisi (tarihçe)
1 → Sonnet'e eklenir (hata düzeltmesi, eşik değil). 2, 3 → yeni ölçüt; 6 → yalnız raporla (eşik değil). 4 → raporda not.
5 → ölçülür, sonra karar.
