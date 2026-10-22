"""T33 party 1: custom daily pattern strategies and no-look-ahead guarantees."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from backtests import tarama
from strategies.ozel import a1_027

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def _frame(high: list[float], low: list[float], close: list[float] | None = None, start: str = "2024-01-01") -> pd.DataFrame:
    close = close or [(h + l) / 2 for h, l in zip(high, low, strict=True)]
    index = pd.bdate_range(start, periods=len(high), tz="UTC")
    return pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": 1000.0}, index=index,
    )


def _a1_pattern_frame() -> pd.DataFrame:
    high = [12, 13, 25, 20, 18, 16, 10, 10, 10, 10, 15, 13, 12, 11, 10, 16, 25, 24]
    low = [9, 9, 10, 9, 8, 7, 5, 6, 7, 8, 9, 8, 7, 6, 5.2, 6, 12, 13]
    close = [10, 11, 20, 15, 13, 10, 7, 8, 9, 10, 13, 11, 9, 8, 10, 16, 24, 20]
    return _frame(high, low, close)


def test_a1_027_double_bottom_enters_and_completes_a_trade() -> None:
    frame = _a1_pattern_frame()
    signal = a1_027.signals(frame, length=3, tolerance=15, fib=100)
    assert signal["entry"].any()
    card = {
        "id": "A1-027", "tf": "1D", "ozel_kod": True,
        "parametreler": {"len": 3, "tol": 15, "fib": 100},
    }
    prepared = tarama.prepare(
        card, {"X": frame}, "ABD25", start=frame.index[0], end=frame.index[-1],
    )
    result = prepared.run()
    assert not result.trades.empty
    assert result.trades.iloc[0]["exit_reason"] in {"target", "gap_target", "stop", "gap_stop"}


def test_a1_027_does_not_change_past_signals_when_future_changes() -> None:
    frame = _a1_pattern_frame()
    cut = 16
    before = a1_027.signals(frame.iloc[:cut], length=3)
    changed = frame.copy()
    changed.iloc[cut:, changed.columns.get_loc("high")] *= 5
    after = a1_027.signals(changed, length=3).iloc[:cut]
    pd.testing.assert_frame_equal(before, after)


def test_only_implemented_party_one_cards_load() -> None:
    loaded = {card["id"] for card in tarama.load_cards(SPEC, "1D")}
    assert "A1-027" in loaded
    assert {"A6-015", "P3-010", "M019"}.isdisjoint(loaded)
