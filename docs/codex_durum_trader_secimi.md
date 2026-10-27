# Durum — Trader seçimi (CT-Kapı v1.1 + Keşif verisi)

## Adımlar (her commit'te güncellenir)
- [x] 1. **26** — küçük PR: izleme/Worker değişiklikleri ayrı dalda → [sg-arge#299](https://github.com/sselimgenc-oss/sg-arge/pull/299); bu dal yalnız kapı/ölçü dosyalarında
- [ ] 2. **15 + 19** — payda hatası (düşüş/getiri/calmar); kopya defteri (mum zaman sınırı, miras pozisyon, açık pozisyon fiyatlama, funding)
- [ ] 3. **20 + 21 + 22** — plasebo aynı motor; alfa maruziyeti pozisyon çizelgesinden; kaldıraç/ücret/en iyisiz PF/martingale
- [ ] 4. **14 + 23** — %44/%49; tüm eşikler yalnız kurallar.yaml; karar–kod uygunluk testi; dondurma özetleri
- [ ] 5. **25 + 18** — ≥6 altın örnek; akıl sağlığı kapısı; ölü sütunlar; `kopya_eksik`, `dolum_siniri`
- [ ] 6. **24 + 16** — `|| true` kalktı, eksik koşu `durum: eksik`; dış adaylar (`kaynak = dis_aday`)
- [ ] 7. Hızlı koşu (9 aday + 0x1404 + dış adaylar) + sütun özeti raporu (tam koşu başlatılmaz; lider onaylar)

SORU: (yok)

Yapan: Sonnet. Dal: `claude/kapi-v1-1`. Görev: `docs/GOREV_TRADER_SECIMI.md` (iş 1–9). Kullanıcı kararlarına ve eşiklere
dokunulmadı; yeni eşikler yalnız `copytrade/kurallar.yaml`'da.

## Yapılanlar
1. **Plasebo** (`copytrade/kapi.py`): çakışma yasağı **coin başına**. Bir coinin işlemleri rastgele sırayla, sıralı rastgele
   boşluklarla (tekdüze, ret örneklemesi yok) birbirine değmeden yerleştirilir; farklı coinler aynı anda açık olabilir.
   Coin, yön, büyüklük, süre, maliyet aynı. Süreleri toplamı pencereye sığmayan coin için o coinin dizisi bütün olarak
   dairesel kaydırılır ve `plasebo_not`'a `COIN: dairesel kaydırma` yazılır. 1000 tekrar, tek yönlü p ≤ 0,05.
   Gecikme **tarzın gecikmesi** (giriş ve çıkışa; intraday 30, swing 120 dk). Mum araması `bisect` ile (eski kod her çağrıda
   sıralıyordu).
2. **Tarz ve eşikler:** medyan elde tutma < 1 sa `scalp` (adım 3 Kaldı), 1–24 sa `intraday`, ≥ 24 sa `swing`. Scalp ayıklama:
   kısa işlem payı ≤ %25 (kısa = intraday < 15 dk, swing < 120 dk). Adım 3 net > 0 şartı tarzın gecikmesinde; stres
   gecikmesi (120 / 480 dk) yalnız raporlanır, swing'de negatifse `not = gece riskli`. Yeni sütunlar: `tarz`,
   `kisa_islem_payi`, `gecikme_480dk_net`, `katman`, `genc_aday`, `alfa_kiyas`, `kapi_gecikme_dk`, `pay_*`, `binance_payi`,
   `plasebo_not`, `plasebo_hata`, `iliskili_adresler`, `iliskili_not`, `gecmis_gun`, `account_age_days`.
3. **Katman:** `kopyalanabilir` (adım 1–7 Geçti), `izleme_adayi` (1, 2, 3 Geçti), `yok`.
4. **Alfa kıyası:** hacmin ≥ %50'si kripto → BTC; değilse işlem yapılan varlıkların eşit ağırlıklı, maruziyet eşleşmiş sepeti
   (1 saatlik mumlar, günlük kapanış getirisi).
5. **Kapsam:** shard 16 → 32; `--eksikleri-tamamla`; HTTP 5xx için 3 deneme (2 sn, 6 sn bekleme); RAPOR'da "işlenen / evren"
   (hedef ≥ %98 ✓/✗) ve huni tarz ve katmana göre ayrı.
6. **İlişkili hesap** (`copytrade/kesif.py`): `subAccounts`, `userVaultEquities` + `vaultDetails.leader`, `extraAgents`,
   `userNonFundingLedgerUpdates` (iç transfer karşı adresleri); adaylar arasında ortak API ajanı / iç transfer bağı. Yalnız işaret;
   puanı ve katmanı değiştirmez. Bir istek düşerse not `kontrol edilemedi: …` der.
7. **`kesif/kesif.json`** (şema v1): `copytrade-kapi` veri dalında; yalnız katmanı `yok` olmayanlar; sıra: katman, genç olmayan,
   `alfa_t`. `adimlar` 1–7 (adım 8 kümeleme bu görevde yok, anahtar yazılmaz).
8. **İş akışı** (`copytrade_kapi.yml`): `main` ve geliştirme dalından `copytrade/kapi/CALISTIR` yoluna push (dosyada
   `mod=hizli|eksik` satırı olabilir), elle (mod seçimi), haftalık (pazar 22:43 TSİ). Sonuçlar ve `kesif.json` yalnız
   `copytrade-kapi` veri dalına (`.github/scripts/kapi_yayimla.sh`); `main`'e yazılmaz.
9. **Worker:** cron her dakika; mesajda `[Intraday]` / `[Swing]` (`durum.json` → `traderlar[].tarz`). D1'e yalnız değişince yazılır
   (dakikalık çalışma yazma kotasını yemesin).
10. **İzleme motoru:** `tarz` izleme listesinden (isteğe bağlı alan), yoksa en son kapı sonucundan, yoksa `bilinmiyor`
    (gecikme 30 dk, bugünkü davranış). Gecikme intraday 30 / swing 120 dk; `sanal_kopya.gecikme_dk` ona göre. İzleme iş akışı kapı
    sonuçlarını `copytrade-kapi` dalından getirir. Sözleşme v1.3 notu `bilinmiyor` için güncellendi; `izleme/ornek_durum.json`'a
    `tarz` eklendi (T2 swing, gecikme 120; eğri yeniden hesaplanmadı, örnek veri).
11. **Binance karşılığı (HIP-3, iş 9):** önek atılır, takma ad tablosu `kurallar.yaml`'da (`GOLD→XAU, SILVER→XAG, BRENTOIL→BZ`),
    `USDT` eklenir, Binance sembol listesinde varsa `var`.

## Seçimler (belgede açıkça yazmayanlar)
- **Plasebo yerleştirmesi** ret örneklemesi yerine tekdüze, çakışmasız yerleştirme (aynı dağılım, hızlı, asla "yerleşemedi" demez);
  "dairesel kaydırma" yalnız coin tek başına sığmazsa. Kaydırmada pencere sonunu aşan işlem başa sarılır.
- **Eski testler değişti (zayıflatma değil, belirtim değişti):** `test_placebo_placement…` artık coinler arası değil coin başına
  çakışmasızlığı sınar; `binance_availability("xyz:SPX", {"SPXUSDT"})` artık `var` (eski: HIP-3 hepsi `yok`).
- Adım 3'te `kisa_islem_payi` hesaplanamazsa (süresi bilinen işlem yok) şartı geçirir; kapıya giren her satırda ≥ 50 kapanmış işlem
  olduğundan pratikte hesaplanır.
- `genc_aday`: `max(history_days, hesabın tüm geçmişi) ∈ [180, 365)`; hesabın tüm geçmişi `allTime.pnlHistory` uzunluğundan
  (365 günlük pencereyle kırpılmaz).
- Hızlı koşu (`--yalniz-adim5`) plaseboyu adım 3–4'e bakmadan hesaplar; satırın adım değerleri yine kurallara göredir.
- Plasebo hesaplanamazsa satırda `plasebo_hata` nedeni yazılır (ör. "yerleştirilecek kapanmış işlem yok"); adım 5 mevcut kurala
  göre `Kaldı` kalır (p yok).
- `tarz = bilinmiyor` seçimi: kapı sonucu yoksa gecikme eski değerde (30 dk) kalır; panoda/Worker'da etiket çıkmaz.
- Binance listesi Actions'tan alınamazsa (HTTP 451) `binance_payi` boş, pozisyon `binance` değeri `bilinmiyor` kalır.

## Sınırlar
- Mum penceresi 200 gün (1 saatlik mumlar, tek istekte ≤ 5000): alfa ve plasebo bu pencerede; 365 günlük alfa penceresinde BTC/sepet
  getirisi önceki 165 günde 0 sayılır (eski davranış; değiştirilmedi).
- Gecikme saat başına yuvarlanır (üst sınır); 30 dk gecikme fiilen bir sonraki saat açılışıdır.
- Adım 8 (kümeleme) ve Arbitrum köprü analizi yok; ilişkili hesap kontrolü yalnız Hyperliquid `/info` istekleri.
- Hyperliquid'e oturumdan erişim yok: koşular yalnız Actions'ta; hiçbir canlı sonuç elle yazılmadı.

## Koşular
Aşağıdaki bölüm koşular bitince doldurulur (kaynak: `copytrade-kapi` veri dalı).
