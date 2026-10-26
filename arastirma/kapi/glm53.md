Kapı Eleştirisi (bağımsız bakış)
Önce genel yargı: Kapı sıradan bir backtest sürecinden iyi (nedensellik kontrolü, sadık test, maliyet farkındalığı, kopya ayıklama var). Ama istikrarlı bir seçim makinesi değil: geçiş şartı istatistiksel olarak çok zayıf, çoklu test düzeltmesi yok, geçiş sonrası elle ekranlar öznel ve kayıt dışı. Aşağıda soru soru.

1) Adil mi?
İyi stratejiyi haksız yere elenmesi (yanlış negatif):

"Net getiri > 0" tek yol, tek veri. 6 aylık pencerede gerçek bir avantaj negatif net getiriyle karşınıza çıkabilir. Varyans, neredeyse her şeyi belirliyor. Sınama süresi 6 ay–3 yıl arasında değişiyor: eşik sabit ama örneklem gücü 36 kat farklı.
Sadık test, yazarın overfit'ini koruyor. "Kendi sembolü, kendi zaman dilimi" = yazarın zaten veriye fit ettiği kombinasyonu doğulamak. Sadakat, yazara adil; stratejinin genel geçerliliğine değil.
Yayın tarihi kesimi güvenilir değil. Pine stratejileri revize edilir; "yayımlandıktan sonraki dönem" yazarın sürüm yinelemeleriyle (versiyon isabeti, popülerlik etkisi) kirlenebilir.
%0,05/taraf + 1 tick küçük ölçekli yüksek devirli 15 dk stratejileri için iyimser olabilir (özellikle likiditesi düşük sembollerde). Kripto %0,1/taraf taker fiyatı; maker iptal edilebilir, kalıcı sözleşmelerde funding rate yok.
Pine yorumlayıcı farkları (emir doldurma varsayımı, fill_orders_on_*, bar magnifier vb.) hem yanlış elme hem yanlış geçiş üretir; 93 "hiç işlem yapmayan"ın bir kısmı muhtemelen çeviri hatası, strateji değil.
401 test edilemedi = seçim evreni ücretsiz verinin evrenine sıkıştı, bu da popüler/likit sembollere, yani kalabalık işlem gören fikirlere doğru bir biyasa üretir.
Kötü stratejiyi haksız yere geçirmesi (yanlış pozitif) — daha büyük problem:

