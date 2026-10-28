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
- [x] **Kanıt (#18 dalında; sürüm 2 dalında yalnız iki önce/sonra karşılaştırması kaldı):** `ofis/kanit/` — yeni masaüstü (gündüz, gece, avlu yakın, alarm/bayat) ve telefon görüntüleri, 15 sn kayıt, `karsilastirma_once_sonra.png`, `karsilastirma_telefon.png`, `karsilastirma_etre.png` (Etre görseli yalnız lider kontrolü için; birleştirmeden önce silinebilir).
- Kontroller: yol bulma (54 koltuk + 5 çapraz kat geçişi, çıkış), arayüz testleri (ipucu, oda seçimi, menü, panel gizleme, azaltılmış hareket, 390 px'te yatay kaydırma yok), 2 turluk döngü testi, kontrast (31 çift ≥ 4,5:1) geçti. Gerçek 60 fps yine başsız ortamda ölçülemedi (`?perf=1` ile GPU'lu makinede ölçülmeli).
- Sürüm 2 (odaya girme vb.) bu turda başlamadı; seçim sonucu gelince bu iş bırakılıp seçime dönülür.

## Sürüm 2 — ilk 5 iş (dal `claude/ofis-v2`, 2026-10-28)
Not: #18 (Adım 0) bu dalı açarken henüz birleşmemişti; dal `sonnet/ofis-tasarim` ucundan açıldı (Adım 0 commit'leri bu PR'da da görünür).
- [x] **1) Oda içi görünüm:** aynı tuvalde kamera yakınlaşması; diğer odalar soluklaşır, seçili odanın tam yükseklikli duvarları kalkar; adres `#oda/<id>`; Esc, "← Bina" ve tarayıcı geri/ileri tuşları. Lab, ardından Kapı ve Arşiv aynı kalıpla (14 odanın hepsi açılır).
- [x] **2) Ortak bilgi kutusu:** masaüstünde sağda panel, telefonda alttan çekmece; Kimlik · Gerçek veri ("X dk önce", n; "Neden burada?": olay_id, kural, tarih) · Replik (olay repliği + "ofis esprisi" etiketli ayrı kutu). 57 figürün tamamı ve her odada ≥ 3 nesne tıklanabilir; tıklanan kişi sıçrayıp gülümseme balonu çıkarır. Dokunma hedefi ≥ 44 px; hover'a bağlı işlev yok.
- [x] **3) `replikler.json`:** `veri` (olay_turu, rol, sablon) + ayrı `suz` listesi; test `ofis/test/replik.test.js` (süs replikte rakam, adres, oran, para, yer tutucu yok).
- [x] **4) `OLAYLAR.md`:** olay → zarf/not/ok tablosu; örnek veri 21 olay türünün hepsini tetikler (yeni: `kirmizi_bayrak`, `bayrak_kalkti`: denetçi trader masasına yürüyüp kırmızı bayrak notu bırakır). Olay kuyruğu: yürüyüş hızlanır/atlanır, durum anında doğru; olay yokken çizim döngüsü durur.
- [x] **5) Adlar:** oda ve çalışan adları (+ trader takma adı) tarayıcıda saklanır, JSON dışa/içe aktarılır; varsayılanlar `kadro.json`; gerçek adres (kısaltılmış) sabit.
- Performans körlüğü: **kasa değeri/eğrisi, günlük toplam K/Z ve kol getirisi ofiste yok** (kasa kartı ve Finans ekranı "kilitli (hafta x/12)"); kâr/zarar rengi yok (masa ekranı tek ton, K/Z işaretli nötr sayı); rozet/seri yok. Her ekranda "araştırma/sanal, yatırım tavsiyesi değil".
- Karar noktası (lider): kasa değeri v1'de görünürdü; "toplanmış kol performansı gösterilmez" kuralı gereği kilitlendi. Geri açmak `Off.KILIT=false` ile olur (yalnız lider kararıyla).
- Kanıt (sürüm 2): `ofis/kanit/v2/` — masaüstü (bina, Lab kişi/nesne bilgisi, Kapı, Arşiv, iletişim işaretleri: terfi, kırmızı bayrak taşıyıcısı ve notu, ayarlar) ve telefon (bina, Lab + çekmece) ekran görüntüleri, 30 sn kayıt (`ekran_kaydi_30sn.mp4/.gif`: bina → Lab → kişiye tıklama → iletişim işareti).
- Testler: `node ofis/test/replik.test.js` (18 kontrol), `node ofis/test/ui.test.js` (Playwright; 50 kontrol). Sonuçlar PR açıklamasında.
- Düzeltme (testle bulundu): Kontrol, Lab, Finans, Haberleşme, Çay ve Aday'daki bitki/buzdolabı/sebil iç kapı boşluklarını kapatıyordu (v1'den kalma); taşındı. Artık denetçi trader masasına ve postacı posta kutusuna yürüyebilir.

## Sürüm 2b (dal `claude/ofis-v2b`, 2026-10-28)
- [x] Olay çekmecesi (filtre, tıkla → kamera + figür vurgusu, telefonda alttan çekmece) · [x] Bayatlık (`esik_dk` veride, "X dk önce", sis, "VERİ ESKİ") · [x] Oda ayrıntıları (Risk alarm paneli, Haberleşme ekranı + zarf rafı, ön kayıt kasası, Oda masaları, "ne yapar / ne yapmaz" kartı)
- [x] Günlük özet (yalnız olay günlüğü; boş günde "değişiklik yok") · [x] Ses (varsayılan kapalı, kodla üretilen ton) · [x] Terfi kuralı düzeltildi ("≥ 3 hafta ve ≥ 10 kapanmış işlem"), kural metni olaydan gelir.
- Düzeltme (testle bulundu): terfi eden trader'ın `kat_olay` kaydı eski (Kapı) kuralında kalıyordu; artık olaydan güncelleniyor.
- Kanıt: `ofis/kanit/v2b/` (masaüstü + telefon ekran görüntüleri, 20 sn kayıt: çekmece → filtre → olaya tıkla → kamera odaya → bayat oda sisi). v2'nin gif kopyası alan açmak için silindi (mp4 duruyor).
- Testler: `node ofis/test/replik.test.js`, `node ofis/test/ui.test.js` (86 kontrol) — hepsi geçti.

## Ofis paneli (dal `claude/ofis-panel`, 2026-10-28)
- [x] Kart sütunu masaüstünde varsayılan gizli; tuval tüm genişlik. [x] Sol menü → kamera + açılır panel (tek eşleme tablosu `PANEL_ESLE`). [x] Kapatma yolları (×, Esc, boş alan, ikinci tıklama, Tüm ofis). [x] Günlük özet şeridi. [x] Gözcü kaydı yerinde, telefon düzeni aynı.
- Karar: Kontrol → Kohort ↔ Kontrol kartı ve Oda → +Son kapananlar eklendi (aksi halde bu kartlar masaüstünde erişilemez olurdu); `PANEL_ESLE` tek satırla değişir.
- Eski testlerde Esc davranışı: menüden açılan panel varsa ilk Esc paneli kapatır (Lab testi güncellendi).
- Kanıt: `ofis/kanit/panel/` (önce/sonra, 1440 ve 1920). `ofis/kanit` boyutu 15 MB sınırı için v2 PNG'leri palet sıkıştırmasına çevrildi (≈ 10 MB).
- Testler: `ui.test.js` bölüm Q (panel aç/kapa; 112 kontrol), `replik.test.js` geçti.
