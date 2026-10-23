# U3 erişim ve tarama notları (Sonnet, 2026-10-23; tur 2 – kod izinden arama)

Kayıt sayısı bu sürümde: **50** (`arastirma/U3_mtf.csv`). Hedef ≥100; aşağıdaki "Durma nedeni" bölümüne bak.
Ortam: bulut kapsayıcısı, çıkışlar proxy'den. `raw.githubusercontent.com` ve `git clone` (açık depolar) çalışıyor, `github.com/api` ve HTML sayfaları oturum kapsamı dışında 403.

## 1. İncelenen kaynaklar (depo / platform / sayfa grubu) ve sonuç

| # | Kaynak | Ne denendi | Bulunan / sonuç | Kayıt |
|---|---|---|---|---|
| 1 | freqtrade/freqtrade-strategies (resmi) | klon, `@informative`/`informative_pairs` taraması | Strategy001-005, multi_tf vb.: 5m + yalnız 15m bilgi katmanı; Faz 1'de zaten var (A3-010/012). | 0 |
| 2 | werkkrew/freqtrade-strategies | klon, 30+ dosya (Schism, Solipsis, Hacklemore, Lateralus, Fakebuy, Stinkfist, XtraThicc, Enchilada…) | 1H/4H bilgi katmanı + 5m/15m giriş; Enchilada'da `X` yer tutucu eşik (kural tam değil) elendi; Schism/Solipsis sürümleri tek kayıt (+SchismLess 4H/15m b-kaydı) | 8 |
| 3 | behradhesami/Projects | klon | multi.py (1H+15m+5m); multiOpt/Momentum_OPT multi'nin parametre varyantı, alınmadı | 1 |
| 4 | Stibra1/Multitimeframe_bot | klon | 5m/15m/1h/1d sinyalleri VEYA ile birbirinden bağımsız → kurulum+giriş katmanı yok | 0 |
| 5 | remiotore/freqtrade (≈400 strateji) | klon, otomatik tarama (taban TF + HTF sütunu girişte kullanılıyor mu) + el okuma | ~120 dosya HTF sütununa dokunuyor; çoğu NFI/Cluc/Ichi/Elliot ailesi; 1H "trend_close_1h" = 5m EMA(12) sahte-MTF (naruto, brawbot, Ichi serisi, LSV2, AlvinchenV1, Advanced_Ichimoku, NimmV20) elendi | 9 |
| 6 | TheoBrigitte/freqtrade (1.4 GB) | klon, otomatik tarama | cluc/bigz/nasos/nfix aileleri; FVGAdvanced, slownsteady alındı; Danke/GeneTrader/twinturbo 40-130 KB, kural tek anlamlı özetlenemedi | 2 |
| 7 | XQuant42/ft_pantheon | klon | remiotore ile büyük ölçüde aynı ailesel dosyalar; CombinedBinHClucAndMADV6, SafeCluc alındı | 2 |
| 8 | erdincyasar/freqtrade_kanaxe, ntsd/freqtrade-configs, rukikotoo/ReadingNote, Ilovecodinghhh/Astock, hamidreza07/freqai-strategy, KidsSeeGhxsts/TradingBot, BuyMeAnIcecream/freqtrade-strategies, WhatATragedy/FreqTrade, mrgolfprat/ft_sample, cnacha/freqtrade-docker, phuchust/freqtrade_strategy | klon + otomatik tarama | NFI/BinHCluc/BigZ/Elliot kopyaları (kayıtlı ailelerin sürümleri) | 0 |
| 9 | BastiKopo/freqtrade | klon | EmaMaCrossoverStrategy (15m + 1H rejim) | 1 |
| 10 | Chris6622/…AdvancedFuturesSwingStrategy | klon | 15m + 1H/4H/1D; 4 kollu order-flow/Wyckoff mantığı, tanımlar çok uzun; alınmadı | 0 |
| 11 | iterativv/NostalgiaForInfinity, nateemma/strategies | — | Faz 1'de A3-013 / A3-014; dosyalar 0,2-2,6 MB | 0 |
| 12 | tripolskypetr/backtest-kit + npm `@backtest-kit/sidekick` | klon, jsdelivr dosya listesi, `.pine` kaynakları | sidekick: 4H rejim + 15m EMA kesişimi; example/ klasöründeki 9 örnek: LLM/Polymarket/NN/DCA, MTF yok | 1 |
| 13 | EternaHybridExchange/tradingview-strategies | README | tek TF'li klasik göstergeler | 0 |
| 14 | TradingView (listeler) | 340 etiket + 1900 arama terimi, `script_type=strategies&script_access=open` sayfaları → 4913 bağlantı | 4635 sayfa PUB kimliği → `pine-facade` ile Pine kaynağı okundu | — |
| 15 | TradingView `pubscripts-suggest-json` | 5284 sorgu, `type=2` (strateji) | 3207 açık kaynak strateji; kaynak `pine-facade` ile çekildi; 52'si zaten listelerde; yeni aday 8 | — |
| 16 | TradingView otomatik süzgeç | "HTF literal 60/240 (ya da input varsayılanı) giriş koşulunun bağımlılık kapanışında mı" + grafik 5/15 dk (yayın aralığı ya da metin) | 60 aday; el okumada 21 alındı | 21 |
| 17 | MQL5 CodeBase | `mt5/experts` ve `mt4/experts` listeleri (en çok 43 sayfa/liste → 2874 EA), `.mq4/.mq5` indirildi | 129 dosyada PERIOD_H1/H4 + M5/M15 geçiyor; 29'unda çağrılarda ikisi birden; 4 alındı | 4 |
| 18 | ProRealCode | sitemap: yazılar+snippet (2087 sayfa) tam tarandı; forum konuları (25 421) kısmen (bkz. 4) | `TIMEFRAME(1 hour/4 hours)` içeren 34 yazı; 3 strateji alındı (KAMA & SMA DAX Faz 1 tekrarı olduğundan düşüldü) | 3 |
| 19 | dev.to API | 30 etiket, 8752 makale gövdesi | TF çifti + kural + kod bulunan 13; hiçbiri tam kural vermiyor (eğitim/tanıtım, "bu basitleştirilmiş" ibareli kod) | 0 |
| 20 | arXiv API | 7 sorgu (multi-timeframe, higher timeframe, 4-hour/15-minute vb.) | yalnız sinir ağı tahmini makaleleri; kural tam değil | 0 |
| 21 | QuantConnect forum 14493 | sayfa | kural/metrik yok, yazar look-ahead şüphesi | 0 |
| 22 | WebSearch ≈ 35 sorgu (EN/JP/ZH/RU/ES/KO) | genel + kod izi | eğitim/satış sayfaları; kaynak kodu açık olan tek yeni bulgu: sidekick | — |
| 23 | Qiita, Zenn API | erişim denendi | açık; MTF kodlu yazı için sorgu yapılmadı (tur 3'e bırakıldı) | — |

## 2. Açılamayan / kullanılamayan siteler

| Site | Denenen | Sonuç |
|---|---|---|
| github.com/* (API ve blob HTML) | `curl` | 403 (oturum kapsamı); kod `raw.githubusercontent.com` ve `git clone` ile okundu |
| forexfactory.com | `curl` | 403 |
| reddit.com | `curl` (JSON) | 403 "Blocked" |
| tradingview.com `/u/<kullanıcı>` | `curl` | betikler JS ile yükleniyor, listelenemedi |
| TradingView korumalı/davet-yalnız betikler | — | kaynak yok → kapsam dışı |
| Medium, mql5.com forum, ctrader.com algos | — | denenmedi / kod giriş ister |

## 3. Kapıdan dönen adaylar (örnekler ve nedenler)

| Neden | Örnek |
|---|---|
| 1H/4H yalnız gösterge ya da koruma (girişte yok / sahte MTF) | Stibra1 Multitimeframe, naruto, brawbotv2, Ichi serileri, LS/LSV2, NASOSv4 (1H yalnız pompa filtresi), 24ocak_2025_ozgur (1H EMA200 kodda yanlış hizalanmış, `informative` 15m veri çerçevesine indeksle atanıyor) |
| Kural tam değil / yer tutucu | Enchilada (`X`), BBandRsi (çıkış fonksiyonu `buy` atar) |
| Giriş TF'si 1D/1H (2H+ ya da 4H giriş) | BTC MTF Engulfing Flip (1D+4H kurulum, 1H giriş), Pivot_tuned (1d), ADX_PRICE_WTDCA (giriş tamamen 4H) |
| HTF yalnız tabloda | 9x9ohJ2R santoshpsiii Crypto Algo, s1ufMqI5 Myth-Busting #1, n9ty3SVh Quantum Edge |
| HTF kapanış serisinden chart-TF MACD/EMA hesabı (gerçek HTF göstergesi değil) | G3BQYazv BB+SMI+4H MACD açısı, tPyR1wRW MTF MACD+AC, GOwfPvo1 ARSI (EMA'yı HTF kapanış serisi üzerinde grafik barlarıyla hesaplıyor) |
| Aşırı karmaşık / kural tek anlamlı özetlenemiyor | Squared9 Pro (Gann karesi), AI MES Globex/Asia/London (seans aralığı çatalı), Hungpixi MACD MTF, DeFiers-SMC, Aegis, dualwave/battletank (oy skorlama), RRS Impulse |
| Giriş TF'si belirsiz (grafik aralığı kullanıcıya bağlı) | Triple MA HTF (HTF varsayılan 15), NEtMdbmJ MTF Trend Alignment, SmartMoney AOI (1m yayın) |
| Satış / tanıtım / yalnız fikir | Edgeful ORB, PineForge blog, MQL5 market listeleri, Medium "80% win rate" |
| Tekrar | KAMA & SMA Trading System DAX mtf (ProRealCode) = Faz 1 O1-047 (URL aynı; Faz 1'de "kaynak okunamadı" idi) — tekrar sayıldığı için kayıt dışı bırakıldı |

## 4. Devam eden / tamamlanmayan tarama

- ProRealCode forum konuları: 25 421 URL'den ~3 050'si ilk geçişte tarandı; kalan ~7 300'ü (anahtar sözcükle süzülmüş) ikinci geçişe alındı.
- Qiita/Zenn/note/velog: MTF kodlu yazı araması yapılmadı.
- TradingView: korumalı olmayan ama listelerde/öneri API'sinde görünmeyen betikler (uzun kuyruk) kapsam dışı.

## 5. Durma nedeni (ara sürüm, 50 kayıt)

Ana darboğaz kaynak sayısı değil, kaynakta **iki katmanlı TF + tam kural** bir arada bulunması: açık Pine betiklerinin %0,5'i (yaklaşık 3207 açık strateji içinden 21), freqtrade dosyalarının %5'i (≈400 dosyadan 20) ve MQL5 EA'larının %0,1'i bu kapıyı geçiyor. Otomatik süzgeç TradingView ve freqtrade için büyük ölçüde tükendi; 100'e ulaşmak için ProRealCode forum taraması, Qiita/Zenn ve bölgesel kaynaklar sürüyor.
