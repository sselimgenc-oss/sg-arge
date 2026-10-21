# T2 - B seviyesi stratejiler icin kural kartlari (kod yok)

Sahip: claude-moderator (Sonnet 5.5, sg507). Atayan: lider (Opus 5.5).
Neden: Faz 2'de Codex'in kodlayacagi B seviyesi adaylar icin kriterler v0.3 test 1 (spesifikasyon) simdiden hazir olsun; T1a ile paralel, dosya cakismasi yok.

## Yapilacaklar
1. Su PDF'lerden her strateji icin `docs/spec/<id>.md` kart cikar: `Paper_Test_4_...`, `Paper_Test_8_...`, `Voltran_4_...`, `Reddit_ve_Quant_...`. Oncelik sirasi: P03, P04, R03, R01, P01, P02, R05, R07, V1A, V1B, V2A, V2B, P5-P8 satirlarindaki stratejiler.
2. Kart sablonu (her alan dolu ya da "BELIRSIZ: <ne eksik>"):
   - Kaynak (PDF + sayfa), zaman dilimleri (MTF), evren
   - Karar zamani, kullanilan veri (yalniz kapanmis bar mi?), giris fiyati
   - Giris kurallari, cikis kurallari, ayni bar stop/hedef onceligi
   - Pozisyon boyutu, risk, maliyet varsayimi
   - Parametreler ve PDF'te kac varyant/iterasyon denendigi (DSR icin N)
   - Rapor rakamlari (PF, Sharpe, getiri, MDD, islem)
   - Spesifikasyon durumu: **Tam / Eksik / Day-trade (saatlik veri gerekli)**
3. `docs/KATALOG.csv`: eksik-veri satirlarini (V2A, V2B, P5-P8) karttan doldur; P5-P8 ve L01-L38 toplu satirlarini ayri satirlara bol; `spec_durumu` kolonu ekle.
4. L01-L38 (C seviyesi) icin kart yok; yalniz KATALOG'da tek satir/strateji ve "C" kaniti.

## Kabul kriteri
- Rakam ve kural uydurulmaz; PDF'te yoksa "BELIRSIZ".
- Teslim: kendi dalina push + `main`'e PR, baslik `[Claude-Mod] T2 ...`. Issue #1'de `@auditor` etiketle.
- `state.json`'a yalniz kendi T2 kaydinin `status` alanini yaz.

## Yapmayacagi seyler
Kod, backtest, kriter degisikligi yok. T1a dosyalarina (`data/`, `engine/`, `strategies/`, `backtests/`, `results/`) dokunma.
