# U3 erişim ve tarama notları (2026-10-23, Sonnet)

**Durum: 0 kayıt.** `arastirma/U3_mtf.csv` yalnız başlık satırı içerir. Hedef (≥100) karşılanmadı; sayı şişirilmedi. Tarama kısa tutuldu ve tükenmedi (aşağıya bak).

## Erişim

| Site | Ne denendi | Sonuç |
|---|---|---|
| raw.githubusercontent.com | `curl` | Açık (freqtrade-strategies, EternaHybridExchange dosyaları okundu). |
| github.com / api.github.com | `curl` | 403: oturum yalnız `sg-arge` kapsamında; kod/depo araması yok, depo listesi alınamıyor. Açık depolar `git clone`/`ls-remote` ile alınabiliyor ama keşif aracı yok. |
| tradingview.com/script/* | `curl`, WebFetch | Açık; sayfada açıklama okunuyor, Pine kaynağı gömülü değil. Strategy Tester metrikleri yalnız yazarın açıklamasında varsa görünür. |
| forexfactory.com | `curl` | 403. |
| mql5.com, arxiv.org | `curl` | Açık; arama yapılmadı, yalnız WebSearch ile tarandı. |
| quantconnect.com/forum | WebFetch | Açık; ilgili başlıkta kural ve metrik yok. |

## Taranan ve kapıdan dönen adaylar

| Aday | Neden |
|---|---|
| freqtrade/freqtrade-strategies (tüm depo, klonlandı) | `informative`/`resample_to_interval` kullanan 18 dosya incelendi. Strateji001-005, InformativeSample vb. 5m taban + 15m bilgi katmanı (kurulum TF'si 15m, 4H/1H değil). Backtest metriği ve dönem yok (yalnız PatternRecognition'da hyperopt günlüğü, 1d). FReinforcedStrategy / VolatilitySystem: dönem ve metrik yok, kurulum TF'si parametre. |
| TradingView "BTC MTF Engulfing Flip (1H, 2X)" (XGqSzuxJ) | Metrik ve dönem var (PF 4.63, 74 işlem, 2019-09–2026-04), ancak kurulum 1D/4H, **giriş 1H**. Giriş TF'si 15m/5m değil → kapı 1 (tf_sinir_disi kapsamına da girmez). |
| TradingView "GOLD 5MIN 9-21 EMA" (V3f1ZqEE) | Sayfa açılmadı (404 yönlendirmesi); özet düzeyinde yalnız 5m, üst TF katmanı belirsiz. |
| EternaHybridExchange/tradingview-strategies | Tek TF'li klasik göstergeler, "win rate" tablosu dönem ve işlem sayısı olmadan. |
| QuantConnect forum 14493 | Kural ve metrik yok; yazar look-ahead şüphesi bildiriyor. |
| Medium "80% win rate" , HackerNoon SuperTrend, MQL5 job ilanları, CREX/SOICO/OANDA.jp, Edgeful ORB, PineForge blog | Tarif ya da satış; kural/metrik/dönem üçlüsü yok. |

## Neden durdu
12 WebSearch + 6 sayfa getirme + 1 depo klonu sonucunda kapıyı (iki katmanlı TF + metrik + dönem + tanımlı strateji) geçen **tek aday çıkmadı**. WebSearch dar kanal: sonuçlar ağırlıkla eğitim/satış sayfası ve TV liste sayfaları. Hedefe ulaşmak için gereken ek araçlar: (a) GitHub kod araması (kapsam dışı), (b) TV script arama sonuçlarını toplu çekme, (c) belirli depoların listesi. Kapı gevşetilmeden 100'e ulaşılması bu araç setiyle olası görünmüyor.
