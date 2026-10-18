# SPS-03: 3 Quant Tarz Havuzu ve 27 Strateji Entegrasyon Mimarisi

**Hazırlayan:** Baş Quant Danışmanı Argon & Algobot Ar-Ge Ekibi  
**Kapsam:** 5.000,00 $ Sanal Sermayenin 3 Çekirdek Tarz Havuzuna Dağılımı ve 27 Stratejinin Sınıflandırılması  
**Tarih:** 18 Ekim 2026  

---

## 1. Neden Önceki 7 İsim Değiştirildi? (Quant Gerekçesi)

Önceki prototipteki 7 hesap adı (`Strateji`, `Algo`, `Day trade`, `Day trade hisse/emtia`, `TradingView`, `Swing`, `Trend kolları`), ilk tasarım aşamasında eski `pano ekranlar.pdf` dosyasındaki kurgudan devralınmış taslak isimlerdi.

Bu isimlerin quant zayıflıkları:
- `Strateji` veya `Algo` gibi isimler bir işlem felsefesi veya zaman ufku tanımlamaz.
- `Day trade` ve `Day trade hisse/emtia` şeklinde iki ayrı suni hesap açmak sermayeyi gereksiz yere parçalar ve marjin verimliliğini düşürür.
- `TradingView` indikatör tabanlı modelleri temsil ederken, `Swing` ve `Trend kolları` ile vade çakışması yaratıyordu.

---

## 2. Belirlenen 3 Çekirdek Quant Tarz Havuzu

SPS-03 portföyü, **işlem sıklığı**, **tutma süresi**, **rejim adaptasyonu** ve **matematiksel alfa kaynağına** göre 3 net tarz havuzuna ayrılmıştır:

```
                        TOPLAM PORTFÖY SERMAYESİ: 5.000,00 $
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
 1. DAY TRADE (Seans İçi)      2. SWING (Momentum & Dip)     3. TREND TAKİP (Makro Dalga)
   Bütçe: 1.000,00 $ (%20)       Bütçe: 2.250,00 $ (%45)       Bütçe: 1.750,00 $ (%35)
   5 Model (1H/4H Seanslık)     13 Model (2-6 Gün Tutuş)       9 Model (1-4 Hafta Trend)
```

---

## 3. Havuz 1: Day Trade (Seans İçi) — 1.000,00 $ (%20 Sermaye)
* **Temel Felsefe:** Gece riskini (overnight gap risk) minimuma indiren, seans açılış volatilitesini (ORB) ve kurumsal seans likidite temizliğini (sweep) yakalayan modeller.
* **Tutma Süresi:** 4 saat – 24 saat (aynı gün veya en geç ertesi seans kapanış).
* **Kapsadığı 5 Strateji:**
  1. **#8 VR2_S4_INTRADAY** (Intraday RRS ORB & RVOL Kırılımı) — *Kontrollü Pilot (%5)*
  2. **#9 V2A_INTRA_TOTT_ORB** (Hourly Adaptif TOTT Kanalı & ORB) — *Kontrollü Pilot (%5)*
  3. **#10 R06_S3_PMAX_4H** (4H Sweet Spot MTF PMax & ATR Filtresi) — *Kontrollü Pilot (%5)*
  4. **#13 L01_TRENDSHIFT_1H** (TrendShift Saatlik İntraday Momentum) — *Kontrollü Pilot (%5)*
  5. **#19 V2B_INTRA_SWEEP** (Seans Likidite Süpürmesi & FVG Dengesizliği) — *Öğrenme Pilotu (%1)*

---

