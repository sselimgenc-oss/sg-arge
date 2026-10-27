# SG Pano · Copy trade

`sg-arge` copy trade izleme panosu. **Salt okunur; gerçek emir, para hareketi ve aracı kurum bağlantısı yok.**

- Yayın: GitHub Pages (`main` / kök). Tek sayfa (`index.html`), erişim yöntemi değişmedi (ek hesap/şifre yok).
- Sekmeler: **Copy trade** (kartlar + ayrıntı, `#ct/<id>`) · **CT akış** · **CT istatistik**. Sayfa Copy trade ile açılır.
- Tanım: `sg-arge/docs/PANO_COPYTRADE.md`; veri biçimi: `sg-arge/docs/VERI_SOZLESMESI.md` (v1.1, `surum` 1; başka sürüm reddedilir).
- Sayfa açıkken her 5 dakikada veriyi yeniden okur; üstteki **Yenile** düğmesi hemen okur.
- Sahte veri yok: veri okunamazsa sayfa hata gösterir; olmayan alanlar "veri yok" der.
- Paper/strateji araştırması kapandı; ona ait pano, sekmeler ve `data.json` kaldırıldı.

## Veri kaynağı
`index.html` içindeki iki sabit:
- `CT_KAYNAK` = `./izleme/ornek_durum.json` (sg-arge `main`'deki sabit örneğin birebir kopyası; **sahte veri**, sayfada "ÖRNEK VERİ" uyarısı çıkar).
- `CT_KARAR` = `./izleme/kararlar.jsonl` (şimdilik boş; "henüz karar kaydı yok" sayılır).

Canlıya geçiş yalnız bu iki sabittir; adresler `index.html`'de yorum olarak yazılı
(sg-arge `copytrade-izleme` dalındaki ham `izleme/durum.json` ve `izleme/kararlar.jsonl`). Karar dosyası canlıda henüz yoksa (404) sayfa bunu "karar kaydı yok" sayar.

## Dosyalar
| Dosya | Görev |
|---|---|
| `index.html` | Pano (tek sayfa). |
| `izleme/` | Örnek durum ve (boş) karar kaydı. |
| `vendor/` | Sabit sürümlü kütüphaneler: Chart.js 4.4.1 (ayrıntı grafikleri, MIT), Lucide 0.460.0 (ikonlar, ISC), Tailwind 3.4.17 ile derlenmiş CSS (MIT). Dış CDN kullanılmaz. |

## Tailwind CSS'i yeniden derleme (index.html'de yeni sınıf kullanılırsa)
```bash
npm i tailwindcss@3.4.17
printf '@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' > in.css
echo "module.exports = { darkMode: 'class', content: ['index.html'], theme: { extend: {} } };" > tailwind.config.js
npx tailwindcss -c tailwind.config.js -i in.css -o vendor/tailwind.3.4.17.css --minify
```
