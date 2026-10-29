# Ofis izometrik tema — üç aday karşılaştırması (2026-10-29, lider yetkisi devredilmiş denetçi: Sonnet)

`docs/GOREV_OFIS_TEMA.md` Sürüm 1 için üç aday geldi: Codex (sg-pano PR #37), Sonnet (sg-pano PR #38, bu belgeyi
yazan), Argon (`arastirma/ofis_tema/argon/`, tek dosya HTML). Aşağıdaki ölçütlerle karşılaştırıldı; sonuçta Sonnet
temel alındı, Codex'ten iki gerçek kazanım (gerçek `saglik.isik` alanı, referans görselin yalnız izometrik temada
yüklenmesi) PR #38'e taşındı, Argon mimari olarak temel alınamadı (gerekçe aşağıda).

## Ölçüt tablosu

| Ölçüt | Codex (#37) | Sonnet (#38) | Argon |
|---|---|---|---|
| Oda bölgelerinin görsele oturması | İyi (9 bölge, elle hizalanmış) | İyi (9 bölge, elle hizalanmış) | İyi (`?bolge=1` hata ayıklama modu var — geliştirici aracı olarak değerli fikir) |
| 390 px telefonda okunurluk/akıcılık | İyi; `fitFrame()` ile görsel konteynerı tam dolduruyor | **Düzeltme öncesi zayıf** (CSS `aspect-ratio` + `width:100%`, konteyner oranı farklıysa boşluk kalıyordu) → **düzeltildi**: JS ile `contain-fit` hesaplanıyor, artık Codex'le eşdeğer | İddialı (360/390/768/1280 px test matrisi), ama bağımsız dosya — ofis'in gerçek telefon düzenine (sol menü, kart sütunu, panel) hiç entegre değil |
| Açılışta görsel ekranı doldursun | Evet | Düzeltmeden önce hayır (bkz. yukarı) → şimdi evet | Tek başına sayfa olduğu için ölçüt bu bağlamda uygulanamaz |
| Rozet verisinin doğruluğu (gerçek `durum.json` ile) | **Oda rozeti `t.saglik.isik` kullanıyor — gerçek alan, canlı veriyle anlamlı** (bugün: 18 oda traderından 🟢2 🟡10 🔴6). Risk rozetindeki "kalabalık" kontrolü `oda.kapasite` üzerinden; `gercek.js` bu alanı hiç doldurmadığından gerçek veride hep sessiz kalıyor (zararsız ama işlevsiz kod) | **Düzeltme öncesi hatalı**: Oda rozeti yalnız `lik_uzaklik`'e bakıyordu; gerçek veride `acik_islemler` her zaman boş olduğundan (SEMA.md §9: "açık/kapanan işlem... boştur") her trader sessizce **yeşil varsayılıyordu** — sahte "herkes sağlıklı" izlenimi. → **düzeltildi**: önce `t.saglik.isik` (gerçek alan, `gercek.js` zaten taşıyor), yoksa `lik_uzaklik`, o da yoksa "veri yok" (sayı uydurulmadan). Aynı sağlıklı öncelik artık Sonnet'te de var. Risk'teki kalabalık notu da yalnız kapasite bilinen kaynakta (örnek veri) gösteriliyor — gerçek veride sessiz, Codex'teki gibi | Veri doğru kaynaktan (`copytrade-izleme/izleme/durum.json`) okunuyor, ama **`sanal_kopya.getiri` oranını yüzdeymiş gibi** okuyordu (lider düzeltmesi sonradan uygulandı — bkz. not). Üstelik `ofis/gercek.js`'i hiç kullanmıyor; `copytrade-kapi` seçim/kapı zincirini atlıyor |
| Sahte veri yok (veri yoksa "bilinmiyor"/"veri yok") | Uyuyor | Düzeltme sonrası uyuyor (yukarıdaki düzeltme bunun bir parçası) | Niyeti doğru (varsayımlar README'de açık yazılmış) ama en az bir varsayım (getiri) yanlıştı; bu da "sahte veri yok" ilkesini dolaylı ihlal ediyordu |
| Tema seçimi ve klasiğe dönüş | `localStorage` + `?tema=`; sorunsuz | `localStorage` + `?tema=`; sorunsuz | Yok (tema kavramı yok, zaten ayrı sayfa) |
| **Oda içi görünüm, panel, olay çekmecesi ortaklığı** (görev belgesi kuralı) | **Kısmi**: panel/kart açılıyor (paylaşılan DOM) ama oda içine girince klasik piksel sahnesi (aktörler, tıklanabilir nesneler) hiç açılmıyor — `#tuval` izometrik temada kalıcı olarak gizli, oda içinde de yalnız statik görselin yakınlaştırılmış hâli gösteriliyor. Yani izometrik temada bina içine "girilmiyor", sadece resim yakınlaşıyor | **Tam**: `#tuval` yalnız bina genel görünümünde gizli; bir odaya girilince (`body.oda-ici`) klasik piksel oda-içi sahnesi (aktörler, nesneler, tıklama) aynen açılıyor — görev belgesindeki "oda iç görünümü iki temada ortaktır" cümlesi birebir karşılanıyor | Yok (paylaşılacak bir oda-içi/panel mimarisi zaten yok) |
| Testler | `tema.test.js` + `tema_ui.test.js` (Playwright); kendi notunda da `ui.test.js`'teki 4 ön var olan başarısızlığı (3 kilit + 1 favicon) doğru tespit etmiş | `tema.test.js` (Playwright, 36 kontrol); `ui.test.js`/`gercek*.test.js`/`replik.test.js` regresyonsuz çalıştırıldı | Yok (README'de "headless Chromium ile doğrulandı" deniyor ama repoda test dosyası yok) |
| `gercek.js` / `SEMA.md` dokunuldu mu | Hayır | Hayır | Kullanılmıyor bile (ayrı veri yolu) |
| Mimari risk | `main.js`'in çizim döngüsüne (`step()`, `enterRoom`, `exitRoom`, `goBuilding`, `zoomBy`) doğrudan müdahale — paylaşılan dosyada 7 ayrı değişiklik noktası, bakım yükü yüksek | Paylaşılan dosyalara (`main.js`, `office.js`, `world.js`, `sprites.js`, `px.js`, `panel.js`) **sıfır dokunuş**; tema seçimi yalnız görünürlük (CSS/`hidden`) ve sol menü düğmesini programatik tıklamakla çalışıyor | Bağımsız dosya; ofis'e entegre etmek pratikte yeniden yazım gerektirir |

**Not — Argon'un `sanal_kopya.getiri` varsayımı:** Argon README'si hâlâ "yüzde cinsinden (12.4 → +%12,4)" diyor; gerçek
`durum.json`'da bu alan **oran** (`-0.0018` gibi; ör. `-%0,18`), lider bunu düzelmiş olarak bildirdi. Doğrulamak için
bugünkü canlı `durum.json` çekildi: `sanal_kopya.getiri` değerleri `-0.0018 … +0.09` aralığında — gerçekten oran,
Argon'un ilk varsayımı (zaten düzeltilmiş) yanlıştı. Sonnet/Codex bu alanı hiç kullanmıyor (ön kayıt körlüğü, kasa
getirisi `gercek.js`'in kendi `kasa.deger_usd/baslangic_usd` hesabından geliyor), o yüzden bu hata PR'lara taşınmadı.

## Canlı veri ile doğrulama (2026-10-29, `copytrade-izleme/izleme/durum.json`)
- 61 trader, hepsinde `saglik.isik` var; `kol`/`kollar` içinde `"oda"` geçen 18 trader: 🟢2 🟡10 🔴6.
- Üst düzey `kalabalik` nesnesi gerçekten var (`{n_oda, uyari, uyari_metni, ...}`) ama **`ofis/gercek.js` bunu
  ofis veri modeline hiç aktarmıyor** — ne Codex ne Sonnet gerçek `kalabalik` alanını okuyabiliyor; ikisi de yalnız
  `katlar.oda.kapasite` üzerinden yaklaşık bir "kalabalık" notu deniyor, ki bu alan da gerçek veride her zaman
  `null` (`gercek.js` satır 83: `kapasite: null`). Yani **"kalabalık uyarısı" sürüm 1'de gerçek veride hiçbir
  adayda çalışmıyor** — bu, `gercek.js`'e dokunmadan (görev belgesi kuralı) çözülemeyen bilinen bir sürüm 1
  sınırı; sürüm 2 ya da ayrı bir `gercek.js` görevi için not düşüldü.

## Karar
**Temel: Sonnet (#38).** Gerekçe: tek gerçek mimari fark olan "oda içi görünüm iki temada ortak" kuralını
yalnız Sonnet tam karşılıyor (Codex'te oda içine girince hâlâ düz resim gösteriliyor, aktör/nesne etkileşimi
kayboluyor); paylaşılan dosyalara dokunmadığı için bakım riski de daha düşük. Codex'in gerçekten daha iyi olduğu
iki nokta (telefon doldurma/`contain-fit` ve `saglik.isik` alanının kullanımı) PR #38'e taşındı; ikisi de şimdi
eşdeğer ya da üstün. Argon mimari olarak temel alınamadı (ayrı dosya, `gercek.js`/panel/oda-içi mimarisi yok,
bir varsayım hatalıydı) ama `?bolge=1` hata ayıklama fikri ve geniş ekran test matrisi notu kayda değer; sürüm 2
çalışmasında hatırlanabilir.

PR #37 (Codex) bu nedenle **kullanılmıyor**; PR açıklamasına "yerine #38" notu düşülüp kapatılacak. PR #38
(Sonnet), yukarıdaki düzeltmelerle güncellendi ve birleştirildi.
