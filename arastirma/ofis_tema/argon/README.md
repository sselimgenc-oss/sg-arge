# Ofis İzometrik Canlı Haritası (`ofis_izometrik.html`)

Şirket ofisinin izometrik kesit görünümü (1536×1024) üzerinde canlı izleme verilerini gösteren, telefon öncelikli (mobile-first), sıfır bağımlılıklı tek dosya web uygulaması.

## 1. Dosya Yapısı

Aynı klasörde şu dosyalar yer alır:

- `ofis_izometrik.html` — Tüm HTML, CSS ve JavaScript kodunu barındıran tek dosyalık uygulama (önizleme ortamları için gömülü WebP yedeği de içerir; aynı klasörde `ofis_izometrik_referans.webp` bulunduğunda doğrudan yerel dosyayı yükler).
- `ofis_izometrik_referans.webp` — 1536×1024 çözünürlüklü izometrik ofis arka plan görseli.
- `README.md` — Kurulum, koordinat düzenleme, test ve varsayım notları.

## 2. Nasıl Açılır? (Yerel Sunucu Komutu)

Tarayıcıların `fetch()` ve yerel kaynak güvenlik kurallarıyla tam uyumlu çalışması için dosyaların bulunduğu klasörde basit bir yerel HTTP sunucusu başlatılması önerilir:

```bash
# Python 3 ile yerel sunucu başlatma (8000 portunda)
python3 -m http.server 8000
```

Ardından tarayıcıda şu adresleri açabilirsiniz:

- **Normal görünüm:** `http://localhost:8000/ofis_izometrik.html`
- **Bölge hata ayıklama (`?bolge=1`) görünümü:** `http://localhost:8000/ofis_izometrik.html?bolge=1`

Alternatif olarak Node.js kuruluysa `npx serve .` komutuyla da çalıştırılabilir.

## 3. `ODALAR` Koordinatları Nasıl Düzeltilir?

Tüm oda sınırları ve rozet konumları `ofis_izometrik.html` içindeki `<script>` bölümünün en başında yer alan `ODALAR` nesnesinde **0 ile 1 arasında oranlı (`x`, `y`)** koordinatlarla tanımlanmıştır (`(0,0)` sol üst köşe, `(1,1)` sağ alt köşe):

```javascript
const ODALAR = window.ODALAR = {
  finans: {
    ad: "Finans",
    rozetGoster: true,
    sadeEtiket: false,
    rozetKonum: { x: 0.190, y: 0.082 },
    odak: { x: 0.200, y: 0.155, olcek: 2.35 },
    renk: "rgba(59, 130, 246, 0.42)",
    cizgi: "#60a5fa",
    poligon: [
      { x: 0.055, y: 0.105 },
      { x: 0.230, y: 0.012 },
      // ...
    ]
  },
  // ...
};
```

Koordinatları düzenlemek için:

1. Sayfayı `?bolge=1` parametresiyle açın (`ofis_izometrik.html?bolge=1`) veya üst çubuktaki **Bölgeler** düğmesine dokunun.
2. Yarı saydam renkli çokgenleri ve köşe noktalarını görsel üzerindeki duvar/zemin sınırlarıyla karşılaştırın.
3. İlgili odanın `poligon` dizisindeki `{ x, y }` değerlerini, rozet yerini değiştirmek için `rozetKonum: { x, y }` değerini, tıklama sonrası yakınlaşma merkezini ayarlamak için `odak: { x, y, olcek }` değerini güncelleyip sayfayı yenileyin.

## 4. Veri Kaynağı ve Varsayımlar

Veri şu adresten canlı olarak okunur (sahte veri üretilmez):
`https://raw.githubusercontent.com/sselimgenc-oss/sg-arge/copytrade-izleme/izleme/durum.json`

Uygulamada belirsiz alanlar için uydurma veri üretilmemiş, aşağıdaki **varsayımlar** uygulanmıştır:

- **Finans başlangıç kasası (`başlangıç = trader sayısı × 1000`):** `traderlar` dizisinde `kol === "oda"` olan trader sayısı esas alınarak `odaTraderSayisi * 1000` USD olarak hesaplanmıştır. Kasa toplamı için `kol === "oda"` olan traderların sayısal `sanal_kopya.bakiye_usd` değerleri toplanır; bu alan yoksa rozet `"veri yok"` gösterir.
- **Risk odası sağlık ışıkları:** Öncelikle aktif takip kolu olan `kol === "oda"` traderlarının `saglik.isik` (veya doğrudan string `saglik`) değerleri sayılır; eğer `oda` kolunda kayıt yoksa tüm `traderlar` dizisine bakılır. En kötü ışık önceliği `kirmizi (🔴) > sari (🟡) > yesil (🟢)` şeklindedir. Risk detay panelinde hem `oda` kolu hem tüm kollar ayrı ayrı gösterilir.
- **Kalabalık uyarısı (`kalabalik` alanı):** Şemada `{...uyarı alanları...}` genel olarak belirtildiği için sahte alt alan adı uydurulmamıştır. `kalabalik` nesnesi içindeki boolean (`uyari`, `var`, `aktif`, `alarm`, `risk`), pozitif sayısal (`uyari_sayisi`, `sayi`, `adet`), uyarı metni (`"uyari"`, `"sari"`, `"kirmizi"`, `"yuksek"`, `"kritik"`) veya dolu dizi alanları kontrol edilerek uyarı varsa rozete `⚠` eklenir ve detay panelinde `kalabalik` nesnesinin tüm mevcut anahtar-değer çiftleri olduğu gibi listelenir.
- **Sanal getiri (`sanal_kopya.getiri`):** `durum.json` içerisindeki sayısal `getiri` değerinin yüzde cinsinden (ör. `12.4` → `+%12,4`) olduğu varsayılmıştır. Alan mevcut değilse tabloda `"veri yok"` yazılır.
- **Makam haftası (`t0 = 2026-10-29`):** `2026-10-29T00:00:00+03:00` tarihinden güncel zamana kadar geçen `tam hafta + 1` formülüyle hesaplanır.

## 5. Test Edilen Cihazlar ve Ekran Genişlikleri

Headless Chromium (Selenium CDP) ile aşağıdaki ekran genişlikleri ve modlar doğrulanmıştır:

- **360×800 px** (Küçük ekranlı Android telefonlar)
- **390×844 px** (iPhone 12 / 13 / 14 / 15 standart genişliği — rozetlerin taşmadığı, çakışmadığı ve tüm dokunma alanlarının `≥ 44×44 px` olduğu doğrulandı)
- **768×1024 px** (Tablet dikey görünüm)
- **1280×800 px** (Masaüstü geniş ekran görünümü)

## 6. Bilinen Eksikler ve Kısıtlar

- **Çok küçük ekranlarda (< 340 px) rozet yoğunluğu:** 390 px ve üzerinde rozetler çakışmadan okunur; ancak 320 px gibi çok dar ekranlarda üst kattaki dört oda yan yana dizildiği için rozet metinleri birbirine yaklaşabilir (odaya yakınlaşıldığında rahatça ayrışır).
- **`file://` protokolü kısıtları:** Sayfa doğrudan çift tıklanarak (`file://`) açıldığında tarayıcıların CORS politikası uzak JSON (`raw.githubusercontent.com`) okumasına izin verir; ancak bazı katı tarayıcı güvenlik ayarlarında yerel sunucu (`python3 -m http.server`) kullanılması daha kararlıdır.
