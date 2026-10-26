İyi kaynak topladım; şimdi eleştirisel değerlendirmeyi bunlarla birlikte yazıyorum.

---

# Test Kapınızın Bağımsız ve Eleştirel Değerlendirmesi

**Kısa verdict:** Kapı **şu an için adil değil**. Bileşenleri büyük ölçüde doğru düşünülüyor, ancak üç yapısal hata var: (1) geçme kriteri tek başına yeterli sayılıyor, (2) piyasa (beta) etkisi ayrıştırılmıyor, (3) strateji evreni long-only ve yayın sonrası veriyle sınanmış ama farklı uzunlukların tek bir listeye basıldığı izlenemiyor. Aşağıda sorularınızın tek tek cevabı ve en önemli zayıflıklar.

---

## 1. Kapı adil mi? En önemli zayıflıklar

### Haksız geçme (iyi strateji eliyor) yönündeki riskler — asıl kaygı

- **"Net getiri > 0" tek geçme şartı, istatistiksel düzeltme olmadan kullanılıyor.** 933 + 119 strateji denenmiş demişsiniz; her biri başına %5 nominal false positive payı ile test sonrası "net > 0" geçenler seçilmişse, beklenen yanlış pozisyon ~1.000 test × 5% ≈ 50 eder (Bailey, de Caraban & Mullins, *The Deflated Sharpe Ratio*, JPM 40(5):94–107, 2014). DSR'yi "bilgi amaçlı" olarak ayırmış olmanız, eleme kararında kullanılmamış olması büyük ihtimalle kritik. Bilimsel literatür (Harvey, Liu & Zhu, *…and the Cross-Section of Expected Returns*, RFS 29(1):5–68, 2016) şunu net diyor: tek testte t ≥ 2 anlamlıdır; 20 testte aynı t ≥ 2'lik bir "iyi" flukstan %64 ihtimalle anlamsızdır. Kapınız ~1.000 strateji denediği için "en iyi örnek" mantığı zayıf.
- **DSR eleme için uygulanmamış.** DSR, Bailey & López de Prado (2014) tarafından, number-of-trials ve non-normality düzeltmesiyle FWE'yi kontrol eder. Parametrik arama (optimizer) senaryolarında standart araçtır. Ancak ~933 bağımsız yayın stratejisi + varyantları gibi yapılar için daha güçlü alternatif: **Hansen's SPA testi** (Hansen, *Expected Returns and Risk Factors*, J. Econometrics 126(2):611–634, 2005; Lopez de Prado & Hansen, 2009) ya da **White'ın Reality Check bootstrap'i** (White, *A Reality Check for Data Snooping*, Econometrica 68(5):1097–1117, 2000; Sullivan, Timmermann & White, *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*, JFE 54(5):1647–1691). Onların "en iyi strateji benchmark'ı geçemiyor" testi mantığı, "kapıdan geçen strateji geçsin" testinden daha doğrudur.

### Haksız elme (kötü strateji geçiyor) yönündeki riskler

- **Long-only evren.** Kapıda "çoğu yalnızca alım (long) yapıyor" — yani short üretimi değerlendirmeyen bir evrenle kapı kurulmuş. Validasyon sırasında short'lanmayan ama kısa pozisyon üretebilen stratejiler hep eleniyor. Geçici değil, sistemik bir eksik.
- **Maliyet modelinin parametrik hassasiyeti.** %0,05 + 1 tick (equities) ve %0,1/taraf (krypto) — bu sayılar broker ve zaman dilimine göre değişir; per-trade mu per-side mi sorusu, kripto funding'i, illikidity, slippage modeli (ATR×kat gibi) belirlenmemiş. Kapıdaki "2 kat maliyet" ve "30 trades/yıl" eşikleri kararlı görünse de, az sayıda trade içeren stratejilerin eleme mantığıyla çelişme riski var.
- **Veri ve evren önyargısı.** 401 strateji ücretsiz veri olmadığı için test edilemedi — yani denenen evren, yayınlı veri olan ve likid olduğu varsayılan sembolleri kapsıyor; delisted/shrinkage önyargısı var. 26 haftalık paper trade ile son karar, istatistiksel olarak zayıf bir sınama.

---

## 2. "Net getiri > 0" geçme şartı uygun mu?

**Hayır, tek başına geçme kriteri olarak uygun değil.** Yetersiz bir *gereklilik* olarak kullanılması teknik olarak temel bir adım (cost sonrası pozitiflik), yanlış bir *yeterlilik* olarak kullanılması ise hata. Gerekli yeterliktir; yanlış olarak uygulanmış.

