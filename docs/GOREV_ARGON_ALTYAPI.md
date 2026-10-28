# Görev: Altyapı sınırları araştırması (Argon, 2026-10-28)

Kullanıcı bu metni Argon'a (Gemini) elle verir; Argon GitHub'a bağlanamaz. Çıktı kullanıcı tarafından getirilir, lider
`arastirma/copytrade/argon_altyapi_sinirlari.md` olarak koyar.

---

**Argon'a verilecek metin:**

Hyperliquid kaldıraçlı işlemlerinde ~300 trader adresini sürekli izleyip "gölge" (sanal) kopyalamak ve verileri arşivlemek
istiyoruz. Gerçek emir yok. Aşağıdakileri **resmî dokümanlardan** doğrula; her bilgiye kaynak bağlantısı ve erişim tarihi ekle.
Emin olmadığını "doğrulanamadı" diye yaz, tahmin etme.

1. **Hyperliquid info API:** IP başına istek ağırlığı sınırı (dakikada); `clearinghouseState`, `userFillsByTime`, `userFunding`,
   `candleSnapshot`, `l2Book`, `leaderboard` isteklerinin ağırlığı. `userFillsByTime` en çok kaç dolum döndürür, sayfalama nasıl?
   `candleSnapshot` en çok kaç mum döndürür, 1 dakikalık mumda ne kadar geriye gidilir?
2. **Hyperliquid websocket:** IP başına bağlantı ve abonelik sınırı; kullanıcıya özel aboneliklerde (`userFills`, `userEvents`)
   kaç farklı kullanıcı izlenebilir?
3. **Cloudflare Workers ücretsiz ve ücretli plan:** cron sıklığı, çağrı başına alt istek (subrequest) sınırı, CPU süresi, aylık ücret.
4. **Cloudflare R2:** ücretsiz katman (depolama GB, A/B sınıfı işlem sayısı), aşınca ücret, çıkış ücreti.
5. **GitHub Actions (herkese açık repo):** zamanlanmış iş en sık kaç dakikada bir, gerçekte ne kadar gecikebilir, iş süresi
   sınırı, eşzamanlı iş sayısı.
6. **Hyperliquid ücretleri:** güncel taker ücreti (temel kademe), HIP-3 piyasalarında farklı mı?

Sonuç: her madde için kısa tablo (değer, kaynak, tarih) ve en sonda "300 adresi her 5 dakikada bir taramak hangi seçenekle
mümkün?" sorusuna hesaplı bir cevap.
