# Gölge motoru durumu (Codex, 2026-10-28)

## Faz 2 sayıları
- Kullanıcı onayıyla donan V2 ve 3× tavan değerleri `copytrade/kurallar.yaml`'a aktarıldı; kodda eşik yok.
- Swing: 0–7 gün −%50; 7–14 gün −%30 / +%60; 14. günden sonra −%20 / +%40. Intraday −%50 zarar kes.

## Faz 2 kapsamı
- `copy_ledger` üstünde V0/V1/V2 katmanı, gecikme zinciri, eksik/kaçırılan/bant/kırpma olayları ve sıfır maliyet/gecikme sağlaması eklendi.
- Faz 3'e geçilmedi; lider onayı gerekir.
# Sağlama ayrıştırması (Lider denetimi 7)

- Pencere başında açık pozisyonu kapatan dolumun `closedPnl`i trader'da eski giriş fiyatına göre gerçekleşir; `copy_ledger` ise pencereyi sıfır pozisyonla başlatır ve bu kapanışı bilinçli olarak gerçekleştirmez. Bu nedenle tüm-dolum sağlama farkı, çekirdek hesap hatası değil pencere sınırı karışımıdır.
- Sağlama artık adres × coin ilk `startPosition`, pencere-öncesi açık işareti, tüm dolumlar ve yalnız pencere içinde açılıp kapanan pozisyonlar için ayrı fark tabloları üretir. İkinci kıyas sağlama ölçüsüdür.
- Kapı etkisi: `copy_ledger` aynı pencere-sıfır pozisyon davranışını kullanır; pencere öncesi açık pozisyonları kapatan trader PnL'i kapı netine aktarılmaz. Bu bir raporlama/payda sınırıdır. Kapı kodu değiştirilmedi.