- **Rastgele strateji olasılığı:** Bunu ölçmüyorsunuz. Doğru yöntem: Monte Carlo / permutasyon testi — kapıdaki pipeline'ı (maliyet, filtreler dahil) rastgele üretilmiş sinyaller, sinyal permütasyonları veya rastgele varlık girişimleriyle koşturun. Kaç rastgele strateji'nin "net > 0" + PF + bootstrap geçerek paper'a kalacağına bakın. Beklenen sonuç: gerçekçi maliyet sonrası rastgele stratejilerin büyük çoğunluğun geçmemesi, ama ~1.000 test yapıldığında nominal %5'lik bir eşik bile beklenen yanlış pozisyon üretir. "Net > 0" bir p-değeri değildir; DSR/PSR/SPA p-değeri üretmek gerekir.
- **Nasıl ölçülür:** White's Reality Check bootstrap p-değeri, SPA (data-dependent null), ya da Monte Carlo null dağılımı. Pratik öneri: rastgele strateji deneyleri → geçen oran → elindeki 96 ve 85 sayılarının anlamlılığı.

---

## 3. Seçim yanlılığı: DSR, BHY, White, Hansen SPA ya da placebo — hangisi?

Pratik önerim, tek bir testle yetinmemek ama final kararını doğrudan veren test olarak **Hansen's SPA testi** alınır:

- SPA, Hansen (2005)'deki gibi data-dependent null ile (irrelevant alternatifleri elemek için studentized statistic), daha güçlü ve conservative White's RC'ye göre daha yüksek power'a sahiptir. White RC bootstrap'i (Sullivan vd., 1999) de iyi ve implementasyonu kolay; ama çok sayıda zayıf alternatifin dahil olması power kaybına yol açabiliyor (Hansen'ın temelli argümanı).
- **DSR:** Bailey & López de Prado (2014) — özellikle parametrik arama/optimizer senaryoları için. Bağımsız strateji evreni seçimi için SPA daha uygun.
- **Benjamini-Hochberg:** FDR kontrolü için tasarlanmış; FWE ("en iyi tek stratejiyi bul") kontrolünde değil. Eğer "top-K" mantığı kuruyorsanız BHY durulur, ama tek final stratejisi için White/SPA doğrudur.
- **Placebo (rastgele strateji) testi:** kapının kendi sorusu gibi — en pratik, model-bağımsız kontrol. SPA + placebo birlikte en sağlam trio.

Önerilen yığın: önden eleme aşaması → DSR/SPA; final tek strateji seçimi → SPA (benchmark: piyasa/B&H) veya White's Reality Check; her ikiside → placebo/Monte Carlo cross-check.

---

## 4. Yükselen piyasada yalnızca alım yapan stratejiler: piyasa etkisi ayrıştırılıyor mu?

**Hayır — ayrıştırılmamış.** Bu, kapının en kritik tasarım hatasıdır şu an:

- Test dönemi büyük ölçüde 2023–2026 bull run. Yalnızca long, net>0 geçen stratejiler büyük ölçüde bu tailwind'i yansıtıyor olabilir. Net getiri > 0 (cost sonrası) hurdle'ı bile bull market ortalamasını geçebilecek seviyede.
- Doğru kontrol: **Al-vs-hold (buy-and-hold) karşılaştırması.** Stratejin OOS net getirisi, aynı evren/BUH cost sonrası, B&H getirisiyle karşılaştırılıp α ≤ 0 ise reddedilmeli. Harvey, Liu & Zhu (2016) "Backtesting" makalesi de bu tür "profit hurdle" (anlamlılık eşiği) konusunda öneriyor: bir stratejin "significant" olması için ulaşması gereken makul profit eşiği var.
- **Beta ayarlı alfa:** strateji long-only olduğu için market beta'sı taşıyor; ham α hesabı yanıltıcı olabilir (sektör rotasyonu vs genel piyasa). Piyasa ile regresyon yapıp α'yı ölçmek — hem raw α (B&H ile) hem beta-adj α (piyasa ile) — iki karşılaştırmayı da yapılmalı. İkisi de geçmeli.

---

## 5. Farklı sınama süreleri (6 ay – 3 yıl) adil karşılaştırımı

- **Farklı uzunluklardan oluşan bir final listesinin tek bir istatistikle kıyaslanması adil değil.** Walk-forward / çapraz katlama (rolling out-of-sample folds) önerilir.
- Her strateji için pre-registered OOS penceresi; final değerlendirmesi için sabit bir penceresi (örn. son 12 ay) olmalı. Farklı uzunluklarda elenen/elegelen stratejiler karışık olmamalı.
- Tutarlılık: bir strateji final listesine girebilmeli — en az X fold'ta (örn. en az 2/3) outperform etmeli. "Kısa sınama" (<1 yıl veya <10 trade) etiketi verilmiş ama bu etiket final elemesine yansımıp yansımadığı da belirsiz — protocol pre-registered olmalı.

---

## 6. ML'nin binlerce fikir üreteceği bu kapıda ne bozulur?

