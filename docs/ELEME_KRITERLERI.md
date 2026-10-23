# Paper Trading Aday Eleme Kriterleri (v0.3)

Durum: Claude-Mod önerisi + Codex görüşü (Issue #1) + **lider/denetçi (Opus) kararları** (`tartisma/001_cevap_opus.md`). Lider ve kullanıcı onaylı (2026-10-21).
Eşikler evrensel yasa değil, kural-ı pratik (Pardo, Bailey & López de Prado, Harvey-Liu-Zhu, Davey, Carver).

## İlkeler
1. Paper = uygulama doğrulaması (sinyal paritesi, zamanlama, maliyet, operasyon). Kârlılık kanıtı değil. Giriş kapısı gevşek, canlı kapısı sıkı.
2. Eksik veri/doğrulanamama başarısızlık değildir. Durumlar ayrı: **Geçti / Koşullu / Doğrulanamaz / Reddedildi**.
3. Rapor rakamı kanıt sayılmaz; her aday bizim motorumuzda yeniden üretilir.

Uygulama ortamı (sinyal zamanı, boyut, stop, evren, veri, dönem) tüm stratejiler için ortaktır: `docs/EVRENSEL_KURALLAR.md`. Huni: aşama 0 triyaj → aşama 1 tarama (geçiş kuralı `docs/GOREV_T5.md`) → aşama 2 bu dosyadaki testler 3-10.

## Kanıt seviyeleri
A: OOS + stres testli rapor (Codex Algo 21; OOS'u seçim sonrası olduğu için fiilen "A-") · B: çok piyasalı backtest, OOS/stres yok, optimizasyon izi · C: yalnız yayıncı beyanı.

## Test sırası (pahalı testler zayıf adaylara harcanmaz)
1. **Spesifikasyon:** karar zamanı, veri, giriş fiyatı, çıkış önceliği, boyut, evren, kurumsal aksiyon, maliyet tek anlamlı yazılı. Aynı bar bilgisiyle aynı bar fiyatından dolum = otomatik hata.
2. **Veri/look-ahead:** point-in-time evren, delisted semboller, split/temettü politikası, takvim/timezone, eksik/stale bar. BIST/ABD'de survivorship kanıtı yoksa sonuç **Koşullu**.
3. **Replikasyon:** işlem sayısı ±%15, net getiri işareti aynı, PF ±%25 **veya** bizim bootstrap %90 aralığında; aynı veriyle giriş tarihlerinin >= %70'i örtüşür. Tutmazsa önce spesifikasyon farkı aranır. Kaynak işlem listesi yayımlamamışsa örtüşme ölçülemez; replikasyon yalnız metriklerle değerlendirilir ve "Geçti (metrik)" yazılır (lider kararı, `tartisma/004`).
3b. **Ön dönem tutma testi (gerçek OOS):** kurallar değiştirilmeden 2015-01-01 → 2019-12-31 (kripto 2018 →) çalıştırılır. Bu dönem rapor yazarlarınca görülmedi. Beklenen: maliyet sonrası pozitif beklenti; negatifse aday **Reddedildi** değil **Koşullu**ya düşer ve paper'da yarım ağırlık alır.
4. **Maliyet/gecikme stresi:** baz maliyet aşağıdaki tablodan; 1x, 2x, 3x komisyon+spread/slippage; +1 bar gecikme; kötü fiyat senaryosu. 2x'te PF >= 1,2, 3x'te ve +1 barda pozitif.
5. **Walk-forward:** anchored + rolling, purge/embargo; karar birleşik OOS ve pozitif dönem oranına göre (tek pencere değil). Kapı: OOS işlem >= 30 ve OOS işlem başı ortalama R > 0; WFE (OOS/IS Sharpe) raporlanır. OOS PF < 1,1 yumuşak uyarı.
6. **Parametre platosu:** 2-3 boyutlu komşuluk; komşu medyan OOS, pozitif hücre oranı, optimum sınırda mı. Kapı = plato kararlılığı.
7. **Block bootstrap Monte Carlo:** CAGR, PF, Sharpe, MDD, kayıp serisi, risk-of-ruin dağılımı; kapı alt güven sınırına dayanır, nokta tahmine değil. Beklenen MDD ~ backtest MDD x 1,5-2.
8. **DSR/PBO (canlı kapısı):** N alt sınırı: Codex Algo 44, Reddit/Voltran/Paper_Test 256 + iterasyonlar; bilinmeyen kısım için N, 2N, 5N'de raporlanır, kötümser olan esas. Kendi taramamız da deneme sayar: aşama 1'de test edilen (strateji × piyasa) çiftlerinin toplamı (~316 × 4) DSR'ın N'ine eklenir. Deneme sayısına PDF varyantları + bizim taramalarımız + reddedilenler dahil; korele varyantlar kümelenip "etkin bağımsız deneme" ayrıca raporlanır. PBO az örneklemde (60-100 işlem) sert kapı değil **uyarı**.
9. **Örneklem/anlamlılık:** >= 100 işlem (swing >= 60); t-stat > 2 yalnız canlı kapısında (çoklu test düzeltmesi DSR ile, t > 3 ayrıca aranmaz); tek enstrüman/yıla bağımlılık yok (en iyi işlem/enstrüman çıkarılınca pozitif).
10. **Aşırı uyum alarmı:** PF > 4, Sharpe > 2-3, getiri > %500 veya "hedefe ulaşana dek iterasyon" (Voltran v1→v3) → ek doğrulama zorunlu (3-8 hepsi sıkı; 3b geçilmeden paper yok).

## Piyasa betasına karşı testler (lider, ilk tarama sonrası; `tartisma/005`)
- **BIST USD bazında** test edilir (`USDTRY=X`). Karar USD sonucuna göre verilir.
- **Rastgele giriş (null model):** aynı çıkış kuralları, aynı işlem sayısı ve tutma süresiyle ≥500 rastgele giriş. Stratejinin PF'i ve ortalama R'si rastgele dağılımın %95 yüzdeliğini geçmeli; geçemiyorsa **Reddedildi (piyasa betası)**. Aşama 2'nin ilk testidir; kalan testler bunu geçenlere uygulanır.

## Baz maliyet (tek yön, komisyon + kayma; lider kararı)
| Piyasa | Baz | 2x | 3x |
|---|---|---|---|
| BIST30 | %0,15 | %0,30 | %0,45 |
| ABD hisse | %0,05 | %0,10 | %0,15 |
| Kripto (Binance spot) | %0,15 | %0,30 | %0,45 |
| Emtia ETF | %0,05 | %0,10 | %0,15 |

PDF'lerde baz maliyet yazmadığı için replikasyon bu tabloyla yapılır; fark sapma notuna yazılır.

## Kapı özeti
| Test | Paper'a giriş | Canlıya geçiş |
|---|---|---|
| 1-2 Spesifikasyon, veri | Zorunlu | Zorunlu |
| 3 Replikasyon | Zorunlu | Zorunlu |
| 3b Ön dönem tutma | Pozitif → tam; negatif → Koşullu, yarım ağırlık | Pozitif zorunlu |
| 4 Maliyet/gecikme | 2x PF >= 1,2; 3x ve +1 bar pozitif | Aynı |
| 5 Walk-forward | OOS ort. R > 0 | + WFE >= 0,5 |
| 6-7 Plato, bootstrap | Raporlanır | Plato kararlı; bootstrap %95 MDD risk bütçesinde |
| 8-9 DSR, t-stat | Raporlanır | DSR >= 0,95 (kötümser N), t > 2 |
| Paper sonucu | - | Aşağıdaki canlı kapısı |

## Day trade
Günlük OHLCV ile doğrulanamayanlar: gün içi sinyal sırası, aynı bar stop/target önceliği, gerçek spread, derinlik, kısmi dolum, seans içi likidite, açılış müzayedesi. İntraday adaylar saatlik/dakikalık veri olmadan **Doğrulanamaz** etiketi alır (reddedilmez, geçmiş de sayılmaz).

**Saatlik veri (kullanıcı kararı: ücretsiz internet kaynakları; lider doğruladı 2026-10-21):**
- BIST30, ABD, emtia ETF: yfinance `interval=1h`, yalnız son ~730 gün (bugün 2023-11 →). Kayan pencere: eski veri kaybolur, **haftalık arşivlenir**.
- Kripto: Binance `data-api.binance.vision` (api.binance.com bulut IP'lerinde coğrafi engel veriyor), 2017 →.
- 4H barlar 1H'den yeniden örneklenir; seans sınırına (BIST 10:00-18:00 TRT) hizalanır.
- Sonuç: BIST/ABD/emtia day trade adaylarında 2015-2019 ön dönem testi **yapılamaz**. Bunun yerine ilk 2 yıl IS, son ~1 yıl tutma (adaylar görülmeden ayrılır) ve gerçek OOS = paper dönemi. Bu adaylar paper'a en fazla **Koşullu** girer. Kripto day trade adayları 2018-2019 ön dönem testine tabidir.

## Short ve kaldıraç (x2/x3)
Ayrı kapı: borrow/fee, funding, short kısıtları, gap ve tasfiye/marjin riski modellenmeden long sonucu ölçeklenmez. Her varyantın ayrı OOS + stres sonucu olur. Önce long-only x1 geçmeli.

## Portföy riski
MDD üst sınırı istatistik eşiği değil **risk bütçesidir**. Portföy MDD üst sınırı **%15 (kullanıcı onayladı, 2026-10-21)**. Strateji başına sermaye, marj ve korelasyon buna göre çözülür; tek strateji MDD'sini %15'e eşitlemek yerine bootstrap %95 MDD ve portföy katkısı kapı olur. İşlem başı risk %0,5, toplam açık risk %2, paper kill-switch %10 MDD.
**Getiri hedefi (kullanıcı, 2026-10-23, `tartisma/012_ozet_karar.md`):** portföy için yılda %20-30 net, MDD ≤ %15. Tek strateji değil, düşük korelasyonlu 6-8 stratejilik sepet hedeflenir.

## Altyapı (Codex önerisi)
Tarama/plato için VectorBT/Numba; nihai doğrulama ve paper paritesi için aynı emir kurallarını kullanan küçük event-driven referans motor. Sabit çıktı şeması: IS/OOS ayrımı, deneme sayısı, maliyet senaryoları, güven aralıkları, veri kusurları, yeniden üretim hash'i.

## Canlıya geçiş kapısı (paper sonrası)
>= 3 ay ve >= 30 işlem, paper sonucu backtest beklentisinin güven aralığında, gerçek kayma varsayımı aşmıyor, portföyde düşük korelasyon, kaldıraç x1 → x2 → x3 kademeli.

## Kullanıcı kararları
- ~~Portföy MDD %15~~: onaylandı.
- ~~Saatlik veri kaynağı~~: ücretsiz internet kaynakları (yukarıda).

## Görev olarak açılanlar
- Sol 6.1: T1a kod incelemesi (look-ahead/survivorship korumaları dahil), T3.
