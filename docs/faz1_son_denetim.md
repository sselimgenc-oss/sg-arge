# Faz 1 son denetim — lider (Sol 6.1 denetimi bekleniyor)

Kullanıcı: "Nihai karar içinize sindi mi? İkiniz de işlemleri denetleyin, B kararını da siz verin."

## Lider bulguları

### D1. Kendi hatam: "yılda işlem" hesabı yanlıştı
Yılda işlem sayısını sürüm tarihinden bugüne böldüm; oysa yfinance saatlik veri yalnız son ~2,9 yılı kapsıyor. Doğru pencereyle:
- **G4RNcGXg (SPY 1s): 30,6 işlem/yıl → kullanıcı kuralını geçiyor.** B kararı ortadan kalkıyor; aday kalır.
- hWvuZJN1 25,8 · oZYSB6Ui 20,7 · PZ5MpxP1 12,4 · WfaaCqaN 12,0 → yine kuralın altında, çıkar.
- Kullanıcının daha önce çıkardığı zayıflardan 4'ü (CSGmHoik TQQQ, xXrbltSH NQ, jn1rXKpM GOLD, MNBZqC72 MSI) doğru pencereyle ≥ 30/yıl; ama hepsi ~2,5 aylık veride 6–25 işlem. Kanıt yok denecek kadar az; çıkarılmış kalmaları önerilir.

### D2. Getirinin ne kadarı piyasa? (2023→, günlük; beta = piyasaya duyarlılık, alfa = piyasadan bağımsız kısım, t ≥ 2 anlamlı sayılır)

| Kimlik | Piyasa | Yıllık | Piyasa payı | Alfa | Alfa t |
|---|---|---:|---:|---:|---:|
| TV-zoY9DmsF | SPY | 4,4 | 1,7 | 2,6 | **2,1** |
| TV-DUCODGjC | SPY | 7,2 | 2,7 | 4,5 | 1,6 |
| TV-IMKs0OPw | SPY | 3,7 | 1,6 | 2,1 | 1,4 |
| G4RNcGXg | SPY | 4,7 | 2,6 | 2,1 | 1,2 |
| U4-H3:ABD25:1D | SPY | 3,9 | 2,7 | 1,2 | **0,6** |
| TV-dpkq3n4O (yedek) | SPY | 5,9 | 2,3 | 3,7 | 1,5 |
| TV-70PkIvTL (yedek) | SPY | 5,2 | 2,6 | 2,7 | 1,5 |
| TV-71yKm18B | BTC | 12,1 | 4,0 | 8,1 | 1,9 |
| TV-3BXWqwnF | BTC | 13,7 | 6,0 | 7,7 | 1,5 |
| U4-H2:KRIPTO25:1D | BTC | 7,5 | 4,0 | 3,5 | **0,6** |
| wcegMOXj (ETHBTC) | BTC | 1,9 | 0,1 | 1,8 | **2,2** |
| TV-egTb7TgJ (gölge) | BTC | 5,0 | 2,5 | 2,5 | 1,1 |
| TV-Q9OQye4C (gölge) | BTC | 7,4 | 4,4 | 3,0 | 1,1 |

(Yıllık değerler aynı ölçekte günlük ortalama × gün; aday tablosundaki "ölçekli yıllık" ile birebir aynı değil.)

Yorum: 2023-2026 hem ABD hem kripto için güçlü yükseliş dönemi. Stratejilerin çoğu uzun yönlü; getirinin %35-70'i piyasanın yükselişinden. Piyasadan bağımsız kısım (alfa) hepsinde pozitif ama yalnız 2'sinde istatistiksel olarak güçlü (zoY9DmsF, wcegMOXj). **Bu, stratejilerin kötü olduğu anlamına gelmez; beklentiyi düşürür ve paper'ın asıl test olduğunu gösterir.** Düşen piyasada bu kitapların birlikte zarar etmesi beklenmeli.

### D3. Mutabakat
wcegMOXj, G4RNcGXg, yhoK9cH4: günlük seri ile CSV neti tutarlı (fark ≤ 1,4 puan, günlük yeniden örnekleme). QCkIgf3z: tutarsız (4,8 ↔ 22,6) → beklemede kalır.

## Liderin karar önerisi (değişiklikler)
1. **U4-H3:ABD25:1D → yedek; yerine TV-dpkq3n4O.** Alfa t 0,6, getirinin çoğu piyasa; Sol da "yöntem çeşitliliği tercihi, p10 ile savunulamaz" demişti. dpkq3n4O'nun ilk dalgaya korelasyonu ≤ 0,31.
2. **G4RNcGXg kalır** (D1). Ama aktif günlerde SPY ile 0,87 korelasyon: fiilen "zamanlı SPY". Küçük boyut.
3. **U4-H2:KRIPTO25:1D çekirdekte kalır ama küçük** (alfa zayıf; tek değeri çekirdeğe düşük korelasyon 0,37/0,54). Alternatif yok: diğer sepetlerin hepsi çekirdeğe ≥ 0,6.
4. Portföy kuralına ekleme: **piyasa yönü tavanı** — ABD kitaplarının toplam SPY betası ve kripto kitaplarının toplam BTC betası ayrı izlenir; düşüş rejiminde (SPY/BTC 200 günlük ortalamanın altı) yeni giriş yarıya iner. (Öneri; Sol'un görüşü alınacak.)

## Sol 6.1 denetimi

(bekleniyor)
