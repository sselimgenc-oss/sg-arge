"""RD-02 Ay sonu SPY/TLT (arastirma/reddit/ozet.md A): ay bitimine 4 islem gunu kala SPY ve TLT'nin ay basindan beri getirisi karsilastirilir.
SPY TLT'nin %2+ gerisindeyse o kapanista al, ayin son kapanisinda sat; %2+ onde ise ayin son kapanisinda al, sonraki ayin 3. islem gunu
kapanisinda sat. TLT yalniz olcut (alinmaz); dolum kapanisla."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine.kart_sinyal import EndeksYok, KartPlan
from strategies.ozel import tv_ortak as T

ROOT = Path(__file__).resolve().parents[2]


def benchmark_frame(data: Mapping[str, pd.DataFrame], name: str) -> pd.DataFrame:
    """Olcut enstrumani: kosucunun verdigi cerceve ya da arsiv (data/daily/<ad>.parquet)."""
    if name in data:
        return data[name]
    path = ROOT / "data" / "daily" / f"{name}.parquet"
    if not path.exists():
        raise EndeksYok(f"olcut verisi yok: {name}")  # tarama bunu adli atlama sayar (veri yok), coktu saymaz
    from data.fetch import normalize_ohlcv  # noqa: PLC0415

    return normalize_ohlcv(pd.read_parquet(path))


def signals(frame: pd.DataFrame, p: Mapping[str, Any], measure: pd.Series) -> pd.DataFrame:
    close = frame["close"]
    index = frame.index
    naive = index.tz_localize(None) if index.tz is not None else index
    month = pd.Series(naive.to_period("M"), index=index)
    last_prev = close.groupby(month).last().shift(1)  # onceki ayin son kapanisi
    base = month.map(last_prev)
    gauge = measure.reindex(index, method="ffill")
    gauge_base = month.map(gauge.groupby(month).last().shift(1))
    spy_ret, tlt_ret = close / base - 1.0, gauge / gauge_base - 1.0
    diff = (spy_ret - tlt_ret).to_numpy(dtype=float)
    pos_in_month_from_end = month.groupby(month).cumcount(ascending=False).to_numpy()  # 0 = ayin son islem gunu
    pos_in_month_from_start = month.groupby(month).cumcount().to_numpy()  # 0 = ayin ilk islem gunu
    n = len(frame)
    entry, exit_ = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    left = int(p["days_left"])  # 4 islem gunu kala -> sondan 5. gun
    threshold = float(p["gap_pct"]) / 100.0
    sell_day = int(p["next_month_sell_day"])
    for i in range(n):
        if pos_in_month_from_end[i] != left or not np.isfinite(diff[i]):
            continue
        last_loc = i + left  # ayin son islem gunu
        if last_loc >= n:
            continue
        if diff[i] <= -threshold:
            entry[i] = True
            exit_[last_loc] = True
        elif diff[i] >= threshold:
            entry[last_loc] = True
            sell_loc = next((j for j in range(last_loc + 1, n) if pos_in_month_from_start[j] == sell_day - 1), None)
            if sell_loc is not None:
                exit_[sell_loc] = True
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=index)


def build_plan(card: Mapping[str, Any], data: Mapping[str, pd.DataFrame], **_) -> KartPlan:
    params = dict(card.get("parametreler") or {})
    measure_name = str(params["measure"])
    measure = benchmark_frame(data, measure_name)["close"]
    tradable = {k: v for k, v in data.items() if k != measure_name}
    return T.plan(card, tradable, lambda frame, q: signals(frame, q, measure))
