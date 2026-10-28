# Ofis veri şeması (v1, 2026-10-28)

Tek giriş dosyası: `ofis/ornek_durum.json`. Biçim `sg-arge/docs/VERI_SOZLESMESI.md` tarzındadır (`surum`, `uretildi`, `kaynak`).
İlk sürüm **örnek veriyle** çalışır; D yolu Faz 5'te aynı biçim gerçek `durum.json`'dan (ve gölge defteri çıktısından) üretilir.
Sayfa `surum` ≠ 1 ise veriyi reddeder ve "Sahte veri gösterilmiyor" der (sessizce örnek göstermez).

## 1. Kurallar
- **Her sayının yanında zaman damgası ya da n vardır** (`zaman`, `gun_n`, `n`). Ekranda hep birlikte gösterilir.
- **Veri yoksa "bilinmiyor"** yazılır, sıfır değil: alan `null` ya da hiç yok → panel "bilinmiyor" der. Örnekte
  `veri_kalitesi[gecikme].deger = null` bunu gösterir.
- **Örnek veri işareti:** `kaynak` değeri `ornek` ile başlıyorsa üstte `ÖRNEK VERİ` etiketi, ofiste "adresler uydurma" çipi, her kartta `örnek`
  rozeti ve trader ipuçlarında `örnek` görünür. Gerçek veride `kaynak` `hyperliquid` vb. olur ve etiketler kalkar.
- Örnekteki adresler uydurmadır (`0xAAAA…0031` biçimi); gerçek adres yoktur.
- Para birimi USD; oranlar yüzde olarak (`kz_yuzde: 2.1` = %2,1), kasa payları 0–1 arası.
- Zamanlar ISO-8601 UTC (`2026-10-28T14:20:00Z`); ekranda yerel saat (SS:DD).

## 2. Üst düzey alanlar
```json
{
  "surum": 1,
  "uretildi": "2026-10-28T14:20:00Z",
  "kaynak": "ornek (sahte veri; adresler gerçek değil)",
  "vardiya": {"gunduz_baslangic": "07:00", "aksam_baslangic": "19:00"},
  "cipler": {"golge": "GÖLGE · SİM", "telegram": "AÇIK"},
  "kasa": {...}, "ozet": {...}, "katlar": {...}, "traderlar": [...],
  "acik_islemler": [...], "kapananlar": [...], "kohort_kontrol": {...},
  "veri_kalitesi": [...], "risk": {...}, "telegram": {...}, "tarama": {...},
  "olaylar": [...], "akis_suresi_sn": 156
}
```
Vardiya adı ve gün ışığı **gerçek saate** göre sayfada hesaplanır (`vardiya` yalnız sınırları verir); `?saat=SS:DD` ile denenebilir.

## 3. Alanlar
**`kasa`** (gölge kasası, sanal): `deger_usd`, `baslangic_usd`, `zaman`, `gun_n` (kaç günlük veri), `egri: [["2026-10-20", 1000.0], …]` günlük değer.
`egri` 5 günden kısaysa kart ve Finans duvar ekranı "veri birikiyor" der.

**`ozet`**: `islem_basi_usd` (kural), `bugun_kz_usd`, `bugun_acilan_n`, `bugun_kapanan_n`, `zaman`.

**`katlar`** (huni): her biri `{n, masa, zaman}`; `oda` ayrıca `kapasite`. `n` gerçek sayıdır; `masa` ofiste çizilen koltuk sayısıdır
(en yüksek puanlı `masa` adres figür olur, kalanı yalnız sayıdır — ofis ölçeklenmez). `havuz` → Lab, `aday` → Aday, `oda` → Oda, `kontrol` → Kontrol grubu.

**`traderlar[]`**: `id`, `adres` (kısa), `kat` (`lab|aday|oda|kontrol|disari`), `kol` (`havuz|kohort|kontrol`), `tarz` (`intraday|swing`),
`etiket` (etiketlenme tarihi), `gun` (n), `islem_n` (n), `puan` (bilgi sütunu; karar vermez), `ornek: true`.
Yalnız figür çizilecek adresler listelenir (`masa` sınırı kadar).

