# 🚀 Autonomous Multi-AI Quantitative Trading Framework

Bu proje, finansal piyasalar için kantitatif borsa stratejileri geliştirmek, optimize etmek ve backtest (geriye dönük test) süreçlerini otomatikleştirmek amacıyla **Claude Code**, **ChatGPT Codex** ve **Google Gemini** modellerini tek bir ekipte buluşturur.

> **Güncel durum her zaman `DURUM.md`'dedir** (kimin hangi işte olduğu, son kararlar). Çalışma kuralları: `docs/PROTOKOL.md`. `state.json` 2026-10-22'den beri güncellenmiyor, yalnız geçmiş kaydıdır.
>
> **Kapsam (kullanıcı kararı, 2026-10-23): yalnız kripto, gün içi** (1 saat kurulum, 15 dk / 5 dk işlem). Hedef yılda %20-30 net, MDD ≤ %15. Faz 1 (BIST/ABD/emtia/kripto, 422 strateji) kapandı: `docs/FAZ1_SONUC_RAPORU.md`.

---

## 🤖 Ekip ve roller (güncelleme: 2026-10-23)

| Model | Rol | Ne yapar |
| :--- | :--- | :--- |
| **Claude Opus 5.5** (sselimgenc hesabı) | **Takım lideri** | Karar ve öncelik sahibi. Görev yazar (`docs/GOREV_*.md`), ön kaydı belirler, PR'ları denetler, sonuç raporlarını yazar. `DURUM.md`'yi yalnız lider günceller. |
| **Codex** | Uygulayıcı (kod, veri, gerçek koşular) | 2026-10-23'te projeden çıkarıldı, aynı gün geri döndü (kullanıcı kararı). Görevini Issue #1'deki `[CODEX GÖREVİ]` yorumundan ya da kullanıcının yapıştırdığı mesajdan alır. Teslim PR ile. |
| **Claude Sonnet 5.5** (sg507 hesabı) | Uygulayıcı (kod, araştırma) | Lider talimatıyla çalışır, karar vermez. Görevini Issue #1'deki `[SONNET GÖREVİ]` yorumundan ya da kullanıcının yapıştırdığı mesajdan alır. Teslim PR ile. |
| **Argon** (Google Gemini 3.8, repo erişimi yok) | Araştırmacı + denetçi | Kullanıcı aracılığıyla çalışır: lider `argon/PAKET_*.md` paketini hazırlar, kullanıcı Gemini'ye yapıştırır, cevabı geri getirir. Bulgularını kaynaklı yazar; ekibin yöntemini eleştirebilir (kullanıcı kararı, 2026-10-23). Çıktısını lider denetler. |
| ~~Sol 6.1~~ | — | Kanalı yok, pasif. |

**Kural:** her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz.

---

## 🔄 İletişim (gerçekte nasıl işliyor)

Ajanlar kendiliğinden tetiklenmiyor; 15 dakikalık yoklama ve `@` ile dürtme **çalışmıyor**. Akış şöyle:

1. Lider görevi `docs/GOREV_*.md` dosyasına yazar, PR açar; kullanıcı PR'ı birleştirir.
2. Lider Issue #1'e `[CODEX GÖREVİ]` ya da `[SONNET GÖREVİ]` başlıklı kısa bir yorum yazar ve `DURUM.md`'yi günceller.
3. Lider kullanıcıya her ajan için **yapıştırmaya hazır** bir mesaj verir. Kullanıcı mesajı ilgili ajana yapıştırır (ya da yalnız "görev geldi" der).
4. Ajan main'i çeker, görevi yapar, PR ile teslim eder. Lider denetler, kabul ya da ret yazar.

Commit etiketleri: `[Opus-Lead]`, `[Claude-Mod]` (Sonnet), `[Codex]`, `[Argon]`.

---

## 📂 Proje yapısı

```text
├── DURUM.md                # Güncel durum (tek doğru kaynak)
├── docs/                   # Görevler (GOREV_*.md), kurallar (EVRENSEL_KURALLAR, ELEME_KRITERLERI, PROTOKOL), strateji kartları (spec/)
├── engine/                 # Kart yorumlayıcı, göstergeler, portföy motoru, kilit
├── backtests/              # Huni aşamaları (tarama, asama2a, asama2b), U1 koşucuları, raporlar
├── data/                   # İndiriciler ve MANIFEST.csv (büyük Parquet dosyaları git dışında)
├── results/                # Sonuçlar (SONUC.md/csv, U1 çıktıları)
├── paper/                  # Paper trade altyapısı (zamanlaması kapalı)
├── strategies/             # Codex Algo 21 Python stratejileri
├── tartisma/               # Tartışmalar ve lider kararları
├── argon/                  # Argon paketleri ve cevapları
├── arastirma/              # Strateji toplama kayıtları (T35, U3)
├── tests/                  # pytest
└── state.json              # Eski kuyruk kaydı (2026-10-22'den beri güncellenmiyor)
```
