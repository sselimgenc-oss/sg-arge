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


## Adım 0 — özgünleştirme (2026-10-28, `GOREV_OFIS_TASARIM.md` "Karar: temel taslak ve sıra")
- [x] **Bina biçimi:** ortasında avlu + havuzlu bahçe olan iki kanatlı yapı (güney kanat Aday/Oda/Kapı +4 satır kaydı; doğu ucu cam galeri duvarı, batı ucu çit; yürüme ağı yalnız taş yollar). Otopark kuzeydoğuda, düz/dik park yerleri; sol altta açılı otopark yok.
- [x] **Gezinme:** üst çubuk, sekmeler, "SİM/TELEGRAM AÇIK" çipleri, vardiya/saat ve "Ofis tam ekran" kalktı → sol dikey menü (15 oda düğmesi + Tüm ofis), durum plakaları ("kayıt kipi", "haber hattı", "ışık saati"), tuval köşesinde `örnek veri` şeridi, tuvalde panel gizleme düğmesi.
- [x] **Etiket ve palet:** krem kutular yerine kesik köşeli koyu plaka (oda renginde şerit; bayatta taralı "veri eski"); deniz-yeşili/aqua/kayısı palet; zeminler ve duvarlar yeniden renklendi.
- [x] **Taslak 1'den (kodla yeniden çizildi, PNG yok):** odalara sıcak iç ışık (saat bazlı; bayat odada yok), cam bölmeler (avluya bakan cam galeri), havuzlu bahçe (su altı ışığı geceleri).
- [x] **Hızlı kazanımlar:** ortam ışığı (ışık yönü + kenar kararması), oda başına zemin (Makam balıksırtı parke, Denetim metal ızgara, Çay ocağı fayans), küçük nesneler (semaver, koliler, sunucu LED'i + parıltı = `denetim` durumu).
- [x] **Kurallar:** dış varlık yok; çaycı yürüyüşü ve ağaç sallanması kaldırıldı (olaydan doğmayan hareket yok); kâr/zarar rengi kaldırıldı (K/Z işaretli sayı, nötr renk); telefon: yatay kaydırma yok, menü yatay şeride dönüşür.
- [x] **Kanıt:** `ofis/kanit/` — yeni masaüstü (gündüz, gece, avlu yakın, alarm/bayat) ve telefon görüntüleri, 15 sn kayıt, `karsilastirma_once_sonra.png`, `karsilastirma_telefon.png`, `karsilastirma_etre.png` (Etre görseli yalnız lider kontrolü için; birleştirmeden önce silinebilir).
- Kontroller: yol bulma (54 koltuk + 5 çapraz kat geçişi, çıkış), arayüz testleri (ipucu, oda seçimi, menü, panel gizleme, azaltılmış hareket, 390 px'te yatay kaydırma yok), 2 turluk döngü testi, kontrast (31 çift ≥ 4,5:1) geçti. Gerçek 60 fps yine başsız ortamda ölçülemedi (`?perf=1` ile GPU'lu makinede ölçülmeli).
- Sürüm 2 (odaya girme vb.) bu turda başlamadı; seçim sonucu gelince bu iş bırakılıp seçime dönülür.
