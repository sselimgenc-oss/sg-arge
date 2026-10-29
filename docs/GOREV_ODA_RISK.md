# Görev — Oda risk bayrakları: fonlama/korunma ve kalabalıklaşma (Sonnet, 2026-10-29, lider)

Dayanak: Argon A26 ve A27 (`arastirma/copytrade/argon_a26_*.md`, `argon_a27_*.md`) — **lider denetim notlarındaki düzeltmelerle**.
Yalnız bilgi/uyarı: seçim, kapı, oda ve eşik kararı değişmez; otomatik işlem yok. Eşik değerleri `kurallar.yaml`'a yeni anahtar
(PR'da gerekçe; "sezgisel" diye işaretli). Testler zayıflatılmaz; yeni kod testle gelir. PR açılır; birleştirmeyi lider yapar.

## İş (sg-arge, `izleme_motoru` saatlik çıktısına isteğe bağlı alanlar)
1. **Trader başına `yonsuz_bayrak`** (oda + kontrol): funding geliri / toplam kâr (son 90 gün), aynı coinde spot ↔ perp ters pozisyon
   oranı (`spotClearinghouseState`), maker payı (dolumlarda `crossed`). Her biri değer + eşik aşıldı mı; bayrak = herhangi biri.
   API yükü: spot durumu ve funding günde bir kez yeterli (önbellek motor.json'da).
2. **Oda düzeyinde `kalabalik`**: coin başına net yön payı = Σ(kopya ağırlığı × pozisyon nosyoneli / trader hesap değeri × yön) /
   Σ|...| (kaldıraç ikinci kez çarpılmaz); aynı coinde aynı yöndeki oda üyesi sayısı. Eşik aşılırsa tek satır uyarı metni.
3. `docs/VERI_SOZLESMESI.md`'ye isteğe bağlı alanlar; Telegram `/durum`'a tek satır (yalnız uyarı varsa).
4. Altın örnek testler: bilinen funding-arbitraj profili bayraklanır, yönsel profil bayraklanmaz; kalabalık hesabı elle doğrulanan örnek.
