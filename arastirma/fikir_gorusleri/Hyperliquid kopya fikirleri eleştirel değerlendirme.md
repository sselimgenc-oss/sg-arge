# Hyperliquid kopya fikirleri: eleştirel değerlendirme

Oct 29, 2026 · @Selim

## Kısa özet

Asıl sorununuz fikir eksikliği değil, **istatistiksel güç** (gerçek bir fark varsa onu görebilme olasılığı). 18'e 18 kişilik oda/kontrol karşılaştırmasıyla 12 haftada yıllık %150'nin altındaki farkı göremiyorsunuz. Listedeki fikirlerin çoğu (yeni odalar, yeni pencereler, yeni kurallar) karşılaştırılan kol sayısını artırıyor; bu da gücü daha çok bölüyor ve şans eseri "kazanan" bulma olasılığını büyütüyor.

- **Önerdiğim yön:** Yeni oda açmayın. Önce ölçümü güvenilir yapın (mutabakat), sonra "seçim mümkün mü?" sorusunu 18 kişilik odada değil, arşivdeki binlerce hesap üzerinde test edin. Canlı oda kanıt üretmez, yalnızca doğrulama yapar.
- **Sanal olmanın avantajını kullanın:** Para yok, o halde oda 18 kişiyle sınırlı olmak zorunda değil. Ölçüm için ilk 100 skorlu trader'ı ve 100 kişilik kontrolü izlemek, ek maliyet olmadan gücü belirgin biçimde artırır (ortak kripto hareketi yüzünden artış tam orantılı olmaz).
- **Dürüst beklenti:** Tayvan'daki gün içi trader'lar üzerine yapılan büyük bir çalışmada, ücret sonrası öngörülebilir ve istikrarlı kazanan oranı %1'in altında bulundu ([Barber, Lee, Liu, Odean 2014](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)). Yani en olası sonuç "seçilebilir çok az kişi var ve onları az veriyle ayırt etmek zor". Bu da değerli bir bulgudur; projeyi başarısız saymayın.

## 1. Fikir tablosu

En yüksek değerliler: mutabakat (4), paralel deney (11), tarz kayması (8), kopya kapasitesi (12d) ve Deflated Sharpe (12c). En riskliler: kaldıraç odaları (2), futbol modeli (5) ve performans pencereleri (3).

| # | Fikir | Değer | Maliyet | İstatistik riski | Gerekçe |
| --- | --- | --- | --- | --- | --- |
| 4 | Operasyon / mutabakat | Yüksek | Düşük–orta | Riski azaltır | Ölçüm hatalıysa (yetim pozisyon, kaçan dolum) diğer tüm sonuçlar sessizce bozulur. |
| 11 | Paralel deney | Yüksek | Orta | Yüksek, deneme sayısı tutulmazsa | Diğer fikirleri canlı odaya dokunmadan sınamanın altyapısı; ama her deneme kaydedilip sayılmalı. |
| 12c | Deflated Sharpe (çoklu test düzeltmesi) | Yüksek | Düşük | Riski azaltır | 48 bin hesaptan seçmek dev bir çoklu test; DSR "bu kadar aday arasından şansla bu kadar iyi biri çıkar mı" sorusunu düzeltir. |
| 12d | Likidite kapasitesi / kopya aşınması | Yüksek | Orta | Düşük | Gecikme ve kayma (beklenen fiyattan kötü dolum) sonrası kaybolan getiri sahte alfadır; kârdan bağımsız bir eleme ölçütü. |
| 8 | Tarz kayması tespiti | Yüksek | Orta | Düşük–orta | Kâra değil davranışa bakar; trader değiştirmenin en temiz gerekçesi (hesap el değiştirmiş, bot değişmiş olabilir). |
| 12b | Anti-martingale disiplin skoru | Orta–yüksek | Orta | Düşük–orta | Davranış ölçer, kâr görmez; ama gelecek getiriyi öngördüğü kanıtlanmamış, önce arşivde sınanmalı. |
| 6 | Panoyu sadeleştirme | Orta | Düşük | Riski azaltır | Telefonda çok gösterge gürültüye tepki vermeye iter; bir karar ölçütü, belirsizlik aralığı ve sağlık durumu yeter. |
| 10 | Lider tablosu dışı keşif | Orta | Yüksek | Orta | Tabloya girmek zaten bir başarı filtresi (hayatta kalma yanlılığı: yalnız "yaşayanları" görmek); temsili kontrol grubu için faydalı, pahalı. |
| 3 | Performans pencereleri | Orta | Düşük | Çok yüksek | Beş pencere × odalar = çoklu test; tek, önceden yazılmış bir soru olarak arşivde yapılırsa değerli. |
| 7 | Karantina (%50 pay, 2–4 hafta) | Orta | Düşük | Orta | Risk yönetimi olarak makul; uyarı bandı kâra dayanıyorsa "kâra bakarak değiştirme" olur. |
| 12a | Calmar / maks düşüş | Düşük–orta | Düşük | Orta | Maks düşüş tek bir kötü döneme dayanır, kısa veride çok oynak; ortalama düşüş gibi daha sağlam ölçütler tercih edilmeli. |
| 5 | Futbol takımı modeli | Düşük–orta | Orta | Yüksek | Terfi/düşme son performansa bağlıysa ortalamaya dönüş (şanslı dönemden sonra normale dönme) sizi kandırır. |
| 9 | Günlük kayıp soğuması | Düşük | Düşük | Orta | Faydasını gösteren genel bir kanıt bilmiyorum; kötü günden sonraki toparlanmayı da kaçırabilir. Yalnız paralel deneyde sınayın. |
| 1 | Spot odası | Düşük | Orta | Orta | Spotta BTC/HYPE gibi ortak hareket baskın, kopyalanabilir beceri daha az; yeni kol gücü daha da böler. |
| 2 | Atak / dengeli / temkinli odalar | Düşük (atak oda zararlı) | Orta | Yüksek | >10x oda kendi kapınızdaki maks 10x kuralıyla çelişir ve 30 dk gecikmede tasfiye riski asimetriktir. Kaldıracı oda yerine raporda kırılım olarak izleyin. |

