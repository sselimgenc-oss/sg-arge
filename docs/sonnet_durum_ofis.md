# Sonnet durum — Ofis görünümü (sg-pano `ofis/`)

Dal: `sonnet/ofis-tasarim`. Görev: `sg-arge/docs/GOREV_OFIS_TASARIM.md`.

- [x] Önce `DURUM.md` ve `GOREV_D_YOLU.md` okundu (roller → 14 oda).
- [x] İzometrik ofis (Canvas 2D, kodla çizilmiş piksel sanatı; dış varlık yok): bina, 14 oda, çimen/ağaç/otopark/yol, gün ışığı.
- [x] Trader figürleri Lab/Aday/Oda/Kontrol masalarında; üstte kısa adres, üzerine gelince ayrıntı.
- [x] Olay → animasyon (`OLAYLAR.md`), Gözcü kaydı, oda vurgusu, bayat oda grileşmesi, Risk alarmı, Haberleşme zarfı.
- [x] Sol panel: kasa, özet, açık işlemler, son kapananlar, huni, kohort↔kontrol (performans kilitli), veri kalitesi, risk, Telegram.
- [x] `ornek_durum.json` + `SEMA.md`; her sayıda zaman/n; veri yoksa "bilinmiyor"; `ÖRNEK VERİ` etiketi.
- [x] `LISANSLAR.md` (dış varlık yok, ≈185 KB toplam), kanıtlar `ofis/kanit/`.
- [x] Erişilebilirlik: gerçek `<button>`, kontrast ≥ 4,5:1 (25 çift ölçüldü), tuval açıklaması, klavye ile kamera, `prefers-reduced-motion`.

Kontroller: koltuk erişilebilirliği (yol bulma, 54 koltuk), arayüz testleri (ipucu, oda seçimi, sekmeler, tam ekran, azaltılmış hareket,
390 px'te yatay kaydırma yok) geçti. Kare süresi (yazılım oluşturucu, başsız): sahne ≈ 2,3 ms + aktarım ≈ 3 ms; gerçek 60 fps ölçümü
lider tarafından GPU'lu makinede `?perf=1` ile yapılmalı (başsız ortamda ölçülemedi).

Açık/bilinen: örnek akış 156 sn'de başa sarar (hız 1×); `hiz` > 4 yürüyüşlerden hızlı olduğu için desteklenmez. Gerçek veriye bağlama Faz 5.
