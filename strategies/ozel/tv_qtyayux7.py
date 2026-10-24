"""TV-QTYaYuX7 Hull Fisher: Hull MA uzerinde Fisher donusumu (ozyinelemeli) + CCI/HMA filtreleri; kaynak fiyat open."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def cci(s: pd.Series, n: int) -> pd.Series:
    mean = s.rolling(n).mean()
    dev = s.rolling(n).apply(lambda w: float(np.abs(w - w.mean()).mean()), raw=True)
    return (s - mean) / (0.015 * dev)


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    price = frame["open"] if p["source"] == "open" else frame["close"]
    period, length = int(p["period"]), int(p["length"])
    line1, line5 = float(p["top_line"]), float(p["bottom_line"])
    hma = T.hma(price, period)
    hma2 = hma.shift(1)
    high_, low_ = T.highest(hma, length), T.lowest(hma, length)
    h = hma.to_numpy()
    hi, lo = high_.to_numpy(), low_.to_numpy()
    size = len(frame)
    value = np.full(size, np.nan)
    value1 = np.full(size, np.nan)
    prev, prev1 = 0.0, 0.0  # nz(value[1]), nz(value1[1])
    for i in range(size):
        raw = 0.66 * ((h[i] - lo[i]) / max(hi[i] - lo[i], 0.001) - 0.5) + 0.67 * prev if not (np.isnan(h[i]) or np.isnan(lo[i]) or np.isnan(hi[i])) else np.nan
        v = np.nan if np.isnan(raw) else (0.999 if raw > 0.99 else -0.999 if raw < -0.99 else raw)
        value[i] = v
        v1 = np.nan if np.isnan(v) else 0.5 * np.log((1 + v) / max(1 - v, 0.001)) + 0.5 * prev1
        value1[i] = v1
        prev = 0.0 if np.isnan(v) else v
        prev1 = 0.0 if np.isnan(v1) else v1
    v1s = pd.Series(value1, index=frame.index)
    v2s = v1s.shift(1)
    cci1 = cci(price, period)
    cci2 = cci1.shift(1)
    long7 = (v1s > v2s) & (v1s < line5) & (cci1 > cci2) & (hma > hma2) & bool(p["entry1"]) & bool(p["use_cci"]) & bool(p["use_hma"])
    long8 = (v1s > v2s) & (v1s > 0) & (cci1 > cci2) & (hma > hma2) & bool(p["entry2"]) & bool(p["use_cci"]) & bool(p["use_hma"])
    exit_ = (bool(p["hma_close"]) & (hma < hma2)) | (bool(p["fish_close"]) & (v1s < v2s))
    # ters yonde short girisi de long'u kapatir; short kosullari zaten value1 < value2 ve HMA < HMA2 icerir (exit ile ortuk)
    return pd.DataFrame({"entry": long7 | long8, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
