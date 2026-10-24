"""TV-yvDyq0pv Moon Phases Strategy [LuxAlgo]: ay evresi (UNIX zamanindan) long/short, sinyal bari kapanisindan dolum."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    time_ms = np.asarray((frame.index - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(milliseconds=1), dtype=float)  # bar acilis zamani (ms); Pine `time`
    cycle = float(p["cycle_ms"])
    diff = pd.Series(np.mod(float(p["new_moon_ms"]) + time_ms + 2.0 * float(p["day_ms"]), cycle) / cycle, index=frame.index)
    newmoon = T.crossover(diff, 0.5)
    fullmoon = (diff < diff.shift(1)).fillna(False)
    src = frame["close"]
    ev = newmoon | fullmoon
    higher = T.valuewhen(ev, src, 0) > T.valuewhen(ev, src, 1)
    lower = T.valuewhen(ev, src, 0) < T.valuewhen(ev, src, 1)
    rules = {"New Moon": newmoon, "Full Moon": fullmoon, "Higher Moon": higher, "Lower Moon": lower}
    long = rules[p["buy"]]
    short = rules[p["sell"]]
    return pd.DataFrame({"entry": long, "exit": short, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
