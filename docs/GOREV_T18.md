# T18 — Koşullu adaylardan portföy analizi (sahibi: claude-moderator / Sonnet)

## Amaç
Aşama 2b'de `Kosullu` çıkan adayların birlikte işletildiği bir portföyü değerlendirmek. Kullanıcının önerisi: tek başına zayıf ama birbirinden bağımsız stratejileri birlikte paper trade etmek.

## Girdi
`results/asama2b.csv`'de `karar == Kosullu` olan satırlar:
- Codex satırları: C04, C07.
- Kart satırları: A6-010, R01, G011, M015, M038.

Lider ayrıca `--evren pit` ile yeniden koşu yapıyor; sonuçlar gelince `results/asama2b_pit.csv` dosyasına yazılacak. Önce bu dosyayı kullan, yoksa `results/asama2b.csv`'ye dön.

## İstenenler (`backtests/portfoy.py`)
1. **Getiri serileri:** Her aday için IS (2020-01-01 → 2024-09-30) ve OOS (2024-10-01 →) dönemlerinde günlük getiri serisi üret. `tarama.prepare(...).run()` ve asama2b'deki yükleyiciyi kullan; BIST USD bazında.
2. **Korelasyon:** Adaylar arası günlük getiri korelasyon matrisi. Ayrıca stres günlerindeki (piyasa endeksinin en kötü %5'lik günleri) korelasyon.
3. **Birleşik portföy:** Eşit risk dağılımı.
   - Strateji başına sermaye payı 1/N.
   - EVRENSEL_KURALLAR'daki toplam açık risk %2 tavanı portföy genelinde korunur.
   - Raporlanacaklar: IS ve OOS getiri, PF, MDD; 20 günlük block bootstrap ile %95 MDD (≤ %15 kapısı) ve CAGR p05.
4. **Seçim yanlılığı uyarısı:** Adaylar IS sonuçlarına bakılarak seçildi. Raporda OOS sonucunu ayrı ve öne çıkacak biçimde ver. Ağırlık optimizasyonu yapma, yalnız eşit risk kullan.
5. **Çıktı:** `results/portfoy.md` (tablo + kısa yorum) ve `results/portfoy_korelasyon.csv`.
6. **Test:** Sentetik iki stratejiyle korelasyon hesabının ve risk tavanının doğrulandığı birim test.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. Gerçek veriyle koşu sandbox'ta yapılamıyorsa kodu ver, gerçek koşuyu lider yapar.
