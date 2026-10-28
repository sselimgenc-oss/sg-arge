# SG Pano · Copy trade

`sg-arge` copy trade izleme panosu. **Salt okunur; gerçek emir, para hareketi ve aracı kurum bağlantısı yok.**

- Yayın: GitHub Pages (`main` / kök). Tek sayfa (`index.html`), erişim yöntemi değişmedi (ek hesap/şifre yok).
- Sekmeler (sürüm `pano-sade`): **Özet** (`#ozet`: hafta x/12, oda doluluğu, kol başına trader, veri tazeliği, son 5 olay; altında kapalı bölümler: tüm akış, açık işlemler, "Kararlarım değer kattı mı?") · **Trader'lar** (`#traderlar`: kol filtresi + kartlar; trader sayfası `#trader/<adres>`) · **Huni** (`#huni`: havuz → aday → oda, son tarama, aday listesi) · **Ayarlar** (`#ayarlar`: tutar hesaplayıcı, sözlük). Sayfa Özet ile açılır. Eski adresler yönlenir: `#ct/<id>`, `#kesif/<adres>` → trader sayfası; `#ctakis`, `#ctistat` → Özet; `#kesif` → Huni.
- Telefon öncelikli, kısa Türkçe; her teknik terimin yanında "?" (dokununca açıklama; tam liste Ayarlar → Sözlük). "Araştırma / sanal, yatırım tavsiyesi değil" ibaresi sabit üst bantta her sekmede görünür.
- **Performans körlüğü (ön kayıt):** canlı gölge süresince "sanal kopya (hepsi)", kol toplamları ve kohort ↔ kontrol kıyası gösterilmez; yerine "kilitli · hafta x/12" yazar. Tek tek işlem K/Z'si görünür. Kâr/zarar rengi, K/Z'ye göre sıralama, rozet ve seri yok.
- **Veride isteğe bağlı yeni alanlar** (yoksa "bilinmiyor" yazar, çökmez): trader başına `kol` (`oda|aday|kontrol|taban|elle`), `neden_secildi`, `kirmizi_bayraklar[]` (yoksa `saglik` ışığı/nedenleri); üst düzey `golge: {hafta, hafta_toplam (varsayılan 12), oda_kapasite, oda_n}`; keşifte `havuz`, `aday_sayisi` (yoksa `islenen` ve aday sayısı).
- Testler: `node test/pano.test.js` (ana pano, Playwright; ağ yakalanır, yalnız örnek veri).
- Tanım: `sg-arge/docs/PANO_COPYTRADE.md`; veri biçimi: `sg-arge/docs/VERI_SOZLESMESI.md` (v1.1, `surum` 1; başka sürüm reddedilir).
- Sayfa açıkken her 5 dakikada veriyi yeniden okur; üstteki **Yenile** düğmesi hemen okur.
- Sahte veri yok: veri okunamazsa sayfa hata gösterir; olmayan alanlar "veri yok" der.
- Paper/strateji araştırması kapandı; ona ait pano, sekmeler ve `data.json` kaldırıldı.

