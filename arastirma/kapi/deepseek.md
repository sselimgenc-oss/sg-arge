## Kısa hüküm

Kapı **iyi niyetli ama istatistiksel olarak zayıf**: asıl sorunu "çok sıkı" olması değil, **iki farklı soruyu tek araçla yanıtlaması**. (a) "Yazarın iddiası doğru mu?" ile (b) "Bunu trade etmeli miyiz?" aynı şey değil. "Sadık test" (a) için doğru, (b) için yanlış bir tasarım. Ayrıca geçme şartı **beta'ya karşı korumasız**; 2023–2026 boğasında bu, kapının en büyük açığı.

En çarpıcı iki sayı sizde zaten var:
- Yayımlanmış 933'te test edilebilenlerin **%24'ü** geçmiş (96/400).
- Kendi varyantlarınızda **%71'i** geçmiş (85/119).
- Rastgele, %50 pozisyonlu, long-only bir stratejinin bu pencerede geçme olasılığı ~%70–85 (aşağıda). Yani 933'lük popülasyon rastgeleden *kötü*, 119'luk popülasyon ise rastgeleye *eşit* görünüyor. Bu, kapının değil, **seçim etkisinin ve in-sample tasarımın** işareti.

---

## 1) Adil mi? Haksız eleme ve haksız geçirme (önem sırasıyla)

**Haksız eleme (yanlış negatif) — en önemliden:**
1. **Güç yok.** 6 aylık pencerede gerçek Sharpe'ı 1.0 olan bir strateji bile ~%24 ihtimalle negatif biter; Sharpe 0.5'te bu ~%36. Yani iyi stratejileri şansa eliyorsunuz. (MinTRL: SR=1 için 90–95% güvende **~5–7 yıl** gerekir — Bailey & LdP 2012.)
2. **Tek sembol = tek çekiliş.** "Yazarın sembolü" sadakati, iyi stratejiyi kötü sembolde öldürür, kötüyü şanslı sembolde yaşatır. Seçim için gereken **sağlamlık**, sadakat değil.
3. **Maliyet modeli iyimser.** 5 bp/taraf + 1 tick: likit ABD büyük hissede kabul edilebilir; küçük hisse, 15 dk bar, emtia ve kripto'da değil. Kripto 10 bp/taraf + spread + perp funding + likidite etkisi yok. (Novy-Marx & Velikov 2016 maliyet duyarlılığını gösteriyor.)
4. **Uygulama varsayımları.** Aynı bar kapanışında giriş, limit emrin "değdi" sayılması, kısmi dolum yok, gap yok. Gerçek getiri kaybının çoğu burada.
5. **%43 test edilemedi.** Ücretsiz veri yokluğu rastgele değil; etiket setiniz "verisi olan semboller" yanlılığı taşıyor. ML eğitimi için bu ciddi.
6. **Yorumlayıcı riski.** 93 işlemsiz + 39 sonuçsuz = %14 çözülmemiş. Pine yorumlayıcınızın TradingView ile farkı ölçülmemişse "sadık test" iddiası çöker. En az 50 stratejide TV çıktısıyla satır satır karşılaştırma şart.

**Haksız geçirme (yanlış pozitif) — en önemliden:**
1. **Beta süzgeci yok.** Long-only + boğa piyasası + "net > 0" = piyasa getirisini keşfetmek. En büyük açık bu.
2. **DSR hesaplanıyor ama elenmiyor.** Elinizde doğru alet var, kullanmıyorsunuz. N≈1000'de DSR eşiği yıllık SR ≈ **1.5–1.9**; 13'ünüzün çoğu bunu geçmez. Bu, kapının gerçek testi.
3. **Manuel filtreler sonradan seçilmiş.** p10, PF<1.2, 30 işlem, 0.6 korelasyon eşikleri sonuçları gördükten sonra konduysa, 13 aynı veride tasarlanmış bir filtrenin ürünü → "garden of forking paths".
4. **PF kötü bir istatistik.** Birkaç işleme aşırı duyarlı, ölçeksiz, geniş stop'la şişirilebilir. PF yerine **expectancy + alt güven sınırı**.
5. **26 hafta paper trade istatistiksel olarak boş.** 26 haftada yıllık Sharpe'ın SE'si ~1.4. Bu bir *execution/plumbing* testi; karar testi değil.
6. **Nedensellik testi dar.** Kesimden önceki emirleri değiştirmeyen look-ahead'i (bar kapanışında aynı bardan dolum, `request.security(lookahead=on)`, repaint) kaçırır. "Sadık test", yazarın look-ahead'ini sadakatle kopyalamak anlamına da gelebilir.

