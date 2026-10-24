"""U6 parti bekliyor:motor kartlari: TV-<id> kartlari (docs/GOREV_U6.md bolum 2 ve 5A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

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
PARTI_IDS = ['16yhUQN3', '70PkIvTL', '8GIAFRcP', 'IFSv46kK', 'NXbsqL9n', 'Q9OQye4C', 'ROM3crig', 'Y9ppyIk2', 'cz5KaioF', 'et8U6rd3', 'f80Cfpfp', 'hezSShJr', 'jjhUHcje', 'o9qty0BL', 'odnW4iA5', 'vMuEblZr']
TAM_IDS = ['70PkIvTL', 'Q9OQye4C', 'cz5KaioF', 'o9qty0BL', 'vMuEblZr']
OZEL_IDS = ['cz5KaioF', 'o9qty0BL', 'vMuEblZr']
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
    index = pd.date_range("2021-10-01", periods=bars, freq=freq, tz="UTC")
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


# ----------------------------------------------------------------------------- piramit alani ve motor plani
PIRAMIT = {"70PkIvTL": 8, "vMuEblZr": 2, "o9qty0BL": 1, "cz5KaioF": 2}


@pytest.mark.parametrize("script_id,en_cok", sorted(PIRAMIT.items()))
def test_piramit_alani_motor_planina_gecer(script_id, en_cok):
    card = load(script_id)
    assert card["piramit"] == {"en_cok": en_cok}
    frame = walk(900, 5, freq_of(card))
    plan = ozel_plan(card, {"X": frame}) if card["ozel_kod"] else dsl_plan(card, {"X": frame}, week_end="SUN", market="KRIPTO25")
    assert plan.engine_kwargs["pyramid_max"] == en_cok


def test_q9oqye4c_piramit_yok():
    # pyramiding = 1: ayni yonde en fazla 1 giris -> kartta piramit alani yok
    assert "piramit" not in load("Q9OQye4C")


def test_bekliyor_motor_kalmadi():
    # Bu PR'dan sonra hicbir karti 'bekliyor:motor' degil: ya cevrildi ya Dogrulanamaz (ceviri)
    for script_id in PARTI_IDS:
        card = load(script_id)
        if card["spec_durumu"] == "eksik":
            assert card["dogrulanamaz"]["neden"] == "ceviri"


# ----------------------------------------------------------------------------- elle hesaplanmis ornekler
def test_q9oqye4c_hma_egimi_elle_ornek():
    # dogrusal rampada wma(n) = t - (n - 1)/3: ham = 2 wma(27) - wma(55) = (t - 26/3) * 2 - (t - 18) = t + 4/3;
    # HMA = wma(ham, 7) = t + 4/3 - 2 = t - 2/3. Ilk gecerli bar: 54 (wma55) + 6 (wma7) = 60.
    up = signals("Q9OQye4C", frame_from(np.arange(120, dtype=float) + 100.0))
    assert list(np.flatnonzero(up["entry"].to_numpy()))[0] == 62        # hull[0] > hull[2] icin hull[2] da gecerli: bar 60 + 2
    assert not up["exit"].any()
    down = signals("Q9OQye4C", frame_from(300.0 - np.arange(120, dtype=float)))
    assert list(np.flatnonzero(down["exit"].to_numpy()))[0] == 62 and not down["entry"].any()


def _bekleyen_capitulation_frame():
    # 250 bar 300 -> 250 duzgun dusus (ZigZag zirvesi / dibi yok, SMA200 > 250), sonra 100..106..100 ucgen dalga x 6 (periyot 14; kapanis SMA200 altinda).
    base = np.linspace(300.0, 250.0, 250)
    wave = np.r_[np.arange(100, 107, dtype=float), np.arange(106, 99, -1, dtype=float)]
    close = np.r_[base, np.tile(wave, 6)]
    return frame_from(close, high=close + 0.5, low=close - 0.5, open_=close.copy())


def test_vmueblzr_dalga_durumu_ve_ilk_alim_elle_ornek():
    frame = _bekleyen_capitulation_frame()
    sig = signals("vMuEblZr", frame)
    assert not sig["entry"].any()                      # kapitulasyon mumu yok: ilk alim yok
    # ZigZag(3): bir zirve high[3] == highest(high, 7). Dalga zirveleri bar 256 (106,106 esit -> bayrak 259-260), 270 (273-274), 284 (287-288);
    # dipler bar 263 (266-267), 277 (280-281). Durum: A = bar 259 (zirve), B = bar 266 (dip), C = bar 273 (zirve), bar 280'de dip C'yi sifirlar.
    # Dalga C icinde (273..279) kirmizi, igneli, hacimli bir mum (bar 275) ilk alimi verir.
    idx = 275
    open_ = frame["open"].to_numpy().copy()
    high, low, close = frame["high"].to_numpy().copy(), frame["low"].to_numpy().copy(), frame["close"].to_numpy().copy()
    volume = frame["volume"].to_numpy().copy()
    open_[idx] = close[idx] + 0.1                       # govde 0.1
    high[idx] = close[idx] + 3.0                        # igne = (high - low) - govde = 5.9 > 0.1
    low[idx] = close[idx] - 3.0
    volume[idx] = 10.0                                  # SMA(20) hacmi 1: 10 > 1.4
    altered = frame_from(close, high=high, low=low, open_=open_, volume=volume)
    sig = signals("vMuEblZr", altered)
    entries = list(np.flatnonzero(sig["entry"].to_numpy()))
    assert entries[0] == idx
    # ikinci alim: ilk alimdan sonra kapanisin SMA(50)'yi ilk yukari kesisi (SMA(50) hala 250-300 tabanini tasidigindan bar 298'de)
    sma50 = altered["close"].rolling(50).mean()
    assert entries[1:] == [298] and altered["close"].iloc[298] > sma50.iloc[298] and altered["close"].iloc[297] <= sma50.iloc[297]
    assert not sig["exit"].any()                        # son alim olmadan cikis yok
    # ayni mum dalga C disinda (bar 282: durum 0) ilk alim vermez
    assert not np.flatnonzero(signals("vMuEblZr", _with_capitulation(frame, 282))["entry"].to_numpy()).size


def _with_capitulation(frame, idx):
    open_, high, low, close, volume = (frame[c].to_numpy().copy() for c in ("open", "high", "low", "close", "volume"))
    open_[idx] = close[idx] + 0.1
    high[idx] = close[idx] + 3.0
    low[idx] = close[idx] - 3.0
    volume[idx] = 10.0
    return frame_from(close, high=high, low=low, open_=open_, volume=volume)
