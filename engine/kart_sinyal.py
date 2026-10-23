"""Strategy card -> signals and portfolio-engine parameters (stage 1 scan).

The card expression language (`engine.expr`) and indicator library
(`engine.gosterge`) produce boolean entry/exit series plus the stop/target
columns that `engine.portfolio.run_portfolio` understands. Exit semantics are
fixed in docs/EVRENSEL_KURALLAR.md D5. A card feature the engine does not
implement raises `MotorDestegiYok`; the scan then skips the card and writes
``motor_destegi_yok:<alan>`` - nothing is silently ignored.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from . import expr as _expr
from .expr import ExprError
from . import gosterge as _ind
from .spec import RUNTIME_NAMES

BENCHMARK_RUNTIME = frozenset({"endeks_close"})
POSITION_RUNTIME = RUNTIME_NAMES - BENCHMARK_RUNTIME
STOP_TYPES = ("atr", "yuzde", "puan", "pips", "max", "seviye")
TARGET_TYPES = ("atr", "yuzde", "puan", "pips", "seviye")
TRAIL_TYPES = {"atr_zirve": "high", "atr_kapanis_zirve": "close"}
STANDARD_STOP_ATR = 3.0  # EVRENSEL_KURALLAR A7: ATR14 x 3 when the card has no stop of its own
SIZING_ATR = 14


class MotorDestegiYok(Exception):
    """The card uses a field the engine does not implement."""

    def __init__(self, field_name: str) -> None:
        super().__init__(field_name)
        self.field_name = field_name


class EndeksYok(Exception):
    """The card needs a market index series that is not available."""


class PipsPiyasaDisi(Exception):
    """Pip-denominated rules are defined only for the FX8 market."""


@dataclass
class KartPlan:
    signals: dict[str, pd.DataFrame]
    engine_kwargs: dict[str, Any]
    stop_eklendi: bool
    dolum_kapanis: bool = False
    notlar: list[str] = field(default_factory=list)


def _uses(card: Mapping[str, Any], names: frozenset[str]) -> bool:
    return any(
        names & _expr.parse(str(card[key])).names
        for key in ("giris", "cikis", "giris_short", "cikis_short")
        if card.get(key)
    )


YONLER = ("long", "short", "iki")
SHORT_YOK = ("kismi_kar", "roi_tablosu", "kar_kilidi", "giris_emri")  # long-only engine features (D17)


def card_direction(card: Mapping[str, Any]) -> str:
    """``yon`` of the card: ``long`` (default), ``short`` or ``iki`` (two-way)."""
    return str(card.get("yon") or "long")


def _uses_expr(card: Mapping[str, Any], keys: tuple[str, ...], names: frozenset[str]) -> bool:
    return any(names & _expr.parse(str(card[key])).names for key in keys if card.get(key))


def desteklenmeyen_alan(card: Mapping[str, Any]) -> str | None:
    """Name of the first card field the engine cannot honour, else None."""
    yon = card_direction(card)
    if yon not in YONLER:
        return f"yon.{yon}"
    if yon != "long":
        for key in SHORT_YOK:
            if card.get(key):
                return f"yon.{yon}+{key}"
        for key in ("stop", "hedef"):
            if isinstance(card.get(key), Mapping) and card[key].get("tip") == "seviye":
                return f"yon.{yon}+{key}.seviye"
        if yon == "iki" and not card.get("giris_short"):
            return "yon.iki+giris_short_yok"
    stop = card.get("stop")
    if stop and stop.get("tip") not in STOP_TYPES:
        return f"stop.{stop.get('tip')}"
    hedef = card.get("hedef")
    if hedef and hedef.get("tip") not in TARGET_TYPES:
        return f"hedef.{hedef.get('tip')}"
    trail = card.get("iz_suren")
    if trail and trail.get("tip") not in TRAIL_TYPES:
        return f"iz_suren.{trail.get('tip')}"
    if card.get("giris") and "giris_modu" in _expr.parse(card["giris"]).names:
        return "giris_modu"
    if card.get("cikis") and "giris_modu" in _expr.parse(card["cikis"]).names:
        return "giris_modu"
    if card.get("dolum") not in (None, "kapanis"):
        return f"dolum.{card.get('dolum')}"
    return None


def pip_size(symbol: str) -> float:
    """Price increment represented by one pip for an FX8 pair."""
    return 0.01 if "JPY" in symbol.upper() else 0.0001


def _uses_pips(card: Mapping[str, Any]) -> bool:
    return any(isinstance(card.get(field), Mapping) and card[field].get("tip") == "pips" for field in ("stop", "hedef"))


def needs_benchmark(card: Mapping[str, Any]) -> bool:
    if _uses(card, BENCHMARK_RUNTIME):
        return True
    for spec in (card.get("gostergeler") or {}).values():
        if not isinstance(spec, dict):
            continue
        if spec.get("benchmark") or spec.get("veri"):
            return True
        if any("endeks_close" in str(spec.get(key) or "") for key in ("src", "ifade")):
            return True
    order = card.get("giris_emri")
    if isinstance(order, Mapping) and order.get("seviye"):
        if BENCHMARK_RUNTIME & _expr.parse(str(order["seviye"])).names:
            return True
    return False


def mtf_callback(frame: pd.DataFrame) -> Callable[[str, pd.Series], pd.Series]:
    """`mtf("1W", x)`: value of x at the last bar of the previous completed higher-timeframe bar."""
    def callback(tf: str, series: pd.Series) -> pd.Series:
        keys = _ind._htf_keys(frame.index, tf)  # noqa: SLF001 - shared bin definition
        return _ind.align_htf(series.groupby(keys, sort=True).last(), keys, frame.index)

    return callback


LAZY_FUNCS = frozenset({"cross_over", "cross_under", "max", "min", "abs", "eger"})
LAZY_FIRST_CHUNK, LAZY_MAX_CHUNK = 64, 4096


def _lazy_warmup(expression: _expr.Expr) -> int | None:
    """Bars of history a chunked evaluation of ``expression`` needs, or None when it must see the whole series.

    Only elementwise rules qualify: lags (`x[k]`) and crossings look back a bounded number of bars, whereas
    `valuewhen`/`barssince`/`mtf`/calendar functions depend on the whole index."""
    if not expression.funcs <= LAZY_FUNCS:
        return None
    lags = 0
    for node in ast.walk(expression.tree):
        if isinstance(node, ast.Subscript):
            lags += int(node.slice.value)
        elif isinstance(node, ast.Call) and node.func.id in ("cross_over", "cross_under"):
            lags += 1
    return lags


def _arrays(env: Mapping[str, Any]) -> dict[str, Any]:
    """Env with every Series/DataFrame replaced by float64 arrays (DataFrames by a dict of columns)."""
    out: dict[str, Any] = {}
    for name, value in env.items():
        if isinstance(value, pd.Series):
            out[name] = value.to_numpy(dtype=float)
        elif isinstance(value, pd.DataFrame):
            out[name] = {column: value[column].to_numpy(dtype=float) for column in value.columns}
        elif isinstance(value, dict):
            out[name] = _arrays(value)
        else:
            out[name] = value
    return out


def _flag(value: Any) -> Any:
    """`expr._as_bool` on arrays: NaN counts as False."""
    if isinstance(value, np.ndarray):
        return value if value.dtype == bool else (np.nan_to_num(value, nan=0.0) != 0)
    return bool(value)


def _shift(value: Any, lag: int) -> Any:
    if not isinstance(value, np.ndarray) or lag == 0:
        return value
    out = np.full(len(value), np.nan)
    if lag < len(value):
        out[lag:] = value[:-lag]
    return out


def _cmp(op: ast.cmpop, left: Any, right: Any) -> Any:
    return {ast.Lt: np.less, ast.LtE: np.less_equal, ast.Gt: np.greater, ast.GtE: np.greater_equal,
            ast.Eq: np.equal, ast.NotEq: np.not_equal}[type(op)](left, right)


def _both(a: Any, b: Any) -> Any:
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.asarray(a, dtype=bool) & np.asarray(b, dtype=bool)
    return bool(a) and bool(b)


def _either(a: Any, b: Any) -> Any:
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.asarray(a, dtype=bool) | np.asarray(b, dtype=bool)
    return bool(a) or bool(b)


def _np_eval(node: ast.AST, env: Mapping[str, Any], size: int) -> Any:
    """Array twin of `engine.expr` for the elementwise subset (LAZY_FUNCS); same NaN semantics as the pandas evaluator."""
    def ev(item: ast.AST) -> Any:
        return _np_eval(item, env, size)

    def full(value: Any) -> np.ndarray:
        return value if isinstance(value, np.ndarray) else np.full(size, value)

    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return env[node.id]
    if isinstance(node, ast.Attribute):
        return env[node.value.id][node.attr]
    if isinstance(node, ast.Subscript):
        return _shift(ev(node.value), int(node.slice.value))
    if isinstance(node, ast.UnaryOp):
        operand = ev(node.operand)
        if isinstance(node.op, ast.Not):
            flag = _flag(operand)
            return ~flag if isinstance(flag, np.ndarray) else (not flag)
        return -operand if isinstance(node.op, ast.USub) else +operand
    if isinstance(node, ast.BinOp):
        left, right = ev(node.left), ev(node.right)
        with np.errstate(all="ignore"):
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            return left / right
    if isinstance(node, ast.Compare):
        left, result = ev(node.left), None
        for op, comparator in zip(node.ops, node.comparators):
            right = ev(comparator)
            with np.errstate(all="ignore"):
                part = _cmp(op, left, right)
            result = part if result is None else _both(result, part)
            left = right
        return result
    if isinstance(node, ast.BoolOp):
        values = [_flag(ev(v)) for v in node.values]
        result = values[0]
        for value in values[1:]:
            result = _both(result, value) if isinstance(node.op, ast.And) else _either(result, value)
        return result
    if isinstance(node, ast.Call):
        name, args = node.func.id, [ev(arg) for arg in node.args]
        if name in ("cross_over", "cross_under"):
            a, b = full(args[0]), full(args[1])
            with np.errstate(all="ignore"):
                if name == "cross_over":
                    return (a > b) & (_shift(a, 1) <= _shift(b, 1))
                return (a < b) & (_shift(a, 1) >= _shift(b, 1))
        if name == "eger":
            cond = _flag(args[0])
            if isinstance(cond, np.ndarray) or any(isinstance(a, np.ndarray) for a in args[1:]):
                return np.where(full(cond).astype(bool), full(args[1]), full(args[2]))
            return args[1] if cond else args[2]
        if name in ("max", "min"):
            return (np.maximum if name == "max" else np.minimum)(args[0], args[1])
        return abs(args[0])
    raise ExprError(f"cannot evaluate {type(node).__name__}")


def _window(value: Any, begin: int, stop: int) -> Any:
    if isinstance(value, np.ndarray):
        return value[begin:stop]
    if isinstance(value, dict):
        return {key: _window(item, begin, stop) for key, item in value.items()}
    return value


class LazyExit:
    """`built[loc]` of a position-state exit rule, evaluated per chunk of bars instead of over the whole series.

    The engine reads one bar at a time while the position is open; a 5-minute book with thousands of entries
    otherwise re-evaluates the rule over ~700k bars per entry. Results equal the full evaluation (each chunk
    carries ``warmup`` bars of history; bars before the entry are False)."""

    def __init__(self, expression: _expr.Expr, arrays: Mapping[str, Any], runtime: Mapping[str, Any], size: int,
                 entry_loc: int, warmup: int) -> None:
        self.expression, self.arrays, self.runtime = expression, arrays, runtime
        self.size, self.entry_loc, self.warmup = size, entry_loc, warmup
        self.first = self.last = entry_loc
        self.values = np.zeros(0, dtype=bool)
        self.step = LAZY_FIRST_CHUNK

    def __getitem__(self, loc: int) -> bool:
        while loc >= self.last:
            self._extend()
        return bool(self.values[loc - self.first]) if loc >= self.first else False

    def _extend(self) -> None:
        start = self.last
        stop = min(start + self.step, self.size)
        self.step = min(self.step * 2, LAZY_MAX_CHUNK)
        begin = max(start - self.warmup, 0)
        env = {name: _window(value, begin, stop) for name, value in self.arrays.items()}
        env.update(self.runtime)
        env["bars_since_entry"] = np.arange(begin, stop, dtype=float) - self.entry_loc
        chunk = _flag(_np_eval(self.expression.tree.body, env, stop - begin))
        chunk = chunk if isinstance(chunk, np.ndarray) else np.full(stop - begin, chunk)
        self.values = np.concatenate([self.values, chunk[start - begin:]])
        self.last = stop


def _bool(value: Any, index: pd.Index) -> pd.Series:
    if isinstance(value, pd.Series):
        return value.fillna(False).astype(bool)
    return pd.Series(bool(value), index=index)


def _series(value: Any, index: pd.Index) -> pd.Series:
    return value.astype(float) if isinstance(value, pd.Series) else pd.Series(float(value), index=index)


def _eval_series(text: str, env: Mapping[str, Any], index: pd.Index, mtf: Callable) -> pd.Series:
    return _series(_expr.parse(text).evaluate(env, index=index, mtf=mtf), index)


def card_frame_signals(
    card: Mapping[str, Any],
    frame: pd.DataFrame,
    *,
    week_end: str,
    benchmark: pd.DataFrame | None = None,
    pip_value: float | None = None,
) -> tuple[pd.DataFrame, Callable[..., pd.Series | None] | None]:
    """Signals for one symbol plus an optional position-state exit builder."""
    index = frame.index
    benchmarks = {"endeks": benchmark} if benchmark is not None else None
    if needs_benchmark(card) and benchmarks is None:
        raise EndeksYok(card["id"])
    env = _ind.build_env(frame, card.get("gostergeler") or {}, benchmarks=benchmarks, week_end=week_end)
    mtf = mtf_callback(frame)
    positions = np.arange(len(index))

    def rules(entry_text: str, exit_text: Any, short: bool = False):
        """Entry series, static exit series and the position-state exit builder of one side."""
        entry = _bool(_expr.parse(entry_text).evaluate(env, index=index, mtf=mtf), index)
        if isinstance(exit_text, str) and exit_text.strip().lower() == "false":
            exit_text = None  # Argon writes the text 'false' for "no exit rule"; stops/targets close the trade
        builder = None
        if not exit_text:
            exit_static = pd.Series(False, index=index)
        elif POSITION_RUNTIME & _expr.parse(exit_text).names:
            exit_static = pd.Series(False, index=index)
            exit_expr = _expr.parse(exit_text)
            warmup = _lazy_warmup(exit_expr)
            arrays = _arrays({name: env[name] for name in exit_expr.names if name in env}) if warmup is not None else None

            def builder(symbol: str, entry_date: pd.Timestamp, price: float, stop: float, target: float):  # noqa: ARG001
                loc = index.get_loc(entry_date)
                runtime = {
                    "giris": price, "giris_fiyati": price, "giris_stop": stop,
                    "giris_hedef": target, "stop_mesafesi": (stop - price) if short else (price - stop),
                }
                if warmup is not None:  # elementwise rule: evaluate in chunks, only as far as the position lives
                    return LazyExit(exit_expr, arrays, runtime, len(index), loc, warmup)
                runtime["bars_since_entry"] = pd.Series(positions - loc, index=index, dtype=float)
                out = _bool(exit_expr.evaluate({**env, **runtime}, index=index, mtf=mtf), index)
                return out & pd.Series(positions >= loc, index=index)
        else:
            exit_static = _bool(_expr.parse(exit_text).evaluate(env, index=index, mtf=mtf), index)
        return entry, exit_static, builder

    yon = card_direction(card)
    entry, exit_static, builder = rules(card["giris"], card.get("cikis"), short=(yon == "short"))
    atr_sizing = _ind.atr(frame, SIZING_ATR)
    if yon == "long":
        out = pd.DataFrame({"entry": entry, "exit": exit_static, "atr": atr_sizing}, index=index)
    elif yon == "short":  # `giris`/`cikis` describe the short side (D17)
        never = pd.Series(False, index=index)
        out = pd.DataFrame({"entry": never, "exit": never, "entry_short": entry, "exit_short": exit_static,
                            "atr": atr_sizing}, index=index)
    else:  # iki: `giris`/`cikis` = long side, `giris_short`/`cikis_short` = short side
        entry_short, exit_short, builder_short = rules(card["giris_short"], card.get("cikis_short"), short=True)
        out = pd.DataFrame({"entry": entry, "exit": exit_static, "entry_short": entry_short, "exit_short": exit_short,
                            "atr": atr_sizing}, index=index)
        if builder is not None or builder_short is not None:
            long_builder = builder

            def builder(symbol, entry_date, price, stop, target, _long=long_builder, _short=builder_short):  # noqa: ANN001
                chosen = _short if stop > price else _long  # the stop sits above a short fill
                return chosen(symbol, entry_date, price, stop, target) if chosen else None

    entry_order = card.get("giris_emri")
    if entry_order:
        out["entry_level"] = _eval_series(str(entry_order["seviye"]), env, index, mtf)

    stop, hedef, trail = card.get("stop"), card.get("hedef"), card.get("iz_suren")
    if stop and stop["tip"] == "seviye":
        pass  # absolute level resolved at the fill from signal-bar values (level_fns)
    elif stop:
        if stop["tip"] == "atr":
            out["stop_dist"] = float(stop["carpan"]) * _ind.atr(frame, int(stop.get("n", SIZING_ATR)))
        elif stop["tip"] == "yuzde":
            out["stop_pct"] = float(stop["deger"]) / 100.0
        elif stop["tip"] == "puan":
            out["stop_dist"] = float(stop["deger"])
        elif stop["tip"] == "pips":
            if pip_value is None:
                raise ValueError("pips requires an FX symbol")
            out["stop_dist"] = float(stop["deger"]) * pip_value
        else:
            out["stop_dist"] = pd.concat(
                [_eval_series(text, env, index, mtf) for text in stop["secenekler"]], axis=1
            ).max(axis=1, skipna=False)
    elif trail:
        out["stop_dist"] = float(trail["carpan"]) * _ind.atr(frame, int(trail.get("n", SIZING_ATR)))
    else:
        out["stop_dist"] = STANDARD_STOP_ATR * atr_sizing
    if hedef and hedef["tip"] == "seviye":
        pass
    elif hedef:
        if hedef["tip"] == "atr":
            out["target_dist"] = float(hedef["carpan"]) * _ind.atr(frame, int(hedef.get("n", SIZING_ATR)))
        elif hedef["tip"] == "yuzde":
            out["target_pct"] = float(hedef["deger"]) / 100.0
        elif hedef["tip"] == "pips":
            if pip_value is None:
                raise ValueError("pips requires an FX symbol")
            out["target_dist"] = float(hedef["deger"]) * pip_value
        else:
            out["target_dist"] = float(hedef["deger"])
    if trail:
        out["trail_atr"] = _ind.atr(frame, int(trail.get("n", SIZING_ATR)))
    if _uses_signal_levels(card):
        out.attrs["sinyal_baglam"] = signal_context(card, frame, env)
    return out, builder


def _uses_signal_levels(card: Mapping[str, Any]) -> bool:
    stop, hedef, lock = card.get("stop"), card.get("hedef"), card.get("kar_kilidi")
    return bool(
        (stop and stop.get("tip") == "seviye") or (hedef and hedef.get("tip") == "seviye")
        or (lock and "tetik_seviye" in lock)
    )


def _level_texts(card: Mapping[str, Any]) -> list[str]:
    """Expressions of the card's signal-bar level rules (stop/target level, profit lock)."""
    texts = []
    for key in ("stop", "hedef"):
        block = card.get(key)
        if block and block.get("tip") == "seviye":
            texts.append(str(block["ifade"]))
    lock = card.get("kar_kilidi")
    if lock and "tetik_seviye" in lock:
        texts += [str(lock["tetik_seviye"]), str(lock["stop"])]
    return texts