## Ofis (animasyonlu görünüm)
`ofis/` altında ayrı bir sayfa: izometrik piksel sanatı ofis + sol pano. **İlk sürüm örnek veriyle çalışır** (`ofis/ornek_durum.json`, ofiste
`örnek veri` şeridi); gerçek `durum.json`'a bağlanması D yolu Faz 5'tir. Derleme yok, kütüphane yok, görsel varlık yok (hepsi kodla çizilir).
- **Sürüm 2 (ilk 5 iş):** odaya tıklayınca iç görünüm (`#oda/lab`, Kapı, Arşiv…), ortak bilgi kutusu (masaüstü panel / telefon çekmece), `replikler.json`, iletişim işaretleri (zarf/not/ok), oda ve çalışan adlarını değiştirme (`kadro.json`). Testler: `node ofis/test/replik.test.js`, `node ofis/test/ui.test.js` (Playwright).
- **Sürüm 2b:** olay çekmecesi (filtre, kameraya git), veriden türeyen bayatlık (`esik_dk`, sis, "VERİ ESKİ"), oda iç ayrıntıları, günlük özet, isteğe bağlı ses (varsayılan kapalı).
- Düzen: ortasında avlu ve havuzlu bahçe olan iki kanatlı bina; sol dikey menü (Bina / Hat / Destek), durum plakaları (Adım 0 özgünleştirmesi, `ofis/LISANSLAR.md`).
- **Ofis paneli (`claude/ofis-panel`):** masaüstünde kart sütunu varsayılan **gizli**; ofis tuvali tüm genişliği kullanır. Sol menüde bir öğeye tıklayınca kamera o odaya gider ve ilgili kart(lar) ofisin üstünde açılır panel olarak gelir (eşleme tek tablo: `main.js` → `PANEL_ESLE`; tabloda olmayan odalar oda bilgisi kartını açar). Kapatma: ×, Esc, boş alana tıklama, aynı menüye ikinci tıklama, "Tüm ofis". Günlük özet ofisin üst kenarında tek satırlık şerit (tıklayınca ayrıntı paneli). ◧ düğmesi klasik kart sütununu geri getirir. Telefon düzeni değişmedi (kartlar sayfada, alttan çekmece).
- Sayfa: `ofis/` (GitHub Pages'te `…/ofis/`). Belgeler: `ofis/SEMA.md` (veri), `ofis/OLAYLAR.md` (olay → animasyon), `ofis/LISANSLAR.md`.
- Deneme parametreleri: `?saat=23:14` (gün ışığı), `?hiz=2`, `?etiket=0`, `?hareket=0`, `?perf=1` (ayrıntı `ofis/SEMA.md` §6).
- Salt okunur; gerçek emir, para ve aracı kurum bağlantısı yok.

## Veri kaynağı
`index.html` içindeki iki sabit, canlı veriyi gösterir (sg-arge `copytrade-izleme` dalı, ham GitHub adresi):
- `CT_KAYNAK` = `…/copytrade-izleme/izleme/durum.json` (saatte bir güncellenir).
- `CT_KARAR` = `…/copytrade-izleme/izleme/kararlar.jsonl`. Dosya yoksa (404) "henüz karar kaydı yok" sayılır; tarayıcı bu 404'ü konsola yine de yazar, sayfa hata göstermez.

Eski veri uyarısı 90 dakikadan sonra çıkar (`CT_ESKI_DK`). "ÖRNEK VERİ" etiketi yalnız `kaynak` alanı `ornek` ile başlıyorsa görünür.
`izleme/ornek_durum.json`: sg-arge `main`'deki sabit örneğin kopyası (sahte veri); test için `CT_KAYNAK` geçici olarak `./izleme/ornek_durum.json` yapılabilir.

Keşif kaynağı `index.html` içindeki `KESIF_KAYNAK` sabitidir. GitHub API ile `copytrade-kapi` dalındaki en yeni tarih klasörünü bulur, içinde `kesif.json` yoksa önceki tarihi dener ve ham dosyayı okur. Canlı kaynak yoksa görünür uyarıyla yerel örneğe düşer. Keşif'teki “Adresi kopyala” düğmesi yalnız cüzdan adresini panoya yazar; emir göndermez.

## Dosyalar
| Dosya | Görev |
|---|---|
| `index.html` | Pano (tek sayfa). |
| `test/` | Ana pano testi (`pano.test.js`) ve ortak yardımcı (`pano_yardim.js`). |
| `docs/pano_sade/` | Önce / sonra ekran görüntüleri ve kabul notu. |
| `izleme/` | Test için sabit örnek durum (sahte veri); canlıda kullanılmaz. |
| `kesif/` | Keşif sekmesi için v1 şemasına uygun sahte aday verisi. |
| `vendor/` | Sabit sürümlü kütüphaneler: Lucide 0.460.0 (ikonlar, ISC), Tailwind 3.4.17 ile derlenmiş CSS (MIT). Dış CDN kullanılmaz. |

## Tailwind CSS'i yeniden derleme (index.html'de yeni sınıf kullanılırsa)
```bash
npm i tailwindcss@3.4.17
printf '@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' > in.css
echo "module.exports = { darkMode: 'class', content: ['index.html'], theme: { extend: {} } };" > tailwind.config.js
npx tailwindcss -c tailwind.config.js -i in.css -o vendor/tailwind.3.4.17.css --minify
```
