"""U7 Ek 1: U6'da piyasa/veri nedeniyle atlanan 49 TV karti, kol eslemesi (docs/GOREV_U7.md Ek 1): sema, ileriye bakma yok, elle ornek."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine.kart_sinyal import build_plan as dsl_plan, card_frame_signals
from engine.spec import validate_card
from strategies.ozel import build_plan as ozel_plan
from strategies.ozel import tv_ortak as T

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
EMTIA_SEMBOL = {"TVC:GOLD", "OANDA:XAUUSD", "PEPPERSTONE:XAUUSD", "FX_IDC:USDWTI", "MCX:NATGASMINI1!"}


def _kartlar() -> dict[str, dict]:
    out = {}
    for path in sorted(SPEC.glob("TV-*.yaml")):
        card = yaml.safe_load(path.read_text(encoding="utf-8"))
        if any(str(b).startswith("U7 Ek 1") for b in card["belirsiz"]):
            out[card["id"][3:]] = card
    return out


KARTLAR = _kartlar()
TAM_IDS = [i for i, c in KARTLAR.items() if c["spec_durumu"] == "tam" and not c["ozel_kod"]]
OZEL_IDS = [i for i, c in KARTLAR.items() if c["spec_durumu"] == "tam" and c["ozel_kod"]]
DOGRULANAMAZ_IDS = [i for i, c in KARTLAR.items() if c["spec_durumu"] == "eksik"]


def beklenen_kol(card: dict) -> tuple[str, str] | None:
    """(piyasa_kisiti, kol etiketi) Ek 1 kurallarindan: yayin sembolu yoksa None."""
    sym = card["yayin_sembolu"]
    if not sym:
        return None
    if sym in EMTIA_SEMBOL:
        return "EMTIA", "EMTIA"
    exchange = sym.split(":")[0]
    if exchange == "BIST":
        return "BIST", "BIST30"
    if exchange in ("FX", "OANDA", "FX_IDC", "PEPPERSTONE", "VANTAGE") and sym != "FX:SPX500":
        return "FX", "FX8"
    return "ABD", "ABD25"


def load(script_id: str) -> dict:
    return yaml.safe_load((SPEC / f"TV-{script_id}.yaml").read_text(encoding="utf-8"))


def signals(script_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    card = load(script_id)
    if card.get("ozel_kod"):
        return ozel_plan(card, {"X": frame}).signals["X"]
    out, _ = card_frame_signals(card, frame, week_end="FRI")
    return out


def walk(bars: int, seed: int, freq: str, sigma: float = 0.012) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.001, sigma, bars)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, bars))
    spread = rng.uniform(0.0, 0.01, bars)
    index = pd.date_range("2018-01-01", periods=bars, freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * (1 + spread),
                         "low": np.minimum(open_, close) * (1 - spread), "close": close,
                         "volume": rng.uniform(100, 1000, bars)}, index=index)


def freq_of(card: dict) -> str:
    return "4h" if card["tf"] == "4H" else "1D"


@pytest.mark.parametrize("script_id", list(KARTLAR))
def test_kol_eslemesi_ve_not(script_id):
    card = KARTLAR[script_id]
    expected = beklenen_kol(card)
    if expected is None:
        assert card["spec_durumu"] == "eksik" and card["dogrulanamaz"]["neden"] == "piyasa"
        return
    token, label = expected
    kol = f"{label}-{card['tf']}"
    assert card["piyasa_kisiti"] == [token] and card["kol"] == kol and card["parametreler"]["kol"] == kol
    assert any(str(b).startswith("U7 Ek 1: kol ") and kol in str(b) for b in card["belirsiz"])
    assert card["deneme_sayisi_kaynakta"] == 205 and card["rapor"]["pf"] is None


@pytest.mark.parametrize("script_id", TAM_IDS + OZEL_IDS)
def test_kart_semasi_tam(script_id):
    card = load(script_id)
    assert validate_card(SPEC / f"TV-{script_id}.yaml", card, set()).errors == []
    assert card["spec_durumu"] == "tam" and card["yalniz_long_bacak"] is True and card["belirsiz"]
    assert card["giris"] or card.get("ozel_kod")
    plan = ozel_plan(card, {"X": walk(500, 1, freq_of(card))}) if card["ozel_kod"] else dsl_plan(card, {"X": walk(500, 1, freq_of(card))}, week_end="FRI", market="ABD25")
    assert plan.stop_eklendi == card["stop_eklendi"]


@pytest.mark.parametrize("script_id", DOGRULANAMAZ_IDS)
def test_dogrulanamaz_kart(script_id):
    card = load(script_id)
    assert validate_card(SPEC / f"TV-{script_id}.yaml", card, set()).errors == []
    assert card["spec_durumu"] == "eksik" and card["dogrulanamaz"]["neden"] in ("ceviri", "piyasa", "veri") and card["dogrulanamaz"]["ayrinti"]


@pytest.mark.parametrize("script_id", TAM_IDS + OZEL_IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(script_id, seed):
    card = load(script_id)
    frame = walk(1000, seed, freq_of(card))
    full = signals(script_id, frame)
    rng = np.random.default_rng(seed + 100)
    for cut in (350, 600, 850):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.15, len(frame) - (cut + 1)).cumsum())
        for column in ("open", "high", "low", "close"):
            altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
        altered.iloc[cut + 1:, altered.columns.get_loc("volume")] = rng.uniform(100, 1000, len(frame) - (cut + 1))
        again = signals(script_id, altered)
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("script_id", TAM_IDS + OZEL_IDS)
def test_ornek_seri_sinyal_uretir_ya_da_nadir(script_id):
    card = load(script_id)
    total = 0
    for seed in (7, 8, 9):
        sig = signals(script_id, walk(4000, seed, freq_of(card)))
        total += int(sig["entry"].sum()) + int(sig["exit"].sum())
    assert total > 0


# ------------------------------------------------------------------------------------------ elle ornekler
def test_4nv68grw_direnc_cizgisi_pivot_referansiyla_ayni():
    """Direnc cizgisi (son iki pivot tepesinden gecen dogru) tv_ortak.pivothigh ile bagimsiz hesaplananla ayni."""
    from engine import gosterge
    frame = walk(1500, 3, "4h")
    env = gosterge.build_env(frame, load("4NV68grw")["gostergeler"])
    ph = T.pivothigh(frame["high"], 3, 1)
    idx, vals, expected = [], [], np.full(len(frame), np.nan)
    for t in range(len(frame)):
        if not np.isnan(ph.iloc[t]):
            idx.append(t - 1); vals.append(ph.iloc[t])
        if len(idx) >= 2:
            expected[t] = vals[-1] + (vals[-1] - vals[-2]) / (idx[-1] - idx[-2]) * (t - idx[-1])
    got = env["res"].to_numpy()
    mask = ~np.isnan(expected)
    assert mask.sum() > 100
    assert np.allclose(got[mask], expected[mask], rtol=1e-9)
    assert np.isnan(got[~mask]).all()


def test_8yopuuso_rsi_kesisimi_elle():
    """RSI 35'i asagidan yukari keserken giris, 70'i yukaridan asagi keserken cikis (yalnizca kesisim barinda True)."""
    from engine import gosterge
    close = np.r_[np.linspace(100, 60, 30), np.linspace(60, 110, 40), np.linspace(110, 70, 30)]
    frame = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0},
                         index=pd.date_range("2020-01-01", periods=len(close), freq="4h", tz="UTC"))
    sig = signals("8YopUUSO", frame)
    rsi = gosterge.build_env(frame, load("8YopUUSO")["gostergeler"])["rsi14"]
    up = ((rsi > 35) & (rsi.shift(1) <= 35)).to_numpy()
    down = ((rsi < 70) & (rsi.shift(1) >= 70)).to_numpy()
    assert up.sum() == 1 and down.sum() == 1
    assert np.array_equal(sig["entry"].to_numpy(), up) and np.array_equal(sig["exit"].to_numpy(), down)


def test_spnx5z74_yuzde_supertrend_elle():
    """hl2 = 100 duz seri: bantlar 120/80. Bar 5'te kapanis 70 (< alt bant 80) -> trend -1, cikis. Bar 6'da kapanis 130
    (> bar 5'in ust bandi min(70 x 1,2 = 84, 120) = 84) -> trend +1, giris."""
    close = np.array([100.0] * 5 + [70.0, 130.0, 130.0])
    frame = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0},
                         index=pd.date_range("2020-01-01", periods=len(close), freq="1D", tz="UTC"))
    sig = signals("sPNx5Z74", frame)
    assert sig["exit"].tolist() == [False] * 5 + [True, False, False]
    assert sig["entry"].tolist() == [False] * 6 + [True, False]


def test_akf0t6mz_stop_hedef_formulu_kartta():
    """Stop = giris - min(giris - sinyal_dip, %1 x giris); hedef RR'si sinyal mumu araligi > %1 ise 1, degilse 2."""
    card = load("aKf0t6Mz")
    assert card["stop"]["ifade"] == "giris - min(giris - sinyal_low, giris * 0.01)"
    assert "eger((sinyal_high - sinyal_low) / sinyal_low * 100 > 1, 1, 2)" in card["hedef"]["ifade"]
    assert card["dolum"] == "kapanis"
