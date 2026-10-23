"""U1d: backtests/u1_huni.py funnel on synthetic data (docs/GOREV_U1.md)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtests import u1, u1_huni
from tests.test_u1 import crypto


def passing_row(**overrides) -> dict:
    row = {
        "null_gecti": True, "oos_islem": 80, "oos_ortR": 0.2, "oos_PF_2x": 1.4, "oos_net_3x": 0.05, "net_gecikme": 0.04,
        "mdd_p95": 0.08, "kardes_oran": 0.75, "kardes_gecen": "6/8", "en_buyuk_kar_payi": 0.2, "en_iyi_ay_haric_pf": 1.3,
    }
    row.update(overrides)
    return row


def test_decision_all_gates_pass():
    assert u1_huni.decide(passing_row())[0] == "Gecti"


@pytest.mark.parametrize(("change", "word"), [
    ({"null_gecti": False}, "null"), ({"oos_ortR": -0.1}, "OOS ortR"), ({"oos_PF_2x": 1.1}, "2x PF"),
    ({"oos_net_3x": -0.01}, "3x net"), ({"net_gecikme": 0.0}, "+1 bar"), ({"mdd_p95": 0.16}, "MDD95"),
    ({"mdd_p95": float("nan")}, "MDD95"),
])
def test_funnel_gate_failures_reject(change, word):
    decision, reason = u1_huni.decide(passing_row(**change))
    assert decision == "Reddedildi" and word in reason


@pytest.mark.parametrize(("change", "word"), [
    ({"kardes_oran": 0.5, "kardes_gecen": "4/8"}, "kardes"), ({"en_buyuk_kar_payi": 0.4}, "kar payi"),
    ({"en_iyi_ay_haric_pf": 0.95}, "en iyi ay"), ({"oos_islem": 20}, "ornek"),
])
def test_sibling_gate_failures_are_conditional(change, word):
    decision, reason = u1_huni.decide(passing_row(**change))
    assert decision == "Kosullu" and word in reason


def test_sibling_threshold_is_sixty_percent_of_eight():
    assert u1_huni.decide(passing_row(kardes_oran=5 / 8, kardes_gecen="5/8"))[0] == "Gecti"
    assert u1_huni.decide(passing_row(kardes_oran=4 / 8, kardes_gecen="4/8"))[0] == "Kosullu"


def test_trials_add_the_source_count_for_hat0_only():
    assert u1_huni.trials_for({"id": "T8-07", "deneme_sayisi_kaynakta": 256}) == 14 + 256
    assert u1_huni.trials_for({"id": "V2B", "deneme_sayisi_kaynakta": 3}) == 14 + 3
    assert u1_huni.trials_for({"id": "U1-H2-A", "deneme_sayisi_kaynakta": 4}) == 14  # its grid is already inside the 14


def make_archive(root, folders, days=170):
    for folder, minutes in folders:
        (root / folder).mkdir(parents=True)
        for k, symbol in enumerate(u1.CORE[:4] + u1.SIBLINGS[:4]):
            crypto(minutes, days, k).to_parquet(root / folder / f"{symbol}.parquet")


def test_funnel_end_to_end_on_synthetic_data(tmp_path, monkeypatch):
    root = tmp_path / "data"
    make_archive(root, (("15m", 15), ("hourly", 60)))
    monkeypatch.setitem(u1.PERIODS, "IS", (pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-04-15", tz="UTC")))
    monkeypatch.setitem(u1.PERIODS, "OOS", (pd.Timestamp("2024-04-16", tz="UTC"), pd.Timestamp("2024-06-15", tz="UTC")))
    out = tmp_path / "res"
    assert u1_huni.main(["--hat", "0,2", "--kart-ids", "U1-H2-A,V2B", "--tf", "15m,1H", "--tekrar", "12", "--tekrar-yuksek", "12",
                         "--bootstrap-tekrar", "30", "--isci", "1", "--veri-kok", str(root), "--results-dir", str(out)]) == 0
    table = pd.read_csv(out / "huni_ozet.csv")
    assert list(table.columns) == u1_huni.COLUMNS
    assert set(table["kart"]) == {"U1-H2-A", "V2B"} and len(table) == 3  # the 15m grid points of U1-H2-A (R = 3, 5 ATR) + V2B
    assert set(table["karar"]) <= {"Gecti", "Kosullu", "Reddedildi"}, table[["varyant", "karar", "neden"]]
    assert table["is_islem"].gt(0).all() and table["oos_islem"].gt(0).all()
    assert table["dsr_deneme"].tolist().count(14 + 3) == 1  # V2B carries its source trial count
    assert (out / "huni_ozet.md").read_text(encoding="utf-8").startswith("# U1 huni ozeti")
    assert list(out.glob("kardes_*.md")) and list(out.glob("islemler_*_OOS.csv"))
    # the sibling report reads the OOS csv the funnel wrote
    first = sorted(out.glob("islemler_*_OOS.csv"))[0]
    assert {"symbol", "net_pnl", "exit_date"} <= set(pd.read_csv(first).columns)


def test_locked_period_cannot_be_opened_by_the_funnel(tmp_path, monkeypatch):
    root = tmp_path / "data"
    make_archive(root, (("15m", 15),), days=60)
    monkeypatch.setitem(u1.PERIODS, "OOS", (pd.Timestamp("2025-10-01", tz="UTC"), pd.Timestamp("2100-01-01", tz="UTC")))
    monkeypatch.delenv("KILIT_AC", raising=False)
    with pytest.raises(PermissionError):
        u1_huni.stage_2b("x", u1.load_card("U1-H2-A"), {}, 10, tmp_path)


def test_funnel_data_is_cut_at_the_lock(tmp_path, monkeypatch):
    """Data that runs past 2025-09-30 never reaches the engine, whatever the card id."""
    index = pd.date_range("2025-09-20", "2025-10-10", freq="15min", tz="UTC")
    rng = np.random.default_rng(2)
    close = pd.Series(100 + rng.normal(0, 0.1, len(index)).cumsum(), index=index)
    frame = pd.DataFrame({"open": close, "high": close + 0.1, "low": close - 0.1, "close": close, "volume": 5.0})
    seen = {}
    real_prepare = u1_huni.tarama.prepare

    def spy(card, data, market, **kwargs):
        prepared = real_prepare(card, data, market, **kwargs)
        seen["last"] = max(f.index.max() for f in prepared.frames.values())
        seen["kilit"] = kwargs.get("kilit")
        return prepared

    monkeypatch.setattr(u1_huni.tarama, "prepare", spy)
    monkeypatch.setitem(u1.PERIODS, "OOS", (pd.Timestamp("2025-09-22", tz="UTC"), pd.Timestamp("2025-09-30", tz="UTC")))
    monkeypatch.delenv("KILIT_AC", raising=False)
    u1_huni.stage_2b("x[tf=15m]", u1.load_card("U1-H2-A"), {"BTCUSDT": frame}, 10, tmp_path)
    assert seen["kilit"] is True and seen["last"] <= pd.Timestamp("2025-09-30 23:59:59", tz="UTC")
