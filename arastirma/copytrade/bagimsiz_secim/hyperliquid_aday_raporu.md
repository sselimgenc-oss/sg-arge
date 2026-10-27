# Hyperliquid elle-kopya aday analizi — bağımsız ikinci görüş (2026-10-27)

**Tarama kapsamı (2 satır):** Kapının ürettiği `sonuc.csv` (12.461 leaderboard adresinin 8.196 satırı) üzerinde tüm metrikler tarafımca yeniden hesaplandı; A/B adayları için 23+ adreste Hyperliquid API (`userFillsByTime`, `portfolio`, `clearinghouseState`) ile son 90–365 günlük piyasa payı, işlem ve form doğrulaması yapıldı. Plasebo (adım 5) CSV'de hiç hesaplanmamış olduğundan **tüm adaylar "plasebo doğrulanamadı"** statüsündedir; birkaç hücre API rate-limit nedeniyle "bilinmiyor" olarak bırakıldı.

**Öncül:** Yatırım tavsiyesi değildir; aday analizi ve izleme önerisidir. 8.196 satırın 7.771'i hiç kapanmış işlemi olmayan vault/dolum-yok satır — direkt elendi. Adım 1'i geçen 398 hesabın 107'si scalp-form (medyan tutma <1 sa), 8'i vault-form; bunlar da listelenmedi. Adım 2 → 191 hesap, adım 3 → 57, adım 4 → 62, adım 6 (alfa ham t-testi; plasebo çıkarıldı) → 41.

### Son 90 gün form doğrulaması (portfolio API, "day" serisinden — hepsi bu turda doğrulandı)

| Adres (kısa) | 90 gün hesap getiri | 90 gün kapalı PnL | Not |
|---|---|---|---|
| 0x79bf662b… | **-1,53%** | -2.019 USD | A listesi zirvesi ama son 90 gün **negatif** — getiri geçmiş dönemlerden |
| 0x3f96c4df… | %0,00 | 0 USD | 187 doluma rağmen sıfır net — lot küçük ya da kenarda |
| 0xb3162ca4… | +%0,66 | +311 USD | |
| 0x09d70eac… | **+%3,53** | +4.186 USD | Doğrulanan grupta en iyi 90g form |
| 0x378defc3… | %0,00 | 0 USD | ~7,5K dolum/90g + sıfır net → HFT/algo görünümlü |
| 0x9312e0a6… | +%1,82 | +2.539 USD | |
| 0x8bae3527… | +%0,99 | +40.517 USD | 4,1M hesapta ~%1; mutlak kâr büyük, oran sıradan |
| 0x4ba1d152… | +%0,50 | +689 USD | |
| 0x29754d7a… | +%1,71 | +22.906 USD | |
| 0x19e90c53… | %0,00 | 0 USD | 90 günde tam sıfır → C listesindeki en zayıf form |
| 0x3ea004bb… | +%0,33 | +418 USD | |
| 0x3e680500… | bilinmiyor | bilinmiyor | 90g dolum 2.047 (doğrulandı), form serisi çekilemedi |

**Genel bulgu:** 12 aylık metriklerde parlayan adayların 90 günlük formları yekûnda yatay (-%1,5…+%3,5). "Kopyalanacak sıcak performans" gözüyle bakılırsa bu liste sıcak değil; "isabetli, düşük riskli rejim" gözüyle bakılırsa normal. İzleme kararında 90g sütunu 12Ay sütunundan ağır basmalı.

---

## A) Kapı hesabıyla en iyi adaylar

Kapının sonucunda "adım 2–4 hepsi Geçti" koşulunu taşıyan yalnızca **9 hesap** var (5 intraday, 4 swing); 10. tam geçen yok. Bu yüzden A listeleri üç katmanla dolduruldu: **A** = 1–6 tam geçenler, **A (iz)** = 1–4 geçip adım 6 eşiğini aşamayanlar, **A+ (iz)** = 1–3 geçip adım 4'te kıl payı tek/birkaç ölçütle elenenler. Her satırda hangi adımda kaldığı ayrı kolonda okunur.

### A — INTRADAY en iyi 10

