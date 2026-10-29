# Argon görevleri — 3. tur (2026-10-29, lider)

Kullanıcı kutulardan **birini** olduğu gibi kopyalayıp Argon'a verir, cevabı getirir; lider `arastirma/copytrade/argon_*.md`
olarak kaydeder ve denetim notu yazar. Sıra: A20 → A21.

---

## A20 — Hyperliquid'de HIP‑3 ve küçük coin gerçek işlem maliyeti

```
Bağlam: Hyperliquid perp borsasında traderları gölge olarak (gerçek parasız) kopyalayan bir araştırma yürütüyoruz. Maliyeti
şu an tek oranla modelliyoruz: taker ücreti %0,045 + kayma %0,05 (tek yön). Bu, BTC/ETH gibi likit coinlerde makul; ama
HIP-3 piyasalarında (kripto dışı: hisse, emtia, endeks perp'leri) ve küçük coinlerde iyimser olabilir.

İstenen:
1. HIP-3 piyasalarının güncel ücret yapısı: taker/maker ücreti, piyasa kurucusunun (deployer) ek ücreti, ücret çarpanı varsa
   ne kadar. Resmî Hyperliquid belgesi ve duyurularından, bağlantıyla.
2. Kayma (slippage) için ölçüt: HIP-3 ve küçük hacimli coinlerde tipik alış-satış makası ve 1.000–10.000 $ emirde fiyat etkisi.
   Ücretsiz kaynaklardan (Hyperliquid'in halka açık API'si: l2Book, ya da halka açık panolar). Ölçtüysen ne zaman, hangi
   coinlerde, kaç örnekle ölçtüğünü yaz.
3. Asgari emir değeri (minimum order size/notional) Hyperliquid'de kaç $; HIP-3'te farklı mı?
4. Sonuç olarak üç sınıf için önerilen tek yön maliyet aralığı: (a) BTC/ETH, (b) diğer büyük coinler, (c) küçük coin + HIP-3.
   Her sayının kaynağını ya da hesabını göster.

Kurallar: kaynak bağlantısı ve erişim tarihi zorunlu; açılıp görülmeyen bilgi "doğrulanamadı" diye işaretlenir; tahmin tahmin
diye yazılır; ödeme, kayıt, kart ya da API anahtarı gerektiren adım yapılmaz. Cevap Türkçe, tablo + kısa açıklama.
```

---

## A21 — Hyperliquid halka açık API'sinden geçmiş dolumları geri alma sınırları

```
Bağlam: Hyperliquid'de ~200 adresin işlem dolumlarını (fills), funding ödemelerini ve saatlik mumlarını halka açık API ile
(https://api.hyperliquid.xyz/info, anahtarsız) 15 dakikada bir arşivliyoruz. Arşivde birkaç saatlik boşluk oldu; bu boşluğu
geriye dönük doldurabilir miyiz, bilmek istiyoruz.

İstenen (resmî Hyperliquid API belgesinden, bağlantıyla):
1. userFills ve userFillsByTime: en fazla kaç kayıt döner, ne kadar geriye gidilebilir (ör. "en son 10.000 dolum"), sayfalama
   nasıl yapılır? Çok aktif bir adreste (günde 1.000+ dolum) bir haftalık boşluk geri alınabilir mi?
2. userFunding: aynı sorular.
3. candleSnapshot: saatlik mumda en fazla kaç mum / ne kadar geriye; HIP-3 piyasaları için coin adı nasıl yazılır?
4. İstek sınırları (rate limit): ağırlık sistemi, IP başına dakikalık sınır; 200 adres × 3 istek tipini 15 dakikada güvenle
   sığdırmak için önerin.
5. Belgede olmayan ama topluluk kaynaklarında (GitHub issue, Discord özeti) geçen sınırlamalar — "doğrulanamadı" etiketiyle.

Kurallar: kaynak bağlantısı ve erişim tarihi zorunlu; tahmin tahmin diye yazılır; ödeme, kayıt ya da anahtar gerektiren adım
yapılmaz. Cevap Türkçe, madde madde.
```
