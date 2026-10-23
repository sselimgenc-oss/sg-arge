# 011: T35 parti 2 değerlendirmesi (lider)

Teslimler geldikçe güncellenir. Parti 1: `tartisma/010_t35_ilk_parti_degerlendirme.md`.

## ChatGPT kolu (Avrupa + Amerika): `arastirma/chatgpt_p2.csv`
Codex bulut ortamı iki kez açılmadı. Bu yüzden kol `argon/PAKET_T35P2_chatgpt_avrupa_amerika.md` paketiyle normal ChatGPT sohbetinde yürütüldü.

**Teslim:** 10 satır. Lider denetiminden sonra **9 satır**.

### Lider düzeltmeleri
- **EU-012 çıkarıldı:** sayısal metrik yok; yalnız "Sharpe S&P 500'ü aştı" deniyor. Kapı 1'den döner.
- **EU-013 satırında sütun kayması** düzeltildi (bir alan sağa kaymıştı). Ayrıca `maliyet_dahil: evet` iken bayrakta `maliyet_yok` yazıyordu; çelişki giderildi.
- **US-010** ayrı bir strateji değil, US-005..009'un birleşik kitabı: `motor_notu: portfoy`, `kural_tam: kismen`.

### İçerik değerlendirmesi
- **Avrupa forumları beklendiği gibi zayıf çıktı.** wallstreet-online, ABC Bourse, X-Trader, Investire ve FinanzaOnline'da rakamlı strateji bulunamadı; Trade2Win 403 verdi. Yalnız **smart-lab.ru** verdi. Sonuç: Avrupa'da açık, rakamlı strateji paylaşım kültürü zayıf; Rusya istisna.
- **EU-011:** 65 yıl, ama Sharpe ~0,1. Kârlılık iddiası zayıf; işaretlendi.
- **EU-013 (Algebra, Capitalizer):** 2024-07 → 2026-05, net %43,5, MDD %21, Sharpe 1,32; MOEX endeksi aynı dönemde -%2,4. Kural yok, otomatik takip ürünü. Platform takipli olduğu için rakamın değeri var, ama test edilemez.
- **EU-015 (OFZ tahvil grid):** CAGR %31, Sharpe 2,79, ~2 yıl. Grid stratejisi, tarihsel veri "talep üzerine". Yüksek risk profili.
- **US-005..010 (STS Futures, NQ):** 2011-2026, 300-1.650 işlem, ayrıntılı istatistik. Ama **ticari satıcı** ("the combined book is the product"), kurallar kısmen, maliyet yok. Tümüne `ticari_satici` bayrağı eklendi.
  - En şeffaf olanı **US-009 (NQ overnight):** 796 işlem, PF 1,57, Sharpe 1,06, MDD özkaynak eğrisinin %10,3'ü.
  - US-006 (NQ ORB, 09:30-09:45) Faz 1'deki ORB ailesiyle akraba, ama piyasa NQ vadeli.

### Doğrulama
Lider oturumu smart-lab.ru ve stsfutures.com'u açamıyor. Kullanıcıdan 2 örneklem kontrolü isteniyor:
- **EU-015:** https://smart-lab.ru/blog/1310045.php → CAGR %31, MDD -%11, Sharpe 2,79.
- **US-009:** https://stsfutures.com/learn/nq-overnight-strategy-backtest → 796 işlem, PF 1,57, $194.333 net, MDD $20.073.

## Argon kolu (Afrika + G. Amerika): `arastirma/argon_p2.csv`
**Teslim:** 30 satır. 13'ü parti 1'in tekrarıydı, atlandı; 17 yeni satır kaldı. Lider denetiminden sonra **13 satır**.

### Çıkarılanlar (4)
| id | Ad | Neden |
|---|---|---|
| SA-011 | B3 Day Trade canlı portföyü | Canlı day trade portföyü zararda (yazar "péssimo resultado" diyor); kârlılık iddiası yok. Tek strateji değil, 28 karışık sinyal. |
| SA-013 | B3 Day Trade M10 | Strateji değil: canlı portföyün 10 dk zaman dilimi alt kümesi. Yalnız WR var, 18 işlem. |
| SA-014 | B3 Swing Trade H1 | Strateji değil: canlı portföyün 60 dk zaman dilimi alt kümesi. Yalnız WR var. |
| AF-003 | NSE 20 contrarian EMA | Sayısal metrik yok ("al-tutun üstünde anlamlı alfa" ifadesi); kapı 1. |

