"""TV-QA8AC0vs Moon Phase Strategy: Julian gunu tabanli yeni ay / dolunay donum tarihi; faz degisiminde long (yeni ay +1) ve cikis (-1)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def _unix_from_jd(jd: float) -> float:
    """Pine getUNIXTimeFromJD: saat/dakika float bolmesiyle hesaplanir; timestamp() tam sayiya keser, dakika 0 olur."""
    z = math.floor(jd + 0.5)
    f = (jd + 0.5) % 1
    alpha = math.floor((z - 1867216.25) / 36524.25)
    a = z if z < 2299161 else z + 1 + alpha - math.floor(alpha / 4.0)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    day_float = b - d - math.floor(30.6001 * e) + f
    day = int(day_float)
    month = int(e - 1) if e < 13.5 else int(e - 13)
    year = int(c - 4716) if month > 2.5 else int(c - 4715)
    second_total = int((day_float % 1) * 60 * 60 * 24)
    hour = second_total / (60 * 60)
    minute = (second_total - hour * 60 * 60) / 60  # = 0 (hour float)
    second = second_total % 60
    base = datetime(year, month, 1, tzinfo=timezone.utc)
    moment = base + timedelta(days=day - 1, hours=int(hour), minutes=int(minute), seconds=second)
    return moment.timestamp() * 1000.0


def moon_events(close_times: pd.DatetimeIndex) -> np.ndarray:
    """Her bar icin moonType (+1 yeni ay, -1 dolunay, 0 yok); girdi time_close (UTC)."""
    size = len(close_times)
    ms_now = (close_times - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(milliseconds=1)
    years, doys = close_times.year.to_numpy(), close_times.dayofyear.to_numpy()
    out = np.zeros(size, dtype=int)
    prev_last = np.nan
    adjusted = 0
    prev_adjusted = 0
    for i in range(size):
        k = (doys[i] / 364.25 + years[i] - 1900) * 12.3685
        if (k % 1.0) < 0.5:
            k, phase = math.floor(k), 1
        else:
            k, phase = math.floor(k) + 0.5, -1
        a_sun = math.radians(359.2242 + 29.10535608 * k)
        a_moon = math.radians(306.0253 + 385.81691806 * k)
        dev = 0.1734 * math.sin(a_sun) - 0.4068 * math.sin(a_moon)
        last = _unix_from_jd(2415020.75933 + 29.53058868 * k + dev)
        if last >= ms_now[i]:
            last = prev_last  # timeLastMoonPhase[1]
        changed = (not np.isnan(last)) and (not np.isnan(prev_last)) and last != prev_last
        if i == 0:
            adjusted, prev_adjusted = phase, phase
        else:
            prev_adjusted = adjusted
            if changed:
                adjusted = phase
        if i > 0 and adjusted != prev_adjusted:
            out[i] = phase
        prev_last = last
    return out


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    step = frame.index.to_series().diff().median() if len(frame) > 1 else pd.Timedelta(hours=4)
    events = moon_events(frame.index + step)
    return pd.DataFrame({"entry": events == 1, "exit": events == -1, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