Geçiş şartı anlamlılık içermiyor: "net > 0" bir kat, ihtimallerin oynadığı tek ölçüm (bkz. Soru 2).
2023–2026 boğa dönemi + long ağırlıklı: para kazanan hemen her long strateji geçer; sınama döneminde piyasa getirisinden ayrışma (alfa) hiç ölçülmüyor.
933 + 119 → ~1.050 deneme; geçenler aynı sınama verisi üzerinde seçiliyor. Bu klasik veri snooping: hayatta kalanların görünür Sharpe'ı sistematik olarak şişik (winner's curse).
Kapıdan sonra elle ekranlar (PF < 1,2, 2× maliyet, "hata şüphesi") arbitrary ve denetçiye açık: her psikolojik bütçe ve cherry-picking için bir serbestlik derecesi. Bunlar kapının içine, ölçülebilir ve kaydı/anlamı önceden belirlenmiş kurallar olarak girmeli.
2) "Net getiri > 0": rastgele strateji hangi olasılıkla geçer?
Sıfır avantajlı, işlem başına simetrik dağılım varsayımıyla, maliyetsiz: P(pass) ≈ %50.
Maliyet sürüklemesi yıkıcı değil: 0,1% tur başına maliyet × ~200 işlem → −20% sürükleme; işlem başına σ ≈ %2 ise σ_t ≈ %28 → P(pass) ≈ Φ(−0,7) ≈ %25 civarı. Yani hisse tarafında kapı, madalyonun kuyruklu yüzüne yakın bir para atışı.
Long-only + boğa piyasası sürüklemesi pozitif ve büyüktür (BTC/SPY 2023–24): rastgele bir long stratejinin geçme olasılığı %50'ye ta çıkabilir, kripto tarafında muhtemelen>%50.
Ayrıca formal kriter: Sharpe anlamlılığı t ≈ SR·√T(yıl). %95 tek yanlı test için SR₀,₅ yıllık 0,95:T = 3 yıl → SR ≈ 0,95 gerekir; T = 6 ay → SR ≈ 2,3. "Net > 0" bunun çok çok altında.
Nasıl ölçülür (pratik): Aynı veri, aynı maliyet, aynı sürdürme süresi/işlem sayısı ile permütasyon/ Monte Carlo sıfır dağılımı üretin: giriş zamanlarını yerinde rastgele kaydır veya sinyalleri koruyarak rastgele giriş üret (Aronson'ın "Monte Carlo permutation" testi, 2007). Stratejinin sonucunu bu dağılıma kıyasla dene: kapı "net > 0" değil, "sıfır dağılımın %90–95'ini yensin" demeli.
Kaynak: Aronson (2007), Evidence-Based Technical Analysis; Hsu–Kuan (2005).
3) Çoklu test / seçim yanlılığı
DSR: hesaplaması kolay, strateji başına düzeltme; ama etkin deneme sayısı N_t gerçekten bilinmeli (sizin durumda en az 1052, korelasyonlu varyantlarla etkin N daha az — kümeleme ile şişmiş sayıyı küçültün). Şu an "bilgi amaçlı" tutuyorsunuz; aslında eleme şartına çevirilmeli (DSR > 0 veya PSR ≥ ~%90).
White RC / Hansen SPA: ailenin en iyisini sınamak için doğru araç, ama binlerce ML stratejisiyle iki kez (artık + evrimleşen aile) durumunda katı yapılır; animasyon bir bitmeli.
BHY (FDR): binlerce paralel hipotezi, aile çok büyükse en pratik kontrol (Hansen SPA tam aile kovaryansını ister; BHY ölçeklenir). Bajgrowicz–Scaillet (2012) teknik kurallarda aynen bunu yapar.
Plasebo/permütasyon testi: sizin kurulumunuz için en uygun olan bu — kapıdaki "geçme olasılığı" sorununu doğrudan ölçer ve ML üretimli evrende bile model-agnostik çalışır.
Pratik önerim: tarama aşamasında BHY-FDR (q ≈ 0,10–0,25) + permütasyon ile sıfır dağılım kalibrasyonu; final kısa listeye gece Hansen SPA p-değeri (Reality Check'in güçsüzlüğünü düzelten versiyon). DSR'i de kişisel ön-eleme olarak tutun. Kaynaklar: White (2000); Hansen (2005); Bailey vd. (2014, DSR/ PBO); Bailey–LdP (2014, "Pseudo-Mathematics"); Harvey–Liu–Zhu (2016); Benjamini–Yekutieli (2001).

4) Long-only + boğa piyasası: piyasa etkisi ayrıştırma
En basit ve iptal edici kıyas: aynı para/basketi al-ve-tut (B&H) deli getirdir. Fark = "stratejinin yüzeyde getirdiği şey". Bunu uzun vadeli bir kapı şartı yapın: net getiri > net benchmark.
Daha doğrusu: haftalık strateji getirilerini piyasa getirisine regrese et (beta ayarlı alfa) ve alfanın 0'dan anlamlı ayrışmasını (bootstrap CI) test et; sadece "net > 0" değil, "alfa > 0" (veya tek.INTERSEÇ).
Üçüncü katman: rejim stratifikasyonu — 2024 (çekişme) vs 2025 (imkânsız) gibi alt pencerelerde ayrı ayrı rapor; "%X rejimin en az K'ünde piyasaya üstün" gibi bir kural. Tek regim kazanan, piyasa etkisi olur.
Kripto için: B&H basket + funding rate maliyeti eklensin; ETF/hisse için: toplam getiri (temettü dahil) vs fiyat getirisi tutarlılığı kontrol edilsin.
Kaynak: Frazzini–Israel–Moskovitz, Trading Costs; Carino vb.
5) Farklı sınama süresi (6 ay → 3 yıl) adil kıyaslama
Mutlak "net > 0" penti eşik yerine, süreyi normalize eden bir test gerekli. En doğru araç Probabilistic Sharpe Ratio (PSR / DSR):
PSR(SR*) = Φ( (SR − SR*)·√(n−1) / √(1 − γ₃·SR + ((γ₄−1)/4)·SR²) )

Bu, SR'nın örneklem varyansını, çarpıklığını, basıklığı ve n'i otomatik hesaba katar. 6 aylık bir pencere, kendini savunmak için daha yüksek SR göstermek zorunda kalır — adalet bu.

