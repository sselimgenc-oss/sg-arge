# Oturum 1 durumu

Dal: `codex/tv2-son`

- 14:58 — 3. madde — `jLKPS0lF` için NVDAXUSDT → NVDAUSDT ikamesinin yanlış olduğu saptandı; satır `veri_yok` olarak "sembol eşlemesi yanlış" nedeniyle düzeltildi, diğer TradFi perp eşlemeleri denetlendi.
- 15:00 — 5. madde — Riskli üç kaynaktan yalnız `w45uet8E` `izle` durumunda olduğundan satırına `lookahead_riskli=true` ve kaynak satırı `22` bilgi alanları eklendi; kapı ve karar değişmedi.
- 15:08 — 1. madde — `40316028018` tamamlandı; `codex/kripto-disi` checkpoint sonuçları birleştirildi. Kripto dışı kuyruğundaki 636 kimliğin 636'sında satır var, ek kuyruk gerekmiyor.
- 15:12 — 2. madde — Satırlar birleştirildi ve sıralama üretildi; kripto dışı geçenlerin 49'undan 39'u aşırı getiri, `<30` işlem, `lookahead_on` veya `veri_kisa` ölçütleriyle inceleme için işaretlendi. Kararlar değiştirilmedi.
- 15:12 — 6. madde — 371 `izle` satırı eldeki kısa sınamayla tek kapıdan geçirildi: 64 `gecti`, 246 `kaldi`, 61 `islem_yok`; her satıra `kisa_sinama=true` ve hafta sayısı yazıldı, sıralama yenilendi.
- 17:30 — 3. madde — 214 `veri_yok` Dukascopy eşlemesi (ABD endeks CFD eşdeğerleri dahil) için yalnız ilgili kimliklerden kuyruk oluşturuldu. Workflow önce 14 sembolün arşivini Actions cache'ine indirir; veri repoya yazılmaz.
- 17:30 — KOSU_ISTEGI: dal `codex/tv2-son`; iş akışı `TV-2 kripto kuyruğu`; girdiler `kuyruk=results/tv2/kuyruk_dukascopy.txt`, `dukascopy=true`. Sekiz parça birlikte çalıştırılmalı.
- 17:30 — 4. madde — Dukascopy kuyruğu dışındaki 187 `veri_yok` ve 13 `zaman_asimi` satırı mevcut gerekçeleriyle kapatıldı; yeni deneme veya uzun koşu istenmedi.