---

## 2) "Net getiri > 0" uygun mu? Rastgele strateji hangi olasılıkla geçer?

**Hayır, uygun değil** — çünkü sıfır hipotezi "sıfır getiri" değil. Long-only bir stratejinin null'ı **piyasa drifti × maruziyet**tir.

Kaba formül: geçme olasılığı ≈ Φ(SR·√T), SR yıllık, T yıl.

| Senaryo (2023–26, ABD hisse) | Yaklaşık SR | T=2 → geçme |
|---|---|---|
| Rastgele long-only, %100 maruziyet | ~1.0 | **~%92** |
| Rastgele long-only, %50 maruziyet, maliyet sonrası | ~0.4 | **~%72** |
| Rastgele long/short, düşük devir | ~−0.2 | ~%39 |
| Rastgele long/short, yüksek devir | ~−0.6 | ~%20 |

Yani geçme olasılığı **maruziyete bağlı**; kapınız maruziyeti kontrol etmiyor → long-only için fiili yanlış pozitif oranı %70–90.

**Nasıl ölçülür (yapılması gereken tek şey):**
1. Null üreticisini eşleştir: aynı evren, aynı tarih, aynı **maruziyet**, aynı işlem sayısı, aynı tutma süresi dağılımı, aynı long/short karışımı.
2. 2.000–10.000 sentetik strateji üret (giriş tarihleri rastgele, veya sinyali blok-bootstrap'la).
3. **Aynı pipeline'dan** (maliyetler dahil) geçir.
4. Ampirik FPR = geçenlerin oranı. Timeframe ve maruziyet kırılımında raporla.
5. Eşiği FPR ≤ %5 olacak şekilde ayarla.

Ek iki ucuz test: **shift testi** (sinyali +k bar kaydır; getiri çökmiyorsa zamanlama bilgisi yok) ve **random exit** (girişler aynı, çıkışlar rastgele).

---

## 3) Çoklu test: hangisi pratikte en uygun?

| Yöntem | Neyi kontrol eder | Zayıflığı | Sizde kullanım |
|---|---|---|---|
| **DSR** (Bailey & LdP 2014) | Tek strateji, N deneme, skew/kurt | N_eff gerekir; az işlemde güvenilmez | **Kapı olarak kullanın** (şu an bilgi amaçlı — yanlış) |
| **BHY** (2001) | FDR, keyfî bağımlılıkta geçerli | Muhafazakâr; p-değeri null'ı yine beta içerir | Etiket/rapor için |
| **White RC** (2000) | "En iyi strateji benchmark'ı geçiyor mu" | Kötü alternatiflere karşı güçsüz | Aile testi |
| **Hansen SPA** (2005) | Aynı, studentized + iyileştirme | Tek "en iyi" sorusu; sıralama vermez | **RC yerine bunu** |
| **Plasebo/permütasyon** | Tüm pipeline'ın ampirik FPR'ı | Pahalı; strateji-bazlı değil | **Eşik kalibrasyonu + iletişim** |
| **PBO / CSCV** (Bailey vd. 2017) | Backtest aşırı uyum olasılığı | Tüm arama sürecini bilmek ister | ML ölçeğinde **zorunlu** |

**Pratik öneri (katmanlı):**
1. İstatistiği **benchmark'a göre fazla getiri** yap (yoksa beta test ediyorsunuz).
2. Her stratejiye **DSR ≥ 0.95**, N_eff = korelasyon kümelemesiyle düzeltilmiş deneme sayısı.
3. Hayatta kalan aileye **Hansen SPA**, p < 0.05.
4. **Plasebo** ile ampirik FPR'ı ölç ve raporla (yönetime/denetime en ikna edici sayı).
5. BHY'yi yalnızca etiketleme için tut.

Not: N≈1000'de beklenen maksimum null Sharpe ≈ **1.9** (N=100'de ≈1.5). Yani "SR>0" eşiği, gürültü tavanının ~2σ altında. Harvey-Liu-Zhu (2016) yeni faktörler için **t > 3.0** öneriyor; sizin ölçeğinizde bu yetmez.

---

## 4) Boğada long-only: piyasa etkisi nasıl ayrıştırılır?

