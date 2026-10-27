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


COMMODITIES = {"CL", "BRENTOIL", "OIL", "GOLD", "SILVER", "XAU", "XAG", "NATGAS", "NG", "COPPER", "HG", "PLATINUM"}
INDICES = {"XYZ100", "SPX", "US500", "NDX", "NAS100", "US30", "DJI", "RUT", "SP500", "USA500", "USTECH"}


def asset_class(coin: str) -> str:
    """Hyperliquid coin -> kripto / hisse / endeks / emtia / spot. HIP-3 markets carry a ``dex:`` prefix."""
    coin = str(coin)
    if coin.startswith("@") or "/" in coin:
        return "spot"
    if ":" not in coin:
        return "kripto"
    name = coin.split(":", 1)[1].upper()
    return "emtia" if name in COMMODITIES else "endeks" if name in INDICES else "hisse"


def perp_fills(fills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Spot fills have no position/closedPnl semantics; metrics use perpetual fills only."""
    return [f for f in fills if asset_class(f.get("coin", "")) != "spot"]


def closed_round_trips(fills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify a transaction when signed position returns to zero (or flips sign).

    PnL accumulates over every partial close of the transaction, not only the last fill. A position already open
    when the window starts has unknown opening time: its PnL counts, its holding time is ``None``.
    """
    data = _frame(fills)
    open_time: dict[str, pd.Timestamp | None] = {}
    pnl: defaultdict[str, float] = defaultdict(float)
    position: defaultdict[str, float] = defaultdict(float)
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for row in data.to_dict("records"):
        coin = str(row.get("coin", ""))
        before = float(row.get("startPosition", position[coin]))
        side = str(row.get("side", ""))
        signed = float(row.get("sz", 0.0)) * (-1 if side in {"A", "Sell", "sell"} else 1)
        after = before + signed
        if coin not in seen:
            seen.add(coin)
            if abs(before) > 1e-12:
                open_time[coin] = None  # opened before the window
        pnl[coin] += float(row.get("closedPnl", 0)) - float(row.get("fee", 0))
        closes = abs(before) > 1e-12 and (abs(after) < 1e-12 or before * after < 0)
        if closes:
            start = open_time.pop(coin, None)
            rows.append({"coin": coin, "open_time": start, "close_time": row["time"],
                         "holding_hours": (row["time"] - start).total_seconds() / 3600 if start is not None else None,
                         "net_pnl": pnl.pop(coin, 0.0)})
        if abs(after) > 1e-12 and (abs(before) < 1e-12 or before * after < 0):
            open_time[coin] = row["time"]
        position[coin] = after
    return rows


def _orders(data: pd.DataFrame) -> list[dict[str, Any]]:
    """Fill'leri emir (``oid``) düzeyinde birleştirir: tek emrin parçalı dolumları tek ekleme sayılır."""
    if "oid" not in data:
        return data.to_dict("records")
    rows = []
    for _, group in data.groupby("oid", sort=False):
        first = group.iloc[0].to_dict()
        size = float(group["sz"].sum())
        first["px"] = float((group["px"] * group["sz"]).sum() / size) if size else float(group["px"].iloc[0])
        first["sz"] = size
        rows.append(first)
    return sorted(rows, key=lambda r: r["time"])


def martingale_ratio(fills: list[dict[str, Any]], min_adverse: float = 0.02) -> tuple[float, int]:
    """Share of same-direction additions made while the open position is under water by more than ``min_adverse``.

    Measured per order (``oid``), so a laddered entry is not many additions. An addition never closes PnL, so
    ``closedPnl`` cannot show it; the running average entry per coin is rebuilt from the orders instead.
    Returns (ratio, number of additions).
    """
    data = _frame(fills)
    if data.empty:
        return 0.0, 0
    position: defaultdict[str, float] = defaultdict(float)
    entry: dict[str, float] = {}
    additions = losing = 0
    for row in _orders(data):
        coin = str(row.get("coin", ""))
        before = float(row.get("startPosition", position[coin]))
        signed = float(row.get("sz", 0)) * (-1 if str(row.get("side", "")) in {"A", "Sell", "sell"} else 1)
        px = float(row.get("px", 0))
        after = before + signed
        if abs(before) > 1e-12 and before * signed > 0:
            if coin in entry:  # opening fill seen: we know the average entry
                additions += 1
                if (px / entry[coin] - 1) * (1 if before > 0 else -1) < -min_adverse:
                    losing += 1
                entry[coin] = (entry[coin] * abs(before) + px * abs(signed)) / abs(after)
        elif abs(before) < 1e-12 or before * after < 0:
            entry[coin] = px  # new position (or flip): fresh average
        if abs(after) < 1e-12:
            entry.pop(coin, None)
        position[coin] = after
    return (losing / additions if additions else 0.0), additions


def effective_leverage(fills: list[dict[str, Any]], account_value: float) -> tuple[float | None, float | None]:
    """(medyan, en yüksek) gerçek kaldıraç: dolumlardan kurulan toplam pozisyon değeri / hesap değeri.

    Hesap ayarındaki kaldıraç (ör. 20x) değil; açık pozisyonların nominal büyüklüğü. Her dolumdan sonra örneklenir.
    """
    data = _frame(fills)
    if data.empty or not account_value or account_value <= 0:
        return None, None
    position: defaultdict[str, float] = defaultdict(float)
    price: dict[str, float] = {}
    samples = []
    for row in data.to_dict("records"):
        coin = str(row.get("coin", ""))
        before = float(row.get("startPosition", position[coin]))
        signed = float(row.get("sz", 0)) * (-1 if str(row.get("side", "")) in {"A", "Sell", "sell"} else 1)
        position[coin], price[coin] = before + signed, float(row.get("px", 0))
        samples.append(sum(abs(q) * price.get(c, 0) for c, q in position.items()) / account_value)
    series = pd.Series(samples)
    active = series[series > 0]
    return (float(active.median()) if len(active) else 0.0), float(series.max())


def calculate_metrics(fills: list[dict[str, Any]], funding: list[dict[str, Any]] | None = None,
                      portfolio: list[dict[str, Any]] | None = None, liquid_coins: set[str] | None = None,
                      leverages: list[float] | None = None, account_value: float | None = None,
                      martingale_max_ratio: float = 0.25, martingale_min_additions: int = 5,
                      martingale_min_adverse: float = 0.02) -> dict[str, Any]:
    """``account_value`` is the return denominator when no ``portfolio`` history is given (never 1 USD)."""
    fills = perp_fills(fills)
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
    ratio, additions = martingale_ratio(fills, martingale_min_adverse)
    lev_median, lev_max = effective_leverage(fills, denominator)
    return {
        "history_days": int((data.time.iloc[-1] - data.time.iloc[0]).total_seconds() // 86400),
        "closed_trades": len(rounds), "profitable_month_ratio": float((daily.resample("MS").sum() > 0).mean()),
        "sortino": sortino, "calmar": (cagr / mdd if cagr is not None and mdd else None),
        "ulcer_index": float(math.sqrt((drawdown.pow(2)).mean())),
        "largest_trade_share": (max(wins) / sum(wins) if sum(wins) else None),
        "profit_factor_without_best": (sum(x for x in without_best if x > 0) / gross_loss if gross_loss else None),
        "median_holding_hours": (float(pd.Series(held).median()) if (held := [x["holding_hours"] for x in rounds
                                  if x["holding_hours"] is not None]) else None),
        "median_leverage": lev_median, "max_leverage": lev_max,
        "setting_leverage": max(leverages) if leverages else None, "liquid_coin_share": liquid_share,
        "martingale_ratio": ratio, "martingale_additions": additions,
        "martingale_signal": additions >= martingale_min_additions and ratio > martingale_max_ratio,
    }
