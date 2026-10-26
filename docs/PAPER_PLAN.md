# Paper planı taslağı — Faz 1

Bu bir uygulama yapılandırması değildir. `paper/` ve `paper.yml` değiştirilmeden, kullanıcı onayından önce dondurulmuş girdi `results/faz1_paper_listesi.csv` olarak tutulur.

## Kitaplar ve risk payı

Toplam hedef yıllık oynaklık yaklaşık %6'dır. Aşağıdaki oranlar sermaye, kaldıraç ya da emir büyüklüğü değildir; maksimum risk bütçesi payıdır. Kullanılmayan %10 boş kalır.

| Kitap | Rol | Risk payı |
|---|---|---:|
| TV-zoY9DmsF | ilk dalga | %9 |
| TV-DUCODGjC | ilk dalga | %7 |
| TV-dpkq3n4O | ilk dalga | %7 |
| TV-70PkIvTL | ilk dalga | %7 |
| G4RNcGXg | ilk dalga, küçük | %5 |
| TV-71yKm18B | ilk dalga | %15 |
| TV-3BXWqwnF | ilk dalga, daha küçük | %10 |
| wcegMOXj | ilk dalga, küçük | %5 |
| TV-KO7Qe4Xb | ilk dalga | %13 |
| U4-H3:EMTIA:1D | ilk dalga, küçük | %7 |
| yhoK9cH4 | keşif, çok küçük | %5 |
| TV-egTb7TgJ; TV-Q9OQye4C; U4-H2:KRIPTO25:1D | gölge | %0 |
| boş | rezerve | %10 |

Alan tavanları: ABD %35, kripto %30, emtia %20, keşif %5. Gölge kitaplar aynı sinyal/günlük özkaynak izleme hattında çalışır ama risk bütçesine sayılmaz ve emir üretmez.

## Zorunlu çalışma kapıları

- Kitap başına sanal sermaye 5.000 USD'dir; miktar, donmuş kaynakta yazan birim ve uygulanabilir notional/teminat sınırıyla riskten hesaplanır. Geçmiş düşük oynaklık sınırsız kaldıraç gerekçesi değildir.
- `wcegMOXj` için hesap birimi BTC'dir: ETH adetinden oluşan PnL her değerleme anında aynı zaman damgalı BTCUSD kapanışı ile USD'ye çevrilir. BTC bakiyesi, USD karşılığı ve dönüşüm kuru ayrı kaydedilir. Bu mutabakat tamamlanana kadar risk payı kullanılamaz.
- TV-2 kitapları G4RNcGXg, wcegMOXj ve yhoK9cH4 için kaynak Pine metni, varsayılan parametreler ve maliyet varsayımı hash'lenmeden emir üretilemez.
- Aynı sembol/yön pozisyonları toplanır; **aynı sembolde aynı yönde** en fazla üç kitap aynı anda açık risk taşır (toplam kitap sayısı sınırı değildir).

## Durdurma ve rejim kuralları

- Her kitap, kendi sermaye zirvesinden %10 gerilediğinde durur; yeniden başlatma insan onayı ve mutabakat ister.
- Sermaye girişlerinden arındırılmış portföy özkaynağı zirveden %5 gerilerse yeni girişler durur; açık koruyucu çıkışlar çalışmaya devam eder.
- Günlük korelasyonu 0,6'nın üzerindeki çiftlere eşzamanlı bağımsız tam bütçe verilmez. Haftalık ve son 90 günlük korelasyon uyarı olarak kaydedilir.
- SPY ve BTC betası risk açılmadan kaydedilir. Önceki kapanış kendi 200 günlük ortalamasının altındaysa, yalnız yeni uzun yön riski yarıya iner; koruyucu azaltma/çıkış emirleri otomatik küçültülmez.

Bu taslak karar ya da kapı değişikliği değildir. Adım 0'daki `KOŞULLU` sonuçlar ve CSV'deki mutabakat açıkları listede kalır; lider ve kullanıcı karar vermeden etkinleştirilmez.
