"""Known-result tests for every T6b statistical gate."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import asama2b, tarama
from backtests.run_codex21 import ROWS
from engine.portfolio import BacktestResult
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


def test_intraday_plateau_varies_every_parameter_twenty_percent_one_at_a_time() -> None:
    assert asama2b._plateau_factor_cells(3, intraday=True) == [
        (1.0, 1.0, 1.0),
        (0.8, 1.0, 1.0), (1.2, 1.0, 1.0),
        (1.0, 0.8, 1.0), (1.0, 1.2, 1.0),
        (1.0, 1.0, 0.8), (1.0, 1.0, 1.2),
    ]
    assert len(asama2b._plateau_factor_cells(2, intraday=False)) == 25


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


def test_intraday_equity_is_sampled_once_per_utc_day_for_bootstrap() -> None:
    index = pd.date_range("2024-01-01", periods=72, freq="1h", tz="UTC")
    equity = pd.Series(100 + np.arange(72) + 5 * np.sin(np.arange(72)), index=index)
    result = BacktestResult(100.0, equity, pd.Series(0.0, index=index), pd.DataFrame(), 0)
    returns = asama2b._validation_returns(result, daily_equity=True)
    expected = equity.resample("1D").last().pct_change().dropna()
    pd.testing.assert_series_equal(returns, expected)
    assert len(returns) == 2


def test_intraday_candidate_filter_and_daily_result_regression(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    results = tmp_path / "results"
    cards.mkdir(); results.mkdir()
    for card_id, tf in (("I5", "5m"), ("D1", "1D")):
        (cards / f"{card_id}.yaml").write_text(yaml.safe_dump({"id": card_id, "tf": tf}), encoding="utf-8")
    pd.DataFrame([
        {"id": "I5", "piyasa": "KRIPTO25", "tf": "5m", "karar": "Gecti (null)"},
        {"id": "D1", "piyasa": "ABD25", "tf": "1D", "karar": "Gecti (null)"},
    ]).to_csv(results / "asama2a.csv", index=False)
    pd.DataFrame({"id": ["I5", "I5", "D1"], "piyasa": ["KRIPTO25", "ABD25", "ABD25"],
                  "tf": ["5m", "5m", "1D"]}).to_csv(results / "tarama.csv", index=False)
    chosen = asama2b.load_card_candidates(results, cards, None, {"5m"})
    assert [(card["id"], market) for card, market, _ in chosen] == [("I5", "KRIPTO25")]
    assert asama2b.trial_count({"deneme_sayisi_kaynakta": 99}, results, intraday=True) == 2

    existing = pd.read_csv(Path(__file__).resolve().parents[1] / "results" / "asama2b.csv")
    fresh = pd.DataFrame([{**{column: np.nan for column in asama2b.OUTPUT_COLUMNS}, "id": "I5", "piyasa": "KRIPTO25"}])
    merged = asama2b.merge_selected_results(existing, fresh, {"I5"})
    pd.testing.assert_frame_equal(merged.iloc[:len(existing)].reset_index(drop=True), existing, check_dtype=False)
    pit = pd.read_csv(Path(__file__).resolve().parents[1] / "results" / "asama2b_pit.csv")
    pd.testing.assert_frame_equal(pit, pd.read_csv(Path(__file__).resolve().parents[1] / "results" / "asama2b_pit.csv"))


def test_a6_019_utc_signal_fills_at_22_and_exits_at_midnight() -> None:
    root = Path(__file__).resolve().parents[1]
    card = yaml.safe_load((root / "docs/spec/A6-019.yaml").read_text(encoding="utf-8"))
    index = pd.date_range("2020-01-01", periods=96, freq="1h", tz="UTC")
    close = 100 + np.arange(len(index)) * 0.01
    frame = pd.DataFrame(
        {"open": close, "high": close + 0.1, "low": close - 0.1, "close": close, "volume": 1000.0},
        index=index,
    )
    prepared = tarama.prepare(card, {"BTCUSDT": frame}, "KRIPTO25", start=index[0], end=index[-1])
    result = prepared.run()
    assert prepared.plan.stop_eklendi is True and len(result.trades) >= 3
    assert set(result.trades["entry_date"].dt.hour) == {22}
    completed = result.trades[result.trades["exit_reason"] != "end_of_test"]
    assert set(completed["exit_date"].dt.hour) == {0}


def test_intraday_crypto_without_any_2017_2019_symbol_is_unverifiable(tmp_path: Path) -> None:
    card = {
        "id": "NOPRE", "tf": "1H", "gostergeler": {}, "giris": "saat_utc() == 0", "cikis": None,
        "stop": {"tip": "yuzde", "deger": 20}, "hedef": None, "zaman_stop": {"bar": 2},
        "parametreler": {}, "deneme_sayisi_kaynakta": 1,
    }
    indexes = [pd.date_range("2020-01-01", periods=240, freq="1h", tz="UTC"),
               pd.date_range("2024-10-01", periods=120, freq="1h", tz="UTC")]
    index = indexes[0].append(indexes[1])
    close = 100 + np.arange(len(index)) * 0.01
    frame = pd.DataFrame({"open": close, "high": close + 0.1, "low": close - 0.1,
                          "close": close, "volume": 1000.0}, index=index)
    row = asama2b.evaluate_card(
        card, "KRIPTO25", {"BTCUSDT": frame}, None, pd.Series(), results_dir=tmp_path,
        bootstrap_reps=2, data_hash="x", workers=1,
    )
    assert row["karar"] == "Dogrulanamaz"
    assert row["neden"] == "on donem verisi yok (2017-2019)"


def test_intraday_stage2b_end_to_end_preserves_existing_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cards = tmp_path / "cards"
    results = tmp_path / "results"
    archive = tmp_path / "data/hourly"
    cards.mkdir(); results.mkdir(); archive.mkdir(parents=True)
    card = {
        "id": "IH", "ad": "intraday synthetic", "kart_yazari": "test", "tarz": "day", "tf": "1H",
        "mtf": None, "gostergeler": {}, "ozel_kod": False, "giris": "saat_utc() == 0", "cikis": None,
        "stop": {"tip": "yuzde", "deger": 20}, "hedef": None, "zaman_stop": {"bar": 2},
        "stop_eklendi": False, "parametreler": {"hold_hours": 2}, "deneme_sayisi_kaynakta": 1,
        "spec_durumu": "tam", "belirsiz": [],
    }
    (cards / "IH.yaml").write_text(yaml.safe_dump(card, sort_keys=False), encoding="utf-8")
    pd.DataFrame([{
        "id": "IH", "piyasa": "KRIPTO25", "tf": "1H", "karar": "Gecti (null)",
        "null_tekrar": 200, "null_pf_p95": 1.1, "null_ortr_p95": 0.1, "p_pf": 0.01, "p_ortr": 0.01,
    }]).to_csv(results / "asama2a.csv", index=False)
    sentinel = {column: np.nan for column in asama2b.OUTPUT_COLUMNS}
    sentinel.update(id="DAILY", piyasa="ABD25", karar="Gecti", neden="koru")
    pd.DataFrame([sentinel]).to_csv(results / "asama2b.csv", index=False)
    pit_path = results / "asama2b_pit.csv"
    pit_path.write_text("id,piyasa,karar\nPIT,ABD25,Gecti\n", encoding="utf-8")
    pit_before = pit_path.read_bytes()

    pieces = []
    for start, periods in (("2017-01-01", 240), ("2020-01-01", 720), ("2024-10-01", 240)):
        idx = pd.date_range(start, periods=periods, freq="1h", tz="UTC")
        close = 100 + np.arange(periods) * 0.01
        pieces.append(pd.DataFrame({"open": close, "high": close + 0.1, "low": close - 0.1,
                                    "close": close, "volume": 1000.0}, index=idx))
    pd.concat(pieces).to_parquet(archive / "BTCUSDT.parquet")
    monkeypatch.setattr("backtests.run_codex21._symbols_for_market", lambda market, evren="sabit": ["BTCUSDT"])
    monkeypatch.setattr(asama2b, "_git_sha", lambda: "test-sha")
    monkeypatch.setattr(asama2b, "parse_args", lambda: argparse.Namespace(
        kartlar=cards, data_dir=tmp_path / "data/daily", veri_kok=tmp_path / "data", results_dir=results,
        tf="1H", null_tekrar=2, null_tekrar_yuksek=3, bootstrap_tekrar=5, kart_ids="", codex_ids="",
        evren="sabit", isci=2,
    ))
    assert asama2b.main() == 0
    output = pd.read_csv(results / "asama2b.csv")
    assert output["id"].tolist() == ["DAILY", "IH"]
    assert output.loc[0, "neden"] == "koru"
    assert output.loc[1, "karar"] in ("Gecti", "Kosullu", "Reddedildi")
    assert output.loc[1, "plato_hucre"] == 3
    assert pit_path.read_bytes() == pit_before