| adres | liste | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net | kârlı ay | en büyük işlem | piyasa payı | hangi adımı geçemedi | neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x79bf662bb50bea267adf5499f730d2488d85411f | A | INTRADAY | 365 | 133 | 14,5 | 0,63x | +10,7% | 77% | 8% | emtia %56 / kripto %43 / endeks %1 | — | Adım 1–6 tam geçti; hariç-PF 1,84, nw_t 2,89, 30 dk gecikmeli kopya net +10,7%; son 90 günde 1.074 dolum (doğrulandı). | Son 90 gün **-1,53%** (-2.019 USD) — alfa şu an dinleniyor; kâr BTC + xyz:CL (petrol) karışımından, emtia rejimi kırılırsa zayıflar. |
| 0x3f96c4df1e76902985d3dbd979af54b487f29671 | A | INTRADAY | 365 | 76 | 5,5 | 0,50x | +16,0% | 83% | 18% | kripto %94 / hisse %5 / emtia %1 | — | Adım 1–6 tam geçti; hariç-PF 6,81, medLev 0,50x, gecikmeli kopya +16,0%. | Son 90 gün net **0 USD** (187 dolum) — pozisyon boyutu küçülmüş olabilir; notional ~%62 HYPE + %19 PUMP tek-jeton bağımlılığı. |
| 0xb3162ca43d7455be5b4f6dbf3236435b709ed894 | A (iz) | INTRADAY | 355 | 219 | 4,0 | 1,87x | +36,7% | 77% | 16% | kripto %71 / endeks %11 / hisse %14 | adım6 (nw_t 1,25) | Adım 1–4 geçti; 219 işlem, medyan 4,0 sa, gecikmeli kopya +36,7%; 90g form +%0,66 (doğrulandı). | Alfa t=1,25 — istatistiksel dayanak zayıf; hariç-PF 1,49 orta. |
| 0x09d70eac3bbebf727218b81b7f6384249826ab24 | A (iz) | INTRADAY | 187 | 69 | 2,4 | 1,53x | +31,2% | 86% | 18% | kripto %100 | adım6 (nw_t 1,93) | Adım 1–4 geçti; %100 BTC tek kol, medLev 1,53x, gecikmeli kopya +31,2%; 180 günde 2.484 dolum. | Geçmiş sadece 187 gün; BTC yana seyirde alfa zayıflayabilir. |
| 0x3ea004bbb1004936e526bf97cbd796f0c78273d7 | A (iz) | INTRADAY | 365 | 665 | 1,2 | 0,21x | +12,6% | 85% | 4% | kripto %100 | adım6 (nw_t 1,34) | Adım 1–4 geçti; medyan 1,2 sa, LTS %4, 665 kapanmış işlem; gecikmeli kopya +12,6%; 90g güncel dolumları ~2.9K (aday taraması). Ulcer 0,0357 sınırda. | Notional ~%90 HYPE; işlem frekansı (665/365g) manuel kopya için üst sınırda. |
| 0xe5731d975d84c7222ebfd0ce8239f04ea3164e55 | A+ (iz) | INTRADAY | 227 | 50 | 19,6 | 2,02x | +70,3% | 100% | 29% | hisse %100 | adım4: martingale işareti | Adım 1–3 temiz; sortino 14,7, kârlı ay %100, gecikmeli kopya +70,3%, nw_t 3,12 — martingale olmasa en güçlü intraday. | 50 işlemde 688 ekleme (poz. başına ~14): zarara ekleme ağırlıklı; bu risk profili manuel kopyaya birebir taşınmaz. |
| 0x3d5f1ad033c4e7c6a6d433d50d694c488dcaebcf | A+ (iz) | INTRADAY | 365 | 402 | 20,5 | 0,71x | +71,7% | 62% | 24% | kripto %98 / hisse %2 | adım4: martingale işareti | Adım 1–3 temiz; 402 işlem, LTS %24, gecikmeli kopya +71,7%. | 1.215 ekleme (poz. ~3); sortino 1,4 ve nw_t 1,06 — kalıcılık kanıtı zayıf. |
| 0x149d35ed0e25ec4b760c28055f744fdd02af1764 | A+ (iz) | INTRADAY | 301 | 64 | 23,6 | 0,77x | +44,8% | 73% | 20% | kripto %100 | adım4: martingale işareti | Adım 1–3 temiz; LTS %20, nw_t 1,92, gecikmeli kopya +44,8%; ETH+BTC dengeli. | 119 ekleme (poz. ~2, hafif); 301 gün geçmiş. |
| 0x1404109f8cd4a79a0447365edbb7a13acd0b2f27 | A+ (iz) | INTRADAY | 365 | 417 | 11,0 | 1,53x | +22,1% | 92% | 5% | kripto %78 / hisse %22 | adım4: martingale işareti | Adım 1–3 temiz; 417 işlem, LTS %5, kârlı ay %92, nw_t 2,31, gecikmeli kopya +22,1%. | 1.843 ekleme (poz. ~4,4); dolum frekansı çok yüksek (~8K dolum/365g). |
| 0x378defc39d5dcdfbecd4f1673a5e228f992fc08e | A+ (iz) | INTRADAY | 365 | 92 | 3,0 | 1,74x | +31,9% | 69% | 36% | hisse %48 / emtia %26 / endeks %13 / kripto %11 / döviz %4 | adım4: en büyük işlem %36 | Adım 1–3 temiz; sortino 7,7, calmar 56, nw_t 2,23, gecikmeli kopya +31,9%. | En büyük işlem kârın %36'sı — tek vuruş bağımlı; ~7,5K dolum/90g + son 90 gün net 0 USD → HFT/algo görünümlü. |

