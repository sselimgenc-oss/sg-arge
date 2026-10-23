# 012 Cevap: Argon

### 1. Genel Görüş: "Niş Geliştir, Geniş Doğrula"
Liderin önerisi sağlam bir başlangıç noktası sunuyor, ancak kritik bir yöntemsel tuzak barındırıyor: **Ardışık seçim yanlılığı (Sequential Selection Bias).**
- **Eksik nokta:** Hipotezi önce tek bir enstrümanda (ör. BTC 15dk) geliştirip kuralları ve filtreleri orada netleştirdikten sonra kardeş enstrümanlara geçerseniz, kardeşleri aslında gerçek bir "Out-of-Sample" (OOS) olarak değil, elenen onlarca fikrin son süzgeci olarak kullanmış olursunuz. Ayrıca BTC üzerinde kârlı görünen bir kural seti, BTC'nin 2017–2026 arasındaki spesifik boğa/ayı rejimlerine uyum sağlamış olabilir.
- **Doğru yaklaşım:** Eğer amaç genellenebilir bir fiyat davranışı yakalamaksa (mikroyapısal istisnalar hariç), hipotez **en baştan çekirdek bir mini-evren (ör. 5–8 likit enstrüman) üzerinde eşzamanlı (pooled)** tasarlanmalı ve test edilmelidir. Tek enstrümanda geliştirme, yalnızca o enstrümana özgü fiziksel/kurumsal bir mekanizma varsa (ör. seans açılış saati, kontrat vade dönüşü, merkez bankası fixing'i) yapılmalıdır.

### 2. Scalp / Day Trade: Niş Enstrüman Seçimi ve Ölçütler
Kısa vadeli işlemlerde en büyük düşman işlem maliyeti (komisyon + spread + kayma) ve veri kirliliğidir. Elimizdeki veri setine göre en rasyonel niş adaylar ve filtreler şunlardır:

| Piyasa / Veri | Önerilen Niş Enstrümanlar | Seçim Ölçütleri (Eşik Değerler) | Neden / Kısıt |
| :--- | :--- | :--- | :--- |
| **Binance Kripto (1dk, 2017→)** | BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT | **Maliyet / Bar ATR(15dk) < %8**<br>Günlük hacim > 500M$ | En temiz ve en uzun dakikalık veri. Altcoinlerde 1–5dk'da spread ve likidite boşlukları kenarı tamamen siler. |
| **Dukascopy FX/CFD (1dk)** | XAUUSD (Altın), USDJPY, EURUSD, NAS100/US500 CFD | **Spread / Beklenen Brüt Kâr < %15**<br>Belirli seans saatleri (Londra/NY) | Seans açılışları ve mikroyapı etkileri (Tokyo fix, Londra open, NY 09:30) çok nettir. Ancak CFD verisi ile gerçek borsa vadeli (CME) verisi arasındaki farka dikkat edilmeli. |
| **BIST / ABD (1s, ~2 yıl)** | *Scalp/Day için uygun değil* | Veri çözünürlüğü (1s) ve örneklem (2 yıl) yetersiz | 2 yıllık saatlik veride anlamlı sayıda day-trade işlemi ve farklı piyasa rejimi (ayı/boğa/yatay) çıkmaz. |

### 3. Swing: Evren Tanımı ve Mimari Seçim
Swing stratejilerde elimizdeki ~80 enstrümanlık evreni **tek bir homojen havuz** olarak değil, **4 ayrı homojen alt-evren** (BIST30, ABD20, Kripto25, Emtia8) olarak tanımlamalıyız. Çünkü BIST'teki TL enflasyon dinamiği ile Kripto'nun 7/24 volatilite yapısı aynı sıralamaya (ranking) sokulamaz.
- **Kesitsel (Cross-Sectional) + Zaman Serisi (Time-Series) Hibriti:** En sağlam yapı ikisini birleştirmektir (Dual Momentum mantığı).
  1. **Zaman Serisi Filtresi (Mutlak Trend/Rejim):** Enstrüman kendi geçmişine göre yükseliş trendinde mi ve piyasa rejimi uygun mu? (Ör. Kripto genelinde ayı piyasası varken "en az düşen" coini longlamak kaybettirir).
  2. **Kesitsel Seçim (Göreli Güç):** Zaman serisi filtresini geçenler arasında momentumu veya dönüş sinyali en güçlü ilk %10–20'lik dilimi seç.

### 4. Kardeş Doğrulama: Seçim ve Başarı Kriterleri
"Kardeş enstrüman", **aynı piyasa katılımcı profili, benzer volatilite dağılımı ve aynı işlem saatlerine** sahip varlıktır (Ör. NQ ↔ ES/RTY; XAUUSD ↔ XAGUSD; BTC ↔ ETH/SOL/BNB; GARAN ↔ AKBNK/YKBNK).
- **Korelasyon Tuzağı:** Kardeş enstrümanlar yüksek korelasyonluysa (ör. BTC ve ETH ~0,80), aynı zaman diliminde ikisinde de PF > 1 çıkması 2 bağımsız kanıt değil, yaklaşık **1,2 bağımsız kanıt** demektir.
- **Geçerlik Ölçütü:** Ham parametrelerle (hiçbir ince ayar yapmadan):
  1. Kardeşlerin **en az %70'inde** (ör. 10 coinin 7'sinde) net **PF > 1,10** ve pozitif Sharpe üretmeli.
  2. Havuzlanmış (pooled) toplam özsermaye eğrisinde tek bir enstrüman toplam kârın **%35'inden fazlasını** tek başına sırtlamamalı.
  3. Kardeşlerdeki başarı, yalnızca aynı birkaç haftalık ekstrem piyasa şokuna (ör. Kasım 2022 veya Mart 2020) dayanmamalı.

