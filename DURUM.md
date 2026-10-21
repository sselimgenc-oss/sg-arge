# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-21, lider (Opus)

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

## Şu an
| Ajan | İş | Durum | Kullanıcıdan beklenen |
|---|---|---|---|
| Codex | T1a: Codex Algo pilotu (motor + 6 aday + replikasyon + 2015-2019 testi) | **Duraklatıldı: saatlik limit, 04:30 (TR) sonrası devam.** Henüz dal/PR yok | 04:30 sonrası "devam et" |
| Sonnet (ilk oturum) | T5a: kart okuyucu motor çekirdeği (kod, internet gerekmez) | Çalışıyor | Yok. PR açınca lidere haber |
| Argon | T2 yeniden okuma (38 kart) | Sıradaki iş | `argon/PAKET_T2_yeniden.md`'yi aynı sohbete yapıştır; cevabı `argon/T2_yeniden.yaml` olarak yükle |
| Veri arşivi | Saatlik arşiv | 2. çalıştırma sürüyor (düzeltilmiş iş akışıyla) | Yok |

## Sırada bekleyen (açılmadı)
- Argon: `PAKET_T2_yeniden2.md` (36 kart), partiler 6, 7, 8, 9
- Argon parti 4 kabul edildi (40 kart). 17'sinin kaynağı okunamadı (prorealcode 9, ninjatrader 7: büyük ihtimalle üyelik gerekiyor) → YENIDEN.csv
- Codex: T1b (kalan 9 aile), T5b (hızlı tarama). T1a onayından sonra.
- Sonnet: T5a'dan sonra kart tutarlılık denetimi
- Codex limit penceresinde Codex'e yeni iş verilmez; T1a tek iştir.
- İkinci Sonnet oturumu kapatıldı; ortamı web'e erişemiyor (B planı: web okuma Argon'da)

## İlerleme
- Kart: 203 / ~316 (Sonnet 1, 3, 5; Argon 2, 4). Yeniden okunacak: 91
- Kriterler: v0.3 + EVRENSEL_KURALLAR D-D4 onaylı
- Veri katmanı: hazır (88 sembol)
