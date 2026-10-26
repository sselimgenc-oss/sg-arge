"""TV-2 sıralama: ortak ölçek, bootstrap alt sınır, kopya kümeleri (TEST_YAPISI Adım 3)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtests import tv2_sirala as S


def _seri(seed: int, n: int = 400, ort: float = 0.0005) -> pd.Series:
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(ort, 0.01, n), index=pd.date_range("2024-01-01", periods=n, freq="D", tz="UTC"))


def test_scaling_sets_annual_volatility_to_target() -> None:
    g = S.olcekle(_seri(1) * 7.3)
    assert abs(g.std(ddof=1) * np.sqrt(365) - S.HEDEF_OYNAKLIK) < 1e-12


def test_lower_bound_is_below_the_mean_and_positive_for_a_strong_edge() -> None:
    rng = np.random.default_rng(0)
    haftalik = pd.Series(np.random.default_rng(2).normal(0.01, 0.005, 120))
    p10 = S.alt_sinir(haftalik, rng)
    assert 0 < p10 < haftalik.mean()
    assert np.isnan(S.alt_sinir(haftalik.iloc[:5], rng))


def test_copies_join_the_better_ranked_representative() -> None:
    a = _seri(3)
    kopya = a * 2 + _seri(4) * 0.05          # neredeyse aynı işaret/zaman
    ayri = _seri(5)
    kume = S.kumele({"a": a, "k": kopya, "b": ayri}, ["a", "k", "b"])
    assert kume == {"a": "a", "k": "a", "b": "b"}


def test_effective_trials_is_information_only_and_tracks_correlation() -> None:
    a = _seri(10)
    identical = a.copy()
    independent = _seri(11)
    assert S.etkin_deneme_sayisi({"a": a}) == 1.0
    correlated = S.etkin_deneme_sayisi({"a": a, "b": identical})
    mixed = S.etkin_deneme_sayisi({"a": a, "b": independent})
    assert 1.0 <= correlated < mixed <= 2.0
