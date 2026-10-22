"""T18 portfolio: correlation, equal-risk combination and the 2% open-risk cap on synthetic books."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtests import portfoy
from engine.portfolio import run_portfolio
from tests.test_tarama import synthetic


def _equity_result(returns: pd.Series, trades: pd.DataFrame | None = None):
    from engine.portfolio import BacktestResult

    equity = 100.0 * (1.0 + returns).cumprod()
    return BacktestResult(100.0, equity, pd.Series(0.0, index=equity.index), trades if trades is not None else pd.DataFrame(), 0)


def _index(n: int = 300) -> pd.DatetimeIndex:
    return pd.bdate_range("2021-01-04", periods=n, tz="UTC")


def test_equal_risk_portfolio_is_mean_and_missing_days_are_flat() -> None:
    index = _index(5)
    a = pd.Series([0.02, 0.0, -0.01, 0.03, 0.01], index=index)
    b = pd.Series([0.01, 0.01, 0.01], index=index[:3])  # market closed on the last two days
    frame = portfoy.align({"a": a, "b": b})
    combined = portfoy.equal_risk_portfolio(frame)
    np.testing.assert_allclose(combined.to_numpy(), [0.015, 0.005, 0.0, 0.015, 0.005])


def test_correlation_known_values_and_stress_subset() -> None:
    rng = np.random.default_rng(3)
    index = _index(400)
    base = pd.Series(rng.normal(0, 0.01, 400), index=index)
    frame = pd.DataFrame({"x": base, "same": base, "inverse": -base, "noise": rng.normal(0, 0.01, 400)}, index=index)
    table = portfoy.correlation_table(frame, base, "IS")
    pick = lambda kind, a, b: table[(table.tip == kind) & (table.a == a) & (table.b == b)]["korelasyon"].iloc[0]  # noqa: E731
    assert pick("tum", "x", "same") == pytest.approx(1.0)
    assert pick("tum", "x", "inverse") == pytest.approx(-1.0)
    assert abs(pick("tum", "x", "noise")) < 0.2
    stress = table[table.tip == "stres"]
    assert (stress["gun"] == 20).all()  # worst 5% of 400 days
    assert pick("stres", "x", "same") == pytest.approx(1.0)


def test_stress_correlation_is_nan_when_too_few_days() -> None:
    index = _index(100)
    base = pd.Series(np.linspace(-0.01, 0.01, 100), index=index)
    table = portfoy.correlation_table(pd.DataFrame({"a": base, "b": base}, index=index), base, "OOS")
    assert table[(table.tip == "stres")]["korelasyon"].isna().all()


def test_open_risk_cap_is_structural_at_one_over_n() -> None:
    """Each book is capped at 2% of its own capital; at 1/N each the portfolio open risk is the mean, so <= 2%."""
    index = _index(50)
    at_cap = pd.Series(portfoy.OPEN_RISK_CAP, index=index)
    quiet = pd.Series(0.005, index=index)
    combined = portfoy.portfolio_open_risk({"a": at_cap, "b": at_cap, "c": quiet})
    assert combined.max() <= portfoy.OPEN_RISK_CAP + 1e-12
    assert combined.max() == pytest.approx((2 * 0.02 + 0.005) / 3)
    one = portfoy.portfolio_open_risk({"a": at_cap})
    assert one.max() == pytest.approx(portfoy.OPEN_RISK_CAP)


def test_open_risk_series_and_returns_from_real_engine_book() -> None:
    data = {f"S{k}": synthetic(110 + k, periods=800) for k in range(6)}
    signals = {}
    for symbol, frame in data.items():
        atr = (frame["high"] - frame["low"]).rolling(14).mean()
        entry = pd.Series(np.arange(len(frame)) % 7 == 0, index=frame.index)
        signals[symbol] = pd.DataFrame({"entry": entry, "exit": False, "atr": atr, "stop_dist": 3 * atr})
    result = run_portfolio(data, None, market="ABD25", start=pd.Timestamp("2012-06-01", tz="UTC"),
                           end=pd.Timestamp("2014-12-31", tz="UTC"), cost_rate=0.0005, precomputed_signals=signals)
    assert not result.trades.empty
    risk = portfoy.open_risk_series(result)
    assert risk.max() > 0.005  # sizing risks 0.5% per trade, several trades overlap
    assert risk.max() < 0.05
    returns = portfoy.daily_returns(result)
    assert (1 + returns).prod() == pytest.approx(result.equity.iloc[-1] / result.equity.iloc[0])


def test_period_metrics_known_path() -> None:
    returns = pd.Series([0.10, -0.20, 0.10], index=_index(3))
    out = portfoy.period_metrics(returns, repetitions=20, seed=1, annualization=252)
    assert out["mdd"] == pytest.approx(0.20)
    assert out["pf"] == pytest.approx(1.0)
    assert out["gun"] == 3


def test_report_and_correlation_files_are_written(tmp_path) -> None:
    rng = np.random.default_rng(5)
    index = _index(300)
    frame = pd.DataFrame({"A:BIST30": rng.normal(0.0004, 0.01, 300), "B:ABD25": rng.normal(0.0004, 0.01, 300)}, index=index)
    proxy = pd.Series(rng.normal(0, 0.01, 300), index=index)
    summary = {p: portfoy.period_metrics(portfoy.equal_risk_portfolio(frame), repetitions=30, seed=1, annualization=252) for p in ("IS", "OOS")}
    corr = pd.concat([portfoy.correlation_table(frame, proxy, p) for p in ("IS", "OOS")], ignore_index=True)
    per = pd.DataFrame([{"aday": c, "is_getiri": 0.1, "is_mdd": 0.05, "oos_getiri": 0.02, "oos_mdd": 0.03} for c in frame.columns])
    portfoy.write_report(tmp_path, "asama2b.csv", list(frame.columns), per, summary, corr, 0.015, "sabit")
    text = (tmp_path / "portfoy.md").read_text(encoding="utf-8")
    assert text.index("**OOS**") < text.index("**IS**")  # out-of-sample first
    assert "Secim yanliligi" in text and "A:BIST30" in text
    assert set(corr.columns) == set(portfoy.CORRELATION_COLUMNS)
