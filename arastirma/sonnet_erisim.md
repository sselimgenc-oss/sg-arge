# Sonnet kolu erişim notları (T35 ilk parti, 2026-10-23)

Ortam: Claude Code bulut kapsayıcısı, proxy üzerinden dışarı çıkış. `curl` ile köke istek ve WebSearch/WebFetch denendi. GitHub için bu oturumun kapsamı yalnız `sg-arge`; başka depolar okunmadı.

| Site | Ne denendi | Sonuç |
|---|---|---|
| bigquant.com (策略广场 / 研报 `square/paper/*`) | `curl` + WebSearch | **Açıldı.** Broker araştırma raporları metin olarak okunuyor. Bu partinin Çin kayıtlarının hepsi buradan. `wiki/doc/*` bazı sayfalar (örn. 打板追涨停) JS ile yükleniyor, boş döndü. |
| joinquant.com | `curl` köke 200; `post/19837` | Çin dışı IP engeli: "当前地区暂不支持访问". Okunamadı. |
| zhihu.com / zhuanlan | `curl` 302; WebFetch | `curl` giriş sayfası, WebFetch 403. WebSearch özetlerinden rakam görüldü ama sayfa okunmadığı için kayıt yazılmadı. |
| qiita.com | `curl`, API `/api/v2/items` | Açıldı. API arama sonucu az ve gürültülü; kayıtlar WebSearch ile bulundu. |
| zenn.dev | `curl` | Açıldı. Bulunan makaleler (örn. gamella) sonuç göstermiyor ya da kural vermiyor, kayıt çıkmadı. |
| note.com | `curl` | Açıldı. Ücretli bölümler olabilir; okunan sayfalarda tam metin vardı. |
| velog.io | `curl` | Açıldı. |
| brunch.co.kr, blogspot | WebSearch / `curl` | Açıldı. |
| wikidocs.net | `curl` | 403. |
| github.com ve api.github.com | `curl` | 400/403. Ayrıca oturum kapsamı gereği başka depolar okunmadı (örn. Upbit volatilite kırılımı depoları, `ldhbenecia/orbit`). Bu kaynak sınıfı bu partide kapalı. |
| medium.com | `curl` | Cloudflare engeli (403). Hindistan opsiyon stratejileri (920 straddle, short strangle) buradan okunamadı. |
| tradetron.tech (strateji sayfaları `strategy/*`) | `curl`, WebFetch | Sayfalar JS ile yükleniyor, performans verisi gelmedi. `tradetron.tech/blog/*` metin açılıyor ama rakam yok (bkz. elenenler). |
| tradingqna.com | `curl` | Açıldı. |
| streak.tech, chartink.com | yalnız köke `curl` (Chartink 200) | İçerik için derin deneme yapılmadı. |
| fx-on.com | `curl` köke 301 | Yönlendirme izlenmedi; denenmedi sayılır. |
| naver.com (Cafe/Blog) | WebSearch `allowed_domains` | Arama aracı alan adını reddetti (kullanılamaz). |

## Elenenler (kapıdan dönen adaylar)

| Aday | Neden |
|---|---|
| TVExtBot volatilite kırılımı (Qiita `tvextbot/3dc90caabc15`) | Bot/abonelik satışı reklamı, strateji davetli scripte bağlı. |
| Frontier@FX AUD/NZDJPY EA (note) | EA satış sayfası ("割引あり"), kural kapalı. |
| Marketcalls "Yesterday's VWAP" (AmiBroker AFL) | Kural ve kod var ama performans metriği yok (yazı yalnız "maliyet sonrası kârsız" diyor). |
| Tradetron blog "₹50 straddle" | Rakamlı metrik yok, yalnız "30 aylık backtest" ve eğri tarifi. |
| London Breakout (note, siroki5715) | Sonuç negatif (PF 0.75-0.87), kârlılık iddiası yok. |
| 변동성돌파전략 (velog 111sdf) | CAGR %7.94 / MDD %27.78 var ama test dönemi yazılı değil. |
| Zenn gamella (2026 alfa kaybı) | Kural yok, sonuç X paylaşımlarına atıf. |
| note umaki11 "決算またぎ" | Strateji değil, olay çalışması (50.8% isabet); ücretli bölüm. |
