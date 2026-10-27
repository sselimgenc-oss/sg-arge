# Codex durum — izleme

- Tarih: 2026-10-27. Dal: `codex/izleme`, güncel `main` üzerinden açıldı.
- Kapsam: yalnız İş A; İş B / Telegram başlatılmadı.
- Okunanlar: `AGENTS.md`, `DURUM.md`, `docs/GOREV_IZLEME.md`,
  `docs/VERI_SOZLESMESI.md`, `docs/PANO_COPYTRADE.md`.
- **Engel:** İş A madde 5'in yeniden kullanmayı zorunlu tuttuğu
  `copytrade/kapi.delayed_copy`, `main` (`2b8bd61`) üzerinde yok.
  Fonksiyon `codex/copytrade-kapi` (`2c0cdfc`) dalında bulunuyor.
  Kapı kodu kopyalanmadı, başka dal birleştirilmedi ve sözleşme değiştirilmedi.
- **Karar sorusu:** kapı dalını bu dala birleştirerek mi ilerleyelim,
  yoksa liderin kapıyı `main`'e birleştirmesini mi bekleyelim?
  `AGENTS.md` başlangıç madde 3 gereği karar bekleniyor.
- İş A motoru ve saatlik iş akışı henüz uygulanmadı; `durum.json`
  üretimi veya Actions koşusu doğrulandı denmiyor.
- Ortam: Python 3.12.14, `.venv`, `requirements.txt` bağımlılıkları kuruldu.
  Etkinleştirme: `source .venv/bin/activate`.
- Doğrulama: `python -m pip check` başarılı;
  `python -m pytest -q`: **30 başarılı, 9 uyarı** (mevcut testler).
- Teknik seçim: bağımlılıklar depo içinde zaten ignore edilen `.venv`'e
  kuruldu; bağımlılık bildirimleri ve uygulama kodu değiştirilmedi.
- Yeniden kullanılabilir `install_script` ve `start_skill` ortam taslağına
  kaydedildi; yayımlama kullanıcı tarafından ortam ayarlarında yapılır.