def signal_context(card: Mapping[str, Any], frame: pd.DataFrame, env: Mapping[str, Any]) -> dict[str, Any]:
    """Arrays of signal-bar values for the ``sinyal_<ad>`` references of the level rules (OHLC columns and card indicators).

    Only names a level expression mentions are kept: the full set (every indicator, 8 bytes a bar) is what made
    5-minute books of 25 symbols run out of memory."""
    wanted = set().union(*(parse_names(text) for text in _level_texts(card)))
    context: dict[str, Any] = {}
    for name in ("open", "high", "low", "close", "volume"):
        if f"sinyal_{name}" in wanted:
            context[f"sinyal_{name}"] = frame[name].to_numpy(dtype=float)
    for name in (card.get("gostergeler") or {}):
        if f"sinyal_{name}" not in wanted:
            continue
        value = env.get(name)
        if isinstance(value, pd.Series):
            context[f"sinyal_{name}"] = value.to_numpy(dtype=float)
        elif isinstance(value, pd.DataFrame):
            context[f"sinyal_{name}"] = {col: value[col].to_numpy(dtype=float) for col in value.columns}
    return context


def parse_names(text: str) -> frozenset[str]:
    return _expr.parse(text).names


def _level_fn(text: str, contexts: Mapping[str, dict[str, Any]], extra: tuple[str, ...]) -> Callable[..., float]:
    """``fn(symbol, signal_loc, fill_price, *extra_values)`` evaluating ``text`` at the signal bar."""
    expression = _expr.parse(str(text))

    def fn(symbol: str, loc: int, price: float, *values: float) -> float:
        env: dict[str, Any] = {"giris": price, "giris_fiyati": price}
        for name, array in contexts[symbol].items():
            env[name] = {col: values_[loc] for col, values_ in array.items()} if isinstance(array, dict) else array[loc]
        env.update(zip(extra, values))
        return float(expression.evaluate(env, index=None))

    return fn


