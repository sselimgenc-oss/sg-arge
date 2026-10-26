# Kapı hakkında bağımsız görüş

Tarih: 2026-10-27. Bu görüş karar veya kod değişikliği değildir.

## 1. Kendi görüşüm (lider belgesini okumadan önce)

**Hüküm:** Mevcut kapı, çeviri/uygulama hatasını elemede makul; istatistiksel olarak seçilmiş alfa kanıtı üretmede zayıf. Paper'a küçük ve açıkça deneysel bir havuz almak için savunulabilir; ``geçti`` etiketini alfa/gerçek-para adaylığı gibi yorumlamak savunulamaz.

- **Kötüyü haksız geçirme — en büyük risk:** Long-only ve 2023–26 yükseliş rejiminde net > 0, zamanlama değil piyasa maruziyetini ödüllendirir. 933 + 119 fikir arasından kazananı seçmek, tek strateji p-değerini anlamsızlaştırır. Sonuç görüldükten sonraki p10/PF/maliyet/işlem sayısı elemesi de fiilen ek deneme ve seçici serbestliktir.
- **İyiyi haksız eleme — ikinci risk:** Yılda 30 işlem ve tek sembole sadakat, seyrek trend veya negatif-betalı koruyucu stratejileri dışlayabilir. ``veri_yok`` ve yorumlayıcı uyumsuzluğu rastgele değilse test edilebilir evreni yanlı seçer. Buna karşılık düşük işlem sayısının korunması gerekir; çözüm eşiği gevşetmek değil, sonucu **Yetersiz** yapmak veya önceden tanımlı bir sepette doğrulamaktır.
- **Nedensellik testi ve sürüm-sonrası sınama güçlü yönlerdir.** Bunlar sırasıyla uygulama sahteciliğini ve yazarın geçmişe uyumunu azaltır; fakat kendi hipotezinizde ve 2023+ sepete taşınan TV kurallarında araştırmacının dönem bilgisi yüzünden gerçek OOS değildir.

### Net > 0

- Sıfır beklentili, simetrik ve bağımsız getiride olasılık kabaca %50'dir. Pozitif piyasa drift'i, yüksek long maruziyeti, otokorelasyon ve kısa örneklem bunu önemli ölçüde yükseltir; tek bir evrensel yüzde vermek doğru değildir.
- Ölçüm: her strateji için **aynı piyasa, dönem, yön karışımı, işlem sayısı, tutma süresi ve maliyetle** en az 1.000 giriş-permütasyon plasebosu; ``P(null net > 0)`` kapının gerçekleşmiş yanlış-geçme oranıdır. Stratejinin plasebo yüzdeliği/p-değeri ayrıca raporlanır.
- Bu nedenle net > 0 yalnız gerekli bir ekonomik tutarlılık kontrolü olmalı; tek başına geçme koşulu olmamalı.

### Çoklu test ve piyasa etkisi

- **İlk tercih:** Önceden tanımlı ailede geçerli p-değerlerine BHY-FDR (bağımlılık altında muhafazakâr) uygulanmalı. BH/BHY yalnız p-değerleri test hipotezine uygun ve seçimden önce tanımlıysa anlamlıdır.
- **Son liste:** Aynı kıyas ve aynı tarih için White Reality Check veya daha güçlü/pratik SPA; bootstrap blok uzunluğu ve aday ailesi önceden kilitlenmeli. Romano–Wolf, birden çok hipotez/istatistik için uygundur ama daha ağırdır.
- **DSR:** Faydalı bir bilgi sütunu ve minimum eşiğe ek koruma olabilir; deneme sayısı ile aday korelasyonunu yaklaşıklaştırır, ancak tüm araştırma yollarını ve veri/parametre seçimlerini saymaz. Tek başına FWER/FDR düzeltmesi değildir.
- **Plasebo:** En anlaşılır ve bu proje için en yüksek getirili ilk kontrol; gerçek motorla, aynı çıkış/dolum kurallarıyla çalışmalıdır. Yerine yalnız getiri serisi permütasyonu konursa giriş-çıkış etkileşimi kaybolur.
- Long-only için kıyas, al-tut değil **maruziyet eşleşmiş piyasa + nakit** olmalı. Ardından günlük excess return üzerinde beta ve alfa, Newey–West standart hatası (en az 5 gecikme; frekansa göre ön kayıtlı) raporlanmalı. Beta ayarlı alfa pozitif olsa da çoklu-test ve rejim riski çözülmüş sayılmaz.

### Farklı süreler, paper ve ML

- Ham getiri karşılaştırılmaz. Aynı para biriminde maliyet sonrası günlük/haftalık excess return; yıllıklaştırılmış alfa, NW t, PSR/Sharpe alt sınırı ve plasebo p-değeri birlikte verilir. Kısa örneklem ``geçti`` değil **Yetersiz**; bu adalet için önemlidir.
- 26 hafta paper, sinyal zamanlaması, veri, dolum ve operasyon için değerlidir; bağımsız işlem haftası/işlem sayısı yoksa alfa kanıtı değildir. Paper sonucunu mevcut backtest seçimiyle birleştirmek de seçimi doğrulamaz.
- ML'de yayın tarihi bariyeri yoktur. Binlerce model/özellik/etiket/erken-durdurma denemesi saklanmazsa kapı çöker: en iyi Sharpe beklenen gürültü olabilir. Ayrı araştırma/validasyon/test dönemleri, her denemenin kaydı, tek-kullanımlık kilitli holdout, zaman-serisi CPCV/PBO ve son holdout'a yalnız bir kez erişim gerekir.

### Önerdiğim yeni-strateji kapısı

