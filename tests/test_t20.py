"""T20: signal-bar level references (D10), Williams fractal, Renko counter, index-ATR indicators.

Every new primitive has a look-ahead test: values up to bar t are unchanged when the series is cut at t.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import tarama
from engine import expr as _expr
from engine import gosterge as g
from engine.kart_sinyal import card_frame_signals
from engine.portfolio import run_portfolio
from tests.test_tarama import synthetic

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
UTC = "UTC"


def _card(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ Williams fractal
def _pine_fractal(values: np.ndarray, n: int, down: bool) -> np.ndarray:
    """Literal port of the 3MAF.pine loops (``low``/``high`` indexed as ``x[k]`` = k bars back)."""
    out = np.zeros(len(values), dtype=bool)
    better = (lambda a, b: a > b) if down else (lambda a, b: a < b)
    orequal = (lambda a, b: a >= b) if down else (lambda a, b: a <= b)
    for t in range(len(values)):
        def x(k: int) -> float:
            return values[t - k] if t - k >= 0 else np.nan
        flag_front = True
        flag_back = [True] * 5
        for i in range(1, n + 1):
            flag_front = flag_front and better(x(n - i), x(n))
            flag_back[0] = flag_back[0] and better(x(n + i), x(n))
            for extra in range(1, 5):
                cond = all(orequal(x(n + j), x(n)) for j in range(1, extra + 1)) and better(x(n + i + extra), x(n))
                flag_back[extra] = flag_back[extra] and cond
        out[t] = flag_front and any(flag_back)
    return out


@pytest.mark.parametrize("n", [2, 3])
def test_williams_fractal_matches_pine_loops(n: int) -> None:
    rng = np.random.default_rng(4)
    # coarse prices create the ties the "extended" variants exist for
    frame = pd.DataFrame({"open": 0.0, "close": 0.0, "volume": 1.0,
                          "high": rng.integers(10, 16, 400).astype(float), "low": rng.integers(4, 10, 400).astype(float)},
                         index=pd.bdate_range("2020-01-01", periods=400, tz=UTC))
    result = g.williams_fractal(frame, n)
    np.testing.assert_array_equal(result["down"].to_numpy(), _pine_fractal(frame["low"].to_numpy(), n, True))
    np.testing.assert_array_equal(result["up"].to_numpy(), _pine_fractal(frame["high"].to_numpy(), n, False))
    assert result["down"].sum() > 5 and result["up"].sum() > 5


def test_williams_fractal_is_known_only_n_bars_after_the_pivot() -> None:
    low = [5, 5, 5, 3, 4, 5, 5, 5.0]  # pivot low at position 3
    frame = pd.DataFrame({"open": 1.0, "close": 1.0, "volume": 1.0, "high": 9.0, "low": low},
                         index=pd.bdate_range("2020-01-01", periods=len(low), tz=UTC))
    down = g.williams_fractal(frame, 2)["down"]
    assert list(down[down].index) == [frame.index[5]]  # pivot bar 3 + n = 2


# ------------------------------------------------------------------ Renko counter
def test_renko_counter_known_path_and_lookahead() -> None:
    close = [100, 100, 101, 105, 111, 111, 106, 100, 95, 90, 111]
    frame = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0},
                         index=pd.bdate_range("2020-01-01", periods=len(close), tz=UTC))
    result = g.renko_sayac(frame, kutu=5, ilk_bar=1)
    # anchor at bar 1: upbrick 100 / downbrick 95. 105 -> 1 brick up, 111 -> 1 more (upbrick 110);
    # 100 <= 105 - 5 -> 1 down, 95 -> 2, 90 -> 3; 111 >= 95 + 5 -> floor(16 / 5) = 3 up and the down run resets
    assert result["up"].tolist() == [0, 0, 0, 1, 2, 2, 2, 0, 0, 0, 3]
    assert result["down"].tolist() == [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0]
    full = g.renko_sayac(frame, kutu=5, ilk_bar=1)
    for cut in range(2, len(close)):
        part = g.renko_sayac(frame.iloc[:cut], kutu=5, ilk_bar=1)
        pd.testing.assert_frame_equal(part, full.iloc[:cut])


# ------------------------------------------------------------------ eger / veri
def test_eger_scalar_and_series() -> None:
    assert _expr.parse("eger(a > 1, 10, 20)").evaluate({"a": 2}) == 10
    index = pd.RangeIndex(4)
    env = {"a": pd.Series([0, 2, 0, 2], index=index), "b": pd.Series([1.0, 2.0, 3.0, 4.0], index=index)}
    out = _expr.parse("eger(a > 1, b, b * 10)").evaluate(env)
    assert out.tolist() == [10.0, 2.0, 30.0, 4.0]


def test_veri_endeks_computes_the_indicator_on_the_benchmark_calendar() -> None:
    frame, bench = synthetic(1, 300), synthetic(2, 300)
    spec = {"f": "atr", "n": 14, "veri": "endeks"}
    out = g.compute(frame, spec, benchmarks={"endeks": bench})
    pd.testing.assert_series_equal(out, g.atr(bench, 14).reindex(frame.index, method="ffill"), check_names=False)
    with pytest.raises(ValueError):
        g.compute(frame, spec)


# ------------------------------------------------------------------ card signals: no look-ahead
CARDS = [("A3-002c", None), ("A3-002b", None), ("M013", None), ("M010", "bench"), ("M027", None)]


@pytest.mark.parametrize("card_id,needs_bench", CARDS)
def test_converted_cards_have_no_lookahead(card_id: str, needs_bench: str | None) -> None:
    card = _card(card_id)
    assert card["ozel_kod"] is False
    frame = synthetic(7, 900, calendar=True)
    bench = synthetic(8, 900, calendar=True) if needs_bench else None
    full, _ = card_frame_signals(card, frame, week_end="SUN", benchmark=bench)
    for cut in (300, 551, 777):
        part, _ = card_frame_signals(card, frame.iloc[:cut], week_end="SUN", benchmark=bench.iloc[:cut] if bench is not None else None)
        columns = [c for c in ("entry", "exit", "atr") if c in full.columns]
        pd.testing.assert_frame_equal(part[columns], full[columns].iloc[:cut], check_exact=False, rtol=1e-9, atol=1e-9)


# ------------------------------------------------------------------ engine: signal-bar levels
def _bars(rows: list[tuple[float, float, float, float]]) -> pd.DataFrame:
    index = pd.bdate_range("2021-01-04", periods=len(rows), tz=UTC)
    opens, highs, lows, closes = zip(*rows)
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": 1.0}, index=index)


def _signals(frame: pd.DataFrame, entry_bar: int) -> pd.DataFrame:
    entry = pd.Series(False, index=frame.index)
    entry.iloc[entry_bar] = True
    return pd.DataFrame({"entry": entry, "exit": False, "atr": 2.0}, index=frame.index)


def _run(frame, signals, **kwargs):
    return run_portfolio({"X": frame}, None, market="ABD25", start=frame.index[0], end=frame.index[-1], cost_rate=0.0,
                         precomputed_signals={"X": signals}, trail_mode=None, **kwargs)


def test_level_fns_stop_target_use_the_signal_bar_and_the_fill_price() -> None:
    # bar 1 is the signal bar (low 98, high 104); fill at bar 2 open 101
    frame = _bars([(100, 101, 99, 100), (100, 104, 98, 101), (101, 103, 100, 102), (102, 112, 101, 111), (111, 112, 110, 111)])
    levels = {
        "stop": lambda symbol, loc, price: float(frame["low"].iloc[loc]),
        "target": lambda symbol, loc, price, stop: float(frame["high"].iloc[loc]) + (float(frame["high"].iloc[loc]) - float(frame["low"].iloc[loc])),
    }
    result = _run(frame, _signals(frame, 1), level_fns=levels)
    trade = result.trades.iloc[0]
    assert trade["entry_price"] == pytest.approx(101.0)
    assert trade["initial_stop"] == pytest.approx(98.0)
    assert trade["exit_reason"] == "target" and trade["exit_price"] == pytest.approx(110.0)  # 104 + (104 - 98)


def test_level_fns_skip_entries_with_a_target_not_above_the_fill() -> None:
    frame = _bars([(100, 101, 99, 100), (100, 104, 98, 101), (110, 111, 109, 110), (110, 112, 109, 111)])
    levels = {"stop": lambda s, loc, price: 98.0, "target": lambda s, loc, price, stop: 104.0}  # gap above the target
    assert _run(frame, _signals(frame, 1), level_fns=levels).trades.empty


def test_level_profit_lock_moves_the_stop_to_the_signal_bar_level() -> None:
    frame = _bars([(100, 101, 99, 100), (100, 104, 98, 101), (101, 103, 100, 102), (102, 107, 101, 106), (106, 106.5, 103.5, 104), (104, 105, 100, 101), (101, 102, 99, 100)])
    levels = {"stop": lambda s, loc, price: 98.0, "target": lambda s, loc, price, stop: 120.0}
    lock = {"trigger_level_fn": lambda s, loc, price, stop, target: 107.0, "stop_level_fn": lambda s, loc, price, stop, target: 104.0}
    result = _run(frame, _signals(frame, 1), level_fns=levels, profit_lock=lock)
    trade = result.trades.iloc[0]
    # high 107 on bar 3 reaches the trigger -> stop 104; bar 5 low 100 <= 104 exits at 104
    assert trade["exit_reason"] == "stop" and trade["exit_price"] == pytest.approx(104.0)


# ------------------------------------------------------------------ card integration (CP1 levels)
def test_a3_002c_trades_follow_the_cp1_levels() -> None:
    card = _card("A3-002c")
    data = {f"S{k}": synthetic(k, 1500, calendar=True) for k in range(4)}
    prepared = tarama.prepare(card, data, "KRIPTO25", start=pd.Timestamp("2012-03-01", tz=UTC), end=pd.Timestamp("2016-01-01", tz=UTC))
    trades = prepared.run().trades
    assert len(trades) > 10
    for trade in trades.itertuples():
        frame = data[trade.symbol]
        signal_bar = frame.index.get_loc(trade.entry_date) - 1
        high = float(frame["high"].iloc[signal_bar])
        assert trade.initial_stop == pytest.approx(2 * trade.entry_price - high)
        if trade.exit_reason == "target":
            assert trade.exit_price == pytest.approx(high)


def test_a3_002b_stop_is_ema50_or_ema100_of_the_signal_bar() -> None:
    card = _card("A3-002b")
    data = {f"S{k}": synthetic(k + 20, 1500, calendar=True) for k in range(4)}
    prepared = tarama.prepare(card, data, "KRIPTO25", start=pd.Timestamp("2012-03-01", tz=UTC), end=pd.Timestamp("2016-01-01", tz=UTC))
    trades = prepared.run().trades
    assert len(trades) > 10
    for trade in trades.itertuples():
        frame = data[trade.symbol]
        signal_bar = frame.index.get_loc(trade.entry_date) - 1
        ema50, ema100 = g.ema(frame, "close", 50).iloc[signal_bar], g.ema(frame, "close", 100).iloc[signal_bar]
        expected = ema50 if frame["low"].iloc[signal_bar] > ema50 else ema100
        assert trade.initial_stop == pytest.approx(expected)
        if trade.exit_reason == "target":  # tpCoef 1: target = entry + (entry - stop)
            assert trade.exit_price == pytest.approx(2 * trade.entry_price - expected)
