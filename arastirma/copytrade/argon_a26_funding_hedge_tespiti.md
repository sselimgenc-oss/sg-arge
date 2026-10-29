> **Lider denetim notu (2026-10-29):** Argon A26. Yöntem makul ve veriyle hesaplanabilir. Düzeltmeler: (1) arXiv:2212.06888
> "Fundamentals of Perpetual Futures" makalesinin yazarları He, Manela, Ross, von Wachter'dir; Leippold değil. (2) arXiv:2605.06405
> doğrulanamadı. (3) Kapıda kısa işlem payı (`kisa_islem_payi`) zaten var; "tutma < 30 dk" ölçütü onunla çakışır.
> Eşikler sezgisel (Argon da belirtiyor). **Kullanım:** funding payı, spot↔perp ters pozisyon ve maker payı, seçim kapısına
> değil önce *bayrak* olarak (`bayrak_ek`) eklenebilir; oda üyeleri için bir kez hesaplanıp kullanıcıya gösterilir.

# Hyperliquid Copy-Trading Filtresi: Yönsel Olmayan Trader Tespiti

Bu kılavuz, Hyperliquid vadeli işlemler (perpetual futures) lider tablosundaki trader'ları 30 dakika ile 2 saat arasındaki gecikmeyle ve **yalnızca perp bacağını** kopyalayan sistemler için tasarlanmıştır.

Amaç; yönsel tahmin yapmayan, kârını fonlama (funding) arbitrajından, delta-nötr hedge mekanizmalarından veya piyasa yapıcılıktan (market making) elde eden hesapları eleyerek kopyalama işleminin tek bacaklı kontrolsüz bir yöne dönüşmesini engellemektir.

---

## 1. Tespit Ölçütleri

Aşağıdaki ölçütler Hyperliquid genel veri uçları (`userFills`, `userFunding`, `clearinghouseState`, `spotClearinghouseState`, `portfolio`) kullanılarak hesaplanır.

| Ölçüt | Formül | Gereken Alanlar | Önerilen Eşik | Gerekçe |
| :--- | :--- | :--- | :--- | :--- |
| **Funding Geliri Payı ($R_{\text{fund}}$)** | $\frac{\sum \text{FundingPayment}}{\max(\|\text{TotalPnL}\|, \epsilon)}$ | `userFunding` (`delta.usdc`), `portfolio` veya `userFills` (`closedPnl`) | $> \%50$ | Arbitrajcıların kârı fiyat hareketinden değil, düzenli fonlama tahsilatından oluşur. Yönsel trader'lar için fonlama ikincil bir kalemdir. |
| **Dahili Spot-Perp Bazı ($R_{\text{basis}}$)** | $\frac{\|\min(S_{\text{coin}}, -P_{\text{coin}})\|}{\max(S_{\text{coin}}, \|P_{\text{coin}}\|)}$ *(eğer $S \times P < 0$)* | `spotClearinghouseState` (`balances`), `clearinghouseState` (`assetPositions[].position.szi`) | $> \%80$ hacim örtüşmesi | Platform içinde spot uzun / perp kısa (cash & carry) kurularak delta sıfırlanmıştır. Sadece perp bacağını kopyalamak çıplak short riski yaratır. |
| **Pozisyon Yönü - Funding Uyumu ($S_{\text{align}}$)** | $\frac{T_{\text{pozitif carry}}}{T_{\text{toplam pozisyon}}}$ | `clearinghouseState` (pozisyon yönü), `userFunding` / `fundingHistory` ($F_t$) | $> \%85$ | Harici borsalarda (Binance, Bybit vb.) karşı bacak tutan carry trader'lar sürekli pozitif fonlama toplayan tarafta pozisyon açarlar. |
| **Maker Hacim Oranı ($R_{\text{maker}}$)** | $\frac{\sum \text{Hacim}_{\text{maker}}}{\sum \text{Hacim}_{\text{toplam}}}$ | `userFills` (`crossed == false`, `sz`) | $> \%90$ | Piyasa yapıcılar pasif limit emirlerle spread toplar. Gecikmeli kopyalamada spread avantajı silinir, ters seçim ve kayma zararı kalır. |
| **Ortalama Tutma Süresi ($\overline{T}_{\text{hold}}$)** | $\frac{\sum V_i \cdot (t_{\text{kapanış}, i} - t_{\text{açılış}, i})}{\sum V_i}$ | `userFills` (`time`, `dir`, `closedPnl`) | $< 1$ saat ($< 30\text{ dk}$ kritik) | 30 dk – 2 sa gecikmeyle çalışan bir kopyalama botu, pozisyon kapatıldıktan sonra işleme girerek tamamen uyumsuz kalır. |
| **Kazanma Oranı / Kâr Dağılımı Asimetrisi** | $\text{WinRate} = \frac{N_{\text{kârlı}}}{N_{\text{toplam}}}$, $\text{Payoff} = \frac{\overline{\text{Kâr}}}{\overline{\text{Zarar}}}$ | `userFills` (`closedPnl`) | $\text{WinRate} > \%85$ ve $\text{Payoff} < 0.35$ | Yüksek işlem sayılı, mikro kârlı arbitraj ve piyasa yapıcı profili. Gecikme ve işlem komisyonu bu marjı yok eder. |

---

## 2. "Kopyalanamaz" Karar Ağacı (5 Adım)

Hesaplar kopyalama havuzuna alınmadan önce sıralı olarak şu 5 aşamalı eleme süzgecinden geçirilir:

