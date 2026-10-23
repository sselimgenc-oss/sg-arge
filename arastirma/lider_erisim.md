# T35 lider kolu: erişim ve verim notu (2026-10-23)

## Erişim (bu bulut oturumu)
- **Açılan:** yalnız `www.tradingview.com` (WebFetch ve curl). Web arama (WebSearch) çalışıyor, ama yalnız sonuç özetini verir; özetteki rakamlar kaynak okunmadan kayda alınmadı.
- **Açılmayan (DNS/proxy):** TradingView bölgesel alt alan adları (`jp.`, `kr.`, `cn.`, `br.`, `in.` ...), qiita.com, smart-lab.ru, quantbrasil.com.br, joinquant.com, ProRealCode, MQL5, ForexFactory, Reddit, QuantifiedStrategies, Elite Trader, Forex Station.
- Bölgesel içerik www üzerinden piyasa adıyla arandı: Nikkei, KOSPI, Nifty/BankNifty, mini índice, Bovespa, MOEX, DAX, VN30, Hang Seng, FTSE, "profit factor", "backtest results".

## Verim
| Adım | Sayı |
|---|---:|
| Açılan strateji/fikir sayfası | ~30 |
| Kapıyı geçen (rakam + dönem) | 4; biri (BIST30 → S&P 500 ATR Momentum Rider) Faz 1 tekrarı çıktı (A1-019), listeden çıkarıldı. Kalan 3 |
| Rakam var, dönem yok (geçmedi) | 3: Line Break (Mizuki32, Nikkei dahil PF tablosu), Bank Nifty Five Rounds (yalnız beklenti), Nikkei 12H ALMA (Goldfinch_song; sinyal satıcısı, dönem yok) |
| Rakam yok | ~23 |

**Bulgu:** TradingView yazarlarının büyük çoğunluğu performansı açıklamaya yazmıyor; rakamlar yalnız JavaScript ile çizilen Strategy Tester panelinde. Bu panel sayfa metninde yok, bu yüzden okunamıyor. TradingView bu toplama amacı için **düşük verimli** bir kaynak: ~%13 geçiş.

Rakam veren yazarlar çoğunlukla kurumsal: aracı kurumlar (DNSE Vietnam, Genial Investimentos Brezilya) ya da araştırma tarzı yazanlar (newton61).

## Öneri (ikinci parti için)
- Benim kolumda TradingView'e devam etmek pahalı (kayıt başına ~7 sayfa). Aracı kurum hesapları (DNSE, Genial, Lab106 KOSPI gibi) ve "held-out/out-of-sample" kelimeleriyle hedefli arama sürdürülebilir.
- Bölgesel kaynaklar (JoinQuant, QuantBrasil, Qiita) bu oturumdan açılmıyor. Sonnet/Codex/Argon kolları ve kullanıcının sohbet uygulamaları bu yüzden daha önemli.
- Faz 1'de olmayan yeni bir bölge çıktı: **Vietnam (VN30 vadeli)**. DNSE ve PhaisinhOnline/Khanhtq26 serileri 30+ açık kodlu strateji içeriyor, ama çoğu rakamsız.
