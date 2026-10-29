# Hyperliquid Trader Kopyalama — Fikir Değerlendirmesi

*Tarih: 29 Ekim 2026 · Kapsam: gölge (sanal) kopya pilotu v1.3*

## Özet

Asıl sorununuz fikir eksikliği değil, **istatistiksel gücün** (gerçek bir fark varsa onu yakalama olasılığı) düşük olması. Listedeki fikirlerin çoğu yeni kollar, yeni eşikler ve yeni pencereler ekliyor. Bunlar gücü artırmıyor, yalnızca çoklu test riskini büyütüyor. Değerli olanlar ölçümü temizleyen ya da örneklemi büyüten fikirler.

---

## 1. Fikir değerlendirmesi

| # | Fikir | Değer | Maliyet | İstatistiksel risk | Gerekçe |
|---|---|---|---|---|---|
| 1 | Spot odası | Düşük | Orta | Orta (yeni kol) | Zaten küçük olan örneklemi böler. Hyperliquid spot piyasası sığ, oradaki trader kitlesi de farklı. Asıl soruya katkısı yok. |
| 2 | Atak/dengeli/temkinli odalar | Düşük, hatta zararlı | Orta | Yüksek | 10x üstü kaldıraç kendi kapınızla çelişiyor. 18 kişiyi üçe bölünce her oda gürültü olur. Ayrıca tasfiye olanlar tablodan düştüğü için yüksek kaldıraçta **hayatta kalan yanlılığı** (yalnız batmayanları görmek) en güçlü haliyle çalışır. |
| 3 | Performans pencereleri | **Yüksek** (doğru kurulursa) | Orta | Yüksek (5 pencere = 5 test) | Projenin çekirdek sorusu bu: "Geçmiş geleceği söylüyor mu?" Ama bunu 18 kişilik odada değil, binlerce hesap üzerinde çalışan bir sıralama testi olarak kurmak gerekir (aşağıda yeni fikir A). |
| 4 | Operasyon/mutabakat | **Yüksek** | Düşük–orta | Yok | Gölge kopya yanlışsa diğer her sonuç da yanlış olur. Gün içi aktif trader'larda 10.000 dolum sınırı veri kaybına yol açabilir. |
| 5 | Futbol takımı modeli | Orta | Orta | **Yüksek** | Terfi ve küme düşme kuralları elle uygulanırsa bu düpedüz "kâra bakarak değiştirme" olur. Mekanik, önceden yazılmış ve kendi kolunda ölçülen bir kural olursa kabul edilebilir. |
| 6 | Pano sadeleştirme | Yüksek (sizin için) | Düşük | Yok | Telefondan bakan, teknik olmayan biri için kalabalık pano yanlış tepki vermeye iter. En ucuz kazanç bu. |
| 7 | Karantina (%50 pay, 2–4 hafta) | Orta | Düşük | Orta | Tetiği trader'ın davranışıysa iyi bir fikir. Tetiği kârı/zararıysa getiri kovalamaya döner. Ayrıca 9 numarayla çakışıyor. |
| 8 | Tarz kayması tespiti | **Yüksek** | Orta | Düşük | Kârdan bağımsız, davranışa dayalı bir sinyal. Hesabın el değiştirmesini ya da stratejinin değişmesini yakalar. Trader değiştirmenin en meşru gerekçesi bu tür bir sinyaldir. |
| 9 | Günlük kayıp soğuması | Düşük | Düşük | Orta (yeni parametre) | Zaten 30 dk–2 sa geridesiniz. Kayıptan sonra durmak çoğu zaman toparlanmayı kaçırmak demek. Ancak paralel deneyde (11) ucuzca test edilebilir. |
| 10 | Lider tablosu dışı keşif | Düşük (şimdilik) | Yüksek | Yüksek | 48 bin hesap fazlasıyla yeterli. Evreni büyütmek, en iyileri arayan testlerin sayısını artırır. |
| 11 | Paralel deney | **Yüksek** | Orta | **Çok yüksek** | Altyapı olarak çok değerli. Ancak denenen her varyant kayda geçmeli ve 12c ile düzeltilmeli. Aksi halde 50 kural denenir, en iyisi seçilir ve kendinizi kandırırsınız. |
| 12a | Calmar oranı (getiri ÷ en büyük düşüş) | Orta | Düşük | Orta | Birkaç aylık veride en büyük düşüş tek bir olaydan ibaret, bu yüzden gürültülü bir ölçü. |
| 12b | Anti-martingale disiplin skoru | **Yüksek** | Orta | Düşük–orta | Davranışa dayalı ve mantıklı bir hikâyesi var: zarardaki pozisyonu büyüten trader eninde sonunda batar. Kâr kovalamaz. |
| 12c | Deflated Sharpe (çok sayıda denemenin şans etkisini düzelten Sharpe) | **Yüksek** (hijyen olarak) | Düşük | Riski azaltır | 48 binden seçim yapınca en iyi görünenin önemli kısmı şanstır. Bu yöntem o şans payını hesaptan düşer. |
| 12d | Kapasite / kopya aşınması | Orta | Orta | Düşük | Gerçek para olmadığı için şimdilik ikincil. Yine de 30 dk gecikmenin kime ne kadar mal olduğu zaten ölçülüyor, o ölçüm burada yeniden kullanılabilir. |