Somut öneri: PSR(SR = 0) ≥ %90* ve ayrı olarak minimum işlem sayısı (örn. ≥ 100 işlem) ve minimum dolduk dönem çeşitliliği (en az 2 ayrı çekişme rejimi örneği) şartı.
Bir de pratik kural: t ≈ SR_yıllık × √T_yıl ≥ 1,6 tek başına da yeterli bir proxy.
Kaynak: Bailey–LdP (2012, "The Sharpe Ratio Efficient Frontier", JPM).
6) ML binlerce fikir üretince ne bozulur?
Goodhart etkisi / kapının kendisi overfit hedefi olur: üretici ML, kapı eşiklerini (PF ≥ 1,2, p10 > 0, 2× maliyet) öğrenip "kapıyı geçecek şekilde tasarlanmış" stratejiler üretir; kapı artık kalite değil, kaçak yolu tespit ediyor.
Deneme sayısı patlar: DSR'deki N_t artık binlerce–on binlerce; her geçen tarama turu, sınamanın geçtiği veriye fit edilmiş seçimi büyütür.
Leakage mümkün olur: üretici, internetten toplanmış "hayatta kalmış" stratejilerle eğitilmişse — eğitim kümesinin kendisi survivorship bias içerir.
Çözüm (tasarım):
Kronolojik üçlü bölünme: üretim/ geliştirme penceresi (örn. ≤ 2023 son), doğrulama penceresi (2024–), kilitli (data-seeless) test penceresi (2025–). Test penceresine yalnız bir kez, final karar anında ulaşın.
Deneme sayacı: her üretilen ve test edilen varyant kayda geçsin; DSR'deki N_t bunu kullanır.",
Purge/embargo + Combinatorial Purged CV (CPCV) — LdP (2018).
Protokol çerçevesini tamamen benimseyin: Arnott–Harvey–Markowitz (2019), "A Backtesting Protocol in the Era of Machine Learning", JPM — bu sorunun doğrudan cevabı.
7) Önerdiğim kapı (somut adımlar + eşikler)
Katman 0 — Veri bütünlüğü: PIT (point-in-time) veri; temettü/split tutarlılığı; kriptoda funding; delisted varlıkları içeren non-survivorship sepette test; dolgu (fill) varsayımı kötümser (stop: worst of open/tick).

Katman 1 — Sağlamlık (bugünkü gibi, + ekstremaları): nedensellik/look-ahead taraması; ±1 bar zaman kaymasında ölçüt; maliyet 1,5× ve 2×; çeyrek pencere kaydırması (±%25) — hiçbirinde işaret değişmesin (kırılganlık testi, "net > 0" yerine).

Katman 2 — İstatistiksel kapı (sırayla):

Kısa sınama elenir: < 12 ay veya < 100 işlem → elensiz değil, PSR gücü azalır zaten; ama pratik olarak < 6 ay veya < 40 işlem = oylama dışı.
PSR(0) ≥ %90 ve DSR > 0 (N_t = kayıtlı gerçek deneme sayısı) → ikisi birden.
Alfa şartı: dönem boyunca catchError net getiri − aynı obsaradeCase piyasa B&H getirisi > 0 VE β-ayarlı alfa SI 1,6> 0_codegen.
Sıfır dağılım üstünlüğü: permütasyon testinde p < 0,10.
Maliyet dayanıklılığı: 2× maliyette PSR(0) ≥ %80.
Katman 3 — Multiple-testing kontrolü: tüm aileye BHY FDR (q=0,20); final kısa listeye (≤ 30 strateji) Hansen SPA p < 0,10.

Katman 4 — Portföy kurma (elle ekranların yerine ölçülebilir kurallar):

korelasyon §0,6 budaması otomatik;
kapasite divsör dökümü: her stratejinin AUM limiti (hacim/katı katılım payı) raporu;
konsantrasyon: tek enstrüman ≤ X%.
Katman 5 — Paper kapısı (26 hafta, kişi değil kural):

Önceden yazılı karar kuralı: "net alfa'nın backtest alfaşı %70- Üstü inecek< tut); terk" maarifde süre.
canlı vs backtest kayma testi: ham 26 haftalık sonuç, backtest pencerelerinden örneklemeyle patch-bench станK(instanB asıl farklılık SOnuç dağılımının alt * in%10'd farklıxf harici misc (LdP "strateji başarak dışarı rasını beğen "continueb").
Yönetsel katman: tüm denemeler günlüğe; iki bağımsız denetçi — ama denetçinin "hata şüphesi" gibi anlık serbestten, kaçınması gereken kriter listesi önceden yazılmış olmalı; veto gerekçesi metin olarak arşivlensin.

Kaynaklar (özet): Bailey–LdP (2012 PSR; 2014 DSR); Bailey vd. (2017 PBO); White (2000); Hansen (2005); Sullivan–Timmermann–White (1999); Harvey–Liu–Zhu (2016); Aronson (2007); LdP (2018, AFML); Arnott–Harvey–Markowitz (2019); Bajgrowicz–Scaillet (2012); Benjamini–Yekutieli (2001); Frazzini–Israel–Moskowitz (2018).

En kritik üç değişiklik özet: (1) "net > 0" → PSR ≥ %90 + B&H üstü alfa + permütasyon p değeri; (2) bugünkü elle ekranları a priori yazılmış, ölçülebilir kurallara çevirin; (3) ML'ye açılmadan önce kronolojik kilitli test penceresi + deneme sayacı altyapısını kurun — bunu sonra eklemek imkânsız.