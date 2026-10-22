# T31 — 13 kartın kaynağını oku (eski Argon T19; sahibi: claude-moderator / Sonnet)

## Neden
Kullanıcı kararı (2026-10-22): Argon'un limiti ekran görüntüsü tabanlı gezinmeyle hızla tükeniyor. Bu yüzden ikinci talimata kadar **Argon kullanılmayacak**; T19 Sonnet'e geçti. Paket: `argon/PAKET_T19_kaynak.md`. Kartlar ve URL'ler orada; kurallar aynen geçerli: uydurma yok, giriş yapma ve form doldurma yok, kod varsa aynen kopyalanır.

T21'de bu sayfaların düz WebFetch ile okunamadığını biliyoruz. Bu sefer **alternatif yolları** dene:
- **jesse.trade (O2-017, O2-019):** Stratejilerin kodu genelde GitHub'da (jesse-ai organizasyonu veya yazarın deposu). Depoyu bul ve `raw.githubusercontent.com` üzerinden oku.
- **mql5.com/en/code/78275 (A2-011):** Kod tabanındaki dosyalar çoğu zaman doğrudan indirme bağlantısıyla (`/en/code/download/...`) ya da sayfa kaynağında bulunur. Giriş isteyen yol yasak.
- **prorealcode.com (O1-045, O1-050):** Kod sayfanın HTML'inde `<pre>` bloğunda olabilir; ham HTML'i oku.
- **algokutuphanesi.com (O1-006/008/009/010/013):** Ham HTML ya da sitenin JSON uçları denenebilir. Olmazsa **web.archive.org** kopyası denenebilir. OTT/MOTT için Anıl Özekşi'nin kamuya açık formülleri (TradingView OTT betiği) yalnız kartın tanımıyla **birebir** örtüşüyorsa kullanılır; örtüşmüyorsa kullanılmaz.
- **usethinkscript.com (M003), financial-hacker.com (A6-014), wisestocktrader.com (O1-055):** Ham HTML ya da web.archive.org kopyası.

## İstenenler
1. Her kart için `argon/PAKET_T19_kaynak.md`'deki şablonla `docs/kaynak/T31_kaynaklar.md` dosyasını yaz: durum, kaynak_url (archive kullanıldıysa o URL), kurallar, kod.
2. Okunabilen kartları T20/T21 yöntemiyle motora taşı: `ozel_kod: false`, gerekirse ilkel ekle (D11 tarzı, look-ahead testli). Taşınanların `belirsiz` notunu güncelle.
3. Okunamayanlar `ozel_kod` kalır. `belirsiz`e şunu yaz: `T31: kaynak okunamadı (<denenen yollar>)`. Sonuçta **Doğrulanamaz** olurlar; tahminle doldurma.
4. `INDEKS.csv`'yi yeniden üret ve `engine.spec --kontrol`'ü hatasız geçir. Yeni ilkeller için testler yaz.

Sıra: **T30 bittikten sonra** başla (her ajanda tek iş kuralı).

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. Gerçek taramayı lider yapar.
