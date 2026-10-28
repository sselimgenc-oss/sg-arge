# Ofis · varlık kaynakları ve lisanslar

**Sonuç: dış görsel varlık yok.** Ofisin tüm görselleri (zemin, duvar, mobilya, ağaç, araba, kişi, simge) bu klasördeki JavaScript
kodunun çalışırken piksel piksel çizdiği, **bu iş için elle yazılmış** çizimlerdir. Hiçbir resim dosyası (PNG/WebP/SVG sprite sayfası)
indirilmedi ya da kopyalanmadı; bu yüzden üçüncü taraf lisans yükümlülüğü yoktur.

| Varlık | Kaynak | Lisans |
|---|---|---|
| Zemin dokuları (çim, ahşap, halı, fayans, taş, asfalt) | `sprites.js` içinde kodla üretilir (gürültü + desen kuralları) | Bu reponun kendi içeriği |
| Duvar, cam bölme, pencere, giriş | `sprites.js` | Bu reponun kendi içeriği |
| Mobilya (masa, monitör, raf, sunucu dolabı, kasa, tezgâh, vb.) | `sprites.js` | Bu reponun kendi içeriği |
| Ağaçlar, çalılar, arabalar, park lambası, tabela | `sprites.js` | Bu reponun kendi içeriği |
| Kişi figürleri, sandalye, balon simgeleri, zarf/para/kutu | `kisiler.js` | Bu reponun kendi içeriği |
| Duvar ekranlarının içeriği (eğri, çubuklar) | `office.js` — çalışma anında veriden çizilir | Bu reponun kendi içeriği |
| Arayüz simgeleri (logo, kilit) | Sayfa içinde elle yazılmış SVG yolları (`index.html`, `panel.js`) | Bu reponun kendi içeriği |
| Yazı tipi | Sistem yazı tipleri (`ui-monospace` / `Segoe UI` / `Roboto` yığını); yazı tipi dosyası indirilmez | İşletim sistemine ait; dağıtılmaz |
| Kütüphane | Yok (saf JavaScript + Canvas 2D). CDN kullanılmaz | — |

Lisansı belirsiz varlık kullanılmadı. Telif konusunda şüphe doğarsa bu belgeye değil önce kodun ilgili işlevine bakın: her çizim
`sprites.js` / `kisiler.js` içinde okunabilir hâldedir.

## Etre V2 ile ilişki (kopya değil, aynı tarz)
`sg-arge/arastirma/etre/` yalnız **tarz** referansı olarak okundu: izometrik piksel sanatı, oda düzeni fikri, yan panel yapısı.
- Etre'nin hiçbir görseli, çizimi ya da ekran görüntüsü parçası bu repoya alınmadı, üzerinden çizilmedi, iz sürülmedi.
- Oda sırası ve içerikleri Etre'den değil `sg-arge/docs/GOREV_D_YOLU.md` Roller tablosundan (14 oda) çıkarıldı; yerleşim, mobilya
  seçimi, renkler, karakter tasarımı, ekran içerikleri bize aittir.
- Kasıtlı farklar: bina 26×16 karo ve 15 bölgeli (hol dâhil); koltuk düzeni "koridor sütunlu" havuz/kat mantığına göre; sol panelde
  Kohort ↔ Kontrol kartı (performans kilitli), risk tavanları, veri kalitesi, Telegram kartı; her sayıda zaman damgası / n; duvar ekranları
  gerçek veriyle çizilir; ofis içinde kapı-turnike, Haberleşme zarfı, Risk alarm lambası gibi bize özgü olaylar vardır.

## Varlık boyutu raporu (2026-10-28)
Hedef: toplam varlık ≤ 15 MB. Gerçekleşen: **görsel varlık dosyası 0 bayt**; tüm sayfa (kod + stil + örnek veri) aşağıdaki gibidir.

| Dosya | Boyut (bayt) |
|---|---:|
| `sprites.js` | 33 802 |
| `office.js` | 27 546 |
| `main.js` | 25 627 |
| `world.js` | 23 902 |
| `ornek_durum.json` | 20 084 |
| `ofis.css` | 13 782 |
| `panel.js` | 13 519 |
| `kisiler.js` | 10 739 |
| `px.js` | 9 171 |
| `index.html` | 6 760 |
| **Toplam (gzip öncesi)** | **≈ 185 KB** |

Çalışma belleğinde: zemin tuvali 1320×796 px (≈ 4 MB RAM) ve birkaç yüz küçük önbellekli sprite. Ağ üzerinden ≈ 56 KB (gzip).
`kanit/` klasöründeki ekran görüntüsü ve kayıtlar sayfanın parçası değildir (yalnız PR kanıtı).
