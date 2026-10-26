## 1) Bu kapı adil mi?

**İyi stratejiyi haksız yere eliyor (false negative) — en önemliler:**
- **Tek kriter net getiri > 0**: düşük frekanslı ama pozitif beklenen değerli stratejiler, kısa/gürültülü örneklemde negatif çıkıp elenebilir.
- **“Tek enstrümanda yılda ≥30 işlem” elle eleme kuralı**: trend takip gibi seyrek ama geçerli stratejileri haksız yere atar.
- **Yazarın kendi sembolü/zaman dilimi**: yazar seçim yanlılığı (symbol snooping) kalır; yayın tarihi sonrası test bunu tamamen çözmez.
- **2023–2026 ağırlıklı dönem**: yükseliş rejiminde negatif çıkan, ama başka rejimde iyi olan stratejiler elenebilir.
- **Maliyet modeli sabit ve kaba**: likiditeye/volatiliteye duyarlı slippage yok; bazı stratejiler haksız yere geçer/geçemez.
- **Post-hoc elle filtreler** (PF, p10, korelasyon vb.): eşikler test sonuçları görüldükten sonra uygulanıyorsa data snooping riski.

**Kötü stratejiyi haksız yere geçiriyor (false positive) — en önemliler:**
- **Long-only stratejiler yükselen piyasada beta ile para kazanır**: net getiri > 0, piyasa etkisi ayrıştırılmadığı için “beceri” yerine “piyasa maruziyeti” ödüllendirilir.
- **Risk/drawdown/queue görmezden gelinir**: yüksek varyanslı, tesadüfen pozitif ortalama yakalayan stratejiler geçebilir.
- **Yayın yanlılığı + çoklu test**: 933 strateji test edilip “geçenler” seçilmesi, tesadüfen iyi görünenleri seçme yanlılığı yaratır; DSR sadece bilgi amaçlı.
- **Survivorship bias**: ücretsiz veri olmayan 401 strateji (genelde daha az likit/delist) dışarıda; test evreni seçilmiş.
- **Kısa paper trade (26 hafta)**: rejim değişimi ve tail risk yakalanamayabilir.

## 2) “Net getiri > 0” uygun mu? Rastgele strateji geçme olasılığı?

**Uygun değil (tek başına).** Özellikle long-only ve yükselen piyasada rastgele giriş de pozitif getiri üretebilir.

**Ölçüm yöntemi (plasebo testi):**
- Aynı evren, maliyet, dönem ve işlem frekansı ile **rastgele sinyal** stratejileri (random entry/exit, buy-and-hold benzeri holding) üret.
- N (örn. 10.000) simülasyon; net getiri dağılımını çıkar.
- **Geçme olasılığı = P(net getiri > 0)**. Ayrıca “kaç trade, ne kadar süre” koşullarını sabitle.
- Raporla: medyan, 95. persentil, false positive oranı.

**Daha iyi geçme şartı (öneri):**
- Net getiri > 0 **ve**
- benchmark (beta) ayarlı alfa > 0 (t-stat anlamlı) **ve**
- Sharpe/Sortino eşiği (örn. > 0.5) **ve**
- max drawdown ≤ %20 (veya benchmark DD’den düşük) **ve**
- işlem sayısı ve süre minimumları.

## 3) Seçim yanlılığı: hangi düzeltme en pratik?

- **Plasebo/rastgele strateji testi**: en sezgisel ve doğrudan; null dağılımı kalibre eder. **Pratikte ilk adım olarak önerilir.**
- **DSR (Bailey & López de Prado, 2014)**: Sharpe’ı deneme sayısına ve çarpıklık/basıklığa göre “deflate” eder; tek strateji düzeyinde iyi.
- **BHY (Benjamini & Yekutieli, 2001)**: çok sayıda hipotezde FDR kontrolü; konservatif ama uygulanabilir.
- **White’s Reality Check (2000)**: en iyi stratejiyi benchmark’a karşı, data snooping düzeltmeli test eder; ağır ama final seçime uygun.
- **Hansen SPA (2005)**: Reality Check’in daha güçlü versiyonu; superior predictive ability için.

**Pratik öneri (kademeli):**
1. Plasebo ile false positive oranını ölç ve kalibre et.  
2. Her strateji için DSR hesapla (bilgi değil, gate’e dahil et).  
3. Aday seti için BHY/FDR (q=0.05) uygula.  
4. Final 10–20 strateji için White RC / Hansen SPA ile benchmark’a karşı doğrula.  
5. Kural/eşikleri **önceden kaydet** (pre-registration) to avoid post-hoc.

Kaynaklar: Bailey & López de Prado (2014) DSR; Bailey et al. PBO/CSCV (2015/2016); White (2000); Hansen (2005); Benjamini & Yekutieli (2001); Harvey, Liu & Zhu (2016) multiple testing.

