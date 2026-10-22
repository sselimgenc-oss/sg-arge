"""Known-result tests for every T6b statistical gate."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtests import asama2b
from backtests.run_codex21 import ROWS
from tests.test_tarama import synthetic


def test_max_drawdown_has_known_result() -> None:
    # 1.00 -> 1.10 -> 0.88 -> 0.968, hence the peak-to-trough loss is 20%.
    assert asama2b.max_drawdown(np.array([0.10, -0.20, 0.10])) == pytest.approx(0.20)


def test_block_bootstrap_is_reproducible_and_constant_path_is_known() -> None:
    returns = pd.Series(np.full(40, 0.001))
    first = asama2b.block_bootstrap(returns, repetitions=25, block=20, seed=7)
    second = asama2b.block_bootstrap(returns, repetitions=25, block=20, seed=7)
    np.testing.assert_array_equal(first["mdd"], second["mdd"])
    assert first["mdd_p95"] == pytest.approx(0.0)
    assert first["cagr_p05"] == pytest.approx((1.001**40) ** (252 / 40) - 1)


def test_psr_and_dsr_separate_flat_random_walk_from_trend() -> None:
    flat = np.tile(np.array([-0.01, 0.01]), 300)
    trend = np.tile(np.array([0.001, 0.003, 0.002, 0.004]), 150)
    assert asama2b.probabilistic_sharpe_ratio(flat) == pytest.approx(0.5)
    assert asama2b.deflated_sharpe_ratio(flat, 168) < 0.05
    assert asama2b.deflated_sharpe_ratio(trend, 168) > 0.95
    assert asama2b.deflated_sharpe_ratio(trend, 840) <= asama2b.deflated_sharpe_ratio(trend, 168)


def test_plateau_reports_positive_cells_median_and_edge_without_optimising() -> None:
    cells = [
        ((0.6,), 1.0, -0.1),
        ((0.8,), 1.2, 0.1),
        ((1.0,), 1.3, 0.2),
        ((1.2,), 1.1, 0.1),
        ((1.4,), 2.0, -0.1),
    ]
    result = asama2b.plateau_summary(cells)
    assert result["median_pf"] == pytest.approx(1.2)
    assert result["positive_rate"] == pytest.approx(0.6)
    assert result["best_on_edge"] is True


def test_parameter_source_precedence_and_integer_rounding() -> None:
    card = {
        "parametreler": {"period": 10, "threshold": 2.5, "ignored": "x"},
        "gostergeler": {"sma": {"n": 10}, "rsi": {"n": 14}},
        "giris": "close > sma and rsi > 2.5",
    }
    paths = asama2b._numeric_parameter_paths(card)
    assert paths == [(('parametreler', 'period'), 10.0), (('parametreler', 'threshold'), 2.5)]
    changed = asama2b._mutate_card(card, paths, (0.6, 1.2))
    assert changed["parametreler"]["period"] == 6
    assert changed["parametreler"]["threshold"] == pytest.approx(3.0)
    assert changed["gostergeler"]["sma"]["n"] == 6
    assert changed["giris"] == "close > sma and rsi > 3"
    assert card["parametreler"]["period"] == 10  # source centre is untouched


def _passing_row() -> dict[str, object]:
    return {
        "null_gecti": True,
        "piyasa": "EMTIA",
        "oos_islem": 40,
        "oos_ort_r": 0.1,
        "on_islem": 40,
        "on_ort_r": 0.1,
        "stres_pf_2x": 1.3,
        "stres_net_3x": 0.01,
        "stres_net_gecikme": 0.01,
        "plato_pozitif_oran": 0.6,
        "bootstrap_mdd_p95": 0.14,
    }


def test_decision_gates_known_cases() -> None:
    passing = _passing_row()
    assert asama2b.decide(passing)[0] == "Gecti"
    conditional = {**passing, "on_ort_r": -0.01}
    assert asama2b.decide(conditional)[0] == "Kosullu"
    rejected = {**passing, "stres_pf_2x": 1.19}
    assert asama2b.decide(rejected)[0] == "Reddedildi"


def test_codex_signal_defaults_are_identical_with_explicit_pdf_parameters() -> None:
    """T6b's optional parameters must not alter the T1a/T1b source centre."""
    frame = synthetic(23, periods=400)
    for config in ROWS.values():
        params = {name: value for name, value in config.plato_parametreleri}
        default = config.signal_function(frame, config.market)
        explicit = config.signal_function(frame, config.market, **params)
        pd.testing.assert_frame_equal(default, explicit)


def test_every_codex_row_has_two_signal_not_sizing_plateau_parameters() -> None:
    banned = {"atr_stop_multiple", "risk_per_trade"}
    for config in ROWS.values():
        assert len(config.plato_parametreleri) == 2
        assert not {name for name, _ in config.plato_parametreleri}.intersection(banned)



def test_pit_universe_lifts_survivorship_flag():
    base = {"null_gecti": True, "oos_islem": 100, "oos_ort_r": 0.1, "stres_pf_2x": 1.5,
            "stres_net_3x": 0.1, "stres_net_gecikme": 0.1, "plato_pozitif_oran": 1.0,
            "bootstrap_mdd_p95": 0.1, "on_islem": 50, "on_ort_r": 0.1}
    assert asama2b.decide({**base, "piyasa": "ABD25"})[0] == "Kosullu"
    assert asama2b.decide({**base, "piyasa": "ABD25", "evren": "pit"})[0] == "Gecti"
    assert asama2b.decide({**base, "piyasa": "BIST30", "evren": "pit"})[0] == "Kosullu"


def test_codex_rows_accept_the_fast_null_path() -> None:
    """T17 calls ``run(..., trusted_inputs=True, trades_only=True)`` in the null; Codex rows must give the same trades."""
    config = ROWS["C07"]
    data = {f"S{i}": synthetic(30 + i, periods=1500) for i in range(3)}
    start, end = pd.Timestamp("2012-01-01", tz="UTC"), pd.Timestamp("2030-01-01", tz="UTC")
    prepared = asama2b.prepare_codex(config, data, start, end)
    slow = prepared.run(1.0, signals=prepared.plan.signals).trades
    fast = prepared.run(1.0, signals=prepared.plan.signals, trusted_inputs=True, trades_only=True).trades
    pd.testing.assert_frame_equal(slow.reset_index(drop=True), fast.reset_index(drop=True))