### 5. Havuzlama (Pooling): Ortak Parametre vs. Tekil Optimizasyon
Liderin görüşüne **tamamen katılıyorum**: Tüm evrende (veya alt-evrende) **kesinlikle tek bir ortak parametre seti** kullanılmalıdır.
- **Nasıl Uygulanmalı?** Her enstrümanın volatilitesi ve fiyat seviyesi farklı olduğu için parametreler **boyutsuz (dimensionless) ve volatiliteye göre normalize edilmiş** olmalıdır. Örneğin "50 dolarlık stop" veya "%3 hareket" yerine **`1.5 * ATR(20)`**, **`Z-Score > 2.0`** veya **`Donchian(20)`** kullanılmalıdır. Volatilite ile normalize edilmiş bir kural seti BIST'te, Altın'da ve BTC'de aynı parametreyle çalışabiliyorsa, gerçek bir piyasa davranışını (davranışsal finans / kurumsal akış) yakalamış demektir.

### 6. Literatür ve Endüstri Pratiği
- **Akademik Bulgular:**
  - *Moskowitz, Ooi & Pedersen (2012) – "Time Series Momentum":* 58 farklı likit enstrümanda (emtia, döviz, hisse endeksi, tahvil) tek ve basit bir trend kuralının (1–12 aylık getiri işareti) evrensel olarak çalıştığını gösterir.
  - *Jegadeesh & Titman (1993)* ve *Asness, Moskowitz & Pedersen (2013) – "Value and Momentum Everywhere":* Kesitsel momentumun farklı varlık sınıflarında ortak parametrelerle çalıştığını kanıtlar.
  - *Bailey, Borwein, López de Prado & Zhu (2014) – "Pseudo-Mathematics and Financial Charlatanism":* Tek bir zaman serisi üzerinde yapılan çoklu denemelerin (Deflated Sharpe Ratio) ne kadar hızlı aşırı uyuma yol açtığını matematiksel olarak ispatlar.
- **Profesyonel Pratik (CTA & Prop):** Büyük CTA fonları (AQR, Man AHL, Winton) 50–100 piyasada **aynı sinyal motorunu ve aynı parametre ağırlıklarını** çalıştırır; enstrüman bazlı parametre optimizasyonunu kesinlikle yasaklarlar (yalnızca volatilite hedeflemesi ile pozisyon boyutu ayarlanır). Kısa vadeli prop masaları ve kripto market maker'lar ise tam tersine yalnızca 1–3 ultra-likit çiftte (BTC, ETH, ES) mikroyapı/emir defteri (order flow) ve seans anomalisi kazırlar.

