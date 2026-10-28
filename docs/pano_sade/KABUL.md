# pano-sade — ana panoyu kullanıcı dostu yapma (dal `claude/pano-sade`)

Kaynak: sg-arge `DURUM.md` ve `docs/GOREV_D_YOLU.md` (havuz → aday → oda; kollar: oda / kontrol / taban / elle).

## Yapılanlar
- **Sekmeler:** Özet · Trader'lar · Huni · Ayarlar (telefon öncelikli, sabit üst bant: başlık, sekmeler, "Araştırma / sanal, yatırım tavsiyesi değil").
- **Özet:** hafta x/12, oda doluluğu, kol başına trader sayısı, veri tazeliği ("X dk önce"), son 5 olay. "CT akış" → **Tüm akış**, eski "açık işlemler" şeridi (kayan değil) ve "Kararlarım değer kattı mı?" Özet'te kapalı bölümler olarak durur (sadeleştirildi: açtım/atladım/cevapsız sayıları + atlama nedenleri; kıyas kilitli).
- **Trader'lar:** kol filtresi (Tümü · Oda · Aday · Kontrol · Taban · Elle liste · kol bilinmiyor) ve kartlar: takma ad, tarz, kol, neden seçildi, kırmızı bayraklar, açık işlem sayısı. Sıralama nötr (kol, sonra ad).
- **Trader sayfası:** üstte kimlik + kol + neden seçildi + bayraklar; Hyperliquid ve Hyperdash bağlantıları başlıkta; açık pozisyonlar **tek liste** (canlı veri varsa canlı, yoksa kayıttaki); işlem geçmişi **varsayılan kapalı** (aç/kapa); olaylar, kararlar, seçim ayrıntıları kapalı bölümler. Canlı veri alınamazsa kayıttaki pozisyonlar ve görünür uyarı.
- **Huni:** havuz → aday → oda sayıları, son tarama durumu, aday listesi (eski Keşif). Oda sayısı `kol` alanı yoksa "bilinmiyor".
- **Ayarlar:** tutar hesaplayıcı (aynı) + Sözlük.
- **"?" açıklamaları:** kapı, kol, oda, aday, havuz, kontrol, taban, elle, tarz, gecikme, gölge, hafta, kilitli, bayrak, kayma, tazelik, neden seçildi, sanal kopya.
- **Performans körlüğü:** "Sanal kopya (hepsi)", trader başına sanal kopya getirisi/eğrisi, kol toplamları, kohort ↔ kontrol / açtıklarım ↔ tümü kıyası kaldırıldı → "kilitli · hafta x/12". K/Z rengi (yeşil/kırmızı), "sanal +%" rozet rengi, K/Z'ye göre sıralama (form skoru, 30 dk/2 sa kopya sıralaması) kaldırıldı; tek tek işlem K/Z'si nötr renkle görünür. Rozet ve seri yok.
- Veri kaynakları ve canlı bağlantılar (`CT_KAYNAK`, `CT_KARAR`, `KESIF_KAYNAK`, Hyperliquid `info`) aynı. Chart.js artık kullanılmadığı için sayfadan çıkarıldı (vendor dosyası duruyor).

## Bulunan hata
`#ct/<id>` ayrıntı sayfası, tanımsız `hlDetayYukle…Html` işlevi yüzünden çalışmıyordu; yeni yapıda `#ct/<id>` trader sayfasına yönlenir.

## Veri notları (lider/Codex için)
Veride henüz olmayan, panonun okumaya hazır alanları: trader `kol`, `neden_secildi`, `kirmizi_bayraklar[]`; `golge.{hafta, hafta_toplam, oda_kapasite, oda_n}`; keşifte `havuz`, `aday_sayisi`. Yoksa "bilinmiyor"/"kol bilinmiyor" yazılır (veri sözleşmesi `sg-arge docs/VERI_SOZLESMESI.md` ayrı işte güncellenmeli).

## Kanıt
`once/` ve `sonra/`: masaüstü (1440×900) ve telefon (390×844) ekran görüntüleri. Testler: `node test/pano.test.js`, `node ofis/test/replik.test.js`, `node ofis/test/ui.test.js`.
