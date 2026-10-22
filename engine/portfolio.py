"""Small event-driven, long-only portfolio reference engine."""

from __future__ import annotations

import bisect
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
    runtime_exit: np.ndarray | None = None
    orig_quantity: float = float("nan")
    partial_done: bool = False
    realized: float = 0.0
    exit_cost_acc: float = 0.0
    entry_cost_sold: float = 0.0


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
    partial_profit: dict | None = None,
    roi_table: dict[float, float] | None = None,
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
      initial_stop, target)``);
    * ``roi_table``: Freqtrade ``minimal_roi`` ({minutes held: profit ratio}); from the bar
      whose open time is at least that many minutes after the entry bar's open time, the
      position exits once the bar reaches ``entry * (1 + ratio)`` (fills at the open on a
      gap, else at that price). The stop is checked first (A3);
    * ``partial_profit``: ``gun`` (bars held), ``oran`` (fraction sold), ``trigger_atr`` or
      ``trigger_fn(entry_price, stop_distance)`` (price gain needed at the close) and
      ``stop_fn(entry_price)`` (stop for the remainder). Taken once; the fraction fills at
      the next open (or the same close with ``fill_at_close``). The trade stays one row,
      its ``exit_reason`` ends with ``+partial``.
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
    symbols = sorted(clean_data)
    all_dates = pd.DatetimeIndex([])
    for frame in clean_data.values():
        all_dates = all_dates.union(frame.index)
    window = all_dates[(all_dates >= start) & (all_dates <= end)]
    dates = list(window)
    if not dates:
        raise ValueError("no bars in requested backtest period")

    # Array views: the event loop below runs on numpy positions, not pandas lookups.
    index_of = {symbol: clean_data[symbol].index for symbol in symbols}
    locs = {symbol: index_of[symbol].get_indexer(window) for symbol in symbols}
    price_arr = {
        symbol: {field: clean_data[symbol][field].to_numpy(dtype=float) for field in ("open", "high", "low", "close")}
        for symbol in symbols
    }
    nan_col = {symbol: np.full(len(index_of[symbol]), np.nan) for symbol in symbols}
    # last bar at or before each date (a symbol without a bar that date is marked at its last close)
    prev_loc = {symbol: index_of[symbol].searchsorted(window, side="right") - 1 for symbol in symbols}

    def column(symbol: str, name: str) -> np.ndarray:
        frame = signals[symbol]
        return frame[name].to_numpy(dtype=float) if name in frame.columns else nan_col[symbol]

    sig_entry = {symbol: signals[symbol]["entry"].to_numpy().astype(bool) for symbol in symbols}
    sig_exit = {symbol: signals[symbol]["exit"].to_numpy().astype(bool) for symbol in symbols}
    sig_atr = {symbol: column(symbol, "atr") for symbol in symbols}
    sig_trail = {
        symbol: column(symbol, "trail_atr") if "trail_atr" in signals[symbol].columns else sig_atr[symbol]
        for symbol in symbols
    }
    sig_stop_dist = {symbol: column(symbol, "stop_dist") for symbol in symbols}
    sig_target_dist = {symbol: column(symbol, "target_dist") for symbol in symbols}
    sig_stop_pct = {symbol: column(symbol, "stop_pct") for symbol in symbols}
    sig_target_pct = {symbol: column(symbol, "target_pct") for symbol in symbols}
    has_stop_dist = {symbol: "stop_dist" in signals[symbol].columns for symbol in symbols}

    # Entry signals per date: only symbols holding a position or flagging an entry need a signal-step visit.
    entry_matrix = np.zeros((len(window), len(symbols)), dtype=bool)
    for column_number, symbol in enumerate(symbols):
        valid = locs[symbol] >= 0
        entry_matrix[valid, column_number] = sig_entry[symbol][locs[symbol][valid]]
    entry_rows, entry_cols = np.nonzero(entry_matrix)
    entry_starts = np.searchsorted(entry_rows, np.arange(len(window) + 1))

    cash = initial_capital
    positions: dict[str, Position] = {}
    scheduled: dict[pd.Timestamp, list[Order]] = {}
    pending: dict[str, str] = {}
    trades: list[Trade] = []
    equity_points: dict[pd.Timestamp, float] = {}
    exposure_points: dict[pd.Timestamp, float] = {}
    max_open_positions = 0
    last_exit_loc: dict[str, int] = {}
    di = 0  # index of the current date in ``dates``
    roi_keys = sorted(roi_table) if roi_table else []
    roi_values = [roi_table[key] for key in roi_keys]

    def mark(symbol: str, field: str) -> float:
        loc = locs[symbol][di]
        if loc >= 0:
            return float(price_arr[symbol][field][loc])
        previous = prev_loc[symbol][di]
        return float(price_arr[symbol]["close"][previous]) if previous >= 0 else float("nan")

    def equity_at(field: str) -> float:
        marked = cash
        for symbol, position in positions.items():
            price = mark(symbol, field)
            if np.isfinite(price):
                marked += position.quantity * price
        return marked

    def close_position(symbol: str, date: pd.Timestamp, price: float, reason: str) -> None:
        nonlocal cash
        position = positions.pop(symbol)
        exit_cost = position.quantity * price * cost_rate
        cash += position.quantity * price - exit_cost
        net_pnl = (price - position.entry_price) * position.quantity - position.entry_cost - exit_cost
        if position.partial_done:
            net_pnl += position.realized
        trades.append(
            Trade(
                symbol=symbol,
                entry_date=position.entry_date,
                exit_date=date,
                entry_price=position.entry_price,
                exit_price=price,
                quantity=position.orig_quantity,
                initial_stop=position.initial_stop,
                initial_risk=position.initial_risk,
                entry_cost=position.entry_cost + (position.entry_cost_sold if position.partial_done else 0.0),
                exit_cost=exit_cost + position.exit_cost_acc,
                net_pnl=net_pnl,
                r_multiple=net_pnl / position.initial_risk if position.initial_risk else np.nan,
                exit_reason=reason + ("+partial" if position.partial_done else ""),
            )
        )
        pending.pop(symbol, None)
        if locs[symbol][di] >= 0:
            last_exit_loc[symbol] = int(locs[symbol][di])

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
        field = "close" if fill_at_close else "open"
        portfolio_equity = equity_at(field)
        initial_stop = price - stop_dist
        risk_per_unit = price - initial_stop
        existing_risk = sum(
            max(mark(held, field) - position.stop, 0.0) * position.quantity
            for held, position in positions.items()
        )
        gross = sum(position.quantity * mark(held, field) for held, position in positions.items())
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
        runtime_exit = None
        if exit_builder is not None:
            built = exit_builder(symbol, date, price, initial_stop, target)
            if built is not None:
                runtime_exit = built.reindex(index_of[symbol]).fillna(False).to_numpy().astype(bool)
        positions[symbol] = Position(
            symbol=symbol, entry_date=date, entry_price=price, quantity=quantity,
            stop=initial_stop, initial_stop=initial_stop, initial_risk=initial_risk,
            entry_cost=entry_cost, target=target, signal_atr=signal_atr,
            runtime_exit=runtime_exit, orig_quantity=quantity,
        )
        max_open_positions = max(max_open_positions, len(positions))

    def take_partial(symbol: str, price: float) -> None:
        nonlocal cash
        position = positions[symbol]
        sold = position.quantity * float(partial_profit["oran"])
        part_cost = sold * price * cost_rate
        entry_share = position.entry_cost * float(partial_profit["oran"])
        cash += sold * price - part_cost
        position.realized = (price - position.entry_price) * sold - entry_share - part_cost
        position.exit_cost_acc = part_cost
        position.entry_cost_sold = entry_share
        position.entry_cost -= entry_share
        position.quantity -= sold
        position.partial_done = True
        position.stop = max(position.stop, float(partial_profit["stop_fn"](position.entry_price)))

    def partial_due(symbol: str, loc: int) -> bool:
        position = positions[symbol]
        if partial_profit is None or position.partial_done or position.bars_held < int(partial_profit["gun"]):
            return False
        if "trigger_atr" in partial_profit:
            trigger = float(partial_profit["trigger_atr"]) * position.signal_atr
        else:
            trigger = float(partial_profit["trigger_fn"](position.entry_price, position.entry_price - position.initial_stop))
        return float(price_arr[symbol]["close"][loc]) - position.entry_price >= trigger

    def cooled_down(symbol: str) -> bool:
        if cooldown_bars <= 0 or symbol not in last_exit_loc:
            return True
        return int(locs[symbol][di]) - last_exit_loc[symbol] > cooldown_bars

    def sizing_at(symbol: str, loc: int) -> tuple[float, float, float, float, float]:
        atr_value = float(sig_atr[symbol][loc])
        stop_dist = float(sig_stop_dist[symbol][loc]) if has_stop_dist[symbol] else atr_stop_multiple * atr_value
        return (
            atr_value, stop_dist, float(sig_target_dist[symbol][loc]),
            float(sig_stop_pct[symbol][loc]), float(sig_target_pct[symbol][loc]),
        )

    for di, date in enumerate(dates):
        todays_orders = sorted(
            scheduled.pop(date, []), key=lambda order: ({"exit": 0, "partial": 1}.get(order.kind, 2), order.symbol)
        )
        for order in todays_orders:
            if pending.get(order.symbol) != order.kind:
                continue
            loc = locs[order.symbol][di]
            if loc < 0:
                continue
            open_price = float(price_arr[order.symbol]["open"][loc])
            if order.kind == "partial":
                pending.pop(order.symbol, None)
                if order.symbol in positions and not positions[order.symbol].partial_done:
                    take_partial(order.symbol, open_price)
                continue
            if order.kind == "exit":
                pending.pop(order.symbol, None)
                if order.symbol in positions:
                    close_position(order.symbol, date, open_price, "signal")
                continue
            pending.pop(order.symbol, None)
            open_position(order.symbol, date, open_price, order.signal_atr, order.stop_dist,
                          order.target_dist, order.stop_pct, order.target_pct)

        # Stops are active during the bar, including a position entered at its open.
        for symbol in sorted(positions):
            loc = locs[symbol][di]
            if loc < 0:
                continue
            position = positions[symbol]
            open_price = float(price_arr[symbol]["open"][loc])
            low_price = float(price_arr[symbol]["low"][loc])
            if open_price <= position.stop:
                close_position(symbol, date, open_price, "gap_stop")
            elif low_price <= position.stop:
                close_position(symbol, date, position.stop, "stop")
            elif np.isfinite(position.target) and open_price >= position.target:
                close_position(symbol, date, open_price, "gap_target")
            elif np.isfinite(position.target) and float(price_arr[symbol]["high"][loc]) >= position.target:
                close_position(symbol, date, position.target, "target")
            elif roi_keys:
                elapsed = (date - position.entry_date).total_seconds() / 60.0
                slot = bisect.bisect_right(roi_keys, elapsed) - 1
                if slot >= 0:
                    roi_price = position.entry_price * (1.0 + roi_values[slot])
                    if open_price >= roi_price:
                        close_position(symbol, date, open_price, "roi")
                    elif float(price_arr[symbol]["high"][loc]) >= roi_price:
                        close_position(symbol, date, roi_price, "roi")

        # A trailing stop calculated from today's close becomes active tomorrow.
        for symbol, position in positions.items():
            loc = locs[symbol][di]
            if loc < 0:
                continue
            position.bars_held += 1
            if profit_lock is not None and not position.locked and (
                float(price_arr[symbol]["high"][loc])
                >= position.entry_price + profit_lock["trigger_atr"] * position.signal_atr
            ):
                position.locked = True
                position.stop = max(position.stop, float(profit_lock["stop_fn"](position.entry_price)))
            if trail_mode is None:
                continue
            current_atr = float(sig_trail[symbol][loc])
            if np.isfinite(current_atr):
                # VARSAYIM: PDF's ATR14x3 trailing stop uses close - ATR14x3.
                reference = float(price_arr[symbol]["close" if trail_mode == "close" else "high"][loc])
                position.stop = max(position.stop, reference - trail_m * current_atr)

        # Closed-bar signals schedule orders for a later open; never this bar.
        # With fill_at_close the order fills at this bar's close (exits first).
        close_fills: list[tuple[str, float, float, float, float, float]] = []
        visit = set(positions) | {symbols[c] for c in entry_cols[entry_starts[di]:entry_starts[di + 1]]}
        for symbol in sorted(visit):
            loc = locs[symbol][di]
            if loc < 0:
                continue
            position = positions.get(symbol)
            exit_signal = bool(sig_exit[symbol][loc])
            if position is not None:
                if position.runtime_exit is not None and bool(position.runtime_exit[loc]):
                    exit_signal = True
                if time_stop_bars is not None and position.bars_held >= time_stop_bars:
                    exit_signal = True
            entry_signal = bool(sig_entry[symbol][loc])
            if fill_at_close:
                if position is not None and exit_signal:
                    close_position(symbol, date, float(price_arr[symbol]["close"][loc]), "signal")
                elif position is not None:
                    if partial_due(symbol, loc):
                        take_partial(symbol, float(price_arr[symbol]["close"][loc]))
                elif position is None and entry_signal and cooled_down(symbol):
                    close_fills.append((symbol, *sizing_at(symbol, loc)))
                continue
            if symbol in positions and not exit_signal and symbol not in pending and partial_due(symbol, loc):
                target_loc = loc + 1 + extra_delay_bars
                if target_loc < len(index_of[symbol]) and index_of[symbol][target_loc] <= end:
                    execute_date = index_of[symbol][target_loc]
                    scheduled.setdefault(execute_date, []).append(
                        Order(symbol, "partial", execute_date, date, float(sig_atr[symbol][loc]))
                    )
                    pending[symbol] = "partial"
            elif symbol in positions and exit_signal and (symbol not in pending or pending[symbol] == "partial"):
                target_loc = loc + 1 + extra_delay_bars
                if target_loc < len(index_of[symbol]) and index_of[symbol][target_loc] <= end:
                    execute_date = index_of[symbol][target_loc]
                    order = Order(symbol, "exit", execute_date, date, float(sig_atr[symbol][loc]))
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "exit"
            elif symbol not in positions and entry_signal and symbol not in pending and cooled_down(symbol):
                target_loc = loc + 1 + extra_delay_bars
                if target_loc < len(index_of[symbol]) and index_of[symbol][target_loc] <= end:
                    execute_date = index_of[symbol][target_loc]
                    atr_value, stop_dist, target_dist, stop_pct, target_pct = sizing_at(symbol, loc)
                    order = Order(symbol, "entry", execute_date, date, atr_value,
                                  stop_dist, target_dist, stop_pct, target_pct)
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "entry"
        for symbol, atr_value, stop_dist, target_dist, stop_pct, target_pct in close_fills:
            loc = locs[symbol][di]
            open_position(symbol, date, float(price_arr[symbol]["close"][loc]), atr_value,
                          stop_dist, target_dist, stop_pct, target_pct)

        marked_equity = equity_at("close")
        gross_close = sum(position.quantity * mark(symbol, "close") for symbol, position in positions.items())
        equity_points[date] = marked_equity
        exposure_points[date] = gross_close / marked_equity if marked_equity > 0 else np.nan

    final_date = dates[-1]
    for symbol in sorted(positions):
        loc = int(index_of[symbol].searchsorted(final_date, side="right")) - 1
        if loc < 0:
            continue
        close_position(symbol, index_of[symbol][loc], float(price_arr[symbol]["close"][loc]), "end_of_test")
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
