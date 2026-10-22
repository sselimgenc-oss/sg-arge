"""Stage 2a: USD conversion and the random-entry null model."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import asama2a, tarama
from tests.test_tarama import synthetic

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def test_usd_conversion_divides_prices_by_same_day_rate_and_forward_fills() -> None:
    data = {"X": synthetic(1, periods=30)}
    rate = pd.DataFrame({"close": 10.0 + np.arange(30) * 0.1}, index=data["X"].index)
    rate = rate.drop(rate.index[5])  # FX holiday: the previous rate carries over
    out = asama2a.usd_frames(data, rate)["X"]
    day = data["X"].index[10]
    assert out.loc[day, "close"] == pytest.approx(data["X"].loc[day, "close"] / rate.loc[day, "close"])
    holiday = data["X"].index[5]
    assert out.loc[holiday, "open"] == pytest.approx(data["X"].loc[holiday, "open"] / rate.loc[data["X"].index[4], "close"])
    assert (out["volume"] == data["X"]["volume"]).all()


def test_trade_stats_and_p_value() -> None:
    trades = pd.DataFrame({"net_pnl": [10.0, -5.0, 5.0], "r_multiple": [2.0, -1.0, 1.0]})
    pf, mean_r, count = asama2a.trade_stats(trades)
    assert pf == pytest.approx(3.0) and mean_r == pytest.approx(2 / 3) and count == 3
    assert asama2a.trade_stats(pd.DataFrame({"net_pnl": [1.0], "r_multiple": [1.0]}))[0] == asama2a.PF_CAP
    assert np.isnan(asama2a.trade_stats(pd.DataFrame(columns=["net_pnl", "r_multiple"]))[0])
    null = np.array([1.0, 2.0, 3.0, np.nan])
    assert asama2a.p_value(2.5, null) == pytest.approx((1 + 1) / (1 + 3))
    assert asama2a.p_value(0.0, null) == pytest.approx(1.0)


def _prepared(card_id: str = "A3-007"):
    card = yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))
    data = {f"S{i}": synthetic(i, periods=2800) for i in range(4)}
    return tarama.prepare(card, data, "ABD25")


def test_random_entries_only_inside_period_and_count_per_symbol() -> None:
    prepared = _prepared()
    rng = np.random.default_rng(7)
    signals = asama2a.random_entry_signals(prepared, {"S0": 10, "S1": 3}, 1.0, rng)
    assert signals["S0"]["entry"].sum() == 10 and signals["S1"]["entry"].sum() == 3
    assert signals["S2"]["entry"].sum() == 0 and signals["S3"]["entry"].sum() == 0
    chosen = signals["S0"].index[signals["S0"]["entry"].to_numpy()]
    assert ((chosen >= prepared.start) & (chosen <= prepared.end)).all()
    # exits and stop columns are the card's own, untouched
    pd.testing.assert_series_equal(signals["S0"]["exit"], prepared.plan.signals["S0"]["exit"])


def test_null_distribution_is_reproducible_and_matches_trade_count() -> None:
    prepared = _prepared()
    real = prepared.run(1.0).trades
    assert len(real) > 30
    first = asama2a.null_distribution(prepared, real, reps=6, seed=11)
    second = asama2a.null_distribution(prepared, real, reps=6, seed=11)
    np.testing.assert_array_equal(first["pf"], second["pf"])
    assert abs(first["count"].mean() - len(real)) / len(real) < 0.25
    assert np.isfinite(first["hold"]).all()

    # Regression: the accelerated trade-only path must retain the original daily
    # RNG stream and produce byte-for-byte identical null observations.
    rng = np.random.default_rng(11)
    per_symbol = real["symbol"].value_counts().to_dict()
    factor = 1.0

    def reference_one():
        signals = asama2a.random_entry_signals(prepared, per_symbol, factor, rng)
        return prepared.run(1.0, signals=signals).trades

    for _ in range(4):
        counts = [len(reference_one()) for _ in range(asama2a.CALIBRATION_REPS)]
        mean_count = max(float(np.mean(counts)), 1.0)
        if abs(mean_count - len(real)) / len(real) <= 0.05:
            break
        factor = min(factor * len(real) / mean_count, asama2a.MAX_ENTRY_FACTOR)
    expected = [asama2a.trade_stats(reference_one()) for _ in range(6)]
    np.testing.assert_array_equal(first["pf"], [item[0] for item in expected])
    np.testing.assert_array_equal(first["ortr"], [item[1] for item in expected])
    np.testing.assert_array_equal(first["count"], [item[2] for item in expected])


def test_trades_only_fast_path_preserves_the_complete_trade_ledger() -> None:
    prepared = _prepared()
    signals = asama2a.random_entry_signals(
        prepared, {symbol: 12 for symbol in prepared.frames}, 1.0, np.random.default_rng(19)
    )
    normal = prepared.run(1.0, signals=signals).trades
    fast = prepared.run(1.0, signals=signals, trusted_inputs=True, trades_only=True).trades
    pd.testing.assert_frame_equal(fast, normal)


def test_evaluate_pair_rejects_a_pure_market_beta_card_and_is_deterministic() -> None:
    card = yaml.safe_load((SPEC / "A3-007.yaml").read_text(encoding="utf-8"))
    data = {f"S{i}": synthetic(i, periods=2800) for i in range(4)}
    key = ("1D", "ABD25")
    asama2a._STATE.update(data={key: data}, usd={}, benchmarks={}, hashes={key: "h"}, tl_rows={}, git_sha="x")
    task = {"card": card, "market": "ABD25", "reps": 8, "reps_high": 12}
    row_a, row_b = asama2a.evaluate_pair(task), asama2a.evaluate_pair(task)
    assert row_a["karar"] in ("Gecti (null)", "Reddedildi (piyasa betasi)")
    assert row_a["null_pf_p95"] == row_b["null_pf_p95"] and row_a["p_pf"] == row_b["p_pf"]


def test_intraday_candidates_are_selected_but_bist_1h_stays_unverifiable(tmp_path: Path) -> None:
    cards = tmp_path / "cards"
    results = tmp_path / "results"
    cards.mkdir(); results.mkdir()
    for card_id, tf in (("I5", "5m"), ("H1", "1H"), ("D1", "1D")):
        (cards / f"{card_id}.yaml").write_text(yaml.safe_dump({"id": card_id, "tf": tf}), encoding="utf-8")
    pd.DataFrame(
        [
            {"id": "I5", "piyasa": "KRIPTO25", "tf": "5m", "asama2_aday": True},
            {"id": "H1", "piyasa": "BIST30", "tf": "1H", "asama2_aday": True},
            {"id": "H1", "piyasa": "ABD25", "tf": "1H", "asama2_aday": True},
            {"id": "D1", "piyasa": "ABD25", "tf": "1D", "asama2_aday": True},
        ]
    ).to_csv(results / "tarama.csv", index=False)
    selected = asama2a.load_candidates(results, cards, None, {"1H", "5m"})
    assert [(task["card"]["id"], task["market"]) for task in selected] == [("I5", "KRIPTO25"), ("H1", "ABD25")]


def test_intraday_merge_preserves_existing_daily_rows_exactly() -> None:
    existing = pd.read_csv(Path(__file__).resolve().parents[1] / "results" / "asama2a.csv")
    daily_before = existing[existing["tf"].isin(asama2a.tarama.DAILY_TFS)].reset_index(drop=True)
    fresh = pd.DataFrame([{**{column: np.nan for column in asama2a.OUTPUT_COLUMNS}, "id": "I5", "piyasa": "KRIPTO25", "tf": "5m"}])
    merged = asama2a.merge_selected_results(existing, fresh, {"5m"})
    daily_after = merged[merged["tf"].isin(asama2a.tarama.DAILY_TFS)].reset_index(drop=True)
    pd.testing.assert_frame_equal(daily_after, daily_before, check_dtype=False)


def test_intraday_end_to_end_reads_tarama_archive_and_writes_null_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cards = tmp_path / "cards"
    results = tmp_path / "results"
    data_root = tmp_path / "data"
    archive = data_root / "5m"
    cards.mkdir(); results.mkdir(); archive.mkdir(parents=True)
    item = {
        "id": "I5", "ad": "synthetic intraday", "kart_yazari": "test", "tarz": "day", "tf": "5m",
        "mtf": None, "gostergeler": {}, "ozel_kod": False, "giris": "close > 0", "cikis": None,
        "stop": {"tip": "yuzde", "deger": 20}, "hedef": None, "zaman_stop": {"bar": 2},
        "stop_eklendi": False, "parametreler": {}, "spec_durumu": "dakikalik", "belirsiz": [],
    }
    (cards / "I5.yaml").write_text(yaml.safe_dump(item, sort_keys=False), encoding="utf-8")
    pd.DataFrame(
        [{"id": "I5", "piyasa": "KRIPTO25", "tf": "5m", "asama2_aday": True, "PF_1x": 1.2, "net_1x": 0.1}]
    ).to_csv(results / "tarama.csv", index=False)
    rng = np.random.default_rng(4)
    index = pd.date_range("2020-01-01", periods=360, freq="5min", tz="UTC")
    close = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.002, len(index))))
    frame = pd.DataFrame(
        {"open": close, "high": close * 1.002, "low": close * 0.998, "close": close, "volume": 1000.0},
        index=index,
    )
    frame.to_parquet(archive / "BTCUSDT.parquet")
    monkeypatch.setattr("backtests.run_codex21._symbols_for_market", lambda market, evren="sabit": ["BTCUSDT"])
    monkeypatch.setattr(asama2a, "_git_sha", lambda: "test-sha")
    monkeypatch.setattr(
        asama2a,
        "parse_args",
        lambda: argparse.Namespace(
            kartlar=cards, data_dir=data_root / "daily", veri_kok=data_root, results_dir=results,
            tf="5m", tekrar=3, tekrar_yuksek=4, kart_ids="", isci=1,
        ),
    )
    assert asama2a.main() == 0
    output = pd.read_csv(results / "asama2a.csv")
    assert len(output) == 1
    row = output.iloc[0]
    assert row["id"] == "I5" and row["tf"] == "5m" and row["null_tekrar"] == 3
    assert row["islem"] >= 5 and row["karar"] in ("Gecti (null)", "Reddedildi (piyasa betasi)")
