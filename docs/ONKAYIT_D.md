# Ön kayıt — D yolu (2026-10-28; kullanıcı onaylı, K1–K11)

Bu belge gölge verisi görülmeden yazıldı. Değişiklik yalnız kullanıcı kararıyla, yeni sürüm olarak (eski sürüm silinmez).
Sayılar uygulamada yalnız `copytrade/kurallar.yaml`'dan okunur; bu belge ↔ yaml uygunluk testi zorunlu.
**Dondurma:** Faz 3 başlamadan önce lider bu dosyanın commit hash'ini `DURUM.md`'ye yazar.

## Katlar
- Havuz: ön elemeyi (veri yeterliliği, tarz, kaldıraç, hesap değeri tabanı) geçen adreslerin tamamı; hepsi gölgede.
- Aday: gölge puanına göre havuzun en iyi %15'i.
- Oda: aday katından en iyi 10–20 adres.
- Terfi: gölgede en az 3 hafta ve 10 kapanmış işlem. Odadan çıkış: puan aday katının alt yarısına düşerse.
- Etiketlenen adres hiçbir kayıttan silinmez; pasifleşirse sıfır getirili gün olarak paydada kalır.

## Kollar
- Kohort: oda (ikincil: aday katı).
- Kontrol: havuzdan puana bakmadan rastgele, oda ile aynı sayıda; tohum her etiketleme için `tarih` + sabit tohum, kayda geçer.
- Taban: leaderboard 30 günlük PnL ilk N (N = oda sayısı).
- Elle liste: `copytrade/izleme_listesi.yaml`.
- Elle kopya: Telegram [Açtım]/[Atladım].

## Kopya kuralı varyantları (aynı sinyaller, paralel gölge)
- V0 birebir (tarz gecikmesi: intraday 30 dk, swing 120 dk).
- V1 fiyat bandı: giriş, trader girişinden intraday ≤ %1, swing ≤ %2 uzaksa; atlananlar ayrıca izlenir.
- V2 zarar/süre çıkışı: teminatın %50'si zararda çık; swing'de 7. ve 14. günde zarar/kâr sınırı daralır (ayrıntı Faz 2'de
  `kurallar.yaml`'a yazılır, Faz 3'ten önce donar).

## Ölçüm
- Birincil: eşit ağırlıklı, sabit sermayeli kohort ve kontrol portföylerinin günlük net getiri farkı (V0).
- Belirsizlik: haftalık blok bootstrap, %95; ikincil: trader kümesi bootstrap, BTC betası düzeltilmiş fark.
- Başarı: fark alt sınırı > 0 **ve** kohortun maliyet sonrası mutlak getirisi > 0.
- Canlı gölge: en az 12 hafta; performansa yalnız analiz tarihinde bakılır, arada yalnız veri kalitesi. Belirsizse bir kez
  12 hafta uzatılır.

## Durdurma
1. Faz 3 (geçmiş prova) pencerelerinin yarısından fazlasında kohort kontrolü geçemiyorsa canlı gölge başlamaz.
2. Hiçbir kol gecikme ve maliyet sonrası > 0 değilse "bu yöntemle işe yaramıyor" sonucu sunulur.
