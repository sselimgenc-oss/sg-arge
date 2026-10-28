# Argon A8–A9: rejim sınıflandırıcısı ve kalıcılık (2026-10-28)

## Lider denetim notu
- **Kod kabul edildi** → `copytrade/rejim.py`, `copytrade/kalicilik.py` (+ testler). Lider bağımsız denetimi:
  - Rejim etiketleri elle döngüyle yazılmış referansla 400 günlük rastgele yürüyüşte **birebir** (0 fark); geleceğe bakma testi
    (her günü yalnız o güne kadarki veriyle yeniden hesapla) **0 fark**.
  - Spearman, numpy sıra korelasyonuyla fark 0 (eşitlikli veri).
  - Blok bootstrap: AR(1) ρ=0,5, n=40, blok=4 seride %95 aralığın kapsaması **~%83** (yüzdelik MBB küçük örneklemde iyimser).
    Faz 3 raporunda aralık "iyimser" diye etiketlenir; karar ölçütü değildir.
  - Lider eki: boşluklu (eksik günlü) seri artık hata verir (pencereler satırla kaydığı için); test eklendi.
- **Araştırma zayıf:** dışa aktarılan tablolar hücrelerde kesik; **bağlantı ve erişim tarihi yok**. Çalışma adları tanınır
  (Carhart 1997 JF; Barber–Lee–Liu–Odean 2014 J. Financial Markets; Pelster–Hofmann 2018 JBF; Oehler–Horn–Wendt 2016),
  ama lider açıp doğrulamadı; **Kawai vd. 2024 (TraderWagon/Bybit) doğrulanamadı.** Hiçbiri karar gerekçesi olarak kullanılmaz.
- **Eşik önerileri** (pencere 30 g, getiri ±%10, şok yüzdeliği 0,90, yüzdelik penceresi 180 g) kaynaksız gerekçedir;
  `kurallar.yaml`'a taşınması **kullanıcı kararı** (bilgi amaçlı rejim kırılımı için; kapıyı etkilemez).
- Örnek dağılım (rastgele yürüyüş, günlük σ %3, önerilen eşikler): yatay 84, şok 41, düşüş 40, yükseliş 26 gün / 191.

## A8 araştırma (Argon, ham)
```
Parametre Önerilen Değer Gerekçe
pencere_gun 30 gün 7/24 işlem gören kripto piyasasında 30 gün, haftalık mikro yapı gürültüsünü süzerken aylık makro trend dönüşlerini gecikmeden yakalamak için standart takvim aralığıdır.
getiri_esik 0.10 (%10) Bitcoin'in tarihsel yıllıklandırılmış oynaklığı (%50–%70 bandı) göz önüne alındığında, 30 günlük süreçte ±%10 aralığında kalan fiyat hareketleri yönlü bir trendden ziyade yatay bant hareketini (konsolidasyon) temsil eder. ±%10 aşımı net bir yönlü ivmeyi gösterir.
sok_yuzdelik 0.90 (%90) Dağılımın en üst %10'luk dilimine denk gelen oynaklık patlamaları, normal trend içi dalgalanmalardan ziyade kaldıraç tasfiyeleri (long/short squeeze), ani borsa/düzenleyici şokları veya flaş çöküşleri yakalar; yönlü sinyallerin önüne geçmesi risk ayrıştırması açısından kritiktir.
yuzdelik_pencere_gun
180 gün 6 aylık geriye dönük pencere, kriptodaki döngüsel dinamiklere (yarılanma, faiz kararları, ETF akımları) uyum sağlarken çok eski ve güncelliğini yitirmiş rejimlerin mevcut eşiği bozmasını engeller.

```

## A9 araştırma (Argon, ham; tablo dışa aktarımında kesik)
```
Çalışma Kategori / Platform Örneklem Dönem Bulunan Etki Büyüklüğü & Temel Sonuç
Bağlantı
Carhart (1997) Yatırım Fonları (Mutual Funds) 1.892 adet hisse senedi fonu (hayatta kalma yanlılığı içermeyen CRSP verisi) 1962–1993 (32 yıl)
1 yıllık ham getirilerde en üst ve en alt desil arasında yıllık ~%8 getiri fark
Carhart (1997) JF
Barber, Lee, Liu & Odean (2014) Bireysel Gün İçi Trader'lar (Day Traders) Tayvan Menkul Kıymetler Borsası'ndaki (TWSE) tüm bireysel trader popülasyonu (~450.000 kişi) 1992–2006 (15 yıl)
y yılında en başarılı ilk 500 trader, takip eden y+1 yılında işlem maliyeti ö
Barber et al. (2014) JFM
Oehler, Horn & Wendt (2016) Sosyal Trading / Sertifikalar (Wikifolio) Wikifolio üzerinde ihraç edilmiş 1.084 adet sertifika 2012–2013 Sosyal portföyler ortalamada piyasayı yenemez (sıfır/negatif alfa). En iyi
Oehler et al. (2016) IRFA
Pelster & Hofmann (2018) Sosyal Trading / FX & CFD (eToro) eToro platformunda işlem yapan 354.817 trader 2012–2015 Takipçi sayısı ve görünürlük arttıkça lider trader'larda itibar kaybı korkusu
Pelster & Hofmann (2018) JBF
Kawai, Soska, Routledge, Zetlin-Jones & Christin (2024) Kripto Türev Kopya İşlemleri (TraderWagon & Bybit) 3–8 milyon USD AUM büyüklüğüne ve yüzlerce aktif lider portföyüne sahip TraderWagon ve Bybit ekosistemi Ekim 2022 – Ağustos 2023
Liderlik tablosundaki geçmiş ROI sıralaması ile liderlerin gelecekteki geti
Kawai et al. (2024) ACM CHI

```
