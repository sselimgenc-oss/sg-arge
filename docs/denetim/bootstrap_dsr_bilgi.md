# Bootstrap p10 ve DSR bilgi envanteri

Bu belge yalnız bilgi amaçlıdır; kapı, eşik, sıralama veya canlı kitap kararı
değiştirmez.

| Kaynak | Bootstrap p10 | DSR | Kanıt | Not |
|---|---|---|---|---|
| TV-2 | var | var | `origin/codex/analiz:results/tv2/siralama.csv` | `alt_sinir_haftalik_p10`, `n_eff` ve `dsr` bilgi sütunları bulunur. |
| U7 | var | yok | `origin/codex/analiz:results/u7/siralama.csv` | 85 satır / 72 temsilci; `alt_sinir_haftalik_p10` ve OOS Sharpe var, birleşik DSR sütunu yok. |
| A dalı TV-2 snapshot | var | yok | `results/tv2/siralama.csv` | Bu dal eski 19 satırlık snapshot taşır; DSR bilgisi analiz dalında üretilmiştir. |

## Yorum

- TV-2 ve U7 için ortak DSR hesabı, aynı deneme ailesi tanımı olmadan
  birleştirilemez. U7’nin aile/genel deneme sayısını varsayarak yeni DSR
  türetmek yanlış bilgi üretir.
- Her iki ailedeki p10 değeri yalnız sıralama bilgisidir; Adım 2 kararını
  değiştirmez.
- Ortak bir tablo gerekirse, kaynak commit’leri ve aileye özgü deneme sayıları
  kalıcı biçimde kaydedildikten sonra analiz dalında yeniden üretilecektir.
