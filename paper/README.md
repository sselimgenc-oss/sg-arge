# Paper trade altyapısı (T27)

Gerçek para ve aracı kurum bağlantısı yoktur: günlük sinyal, sanal defter, takip raporu ve kullanıcı panosu için `data.json`.

| Dosya | Görev |
|---|---|
| `portfoy.yaml` | paper satırları (C07:ABD25, R01:ABD25, A6-010:EMTIA), sanal sermaye 5.000 USD, alarm eşikleri, başlangıç tarihi (yer tutucu) |
| `gunluk.py` | her işlem günü kapanıştan sonra: satırları **backtest motoru yolundan** (`tarama.prepare` / `asama2b.prepare_codex`) paper başlangıcından son kapanmış bara koşar; yeni emir/dolum/pozisyon/özkaynak satırlarını deftere **ekler**, `RAPOR.md` yazar |
| `parite.py` | defteri gün gün yeniden oynatır, tek bir backtest ile işlem işlem karşılaştırır (`python paper/parite.py --baslangic 2025-01-01 --adim 5`) |
| `panel.py` | defterden ve `results/SONUC.csv`'den `paper/panel/data.json` (sg-test-panel şeması) |
| `defter/` | `emirler.csv`, `dolumlar.csv`, `pozisyonlar.csv`, `ozkaynak.csv`, `alarmlar.csv`; yalnız ekleme, her satırda `git_sha` ve `data_hash` |

Defter, rapor ve panel dosyası `main`'e değil `paper-defter` dalına yazılır (`.github/workflows/paper.yml`). Kurallar: EVRENSEL_KURALLAR D15.
