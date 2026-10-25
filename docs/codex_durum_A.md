# Oturum A durumu

Tarih: 2026-10-25 (Europe/Istanbul)
Dal: `codex/kripto-disi`

- 4.1 TAMAMLANDI — Dukascopy yükleyicisi FX, XAU/XAG ve endeks CFD sembol ölçekleriyle birleştirildi; sahte indirme testleri geçti (19 test).
- 4.2 TAKILDI: `vnstock` paketi ortamda yok (`ModuleNotFoundError`); vnstock dalı çalıştırılmadı.
- 4.3 TAMAMLANDI — `arastirma/tv2_veri_eslesme.csv` oluşturuldu: 636 kripto-dışı strateji; Dukascopy 214, yfinance 422.
- 4.4 TAMAMLANDI — `results/tv2/kuyruk_kripto_disi.txt` oluşturuldu; sürüm tarihi 2026 öncesi 72 öğe önce sıralandı, toplam 636 öğe.
- 4.5 HAZIR, KOŞU KULLANICIDAN BEKLENİYOR — `codex/tv2-kosu` birleştirildi; `.github/workflows/tv2.yml` içindeki `kuyruk` girdisi varsayılan olarak `results/tv2/kuyruk_kripto_disi.txt` seçiyor. Kullanıcı workflow’u başlatabilir.

Son doğrulama: `./.venv/bin/python -m pytest -q tests/` → 1328 geçti, 4 atlandı.

## Ek iş havuzu

- E3 TAMAMLANDI — 31 `veri_yok` satırı için OKX ikinci kaynak fallback’i eklendi ve Bybit/OKX sorguları denendi. Bybit çalışma bölgesinden HTTP 403 ile engelli; OKX’te bu 31 sembol için kullanılabilir veri bulunamadı; yeniden koşulacak satır çıkmadı.
- E5 TAMAMLANDI — 11 `islem_yok` satırı kaynak okumasıyla sınıflandırıldı: brMq1l1s, CFOy39oC, 2lGyzYkC ve XIJrNXQc harici `input.source` bağlayıcısı bekliyor; KHBR2H0R, IvMdQJNW, 8N8DT3Pv, sxo2gPSm, Bz7isFiX, 7VqlwJsL ve 6MsOzaoy kaynakta/koşuda sinyal üretmedi.
- E4 TAMAMLANDI — 12 desteklenmiyor satırı gruplandı: 9 `request.security` dış sembol verisi yok, 2 çizim nesnesi `get_y1/get_top`, 1 footprint verisi yok. İlk grup veri erişimi, ikinci grup yorumlayıcı semantiği, üçüncü grup ücretli veri kapsamı olduğundan karar değiştiren varsayımsal uygulama yapılmadı.