## 4. Havuz 2: Swing (Momentum & Dip) — 2.250,00 $ (%45 Sermaye)
* **Temel Felsefe:** Portföyün ana kâr motoru. Aşırı satım anomalilerini (IBS < 0.28, Z-Skor < -0.10) dipten toplayan ve yüksek hacimli flama kırılımlarını (Qullamaggie HTF, SMC Order Block) yakalayan modeller.
* **Tutma Süresi:** 2 gün – 7 gün.
* **Kapsadığı 13 Strateji:**
  1. **#1 R05_ZSCORE** (65G Z-Skor Rejim Sentinel & Momentum) — *Kontrollü Pilot (%5, Lider)*
  2. **#3 VR1_SWING** (Voltran-R1 Reddit-Quant Çift Motorlu Hibrit) — *Kontrollü Pilot (%5)*
  3. **#4 V1B_SWING_SMC_ML** (Kurumsal Likidite FVG & 4D Lorentzian ML) — *Kontrollü Pilot (%5)*
  4. **#6 S2_KEVIN_DAVEY** (Kevin Davey Donchian + 4. Gün Kısmi Kâr) — *Kontrollü Pilot (%5)*
  5. **#7 C01_PULLBACK** (1W Boğa İçi EMA20 Geri Çekilme Destek Dönüşü) — *Kontrollü Pilot (%5)*
  6. **#12 R01_QULLAMAGGIE** (High Tight Flag Sıkışması & Episodic Pivot) — *Kontrollü Pilot (%5)*
  7. **#16 C02_CCI_CONT** (CCI Sıfır Çizgisi Aşımı & Trend Devamı) — *Kontrollü Pilot (%5)*
  8. **#18 L08_LORENTZIAN_1D** (4 Boyutlu k-NN Lorentzian Bükümlü Uzay) — *Öğrenme Pilotu (%1)*
  9. **#20 L05_RANGEFLIP_1D** (Piyasa Yapısı Kırılımı BOS & Polarite Değişimi) — *Öğrenme Pilotu (%1)*
  10. **#22 L04_ORBPRO_1D** (Günlük Volatilite Bant Kırılımı & ORB Pro) — *Öğrenme Pilotu (%1)*
  11. **#24 L03_SMCPRO_1D** (ICT Emir Blokları & Kurumsal Likidite) — *Öğrenme Pilotu (%1)*
  12. **#26 C11_REVERSION** (Larry Connors 2 Günlük Panik Dönüşü) — *Öğrenme Pilotu (%1)*
  13. **#27 R02_IBS_MEANREV** (IBS < 0.30 & 25G Volatilite Dip Bandı) — *Öğrenme Pilotu (%1)*

---

## 5. Havuz 3: Trend Takip (Makro Dalga) — 1.750,00 $ (%35 Sermaye)
* **Temel Felsefe:** Piyasadaki mega boğa trendlerini (Bitcoin, Altın, Teknoloji hisseleri) haftalarca süren dinamik iz süren stoplarla (Chandelier, OTT, Supertrend) sonuna kadar taşıyan modeller.
* **Tutma Süresi:** 1 hafta – 4 hafta.
* **Kapsadığı 9 Strateji:**
  1. **#2 S1_TWIN_OTT_DUAL** (Twin OTT Çift Bantlı Volatilite Kanalı) — *Kontrollü Pilot (%5, Lider)*
  2. **#5 V1A_SWING_BREAK** (Volatilite Sıkışması Patlaması & Donchian 12G) — *Kontrollü Pilot (%5)*
  3. **#11 L01_TRENDSHIFT_1D** (TrendShift Günlük Dalga Doğrulama & Supertrend) — *Kontrollü Pilot (%5)*
  4. **#14 C04_ICHIMOKU** (Tamamlanmış Kumo Bulut Kırılımı & Kijun Denge) — *Kontrollü Pilot (%5)*
  5. **#15 C05_DMI_TREND** (DMI Yönsel İvme & ADX >= 20 Doğrulama) — *Kontrollü Pilot (%5)*
  6. **#17 C06_KAMA_EFF** (Kaufman Adaptif Ortalama & Verimlilik Oranı) — *Kontrollü Pilot (%5)*
  7. **#21 C08_DUAL_MOM** (Antonacci Çift Momentum: ROC63 & ROC21) — *Öğrenme Pilotu (%1)*
  8. **#23 L02_TRENDLOCK_1D** (1W Supertrend & 20G Donchian Hacimli Kırılım) — *Öğrenme Pilotu (%1)*
  9. **#25 C07_ADX_BREAK** (55-Günlük Tepe Kırılımı & ADX Patlaması) — *Öğrenme Pilotu (%1)*

---

## 6. Risk Yönetimi ve Sermaye Bütçesi
1. **İşlem Başı Risk (SPS-03 K4 Kuralı):**
   - Toplam 5.000 $ sermaye için işlem başı maksimum risk = **%0,50 (25,00 $)**.
   - Stop-Loss seviyeleri ATR(14)x3 veya Çift OTT bantlarıyla korunur.
2. **Kâr Kilidi (Profit Ratchet):**
   - Kâr +1.05x ATR'ye ulaştığında stop seviyesi otomatik olarak Giriş + %0.20 başabaşa çekilir.
3. **Maksimum Portföy Riski:**
   - Eşzamanlı tüm açık pozisyonların toplam riski sermayenin %2,00'sini (100 $) asla aşamaz.
