"""Calendar primitives for the card expression language.

All helpers take a DatetimeIndex (tz-aware or naive) and return a boolean or
integer Series on that index. Trading days are the distinct dates present in
the index, so intraday frames mark every bar of the matching day.

Limitation: the first and last month of a frame are ranked from the data that
is present. A frame that starts or ends mid-month ranks those months wrongly.
"""

from __future__ import annotations

import pandas as pd


def _dates(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    naive = index.tz_localize(None) if index.tz is not None else index
    return naive.normalize()


def _month_ranks(index: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series]:
    dates = _dates(index)
    unique = pd.DataFrame({"d": pd.DatetimeIndex(sorted(set(dates)))})
    month = unique["d"].dt.to_period("M")
    unique["from_start"] = unique.groupby(month).cumcount() + 1
    unique["from_end"] = unique.groupby(month)["d"].transform("count") - unique["from_start"] + 1
    lookup = unique.set_index("d")
    return (
        pd.Series(lookup["from_start"].reindex(dates).to_numpy(), index=index),
        pd.Series(lookup["from_end"].reindex(dates).to_numpy(), index=index),
    )


def ay_islem_gunu_bastan(index: pd.DatetimeIndex, k: int) -> pd.Series:
    """True on bars of the k-th trading day of the month (k >= 1)."""
    if int(k) < 1:
        raise ValueError("k must be >= 1")
    return _month_ranks(index)[0] == int(k)


def ay_islem_gunu_sondan(index: pd.DatetimeIndex, k: int) -> pd.Series:
    """True on bars of the k-th trading day counted from the month end (k >= 1)."""
    if int(k) < 1:
        raise ValueError("k must be >= 1")
    return _month_ranks(index)[1] == int(k)


def haftanin_gunu(index: pd.DatetimeIndex) -> pd.Series:
    """Weekday as int, Monday=0 .. Sunday=6."""
    return pd.Series(_dates(index).weekday.to_numpy(), index=index)
