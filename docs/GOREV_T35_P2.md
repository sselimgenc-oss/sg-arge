# T35 parti 2: bölgesel strateji toplama (Codex + Argon)

Ön koşul: `docs/GOREV_T35.md` (amaç, kapı, şablon) aynen geçerli. Parti 1 değerlendirmesi: `tartisma/010_t35_ilk_parti_degerlendirme.md`.
**Backtest yok, kod yok.** Yalnız `arastirma/` altına yazılır.

## Ortak kurallar (parti 1'e ek)
- **Tekrar kontrolü iki katmanlı:**
  1. Faz 1 (`strateji_listesi (2).xlsx`, `docs/KATALOG.csv`, `docs/spec/*.yaml`);
  2. parti 1 (`arastirma/*.csv`).

  Aynı aile ama farklı piyasa ya da filtre ise kayıt girer, `faz1_tekrar: supheli <id>` yazılır.
- **Birimler net yazılır:** `iddia_pf` yalnız profit factor (brüt kâr / brüt zarar) içindir. Kâr/zarar oranı, ortalama kazanç/kayıp gibi başka metrikler `not` alanına yazılır, birimiyle birlikte.
- **Al-tut kıyası:** Kaynak al-tut ya da endeks getirisi veriyorsa `not`'a yazılır. Strateji al-tutun altındaysa `kirmizi_bayrak: al_tut_altinda`.
- Uydurma yok; boş alan boş kalır. Lider her koldan rastgele 2 kaydı kaynağında kontrol eder (kullanıcı aracılığıyla).

## Codex (Avrupa + Amerika): hedef 10-12, çıktı `arastirma/codex_p2.csv`
Parti 1'in 10 kaydı yalnız arXiv'dendi ve 5'i ML modeliydi. Bu partide:
- **arXiv/SSRN en fazla 2 kayıt**, yalnız mekanik kurallı olanlar. ML/derin öğrenme modeli girmez (girerse `motor_notu: ml`, en fazla 1).
- **Öncelikli kaynaklar (sırayla dene):**
  - Avrupa: smart-lab.ru (RU), wallstreet-online.de ve trader-forum (DE), ABC Bourse forum ve Zone Bourse (FR), X-Trader.net (ES), Investire.biz / FinanzaOnline (IT), Trade2Win (UK).
  - Amerika: AmiBroker AFL Library, TradeStation Strategy Network / EasyLanguage forumları, futures.io (yalnız yeni içerik), BabyPips, Myfxbook (doğrulanmış hesap + açıklanmış strateji).
- **Türler:** en az 3 scalp ya da day (DAX/ES/NQ açılış, Euro Stoxx, MOEX vadeli) olsun.
- Her siteyi denediğini `arastirma/codex_p2_erisim.md`'ye yaz: site, denenen sayfa, sonuç (açıldı / 403 / giriş / rakamlı içerik yok).
- **Parti 1 düzeltmesi:** `arastirma/codex.csv` içinde US-002..004'ün `iddia_getiri` alanındaki "P&L 1,11 / 1,40 / 1,24" ifadesinin ne olduğunu makaleden kontrol et. PF ise `iddia_pf`'ye taşı, değilse birimini `not`'a yaz.
- Teslim: PR, başlık `[T35-P2] codex ikinci parti`. Açıklamada kayıt sayısı, kaynak dağılımı, açılamayan siteler.

## Argon (Afrika + G. Amerika): hedef 15, paket `argon/PAKET_T35P2_latam.md`
Parti 1 kabul edildi (kullanıcı doğrulaması). QuantBrasil devam, ek olarak Meksika/Kolombiya/Şili/Peru ve Afrika.

## Lider
TradingView'de aracı kurum hesapları (DNSE, Genial, Lab106 vb.) ve "out-of-sample / held-out" ifadeli yazılar. Sonnet parti 1'i gelince değerlendirilir.