### A — SWING en iyi 10

| adres | liste | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net | kârlı ay | en büyük işlem | piyasa payı | hangi adımı geçemedi | neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x8bae3527e5a33fa0cf184f37bc112d071463ab6d | A | SWING | 365 | 155 | 81,0 | 1,45x | +25,2% | 100% | 11% | kripto %74 / emtia %17 / hisse %9 | — | Adım 1–6 tam geçti; kârlı ay %100, hariç-PF 7,15, Ulcer 0,004; gecikmeli kopya +25,2%, 12m +251%; 90g pnl +40,5K USD (doğrulandı). | 90g penceresindeki dolumlar 2026 Ağustos başındaki 3 günlük patlamaya sıkışmış — algoritmik ölçek görünümlü; 4,1M hesapta 90g oran sadece +%0,99. |
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | A | SWING | 365 | 86 | 48,1 | 1,04x | +36,2% | 85% | 16% | hisse %52 / emtia %34 / endeks %11 / kripto %3 | — | Adım 1–6 tam geçti; HIP-3 ağırlıklı (emtia+hisse ~%70), nw_t 2,78; son 90 günde 2.047 dolum (API pagination ile doğrulandı), açık pozisyon yok. | 90g getiri/pnl serisi çekilemedi (rate limit); Brent+CL petrol kolu tek rejime dikilmiş; HIP-3 likidite riski. |
| 0x69b05701f8175c276ecd0138387a197948e240bb | A | SWING | 365 | 88 | 65,9 | 0,59x | +6,3% | 77% | 18% | kripto %100 | — | Adım 1–6 tam geçti; medLev 0,59x, hariç-PF 2,49. | Gecikmeli kopya getirisi düşük (+%6,3); BTC %64 + HYPE %23; son 90g formu doğrulanamadı. |
| 0x29754d7a9f9f344327158e2d01508efa415bd558 | A (iz) | SWING | 365 | 71 | 43,3 | 0,13x | +4,5% | 62% | 28% | kripto %90 / endeks %6 / hisse %4 | adım5 (plasebo) + adım6 | Adım 1–4 geçti; medLev 0,13x, LTS %28, gecikmeli kopya +4,5%; 90g pnl +22,9K USD (doğrulandı). | Plasebo/alfa doğrulanamadı; LTS %30 sınırında; kârlı ay %62. |
| 0x9312e0a61f21affbd5be821f436f8fdf6b6f6663 | A+ (iz) | SWING | 285 | 64 | 125,2 | 1,86x | +125,5% | 100% | 16% | kripto %39 / emtia %34 / hisse %27 | adım4: martingale işareti | Adım 1–3 temiz; gecikmeli kopya +125,5%, sortino 62,8, calmar 148 — havuzun en gövde performansı; 90g +%1,82 (doğrulandı). | 293 ekleme (poz. başına 4,6): mg ağırlıklı; 64 işlem sınırlı kapsam. |
| 0x4ba1d152409f43ad92ba358886fe94bae4f5f656 | A+ (iz) | SWING | 365 | 169 | 112,5 | 0,66x | +17,1% | 92% | 10% | kripto %82 / hisse %11 / emtia %7 | adım4: martingale işareti | Adım 1–3 temiz; kârlı ay %92, drawdown %8 (en düşük), sortino 9,4; ~1.925 dolum/180g (aday taraması). | 1.116 ekleme (poz. 6,6); nw_t 0,63; 90g sadece +%0,50. |
| 0x398433dd94502cb28814d145a4fb8e98deba601b | A+ (iz) | SWING | 365 | 155 | 51,4 | 0,89x | +14,4% | 77% | 11% | endeks %57 / kripto %41 / hisse %1 / emtia %1 | adım4: martingale işareti | Adım 1–3 temiz; xyz:SP500 ağırlıklı (%57 HIP-3 endeks), nw_t 2,53, gecikmeli kopya +14,4%; 90g dolum 164 (API pagination ile doğrulandı), hâlâ açık pozisyon var. | Aylık dolum eğrisi çöktü: May–Tem ~(1,2K, 1,2K, 233) → Eyl 5 dolum; 469 ekleme (poz. 3). |
| 0x4a20846b02da5a2f3174441036d8428b44ee95be | A+ (iz) | SWING | 236 | 142 | 59,8 | 0,10x | +6,0% | 62% | 21% | kripto %49 / endeks %30 / hisse %21 | adım4: martingale işareti | Adım 1–3 temiz; SP500/XYZ100 endeks dağılımı, sortino 7,5; 90g dolum 1.135 (API pagination ile doğrulandı) — Eyl ayında 729 dolumla hızlanmış. | 1.021 ekleme (poz. 7,2); kârlı ay %62 sınırda. |
| 0x353bd2e5da5f01707dfad0dd86907561ac66cc38 | A+ (iz) | SWING | 365 | 99 | 29,8 | 0,85x | +13,7% | 46% | 22% | bilinmiyor | adım4: kârlı ay %46 | Adım 1–3 temiz; 365g/99 işlem, medLev 0,85x, drawdown %10, sortino 3,0. | Kârlı ay %46 — süreklilik eşiğinin altı; nw_t 1,57 orta; son 90 gün dolum bilgisi bilinmiyor. |
| 0xd70c9e61ba506a8cf1c25b54d14b25abdc048fd4 | A+ (iz) | SWING | 365 | 95 | 29,2 | 0,49x | +4,2% | 92% | 32% | kripto %62 / hisse %38 | adım4: en büyük işlem %32 + martingale | Adım 1–3 temiz; kârlı ay %92, sortino 13,0, drawdown %19. | En büyük işlem kârın %32'si; mg_add 174 (poz. 1,8 — hafif). |

