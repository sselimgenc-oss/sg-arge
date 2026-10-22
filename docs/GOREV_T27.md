# T27 — Paper trade altyapısı (sahibi: claude-moderator / Sonnet)

## Neden
HEDEF'in bir sonraki fazı paper trade. `results/SONUC.md` (T25) ve `results/portfoy.md` (T18) hazır:
- **Geçti:** C07 (ABD, PIT) ve R01 (ABD, PIT).
- **Koşullu:** A6-010 (Emtia).
- **Önerilen portföy:** C07 + R01 + A6-010, eşit risk.

Bu görev **gerçek para ve aracı kurum bağlantısı içermez**: API anahtarı yok, emir gönderimi yok. Yalnız günlük sinyal, sanal defter ve takip raporu yazılır.

## İstenenler
1. **`paper/portfoy.yaml`:** paper'a giren satırlar (id, piyasa, tf, evren, ağırlık).
   - Başlangıç: C07:ABD25, R01:ABD25, A6-010:EMTIA; 1/N ağırlık.
   - Sanal sermaye: 100.000 USD.
   - Evrensel kurallar aynen geçerli: işlem başı %0,5 risk, toplam açık risk %2, ATR14×3 stop (kartta yoksa).
2. **`paper/gunluk.py`** (her işlem günü kapanıştan sonra çalışır):
   - Güncel veriyi indirir (`data/fetch.py`, yalnız gereken semboller).
   - Satırları **backtest'le aynı motor yolundan** çalıştırır: `tarama.prepare` / `asama2b.prepare_codex`. Ayrı bir sinyal kodu yazılmaz; kural kopyalanmaz.
   - Son kapanmış bara göre şunları üretir: ertesi açılışta verilecek emirler (giriş/çıkış, adet, stop seviyesi) ve açık pozisyon listesi.
   - Bir önceki günün emirlerini **gerçekleşen açılış fiyatıyla** doldurur (maliyet EVRENSEL_KURALLAR D).
3. **Defter:** `paper/defter/` altında `emirler.csv`, `dolumlar.csv`, `pozisyonlar.csv`, `ozkaynak.csv`. Sadece ekleme yapılır; geçmiş satır değiştirilmez. Her satırda `git_sha` ve `data_hash` bulunur.
4. **Parite (en önemli test):** Defter, son N günü (ör. 2025-01-01'den bugüne) gün gün yeniden oynatırsa, aynı dönemin backtest işlem listesiyle **birebir** aynı işlemleri vermeli. Bu, paper sonuçlarının backtest'le karşılaştırılabilir olduğunu kanıtlar. Hem sentetik veride test hem gerçek veride bir doğrulama betiği yaz (`paper/parite.py`).
5. **Takip raporu `paper/RAPOR.md`** (her gün yeniden üretilir):
   - özkaynak, getiri, MDD;
   - satır bazında gerçekleşen PF / işlem sayısı ile backtest OOS beklentisi;
   - kayma (dolum fiyatı – sinyal anı beklentisi).

   **Alarmlar:**
   - portföy MDD ≥ %10 → uyarı;
   - portföy MDD ≥ %15 → **durdur** (yeni giriş yok; kullanıcı kararı);
   - 30 işlem sonra PF < 1 olan satır → inceleme.
6. **Zamanlama:** `.github/workflows/paper.yml`, hafta içi ABD kapanışından sonra (ör. 22:30 UTC) çalışır, defteri ve raporu ayrı bir `paper-defter` dalına commit eder. Ana dala yazmaz. `workflow_dispatch` ile elle de tetiklenebilir.
7. **Testler:**
   - sentetik veride uçtan uca gün akışı (emir → ertesi gün dolum → pozisyon → çıkış);
   - parite (madde 4);
   - durdurma alarmı;
   - tatil/eksik veri günü (emir bekler, uydurma dolum yok).

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. Gerçek paper başlangıç tarihi kullanıcı onayıyla belirlenecek; workflow'u etkinleştirmeyi lider yapar.
