# Sonnet parti 2 erişim notları (T35-P2, 2026-10-23)

Ortam: Claude Code bulut kapsayıcısı (proxy). Keşif için WebSearch, `curl` ve sitelerin kendi açık API'leri (Qiita, note.com, velog GraphQL, Discourse JSON, Blogger feed). Bu partide parti 1'de kapalı görünen birkaç kaynağa API üzerinden ulaşıldı.

| Site | Ne denendi | Sonuç |
|---|---|---|
| bigquant.com `square/paper/*` | WebSearch (alan adı filtreli) + `curl` | **Açıldı.** Broker araştırma raporları metin olarak okunuyor: 东证期货, 西部证券, 海通证券, 国信证券, 天风证券, 渤海证券, 开源证券. 7 kayıt buradan. `wiki/doc/*` bazı sayfaları JS ile yükleniyor (örn. 打板追涨停 sayfası boş döndü). |
| note.com | `curl`; kamuya açık `api/v3/hashtags/<etiket>/notes` ve `api/v3/notes/<key>` | **Açıldı.** Liste yanıtları yalnız ilk ~240 karakteri veriyor; tam gövde `notes/<key>` ile alınıyor. ~4200 notun başlıkları tarandı, ücretsiz olanlar gövdeyle süzüldü. 4 JP kaydı buradan. |
| qiita.com | `curl`, `api/v2/items` | Açıldı; arama sonucu az, bu partide yeni kayıt çıkmadı. |
| zenn.dev | `curl` | Açıldı, bu partide yeni kayıt çıkmadı. |
| ameblo.jp | `curl` | Açıldı (cfpurawa Nikkei 225 vadeli blogu). Metin var, performans rakamı yok. |
| velog.io | `v2.velog.io/graphql` `searchPosts` | **Açıldı.** Arama tek kelimelik anahtarla çalışıyor; gövde ilk 8000 karakterle sınırlı. Kore blog kaydı çıkmadı (kayıtlar ABD hissesi, yinelemeli deney günlüğü ya da dönemsiz). |
| tistory.com, brunch.co.kr | WebSearch alan adı filtresi | Arama sonucu boş ya da ilgisiz. Sayfalara doğrudan gidilemedi. |
| thebook.io | `curl` | **Açıldı** (Kiwoom kitabı bölümleri). KR-003 buradan. Kullanım şartı içeriği çoğaltmayı yasakladığı için kayıtta yalnız bilgi özeti var. |
| moonshotreport.blogspot.com | `curl` ve Blogger feed (`feeds/posts/default?alt=json`) | **Açıldı.** KR-004a/b buradan. Feed'de ayrıca ABD büyük hisse momentum raporu var (Codex bölgesi, alınmadı). |
| tradingqna.com | Discourse `search.json` ve `t/<id>.json` | **Açıldı.** Arama bu partide ~50 başlık verdi; rakamlı olanlardan IN-003 çıkarıldı. 920 straddle analizi (id 130677) rakamlar görselde, metinde yok, elendi. |
| marketcalls.in | WordPress `wp-json/wp/v2/posts?search=` ve `curl` | **Açıldı.** Nautilus Trader serisi (Parça 1-3) tam metin. IN-004 buradan. Parça 3 (6 hisse, iki strateji) negatif sonuç verdiği için kayıt dışı. |
| intradaylab.com | `curl` | Parti 1\'de alındı (IN-002). |
| joinquant.com | `curl` | Parti 1\'deki gibi Çin dışı IP engeli. Denenmedi. |
| zhihu.com, medium.com, wikidocs.net | parti 1\'de 403/Cloudflare | Bu partide yeniden denenmedi. |
| tradetron.tech blog | `curl` | Metin açılıyor; rakamlı strateji sonucu yok (parti 1\'de de elenmişti). |
| github.com | oturum kapsamı | Oturumun GitHub kapsamı yalnız `sg-arge`; başka depolar okunmadı. KIS API bot örnekleri ve Upbit VB depoları bu yüzden kapalı. |
| scienceon.kisti.re.kr, kci.go.kr | `curl` | Açıldı; KOSPI200 gece vadelisi/gün içi akademik çalışmaların yalnız özeti var, rakam yok (elendi). |
| financewithsai.com | `curl` | Açıldı; Nifty gün içi ayar, sonuçlar videoya bağlı. Elendi. |

## Elenenler (kapıdan dönen adaylar)

| Aday | Neden |
|---|---|
| rakuenfx USDJPY 2021-2025 (note) | Kural yalnız "MA ile 4H/1H trend takibi" (işlem tablosu görsel). PF 4.4-6.5, yılda 18-26 işlem. Strateji tanımsız. |
| cfpurawa Nikkei 225 range breakout (ameblo) | Yalnız tarif, rakam yok; serbest yorumlu işlem. |
| takezo75 Nikkei 225 otomatik sistem (note) | "4 yıl BT PF 1.57, 825 işlem" var ama kural yok (seri tanıtımı). |
| icekingkling "【検証】…試した結果" serisi (note) | Başkasının yönteminin üçüncü kişi sınaması, sonuçlar çoğunlukla olumsuz; kârlılık iddiası yok. |
| Nautilus Parça 3 (Marketcalls) | İki strateji, altı hisse: Keltner CAGR %0.52, ortalamaya dönüş -%2.62; kârlılık iddiası yok. |
| 920 short straddle analizi (TradingQnA 130677) | Rakamlar görselde; metinde yalnız "1300 işlem / son 5 yıl" ve "üst %10 işlem çıkarılırsa toplam negatif". |
| thebook.io dışındaki Kore kaynakları (velog asdf7994 deney günlüğü, homiru VB, dev_dreamer çift momentum, Chuseok mevsimselliği) | ABD hissesi ya da ETF'i (Kore dışı), sonuç görselde, olay çalışması (strateji yok) ya da dönemsiz. |
| miningrealtruth Bitcoin VB (Blogger, systrader79 alıntısı) | Yıllık getiri 34.1/67.2/96.7 (risk kuralına göre) ve maliyet %0.15 var ama dönem yazılı değil; Kore için tarihli dönem şartı. |
| Qiita yoggydev "50 FX yöntemi öldürdüm" | Olumsuz sonuç (hepsi elendi). |
| BigQuant 打板追涨停 (wiki) | JS sayfası boş; yıllık %82.43 / MDD -20.74% yalnız arama özetinde (2024-09 – 2025-03, 6 ay, T+1 hisse). |
