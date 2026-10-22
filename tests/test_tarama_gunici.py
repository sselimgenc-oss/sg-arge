"""T12: intraday / sub-hourly scan rules (periods, skips, annualisation, end-to-end on synthetic bars)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtests import tarama
from backtests.run_codex21 import _filename
from tests.test_tarama import SPEC

HOURLY_START = pd.Timestamp("2020-01-01", tz="UTC")


def hourly(seed: int, periods: int = 4000, start=HOURLY_START, freq: str = "h") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = pd.date_range(start, periods=periods, freq=freq, tz="UTC")
    close = 100 * np.exp(np.cumsum(rng.normal(0.0001, 0.004, periods)))
    open_ = close * (1 + rng.normal(0, 0.001, periods))
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) * (1 + abs(rng.normal(0, 0.002, periods))),
            "low": np.minimum(open_, close) * (1 - abs(rng.normal(0, 0.002, periods))),
            "close": close,
            "volume": rng.uniform(1e3, 1e5, periods),
        },
        index=index,
    )


def test_period_rules() -> None:
    frames = {"A": hourly(1, 3000, start=pd.Timestamp("2023-11-01", tz="UTC"))}
    assert tarama.period_for("1H", "KRIPTO25", frames) == (tarama.IS_START, tarama.IS_END)
    assert tarama.period_for("1D", "ABD25", frames) == (tarama.IS_START, tarama.IS_END)
    start, end = tarama.period_for("1H", "ABD25", frames)
    first, last = frames["A"].index[0], frames["A"].index[-1]
    assert start == first and end == first + (last - first) * (2 / 3)


def test_skip_rules_and_annualisation() -> None:
    card = {"id": "X", "tf": "5m"}
    assert tarama._skip_reason(card, "ABD25") == ("Dogrulanamaz", "dakikalik_veri_yok")
    assert tarama._skip_reason(card, "KRIPTO25") is None
    one_hour = {"id": "Y", "tf": "1H"}
    assert tarama._skip_reason(one_hour, "BIST30")[1].startswith("veri_kalitesi")
    assert tarama._skip_reason(one_hour, "BIST30", bist_1h_quality_ok=True) is None
    assert tarama._skip_reason(one_hour, "ABD25") is None
    assert tarama._skip_reason({"id": "Z", "tf": "1H", "piyasa_kisiti": ["ABD"]}, "EMTIA")[1].startswith("piyasa_ozgu")
    assert tarama.annualization_for("1H", "KRIPTO25") == 24 * 365
    assert tarama.annualization_for("5m", "KRIPTO25") == 288 * 365
    assert tarama.annualization_for("2H", "KRIPTO25") == 12 * 365
    assert tarama.annualization_for("4H", "ABD25") == 252
    assert tarama.annualization_for("1D", "BIST30") == 252 and tarama.annualization_for("1W", "ABD25") == 52


def test_card_loader_normalizes_legacy_lowercase_hour(tmp_path: Path) -> None:
    (tmp_path / "legacy.yaml").write_text(
        "id: legacy\nspec_durumu: tam\nozel_kod: false\ntf: 1h\n", encoding="utf-8"
    )

    cards = tarama.load_cards(tmp_path, "1H")

    assert cards[0]["tf"] == "1H"


@pytest.mark.skipif(not SPEC.is_dir(), reason="docs/spec not present")
def test_intraday_scan_end_to_end_on_synthetic_bars(tmp_path: Path) -> None:
    cards = tarama.load_cards(SPEC, "1H") + tarama.load_cards(SPEC, "5m,15m,30m,1m")
    assert cards, "expected ready intraday cards"
    one_hour = next(card for card in cards if card["tf"] == "1H" and not card.get("roi_tablosu"))
    minute = next(card for card in cards if card["tf"] != "1H" and not card.get("piyasa_kisiti"))
    universe = pd.read_csv(Path(tarama.ROOT) / "data" / "evren.csv", dtype=str).fillna("")
    root = tmp_path / "data"
    for directory, freq in (("hourly", "h"), (minute["tf"], {"1m": "min", "5m": "5min", "15m": "15min", "30m": "30min"}[minute["tf"]])):
        (root / directory).mkdir(parents=True)
        for number, row in universe.iterrows():
            if directory != "hourly" and row.piyasa != "KRIPTO25":
                continue
            frame = hourly(number, periods=6000, freq=freq)
            frame.index.name = "timestamp"
            frame.to_parquet(root / directory / _filename(row.sembol))
    results = tmp_path / "results"
    table = tarama.scan(
        [one_hour, minute], root / "daily", results, data_root=root, summary_name="tarama_gunici_ozet.md", merge=True,
    )
    rows = table.set_index(["id", "piyasa"])
    assert rows.loc[(minute["id"], "ABD25"), "neden"] == "dakikalik_veri_yok"
    assert rows.loc[(one_hour["id"], "BIST30"), "durum"] == "Hesaplandi"
    assert (table["durum"] != "Hata").all(), table[table["durum"] == "Hata"][["id", "piyasa", "neden"]]
    assert "Hesaplandi" in set(table[table["id"] == one_hour["id"]]["durum"])
    assert (results / "tarama_gunici_ozet.md").read_text(encoding="utf-8").startswith("# Gun ici")
    assert (results / "tarama.csv").exists()
