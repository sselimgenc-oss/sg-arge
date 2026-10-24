# F2-GÖLGE: Kripto 4H trend gölge kitabı (canlı, paper)

**Karar:** kullanıcı, 2026-10-24. `results/U4_SONUC.md` bölüm 3, seçenek (b).
**Sahip:** Codex. **Denetim:** lider.

## Amaç
U4'te kripto 4H trend kartı U4-H1 IS ve OOS'ta kârlıydı ama kapılarda elendi (MDD95 %28, DSR, kardeş). Kilitli dönemi harcamadan, kartı **canlı veride, ana portföyden ayrı bir gölge kitapta** izlemek.

## Tanım (sabit; sonuca bakılarak değişmez)
- **Kart:** `U4-H1`, değiştirilmeden. `tf: 4H`, 1H Binance verisinden UTC 00/04/08/12/16/20 kovalarıyla.
- **Evren:** yalnız çekirdek 6 coin: BTC, ETH, SOL, BNB, XRP, TRX (USDT, spot).
- **Boyut:** işlem başı risk **%0,25** (ana portföyün yarısı), toplam açık risk %1, kitap brütü %100, kaldıraç yok.
- **Maliyet:** tek yön %0,15 (KRIPTO25).
- **Sermaye:** ayrı, 5.000 USD sanal. **Ana portföy özkaynağına, alarmlarına ve DURDUR kuralına karışmaz.**
- **Başlangıç:** kitap **canlı başlar** (`baslangic` = birleştirme günü, UTC). **Geriye dönük doldurma yapılmaz:** 2025-10-01 sonrası kilitli dönemdir; orayı doldurmak kilidi dolaylı yoldan açmak olur. Göstergelerin ısınması için geçmiş veri kullanılır, işlem açılmaz.
- **Alarm (yalnız bilgi):** gölge kitap MDD ≥ %15 olursa panoda uyarı. Durdurma kararı kullanıcınındır.

## Yapılacaklar (Codex)
1. `paper/portfoy.yaml`'a ayrı bir `golge:` bölümü. Örnek: `{id: U4-H1, piyasa: KRIPTO25, tf: 4H, semboller: [...6...], risk: 0.0025, sermaye: 5000, baslangic: <gün>}`. `gunluk.py` bu bölümü ana satırlardan **ayrı** koşar ve ayrı deftere yazar: `paper/defter/golge/*.csv`, aynı ekleme-yalnız kurallar.
2. **Veri:** kripto 1H Binance (`data/fetch.py`, `--append`). Saatlik koşuda yalnız 6 coin indirilir.
3. **Yarım bar koruması (4H):** içinde bulunulan 4 saatlik kova kapanmadan o 4H bar kullanılmaz. Kova kapanışı + 5 dk sonrası kapanmış sayılır. Test zorunlu: kova içi bir saatte son 4H barın atıldığını, kapanıştan sonra kullanıldığını doğrula.
4. **Pano:** `paper/panel.py` `data.json`'a ayrı bir `golge` anahtarı ekler: özkaynak, açık pozisyonlar, kapanmış işlemler, MDD, başlangıç tarihi ve "gölge kitap: ana portföyden ayrı, kilitli dönem kullanılmadı" notu. Ana `kpis` değişmez.
5. `paper.yml` aynı saatlik iş içinde gölge kitabı da koşar. Süre sınırı 10 dk aşılmamalı.

## Kabul
- `pytest -q` tamamı geçer. Yeni testler: yarım 4H bar, ayrı defter, ana özkaynağa etki yok, geriye dönük işlem yok (başlangıçtan önce dolum yok).
- Yerel prova: gölge kitap boş defterle başlar; ilk koşuda yalnız başlangıç sonrası barlar işlenir.
- PR `[F2] gölge kitap: kripto 4H trend`. Açıklamada prova çıktısı.

## Pano reposu (lider)
`sg-pano/index.html`'e "Gölge kitap" sekmesi lider tarafından eklenir: `data.json` `golge` anahtarı, ana portföyden ayrı gösterilir.