---

## 2. İlk 3 öncelik

1. **Mutabakat (4).** Yetim pozisyonları (trader'ın kapattığı ama kopyada açık kalan pozisyonlar) ve kaçırılan dolumları her gün sayın. Kopyanın hesap değeri trader'ınkiyle ne kadar uyuşuyor, bunu da raporlayın. Sağlam veri olmadan yapılan hiçbir istatistik anlam taşımaz.
2. **Fikir 3'ü yeniden çerçevelemek: kesitsel kalıcılık testi** (ayrıntısı aşağıda, yeni fikir A). Gücü artırabilecek tek yol bu.
3. **Davranış skorları: 12b + 8, hijyen olarak 12c.** Bunlar size kârdan bağımsız bir seçim ve değiştirme gerekçesi verir.

Hızlı kazanç olarak 6'yı (pano) da hemen yapın. Bir öğleden sonralık iş.

**Birbirini tamamlayanlar:**

- 11 + 12c + 3: Paralel deneyde ne denerseniz deneyin, deneme sayısı Deflated Sharpe'a girer.
- 8 → 7: Tarz kayması tespit edilince otomatik karantina devreye girer. Böylece karantinanın tetiği davranış olur.
- 12b + 8: İkisi de aynı davranış verisinden üretilir.

**Çakışanlar:**

- 2, kendi kaldıraç kapınızla çelişiyor.
- 1 ve 2, zaten küçük olan örneklemi bölüyor.
- 7 ile 9 aynı işi yapıyor (risk azaltma). Birini seçin.
- 10, 12c'nin amacına ters düşüyor.
- 5, sabit referans kolunu anlamsızlaştırabilir. Oda sürekli değişirse "ilk oda" kıyası zayıflar.

---

## 3. "Kâra bakarak değiştirme" tuzağı

**Tuzağa düşürenler:** 5 (elle uygulanırsa), 7 ve 9 (kâr/zarar tetikliyse), 2, ve 3 (oda üyelerini pencereye göre değiştirmek için kullanılırsa). Ayrıca 12 hafta kuralını kaldırmak da bu kapıyı açtı.

**Önleme yolları:**

- **Gerekçe kodu listesi.** Trader yalnızca kâr dışı bir gerekçeyle çıkarılabilsin: kaldıraç ihlali, tarz kayması, hareketsizlik, veri sorunu, anti-martingale davranışı. "Kötü gitti" geçerli bir kod olmasın.
- **Değişim tavanı.** Örneğin 4 haftada en fazla 2 değişiklik. Değişim hızı ne kadar yüksekse, karar o kadar çok gürültüye dayanmış olur.
- **Karşı-olgu defteri.** Her değişiklikte çıkan ve giren trader'ı ayrı ayrı 4–8 hafta izlemeye devam edin. Sonra "değişim alfası"nı ölçün: giren eksi çıkan. Birkaç değişiklik sonra kararlarınızın değer katıp katmadığını sayıyla görürsünüz.
- **Mekanik ikiz.** Kuralı bilgisayara da uygulatın ve sizin elle yönettiğiniz odayla yan yana izleyin. Böylece kuralın kendisini ve sizin yorumunuzu ayrı ayrı ölçersiniz.

---

## 4. Listede olmayan en önemli 3 fikir

### A. Ölçüm birimini değiştirmek: odadan sıralamaya

Şu an testinizin örneklemi aslında 18 kişi değil, **12 haftalık tek bir zaman serisi**. Oda içindeki trader'lar birbiriyle ve BTC ile yüksek korelasyonlu, bu yüzden bağımsız gözlem sayısı haftaların sayısı kadar. Gücün düşük çıkmasının sebebi bu.

Önerim: Her hafta lider tablosundaki, örneğin, 500–2.000 hesabı skorlarına göre sıralayın. Ardından bu sıralamanın sonraki haftanın getirisiyle korelasyonunu ölçün. Buna **rank IC** denir (skor sıralaması ile sonraki getiri sıralaması arasındaki Spearman korelasyonu). Her hafta binlerce trader'ın ortalamasını aldığınız için gürültü ciddi biçimde düşer.

Getiriyi hesap değeri geçmişinden alabilirsiniz, ancak para yatırma/çekme düzeltmesi şart. Bunun için `userNonFundingLedgerUpdates` uç noktası var. Kopya simülasyonu gerekmediği için 10.000 dolum sınırına da takılmazsınız. Fikir 3'ün beş penceresi bu yapıda beş skor olarak test edilir.

### B. Yanlılık denetimi

- **Hayatta kalan yanlılığı:** Tasfiye olup tablodan düşen hesaplar görünmüyor.
- **Para hareketleri:** Yatırma/çekme düzeltilmezse getiri sahte görünür.
- **Dolum sınırı:** 10.000 dolum sınırı nedeniyle aktif trader'ların geçmişi kesik.
- **Etkin örneklem:** Trader'lar arası korelasyon yüzünden gerçek bağımsız gözlem sayısı göründüğünden az.

Bunlar mevcut sonuçları sistematik olarak iyimser gösterir. Her biri için tek satırlık bir ölçüm koyun, örneğin "kesik geçmişli trader oranı: %X".

### C. Basit strateji kıyası (faktör ayrıştırması)

Odanın getirisini yalnız BTC betasına karşı değil, şu basit stratejilere karşı da regresyona sokun: ETH/alt sepeti, BTC trend takibi (momentum) ve funding taşıma. **Funding taşıma**, funding ödemesini alan tarafta durmaktan kazanç sağlamak demek. Oda bunlardan birine yüksek yükleniyorsa kopyalama yerine o basit kuralı uygulamak yeterli olur. "Trader seçmek mümkün mü?" sorusunun dürüst cevabı da bu testten geçer.

---

## 5. Az örnekle dürüst karar

Önce beklentiyi gerçekçi tutmak gerekiyor. Bu güçle elde edebileceğiniz en iyi sonuç büyük olasılıkla "büyük bir fark yok" demek olacak. "Fark var" demek zor. Önceden şunu kararlaştırın: "Yılda %40'tan büyük bir farkı dışlayabilirsem bu da faydalı bir cevaptır."

Ayrıca yürüyen pencereli provada pencereler birbiriyle yaklaşık 4 kat örtüşüyor (60 gün ileri, 14 gün adım). Bu yüzden "pencerelerin yarısından fazlası" bağımsız kanıt sayılmaz. Örtüşmeyen pencereleri ayrıca raporlayın.

### Bayesçi öneri (somut)

1. Haftalık farkı hesaplayın: d = oda − kontrol, BTC betası düzeltilmiş. Ortalaması d̄, standart hatası se olsun. se'yi blok bootstrap ile bulun.
2. Şüpheci bir ön inanç (prior) koyun: yıllık fark ~ Normal(0, %30). Haftalığa çevirmek için ortalamayı ve standart sapmayı uygun biçimde ölçekleyin.
3. Sonsal (posterior) inanç şöyle güncellenir:
   - sonsal ortalama = (d̄/se²) / (1/se² + 1/σ₀²)
   - sonsal varyans = 1 / (1/se² + 1/σ₀²)

   Burada σ₀, ön inancın standart sapmasıdır.
4. Her hafta panoda tek sayı gösterin: **P(yıllık fark > %20)**.
5. Önceden yazılmış karar kuralları:
   - **Durdur (umut yok):** P(fark > %20) < %10.
   - **Başarı adayı:** P(fark > 0) > %95 ve P(fark > %20) > %70.
   - **Üst sınır:** 26 hafta. Bu noktada hâlâ belirsizse "kanıt yok" denir.
   - %20 eşiği **ROPE** görevini görüyor (pratikte sıfır sayılan aralık: bunun altındaki fark işe yaramaz kabul edilir).
6. Trader düzeyinde de **hiyerarşik büzülme** (shrinkage) kullanın. Bu yöntem her trader'ın alfasını grup ortalamasına doğru çeker, böylece 3 iyi hafta geçiren biri "yıldız" görünmez. Oda içi sıralama kararlarını ham getiriye göre değil, bu büzülmüş alfaya göre verin.

### Sıralı test alternatifi (istediğiniz kadar bakabilirsiniz)

Klasik testlerde sonuca her bakış yanlış alarm olasılığını artırır. **Her an geçerli** (anytime-valid) testlerde ise her hafta bakmak testi bozmaz. Basit bir sürümü bahis martingalesidir:

1. Haftalık farkı sınırlayın, örneğin ±%5'te kırpın: c = 0,05.
2. Her hafta "servet" değerini güncelleyin: E ← E × (1 + λ·d/c). λ, 0,2 gibi küçük ve sabit bir sayı olsun.
3. E ≥ 20 olursa %5 düzeyinde "fark var" deyin. Bu, Ville eşitsizliği sayesinde sürekli izleme altında da geçerlidir.

E 1'in altında kalıp eriyorsa, kanıt sıfır farkı destekliyor demektir.

---

## 6. Kaynaklar

Bu bağlantılar bellekten verildi, tek tek açılıp doğrulanmadı. Hepsi bilinen yayınlar, yine de kullanmadan önce açıp kontrol edin.

- Deflated Sharpe, Bailey & López de Prado: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
- Geriye dönük testte aşırı uyum olasılığı (PBO): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
- Finansta çoklu test sorunu, Harvey, Liu & Zhu: https://www.nber.org/papers/w20592
- Kopya ticaretin davranışa etkisi, Apesteguia ve ark. (Management Science): https://doi.org/10.1287/mnsc.2019.3508
- Fon performansının kalıcılığı, Carhart 1997: https://doi.org/10.1111/j.1540-6261.1997.tb03808.x
- Zarardaki pozisyonu tutma eğilimi (disposition effect), Odean 1998: https://doi.org/10.1111/0022-1082.00072
- Her an geçerli çıkarım (anytime-valid inference), Ramdas ve ark.: https://arxiv.org/abs/2210.01948
- Bahis tabanlı güven aralıkları, Waudby-Smith & Ramdas: https://arxiv.org/abs/2010.09686
- Zamandan bağımsız güven dizileri, Howard ve ark.: https://arxiv.org/abs/1810.08240
- ROPE yaklaşımı, Kruschke 2018: https://doi.org/10.1177/2515245918771304
- Hyperliquid info API: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
  - 10.000 dolum sınırı kullanıcı tarafından belirtildi. Bu sayfada yazdığı hatırlanıyor ama **doğrulanamadı**.
