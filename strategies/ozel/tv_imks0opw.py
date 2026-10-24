"""TV-IMKs0OPw Volatility Reversion Scalper: Williams VIX Fix yuzdelik esigi + Fibonacci Bollinger alt bandi + donus mumu; %5 hedef."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from strategies.ozel import tv_ortak as T


def percentile_linear(s: pd.Series, length: int, pct: float) -> pd.Series:
    """ta.percentile_linear_interpolation(s, length, pct): son `length` degerin (guncel dahil) pct'inci yuzdeligi, dogrusal ara deger."""
    return s.astype(float).rolling(int(length)).quantile(float(pct) / 100.0, interpolation="linear")


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, open_, low = frame["close"], frame["open"], frame["low"]
    top = T.highest(close, int(p["pd"]))
    wvf = (top - low) / top * 100.0
    # Pine cagrisi ta.percentile_linear_interpolation(wvf, int(ph*100), lb): yazar 2. ve 3. argumani (length, yuzde) ters vermis
    range_high = percentile_linear(wvf, int(p["percentile_len"]), float(p["percentile_pct"]))
    basis = T.sma(close, int(p["bb_length"]))
    lower = basis - float(p["mult_fib"]) * T.stdev(close, int(p["bb_length"]))
    cond1 = (close <= lower) | (open_ <= lower)
    cond2 = wvf >= range_high
    cond3 = (close > open_) & (close.shift(1) < open_.shift(1))
    start, end = pd.Timestamp(str(p["start"]), tz="UTC"), pd.Timestamp(str(p["end"]), tz="UTC")
    in_range = pd.Series((frame.index >= start) & (frame.index <= end), index=frame.index)
    entry = (cond1 & cond2 & cond3 & in_range).fillna(False)
    return pd.DataFrame({"entry": entry, "exit": False, "atr": T.atr(frame, 14), "target_pct": float(p["tp_perc"])}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
