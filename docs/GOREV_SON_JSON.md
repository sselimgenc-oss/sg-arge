# Görev (Codex) — veri dalına `son.json` işaretçisi

**Neden.** sg-pano ofisi "en son seçim / en son kapı" bilgisini şimdi GitHub API'sinden (`git/trees/copytrade-kapi?recursive=1`) okuyor.
Kimliksiz API saatte 60 istekle sınırlı; paylaşılan IP'de ya da çok sekmede sınıra takılır ve ofis "veri okunamadı" der. Ağaç ayrıca
büyüyünce `truncated` döner. Çözüm: yayıncı, her yayında veri dalının köküne sabit adlı küçük bir işaretçi yazar; ofis yalnız ham
dosyayı (`raw.githubusercontent.com`, API sayacına girmez) okur. **Yayıncı tarafı bu görevdir; sg-pano tarafı yayıncı hazır olunca ayrı PR.**

## Dosya: `son.json` (dal `copytrade-kapi`, kök)
```json
{
  "surum": 1,
  "uretildi": "2026-10-29T06:12:00Z",
  "secim": { "klasor": "2026-10-27-v1.3", "yol": "secim/2026-10-27-v1.3/secim.json", "kapi_tarihi": "2026-10-27" },
  "kapi":  { "tarih": "2026-10-28", "yol": "copytrade/kapi/2026-10-28/durum.json" },
  "kesif": { "yol": "kesif/kesif.json" }
}
```
- Yollar dal köküne göredir; pano `https://raw.githubusercontent.com/sselimgenc-oss/sg-arge/copytrade-kapi/<yol>` adresini kurar.
- `secim.klasor`: `secim/<klasör>/secim.json` yollarının klasör adına göre sıralanmış **en sonu** (`<tarih>-v1.3`, aynı günkü `<tarih>`'ten sonra gelir; panonun şimdiki kuralıyla aynı).
- `kapi`: `copytrade/kapi/<tarih>/durum.json` yollarının en son tarihi. (Seçimin dayandığı kapı `secim.kapi_tarihi`'dir; pano ikisini de ayrı gösterir.)
- Bir alan henüz yoksa **alan hiç yazılmaz** (null yazılmaz); pano eksik alanı "yok" sayar. Yeni alan eklemek sürümü değiştirmez, alan silmek ya da anlamını değiştirmek `surum`'u artırır.

## Yayıncı kuralları
1. **Sonda ve aynı commit'te:** `son.json`, işaret ettiği dosyalarla **aynı commit'te** yazılır; hedefi olmayan işaretçi (dangling) yazılmaz. İşaretçi her zaman var olan dosyaya gider.
2. **Her iş yalnız kendi alanını günceller:** kapı iş akışı `kapi`'yi, seçim iş akışı `secim`'i, keşif/tarama `kesif`'i; diğer alanlar okunup korunur (oku-değiştir-yaz). `uretildi` her yazışta güncellenir.
3. **Eşzamanlılık:** iş akışları veri dalına yazarken `concurrency: group: copytrade-kapi-veri` kullanır; iki iş aynı anda `son.json`'ı ezemez.
4. **Geriye gidiş yok:** yeni değer, mevcut değerden eski tarihliyse (örn. eski bir koşunun yeniden çalışması) alan değişmez.
5. **Kendini doğrula:** yayın adımının sonunda `son.json` şeması ve "işaret edilen her yol dalda var mı" denetimi çalışır; başarısızsa iş kırmızı olur (sessiz bozulma yok).
6. **Boş sayı yok / uydurma yok:** yayıncı yalnız dalda gerçekten bulunan dosyaları işaret eder; tarih bulunamazsa alan eksik kalır.

## Tüketici sözleşmesi (sg-pano, sonraki PR)
- Önce `son.json` (ham dosya). 200 ise içindeki yollar okunur; `ağaç` çağrısı yapılmaz.
- `son.json` 404 ise (geçiş dönemi) bugünkü ağaç yöntemine düşülür ve ofis bunu tek satırla belirtir; yayıncı hazır olunca ağaç yolu kaldırılır.
- Şema dışı içerik (`surum` ≠ 1, yol `..` ya da `.json` ile bitmiyor, yol izinli desen dışında) → açık hata, sahte veri yok.
- Ham dosya önbelleği (~5 dk) kabul edilir; panodaki "VERİ ESKİ" eşiği (7 gün) bundan etkilenmez.

## Kabul
- Tam test paketi yeşil; yeni testler: şema doğrulama; "dangling yok"; iki işin art arda yazması diğerinin alanını korur; eski tarihli koşu alanı geriye almaz; `secim` klasör sıralaması (`<tarih>` < `<tarih>-v1.3`).
- Yerelde gerçek dal klonunda bir yayın denemesi: `son.json` üretilir, işaret ettiği her dosya vardır (çıktı PR açıklamasında).
- main'e doğrudan push yok; PR açılır.
