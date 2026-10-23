# 011: T35 parti 2 değerlendirmesi (lider)

Teslimler geldikçe güncellenir. Parti 1: `tartisma/010_t35_ilk_parti_degerlendirme.md`.

## ChatGPT kolu (Avrupa + Amerika): `arastirma/chatgpt_p2.csv`
Codex bulut ortamı iki kez açılmadı. Bu yüzden kol `argon/PAKET_T35P2_chatgpt_avrupa_amerika.md` paketiyle normal ChatGPT sohbetinde yürütüldü.

**Teslim:** 10 satır. Lider denetiminden sonra **9 satır**.

### Lider düzeltmeleri
- **EU-012 çıkarıldı:** sayısal metrik yok; yalnız "Sharpe S&P 500'ü aştı" deniyor. Kapı 1'den döner.
- **EU-013 satırında sütun kayması** düzeltildi (bir alan sağa kaymıştı). Ayrıca `maliyet_dahil: evet` iken bayrakta `maliyet_yok` yazıyordu; çelişki giderildi.
- **US-010** ayrı bir strateji değil, US-005..009'un birleşik kitabı: `motor_notu: portfoy`, `kural_tam: kismen`.

### İçerik değerlendirmesi
- **Avrupa forumları beklendiği gibi zayıf çıktı.** wallstreet-online, ABC Bourse, X-Trader, Investire ve FinanzaOnline'da rakamlı strateji bulunamadı; Trade2Win 403 verdi. Yalnız **smart-lab.ru** verdi. Sonuç: Avrupa'da açık, rakamlı strateji paylaşım kültürü zayıf; Rusya istisna.
- **EU-011:** 65 yıl, ama Sharpe ~0,1. Kârlılık iddiası zayıf; işaretlendi.
- **EU-013 (Algebra, Capitalizer):** 2024-07 → 2026-05, net %43,5, MDD %21, Sharpe 1,32; MOEX endeksi aynı dönemde -%2,4. Kural yok, otomatik takip ürünü. Platform takipli olduğu için rakamın değeri var, ama test edilemez.
- **EU-015 (OFZ tahvil grid):** CAGR %31, Sharpe 2,79, ~2 yıl. Grid stratejisi, tarihsel veri "talep üzerine". Yüksek risk profili.
- **US-005..010 (STS Futures, NQ):** 2011-2026, 300-1.650 işlem, ayrıntılı istatistik. Ama **ticari satıcı** ("the combined book is the product"), kurallar kısmen, maliyet yok. Tümüne `ticari_satici` bayrağı eklendi.
  - En şeffaf olanı **US-009 (NQ overnight):** 796 işlem, PF 1,57, Sharpe 1,06, MDD özkaynak eğrisinin %10,3'ü.
  - US-006 (NQ ORB, 09:30-09:45) Faz 1'deki ORB ailesiyle akraba, ama piyasa NQ vadeli.

### Doğrulama
Lider oturumu smart-lab.ru ve stsfutures.com'u açamıyor. Kullanıcıdan 2 örneklem kontrolü isteniyor:
- **EU-015:** https://smart-lab.ru/blog/1310045.php → CAGR %31, MDD -%11, Sharpe 2,79.
- **US-009:** https://stsfutures.com/learn/nq-overnight-strategy-backtest → 796 işlem, PF 1,57, $194.333 net, MDD $20.073.
