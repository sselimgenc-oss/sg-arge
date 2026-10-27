# Görev: Copy trade kapısı (CT-Kapı v1) ve geniş tarama (2026-10-27)

Dal: `codex/copytrade-kapi` (`main`'den). Durum: `docs/codex_durum_copytrade_kapi.md`. PR: `[CT] kapı + geniş tarama`.
Önce `AGENTS.md`, `DURUM.md`, `docs/KAPI_V3.md` (ilkeler) oku. **Eşikler bu belgede; değiştirme** (değişiklik kullanıcı
kararı). Belgede yazmayan karar gerekirse dur, durum dosyasına yaz.

**Kapsam sınırı:** yalnız herkese açık Hyperliquid verisi (`/info`, lider tablosu). Cüzdan, anahtar, emir, gerçek para yok.
Mevcut kod: `copytrade/` (tarama, ölçütler, kurallar, inceleme), `kapi/istatistik.py` (NW alfa, DSR, N_eff). Bunları
kullan; yeniden yazma. İlk örnek inceleme raporu: `copytrade/inceleme/RAPOR_istikrar.md` (lider dalı; bulgular aşağıda).

## 0. Önceki incelemeden bilinen sorunlar (düzelt)
1. **Para yatırma/çekme:** `portfolio` hesap değeri yatırma/çekmeyi içerir → bazı adreslerde %4.500.000 gibi getiri.
   `userNonFundingLedgerUpdates` ile yatırma/çekme okunur; getiri **zaman ağırlıklı** (nakit akışından arındırılmış) hesaplanır.
2. **Dolum sayısı ölçüt değildir** (tek emir yüzlerce dolum olur): işlem = pozisyonun sıfıra dönmesi/ters dönmesi
   (`olcut.closed_round_trips`), martingale emir (`oid`) düzeyinde ve > %2 aleyhte (`olcut.martingale_ratio`), kaldıraç =
   pozisyon değeri / hesap değeri (`olcut.effective_leverage`). Bunlar yapıldı; testleriyle koru.
3. `API sınırı (10.000)` uyarısı yanlış (sayfalama 10.000'i aşabiliyor); dolum tavanı parametre olsun.

## 1. Geniş tarama (iki aşama, Actions)
- **Evren:** lider tablosundaki tüm adresler; hesap ≥ 25.000 USD ve tüm zaman PnL > 0. Taranan adres sayısı (ham N)
  her koşuda kaydedilir.
- **1. aşama (kâr eğrisi):** her adres için `portfolio` (tek istek). Son 12 ay, zaman ağırlıklı aylık getiri: ≥ 6 ay,
  kârlı ay ≥ %60, zirveden düşüş ≤ %30, 12 ay getiri > 0. Matris: adresler 8 parçaya bölünür (paralel iş, ayrı IP);
  istemci tarafı hız sınırı korunur (`tarama.RateLimiter`).
- **2. aşama:** 1. aşamayı geçenlerin **tamamı** (sınır yok; çoksa ayrı matris) için dolum, funding, ledger ve
  mum verisi (`candleSnapshot`) → kapı adımları.

## 2. CT-Kapı v1 adımları (sonuç: Geçti / Yetersiz / Kaldı)
| # | Adım | Şart | Sağlanmazsa |
|---|---|---|---|
| 1 | Veri bütünlüğü | Yatırma/çekme arındırılmış; spot ayrı; dolum geçmişi pencereyi kapsıyor | **Yetersiz** |
| 2 | Asgari kanıt | ≥ 180 gün, ≥ 50 kapanmış işlem, ≥ 6 aktif ay | **Yetersiz** |
| 3 | Kopyalanabilirlik | Medyan tutma ≥ 1 saat; gerçek kaldıraç medyan ≤ 3x, en yüksek ≤ 10x; **30 dk gecikmeli** sanal kopyada (giriş/çıkış 30 dk sonraki mum açılışı, taker %0,045 + kayma %0,05 her taraf, gerçek funding) net > 0 | **Kaldı** |
| 4 | Sağlamlık | Kârlı ay ≥ %60; en büyük işlem kârın < %30'u; en iyi işlem çıkınca PF > 1,2; martingale işareti yok | **Kaldı** |
| 5 | Plasebo | **İşlem yerleştirme plasebosu:** trader'ın kendi işlemleri (coin, yön, boyut/hesap, tutma süresi) aynı dönemde rastgele başlangıçlara, çakışmasız yerleştirilir; gerçek mumlar ve aynı maliyet; 1.000 tekrar; tek yönlü p ≤ 0,05 | **Kaldı** |
| 6 | Alfa | Günlük getiri, maruziyet eşleşmiş kıyasa (pozisyonda olunan oran × BTC) göre; yıllık alfa > 0 ve NW t ≥ 2 (`kapi/istatistik.nw_alpha`, 365 gün) | Alfa > 0 ama t < 2 → **Yetersiz**; alfa ≤ 0 → **Kaldı** |
| 7 | Çoklu test | 5. adıma ulaşan **tüm** adreslerin plasebo p-değerlerine BHY, q ≤ 0,10 | **Kaldı** |
| 8 | Kümeleme | Geçenlerin günlük PnL korelasyonu; hiyerarşik, ρ ≤ 0,5; her kümeden en yüksek alfa-t | seçim |

Bilgi sütunları (eleme yapmaz): varlık sınıfı payları (kripto/hisse/endeks/emtia), en çok işlem gören 3 coin ve
Binance'te karşılığı olup olmadığı (sabit liste), HYPE payı, gecikme 0/5/30/120 dk net sonuçları, DSR (N_eff ile).

## 3. Çıktı
Actions iş akışı `copytrade_kapi.yml` (`workflow_dispatch` + push tetiği yalnız `codex/copytrade-kapi` dalında).
Sonuçlar dala: `copytrade/kapi/<tarih>/asama1.csv.gz`, `sonuc.csv` (adres, her adımın değeri ve geçti/kaldı, sınıf),
`RAPOR.md` (huni sayıları, Geçti listesi, Yetersiz'lerin en iyi 10'u, sınırlamalar). **Karar önerisi yok.**
Koşu süre sınırına takılırsa o ana kadarki sonuç yazılsın (parça parça kayıt).

## 4. Testler (ağsız, sabit örnek yanıtlarla)
Zaman ağırlıklı getiri (yatırma/çekme olan ve olmayan seri); gecikmeli kopyanın bir sonraki mum açılışını kullanması;
plasebonun işlem sayısı/tutma/yön/coin'i koruması ve çakışmasızlığı, sabit tohumla aynı sonuç; BHY bilinen örnek;
her adımın Geçti/Yetersiz/Kaldı ayrımı bilinen örneklerle; matris parçalamanın adres kaybetmemesi.

## Başlarken / bitirirken
`git checkout main && git pull origin main && git checkout -b codex/copytrade-kapi`. Bitince `python -m pytest -q`
(sonuç PR'a) ve `git push -u origin codex/copytrade-kapi`. PR açılamazsa push yeterli.