**Sadece al-ve-tut yetmez** — maruziyeti hesaba katmaz. Sıra:

1. **Maruziyet-eşleşmiş benchmark** (asgari): aynı zaman-içi-piyasa oranı × aynı evren eşit ağırlık. %30 maruz kalan stratejiyi %100 endeksle kıyaslamak haksız.
2. **Faktör regresyonu:** günlük getirilerde FF5 + momentum (kripto için piyasa/boyut/momentum), **Newey-West** t. 15 dk barlarda regresyon yapmayın (Epps etkisi, mikro yapı gürültüsü).
3. **En temiz test: giriş permütasyonu.** Aynı işlem sayısı ve tutma süresiyle girişleri rastgeleleştir; strateji bu dağılımın **95. yüzdeliğini** geçmeli. Bu, beta'yı doğrudan çıkarır.
4. **Raporla:** beta, R², alpha ve t(alpha). R² > 0.7 ve t(alpha) < 2 ise bu bir beta ürünüdür — kaç stratejinizin böyle olduğunu görün.
5. **Boşta nakit** risksiz faiz kazanmalı (cash drag).

**Geçme şartı:** `alpha > 0` **ve** `t(alpha) ≥ 3.0` **ve** giriş-permütasyon 95. yüzdelik üstü. "Net > 0" değil.

---

## 5) 6 ay – 3 yıl arası farklı süreleri adil karşılaştırma

- **Toplam getiriyi asla kıyaslamayın.** Yıllıklaştırın ve **güven aralığı** verin.
- Sıralama metriği: **yıllık Sharpe'ın alt güven sınırı** (blok bootstrap, stationary bootstrap — Politis & Romano 1994, blok ≈ n^(1/3)). LCB, kısa T'yi otomatik cezalandırır; p10'u farklı T'lerde kıyaslamak geçersiz.
- **Asgari örnek:** ≥ 24 ay **ve** ≥ 100 kapalı işlem **ve** ≥ 2 rejim. 6 aylık pencere yalnızca *reddetmek* için kullanılabilir, *onaylamak* için değil.
- **Ortak pencere + kendi penceresi:** her strateji için (i) ortak kesişim penceresi (ör. 2024-01→2026-06), (ii) yayın sonrası pencere. İkisini de raporlayın.
- **Haftalık p10'u bırakın:** 15 dk stratejisinin haftalık getirisi otokorelasyonu ve maliyet zamanlamasını gizler; günlük getiri + LCB kullanın.
- DSR zaten T'ye göre düzeltir; ama N_eff'i de düzeltin.

---

## 6) ML binlerce fikir üretirse ne bozulur?

- **Eşik patlar.** Gerekli t ≈ √(2 ln N): N=10³→3.7, 10⁵→4.8, 10⁶→5.3. "t>3" ML ölçeğinde komik.
- **Deneme sayısı ölçülemez olur.** Her hiperparametre, feature seçimi, CV katı bir denemedir. **Deney kayıt defteri** (trial registry) ve `N_eff` zorunlu.
- **OOS kirlenir.** Kapı bir **fitness fonksiyonu** olur → Goodhart. ML kapıyı geçmeyi öğrenir, kâr etmeyi değil. Çözüm: kilitli, hiç dokunulmayan son holdout + rastgeleleştirilmiş/gizli eşikler.
- **Veri sızıntısı ölçekte ölür.** PIT evren, delisting getirisi, kurumsal işlemler, vendor revizyonları, timestamp hizası. 933'te manuel yakalayabilirsiniz; 10⁶'de yakalayamazsınız.
- **Yorumlayıcı denetimi ölçeklenmez.** 14% çözülmemiş oran 10⁶'de felaket. Otomatik referans-diff şart.
- **İnsan denetimi ölçeklenmez.** "İki bağımsız denetim" 1.000'de anlamlı, 100.000'de değil. Örneklemeli + otomatik.
- **Maliyet modeli isim-bazlı olmalı.** Düz 5 bp, ML'in likit olmayan isimlere kaçmasını ödüllendirir.
- **PBO/CSCV + purged & embargo'lu CV** (López de Prado 2018) zorunlu hale gelir.
- **Karar kuralı değişmeli:** ikili kapı yerine **sıralama + yanlış keşif bütçesi** (ör. 13 slot için beklenen ≤1 yanlış → FDR ≤ %8).

---

