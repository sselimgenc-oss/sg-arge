# Codex durum — izleme

- Kapsam: yalnız İş A. İş B / Telegram başlatılmadı; anahtar ve emir yok.
- `main` güncellendi ve `codex/izleme` içine birleştirildi (`53b69ec`).
  `copytrade/kapi.delayed_copy` bağımlılığı artık mevcut.
- Liderin `copytrade/izleme_listesi.yaml` dosyası aynen kullanılıyor:
  iki test trader'ı, `izlemede`, t0 `2026-10-28`; kopyalama kararı değil.
- Komut: `source .venv/bin/activate` ardından
  `python -m copytrade.izleme_motoru --root . --output /tmp/izleme`.
  Actions çıktısı `copytrade-izleme` dalındaki `izleme/` dizinine gider;
  `main` içine canlı çıktı yazılmaz.
- Motor: kalıcı trader imleciyle artımlı dolumlar, aynı milisaniyede sınır
  tekrarını tekilleştirme, günlük portfolio önbelleği, ana/HIP-3 hesap
  pozisyonları, kalıcı olay kimlikleri ve son 200 olay.
- Sanal defter: 1.000 USD, 30 dk, `delayed_copy` maliyeti ve funding;
  geçmiş yürütme mumları arşivlenir. Gecikmesi dolmayan işlem ücretlenmez.
  Tam yürütme mumu yoksa veya arşivsiz geçmiş 5.000 dakika dışındaysa
  koşu hata verir; eski başarılı arşiv yayımlanmaz/değiştirilmez.
- Sağlık: mevcut blok bootstrap ve CUSUM yeniden kullanıldı. Günlük
  seride 28 günlük blok ve %5/%20 kantilleri seçildi; mevcut pano
  çağrılarının varsayılanları değişmedi. Kaldıraç brüt pozisyon / hesap.
  Martingale mevcut ölçütten; yeni eşik veya kapı kararı yok.
- Teknik ayrıntılar: iç durum `motor.json` (dış şemadan ayrı); kimlik
  dolumun coin/tid karması + olay türü; t0/adres aynı id altında değişmez.
  Kopya paydası ilk pozitif hesap değerinde sabitlenir. t0 öncesi
  pozisyonun kapanışı ters sanal pozisyon açmaz. Olay sonuçları FIFO
  lotlara, giriş/çıkış maliyeti ve pozisyondaki funding ile dağıtılır.
  Defterde günler yürütme zamanına göre kaydedilir; başlangıç/t0 gelmeden
  bakiye 1.000 ve günlük eğri boştur. İşlem yoksa son işlem alanları boş
  metin/0; eksik kapı `Yetersiz`, engelli Binance katalogu `bilinmiyor`.
- İş akışı: saatlik `23 * * * *`, elle tetikleme ve dalda push denemesi;
  eşzamanlılık grubu, ilk koşuda yetim veri dalı, rebase ile 3 push denemesi.
  Mevcut `kararlar.jsonl` korunur; bu iş karar dosyası üretmez.
- Test: `python -m pytest -q` — **79 başarılı, 112 uyarı**. Ağsız testler
  gerçek liste biçimi/iki trader, boş liste, şema, olay eşiği/kimliği,
  artımlı okuma, günlük önbellek, gecikme/maliyet/funding, sağlık koşulları,
  arşiv güvenliği ve yerel Git deposunda yetim dal/yeni koşuyu kapsar.
- Canlı API ve push ile Actions doğrulaması devam ediyor; sonuç aşağıya
  eklenecek. Henüz doğrulanmış canlı pano sonucu iddia edilmiyor.
