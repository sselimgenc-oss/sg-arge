"""Approximate daily paper-copy ledger.  It cannot place an order."""
from __future__ import annotations

import pandas as pd

from copytrade.olcut import _funding_amount


def simulate(fills: list[dict], account_value: float, nominal: float = 1000.0, slippage: float = 0.0005,
             taker_fee: float = 0.00045, funding: list[dict] | None = None) -> pd.DataFrame:
    """Scale leader realized PnL and charge our own friction (slippage + taker) on fill notional.

    The leader's own fee is not deducted: the copier pays its own taker fee instead (no double fee).
    """
    records = []
    scale = nominal / account_value if account_value > 0 else 0.0
    for fill in fills:
        time = pd.to_datetime(fill.get("time"), unit="ms", utc=True)
        notional = abs(float(fill.get("px", 0)) * float(fill.get("sz", 0))) * scale
        realized = float(fill.get("closedPnl", 0)) * scale
        records.append((time, realized - notional * (slippage + taker_fee)))
    for item in funding or []:
        records.append((pd.to_datetime(item.get("time"), unit="ms", utc=True), _funding_amount(item) * scale))
    if not records:
        return pd.DataFrame(columns=["date", "equity", "net_pnl"])
    series = pd.DataFrame(records, columns=["time", "net_pnl"]).set_index("time")["net_pnl"].resample("1D").sum()
    return pd.DataFrame({"date": series.index.date.astype(str), "net_pnl": series.values,
                         "equity": nominal + series.cumsum().values})
