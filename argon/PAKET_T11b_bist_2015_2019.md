# Argon görev paketi: T11b BIST 30 bileşenleri 2015-2019 (ikinci deneme)

Bu mesajı olduğu gibi Argon'a yapıştır. Cevabı `T11b_bist30_2015_2019.csv` adıyla `argon/` klasörüne yükle.

---

Sen bir veri toplama işçisisin (rol adı: Argon). Takım lideri Claude Opus. Çıktın satır satır denetlenecek.

T11'de BIST 30'un 2020-2026 dönemlerini buldun, teşekkürler. 2015-2019 arasındaki 20 dönem "bulunamadi" kaldı. Bu dönemleri farklı yollarla bir kez daha ara:

- **KAP arşivi:** "BIST Pay Endeksleri Dönemsel Değişiklikleri" ya da "Endeks Dönemsel Değişiklikleri" başlıklı Borsa İstanbul bildirimleri. Gönderen Borsa İstanbul A.Ş., yıllar 2014-12 ile 2019-12 arası.
- **Borsa İstanbul duyuru arşivi:** Eski duyuru numaraları; 2020 duyuruları 12557 civarındaydı, 2015-2019 duyuruları daha küçük numaralarda olmalı.
- **Aracı kurum günlük bültenleri:** Gedik, Oyak, İş Yatırım, Garanti BBVA Yatırım, Deniz Yatırım. Örnek arama: "BIST 30 endeksine dahil edilecek" ya da "BIST 30'dan çıkarılacak" + yıl. Bir dönemin listesini, önceki dönemin listesine giren/çıkan değişikliklerini uygulayarak çıkarabilirsin. Bu durumda `not` sütununa "degisiklikten turetildi: <kaynak>" yaz.
- **Wayback Machine (web.archive.org):** borsaistanbul.com endeks sayfalarının eski kopyaları.

Kurallar ve CSV biçimi T11 ile aynı:

```
donem_baslangic,hisse_kodu,kaynak_url,not
```

- Her dönem için tam 30 satır. Bulamadığın dönemi tek satırla `bulunamadi` olarak bırak.
- Uydurma yok; her satırın kaynağı olmalı. Hisse kodları bugünkü haliyle yazılır.
- En sona şu satırı ekle: `# ozet: bist_donem=N, bist_bulunamayan=N`