## 4) Yükselen piyasada long-only: piyasa etkisi nasıl ayrıştırılır?

- **Buy-and-hold karşılaştırması**: basit ama riski/betayı görmez; yetersiz.
- **Beta-ayarlı alfa (CAPM/multi-factor)**: daha doğru; Jensen alfası, faktör regresyonu (market, size, value, momentum). Kısa dönem beta tahmini gürültülü.
- **Pratik öneri**: 
  - Evren-bazlı benchmark (hisse: SPY/QQQ, kripto: BTC/ETH, emtia: ilgili endeks).
  - **Beta-adjusted excess return** + **t-stat** gerektir.
  - Ek olarak **upside/downside capture** ve max DD karşılaştırması.
  - “Rastgele long” baseline ile de karşılaştır.

## 5) Farklı test süreleri (6 ay–3 yıl) adil karşılaştırma

- Ham getiriyi karşılaştırma; **yıllıklaştırılmış getiri + risk** kullan.
- **Trade sayısı ve süre minimumları** belirle (örn. ≥100 trade ve ≥2 yıl) **veya** t-stat/CI alt sınırı > 0 (kısa örneklemi otomatik cezalandırır).
- **Walk-forward/rolling pencereler**: her pencerede pozitiflik oranı gerektir (örn. ≥3 pencereden 2’si pozitif).
- **Alt dönem stabilitesi**: profit factor ve drawdown rejimler arası tutarlı olmalı.

## 6) ML binlerce fikir üretirse kapıda ne bozulur? Nasıl tasarlanmalı?

**Bozulanlar:**
- False positive patlaması; gate’e overfit; Goodhart (metrik hedef olunca oyunlaştırma).
- Look-ahead/repainting, survivorship, data snooping; kapasite/likidite ihmal.
- Rejim tek taraflılığı (2023–2026).

**Tasarım:**
- **Ayrı veri kümeleri**: araştırma (train) / OOS test / paper (live) katı ayrımı; test setine iteratif dokunma yok.
- **Purged & embargoed CV** (López de Prado, 2018) for time series.
- **Otomatik nedensellik/look-ahead testleri** + deterministic replay.
- **Survivorship-bias-free, point-in-time veri** (delistings dahil).
- **Gerçekçi maliyet + kapasite modeli** (slippage, fees, funding, ADV limiti).
- **Çoklu test düzeltmesi** (DSR, FDR, plasebo) ve **PBO (CSCV)** ile overfitting olasılığı.
- **Rejim çeşitliliği** (bull/bear/sideways, kriz dönemleri) + stres testi.
- **Pre-registration** of rules/thresholds.
- **Paper trade** final gate (26 hafta+), decay monitoring.

## 7) Benim önereceğim kapı (somut)

1. **Veri**: survivorship-bias-free, point-in-time, delistings dahil; sabit evren; maliyet modeli (fee + slippage ADV/vol bazlı).  
2. **Nedensellik**: otomatik lookahead/repainting testleri; gelecek veri yok.  
3. **Pre-registration**: kurallar/eşikler/evren/dönem test öncesi kilitlenir.  
4. **Araştırma (in-sample)**: fikir üretimi/parametre seçimi burada; test setine dokunulmaz.  
5. **OOS (sabit dönem + stres)** koşulları:
   - Yıllıklandırılmış benchmark-ayarlı alfa > 0 ve t-stat anlamlı  
   - Sharpe > 0.5, max DD ≤ %20 (veya benchmark’tan düşük)  
   - ≥ 100 trade ve ≥ 2 yıl (veya CI alt sınırı > 0)  
   - Walk-forward: ≥3 pencereden ≥2 pozitif  
   - Profit factor ≥ 1.3; 2x maliyet senaryosunda hâlâ pozitif  
6. **Çoklu test**: DSR > 0.95? (deflated Sharpe pozitif/anlamlı), BHY FDR q=0.05, plasebo geçme oranı < %5, PBO < 0.5.  
7. **Sağlamlık**: parametre pertürbasyonu ±20% ile sonuç işaretinin korunması; korelasyon >0.6 olanlardan biri elenir.  
8. **Kapasite**: ortalama pozisyon ADV’nin %1’inden küçük.  
9. **Paper trade**: 26 hafta canlı veri; önceden belirlenmiş kriterlerle final karar; bozulma izleme.

**Özet:** Mevcut kapı “net getiri > 0” ile yükselen piyasada long-only stratejileri aşırı geçirir ve çoklu test seçim yanlılığını yeterince düzeltmez. En kritik eksikler: piyasa etkisi ayrıştırma, risk/drawdown, sample-size duyarlı istatistik, survivorship-bias-free veri, pre-registration.