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
| `izleme/ornek_durum.json` | Copy trade izleme sekmelerinin geçici kaynağı: sg-arge `main`'deki sabit örneğin birebir kopyası (**sahte veri**, sayfada "ÖRNEK VERİ" uyarısı çıkar). |
| `vendor/` | Sabit sürümlü kütüphaneler: Chart.js 4.4.1 (MIT), Lucide 0.460.0 (ISC), Tailwind 3.4.17 ile derlenmiş CSS (MIT). Dış CDN kullanılmaz. |

## Tailwind CSS'i yeniden derleme (index.html'de yeni sınıf kullanılırsa)
```bash
npm i tailwindcss@3.4.17
printf '@tailwind base;\n@tailwind components;\n@tailwind utilities;\n' > in.css
echo "module.exports = { darkMode: 'class', content: ['index.html'], theme: { extend: {} } };" > tailwind.config.js
npx tailwindcss -c tailwind.config.js -i in.css -o vendor/tailwind.3.4.17.css --minify
```

## Copy trade sekmeleri (Copy trade · CT akış · CT istatistik)
Tanım: `sg-arge/docs/PANO_COPYTRADE.md`; veri biçimi: `sg-arge/docs/VERI_SOZLESMESI.md` (sürüm 1; başka sürüm reddedilir). Salt okunur: emir ve para hareketi yok.
Kaynak adresleri `index.html` içinde `CT_KAYNAK` / `CT_KARAR` sabitleridir. Canlı veriye geçmek için yalnız bu ikisi, sg-arge `copytrade-izleme` dalındaki ham `izleme/durum.json` ve `izleme/kararlar.jsonl` adreslerine çevrilir (yorum satırında yazılı). Karar dosyası yoksa (404) "henüz karar kaydı yok" sayılır; okunamazsa sayfa bunu belirtir.
Sözleşme v1.1 alanları (`sanal_kopya.egri`, `olaylar[].sanal_sonuc`) kullanılır; "açtıklarım ↔ tümü" kapanmış olayların ortalama net %'sidir, kapanmış ve karar verilmiş olay < 10 ise "yetersiz veri" yazar. Veride olmayan şey ekranda "veri yok" der, uydurulmaz.
