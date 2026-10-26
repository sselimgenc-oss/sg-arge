# TV-2 şüpheli sonuçlar

Bu liste kararları değiştirmez. Ölçüt, uygulanabilir tüm-dönem net getirinin `%−100` altı veya `%+300` üstü olmasıdır.

| Grup | Kimlikler | Gözlenen | Olası yorumlayıcı/strateji nedeni |
|---|---|---|---|
| Çok kısa TF, aşırı negatif | `1HAKnNRc`, `4qLy8AFi`, `7qUtuiBt`, `9ewY0OQg`, `NWIwEuKt`, `UJwSLens`, `anNnwsQo`, `biUvPKOz`, `d7hoosSf`, `fq8iiXQI`, `pcoISSiu`, `sYMa3n2C`, `tpgANCaq` | %−234 ile %−781.567 | 1–15 dk serilerde her doluma komisyon/kayma birikimi; yazarın kaldıraç, `default_qty_type` veya sözleşme çarpanı kullanımının nominal boyutu büyütmesi ayrıca incelenmeli. |
| Diğer aşırı negatif | `1i9HDUUV`, `Cf6gXdy1`, `PIOU52P5`, `TNuMDlbv`, `UA83Q4Je`, `YgYQ9MG2`, `ZyJPE4QX`, `dzpmnane`, `f7F71vdS`, `fIVuGtFw`, `mpawgWIA`, `w45uet8E`, `zCYYilCg`, `9YaLIh0i` | %−100 ile %−184.188 | Kaldıraç/pozisyon boyutu ve ters-yön `strategy.entry` dönüşleri; stopların seviyeden ziyade tick/point tanımıyla kurulmuş olması olasıdır. |
| Aşırı pozitif | `Djj394ka`, `GoUoySJs`, `IVx6SIX8`, `KdC6xqb8`, `QCkIgf3z`, `V3jpZpIs`, `YgAz2p0E`, `byjop8YP`, `cJNpcbta`, `ec57c7xL`, `jTHvkEVo`, `jtPXA64T`, `tDChqhhR`, `wVNfdkHu`, `xYFoVctF` | %+304 ile %+45.742 | `pyramiding`, yüzde-sermaye boyutunun bileşik etkisi veya sembol/platform farkından kaynaklanan pointvalue/mintick varsayımı sonuçları büyütebilir. |

Not: sonuç birimleri kaynak sembolü/kontrat çarpanı yerine TV-2 emülatörünün fiyat-adet P&L birimidir. Özellikle vadeli `.P`, USD-dışı çiftler ve 1–5 dk kaynaklar yeniden el okumada önceliklidir.
