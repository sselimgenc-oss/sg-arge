# Görev: D yolu — geçmiş kapı + ileriye dönük gölge (2026-10-28, lider; kullanıcı onaylı)

Kaynak: kullanıcı kararı 2026-10-28 (proje yeniden açıldı, lider Claude), Sol 6.1'in iki görüşü, Etre V2 incelemesi.
Bu belge yöntemi değiştirir: **trader'ı seçen artık geçmiş kapı değil, ileriye dönük gölge ölçümüdür.** Geçmiş kapı ön eleme olur.

## Neden
- Geçmişi yeniden kurmak hatalara açık (düşüş > 1, plasebo, mum sınırı, dolum sınırı; `docs/DENETIM_2026-10-27.md`).
- 9–20 adresle 3 ay izlemenin istatistiksel gücü neredeyse sıfır.
- Asıl soru "bu trader iyi mi?" değil, **"seçim yöntemimiz rastgele seçimden iyi mi?"** sorusu. Bunu ancak kontrol grubu yanıtlar.
- Etre'den alınan: ileriye dönük gölge, kohort ↔ kontrol, sürekli keşif. Alınmayan: kısa gölge sonucuyla odaya alma (şansa göre seçim),
  gecikmesiz gölge, memecoin spot.

## Hat
| # | Aşama | Ne yapar | Kod |
|---|---|---|---|
| 1 | Keşif | Leaderboard haftalık taranır; yeni adresler havuza girer | `copytrade/tarama.py`, `kapi.py` |
| 2 | Ön eleme (sert filtre) | Veri yeterliliği, tarz (intraday/swing), kaldıraç, hesap değeri tabanı | `kapi.py` adım 1–2 |
| 3 | Puan | Geçmişte tarz gecikmeli, maliyetli kopya getirisi (`copy_ledger`) | `copytrade/defter.py` |
| 4 | Kollar | Kohort / kontrol / leaderboard tabanı / elle liste (aşağıda) | yeni: `copytrade/kollar.py` |
| 5 | Gölge defter | Etiketten **sonraki** her dolum, tarz gecikmesi + maliyet + funding ile sanal kopyalanır | yeni: `copytrade/golge.py` (`copy_ledger` üstüne) |
| 6 | Oda | Ön kayıtlı kural geçerse en iyi 10–20 adres Telegram ile elle kopyalanır | izleme motoru + Worker |

Plasebo, alfa, BHY ve istikrar ölçütleri **bilgi sütunu** olarak kalır; karar vermez.

## Kollar (her etiketleme anında, aynı uygun havuzdan)
- **Kohort:** uygun havuzda puanı en yüksek N adres.
- **Kontrol (birincil kıyas):** uygun havuzdan puana bakmadan, sabit tohumla rastgele N adres (kohort üyeleri de çıkabilir).
- **Taban:** leaderboard 30 günlük PnL'de ilk N adres (ön elemesiz). Kapı bunu geçemiyorsa gereksizdir.
- **Elle liste:** `copytrade/izleme_listesi.yaml` (bugünkü 9 adres).
- **Elle kopya (Telegram):** [Açtım]/[Atladım] ayrı bir kol olarak ölçülür; elle seçim değer katıyor mu.

**Üç kat (Etre: 1000 → 100 → 20, her katta gölge kopya):** uygun havuzun **tamamı** gölgede izlenir (altyapı izin verdiği ölçüde);
gölge puanına göre **aday** katı (≈ havuzun %10–20'si) ve **oda** (10–20 adres) seçilir. Kat geçiş kuralları önceden yazılır (en az gün
ve işlem sayısı, histerezis). Asıl ölçüm her katın **terfiden sonraki** getirisinin havuzun geri kalanıyla farkıdır (Etre'nin
"kohort ↔ havuz" kıyası); terfi öncesi gölge sonucu kanıt sayılmaz.

**Dinamiklik:** her haftalık taramada yeni uygun adresler aynı kurallarla kollara eklenir ve **kendi etiket tarihinden** itibaren ölçülür
(giriş haftası = "vintage"). Etiketlenen adres sonradan kollardan silinmez; pasifleşirse sıfır getirili gün olarak paydada kalır.

## Kopya kuralı varyantları (Etre tweeti, 2026-10-28)
Aynı sinyaller üzerinde paralel gölge; aynı işlemler karşılaştırıldığı için az veriyle güçlü kıyas. Önceden kayıt; sonuçla değiştirilmez.
- **V0 birebir:** trader ne yaparsa, tarz gecikmesiyle.
- **V1 fiyat bandı:** bizim giriş fiyatı trader girişinden %X'ten uzaksa girme (X `kurallar.yaml`'da). Atlanan işlemler de gölgede
  izlenir: band, kazananları mı atlatıyor (ters seçim) ölçülür.
