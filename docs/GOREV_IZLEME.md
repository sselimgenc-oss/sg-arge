# Görev: copy trade izleme motoru ve Telegram bildirimi (2026-10-27)

Yapan: **Codex**. Dal: `codex/izleme` (`main`'den). Durum: `docs/codex_durum_izleme.md`. Önce `AGENTS.md`,
`DURUM.md`, **`docs/VERI_SOZLESMESI.md`** (bağlayıcı) ve `docs/PANO_COPYTRADE.md` oku. Sözleşmeyi değiştirme;
gerekirse dur ve durum dosyasına yaz. Sonucu değiştirmeyen teknik ayrıntıyı kendin seç, bir satır not düş.
Yalnız herkese açık Hyperliquid verisi; emir, cüzdan, gerçek para yok.

## İş A — izleme motoru (önce bu)
1. **İzleme listesi:** `copytrade/izleme_listesi.yaml` (main'de MEVCUT, 2 test trader; biçimi koru) — `id, adres, takma_ad, durum (kopyala|izlemede|durdu), t0`.
   Listeyi lider/kullanıcı doldurur; başlangıçta boş olabilir (motor boş listede de çalışır ve geçerli dosya yazar).
2. **İş akışı** `.github/workflows/izleme.yml`: `schedule` **saatte bir** + `workflow_dispatch` (lider kararı
   2026-10-27, Argon notu: Actions zamanlaması 10–60 dk gecikebilir; hızlı bildirim İş B'de Cloudflare'de olacak). Sonuç ve durum
   dosyaları `copytrade-izleme` dalına (yoksa yetim dal açılır; `main` büyümez). Eşzamanlılık grubu, push'ta
   `git pull --rebase` ile 3 deneme.
3. **Her koşuda, her trader için:** `clearinghouseState` (açık pozisyonlar, hesap değeri); son koşudan beri
   `userFillsByTime` (durum dalında trader başına son dolum zamanı tutulur, artımlı); günde bir `portfolio` (kâr eğrisi).
   `copytrade/tarama.PublicClient` ve `RateLimiter` kullan.
4. **Olaylar** (sözleşme §2): açılış, kapanış, büyütme/azaltma (> %25), ışık değişimi; kalıcı tekil `id`.
5. **Sanal kopya:** t0'dan itibaren, 30 dk gecikmeli, maliyetli — `copytrade/kapi.delayed_copy` ile aynı hesap
   (canlıda 1 dk mum yeterli: son 5.000 dakika). Defter durum dalında birikir.
6. **Sağlık ışığı ve form:** sözleşme §3; `pano/saglik.py` (blok bootstrap konisi, CUSUM) yeniden kullanılır. Koni
   t0 öncesi günlük PnL'den.
7. `izleme/durum.json` sözleşme şemasına tam uyar (şema testi: `izleme/ornek_durum.json` ile aynı anahtarlar/türler).

## İş B — Telegram (BAŞLAMA: Cloudflare Worker'a taşınıyor; ayrı görev belgesi gelecek)
Aşağıdaki maddeler yalnız bilgi içindir. Argon notu: düğme cevapları (`answerCallbackQuery`) birkaç saniyede
verilmeli; 10 dakikalık `getUpdates` çalışmaz. Hızlı katman (5 dk'da bir pozisyon kontrolü, bildirim, düğmeler,
karar kaydı) Cloudflare Worker + KV olacak; İş A yalnız saatlik ağır hesap ve `durum.json`.
- Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Yoksa iş B adımları atlanır, iş A çalışmaya devam eder.
- Aynı 10 dakikalık işte: yeni olaylar sözleşme §5 metniyle gönderilir; gönderilen `olay.id`'ler durum dalında
  tutulur (tekrar yok). Açılış/büyütmede inline düğmeler: `[Açtım] [Atladım]`; Atladım → neden düğmeleri.
- Cevaplar `getUpdates` ile aynı işte okunur → `izleme/kararlar.jsonl` (sözleşme §4; tutar/isim yok).
  `callback_data` = `olay_id|karar|neden` (64 bayt sınırına dikkat; gerekirse kısa kod tablosu).
- Anahtar hiçbir günlüğe, dosyaya, hata mesajına yazılmaz.

## Testler (ağsız, sabit örnek yanıtlarla)
Olay üretimi (açılış/kapanış/%25 eşiği, tekil id); artımlı dolum okuma; sanal kopya maliyeti ve gecikmesi; ışık
kuralları (her koşul için örnek); şema uyumu; boş liste; Telegram mesaj metni ve düğme verisi; tekrar göndermeme;
karar kaydının biçimi.

## Bitirirken
`python -m pytest -q`, `git push -u origin codex/izleme`, PR `[CT] izleme motoru`. İş akışının zamanlaması
birleştirmeden sonra `main`'de çalışır; dalda `workflow_dispatch` ile değil push tetiğiyle bir kez dene.
