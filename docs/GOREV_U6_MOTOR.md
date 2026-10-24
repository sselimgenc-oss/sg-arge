# U6-MOTOR: Piramit ve çok seviyeli kısmi çıkış desteği (Codex)

**Karar:** kullanıcı, 2026-10-24: "205'in hepsi test edilsin". **Sahip:** Codex. **Denetim:** lider.

## Neden
U6 parti 1'de 52 scriptten 23'ü "Doğrulanamaz (çeviri)" çıktı. Bunların yaklaşık 15'i yalnız üç motor eksiğinden kaynaklanıyor:
- **piramit:** pozisyon açıkken aynı yönde ek giriş (`pyramiding = N`);
- **çok seviyeli kısmi çıkış:** `strategy.exit(qty_percent=…)` ile birden çok hedefte pozisyonun bir kısmını kapatma;
- **başa baş (break-even) stopu:** fiyat belirli bir R'ye ulaşınca stopun giriş fiyatına taşınması.

Bu yapılar desteklenirse kalan partilerde de benzer kartlar çevrilebilir.

## Ön kayıt eki (`docs/GOREV_U6.md` bölüm 2 "Çevrilemeyen" maddesi)
Bu üç yapı **motor desteklendikten sonra** çevrilebilir sayılır. Bu yapıları içeren hiçbir scriptin sonucu görülmedi; ek, sonuçtan önce yapılıyor. Kalan Doğrulanamaz nedenleri değişmez: pozisyon ortalama fiyatına ya da açık kâra bağlı **serbest biçimli** çok aşamalı yönetim, dış veri, Pine içi ML, tick bazlı izleyen stop.

## Yapılacaklar
1. **Piramit** (kart alanı `piramit: {en_cok: N}`, varsayılan 0 = bugünkü davranış):
   - Pozisyon açıkken gelen yeni giriş sinyali, ek sayısı N'yi aşmadıkça ek birim açar.
   - Her ek birim kendi stop mesafesiyle EVRENSEL boyut kuralına göre boyutlanır. **Toplam açık risk sınırı (%2) bütün birimleri kapsar.**
   - Çıkış sinyali bütün birimleri kapatır. Stop: her birimin kendi stopu.
2. **Çok seviyeli kısmi çıkış** (kart alanı `kademeli_cikis: [{tetik: <ifade>, oran: <0-1>}, …]`):
   - Seviyeler sırayla. Oran, **başlangıç** adedinin yüzdesi (Pine `qty_percent` ile aynı).
   - Aynı barda stop ve hedef birlikte değerse önce stop (EVRENSEL kural).
   - Mevcut tek seviyeli `kismi_kar` bozulmadan kalır.
3. **Başa baş stopu** (kart alanı `basa_bas: {tetik_r: x}`): fiyat giriş + x·R'ye ulaşınca stop giriş fiyatına çekilir. Tetik bar içi en yüksek fiyatla değerlendirilir; stop bir sonraki bardan geçerli.
4. `engine/spec.py` şema kontrolü yeni alanları tanır.

## Kabul (zorunlu)
- **Parite:** yeni alanları olmayan kartlarda sonuç birebir aynı. Faz 1 / U4 / U6 parti 1 kartlarının işlem listeleri değişmemeli (CI parite işi + `u4.py --sadece-say` ve örnek bir U4 varyantının IS işlem listesi karşılaştırması).
- **Birim testler:** her yapı için elle hesaplanmış küçük senaryolar:
  - piramit sınırı ve toplam risk sınırı;
  - kademeli çıkışta kalan adet;
  - aynı barda stop önceliği;
  - başa baş stopunun ertesi bardan geçerli olması.
- Gerçek veride bir örnek: parti 1'den piramitli bir kart (ör. `TV-f80Cfpfp`) Sonnet tarafından yeniden çevrildiğinde planın kurulduğunu göster. Kart çevirisi Sonnet'in işi; sen yalnız motorun onu kabul ettiğini test et.
- PR `[U6] motor: piramit + kademeli çıkış + başa baş`. Açıklamada parite kanıtı.

## Yapılmayacak
Short desteği (U2a ayrı iş), kart çevirisi, U6 koşusu, sonuçlara bakıp parametre değişikliği.
