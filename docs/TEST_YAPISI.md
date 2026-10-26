# Test yapısı v2: sadık ölçüm, geniş aday, sıkı canlı sınav

**Karar:** kullanıcı onayı, 2026-10-24 (lider önerisi + Codex/Sol 6.1 eleştirisiyle birleşik son hali). Sonuçlar görülmeden yazıldı.
**Yerini aldığı:** `docs/ELEME_KRITERLERI.md` hunisi (Aşama 1 → 2a → 2b) artık **eleyici değildir**; o testlerin sonuçları bilgi sütunu olarak raporlanır. Kapsam: TV-2 (942) ve daha önce test edilen bütün aileler (Faz 1, U1, U4, U6/TV, Reddit; U7 koşusu).

## İlke
Sertlik backtest'ten canlı paper'a taşınır. Backtest geniş bir aday seçicidir; asıl süzgeç canlı gölge kitaptır; gerçek para yalnız canlıda kanıtlanmış stratejiye ve kullanıcı kararıyla.

## Adım 0: çalıştırılabilirlik ve nedensellik denetimi (zorunlu)
Her çeviride aranır: geleceği gören veri (`request.security` lookahead, `barstate`/kapanmamış bar), repaint (sonradan değişen pivot/zigzag/sinyal), gerçek dışı dolum (aynı bar bilgisiyle aynı bar fiyatı, `calc_on_every_tick` varsayımı, bar içi sıra iyimserliği).
- **Yazar sonucu:** Pine kodu ve `strategy()` ayarları birebir; yalnız bilgi.
- **Uygulanabilir sonuç:** yukarıdaki hatalar düzeltilmiş (kapanmış bar, sonraki açılışta dolum, kötümser bar içi sıra) + gerçekçi maliyet ve kayma (kripto %0,1/taraf, diğerleri %0,05/taraf + 1 tick). **Bütün kararlar bu sonuca göredir.**
- Düzeltme kuralın kendisini değiştiriyorsa (strateji yalnız geleceği görerek çalışıyorsa) satır "Uygulanamaz (nedensellik)" olarak, nedeniyle listelenir.

## Adım 1: sadık test
- Yazarın sembolü, zaman dilimi, kodu ve parametreleri; long **ve** short. Evren havuzuna taşıma, sınıf eşleme, parametre değişikliği yok.
- **Sınama dönemi = test edilen kod sürümünün doğrulanabilir tarihinden sonrası.** Sürüm tarihi TradingView sürüm geçmişinden (pine-facade sürüm listesi) alınır; ilk yayın tarihi tek başına yetmez.
- Her satıra etiket:
  - `temiz`: sürüm tarihi belli, sonrası en az 1 yıl veri;
  - `tarih_belirsiz`: sürüm geçmişi yok ya da kod sonradan değişmiş ve test edilen sürümün tarihi bilinmiyor; sınama yine yapılır, "temiz OOS" denmez;
  - `yetersiz_kanit`: sürüm sonrası 1 yıldan az veri. Başarısız sayılmaz.
- Daha önce test edilen ailelerde (yayın tarihi olmayan kaynaklar) sınama dönemi o ailenin mevcut OOS dönemidir ve etiket `tarih_belirsiz`'dir.

## Adım 2: tek kapı
**Geçer:** Adım 0'ı geçmiş **ve** uygulanabilir sonuçta sınama dönemi net kârı > 0.
- **İzle listesi:** sınama döneminde işlem açılan farklı takvim haftası < 10 (etkin örneklem; aynı gün açılan ilişkili işlemler tek sayılır). Elenmez; sanal havuzda izlenir.
- **Koruma listesi:** tek başına net zararda ama aynı risk bütçesiyle mevcut gölge sepete eklendiğinde sepetin bootstrap MDD95'ini düşüren stratejiler. Ayrı değerlendirilir.
- Kapıdan kalan her satır nedeniyle yazılır; sessiz eleme yoktur.

