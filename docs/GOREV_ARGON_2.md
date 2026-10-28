# Argon görevleri — 2. tur (2026-10-28, lider)

Amaç: Sonnet ve Codex'in kullanım sınırını kod işlerine saklamak; dış araştırma, hesap ve görsel karşılaştırma Argon'da.
Argon GitHub'a bağlanamaz: kullanıcı aşağıdaki kutulardan **birini** olduğu gibi kopyalayıp verir, cevabı getirir; lider
`arastirma/copytrade/argon_*.md` olarak kaydeder ve başına denetim notu yazar. Sıra: A1 → A2 → A3 (hemen); A4 ve A5 malzeme gelince.

Her görevde ortak kurallar (kutulara dahil): kaynak bağlantısı ve erişim tarihi zorunlu; açılıp görülmeyen bilgi
"doğrulanamadı" diye işaretlenir; tahmin tahmin diye yazılır; ödeme, kayıt kartı ya da anahtar gerektiren adım yapılmaz.

---

## A1 — Ücretsiz geçmiş Hyperliquid hesap verisi (hemen)

```
Bağlam: Hyperliquid (perp DEX) copy trade araştırması yapıyoruz. Geçmiş bir tarihte (ör. 6 ay önce) leaderboard'da hangi
hesapların olduğunu ve o günkü hesap değeri / PnL'lerini bilmemiz gerekiyor (hayatta kalan yanlılığını önlemek için).
Dune bu veriyi veriyor ama API'si ücretli çıktı. Önceki araştırmanda Dune, Hyperliquid S3 (requester-pays) ve Nansen'i
bulmuştun.

Görev: ÜCRETSİZ (kredi kartı istemeyen) başka kaynak bul. Adaylar örnek: Hyperliquid'in kendi stats/leaderboard uç
noktaları, Hypurrscan, HyperDash, Allium, Flipside, Goldsky, Artemis, ASXN, açık GitHub veri setleri, Kaggle, Hugging Face.
Her aday için sayfayı/dokümanı gerçekten aç ve kontrol et:
1. Geçmiş tarihli veri var mı (günlük hesap değeri, PnL ya da leaderboard görüntüsü)? Ne kadar geriye gidiyor?
2. Kaç adres kapsıyor (yalnız ilk 100 mü, binlerce mi)?
3. Erişim: API / indirilebilir dosya / yalnız web arayüzü? Ücretsiz sınırı ne? Kayıt veya kart gerekiyor mu?
4. Örnek bir istek ya da indirme bağlantısı.

Çıktı: Markdown tablo (kaynak | geçmiş derinliği | adres kapsamı | erişim | ücretsiz mi | doğrulandı mı | bağlantı),
sonra en iyi 1–2 öneri ve neden. Bulamazsan "ücretsiz kaynak yok" de; uydurma.
```

## A2 — Kopya maliyet varsayımı doğru mu (hemen)

```
Bağlam: Hyperliquid'de bir trader'ın işlemlerini 30 dk (kısa vadeli) ya da 120 dk (uzun vadeli) gecikmeyle kopyalamayı
simüle ediyoruz. Kopyalayan küçük hesap: işlem başı 1.000–10.000 $. Her dolumda maliyet varsayımımız: taker ücreti
%0,045 + kayma %0,05 = işlem büyüklüğünün %0,095'i. Funding ayrıca gerçek oranlarla hesaplanıyor.

Görev:
1. Hyperliquid'in güncel ücret tablosunu bul: en alt (taban) kademede perp taker ve maker ücreti. HIP-3 (kullanıcıların
   açtığı) piyasalarda ücret farklı mı?
2. 1.000 $, 10.000 $ ve 50.000 $'lık piyasa emrinde tipik kayma: BTC, ETH, orta hacimli bir coin (ör. SOL ya da HYPE),
   küçük hacimli bir coin ve bir HIP-3 piyasası. Emir defteri derinliğini gösteren bir kaynak (Hyperliquid arayüzü,
   Coinglass, analiz yazıları) kullan; mümkünse sayısal örnek ver.
3. Funding hangi aralıkla ödeniyor (saatlik mi)?

Çıktı: tablo (piyasa | büyüklük | ücret | tahmini kayma | toplam) ve sonuç: %0,095 varsayımı "iyimser / makul / kötümser"?
Coin türüne göre farklı bir değer önerirsen gerekçesini yaz. Kaynak bağlantıları zorunlu.
```

