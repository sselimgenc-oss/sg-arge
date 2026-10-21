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
    stop_dist: float = float("nan")
    target_dist: float = float("nan")
    stop_pct: float = float("nan")
    target_pct: float = float("nan")


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
    target: float = float("nan")
    signal_atr: float = float("nan")
    bars_held: int = 0
    locked: bool = False
    runtime_exit: pd.Series | None = None


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
    trail_mode: str | None = "close",
    trail_multiple: float | None = None,
    fill_at_close: bool = False,
    time_stop_bars: int | None = None,
    cooldown_bars: int = 0,
    profit_lock: dict | None = None,
    exit_builder: Callable[..., pd.Series | None] | None = None,
) -> BacktestResult:
    """Run shared-capital portfolio events without same-bar signal fills.

    Defaults reproduce the T1a reference behaviour exactly. Optional card-driven
    extras (docs/EVRENSEL_KURALLAR.md D5):

    * signal columns ``stop_dist`` / ``target_dist`` / ``trail_atr`` (price units at
      the signal bar) and ``stop_pct`` / ``target_pct`` (fraction of the fill price); a
      missing stop column falls back to ``atr_stop_multiple * atr``;
    * ``trail_mode``: ``"close"`` ratchets ``close - m*ATR``, ``"high"`` ratchets
      ``high - m*ATR``, ``None`` keeps the initial stop;
    * ``fill_at_close``: signal-bar close fills (MOC); costs are the caller's job;
    * ``time_stop_bars``, ``cooldown_bars``, ``profit_lock`` (``trigger_atr`` and a
      ``stop_fn(entry_price)`` returning the locked stop), ``exit_builder`` (position
      state dependent exit series, called as ``(symbol, entry_date, entry_price,
      initial_stop, target)``).
    """

    if extra_delay_bars < 0:
        raise ValueError("extra_delay_bars must be non-negative")
    if trail_mode not in ("close", "high", None):
        raise ValueError("trail_mode must be 'close', 'high' or None")
    trail_m = atr_stop_multiple if trail_multiple is None else trail_multiple
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
    last_exit_loc: dict[str, int] = {}

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
        if symbol in clean_data and date in clean_data[symbol].index:
            last_exit_loc[symbol] = int(clean_data[symbol].index.get_loc(date))

    def open_position(symbol: str, date: pd.Timestamp, price: float, signal_atr: float,
                      stop_dist: float, target_dist: float,
                      stop_pct: float = float("nan"), target_pct: float = float("nan")) -> None:
        nonlocal cash, max_open_positions
        if symbol in positions or not np.isfinite(signal_atr) or signal_atr <= 0:
            return
        if np.isfinite(stop_pct):
            stop_dist = price * stop_pct
        if np.isfinite(target_pct):
            target_dist = price * target_pct
        if not np.isfinite(stop_dist) or stop_dist <= 0:
            return
        portfolio_equity = equity_at(date, "close" if fill_at_close else "open")
        field = "close" if fill_at_close else "open"
        initial_stop = price - stop_dist
        risk_per_unit = price - initial_stop
        existing_risk = sum(
            max(_mark_price(held, date, clean_data, last_close, field) - position.stop, 0.0)
            * position.quantity
            for held, position in positions.items()
        )
        gross = sum(
            position.quantity * _mark_price(held, date, clean_data, last_close, field)
            for held, position in positions.items()
        )
        risk_budget = min(
            risk_per_trade * portfolio_equity,
            max(max_total_risk * portfolio_equity - existing_risk, 0.0),
        )
        gross_budget = max(max_gross * portfolio_equity - gross, 0.0)
        cash_budget = max(cash / (1 + cost_rate), 0.0)
        quantity = min(risk_budget / risk_per_unit, gross_budget / price, cash_budget / price)
        if quantity <= 0 or not np.isfinite(quantity):
            return
        entry_cost = quantity * price * cost_rate
        cash -= quantity * price + entry_cost
        initial_risk = quantity * risk_per_unit
        target = price + target_dist if np.isfinite(target_dist) and target_dist > 0 else float("nan")
        runtime_exit = (
            exit_builder(symbol, date, price, initial_stop, target) if exit_builder is not None else None
        )
        positions[symbol] = Position(
            symbol=symbol, entry_date=date, entry_price=price, quantity=quantity,
            stop=initial_stop, initial_stop=initial_stop, initial_risk=initial_risk,
            entry_cost=entry_cost, target=target, signal_atr=signal_atr,
            runtime_exit=runtime_exit,
        )
        max_open_positions = max(max_open_positions, len(positions))

    def signal_value(symbol: str, date: pd.Timestamp, column: str, default: float) -> float:
        row = signals[symbol].loc[date]
        return float(row[column]) if column in row.index else default

    def cooled_down(symbol: str, date: pd.Timestamp) -> bool:
        if cooldown_bars <= 0 or symbol not in last_exit_loc:
            return True
        return int(clean_data[symbol].index.get_loc(date)) - last_exit_loc[symbol] > cooldown_bars

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
            open_position(order.symbol, date, open_price, order.signal_atr, order.stop_dist,
                          order.target_dist, order.stop_pct, order.target_pct)

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
            elif np.isfinite(position.target) and open_price >= position.target:
                close_position(symbol, date, open_price, "gap_target")
            elif np.isfinite(position.target) and float(frame.at[date, "high"]) >= position.target:
                close_position(symbol, date, position.target, "target")

        # A trailing stop calculated from today's close becomes active tomorrow.
        for symbol, position in positions.items():
            frame = clean_data[symbol]
            if date not in frame.index:
                continue
            position.bars_held += 1
            signal_row = signals[symbol].loc[date]
            if profit_lock is not None and not position.locked and (
                float(frame.at[date, "high"])
                >= position.entry_price + profit_lock["trigger_atr"] * position.signal_atr
            ):
                position.locked = True
                position.stop = max(position.stop, float(profit_lock["stop_fn"](position.entry_price)))
            if trail_mode is None:
                continue
            current_atr = float(signal_row["trail_atr"]) if "trail_atr" in signal_row.index else float(signal_row["atr"])
            if np.isfinite(current_atr):
                # VARSAYIM: PDF's ATR14x3 trailing stop uses close - ATR14x3.
                reference = float(frame.at[date, "close" if trail_mode == "close" else "high"])
                position.stop = max(position.stop, reference - trail_m * current_atr)

        # Closed-bar signals schedule orders for a later open; never this bar.
        # With fill_at_close the order fills at this bar's close (exits first).
        close_fills: list[tuple[str, str, float, float, float, float, float]] = []
        for symbol in sorted(clean_data):
            frame = clean_data[symbol]
            if date not in frame.index:
                continue
            signal_row = signals[symbol].loc[date]
            position = positions.get(symbol)
            exit_signal = bool(signal_row["exit"])
            if position is not None:
                if position.runtime_exit is not None and bool(position.runtime_exit.get(date, False)):
                    exit_signal = True
                if time_stop_bars is not None and position.bars_held >= time_stop_bars:
                    exit_signal = True
            if fill_at_close:
                if position is not None and exit_signal:
                    close_position(symbol, date, float(frame.at[date, "close"]), "signal")
                elif position is None and bool(signal_row["entry"]) and cooled_down(symbol, date):
                    atr_value = float(signal_row["atr"])
                    close_fills.append((
                        symbol, "entry", atr_value,
                        signal_value(symbol, date, "stop_dist", atr_stop_multiple * atr_value),
                        signal_value(symbol, date, "target_dist", float("nan")),
                        signal_value(symbol, date, "stop_pct", float("nan")),
                        signal_value(symbol, date, "target_pct", float("nan")),
                    ))
                continue
            if symbol in positions and exit_signal and symbol not in pending:
                execute_date = _next_execution_date(frame.index, date, extra_delay_bars)
                if execute_date is not None and execute_date <= end:
                    order = Order(symbol, "exit", execute_date, date, float(signal_row["atr"]))
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "exit"
            elif symbol not in positions and bool(signal_row["entry"]) and symbol not in pending and cooled_down(symbol, date):
                execute_date = _next_execution_date(frame.index, date, extra_delay_bars)
                if execute_date is not None and execute_date <= end:
                    atr_value = float(signal_row["atr"])
                    order = Order(
                        symbol, "entry", execute_date, date, atr_value,
                        signal_value(symbol, date, "stop_dist", atr_stop_multiple * atr_value),
                        signal_value(symbol, date, "target_dist", float("nan")),
                        signal_value(symbol, date, "stop_pct", float("nan")),
                        signal_value(symbol, date, "target_pct", float("nan")),
                    )
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "entry"
        for symbol, _kind, atr_value, stop_dist, target_dist, stop_pct, target_pct in close_fills:
            open_position(symbol, date, float(clean_data[symbol].at[date, "close"]), atr_value,
                          stop_dist, target_dist, stop_pct, target_pct)

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