### Düzeltmeler: kural ihlalleri
- **SA-010: Argon PF'yi kendisi hesaplamış.** Kayıtta "(0.59*2)/0.41 = 2.88" yazıyordu. Bu yazar beyanı değil, türetilmiş bir değer; `iddia_pf` boşaltıldı. Paketteki "uydurma yok, kaynakta olmayanı boş bırak" kuralına aykırı.
- **SA-012: "fator 1.97" PF değil.** Ortalama kazanç / ortalama kayıp oranı. Aynı hata SA-011'de de vardı (1.55). `iddia_pf` boşaltıldı, açıklama `not`'a yazıldı.
- **SA-016/017 (QuantBrasil Feed):** Kaynak yalnız sonuç tablosunu veriyor. Argon'un yazdığı "sistemik filtreler ve dip reversiyon teyidi" gibi giriş/çıkış ifadeleri kaynakta yok. Alanlar boşaltıldı, `kural_tam: hayir`.

### İçerik
- **İyi kayıtlar:**
  - SA-008a/b ve SA-009/010 (Setup 123, Eden dos Traders): kural tam, B3.
  - SA-012: canlı swing portföyü, 6 ayda %20; IBOV aynı dönemde %6. Canlı hesap, ama karma sinyal.
  - AF-005 (EGX30 klasik formasyonlar): 1998-2016, 598 desen.
- **Kapsam şüphesi:** SA-018 (BMV copula-GARCH), SA-019 (COLCAP Markowitz) ve AF-002 (JSE Max Sharpe) al-sat stratejisi değil, akademik portföy optimizasyonu. Kaldılar, ama `kapsam_supheli` olarak işaretlendi. SA-019'daki "966 işlem / WR %64" büyük ihtimalle gün sayısı.
- **AF-004 (Nijerya Random Forest):** ML modeli, Sharpe 5,6; aşırı uyum şüphesi.

**Genel:** Argon'un parti 2 kalitesi parti 1'in altında. QuantBrasil kayıtları iyi, ama yeni ülkelerde akademik makalelere kaymış. Ayrıca iki kural ihlali var: türetilmiş PF ve kaynakta olmayan kural metni.

**Doğrulama:** UdeM ve SciELO sayfaları lider oturumundan açılmıyor. Kullanıcıdan 1 örneklem kontrolü:
- SA-008a: https://quantbrasil.com.br/blog/backtest-da-estrategia-123-utilizando-python/ → 48 işlem, %54, PF 1.15, DD %9.52.

## Doğrulama sonuçları (kullanıcı, ekran görüntüleri, 2026-10-23)
| Kayıt | Sonuç |
|---|---|
| EU-015 (smart-lab grid) | ✅ CAGR %31, MDD -%11, Sharpe 2,79 birebir. Ek: volatilite %11,1, beta 0,0. |
| US-009 (STS NQ overnight) | ✅ $194.333, 796 işlem, 14 yıl, WR %56,3, Sharpe 1,06 birebir. Yazar "tek başına edge değil, çeşitlendirici" diyor. |
| SA-008a (QuantBrasil 123) | ✅ 48 işlem, %54, %3,35, DD 9,52 birebir. ❌ **Tabloda PF satırı yok.** |

### Sistematik Argon hatası: türetilmiş PF
QuantBrasil sonuç tablosu PF vermiyor. Argon'un yazdığı PF'ler hesaplandı:
- SA-008a: 26 × 965,27 / (22 × 988,41) = **1,154** (Argon 1,15)
- SA-008b: 8 × 1216,62 / (4 × 1296,75) = **1,876** (Argon 1,88)
- SA-009: 29 × 1860,86 / (15 × 1897,80) = **1,896** (Argon 1,90)
- SA-001b: 1793 / 994 = **1,80** (Argon 1,80). Bu PF bile değil, payoff oranı.

**Karar:** Yazarın açıkça "Fator de Lucro" yazdığı SA-016 ve SA-017 dışındaki tüm QuantBrasil kayıtlarında `iddia_pf` boşaltıldı: SA-001a/b, SA-003, SA-008a/b, SA-009. Değerler `not` alanına açıklamayla taşındı. Diğer rakamlar (işlem, WR, getiri, DD) doğru çıktı; Argon kayıtları uydurma değil, ama PF alanı güvenilmez.

**Sonraki Argon paketine kural:** "PF yalnız kaynakta 'profit factor / fator de lucro / factor de beneficio' diye yazıyorsa; hesaplama yapma."