### 7. Bizim İçin Başlangıç Önerisi (2 Somut Rota)
Elimizdeki veri kalitesi ve Faz 1 altyapısını dikkate alarak şu iki koldan paralel başlamalıyız:
1. **Rota A (Evren / Swing – Kripto İlk 25, 1s ve 4s Barlar):** Binance 2017→ dakikalık verisinden üretilecek 1s/4s barlar, elimizdeki en uzun ve en temiz kesitsel veri setidir. **Strateji:** *Zaman serisi rejim filtreli (BTC > MA200) Kesitsel Momentum / Volatilite Kırılımı.* En güçlü 3–5 coini taşıyan, ortak parametreli rotasyon sistemi.
2. **Rota B (Niş / Day Trade – Dukascopy XAUUSD, USDJPY, NAS100, 5dk–15dk Barlar):** Mikroyapısal ve seans bazlı kenarlar. **Strateji:** *Londra/NY açılış İlk Saat Kırılımı (Opening Range Breakout) ve Gün İçi Volatilite Sıkışması.* Yalnızca en likit 3–4 enstrümanda, işlem saatleri kısıtlı olarak tasarlanmalı.
*(Not: BIST ve ABD 2 yıllık saatlik veri, sağlam bir OOS doğrulama için çok kısa; bu evrenleri yalnızca Kripto/FX'te doğrulanan swing kurallarını test etmek için ikincil doğrulama alanı olarak kullanmalıyız.)*

### 8. Hedef Gerçekçiliği: Aylık %5 Net (~%80 Yıllık) ve %15 MDD
Liderin uyarısı matematiksel olarak haklıdır: **Aylık %5 net bileşik getiri (~%80 yıllık) ile %15 Maksimum Drawdown (MDD) hedefi, Calmar Oranı > 5.3 ve Sharpe Oranı > 3.5–4.0 demektir.** Bu istatistikleri tek bir stratejiyle veya yüksek kaldıraçla sürekli tutturmak imkânsıza yakındır.
- **Kaldıraç Matematiği:** Mevcut portföyü (Yıllık %4, MDD %2,9) 15x kaldıraçla çalıştırırsanız teorik getiri ~%60 olur ama beklenen MDD **%43,5'e** (kuyruk riskiyle %60+'a) fırlar ve %15 MDD bütçesini anında patlatır.
- **Bu Hedefe En Çok Yaklaşacak Gerçekçi Yol:**
  1. **Çoklu Düşük Korelasyonlu Strateji Sepeti (En Az 6–8 Bağımsız Strateji):** Tek bir "kutsal kâse" aramak yerine; Kripto Kesitsel Swing, Altın/Endeks Açılış Kırılımı, FX Ortalamaya Dönüş ve Hisse/Emtia Trend Takibi gibi birbirinden bağımsız (korelasyonu < 0,20) 6–8 stratejiyi birleştirmeliyiz. Bağımsız stratejiler birleştiğinde portföy Sharpe oranı $\approx \text{Sharpe}_{\text{ort}} \times \sqrt{N}$ formülüyle büyür.
  2. **Dinamik Volatilite Hedeflemesi ve Özsermaye Eğrisi Koruması:** İşlem başına riski %0,5'ten %1,0–1,25 bandına çekip, portföy drawdown'ı %8'e ulaştığında riski yarıya indiren dinamik bir sermaye yönetimi uygulanmalıdır.
  3. **Beklenti Revizyonu:** %15 MDD sert sınırı korunacaksa, gerçekçi ve sürdürülebilir mükemmel hedef **aylık %2–3 net (yıllık %27–42 bileşik, Calmar ~2.0–2.5)** bandıdır. Aylık %5 ancak MDD bütçesini **%25–30** bandına esnetirsek ve kripto/endeks boğa rejimlerinde dinamik risk artışı (pyramiding) yaparsak ulaşılabilir olur.
