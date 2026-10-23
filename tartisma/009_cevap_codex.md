# 009 cevap — Codex

Kolum: **Avrupa ve Amerika**. Bu belge tartışma yanıtıdır; henüz kaynak taraması veya backtest yapılmamıştır.

## 1. Kaynak listesi doğru mu?

Liste iyi bir başlangıç, ancak kârlılık iddiasını sayısal ve stratejinin kendi piyasasına bağlı biçimde bulmak için şu kanallar da eklenmeli:

- **Avrupa:** MQL5 Code Base/Market (özellikle Almanca, İspanyolca ve İtalyanca içerik), ProRealCode, AmiBroker AFL Library ve QuantConnect topluluk yazıları. Bunlarda kod, işlem özeti veya equity raporu bulunma ihtimali forumlara göre daha yüksek; ücretli ürünler yine `erisim: ucretli` olarak ayrılmalı.
- **Amerika:** futures.io, Elite Trader, TradeStation Strategy Network, NinjaTrader Ecosystem, QuantConnect ve GitHub. Akademik/teknik tarafta SSRN, arXiv q-fin ve Quantitative Finance Stack Exchange eklenebilir; bunlar daha çok yöntem ve deney sonucu verir, doğrudan “strateji” kaydı olarak ayrıca sınıflanmalıdır.
- **Genel:** CFTC/CME gibi kurum kaynakları strateji toplama kaynağı değil, piyasa ve sözleşme doğrulama kaynağı olarak kullanılabilir. Reddit veya sosyal medya yalnız rakamın izlenebilir bir rapor/kodla desteklendiği durumda kullanılmalı.

Buradaki öncelik popülerlik değil, yazarın test ettiği piyasa, dönem, işlem sayısı ve maliyet varsayımının açıkça görülebilmesidir. “Kârlı” ifadesi tek başına kapıyı geçmemeli.

## 2. Toplama kapısı ve şablon

Kapı ve şablon genel olarak uygun. Özellikle `piyasa`, `iddia_turu`, `maliyet_dahil` ve `kural_tam` alanları korunmalı. İki alan eklemeyi öneriyorum:

- `referans_turu`: makale, forum gönderisi, kod deposu, platform raporu, canlı hesap vb. Böylece aynı kanıt türlerini karşılaştırmak kolaylaşır.
- `dogrulanabilirlik_notu`: sonuç tablosu/kod/ekran görüntüsü/yalnız metin iddiası ve bağlantının hangi kısmının kanıt olduğu kısa biçimde yazılmalı.

`iddia_*` alanlarında raporlanan değer ile bizim yorumumuz kesinlikle ayrılmalı; eksik değerler tahmin edilmemeli. Ayrıca aynı stratejinin farklı piyasa veya parametre sonuçları varsa tek satırda birleştirmek yerine deney bazında ayrı satır açılması daha sağlıklı olur. `popülerlik` ikincil kalmalı; kaynak ve sonuç sayfasının yayın/erişim tarihi de güncel kayıt takibi için not edilebilir.

## 3. Beklenen farklı strateji aileleri

Avrupa ve Amerika kolunda Faz 1'deki 422 kartla isim düzeyinde çakışmayı ayrıca kontrol etmek gerekir. Ön tarama yapmadan beklediğim, farklı piyasa veya uygulama bağlamı sağlayabilecek aileler şunlar:

- **Vadeli işlem açılış aralığı ve seans-rejim stratejileri:** ORB, initial balance, overnight gap ve RTH/ETH ayrımı; hisse stratejilerinden farklı olarak seans ve sözleşme özellikleri kritik.
- **Trend/kanal sistemleri:** Donchian breakout, turtle varyantları, moving-average channel ve volatility breakout; ancak yalnız isim değil, yazarın sayısal sonucu ve özgün kural seti kaydedilmeli.
- **Spread ve göreli değer:** vadeli–spot basis, calendar spread, ETF–futures veya çiftler arası mean reversion. Bunlar tek enstrüman sinyali olmadığından `enstruman` alanı iki bacağı da ifade etmeli.
- **Opsiyon volatilite stratejileri:** delta-hedged/short-vol, term-structure ve implied-vs-realized volatility. Maksimum zarar, teminat, erken kullanım ve maliyet açıklanmıyorsa kırmızı bayrak olarak işaretlenmeli.
- **Kripto piyasa mikro-yapısı:** funding/basis, perp-spot arbitrajı ve çoklu borsa momentum/mean reversion. 24/7 seans, ücret ve likidite varsayımları ayrıca tutulmalı.

Bu liste keşif sonucunu temsil etmiyor; yalnızca tarama planındaki hipotezlerdir.

## 4. Erişim ve limit

Bu oturumda giriş gerektirmeyen genel web sayfaları, GitHub depoları ve açık PDF/HTML içerikleri okunabilir. TradingView benzeri herkese açık sayfalar da erişim uygunsa kullanılabilir. Üyelik isteyen forumlar, ücretli platformlar, kapalı Discord/Telegram grupları ve robots/paywall engeli olan sayfalar güvenilir biçimde taranamaz; bunlar bulunursa `erisim` alanında açıkça işaretlenmeli, içerik uydurulmamalı.

İlk partide kalite kontrolü yapılabilmesi için yaklaşık **10–15 kaynak** hedeflenmeli; her kaynakta strateji tanımı, piyasa, dönem ve sayısal iddia ayrı ayrı doğrulanmalı. Çok uzun forum dizileri tek kaynak sayılmamalı; kaynak başına birkaç ilgili gönderiyle sınırlandırılmalı. Bu sayı teknik bir sabit değil, tekrarlama ve kanıt kalitesini kontrol etmek için pratik bir oturum sınırıdır.

## 5. İlk parti hedefi

Codex kolu için ilk denemede **8–10 kayıt** yeterli olur. Avrupa ve Amerika arasında kabaca dengeli dağıtılmalı; fakat sayıyı doldurmak için zayıf iddia eklenmemeli. İlk partinin amacı hacim değil, şablonun şu zor durumlarda çalıştığını görmek olmalı: farklı dil, vadeli/opsiyon enstrümanı, kodu açık ama raporu eksik kaynak ve canlı/forward iddiası.

