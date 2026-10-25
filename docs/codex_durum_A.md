# Oturum A durumu

Tarih: 2026-10-25 (Europe/Istanbul)
Dal: `codex/kripto-disi`

- 4.1 TAMAMLANDI — Dukascopy yükleyicisi FX, XAU/XAG ve endeks CFD sembol ölçekleriyle birleştirildi; sahte indirme testleri geçti (19 test).
- 4.2 TAKILDI: `vnstock` paketi ortamda yok (`ModuleNotFoundError`); vnstock dalı çalıştırılmadı.
- 4.3 TAMAMLANDI — `arastirma/tv2_veri_eslesme.csv` oluşturuldu: 636 kripto-dışı strateji; Dukascopy 214, yfinance 422.
- 4.4 TAMAMLANDI — `results/tv2/kuyruk_kripto_disi.txt` oluşturuldu; sürüm tarihi 2026 öncesi 72 öğe önce sıralandı, toplam 636 öğe.
- 4.5 TAKILDI: Bu checkout’ta `.github/workflows/tv2.yml` yok ve `gh auth status` geçersiz token gösteriyor; Actions matrisi başlatılamadı. Yerel uzun koşu başlatılmadı.

Son doğrulama: `./.venv/bin/python -m pytest -q tests/test_dukascopy.py tests/test_tv2_kosucu.py` → 19 geçti.
