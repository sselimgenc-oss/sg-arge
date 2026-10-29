"""Oda yoğunlaşması ve puan tutarlılığı (Argon A14).

Bu modül portföy/trader getirilerinin ikili Pearson korelasyon matrisini,
ortalama bağlantılı (average linkage) hiyerarşik kümelemesini, yoğunlaşma
özet metriklerini (Herfindahl tersi / etkin küme sayısı vb.) ve iki yarının
puan tutarlılığını (Spearman sıra korelasyonu) hesaplar.
SciPy yok. Eşikler çağırandan gelir (``kurallar.yaml``: ``yogunlasma_min_ortak_gun``, ``yogunlasma_kume_esik``); modülde varsayılan yok. Bilgi ölçüsüdür, karar değil.
"""

from collections import Counter
from typing import Callable, Dict, Union
import numpy as np
import pandas as pd

from copytrade.analiz_d import birincil_spearman


def korelasyon_matrisi(
    getiri: pd.DataFrame,
    min_ortak_gun: int,
) -> pd.DataFrame:
    """
    İkili Pearson korelasyon matrisini hesaplar.
    
    Ortak gün sayısı min_ortak_gun'ün altındaysa ilgili çift için NaN döndürür.
    
    Parametreler:
        getiri: pd.DataFrame
            Satırlar gün, sütunlar trader adresi, değerler günlük getiri.
        min_ortak_gun: int
            İkili korelasyon hesaplamak için gereken asgari ortak gün sayısı.
            
    Döndürür:
        pd.DataFrame: Sütunlar ve satırlar trader adresleri olan korelasyon matrisi.
    """
    if not isinstance(getiri, pd.DataFrame):
        getiri = pd.DataFrame(getiri)
        
    return getiri.corr(method="pearson", min_periods=min_ortak_gun)


def kumele(
    korelasyon: Union[pd.DataFrame, np.ndarray],
    esik: float,
) -> Dict[str, int]:
    """
    Ortalama bağlantılı (average linkage) hiyerarşik kümeleme uygular.
    
    İki küme arasındaki ortalama korelasyon esik'in altına düşünce birleştirme durur.
    Hesaplanamayan (NaN) çiftler bağlantısız sayılır.
    
    Parametreler:
        korelasyon: pd.DataFrame veya np.ndarray
            Korelasyon matrisi (elemanlar [-1, 1] veya NaN).
        esik: float
            Kümeleri birleştirmeyi durdurma eşiği. Ortalama korelasyon eşiğin
            altına düşünce birleştirme durdurulur (ortalama >= esik iken birleştirilir).
            
    Döndürür:
        dict[str, int]: Trader adresi -> Küme numarası (0, 1, ..., K-1).
    """
    if isinstance(korelasyon, pd.DataFrame):
        addresses = [str(col) for col in korelasyon.columns]
        mat = korelasyon.to_numpy(dtype=float, copy=True)
    else:
        mat = np.asarray(korelasyon, dtype=float)
        addresses = [str(i) for i in range(len(mat))]
        
    n = len(addresses)
    if n == 0:
        return {}
    if n == 1:
        return {addresses[0]: 0}
        
    # Başlangıçta her trader tek başına bir kümedir.
    # cluster_id -> [trader_index, ...]
    clusters: Dict[int, list[int]] = {i: [i] for i in range(n)}
    
    # S[(ca, cb)]: ca ve cb kümeleri arasındaki geçerli (non-NaN) korelasyonların toplamı
    # W[(ca, cb)]: ca ve cb kümeleri arasındaki geçerli bağlantı sayısı
    # Hesaplanamayan (NaN) çiftler bağlantısız kabul edildiğinden W=0 olur.
    S: Dict[tuple[int, int], float] = {}
    W: Dict[tuple[int, int], int] = {}
    
    for i in range(n):
        for j in range(i + 1, n):
            val = mat[i, j]
            if np.isnan(val) and not np.isnan(mat[j, i]):
                val = mat[j, i]
                
            if np.isnan(val):
                S[(i, j)] = 0.0
                W[(i, j)] = 0
            else:
                S[(i, j)] = float(val)
                W[(i, j)] = 1
                
    next_cluster_id = n
    tol = 1e-12  # Kayan nokta hassasiyeti için tolerans
    
    while len(clusters) > 1:
        best_pair = None
        best_avg = -np.inf
        
        active_ids = sorted(clusters.keys())
        num_active = len(active_ids)
        
        for idx_a in range(num_active):
            ca = active_ids[idx_a]
            for idx_b in range(idx_a + 1, num_active):
                cb = active_ids[idx_b]
                pair_key = (min(ca, cb), max(ca, cb))
                w = W.get(pair_key, 0)
                
                # Sadece bağlantısı olan (en az 1 geçerli korelasyonu bulunan) çiftler birleşebilir
                if w > 0:
                    avg_c = S[pair_key] / w
                    if avg_c > best_avg:
                        best_avg = avg_c
                        best_pair = (ca, cb)
                        
        # Eşiğin altına düşünce birleştirme dursun (best_avg >= esik devam eder)
        if best_pair is None or best_avg < (esik - tol):
            break
            
        ca, cb = best_pair
        new_c = next_cluster_id
        next_cluster_id += 1
        
        clusters[new_c] = clusters[ca] + clusters[cb]
        del clusters[ca]
        del clusters[cb]
        
        # Yeni kümenin diğer aktif kümelerle ortalama bağlantısını güncelle
        for ck in clusters.keys():
            if ck == new_c:
                continue
            pair_a = (min(ca, ck), max(ca, ck))
            pair_b = (min(cb, ck), max(cb, ck))
            
            s_new = S.get(pair_a, 0.0) + S.get(pair_b, 0.0)
            w_new = W.get(pair_a, 0) + W.get(pair_b, 0)
            
            pair_new = (min(new_c, ck), max(new_c, ck))
            S[pair_new] = s_new
            W[pair_new] = w_new
            
    # Deterministik ve 0'dan başlayan küme numaralandırması:
    # Kümeleri içerdikleri en küçük ilk trader indeksine göre sırala
    sorted_clusters = sorted(clusters.values(), key=lambda members: min(members))
    result: Dict[str, int] = {}
    for cluster_num, members in enumerate(sorted_clusters):
        for idx in members:
            result[addresses[idx]] = cluster_num
            
    return result


