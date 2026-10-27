# SG Pano · Copy trade

`sg-arge` copy trade izleme panosu. **Salt okunur; gerçek emir, para hareketi ve aracı kurum bağlantısı yok.**

- Yayın: GitHub Pages (`main` / kök). Tek sayfa (`index.html`), erişim yöntemi değişmedi (ek hesap/şifre yok).
- Sekmeler: **Copy trade** (kartlar + ayrıntı, `#ct/<id>`) · **Keşif** (`#kesif/<adres>`) · **CT akış** · **CT istatistik**. Sayfa Copy trade ile açılır.
- Tanım: `sg-arge/docs/PANO_COPYTRADE.md`; veri biçimi: `sg-arge/docs/VERI_SOZLESMESI.md` (v1.1, `surum` 1; başka sürüm reddedilir).
- Sayfa açıkken her 5 dakikada veriyi yeniden okur; üstteki **Yenile** düğmesi hemen okur.
- Sahte veri yok: veri okunamazsa sayfa hata gösterir; olmayan alanlar "veri yok" der.
- Paper/strateji araştırması kapandı; ona ait pano, sekmeler ve `data.json` kaldırıldı.

## Veri kaynağı
`index.html` içindeki iki sabit, canlı veriyi gösterir (sg-arge `copytrade-izleme` dalı, ham GitHub adresi):
- `CT_KAYNAK` = `…/copytrade-izleme/izleme/durum.json` (saatte bir güncellenir).
- `CT_KARAR` = `…/copytrade-izleme/izleme/kararlar.jsonl`. Dosya yoksa (404) "henüz karar kaydı yok" sayılır; tarayıcı bu 404'ü konsola yine de yazar, sayfa hata göstermez.

Eski veri uyarısı 90 dakikadan sonra çıkar (`CT_ESKI_DK`). "ÖRNEK VERİ" etiketi yalnız `kaynak` alanı `ornek` ile başlıyorsa görünür.
`izleme/ornek_durum.json`: sg-arge `main`'deki sabit örneğin kopyası (sahte veri); test için `CT_KAYNAK` geçici olarak `./izleme/ornek_durum.json` yapılabilir.

Keşif kaynağı `index.html` içindeki tek `KESIF_KAYNAK` sabitidir. Şimdilik `./kesif/ornek_kesif.json` kullanılır; canlıda sg-arge `copytrade-kapi` dalındaki `kesif/kesif.json` adresine çevrilecektir. Şema sg-arge `docs/GOREV_TRADER_SECIMI.md` içindeki `kesif.json` v1 bölümüdür. Keşif'teki “Adresi kopyala” düğmesi yalnız cüzdan adresini panoya yazar; emir göndermez.

## Dosyalar
| Dosya | Görev |
|---|---|
| `index.html` | Pano (tek sayfa). |
| `izleme/` | Test için sabit örnek durum (sahte veri); canlıda kullanılmaz. |
| `kesif/` | Keşif sekmesi için v1 şemasına uygun sahte aday verisi. |
| `vendor/` | Sabit sürümlü kütüphaneler: Chart.js 4.4.1 (ayrıntı grafikleri, MIT), Lucide 0.460.0 (ikonlar, ISC), Tailwind 3.4.17 ile derlenmiş CSS (MIT). Dış CDN kullanılmaz. |

## Tailwind CSS'i yeniden derleme (index.html'de yeni sınıf kullanılırsa)
```bash
npm i tailwindcss@3.4.17
printf '@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' > in.css
echo "module.exports = { darkMode: 'class', content: ['index.html'], theme: { extend: {} } };" > tailwind.config.js
npx tailwindcss -c tailwind.config.js -i in.css -o vendor/tailwind.3.4.17.css --minify
```
