# Worker yedek tetikleme — GitHub token kurulumu (telefondan)

GitHub'ın kendi zamanlayıcısı bu repoda saatlik/15 dakikalık koşuları sık atlıyor. Telegram Worker'ına (zaten her 5
dakikada bir çalışıyor) bir yedek eklendi: `izleme.yml`'i saatte bir, `arsiv.yml`'i 15 dakikada bir, **yalnız o iş
akışının çalışan/sıradaki bir koşusu yoksa ve son biten koşusu (sonucu ne olursa olsun) beklenenden eskiyse** kendisi tetikler. GitHub'ın
kendi zamanlayıcısı yedek olarak çalışmaya devam eder; ikisi çakışmaz (Worker önce kontrol eder).

Bunun çalışması için GitHub'a "bu repoda iş akışı başlat" izni veren bir **ince taneli token** gerekir. Aşağıdaki
adımlar telefonda GitHub uygulaması ya da tarayıcısından yapılabilir.

## 1. Token oluştur
1. GitHub'da sağ üstteki profil resmine dokun → **Settings**.
2. Sayfayı aşağı kaydır, soldaki menüden **Developer settings** (en altta).
3. **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
4. **Token name**: `sg-arge-worker-tetikleme` gibi tanıdık bir ad yaz.
5. **Resource owner**: kendi hesabın (sselimgenc-oss) seçili kalsın.
6. **Repository access**: **Only select repositories** seç, listeden yalnız **sg-arge**'ı işaretle. (Başka hiçbir
   repoya erişimi olmasın.)
7. **Permissions** → **Repository permissions**'ı aç, **Actions** satırını bul, sağındaki açılır menüden
   **Read and write** seç. Başka hiçbir izni açma.
8. **Expiration** (süre) istersen uzun bir tarih seç (token süresi dolunca otomatik tetikleme sessizce durur, hiçbir
   şey bozulmaz — gerektiğinde yenisi oluşturulur).
9. En alttaki **Generate token** düğmesine dokun.
10. Açılan token metnini (`github_pat_` ile başlar) kopyala. **Bu ekrandan ayrılınca bir daha gösterilmez.**

## 2. Token'ı GitHub Secret olarak ekle
1. sg-arge reposuna git → **Settings** (repo ayarları, hesap ayarları değil) → soldaki menüden **Secrets and
   variables** → **Actions**.
2. **New repository secret** düğmesine dokun.
3. **Name**: tam olarak `TETIK_TOKEN` yaz (büyük/küçük harf önemli; GitHub `GITHUB_` ile başlayan ada izin vermez).
4. **Secret**: 1. adımda kopyaladığın token'ı yapıştır.
5. **Add secret** ile kaydet.

## 3. Devreye alma
Bir şey yapmana gerek yok — bir sonraki Worker dağıtımında (`worker/**` dosyalarına her push'ta otomatik çalışır,
ya da Actions sekmesinden **Telegram Worker dağıtımı** iş akışını elle çalıştırabilirsin) token Worker'a secret
olarak aktarılır ve yedek tetikleme kendiliğinden açılır.

## Durumu kontrol etme
Telegram botuna `/durum` yaz: en altta token yoksa "🔁 Otomatik tetikleme: kapalı (GITHUB_ACTIONS_TOKEN secret'ı
yok)" notu görünür; token varsa bu not hiç çıkmaz (sessizce çalışıyordur).

## Token'ı iptal etme
Settings → Developer settings → Fine-grained tokens → token'ın yanındaki **Delete**. Worker bir sonraki
kontrolünde GitHub'dan hata alır, sessizce o turu atlar; repo Secrets'tan da `TETIK_TOKEN`'ı silersen
Worker hiç denemez.
