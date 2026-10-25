# Oturum C — Analiz ve Denetim Durumu

Tarih: 2026-10-25 (Europe/Istanbul)
Dal: `codex/analiz`

## İlerleme

- **6.3 tamamlandı:** TV-2’de geçen ilk beş stratejinin Pine kaynağı okundu;
  giriş, çıkış, boyut, maliyet ve `security` kullanımı yorumlayıcıyla
  karşılaştırıldı. Rapor: `docs/denetim/S1_codex.md`.
- **6.7 tamamlandı:** ML iddiaları kaynak/PDF ve ortam kanıtıyla denetlendi;
  `dsr`/`n_eff` yalnız bilgi sütunu olarak eklendi ve üst zaman dilimi +
  `lookahead_on` satırları listelendi. Test: `4 passed`.
- **6.1 tamamlandı:** U7 dalından `karar_adim2` karşılığı olan OOS net>0 ve
  en az 10 haftalık 85 varyant (U4: 14, U6: 71) alındı; TV-2 ile aynı %10
  oynaklık ölçeği, 4 haftalık blok bootstrap p10, kopya ayıklama ve `TOHUM`
  uygulandı. 72 temsilci çıktı: `results/u7/siralama.csv`.
- **6.6 tamamlandı:** Copy-trade PDF’sindeki 12 kritik iddia denetlendi;
  varlık sınıfı görüşleri, t0 tabanlı sanal izleme pilotu ve kullanıcı kararları
  `docs/FAZ2_NOTLAR.md` sonuna eklendi. Hukuki/para kararı verilmedi.
- **6.4 tamamlandı:** `docs/FAZ3_YURUTME.md` sonuna emir yolu, manuel ölçüm,
  gerçek enstrüman farkı, risk bölüşümü, güvenlik ve aşamalı geçiş eleştirisi
  eklendi.
- **ALDIM: E4** — `desteklenmiyor` ve `hata` sonuçlarını gruplama; en sık üç
  eksik Pine özelliğini belgeye dayalı test ve kodla ele alma.

İstenen sıra: `6.3 → 6.7 → 6.1 → 6.6 → 6.4`

Karar, kapı ve eşik değiştirilmedi. TV-2 ve U7 sonuçları ilgili uzak dallardan
`git show` ile salt-okunur okunacaktır.

