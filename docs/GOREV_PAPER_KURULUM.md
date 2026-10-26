# Görev: Faz 1 nihai listesini paper'a kurmak (kullanıcı onayı 2026-10-26)

Kaynak: `docs/faz1_son_denetim.md` (ortak nihai karar), `docs/PAPER_PLAN.md`, `results/faz1_paper_listesi.csv`.
Kullanıcı kararları (2026-10-26): **"gölge" kavramı yok** — 3 eski gölge kripto kitabı (TV-egTb7TgJ, TV-Q9OQye4C, U4-H2:KRIPTO25:1D) normal kitap olur, kripto %30 bütçesinin içinde. Paper başlasın.
Dal: `codex/paper-kurulum` (`main`'den). Durum: `docs/codex_durum_paper.md`. PR: `[Faz1] paper kurulumu`.

## Kitaplar ve risk payı (toplam %100 risk bütçesi; %10 boş)
| Kitap | Piyasa | TF | Pay |
|---|---|---|---:|
| TV-zoY9DmsF | ABD25 | 1D | 9 |
| TV-DUCODGjC | ABD25 | 1D | 7 |
| TV-dpkq3n4O | ABD25 | 1D | 7 |
| TV-70PkIvTL | ABD25 | 1D | 7 |
| G4RNcGXg (TV-2, SPY 1s) | SPY | 60 | 5 |
| TV-71yKm18B | KRIPTO25 | 4H | 10 |
| TV-3BXWqwnF | KRIPTO25 | 1D | 6 |
| wcegMOXj (TV-2, ETHBTC 6s) | ETHBTC | 360 | 5 |
| TV-egTb7TgJ | KRIPTO25 | 1D | 3 |
| TV-Q9OQye4C | KRIPTO25 | 1D | 3 |
| U4-H2:KRIPTO25:1D | KRIPTO25 | 1D | 3 |
| TV-KO7Qe4Xb | EMTIA | 1D | 13 |
| U4-H3:EMTIA:1D | EMTIA | 1D | 7 |
| yhoK9cH4 (TV-2, META 15dk) | META | 15 | 5 |

## Lider kararları (Codex sorularına, 2026-10-26)
1. **Sermaye:** tek portföy, toplam sanal sermaye **5.000 USD** (mevcut mimari; "her kitap 5.000 USD" ifadesi geçersiz). `agirlik` = pay / 100; ağırlık toplamı **≤ 1** olabilir, kalan **nakit** olarak boş durur (11 U7 = 0,75; TV-2 payları 0,15 Aşama B'ye kadar nakit; 0,10 rezerv). `gunluk.py`'deki "toplam = 1" doğrulaması "≤ 1 ve kalan nakit" olarak değişir; test eklenir.
2. **4 saatlik kitap (TV-71yKm18B):** yeni akış yazma; gölge kitap için zaten var olan 4s yolunu (`indir_golge`, `yukle_golge_veri`, `kapanmamis_4h_bari_at`, saatlik → 4s) normal kitaplara açık hale getir: satırda `tf: 4H` olan kitap bu veri akışını kullanır. Kart TF'si değişmez (`tf_override` yok).

## Aşama A — bugün: 11 U7 kitabı (kart motoru, mevcut `paper/gunluk.py` yolu)
1. `paper/portfoy.yaml`: `satirlar` yeni 11 U7 kitabı (`kaynak: kart`), `agirlik` = pay / 100. 
2. **Eski kitaplar emekliye:** C07, R01, A6-010 ve `golge:` bölümü (U4-H1, T8-07, V2B) yeni portföyden çıkar. Defterleri **silinmez**: `paper/defter/arsiv/2026-10-26/` altına taşınır; panoda "arşiv" olarak kalır. `golge` kod yolu kullanılmaz hale gelir (silme ayrı temizlikte).
3. Başlangıç: `baslangic` = `canli_baslangic` = kurulum PR'ının birleştiği gün (geriye dönük dolum yok; geçmiş zaten backtest).
4. Risk kuralları (`docs/PAPER_PLAN.md`): kitap zirvesinden %10 → kitap durur; portföy zirvesinden %5 → yeni giriş durur; SPY/BTC önceki kapanışı 200 günlük ortalamanın altındaysa yeni uzun risk yarıya; aynı sembolde aynı yönde en çok 3 kitap. `alarmlar` bu eşiklere güncellenir.
5. Panel: yeni kitaplar alan (ABD/Kripto/Emtia/Keşif) etiketiyle; eski kitaplar arşiv sekmesinde.
6. Yerel prova: `python paper/gunluk.py` boş defterle; ilk koşu yalnız başlangıç sonrası barları işler. Prova çıktısını PR'a yaz.

## Aşama B — sonra: 3 TV-2 kitabı (Pine emülatörü)
1. **Kaynak dondurma:** G4RNcGXg, wcegMOXj, yhoK9cH4 için TV-2 koşusunun kullandığı Pine metni + varsayılan parametreler + maliyet → `paper/tv2_kaynak/<id>.pine` ve SHA256 `results/faz1_paper_listesi.csv`'ye.
2. **Paper koşucusu:** `backtests/tv2.py` emülatörünü saatlik işte yalnız bu 3 kitap için, kapanmış barla çalıştıran ince bir katman (`paper/tv2_kitap.py`); dolum sonraki bar açılışı, maliyet TV-2 ile aynı.
3. **wcegMOXj USD dönüşümü:** PnL BTC cinsinden; her değerlemede aynı zaman damgalı BTCUSDT kapanışıyla USD'ye çevrilir; BTC bakiyesi, kur ve USD karşılığı ayrı kolon.
4. Bunlar bitene kadar bu 3 kitabın payı boş kalır (kendi alanında yeniden dağıtılmaz).

## Kurallar
Kapı, maliyet, strateji kodu değişmez; testler zayıflatılmaz/silinmez; `main`'e doğrudan push yok; gerçek para/aracı kurum bağlantısı yok; repoya veri (parquet) yazılmaz. `paper.yml` yalnız yeni işler için gereken kadar değişir.
