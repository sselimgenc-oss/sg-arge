# SG Pano

`sg-arge` paper trade defterinin panosu. **Sanal para; gerçek emir ve aracı kurum bağlantısı yok.**

- Yayın: GitHub Pages (`main` / kök).
- Veri: `data.json`. Bu dosyayı yalnız `sg-arge` deposundaki `paper.yml` iş akışı yazar (`paper/panel.py` + `paper/anlik.py`). Elle düzenlenmez.
- Güncelleme: işlemler ve defter günde bir, ABD kapanışından sonra; açık pozisyonların değerlemesi saatlik. Sayfa açıkken her 5 dakikada `data.json`'u yeniden okur.
- Sahte veri yok: `data.json` okunamazsa sayfa hata gösterir; verisi olmayan bölümler "henüz veri yok" der.

## Dosyalar
| Dosya | Görev |
|---|---|
| `index.html` | Pano (tek sayfa). |
| `data.json` | Pano verisi (şema: `sg-arge/paper/panel.py`). |
| `vendor/` | Sabit sürümlü kütüphaneler: Chart.js 4.4.1 (MIT), Lucide 0.460.0 (ISC), Tailwind 3.4.17 ile derlenmiş CSS (MIT). Dış CDN kullanılmaz. |

## Tailwind CSS'i yeniden derleme (index.html'de yeni sınıf kullanılırsa)
```bash
npm i tailwindcss@3.4.17
printf '@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' > in.css
echo "module.exports = { darkMode: 'class', content: ['index.html'], theme: { extend: {} } };" > tailwind.config.js
npx tailwindcss -c tailwind.config.js -i in.css -o vendor/tailwind.3.4.17.css --minify
```
