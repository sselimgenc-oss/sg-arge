# Tartışma 002: Kullanıcının amacı (lidere brifing)

Lider (Opus 5.5) kullanıcının amacını ilk elden bilmiyor. Elinde yalnızca `docs/DEVIR.md`'deki özet var. Kullanıcıyla doğrudan konuşmuş her ekip üyesi, bildiğini **kendi dosyasına** yazar:
`tartisma/002_hedef_<model>.md` (örn. `002_hedef_sonnet.md`, `002_hedef_codex.md`). Commit etiketi `[Claude-Mod]` / `[Codex-Sol]`. Kendi dalından PR açılır.

**Öncelik:** T1a/T2'den önce yapılır, kısa tutulur (en fazla ~10 madde). Yorum katma: kullanıcının söylediğini yaz. Varsa kendi çıkarımını ayrı bir "Çıkarım" başlığı altında ver.

## Doldurulacak başlıklar
1. Nihai amaç (örn. canlı işlem mi, gelir hedefi mi, araştırma mı?)
2. Sermaye ölçeği ve getiri/risk beklentisi (kullanıcının verdiği rakamlar)
3. Piyasa ve broker/borsa (BIST aracı kurum, ABD broker, kripto borsası)
4. Zaman ufku ve takvim (paper ne zaman, canlı ne zaman)
5. Day trade / swing tercihi ve ağırlığı
6. Kullanıcının kendi zaman ve operasyon kapasitesi (manuel emir mi, otomasyon/API mi?)
7. Kesin istemedikleri (kırmızı çizgiler)
8. Kullanıcının PDF'lerle ilgili beklentisi (hangi raporlara güveniyor, hangisini sorguluyor)
9. Bütçe kısıtları (token/haftalık limit, ücretli veri)
10. Başka önemli not

## Liderin şu anki bildiği (DEVIR.md)
Paper trading'e girecek stratejileri seçmek. Piyasalar BIST30, ABD, kripto, emtia. Day trade + swing. Temel mod long-only; short ve x2/x3 kaldıraç ayrı varyant, ayrı kapı.
