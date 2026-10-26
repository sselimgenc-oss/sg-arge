## Kısa hüküm

Kapı, **falsifikasyon filtresi olarak ortalamanın üstünde**, ama **seçim kapısı olarak zayıf**. İki yapısal sorun var:

1. **Test edilen hipotez yanlış.** "Net getiri > 0" bir istatistiksel test değil; sıfır hipotezi altında geçme olasılığı ~%50, boğa piyasasında %60–80. Yani kapı, "iyi" ile "şanslı"yı ayırmıyor.
2. **Test birimi yanlış.** Ölçtüğünüz şey "bu strateji portföye girmeli mi" değil, "yazarın iddiası kendi sembolünde doğrulandı mı". Bu bir *replikasyon* testi; *seçim* testi değil. İkisi karışmış.

Ve sizin verinizde somut bir uyarı var (aşağıda).

---

## 0. Çalışma dizinindeki panodan çıkan somut bulgular

`stratejiler_final.json` içindeki 53 kaydı taradım. Kapının "kopya ayıklama" ve "hata şüphesi" adımlarının bu tabloda çalışmadığını gösteren izler:

- **Birebir kopyalar ayrı strateji sayılmış:** `L4-3` ile `R6` aynı metrik setine sahip (PF 2,83 / Sharpe 1,42 / getiri 554,3 / işlem 143,1). `L4-4` ile `VOLTRAN-R2` de aynı (2,73 / 1,33 / 462,3 / 154,7). `L8-4` ile `L8H-6` aynı getiriyi (303,7) farklı işlem sayısıyla raporluyor.
- **Birimler karışık:** işlem sayıları kimi yerde tam sayı (21, 26, 56), kimi yerde kesirli (21,7; 143,1; 229,5) — yani bir kısmı sepet ortalaması, bir kısmı tek sembol. Getiri sütunu bazı satırlarda %200–1150, bazılarında %3–70.
- **DD işareti tutarsız:** `CX*` grubunda DD negatif (−5,89; −6,01), diğerlerinde pozitif.
- **Aşırı küçük örneklem + aşırı yüksek PF:** 21–31 işlemle PF 2,8–5,4 ve %200–850 getiri. PF, N=20'de son derece kararsız bir orandır; bu tablo tam olarak "küçük örneklem yanılsaması" görüntüsü veriyor.

Bu, "13 bağımsız strateji" iddiasını da zayıflatıyor: en az 4 kayıt birebir aynı; gerçek bağımsız fikir sayısı 13'ten belirgin şekilde az olabilir. Aynı veri üzerinde seçim yapıldığı için de raporlanan PF/Sharpe'lar artık yanlı (optimistic) — geriye tarafsız bir tahmin kalmamış.

---

## 1. Adalet: iki yönde en önemli zayıflıklar

### A. İyi stratejiyi haksız yere eleme (yanlış negatif)