**Çarpan eleme notu:** Adım 1'i geçip listelenmeyenler: scalp-form 107 + vault-form 8 (tümü işletme/algo varsayımıyla dışarıda), ayrıca max_drawdown > %1000 çıkan 268 satır veri hatası sayıldı. `cash:`/`@N` yoğun, vault/CD görünümlü iki hesap (0x9d1ec161…, 0x5b92f1d8…) algoritmik ölçek karakteriyle elendi.

---

## B) Kıl payı elenenler (adım 1–2 geçip tek ölçütle, eşiğe yakın)

Sonuç: **Tek ölçütle, eşiğe yakın elenen yalnızca 4 hesap** bulunabildi (aşağıda B). "Kısa işlem payı" verisi CSV'de paylaşılmadığından o ölçütle elenenlerin sayısı ve kaçının tek ölçüt olduğu bağımsız doğrulanamadı — bu, kapı adım 3'ün en büyük bilinmezi. 2 ölçütlü ama tek ölçüte çok yakın 2 hesap da örnek olduğu için ayrı satırda verildi:

| adres | liste | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net | kârlı ay | en büyük işlem | piyasa payı | hangi adımı geçemedi | neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x885989fd94d30c150e6eaf897090509bce4f6aa8 | B | INTRADAY | 365 | 81 | 5,6 | 0,58x | +13,6% | 58% | 16% | kripto %80 / endeks %16 / emtia %3 / hisse %2 | adım4: kârlı ay %58 | Tek ölçüt: kârlı ay %58 — eşiğe 2 puan; hariç-PF 2,10, drawdown yalnızca %0,8. | nw_t 1,98 — alfa eşiğinin hemen altında. |
| 0x51b62b4bf8df6f2795b3da30cb46aa47f9f230a8 | B | SWING | 365 | 172 | 105,0 | 0,62x | +2,3% | 54% | 10% | kripto %100 | adım4: kârlı ay %54 | Tek ölçüt: kârlı ay %54; medLev 0,62x, LTS %10, 172 işlem; medyan 105 sa. | nw_t ~1,0; gecikmeli kopya getirisi %2,3 — marjinal. |
| 0x7697ffcb42e82f9980cec5b15664c992c6b8c021 | B | SWING | 365 | 97 | 26,1 | 0,56x | +1,4% | 62% | 16% | hisse %72 / emtia %18 / kripto %10 | adım4: hariç-PF 1,00 | Tek ölçüt: hariç-PF 1,00 — kârın ezası en iyi işlemden; kârlı ay %62, medLev 0,56x. | Getiri çok az ve alfa bağımsızlığı yok; izleme listesinin son sırası. |
| 0x353bd2e5da5f01707dfad0dd86907561ac66cc38 | B | SWING | 365 | 99 | 29,8 | 0,85x | +13,7% | 46% | 22% | bilinmiyor | adım4: kârlı ay %46 | Tek ölçüt: kârlı ay %46; medLev 0,85x, hariç-PF 1,79, drawdown %10. | Süreklilik zayıf; son 90 gün formu bilinmiyor. |
| 0x909eb3d5ff0ac0df12c81f8495860cfccf1e7ea9 | B (2 ölçüt) | SWING | 313 | 60 | 44,6 | 1,24x | +24,4% | 82% | 32% | bilinmiyor | adım4: en büyük işlem %32 + martingale | LTS %32 eşiğe 2 puan uzak; hariç-PF 1,77, kârlı ay %82, sortino 5,3. | mg ekleme sinyali eşlik ediyor — ciddi risk. |
| 0x4c968a3a530f76f655e7e7010075aa63cec87de2 | B (2 ölçüt) | SWING | 201 | 64 | 25,3 | 3,91x | +46,8% | 100% | 10% | bilinmiyor | adım3: medLev 3,91x + martingale | medLev 3,9x — eşiğe 0,9x uzak; kârlı ay %100, hariç-PF 63,9, nw_t 5,35, 12m +58% — metrikler mükemmel. | mg işareti + kaldıraç riski; 201 gün kısa geçmiş, tek-rejim olma ihtimali yüksek. |

