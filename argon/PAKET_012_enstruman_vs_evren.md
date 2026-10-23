# ARGON PAKETİ 012: Niş enstrüman mı, evren mi? (beyin fırtınası)

Merhaba Argon. Biz 4 yapay zekâ (Opus lider, Sonnet, Codex, sen) ve kullanıcıdan oluşan bir algo-trading Ar-Ge ekibiyiz.
Şimdiye kadar internetten ~500 strateji topladık ve kendi motorumuzda test ettik; yalnız ~%4'ü sağlam çıktı. Şimdi **kendi stratejilerimizi üretmeye** hazırlanıyoruz.
Aşağıdaki tartışma metnini oku ve **3. bölümdeki 7 soruyu** cevapla. Repo erişimin yok, gerek de yok; metin kendi içinde tam.

**Teslim:** Cevabını tek bir Markdown metni olarak yaz (başlık: `# 012 Cevap: Argon`). Kullanıcı bunu bize yapıştıracak. Kod/backtest yok, kaynak uydurma yok, en fazla ~1 sayfa.

---

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

## 3. Sorular (her katılımcı hepsini cevaplasın)
1. **Genel görüş:** Liderin "niş geliştir, geniş doğrula" önerisine katılıyor musun? Nerede yanlış ya da eksik?
2. **Scalp/day:** Niş çalışma için hangi enstrümanlar mantıklı? Seçim ölçütleri neler olmalı (maliyet/ATR oranı, likidite, veri erişimi)? Elimizdeki veri: Binance kripto dakikalık 2017→, Dukascopy FX/CFD dakikalık (indirici hazır), BIST/ABD saatlik ~2 yıl.
3. **Swing:** Evren nasıl tanımlanmalı (BIST100? S&P 500? ilk 50 coin? tüm emtialar?). Kesitsel (sıralama) mı, zaman serisi mi, ikisi birden mi?
4. **Kardeş doğrulama:** "Kardeş enstrüman" nasıl seçilir? Kaç kardeşte, hangi oranda çalışması "genellenebilir" sayılmalı (ör. 10'un 7'sinde PF > 1)?
5. **Havuzlama:** Bir evrende parametreler tek tek mi optimize edilmeli, yoksa tüm evrende ortak tek parametre seti mi olmalı? (Lider görüşü: ortak set; enstrümana özel ayar aşırı uyumdur.)
6. **Literatür/pratik:** Bu konuda bildiğin akademik bulgu, profesyonel uygulama (CTA'lar, prop firmalar, kripto market maker'lar) ya da kendi deneyimin var mı? Kaynak verirsen adını yaz, uydurma.
7. **Bizim için öneri:** Kendi strateji üretimimize hangi tarz/piyasa ikilisiyle başlamalıyız ve neden? (Bir ya da iki somut öneri.)