## Sonnet kolu (Çin, Japonya, Kore, Hindistan): `arastirma/sonnet_p2.csv` (PR #130)
**16 satır, hepsi kabul.** En kaliteli teslim: kaynaklar API üzerinden tam metin okunmuş, elenenler gerekçesiyle listelenmiş (`arastirma/sonnet_p2_erisim.md`), metin-tablo çelişkisi bile not edilmiş (CN-008a).
- **Çin (BigQuant, 7):** aracı kurum raporları, hepsi maliyet dahil. CN-007a (gürültü bölgesi gün içi momentum, 2013-2024, Sharpe 2,11) ve CN-008b (IF R-Breaker, 440 işlem, Sharpe 1,89) güçlü.
- **Japonya (note.com, 4):**
  - **JP-005:** USDJPY 5 dk RSI + SMA200, 2010-2026, 2.477 işlem, PF 1,56, maliyet dahil. Bu turun en güçlü scalp kaydı.
  - **JP-004:** Gotobi günü, 946 işlem, PF 1,37, maliyet duyarlılığı ve 1.000 rastgele gün permütasyon testi var. Faz 1'deki null testimize benzer bir yaklaşım.
- **Kore (3), Hindistan (2):** IN-004 (SBIN Keltner, 10 yıl, PF 1,70, maliyet dahil) ama al-tutun altında.

**Lider bayrakları:**
- CN-006a: ML (sınıflandırma ağacı).
- KR-003: stopsuz, 221/221 kazanç, MDD %39,7. Connors RSI2 ailesinden.
- CN-008a: metin-tablo çelişkisi.
- IN-003: tarihsiz dönem.

## Parti 2 sonucu ve toplam
| Kol | Parti 1 | Parti 2 | Toplam |
|---|---:|---:|---:|
| Sonnet | 16 | 16 | 32 |
| Argon | 12 | 13 | 25 |
| Codex / ChatGPT | 10 | 9 | 19 |
| Lider | 3 | 1 | 4 |
| **Toplam** | **41** | **39** | **80** |

Türlere göre: swing 43, day 26, scalp 6, belirsiz 5. Birleşik dosya: `arastirma/TUM_KAYITLAR.csv`.

## Lider kısa listesi: sonraki backtest için öncelik
Ölçüt: uzun dönem (en az ~5 yıl) ya da kullanıcı doğrulaması; maliyet dahil ya da şeffaf; kural tam ya da tama yakın; en az ~100 işlem; tek ürün reklamı değil.

| # | id | Strateji | Piyasa / TF | Neden |
|---|---|---|---|---|
| 1 | JP-005 | USDJPY RSI(14) geri dönüş + SMA200 | FX, 5 dk (scalp) | 2010-2026, 2.477 işlem, PF 1,56, maliyet dahil, 17 yılın 16'sı artıda |
| 2 | CN-007a | Gürültü bölgesi gün içi momentum | CSI 500 endeks/ETF, 1 dk | 2013-2024, Sharpe 2,11, maliyet dahil, kural tam (aracı kurum raporu) |
| 3 | JP-004 | USDJPY Gotobi 仲値 saat etkisi | FX, 1 dk (day) | 946 işlem, PF 1,37, maliyet duyarlılığı + permütasyon testi |
| 4 | CN-008b | IF R-Breaker gün içi | CFFEX IF, 1 dk | 440 işlem, Sharpe 1,89, maliyet dahil (2010-2014, eski) |
| 5 | CN-001 | Endeks vadelisi açılış momentumu | CFFEX IF/IC/IH, 15 dk | yıllık %25,8, MDD %7,7, maliyet sonrası |
| 6 | US-009 | NQ overnight momentum | NQ vadeli | doğrulandı; 796 işlem, PF 1,57, Sharpe 1,06; satıcı, kural kısmi |
| 7 | IN-002 | Nifty 30 dk ORB, 2R | Nifty, 15 dk | 2017-2026, 2.122 işlem, PF 1,23; maliyetsiz |
| 8 | SA-003 | Yavaş Stokastik + MME80, 2R | ITUB4, 120 dk | 2013-2021, 159 işlem, kural tam; maliyetsiz, tek hisse |
| 9 | IN-004 | SBIN Keltner kırılımı | NSE, 1 saat | 10 yıl, PF 1,70, maliyet dahil; al-tutun altında |
| 10 | SA-006 | Gap Trap | WDO, 15 dk | doğrulandı; kural tam; yalnız 37 işlem |

**Not:** Bu sıralama yazar beyanına göredir; kanıt değildir. Kısa listenin gerçek değeri, sonraki aşamada bizim motorumuzda (Faz 1 hunisi: maliyet, null testi, OOS) yeniden üretilince ortaya çıkar. Ön koşullar:
- vadeli/FX/dakikalık veri (CFFEX, NQ, USDJPY 1-5 dk);
- motorda seans saati ilkeli;
- short desteği.
