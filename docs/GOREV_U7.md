# U7: Bütün test edilebilir stratejiler, bugüne kadar

**Karar:** kullanıcı, 2026-10-24: "Kilitli mitli yapma, hepsini bugüne kadar koştur. 400 küsür neyse hepsini o kilitli dediğin yerde koştur ve işimize yarayanları alalım."
**Sahip:** Codex (koşu), lider (denetim ve rapor).

## 1. Kilit kaldırıldı
- `engine/kilit.py`: kilitli dönem kaldırılır. Bütün koşucular veriyi **son kapanmış bara kadar** kullanır. `KILIT_AC` artık gerekmez.
- `backtests/u6_kilit.py` ve "en çok 5 aday kilitli dönemde" adımı (`docs/GOREV_U6.md` bölüm 1-2 ve 4) iptal. U6'nın resmî koşusu U7'nin içinde yapılır.

## 2. Kapsam: test edilebilir her kart
| Grup | Kart | Koşucu |
|---|---:|---|
| Faz 1 (`spec_durumu: tam`, U1/U4/TV dışı) | 126 | `tarama.py` → `asama2a.py` → `asama2b.py` (+ PIT evren) |
| U1 (kripto gün içi) | 3 kart, 14 varyant | `u1.py` + `u1_huni.py` |
| U4 | 4 kart, 16 varyant | `u4.py` + `u4_huni.py` |
| U6 (TradingView, `tam`) | 74 | `u6.py` + `u6_huni.py` |

Her kart, kendi grubunun mevcut piyasa/zaman dilimi kurallarıyla koşar (Faz 1 kartları uyumlu bütün piyasalarda, U4/U6 kendi kolunda). Kart ve parametre değişmez.

**Test edilemeyenler** (çevrilemeyen, gizli kaynak, ihtiyari, yalnız short, kapsam dışı) koşulmaz. Tek istisna: Faz 1'de `dakikalik` (62 kart). Codex bunların piyasasına bakar. Kripto ise Binance 1m/5m verisiyle koşulabilir; listesini çıkarır, koşulabilenleri U7'ye ekler, kalanları nedeniyle yazar.

## 3. Dönemler
- **Faz 1 kartları:** Faz 1 düzeni. IS 2020-01-01 → 2024-09-30, OOS 2024-10-01 → **son kapanmış bar**, ön dönem 2015-2019. yfinance 1H piyasalarında mevcut kural (ilk 2/3 IS, kalan OOS).
- **U1 / U4 / U6:** IS 2018-01-01 → 2022-12-31, OOS 2023-01-01 → **son kapanmış bar**, ABD/emtia ön dönem 2015-2017.

## 4. Eleme (değişmez)
Mevcut huni aynen: Aşama 1, rastgele giriş testi (2a), OOS + maliyet stresi + gecikme + bootstrap MDD95 ≤ %15 + DSR (2b), kripto kardeş ölçütü, Koşullu şerhleri.
**DSR deneme sayısı N = U7'de koşulan toplam varyant sayısı** (bütün gruplar birlikte). Çok sayıda strateji denendiğinde şansla iyi görünenleri ayıklayan kapı budur; çıta buna göre yükselir.

## 5. Çıktı
- `results/u7/huni_ozet.csv`: her varyant için tek satır (grup, kart, piyasa, tf, kapı değerleri, karar, neden).
- `results/U7_SONUC.md` (lider): Geçti ve Koşullu listesi, eski sonuca göre değişenler, portföy önerisi.
- Paper'a alma kararı kullanıcınındır.

## 6. Codex iş sırası
1. `kilit.py` kaldırma + testlerin güncellenmesi (ayrı küçük PR `[U7] kilit kaldırıldı`).
2. Koşu: önce U4 + U1 (kısa), sonra U6, sonra Faz 1 (uzun). Her grup bitince `huni_ozet.csv`'ye eklenir. DSR'ler en sonda toplam N ile yeniden hesaplanır.
3. `dakikalik` listesi (bölüm 2).
4. İşlem dökümleri commit edilmez.
5. PR `[U7] tüm stratejiler bugüne kadar`. Açıklamada grup başına varyant sayısı, toplam N, süre.

## 7. Lider
Her gruptan 1 varyantı bağımsız tekrar koşar. `U7_SONUC.md`'yi yazar.

## Ek 1 (lider, 2026-10-24): U6'da piyasa/veri yüzünden atlanan 49 TradingView kartı
Kullanıcı kararı ("hepsini test et") gereği U6'nın "kol sınıfı değiştirilmez" kuralı U7'de gevşetilir. Kural ve parametreler yine değişmez; yalnız kol eşlenir:
- FX yayın sembolü → `FX8` (Faz 1 FX arşivi); BIST → `BIST30`;
- diğer borsalardaki hisse/endeks (NSE, ASX, TSE, XETR, MYX, BCBA, EUREX) → `ABD25` (PIT);
- ABD/emtia/FX 4H → yfinance 1H'den 4H, Faz 1 yfinance 1H dönem kuralı (ilk 2/3 IS, kalan OOS).
Çeviri Sonnet'te (`[U7] piyasa/veri kartları`), koşu Codex'te. Verisi bulunamayan kol `Doğrulanamaz (veri)` olarak kalır.

## Ek 2 (lider, 2026-10-24): OOS bitişi
`u1.py`, `u4.py`, `u6.py` ve Faz 1 koşucularındaki OOS bitiş tarihleri (2025-09-30 vb.) U7 koşusunda **son kapanmış bara** uzatılır. Bu, U7 koşu PR'ının parçasıdır.
