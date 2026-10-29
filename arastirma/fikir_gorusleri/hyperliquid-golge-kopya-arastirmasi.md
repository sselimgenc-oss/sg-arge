# Hyperliquid gölge kopya araştırması: fikir değerlendirmesi

## Kısa hüküm

Bu kurulum, **kopyalamanın işe yarayıp yaramadığını öğrenmek** için makul bir başlangıç. Şu aşamada en büyük tehlike daha iyi bir seçim puanı bulamamak değil; aynı kısa geçmişe bakarak çok sayıda puan, oda ve değiştirme kuralı denemek. Geçmişte en iyi görünen kuralın ileri dönemde sönmesi, finansal geriye dönük testlerde bilinen bir sorundur. [Bailey ve diğerleri, *The Probability of Backtest Overfitting*](https://escholarship.org/uc/item/4w1110bb)

Önce küçük bir mutabakat: **18 + 18 + 18 + 8 = 62**, 61 değil. Bir kişi iki grupta mı, yoksa sayı mı eski kaldı? Analizden önce bunu kayıt düzeyinde çözün; grup üyeliği hatası, ince istatistik yöntemlerinden daha büyük zarar verir.

## 1. Fikirlerin değerlendirmesi

“İstatistiksel risk”, fikrin gerçek bir etki yokken varmış gibi görünmeye ne kadar açık olduğunu anlatır. Değer puanları **bugünkü araştırma hedefiniz** içindir.

| # | Fikir | Değer | Maliyet / zorluk | İstatistiksel risk | Gerekçe |
|---|---|---|---|---|---|
| 1 | Spot odası | Düşük | Orta–yüksek | Yüksek: yeni pazar ve test | Perp seçiminin işe yarayıp yaramadığı netleşmeden farklı bir ürüne geçmek ana soruyu dağıtır. |
| 2 | Kaldıraca göre üç oda ve bütçe | Orta | Orta | Yüksek: küçük gruplar, sonradan bütçe ayarı | Risk sınırı olarak yararlı olabilir; üç odanın getirisini kıyaslamak için örnek çok küçülür. |
| 3 | Beş performans penceresi | Orta | Orta | Çok yüksek: beşli kural araması | “Hangi geçmiş öngörüyor?” iyi bir soru, fakat kazanan pencereyi aynı veride seçmek yanıltır. |
| 4 | Operasyon ve mutabakat | **Yüksek** | Orta | Düşük; veri hatası riskini azaltır | Yetim pozisyon veya hatalı kopya hesabı varsa sonuç ölçtüğünüz stratejiye ait olmaz. |
| 5 | Futbol takımı modeli | Düşük | Orta | Çok yüksek: sürekli terfi ve düşürme | İyi bir arayüz benzetmesi; birkaç haftalık getiriye göre terfi sistemi kurmak gürültüyü ödüllendirir. |
| 6 | Panoyu sadeleştirme | Orta | Düşük | Düşük | Telefonda karar için gerekli birkaç göstergenin görünmesini sağlar; araştırma gücünü doğrudan artırmaz. |
| 7 | Karantina, payı %50 azaltma | Orta | Orta | Yüksek: uyarı eşiği ve süre araması | Önceden tanımlı davranış veya veri alarmına bağlanırsa yararlı; yakın kayba bağlanırsa performans kovalamadır. |
| 8 | Tarz kayması uyarısı | **Yüksek** | Orta | Orta: eşik araması | Seçtiğiniz trader’ın artık aynı davranışı gösterip göstermediğini, getiriye bakmadan izleyebilirsiniz. |
| 9 | Günlük kayıp sonrası 24 saat durma | Düşük–orta | Düşük | Yüksek: zarar sonrası giriş çıkış zamanlaması | Zarar bir risk sınırı olabilir; otomatik bir günlük ara getiriyi iyileştirir varsayımı ayrıca sınanmalıdır. |
| 10 | Lider tablosu dışı keşif | Düşük | Yüksek | Yüksek: yeni evrenden seçme yanlılığı | Evreni büyütür, fakat önce mevcut evrende ileriye dönük seçimin değerini gösterin. |
| 11 | Aynı arşivde paralel deney | **Yüksek** | Orta | Orta; disiplinsiz kullanılırsa çok yüksek | Canlı gölge pilotu koruyarak fikirleri inceleyebilirsiniz; tüm denenen kuralları kaydetmeniz şart. |
| 12a | Calmar / düşüşe göre getiri | Orta | Düşük–orta | Yüksek: kısa dönemde düşüş ölçüsü oynak | Tek bir büyük kayıp sıralamayı değiştirebilir; şimdilik aday kuraldır. |
| 12b | Anti-martingale disiplin puanı | Orta | Orta–yüksek | Orta–yüksek: eksik işlem geçmişi | Riskli davranışı yakalayabilir; geçmiş dolumlar eksikse puan güvenilmez olur. |
| 12c | Deflated Sharpe | Orta | Orta | Düşük; **kayıtlı tüm denemeler varsa** | Çoklu deneme yanlılığını teşhis etmeye yarar; tek başına iyi trader seçmez. [Bailey ve López de Prado, *The Deflated Sharpe Ratio*](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) |
| 12d | Likidite / kopya aşınması | **Yüksek** | Orta–yüksek | Orta: maliyet varsayımı | Ekrandaki trader getirisi ile gecikmeli sanal kopyanın erişebileceği getiri arasındaki farkı doğrudan sorgular. |

## 2. İlk üç öncelik

1. **#4 Mutabakat.** Her saat “trader ne yaptı → gölge kopya ne yaptı → fark nereden geldi?” zinciri kapanmalı. Önce 61/62 uyuşmazlığını da çözün.
2. **#12d Kopya aşınması.** Gecikme, makas, işlem büyüklüğü ve kaçırılan işlemler için iyimser/orta/kötümser maliyet senaryosu çıkarın. Kârlılık yalnız iyimser senaryoda varsa seçim modelini geliştirmeye henüz değmez.
3. **#11 Paralel deney, sıkı kayıtla.** Kuralın yazıldığı tarih, kullanılan geçmiş, tüm adaylar ve sonraki dönem sonucu saklansın. İlk oda ile kontrol **sabit referans** kalsın; değiştirdiğiniz oda ayrı bir “karar politikası” olarak ölçülsün.

**Birbirini tamamlayanlar:** #4 ve #12d ölçümün güvenilirliğini kurar; #11 bunun üstünde #3, #8 ve #12a–c’yi sınar. #8, önceden belirlenmiş eşiklerle #7’ye gerekçe sağlayabilir.

**Çakışanlar:** #2, #5 ve #7 aynı trader’ın payını farklı gerekçelerle değiştirebilir; birlikte açılırsa hangi kararın sonuç verdiği anlaşılmaz. #3, #10 ve #12a–c aynı dönemde geniş bir seçim yarışına dönüşür. Spot odası da ayrı bir araştırma sorusudur.

## 3. “Kâra bakarak değiştirme” tuzağı

En açık risk **#5, #7 ve #9**. **#2, #3, #12a ve #12c** de odaları veya eşikleri son sonuçlara göre ayarlarsanız aynı tuzağa girer. #8’de bile “tarz kayması” eşiğini zarar edenleri yakalayacak biçimde sonradan seçebilirsiniz.

Bunu üç kayıtla önleyin:

- **Değişim nedeni:** Veri/operasyon hatası, önceden belirlenmiş risk ihlali, önceden belirlenmiş davranış değişimi veya araştırmacı takdiri. Sonuncusunu saklamayın; ayrı işaretleyin.
- **Karar anındaki bilgi:** Kullanılan verinin zaman damgasını ve o anda bilinen eşikleri dondurun. Sonradan öğrenilen bilgiyle eski kararı yeniden yazmayın.
- **İki ayrı sonuç:** İlk sabit oda − ilk sabit kontrol, başlangıç seçiminin sınamasıdır. Değişen oda − **aynı tarihlerde izlenen uygun kontrol**, sizin karar politikanızın sınamasıdır. İkisini tek başarı hikâyesine toplamayın.

## 4. Listede eksik olan üç önemli fikir

1. **Veri kapsamı ve eksiklik panosu.** Her hesap için erişilebilen en eski dolum, eksik saat, kopan arşiv kaydı ve yeniden kurulamayan pozisyon oranını gösterin; eksik geçmişi “işlem yapmadı” saymayın. Hyperliquid, API’de yalnız son **10.000 dolumun** erişilebilir olduğunu ve zaman aralıklı sorguda yanıt başına ayrıca sınır bulunduğunu belgeliyor. [Hyperliquid bilgi uç noktası](https://hyperliquid.gitbook.io/Hyperliquid-docs/for-developers/api/info-endpoint)
2. **Olay anında dondurulmuş evren.** Adayın hangi tarihte, hangi bilgiyle seçilebilir olduğunu arşivleyin; bugün görünen lider tablosunu geçmiş tarihe uygulamayın. Bu, sonradan başarılı görünenleri geçmişe taşıma yanlılığını azaltır. Bu riskin sizin arşivinizdeki büyüklüğü **doğrulanamadı**.
3. **Önceden ilan edilmiş ekonomik karar eşiği.** “İstatistiksel olarak sıfırdan büyük mü?” yerine “maliyet sonrası haftalık fark, uğraşa değecek kadar büyük mü?” sorusunu yazın. Örneğin haftalık **%0,25** net farkı iş eşiği seçin; bu sayı bilimsel sabit değil, sizin karar varsayımınız olsun.

## 5. Küçük örnekle dürüst karar

**Analiz birimi trader sayısı veya saat sayısı değil, aynı takvim haftasındaki oda − kontrol farkı olsun.** Trader’lar aynı piyasa şoklarını yaşar; saatler de bağımsız tekrar değildir. 12 haftalık gözlemde 7 günlük blok bootstrap yaklaşık 12 zaman bloğuna dayanır; aralığı kesin kanıt gibi okumayın. Blok örnekleme zaman bağımlılığını ele almak için geliştirilmiştir, fakat kısa örneği büyütmez. [Politis ve Romano, *The Stationary Bootstrap*](https://doi.org/10.1080/01621459.1994.10476870)

Somut bir Bayesçi rapor önerim:

- Her hafta, maliyet ve BTC etkisi çıkarılmış **eşzamanlı oda − kontrol farkını** hesaplayın. Tek ana ölçüt bu olsun.
- Gerçek ortalama haftalık fark için başlangıç dağılımını **ortalama 0, standart sapma %1** alın. Bu, “önceden büyük bir üstünlük beklemiyorum” varsayımıdır; %0,5 ve %2 ile duyarlılık raporu da verin.
- Her ay iki olasılığı gösterin: **üstünlük olasılığı** `P(fark > 0)` ve **işe değer üstünlük olasılığı** `P(fark > %0,25/hafta)`. Yanına tahmini fark aralığını, en kötü haftayı ve maliyet senaryolarını koyun. “Bayesçi” burada varsayımı açıkça yazıp yeni veriyle bu olasılıkları güncellemek demektir.
- **Devam kararı** için baştan örnek kural: `P(fark > %0,25) > %90` ve sonuç kötümser maliyet senaryosunda da pozitifse “umut verici”; `P(fark < −%0,25) > %90` ise “zarar lehine kanıt”; arası **belirsiz**. Bu eşikler keşif için karar kuralıdır, keşfin doğru olma garantisi değildir.
- Pencere, puan ve oda değişiklikleri arttıkça aynı olasılığı “resmî başarı kanıtı” diye sunmayın. Sabit ilk kolu esas rapor, uyarlanan kolu ayrı ürün deneyi olarak tutun. Bayesçi yöntem de seçilmiş sonuçları ve hatalı varsayımları kendiliğinden düzeltmez; durdurma davranışının geçerliliği modele ve başlangıç varsayımına bağlıdır. [Hendriksen ve diğerleri, Bayes faktörleri ve isteğe bağlı durdurma](https://ir.cwi.nl/pub/31055)

Yürüyen 60 günlük pencereler 14 günde bir kaydığı için büyük ölçüde **aynı günleri paylaşır**. “Pencerelerin yarısından fazlası başarısız” kuralını bağımsız oylama veya güçlü istatistiksel kanıt gibi kullanmayın; operasyonel alarm olarak kullanın. Mevcut güç simülasyonunuz doğruysa, birkaç ay sonunda en dürüst ve muhtemel sonuç **“anlamlı üstünlük henüz gösterilemedi; şu büyüklükte üstünlük hâlâ mümkün”** olacaktır. Bu, başarısız bir araştırma sonucu değildir; yanlış kesinlikten daha değerlidir.
