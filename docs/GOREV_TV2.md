# TV-2: 942 TradingView stratejisi, yazarın kendi koşullarında (eleme hunisi yok)

**Karar (kullanıcı, 2026-10-24):** "Kendi timeframe'imi ya da piyasamı istemiyorum; 942 stratejiyi kendi timeframe'inde, kendi mantığıyla test edelim. Huni yok."
**Kaynak:** `arastirma/U5_tv.csv`, `suzgec_sonucu` = `elendi:tf_disi` (942) + `elendi:tf_belirsiz` (60). Pine kodu: `pine-facade.tradingview.com/pine-facade/get/<PUB>/last` (U5 yöntemi).

## 1. Test koşulları = yazarınki
- **Piyasa:** script sayfasındaki yayın sembolünün kendisi (BTCUSDT, XAUUSD, SPX, EURUSD, tek hisse…). Evren havuzuna taşınmaz, sınıf eşlemesi yok.
- **Zaman dilimi:** yayın aralığı (1m…1W).
- **Mantık:** Pine kodu birebir: long **ve short** bacaklar, `strategy.entry/exit/close`, stop/limit/izleyen stop, `qty_percent` kısmi çıkışlar, `pyramiding`, takvim/seans filtreleri.
- **Boyut ve maliyet:** yazarın `strategy()` ayarları (`initial_capital`, `default_qty_type/value`, `commission`, `slippage`). Rapora ek bir sütun: aynı işlemler **gerçekçi maliyetle** (kripto %0,1/taraf, diğerleri %0,05/taraf + 1 tick kayma); yazar maliyet girmediyse bu sütun asıl bakılacak olandır.
- **Dolum:** TradingView strateji test aracı semantiği (`process_orders_on_close=false`: sinyal bar kapanışı, dolum sonraki açılış; stop/limit bar içi; aynı barda stop/hedef belirsizliğinde kötümser sıra).

## 2. Değerlendirme
`docs/TEST_YAPISI.md` (Adım 0-5): nedensellik denetimi, yazar ve uygulanabilir sonuç, sürüm tarihi sonrası sınama, tek kapı, sıralama, sanal havuz + 20 gölge kitap. Her strateji için tek satır; bilgi sütunları o dosyada. Kapıdan kalan da nedeniyle listelenir.

## 3. Veri
- Kripto: Binance, her zaman dilimi, 2017→.
- ABD/endeks/emtia/FX günlük ve üstü: yfinance, tam tarih.
- ABD/endeks/emtia/FX 1H-12H: yfinance 1H (~2 yıl); daha uzun gerekirse Dukascopy.
- ABD/endeks/emtia/FX dakikalık: **Dukascopy** (M1, ücretsiz; temizlikte silinen indirici geri getirilir).
- Verisi hiçbir ücretsiz kaynakta olmayan sembol (ör. bazı yerel borsalar) raporda "veri yok" diye ayrı listelenir; sessizce atılmaz.

## 4. Çevrilemeyen
Yalnız gerçekten çalıştırılamayan kod: harici veri servisi, Pine içinde eğitilip tekrarlanamayan model, repaint eden (geleceği gören) kod. Her biri nedeniyle listelenir. "Motor desteklemiyor" bir neden değildir: motor eksikse motor genişletilir.

## 5. İş bölümü
- **Lider:** TradingView strateji test aracını taklit eden yürütücü (`engine/tv_emulator.py`: long/short, pyramiding, stop/limit/izleyen, qty_percent, yazar boyutu ve komisyonu) + birim testleri; her partiden 5 kartın kaynak karşılaştırması.
- **Çevirmenler (Sonnet, Codex):** her script için `strategies/tv2/<id>.py`: Pine mantığını bar bar emirlere çeviren modül. 50'şerlik partiler, PR `[TV-2] parti n`. Öncelik: 1H-12H + 1W/3D (~265) → tf_belirsiz (60) → 30m-45m → 15m ve altı.
- **Koşu:** Codex, partiler birleştikçe; çıktı `results/tv2/sonuclar.csv` + `results/TV2_RAPOR.md`.
- **Sürüm tarihleri:** her script için pine-facade sürüm listesinden test edilen sürümün tarihi `arastirma/tv2_surumler.csv`'ye (çevirmen, parti PR'ında).
- Öncelik `TEST_YAPISI.md` "Çeviri sırası"na göre; yazarın iddia ettiği getiri kullanılmaz.

## Ek 1 (kullanıcı kararları, 2026-10-24, denetim 18:46 B2/B3)
1. **Dakikalık (15 dakikanın altı):** sürüm tarihinden 1 yıl önce başlayan pencereyle koşulur (`backtests/tv2.py --dakikalik`). Tüm dönem sütunu bu pencereyi kapsar; `pencere_bas` sütununda yazılır.
2. **Eşdeğer veri kabul:** BITFINEX/BITSTAMP/COINBASE/BYBIT `…USD` ve vadeli `.P` semboller Binance spot `…USDT` verisiyle koşulur; `veri` sütununda açık. mintick Binance'ten (TradingView sembol servisi erişilemiyor); tick cinsinden parametre kullananlarda `uyari`.

## Ek 2: Kapsam kuralı (kullanıcı, 2026-10-24)
"942 stratejiyi test edeceğiz diye yola çıktık; 'geçersiz, ulaşamadık' kabul etmiyorum."
- Her strateji ya bir test sonucu ile biter ya da açık bir **çözüm görevi** ile kuyruğa döner. "Desteklenmiyor", "veri_yok", "zaman_asimi" nihai sonuç değildir.
- "yetersiz_kanit" bir test sonucudur (test edildi, kanıt kısa); eleme değildir.
- Çözüm yolları:
  - **Desteklenmiyor:** `calc_on_order_fills`, kütüphane `import` (kaynak pine-facade'den), `heikinashi`, `risk.max_intraday_*`, `matrix` ve `request.security_lower_tf` yorumlayıcıya eklenecek; her biri testle.
  - **Zaman aşımı:** Actions'ta 6 saat sınırı, gerekirse hızlandırma.
  - **Kripto dışı veri:**
    - FX/metal/endeks CFD (OANDA, FX, TVC): Dukascopy ücretsiz dakikalık geçmiş.
    - CME vadeli: Dukascopy endeks/emtia CFD eşdeğeri, yoksa yfinance (60m ≤ 730 gün).
    - ABD hisse/ETF: yfinance gün içi, gerekirse Alpaca/Polygon ücretsiz anahtar (kullanıcı kararı).
    - NSE: yfinance `.NS`; HNX/HOSE: vnstock.
    - Eşdeğer veri `veri` sütununda açık yazılır (Ek 1 kuralı).
  - **Kaynağı kapalı / bulunamadı (33):** eski alfanümerik id ve sayfa üzerinden yeniden aranır. Gerçekten kapalıysa yazarın yayımladığı performans "doğrulanamadı" etiketiyle satır olur ve ayrı raporlanır.
