# Gece görev listesi (Codex), 2026-10-24 → sabah

Kullanıcı uyuyor. Sırayla, durmadan ilerle; biri takılırsa not düş ve sıradakine geç.
Uzun koşular GitHub Actions'ta (`workflow_dispatch`): Codex oturumu kapanınca süreçler ölüyor.
Yöntem, eşik ve karar kodu değişmez (docs/TEST_YAPISI.md, docs/GOREV_TV2.md Ek 1-2).

Her adım bitince bu dosyadaki kutuyu işaretle, `#200` dalına veya `claude/magical-ride-c7apbp` dalına
(yalnız `results/` ve bu dosya) commit'le. Lider (Claude) ~2-3 saatte bir kontrol eder, yeni not buraya ekler.

## Sıra
- [ ] 1. Actions iş akışı: `huni.yml`'ye `workflow_dispatch` girdili (görev adı + parça) iş; `timeout-minutes: 350`, kayıt noktasından devam, sonuç artifact + commit.
- [ ] 2. U1 5m (5 varyant) Actions'ta; bitince `#200`'e.
- [ ] 3. TV-2 kalan kripto: `results/tv2/kuyruk_kripto.txt` (204 id), `timeout 7200 python -m backtests.tv2 --ayri --dakikalik <id>`, 4 paralel, 4-6 parça. Var olan satırları ezme.
- [ ] 4. U6 kalan 2 kart, Reddit 2a/2b (kısa işler, aradaki boşluklarda).
- [ ] 5. TV-2 veri eşleme (kripto dışı 636): `arastirma/tv2_veri_eslesme.csv` → id, yayin_sembolu, tf, kaynak (dukascopy / yfinance / vnstock / yok), eşdeğer sembol, en eski tarih, not. Önce son sürümü 2026'dan önceki ~78'i.
  - FX/metal/endeks CFD (OANDA, FX, TVC, CAPITALCOM, PEPPERSTONE…): Dukascopy.
  - CME_MINI/CME/COMEX/NYMEX/CBOT: Dukascopy eşdeğer CFD (ES→USA500, NQ→USATECH, GC→XAUUSD, CL→LIGHT…); yoksa yfinance `ES=F` (60m ≤ 730 gün).
  - NASDAQ/NYSE/AMEX: yfinance (gün içi sınırını not et).
  - NSE/BSE: yfinance `.NS/.BO`. HNX/HOSE: vnstock.
  - "yok" yazmadan önce en az iki kaynak dene ve not et.
- [ ] 6. Veri yükleyicisi: `backtests/tv2.py` `_dis_veri`'ye eşleme tablosunu okuyan dal (Dukascopy/vnstock), testiyle. Sonra eşlenen ilk 78'i Actions'ta koş.
- [x] 7. Kaynağı kapalı/bulunamadı 33: eski alfanümerik id ve script sayfası üzerinden yeniden ara; bulunanları `tv2_surumler.csv`'ye ekle. (2026-10-25: 33/33 tekrar denendi; hiçbiri açılmadı, her satırda deneme nedeni kaydedildi.)
- [x] 8. Faz 1 (Actions). (2026-10-25: özel `faz1_u7` işi tamamlandı; özet tablolar U7 dalına alındı. Genel iş akışındaki eski asama2a zinciri ayrı USDTRY/artefakt bağlamında başarısız.)
- [ ] Sabah: bu dosyanın sonuna 10 satırlık özet (ne bitti, ne takıldı, Actions dakikası).

## Lider notları

### Not 1 (lider, 2026-10-24 ~21:05 UTC)
- **Kuyruğu koşmadan önce `git pull` yap.** Yorumlayıcıya yeni özellikler eklendi: `calc_on_order_fills`, gün içi risk sınırları (`max_intraday_loss`, `max_intraday_filled_orders`, `max_cons_loss_days`), Heikin Ashi, `ta.nvi/pvi/pvt/accdist/wad/wvad/iii`, çizgi/kutu/etiket koordinat okuma. Eski kodla koşulan satırlar "desteklenmiyor" çıkar.
- **Adım 5-6 için:** yfinance gün içi yükleyici gerekiyor (60m ≤ 730 gün, 1m ≤ 7 gün; 2h/4h/8h için 60m'den TradingView seans hizasıyla birleştirme). Bunu ilk kullanacak olan `cFY26Qg8` (CME:BTC1! ile spot arasındaki fark, 8H, sürüm 2024-09-25). **Spot eşdeğeri bu stratejide kullanılamaz**: mantık iki fiyatın farkına dayanıyor, `BTC=F` gerekli.
- **`czUjU1Zi`:** GLASSNODE:BTC_MARKETCAP kullanıyor. Önerilen eşdeğer: Binance BTC fiyatı × dolaşımdaki arz (blok takviminden). Bunu eşleme tablosuna "eşdeğer" notuyla yaz.

### Not 2 (lider, ~21:20 UTC)
- Yorumlayıcıya eklendi: `matrix`, `request.security_lower_tf` ve düşük dilimli `request.security`, döngüde oluşan negatif geçmiş indeksi (na). Koşudan önce `git pull`.
- **Kütüphane `import`:** pine-facade kütüphane kaynağını yol adıyla (`kullanıcı/ad/sürüm`) vermiyor, PUB kimliği gerekiyor. Kripto dışı kaynakları çekerken her `import` satırını `arastirma/tv2_kutuphaneler.csv`'ye yaz (sütunlar: kullanıcı, ad, sürüm, kullanan id'ler). Kütüphane sayfasını ve PUB kimliğini lider bulacak.

