# F2-PANO: Paper defteri canlı panoda, saatlik güncelleme

**Karar:** kullanıcı, 2026-10-23.
- Paper portföyü: C07 + R01 + A6-010 (`paper/portfoy.yaml`, başlangıç 2026-10-23).
- Pano: `sg-test-panel` yeniden adlandırılır (yeni ad: `sg-pano`). Public, GitHub Pages ile yayınlanır.
- Güncelleme saatlik ve otomatik. `strateji-test-pano`, yeni pano çalışınca kullanıcı tarafından silinir.

| Parça | Sahip | Repo |
|---|---|---|
| A. Saatlik çalışma, yarım bar koruması, anlık değerleme, panoya gönderme | **Codex** | `sg-arge`, dal `codex/f2-saatlik` |
| B. Pano temizliği (sahte motor kaldırılır, kütüphaneler sabit sürümle repoda, boş bölümler) | Lider | `sg-pano` |
| C. Repo adı, Pages, `strateji-test-pano` silme | Kullanıcı | GitHub ayarları |

## A. Codex görevi

### 0. Yasaklar
1. Strateji kartları, `engine/`, `backtests/` ve `paper/portfoy.yaml` satırları değişmez.
2. **Defter yalnız günlük kapanmış barla yazılır.** Saatlik fiyat deftere (`paper/defter/*.csv`) asla girmez; yalnız panodaki "anlık değerleme" alanlarına girer.
3. Uydurma yok. Fiyat alınamazsa son günlük kapanış gösterilir ve `fiyat_kaynagi: "son_kapanis"` yazılır.

### 1. Yarım bar koruması (önce bu; testli)
Sorun: seans açıkken yfinance günlük verisinde bugünün **kapanmamış** barı gelir. `paper/gunluk.py` bunu kesmiyor (`Veri.kes` yalnız `as_of` ile kesiyor, `main` bugünü veriyor). Saatlik çalışmada bu, yarım barla sinyal üretmek, yani ileriye bakmak olur.
- `gunluk.py`'de defter hesabından önce: bir piyasanın son günlük barı, o piyasanın kapanışı + 30 dk (ABD25/EMTIA: 16:00 America/New_York, yaz saati dahil) geçmemişse **atılır**. Hafta sonu ve tatil günleri bundan etkilenmez.
- Test: seans içi bir saat (ör. 2026-10-26 15:00 UTC) ile çağrılınca son barın kullanılmadığını, 21:30 UTC'den sonra kullanıldığını doğrulayan birim test (`tests/test_paper.py`).
- Aynı gün içinde defter hesabı tekrar koşarsa sonuç değişmemeli (idempotent). Bunu da teste ekle: aynı veriyle iki koşu → defterde ek satır yok.

### 2. Anlık değerleme (`paper/anlik.py`, yeni)
- Girdi: defterdeki açık pozisyonlar (`pozisyonlar.csv` son durumu) ve `paper/panel/data.json`.
- Her açık pozisyonun sembolü için son fiyat: yfinance `1h` (ya da `fast_info.last_price`). Zaman damgası da alınır.
- `data.json` güncellenir:
  - `open_positions[*]`: güncel fiyat ve açık kâr;
  - `kpis.total_value`, `kpis.total_return_pct`;
  - `meta`: `updated_at` (UTC), `fiyat_zamani`, `fiyat_kaynagi` (`anlik` ya da `son_kapanis`).
  - Kapanmış işlemler, istatistik ve defter **değişmez**.
- Panoda "anlık değerleme, defter dışı" notu görünmesi için `meta.anlik_not` alanı: `"Açık pozisyonlar saatlik fiyatla değerlenir; işlemler ve defter yalnız günlük kapanışta güncellenir."`

### 3. `paper.yml`
- `schedule: - cron: "17 * * * *"` (her saat :17). `workflow_dispatch` kalır.
- Adımlar:
  1. `gunluk.py --indirme`; yarım bar koruması sayesinde gün içinde yeni işlem üretmez.
  2. `panel.py`.
  3. `anlik.py`.
  4. Defter `paper-defter` dalına.
  5. `data.json` panoya.
- Pano reposu adı tek yerde, ortam değişkeni olarak: `PANEL_REPO: sselimgenc-oss/sg-pano`. Repo yeniden adlandırılınca GitHub eski adı yönlendirir; yine de yeni adı yaz.
- Süre: her saatlik koşu ≤ 10 dk (gerekirse yalnız portföy sembolleri indirilir; zaten öyle).
- Önceki bulgu: `indir()` `--veri-dir`'i yok sayıp varsayılan klasöre indiriyor. Bunu düzelt (parametreyi `fetch_asset`'e geçir) ve test ekle.

### 4. Kabul ölçütü
- `python -m pytest -q` tamamı geçer.
- Yerel prova:
  - `gunluk.py --indirme` + `panel.py` + `anlik.py` art arda çalışır.
  - Seans içi saat simülasyonunda defterde yeni satır oluşmaz.
  - `data.json`'da `meta.fiyat_zamani` dolu.
- PR açıklamasına:
  - prova çıktısı (özkaynak, açık pozisyon sayısı, fiyat zamanı);
  - yarım bar testinin adı;
  - bir saatlik koşunun süresi.

## B. Lider (pano reposu)
- `bot_engine.py` ve saatlik `paper_trader.yml` (sahte motor) kaldırılır. Pano verisi yalnız `sg-arge` paper işinden gelir.
- Tailwind (derlenmiş CSS), Chart.js 4.4.1 ve Lucide sabit sürümle repoya konur; `@latest` ve dev CDN kalkar.
- Henüz gerçek karşılığı olmayan bölümler (gölge mod, koç önerileri, skor kartları, "Sor") sahte rakam göstermez; "henüz veri yok" ve nedeni yazılır.
- `index.html` temel: `sg-test-panel` sürümü (13 sekme, strateji kart/tablo görünümü).

## C. Kullanıcı
1. `sg-test-panel` → Settings → General → Repository name: `sg-pano` → Rename.
2. Settings → Pages: Source "Deploy from a branch", `main` / root (zaten açıksa dokunma).
3. Yeni pano çalıştıktan sonra `strateji-test-pano` → Settings → Delete this repository.
