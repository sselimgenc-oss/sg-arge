# Son-bar durum değişkeni denetimi

299 TV-2 kaynağında `barstate.islast` veya
`barstate.islastconfirmedhistory` arandı. Çoğu kullanım tablo, etiket veya
çizim güncellemesi koşuludur. Geçen iki strateji kaynak bağlamında ayrıca
incelendi.

| Kimlik | Koşul | Kaynak bağlamı | Sonuç |
|---|---|---|---|
| GjZOz8Pu | `barstate.islast` (satır 276) | Eski TP etiketlerini silip açık pozisyon için TP etiketleri çiziyor; `strategy.entry/exit` çağrısı yok. | görsel çıktı, işlem mantığına kanıtlı etkisi yok |
| YqnWtjnn | `barstate.islastconfirmedhistory` (satır 638) | 30/90/180/360 günlük performans hesaplarıyla birleşik tabloyu güncelliyor; emir çağrısı yok. | raporlama çıktısı, işlem mantığına kanıtlı etkisi yok |

Son-bar durumu tek başına işlem kuralına bağlanmadığı için bu iki satıra yeni
nedensellik etiketi eklenmedi. Kaynak sürümü değişirse veya emir çağrısı bu
bloklara taşınırsa denetim tekrarlanmalıdır.