## A3 — Kaç haftada ne görebiliriz (güç hesabı, hemen)

```
Bağlam: Seçtiğimiz trader grubunu (oda, 15 trader) aynı sayıda rastgele seçilmiş kontrol grubuyla 12 hafta karşılaştıracağız.
Her grup eşit ağırlıklı, sabit sermayeli sanal portföy. Ölçüm: iki portföyün günlük net getiri farkı. Belirsizlik: haftalık
blok bootstrap, %95 güven aralığı. Başarı: farkın alt sınırı > 0.

Görev: istatistiksel güç hesabı yap (formülleri ve varsayımları açıkça yaz):
1. Tek trader'ın kopya portföyünün günlük getiri standart sapması %1, %3 ve %5 iken; trader'lar arası ortalama korelasyon
   0,1 / 0,3 / 0,5 iken; 15'er kişilik iki grubun günlük getiri farkının standart sapması ne olur?
2. Haftalık bloklarla 12 haftada, %80 güçle ve %95 güvenle saptanabilecek en küçük günlük ortalama fark (ve yıllık karşılığı)
   nedir? 24 hafta için de ver.
3. Hafta içi otokorelasyonun etkisini kısaca belirt.

Çıktı: tablo (sd | korelasyon | 12 hafta en küçük fark | 24 hafta en küçük fark) + 3–4 cümlelik yorum: "12 haftada makul
bir farkı görebilir miyiz?" Hesabı adım adım göster ki kontrol edilebilsin.
```

## A4 — Oda listesinin dış doğrulaması (oda listesi çıkınca; lider adresleri verir)

```
Bağlam: Hyperliquid'de kopyalamak için seçtiğimiz trader adresleri aşağıda. Kendi verilerimizle seçtik; dışarıdan bakarak
gözden kaçan bir şey var mı kontrol etmeni istiyoruz. Hiçbir adresi eleme kararını sen vermiyorsun; yalnız bulguları yaz.

Adresler: <LİDER BURAYA LİSTEYİ KOYACAK>

Her adres için Hypurrscan, HyperDash ve arama motorlarında bak:
1. Vault, kurum, piyasa yapıcı (market maker), borsa ya da bot hesabı olarak etiketlenmiş mi?
2. Bilinen bir kişiye/X (Twitter) hesabına bağlı mı? Kamuya açık bilgiyle sınırlı kal.
3. Son 6 ayda büyük likidasyon, ani büyük para çekme ya da uzun süre işlemsizlik var mı?
4. Başka adreslerle bağlantısı (aynı kişiye ait görünen cüzdanlar) var mı?

Çıktı: tablo (adres ilk 6 hane | etiket | bulgu | kaynak bağlantısı | önem: yok/düşük/yüksek). Bulgu yoksa "bulgu yok".
```

## A5 — Ofis taslaklarını karşılaştırma (kullanıcı ekran görüntülerini verince)

```
Bağlam: Bir copy trade projesinin panosu için "izometrik piksel sanat ofis" ekranı yaptırdık. İki taslak var: Taslak 1
(çizim kalitesi iyi ama içinde insan figürü yok) ve Taslak 2 (ofis içi hareketlilik ve figürler daha iyi). Referans tarz:
ekteki Etre görüntüleri. Ekte üç grubun ekran görüntüleri/kayıtları var.

Görev:
1. Her taslağı 1–5 puanla: çizim ayrıntısı, renk/ışık sıcaklığı, figür ve animasyon, yan panelin okunurluğu, telefonda
   görünüm, Etre'ye yakınlık (kopya olmadan aynı tarz).
2. Birleştirme planı: hangi taslak esas alınmalı, öbüründen hangi 3–5 öğe taşınmalı? Somut ve maddeli yaz.
3. Etre'nin görüntülerinde olup ikisinde de olmayan en önemli 5 öğe.

Çıktı: puan tablosu + birleştirme planı + eksikler listesi.
```