- **Evren uyuşmazlığı:** Kapı ~933 yayın + ~120 varyant tasarlandı; ML binlerce üretiyor. N bu kadar büyük olunca DSR'in ayarladığı SR₀ eşiği katlanarak yükselir; winner's curse kontrolı güçleşir; CLRS (2005) sequential testing / alpha-spending yaklaşımı önerilir.
- **Üretim sırasında leakage:** ML üretimi eğer in-sample (tüm veri) üzerinde "en iyi" aranıyorsa, kapının DSR mantığı tam isabet; ama strateji seviyesinde train/test ayrımı yapılırsa DSR değil SPA/CLRS gerekir. Üretim train'de, doğrulama/test'te gerçekten görünmemiş veride yapılmalı.
- **Kaç strateji kalacağı:** "En iyi 13" mantığı kapının kendisi gibi olursa DSR doğru; ama "üretim sonrası eleme" akışı tasarımı öyle değil.
- **Diğer eleme adımları:** p10 bootstrap, PF, maliyet — bunlar ML stratejileri için hâlâ geçerli; fakat trade-frequency eşiği (30/yıl) ve long-only varsayımı ML üretimini sınırlandırır.

---

## 7. Senin önereceğin kapı nasıl olurdu? Somut adımlar ve eşikler

Önerilen revize protokolü:

1. **Evren:** dengeli (ABD hisse + ETF, kripto, emtia), survivor bias ve adjusted price düzeltmesi, delisted semboller dahil.
2. **Faithfulness & maliyet:** TV kod → kendi yorumcuya aktarım; maliyet = per-side komisyon + volatility slippage (örn. ATR×kat); kripto funding/perp dahil; equity için 1 tick + komisyon.
3. **Ayrılmış veri:** tüm stratejiler için aynı pre-registered OOS penceresi (strateji yayım tarihinden sonraki ilk yıl ya da sabit final pencere).
4. **Eleme adımları (sıralı):**
   - Oturmuyor (trade yok) → **reddet**.
   - OOS net getiri (cost sonrası) ≤ 0 → **reddet**.
   - SPA p < 0.05 (FWE kontrolü) → **reddet** (DSR alternatif olarak).
   - Blok bootstrap (haftalık getiri, block ≈ 252 gün) p10 ≤ 0 → **reddet**.
   - Cost sonrası PF < 1.2 → **reddet**.
   - Korelasyon: OOS döneminde pairwise ρ > 0.6 → biri **reddet**.
5. **Final:** SPA/B&H karşılaştırması geçen tek strateji → paper'a alınır.

**Somut önerilen eşikler:**

| Adım | Eşik |
|---|---|
| Geçme şartı (gerekli) | OOS net (cost sonrası) > 0 |
| Geçme şartı (istatistiksel) | SPA p < 0.05 (FWE) |
| Geçme şartı (maliyet/momentum) | Bootstrap p10 > 0; PF_after_cost ≥ 1.2 |
| Minimum veri | OOS ≥ belirlenmiş pencere; final adayları için ≥ ~30 trade/yıl (kısa sınama ayrımı korunur) |
| Portföy düzeltmesi | Korelasyon filtresi OOS istatistiklerinden |

Paper trade: 26 hafta iyi bir "sanity check"; ancak karar önceden planlı olmalı — paper sonucu test istatistiğini çelişkili görüyorsa stop.

---

## 8. Kaynaklar

- Bailey, D. H., de Caraban, M., & Mullins, B. (2014). *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality*. JPM 40(5), 94–107.
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley — DSR, SPA, White's Reality Check, CLRS sequential testing konuları.
- Hansen, P. R. (2005). *Expected Returns and Risk Factors*. J. Econometrics 126(2), 611–634 (SPA testi).
- White, H. (2000). *A Reality Check for Data Snooping*. Econometrica 68(5), 1097–1117.
- Sullivan, B. T., Timmermann, A., & White, H. (1999). *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*. JFE 54(5), 1647–1691.
- Harvey, C. R., Liu, Y., & Zhu, H. (2016). *…and the Cross-Section of Expected Returns*. RFS 29(1), 5–68 (multiple testing, t ≥ 3 hurdle, backtest evaluation).
- Harvey & Liu (2015). *Evaluating Trading Strategies*. JPM 40(5), 94–107; *Backtesting*. JPM 42(1), 13–33 (profit hurdle).

---

## Sonuç

- **Adil değil, ama düzeltilebilir.** En kritik hatalar: tek başına "net > 0", FWE kontrolünün zayıtlığı, piyasa etkisi ayrıştırılmaması.
- **Rastgele strateji olasılığı** için Monte Carlo/placebo testi şart; beklenen false-positive yük ~N×α — 1.000 stratejiyle tek başına intoleranslı.
- **Doğru araç seti:** final kararında **SPA**, ön eleme/parametrik senaryoda **DSR**, cross-check'ta **placebo**; White RC bootstrap alternatifi.
- **Piyasa etkisi:** al-vs-hold + beta-adj alfa, ikisi birlikte.
- **Farklı uzunluklar:** çapraz katlama / pre-registered sabit OOS penceresi.
- **ML:** train→test ayrımı, CLRS/alpha-spending, SPA ile çoğaltılmış DSR.

Kalan zayıflıklar (sizin gördüğünüz gibi değil, benim gördüğüm gibi): long-only evren, maliyet modeli parametrik hassasiyeti, survivor bias, 26 haftalık paper kararı istatistiksel gücü. Bunların tamamına kapatılmadan bu kapı, "iyi mi kötü mü" sorusuna verilecek olan cevabı değiştirmez — cevap yalnızca zamanla ve gerçek para ile denecek.