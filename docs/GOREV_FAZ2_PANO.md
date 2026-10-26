# Görev: Faz 2 asıl iş — pano ve koç bulguları (kullanıcı onayı 2026-10-26)

Kaynak: `docs/FAZ2_NOTLAR.md` §2 (a, b) ve §3. Strateji seçimi kapandı; bu iş **yalnız gösterir ve açıklar**,
hiçbir işlem kararını değiştirmez. Paper kitapları, kartlar, ağırlıklar, risk kuralları, kapılar değişmez.
Dal: `codex/faz2-pano` (`main`'den). Durum: `docs/codex_durum_faz2.md`. PR: `[Faz2] pano + koç`. PR öncesi tam test paketi.

## Amaç

Kullanıcı panoyu açtığında üç soruya cevap görsün:
1. **Ne oldu?** Her işlem neden açıldı, neden kapandı.
2. **Beklendiği gibi mi?** Her kitabın canlı sonucu, backtest'ten beklenen aralığın içinde mi.
3. **Dikkat edilecek ne var?** Kurallı, kısa koç notları.

## 1. İşlem açıklamaları (`paper/gunluk.py` defteri → `paper/panel.py`)
- Defterdeki `dolumlar.neden` (motorun çıkış nedeni: `stop`, `hedef`, `zaman_stop`, Pine `exit_id`/`comment` ...) panelde
  Türkçe okunur etikete çevrilir (eşleme tablosu tek yerde; bilinmeyen neden olduğu gibi gösterilir).
- Kapanmış işlemde: giriş/çıkış tarihi ve fiyatı, net, R (stop varsa), tutma süresi, giriş nedeni, çıkış nedeni.

## 2. Beklenti bandı ve sağlık ölçüleri (kitap kartı)
Yöntem: Argon notu `arastirma/faz2_izleme_notu.md` §1–2. Hepsi bilgi amaçlı; işlem kararını değiştirmez.
- **Kaynak:** her kitabın backtest sınama dönemi haftalık getirileri (`results/u7/**/getiriler`, TV-2 için
  `results/tv2/getiriler/<id>.csv`). Eski `gunluk._expectations` (asama2b tablosu) bu kitaplar için geçerli değil, kullanma.
- **Koni:** **blok bootstrap** (blok 4 hafta; i.i.d. karıştırma yok — MDD'yi olduğundan düşük gösterir), 5.000 yol,
  canlı hafta n için birikimli getiri p5–p95 ve p1–p99. Canlı değerin dilimi (pXX) yazılır.
- **MDD oranı:** canlı MDD / backtest MDD (1,0x ve 1,5x çizgileri).
- **CUSUM (alt):** z_t = (r_t − μ_BT)/σ_BT; S_t = max(0, S_{t−1} − z_t − k), k = 0,5; eşik h = 3,5 (sarı), 4,77 (kırmızı).
- **Sinyal sıklığı:** canlı işlem sayısı, backtest oranıyla Poisson %95 / %99 aralığı dışında mı; < %50 ise kırmızı.
- **Ardışık kayıp:** eşik kazanma oranı w ve işlem sayısı N'den: P(seri ≥ k) < 0,05 sarı, < 0,01 kırmızı (sabit sayı yok).
- **Az işlemli kitap** (sınamada yılda < 30 işlem): getiri yerine işlem bazlı bootstrap (n işlemlik alt örneklem
  p5–p95); "örneklem küçük" etiketi.
- Durum ışığı: tüm ölçüler yeşil → 🟢; herhangi biri sarı → 🟡; herhangi biri kırmızı → 🔴.

## 3. Koç bulguları (kurallı, ML yok)
`paper/koc.py`: §2 ölçülerinden ve defterden kısa notlar; her not kitap, ölçü, değer, eşik, tarih. Ek kurallar:
aynı gün aynı yönde ≥ 3 kitap giriş (yoğunlaşma); `KAYNAK_HATASI` / `VERI_ESKI` son 24 saatte; gerçekleşen kayma
backtest varsayımının > 1,5 katı. Not yoksa "dikkat gerektiren durum yok". Eşikler `koc.py` başında sabit.

**Değerlendirme ilkesi (Argon notu):** 26 hafta, yıllık Sharpe ≈ 2,3 altındaki bir stratejinin pozitif getirisini
kanıtlamaya yetmez. Amaç bozuk/aşırı uyumlu kitabı yakalamak (🔴) ve beklenti içinde kalanı onaylamaktır; 13 kitap
aynı anda bakıldığı için tek kitabın "iyi görünmesi" kanıt sayılmaz. Kırmızı ışık kitabı **durdurmaz** (paper kaydı
sürer); mevcut tek durdurma kuralları değişmez (kitap %10, portföy %5).

## 4. Pano
- `paper/panel.py` `data.json` şemasına yeni alanlar: `islemler[].giris_nedeni/cikis_nedeni`, `kitaplar[].saglik`
  (§2 ölçüleri + ışık + 26 haftalık mini seri), `koni` (seçili kitap için p1/p5/p50/p95/p99), `koc[]`.
- Ekran düzeni (Argon §3): üstte portföy özeti + ışık sayacı (🟢/🟡/🔴); ortada 13 satırlık sağlık matrisi;
  satıra tıklayınca koni, su altı grafiği, haftalık getiri dağılımı. Eski alanlar korunur (geriye uyumlu).
- Arayüz `sselimgenc-oss/sg-pano`'da; bu PR yalnız veriyi üretir. Arayüz değişikliğini lider ayrıca yapar.

## 5. Testler
Neden eşlemesi; blok bootstrap konisi (sabit tohum, sabit örnek getiri: bant içinde/altında); CUSUM (bilinen kaymada eşik aşımı, kaymasızda aşmama); Poisson sıklık ve ardışık kayıp eşikleri; her koç kuralı için tetiklenen/tetiklenmeyen örnek; `data.json` eski alanlar korunuyor.
