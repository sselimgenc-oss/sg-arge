# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-24, lider (Opus).

## Şu an
**Faz 2: paper trade çalışıyor.** C07 + R01 (ABD günlük) + A6-010 (emtia günlük), eşit ağırlık, 5.000 USD sanal (`paper/portfoy.yaml`). Gerçek para yok.
- Defter 2026-09-01'den geriye dönük (aynı kurallar, gerçek veri); **canlı paper 2026-10-24'ten itibaren.** Karar canlı döneme bakılarak verilir.
- `paper.yml` her saat :17'de çalışır. Defter yalnız kapanmış günlük barla (yarım bar koruması); açık pozisyonlar saatlik fiyatla yalnız panoda değerlenir.
- Pano: `sg-pano` reposu, GitHub Pages (https://sselimgenc-oss.github.io/sg-pano/). Veri `PANEL_TOKEN` ile gönderilir.
- Alarmlar: portföy MDD %10 uyarı, %15 yeni giriş durur; bir satır 30 kapanmış işlemden sonra PF < 1 ise inceleme.

| Ajan | Görev |
|---|---|
| Lider | U4 kapandı (`results/U4_SONUC.md`): 16/16 Reddedildi, ama kripto 4H trendinde (H1, H2) gerçek kâr izi var. Sonraki yön için kullanıcı kararı bekleniyor. |
| Codex | Beklemede. U4 gerçek koşu (PR #171) kabul edildi; lider tekrar koşusuyla birebir. |
| Sonnet | Beklemede. U5 tamam (PR #173): 1.298 TradingView açık kaynak strateji tarandı, süzgeçten 205 geçti (`arastirma/U5_tv.csv`, `U5_ozet.md`); örneklem denetimi 3/3. Test için en çok 10 aday seçimi kullanıcı kararıyla. |
| Argon | Beklemede. |

## Sırada (kullanıcı kararı bekleyen)
1. ~~Yeni strateji arayışı~~ → **U4 başladı** (kullanıcı kararı 2026-10-24: kripto 4H/1D + ABD/emtia 1D, kendi hipotezlerimiz, yalnız long).
2. Faz 2 pano modülleri (`docs/FAZ2_NOTLAR.md`): koç bulguları, öğrenen koç (gölge mod), strateji radarı.
3. Küçük iyileştirmeler: hesap kartları saatlik değerlenmiyor (yalnız toplam); fiyat zamanı saatlik barın başlangıcını gösteriyor.

## Kapanan fazların özeti
- **Faz 1** (`docs/FAZ1_SONUC_RAPORU.md`): 422 strateji, 137 test. Geçti 2 (C07, R01), Koşullu 3 (A6-010, T8-07, V2B emtia 1H), Reddedildi 132, Doğrulanamaz 273. Önerilen portföy OOS %7,5, MDD %2,9.
- **U5** (`arastirma/U5_ozet.md`): TradingView açık kaynak, 4H/1D, repaint izsiz 205 aday; test edilmedi.
- **U4** (`results/U4_SONUC.md`): seyrek işlem, 4 kart × 4 kol. 16/16 Reddedildi. Kripto 4H trend IS ve OOS'ta kârlı (3x maliyette de) ama MDD95 %28, DSR düşük, kâr büyük coinlerde.
- **U1** (`results/U1_SONUC.md`): kripto gün içi, 14 varyantın 14'ü Reddedildi. 15m/5m'de brüt kenar yok; 1H'de küçük ama maliyete yetmiyor.
- **U3** (`docs/GOREV_U3.md`, `arastirma/U3_mtf.csv`): 53 MTF strateji kaydı, test edilmedi.
- **T35** (`arastirma/TUM_KAYITLAR.csv`): 80 bölgesel strateji kaydı.

## Temizlik (2026-10-24, kullanıcı onayı)
Faz 1'in kaynak PDF/xlsx'leri, eski görev dosyaları (`docs/GOREV_T*`), `tartisma/`, `argon/`, `kaynak/`, `state.json`, Dukascopy kodu ve büyük işlem dökümleri (`results/tarama_islemler`, `results/trades`, `results/u1/**/islemler_*`) silindi. Hepsi git geçmişinde duruyor: `git log --diff-filter=D --name-only` ile bulunur, `git checkout <commit>^ -- <yol>` ile geri gelir. İşlem dökümleri artık commit edilmez (`.gitignore`); huni ve CI her koşuda yeniden üretir.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz. Çalışma düzeni: `docs/PROTOKOL.md`.