1. Hipotez, veri, evren, maliyet, parametre ızgarası, deneme ailesi ve eşikler **çalışmadan önce** kayda geçer.
2. Nedensellik/repaint/dolum denetimi; ardından yazar sadakati değil, uygulanabilir gerçekçi sonuç.
3. Asgari kanıt: en az 1 yıl ve 50 işlem **veya** önceden kayıtlı çoklu-varlık sepetinde yeterli bağımsız aktif hafta. Aksi: Yetersiz.
4. Net > 0, 2x maliyette net > 0 veya açık ``kırılgan`` etiketi; ±1 bar ve parametre ±%20 sağlamlığı bilgi değil zorunlu testtir.
5. Aynı motorla giriş plasebosu: p ≤ 0,05 (keşifte en fazla 0,10 etiketi, terfi değil).
6. Maruziyet eşleşmiş kıyasa göre yıllık alfa > 0 ve NW t ≥ 2; ML/çok büyük ailede t ≥ 3 yalnız ön eleme, kesin kanıt değil.
7. Aile düzeyinde BHY q ≤ 0,10; kısa listenin tamamında SPA/RC. DSR, N_eff ve ham N raporlanır.
8. Sıralama: risk-bütçeli marjinal portföy katkısı ve hiyerarşik kümeleme. Paper: icra doğrulaması; gerçek para kararı ayrı ve kullanıcıya aittir.

### Tüm evreni yeniden değerlendirme sırası

1. Önce sonuçlara bakmadan aileleri ayırın: TV yayımlı, kendi hipotezi, U7 sepete taşınanlar, ML. Her aile için deneme defterini mümkün olduğu kadar geriye dönük tamamlayın; eksik sayıyı alt sınır değil üst sınır olarak işaretleyin.
2. Veri/yorumlayıcı paritesini rastgele değil, katmanlı örneklemle doğrulayın; ``veri_yok``/``işlem_yok`` kararlarını ayrı kapsama raporlayın.
3. Tarih kesimlerini, maliyeti, benchmarkı, plasebo tasarımını, asgari örneklemi, p/t/q eşiklerini ve kümeyi dondurun; pilot sonuçları **bu dondurmadan önce** yalnız kalibrasyon için kullanın.
4. Her aday için önce uygulanabilir getiri, plasebo ve alfa; sonra aile içi BHY; sonra önceden sabit kısa listeye SPA/RC uygulayın. Aynı sonuçlarla yeni eşik seçmeyin.
5. Sadece bu zincirin sonunda portföy-küme seçimi yapın. Daha sonra bulunan istisna yeni sürüm/ayrı ailedir; önceki sonuçlarla birleştirilmez.

## 2. Lider belgesini okuduktan sonra: uzlaşma ve ayrışma

### Katıldıklarım

- Ortak hüküm doğru: net > 0 kapısı geçirgen; piyasa etkisi, çoklu test ve kısa örneklem birlikte ele alınmalı.
- Maruziyet eşleşmiş kıyas, NW alfa, giriş plasebosu, N_eff ve önceden yazılı otomatik kurallar doğru yön.
- Argon'un uyarısı önemli: 2026'da tasarlanıp 2023–26'da test edilen U4/U7 fikirleri gerçek OOS değildir.
- Liderin somut bulgusu belirleyici: eski null testinde paper'daki 11 U7 kitabından yalnız birinin geçmesi, giriş kenarı iddiasını ciddi biçimde zayıflatır. Bu kitaplar şimdilik ``alfa`` değil ``piyasa/çıkış kuralı deneyi`` olarak etiketlenmeli.
- Mevcut paper'ı geriye dönük değiştirmemek makul; bu yeni kapı gelecek seçim ve ayrı gölge değerlendirme için kullanılmalı.

### Ayrıştıklarım / ek şerhler

- ``Plasebo %95 üstü`` tek başına yeterli kapı değildir. Aynı ailede çok aday varsa plasebo p-değerleri BHY/SPA zincirine girmeli; aksi halde %5 eşiği yüzlerce adayda beklenen yanlış pozitif üretir.
- ``NW t ≥ 2`` de tek başına kesin eşik değildir: kısa, ağır kuyruklu ve üst üste binen tutma süreli seride boyut bozulabilir. Blok bootstrap güven aralığıyla kontrol edilmeli; ML için t ≥ 3 bile çoklu seçimden sonra yeterli kabul edilmemeli.
- ≥50 işlem + ≥1 yıl kuralını mutlaklaştırmıyorum. Çok-varlıklı, önceden sabit bir sepetin bağımsız aktif haftaları yeterliyse seyrek strateji Yetersiz yerine sepet düzeyinde sınanabilir. Buna karşılık tek enstrümanda 30/yıl yerine sabit bir eşik koymak keyfîdir.
- White RC/SPA'yı yalnız nihai, önceden kilitli aday ailesinde kullanırım. Sonuçlara bakılarak daraltılmış 13 aday üzerinde çalıştırmak, orijinal araştırma evrenini unutursa seçilim cezasını küçültür.

## Kaynaklar

- White (2000), *A Reality Check for Data Snooping*.
- Hansen (2005), *A Test for Superior Predictive Ability*.
- Benjamini & Yekutieli (2001), bağımlılık altında FDR kontrolü.
- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*.
- Harvey, Liu & Zhu (2016), *…and the Cross-Section of Expected Returns*; çoklu deneme uyarısı.
- Bailey et al. (2017), *The Probability of Backtest Overfitting*.
- Arnott, Harvey & Markowitz (2019), *A Backtesting Protocol in the Era of Machine Learning*.