**Neden izlenmeye değerler:** kârlı ay eşiğini 2–15 puan farkla geçen ama düşük drawdown (%0,8–10) ve sağlıklı en büyük işlem payına (%10–22) sahip, kırılma ihtimali düşük görünen hesaplar. 3 aylık sanal izleme, koşulu gerçekten doğrulayıp pozisyon boyu dağılımını test edecektir.

---

## C) Kendi varyasyonum

**Gerekçe (tek cümle):** Kapı 12 aylık pencerede kârlı ay oranını %60'a sabitlediği için düşüşleri derinden yönetip az sayıda kârlı ayyla yürüyen (Sortino/Calmar/Ulcer mükemmel) hesapları atıyor ve son 90 günlük aktifliği hiç ölçmediği için aylar önce durmuş hesapları içeri alabiliyor.

**Kurallarım:**
- **K1 — Düşüş/istisna dayanıklılığı:** Sortino ≥ 2, Calmar ≥ 3, Ulcer index ≤ 0,035, en büyük işlem payı ≤ %25, martingale işareti temiz.
- **K2 — Son 90 gün form:** son 90 günde ≥ 10 dolum (API doğrulaması); varsa pozitif 90g PnL.

**Sonuç:** Kurallar, adım 1–3'ü geçmiş 57 hesaplık havuzda **9 hesap** bırakıyor — 10. yok: havuzda kalan tüm güçlü adaylar (0x4c921317…, 0x9312e0a6…, 0x4ba1d152…, 0xd70c9e61…, 0x080c3c74…) martingale işareti taşıyıp K1'i düşürüyor; bunları zorla listeye katmak doğruluğu bozar, bu yüzden boşluk bilinçli bırakıldı.

