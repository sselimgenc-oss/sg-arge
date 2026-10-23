# T35: Bölgesel strateji toplama, ilk parti (deneme)

Sahipler: Sonnet (Çin, Japonya, Kore, Hindistan), Codex (Avrupa, Amerika), Argon (Afrika, G. Amerika: `argon/PAKET_T35_afrika_gamerika.md`), lider (TradingView bölgesel + denetim).
Karar kaynağı: `tartisma/009_ozet_karar.md`. Başlama koşulu: kullanıcı onayı.

## Amaç
Faz 1'in 422 stratejisinin **dışında**, yazarının **rakamla** kârlı olduğunu iddia ettiği scalp/day/swing stratejilerini, **yazarın kendi piyasasıyla** kaydetmek.
**Backtest yok. Kod yazılmaz. Motor ve `docs/spec/` kartlarına dokunulmaz.**

## Toplama kapısı: kayıt listeye girer, eğer
1. En az bir performans metriği (PF, WR, getiri, Sharpe, MDD) **ve** test dönemi yazılı. İşlem sayısı yoksa yine girer, `kirmizi_bayrak: islem_sayisi_yok`.
2. Strateji tanımlı: en az bir paragraf açıklama ya da kod. Kurs, sinyal ya da bot satışı reklamı girmez.
3. Faz 1 tekrarı değil. Kontrol `strateji_listesi (2).xlsx` (URL sütunu), `docs/KATALOG.csv`, `docs/spec/*.yaml` (`kaynak.url`, `ad`) ile yapılır. Tekrar şüphesi varsa `faz1_tekrar: supheli <id>`.

Giriş gerektiren ya da ücretli kaynak atılmaz, `erisim` alanında işaretlenir. Kırmızı bayraklar da atılmaz, işaretlenir: `islem_sayisi_yok`, `az_islem(<30)`, `pf_gt_4`, `maliyet_yok`, `kisa_donem(<1yil)`, `yalniz_ekran_goruntusu`, `t_arti_1`, `iterasyon_izi`.

## Şablon: `arastirma/SABLON.csv`
Her deney bir satır. Aynı strateji farklı piyasa ya da parametreyle ayrı sonuç veriyorsa id `KR-003a`, `KR-003b` olur.

| Alan | Değer |
|---|---|
| id | `CN/JP/KR/IN/EU/US/SA/AF-<3 hane>` |
| kol | sonnet / codex / argon / lider |
| ad, ad_orijinal | Türkçe/İngilizce ad + orijinal dildeki ad |
| tur | scalp (1H altı) / day / swing / belirsiz |
| piyasa, enstruman | Yazarın test ettiği piyasa (ör. "Nikkei 225 mini vadeli", "KOSPI200 hisseleri", "Upbit BTC/KRW") |
| veri_kodu | Bildiğin kadarıyla veri sembolü (`7203.T`, `005930.KS`, `^NSEBANK`, `WIN$`); bilinmiyorsa boş |
| giris, cikis, stop | Kaynakta yazdığı kadar, **uydurmadan**; yoksa boş |
| orijinal_alinti | Giriş/çıkış kuralının orijinal dilde kısa alıntısı (çeviri hatasına karşı) |
| ceviri_dogrulandi | evet / makine / gerek_yok |
| kural_tam | evet / kismen / hayir |
| iddia_* | **Yalnız yazarın beyanı.** Birim yaz: `%42`, `1.8`. Yoksa boş. Tahmin yok |
| iddia_turu | backtest / canli / forward / karisik |
| maliyet_dahil | evet / hayir / belirtilmemis |
| referans_turu | forum / blog / kod_deposu / platform_raporu / canli_hesap / makale |
| dogrulama | platform_dogrulamali (JoinQuant/BigQuant grafiği, Myfxbook, Tradetron canlı, QuantConnect gömülü backtest) / yazar_beyani |
| kanit_notu | Kanıt nerede: "README tablosu", "3. gönderideki rapor", "yalnız metin" |
| erisim | acik / giris_gerekli / ucretli |
| motor_notu | cok_bacakli / opsiyon / short / tick_veri / seans_saati; yoksa boş |
| faz1_tekrar | hayir / supheli <id> |

Çıktı `arastirma/<kol>.csv` (UTF-8, virgüllü; metin alanlarında tırnak). Açılamayan siteler `arastirma/<kol>_erisim.md` dosyasına "site, ne denendi, sonuç" olarak yazılır.

## Kollar ve ilk parti hedefi
| Kol | Bölge | Hedef | Öncelikli kaynaklar |
|---|---|---|---|
| Sonnet | Çin, Japonya, Kore (Hindistan son) | 15-20 | JoinQuant 策略分享, BigQuant 策略广场, RiceQuant 社区, Uqer, 天勤; Qiita, Zenn, Hatena Blog, FX-On; WikiDocs, 퀀터, Upbit 변동성 돌파 GitHub; Tradetron, Streak, Chartink |
| Codex | Avrupa, Amerika | 8-10 | smart-lab.ru, wallstreet-online, ABC Bourse, Trade2Win, X-Trader.net; AmiBroker AFL, TradeStation Strategy Network, GitHub, arXiv/SSRN, Myfxbook. Faz 1 siteleri (MQL5, ProRealCode, Elite Trader, NinjaTrader, QuantConnect, futures.io) yalnız yeni içerik |
| Argon | Afrika, G. Amerika | 8-12 | `argon/PAKET_T35_afrika_gamerika.md` |
| Lider | TradingView bölgesel (ja/ko/zh/pt/es/ru/de/fr/it/in) | 10 | |

Her kol türleri karıştırmaya çalışır: en az birkaç scalp, day ve swing. İlk partinin amacı şablonun zor durumlarda çalıştığını görmek: farklı dil, vadeli/opsiyon, kodu açık ama raporu eksik, canlı iddia.

## Teslim
- Sonnet/Codex: PR (dal adı serbest), başlık `[T35] <kol> ilk parti`. PR açıklamasında: kayıt sayısı, kapıdan dönen sayısı ve en sık dönme nedeni, açılamayan siteler.
- Yasak: uydurma metrik ya da kural, tahminle doldurulmuş alan, başka kolun bölgesi, `docs/` / `engine/` / `state.json` değişikliği (`DURUM.md` dahil; onu lider günceller).

## Lider denetimi
Rastgele 5 kayıt kaynaktan kontrol edilir. Uydurma bulunursa o kolun partisi geri döner. İlk parti sonunda kapıdan geçme oranına göre ikinci parti hedefleri belirlenir.
