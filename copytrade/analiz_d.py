"""Ön kayıt D v1.3 analiz kodu (docs/ONKAYIT_D.md, madde 4–7). Gölge verisi görülmeden yazıldı; altın örnekleri ``tests/test_analiz_d.py``.

Tüm eşikler ``kurallar.yaml``'dan gelir. Yalnız saf fonksiyonlar (veri okuma/yazma yok): girdiler günlük getiri dizileri ve puan/getiri çiftleridir.
* ``birincil_spearman``: havuz genelinde seçim puanı ↔ sonraki dönemin maliyet sonrası net getirisi (Spearman ρ, tek yönlü p, iki yönlü %90 GA).
* ``ikincil_fark``: oda ↔ eşleştirilmiş kontrol günlük farkı, BTC betası düzeltilmiş; haftalık blok bootstrap (MBB) %95.
* ``karar``: üç sonuç (ise_yariyor | ise_yaramiyor | sinanamadi). * ``mde``: saptanabilir en küçük fark (rapor satırı).
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any, Sequence

import numpy as np

from copytrade.kurallar import load_rules

NORMAL = NormalDist()
SONUCLAR = ("ise_yariyor", "ise_yaramiyor", "sinanamadi")


def _ranks(values: Sequence[float]) -> np.ndarray:
    """Ortalama sıra (bağlarda): 1 tabanlı."""
    array = np.asarray(values, dtype=float)
    order = np.argsort(array, kind="mergesort")
    ranks = np.empty(len(array))
    sorted_values = array[order]
    start = 0
    while start < len(array):
        end = start
        while end + 1 < len(array) and sorted_values[end + 1] == sorted_values[start]:
            end += 1
        ranks[order[start:end + 1]] = (start + end) / 2 + 1
        start = end + 1
    return ranks


def spearman_ozeti(rho: float | None, n: int, rules: dict | None = None) -> dict[str, Any]:
    """ρ ve n'den tek yönlü p (H1: ρ > 0) ve iki yönlü %90 GA (Fisher z; Spearman için SE = √(c / (n − 3)), c = ``onkayit_spearman_varyans_carpani``).
    GA düzeyi = 1 − 2 × ``onkayit_p_max`` (tek yönlü %95'e denk). n ≤ 3 ya da ρ tanımsızsa p ve GA ``None``."""
    rules = rules or load_rules()
    out: dict[str, Any] = {"rho": rho, "n": int(n), "p_tek_yonlu": None, "ga90_alt": None, "ga90_ust": None}
    if rho is None or n <= 3:
        return out
    level = 1.0 - 2.0 * float(rules["onkayit_p_max"])
    z_crit = NORMAL.inv_cdf(0.5 + level / 2.0)
    se = math.sqrt(float(rules["onkayit_spearman_varyans_carpani"]) / (n - 3))
    clipped = max(min(rho, 1 - 1e-12), -1 + 1e-12)
    z = math.atanh(clipped)
    out["p_tek_yonlu"] = 1.0 - NORMAL.cdf(z / se)
    out["ga90_alt"], out["ga90_ust"] = math.tanh(z - z_crit * se), math.tanh(z + z_crit * se)
    return out


def birincil_spearman(puan: Sequence[float], ileri_getiri: Sequence[float], rules: dict | None = None) -> dict[str, Any]:
    """Birincil ölçüt. ``puan`` ve ``ileri_getiri`` aynı uzunlukta (adres başına bir değer; havuzun tamamı)."""
    if len(puan) != len(ileri_getiri):
        raise ValueError("puan ve ileri_getiri aynı uzunlukta olmalı")
    n = len(puan)
    rho = None
    if n >= 2:
        a, b = _ranks(puan) - (n + 1) / 2, _ranks(ileri_getiri) - (n + 1) / 2
        denominator = math.sqrt(float((a * a).sum() * (b * b).sum()))
        rho = float((a * b).sum() / denominator) if denominator > 0 else None
    return spearman_ozeti(rho, n, rules)


def _alpha(difference: np.ndarray, btc: np.ndarray) -> tuple[float, float]:
    """Fark = α + β × BTC (en küçük kareler): (α, β). BTC sabitse β = 0, α = ortalama fark."""
    centered = btc - btc.mean()
    variance = float((centered * centered).sum())
    beta = float((centered * (difference - difference.mean())).sum() / variance) if variance > 1e-18 else 0.0
    return float((difference - beta * btc).mean()), beta


def ikincil_fark(kohort_gunluk: Sequence[float], kontrol_gunluk: Sequence[float], btc_gunluk: Sequence[float], blok: int | None = None,
                 tekrar: int | None = None, tohum: int = 0, rules: dict | None = None) -> dict[str, Any]:
    """Günlük fark (kohort − kontrol) = α + β × BTC; ``fark`` = α (BTC betası düzeltilmiş günlük fark). Aralık: örtüşen bloklu (``blok`` gün,
    varsayılan ``onkayit_blok_gun``) bootstrap, ``tekrar`` yeniden örnekleme, ``onkayit_ci_ikincil`` düzeyi, ``tohum`` ile tekrarlanabilir."""
    rules = rules or load_rules()
    kohort, kontrol, btc = (np.asarray(x, dtype=float) for x in (kohort_gunluk, kontrol_gunluk, btc_gunluk))
    if not len(kohort) == len(kontrol) == len(btc):
        raise ValueError("kohort, kontrol ve BTC serileri aynı uzunlukta olmalı")
    n = len(kohort)
    if n < 2:
        raise ValueError("en az 2 gün gerekir")
    blok = int(blok or rules["onkayit_blok_gun"])
    blok = min(blok, n)
    tekrar = int(tekrar or rules["onkayit_bootstrap_tekrar"])
    difference = kohort - kontrol
    alpha, beta = _alpha(difference, btc)
    rng = np.random.default_rng(tohum)
    starts = np.arange(n - blok + 1)
    count = math.ceil(n / blok)
    estimates = np.empty(tekrar)
    for i in range(tekrar):
        picked = rng.choice(starts, size=count)
        index = np.concatenate([np.arange(s, s + blok) for s in picked])[:n]
        estimates[i] = _alpha(difference[index], btc[index])[0]
    level = float(rules["onkayit_ci_ikincil"])
    low, high = np.quantile(estimates, [(1 - level) / 2, 1 - (1 - level) / 2])
    return {"fark": alpha, "beta": beta, "ga_alt": float(low), "ga_ust": float(high), "n": n, "blok": blok, "tekrar": tekrar, "duzey": level,
            "not": "küçük örneklemde MBB aralığı iyimserdir (kapama ≈ %83)"}


def karar(birincil: dict[str, Any], ikincil: dict[str, Any] | None, kohort_mutlak: float | None, rules: dict | None = None) -> dict[str, str]:
    """Üç sonuçlu karar (ön kayıt madde 5).
    * ise_yariyor: ρ > 0 **ve** tek yönlü p < ``onkayit_p_max`` **ve** ikincil nokta tahmini > 0 **ve** kohortun maliyet sonrası mutlak getirisi > 0.
    * ise_yaramiyor: ρ'nun iki yönlü %90 GA üst sınırı < ``onkayit_delta_rho`` (pratik eşik δρ).
    * sinanamadi: diğer her durum (ikincil yoksa — ör. oda < 10 — ise_yariyor denenmez)."""
    rules = rules or load_rules()
    p_max, delta = float(rules["onkayit_p_max"]), float(rules["onkayit_delta_rho"])
    rho, p, upper = birincil.get("rho"), birincil.get("p_tek_yonlu"), birincil.get("ga90_ust")
    second = (ikincil or {}).get("fark")
    if rho is not None and rho > 0 and p is not None and p < p_max and second is not None and second > 0 and kohort_mutlak is not None and kohort_mutlak > 0:
        return {"sonuc": "ise_yariyor", "gerekce": f"ρ={rho:.3f} > 0, p={p:.3f} < {p_max}, ikincil fark > 0, kohort mutlak getirisi > 0"}
    if upper is not None and upper < delta:
        return {"sonuc": "ise_yaramiyor", "gerekce": f"ρ'nun %90 GA üst sınırı {upper:.3f} < δρ={delta}"}
    return {"sonuc": "sinanamadi", "gerekce": "koşullar ne 'ise yarıyor' ne 'ise yaramıyor' için yeterli (24. haftada da sürerse 'bu ölçekte sınanamadı')"}


def mde(sigma: float, rho: float, n: int, gun: int, rules: dict | None = None) -> dict[str, Any]:
    """Saptanabilir en küçük fark (iki yönlü ``onkayit_ci_ikincil`` düzeyi, ``onkayit_guc`` gücü). İki ayrık eşit ağırlıklı portföyün (n trader,
    günlük σ, ikili korelasyon ρ) günlük farkının ``gun`` günlük ortalamasının SD'si = √(2 (1 − ρ) σ² / (n × gün)); MDE = (z_{1−α/2} + z_{güç}) × SD."""
    rules = rules or load_rules()
    if not (-1.0 < rho < 1.0) or sigma <= 0 or n < 1 or gun < 1:
        raise ValueError("σ > 0, −1 < ρ < 1, n ≥ 1, gün ≥ 1 olmalı")
    sd = math.sqrt(2.0 * (1.0 - rho) * sigma * sigma / (n * gun))
    k = NORMAL.inv_cdf(0.5 + float(rules["onkayit_ci_ikincil"]) / 2.0) + NORMAL.inv_cdf(float(rules["onkayit_guc"]))
    daily = k * sd
    pct = lambda x: f"%{100 * x:.2f}".replace(".", ",")      # noqa: E731
    line = f"MDE (güç %{100 * float(rules['onkayit_guc']):.0f}, GA %{100 * float(rules['onkayit_ci_ikincil']):.0f}): günlük {pct(daily)}, dönem toplamı {pct(daily * gun)} (σ={sigma:.4f}, ρ={rho:.2f}, n={n}, gün={gun})"
    return {"sd": sd, "k": k, "mde_gunluk": daily, "mde_donem": daily * gun, "satir": line}


def duyarlilik_net(brut_getiri: float, maliyet: float, tarz: str, rules: dict | None = None) -> float:
    """Tanımlayıcı maliyet duyarlılığı: intraday'de maliyet ``maliyet_duyarlilik_carpani_intraday`` katına çıkarılır (diğer tarzlarda aynı)."""
    rules = rules or load_rules()
    return brut_getiri - maliyet * (float(rules["maliyet_duyarlilik_carpani_intraday"]) if tarz == "intraday" else 1.0)


def veri_eksik(eksik: int, toplam: int, rules: dict | None = None) -> bool:
    """Bir haftada dolum/işaret eksikliği oranı ``onkayit_veri_eksik_max``'ı aşarsa (ya da hiç veri yoksa) hafta 'veri eksik' işaretlenir."""
    rules = rules or load_rules()
    return toplam <= 0 or eksik / toplam > float(rules["onkayit_veri_eksik_max"])
