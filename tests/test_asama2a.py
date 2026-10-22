"""Stage 2a: USD conversion and the random-entry null model."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import asama2a, tarama
from tests.test_tarama import synthetic

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def test_usd_conversion_divides_prices_by_same_day_rate_and_forward_fills() -> None:
    data = {"X": synthetic(1, periods=30)}
    rate = pd.DataFrame({"close": 10.0 + np.arange(30) * 0.1}, index=data["X"].index)
    rate = rate.drop(rate.index[5])  # FX holiday: the previous rate carries over
    out = asama2a.usd_frames(data, rate)["X"]
    day = data["X"].index[10]
    assert out.loc[day, "close"] == pytest.approx(data["X"].loc[day, "close"] / rate.loc[day, "close"])
    holiday = data["X"].index[5]
    assert out.loc[holiday, "open"] == pytest.approx(data["X"].loc[holiday, "open"] / rate.loc[data["X"].index[4], "close"])
    assert (out["volume"] == data["X"]["volume"]).all()


def test_trade_stats_and_p_value() -> None:
    trades = pd.DataFrame({"net_pnl": [10.0, -5.0, 5.0], "r_multiple": [2.0, -1.0, 1.0]})
    pf, mean_r, count = asama2a.trade_stats(trades)
    assert pf == pytest.approx(3.0) and mean_r == pytest.approx(2 / 3) and count == 3
    assert asama2a.trade_stats(pd.DataFrame({"net_pnl": [1.0], "r_multiple": [1.0]}))[0] == asama2a.PF_CAP
    assert np.isnan(asama2a.trade_stats(pd.DataFrame(columns=["net_pnl", "r_multiple"]))[0])
    null = np.array([1.0, 2.0, 3.0, np.nan])
    assert asama2a.p_value(2.5, null) == pytest.approx((1 + 1) / (1 + 3))
    assert asama2a.p_value(0.0, null) == pytest.approx(1.0)


def _prepared(card_id: str = "A3-007"):
    card = yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))
    data = {f"S{i}": synthetic(i, periods=2800) for i in range(4)}
    return tarama.prepare(card, data, "ABD25")


def test_random_entries_only_inside_period_and_count_per_symbol() -> None:
    prepared = _prepared()
    rng = np.random.default_rng(7)
    signals = asama2a.random_entry_signals(prepared, {"S0": 10, "S1": 3}, 1.0, rng)
    assert signals["S0"]["entry"].sum() == 10 and signals["S1"]["entry"].sum() == 3
    assert signals["S2"]["entry"].sum() == 0 and signals["S3"]["entry"].sum() == 0
    chosen = signals["S0"].index[signals["S0"]["entry"].to_numpy()]
    assert ((chosen >= prepared.start) & (chosen <= prepared.end)).all()
    # exits and stop columns are the card's own, untouched
    pd.testing.assert_series_equal(signals["S0"]["exit"], prepared.plan.signals["S0"]["exit"])


def test_null_distribution_is_reproducible_and_matches_trade_count() -> None:
    prepared = _prepared()
    real = prepared.run(1.0).trades
    assert len(real) > 30
    first = asama2a.null_distribution(prepared, real, reps=6, seed=11)
    second = asama2a.null_distribution(prepared, real, reps=6, seed=11)
    np.testing.assert_array_equal(first["pf"], second["pf"])
    assert abs(first["count"].mean() - len(real)) / len(real) < 0.25
    assert np.isfinite(first["hold"]).all()


def test_evaluate_pair_rejects_a_pure_market_beta_card_and_is_deterministic() -> None:
    card = yaml.safe_load((SPEC / "A3-007.yaml").read_text(encoding="utf-8"))
    data = {f"S{i}": synthetic(i, periods=2800) for i in range(4)}
    asama2a._STATE.update(data={"ABD25": data}, usd={}, benchmarks={}, hashes={"ABD25": "h"}, tl_rows={}, git_sha="x")
    task = {"card": card, "market": "ABD25", "reps": 8, "reps_high": 12}
    row_a, row_b = asama2a.evaluate_pair(task), asama2a.evaluate_pair(task)
    assert row_a["karar"] in ("Gecti (null)", "Reddedildi (piyasa betasi)")
    assert row_a["null_pf_p95"] == row_b["null_pf_p95"] and row_a["p_pf"] == row_b["p_pf"]
