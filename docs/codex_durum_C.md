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
- **E4 atlandı:** Kullanıcı yönlendirmesiyle Oturum A yürütüyor; bu dalda E4
  için kod veya rapor değişikliği yapılmadı.
- **ALDIM: E7** — TV-2 nihai değerleriyle `docs/SANAL_HAVUZ.md` taslağını
  güncelleme (yalnız öneri; karar/kapı/eşik değiştirmeden).
- **E7 tamamlandı:** TV-2 uzak sonuç anlık görüntüsündeki 19 satır ve 15
  temsilci, seçim veya terfi kararı üretmeden `docs/SANAL_HAVUZ.md` taslağına
  işlendi. 6.6 kaynak denetim tablosunda her iddiaya bağlantı ve sonuç da
  açıkça eklendi.
- **ALDIM: E6** — Test paketini süreleriyle ölçme; 10 saniyeyi aşan testleri
  davranışı değiştirmeden hızlandırma.
- **E6 tamamlandı:** 30.000×5 bellek örneklemi 14.000×5, tüm günlük kart
  smoke testi de 4 yerine 2 sembolle çalıştırıldı; ikisi de aynı denetim
  kapsamıyla sırasıyla 9.51 sn ve 8.96 sn oldu. Tam paket: `1320 passed,
  4 skipped` ve 162.52 sn (önce 183.35 sn).
- **ALDIM: E2** — Eksik kütüphane import'larını envantere ekleme ve ilgili
  stratejileri yeniden çalıştırma.
- **E2 tamamlandı:** Envanterde yedi açık Pine kütüphanesi doğrulandı ve
  sürümlü PUB çağrısı için ağsız test eklendi. Sonuçlanmış 299 TV-2 kaynağı
  tarandı: import kullanan altı stratejinin tamamı yalnız `TradingView/ta`
  kullanıyor. Altısı yeniden koşuldu; üçü veri/footprint eksikliğiyle
  `desteklenmiyor`, üçü `izle` sonucunda kaldı. Karar/kapı/eşik değişmedi.
- **ALDIM: E1** — Ertelenen yavaş betikler için profil çıkarma, davranışı
  değiştirmeden hızlandırma ve test.
- **E1 tamamlandı:** Yedi hedefin tümü ayrıştırmada 25 sn tavanını aştı;
  `adaptivePredict` ve `closure` çağrıları sıcak yol olarak belgelendi
  (`docs/denetim/yavas_profil.md`). Sadık AST'yi değiştirmeden uygulanabilir
  hızlandırma doğrulanamadığından yorumlayıcı kodu değiştirilmedi.

İstenen sıra: `6.3 → 6.7 → 6.1 → 6.6 → 6.4`

Karar, kapı ve eşik değiştirilmedi. TV-2 ve U7 sonuçları ilgili uzak dallardan
`git show` ile salt-okunur okunacaktır.

