"""Calendar primitives for the card expression language.

All helpers take a DatetimeIndex (tz-aware or naive) and return a boolean or
integer Series on that index. Trading days are the distinct dates present in
the index, so intraday frames mark every bar of the matching day.

Limitation: the first and last month of a frame are ranked from the data that
is present. A frame that starts or ends mid-month ranks those months wrongly.
"""

from __future__ import annotations

import datetime

import pandas as pd
from zoneinfo import ZoneInfo


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


def saat_utc(index: pd.DatetimeIndex) -> pd.Series:
    """Opening hour of each bar in UTC (0-23). Naive indexes are treated as UTC."""
    utc = index.tz_convert("UTC") if index.tz is not None else index
    return pd.Series(utc.hour.to_numpy(), index=index)


def dakika(index: pd.DatetimeIndex) -> pd.Series:
    """Opening minute of each bar in UTC (0-59). Naive indexes are treated as UTC."""
    utc = index.tz_convert("UTC") if index.tz is not None else index
    return pd.Series(utc.minute.to_numpy(), index=index)


def yeni_gun(index: pd.DatetimeIndex) -> pd.Series:
    """True on the first bar of each calendar date, including the very first bar of the data."""
    dates = pd.Series(_dates(index), index=index)
    return (dates != dates.shift(1)).astype(bool)


def ay_gunu(index: pd.DatetimeIndex) -> pd.Series:
    """Day of the month (1-31) of each bar's date."""
    return pd.Series(_dates(index).day.to_numpy(), index=index)


def _easter_sunday(year: int) -> pd.Timestamp:
    """Western (Gregorian) Easter Sunday, anonymous Gregorian algorithm."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return pd.Timestamp(year=year, month=month, day=day)


def paskalya(index: pd.DatetimeIndex, k: int) -> pd.Series:
    """True on bars whose date is ``k`` calendar days after Western Easter Sunday (k may be negative).

    Holy Thursday is ``paskalya(-3)``, the Wednesday before it ``paskalya(-4)``, the Friday
    of the week before Easter week ``paskalya(-9)``. A date without a bar (holiday) yields no signal.
    """
    dates = _dates(index)
    targets = {_easter_sunday(year) + pd.Timedelta(days=int(k)) for year in range(dates.year.min(), dates.year.max() + 1)}
    return pd.Series(dates.isin(list(targets)), index=index)


# --- Yerel saat ilkelleri (T36b, docs/EVRENSEL_KURALLAR.md D17) -------------------------------------------------
# Indeks UTC'ye cevrilir (zaman dilimsiz indeks UTC kabul edilir), sonra ``tz`` (IANA adi) yerel saatine. Yaz/kis
# saati gecisleri tz veritabanindan gelir. Yalniz bar etiketini okurlar, gelecek bar kullanmazlar.


def _yerel(index: pd.DatetimeIndex, tz: str) -> pd.DatetimeIndex:
    try:
        zone = ZoneInfo(str(tz))
    except Exception as exc:  # noqa: BLE001 - bilinmeyen/gecersiz IANA adi
        raise ValueError(f"gecersiz saat dilimi: {tz!r}") from exc
    utc = index.tz_localize("UTC") if index.tz is None else index.tz_convert("UTC")
    return utc.tz_convert(zone)


def saat_yerel(index: pd.DatetimeIndex, tz: str) -> pd.Series:
    """Opening hour (0-23) of each bar in the local time of ``tz`` (e.g. ``"Asia/Tokyo"``)."""
    return pd.Series(_yerel(index, tz).hour.to_numpy(), index=index)


def dakika_yerel(index: pd.DatetimeIndex, tz: str) -> pd.Series:
    """Opening minute (0-59) of each bar in the local time of ``tz``."""
    return pd.Series(_yerel(index, tz).minute.to_numpy(), index=index)


def ay_gunu_yerel(index: pd.DatetimeIndex, tz: str) -> pd.Series:
    """Day of the month (1-31) of each bar's *local* date in ``tz``."""
    return pd.Series(_yerel(index, tz).day.to_numpy(), index=index)


def haftanin_gunu_yerel(index: pd.DatetimeIndex, tz: str) -> pd.Series:
    """Local weekday of each bar in ``tz``, Monday=0 .. Sunday=6."""
    return pd.Series(_yerel(index, tz).weekday.to_numpy(), index=index)


def _is_gunu_geri(day: pd.Timestamp) -> pd.Timestamp:
    """``day`` itself when it is Mon-Fri, otherwise the preceding Friday."""
    while day.weekday() >= 5:
        day = pd.Timestamp(day.to_pydatetime() - datetime.timedelta(days=1))
    return day


def ay_son_is_gunu(index: pd.DatetimeIndex, tz: str, k: int = 1) -> pd.Series:
    """True on bars of the k-th last business day (Mon-Fri) of the *local* month (``k=1`` = the last one).

    Takvime dayanir (veride var olan gunlere degil): kismi ilk/son ay yanlis siralanmaz. Resmi tatiller modellenmez.
    """
    if int(k) < 1:
        raise ValueError("k must be >= 1")
    local = _yerel(index, tz)
    out = pd.Series(False, index=index)
    dates = pd.DatetimeIndex(local.tz_localize(None).normalize())
    for month in sorted(set(dates.to_period("M"))):
        business = pd.bdate_range(month.start_time, month.end_time.normalize())
        if len(business) >= int(k):
            out[dates == business[-int(k)]] = True
    return out


def gotobi(index: pd.DatetimeIndex, tz: str) -> pd.Series:
    """True on bars of a Gotobi day of the local calendar of ``tz``.

    Gotobi = the 5th, 10th, 15th, 20th, 25th and the last day of the month; when such a day falls on a Saturday or
    Sunday the preceding business day (Friday) counts. Japanese public holidays are not modelled (FX still trades on them); the month end therefore equals ``ay_son_is_gunu(tz, 1)``.
    """
    local = _yerel(index, tz)
    dates = pd.DatetimeIndex(local.tz_localize(None).normalize())
    targets: set[pd.Timestamp] = set()
    for month in sorted(set(dates.to_period("M"))):
        for nominal in (5, 10, 15, 20, 25):
            targets.add(_is_gunu_geri(pd.Timestamp(year=month.year, month=month.month, day=nominal)))
        targets.add(_is_gunu_geri(month.end_time.normalize()))
    return pd.Series(dates.isin(list(targets)), index=index)
