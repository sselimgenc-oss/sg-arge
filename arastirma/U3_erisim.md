# U3 erişim ve tarama notları (Sonnet, 2026-10-23; tur 2 – kod izinden arama)

Kayıt sayısı bu sürümde: **53** (parti 1: 50, parti 2: +3, MTF-051..053) (`arastirma/U3_mtf.csv`). Hedef ≥100; aşağıdaki "Durma nedeni" bölümüne bak.
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

## 5. Durma nedeni (ara sürüm, parti 1 sonu: 50 kayıt)

Ana darboğaz kaynak sayısı değil, kaynakta **iki katmanlı TF + tam kural** bir arada bulunması: açık Pine betiklerinin %0,5'i (yaklaşık 3207 açık strateji içinden 21), freqtrade dosyalarının %5'i (≈400 dosyadan 20) ve MQL5 EA'larının %0,1'i bu kapıyı geçiyor. Otomatik süzgeç TradingView ve freqtrade için büyük ölçüde tükendi; 100'e ulaşmak için ProRealCode forum taraması, Qiita/Zenn ve bölgesel kaynaklar sürüyor.


## 6. Parti 2 (MTF-051..053): ek tarama ve durma nedeni

Lider yönergesi: kripto payını artır; ProRealCode forum ikinci geçişi, Qiita/Zenn/note, velog, BigQuant, smart-lab; sürümleri çoğaltma; `tf_sinir_disi` ≤ 10 (şu an 2).

| # | Kaynak | Ne denendi | Sonuç | Kayıt |
|---|---|---|---|---|
| 24 | TradingView `pubscripts-suggest-json?type=2` | 5284 sorgu; 3207 açık strateji kaynağı `pine-facade` ile okundu; zincirleme bağımlılık süzgeci + kullanıcı fonksiyonu içinde `request.security("60")` | 8 yeni aday, +2 (fonksiyon sarmalı) = 10; el okuma: 1 alındı (Weekend Hunter, kripto), 1 fonksiyon-sarmalı BTC betiği (eIRzdfgo) grafik TF'si 60 → elendi | 1 |
| 25 | TradingView, "grafik barlarında HTF kapanış serisi üzerinden gösterge" kusuru | G3BQYazv, tPyR1wRW, GOwfPvo1 | HTF "kapanış" serisi 15m barlarına yayılıp chart-TF periyoduyla hesaplanıyor → gerçek 4H/1H göstergesi değil, elendi | 0 |
| 26 | TradingView Caldera Meridian, Pro Scalper v9, DeFiers-SMC, Squared9 | tam okuma | HTF 100 puanlık skorda 1/7-8/100 ağırlık (kurulum katmanı değil) ya da çok katmanlı Gann/Markov skoru → elendi | 0 |
| 27 | Qiita API (9 sorgu × ≤3 sayfa = 219 yazı) | gövde, TF çifti + kod + kural süzgeci | 24 eşleşme: hepsi gösterge anlatımı / AI yazıları, strateji kuralı yok | 0 |
| 28 | Zenn API (20 konu, 374 yazı) | gövde süzgeci | 9 eşleşme: doğrulama günlüğü, strateji adı/kuralı gizli ("fx-strategy-5-rejected") ya da gösterge testi | 0 |
| 29 | note.com API (20 etiket × ≤10 sayfa = 7074 not) | gövde süzgeci | 405 eşleşme; el taraması: günlük piyasa yorumu, MT4/TV tanıtım; kuralı + 1H/15m olan: "Giorno-shiki" (yalnız 1H), "Gold 4 kural" (1m/5m/1H ayrı, 1H tek başına) → alınmadı | 0 |
| 30 | velog (GraphQL), BigQuant, smart-lab.ru | T35 notlarındaki yöntemler | bu turda MTF kodlu kripto yazısı için sorgu yapılmadı: aynı tür sonuçlar (görsel sonuç, tek TF) T35'te görülmüştü; **tamamlanmadı** | 0 |
| 31 | ProRealCode forum, 2. geçiş | anahtar sözcükle süzülmüş ~7 360 konu, `TIMEFRAME(1 hour/4 hours)` + piyasa emri | ~70 konu; yardım istekleri ve DAX/endeks MTF örnekleri (cowabunga, daxophone vb.); kripto yok, kod blokları HTML'de kaçışlı; el okumada kural tam bir strateji ayıklanamadı | 0 |
| 32 | jesse-ai/example-strategies, jesse-ai/jesse | klon, `get_candles`/`timeframe` taraması | tek TF'li örnekler | 0 |
| 33 | hummingbot/hummingbot (controllers/directional_trading) | klon | her denetleyici tek mum aralığı | 0 |
| 34 | Drakkar-Software/OctoBot-Tentacles, nautechsystems/nautilus_trader, freqtrade/freqtrade (çekirdek) | klon | OctoBot: zaman dilimi yapılandırması, kural yok; Nautilus/freqtrade: şablon | 0 |
| 35 | dev.to API (30 etiket, 8752 makale) | gövde süzgeci | 13 eşleşme, hiçbirinde tam kural yok ("basitleştirilmiş") | 0 |
| 36 | AdvancedFuturesSwingStrategy (Chris6622) | tam okuma | 1H+4H+1D rejimi + 15m dört kollu mantık, kural tam → alındı (MTF-051) | 1 |
| 37 | AI MES Globex (lylerh) | tam okuma | alındı (MTF-053); Asia/London/Structure Break aynı motor, ayrı sayılmadı | 1 |

**Sayım:** 53 kayıt (kripto ve karma kripto ~27; kalan: FX/altın/gümüş, endeks vadeli, piyasası belirtilmemiş).
**Neden 100'e ulaşılamadı:** açık kaynak MTF stratejilerin kapıyı geçme oranı çok düşük (TradingView ~%0,7; freqtrade ~%5; MQL5 ~%0,1; forum/blog kaynaklarında kural tam + iki katmanlı TF birlikte hemen hiç yok). Aynı strateji sürümlerini ayrı sayma yasağı nedeniyle freqtrade/NFI/Cluc/Ichi/Elliot aileleri tek kayıtta kaldı. Kalan kaynaklar (velog, BigQuant, smart-lab) için yöntem T35'te biliniyor ama bu turda MTF kodu içeren yazı bulma beklentisi düşük; denenirse parti 3.