## Adım 3: sıralama (eleme değil)
1. **Ortak ölçek:** karşılaştırma için her adayın günlük net getirisi yıllık %10 oynaklığa ölçeklenir (yazarın boyutu sıralamayı etkilemez).
2. **Belirsizlik:** ana sıralama ölçütü sınama dönemi haftalık net getiri ortalamasının block bootstrap **%10 alt sınırı** (yüksek PF değil).
3. **Kopya ayıklama:** önce kod/kural benzerliğiyle açık kopyalar; sonra ortak tarihlerde günlük getiri korelasyonu > 0,8 **ve** işlem tarihlerinin %50'den fazlası örtüşen adaylar aynı kümeye. Her kümeden en iyi sıralı tek temsilci. Aynı sembol + aynı yön en çok 3 kitap.
4. **Portföy katkısı:** temsilcinin mevcut kitaplarla korelasyonu ve sepet MDD'sine etkisi.
5. Bilgi sütunları: tüm dönem sonucu, PF, getiri/MDD95, kârlı yıl oranı, al-tut (aynı sembol, aynı dönem), rastgele giriş yüzdeliği, 2x/3x maliyet, +1 bar gecikme, yazar sonucu, DSR (aile bazlı).
Yazarın iddia ettiği getiri hiçbir aşamada kullanılmaz.

## Adım 4: canlı izleme
- **Sanal havuz:** Adım 2'yi geçen ve izle listesindeki bütün adaylar tek bir işte, ortak veri indirmesi ve sinyal hesabıyla, kendi zaman dilimlerinin kapanışında sanal olarak izlenir (günde en çok birkaç koşu). Kitap sayısı sınırı yoktur; gerçek Actions maliyeti ölçülür ve DURUM'a yazılır.
- **Canlı paper kitapları (sınırsız, kullanıcı kararı 2026-10-26):** Adım 2'yi geçen **her** strateji (kopya ayıklamadan sonra küme temsilcisi) kendi kitabıyla canlı paper teste girer; sayı sınırı, seçim ya da kura yoktur. Her kitap 5.000 USD sanal sermaye, yazarın mantığı, bizim gerçekçi maliyetimiz, ortak ölçekte risk. (Eski "20 gölge kitap" seçimi kaldırıldı.)
- **Deneme kaydı:** `results/canli/denemeler.csv`: kitaba giren, çıkan, yerine giren her strateji tarihiyle. Hiçbir satır silinmez.

## Adım 5: canlı karar
Sermaye koruması ve başarı kanıtı ayrıdır.
- **Durdurma (zarar bütçesi):** kitap başlangıç sanal sermayesinin **%10'unu** kaybederse durur (deneme kaydına yazılır). Kullanıcı kararı, 2026-10-24.
- **İlerleme:** ayda bir, ayın ilk günü (sabit) kontrol. Kitabın canlı haftalık net getirilerinden, sıfır merkezli temkinli önselle, "beklenen haftalık getiri > 0" olasılığı hesaplanır; en az 26 canlı hafta ve en az 10 işlem haftası varsa ve olasılık eşiği aşılırsa kitap **gerçek para adayı** olur.
- **Eşik kalibrasyonu:** eşik, sıfır kenarlı (getirileri ortalamaya göre merkezlenmiş) stratejilerin simülasyonunda yanlış terfi oranını aylık kontrol boyunca ≤ %10 tutacak şekilde, canlı sonuçlar görülmeden belirlenir ve bu dosyaya yazılır.
- Gerçek para kararı ve boyutu her zaman kullanıcınındır; önce küçük.

## Hedef
Tek tek kazanan değil, maliyet sonrası birlikte çalışan çeşitlendirilmiş bir strateji sepeti.

## Çeviri sırası (TV-2)
1. Açık kod, belli sürüm, verisi ve motor desteği hazır olanlar.
2. Aynı altyapıyı paylaşanlar (birlikte çevrilip birlikte doğrulanır).
3. Sürüm sonrası geçmişi uzun olanlar.
4. Portföyde eksik piyasa ve mekanizmalar.
5. Karmaşık veri, repaint şüphesi ya da erişilemeyen sembol gerektirenler (en sona).
