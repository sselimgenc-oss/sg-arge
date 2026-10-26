# Faz 1 kripto ayağı — lider + Sol 6.1 ortak çalışma (kullanıcı: "kripto 3 az")

## Lider tespiti
- Aday havuzu (ikimizin kalsın/bekleme dediği kripto): 12 KRIPTO25 sepet stratejisi + ETHBTC 6s (wcegMOXj) + ETH 1s (3UcIwSrE, PF 1,08) + beklemede 3 TV-2 (QCkIgf3z ETH 15dk, BR74LOKo / zuEOEYPK BTC perp).
- **Sepet stratejileri birbirine çok benziyor:** 2023→ günlük getiri korelasyonu çoğunlukla 0,55–0,80. Hepsi aynı 25 coinde trend/momentum; kripto düşüşünde birlikte kaybederler. Daha çok sepet kitabı = daha çok kural çeşitliliği, ama **aynı piyasa riski**.
- Gerçek çeşitlendirenler: wcegMOXj (ETHBTC; sepetlerle ~0), 3UcIwSrE (~0), beklemedeki tek-coin TV-2'ler (mutabakattan sonra).

| Kimlik | TF | İşlem | Etkin hafta | Yıllık % | p10 % | PF | PF 3x | En iyi ay hariç PF | Gecikme neti | MDD % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| wcegMOXj (ETHBTC) | 6s | 257 | 169 | 14,4 | 0,118 | 2,19 | – | – | – | 1,1 |
| TV-71yKm18B | 4s | 226 | 110 | 13,5 | 0,098 | 1,99 | 1,57 | 1,79 | 0,54 | 11,1 |
| TV-3BXWqwnF | 1G | 94 | 50 | 12,3 | 0,068 | 2,75 | 2,48 | 2,00 | 0,46 | 11,4 |
| TV-Q9OQye4C | 1G | 285 | 107 | 11,2 | 0,064 | 1,90 | 1,68 | 1,61 | 0,33 | 8,5 |
| TV-ANmKXWWJ | 4s | 394 | 133 | 11,1 | 0,054 | 1,44 | 1,18 | 1,34 | 0,91 | 18,1 |
| TV-egTb7TgJ | 1G | 129 | 73 | 9,9 | 0,053 | 2,38 | 2,03 | 1,88 | 0,19 | 5,0 |
| TV-oF6FmwfR | 1G | 233 | 96 | 10,9 | 0,045 | 2,18 | 1,82 | 1,80 | 0,24 | 10,4 |
| TV-roaahmoi | 4s | 375 | 113 | 10,3 | 0,035 | 1,75 | 1,38 | 1,35 | 0,76 | 21,8 |
| TV-HfxNiEab | 4s | 800 | 151 | 9,9 | 0,033 | 1,38 | 1,10 | 1,27 | 0,67 | 15,9 |
| U4-H2:KRIPTO25:4H | 4s | 372 | 125 | 11,1 | 0,030 | 1,51 | 1,22 | 1,18 | 1,06 | 19,3 |
| U4-H2:KRIPTO25:1D | 1G | 59 | 38 | 6,3 | 0,026 | 2,68 | 2,40 | 1,97 | 0,29 | 13,0 |
| TV-jc2hs2qK | 4s | 95 | 56 | 9,5 | 0,025 | 2,15 | 1,91 | 1,78 | 0,59 | 10,7 |
| 3UcIwSrE (ETH) | 1s | 2988 | 367 | 4,5 | 0,011 | 1,08 | – | – | – | 2,4 |