Maliyet: günümüzdeki arşiv ve kodla ne kadar iş gerektirdiği. İstatistik riski: aşırı uyum (geçmişe fazla iyi uyup geleceği tutturamamak), çoklu test ve veri gözetleme (sonuca bakıp kuralı değiştirmek) tehlikesi.

## 2. İlk 3 öncelik

Sıra önemli: önce ölçüm, sonra deney altyapısı, en son yeni seçim kuralları.

1. **Mutabakat (4) ve sade pano (6).** Ölçtüğünüz şeyin doğru olduğundan emin olmadan hiçbir sonuç güvenilir değil. Somut olarak her saat şunları kontrol edin: kopya pozisyonu ile trader pozisyonu arasındaki oran farkı, kopyada olup trader'da olmayan (yetim) pozisyonlar, kaçırılan dolum oranı, para yatırma/çekme nedeniyle hesap değerindeki sıçramalar. Pano bunları tek bir "sağlık" ışığı olarak göstersin.
2. **Paralel deney (11) ve ön kayıt defteri.** 3, 7, 9 ve 12 numaralı fikirlerin hepsi canlı odada değil burada sınanmalı. Her kuralı denemeden önce yazın (ne ölçülecek, başarı neye denir) ve toplam deneme sayısını tutun; bu sayı Deflated Sharpe'ın ihtiyaç duyduğu girdidir.
3. **Kâra bakmayan seçim ve çıkarma sinyalleri: 12d, 8, 12b (12c her zaman kapıda).** Kopya kapasitesi, tarz kayması ve disiplin skoru trader'ı son getirisine bakmadan değerlendirir. Bu, aşağıdaki tuzağın doğrudan ilacıdır.

**Birbirini tamamlayanlar**

- 4 ve 6: mutabakat sağlık ışığı sade panonun ana parçası olur.
- 11 ile 3, 7, 9, 12: paralel deney bu fikirlerin güvenli test alanıdır.
- 8 ile 5 ve 7: tarz kayması, düşürme veya karantina için kârdan bağımsız bir gerekçe verir.
- 12c ile 3 ve 10: aday ya da pencere çoğaldıkça çoklu test düzeltmesi zorunlu hale gelir.

**Çakışanlar**

- 2 (atak oda) kapınızdaki kaldıraç sınırıyla doğrudan çelişir.
- 5, 7 ve 9 üçü de "kötü gidenden uzaklaş" kuralının farklı biçimleri; üçünü birden koyarsanız hangisinin etkili olduğunu ayırt edemezsiniz. Birini seçin.
- 3 ile 12c: her yeni pencere deneme sayısını artırır ve DSR eşiğini yükseltir.
- 1 ve 2 ile mevcut test: her yeni oda zaten yetersiz olan gücü daha da böler.

## 3. "Kâra bakarak trader değiştirme" tuzağı

En büyük risk listede değil, sizin yeni "gerekçeli değiştirme" hakkınızda. Gerekçe kâr ise, 12 haftalık yasağı kaldırmak veri gözetlemeye kapı açar.

**Tuzağa düşürenler**