def build_plan(
    card: Mapping[str, Any],
    data: Mapping[str, pd.DataFrame],
    *,
    week_end: str,
    benchmark: pd.DataFrame | None = None,
    market: str | None = None,
) -> KartPlan:
    """Signals for every symbol and the engine keyword arguments for the card."""
    missing = desteklenmeyen_alan(card)
    if missing:
        raise MotorDestegiYok(missing)
    if _uses_pips(card) and market is not None and market not in ("FX8", "FXDK"):
        raise PipsPiyasaDisi()
    signals: dict[str, pd.DataFrame] = {}
    builders: dict[str, Callable[..., pd.Series | None] | None] = {}
    contexts: dict[str, dict[str, Any]] = {}
    for symbol, frame in data.items():
        signals[symbol], builders[symbol] = card_frame_signals(
            card, frame, week_end=week_end, benchmark=benchmark,
            pip_value=pip_size(symbol) if _uses_pips(card) else None,
        )
        contexts[symbol] = signals[symbol].attrs.get("sinyal_baglam", {})

    trail = card.get("iz_suren")
    kwargs: dict[str, Any] = {
        "trail_mode": TRAIL_TYPES[trail["tip"]] if trail else None,
        "trail_multiple": float(trail["carpan"]) if trail else None,
        "fill_at_close": card.get("dolum") == "kapanis",
    }
    yon = card_direction(card)
    if yon != "long":
        kwargs["direction"] = "short" if yon == "short" else "both"
    if card.get("seans_sonu_kapat"):
        clock, _, zone_name = str(card["seans_sonu_kapat"]).partition(" ")
        kwargs["session_close"] = (clock.strip(), zone_name.strip() or "UTC")
    entry_order = card.get("giris_emri")
    if entry_order:
        kwargs["entry_order_type"] = str(entry_order["tip"])
        kwargs["entry_order_validity"] = int(entry_order["gecerlilik_bar"])
    zaman = card.get("zaman_stop")
    if zaman:
        kwargs["time_stop_bars"] = int(zaman["bar"])
    if card.get("cooldown_bar"):
        kwargs["cooldown_bars"] = int(card["cooldown_bar"])
    levels: dict[str, Callable[..., float]] = {}
    stop_card, target_card = card.get("stop"), card.get("hedef")
    if stop_card and stop_card.get("tip") == "seviye":
        levels["stop"] = _level_fn(stop_card["ifade"], contexts, ())
    if target_card and target_card.get("tip") == "seviye":
        levels["target"] = _level_fn(target_card["ifade"], contexts, ("stop_seviyesi",))
    if levels:
        kwargs["level_fns"] = levels
    lock = card.get("kar_kilidi")
    if lock and "tetik_seviye" in lock:
        kwargs["profit_lock"] = {
            "trigger_level_fn": _level_fn(lock["tetik_seviye"], contexts, ("stop_seviyesi", "hedef_seviyesi")),
            "stop_level_fn": _level_fn(lock["stop"], contexts, ("stop_seviyesi", "hedef_seviyesi")),
        }
    elif lock:
        lock_expr = _expr.parse(str(lock["stop"]))
        kwargs["profit_lock"] = {
            "trigger_atr": float(lock["tetik_atr"]),
            "stop_fn": lambda price, e=lock_expr: float(e.evaluate({"giris": price, "giris_fiyati": price}, index=None)),
        }
    if card.get("roi_tablosu"):
        kwargs["roi_table"] = {float(k): float(v) for k, v in card["roi_tablosu"].items()}
    partial = card.get("kismi_kar")
    if partial:
        stop_expr = _expr.parse(str(partial["kalan_stop"]))
        config: dict[str, Any] = {
            "gun": int(partial["gun"]), "oran": float(partial["oran"]),
            "stop_fn": lambda price, e=stop_expr: float(e.evaluate({"giris": price, "giris_fiyati": price}, index=None)),
        }
        if "tetik_atr" in partial:
            config["trigger_atr"] = float(partial["tetik_atr"])
        else:
            trigger_expr = _expr.parse(str(partial["tetik"]))
            config["trigger_fn"] = lambda price, distance, e=trigger_expr: float(
                e.evaluate({"giris": price, "giris_fiyati": price, "stop_mesafesi": distance}, index=None)
            )
        kwargs["partial_profit"] = config
    if any(builders.values()):
        kwargs["exit_builder"] = lambda symbol, *args: builders[symbol](symbol, *args) if builders.get(symbol) else None
    return KartPlan(
        signals=signals,
        engine_kwargs=kwargs,
        stop_eklendi=not card.get("stop") and not trail,
        dolum_kapanis=kwargs["fill_at_close"],
    )
