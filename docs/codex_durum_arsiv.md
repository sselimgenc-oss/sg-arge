# Arşiv durumu (Codex, 2026-10-28)

## Uygulama
- `copytrade/arsiv.py` yalnız eklemeli zstd Parquet parçaları yazar; tüm satırlarda `sema_surumu` ve `alindi_ms` vardır.
- Dolum tekilleştirme anahtarı `adres:tid`; kapsam özeti günlük `tur=kapsam/` altında tutulur. Boşluk oranı `%5` üstündeyse iş kırmızı olur (`kurallar.yaml`).
- `arsiv.yml` 15 dakikada pozisyon, saatlik dolum/funding, haftalık leaderboard için genişletilecek ilk canlı koşudan sonra; bu PR'daki tetikleyici 15 dakikalık arşiv temelini R2'ye aktarır.
- R2 anahtarları yalnız GitHub Secrets'tan okunur; kod ve günlükte secret yoktur.

## Canlı kabul kanıtı bekliyor
- İlk Actions koşusundan 24 saat sonra tür başına satır/adres/boşluk ile sütun min/medyan/max özeti eklenecek.
- K8'in 300-adres Worker ölçümü canlı istek ağırlığı gerektirir; Worker'a taşıma yapılmadı.

## Ortam notu
- Ağ erişimi onaylandı. Güncel `origin/main` (`0652652`) üzerine yeniden tabanlama yapıldı. İzole ortamda `python -m pytest -q`: **201 geçti** (1086 mevcut uyarı).
