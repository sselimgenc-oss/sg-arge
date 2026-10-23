"""Small event-driven portfolio reference engine (long-only by default; short and two-way: docs D17)."""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from typing import Callable
from zoneinfo import ZoneInfo

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
    entry_level: float = float("nan")
    activate_loc: int = -1
    expires_loc: int = -1
    side: float = 1.0


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
    sig_loc: int = -1
    side: float = 1.0
    sess_key: int = -1


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
    yon: str = "long"


@dataclass
class BacktestResult:
    initial_capital: float
    equity: pd.Series
    exposure: pd.Series
    trades: pd.DataFrame
    max_open_positions: int
    # Filled only with ``record_state=True`` (paper trading, T27): every fill, the book at the end of the run
    # before the artificial ``end_of_test`` exit, the orders implied by signals of the last bar, and the last marked equity.
    fills: list = field(default_factory=list)
    open_positions: list = field(default_factory=list)
    next_orders: list = field(default_factory=list)
    marked_equity: float = float("nan")


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
    entry_order_type: str | None = None,
    entry_order_validity: int = 1,
    level_fns: dict[str, Callable[..., float]] | None = None,
    trusted_inputs: bool = False,
    trades_only: bool = False,
    runtime_cache: dict | None = None,
    record_state: bool = False,
    direction: str = "long",
    cost_abs: float = 0.0,
    session_close: tuple[str, str] | None = None,
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
    * ``level_fns``: signal-bar referenced levels (docs/EVRENSEL_KURALLAR.md D10), each called as
      ``fn(symbol, signal_loc, fill_price, ...)`` returning an absolute price. ``"stop"`` sets the initial
      stop; ``"target"`` ``(…, stop_level)`` the target; ``"lock_trigger"`` / ``"lock_stop"``
      ``(…, stop_level, target_level)`` replace ``profit_lock``'s ATR trigger and stop. An entry whose
      stop is not below, or target not above, the fill price is skipped.
    * ``entry_order_type``: ``"stop"`` or ``"limit"`` uses the signal-bar
      ``entry_level`` for up to ``entry_order_validity`` following bars.

    Short / two-way / FX-CFD extras (docs/EVRENSEL_KURALLAR.md D17); the defaults leave every long-only result unchanged:

    * ``direction``: ``"long"`` (default) reads the ``entry``/``exit`` signal columns; ``"short"`` reads
      ``entry_short``/``exit_short`` (falling back to ``entry``/``exit`` when those are absent); ``"both"`` reads
      both pairs. A symbol holds one position at a time; a bar carrying both a long and a short entry is skipped.
      A short mirrors every long rule: stop above the fill, target below it, trailing stop ratchets down from
      ``close + m*ATR`` / ``low + m*ATR``, a gap through the stop fills at the open, stop before target on the
      same bar (A3). ``roi_table``, ``partial_profit``, ``profit_lock``, ``level_fns`` and pending entry
      orders are long-only (``ValueError`` otherwise).
    * ``cost_abs``: cost per unit of quantity per side in price units (FX pips), added to ``cost_rate`` x notional.
    * ``session_close``: ``("HH:MM", "<IANA tz>")``; a position is flat-closed at the open of the first bar whose
      local clock time has passed ``HH:MM`` since its entry bar's session (a session runs from ``HH:MM`` to the next
      ``HH:MM`` in local time), reason ``seans_sonu``.
    """

    if extra_delay_bars < 0:
        raise ValueError("extra_delay_bars must be non-negative")
    if entry_order_type not in (None, "stop", "limit"):
        raise ValueError("entry_order_type must be 'stop', 'limit' or None")
    if entry_order_type is not None and entry_order_validity < 1:
        raise ValueError("entry_order_validity must be >= 1")
    if entry_order_type is not None and fill_at_close:
        raise ValueError("pending entry orders cannot use fill_at_close")
    if trail_mode not in ("close", "high", None):
        raise ValueError("trail_mode must be 'close', 'high' or None")
    trail_m = atr_stop_multiple if trail_multiple is None else trail_multiple
    if direction not in ("long", "short", "both"):
        raise ValueError("direction must be 'long', 'short' or 'both'")
    if direction != "long":
        for name, value in (("roi_table", roi_table), ("partial_profit", partial_profit), ("profit_lock", profit_lock),
                            ("level_fns", level_fns), ("entry_order_type", entry_order_type)):
            if value:
                raise ValueError(f"{name} is long-only (direction={direction!r})")
    if cost_abs < 0:
        raise ValueError("cost_abs must be non-negative")
    session_minutes = None
    session_zone = None
    if session_close is not None:
        clock, zone_name = session_close
        hour, minute = (int(part) for part in str(clock).split(":"))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError("session_close time must be HH:MM")
        session_minutes, session_zone = hour * 60 + minute, ZoneInfo(str(zone_name))
    start = _as_utc(start)
    end = _as_utc(end)
    # Repeated null draws reuse frames/signals already normalised and aligned by
    # ``tarama.prepare``. Avoid copying millions of bars on every repetition.
    clean_data = data if trusted_inputs else {symbol: _validate_frame(frame) for symbol, frame in data.items()}
    signals = (
        {
            symbol: signal_function(frame, market).reindex(frame.index)
            for symbol, frame in clean_data.items()
        }
        if precomputed_signals is None
        else (
            precomputed_signals
            if trusted_inputs
            else {
                symbol: precomputed_signals[symbol].reindex(frame.index)
                for symbol, frame in clean_data.items()
            }
        )
    )
    cached = runtime_cache.get("static") if runtime_cache is not None else None
    if cached is None:
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

        sig_exit = {symbol: signals[symbol]["exit"].to_numpy().astype(bool) for symbol in symbols}
        sig_exit_short = {
            symbol: signals[symbol]["exit_short" if "exit_short" in signals[symbol].columns else "exit"].to_numpy().astype(bool)
            for symbol in symbols
        } if direction != "long" else {}
        sess_key = {}
        if session_minutes is not None:
            for symbol in symbols:
                local = index_of[symbol].tz_convert(session_zone)
                day_number = np.asarray((local.tz_localize(None).normalize() - pd.Timestamp("1970-01-01")).days, dtype=np.int64)
                minute_of_day = local.hour.to_numpy() * 60 + local.minute.to_numpy()
                sess_key[symbol] = day_number + (minute_of_day >= session_minutes).astype(np.int64)
        sig_atr = {symbol: column(symbol, "atr") for symbol in symbols}
        sig_trail = {
            symbol: column(symbol, "trail_atr") if "trail_atr" in signals[symbol].columns else sig_atr[symbol]
            for symbol in symbols
        }
        sig_stop_dist = {symbol: column(symbol, "stop_dist") for symbol in symbols}
        sig_target_dist = {symbol: column(symbol, "target_dist") for symbol in symbols}
        sig_stop_pct = {symbol: column(symbol, "stop_pct") for symbol in symbols}
        sig_target_pct = {symbol: column(symbol, "target_pct") for symbol in symbols}
        sig_entry_level = {symbol: column(symbol, "entry_level") for symbol in symbols}
        has_stop_dist = {symbol: "stop_dist" in signals[symbol].columns for symbol in symbols}
        cached = {
            "symbols": symbols, "window": window, "dates": dates, "index_of": index_of, "locs": locs,
            "price_arr": price_arr, "prev_loc": prev_loc, "sig_exit": sig_exit, "sig_atr": sig_atr,
            "sig_trail": sig_trail, "sig_stop_dist": sig_stop_dist, "sig_target_dist": sig_target_dist,
            "sig_stop_pct": sig_stop_pct, "sig_target_pct": sig_target_pct,
            "sig_entry_level": sig_entry_level, "has_stop_dist": has_stop_dist,
            "sig_exit_short": sig_exit_short, "sess_key": sess_key,
        }
        if runtime_cache is not None:
            runtime_cache["static"] = cached
    else:
        symbols = cached["symbols"]
        window, dates = cached["window"], cached["dates"]
        index_of, locs = cached["index_of"], cached["locs"]
        price_arr, prev_loc = cached["price_arr"], cached["prev_loc"]
        sig_exit, sig_atr, sig_trail = cached["sig_exit"], cached["sig_atr"], cached["sig_trail"]
        sig_stop_dist, sig_target_dist = cached["sig_stop_dist"], cached["sig_target_dist"]
        sig_stop_pct, sig_target_pct = cached["sig_stop_pct"], cached["sig_target_pct"]
        sig_entry_level, has_stop_dist = cached["sig_entry_level"], cached["has_stop_dist"]
    sig_exit_short, sess_key = cached["sig_exit_short"], cached["sess_key"]

    sig_entry = {symbol: signals[symbol]["entry"].to_numpy().astype(bool) for symbol in symbols}
    sig_entry_short: dict[str, np.ndarray] = {}
    if direction != "long":
        for symbol in symbols:
            frame = signals[symbol]
            short_column = "entry_short" if "entry_short" in frame.columns else "entry"
            sig_entry_short[symbol] = frame[short_column].to_numpy().astype(bool)
        if direction == "short":
            sig_entry = sig_entry_short
        else:  # "both": a bar that signals both ways is ambiguous and is skipped
            both = {symbol: sig_entry[symbol] & sig_entry_short[symbol] for symbol in symbols}
            sig_entry = {symbol: sig_entry[symbol] & ~both[symbol] for symbol in symbols}
            sig_entry_short = {symbol: sig_entry_short[symbol] & ~both[symbol] for symbol in symbols}

    # Entry signals per date: only symbols holding a position or flagging an entry need a signal-step visit.
    entry_matrix = np.zeros((len(window), len(symbols)), dtype=bool)
    for column_number, symbol in enumerate(symbols):
        valid = locs[symbol] >= 0
        entry_matrix[valid, column_number] = sig_entry[symbol][locs[symbol][valid]]
        if direction == "both":
            entry_matrix[valid, column_number] |= sig_entry_short[symbol][locs[symbol][valid]]
    entry_rows, entry_cols = np.nonzero(entry_matrix)
    entry_starts = np.searchsorted(entry_rows, np.arange(len(window) + 1))

    cash = initial_capital
    positions: dict[str, Position] = {}
    scheduled: dict[pd.Timestamp, list[Order]] = {}
    pending: dict[str, str] = {}
    pending_entries: dict[str, Order] = {}
    trades: list[Trade] = []
    fill_log: list[dict] = []
    order_log: list[dict] = []
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
                marked += position.side * position.quantity * price
        return marked

    def close_position(symbol: str, date: pd.Timestamp, price: float, reason: str) -> None:
        nonlocal cash
        position = positions.pop(symbol)
        exit_cost = position.quantity * price * cost_rate
        if cost_abs:
            exit_cost += position.quantity * cost_abs
        cash += position.side * position.quantity * price - exit_cost
        net_pnl = position.side * (price - position.entry_price) * position.quantity - position.entry_cost - exit_cost
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
                yon="short" if position.side < 0 else "long",
            )
        )
        if record_state:
            fill_log.append({"tarih": date, "sembol": symbol, "tip": "cikis", "fiyat": price, "adet": position.quantity,
                             "maliyet": exit_cost, "neden": reason})
        pending.pop(symbol, None)
        if locs[symbol][di] >= 0:
            last_exit_loc[symbol] = int(locs[symbol][di])

    def size_entry(symbol: str, price: float, signal_atr: float, stop_dist: float, target_dist: float,
                   stop_pct: float, target_pct: float, sig_loc: int, side: float = 1.0):
        """Quantity and levels of an entry at ``price`` with the book as it is now (no side effects), or ``None``."""
        if symbol in positions or not np.isfinite(signal_atr) or signal_atr <= 0:
            return None
        if np.isfinite(stop_pct):
            stop_dist = price * stop_pct
        if np.isfinite(target_pct):
            target_dist = price * target_pct
        if level_fns:
            stop_level = float("nan")
            if "stop" in level_fns:
                stop_level = float(level_fns["stop"](symbol, sig_loc, price))
                stop_dist = price - stop_level
            if "target" in level_fns:
                target_level = float(level_fns["target"](symbol, sig_loc, price, stop_level))
                if not np.isfinite(target_level) or target_level <= price:
                    return None
                target_dist = target_level - price
        if not np.isfinite(stop_dist) or stop_dist <= 0:
            return None
        field_name = "close" if fill_at_close else "open"
        portfolio_equity = equity_at(field_name)
        initial_stop = price - side * stop_dist
        risk_per_unit = side * (price - initial_stop)
        existing_risk = sum(
            max(position.side * (mark(held, field_name) - position.stop), 0.0) * position.quantity
            for held, position in positions.items()
        )
        gross = sum(position.quantity * mark(held, field_name) for held, position in positions.items())
        risk_budget = min(
            risk_per_trade * portfolio_equity,
            max(max_total_risk * portfolio_equity - existing_risk, 0.0),
        )
        gross_budget = max(max_gross * portfolio_equity - gross, 0.0)
        cash_budget = max(cash / (1 + cost_rate), 0.0)
        if cost_abs:  # quantity x (price x (1 + rate) + abs cost) must fit in cash
            quantity = min(risk_budget / risk_per_unit, gross_budget / price,
                           max(cash, 0.0) / (price * (1 + cost_rate) + cost_abs) if side > 0 else float("inf"))
        elif side > 0:
            quantity = min(risk_budget / risk_per_unit, gross_budget / price, cash_budget / price)
        else:  # a short needs no cash for the position itself; gross and risk budgets bound it
            quantity = min(risk_budget / risk_per_unit, gross_budget / price)
        if quantity <= 0 or not np.isfinite(quantity):
            return None
        return quantity, initial_stop, risk_per_unit, target_dist

    def open_position(symbol: str, date: pd.Timestamp, price: float, signal_atr: float,
                      stop_dist: float, target_dist: float,
                      stop_pct: float = float("nan"), target_pct: float = float("nan"), sig_loc: int = -1,
                      side: float = 1.0) -> None:
        nonlocal cash, max_open_positions
        sized = size_entry(symbol, price, signal_atr, stop_dist, target_dist, stop_pct, target_pct, sig_loc, side)
        if sized is None:
            return
        quantity, initial_stop, risk_per_unit, target_dist = sized
        entry_cost = quantity * price * cost_rate
        if cost_abs:
            entry_cost += quantity * cost_abs
        cash -= side * quantity * price + entry_cost
        initial_risk = quantity * risk_per_unit
        target = price + side * target_dist if np.isfinite(target_dist) and target_dist > 0 else float("nan")
        runtime_exit = None
        if exit_builder is not None:
            built = exit_builder(symbol, date, price, initial_stop, target)
            if built is not None:
                runtime_exit = (  # lazy rules (kart_sinyal.LazyExit) already match the symbol's bars
                    built if hasattr(built, "entry_loc") else built.reindex(index_of[symbol]).fillna(False).to_numpy().astype(bool)
                )
        positions[symbol] = Position(
            symbol=symbol, entry_date=date, entry_price=price, quantity=quantity,
            stop=initial_stop, initial_stop=initial_stop, initial_risk=initial_risk,
            entry_cost=entry_cost, target=target, signal_atr=signal_atr,
            runtime_exit=runtime_exit, orig_quantity=quantity, sig_loc=sig_loc, side=side,
            sess_key=int(sess_key[symbol][locs[symbol][di]]) if session_minutes is not None and locs[symbol][di] >= 0 else -1,
        )
        max_open_positions = max(max_open_positions, len(positions))
        if record_state:
            fill_log.append({"tarih": date, "sembol": symbol, "tip": "giris", "fiyat": price, "adet": quantity,
                             "maliyet": entry_cost, "stop": initial_stop, "hedef": target})

    def take_partial(symbol: str, price: float) -> None:
        nonlocal cash
        position = positions[symbol]
        sold = position.quantity * float(partial_profit["oran"])
        part_cost = sold * price * cost_rate
        if cost_abs:
            part_cost += sold * cost_abs
        entry_share = position.entry_cost * float(partial_profit["oran"])
        cash += sold * price - part_cost
        position.realized = (price - position.entry_price) * sold - entry_share - part_cost
        position.exit_cost_acc = part_cost
        position.entry_cost_sold = entry_share
        position.entry_cost -= entry_share
        position.quantity -= sold
        position.partial_done = True
        position.stop = max(position.stop, float(partial_profit["stop_fn"](position.entry_price)))
        if record_state:
            fill_log.append({"tarih": dates[di], "sembol": symbol, "tip": "kismi", "fiyat": price, "adet": sold,
                             "maliyet": part_cost, "stop": position.stop})

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

    def mark_last(symbol: str) -> float:
        loc = int(index_of[symbol].searchsorted(dates[-1], side="right")) - 1
        return float(price_arr[symbol]["close"][loc]) if loc >= 0 else float("nan")

    for di, date in enumerate(dates):
        # Null repetitions consume only the trade ledger. When the portfolio is
        # idle, jump over bars without an entry/order instead of marking an
        # equity point for every one of hundreds of thousands of 5m bars.
        if (
            trades_only
            and not positions
            and not pending_entries
            and date not in scheduled
            and entry_starts[di] == entry_starts[di + 1]
        ):
            continue
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
                          order.target_dist, order.stop_pct, order.target_pct,
                          int(index_of[order.symbol].get_loc(order.signal_date)), order.side)

        # Session flat-close (D17): at the open of the first bar of a new local session every position still open
        # from an earlier session is closed at that open (a time rule known in advance, so no look-ahead).
        if session_minutes is not None:
            for symbol in sorted(positions):
                loc = locs[symbol][di]
                if loc >= 0 and int(sess_key[symbol][loc]) > positions[symbol].sess_key:
                    close_position(symbol, date, float(price_arr[symbol]["open"][loc]), "seans_sonu")

        # A pending stop/limit order becomes active only after its signal bar.
        # It fills before protective stops are evaluated, so a stop touched on
        # the entry bar wins pessimistically over a target touched that day.
        # A fill inside the bar (not at its open) happened after the open and in
        # an unknown order with the bar's high/low: on that bar only the stop
        # (low) is checked; open-gap exits and targets start on the next bar.
        intrabar_fills: set[str] = set()
        for symbol in sorted(list(pending_entries)):
            order = pending_entries[symbol]
            loc = locs[symbol][di]
            if loc < 0 or loc < order.activate_loc:
                continue
            if loc > order.expires_loc:
                pending_entries.pop(symbol, None)
                if pending.get(symbol) == "pending_entry":
                    pending.pop(symbol, None)
                continue
            open_price = float(price_arr[symbol]["open"][loc])
            high_price = float(price_arr[symbol]["high"][loc])
            low_price = float(price_arr[symbol]["low"][loc])
            triggered = (
                high_price >= order.entry_level if entry_order_type == "stop"
                else low_price <= order.entry_level
            )
            if not triggered:
                continue
            fill_price = (
                max(open_price, order.entry_level) if entry_order_type == "stop"
                else min(open_price, order.entry_level)
            )
            pending_entries.pop(symbol, None)
            pending.pop(symbol, None)
            open_position(symbol, date, fill_price, order.signal_atr, order.stop_dist,
                          order.target_dist, order.stop_pct, order.target_pct,
                          int(index_of[symbol].get_loc(order.signal_date)))
            if symbol in positions and fill_price != open_price:
                intrabar_fills.add(symbol)

        # Stops are active during the bar, including a position entered at its open.
        for symbol in sorted(positions):
            loc = locs[symbol][di]
            if loc < 0:
                continue
            position = positions[symbol]
            open_price = float(price_arr[symbol]["open"][loc])
            low_price = float(price_arr[symbol]["low"][loc])
            if symbol in intrabar_fills:
                if low_price <= position.stop:
                    close_position(symbol, date, position.stop, "stop")
                continue
            if position.side < 0:  # short: the stop sits above the fill, the target below (A3: stop first)
                high_price = float(price_arr[symbol]["high"][loc])
                if open_price >= position.stop:
                    close_position(symbol, date, open_price, "gap_stop")
                elif high_price >= position.stop:
                    close_position(symbol, date, position.stop, "stop")
                elif np.isfinite(position.target) and open_price <= position.target:
                    close_position(symbol, date, open_price, "gap_target")
                elif np.isfinite(position.target) and low_price <= position.target:
                    close_position(symbol, date, position.target, "target")
                continue
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
            if profit_lock is not None and not position.locked:
                if "trigger_level_fn" in profit_lock:
                    trigger_price = float(profit_lock["trigger_level_fn"](
                        symbol, position.sig_loc, position.entry_price, position.initial_stop, position.target))
                else:
                    trigger_price = position.entry_price + profit_lock["trigger_atr"] * position.signal_atr
                if float(price_arr[symbol]["high"][loc]) >= trigger_price:
                    position.locked = True
                    locked_stop = (
                        float(profit_lock["stop_level_fn"](
                            symbol, position.sig_loc, position.entry_price, position.initial_stop, position.target))
                        if "stop_level_fn" in profit_lock
                        else float(profit_lock["stop_fn"](position.entry_price))
                    )
                    position.stop = max(position.stop, locked_stop)
            if trail_mode is None:
                continue
            current_atr = float(sig_trail[symbol][loc])
            if np.isfinite(current_atr):
                # VARSAYIM: PDF's ATR14x3 trailing stop uses close - ATR14x3.
                if position.side < 0:  # short: ratchet down from close (or low) + m x ATR
                    reference = float(price_arr[symbol]["close" if trail_mode == "close" else "low"][loc])
                    position.stop = min(position.stop, reference + trail_m * current_atr)
                else:
                    reference = float(price_arr[symbol]["close" if trail_mode == "close" else "high"][loc])
                    position.stop = max(position.stop, reference - trail_m * current_atr)

        # Closed-bar signals schedule orders for a later open; never this bar.
        # With fill_at_close the order fills at this bar's close (exits first).
        close_fills: list[tuple[str, float, float, float, float, float, float]] = []
        visit = set(positions) | {symbols[c] for c in entry_cols[entry_starts[di]:entry_starts[di + 1]]}
        for symbol in sorted(visit):
            loc = locs[symbol][di]
            if loc < 0:
                continue
            position = positions.get(symbol)
            exit_signal = bool(sig_exit[symbol][loc])
            if position is not None and position.side < 0:
                exit_signal = bool(sig_exit_short[symbol][loc])
            if position is not None:
                if position.runtime_exit is not None and bool(position.runtime_exit[loc]):
                    exit_signal = True
                if time_stop_bars is not None and position.bars_held >= time_stop_bars:
                    exit_signal = True
            entry_signal = bool(sig_entry[symbol][loc])
            entry_side = -1.0 if direction == "short" else 1.0
            if direction == "both" and not entry_signal and bool(sig_entry_short[symbol][loc]):
                entry_signal, entry_side = True, -1.0
            if fill_at_close:
                if position is not None and exit_signal:
                    close_position(symbol, date, float(price_arr[symbol]["close"][loc]), "signal")
                elif position is not None:
                    if partial_due(symbol, loc):
                        take_partial(symbol, float(price_arr[symbol]["close"][loc]))
                elif position is None and entry_signal and cooled_down(symbol):
                    close_fills.append((symbol, *sizing_at(symbol, loc), entry_side))
                continue
            if symbol in positions and not exit_signal and symbol not in pending and partial_due(symbol, loc):
                target_loc = loc + 1 + extra_delay_bars
                if target_loc < len(index_of[symbol]) and index_of[symbol][target_loc] <= end:
                    execute_date = index_of[symbol][target_loc]
                    scheduled.setdefault(execute_date, []).append(
                        Order(symbol, "partial", execute_date, date, float(sig_atr[symbol][loc]))
                    )
                    pending[symbol] = "partial"
                elif record_state and target_loc >= len(index_of[symbol]):
                    order_log.append({"sinyal_tarihi": date, "sembol": symbol, "tip": "kismi",
                                      "referans_fiyat": float(price_arr[symbol]["close"][loc])})
            elif symbol in positions and exit_signal and (symbol not in pending or pending[symbol] == "partial"):
                target_loc = loc + 1 + extra_delay_bars
                if target_loc < len(index_of[symbol]) and index_of[symbol][target_loc] <= end:
                    execute_date = index_of[symbol][target_loc]
                    order = Order(symbol, "exit", execute_date, date, float(sig_atr[symbol][loc]))
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "exit"
                elif record_state and target_loc >= len(index_of[symbol]):
                    order_log.append({"sinyal_tarihi": date, "sembol": symbol, "tip": "cikis",
                                      "referans_fiyat": float(price_arr[symbol]["close"][loc]), "adet": positions[symbol].quantity,
                                      "stop": positions[symbol].stop})
            elif symbol not in positions and entry_signal and (symbol not in pending or pending[symbol] == "pending_entry") and cooled_down(symbol):
                if entry_order_type is not None:
                    level = float(sig_entry_level[symbol][loc])
                    if np.isfinite(level) and level > 0:
                        atr_value, stop_dist, target_dist, stop_pct, target_pct = sizing_at(symbol, loc)
                        activate = loc + 1 + extra_delay_bars
                        pending_entries[symbol] = Order(
                            symbol, "pending_entry", date, date, atr_value, stop_dist, target_dist,
                            stop_pct, target_pct, level, activate, activate + entry_order_validity - 1,
                        )
                        pending[symbol] = "pending_entry"
                    continue
                target_loc = loc + 1 + extra_delay_bars
                if target_loc < len(index_of[symbol]) and index_of[symbol][target_loc] <= end:
                    execute_date = index_of[symbol][target_loc]
                    atr_value, stop_dist, target_dist, stop_pct, target_pct = sizing_at(symbol, loc)
                    order = Order(symbol, "entry", execute_date, date, atr_value,
                                  stop_dist, target_dist, stop_pct, target_pct, side=entry_side)
                    scheduled.setdefault(execute_date, []).append(order)
                    pending[symbol] = "entry"
                elif record_state and target_loc >= len(index_of[symbol]):
                    atr_value, stop_dist, target_dist, stop_pct, target_pct = sizing_at(symbol, loc)
                    reference = float(price_arr[symbol]["close"][loc])
                    sized = size_entry(symbol, reference, atr_value, stop_dist, target_dist, stop_pct, target_pct, int(loc), entry_side)
                    order_log.append({
                        "sinyal_tarihi": date, "sembol": symbol, "tip": "giris", "referans_fiyat": reference,
                        "adet": sized[0] if sized else 0.0, "stop": sized[1] if sized else float("nan"),
                        "hedef": reference + sized[3] if sized and np.isfinite(sized[3]) and sized[3] > 0 else float("nan"),
                    })
        for symbol, atr_value, stop_dist, target_dist, stop_pct, target_pct, side in close_fills:
            loc = locs[symbol][di]
            open_position(symbol, date, float(price_arr[symbol]["close"][loc]), atr_value,
                          stop_dist, target_dist, stop_pct, target_pct, int(loc), side)

        if not trades_only:
            marked_equity = equity_at("close")
            gross_close = sum(position.quantity * mark(symbol, "close") for symbol, position in positions.items())
            equity_points[date] = marked_equity
            exposure_points[date] = gross_close / marked_equity if marked_equity > 0 else np.nan

    final_date = dates[-1]
    open_state = (
        [
            {"sembol": symbol, "giris_tarihi": position.entry_date, "giris_fiyati": position.entry_price, "adet": position.quantity,
             "stop": position.stop, "hedef": position.target, "ilk_stop": position.initial_stop, "kismi_yapildi": position.partial_done,
             "son_kapanis": mark_last(symbol)}
            for symbol, position in sorted(positions.items())
        ]
        if record_state else []
    )
    marked_last = equity_points.get(final_date, float("nan"))
    for symbol in sorted(positions):
        loc = int(index_of[symbol].searchsorted(final_date, side="right")) - 1
        if loc < 0:
            continue
        close_position(symbol, index_of[symbol][loc], float(price_arr[symbol]["close"][loc]), "end_of_test")
    equity_points[final_date] = cash
    exposure_points[final_date] = 0.0

    trade_frame = pd.DataFrame([vars(trade) for trade in trades])  # asdict() would deep-copy every field
    if direction == "long" and "yon" in trade_frame.columns:
        trade_frame = trade_frame.drop(columns="yon")  # long-only results keep the historical column set
    equity = pd.Series(equity_points, name="equity", dtype=float).sort_index()
    exposure = pd.Series(exposure_points, name="exposure", dtype=float).sort_index()
    return BacktestResult(
        initial_capital, equity, exposure, trade_frame, max_open_positions,
        fills=fill_log, open_positions=open_state, next_orders=order_log, marked_equity=marked_last,
    )


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