## 7) Benim önerdiğim kapı (somut)

**Aşama 0 — Veri hijyeni (kill switch).** PIT evren, delisting, split/temettü, bar-kapanış hizası; eksik bar > %2 ise reddet; < 3 yıl geçmiş reddet. Maliyet: likit hisse 8–10 bp/taraf, küçük hisse 20+, kripto 10 bp + yarım spread + funding, vadeli 1 tick + komisyon. Kareköklü etki: `impact ≈ σ·√(Q/ADV)`. 2× ve 3× stres.

**Aşama 1 — Geçerlilik.** Sizin truncation testi + (i) tüm girdileri 1 bar geri kaydırınca sonuç *bozulmalı*, (ii) `lookahead`/repaint/aynı-bar dolum taraması, (iii) 50 stratejide TV-yorumlayıcı diff.

**Aşama 2 — Benchmark'a göre performans (asıl geçme şartı).** Günlük net getiri, nakit rf'de. Eşleşmiş benchmark + FF5+MOM alpha, NW t. **Geçme:** `alpha > 0` ∧ `t(alpha) ≥ 3.0` ∧ giriş-permütasyon 95p üstü ∧ IR LCB > 0.

**Aşama 3 — Çokluluk.** Tüm denemeleri kaydet; `N_eff` (korelasyon kümesi). **DSR ≥ 0.95**. Hayatta kalan aileye **SPA p < 0.05** ve **PBO < 0.3**. 2.000 plasebo ile ampirik FPR raporla; FPR > %5 ise eşikleri sık.

**Aşama 4 — Sağlamlık.** Parametre ±%20'de uçurum yok; yuvarlanan 1-yıllık pencerelerin ≥%60'ında pozitif; en iyi sembolü çıkarınca hâlâ pozitif; 2× maliyette pozitif; ADV katılımı < %1; maks DD < %30, Calmar > 0.5.

**Aşama 5 — Portföy.** Greedy değil **hiyerarşik kümeleme** ile korelasyon; maruziyet kümeleri arası ≥ 0.5 ayrıştırma; marjinal Sharpe katkısı > 0.

**Aşama 6 — Paper trade (istatistik değil, icra testi).** ≥ 100 işlem veya 6 ay; gerçekleşen kayma modelin 2 SD'si içinde olmalı; 2× aşarsa öldür. İstatistiksel karar ancak MinTRL dolunca.

**Ek (en değerli tek öneri):** Paper'a alınan 13'ün yanına, kapıyı **az farkla kaçıran rastgele 13 strateji** koyun (kontrol grubu). 26 hafta sonra kapınızın canlı FPR'ını ölçmüş olursunuz. Bu, tüm kapı tasarımından daha bilgilendirici.

---

## Kaynaklar

- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*, JPM 40(5).
- Bailey & López de Prado (2012), *The Sharpe Ratio Efficient Frontier*, Journal of Risk 15(2) — MinTRL.
- Bailey, Borwein, LdP, Zhu (2017), *The Probability of Backtest Overfitting*, J. Computational Finance 20(4) — PBO/CSCV.
- White (2000), *A Reality Check for Data Snooping*, Econometrica 68(5).
- Hansen (2005), *A Test for Superior Predictive Ability*, JBES 23(4).
- Benjamini & Yekutieli (2001), *FDR under Dependency*, Annals of Statistics 29(4).
- Harvey, Liu, Zhu (2016), *…and the Cross-Section of Expected Returns*, RFS 29(1) — t>3.
- Harvey & Liu (2015), *Backtesting*, JPM 42(1) — Sharpe haircut.
- Sullivan, Timmermann, White (1999), *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*, JF.
- Politis & Romano (1994), *The Stationary Bootstrap*, JASA.
- Novy-Marx & Velikov (2016), *A Taxonomy of Anomalies and Their Trading Costs*, RFS.
- Arnott, Harvey, Markowitz (2019), *A Backtesting Protocol in the Era of Machine Learning*, JFDS.
- López de Prado (2018), *Advances in Financial Machine Learning* — purged/embargoed CV.

**Tek cümlelik teşhis:** Kapınız "kötü stratejiyi geçirme" tarafında beta yüzünden, "iyi stratejiyi eleme" tarafında ise kısa pencere ve tek-sembol gürültüsü yüzünden zayıf; DSR'yi bilgi amaçlı bırakmanız ise elinizdeki en güçlü aleti kullanmamak.