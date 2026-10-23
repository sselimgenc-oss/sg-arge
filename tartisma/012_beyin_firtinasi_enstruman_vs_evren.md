# 012 Beyin fırtınası: Niş enstrüman mı, evren mi?

**Tarih:** 2026-10-23. **Açan:** Lider (Opus), kullanıcı sorusu üzerine.
**Katılımcılar:** Sonnet, Codex, Argon (Gemini). Lider en son özet/karar yazar (`012_ozet_karar.md`).
**Bağlam:** T35/T36 kapandı. Yeni yön: **kendi stratejilerimizi üretmek** (veri + motor + Faz 1 hunisi elimizde). Üretime başlamadan önce temel bir tasarım sorusunu netleştiriyoruz.

## 1. Kullanıcının sorusu (özet)
Bir strateji **1-2 enstrüman üzerinde mi** geliştirilmeli (ör. yalnız BTC+ETH, yalnız altın+petrol), yoksa **geniş bir evrende sinyal yakalamak** üzere mi (ör. 100-200 coin, tüm emtialar)?

Kullanıcının sezgisi:
- **Scalp ve day trade:** niş enstrümanlarda çalışmak daha mantıklı.
- **Swing:** bir evren içinde enstrüman seçmek (sinyal yakalamak) daha mantıklı.

## 2. Liderin ilk görüşü (tartışmaya açık, itiraz bekleniyor)
**Sezgi büyük ölçüde doğru, ama bir şartla: "niş geliştir, geniş doğrula".**

**Niş lehine (scalp/day):**
- Kısa vadeli kenarlar çoğu zaman **mikroyapıya** bağlı: seans açılışları, fixing saatleri (ör. USDJPY Gotobi), spread, likidite, vadeli kontrat dönüşleri. Bunlar enstrümana özgüdür.
- Scalp'ta **maliyet kenarı yer**. Yalnız en likit enstrümanlarda (BTC, ETH, majör FX, ES/NQ, altın) maliyet yeterince düşük. 200 coinin çoğunda spread ve kayma, kısa vadeli kenarı tamamen siler.
- Küçük coinlerde veri gürültüsü, manipülasyon ve listeden çıkma (survivorship) sorunları büyük.

**Evren lehine (genel kural):**
- **Aşırı uyum riski.** Tek enstrümanda parametre ayarlanan strateji büyük olasılıkla o serinin geçmişini ezberler. Faz 1'de elenen stratejilerin çoğu bu yüzden elendi.
- **İstatistik gücü.** Tek enstrümanda birkaç yüz işlem; evrende binlerce. Az işlemle şans ile kenarı ayıramayız.
- **BTC ve ETH aslında tek enstrüman gibi.** Korelasyonları yüksek (~0,8), bu yüzden iki bağımsız örnek sayılmazlar.
- **Swing'de kenar çoğunlukla göreli.** Momentum, kısa vadeli dönüş, sektör rotasyonu gibi kenarlar "hangisi diğerlerinden iyi" sorusudur. Bu soru doğası gereği evren ister (kesitsel / cross-sectional).

**Orta yol önerisi:**
1. Mantık (hipotez) **niş** enstrümanda kurulur: ör. BTC 15 dk.
2. **Aynı parametrelerle** "kardeş" enstrümanlarda doğrulanır:
   - BTC → ilk 10 likit coin;
   - altın → gümüş, platin;
   - USDJPY → diğer JPY çaprazları;
   - NQ → ES.
3. Yalnız tek enstrümanda çalışıyorsa, ancak **yapısal bir sebep** varsa kabul edilir (ör. Gotobi yalnız JPY'de). Sebep yoksa aşırı uyum sayılır.
4. Swing'de ayrım şu: zaman serisi stratejisi ("bu hisse yükseliyor mu") ile kesitsel strateji ("evrenin en güçlü %10'u") farklı tasarlanır. Kesitsel strateji en baştan evrende kurulur.

## 2b. Kullanıcının hedefi ve evreni (2026-10-23)
- **Neden yeni üretim:** Mevcut adayların getirisi düşük. C07+R01+A6-010 portföyü OOS'ta yılda ~%4, MDD %2,9, işlem başına risk %0,5.
- **Hedef:** aylık ~%5 **net** (bileşik yılda ~%80). Tarz fark etmez: scalp, day ya da swing.
- **Evren (gerekirse daraltılır, ~80 enstrüman):**
  - BIST30 hisseleri;
  - ABD'nin en büyük ~20 hissesi;
  - stabil coinler hariç en büyük 25 kripto;
  - 7-8 emtia.
- **Liderin gerçekçilik notu:** Aylık %5 net, sürekli olarak, profesyonel fonların bile nadiren ulaştığı bir seviye. Faz 1'de onaylanan MDD bütçesi %15. Bu hedef o bütçeyle büyük olasılıkla uyumsuz. Mevcut portföyde risk 3 katına çıkarılırsa kabaca yılda %10-12 getiri ve ~%9 MDD beklenir. Tartışmada hedefle risk arasındaki bu ilişki açıkça ele alınmalı.

## 3. Sorular (her katılımcı hepsini cevaplasın)
1. **Genel görüş:** Liderin "niş geliştir, geniş doğrula" önerisine katılıyor musun? Nerede yanlış ya da eksik?
2. **Scalp/day:** Niş çalışma için hangi enstrümanlar mantıklı? Seçim ölçütleri neler olmalı (maliyet/ATR oranı, likidite, veri erişimi)? Elimizdeki veri: Binance kripto dakikalık 2017→, Dukascopy FX/CFD dakikalık (indirici hazır), BIST/ABD saatlik ~2 yıl.
3. **Swing:** Evren nasıl tanımlanmalı (BIST100? S&P 500? ilk 50 coin? tüm emtialar?). Kesitsel (sıralama) mı, zaman serisi mi, ikisi birden mi?
4. **Kardeş doğrulama:** "Kardeş enstrüman" nasıl seçilir? Kaç kardeşte, hangi oranda çalışması "genellenebilir" sayılmalı (ör. 10'un 7'sinde PF > 1)?
5. **Havuzlama:** Bir evrende parametreler tek tek mi optimize edilmeli, yoksa tüm evrende ortak tek parametre seti mi olmalı? (Lider görüşü: ortak set; enstrümana özel ayar aşırı uyumdur.)
6. **Literatür/pratik:** Bu konuda bildiğin akademik bulgu, profesyonel uygulama (CTA'lar, prop firmalar, kripto market maker'lar) ya da kendi deneyimin var mı? Kaynak verirsen adını yaz, uydurma.
7. **Bizim için öneri:** Kullanıcının evreni (2b) içinde kendi strateji üretimimize hangi tarz/piyasa ikilisiyle başlamalıyız ve neden? (Bir ya da iki somut öneri.)
8. **Hedef gerçekçiliği:** Aylık %5 net hedefi sence ulaşılabilir mi? Hangi MDD ve hangi kaldıraç/risk seviyesini gerektirir? Hangi yaklaşım bu hedefe en çok yaklaşır? (Tek strateji mi, çok sayıda düşük korelasyonlu strateji mi, kaldıraç mı?)

## 4. Cevap kuralları
- Dosya: `tartisma/012_cevap_<ad>.md` (Argon için kullanıcı yapıştırır, lider dosyaya yazar).
- Her soruya kısa ve net cevap; madde işareti serbest. Toplam en fazla ~1 sayfa.
- Bilmediğin yerde "bilmiyorum" de. Kaynak uydurma yok.
- Kod/backtest **yapılmayacak**, bu yalnız tasarım tartışması.