1. **İstatistiksel güç yok.** t ≈ SR·√T. 6 ayda SR=1 olan *gerçekten iyi* bir strateji %76 olasılıkla geçer; SR=0,5 ise %64. Yani iyi stratejilerin dörtte biri–üçte biri sadece gürültüyle eleniyor.
2. **"Kısa sınama" sadece etiket.** Elenmiyor, geçebiliyor. 6 aylık test bir piyango bileti.
3. **401 "veri yok" sistematik bir sansür.** Veri bulunabilirliği rastgele değil: egzotik semboller, vadeli işlemler, küçük kriptolar düşüyor. Bu, hayatta kalan seti ABD büyük hisse + büyük kripto lehine çarpıtıyor — yani tam olarak 2023–2026 boğasının en güçlü olduğu varlıklara.
4. **Tek sembol = idiyosinkratik piyango.** Yazarın sembolü, "yayınlandığı için" seçilmiş bir sembol. Yayın sonrası dönem bunu kısmen düzeltir, ama sembol seçimi bilgi taşımaya devam eder. İyi bir strateji yanlış sembolde negatif çıkabilir.
5. **Maliyet modeli tek yönlü iyimser.** Hisse 5 bp + 1 tick, 15 dakikalık barlarda ve orta likit isimlerde gerçekçi değil; kriptoda funding, spread ve perp bazı yok. Eksik maliyet kötüyü geçirir; yanlış uygulanan maliyet (geniş spread'li küçük hissede 1 tick) iyiyi eler. İkisi de oluyor.
6. **Manuel filtreler "hayatta kalanlara" uygulanıyor.** p10, PF, 2× maliyet, 30 işlem/yıl, korelasyon — hepsi aynı veride, geçenler üzerinde. Bu, kapıyı ikinci kez optimize etmek. "Hata şüphesi" öznel ve denetlenemez.

### B. Kötü stratejiyi haksız yere geçirme (yanlış pozitif)

1. **Eşik %50'lik bir yazı-tura.** Aşağıdaki tabloya bakın.
2. **Çoklu test kontrolü yok.** 933 + 119 test; FDR/FWER yok. 96 geçen, gürültüyle rahatça açıklanabilir.
3. **Seçim ve değerlendirme aynı pencerede.** Post-2023 tek pencere; manuel filtreler de aynı pencerede. Geriye "dokunulmamış" veri kalmamış.
4. **Minimum işlem sayısı yok.** 3 işlemle geçen bir strateji bile olabilir; panoda 21–31 işlemle PF 5 görmek bunun somut kanıtı.
5. **DSR hesaplanıyor ama kullanılmıyor; deneme sayısı belirsiz.** 933 mü, 119 mu, varyantlar mı, script içindeki parametre aramaları mı? N yanlışsa DSR de yanlış.
6. **Hayatta kalma yanlılığı.** Sadece hâlâ yayında olan scriptler; silinen, bozulan, veri kaybeden yok.
7. **26 hafta paper, kenar (edge) doğrulaması değil.** SR=1 için t≈0,7. Bu ancak operasyonel hata yakalar — ki değerli, ama "son kapı" değil.
8. **%71 geçme oranı bir alarm.** Kendi ürettiğiniz 119 varyantın 85'i geçiyorsa, elinizdeki şey bir kapı değil, kayıt defteri. Yazar scriptlerinde %24 (96/400 test edilebilir), kendi varyantlarınızda %71 — bu fark, varyantların aynı veriye daha fazla uydurulduğunun işareti.

---

## 2. "Net getiri > 0" uygun mu? Rastgele strateji hangi olasılıkla geçer?

**Hayır, uygun değil.** Bu bir *işaret testi*: H₀ "medyan getiri ≤ 0". Ne büyüklük ne de maliyet-farkında bir test.

Yıllıklandırılmış SR ve T yıl için geçme olasılığı (maliyet öncesi, tek yönlü):

| Gerçek SR | 6 ay | 1 yıl | 2 yıl | 3 yıl |
|---|---|---|---|---|
| 0,0 | **%50** | **%50** | **%50** | **%50** |
| 0,5 | %64 | %69 | %76 | %81 |
| 1,0 | %76 | %84 | %92 | %96 |
| 2,0 | %92 | %98 | %99,8 | ~%100 |

Kritik satır birincisi: **sıfır yetenekli strateji her sürede %50 geçer.** İkinci kritik nokta: 5. satır ile 1. satır arasındaki fark, 6 ayda sadece 26 puan.

Rastgele, **uzun-only**, tam maruz kalan bir strateji için: beklenen getiri ≈ piyasa sürüklenmesi. ABD hissesinde SR≈0,45 → 1 yılda geçme ≈ **%67**, 3 yılda ≈ **%78**. Kripto 2023–2025 boğasında bu daha da yüksek. İşlem maliyeti bunu düşürür (yılda 100 gidiş-dönüş × %0,1 ≈ %10 → SR'den ~0,3–1 birim), ama yine de **%40–70 bandı** kalır. Yani "rastgele strateji %5 ile geçer" varsayımı tamamen yanlış; gerçek oran **%50 civarı, boğada %70+**.

### Bunu nasıl ölçersiniz (yapılacak iş)

1. **Placebo A — giriş randomizasyonu.** Aynı sembol/evren, aynı dönem, aynı işlem sayısı, aynı tutma süresi dağılımı, aynı long-only kısıtı, aynı maliyet. Giriş barlarını rastgele seç; 2.000 tekrar. Kapının yanlış pozitif oranı = net getirisi > 0 olan placebo oranı. **Hedef: maliyet sonrası ≤ %10.**
2. **Placebo B — işlem getirisi permütasyonu.** Stratejinin kendi işlem getirilerini yerine koyarak (veya blok bootstrap) örnekle; ortalama > 0 için p-değeri. Bu, "işlem dizisinin işareti anlamlı mı" sorusunu test eder.
3. **Placebo C — sinyal zamanı karıştırma.** Getiri serisini koru, sinyal zamanlarını karıştır; aynı işlem sayısı. Sinyalin bilgi içerip içermediğini ölçer.
4. **Güç enjeksiyonu.** Placebo'ya bilinen küçük bir alfa ekle (ör. işlem başına +5 bp) ve kapının yakalama oranını ölç. **Hedef: ≥ %80.**
5. **2×2 tablo.** Gerçek stratejilerin geçme oranı vs placebo geçme oranı. Fark, kapının "lift"i. Şu an bu fark muhtemelen küçük.

Bu ölçüm, tüm teorik tartışmayı tek bir sayıya indirir: **kapının yanlış pozitif oranı.** O sayı %10'un üstündeyse kapı kalibre değildir.

---

## 3. Çoklu test: hangisi pratikte uygun?

| Yöntem | Ne yapar | Güç | Bu bağlamda verdict |
|---|---|---|---|
| **DSR** (Bailey & López de Prado 2014) | SR'yi deneme sayısı, çarpıklık, basıklık için deflate eder | Orta | **Rapor** olarak iyi; **kapı** olarak zayıf. N_eff bilinmiyor; 933 korele script'te aşırı, 1'de yetersiz cezalandırır. |
| **White Reality Check** (2000) | "En iyi strateji benchmark'ı geçiyor mu?" FWER | Düşük (muhafazakâr) | Sadece "aile içinde bir şey var mı" sorusu. Seçim yapmaz. |
| **Hansen SPA** (2005) | RC'nin güçlendirilmiş hali; kötü stratejileri dışlar | Orta-yüksek | "Aile olarak bir şey var mı" için RC'den iyi. Yine seçim yapmaz. |
| **Romano–Wolf stepdown** (2005) | Hangi stratejiler anlamlı; FWER | Yüksek | **Seçim için en uygun FWER prosedürü.** |
| **BH / BY** (1995/2001) | FDR kontrolü; BY her bağımlılıkta geçerli | Yüksek | Binlerce fikirde pratik. BY muhafazakâr ama geçerli; BH daha güçlü, PRDS varsayar. |
| **Plasebo / rastgele strateji** | Ampirik sıfır dağılımı; kapıyı kalibre eder | — | **En pratik ve en anlaşılır.** Teori gerektirmez; doğrudan yanlış pozitif oranını verir. |

**Pratik reçete (hepsi birlikte):**

1. **Aileyi önceden tanımla.** Çeyrekte test edilen tüm fikirler; korelasyon > 0,9 olanları tek küme say → N_eff.
2. **İstatistik: benchmark'a göre alfa**, HAC/Newey-West standart hata ile.
3. **Stationary bootstrap** (Politis–Romano 1994), 5.000–10.000 tekrar, blok uzunluğu veriden (≈ 5–20 gün).
4. **Romano–Wolf** ile FWER %5 → anlamlı küme. **SPA** ile "aile olarak bir şey var mı" → evet/hayır.
5. **BY** ile FDR %10 → keşif listesi (FWER listesinden daha geniş, daha riskli).
6. **DSR'yi N_eff ile raporla** — kapı değil, "bu Sharpe ne kadar şişmiş" göstergesi.
7. **Plasebo ile tüm hattı kalibre et** — kapının FP oranı ≤ %10 olana kadar eşikleri ayarla.

Tek başına hiçbiri yeterli değil. Sıralama: **plasebo (kalibrasyon) → Romano–Wolf/SPA (karar) → BY (keşif) → DSR (rapor).**

---

## 4. Boğada long-only: piyasa etkisi nasıl ayrıştırılır?

**Al-ve-tut tek başına yanıltıcı.** İki uç durum:
- %20 zamanda piyasada olan bir strateji, %100 maruz kalan B&H'yi boğada geçemez → haksız eleme.
- %100 maruz kalan bir strateji beta sayesinde geçer → haksız geçirme.

**Doğru katmanlar (hepsi raporlanmalı, karar α üzerinden):**

1. **Fazla getiri regresyonu:** r_p − r_f = α + β(r_m − r_f) + ε. HAC standart hata. **α-t > 3** (Harvey–Liu–Zhu 2016) veya bootstrap p < 0,005. β ve R²'yi de raporla.
2. **Maruziyet-eşleşmiş benchmark (asıl anahtar):** r_bench,t = w_t·r_m,t + (1−w_t)·r_f,t; w_t = stratejinin o anki pozisyon ağırlığı. Bu, "aynı zamanda piyasada olsaydım ne olurdu" sorusunu yanıtlar. Long-only için en adil karşılaştırma budur.
3. **Rastgele-giriş benchmark'ı:** aynı w_t yolu, rastgele giriş tarihleri. Placebo ile aynı fikir; ama portföy seviyesinde.
4. **Faktör modeli:** FF5 + momentum (Carhart); kripto için Liu–Tsyvinski–Wu (2022) üç faktör (piyasa, boyut, momentum). Gizli faktör tiltlerini yakalar.
5. **Zamanlama testi:** Henriksson–Merton (1981) veya Treynor–Mazuy (1966). Long-only'de beta asimetrisi kaçınılmaz; en azından ölçün.
6. **Rejim ayrımı:** up-capture / down-capture, ayı aylarında alfa. 2023–2026 tek rejim; en az bir ayı rejimi ekleyin (2022, 2018Q4, 2020-03) veya en kötü %10 piyasa bloğunun bootstrap'ını kullanın. **Şart: ayı rejiminde α > 0 veya down-capture < %80.**

Tek cümle: **"B&H'yi geçti mi" değil, "aynı maruziyetle B&H'yi geçti mi" ve "bu alpha, bilinen faktörlerden sonra kaldı mı".**

---

## 5. Farklı süreleri adil karşılaştırma

1. **Ham getiriyi asla karşılaştırma.** Yıllıklandırılmış SR ve **t = SR·√T** kullan. 6 ayda SR 2,0 (t=1,41) ile 3 yılda SR 0,8 (t=1,39) eşdeğerdir; biri "daha iyi" değildir.
2. **Güç hesabı yap ve kabul et:** %80 güç, α=0,05 çift yönlü için T ≈ (2,80/SR)². SR 0,5 → **31 yıl**; SR 1,0 → **8 yıl**; SR 2,0 → **2 yıl**. Yani 6 ay–3 yıl aralığı, gerçekçi kenarları (SR 0,5–1) ayıramaz. Bu, kapının "seçim" değil "kanıt toplama" olması gerektiğinin matematiksel kanıtı.
3. **İki pencereyi birlikte raporla:** (a) yazar-sadık pencere (birincil, iddiayı test eder), (b) ortak kesişim penceresi (ikincil, karşılaştırma için). Çelişkiyi gizleme, ikisini de göster.
4. **Eşit olmayan örneklemde sıralama:** ampirik Bayes / James–Stein shrinkage. SR_posterior = w·SR_hat + (1−w)·SR_pool, w = τ²/(τ²+σ²_i). Sıralamayı posterior ortalama ile yap; ham SR ile değil.
5. **Bağlayıcı kısıt takvim değil, işlem sayısı.** 3 yıl 15-dk bar, 20 işlem/yıl → 60 işlem. 3 yıl günlük, 20 işlem → 20 işlem. **N_trades** belirleyici. Eşik: ≥ 2 yıl **ve** ≥ 50 işlem (intraday ≥ 200). Altındaysa "geçti" değil **"yetersiz"**.
6. **Paneli kullan.** 25 sembollük sepet doğru yön; tek sembollü testleri de aynı sepete sok. N'i artırmanın en ucuz yolu bu.

---

## 6. ML binlerce fikir üretirse ne bozulur?

- **Optimizer's curse.** N bağımsız denemede, sıfır yetenekle bile beklenen maksimum SR ≈ SE·√(2 ln N). 1 yıllık testte SE≈1 → N=1.000 için **≈3,7**, N=10.000 için **≈4,3**. Yani "Sharpe 4" bir başarı değil, arama maliyetidir. (Smith & Winkler 2006)
- **FWER imkânsızlaşır.** 10.000 denemede FWER %5'i korumak için gereken eşik, gerçek kenarları da siler. FDR bile yüzlerce yanlış pozitif bırakır.
- **Goodhart.** ML, kapıyı hedef olarak öğrenir: eşik, maliyet modeli, sembol, dönem birer hiperparametre olur. Kapı sabit ve **kör** (blind) olmalı; geri bildirim verilmemeli.
- **Sızıntı.** ML aynı geçmişte eğitilip aynı geçmişte kapıdan geçirilirse, kapı sadece ezberi doğrular.
- **Anlam kaybı.** "Geçme oranı" anlamsızlaşır; yerine **seçilen setin beklenen OOS SR'si** ve **FDR** izlenmeli.

**Tasarım:**

1. **Kayıt defteri (registry):** her fikir, hipotez, evren, parametre, deneme sayısı, kod hash'i ile kaydedilir. Kayıtsız fikir değerlendirilmez. (Arnott–Harvey–Markowitz 2019)
2. **Keşif bütçesi:** çeyrek başına sabit sayıda "kabul" hakkı; FDR hedefi önceden ilan edilir.
3. **Nested CPCV + purging/embargo** (López de Prado 2018). Rastgele K-fold yasak; zaman sırası korunur, sızıntı penceresi kesilir.
4. **Donmuş holdout:** son 2–3 yıl hiç kullanılmaz; sadece final karar için bir kez açılır. Rotasyonlu tutulur.
5. **Portföy seviyesinde seçim:** tek tek "kabul" yerine, kısıtlı portföyde marjinal katkı (korelasyon, turnover, kapasite).
6. **Meta-labeling:** sinyal üretimi ile pozisyon boyutlandırma ayrılır; kapı "sinyal var mı" değil "ne kadar güvenilir" sorusunu yanıtlar.
7. **Maliyet düşmanı:** maliyet modeli kapının içinde değil, stres testinde 2× ve 3× olarak uygulanır.

---

## 7. Benim kapım

**Üç değerli çıktı:** `Geçti` / `Yetersiz` / `Reddedildi`. İkili mantık, kısa örneklemleri "geçti"ye zorluyor — asıl hata bu.

| # | Adım | Test | Eşik | Sonuç |
|---|---|---|---|---|
| 0 | **Kayıt** | Hipotez, evren, parametre, deneme sayısı, kod hash | Eksikse | Değerlendirme yok |
| 1 | **Veri & nedensellik** | PIT veri, delisting, 20 rastgele kesim, repaint/`security` lookahead, bar-magic, eksik bar, seans sınırı | **0 tolerans** | 1 ihlal → Red |
| 2 | **Uygulanabilirlik** | Gerçek spread + komisyon + 2 tick; funding/borrow; ADV ≥ 100× pozisyon | 1× maliyette net ≤ 0 | Red |
| 2b | | 2× ve 3× maliyet stresi | 2×'te marjinal | "Kırılgan" etiketi (eleme değil) |
| 3 | **Örneklem** | ≥ 2 yıl **ve** ≥ 50 işlem (intraday ≥ 200) | Altındaysa | **Yetersiz** (geçti değil) |
| 4 | **İstatistik** | Benchmark'a göre α, HAC; stationary bootstrap 5.000; Romano–Wolf FWER %5; BY FDR %10 | α-t > 3 veya boot-p < 0,005 | Red / Geç |
| 5 | **Plasebo** | Aynı işlem sayısı/süre/maruziyetle 2.000 rastgele; kapının FP oranı | FP ≤ %10; strateji placebo p95'in üstünde | Red / Geç |
| 6 | **Sağlamlık** | Parametre ±%20; alt dönemler; sembol dağılımı; ayı rejimi | ≥ %70 pozitif; ≥ %60 alt dönem pozitif; tek dönem PnL ≤ %50; ≥ %60 sembol pozitif; ayı rejiminde α > 0 | Red / Geç |
| 7 | **Portföy** | Korelasyon, marjinal SR katkısı, turnover, kapasite | ρ ≤ 0,7; ΔSR ≥ 0,05 ve bootstrap t ≥ 1,5 | Seç / Ele |
| 8 | **Paper (26 hafta)** | **Operasyonel doğrulama**, edge doğrulaması değil | KS testi p < 0,01; kayma > model + %50; işlem sıklığı ±%40; DD > backtest p95 | Durdur / Devam |
| 9 | **Forward** | Küçük sermaye, 6–12 ay | Aynı kill kriterleri | Ölçekle / Durdur |

**Ek kurallar:**

- **İki anahtar:** istatistiksel anahtar (4–6) + ekonomik anahtar (2–3). İkisi de dönmeden "geçti" yok.
- **p10 kuralı düzeltilsin:** "p10 ≤ 0 olanı çıkar" yerine **2× maliyette p10 > 0** şartı. Tek nokta tahmini değil, alt sınır.
- **"Kısa sınama" etiketi değil, "yetersiz" statüsü.** Etiket, karar değiştirmiyorsa süs.
- **Kopya ayıklama ölçüm öncesi.** Aynı sinyal korelasyonu > 0,95 olanlar tek küme; N_eff buna göre. Aksi halde DSR ve FDR yanlış hesaplanır.
- **Hata denetimi otomatikleşsin.** "Hata şüphesi" yerine: bar-magic, gelecek bar, negatif fiyat, eksik bar, seans sınırı, sinyal barının kapanışında işlem — her biri otomatik test.
- **İki bağımsız denetim:** biri **kör red-team** (stratejiyi kırmaya çalışır), biri **ayrık evrende replikasyon** (farklı semboller, aynı kod). İkisi de geçmeden final yok.
- **13'ü yeniden kapıdan geçirin.** Panodaki kopyalar ve 21–31 işlemlik kayıtlar göz önüne alındığında, muhtemelen 13'ten azı ayakta kalır. Bu kötü haber değil; doğru haber.

---

## Kaynaklar

- White, H. (2000). "A Reality Check for Data Snooping." *Econometrica* 68(5).
- Hansen, P. R. (2005). "A Test for Superior Predictive Ability." *JBES* 23(4).
- Romano, J. & Wolf, M. (2005). "Stepwise Multiple Testing as Formalized Data Snooping." *Econometrica* 73(4).
- Benjamini, Y. & Hochberg, Y. (1995). *JRSS-B* 57(1); Benjamini & Yekutieli (2001). *Annals of Statistics* 29(4).
- Bailey, D. & López de Prado, M. (2014). "The Deflated Sharpe Ratio." *Journal of Portfolio Management* 40(5).
- Bailey, Borwein, López de Prado & Zhu (2017). "The Probability of Backtest Overfitting." *Journal of Computational Finance* 20(4).
- Harvey, C., Liu, Y. & Zhu, H. (2016). "…and the Cross-Section of Expected Returns." *RFS* 29(1).
- Harvey, C. & Liu, Y. (2020). "False (and Missed) Discoveries in Financial Economics." *Journal of Finance* 75(5).
- Sullivan, R., Timmermann, A. & White, H. (1999). *Journal of Finance* 54(5).
- Bajgrowicz, P. & Scaillet, O. (2012). "Technical Trading Revisited." *JFE* 106(3).
- Politis, D. & Romano, J. (1994). "The Stationary Bootstrap." *JASA* 89(428).
- Lo, A. (2002). "The Statistics of Sharpe Ratios." *Financial Analysts Journal* 58(4).
- López de Prado, M. (2018). *Advances in Financial Machine Learning* (purged CV, CPCV).
- Smith, J. & Winkler, R. (2006). "The Optimizer's Curse." *Management Science* 52(3).
- Henriksson, R. & Merton, R. (1981). *Journal of Business* 54(4); Treynor & Mazuy (1966). *HBR*.
- Fama, E. & French, K. (2015). *JFE* 116(1); Carhart, M. (1997). *Journal of Finance* 52(1).
- Liu, Y., Tsyvinski, A. & Wu, X. (2022). "Common Risk Factors in Cryptocurrency." *Journal of Finance* 77(5).
- Arnott, R., Harvey, C. & Markowitz, H. (2019). "A Backtesting Protocol in the Era of Machine Learning." *Journal of Portfolio Management* 45(4).

**Tek cümlelik özet:** Kapıyı "getiri > 0"dan "maruziyet-eşleşmiş, maliyet-sonrası, çoklu-test düzeltilmiş alfa > 0, üstelik plaseboyla kalibre edilmiş" hâle getirin; kısa örneklemleri "geçti" değil "yetersiz" sayın; ve 13'ü seçmeden önce panodaki kopyaları ve birim tutarsızlıklarını temizleyin.