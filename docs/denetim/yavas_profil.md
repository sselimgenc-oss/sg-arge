# TV-2 yavaş betik profili

Tarih: 2026-10-26. Hedefler: `LA06Kpl1`, `OvE4qQgh`, `JeRCEqWU`,
`wQ1dtwbW`, `nmnHkA02`, `qetKgBK2`, `b4EWZCPJ`.

## Ölçüm

Her kaynak Pine Facade önbelleğinden okundu ve `engine.pine.ayristir.ayristir`
ayrı süreçte 25 saniye tavanıyla çalıştırıldı. Yedisi de tavana ulaşmadan AST
üretemedi; dolayısıyla darboğaz veri indirme veya backtest motoru değil,
ayrıştırmadır.

| Kimlik | Kaynak karakteri | 25 sn içinde AST | Sonuç |
|---|---:|---|---|
| LA06Kpl1 | 79.275 | hayır | zaman tavanı |
| OvE4qQgh | 12.104 | hayır | zaman tavanı |
| JeRCEqWU | 91.343 | hayır | zaman tavanı |
| wQ1dtwbW | 105.102 | hayır | zaman tavanı |
| nmnHkA02 | 126.050 | hayır | zaman tavanı |
| qetKgBK2 | 16.272 | hayır | zaman tavanı |
| b4EWZCPJ | 52.416 | hayır | zaman tavanı |

`OvE4qQgh` üzerinde 8 saniyelik süre sınırlı `cProfile` örneklemesi 24,5
milyon çağrı gördü. En sıcak üç yol:

1. `PinescriptParser.start_script` / `statements` — 7,998 sn birikimli;
2. `antlr4.atn.ParserATNSimulator.adaptivePredict` — 45 çağrıda 7,968 sn;
3. `ParserATNSimulator.closure` / `closureCheckingStopState` / `closure_` —
   353 üst çağrı ve yaklaşık 600 bin özyinelemeli çağrıda 7,815 sn.

## Değerlendirme

Mevcut `ayristir` zaten SLL tahmin modu, hata durumunda LL geri dönüşü ve
kaynak özetiyle disk AST önbelleği kullanır. SLL/LL tercihinin zorla
değiştirilmesi veya ayrıştırmayı süre aşımında kesmek farklı/eksik AST ve
dolayısıyla strateji davranışı üretebilir. Bu nedenle doğrulanmış,
davranış-değiştirmeyen kod hızlandırması uygulanmadı.

Önerilen sonraki teknik iş: `pynescript` sürümünde/üretici gramerinde bu
`adaptivePredict` patlamasını izole eden küçük Pine örneğiyle upstream
karşılaştırması. Bu, yorumlayıcı semantiği değişikliği olabileceğinden bu
madde kapsamında yapılmadı.

# Yavaş TV-2 betikleri profil notu

2026-10-26 01:50 TR: E1 için yedi Pine kaynağı önbelleğe alındı. Kaynak
büyüklükleri: LA06Kpl1 79 KB, OvE4qQgh 12 KB, JeRCEqWU 91 KB, wQ1dtwbW
105 KB, nmnHkA02 126 KB, qetKgBK2 16 KB, b4EWZCPJ 52 KB.

`PineStrateji` kurulumunu `cProfile` ile toplu ve tekil olmak üzere iki kez
çalıştırma denemesi, ayrıştırma aşamasında sonuç üretmeden uzadı. Tasarruf
kuralı gereği üçüncü deneme yapılmadı; güvenli bir hızlandırma sonucu yoktur.
Tam koşuların çoğu zaten `zaman_asimi` satırındadır; profil yeniden ancak
süre sınırlı/ayrı bir işçi ortamında alınmalıdır.
