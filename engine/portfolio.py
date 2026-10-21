"""Small event-driven, long-only portfolio reference engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import numpy as np
import pandas as pd

SignalFunction = Callable[[pd.DataFrame, str], pd.DataFrame]


@dataclass
class Order:
    symbol: str
    kind: str
    execute_date: pd.Timestamp
    signal_date: pd.Timestamp
    signal_atr: float


@dataclass
class Position:
    symbol: str
    entry_date: pd.Timestamp
    entry_price: float
    quantity: float
    stop: float
    initial_stop: float
    initial_risk: float
    entry_cost: float


@dataclass
class Trade:
    symbol: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    quantity: float
    initial_stop: float
    initial_risk: float
    entry_cost: float
    exit_cost: float
    net_pnl: float
    r_multiple: float
    exit_reason: str


@dataclass
class BacktestResult:
    initial_capital: float
    equity: pd.Series
    exposure: pd.Series
    trades: pd.DataFrame
    max_open_positions: int


def _as_utc(value: pd.Timestamp | str) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    return timestamp.tz_localize("UTC") if timestamp.tz is None else timestamp.tz_convert("UTC")


def _validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is None:
        raise ValueError("market data requires a timezone-aware DatetimeIndex")
    clean = frame.sort_index().copy()
    clean.index = clean.index.tz_convert("UTC")
    if clean.index.has_duplicates:
        raise ValueError("market data contains duplicate timestamps")
    return clean


def _next_execution_date(
    index: pd.DatetimeIndex,
    signal_date: pd.Timestamp,
    extra_delay_bars: int,
) -> pd.Timestamp | None:
    location = index.get_indexer([signal_date])[0]
    target = location + 1 + extra_delay_bars
    return index[target] if location >= 0 and target < len(index) else None


def _mark_price(
    symbol: str,
    date: pd.Timestamp,
    data: dict[str, pd.DataFrame],
    last_close: dict[str, float],
    field: str,
) -> float:
    frame = data[symbol]
    if date in frame.index:
        return float(frame.at[date, field])
    return last_close.get(symbol, float("nan"))


def run_portfolio(
    data: dict[str, pd.DataFrame],
    signal_function: SignalFunction,
    *,
    market: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
    cost_rate: float,
    extra_delay_bars: int = 0,
    initial_capital: float = 10_000.0,
    risk_per_trade: float = 0.005,
    max_total_risk: float = 0.02,
    max_gross: float = 1.0,
    atr_stop_multiple: float = 3.0,
    precomputed_signals: dict[str, pd.DataFrame] | None = None,
) -> BacktestResult:
    """Run shared-capital portfolio events without same-bar signal fills."""

    if extra_delay_bars < 0:
        raise ValueError("extra_delay_bars must be non-negative")
    start = _as_utc(start)
    end = _as_utc(end)
    clean_data = {symbol: _validate_frame(frame) for symbol, frame in data.items()}
    signals = (
        {
            symbol: signal_function(frame, market).reindex(frame.index)
            for symbol, frame in clean_data.items()
        }
        if precomputed_signals is None
        else {
            symbol: precomputed_signals[symbol].reindex(frame.index)
            for symbol, frame in clean_data.items()
        }
    )
    dates = sorted(
        {
            date
            for frame in clean_data.values()
            for date in frame.index
            if start <= date <= end
        }
    )
    if not dates:
        raise ValueError("no bars in requested backtest period")

    cash = initial_capital
    positions: dict[str, Position] = {}
    scheduled: dict[pd.Timestamp, list[Order]] = {}
    pending: dict[str, str] = {}
    trades: list[Trade] = []
    equity_points: dict[pd.Timestamp, float] = {}
    exposure_points: dict[pd.Timestamp, float] = {}
    last_close: dict[str, float] = {}
    max_open_positions = 0

    def equity_at(date: pd.Timestamp, field: str) -> float:
        marked = cash
        for symbol, position in positions.items():
            price = _mark_price(symbol, date, clean_data, last_close, field)
            if np.isfinite(price):
                marked += position.quantity * price
        return marked

    def close_position(symbol: str, date: pd.Timestamp, price: float, reason: str) -> None:
        nonlocal cash
        position = positions.pop(symbol)
        exit_cost = position.quantity * price * cost_rate
        cash += position.quantity * price - exit_cost
        net_pnl = (price - position.entry_price) * position.quantity - position.entry_cost - exit_cost
        trades.append(
            Trade(
                symbol=symbol,
                entry_date=position.entry_date,
                exit_date=date,
                entry_price=position.entry_price,
                exit_price=price,
                quantity=position.quantity,
                initial_stop=position.initial_stop,
                initial_risk=position.initial_risk,
                entry_cost=position.entry_cost,
                exit_cost=exit_cost,
                net_pnl=net_pnl,
                r_multiple=net_pnl / position.initial_risk if position.initial_risk else np.nan,
                exit_reason=reason,
            )
        )
        pending.pop(symbol, None)

    for date in dates:
        for symbol, frame in clean_data.items():
            if date in frame.index:
                last_close[symbol] = float(frame.at[date, "close"])

        todays_orders = sorted(scheduled.pop(date, []), key=lambda order: (order.kind != "exit", order.symbol))
        for order in todays_orders:
            if pending.get(order.symbol) != order.kind:
                continue
            frame = clean_data[order.symbol]
            if date not in frame.index:
                continue
            open_price = float(frame.at[date, "open"])
            if order.kind == "exit":
                pending.pop(order.symbol, None)
                if order.symbol in positions:
                    close_position(order.symbol, date, open_price, "signal")
                continue
            pending.pop(order.symbol, None)
            if order.symbol in positions or not np.isfinite(order.signal_atr) or order.signal_atr <= 0:
                continue
            portfolio_equity = equity_at(date, "open")
            initial_stop = open_price - atr_stop_multiple * order.signal_atr
            risk_per_unit = open_price - initial_stop
            existing_risk = sum(
                max(
                    _mark_price(symbol, date, clean_data, last_close, "open") - position.stop,
                    0.0,
                )
                * position.quantity
                for symbol, position in positions.items()
            )
            gross = sum(
                position.quantity * _mark_price(symbol, date, clean_data, last_close, "open")
                for symbol, position in positions.items()
            )
            risk_budget = min(
                risk_per_trade * portfolio_equity,
                max(max_total_risk * portfolio_equity - existing_risk, 0.0),
            )
            gross_budget = max(max_gross * portfolio_equity - gross, 0.0)
            cash_budget = max(cash / (1 + cost_rate), 0.0)
            quantity = min(risk_budget / risk_per_unit, gross_budget / open_price, cash_budget / open_price)
            if quantity <= 0 or not np.isfinite(quantity):
                continue
            entry_cost = quantity * open_price * cost_rate
            cash -= quantity * open_price + entry_cost
            initial_risk = quantity * risk_per_unit
            positions[order.symbol] = Position(
                symbol=order.symbol,
                entry_date=date,
                entry_price=open_price,
                quantity=quantity,
                stop=initial_stop,
                initial_stop=initial_stop,
                initial_risk=initial_risk,
                entry_cost=entry_cost,
            )
            max_open_positions = max(max_open_positions, len(positions))

        # Stops are active during the bar, including a position entered at its open.
        for symbol in sorted(list(positions)):
            frame = clean_data[symbol]
            if date not in frame.index:
                continue
            position = positions[symbol]
            open_price = float(frame.at[date, "open"])
            low_price = float(frame.at[date, "low"])
            if open_price <= position.stop:
                close_position(symbol, date, open_price, "gap_stop")
            elif low_price <= position.stop:
                close_position(symbol, date, position.stop, "stop")

        # A trailing stop calculated from today's close becomes active tomorrow.
        for symbol, position in positions.items():
            frame = clean_data[symbol]
            if date not in frame.index:
                continue
            signal_row = signals[symbol].loc[date]
            current_atr = float(signal_row["atr"])
            if np.isfinite(current_atr):
                # VARSAYIM: PDF's ATR14x3 trailing stop uses close - ATR14x3.
                position.stop = max(
                    position.stop,
                    float(frame.at[date, "close"]) - atr_stop_multiple * current_atr,
                )

        # Closed-bar signals schedule orders for a later open; never this bar.
        for symbol in sorted(clean_data):
            frame = clean_data[symbol]
            if date not in frame.index:
                continue
            signal_row = signals[symbol].loc[date]
            if symbol in positions and bool(signal_row["exit"]) and symbol not in pending:
                execute_date = _next_execution_date(frame.index, date, extra_delay_bars)
                if execute_date is not None and execute_date <= end:
                    order = Order(symbol, "exit", execute_date, date, float(signal_row["atr"]))
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "exit"
            elif symbol not in positions and bool(signal_row["entry"]) and symbol not in pending:
                execute_date = _next_execution_date(frame.index, date, extra_delay_bars)
                if execute_date is not None and execute_date <= end:
                    order = Order(symbol, "entry", execute_date, date, float(signal_row["atr"]))
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "entry"

        marked_equity = equity_at(date, "close")
        gross_close = sum(
            position.quantity * _mark_price(symbol, date, clean_data, last_close, "close")
            for symbol, position in positions.items()
        )
        equity_points[date] = marked_equity
        exposure_points[date] = gross_close / marked_equity if marked_equity > 0 else np.nan

    final_date = dates[-1]
    for symbol in sorted(list(positions)):
        frame = clean_data[symbol]
        available = frame.loc[frame.index <= final_date]
        if available.empty:
            continue
        exit_date = available.index[-1]
        close_position(symbol, exit_date, float(available.iloc[-1]["close"]), "end_of_test")
    equity_points[final_date] = cash
    exposure_points[final_date] = 0.0

    trade_frame = pd.DataFrame([asdict(trade) for trade in trades])
    equity = pd.Series(equity_points, name="equity", dtype=float).sort_index()
    exposure = pd.Series(exposure_points, name="exposure", dtype=float).sort_index()
    return BacktestResult(initial_capital, equity, exposure, trade_frame, max_open_positions)


def calculate_metrics(
    result: BacktestResult,
    *,
    annualization: int,
    oos_start: pd.Timestamp | None = None,
) -> dict[str, float | int]:
    equity = result.equity.dropna()
    returns = equity.pct_change().dropna()
    elapsed_days = max((equity.index[-1] - equity.index[0]).days, 1)
    total_return = equity.iloc[-1] / result.initial_capital - 1
    cagr = (equity.iloc[-1] / result.initial_capital) ** (365.25 / elapsed_days) - 1
    sharpe = (
        np.sqrt(annualization) * returns.mean() / returns.std(ddof=1)
        if len(returns) > 1 and returns.std(ddof=1) > 0
        else np.nan
    )
    drawdown = equity / equity.cummax() - 1
    trades = result.trades
    if trades.empty:
        profit_factor = np.nan
        average_r = np.nan
        best_excluded = total_return
    else:
        wins = trades.loc[trades["net_pnl"] > 0, "net_pnl"].sum()
        losses = -trades.loc[trades["net_pnl"] < 0, "net_pnl"].sum()
        profit_factor = wins / losses if losses > 0 else np.inf
        average_r = trades["r_multiple"].mean()
        best_excluded = (
            (equity.iloc[-1] - trades["net_pnl"].max()) / result.initial_capital - 1
        )
    oos_return = np.nan
    oos_sharpe = np.nan
    if oos_start is not None:
        oos_start = _as_utc(oos_start)
        oos = equity.loc[equity.index >= oos_start]
        if len(oos) > 1:
            oos_return = oos.iloc[-1] / oos.iloc[0] - 1
            oos_returns = oos.pct_change().dropna()
            if oos_returns.std(ddof=1) > 0:
                oos_sharpe = np.sqrt(annualization) * oos_returns.mean() / oos_returns.std(ddof=1)
    return {
        "getiri": total_return,
        "cagr": cagr,
        "pf": profit_factor,
        "sharpe": sharpe,
        "mdd": drawdown.min(),
        "islem": len(trades),
        "ortalama_r": average_r,
        "maruziyet": result.exposure.mean(),
        "azami_acik_pozisyon": result.max_open_positions,
        "en_iyi_islem_haric_getiri": best_excluded,
        "oos_getiri": oos_return,
        "oos_sharpe": oos_sharpe,
    }
