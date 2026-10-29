# Görev — Denetim temizlikleri (Codex, 2026-10-29, lider)

Kaynak: `docs/DENETIM_GENEL_2026-10-29.md`. Kapı eşikleri ve karar kodu değişmez; yeni sayılar yalnız `kurallar.yaml`. Altın
örnekli test; testler zayıflatılmaz. Her madde ayrı commit, tek PR. main'e doğrudan push yok.

1. **`gunluk.csv.gz` yayımlanmıyor:** kapı koşusu seçim raporunun yoğunlaşma bölümü için gereken günlük getiri dosyasını veri
   dalına yazmıyor (`secim/2026-10-29-v1.3/RAPOR.md` "yoğunlaşma hesaplanamadı"). `kapi_yayimla.sh` / birleştirme adımı bunu
   `copytrade/kapi/<tarih>/` altına yazsın; dosya yoksa seçim raporu yine "hesaplanamadı" der (uydurma yok).
2. **B21:** ilişkili hesap keşfi havuzun tamamına (yalnız katmanlı 87 değil).
3. **B22:** `binance_payi` tüm parçalarda aynı kaynaktan ya da sütun kaldırılır; "tamamen boş sütun" kapısı 2 değerle geçmesin.
4. **B23:** kapı satırına `kod_hash` ve `now_ms`; birleştirmede farklı hash'ler ayrı raporlanır.
5. **B29:** `.github/workflows/inceleme.yml`'deki `|| true` kaldırılır ya da iş akışı arşivlenir.

Teslim: PR; açıklamada madde başına ne değişti ve test.
