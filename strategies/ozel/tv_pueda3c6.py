"""TV-PUEDA3c6 Confluence x4 Signal Test Bench: varsayilan tetikleyici MT-Stochastic (5 bilesenli skor), 10 bar sabit cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def _stoch(src: pd.Series, high: pd.Series, low: pd.Series, n: int) -> pd.Series:
    """ta.stoch: 100 * (src - lowest(low, n)) / (highest(high, n) - lowest(high-low araligi)); aralik 0 ise NaN."""
    lo, hi = T.lowest(low, n), T.highest(high, n)
    rng = (hi - lo).where(hi != lo)
    return 100.0 * (src - lo) / rng


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, high, low = frame["close"], frame["high"], frame["low"]
    mk1 = T.sma(_stoch(close, high, low, 20), 12)
    md1 = T.sma(mk1, 12)
    mk2 = T.sma(_stoch(close, high, low, 10), 6)
    md2 = T.sma(mk2, 6)
    mk3 = T.sma(_stoch(close, high, low, 5), 3)
    md3 = T.sma(mk3, 3)
    mrsi = T.rsi(close, 14)
    mk = T.sma(_stoch(mrsi, mrsi, mrsi, 14), 3)
    md = T.sma(mk, 3)
    sve_r = T.rsi(close, 13)
    sve_lo = T.sma(sve_r - T.lowest(sve_r, 5), 8)
    sve_rg = T.sma(T.highest(sve_r, 5) - T.lowest(sve_r, 5), 8)
    sve = sve_lo / (0.1 + sve_rg) * 100.0
    kd_ratio = (mk / md).where(md != 0, 1.0)
    mt_pos = T.percentrank(kd_ratio, 100)

    def n(cond: pd.Series) -> np.ndarray:
        return cond.to_numpy(dtype=bool).astype(int)  # NaN karsilastirmasi False -> 0

    up = n(mk1 >= md1) + n(mk2 >= md2) + n(mk3 >= md3) + n(sve > 20) + n(mt_pos >= 50)
    dn = n(mk1 <= md1) + n(mk2 <= md2) + n(mk3 <= md3) + n(sve < 80) + n(mt_pos < 50)
    score = pd.Series(up - dn, index=frame.index)
    thresh = int(p["mt_thresh"])
    bull, bear = score >= thresh, score <= -thresh
    trig_up = bull & ~bull.shift(1, fill_value=False)
    trig_dn = bear & ~bear.shift(1, fill_value=False)
    start = pd.Timestamp(str(p["start"]), tz="UTC")
    in_range = pd.Series(frame.index >= start, index=frame.index)
    return pd.DataFrame({"entry": trig_up & in_range, "exit": trig_dn & in_range, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
