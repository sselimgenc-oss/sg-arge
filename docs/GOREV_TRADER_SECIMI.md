# Görev: Trader seçimi — CT-Kapı düzeltmeleri (3. adım, 2026-10-27, lider)

Yapan: **Codex** (PC, yerel mod). Dal: `codex/kapi-v1-1`. Tek PR, `main`'e; lider birleştirir.
Kaynak: `docs/GOREV_COPYTRADE_KAPI.md`, `copytrade/kapi.py`, son sonuç `copytrade/kapi/2026-10-27/`.
**Eşikler değişmez** (kullanıcı kararı). Bu iş yalnız hataları ve kapsamı düzeltir.

## Lider teşhisi (2026-10-27 sonucundan)
- Adım 1–2'yi 189 adres geçti; adım 3 **ve** 4'ü birlikte geçen **9** adres var (raporun "adım 5: 0" satırı plasebonun
  hiç hesaplanamamasından). 9'unun da `plasebo_hata` = `non-overlapping placebo placement unavailable`.
- **Neden:** `randomize_trades` bir trader'ın **tüm** işlemlerini (tüm coinler) birbirine hiç değmeyecek şekilde
  yerleştirmeye çalışıyor. Gerçek trader'lar aynı anda birden çok coinde pozisyon tutuyor; toplam elde tutma süresi
  pencereyi aşınca yerleştirme imkânsız. Yani hata veri yetersizliği değil, plasebo tasarımı.
- Kapsam: 12.461 adresin 8.196'sı işlendi (shard'lar 100 dk'da bitmedi); 66 adres HTTP 500 ile düştü.

## İşler
1. **Plasebo (adım 5) düzeltmesi:** çakışma yasağı **coin başına** olsun (aynı coinde aynı anda tek pozisyon; farklı
   coinler çakışabilir — gerçekteki gibi). Coin, yön, büyüklük, süre, maliyet aynı kalır; 1000 tekrar; p ≤ 0,05.
   Bir coinin işlemleri coin başına da yerleşemiyorsa o coin için işlem dizisini bütün olarak **rastgele dairesel
   kaydır** (aralıklar korunur) ve satıra `plasebo_not = "dairesel kaydırma: <coin listesi>"` yaz. Plasebo artık
   yerleştirme yüzünden NaN olmamalı; olursa `plasebo_hata` dolu ve sınıf `Yetersiz`.
2. **Kapsam:**
   - Shard sayısı 16 → 32.
   - `--eksikleri-tamamla`: aynı günün `sonuc.csv`'sinde olmayan veya `neden` alanı "veri hatası" olan adresleri işler
     ve birleştirir. HTTP 5xx için adres başına 3 deneme (artan bekleme).
   - RAPOR'a "işlenen / evren" oranı yazılır. Hedef ≥ %98.
3. **Yalnız adım 5–8'i yeniden koş** modu (`--yalniz-adim5` var; son `sonuc.csv`'den 1–4'ü geçenleri alır): önce
   bununla 9 adres için hızlı sonuç, sonra tam koşu.
4. **İlişkili hesap kontrolü** (yalnız adım 6'yı geçenler; puanı değiştirmez, işaret koyar). Kaynak:
   `arastirma/copytrade/argon_hazir_servis_iliskili_hesap.md`. İstekler `subAccounts`, `userVaultEquities` (vault
   lideri mi; `vaultDetails.leader`), `extraAgents`, `userNonFundingLedgerUpdates` (iç transfer karşı adresleri). Yeni
   sütunlar `iliskili_adresler` (`;` ile) ve `iliskili_not`; ilişkili adres de leaderboard'daysa ve ters yönde açık
   pozisyonu varsa `iliskili_not = "ters pozisyonlu ilişkili hesap"`.
5. **Rapor:** `copytrade/kapi/<tarih>/RAPOR.md`'de huni; adım 1–2'yi geçenler için tablo (her adımın sonucu ve
   nedeni); "Geçti" listesi ayrı; ilişkili hesap işaretleri.
6. İş akışı `main`'den tetiklensin (`copytrade/kapi/CALISTIR` yolu; dal kısıtı kalksın). Sonuçlar `main`'e
   yazılmaz; `copytrade-kapi` veri dalına (yoksa yetim) yazılır.

## Testler (ağsız)
Aynı anda iki coinde pozisyonu olan trader için plasebo yerleşir; tek coinde sığmayan dizide dairesel kaydırma ve not;
1000 skor; 5xx yeniden deneme; eksikleri tamamla birleştirmesi (tekrar satır yok); ilişkili hesap işaretleri (sabit
yanıtlarla).

## Kabul
- `python -m pytest -q` yeşil.
- `--yalniz-adim5` koşusunda 9 adresin hepsinde `plasebo_p` sayı (ya da açık nedenli `plasebo_hata`).
- Tam koşuda işlenen ≥ %98; RAPOR huni ve listeler eksiksiz.
- `docs/codex_durum_trader_secimi.md`: yapılanlar, seçimler, sınırlar.

## Sonra (lider + kullanıcı)
"Geçti" ve sınırdaki adaylar lider tarafından incelenir; izleme listesi (≤ 20) **kullanıcı onayıyla**
`copytrade/izleme_listesi.yaml`'a girer; t0 = giriş günü; 3 ay sanal izleme. Gerçek para yok.
