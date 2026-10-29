# Görev — Arşivde kalıcılık testi + deneme defteri (Sonnet, 2026-10-29, lider)

Dayanak: `arastirma/fikir_gorusleri/OZET.md` ("listede olmayan fikir A", 3/6 görüş). Soru: "seçim skoru yüksek hesaplar sonraki
haftalarda gerçekten daha iyi gidiyor mu?" 18'e 18 canlı oda bunu kanıtlayamaz (güç ~%20); binlerce hesapla sorulur.
Bu bir **keşif** analizidir: pilotu, seçimi, kapıyı ve eşikleri değiştirmez. Sonuç raporu kullanıcıya bilgi verir.

Kurallar: değerler yalnız `kurallar.yaml` (yeni `kalicilik_*` anahtarları, PR'da gerekçesiyle); geleceğe bakma yok (T anındaki skor
yalnız T'ye kadarki veriyle); sahte veri yok; testler zayıflatılmaz, yeni kod testle gelir. PR açılır; birleştirmeyi lider yapar.

## İş
1. **Deneme defteri** `arastirma/copytrade/deneme_defteri.jsonl` + `copytrade/deneme.py`: her deneme, sonucu görülmeden önce bir
   satır (tarih, hipotez, skor tanımı, pencere, başarı ölçütü, kod sha). Sonuç sonra ayrı satırla eklenir; silme yok.
   Toplam deneme sayısı rapora ve (sonra) panoya yazılır. Bu görevin denemeleri de buraya ilk iş olarak yazılır.
2. **Evren:** son kapı evreni (lider tablosu, hesap değeri tabanı) — hayatta kalan yanlılığı raporda açıkça yazılır.
   Kaynak: Hyperliquid `portfolio` sorgusu (hesap değeri ve kâr geçmişi; dolum sınırına takılmaz). Önbellek R2 arşivine değil,
   iş akışı önbelleğine/yerel dosyaya; API ağırlık sınırına uy (`RateLimiter`).
3. **Test (önceden yazılı):** son 12 ay, 14 günde bir T anı. Her T'de skor = (a) 90 günlük getiri, (b) 90 günlük getiri / maksimum
   düşüş (Calmar), (c) 180 günlük kârlı ay oranı — yalnız bu üçü (deneme defterine 3 deneme). Hesaplar skora göre 5 dilime;
   sonraki 28 ve 56 günün getirisi (kâr geçmişinden, yatırma/çekme etkisi arındırılmış). Ölçüt: dilim ortalamalarında üstten alta
   düzenli düşüş (Spearman) ve üst − alt farkı; T'ler arası örtüşme için blok bootstrap güven aralığı.
4. **Kopya notu:** bu, trader getirisidir, gecikmeli kopya değildir. Üst dilimden 100 hesaplık örnekte mevcut gölge motoruyla
   30 dk / 2 sa gecikmeli kopya getirisi de hesaplanır (fark = kopya aşınması).
5. **Rapor** `arastirma/copytrade/kalicilik/RAPOR.md`: sade Türkçe özet (ilk 5 satır: "skor gelecek getiriyi söylüyor mu?"),
   tablo, sınırlamalar. İş akışı `kalicilik.yml` (elle tetiklenir; parçalı, zaman aşımı korumalı).
6. Testler: sentetik veriyle (cevabı bilinen: kalıcı beceri var / yok) dilim testinin doğru sonucu verdiği; geleceğe bakma testi.

## Teslim
PR; sentetik doğrulama çıktısı; gerçek koşu kullanıcıya bırakılır (iş akışı adı PR'da yazılı).
