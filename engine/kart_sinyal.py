"""Strategy card -> signals and portfolio-engine parameters (stage 1 scan).

The card expression language (`engine.expr`) and indicator library
(`engine.gosterge`) produce boolean entry/exit series plus the stop/target
columns that `engine.portfolio.run_portfolio` understands. Exit semantics are
fixed in docs/EVRENSEL_KURALLAR.md D5. A card feature the engine does not
implement raises `MotorDestegiYok`; the scan then skips the card and writes
``motor_destegi_yok:<alan>`` - nothing is silently ignored.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from . import expr as _expr
from . import gosterge as _ind
from .spec import RUNTIME_NAMES

BENCHMARK_RUNTIME = frozenset({"endeks_close"})
POSITION_RUNTIME = RUNTIME_NAMES - BENCHMARK_RUNTIME
STOP_TYPES = ("atr", "yuzde", "puan", "max")
TARGET_TYPES = ("atr", "yuzde", "puan")
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
        for key in ("giris", "cikis")
        if card.get(key)
    )


def desteklenmeyen_alan(card: Mapping[str, Any]) -> str | None:
    """Name of the first card field the engine cannot honour, else None."""
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


def needs_benchmark(card: Mapping[str, Any]) -> bool:
    if _uses(card, BENCHMARK_RUNTIME):
        return True
    for spec in (card.get("gostergeler") or {}).values():
        if not isinstance(spec, dict):
            continue
        if spec.get("benchmark"):
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
) -> tuple[pd.DataFrame, Callable[..., pd.Series | None] | None]:
    """Signals for one symbol plus an optional position-state exit builder."""
    index = frame.index
    benchmarks = {"endeks": benchmark} if benchmark is not None else None
    if needs_benchmark(card) and benchmarks is None:
        raise EndeksYok(card["id"])
    env = _ind.build_env(frame, card.get("gostergeler") or {}, benchmarks=benchmarks, week_end=week_end)
    mtf = mtf_callback(frame)
    entry = _bool(_expr.parse(card["giris"]).evaluate(env, index=index, mtf=mtf), index)

    exit_text = card.get("cikis")
    if isinstance(exit_text, str) and exit_text.strip().lower() == "false":
        exit_text = None  # Argon writes the text 'false' for "no exit rule"; stops/targets close the trade
    builder = None
    if not exit_text:
        exit_static = pd.Series(False, index=index)
    elif POSITION_RUNTIME & _expr.parse(exit_text).names:
        exit_static = pd.Series(False, index=index)
        exit_expr = _expr.parse(exit_text)
        positions = np.arange(len(index))

        def builder(symbol: str, entry_date: pd.Timestamp, price: float, stop: float, target: float) -> pd.Series:  # noqa: ARG001
            loc = index.get_loc(entry_date)
            runtime = {
                "giris": price, "giris_fiyati": price, "giris_stop": stop,
                "giris_hedef": target, "stop_mesafesi": price - stop,
                "bars_since_entry": pd.Series(positions - loc, index=index, dtype=float),
            }
            out = _bool(exit_expr.evaluate({**env, **runtime}, index=index, mtf=mtf), index)
            return out & pd.Series(positions >= loc, index=index)
    else:
        exit_static = _bool(_expr.parse(exit_text).evaluate(env, index=index, mtf=mtf), index)

    atr_sizing = _ind.atr(frame, SIZING_ATR)
    out = pd.DataFrame({"entry": entry, "exit": exit_static, "atr": atr_sizing}, index=index)

    entry_order = card.get("giris_emri")
    if entry_order:
        out["entry_level"] = _eval_series(str(entry_order["seviye"]), env, index, mtf)

    stop, hedef, trail = card.get("stop"), card.get("hedef"), card.get("iz_suren")
    if stop:
        if stop["tip"] == "atr":
            out["stop_dist"] = float(stop["carpan"]) * _ind.atr(frame, int(stop.get("n", SIZING_ATR)))
        elif stop["tip"] == "yuzde":
            out["stop_pct"] = float(stop["deger"]) / 100.0
        elif stop["tip"] == "puan":
            out["stop_dist"] = float(stop["deger"])
        else:
            out["stop_dist"] = pd.concat(
                [_eval_series(text, env, index, mtf) for text in stop["secenekler"]], axis=1
            ).max(axis=1, skipna=False)
    elif trail:
        out["stop_dist"] = float(trail["carpan"]) * _ind.atr(frame, int(trail.get("n", SIZING_ATR)))
    else:
        out["stop_dist"] = STANDARD_STOP_ATR * atr_sizing
    if hedef:
        if hedef["tip"] == "atr":
            out["target_dist"] = float(hedef["carpan"]) * _ind.atr(frame, int(hedef.get("n", SIZING_ATR)))
        elif hedef["tip"] == "yuzde":
            out["target_pct"] = float(hedef["deger"]) / 100.0
        else:
            out["target_dist"] = float(hedef["deger"])
    if trail:
        out["trail_atr"] = _ind.atr(frame, int(trail.get("n", SIZING_ATR)))
    return out, builder


def build_plan(
    card: Mapping[str, Any],
    data: Mapping[str, pd.DataFrame],
    *,
    week_end: str,
    benchmark: pd.DataFrame | None = None,
) -> KartPlan:
    """Signals for every symbol and the engine keyword arguments for the card."""
    missing = desteklenmeyen_alan(card)
    if missing:
        raise MotorDestegiYok(missing)
    signals: dict[str, pd.DataFrame] = {}
    builders: dict[str, Callable[..., pd.Series | None] | None] = {}
    for symbol, frame in data.items():
        signals[symbol], builders[symbol] = card_frame_signals(card, frame, week_end=week_end, benchmark=benchmark)

    trail = card.get("iz_suren")
    kwargs: dict[str, Any] = {
        "trail_mode": TRAIL_TYPES[trail["tip"]] if trail else None,
        "trail_multiple": float(trail["carpan"]) if trail else None,
        "fill_at_close": card.get("dolum") == "kapanis",
    }
    entry_order = card.get("giris_emri")
    if entry_order:
        kwargs["entry_order_type"] = str(entry_order["tip"])
        kwargs["entry_order_validity"] = int(entry_order["gecerlilik_bar"])
    zaman = card.get("zaman_stop")
    if zaman:
        kwargs["time_stop_bars"] = int(zaman["bar"])
    if card.get("cooldown_bar"):
        kwargs["cooldown_bars"] = int(card["cooldown_bar"])
    lock = card.get("kar_kilidi")
    if lock:
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
