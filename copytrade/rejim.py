"""rejim.py - Piyasa Rejimi Etiketleme ve Özetleme Modülü.

Hyperliquid copy trade araştırması Faz 3 kapsamında, BTC günlük kapanışlarından
piyasa rejimlerini (yukselis, dusus, yatay, sok) belirler ve rejim bazlı getiri
özetini hesaplar.

Yalnızca Python 3.12 + pandas + numpy kullanılır.
Ağ ve dosya okuma/yazma içermez.
"""

import numpy as np
import pandas as pd


def rejim_etiketle(
    kapanis: pd.Series,
    pencere_gun: int,
    getiri_esik: float,
    sok_yuzdelik: float,
    yuzdelik_pencere_gun: int,
) -> pd.Series:
    """Tarih indeksli günlük kapanış verilerine göre piyasa rejimini etiketler.

    Parametreler
    ------------
    kapanis : pd.Series
        Tarih indeksli (UTC, artan sırada) günlük kapanış fiyatları.
    pencere_gun : int
        Getiri ve oynaklık hesabı için geriye dönük pencere boyutu (gün sayısı).
    getiri_esik : float
        Yükseliş ve düşüş rejimlerini ayıran getiri eşiği (ör. 0.10 -> %10).
    sok_yuzdelik : float
        Şok tespiti için oynaklık yüzdeliği eşiği (0.0 ile 1.0 arası, ör. 0.90).
    yuzdelik_pencere_gun : int
        Oynaklık dağılımı yüzdeliğinin hesaplanacağı geriye dönük pencere boyutu.

    Döndürür
    --------
    pd.Series
        Aynı indekse sahip, değerleri 'yukselis' | 'dusus' | 'yatay' | 'sok' | None
        olan etiket serisi. Yeterli geçmiş yoksa değer None'dır.
    """
    if not isinstance(kapanis.index, pd.DatetimeIndex):
        raise TypeError("kapanis serisinin indeksi pd.DatetimeIndex olmalıdır.")
    if not kapanis.index.is_monotonic_increasing:
        raise ValueError("kapanis indeksi zaman bakımından artan sırada olmalıdır.")
    # Lider (2026-10-28): pencereler satır sayısıyla kaydırılır; boşluklu seride "30 gün" 30 satır olur. Günlük ve boşluksuz zorunlu.
    if len(kapanis) > 1 and not (kapanis.index.to_series().diff().dropna() == pd.Timedelta(days=1)).all():
        raise ValueError("kapanis günlük ve boşluksuz olmalıdır (eksik gün var).")
    if pencere_gun < 2:
        raise ValueError("Standart sapma hesabı için pencere_gun en az 2 olmalıdır.")
    if yuzdelik_pencere_gun < 1:
        raise ValueError("yuzdelik_pencere_gun en az 1 olmalıdır.")
    if not (0.0 <= sok_yuzdelik <= 1.0):
        raise ValueError("sok_yuzdelik 0.0 ile 1.0 arasında bir değer olmalıdır.")

    # 1. Pencere basit getirisi: P_t / P_{t - pencere_gun} - 1
    # Yalnızca geriye dönük shift kullanılır (geleceğe bakma yok).
    pencere_getirisi = kapanis / kapanis.shift(pencere_gun) - 1.0

    # 2. Günlük log getiriler: ln(P_t / P_{t-1})
    log_getiri = np.log(kapanis / kapanis.shift(1))

    # 3. Gerçekleşmiş oynaklık: pencere_gun boyutundaki günlük log getirilerin
    # örneklem standart sapması (ddof=1).
    oynaklik = log_getiri.rolling(
        window=pencere_gun, min_periods=pencere_gun
    ).std(ddof=1)

    # 4. Oynaklık eşiği: oynaklık serisinin son yuzdelik_pencere_gun içindeki
    # dağılımının sok_yuzdelik yüzdeliği (quantile).
    oynaklik_esigi = oynaklik.rolling(
        window=yuzdelik_pencere_gun, min_periods=yuzdelik_pencere_gun
    ).quantile(sok_yuzdelik)

    # 5. Yeterli geçmiş kontrolü: getiri ve oynaklık eşiği her ikisi de hesaplanabilmelidir.
    gecerli = pencere_getirisi.notna() & oynaklik.notna() & oynaklik_esigi.notna()

    # 6. Rejim koşulları (Öncelik: Şok > Yükseliş / Düşüş > Yatay)
    kosullar = [
        gecerli & (oynaklik > oynaklik_esigi),
        gecerli & (pencere_getirisi > getiri_esik),
        gecerli & (pencere_getirisi < -getiri_esik),
        gecerli,
    ]
    secimler = ["sok", "yukselis", "dusus", "yatay"]

    sonuc = np.select(kosullar, secimler, default=None)
    return pd.Series(sonuc, index=kapanis.index, dtype=object)


def rejim_ozeti(etiket: pd.Series, getiri: pd.Series) -> pd.DataFrame:
    """Etiket ve getiri serilerini rejim bazında gruplayarak özet metrikleri hesaplar.

    Parametreler
    ------------
    etiket : pd.Series
        Piyasa rejim etiketleri ('yukselis', 'dusus', 'yatay', 'sok' veya None).
    getiri : pd.Series
        İlgili günlere ait getiri serisi (ör. strateji veya copy trade getirisi).

    Döndürür
    --------
    pd.DataFrame
        İndeksi rejim adı, sütunları 'gun_sayisi', 'ortalama' ve 'medyan' olan özet tablo.
    """
    df = pd.DataFrame({"etiket": etiket, "getiri": getiri})
    # None veya NaN olan etiket/getiri satırları özete katılmaz
    gecerli = df.dropna(subset=["etiket", "getiri"])

    ozet = gecerli.groupby("etiket")["getiri"].agg(
        gun_sayisi="count",
        ortalama="mean",
        medyan="median",
    )
    ozet["gun_sayisi"] = ozet["gun_sayisi"].astype(int)
    return ozet