def yogunlasma_ozeti(kumeler: Union[Dict[str, int], pd.Series, list]) -> dict:
    """
    Kümeleme sonuçları üzerinden oda/küme yoğunlaşma metriklerini özetler.
    
    Parametreler:
        kumeler: dict[str, int], pd.Series veya list
            Trader adresi -> Küme numarası eşleştirmesi veya küme etiketleri.
            
    Döndürür:
        dict:
            - 'kume_sayisi': Benzersiz küme adedi.
            - 'en_buyuk_kume_payi': En büyük kümenin toplam traderlar içindeki oranı.
            - 'etkin_kume_sayisi': Küme paylarının Herfindahl tersi (1 / sum(s_i^2)).
    """
    if isinstance(kumeler, dict):
        labels = list(kumeler.values())
    elif isinstance(kumeler, (pd.Series, pd.DataFrame)):
        labels = list(kumeler.squeeze())
    elif isinstance(kumeler, (list, tuple, np.ndarray)):
        labels = list(kumeler)
    else:
        labels = []
        
    n_total = len(labels)
    if n_total == 0:
        return {
            "kume_sayisi": 0,
            "en_buyuk_kume_payi": 0.0,
            "etkin_kume_sayisi": 0.0
        }
        
    counts = list(Counter(labels).values())
    kume_sayisi = len(counts)
    en_buyuk_kume_payi = float(max(counts) / n_total)
    
    # Herfindahl indeksi HHI = sum((count_i / n_total)^2)
    # Etkin küme sayısı = 1 / HHI = n_total^2 / sum(count_i^2)
    sum_sq_counts = sum(c ** 2 for c in counts)
    etkin_kume_sayisi = float((n_total ** 2) / sum_sq_counts)
    
    return {
        "kume_sayisi": kume_sayisi,
        "en_buyuk_kume_payi": en_buyuk_kume_payi,
        "etkin_kume_sayisi": etkin_kume_sayisi
    }


def yari_tutarliligi(
    getiri: pd.DataFrame,
    puan_fn: Callable[[pd.DataFrame], pd.Series]
) -> dict:
    """Zaman penceresini ikiye böler (ilk ``T // 2`` gün / kalanı), her yarıyı ``puan_fn`` ile puanlar ve iki yarının ortak geçerli puanları
    arasındaki Spearman sıra korelasyonunu döndürür: ``{'n', 'rho'}``. Eşit puanlarda ortalama sıra; ``n < 2`` ya da sabit puanda ``rho`` ``None``.
    Sıra korelasyonu ``analiz_d.birincil_spearman`` ile aynı koddur (tek uygulama)."""
    if not isinstance(getiri, pd.DataFrame):
        getiri = pd.DataFrame(getiri)
    mid = len(getiri) // 2
    first, second = puan_fn(getiri.iloc[:mid]), puan_fn(getiri.iloc[mid:])
    both = pd.DataFrame({"s1": first if isinstance(first, pd.Series) else pd.Series(first),
                         "s2": second if isinstance(second, pd.Series) else pd.Series(second)}).dropna()
    result = birincil_spearman(both["s1"].tolist(), both["s2"].tolist())
    return {"n": len(both), "rho": result["rho"]}
