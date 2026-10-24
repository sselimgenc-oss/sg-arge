# TV-2: 942 TradingView stratejisi, yazarın kendi koşullarında (eleme hunisi yok)

**Karar (kullanıcı, 2026-10-24):** "Kendi timeframe'imi ya da piyasamı istemiyorum; 942 stratejiyi kendi timeframe'inde, kendi mantığıyla test edelim. Huni yok."
**Kaynak:** `arastirma/U5_tv.csv`, `suzgec_sonucu` = `elendi:tf_disi` (942) + `elendi:tf_belirsiz` (60). Pine kodu: `pine-facade.tradingview.com/pine-facade/get/<PUB>/last` (U5 yöntemi).

## 1. Test koşulları = yazarınki
- **Piyasa:** script sayfasındaki yayın sembolünün kendisi (BTCUSDT, XAUUSD, SPX, EURUSD, tek hisse…). Evren havuzuna taşınmaz, sınıf eşlemesi yok.
- **Zaman dilimi:** yayın aralığı (1m…1W).
- **Mantık:** Pine kodu birebir: long **ve short** bacaklar, `strategy.entry/exit/close`, stop/limit/izleyen stop, `qty_percent` kısmi çıkışlar, `pyramiding`, takvim/seans filtreleri.
- **Boyut ve maliyet:** yazarın `strategy()` ayarları (`initial_capital`, `default_qty_type/value`, `commission`, `slippage`). Rapora ek bir sütun: aynı işlemler **gerçekçi maliyetle** (kripto %0,1/taraf, diğerleri %0,05/taraf + 1 tick kayma); yazar maliyet girmediyse bu sütun asıl bakılacak olandır.
- **Dolum:** TradingView strateji test aracı semantiği (`process_orders_on_close=false`: sinyal bar kapanışı, dolum sonraki açılış; stop/limit bar içi; aynı barda stop/hedef belirsizliğinde kötümser sıra).

## 2. Eleme yok, rapor var
Her strateji için tek satır: işlem sayısı, net kâr %, PF, kazanma oranı, en büyük düşüş, Sharpe, ortalama işlem, al-tut getirisi (aynı sembol, aynı dönem). Bilgi amaçlı ek sütunlar (eleme değil): son 2 yılın ayrı sonucu, maliyet 2x sonucu. Tablo net kâra ve PF'ye göre sıralanır; **seçimi kullanıcı yapar.**

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
