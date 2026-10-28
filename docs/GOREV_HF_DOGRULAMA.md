# Görev: Hugging Face geçmiş hesap verisinin doğrulanması (2026-10-28, lider)

Yapan: **Sonnet**. Dal: `claude/hf-dogrulama`. Tek PR, `main`'e; lider birleştirir. Önce `DURUM.md`,
`arastirma/copytrade/argon_ucretsiz_gecmis_veri.md`, `docs/GOREV_GOLGE.md` (Faz 3 evren). Ağ: bulut oturumundan
huggingface.co kapalı → iş GitHub Actions'ta. Kod yöntemi/kapıyı değiştirmez; yalnız veri kaynağını ölçer.

## Kaynak
`ProbioticFarmer/hyperliquid-augmented-copytrading` (Hugging Face, MIT lisans; kullanıcı 2026-10-28'de sayfanın var olduğunu
gördü). 9 alt küme, toplam ~4,26 milyar satır, 268 GB. `account_values`: ~420 milyon satır; sütunlar en az `user`, `dex`,
`collateral_token`, `account_value`, `total_long_notional`, `total_short_notional`. Tamamı indirilmez: DuckDB `hf://` ile yalnız
gereken sütun ve tarih okunur.

## İşler (`copytrade/hf_dogrulama.py` + `.github/workflows/hf_dogrulama.yml`, push tetiği kendi dalında)
1. **Envanter:** 9 alt kümenin adı, satır sayısı, sütunları ve tarih aralığı; veri kartındaki üretim yöntemi (veri nereden,
   hangi sıklıkla, kim üretmiş) kısa özet.
2. **Kapsam:** `account_values` için gün başına adres sayısı; ilk/son tarih; eksik günler (boşluk listesi).
3. **Çapraz doğrulama:** en son tarihte, kapı sonucundaki (veri dalı) 30 adresin `account_value`'su ↔ Hyperliquid
   `clearinghouseState`/`portfolio` aynı güne en yakın değer; göreli fark dağılımı (min/medyan/max). Ayrıca 2–3 geçmiş tarihte
   `portfolio` geçmişiyle aynı karşılaştırma.
4. **Leaderboard'a uygunluk:** iki tarih arası PnL'i ayırmak için yatırma/çekme (ledger) verisi alt kümelerde var mı? Yoksa
   açıkça yaz.
5. Çıktı: `hf_dogrulama.json` + PR açıklamasında özet tablo. Tolerans ya da "kullanılır" kararı koyma; sayıları raporla,
   karar lider ve kullanıcıda.

## Kabul
- Testler: tarih bölümü yol üretimi, boşluk sayımı, göreli fark hesabı (altın örnek, elle hesaplanmış); tam test paketi.
- Canlı Actions koşusunun çıktı özeti PR'da. Ağ/erişim hatası `|| true` ile örtülmez.
- Durum: `docs/sonnet_durum_hf.md`.
