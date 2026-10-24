"""U4 runner and funnel contracts before the four U4 cards are merged."""

from __future__ import annotations

import pandas as pd
import pytest

from backtests import u4, u4_huni


def fake_card(card_id: str, _directory=None) -> dict:
    return {"id": card_id, "tf": "1D"}


def test_fixed_preregistered_variants_are_four_by_four(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(u4, "load_card", fake_card)
    items = u4.all_variants()
    assert u4.deneme_sayisi(items) == 16
    assert {(market, card["tf"]) for _variant, card, market in items} == set(u4.ARMS)
    assert {card["id"] for _variant, card, _market in items} == set(u4.CARD_IDS)


def test_locked_period_has_no_runner_escape_hatch() -> None:
    with pytest.raises(PermissionError):
        u4.lock_check(pd.Timestamp("2025-10-01", tz="UTC"))


def test_runner_writes_only_summaries_on_synthetic_stub(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    item = ("U4-H1:KRIPTO25:4H", fake_card("U4-H1"), "KRIPTO25")
    item[1]["tf"] = "4H"
    monkeypatch.setattr(u4, "all_variants", lambda: [item])
    monkeypatch.setattr(u4, "load_data", lambda *_args: {"BTCUSDT": pd.DataFrame({"close": [1]})})
    monkeypatch.setattr(u4, "run_variant", lambda *_args: ({"varyant": item[0], "kart": "U4-H1", "piyasa": "KRIPTO25", "tf": "4H", "donem": "IS", "islem": 31, "PF_1x": 1.1, "PF_2x": 1.0, "PF_3x": .9, "net_1x": .1, "net_2x": .05, "net_3x": .01, "ortR": .1, "mdd": .1}, pd.DataFrame()))
    assert u4.main(["--donem", "IS", "--veri-kok", str(tmp_path), "--results-dir", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "ozet_IS.csv").exists()
    assert not list((tmp_path / "out").glob("islemler_*.csv"))


def _passing(**changes) -> dict:
    row = {"is_islem": 60, "is_PF": 1.1, "null_gecti": True, "oos_ortR": .2, "oos_PF_2x": 1.3, "oos_net_3x": .01,
           "net_gecikme": .01, "mdd_p95": .1, "dsr": .96, "piyasa": "KRIPTO25", "kardes_oran": .625,
           "en_buyuk_kar_payi": .3, "en_iyi_ay_haric_pf": 1.1, "on_net": float("nan")}
    row.update(changes)
    return row


def test_funnel_gates_and_preperiod_condition() -> None:
    assert u4_huni.decide(_passing())[0] == "Gecti"
    assert u4_huni.decide(_passing(oos_PF_2x=1.19))[0] == "Reddedildi"
    assert u4_huni.decide(_passing(piyasa="ABD25", on_net=-.01))[0] == "Kosullu"
    assert u4_huni.TRIALS == 16


def test_funnel_output_has_one_row_per_fixed_variant(tmp_path) -> None:
    rows = [{"varyant": f"U4-H{i}:KRIPTO25:4H", "kart": f"U4-H{i}", "piyasa": "KRIPTO25", "tf": "4H", **_passing(), "karar": "Gecti", "neden": "ok"} for i in range(1, 5)]
    table = pd.DataFrame(rows).reindex(columns=u4_huni.COLUMNS)
    u4_huni.write_outputs(table, tmp_path)
    assert len(pd.read_csv(tmp_path / "huni_ozet.csv")) == 4
    assert (tmp_path / "huni_ozet.md").read_text(encoding="utf-8").startswith("# U4 huni ozeti")


def test_crypto_4h_arm_reaches_the_engine_with_real_card_and_hourly_archive(tmp_path) -> None:
    # PR #171: load_data resampled 1H to 4H and tarama.prepare resampled again -> "donemde veri yok". End-to-end guard.
    index = pd.date_range("2017-06-01", "2018-06-30 23:00", freq="h", tz="UTC")
    steps = pd.Series(range(len(index)), index=index, dtype=float)
    close = 100 + (steps % 500) * 0.05 + steps * 0.001
    frame = pd.DataFrame({"open": close, "high": close + 0.5, "low": close - 0.5, "close": close, "volume": 1.0}, index=index)
    (tmp_path / "hourly").mkdir()
    frame.to_parquet(tmp_path / "hourly" / "BTCUSDT.parquet")
    data = u4.load_data(tmp_path, "KRIPTO25", "4H")
    assert data["BTCUSDT"].index.equals(frame.index)  # raw 1H; the card's 4H is built once, inside tarama.prepare
    card = dict(u4.load_card("U4-H1"), tf="4H")
    prepared = u4.tarama.prepare(card, data, "KRIPTO25", start=u4.PERIODS["IS"][0], end=u4.PERIODS["IS"][1], kilit=True)
    bars = next(iter(prepared.plan.signals.values()))
    assert len(bars) > 0 and (bars.index.hour % 4 == 0).all()
