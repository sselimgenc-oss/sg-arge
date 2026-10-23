# 010: T35 ilk parti değerlendirmesi (lider)

Tarih: 2026-10-23. Durum: Sonnet bekleniyor; Codex, Argon ve lider kolları teslim etti.

## Özet
| Kol | Dosya | Kayıt | Kaynak çeşitliliği | Kalite | Lider doğrulaması |
|---|---|---:|---|---|---|
| Argon (Afrika, G. Amerika) | `arastirma/argon.csv` | 12 | QuantBrasil 10, Atlas Chile 1, mdingi (JSE) 1 | **İyi.** Kural tam, Python kodu, işlem sayısı ve dönem var | **Yapılamadı.** Siteler bu oturumdan açılmıyor; arama motoru da sayfaları bulamadı. Kullanıcı 2 linki tarayıcıda kontrol edecek |
| Codex (Avrupa, Amerika) | `arastirma/codex.csv` (PR #118) | 10 | **Yalnız arXiv** | Orta. 5'i ML/derin öğrenme (kural kısmen), 2'si tick verisi, 1'i yılda 1 işlem | Kısmen. 2206.12282'nin varlığı ve dönemi (2015-01-01 → 2021-08-28) doğrulandı |
| Lider (TradingView) | `arastirma/lider.csv` | 3 | TradingView | Zayıf-orta. ~30 sayfa okundu, 4 geçti; biri Faz 1 tekrarı (A1-019) olduğu için çıkarıldı | Kendisi okudu |
| Sonnet (Çin, Japonya, Kore, Hindistan) | — | — | — | Bekleniyor | — |

Toplam: **25 kayıt** (Sonnet hariç).

## Bulgular
1. **Argon en verimli kol çıktı.** QuantBrasil, Brezilya'da tam kurallı, kodlu ve rakamlı yazılar yayınlıyor. Tam aradığımız profil. B3 hisse ve WDO/WIN vadelisi kapsıyor. Yeni aileler: Saudade de Casa (açılış bandı dışı + teyit), Candle Pavio (Stormer), Gap Trap (WDO).
2. **Codex yalnız arXiv'e bakmış.** `codex_erisim.md` "açılamayan site yok" diyor; yani forumlar ve bölgesel siteler denenmemiş. Akademik kayıtlar değerli, ama makalelerin çoğu ML modeli (LSTM-ARIMA, DDPG, derin özellikler). Bunlar mekanik kartla test edilemez. Ayrıca MACD+RSI (US-002..004) Faz 1'deki ailelerle akraba.
3. **TradingView düşük verimli** (`arastirma/lider_erisim.md`): yazarlar rakamı açıklamaya yazmıyor, rakam JavaScript panelinde. Rakam yazanlar çoğunlukla aracı kurumlar (DNSE Vietnam, Genial Brezilya).
4. **Faz 1 tekrar kontrolü işe yarıyor:** lider kolunda 1 tekrar yakalandı. Argon'un SA-002a/b (IFR2 = Connors RSI2) kayıtları aile olarak Faz 1'de var (B3-010, M008, M014), ama piyasa (LREN3, B3) ve filtre (SMA50 eğimi) farklı. Kayıt kalır, `faz1_tekrar: supheli` olarak işaretlendi.
5. **Hiçbir kayıtta maliyet tam dahil değil.** Tek istisna AF-001 (bacak başına 10 bps). AF-001 maliyet sonrası yıllık %0,3 net ile dürüst, ama kârlı sayılmaz.

## Kayıt bazında dikkat
- **SA-007 (Atlas Chile):** Temel analiz skoruyla aylık portföy. 9.678 "gözlem" işlem değil. Ürün platformu. `kirmizi_bayrak` eklendi.
- **SA-006 (Gap Trap WDO):** 37 işlem, ~1,4 yıl. Az örnek.
- **SA-004a (Maximas e Minimas):** 6 yılda %232, tek hisse (EQTL3), maliyetsiz. Aşırı iyi; doğrulama öncelikli.
- **EU-001/002 (Tube osilatörü):** Tick/saniye verisi, iterasyon izi. Test için veri yok.
- **EU-006:** Yılda ortalama 1 işlem. Kapıyı kâğıt üzerinde geçiyor ama pratik değeri yok.
- **US-002..004:** "P&L 1,11 / 1,40 / 1,24" büyük ihtimalle kâr/zarar oranı; PF değil. Codex ikinci partide birimi netleştirsin.

## İkinci parti için öneriler (kullanıcı onayına)
1. **Argon:** QuantBrasil'de devam etmeli (yüksek verim). Ek olarak Meksika, Kolombiya, Şili kaynakları. Hedef 15.
2. **Codex:** arXiv'i bırakmalı. smart-lab.ru, wallstreet-online, ABC Bourse, Trade2Win, X-Trader, AmiBroker AFL, TradeStation Strategy Network denemeli; açamadıklarını `codex_erisim.md`'ye yazmalı. ML kayıtları yalnız `motor_notu: ml` ile, en fazla 2 tane.
3. **Lider:** TradingView'de yalnız aracı kurum hesaplarını ve "held-out / out-of-sample" ifadelerini hedeflemeli.
4. **Sonnet:** teslimi bekleniyor.

## Kullanıcıdan istenen (uydurma denetimi)
Argon kayıtlarını bu oturum açamıyor. Lütfen tarayıcıda şu iki sayfayı aç ve rakamları kontrol et:
- SA-006: https://quantbrasil.com.br/blog/backtest-da-estrategia-de-gap-trap-de-compra-ou-venda/ (37 işlem, %59,46, 25.250 R$)
- AF-001: https://mdingi.co.za/work/jse-statistical-arbitrage (262 işlem, maliyet öncesi Sharpe 0,74/0,64)

İkisi tutarsa Argon partisi kabul edilir.
