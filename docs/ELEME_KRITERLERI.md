# Paper Trading Aday Eleme Kriterleri (v0.2 TASLAK)

Durum: Claude-Mod önerisi + Codex görüşü (Issue #1) birleştirildi. **Opus denetimi ve kullanıcı onayı bekliyor.**
Eşikler evrensel yasa değil, kural-ı pratik (Pardo, Bailey & López de Prado, Harvey-Liu-Zhu, Davey, Carver).

## İlkeler
1. Paper = uygulama doğrulaması (sinyal paritesi, zamanlama, maliyet, operasyon). Kârlılık kanıtı değil. Giriş kapısı gevşek, canlı kapısı sıkı.
2. Eksik veri/doğrulanamama başarısızlık değildir. Durumlar ayrı: **Geçti / Koşullu / Doğrulanamaz / Reddedildi**.
3. Rapor rakamı kanıt sayılmaz; her aday bizim motorumuzda yeniden üretilir.

## Kanıt seviyeleri
A: OOS + stres testli rapor (Codex Algo 21) · B: çok piyasalı backtest, OOS/stres yok, optimizasyon izi · C: yalnız yayıncı beyanı.

## Test sırası (pahalı testler zayıf adaylara harcanmaz)
1. **Spesifikasyon:** karar zamanı, veri, giriş fiyatı, çıkış önceliği, boyut, evren, kurumsal aksiyon, maliyet tek anlamlı yazılı. Aynı bar bilgisiyle aynı bar fiyatından dolum = otomatik hata.
2. **Veri/look-ahead:** point-in-time evren, delisted semboller, split/temettü politikası, takvim/timezone, eksik/stale bar. BIST/ABD'de survivorship kanıtı yoksa sonuç **Koşullu**.
3. **Replikasyon:** rapor PF/getirisi +-%25 içinde yeniden üretilmeli.
4. **Maliyet/gecikme stresi:** 1x, 2x, 3x komisyon+spread/slippage; +1 bar gecikme; kötü fiyat senaryosu. 2x'te PF >= 1,2, 3x'te ve +1 barda pozitif.
5. **Walk-forward:** anchored + rolling, purge/embargo; karar birleşik OOS ve pozitif dönem oranına göre (tek pencere değil). OOS PF >= 1,1 (tek başına yetmez; alt güven sınırı ve işlem başı beklenen değer de bakılır).
6. **Parametre platosu:** 2-3 boyutlu komşuluk; komşu medyan OOS, pozitif hücre oranı, optimum sınırda mı. Kapı = plato kararlılığı.
7. **Block bootstrap Monte Carlo:** CAGR, PF, Sharpe, MDD, kayıp serisi, risk-of-ruin dağılımı; kapı alt güven sınırına dayanır, nokta tahmine değil. Beklenen MDD ~ backtest MDD x 1,5-2.
8. **DSR/PBO:** deneme sayısına PDF varyantları + bizim taramalarımız + reddedilenler dahil; korele varyantlar kümelenip "etkin bağımsız deneme" ayrıca raporlanır. PBO az örneklemde (60-100 işlem) sert kapı değil **uyarı**.
9. **Örneklem/anlamlılık:** >= 100 işlem (swing >= 60), t-stat > 2 (çoklu testte > 3), tek enstrüman/yıla bağımlılık yok (en iyi işlem/enstrüman çıkarılınca pozitif).
10. **Aşırı uyum alarmı:** PF > 4, Sharpe > 2-3, getiri > %500 → ek doğrulama zorunlu (3-8 hepsi sıkı uygulanır).

## Day trade
Günlük OHLCV ile doğrulanamayanlar: gün içi sinyal sırası, aynı bar stop/target önceliği, gerçek spread, derinlik, kısmi dolum, seans içi likidite, açılış müzayedesi. İntraday adaylar saatlik/dakikalık veri olmadan **Doğrulanamaz** etiketi alır (reddedilmez, geçmiş de sayılmaz). Saatlik veri kaynağı açık soru.

## Short ve kaldıraç (x2/x3)
Ayrı kapı: borrow/fee, funding, short kısıtları, gap ve tasfiye/marjin riski modellenmeden long sonucu ölçeklenmez. Her varyantın ayrı OOS + stres sonucu olur. Önce long-only x1 geçmeli.

## Portföy riski
MDD üst sınırı istatistik eşiği değil **risk bütçesidir**. Öneri portföy MDD %15 (kullanıcı onayı bekliyor). Strateji başına sermaye, marj ve korelasyon buna göre çözülür; tek strateji MDD'sini %15'e eşitlemek yerine bootstrap %95 MDD ve portföy katkısı kapı olur. İşlem başı risk %0,5, toplam açık risk %2, paper kill-switch %10 MDD.

## Altyapı (Codex önerisi)
Tarama/plato için VectorBT/Numba; nihai doğrulama ve paper paritesi için aynı emir kurallarını kullanan küçük event-driven referans motor. Sabit çıktı şeması: IS/OOS ayrımı, deneme sayısı, maliyet senaryoları, güven aralıkları, veri kusurları, yeniden üretim hash'i.

## Canlıya geçiş kapısı (paper sonrası)
>= 3 ay ve >= 30 işlem, paper sonucu backtest beklentisinin güven aralığında, gerçek kayma varsayımı aşmıyor, portföyde düşük korelasyon, kaldıraç x1 → x2 → x3 kademeli.

## Açık sorular
- Opus: eşikler (özellikle t-stat, OOS PF 1,1, 2x'te PF 1,2, %25 replikasyon toleransı) makul mü? Deneme sayısı nasıl sayılacak?
- Sol 6.1: altyapı ve otomatik look-ahead/survivorship korumaları.
- Kullanıcı: portföy MDD %15 onayı; saatlik veri kaynağı (BIST dahil).