- **5 (futbol modeli):** Terfi ve düşme son getiriye bağlıysa şanslı olanı terfi ettirir, şanssız olanı düşürürsünüz.
- **7 (karantina) ve 9 (kayıp soğuması):** Tetikleyici kayıp ise, zirvede alıp dipte satmanın trader versiyonu olabilir.
- **3 (pencereler):** "En iyi pencereyi" geçmişe bakarak seçip ona göre oda kurmak, seçimin kendisini aşırı uydurur.
- **2 ve 12a:** Geçmişte iyi görünen kaldıraç grubu ya da Calmar sıralaması yine geçmiş kâra dayanır.

**Nasıl önlenir**

1. **Değiştirme tetikleyicilerini önceden ve kârdan bağımsız yazın:** tarz kayması, kaldıraç ihlali, kopya kapasitesinin düşmesi, hesabın pasifleşmesi, mutabakat hatası. Kâr bu listede olmasın.
2. **Kâr yalnız yavaş ve sabit takvimli bir skorda kullanılsın:** örneğin 4 haftada bir güncellenen Bölüm 5'teki büzülmüş (shrinkage) skor. Ara dönemde kâr nedeniyle değişiklik yok.
3. **Değişiklik bütçesi koyun:** ayda en fazla 2 değişiklik.
4. **Çıkarılanı izlemeye devam edin:** Çıkarılan her trader "çıkarılanlar" koluna gitsin. Birkaç ay sonra "çıkardıklarım, yerine koyduklarımdan iyi mi gitti?" sorusu kararlarınızı doğrudan ölçer. Mevcut referans kolunuz bunu oda düzeyinde yapıyor; trader düzeyinde de yapın.
5. **Kör karar verin:** Değişiklik ekranında trader'ın son getirisini gizleyin; yalnız tetikleyici ve davranış verisini gösterin.
6. **Karar günlüğü:** Tarih, gerekçe türü ve o anki veri. Sonra "kâr dışı gerekçelerle yapılan değişiklikler değer kattı mı?" diye ayrıca bakılabilir.

## 4. Listede olmayan en önemli 3 fikir