- **V2 zaman/zarar çıkışı:** sabit zarar kesme + süre uzadıkça daralan zarar ve kâr sınırı (Etre spotta: −%30; 18 sa sonra ±%15;
  24 sa sonra ±%20). Kaldıraç için eşikler teminata göre yazılır.
Faz 3'te (geçmiş prova) ayrıca **çok alanlı puan** (Etre gibi birçok ölçütün ağırlıklı toplamı) ayrı bir kohort kolu olarak
denenir; tek ölçütlü puanı geçemiyorsa kullanılmaz (aşırı uyum riski).
Kohort güncellemesinde gidip gelmeyi azaltmak için histerezis: girmek için ilk N, çıkmak için ilk 2N'nin dışına düşmek.

## Gölge defter kuralları (hepsi altın örnek testiyle)
1. Giriş ve çıkış: trader dolum zamanı + tarz gecikmesi (intraday 30 dk, swing 120 dk), sonraki erişilebilir fiyattan; taker + kayma.
2. Kısmi kapanış: trader pozisyonunun %X'ini kapatırsa gölge de kendi pozisyonunun %X'ini kapatır.
3. Ekleme: orantılı, gölge pozisyonu başına üst sınırlı (sınır `kurallar.yaml`'da).
4. Yön değişimi (flip) = kapanış + yeni açılış.
5. Kaçırılan işlem: gölge girmeden trader çıktıysa işlem silinmez, `kacirildi` diye kaydedilir; ters pozisyon açılmaz.
6. Funding: gölgenin kendi pozisyonu üzerinden saatlik.
7. Likidasyon: gölgenin kendi teminatı ve mark fiyatıyla.
8. Eksik veri: dolum ya da fiyat yoksa satır `eksik` işaretlenir; sessizce düşmez.
9. **Sağlama:** gecikme 0 ve maliyet 0 iken gölge, trader'ın gerçekleşmiş PnL'ini orantılı olarak yeniden üretir. Üretemezse motor
   hatalıdır, sonuç yayımlanmaz.
10. Gecikme zinciri ayrı kaydedilir: trader dolumu → bizim tespit → Telegram mesajı → kullanıcının [Açtım] zamanı.

## Ölçüm ve karar (ön kayıt; veri görülmeden dondurulur)
- **Birincil ölçüt:** eşit ağırlıklı, sabit sermayeli kohort ve kontrol portföylerinin **günlük net getiri farkı**.
- **Belirsizlik:** haftalık blok bootstrap; ikincil olarak trader kümelerine göre bootstrap ve BTC betası düzeltilmiş fark.
  Gölge (işlem) birimiyle güven aralığı kurulmaz.
- **Başarı:** farkın %95 alt sınırı > 0 **ve** kohortun maliyet sonrası mutlak getirisi > 0.
- **Ara bakış:** sürecin ortasında yalnız veri kalitesine bakılır (kaçan dolum, gecikme dağılımı, sağlama). Performansa yalnız ön kayıtlı
  analiz tarihinde bakılır. Kâr görüldükçe trader, eşik ya da süre değiştirilmez.
- **"Belirsiz" geçerli bir sonuçtur.** Süre uzatılacaksa bu da önceden yazılır.

## Fazlar (bir faz bitmeden sıradakine geçilmez)
- **Faz 0 — Temel:** `claude/kapi-v1-1` dalı (`defter.py`, altın örnekler, akıl sağlığı kapısı) gözden geçirilip `main`'e alınır. PR açık
  değil; lider açar ve denetler. Hesap sürümü d ile final hızlı koşu sonucu veri dalında yok (son yazılan: c) → yeniden koşulur.
- **Faz 1 — Ön kayıt:** `docs/ONKAYIT_D.md`: kollar, N, tohum, metrik, birim, süre, analiz tarihi, durdurma kriterleri; commit hash'iyle
  dondurulur. Sayısal değerler kullanıcı onayıyla.
- **Faz 2 — Gölge motoru:** `copytrade/golge.py` + yukarıdaki 10 kural için altın örnekler + sağlama testi. Cevabı bilinen sentetik
  trader'lar: etkisi enjekte edilmiş trader yakalanmalı, sıfır etkili trader ~%5 oranında geçmeli. 10.000+ dolumlu adreste zaman
  penceresiyle sayfalama.
- **Faz 3 — Yürüyen pencereli geçmiş test:** T anına kadarki veriyle etiketle, sonraki 60 günü gölge motoruyla ölç, pencereyi kaydır;
  dört kol. Güç hesabı (gerçek varyansla). Not: evren bugünkü leaderboard'dan geldiği için hayatta kalan yanlılığı var; sonuç
  **iyimser üst sınırdır**.
- **Faz 4 — Canlı gölge:** devam kararı çıkarsa T0'da etiketler dondurulur, canlı gölge başlar; haftalık keşif yeni vintage ekler.
- **Faz 5 — Oda ve ofis:** ön kayıtlı kural geçerse Telegram bildirimleri odaya bağlanır. Pano ofis görünümü ilk canlı veriden sonra
  (her sayı gerçek veriye bağlı, yanında n ve zaman damgası; veri yoksa "bilinmiyor").

## Roller (Etre'deki ajanların karşılığı)
Etre'de her iş bir LLM "ajanı"; bizde her rol **deterministik bir modül ya da kural**dır (kararı oylama değil kural verir).
Karakterler yalnız pano ofis görünümünde, modülün gerçek durumunu gösterir.

| Etre rolü | Bizdeki karşılığı | Durum |
|---|---|---|
| Patron (oylama, son söz) | Kullanıcı karar verir; lider denetler, birleştirir | var |
| Lab müdürleri (gölge) | Gölge defter + kollar (Faz 2–4) | yeni |
| İşlem şefleri (kopyalama kuralları) | Oda kuralları: fiyat kayması toleransı aşılınca "atla", stop, kademeli kâr alma önerisi; Telegram v2 | Faz 5 |
| Finans (kasa, işlem büyüklüğü) | Sanal kasa ve işlem başı tutar kuralı (`kurallar.yaml`); gölge ve oda aynı kuralı kullanır | yeni |
| Risk (yoğunlaşma) | Trader başı ve coin başı tavan, toplam açık risk tavanı, likidasyon mesafesi; aşılırsa bildirim "atla" der | yeni |
| Gözcü (giriş-çıkış kaydı) | Kollara/odaya her giriş-çıkış gerekçesiyle `olaylar.jsonl`'a yazılır; silinmez | yeni |
| Denetçi (veri kalitesi, API, gecikme) | Akıl sağlığı kapısı + gölge sağlaması + gecikme zinciri; bozulunca yayım durur, Telegram uyarır | kısmen var |
| Sekreter (kural kitabı, kararlar) | `kurallar.yaml`, `DURUM.md`, ön kayıt hash'i, git tarihçesi | var |
| Arşivci (eski veri) | Veri dalları (`copytrade-kapi`, `copytrade-izleme`), eski hesap ayrımı | var |
| Haber şefi (Telegram) | Worker: anlık bildirim, `/durum`; eklenecek: gün sonu özeti | kısmen var |
| Çaycı | Yalnız ofis süsü; veri gibi görünmez | Faz 5 |

Veto karşılığı: Risk, Finans ve Denetçi kuralları sağlanmazsa bildirim gönderilmez ya da "atla" işaretlenir. Bunu bir ajan değil kural yapar.

## Durdurma kriterleri (öneri; kullanıcı onayı gerekli)
1. Faz 3'te pencerelerin yarısından fazlasında kohort kontrolü geçemiyorsa canlı teste başlanmaz.
2. Hiçbir kol 30 dk / 2 sa gecikme ve maliyet sonrası > 0 değilse "Hyperliquid copy trade bu yöntemle işe yaramıyor" sonucu
   kullanıcıya sunulur; araştırmayı kapatmak geçerli bir sonuçtur.

## Açık sorular (kullanıcı kararı)
1. Durdurma kriterleri yukarıdaki gibi mi?
2. Canlı gölge süresi: en az 12 hafta öneriliyor; büyük ihtimalle yalnız büyük etkiler görülür.
3. Canlı tarama altyapısı: Hyperliquid istek sınırları Faz 2'de dokümandan doğrulanır. Worker ücretsiz planı tur başına ~50 alt istekle
   sınırlı; yüzlerce adres için dönüşümlü tarama ya da ücretli plan (para kararı).
4. Faz 0–3'ü hangi ajan yapar? (öneri: Faz 0 lider, Faz 2–3 tek ajan, tek dal)

## Değişmez kurallar
`AGENTS.md`: gerçek para ve emir yok; eşikler yalnız `kurallar.yaml`'da; her hesap değişikliği altın örnekle; veri üreten işte çıktı
özeti; `|| true` yok; testler zayıflatılmaz.
