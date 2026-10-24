"""U6 parti 3: TV-<id> kartlari (docs/GOREV_U6.md bolum 2 ve 5A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine.kart_sinyal import build_plan as dsl_plan, card_frame_signals
from engine.spec import validate_card
from strategies.ozel import build_plan as ozel_plan, has_strategy

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
PARTI_IDS = ['MI47rsio', 'yI5AU2ny', 'wu1VhNpf', 'qgTc4zie', 'x9pPfwmI', 'eDyfoKkr', 'mfw4fJST', 'qo43NaGV', 'RcF7t6Am', 'KW2v4SNI', 'u5R6y8cl', 'KO7Qe4Xb', 'efVFRo0C', 'bmIiC79T', 'MyuUXFMc', 'sPNx5Z74', 'PDUqNlVa', 'GDcSJIo9', 'LBcj22se', 'vJc6IOTz', 'cz5KaioF', 'Z4kcoUGT', 'mzv5SGie', 'BXDmlQdj', 'rP7izVek', '1s588fgS', '3BXWqwnF', 'BjjAOuub', 'CeFIpdwB', 'bZ815rmw', 'tuC7aGNI', 'A8gB4ha7', '6MgStabF', 'AR7LCcVC', 'PftCy6TI', 'odnW4iA5', 'bSGjA2Ie', 'fp0zbifH', 'AORNVoek', 'MoL1SwLE', 'Ospkem6i', 'zxTxzt8o', 'XTAGdX8Z', 'DGHCEcnB', 'FQVb4qo4', '7rQKeCN2', 'ALiYX5Gu', 'k13xEYxZ', 'QA8AC0vs', 'JH9IMLVt', 'WrEqzgAo', 'ZDhizQgu']
TAM_IDS = ['qgTc4zie', 'eDyfoKkr', 'qo43NaGV', 'KW2v4SNI', 'LBcj22se', 'vJc6IOTz', 'cz5KaioF', '1s588fgS', '3BXWqwnF', 'BjjAOuub', 'tuC7aGNI', 'AR7LCcVC', 'AORNVoek', 'ALiYX5Gu', 'k13xEYxZ', 'QA8AC0vs', 'ZDhizQgu']
OZEL_IDS = ['qgTc4zie', 'cz5KaioF', '1s588fgS', 'QA8AC0vs', 'ZDhizQgu']
# U7 Ek 1: kolu eslenen kartlar (docs/GOREV_U7.md) tests/test_u7_piyasa.py'de sinanir
_U7_EK1 = {i for i in PARTI_IDS if any(str(b).startswith(("U7 Ek 1", "U7 Ek 4")) for b in yaml.safe_load((SPEC / f"TV-{i}.yaml").read_text(encoding="utf-8"))["belirsiz"])}
PARTI_IDS = [i for i in PARTI_IDS if i not in _U7_EK1]
TAM_IDS = [i for i in TAM_IDS if i not in _U7_EK1]
OZEL_IDS = [i for i in OZEL_IDS if i not in _U7_EK1]
SINIFLAR = ("KRIPTO", "ABD", "EMTIA")
NEDENLER = ("piyasa", "veri", "ceviri", "bekliyor:motor")


def load(script_id: str) -> dict:
    return yaml.safe_load((SPEC / f"TV-{script_id}.yaml").read_text(encoding="utf-8"))


def signals(script_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    card = load(script_id)
    if card.get("ozel_kod"):
        return ozel_plan(card, {"X": frame}).signals["X"]
    out, _ = card_frame_signals(card, frame, week_end="SUN")
    return out


def frame_from(close, high=None, low=None, open_=None, volume=None, freq: str = "1D") -> pd.DataFrame:
    close = np.asarray(close, dtype=float)
    open_ = close.copy() if open_ is None else np.asarray(open_, dtype=float)
    high = close.copy() if high is None else np.asarray(high, dtype=float)
    low = close.copy() if low is None else np.asarray(low, dtype=float)
    volume = np.full(len(close), 1.0) if volume is None else np.asarray(volume, dtype=float)
    index = pd.date_range("2020-01-01", periods=len(close), freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=index)


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


# ------------------------------------------------------------------------------------------------ sema
@pytest.mark.parametrize("script_id", PARTI_IDS)
def test_kart_semasi_ve_alanlari(script_id):
    card = load(script_id)
    result = validate_card(SPEC / f"TV-{script_id}.yaml", card, set())
    assert result.errors == []
    assert card["id"] == f"TV-{script_id}"
    assert card["deneme_sayisi_kaynakta"] == 205
    assert card["yalniz_long_bacak"] is True
    assert card["yayin_sembolu"] is None or ":" in card["yayin_sembolu"]
    assert card["tf"] in ("4H", "1D")
    assert isinstance(card["belirsiz"], list) and card["belirsiz"]
    assert all(value is None for key, value in card["rapor"].items() if key != "maliyet_dahil")  # yazar rakami yok
    if card["spec_durumu"] == "tam":
        assert card["piyasa_kisiti"] == [card["kol"].split("-")[0]]
        assert card["kol"].split("-")[0] in SINIFLAR
        assert card["kol"].endswith("1D") or card["kol"].startswith("KRIPTO")  # ABD/emtia 4H yok
        if card["ozel_kod"]:
            assert card["ozel_kod_nedeni"] and has_strategy(card["id"])
        else:
            assert card["stop_eklendi"] == (card["stop"] is None)
            assert card["giris"] and (card["cikis"] or card["stop"] or card["hedef"])
    else:
        assert card["spec_durumu"] == "eksik"
        assert card["dogrulanamaz"]["neden"] in NEDENLER and card["dogrulanamaz"]["ayrinti"]
        if card["dogrulanamaz"]["neden"] == "veri":
            assert card["kol"].split("-")[0] in ("ABD", "EMTIA") and card["tf"] == "4H"
        if card["dogrulanamaz"]["neden"] == "piyasa":
            assert card["kol"].split("-")[0] not in SINIFLAR


def test_tam_kart_listesi_kayitla_tutarli():
    assert sorted(i for i in PARTI_IDS if load(i)["spec_durumu"] == "tam") == sorted(TAM_IDS)
    assert sorted(i for i in TAM_IDS if load(i)["ozel_kod"]) == sorted(OZEL_IDS)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_motor_plani_kurulur(script_id):
    card = load(script_id)
    frame = walk(900, 5, freq_of(card))
    plan = ozel_plan(card, {"X": frame}) if card["ozel_kod"] else dsl_plan(card, {"X": frame}, week_end="SUN", market="KRIPTO25")
    assert plan.stop_eklendi == card["stop_eklendi"]
    if card.get("zaman_stop"):
        assert plan.engine_kwargs["time_stop_bars"] == card["zaman_stop"]["bar"]
    if card.get("dolum") == "kapanis":
        assert plan.engine_kwargs["fill_at_close"] is True


# ----------------------------------------------------------------------------------- ileriye bakma yok
@pytest.mark.parametrize("script_id", TAM_IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(script_id, seed):
    card = load(script_id)
    frame = walk(1000, seed, freq_of(card))
    full = signals(script_id, frame)
    rng = np.random.default_rng(seed + 100)
    for cut in (350, 600, 850):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.15, len(frame) - (cut + 1)).cumsum())  # cut+1 ve sonrasi tamamen farkli
        for column in ("open", "high", "low", "close"):
            altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
        altered.iloc[cut + 1:, altered.columns.get_loc("volume")] = rng.uniform(100, 1000, len(frame) - (cut + 1))
        again = signals(script_id, altered)
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_ornek_seri_sinyal_uretir_ya_da_nadir(script_id):
    """Ileriye bakma testi bos sinyallerle gecmesin: uzun sentetik seride giris ya da cikis en az bir kez olusmali."""
    card = load(script_id)
    total = 0
    for seed in (7, 8, 9):
        sig = signals(script_id, walk(4000, seed, freq_of(card)))
        total += int(sig["entry"].sum()) + int(sig["exit"].sum())
    assert total > 0


# ----------------------------------------------------------------------------- elle hesaplanmis ornekler
def test_kw2v4sni_sma_kesisimi_elle_ornek():
    # 40 bar sabit 100 (SMA4 = SMA30 = 100, esitlik kesisim degil); bar 40 kapanis 120, bar 41 kapanis 60.
    sig = signals("KW2v4SNI", frame_from([100.0] * 40 + [120.0, 60.0]))
    assert not sig["entry"].iloc[:40].any() and not sig["exit"].iloc[:40].any()
    # bar 40: SMA4 = (3*100 + 120)/4 = 105, SMA30 = (29*100 + 120)/30 = 100.667 -> yukari kesisim
    assert sig["entry"].iloc[40] and not sig["exit"].iloc[40]
    # bar 41: SMA4 = (2*100 + 120 + 60)/4 = 95, SMA30 = (28*100 + 120 + 60)/30 = 99.333 -> asagi kesisim
    assert sig["exit"].iloc[41] and not sig["entry"].iloc[41]


def test_3bxwqwnf_kirilim_stop_ve_kanal_cikisi_elle_ornek():
    n = 60
    close = [100.0] * n + [103.0, 98.5]
    high = [101.0] * n + [103.5, 99.0]
    low = [99.0] * n + [102.0, 98.0]
    frame = frame_from(close, high=high, low=low)
    sig = signals("3BXWqwnF", frame)
    # bar 60: onceki 20 barin en yuksek high'i 101 < 103; SMA(50) = (49*100 + 103)/50 = 100.06 < 103 -> giris; bar 59'da 100 < 101 -> yok
    assert sig["entry"].iloc[60] and not sig["entry"].iloc[59]
    # stop mesafesi = 1.5 x ATR(20): TR = 2 (sabit), bar 60 TR = max(1.5, 3.5, 2) = 3.5 -> ATR = (19*2 + 3.5)/20 = 2.075 -> 3.1125
    assert sig["stop_dist"].iloc[60] == pytest.approx(3.1125)
    # cikis: bar 61 kapanis 98.5 < onceki 10 barin (51..60) en dusuk low'u 99; bar 60'ta 103 > 99
    assert sig["exit"].iloc[61] and not sig["exit"].iloc[60]


def test_qa8ac0vs_ay_evresi_gercek_takvimle_dogrulama():
    # Bagimsiz astronomik tarihler (UTC): yeni ay 2022-01-02 18:33, dolunay 2022-01-17 23:48, yeni ay 2022-02-01 05:46, dolunay 2022-02-16 16:56.
    # Faz, ilk olarak time_close (= bar acilis + 4 saat) bu anlari gecen barda degisir.
    frame = frame_from(np.full(6 * 60, 100.0), freq="4h")
    frame.index = pd.date_range("2021-12-20", periods=6 * 60, freq="4h", tz="UTC")
    sig = signals("QA8AC0vs", frame)
    entries = [str(t) for t in frame.index[sig["entry"].to_numpy()]]
    exits = [str(t) for t in frame.index[sig["exit"].to_numpy()]]
    assert entries == ["2022-01-02 16:00:00+00:00", "2022-02-01 04:00:00+00:00"]   # kapanislar 20:00 ve 08:00, olaylardan sonra
    assert exits == ["2022-01-17 20:00:00+00:00", "2022-02-16 16:00:00+00:00"]


def test_zdhizqgu_pozisyon_kapisi():
    # Giris ve cikis ayni barda olmaz; cikis yalniz acik pozisyonda uretilir.
    sig = signals("ZDhizQgu", walk(1500, 3, "1D"))
    pos = 0
    for entry, exit_ in zip(sig["entry"].to_numpy(), sig["exit"].to_numpy()):
        assert not (entry and exit_)
        pos += int(entry) - int(exit_)
        assert pos in (0, 1)