```
[Yeni Hesap İncelemesi]
         │
         ▼
[Adım 1: Dahili Spot-Perp Bazı]
Aynı varlıkta Spot ve Perp zıt yönlü mü ve hacim örtüşmesi > %80 mi?
   ├── EVET ──► [KOPYALANAMAZ] (Platform İçi Cash & Carry / Arbitraj)
   └── HAYIR
         │
         ▼
[Adım 2: Gecikme ve Tutma Süresi Uyumu]
Ağırlıklı ortalama pozisyon tutma süresi (T_hold) < 30 dakika mı?
   ├── EVET ──► [KOPYALANAMAZ] (HFT / Hızlı Scalper / Mikro Gecikme)
   └── HAYIR
         │
         ▼
[Adım 3: Likidite Sağlayıcı / Piyasa Yapıcı Profili]
Maker hacim oranı > %90 VE günlük işlem adedi > 100 mü?
   ├── EVET ──► [KOPYALANAMAZ] (Pasif Piyasa Yapıcı / Spread Capture)
   └── HAYIR
         │
         ▼
[Adım 4: Fonlama Geliri Dominansı]
Toplam kâr içinde net funding payı (R_fund) > %50 mi?
   ├── EVET ──► [KOPYALANAMAZ] (Fonlama Odaklı Arbitraj)
   └── HAYIR
         │
         ▼
[Adım 5: Harici Karşı Bacak / Çapraz Borsa Hedge Belirtisi]
Fonlama uyumu (S_align) > %85 VE Fiyat kaynaklı PnL sıfıra yakın veya negatif mi?
   ├── EVET ──► [KOPYALANAMAZ] (Harici Borsa Delta-Nötr Arbitrajı)
   └── HAYIR ──► [KOPYALANABİLİR] (Aday Yönsel Trader)
```

---

## 3. Yanlış Pozitif (False Positive) Riskleri

Bu filtrelerin katı uygulanması, bazı meşru yönsel trader'ların sisteme dahil edilmesini engelleyebilir:

1. **Pasif Emir Kullanan Kurumsal / Büyük Yönsel Trader'lar**:
   * Büyük sermayeli swing trader'lar piyasa emri (taker) yerine TWAP veya limit emirlerle likidite sağlayarak maliyet düşürür (`crossed == false`). Bu durum Maker oranını $\%90$'ın üzerine çıkarabilir ve yönsel pozisyon alan bir trader'ın "piyasa yapıcı" sayılarak elenmesine yol açabilir.
   * *Çözüm*: Maker oranını tek başına değil, ortalama pozisyon tutma süresi ($\overline{T}_{\text{hold}} > 12\text{ saat}$) ve işlem başına getiri yüzdesiyle birlikte değerlendirmek.

2. **Trend Takipçilerinin Güçlü Düzeltmelerde Fonlama Toplaması**:
   * Boğa trendinde kısa vadeli aşırı ısınmış altcoin'lerde short açan veya sert düşüş yaşayan coin'lerde dip alımı yapan yönsel trader'lar, yüksek negatif/pozitif fonlama ortamında tesadüfen uzun süre fonlama toplayan tarafta kalabilir. Fiyat kârı henüz realize edilmemişse hesap harici carry trader'ı sanılabilir.
   * *Çözüm*: Fonlama uyumunu tekil günlerde değil, farklı piyasa rejimlerini içeren en az 30 günlük geçmişte test etmek.

3. **Uzun Vadeli Varlık Koruması (Dinamik Makro Hedge)**:
   * Spot cüzdanında soğuk depolama veya ana varlık olarak ETH/BTC tutan bir fon, makro kırılımlarda korunma amacıyla perp üzerinde yönsel short açabilir. Bu durum dahili spot filtresinde tam cash-and-carry arbitrajı gibi görünebilir.
   * *Çözüm*: Spot bakiyesinin işlem sıklığına bakmak; spot bakiye statikse ve perp tarafında dinamik stop/take-profit yönetimi varsa işlem yönsel kabul edilebilir.

---

## 4. Kaynaklar ve Doğruluk Durumu

* **Hyperliquid Resmi Dokümantasyonu**:
  * [Hyperliquid Perpetuals Info API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals): `clearinghouseState`, `userFunding`, `userFills` ve `spotClearinghouseState` veri yapıları.
  * [Hyperliquid Funding Oranları ve Mekaniği](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding): 1 saatlik fonlama hesaplaması, faiz/prim bileşenleri ve $\%4$/saat tavan sınırı.
* **Akademik Çalışmalar**:
  * [Fundamentals of Perpetual Futures (Markus Leippold et al., arXiv:2212.06888)](https://arxiv.org/abs/2212.06888): Sürekli vadeli sözleşmelerin arbitraj sınırları, spot-perp taşıma maliyetleri ve fonlama mekanizmasının teorik çerçevesi.
  * [Funding-Aware Optimal Market Making for Perpetual DEXs (Nam Anh Le, arXiv:2605.06405)](https://arxiv.org/abs/2605.06405): Kripto perp piyasalarında fonlama oranlarının piyasa yapıcı envanter riskine ve kotasyon stratejilerine etkisi.
* **Doğrulanamadı Notu**:
  * Hyperliquid üzerinde **gecikmeli (30 dk / 2 sa) kopya işlemlerde arbitrajcıların filtrelenmesi** konusuna özel bağımsız hakemli bir akademik makale doğrudan literatürde doğrulanmamıştır. Önerilen eşikler ve karar ağacı adımları, DEX piyasa mikro-yapısı kuralları ve kantitatif fonlama arbitrajı dinamiklerinden türetilmiştir.
