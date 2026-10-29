"""Sentetik doğrulama modülü altın örnekleri."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from copytrade.sentetik import deney, sans_eklentisi, secim_basarisi, trader_uret


def test_ayni_tohum_ayni_cikti():
    params = dict(n_trader=40, n_gun=60, yetenekli_oran=.25, alfa_gunluk=.002, oynaklik_gunluk=.01, tohum=42)
    first, truth = trader_uret(**params)
    second, second_truth = trader_uret(**params)
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_series_equal(truth, second_truth)
    pd.testing.assert_frame_equal(sans_eklentisi(first, .3, 5, .1, 99, truth), sans_eklentisi(first, .3, 5, .1, 99, truth))
    kwargs = dict(n_trader=30, n_gun=40, yetenekli_oran=.2, alfa_gunluk=.001, oynaklik_gunluk=.01, k=6)
    pd.testing.assert_frame_equal(deney(lambda df: df.mean(), 5, 123, **kwargs), deney(lambda df: df.mean(), 5, 123, **kwargs))


def test_gurultu_sifirken_ortalama_yetenegi_tam_bulur():
    returns, truth = trader_uret(50, 30, .2, .005, 0.0, 42)
    result = secim_basarisi(returns.mean(), truth, 10)
    assert result == {"isabet": 1.0, "yakalama": 1.0, "sansli_secilen": 0, "k": 10}


def test_rastgele_puan_isabeti_yetenekli_orana_yakindir():
    rng = np.random.default_rng(777)
    result = deney(lambda df: pd.Series(rng.uniform(size=len(df.columns)), index=df.columns), 200, 777,
                   n_trader=100, n_gun=30, yetenekli_oran=.3, alfa_gunluk=.002, oynaklik_gunluk=.02, k=20)
    assert abs(result["isabet"].mean() - .3) < .05


def test_sans_yalniz_yeteneksizlere_ve_son_gunlere_eklenir():
    returns, truth = trader_uret(80, 50, .25, .001, .01, 555)
    lucky = sans_eklentisi(returns, .5, 5, .25, 888, truth)
    difference = lucky - returns
    assert (difference.loc[:, truth[truth].index] == 0).all().all()
    for trader in lucky.attrs["sansli_traderlar"]:
        changed = difference.index[difference[trader] != 0].tolist()
        assert not truth[trader] and len(changed) == 1 and changed[0] in returns.index[-5:]
        assert difference.loc[changed[0], trader] == pytest.approx(.25)


def test_gecersiz_parametreler_valueerror_verir():
    with pytest.raises(ValueError): trader_uret(0, 10, .2, .01, .01)
    with pytest.raises(ValueError): trader_uret(10, 10, 1.1, .01, .01)
    with pytest.raises(ValueError): sans_eklentisi(pd.DataFrame(), .2, 2, .1)
    with pytest.raises(ValueError): sans_eklentisi(pd.DataFrame([[1]]), .2, 0, .1)
    with pytest.raises(ValueError): secim_basarisi(pd.Series([1]), pd.Series([True]), 0)
    with pytest.raises(ValueError): deney(lambda df: df.mean(), 0, n_trader=10, n_gun=10, yetenekli_oran=.2, alfa_gunluk=.01, oynaklik_gunluk=.01)


def test_secim_basarisi_sansli_traderlari_sayir_ve_takma_ad_kabul_etmez():
    score = pd.Series([10., 8., 6., 4., 2.], index=["t000", "t001", "t002", "t003", "t004"])
    truth = pd.Series([True, False, False, True, False], index=score.index)
    assert secim_basarisi(score, truth, 2, ["t001", "t004"]) == {"isabet": .5, "yakalama": .5, "sansli_secilen": 1, "k": 2}
    with pytest.raises(TypeError):
        secim_basarisi(score, truth, 2, sanslilar=["t001"])


def test_trader_kimlikleri_ve_cikti_bicimi():
    returns, truth = trader_uret(15, 10, .2, .002, .01, 12)
    assert returns.shape == (10, 15) and list(returns.columns) == list(truth.index) and truth.dtype == bool
    assert all(name.startswith("t") and name[1:].isdigit() for name in returns.columns)
