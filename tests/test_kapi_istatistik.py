import numpy as np
import pandas as pd

from kapi.istatistik import active_blocks, neff_clusters, nw_alpha, placebo_distribution, random_exposure


def test_blocks_and_seed_preserve_trade_count_and_holding_duration():
    index = pd.date_range("2024-01-01", periods=30, tz="UTC")
    exposure = pd.Series([0, 1, 1, 0, 1, 1, 1] + [0] * 23, index=index)
    blocks = active_blocks(exposure)
    first = random_exposure(index, blocks, np.random.default_rng(7))
    second = random_exposure(index, blocks, np.random.default_rng(7))
    assert sorted(active_blocks(first)) == sorted(blocks)
    assert first.equals(second)


def test_placebo_is_reproducible():
    index = pd.date_range("2024-01-01", periods=60, tz="UTC")
    market = pd.Series(np.linspace(-.01, .01, 60), index=index)
    exposure = pd.Series(([0, 1, 1, 0, 1] * 12), index=index)
    assert np.array_equal(placebo_distribution(market, exposure, repetitions=20, seed=3),
                          placebo_distribution(market, exposure, repetitions=20, seed=3))


def test_newey_west_alpha_and_matched_benchmark_extremes():
    index = pd.date_range("2020-01-01", periods=500, tz="UTC")
    market = pd.Series(np.random.default_rng(2).normal(0, .01, len(index)), index=index)
    alpha = nw_alpha(market + .002, market)
    no_alpha = nw_alpha(market, market)
    assert alpha["nw_t"] > 2 and abs(no_alpha["alfa_yillik"]) < 1e-10
    assert (market * 0).eq(0).all() and (market * 1).equals(market)


def test_neff_correlation_clusters():
    index = pd.date_range("2024-01-01", periods=100, tz="UTC")
    base = pd.Series(np.arange(100, dtype=float), index=index)
    assert neff_clusters({"a": base, "b": base * 2, "c": -base}) == 2


def test_placebo_scale_matches_strategy_size():
    from kapi.istatistik import placebo_distribution
    idx = pd.date_range("2025-01-01", periods=60, freq="D", tz="UTC")
    market = pd.Series(0.01, index=idx)
    exposure = pd.Series([1.0] * 5 + [0.0] * 55, index=idx)
    full = placebo_distribution(market, exposure, repetitions=20, seed=1, round_trip_cost=0)
    tenth = placebo_distribution(market, exposure, repetitions=20, seed=1, round_trip_cost=0, scale=0.1)
    assert abs(tenth.mean()) < abs(full.mean()) / 5  # a 10 % position cannot earn like a 100 % one
