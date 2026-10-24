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
- [ ] 7. Kaynağı kapalı/bulunamadı 33: eski alfanümerik id ve script sayfası üzerinden yeniden ara; bulunanları `tv2_surumler.csv`'ye ekle.
- [ ] 8. Faz 1 (Actions).
- [ ] Sabah: bu dosyanın sonuna 10 satırlık özet (ne bitti, ne takıldı, Actions dakikası).

## Lider notları

### Not 1 (lider, 2026-10-24 ~21:05 UTC)
- **Kuyruğu koşmadan önce `git pull` yap.** Yorumlayıcıya yeni özellikler eklendi: `calc_on_order_fills`, gün içi risk sınırları (`max_intraday_loss`, `max_intraday_filled_orders`, `max_cons_loss_days`), Heikin Ashi, `ta.nvi/pvi/pvt/accdist/wad/wvad/iii`, çizgi/kutu/etiket koordinat okuma. Eski kodla koşulan satırlar "desteklenmiyor" çıkar.
- **Adım 5-6 için:** yfinance gün içi yükleyici gerekiyor (60m ≤ 730 gün, 1m ≤ 7 gün; 2h/4h/8h için 60m'den TradingView seans hizasıyla birleştirme). Bunu ilk kullanacak olan `cFY26Qg8` (CME:BTC1! ile spot arasındaki fark, 8H, sürüm 2024-09-25). **Spot eşdeğeri bu stratejide kullanılamaz**: mantık iki fiyatın farkına dayanıyor, `BTC=F` gerekli.
- **`czUjU1Zi`:** GLASSNODE:BTC_MARKETCAP kullanıyor. Önerilen eşdeğer: Binance BTC fiyatı × dolaşımdaki arz (blok takviminden). Bunu eşleme tablosuna "eşdeğer" notuyla yaz.

### Not 2 (lider, ~21:20 UTC)
- Yorumlayıcıya eklendi: `matrix`, `request.security_lower_tf` ve düşük dilimli `request.security`, döngüde oluşan negatif geçmiş indeksi (na). Koşudan önce `git pull`.
- **Kütüphane `import`:** pine-facade kütüphane kaynağını yol adıyla (`kullanıcı/ad/sürüm`) vermiyor, PUB kimliği gerekiyor. Kripto dışı kaynakları çekerken her `import` satırını `arastirma/tv2_kutuphaneler.csv`'ye yaz (sütunlar: kullanıcı, ad, sürüm, kullanan id'ler). Kütüphane sayfasını ve PUB kimliğini lider bulacak.
