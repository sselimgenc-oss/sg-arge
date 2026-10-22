# Argon görev paketi: T11b BIST 30 değişiklikleri 2015-2019 (küçültülmüş)

Bu mesajı olduğu gibi Argon'a yapıştır. Cevabı `T11b_bist30_degisiklik.csv` adıyla `argon/` klasörüne yükle.

---

Sen bir veri toplama işçisisin (rol adı: Argon). Takım lideri Claude Opus. Çıktın satır satır denetlenecek.

**Tam 30'luk listeleri arama.** Borsa İstanbul'un dönemsel duyuruları yalnızca değişiklikleri verir: "BIST 30 ENDEKSİ — ALINACAK PAYLAR / ÇIKARILACAK PAYLAR". Senden yalnızca bu tabloları istiyoruz. Tam listeleri lider, 2020 listesinden geriye doğru hesaplayacak.

**Dönemler (20 adet):** 2015 Ocak, Nisan, Temmuz, Ekim; aynı şekilde 2016, 2017, 2018 ve 2019. Ayrıca **2020 Ocak** duyurusu da gerekli; geriye hesap oradan başlıyor.

**Nerede:**
- borsaistanbul.com/duyuru/... sayfaları. Örnek: 2017 birinci üç aylık dönem duyurusu `https://www.borsaistanbul.com/duyuru/11511/...`; diğer yılların numaraları bunun çevresinde.
- Başlık kalıbı: "<YIL> yılı <birinci|ikinci|üçüncü|dördüncü> üç aylık dönemi için BIST pay endeksleri kapsamında yer alacak paylarda değişiklik yapılmıştır".
- Bulamazsan aynı başlıkla KAP (kap.org.tr) bildirimine bak.
- Sayfada yalnız **BIST 30 ENDEKSİ** tablosunu oku. BIST 50/100 tablolarını karıştırma.

**CSV biçimi** (her satır bir değişiklik):
```
donem_baslangic,islem,hisse_kodu,kaynak_url
2017-01-02,alinacak,DOHOL,https://www.borsaistanbul.com/duyuru/11511/...
2017-01-02,cikarilacak,DOAS,https://www.borsaistanbul.com/duyuru/11511/...
2017-04-03,degisiklik_yok,,https://...
2016-07-01,bulunamadi,,
```
- `islem`: alinacak | cikarilacak | degisiklik_yok | bulunamadi. Yedek paylar YAZILMAZ.
- `donem_baslangic`: dönemin ilk işlem günü (2017-01-02 gibi). Emin değilsen ayın ilk iş günü.
- Uydurma yok; her satırın kaynağı olmalı.
- En sona şu satırı ekle: `# ozet: donem=N, bulunamayan=N`

Not: Tarayıcı izni sorulursa onay verilebilir; site çerez penceresinde "Tümünü reddet" yeterli. Giriş yapma, form doldurma, kişisel veri girme yok.
