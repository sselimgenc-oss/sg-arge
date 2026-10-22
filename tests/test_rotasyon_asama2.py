"""T23: rotation cards in stage 2a / 2b / portfolio (null model, plateau, PIT membership)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import asama2a, asama2b, portfoy, tarama
from backtests import rotasyon_asama2 as rot
from data.evren_pit import PITUniverse
from engine import rotasyon
from tests.test_rotasyon import frame, gecis_card, gecis_frames, kesitsel_card, universe, walk

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def card(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


def prepared_kesitsel(**block) -> rot.RotationPrepared:
    data = {f"S{i:02d}": frame(walk(i, 1500), start="2016-01-04") for i in range(12)}
    return tarama.prepare(kesitsel_card(**block), data, "ABD25")


def prepared_gecis() -> rot.RotationPrepared:
    frames = {s: frame(walk(i, 1500, 0.0006, 0.02), start="2016-01-04") for i, s in enumerate(("AAA", "BBB", "CCC"))}
    rot._FIXED_CACHE.clear()  # noqa: SLF001
    rot._FIXED_CACHE[(tuple(rotasyon.needed_symbols(gecis_card())), str(tarama.FIXED_DATA_DIR))] = frames  # noqa: SLF001
    return tarama.prepare(gecis_card(), {}, "ABD25")


# ------------------------------------------------------------------------------------------ null model
def test_selection_null_keeps_calendar_n_filters_and_cost() -> None:
    prepared = prepared_kesitsel(filtre="close > sma50", dengeleme={"tip": "hafta"})
    real, null = prepared.base.weights, prepared.base.null(np.random.default_rng(3))
    assert real.index.equals(null.index) and list(real.columns) == list(null.columns)
    assert real.attrs["karar"].equals(null.attrs["karar"])  # same decision days
    decided = real.attrs["karar"].to_numpy()
    assert (null[~decided].to_numpy() == 0.0).all()
    # the filter is a condition, not a selection: the null never holds a symbol the filter rejects, and never exceeds N
    closes = pd.DataFrame({s: f["close"] for s, f in prepared.frames.items()})
    passing = closes > closes.rolling(50).mean()
    assert not ((null > 0) & ~passing).to_numpy().any()
    assert (null.gt(0).sum(axis=1) <= 3).all() and np.allclose(null.to_numpy()[null.to_numpy() > 0], 1 / 3)
    # real and null never hold more names than eligible ones; the null differs from the real ranking
    assert real.gt(0).sum(axis=1).le(3).all()
    assert not np.allclose(real.to_numpy(), null.to_numpy())
    # cost and execution: run_null is run() on the null weights at the same base cost
    first = prepared.run_null(np.random.default_rng(5))
    second = prepared.run(1.0, weights=prepared.base.null(np.random.default_rng(5)))
    pd.testing.assert_series_equal(first.equity, second.equity)


def test_gecis_null_switches_on_the_real_dates_and_holds_one_leaf() -> None:
    prepared = prepared_gecis()
    real, null = prepared.base.weights, prepared.base.null(np.random.default_rng(1))
    changes = lambda w: np.flatnonzero(~np.isclose(w.diff().abs().sum(axis=1).to_numpy()[1:], 0)) + 1  # noqa: E731
    cash = real.sum(axis=1) < 1e-12
    assert (null.sum(axis=1)[cash] == 0).all() and (null.sum(axis=1)[~cash] == 1.0).all()
    assert set(changes(null)) <= set(changes(real)) | {0}  # a switch of the null only happens on a real switch date
    assert (null.gt(0).sum(axis=1)[~cash] == 1).all()
    other = prepared.base.null(np.random.default_rng(2))
    assert not np.allclose(null.to_numpy(), other.to_numpy())  # random, reproducible per seed
    pd.testing.assert_frame_equal(null, prepared.base.null(np.random.default_rng(1)))


def test_null_distribution_is_reproducible_and_has_cagr() -> None:
    prepared = prepared_kesitsel()
    one, two = rot.null_distribution(prepared, 6, 11), rot.null_distribution(prepared, 6, 11)
    for key in ("pf", "cagr", "count"):
        np.testing.assert_array_equal(one[key], two[key])
    assert len(one["cagr"]) == 6 and np.isfinite(one["cagr"]).all()


def test_stage2_run_has_no_lookahead() -> None:
    data = {f"S{i:02d}": frame(walk(i, 1500), start="2016-01-04") for i in range(12)}
    cut = data["S00"].index[900]
    full = tarama.prepare(kesitsel_card(filtre="close > sma50"), data, "ABD25", start=pd.Timestamp("2017-01-02", tz="UTC"), end=cut)
    short = tarama.prepare(
        kesitsel_card(filtre="close > sma50"), {s: f.loc[:cut] for s, f in data.items()}, "ABD25",
        start=pd.Timestamp("2017-01-02", tz="UTC"), end=cut,
    )
    pd.testing.assert_series_equal(full.run().equity, short.run().equity)
    pd.testing.assert_series_equal(full.run(extra_delay_bars=1).equity, short.run(extra_delay_bars=1).equity)


# ------------------------------------------------------------------------------------------ plateau parameters
def test_parameters_are_listed_and_changed_one_at_a_time() -> None:
    holy = card("O2-025")
    params = rotasyon.parametreler(holy)
    labels = [p.etiket for p in params]
    assert any("tqqq_sma200.n" in label for label in labels) and any("#0:79" in label for label in labels)
    threshold = next(p for p in params if "#0:79" in p.etiket)
    changed = threshold.uygula(holy, 1.2)
    assert changed["rotasyon"]["agac"]["ise"]["eger"] == "tqqq_rsi10 > 95"
    assert holy["rotasyon"]["agac"]["ise"]["eger"] == "tqqq_rsi10 > 79"  # the card itself is untouched
    window = next(p for p in params if p.etiket == "gostergeler.tqqq_sma200.n")
    assert window.uygula(holy, 0.8)["gostergeler"]["tqqq_sma200"]["n"] == 160
    for param in params:  # every other node of the tree stays the same
        variant = param.uygula(holy, 0.8)
        assert sum(a != b for a, b in zip(yaml.safe_dump(variant).splitlines(), yaml.safe_dump(holy).splitlines())) <= 2
    ranking = card("M020a")
    n_share = next(p for p in rotasyon.parametreler(ranking) if p.etiket == "rotasyon.n_oran")
    assert n_share.uygula(ranking, 1.2)["rotasyon"]["n_oran"] == pytest.approx(0.024)
    lag = next(p for p in rotasyon.parametreler(card("A6-004")) if p.etiket.endswith("#1:21"))
    assert "sma100[25]" in lag.uygula(card("A6-004"), 1.2)["rotasyon"]["giris"]


def test_plateau_cells_report_centre_and_both_sides() -> None:
    prepared = prepared_kesitsel()
    cells = rot.plateau_cells(prepared, {s: f for s, f in prepared.frames.items()}, None, None)
    assert cells[0][0] == "merkez" and len(cells) == 1 + 2 * len(rotasyon.parametreler(prepared.card))
    assert {c[1] for c in cells[1:]} == {0.8, 1.2}


# ------------------------------------------------------------------------------------------ PIT membership
def test_pit_membership_excludes_symbols_that_left_the_index() -> None:
    data = {f"S{i:02d}": frame(walk(i, 1500), start="2016-01-04") for i in range(12)}
    always = frozenset(data) - {"S03", "S04"}
    universe_ = PITUniverse(abd=((2016, frozenset(data)), (2020, always)))
    mask = tarama.pit_membership(universe_, "ABD25", list(data), rotasyon._calendar(data))  # noqa: SLF001
    assert mask.loc["2019-12-31", "S03"] and not mask.loc["2020-06-01", "S03"]
    block = {"skor": "roc5", "n": 12}  # N = universe: without PIT every eligible symbol is held
    base = rotasyon.agirliklar(kesitsel_card(**block), data)
    pit = rotasyon.agirliklar(kesitsel_card(**block), data, membership=mask)
    after = pit.index >= pd.Timestamp("2020-01-01", tz="UTC")
    assert (base.loc[after, "S03"] > 0).any()
    assert not (pit.loc[after, ["S03", "S04"]] > 0).to_numpy().any()
    assert (pit.loc[~after, "S03"] > 0).any()  # still a member before 2020
    prepared = tarama.prepare(kesitsel_card(**block), data, "ABD25", pit_universe=universe_)
    assert not (prepared.base.weights.loc[after, "S03"] > 0).any()
    assert not (prepared.base.null(np.random.default_rng(0)).loc[after, "S03"] > 0).any()  # the null respects membership too


# ------------------------------------------------------------------------------------------ stage 2a / 2b / portfolio
def test_stage_2a_rotation_row_uses_pf_and_cagr(monkeypatch: pytest.MonkeyPatch) -> None:
    data = {f"S{i:02d}": frame(walk(i, 2400), start="2014-06-02") for i in range(12)}
    monkeypatch.setitem(asama2a._STATE, "data", {("1D", "ABD25"): data})  # noqa: SLF001
    for key, value in (("benchmarks", {}), ("hashes", {("1D", "ABD25"): "h"}), ("git_sha", "x"), ("tl_rows", {}), ("usd", {})):
        monkeypatch.setitem(asama2a._STATE, key, value)  # noqa: SLF001
    row = asama2a.evaluate_pair({"card": kesitsel_card(dengeleme={"tip": "hafta"}) | {"id": "T", "tf": "1D"}, "market": "ABD25", "reps": 12, "reps_high": 12})
    assert row["metrik"] == "PF+CAGR" and row["null_tekrar"] == 12
    assert row["karar"] in ("Gecti (null)", "Reddedildi (piyasa betasi)"), row["neden"]
    assert np.isfinite(row["ort_r"]) and np.isfinite(row["null_ortr_p95"]) and np.isfinite(row["null_pf_p95"])
    assert row["karar"] == ("Gecti (null)" if row["PF_1x"] > row["null_pf_p95"] and row["ort_r"] > row["null_ortr_p95"] else "Reddedildi (piyasa betasi)")


def test_daily_cards_keep_their_stage_2a_metric(monkeypatch: pytest.MonkeyPatch) -> None:
    data = {f"S{i}": frame(walk(i, 2400), start="2014-06-02") for i in range(4)}
    monkeypatch.setitem(asama2a._STATE, "data", {("1D", "ABD25"): data})  # noqa: SLF001
    for key, value in (("benchmarks", {}), ("hashes", {("1D", "ABD25"): "h"}), ("git_sha", "x"), ("tl_rows", {}), ("usd", {})):
        monkeypatch.setitem(asama2a._STATE, key, value)  # noqa: SLF001
    row = asama2a.evaluate_pair({"card": card("A3-007"), "market": "ABD25", "reps": 10, "reps_high": 10})
    assert row["metrik"] == "PF+ortR"


def test_stage_2b_rotation_row(tmp_path: Path) -> None:
    data = {f"S{i:02d}": frame(walk(i, 2900, 0.0004, 0.015), start="2014-06-02") for i in range(12)}
    weekly = kesitsel_card(dengeleme={"tip": "hafta"}) | {"id": "T", "tf": "1D"}
    row = asama2b.evaluate_card(
        weekly, "ABD25", data, None,
        pd.Series({"null_tekrar": 10, "null_pf_p95": 1.0, "null_ortr_p95": 0.0, "p_pf": 0.01, "p_ortr": 0.01}),
        results_dir=tmp_path, bootstrap_reps=30, data_hash="h",
    )
    assert row["metrik"] == "PF+CAGR" and row["plato_hucre"] == 1 + 2 * len(rotasyon.parametreler(weekly))
    assert row["karar"] in ("Gecti", "Kosullu", "Reddedildi")
    for key in ("oos_ort_r", "stres_pf_2x", "stres_net_3x", "stres_net_gecikme", "bootstrap_mdd_p95", "dsr_5N", "plato_pozitif_oran"):
        assert np.isfinite(row[key]), key
    assert row["on_islem"] > 0  # 2015-2019 pre-period exists in the synthetic data


def test_stage_2b_gecis_without_early_data_is_conditional_not_a_crash(tmp_path: Path) -> None:
    frames = {s: frame(walk(i, 1900, 0.0005, 0.02), start="2019-06-03") for i, s in enumerate(("AAA", "BBB", "CCC"))}
    rot._FIXED_CACHE.clear()  # noqa: SLF001
    rot._FIXED_CACHE[(tuple(rotasyon.needed_symbols(gecis_card())), str(tarama.FIXED_DATA_DIR))] = frames  # noqa: SLF001
    row = asama2b.evaluate_card(
        gecis_card() | {"id": "G", "tf": "1D"}, "ABD25", {}, None, pd.Series({"null_tekrar": 10}), results_dir=tmp_path, bootstrap_reps=20, data_hash="h",
    )
    assert row["evren"] == "enstruman" and row["on_islem"] == 0 and "survivorship" not in row["neden"]


def test_decide_unchanged_for_daily_rows_and_conditional_for_missing_pre_period() -> None:
    good = dict(
        null_gecti=True, oos_islem=40, oos_ort_r=0.1, stres_pf_2x=1.5, stres_net_3x=0.1, stres_net_gecikme=0.1,
        plato_pozitif_oran=0.8, bootstrap_mdd_p95=0.1, on_islem=30, on_ort_r=0.1, piyasa="KRIPTO25",
    )
    assert asama2b.decide(dict(good)) == ("Gecti", "paper kapilari gecti; DSR canli oncesi degerlendirilmeli")
    assert asama2b.decide(good | {"piyasa": "ABD25"})[0] == "Kosullu"  # survivorship note for a fixed universe
    assert asama2b.decide(good | {"piyasa": "ABD25", "evren": "enstruman"})[0] == "Gecti"
    assert asama2b.decide(good | {"on_veri_yok": True, "on_islem": 0}) == ("Kosullu", "on donem Dogrulanamaz (veri yok)")


def test_portfolio_accepts_books_without_trade_risk() -> None:
    prepared = prepared_kesitsel()
    result = prepared.run()
    risk = portfoy.open_risk_series(result)
    assert np.isfinite(risk).all() and (risk == 0).all()
    assert portfoy.daily_returns(result).notna().all()
