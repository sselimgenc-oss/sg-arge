"""T30: bellek/hiz iyilestirmelerinin davranisi degistirmedigi ve bellek tavani."""

from __future__ import annotations

import tracemalloc
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import tarama
from engine import kart_sinyal
from engine.expr import parse
from engine.gosterge import _seeded_smooth
from engine.kart_sinyal import EndeksYok, MotorDestegiYok, POSITION_RUNTIME, card_frame_signals

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def intraday(seed: int, periods: int, freq: str = "5min") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = pd.date_range("2020-01-01", periods=periods, freq=freq, tz="UTC")
    close = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.002, periods)))
    open_ = close * (1 + rng.normal(0, 0.0007, periods))
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) * (1 + abs(rng.normal(0, 0.001, periods))),
            "low": np.minimum(open_, close) * (1 - abs(rng.normal(0, 0.001, periods))),
            "close": close,
            "volume": rng.uniform(1e3, 2e4, periods),
        },
        index=index,
    )


def position_exit_cards() -> list[dict]:
    cards = []
    for path in sorted(SPEC.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        text = data.get("cikis")
        if (
            data.get("spec_durumu") in ("tam", "dakikalik") and not data.get("ozel_kod") and not data.get("rotasyon")
            and isinstance(text, str) and text.strip().lower() != "false" and POSITION_RUNTIME & parse(text).names
        ):
            cards.append(data)
    return cards


def test_lazy_exit_equals_full_evaluation(monkeypatch) -> None:
    """Chunked `LazyExit` gives the same bar-by-bar exit flags as evaluating the rule over the whole series."""
    frame = intraday(3, 6000)
    compared = 0
    for data in position_exit_cards():
        if kart_sinyal._lazy_warmup(parse(data["cikis"])) is None:  # noqa: SLF001
            continue
        try:
            _, lazy_builder = card_frame_signals(data, frame, week_end="FRI")
        except (EndeksYok, MotorDestegiYok, ValueError):
            continue
        with monkeypatch.context() as patch:
            patch.setattr(kart_sinyal, "_lazy_warmup", lambda expression: None)
            _, full_builder = card_frame_signals(data, frame, week_end="FRI")
        for entry_loc in (0, 1, 7, 150, 2999, 5990):
            date, price = frame.index[entry_loc], float(frame["close"].iloc[entry_loc])
            args = (data["id"], date, price, price * 0.97, price * 1.03)
            lazy, full = lazy_builder(*args), full_builder(*args)
            expected = full.to_numpy()
            got = np.array([lazy[loc] for loc in range(len(frame))])
            assert np.array_equal(got, expected), (data["id"], entry_loc)
        compared += 1
    assert compared >= 4


def test_lazy_exit_falls_back_for_history_dependent_rules() -> None:
    assert kart_sinyal._lazy_warmup(parse("close > giris_fiyati")) == 0  # noqa: SLF001
    assert kart_sinyal._lazy_warmup(parse("cross_over(close, ema10) or close[3] < giris_stop")) == 4  # noqa: SLF001
    for text in ("bars_since_entry > 3 and highestsince(close > giris_fiyati, close) > 1", "mtf('1W', close) > giris_fiyati"):
        assert kart_sinyal._lazy_warmup(parse(text)) is None  # noqa: SLF001


def _reference_smooth(values: pd.Series, n: int, alpha: float) -> np.ndarray:
    """The pre-T30 loop (numpy scalars), kept as the bitwise reference."""
    arr = values.to_numpy(dtype=float)
    out = np.full(len(arr), np.nan)
    valid = np.flatnonzero(~np.isnan(arr))
    if len(valid) < n:
        return out
    start = valid[0]
    while start + n <= len(arr) and np.isnan(arr[start:start + n]).any():
        nxt = np.flatnonzero(~np.isnan(arr[start + 1:]))
        if not len(nxt):
            return out
        start = start + 1 + nxt[0]
    if start + n > len(arr):
        return out
    state = arr[start:start + n].mean()
    out[start + n - 1] = state
    for i in range(start + n, len(arr)):
        if not np.isnan(arr[i]):
            state = alpha * arr[i] + (1 - alpha) * state
        out[i] = state
    return out


@pytest.mark.parametrize("n", [3, 14, 50])
def test_seeded_smooth_is_bitwise_identical(n: int) -> None:
    rng = np.random.default_rng(n)
    values = rng.normal(100, 5, 5000)
    values[:7] = np.nan
    values[rng.integers(0, 5000, 60)] = np.nan
    series = pd.Series(values)
    for alpha in (1.0 / n, 2.0 / (n + 1)):
        assert np.array_equal(_seeded_smooth(series, n, alpha).to_numpy(), _reference_smooth(series, n, alpha), equal_nan=True)


@pytest.mark.parametrize("card_id", ["A3-002d", "A3-010b"])
def test_trusted_inputs_give_identical_runs(card_id: str) -> None:
    """The scan skips the engine's defensive copies; trades and equity must not change."""
    data = yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))
    frames = {f"S{i}": intraday(i, 4000) for i in range(3)}
    start, end = frames["S0"].index[0], frames["S0"].index[-1]
    prepared = tarama.prepare(data, frames, "KRIPTO25", start=start, end=end)
    copied, trusted = prepared.run(1.0), prepared.run(1.0, trusted_inputs=True)
    pd.testing.assert_frame_equal(copied.trades, trusted.trades)
    pd.testing.assert_series_equal(copied.equity, trusted.equity)
    assert len(copied.trades) > 0


def test_worker_count_follows_free_memory(monkeypatch) -> None:
    """isci = max(1, min(istenen, floor(0.8 * bos_bellek / isci_basina_zirve)))."""
    frames = {"S0": intraday(0, 10_000)}
    one = tarama.veri_baytlari(frames)
    monkeypatch.setattr(tarama, "bos_bellek", lambda: 10.0 * one)
    assert tarama.bellek_isci(8, frames, is_basina=2.5) == 3  # floor(0.8 * 10 / 2.5)
    assert tarama.bellek_isci(2, frames, is_basina=2.5) == 2
    monkeypatch.setattr(tarama, "bos_bellek", lambda: 0.5 * one)
    assert tarama.bellek_isci(8, frames, is_basina=2.5) == 1
    monkeypatch.setattr(tarama, "bos_bellek", lambda: None)
    assert tarama.bellek_isci(4, frames, is_basina=2.5) == 4


def test_memory_ceiling_on_large_synthetic_book() -> None:
    """14k bars x 5 symbols: signals + engine of a position-state exit card stay under the ceiling (tracemalloc peak)."""
    data = yaml.safe_load((SPEC / "A3-002d.yaml").read_text(encoding="utf-8"))
    frames = {f"S{i}": intraday(i, 14_000) for i in range(5)}
    start, end = frames["S0"].index[0], frames["S0"].index[-1]
    tracemalloc.start()
    prepared = tarama.prepare(data, frames, "KRIPTO25", start=start, end=end)
    result = prepared.run(1.0, trusted_inputs=True)
    prepared.runtime_cache.clear()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(result.trades) > 100
    bars = tarama.veri_baytlari(frames)
    assert peak < 3.0 * bars, f"zirve {peak / 2**20:.0f} MB, bar verisi {bars / 2**20:.0f} MB"  # ~2.4x; defensive copies gave ~3.4x