### Not 3 (lider, 23:35 UTC): Actions koşusu 40130058265 incelemesi
Koşu 20:30–22:27 sürdü, 4 iş düştü:
1. **Commit adımları (u1_5m, faz1_u7):** push reddedildi (`fetch first`), çünkü koşu sırasında dala başka commit geldi. Düzeltme, `huni.yml` 69. ve 106. satırlar:
   ```
   for i in 1 2 3 4; do
     git pull --rebase origin "${{ github.ref_name }}" && git push origin HEAD:${{ github.ref_name }} && break
     sleep $((i*5))
   done
   ```
   (yalnız `results/` dosyaları; çakışma beklenmez).
2. **U1 5m sonuçları kaybolmadı.** "Resume U1 5m funnel" adımı başarılı, artifact yüklendi (14 gün saklanır). Artifact'ı indirip `#200` dalına commit'le; yeniden koşma.
3. **asama2a:** `data/daily/USDTRY_X.parquet yok`. "veri" işi `fetch_asset(USDTRY=X)` çağırıyor ama dosya artifact'a girmiyor ya da başka adla yazılıyor. Dosya yolunu ve artifact `path`'ini kontrol et. **faz1_u7**'nin "Run U7 Faz 1 stages" adımı da 5 dakikada düştü; büyük olasılıkla aynı sebep. O adımın logunu kontrol et ve iş içinde USDTRY'yi de indir.
4. **Kuyruk 3 (TV-2 kalan kripto, 204 id)** henüz iş akışında yok. Eklenecek; `claude/magical-ride-c7apbp` dalından çalışmalı (yorumlayıcı oradadır).
5. **Güncelleme:** Kuyruk 3'ü (204 kripto) lider kendi ortamında koşuyor (23:40 UTC başladı), Actions dakikası harcanmasın. Codex bu adımı atlasın.

### Not 4 (lider, ~00:30 UTC)
- **Adım 6'nın yfinance kısmı yapıldı:** `backtests/tv2.py::_yfinance_gun_ici`. Codex yalnız Dukascopy (FX/CFD) ve vnstock yükleyicilerini eklesin, aynı `veri()` dalına.
- **Kapsam taraması** (969 kaynak, yapay veri): ilk geçişte 806 çalıştı. Sonra şunlar eklendi: na demet, bantlı vwap, kütüphane import (5 kütüphane), FIFO, enum ve küçük yerleşikler, alt koşu security, time(tz), tireli import. Kalan desteklenmeyenler: `request.footprint` (2), `request.earnings`/`financial` (2), `renko` (1), `ta.pivot_point_levels` (1), `max_position_size` (1), birkaç tekil ad. Ayrıca ~70 strateji yavaş (90 sn'de bitmedi).
- **Yeni karar `islem_yok`:** tüm geçmişte 0 işlem. `input.source` ile dış göstergeden sinyal bekleyen bağlayıcı şablonlar (9 tane) böyle çıkar.

### Not 5 (lider, ~01:10 UTC)
- **Hızlı ayrıştırıcı** (`engine/pine/ayristir.py`): pynescript'in ANTLR'si SLL modunda ~100 kat hızlı, AST birebir aynı, disk önbelleği `data/tv2/ast`. Taramada "yavaş" çıkan 62 stratejinin 53'ü artık çalışıyor; sebep ayrıştırmaydı, bar yürütmesi değil. **Codex: Actions koşularından önce `git pull`.**
- **`request.footprint` (3 strateji):** iki DOGEUSDT.P stratejisi için gerçek footprint Binance vadeli aggTrades arşivinden (`data.binance.vision`) kurulabilir: 2 saatlik bar başına, fiyat satırı başına alıcı/satıcı hacmi, yalnız sürüm tarihinden itibaren. Ayrı iş. `6ve1ax1D` (CME:MNQ1!, 1 dakika): CME işlem akışı verisi ücretli, 1 dakikalık veri de yalnız 7 günlük ücretsiz. **Kullanıcıya sorulacak.**