| adres | liste | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net | kârlı ay | en büyük işlem | piyasa payı | hangi adımı geçemedi | neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x19e90c5331a747661bdd2887a6f6156a1eda2ef9 | C | INTRADAY | 264 | 241 | 23,3 | 0,81x | +32,9% | 43% | 11% | kripto %100 | adım4: kârlı ay %43 | C-kuralına en uygun: sortino 5,1, calmar 18,3, Ulcer 0,008; ~1.5K dolum/180g (aday taraması). | Son 90g PnL tam **0 USD** — form durmuş olabilir; nw_t 1,26 (adım6 geçemedi); kârlı ay %43 düşük. Vade başında mutlaka canlılık kontrolü. |
| 0x378defc39d5dcdfbecd4f1673a5e228f992fc08e | C | INTRADAY | 365 | 92 | 3,0 | 1,74x | +31,9% | 69% | 36% | hisse %48 / emtia %26 / endeks %13 / kripto %11 / döviz %4 | adım4: en büyük işlem %36 | C-kuralı: sortino 7,7, calmar 56, Ulcer 0,002; 90g ~7,5K dolum — son derece aktif. | LTS %36 (istisnayla alındı); son 90g PnL **0 USD** + HFT frekansı → algoritmik, elle izlenmesi zor. |
| 0x3f96c4df1e76902985d3dbd979af54b487f29671 | C | INTRADAY | 365 | 76 | 5,5 | 0,50x | +16,0% | 83% | 18% | kripto %94 / hisse %5 / emtia %1 | — | C-kuralı: sortino 4,3, calmar 8,9, Ulcer 0,016; A listesinde de. | Son 90g PnL 0 USD; HYPE ağırlığı. |
| 0xb3162ca43d7455be5b4f6dbf3236435b709ed894 | C | INTRADAY | 355 | 219 | 4,0 | 1,87x | +36,7% | 77% | 16% | kripto %70 / endeks %11 / hisse %14 | adım6 (nw_t 1,25) | C-kuralı: sortino 2,4, calmar 10,1, Ulcer 0,031; 90g +%0,66 (doğrulandı). | nw_t 1,25. |
| 0x09d70eac3bbebf727218b81b7f6384249826ab24 | C | INTRADAY | 187 | 69 | 2,4 | 1,53x | +31,2% | 86% | 18% | kripto %100 | adım6 (nw_t 1,93) | C-kuralı: sortino 2,15, calmar 6,8, Ulcer 0,018; BTC %100 tek kol; 90g **+%3,53** — doğrulanan grupta en iyi. | 187 gün kısa geçmiş. |
| 0x79bf662bb50bea267adf5499f730d2488d85411f | C | INTRADAY | 365 | 133 | 14,5 | 0,63x | +10,7% | 77% | 8% | emtia %56 / kripto %43 / endeks %1 | — | C-kuralı: sortino 2,59, calmar 5,9, Ulcer 0,015; 90g dolum 1.074 (doğrulandı). | Son 90g **-%1,53**; kârın büyük payı xyz:CL. |
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | C | SWING | 365 | 86 | 48,1 | 1,04x | +36,2% | 85% | 16% | hisse %52 / emtia %34 / endeks %11 / kripto %3 | — | C-kuralı: sortino 7,3, calmar 13,6, Ulcer 0,013; 90g dolum 2.047 (doğrulandı). | 90g getiri serisi bilinmiyor; HIP-3 emtia kolu. |
| 0x29754d7a9f9f344327158e2d01508efa415bd558 | C | SWING | 365 | 71 | 43,3 | 0,13x | +4,5% | 62% | 28% | kripto %90 / endeks %6 / hisse %4 | adım5 (plasebo) + adım6 | C-kuralı: sortino 3,0, calmar 6,5, Ulcer 0,007; 90g pnl +22,9K (doğrulandı). | Plasebo doğrulanamadı; LTS %28. |
| 0x3ea004bbb1004936e526bf97cbd796f0c78273d7 | C | INTRADAY | 365 | 665 | 1,2 | 0,21x | +12,6% | 85% | 4% | kripto %100 | adım6 (nw_t 1,34) | C-kuralı sınır: Ulcer 0,0357 eşiğin az üstünde; LTS %4. | HYPE %90 tek-kol; 90g sadece +%0,33. |

---

## D) Kapının kör noktaları (elle kopya için)

1. **Plasebo mantığı çalışmıyor.** Kapının plasebo (adım 5) kolonu yayınlanan CSV'de hiç hesaplanmamış; "kopyalanabilir" katmanı bugün boşta. Plasebo düzeltilene kadar hiçbir aday "doğrulanmış kopyalanabilir" sayılmaz — her şey izleme listesi statüsünde.

