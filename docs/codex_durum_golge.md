# Gölge motoru durumu (Codex, 2026-10-28)

## Faz 2 engeli
- V2 için `kurallar.yaml`'a yazılması gereken sayılar eksik: 7. ve 14. günlerdeki kâr/zarar sınırları ile gölge pozisyon üst sınırı.
- Ön kayıt yalnız teminatın `%50` zarar kesmesini ve swing için 7/14 günü belirliyor; bu günlerdeki sınırları ve üst sınırı tanımlamıyor.
- Bu değerler sonuç görülmeden dondurulacak karar eşikleridir. Tahmin edilmedi.

## Hazır taslak
- `copy_ledger` üstünde V0/V1, gecikme zinciri, eksik/kaçırılan olay ve sıfır maliyet/gecikme sağlaması için yerel taslak hazırlandı.
- Taslak commit edilmedi; V2 kararları gelince tamamlanıp her kuralın altın örnekleriyle tek Faz 2 PR'ı olarak açılacak.

## Gereken lider kararı
- V2 swing 7. ve 14. gün için teminata göre zarar ve kâr sınırları.
- Gölge pozisyonu başına üst sınır.
