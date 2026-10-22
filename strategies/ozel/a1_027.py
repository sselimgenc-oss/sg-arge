"""A1-027 Bjorgum Double Tap: source-described alternating pivot matrix."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine.gosterge import atr
from engine.kart_sinyal import KartPlan


def signals(frame: pd.DataFrame, *, length: int = 50, tolerance: float = 15.0, fib: float = 100.0) -> pd.DataFrame:
    """Recognise the long double-bottom only when the neckline is later crossed."""
    high, low, close = frame["high"], frame["low"], frame["close"]
    new_high = high.eq(high.rolling(length, min_periods=length).max())
    new_low = low.eq(low.rolling(length, min_periods=length).min())
    entry = np.zeros(len(frame), dtype=bool)
    stop_level = np.full(len(frame), np.nan)
    target_level = np.full(len(frame), np.nan)
    pivots: list[list[Any]] = []  # [kind, price, bar]; newest four mirror the Pine pivot matrix
    direction: str | None = None
    pattern: tuple[float, float, float] | None = None  # neckline, stop, target

    for loc in range(len(frame)):
        if pattern is not None and loc > 0:
            neckline, stop, target = pattern
            crossed = float(close.iat[loc]) > neckline and float(close.iat[loc - 1]) <= neckline
            if crossed:
                entry[loc] = True
                stop_level[loc], target_level[loc] = stop, target
        if new_high.iat[loc] and new_low.iat[loc]:
            kind = "H" if direction == "L" else "L" if direction == "H" else None
        else:
            kind = "H" if new_high.iat[loc] else "L" if new_low.iat[loc] else None
        if kind is not None:
            price = float(high.iat[loc] if kind == "H" else low.iat[loc])
            if kind == direction and pivots:
                more_extreme = price > pivots[-1][1] if kind == "H" else price < pivots[-1][1]
                if more_extreme:
                    pivots[-1] = [kind, price, loc]
            else:
                pivots.append([kind, price, loc])
                pivots = pivots[-4:]
                direction = kind
            pattern = None
            if [pivot[0] for pivot in pivots] == ["H", "L", "H", "L"]:
                y1, y2, y3, y4 = (float(pivot[1]) for pivot in pivots)
                bottom = min(y2, y4)
                height = y3 - max(y2, y4)
                if y1 > y3 and height > 0 and abs(y2 - y4) <= height * tolerance / 100.0:
                    pattern = (y3, bottom, y3 + (y3 - bottom) * fib / 100.0)

    return pd.DataFrame(
        {"entry": entry, "exit": False, "atr": atr(frame, 14),
         "_stop_level": stop_level, "_target_level": target_level}, index=frame.index,
    )


def build_plan(card: Mapping[str, Any], data: Mapping[str, pd.DataFrame], **_: Any) -> KartPlan:
    params = card.get("parametreler") or {}
    output = {symbol: signals(frame, length=int(params["len"]), tolerance=float(params["tol"]), fib=float(params["fib"]))
              for symbol, frame in data.items()}
    stop_values = {symbol: result["_stop_level"].to_numpy() for symbol, result in output.items()}
    target_values = {symbol: result["_target_level"].to_numpy() for symbol, result in output.items()}
    levels = {
        "stop": lambda symbol, loc, _price: float(stop_values[symbol][loc]),
        "target": lambda symbol, loc, _price, _stop: float(target_values[symbol][loc]),
    }
    return KartPlan(output, {"trail_mode": None, "fill_at_close": False, "level_fns": levels}, False)
