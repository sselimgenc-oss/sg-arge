"""U7 dakikalik kartlar (docs/GOREV_U7.md bolum 2): kripto ile kosulabilir kartlarin semasi ve ileriye bakma testi."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine.kart_sinyal import build_plan, card_frame_signals
from engine.spec import normalize_timeframe, validate_card

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
TAM_IDS = ['A3-002a', 'A3-002b', 'A3-002c', 'A3-002f', 'A3-002h', 'A3-002i', 'A3-010a', 'A3-010b', 'A3-010c', 'A3-010d', 'A3-011e', 'G003', 'O1-011', 'O1-017', 'P3-014']
FREQ = {"1m": "1min", "5m": "5min", "15m": "15min", "30m": "30min"}


def load(card_id: str) -> dict:
    card = yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))
    card["tf"] = normalize_timeframe(card["tf"])
    return card


def walk(card: dict, bars: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.004, bars)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.001, bars))
    spread = rng.uniform(0.0, 0.004, bars)
    index = pd.date_range("2024-01-01", periods=bars, freq=FREQ[card["tf"]], tz="UTC")
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * (1 + spread),
                         "low": np.minimum(open_, close) * (1 - spread), "close": close,
                         "volume": rng.uniform(100, 1000, bars)}, index=index)


def test_dakikalik_kartlarin_durumu_tutarli():
    """62 dakikalik kartin hicbiri 'dakikalik' durumunda kalmamali; her biri tam ya da nedenli eksik."""
    cards = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in SPEC.glob("*.yaml")]
    assert not [c["id"] for c in cards if c.get("spec_durumu") == "dakikalik"]
    for card in cards:
        if card["id"] in TAM_IDS:
            assert card["spec_durumu"] == "tam"
        elif (card.get("dogrulanamaz") or {}).get("ayrinti", "").startswith("U7 dakikalik"):
            assert card["spec_durumu"] == "eksik" and card["dogrulanamaz"]["neden"] in ("veri", "ceviri")


@pytest.mark.parametrize("card_id", TAM_IDS)
def test_kart_semasi_kripto_kolu(card_id):
    card = load(card_id)
    assert validate_card(SPEC / f"{card_id}.yaml", card, set()).errors == []
    assert card["piyasa_kisiti"] == ["KRIPTO"] and card["kollar"] == ["KRIPTO25"]
    assert card["tf"] in FREQ and card["belirsiz"] and any("U7 dakikalik" in str(b) for b in card["belirsiz"])
    plan = build_plan(card, {"X": walk(card, 600, 1)}, week_end="SUN", market="KRIPTO25")
    assert plan.stop_eklendi == bool(card["stop_eklendi"])


@pytest.mark.parametrize("card_id", TAM_IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(card_id, seed):
    card = load(card_id)
    frame = walk(card, 1500, seed)
    full, _ = card_frame_signals(card, frame, week_end="SUN")
    rng = np.random.default_rng(seed + 100)
    for cut in (500, 900, 1300):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.05, len(frame) - (cut + 1)).cumsum())
        for column in ("open", "high", "low", "close"):
            altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
        altered.iloc[cut + 1:, altered.columns.get_loc("volume")] = rng.uniform(100, 1000, len(frame) - (cut + 1))
        again, _ = card_frame_signals(card, altered, week_end="SUN")
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-9, atol=1e-9)
