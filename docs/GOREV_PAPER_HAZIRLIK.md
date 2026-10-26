# Görev: paper öncesi zorunlu kontroller (Faz 1 kapanışı)

Kaynak karar: `docs/faz1_son_denetim.md` → "Ortak nihai karar" (kullanıcı onayı 2026-10-26).
Dal: `codex/paper-hazirlik` (`main`'den). Durum: `docs/codex_durum_paper.md`. Tek PR: `[Faz1] paper öncesi kontroller`.

Kapsam: ilk dalga 11 + gölge 3 = 14 kitap:
TV-zoY9DmsF, TV-DUCODGjC, TV-dpkq3n4O, TV-70PkIvTL, G4RNcGXg, TV-71yKm18B, TV-3BXWqwnF, wcegMOXj,
TV-KO7Qe4Xb, U4-H3:EMTIA:1D, yhoK9cH4 · gölge: TV-egTb7TgJ, TV-Q9OQye4C, U4-H2:KRIPTO25:1D.

## Yapılacaklar
1. **Adım 0 nedensellik/dolum denetimi (U7 kitapları):** her kartın `strategies/` kodunu ve `docs/spec/<id>.yaml`'ı oku; gelecek bar, aynı bar kapanışında dolum, `request.security` lookahead, repaint, tarih filtresi (IMKs0OPw hatası gibi: `start/end` girdisi bugünü dışlıyor mu) kontrol et. Kitap başına tek satır sonuç: `results/faz1_paper_denetim.csv` (kimlik, kontrol, sonuç, not).
2. **Sürüm dondurma:** her kitap için kart/kod commit SHA'sı, parametreler, sembol/evren, TF → `results/faz1_paper_listesi.csv`. Sonra bu dosya paper'ın tek girdisi olacak.
3. **Mutabakat:** her kitap için hesap para birimi (USD/USDT/BTC — wcegMOXj ETHBTC'nin dolar karşılığı nasıl hesaplanacak), miktar birimi, maliyet, günlük özkaynak serisi ile raporlanan net arasında dönüşüm. Ayrışma > 1 puan ise nedenini yaz.
4. **Ölçek düzeltmesi:** ortak ölçek kodunda hisse/ETF/emtia serileri için √365 yerine √252 (kripto √365 kalır). Yalnız ölçek; karar/kapı değişmez. Testi ekle; etkilenen ölçekli yıllık değerleri `results/faz1_adaylar.csv` için yeniden üret (`python scripts/faz1_adaylar.py`, `scripts/faz1_genis.py`).
5. **Risk kuralları taslağı:** `docs/faz1_son_denetim.md`'deki kuralların `paper/` için yapılandırma TASLAĞI: `docs/PAPER_PLAN.md` (kitap, risk payı, gölge bayrağı, %10 kitap durdurma, %5 portföy, 200 günlük ortalama kuralı, korelasyon > 0,6 kuralı). **`paper/`'a dokunma** — uygulama kullanıcı onayından sonra.

## Kurallar
Kapı, maliyet, karar kodu değişmez (madde 4'teki ölçek hariç); testler zayıflatılmaz/silinmez; `main`'e doğrudan push yok; `paper/` ve `paper.yml`'e dokunulmaz; repoya veri (parquet) yazılmaz. Bir kitapta denetim başarısızsa listeden çıkarma — sonucu yaz, lider ve kullanıcı karar verir.
