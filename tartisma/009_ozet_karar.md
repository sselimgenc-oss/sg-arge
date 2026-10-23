# 009 özet ve karar önerisi (lider)

Tarih: 2026-10-23. Girdiler: `009_beyin_firtinasi_bolgesel_tarama.md`, `009_cevap_sonnet.md`, `009_cevap_codex.md`, `009_cevap_argon.md`.
Durum: **kullanıcı onayı bekliyor.** Onaylanınca T35 başlar (`docs/GOREV_T35.md`, `argon/PAKET_T35_afrika_gamerika.md`).

## Uzlaşılanlar (üç ajan da aynı görüşte)
- Amaç doğru: yazarın rakamlı kârlılık iddiası, yazarın piyasası, şimdi backtest yok.
- İlk parti **hacim değil şablon denemesi.** Sayıyı doldurmak için zayıf kayıt eklenmez.
- Rakam, dönem olmadan değersiz. "Kârlı" ya da "günlük +%0,3" tek başına kapıyı geçmez.
- Raporlanan değer ile bizim yorumumuz ayrı tutulur. Eksik değer tahmin edilmez.
- Kimse henüz siteleri denemedi; erişim ilk partide ölçülecek.

## Lider kararları
1. **Rakam kapısı (netleştirildi):** en az bir performans metriği (PF, WR, getiri, Sharpe, MDD) **ve** test dönemi zorunlu. İşlem sayısı yoksa kayıt girer, `kirmizi_bayrak`'a `islem_sayisi_yok` yazılır.
2. **Deney başına satır (Codex):** aynı strateji farklı piyasa ya da parametreyle ayrı sonuç veriyorsa ayrı satır açılır. id: `KR-003a`, `KR-003b`.
3. **Yeni alanlar:**
   - Sonnet'ten `dogrulama`, `veri_kodu`, `ceviri_dogrulandi` + `orijinal_alinti`.
   - Codex'ten `referans_turu`, `kanit_notu`.
   - Lider'den `motor_notu` (çok bacaklı/opsiyon/short; sonraki backtest için) ve `faz1_tekrar`.
4. **Çıkarılan kaynaklar (Argon):** Nairaland, Kenya grupları, Moneyweb/JSE blogları, investing.com forumları.
5. **Eklenen kaynaklar:**
   - Argon: QuantBrasil, ArabicTrader, Rava, ADVFN Brasil, Rankia, MyBroadband, B3 GitHub depoları.
   - Sonnet: Uqer, JoinQuant 策略分享, BigQuant 策略广场, Hatena Blog, FX-On, 퀀터, Upbit 변동성 돌파 depoları, Chartink, StockEdge, Myfxbook.
   - Codex: AmiBroker AFL Library, TradeStation Strategy Network, Quant StackExchange, arXiv/SSRN.
6. **Faz 1 kaynaklarında (MQL5, ProRealCode, Elite Trader, NinjaTrader, QuantConnect, futures.io) yalnız yeni içerik.** Codex bunları önerdi, ama Faz 1'de tarandılar. Tekrar riski yüksek; her kayıtta `faz1_tekrar` kontrolü zorunlu. Codex repoyu okuyabildiği için kontrolü kendisi yapar. Argon yapamaz; onun kayıtlarını lider kontrol eder.
7. **Akademik kaynaklar (arXiv/SSRN) ayrı sınıf:** `referans_turu: makale`. Yalnız mekanik kural ve rakamlı sonuç verenler girer.
8. **İlk parti hedefleri:** Sonnet 15-20, Codex 8-10, Argon 8-12.
9. **Erişim yolu:** Kodlama ajanlarının bulut ortamı sitelerde proxy 403 alıyor. Kendi ortamında açamayan ajan, açamadığı siteleri `arastirma/<kol>_erisim.md`'ye yazar ve uydurmaz. Kullanıcı gerekirse aynı paketi sohbet uygulamasında (web/derin araştırma) çalıştırır.

## Not: sonraki backtest için uyarılar (toplamayı etkilemez)
- Spread/pairs/arbitraj (Arjantin, JSE, vadeli-spot basis) ve opsiyon (BankNifty, 0DTE, short-vol) aileleri tek enstrüman, long-only motorumuzla test edilemez. Toplanır, `motor_notu` ile işaretlenir.
- Çin hisseleri T+1: hissede gün içi strateji yazarın iddiasıyla bile şüphelidir; `kirmizi_bayrak: t_arti_1`.
