# Paper hazırlık durumu

Tarih: 2026-10-26. Dal: `codex/paper-hazirlik`; taban: `397c107c1120bd521f0627fa6f464e34945ddd97` (`main`).

## Paper kurulumu — Aşama A

- Lider kararıyla portföy tek 5.000 USD sanal sermayedir; 11 U7 ağırlığı %75, kalan %25 nakittir. TV-2'nin %15 payı Aşama B'ye kadar nakit kalır.
- `TV-71yKm18B` normal portföy satırı olarak 4 saatlik ham veriyi mevcut gölge veri yolu kurallarıyla (kapanmış bar) kullanır; kartın TF'si değiştirilmedi.
- Eski C07/R01/A6-010 ve gölge yapılandırması yeni portföyden çıkarıldı. Checkout'ta arşivlenecek defter CSV'si yoktu.

## Tamamlananlar

- 14 kitap için Adım 0 sonucu `results/faz1_paper_denetim.csv` içine tek satırla yazıldı. Başarısız/koşullu kitaplar listeden çıkarılmadı.
- Dondurulmuş tek girdi `results/faz1_paper_listesi.csv`: kart/artifact, son değiştiren commit, parametre, evren, TF, para birimi, miktar/maliyet ve günlük seri mutabakatını içerir.
- Ortak ölçek düzeltildi: günlük hisse/ETF/emtia serileri `sqrt(252)`, kripto serileri `sqrt(365)` kullanır. Bu yalnız sıralama ölçeğini değiştirir; kapı ve karar kodu değişmedi. TV-2 ve U7 sıralamaları ile `results/faz1_adaylar.csv` ve `results/faz1_adaylar_genis.md` yeniden üretildi.
- Uygulama öncesi risk taslağı `docs/PAPER_PLAN.md` içine yazıldı; `paper/` ve `paper.yml` değiştirilmedi.

## Açık noktalar

- G4RNcGXg, wcegMOXj ve yhoK9cH4 TV-2 artifact'lerinde yerel Pine kaynak/varsayılan parametre snapshot'ı yok; paper emrinden önce hash'li kaynak kaydı gerekir.
- wcegMOXj ETHBTC'nin BTC PnL'si USD'ye çevrilmeden risk bütçesi kullanılamaz. Günlük seri/rapor net farkı -1.413 puandır; ilk gün, sınırı aşan işlem ve açık pozisyon ayrıştırılmalıdır.
- G4RNcGXg farkı -0.866 puan, yhoK9cH4 farkı -0.231 puandır; ikisi de raporlanan netle günlük seri arasındaki farkı paper başlamadan ayrıştırma kaydına bağlamalıdır.
- D8/U7 Ek 4 ile işaretlenen kitaplarda motor koruma emrinin dolum barı zamanlaması Pine'dan farklıdır; paper olay kaydı dolum-bar stopunu görünür kılmalıdır.

## Doğrulama

` .venv/bin/python -m pytest tests/test_tv2_sirala.py ` → 6 geçti.

Yeniden üretim komutları: `python -m backtests.tv2_sirala`, `python -m backtests.u7_sirala`, `python scripts/faz1_adaylar.py`, `python scripts/faz1_genis.py`.
