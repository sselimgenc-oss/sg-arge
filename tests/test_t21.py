"""T21: ported indicators (literal Pine/Python ports as references) and the cards built on them."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import tarama
from engine import expr as _expr
from engine import gosterge as g
from engine.kart_sinyal import card_frame_signals
from tests.test_tarama import synthetic

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
UTC = "UTC"


def _card(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


def _frame(seed: int, periods: int, freq: str = "15min") -> pd.DataFrame:
    frame = synthetic(seed, periods, calendar=True)
    frame.index = pd.date_range("2020-01-01", periods=periods, freq=freq, tz=UTC)
    return frame


def _truncated_equal(func, frame: pd.DataFrame, cuts: tuple[int, ...]) -> None:
    full = func(frame)
    for cut in cuts:
        part = func(frame.iloc[:cut])
        if isinstance(full, pd.DataFrame):
            pd.testing.assert_frame_equal(part, full.iloc[:cut], check_exact=False, rtol=1e-9, atol=1e-9)
        else:
            pd.testing.assert_series_equal(part, full.iloc[:cut], check_exact=False, rtol=1e-9, atol=1e-9)


# ------------------------------------------------------------------ linreg
def test_linreg_matches_rolling_polyfit() -> None:
    frame = synthetic(1, 200)
    n, offset = 14, 0
    out = g.linreg(frame, "close", n, offset)
    close = frame["close"].to_numpy()
    for t in (13, 50, 199):
        window = close[t - n + 1:t + 1]
        slope, intercept = np.polyfit(np.arange(n), window, 1)
        assert out.iloc[t] == pytest.approx(intercept + slope * (n - 1 - offset))
    assert out.iloc[:13].isna().all()
    shifted = g.linreg(frame, "close", n, 2)
    t = 100
    slope, intercept = np.polyfit(np.arange(n), close[t - n + 1:t + 1], 1)
    assert shifted.iloc[t] == pytest.approx(intercept + slope * (n - 1 - 2))


def test_linreg_matches_talib() -> None:
    talib = pytest.importorskip("talib")
    frame = synthetic(2, 400)
    np.testing.assert_allclose(g.linreg(frame, "close", 20).to_numpy()[19:], talib.LINEARREG(frame["close"].to_numpy(), 20)[19:], atol=1e-8)


# ------------------------------------------------------------------ chandelier (CEZLSMA.pine)
def _pine_chandelier(frame: pd.DataFrame, length: int, mult: float) -> tuple[list, list, list]:
    close = frame["close"].to_numpy()
    high, low = frame["high"].to_numpy(), frame["low"].to_numpy()
    atr_values = g.atr(frame, length).to_numpy()
    long_hist, short_hist, dir_hist = [], [], []
    direction = 1
    for t in range(len(close)):
        atr_t = mult * atr_values[t]
        window = close[max(0, t - length + 1):t + 1]
        long_stop = (window.max() - atr_t) if len(window) == length else math.nan
        short_stop = (window.min() + atr_t) if len(window) == length else math.nan
        long_prev = long_hist[-1] if t > 0 and not math.isnan(long_hist[-1]) else long_stop
        short_prev = short_hist[-1] if t > 0 and not math.isnan(short_hist[-1]) else short_stop
        prev_close = close[t - 1] if t > 0 else math.nan
        if prev_close > long_prev:
            long_stop = max(long_stop, long_prev)
        if prev_close < short_prev:
            short_stop = min(short_stop, short_prev)
        if close[t] > short_prev:
            direction = 1
        elif close[t] < long_prev:
            direction = -1
        long_hist.append(long_stop)
        short_hist.append(short_stop)
        dir_hist.append(direction)
    return long_hist, short_hist, dir_hist


@pytest.mark.parametrize("length,mult", [(1, 2), (22, 3)])
def test_chandelier_matches_pine_port(length: int, mult: float) -> None:
    frame = synthetic(3, 700)
    result = g.chandelier(frame, length, mult)
    long_stop, short_stop, direction = _pine_chandelier(frame, length, mult)
    np.testing.assert_allclose(result["long_stop"].to_numpy(), long_stop, equal_nan=True)
    np.testing.assert_allclose(result["short_stop"].to_numpy(), short_stop, equal_nan=True)
    np.testing.assert_array_equal(result["dir"].to_numpy(), direction)
    assert (np.diff(result["dir"].to_numpy()) != 0).sum() > 5  # direction flips happen


# ------------------------------------------------------------------ Andean oscillator (DHLAOS.pine)
def _pine_andean(frame: pd.DataFrame, length: int, sig_length: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    alpha = 2.0 / (length + 1)
    up1 = up2 = dn1 = dn2 = 0.0
    bull, bear = [], []
    for c, o in zip(frame["close"], frame["open"]):
        up1 = max(c, o, up1 - (up1 - c) * alpha)
        up2 = max(c * c, o * o, up2 - (up2 - c * c) * alpha)
        dn1 = min(c, o, dn1 + (c - dn1) * alpha)
        dn2 = min(c * c, o * o, dn2 + (c * c - dn2) * alpha)
        bull.append(math.sqrt(dn2 - dn1 * dn1) if dn2 - dn1 * dn1 >= 0 else math.nan)
        bear.append(math.sqrt(up2 - up1 * up1) if up2 - up1 * up1 >= 0 else math.nan)
    bull, bear = np.array(bull), np.array(bear)
    peak = pd.DataFrame({"close": np.maximum(bull, bear)}, index=frame.index)
    return bull, bear, g.ema(peak, "close", sig_length).to_numpy()


def test_andean_matches_pine_port() -> None:
    frame = synthetic(4, 600)
    result = g.andean(frame, 50, 9)
    bull, bear, signal = _pine_andean(frame, 50, 9)
    np.testing.assert_allclose(result["bull"].to_numpy(), bull, equal_nan=True)
    np.testing.assert_allclose(result["bear"].to_numpy(), bear, equal_nan=True)
    np.testing.assert_allclose(result["signal"].to_numpy(), signal, equal_nan=True)


# ------------------------------------------------------------------ Nadaraya-Watson (NWERSIASF.pine)
def test_nadaraya_watson_matches_pine_loops() -> None:
    frame = synthetic(5, 140)
    n, h, mult = 30, 4.0, 3.0
    result = g.nadaraya_watson(frame, h=h, carpan=mult, n=n)
    close = frame["close"].to_numpy()
    coefs = [math.exp(-(i ** 2) / (h * h * 2)) for i in range(n)]
    den = sum(coefs)
    mid = [math.nan] * len(close)
    for t in range(n - 1, len(close)):
        mid[t] = sum(close[t - i] * coefs[i] for i in range(n)) / den
    mae = [math.nan] * len(close)
    for t in range(len(close)):
        window = [abs(close[k] - mid[k]) for k in range(t - (n - 1) + 1, t + 1)] if t - (n - 1) + 1 >= 0 else None
        if window is not None and not any(math.isnan(v) for v in window):
            mae[t] = sum(window) / (n - 1) * mult
    np.testing.assert_allclose(result["mid"].to_numpy(), mid, equal_nan=True)
    np.testing.assert_allclose(result["upper"].to_numpy(), np.array(mid) + np.array(mae), equal_nan=True)
    np.testing.assert_allclose(result["lower"].to_numpy(), np.array(mid) - np.array(mae), equal_nan=True)
    assert np.isfinite(result["upper"].to_numpy()).sum() > 20


# ------------------------------------------------------------------ Laguerre RSI (Ehlers)
def test_laguerre_rsi_matches_ehlers_recursion() -> None:
    frame = synthetic(6, 300)
    alpha = 0.2
    l0 = l1 = l2 = l3 = 0.0
    expected = []
    for price in frame["close"]:
        p0, p1, p2 = l0, l1, l2
        l0 = alpha * price + (1 - alpha) * p0
        l1 = -(1 - alpha) * l0 + p0 + (1 - alpha) * l1
        l2 = -(1 - alpha) * l1 + p1 + (1 - alpha) * l2
        l3 = -(1 - alpha) * l2 + p2 + (1 - alpha) * l3
        cu = max(l0 - l1, 0) + max(l1 - l2, 0) + max(l2 - l3, 0)
        cd = max(l1 - l0, 0) + max(l2 - l1, 0) + max(l3 - l2, 0)
        expected.append(cu / (cu + cd) if cu + cd else math.nan)
    result = g.laguerre_rsi(frame, "close", alpha)
    np.testing.assert_allclose(result.to_numpy(), expected, equal_nan=True)
    valid = result.dropna()
    assert ((valid >= 0) & (valid <= 1)).all() and valid.nunique() > 50


# ------------------------------------------------------------------ CDLHAMMER vs TA-Lib
def _wicky_frame(seed: int, n: int = 2500) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    open_ = close + rng.normal(0, 0.3, n)
    high = np.maximum(close, open_) + np.abs(rng.normal(0, 0.3, n)) * (rng.random(n) < 0.5)
    low = np.minimum(close, open_) - np.abs(rng.normal(0, 1, n)) * (rng.random(n) < 0.5)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1.0},
                        index=pd.bdate_range("2010-01-01", periods=n, tz=UTC))


def test_cdl_hammer_matches_talib_exactly() -> None:
    talib = pytest.importorskip("talib")
    frame = _wicky_frame(1)
    reference = talib.CDLHAMMER(*(frame[c].to_numpy() for c in ("open", "high", "low", "close")))
    mine = g.cdl_hammer(frame).to_numpy()
    assert (reference == 100).sum() > 50
    np.testing.assert_array_equal(mine, reference)


def test_cdl_hammer_flags_a_textbook_hammer_only() -> None:
    n = 14
    index = pd.bdate_range("2021-01-04", periods=n, tz=UTC)
    # ten ordinary bars (body 1, range 3), then a down bar, then a small-body long-lower-wick hammer with no upper wick
    open_ = [100.0] * 12 + [95.0, 93.9]
    close = [101.0] * 12 + [94.0, 94.0]
    high = [102.0] * 12 + [95.2, 94.05]
    low = [99.0] * 12 + [93.5, 91.5]
    frame = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1.0}, index=index)
    flags = g.cdl_hammer(frame)
    assert flags.iloc[-1] == 100 and flags.iloc[:-1].sum() == 0


# ------------------------------------------------------------------ expression: barssince
def test_barssince() -> None:
    cond = pd.Series([False, True, False, False, True, False])
    out = _expr.parse("barssince(a)").evaluate({"a": cond}).tolist()
    assert math.isnan(out[0]) and out[1:] == [0.0, 1.0, 2.0, 0.0, 1.0]


# ------------------------------------------------------------------ no look-ahead
@pytest.mark.parametrize("func", [
    lambda f: g.linreg(f, "close", 20),
    lambda f: g.chandelier(f, 5, 2.0),
    lambda f: g.andean(f, 50, 9),
    lambda f: g.nadaraya_watson(f, h=8.0, carpan=3.0, n=60),
    lambda f: g.laguerre_rsi(f, "close", 0.2),
    lambda f: g.cdl_hammer(f),
])
def test_primitives_have_no_lookahead(func) -> None:
    _truncated_equal(func, _wicky_frame(9, 400), (150, 233, 399))


CARDS = ["A3-002a", "A3-002f", "A3-002h", "A3-002i", "A3-010b", "O1-039", "P3-008"]


@pytest.mark.parametrize("card_id", CARDS)
def test_converted_cards_have_no_lookahead(card_id: str) -> None:
    card = _card(card_id)
    assert card["ozel_kod"] is False
    frame = _frame(11, 2600, "D" if card["tf"] == "1D" else "15min")
    full, _ = card_frame_signals(card, frame, week_end="SUN")
    for cut in (1100, 1777, 2300):
        part, _ = card_frame_signals(card, frame.iloc[:cut], week_end="SUN")
        columns = [c for c in ("entry", "exit", "atr") if c in full.columns]
        pd.testing.assert_frame_equal(part[columns], full[columns].iloc[:cut], check_exact=False, rtol=1e-9, atol=1e-9)


# ------------------------------------------------------------------ DHLAOS entry vs the Pine loops
def test_dhlaos_card_matches_the_pine_loops() -> None:
    card = _card("A3-002f")
    frame = _frame(12, 6000, "5min")
    signals, _ = card_frame_signals(card, frame, week_end="SUN")
    bull, bear, signal = _pine_andean(frame, 50, 9)
    high = frame["high"].to_numpy()
    daily_low = g.compute(frame, {"f": "low", "tf": "1D"}).to_numpy()
    size = len(frame)
    n, k = 300, 50
    expected = np.zeros(size, dtype=bool)
    for t in range(size):
        if t < n + 5 or not (bull[t - 1] <= signal[t - 1] and bull[t] > signal[t]):
            continue
        li = None
        cancelled = False
        for i in range(2, n + 1):
            if t - i - 1 < 0:
                break
            a = bull[t - i - 1] >= bear[t - i - 1] and bull[t - i] < bear[t - i]
            b = bull[t - i - 1] >= signal[t - i - 1] and bull[t - i] < signal[t - i]
            c = bull[t - i - 1] <= signal[t - i - 1] and bull[t - i] > signal[t - i]
            d = bull[t - i - 1] <= bear[t - i - 1] and bull[t - i] > bear[t - i]
            if a or b or c:
                cancelled = True
                break
            if d:
                li = i
                break
        if cancelled or li is None:
            continue  # no event in the window: the source would reuse a stale `li`; the card skips
        for i in range(li, li + k + 1):
            if t - i >= 0 and high[t - i] < daily_low[t - i] and bull[t - i] < bear[t - i]:
                expected[t] = True
                break
    entries = signals["entry"].to_numpy()
    start = n + 5
    np.testing.assert_array_equal(entries[start:], expected[start:])
    assert expected.sum() >= 1


# ------------------------------------------------------------------ LRCUTB sell signal (UT Bot) vs Pine text
def test_lrcutb_sell_signal_matches_pine_logic() -> None:
    frame = synthetic(13, 800)
    close = frame["close"].to_numpy()
    atr_values = g.atr(frame, 1).to_numpy()
    stop_prev = 0.0
    stops, sell = [], []
    for t in range(len(close)):
        loss = 2 * atr_values[t]
        if math.isnan(loss):
            stops.append(math.nan)
            sell.append(False)
            continue
        prev_close = close[t - 1] if t else math.nan
        iff_1 = close[t] - loss if close[t] > stop_prev else close[t] + loss
        iff_2 = min(stop_prev, close[t] + loss) if (close[t] < stop_prev and prev_close < stop_prev) else iff_1
        stop = max(stop_prev, close[t] - loss) if (close[t] > stop_prev and prev_close > stop_prev) else iff_2
        previous_stop_value = stops[-1] if stops and not math.isnan(stops[-1]) else math.nan
        below = (stop > close[t]) and (not math.isnan(previous_stop_value)) and previous_stop_value <= close[t - 1]  # crossover(stop, ema(close,1))
        sell.append(bool(close[t] < stop and below))
        stops.append(stop)
        stop_prev = stop
    card = _card("A3-002i")
    env = g.build_env(frame, card["gostergeler"])
    utstop = env["utstop"].to_numpy()
    np.testing.assert_allclose(utstop[1:], np.array(stops)[1:], equal_nan=True)
    mine = _expr.parse("cross_under(close, utstop)").evaluate(env).to_numpy()
    np.testing.assert_array_equal(mine[2:], np.array(sell)[2:])
    assert sum(sell) > 10


# ------------------------------------------------------------------ Strategy002 ingredients
def test_strategy002_indicators_match_talib_and_qtpylib() -> None:
    talib = pytest.importorskip("talib")
    frame = synthetic(14, 500)
    high, low, close = (frame[c].to_numpy() for c in ("high", "low", "close"))
    slowk, _ = talib.STOCH(high, low, close)
    mine = g.stoch(frame, k=5, d=3, smooth=3)["k"].to_numpy()
    np.testing.assert_allclose(mine[10:], slowk[10:], atol=1e-8)
    typical = (frame["high"] + frame["low"] + frame["close"]) / 3
    expected_lower = typical.rolling(20).mean() - 2 * typical.rolling(20).std()  # pandas default = ddof 1 (qtpylib)
    pd.testing.assert_series_equal(g.bb(frame, "typical", 20, 2.0, ddof=1)["lower"], expected_lower, check_names=False)
    rsi = pd.Series(talib.RSI(close, 14), index=frame.index)
    fisher = (np.exp(2 * 0.1 * (rsi - 50)) - 1) / (np.exp(2 * 0.1 * (rsi - 50)) + 1)
    np.testing.assert_allclose(g.fisher_rsi(frame, "close", 14).to_numpy()[20:], fisher.to_numpy()[20:], atol=1e-8)
    np.testing.assert_allclose(g.sar(frame).to_numpy()[2:], talib.SAR(high, low, 0.02, 0.2)[2:], atol=1e-9)


# ------------------------------------------------------------------ integration through the scan path
@pytest.mark.parametrize("card_id", ["A3-002a", "A3-002i", "A3-010b", "O1-039", "P3-008"])
def test_converted_cards_run_in_the_engine(card_id: str) -> None:
    card = _card(card_id)
    freq = "D" if card["tf"] == "1D" else "15min"
    data = {}
    for k in range(4):
        frame = synthetic(30 + k, 4000, calendar=True)
        frame.index = pd.date_range("2020-01-01", periods=4000, freq=freq, tz=UTC)
        if card_id == "A3-010b":  # reach the oversold hammer pocket now and then
            frame["low"] = frame["low"] * (1 - 0.02 * (np.arange(4000) % 37 == 0))
        data[f"S{k}"] = frame
    start, end = data["S0"].index[300], data["S0"].index[-1]
    prepared = tarama.prepare(card, data, "KRIPTO25", start=start, end=end)
    result = prepared.run()
    assert result.equity.notna().all()
    if card_id != "A3-010b":
        assert len(result.trades) > 0
