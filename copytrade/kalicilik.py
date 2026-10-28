"""
Modül: kalicilik.py
Trader performansının kalıcılığını (rank persistence) kayan pencerelerde
ve hareketli blok bootstrap yöntemiyle analiz etmek için temel fonksiyonlar.

Yalnızca Python 3.12+ standart kütüphanesi, pandas ve numpy kullanır (scipy içermez).
Ağ ve dosya okuma/yazma işlemi içermez.
"""

from typing import Dict
import numpy as np
import pandas as pd


def spearman(x: pd.Series, y: pd.Series) -> float:
    """İki seri arasındaki Spearman sıra korelasyonunu hesaplar.

    Kurallar:
    - Seriler ortak indekslerine göre iç birleşimle hizalanır.
    - Eksik (NaN) değerler ayıklanır.
    - Eşit değerlerde ortalama sıra (average rank) yöntemi uygulanır.
    - Sıraların Pearson korelasyonu hesaplanır.
    - Geçerli veri çifti < 2 ise veya serilerden birinin sıraları sabitse
      (varyans = 0) NaN döner.
    """
    df = pd.concat([x.rename("x"), y.rename("y")], axis=1, join="inner").dropna()
    if len(df) < 2:
        return float("nan")

    rx = df["x"].rank(method="average")
    ry = df["y"].rank(method="average")

    vx = rx.var()
    vy = ry.var()
    if vx == 0 or vy == 0 or np.isnan(vx) or np.isnan(vy):
        return float("nan")

    r = rx.corr(ry, method="pearson")
    return float(r)


def pencere_kaliciligi(puan: pd.DataFrame, getiri: pd.DataFrame) -> pd.DataFrame:
    """Kayan pencereler boyunca trader puanları ile sonraki dönem getirileri

    arasındaki Spearman sıra korelasyonunu hesaplar.

    Parametreler:
    - puan: satır = pencere başlangıç tarihi, sütun = trader adresi.
    - getiri: satır = pencere başlangıç tarihi, sütun = trader adresi.

    Çıktı:
    - pd.DataFrame: Satırlar = pencere başlangıç tarihleri,
                    Sütunlar = ['n', 'spearman']
      (ortak ve geçerli adres sayısı n < 3 olan pencerelerde spearman = NaN döner).
    """
    results = []
    for dt in puan.index:
        if dt not in getiri.index:
            results.append({"n": 0, "spearman": float("nan")})
            continue

        p_row = puan.loc[dt]
        g_row = getiri.loc[dt]

        # Ortak adres sütunları
        common_cols = p_row.index.intersection(g_row.index)
        valid = pd.DataFrame(
            {"p": p_row[common_cols], "g": g_row[common_cols]}
        ).dropna()
        n = len(valid)

        if n < 3:
            sp = float("nan")
        else:
            sp = spearman(valid["p"], valid["g"])

        results.append({"n": n, "spearman": sp})

    df_out = pd.DataFrame(results, index=puan.index)
    df_out["n"] = df_out["n"].astype(int)
    df_out["spearman"] = df_out["spearman"].astype(float)
    return df_out


def blok_bootstrap_ortalama(
    degerler: pd.Series, blok: int, tekrar: int, tohum: int, alfa: float
) -> Dict[str, float]:
    """Pencereler arası ortalama Spearman korelasyonu için Hareketli Blok

    Bootstrap (Moving Block Bootstrap - MBB) yöntemiyle güven aralığı hesaplar.

    Parametreler:
    - degerler: Pencere bazlı Spearman korelasyon katsayıları serisi.
    - blok: Blok uzunluğu (pencereler arası otokorelasyon yapısını korumak için).
    - tekrar: Bootstrap yineleme sayısı.
    - tohum: Tekrarlanabilirlik için rastgelelik tohumu (seed).
    - alfa: Anlamlılık düzeyi (örn. 0.05 -> %95 güven aralığı).

    Çıktı:
    - dict: {"ortalama": float, "alt": float, "ust": float, "n": int}
    """
    temiz = degerler.dropna()
    n = len(temiz)
    if n == 0:
        return {
            "ortalama": float("nan"),
            "alt": float("nan"),
            "ust": float("nan"),
            "n": 0,
        }

    ortalama = float(temiz.mean())
    b = max(1, min(int(blok), n))
    num_blocks = int(np.ceil(n / b))

    rng = np.random.default_rng(tohum)
    # Üst üste binen (overlapping) blok başlangıç indeksleri: [0, n - b]
    block_starts = rng.integers(0, n - b + 1, size=(tekrar, num_blocks))
    offsets = np.arange(b)
    sample_indices = (
        block_starts[:, :, None] + offsets[None, None, :]
    ).reshape(tekrar, -1)[:, :n]

    arr = temiz.to_numpy()
    boot_samples = arr[sample_indices]
    boot_means = boot_samples.mean(axis=1)

    alt = float(np.percentile(boot_means, 100.0 * (alfa / 2.0)))
    ust = float(np.percentile(boot_means, 100.0 * (1.0 - alfa / 2.0)))

    return {"ortalama": ortalama, "alt": alt, "ust": ust, "n": n}