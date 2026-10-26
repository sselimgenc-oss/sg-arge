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

## 2. Beklenti bandı (kitap kartı)
- Her kitap için backtest sınama döneminden haftalık getiri dağılımı (`results/u7/**/getiriler`, TV-2 için
  `results/tv2/getiriler/<id>.csv`). Eski `gunluk._expectations` (asama2b tablosu) bu kitaplar için geçerli değil, kullanma.
- Canlı hafta sayısı n için bootstrap ile n haftalık birikimli getirinin %10–%90 aralığı; canlı değer bandın
  altında / içinde / üstünde. Ayrıca beklenen ve gerçekleşen işlem sıklığı.
- Panelde: "beklenti içinde" / "beklentinin altında (n hafta)" / "beklentinin üstünde". Bu bilgi amaçlıdır;
  karar 26 canlı hafta sonunda kullanıcınındır (`docs/TEST_YAPISI.md` Adım 5).

## 3. Koç bulguları (kurallı, ML yok)
`paper/koc.py`: defterden ve beklenti bandından kurallı notlar üretir; panelde liste. Her not: kitap, kural, sayı,
tarih. Kurallar (eşikler sabit, dosyanın başında):
- kitap ≥ 4 hafta beklenti bandının altında;
- kitap zirveden düşüşü durdurma eşiğinin yarısını geçti (%5) — erken uyarı;
- son 20 kapanmış işlemde baskın çıkış nedeni `stop` ve oranı backtest'tekinden belirgin yüksek;
- beklenen işlem sıklığının yarısından azı (sinyal gelmiyor / veri sorunu şüphesi);
- aynı gün aynı yönde ≥ 3 kitap giriş yaptı (yoğunlaşma);
- `KAYNAK_HATASI` / `VERI_ESKI` alarmı son 24 saatte.
Not yoksa "dikkat gerektiren durum yok".

## 4. Pano
- `paper/panel.py` `data.json` şemasına yeni alanlar: `islemler[].giris_nedeni/cikis_nedeni`, `kitaplar[].beklenti`,
  `koc[]`. Eski alanlar korunur (geriye uyumlu).
- Arayüz `sselimgenc-oss/sg-pano`'da; bu PR yalnız veriyi üretir. Arayüz değişikliğini lider ayrıca yapar.

## 5. Testler
Neden eşlemesi; beklenti bandı (sabit örnek getiriyle bant içinde/altında); her koç kuralı için bir tetiklenen ve
bir tetiklenmeyen örnek; `data.json` eski alanlar korunuyor.