## A6 — Açık kaynak copy trade araçlarının doğrulanması (hemen)

```
Bağlam: Hyperliquid'de trader seçip gecikmeli kopyayı simüle eden bir araştırma yapıyoruz (kapı: gecikme+maliyet sonrası
kopya getirisi, Deflated Sharpe, plasebo; ileriye dönük gölge ölçüm, rastgele kontrol grubu, ön kayıt). Başka modellerin
raporları aşağıdaki açık kaynak projeleri önerdi; hiçbirini biz açıp doğrulamadık.

Projeler (GitHub'da ara; adları yaklaşık olabilir):
1. Dennim89/hyperliquid-copytrade-study — 389 hesap, ön kayıtlı kalıcılık çalışması (sıralama korelasyonu +0,54 / 0 / −0,44)
2. winterchill-trading/copy-backtest — canlı motorla aynı kodla backtest; canlı-backtest farkını kalemlere ayırıyor
3. winterchill-trading/hl-leaderboard — 34 metrik, wash trade / hesaplar arası işlem / küme bütünlük bayrakları
4. hl-copy-core — puan: getiri × (1 − MDD) × (0,5 + 0,5 × tutarlılık) × min(1, işlem/20); boyutlandırma modları
5. YieldFund "Is Copy Trading Profitable? 90-day multi-exchange study" (1.486 lider, %97 / %43,6)

Her biri için: gerçekten var mı (bağlantı), son güncelleme tarihi, lisans, yöntem özeti (veri kaynağı, örneklem, dönem,
ön kayıt var mı), bizim için alınabilecek somut parça (ör. bütünlük bayrağının tanımı ve eşiği, kalıcılık testinin
tasarımı), bilinen zayıflıklar. Kalıcılık çalışmasının ön kayıt dosyasını ve sonuç tablosunu ayrıca özetle.
Bulamadığın ya da açamadığın için "doğrulanamadı" yaz; uydurma.

Çıktı: tablo (proje | var mı | lisans | yöntem | alınacak parça | zayıflık | bağlantı) + kalıcılık çalışması özeti.
```

## A7 — Hyperliquid emir kuralları ve sınırları (hemen)

```
Bağlam: Hyperliquid perp'lerinde trader'ları küçük sermayeyle (trader başına 200–1.000 $) kopyalamayı simüle ediyoruz.
Trader'ın işlemi bizim sermayemize oranlanınca çok küçük emirler çıkabiliyor. Gerçekçi simülasyon için borsanın emir
kurallarını kesin bilmemiz gerekiyor.

Görev — yalnız resmi kaynaktan (Hyperliquid docs / API belgesi / resmi duyuru), her madde için bağlantı:
1. Perp'te en küçük emir büyüklüğü (notional, ör. 10 $?) — sabit mi, coine göre mi değişiyor? HIP-3 piyasalarında farklı mı?
2. Büyüklük (lot, szDecimals) ve fiyat (tick, anlamlı basamak) yuvarlama kuralları; `meta` uç noktasında hangi alanlar.
3. Piyasa emri nasıl çalışıyor (IOC + kayma sınırı mı)? Varsayılan kayma sınırı var mı?
4. Azaltma emirlerinde (reduce-only) en küçük emir kuralı farklı mı? Kalan küçük pozisyon kapatılabiliyor mu?
5. API istek sınırları: info uç noktası ağırlıkları (clearinghouseState, userFillsByTime, l2Book, candleSnapshot),
   dakikalık toplam, websocket'te izlenebilecek kullanıcı sayısı; adres başına sınırlar.
6. Kaldıraç ve teminat: coin başına en yüksek kaldıraç nereden okunur; izole/çapraz farkı; likidasyon fiyatı formülü (özet).

Bulamadığın ya da resmi kaynakta olmayan maddeye "resmi kaynakta yok" yaz; ikincil kaynaktan geldiyse ayrıca belirt.
Çıktı: madde başına kısa cevap + bağlantı + erişim tarihi.
```