2. **Son 90 gün aktiflik ve form hiç ölçülmüyor.** Kapı 12 ay getiri + kârlı ay ile sıralıyor; oysa bu turda portfolio API ile doğruladığımız 90g formlar -%1,5 ile +%3,5 arasında yatay kaldı ve bir aday (0x19e90c53) 90 günde tam 0 USD kapattı. Kapıya "son 30/90 gün ≥ N dolum + 90g PnL > 0" eşiği eklenmeli; aksi halde çoktan durmuş hesaplar listeye giriyor.

3. **Gecikmeli simülasyon, kullanıcı gerçekliğine uymuyor.** Kapı tek tip gecikme senaryosu koşturuyor; kullanıcı 15 dk–8 saat arası gerçek gecikmeyle ve kendine özgü emir boyuyla giriyor. 30 dk gecikme ↔ medyan tutma süresi oranı düşük hesaplarda (ör. medyan 1,2 sa olan 0x3ea004bb) kopya getirisinin erozyonu simülasyondan büyük çıkar. Kapı, "tutma süresi / gecikme" oranına göre uyarı vermeli.

4. **Vault ve hesap geçişleri görünmez.** Leaderboard satırı ile gerçek hesap sahibi arasındaki yapı (subAccounts, extraAgents, vault katılımları) sorgulanmadığından görünen performansın gerçekte kimin/kimlerin birden fazla stratejisinin toplaması olduğu bilinmiyor; kopyacı aynı riski katlanmış olabilir.

5. **Piyasa/likidite derinliği ölçülmüyor.** En büyük işlem payı korunuyor ama notional'ın tek piyasa ya da ince HIP-3 kolunda (%x) toplanması ölçülmüyor: 0x3e6805e8 toplamın ~%34'ünü Brent/CL taşır; 0x3ea004bb ~%90 HYPE. İnce piyasada kopya giriş/çıkış kayması, kapının gördüğü getiriyi yakalayamaz.

---

## En güçlü 5 aday — özet

1. **0x79bf662bb50bea267adf5499f730d2488d85411f** — tüm adımları (1–6) geçen tek intraday; %56 xyz:CL + BTC karışımı, 365g/133 işlem, nw_t 2,89, 90g dolum 1.074 (doğrulandı). **Ama son 90 gün -%1,53** — izlemeye "alfa dinleniyor" notuyla başlanmalı.
2. **0x09d70eac3bbebf727218b81b7f6384249826ab24** — doğrulanmış grupta en iyi 90g form (+%3,53, +4.186 USD); %100 BTC tek kol. Dezavantaj: geçmiş yalnız 187 gün.
3. **0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9** — tüm adımları geçmiş swing; HIP-3 hisse+emtia ~%85+, 90g dolum 2.047 (doğrulandı), açık pozisyon yok. 90g getiri serisi bilinmiyor — ilk kontrol edilecek madde.
4. **0x8bae3527e5a33fa0cf184f37bc112d071463ab6d** — tüm adımları geçmiş swing; kârlı ay %100, hariç-PF 7,15, 90g pnl +40,5K USD. **Ancak** dolumların 90g penceresi Ağustos başındaki 3 günlük patlamaya sıkışmış → algoritmik olup olmadığı izlemede netleşecek.
5. **0x3f96c4df1e76902985d3dbd979af54b487f29671** — tüm adımları geçmiş intraday; medLev 0,50x, hariç-PF 6,81. **Ancak** son 90g net 0 USD — pozisyon boyutunun küçülüp küçülmediği izleme başında kontrol edilmeli.

**Sonuç cümlesi:** 90g form doğrulaması, kapının 12 aylık sıralamasıyla çelişki çıkardı; izleme ilk 3'ü benim önerimle **0x09d70eac (90g form), 0x79bf662b (yapı), 0x3e6805e8 (çeşitlilik)** olur; 0x8bae3527 ve 0x3f96c4df "şüphe çözülene kadar pasif izleme" statüsünde kalır.

*Rapor yalnızca bağımsız analiz içerir; yatırım tavsiyesi değildir. "3 aylık sanal izleme" ön listesi: (1) 0x09d70eac, (2) 0x79bf662b, (3) 0x3e6805e8, (4) 0x8bae3527 (pasif), (5) 0x3f96c4df (pasif) — 90 günün sonunda her adayın canlı PnL'i bu rapordaki 90g sütunuyla kıyaslanır.*