**`acik_islemler[]`**: `id`, `trader`, `coin`, `yon` (`long|short`), `kaldirac`, `yas_dk` (veri üretildiğinde yaşı), `kz_usd`, `kz_yuzde`,
`lik_uzaklik` (likidasyona uzaklık, %), `teminat_usd`. Süre sütunu `yas_dk` + sayfada geçen süreyle akar.

**`kapananlar[]`**: `coin`, `yon`, `neden` (`trader_kapatti|zarar_kesme|sure`), `sure_dk`, `kz_usd`, `kz_yuzde`, `trader`. En yeni üstte.

**`kohort_kontrol`**: `hafta`, `hafta_toplam`, `performans_kilitli` (true ise **hiçbir performans sayısı gösterilmez**), `kollar: [{ad, n}]`
(kohort / kontrol / taban / elle liste), `onkayit` (metin), `zaman`.

**`veri_kalitesi[]`**: `anahtar` (`tarama|lab|arsiv|denetim|gecikme|mum`; ilk dördü ofiste ilgili odaya bağlanır), `ad`, `durum`
(`tamam|bayat|uyari|bilinmiyor`), `deger` (metin ya da `null`), `zaman` (ya da `null`).

**`risk`**: `zaman`, `tavanlar: [{anahtar, ad, kullanim, tavan, birim}]`; doluluk = `kullanim / tavan`; ≥ 1 → "TAVAN DOLU" ve Risk odasında alarm.
Eşikler yalnız `kurallar.yaml`'dadır; bu dosya yalnız okur.

**`telegram`**: `bugun_n`, `son: [metin]`, `zaman`.  **`tarama`**: `puanlar` (Tarama duvar ekranındaki sıralama çubukları), `zaman`.

## 4. Olay akışı (`olaylar[]`)
Her olay: `t` (örnek akışta saniye; gerçek veride `zaman` ISO), `tur`, `oda` (vurgulanacak oda) ve türe özgü alanlar. Türler, animasyon eşlemesi ve
panel etkisi **`OLAYLAR.md`**'dedir. Örnek akış `akis_suresi_sn` sonunda başa sarar (sayılar ilk veriye döner; kişiler başlangıç koltuklarına döndüğü
için akış döngü içinde tutarlıdır). Gerçek veride akış yeniden oynatılmaz: yeni olay geldikçe aynı işleyiciler çalışır.

## 5. Gerçek veriye bağlama (Faz 5 taslağı)
| Ofis alanı | Kaynak |
|---|---|
| `traderlar`, `acik_islemler`, `kapananlar`, `olaylar` | `izleme/durum.json` (v1.4) ve gölge defteri (`copytrade/golge.py`); olay `id`'leri kalıcıdır |
| `kasa`, `ozet` | Finans: gölge defterinin sanal kasası (`kurallar.yaml` işlem başı kural) |
| `katlar`, `kohort_kontrol` | `copytrade/kollar.py` etiketleri; kat geçiş kuralları ön kayıttan |
| `veri_kalitesi`, `risk` | Denetçi (akıl sağlığı kapısı, sağlama, gecikme zinciri) ve Risk modülü |
| `telegram` | Worker `/durum` ve bildirim günlüğü |
Eksik kaynak → alan `null` → ekranda "bilinmiyor"; sayfa hiçbir zaman eksiği sıfırla doldurmaz.

## 6. Adres parametreleri (denemek için)
`?durum=URL` başka veri dosyası · `?saat=SS:DD` gün ışığı · `?hiz=2` örnek akış hızı · `?etiket=0` trader etiketlerini gizler ·
`?hareket=0` hareketi kapatır (`prefers-reduced-motion` açıkken zaten kapalıdır) · `?oda=lab` açılışta odaya yaklaşır · `?perf=1` kare süresi.
