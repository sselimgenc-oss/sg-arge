"""Sentetik doğrulama: zemin gerçeği bilinen trader verisiyle puanlama deneyi.

Ağ ve dosya G/Ç'si yapmaz; tüm sayısal deney parametreleri çağırana aittir.
Bu modül raporlama/araştırma içindir, kapı veya seçim kararına bağlanmaz.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import numpy as np
import pandas as pd


def trader_uret(n_trader: int, n_gun: int, yetenekli_oran: float, alfa_gunluk: float,
                oynaklik_gunluk: float, tohum: int | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Günlük getiri tablosu ve bilinen yetenek etiketlerini üretir.

    Yetenekli trader'ın günlük beklenen getirisi ``alfa_gunluk``, diğerinin
    sıfırdır; ikisi de aynı normal gürültüyü alır.
    """
    if n_trader <= 0:
        raise ValueError(f"n_trader pozitif bir tam sayı olmalıdır: {n_trader}")
    if n_gun <= 0:
        raise ValueError(f"n_gun pozitif bir tam sayı olmalıdır: {n_gun}")
    if not 0.0 <= yetenekli_oran <= 1.0:
        raise ValueError(f"yetenekli_oran 0 ile 1 arasında olmalıdır: {yetenekli_oran}")
    if oynaklik_gunluk < 0.0:
        raise ValueError(f"oynaklik_gunluk negatif olamaz: {oynaklik_gunluk}")
    rng = np.random.default_rng(tohum)
    digits = max(3, len(str(n_trader - 1)))
    ids = [f"t{i:0{digits}d}" for i in range(n_trader)]
    capable = np.zeros(n_trader, dtype=bool)
    count = int(round(n_trader * yetenekli_oran))
    if count:
        capable[rng.choice(n_trader, size=count, replace=False)] = True
    noise = rng.normal(0.0, oynaklik_gunluk, size=(n_gun, n_trader)) if oynaklik_gunluk else np.zeros((n_gun, n_trader))
    returns = pd.DataFrame(np.where(capable, alfa_gunluk, 0.0) + noise, index=pd.RangeIndex(n_gun), columns=ids)
    truth = pd.Series(capable, index=ids, name="gercek")
    returns.attrs["gercek"] = truth
    return returns, truth


def sans_eklentisi(getiri: pd.DataFrame, sansli_oran: float, sans_gun: int, sans_getiri: float,
                   tohum: int | None = None, gercek: pd.Series | None = None) -> pd.DataFrame:
    """Yalnız yeteneksizlerin bir kısmına son ``sans_gun`` içinde tek kazanç ekler.

    Girdi değiştirilmez; seçilen trader kimlikleri dönüş tablosunun
    ``attrs['sansli_traderlar']`` alanında bulunur.
    """
    if getiri.empty:
        raise ValueError("getiri tablosu boş olamaz.")
    if not 0.0 <= sansli_oran <= 1.0:
        raise ValueError(f"sansli_oran 0 ile 1 arasında olmalıdır: {sansli_oran}")
    if sans_gun <= 0 or sans_gun > len(getiri):
        raise ValueError(f"sans_gun 1 ile gün sayısı arasında olmalıdır: {sans_gun}")
    truth = gercek if gercek is not None else getiri.attrs.get("gercek")
    candidates = [name for name in getiri.columns if truth is None or (name in truth.index and not bool(truth[name]))]
    selected_count = int(round(len(candidates) * sansli_oran))
    rng = np.random.default_rng(tohum)
    selected = list(rng.choice(candidates, size=selected_count, replace=False)) if selected_count else []
    result = getiri.copy()
    if selected:
        for trader in selected:
            result.loc[rng.choice(list(getiri.index[-sans_gun:])), trader] += sans_getiri
    result.attrs["sansli_traderlar"] = selected
    if truth is not None:
        result.attrs["gercek"] = truth
    return result


def secim_basarisi(puan: pd.Series, gercek: pd.Series, k: int,
                   sansli_traderlar: Iterable[str] | pd.Series | None = None) -> dict[str, Any]:
    """İlk ``k`` puanın isabetini, yakalamasını ve şanslı seçimini döndürür."""
    if k <= 0 or k > len(puan):
        raise ValueError(f"k 1 ile trader sayısı arasında olmalıdır: {k}")
    selected = set(puan.sort_values(ascending=False).iloc[:k].index)
    capable = set(gercek[gercek].index)
    hit = len(selected & capable)
    if isinstance(sansli_traderlar, pd.Series):
        lucky = set(sansli_traderlar[sansli_traderlar].index) if sansli_traderlar.dtype == bool else set(sansli_traderlar.dropna())
    else:
        lucky = set(sansli_traderlar or [])
    return {"isabet": hit / k, "yakalama": hit / len(capable) if capable else 0.0,
            "sansli_secilen": len(selected & lucky), "k": int(k)}


def deney(puanla: Callable[[pd.DataFrame], pd.Series], n_tekrar: int, tohum: int | None = None,
          **uretim_parametreleri: Any) -> pd.DataFrame:
    """Bir puanlayıcıyı aynı parametrelerle tekrarlı sentetik örneklerde ölçer."""
    if n_tekrar <= 0:
        raise ValueError(f"n_tekrar pozitif bir tam sayı olmalıdır: {n_tekrar}")
    required = ("n_trader", "n_gun", "yetenekli_oran", "alfa_gunluk", "oynaklik_gunluk")
    missing = [name for name in required if name not in uretim_parametreleri]
    if missing:
        raise ValueError(f"Eksik üretim parametresi: '{missing[0]}'")
    params = {name: uretim_parametreleri[name] for name in required}
    k = int(uretim_parametreleri.get("k", max(1, round(int(params["n_trader"]) * float(params["yetenekli_oran"])))))
    if k <= 0:
        raise ValueError(f"k pozitif tam sayı olmalıdır: {k}")
    chance = all(name in uretim_parametreleri for name in ("sansli_oran", "sans_gun", "sans_getiri"))
    rng = np.random.default_rng(tohum)
    rows: list[dict[str, Any]] = []
    for _ in range(n_tekrar):
        data_seed = int(rng.integers(0, 2**31 - 1)) if tohum is not None else None
        chance_seed = int(rng.integers(0, 2**31 - 1)) if tohum is not None else None
        returns, truth = trader_uret(**params, tohum=data_seed)
        lucky: list[str] = []
        if chance:
            returns = sans_eklentisi(returns, float(uretim_parametreleri["sansli_oran"]), int(uretim_parametreleri["sans_gun"]),
                                     float(uretim_parametreleri["sans_getiri"]), chance_seed, truth)
            lucky = returns.attrs["sansli_traderlar"]
        rows.append(secim_basarisi(puanla(returns), truth, k, lucky))
    return pd.DataFrame(rows)
