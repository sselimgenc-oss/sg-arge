"""Metrics derived from public fills and funding only (never leaderboard ROI)."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import pandas as pd


def _frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["time"] = pd.to_datetime(frame["time"], unit="ms", utc=True, errors="coerce")
    for col in ("closedPnl", "fee", "px", "sz", "startPosition"):
        if col in frame:
            frame[col] = pd.to_numeric(frame[col], errors="coerce").fillna(0.0)
    return frame.dropna(subset=["time"]).sort_values("time").reset_index(drop=True)


def _funding_amount(item: dict[str, Any]) -> float:
    """Accept both documented ``delta.usdc`` and flattened archive rows."""
    value = item.get("delta", item.get("usdc", 0))
    if isinstance(value, dict):
        value = value.get("usdc", 0)
    return float(value or 0)


def closed_round_trips(fills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify a transaction when signed position returns to zero.

    Hyperliquid's ``startPosition`` makes this robust to a partial close; if it
    is absent we reconstruct signed position from side and size.
    """
    data = _frame(fills)
    open_time: dict[str, pd.Timestamp] = {}
    position: defaultdict[str, float] = defaultdict(float)
    rows: list[dict[str, Any]] = []
    for row in data.to_dict("records"):
        coin = str(row.get("coin", ""))
        before = float(row.get("startPosition", position[coin]))
        side = str(row.get("side", ""))
        signed = float(row.get("sz", 0.0)) * (-1 if side in {"A", "Sell", "sell"} else 1)
        after = before + signed
        if abs(before) < 1e-12 and abs(after) > 1e-12:
            open_time[coin] = row["time"]
        if abs(before) > 1e-12 and abs(after) < 1e-12:
            start = open_time.pop(coin, row["time"])
            rows.append({"coin": coin, "open_time": start, "close_time": row["time"],
                         "holding_hours": (row["time"] - start).total_seconds() / 3600,
                         "net_pnl": float(row.get("closedPnl", 0)) - float(row.get("fee", 0))})
        position[coin] = after
    return rows


def martingale_ratio(fills: list[dict[str, Any]]) -> tuple[float, int]:
    """Share of same-direction additions made while the open position is under water.

    An addition never closes PnL, so ``closedPnl`` cannot show it; instead the running average entry price per coin
    is rebuilt from the fills and the addition's price is compared with it. Returns (ratio, number of additions).
    """
    data = _frame(fills)
    position: defaultdict[str, float] = defaultdict(float)
    entry: dict[str, float] = {}
    additions = losing = 0
    for row in data.to_dict("records"):
        coin = str(row.get("coin", ""))
        before = float(row.get("startPosition", position[coin]))
        signed = float(row.get("sz", 0)) * (-1 if str(row.get("side", "")) in {"A", "Sell", "sell"} else 1)
        px = float(row.get("px", 0))
        after = before + signed
        if abs(before) > 1e-12 and before * signed > 0:
            if coin in entry:  # opening fill seen: we know the average entry
                additions += 1
                if (px - entry[coin]) * (1 if before > 0 else -1) < 0:
                    losing += 1
                entry[coin] = (entry[coin] * abs(before) + px * abs(signed)) / abs(after)
        elif abs(before) < 1e-12 or before * after < 0:
            entry[coin] = px  # new position (or flip): fresh average
        if abs(after) < 1e-12:
            entry.pop(coin, None)
        position[coin] = after
    return (losing / additions if additions else 0.0), additions


def calculate_metrics(fills: list[dict[str, Any]], funding: list[dict[str, Any]] | None = None,
                      portfolio: list[dict[str, Any]] | None = None, liquid_coins: set[str] | None = None,
                      leverages: list[float] | None = None, account_value: float | None = None,
                      martingale_max_ratio: float = 0.25, martingale_min_additions: int = 5) -> dict[str, Any]:
    """``account_value`` is the return denominator when no ``portfolio`` history is given (never 1 USD)."""
    data = _frame(fills)
    funding_frame = pd.DataFrame({"time": pd.to_datetime([x.get("time") for x in funding or []], unit="ms", utc=True),
                                  "net_pnl": [_funding_amount(x) for x in funding or []]})
    if data.empty:
        return {"history_days": 0, "closed_trades": 0, "martingale_signal": False}
    data["net_pnl"] = data["closedPnl"] - data["fee"]
    if not funding_frame.empty:
        cash = pd.concat([data[["time", "net_pnl"]], funding_frame[["time", "net_pnl"]]]).sort_values("time")
    else:
        cash = data[["time", "net_pnl"]]
    daily = cash.set_index("time")["net_pnl"].resample("1D").sum()
    denominator = float(account_value) if account_value and account_value > 0 else 1.0
    if portfolio:
        values = [float(x.get("accountValue", x.get("value", 0))) for x in portfolio]
        positive = [x for x in values if x > 0]
        if positive:
            denominator = sum(positive) / len(positive)
    returns = daily / denominator
    downside = returns[returns < 0]
    sortino = (returns.mean() / math.sqrt((downside ** 2).mean()) * math.sqrt(365)
               if len(downside) and (downside ** 2).mean() > 0 else None)
    equity = denominator + daily.cumsum()
    drawdown = equity / equity.cummax() - 1
    mdd = abs(float(drawdown.min()))
    elapsed_years = (daily.index[-1] - daily.index[0]).total_seconds() / (365.25 * 86400)
    # Annualising a one-day record is meaningless and may overflow numerically.
    cagr = (float(equity.iloc[-1]) / denominator) ** (1 / elapsed_years) - 1 if denominator > 0 and equity.iloc[-1] > 0 and elapsed_years >= 1 / 365 else None
    rounds = closed_round_trips(fills)
    trade_pnl = [x["net_pnl"] for x in rounds]
    wins = [x for x in trade_pnl if x > 0]
    losses = [x for x in trade_pnl if x < 0]
    without_best = [x for x in trade_pnl if x != max(trade_pnl, default=0)]
    gross_loss = abs(sum(x for x in without_best if x < 0))
    volumes = (data["px"].abs() * data["sz"].abs()).groupby(data.get("coin", "")).sum()
    total_volume = float(volumes.sum())
    liquid_share = (float(volumes[volumes.index.isin(liquid_coins or set())].sum()) / total_volume if total_volume else 0.0)
    ratio, additions = martingale_ratio(fills)
    return {
        "history_days": int((data.time.iloc[-1] - data.time.iloc[0]).total_seconds() // 86400),
        "closed_trades": len(rounds), "profitable_month_ratio": float((daily.resample("MS").sum() > 0).mean()),
        "sortino": sortino, "calmar": (cagr / mdd if cagr is not None and mdd else None),
        "ulcer_index": float(math.sqrt((drawdown.pow(2)).mean())),
        "largest_trade_share": (max(wins) / sum(wins) if sum(wins) else None),
        "profit_factor_without_best": (sum(x for x in without_best if x > 0) / gross_loss if gross_loss else None),
        "median_holding_hours": float(pd.Series([x["holding_hours"] for x in rounds]).median()) if rounds else None,
        "median_leverage": float(pd.Series(leverages or []).median()) if leverages else None,
        "max_leverage": max(leverages) if leverages else None, "liquid_coin_share": liquid_share,
        "martingale_ratio": ratio, "martingale_additions": additions,
        "martingale_signal": additions >= martingale_min_additions and ratio > martingale_max_ratio,
    }