1. **Tüm arşivde kalıcılık testi (güç sorununun asıl çözümü).** "Seçim mümkün mü?" sorusunu 18'e 18 ile değil, binlerce hesapla sorun. Her 2 haftada bir tüm hesapları seçim skorunuza göre 5 dilime ayırın, sonraki 4–8 haftadaki gecikmeli kopya getirisine bakın. Skor işe yarıyorsa en üst dilimden en alta doğru getiri düzenli azalmalı. Barber ve arkadaşları Tayvan'da tam olarak bu yöntemle (yıl y'ye göre sırala, y+1'e bak) başarıyı ölçtü ([kaynak](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)). Hyperliquid'in "portfolio" sorgusu hesap değeri ve kâr geçmişini günlük, haftalık, aylık ve tüm zaman pencerelerinde veriyor ([API belgesi](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint.md)); bu, dolum sınırına takılmadan kaba bir geçmiş sağlar.
2. **Ön kayıt ve deneme sayacı.** Her yeni kural, pencere, maliyet varsayımı sonuç görülmeden bir satırla yazılsın: hipotez, ölçüt, karar eşiği, tarih. Toplam deneme sayısı panoda görünsün. Bu olmadan Deflated Sharpe de, "kaç denemede bir şans eseri başarı" hesabı da yapılamaz ([Bailey ve López de Prado 2014](https://papers.ssrn.com/abstract=2460551)). Aynı yazarların geçmiş prova aşırı uyum olasılığı (PBO: seçilen kuralın test döneminde ortalamanın altına düşme olasılığı) yöntemi de paralel deneye uygun ([SSRN 2326253](https://papers.ssrn.com/abstract=2326253)).
3. **Getiri ölçümünün temizliği ve hayatta kalma yanlılığı.** Üç tehlike var. Birincisi, hesap değerindeki artış para yatırmadan gelebilir; getiri yatırma ve çekmelerden arındırılmalı. İkincisi, belgede söylendiği gibi yalnız son 10.000 dolum sorgulanabiliyor ([API belgesi](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint.md)); çok işlem yapan trader'ların geçmişi kısa görünür ve pencere karşılaştırmaları yanlı olur. Üçüncüsü, lider tablosundan düşen ya da sıfırlanan hesaplar arşivden silinmemeli; silinirse geçmiş prova yalnız "hayatta kalanları" görür ve iyimser çıkar.

Yakın bir adım olarak, 12d'nin parçası sayılabilecek bir **gecikme eğrisi** de öneririm: aynı trader'ın getirisini 0, 5, 30 ve 120 dakika gecikmeyle hesaplayın. Getiri gecikmeyle hızla eriyorsa o trader kopyalanamaz, ne kadar iyi olursa olsun.

## 5. Az örnekle dürüst karar

En dürüst yol, soruyu "kanıtlandı mı?" yerine "ne kadar inanmalıyım ve bu inançla ne yaparım?" diye sormak, karar eşiklerini de şimdiden yazmaktır. Üç parça öneriyorum.

**A. Soruyu bölün**

- "Seçim kuralı işe yarıyor mu?" sorusu arşivde binlerce hesapla cevaplanır (Bölüm 4, madde 1).
- "Canlı oda gölgede de tutuyor mu?" sorusu 18'e 18 ile cevaplanır ve bir doğrulamadır, kanıt değildir.
- Sanal olduğu için ölçüm kolunu 100'e 100'e çıkarın; yeni maliyet getirmeden gücü artırır.

**B. Bayesçi karar kuralı (oda düzeyi)**

Her hafta oda − kontrol farkını (beta düzeltilmiş) alın. n hafta sonunda yıllık ortalama fark d̄ ve onun standart hatası se (blok bootstrap'tan) olsun. Önsel inanç (veri gelmeden önceki varsayım) şüpheci olsun: gerçek fark sıfır merkezli, standart sapması τ = yıllık %30. Sonsal (veriyle güncellenmiş inanç):

```latex
m = \bar d \cdot \frac{\tau^2}{\tau^2 + se^2}, \qquad v = \frac{\tau^2 \, se^2}{\tau^2 + se^2}, \qquad P(\text{fark} > 0) = \Phi\!\left(\frac{m}{\sqrt{v}}\right)
```

- **Örnek (benim varsayımlarımla):** Sizin simülasyonunuzdaki %150'lik saptama sınırı, kabaca se ≈ yıllık %54'e karşılık gelir. 12 haftada yıllık +%60 fark görseniz bile m ≈ %14, P(fark > 0) ≈ %71 çıkar. Yani büyük bir fark bile tek başına ikna edici değildir; bunu önceden bilmek hayal kırıklığını önler.
- **Önceden yazılacak eşikler:** P > %90 ve m maliyet tamponunun üzerindeyse genişlet. P < %25 ise durdur. Arasındaysa devam et, karar verme. 26 haftada eşik aşılmazsa "fark küçük ya da yok" kabul et.
- İki farklı τ (%15 ve %50) ile de hesaplayın; sonuç önsele çok duyarlıysa veri henüz konuşmuyor demektir.

**C. Trader düzeyinde büzülme (shrinkage)**

Tek tek trader skorlarını ham getiriyle değil, büzülmüş tahminle sıralayın. Az verisi ya da çok oynak getirisi olan trader'ın skoru grup ortalamasına doğru çekilir; tesadüfen parlayanın odaya girmesi zorlaşır:

```latex
\hat\alpha_i = w_i \, \bar x_i + (1 - w_i)\, \mu, \qquad w_i = \frac{\tau^2}{\tau^2 + \sigma_i^2 / n_i}
```

Burada x̄ trader'ın ortalama gecikmeli kopya fazla getirisi, σ oynaklığı, n hafta sayısı; μ ve τ ise tüm arşivden tahmin edilir (ampirik Bayes: önseli verinin kendisinden kurmak; [Efron, Large-Scale Inference](https://www.cambridge.org/ch/academic/subjects/statistics-probability/statistical-theory-and-methods/large-scale-inference-empirical-bayes-methods-estimation-testing-and-prediction?format=PB)). Futbol modelini kullanacaksanız terfi ve düşmeyi bu skora bağlayın.

**D. Sıralı test: her hafta bakabileceğiniz kanıt bakiyesi**

Panoya her gün baktığınız için klasik testin hata oranı bozulur. Çözüm, bakma sayısından etkilenmeyen bir e-süreci (kanıtı bahis bakiyesi gibi biriktiren gösterge):

```latex
E_t = \prod_{s=1}^{t} \left(1 + \lambda \, \frac{\operatorname{kirp}(d_s, -c, c)}{c}\right), \qquad \lambda = 0.5
```

- d haftalık oda − kontrol farkı, c tipik haftalık oynaklığın 3 katı (uç değerler kırpılır). Başlangıç 1.
- E 20'ye ulaşırsa "oda kontrolü yeniyor" demek için yanlış alarm olasılığı %5'i geçmez; kaç kez bakarsanız bakın. Haftalık farkların birbirinden kabaca bağımsız olduğu varsayılır. Daha gelişmiş biçimi için güven dizileri ([Howard ve diğerleri 2021](https://arxiv.org/abs/1810.08240v3)).
- Dürüst not: Bu yöntem güç eklemez. Mevcut güçle E büyük olasılıkla 20'ye ulaşmayacak. Değeri, sürekli bakmanın sizi kandırmasını engellemesidir.

**E. Mevcut durdurma kuralınıza bir uyarı**

60 günlük pencereler 14 günde bir kaydığı için komşu pencereler yaklaşık %77 örtüşür; bağımsız değildirler. "Yarıdan fazlasında geçemezse dur" kuralının hata oranı bu yüzden bilinmiyor. Aynı kuralı rastgele kurulmuş plasebo odalara da uygulayın ve ne sıklıkla "geçtiğine" bakın; eşiği bu sayıya göre ayarlayın.

## 6. Kaynaklar

Aşağıdaki sayfaları bugün açıp kontrol ettim veya arama sonuçlarında yayın bilgisini doğruladım.

| Kaynak | Neyi destekliyor | Durum |
| --- | --- | --- |
| [Hyperliquid API, info endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint.md) | userFills en fazla 2.000 son dolum; userFillsByTime ile yalnız son 10.000 dolum; mumlarda son 5.000; "portfolio" sorgusu | Sayfa açıldı, doğrulandı |
| [Barber, Lee, Liu, Odean (2014), J. Financial Markets](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24) | Tayvan gün içi trader'larında kalıcılık; ücret sonrası istikrarlı kazanan %1'in altında | Özet açıldı, doğrulandı |
| [Bailey ve López de Prado (2014), Deflated Sharpe Ratio](https://papers.ssrn.com/abstract=2460551) | Çoklu test ve normal olmayan getiriler için Sharpe düzeltmesi | Özet açıldı, doğrulandı |
| [Bailey, Borwein, López de Prado, Zhu, Probability of Backtest Overfitting](https://papers.ssrn.com/abstract=2326253) | Geçmiş prova aşırı uyum olasılığı | Arama sonucunda doğrulandı, sayfa açılmadı |
| [Fama ve French (2010), Luck versus Skill](https://ideas.repec.org/a/bla/jfinan/v65y2010i5p1915-1947.html) | Bootstrap ile şans ve beceriyi ayırma; beceri yalnız uçlarda | Özet açıldı, doğrulandı |
| [Apesteguia, Oechssler, Weidenholzer (2020), Copy Trading](https://econpapers.repec.org/RePEc:inm:ormnsc:v:66:y:12:i:2020:p:5608-5622) | Kopya imkanı ve başarı bilgisi aşırı risk almayı artırıyor (deney) | Özet açıldı, doğrulandı |
| [Howard, Ramdas, McAuliffe, Sekhon (2021), güven dizileri](https://arxiv.org/abs/1810.08240v3) | Her an bakılabilen geçerli sıralı çıkarım | Arama sonucunda doğrulandı |
| [Efron, Large-Scale Inference](https://www.cambridge.org/ch/academic/subjects/statistics-probability/statistical-theory-and-methods/large-scale-inference-empirical-bayes-methods-estimation-testing-and-prediction?format=PB) | Ampirik Bayes ve büzülme | Arama sonucunda doğrulandı |
| [Shefrin ve Statman (1985), disposition etkisi](https://en.wikipedia.org/wiki/Disposition_effect) | Kazancı erken satma, zararı uzun tutma eğilimi (12b'nin çıkış noktası) | Arama sonucunda doğrulandı |
| [Benjamini ve Hochberg (1995), FDR](https://citedrive.com/en/discovery/controlling-the-false-discovery-rate-a-practical-and-powerful-approach-to-multiple-testing) | Çok sayıda trader'ı aynı anda test ederken yanlış keşif oranı kontrolü | Arama sonucunda doğrulandı |

**Doğrulanamayanlar ve benim yargılarım**

- Anti-martingale disiplin skorunun gelecek getiriyi öngördüğü: doğrulanamadı, bilinen bir kanıtı bulamadım.
- Günlük kayıp soğumasının kopya getirisine etkisi: doğrulanamadı.
- Para yatırma ve çekmeleri gösteren Hyperliquid sorgusu: API sayfasında bulamadım, doğrulanamadı; ekibiniz belgenin tam dizinine bakmalı.
- Lider tablosunun \~48 bin hesap olduğu ve sizin güç simülasyonunuz: sizin verinizdir, kontrol etmedim.
- Tablodaki değer, maliyet ve risk notları ile Bölüm 5'teki τ = %30 ve eşikler: benim yargım, bir kaynaktan gelmiyor.
