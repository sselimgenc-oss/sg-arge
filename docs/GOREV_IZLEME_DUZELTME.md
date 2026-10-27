# Görev: İzleme motoru + Telegram Worker düzeltmeleri (Sol 6.1 denetimi, 2026-10-27)

Yapan: **Codex** (PC, yerel). Dal: `codex/izleme-duzeltme`, **Sonnet'in küçük izleme/Worker PR'ı birleştikten sonra**
`main`'den. Tek PR; lider birleştirir. Kaynak: Sol 6.1 denetimi (`docs/DENETIM_2026-10-27.md`, bölüm D).
Eşik değişmez. Kapı dosyalarına (`kapi.py`, `olcut.py`, `kurallar.yaml`) dokunma — Sonnet'te.

## İşler
1. **Olay sonucu emir bazında** (`izleme_motoru.py` `copy_results`): her `acilis`/`buyutme` olayı için kalan miktar,
   toplam maliyet, gerçekleşen K/Z biriktirilir; olay yalnız **tüm** miktarı kapanınca `kapandi`; `net_yuzde` = toplam
   K/Z / toplam kopyalanan tutar. Parçalı dolumlar tek olay.
2. **Sağlık ışığı geçmişi sabit:** eğrinin paydası t0'da sabitlenir (her gün yeniden hesaplanan medyan değil);
   trader başına `veri_zamani` ve `gecerli` (true/false) yayımlanır; hata alan trader'ın eski ışığı "eski veri" olarak
   işaretlenir, pano bunu gösterir (sözleşme v1.4: `traderlar[].veri_zamani`, `traderlar[].gecerli`). Sağlık için
   gereken PnL günde bir değil saatlik güncellenir (portfolio maliyeti uygunsa) ya da açıkça "günlük" yazılır.
3. **Worker "Atladım" düğmesi:** nedensiz `s` tıklaması neden menüsünü açsın (bugün `decision()` null dönüp erken
   çıkıyor). Uçtan uca test: Açtım; Atladım → neden; yeniden basma.
4. **Bildirim kaybı:** `bildirilen` kaydı **gönderim başarılı olduktan sonra** yazılır (ya da `durum: bekliyor|gonderildi`
   ile yeniden denenir). Test: ilk gönderim ağ hatası → sonraki cron'da gönderilir, iki kez gönderilmez.
5. **Sorgulara bölünen emir:** Worker aynı `oid`'nin önceki dolumlarını D1'de biriktirir; olay türü motorla aynı çıkar
   (ortak fixture'a "iki sorguya bölünmüş emir" senaryosu).
6. **Gizlilik:** `kararlar.py` `not` alanı yalnız izinli etiket listesi (boş dahil); serbest metin reddedilir.
   `/kararlar` ve `kararlar.jsonl` alanları kullanıcı kararına göre (aşağıda) daraltılır.
7. **Altın örnekler:** her iş için elle hesaplanmış beklenen sayılı test.

## Kabul
`python -m pytest -q`, Worker testleri yeşil; altın örnekler; canlı: Telegram'da Açtım/Atladım→neden çalışıyor
(kullanıcı dener); `durum.json` v1.4 alanları dolu; `docs/codex_durum_izleme_duzeltme.md`.