## Lider önerisi (kripto risk bütçesi %30 değişmeden, kitap sayısı artar)
Kural: kitaplar arası korelasyon < 0,6 (açgözlü seçim, p10 sırasıyla) → **çekirdek**; 0,6–0,8 arası güçlü adaylar → **ikinci kural seti**, bütçeyi çekirdekle paylaşır ama toplam sepet riski tavanı tek.
1. Çekirdek (korelasyon < 0,6; 4): wcegMOXj, TV-71yKm18B, TV-3BXWqwnF (0,58), U4-H2:KRIPTO25:1D (≤ 0,54). İkinci kural seti (güçlü ama çekirdeğe 0,6–0,8; 2): TV-egTb7TgJ (MDD %5, en iyi ay hariç PF 1,88), TV-Q9OQye4C (285 işlem). Toplam 6 kitap.
2. Toplam KRIPTO25 sepet riski tek tavan (kripto bütçesinin %70'i); wcegMOXj ayrı %20; keşif %10 (mutabakat sonrası QCkIgf3z/BR74LOKo).
3. Yedek: oF6FmwfR, jc2hs2qK, ANmKXWWJ, roaahmoi, HfxNiEab, U4-H2 4H; 3UcIwSrE yalnız maliyet doğrulamasıyla.

## Sol 6.1'e sorular
1. Sepetler arası 0,55–0,80 korelasyonda kitap sayısını artırmak gerçekten fayda sağlar mı (kural çeşitliliği), yoksa tek tavan yeterli mi?
2. Çekirdek 6 seçimine itiraz?
3. Mutabakat bekleyen 3 tek-coin TV-2'yi hızlı doğrulamanın yolu?

## Sol 6.1 cevabı

Altı kitap izlenebilir; ilk dalgada dördüne risk veririm: `TV-71yKm18B`, `TV-3BXWqwnF`, `U4-H2:KRIPTO25:1D` ve `wcegMOXj` çekirdek; `TV-egTb7TgJ` ile `TV-Q9OQye4C` gölge/yedektir. Korelasyonlu kurallar sinyal ve uygulama çeşitliliği sağlayabilir, fakat kitap sayısı bağımsız risk kaynağı sayısını aynı ölçüde artırmaz. Bu nedenle ortak sepet tavanı gereklidir ve önceki “>0,6 korelasyonda birlikte risk vermeme” kuralının yerini almamalıdır. Lidere temel itirazım, `egTb7TgJ` ile `TV-Q9OQye4C`ye çekirdekle eşzamanlı risk verilmesidir.

`wcegMOXj`nin 257 işlem/169 etkin hafta ve PF 2,19'u olumludur; tabloda bulunmayan maliyet/gecikme stresi tamamlanmalıdır. `TV-71yKm18B` (p10 0,098; 3x PF 1,57; en iyi ay hariç PF 1,79) ile `TV-3BXWqwnF` (3x PF 2,48; ay hariç PF 2,00) çekirdek için güçlüdür. `U4-H2:KRIPTO25:1D`, PF 2,68'e rağmen yalnız 59 işlem/38 etkin haftası nedeniyle küçük tutulmalıdır.

2023-01-02–2026-10-24 ortak 1.392 günlük seride `TV-71yKm18B`/`TV-3BXWqwnF` korelasyonu 0,578; `TV-egTb7TgJ`/`TV-71yKm18B` 0,606, `TV-egTb7TgJ`/`TV-3BXWqwnF` 0,766; `TV-Q9OQye4C`/`TV-71yKm18B` 0,610, `TV-Q9OQye4C`/`TV-3BXWqwnF` 0,785'tir. `TV-egTb7TgJ`nin MDD %5'i ve ay hariç PF 1,88'i, `TV-Q9OQye4C`nin 285 işlemi ve p10 0,064'ü onları ilk yedek yapar; aynı anda eklemek yoğunlaşma sınırını aşar.

Diğer yedeklerde `TV-oF6FmwfR` ve `TV-jc2hs2qK` sağlam görünür; ikincisinin örneklemi daha dardır. `TV-ANmKXWWJ`, `TV-roaahmoi`, `TV-HfxNiEab` ve `U4-H2:KRIPTO25:4H`nin daha yüksek düşüşleri ve zayıf stres sonuçları önceliklerini azaltır. `3UcIwSrE`nin 2.988 işlemi PF 1,08'lik ince marjı telafi etmez; maliyet doğrulamasına kadar risk verilmemelidir.

Kripto toplam risk bütçesindeki %30 payı korunmalı; bunun en çok %70'i KRIPTO25 ailesine, %20'si `wcegMOXj`ye, en çok %10'u doğrulanan tek-coin keşiflerine ayrılmalıdır. Keşif doğrulanana kadar bu pay kullanılmamalıdır. Bunlar sermaye/kaldıraç değil risk bütçesi paylarıdır; yaklaşık %6 yıllık toplam risk hedefi birleşik portföyde ayrıca doğrulanmalıdır.

`QCkIgf3z`, `BR74LOKo` ve `zuEOEYPK` için en kısa güvenilir yol dondurulmuş tek bir mutabakat koşusudur: aynı Pine sürümü/parametre, tarih aralığı, borsa-sembol, saat dilimi, veri türü ve emir gerçekleşme varsayımlarıyla TradingView işlem listesi yerel listeyle eşleştirilmelidir. İlk ayrışan işlemde sinyal, yön, giriş/çıkış zamanı ve fiyat karşılaştırılmalıdır. `QCkIgf3z` ETH 15dk serisiyle; `BR74LOKo` ve `zuEOEYPK` gerçek BTC perpetual verisiyle, funding ve maliyet eklenerek sınanmalıdır; perp adayları spot veriyle doğrulanmamalıdır. Ardından temel/3x maliyet, bir bar gecikme ve ortak dönem korelasyonu çıkarılır. Geçen aday keşif payına girer; geçemeyen bekler.

## Uzlaşma (lider)
Sol'un itirazına katılıyorum: egTb7TgJ ve Q9OQye4C çekirdeğe 0,61–0,79 korelasyonlu; ilk dalgada çekirdekle eşzamanlı risk almamalı.
Paper sanal parayla koştuğu için ikisi **paper'da izlenir ama portföy risk bütçesine sayılmaz** (gölge); çekirdekten biri durursa (%10 kayıp) ya da ilk aylık kontrolde ayrışırlarsa risk alırlar.

**Kripto nihai:** çekirdek 4 (risk alır): TV-71yKm18B, TV-3BXWqwnF, U4-H2:KRIPTO25:1D (küçük), wcegMOXj · gölge 2: TV-egTb7TgJ, TV-Q9OQye4C ·
keşif (doğrulama sonrası): QCkIgf3z (ETH 15dk), BR74LOKo / zuEOEYPK (gerçek BTC perp + funding ile yeniden koşu) · yedek: oF6FmwfR, jc2hs2qK.
Bütçe: kripto %30 → KRIPTO25 ailesi ≤ %70, wcegMOXj %20, keşif ≤ %10 (doğrulanana kadar boş).
Not: ilk dalgadaki TV-oF6FmwfR bu çalışmada yedeğe geçti (3BXWqwnF ile 0,70).
