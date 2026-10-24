"""U6 parti 4: TV-<id> kartlari (docs/GOREV_U6.md bolum 2 ve 5A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

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
PARTI_IDS = ['7v1PWf2e', 'GP3FEy2z', 'dpkq3n4O', 'x8rkJOjn', 'uvZ46BZ2', 'VOFjU544', 'BJDRgy7z', '4NV68grw', '4bBrEQ7T', 'TlwmnFdI', '7cisWbRB', 'fDrDSlEM', 'X5M5zevX', 'd1K2qpL3', 'N3ItY18G', 'Ibi0s0z5', 'wigMmPHd', 'RehzSQ8g', '4AzLMpYa', 'QfY9ozPr', 'hcXGamAi', '6XPbhz9C', 'vpopCZIt', 'FEnNQpAn', 'C9c7lz9r', 'TapWBWNO', 'GZCiUApZ', '9SEB7IHb', 'QEVAQHl6', 'qrCrfG0m', 'KKGMELzx', 'qNLQQ9aB', 'pRrH9OWy', '9URAiZJE', 'JFIZkwZR', 'GlCHqK0R', 'bE05CfsO', 'tevFM5BB', '6GReiiLS', 'bA9UFcgj', 'yMnDhKLs', 'qUrvPAmT', '0igXqoj5', '5EGVP61U', 'n3eosaZK', '3Q75d98D', '7yIh8gog', 'aKf0t6Mz', 'oF6FmwfR']
TAM_IDS = ['dpkq3n4O', 'VOFjU544', 'X5M5zevX', 'd1K2qpL3', 'QfY9ozPr', 'vpopCZIt', 'FEnNQpAn', 'QEVAQHl6', 'pRrH9OWy', '9URAiZJE', '6GReiiLS', 'qUrvPAmT', 'n3eosaZK', 'oF6FmwfR']
OZEL_IDS = ['dpkq3n4O', 'VOFjU544', 'X5M5zevX', 'FEnNQpAn', 'qUrvPAmT']
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
def test_qevaqhl6_sma_bandi_elle_ornek():
    # 200 bar sabit 100; bar 200 kapanis 105, bar 201 kapanis 90.
    sig = signals("QEVAQHl6", frame_from([100.0] * 200 + [105.0, 90.0]))
    assert not sig["entry"].iloc[:200].any()          # bar 199: SMA = 100, 100 > 104 degil
    # bar 200: SMA = (199*100 + 105)/200 = 100.025, esik 1.04 x = 104.026 < 105 -> giris
    assert sig["entry"].iloc[200] and not sig["exit"].iloc[200]
    # bar 201: SMA = (198*100 + 105 + 90)/200 = 99.975, alt esik 0.97 x = 96.97 > 90 -> cikis
    assert sig["exit"].iloc[201] and not sig["entry"].iloc[201]


def test_vofju544_izleyen_cizgi_elle_ornek():
    # close = 10,10,10,10,13,9,3 (high = low = close): ATR(1) = gercek aralik = 0,0,0,0,3,4,6; tampon = 3 x ATR.
    sig = signals("VOFjU544", frame_from([10.0, 10.0, 10.0, 10.0, 13.0, 9.0, 3.0]))
    # cizgi: bar 0 = 10 - 0 = 10; bar 1-3 = 10 (kapanis cizgiye esit -> else dali p + tampon = 10)
    # bar 4: kapanis 13 > 10 ama onceki kapanis 10 > 10 degil -> 13 - 9 = 4; yukari kesisim (10 <= 10 ve 13 > 4): giris
    assert list(np.flatnonzero(sig["entry"].to_numpy())) == [4]
    # bar 5: 9 > 4 ve 13 > 4 -> max(4, 9 - 12) = 4. bar 6: 3 < 4 ama onceki 9 < 4 degil -> 3 + 18 = 21; cizgi 4 -> 21 kesisimi: cikis
    assert list(np.flatnonzero(sig["exit"].to_numpy())) == [6]


def test_dpkq3n4o_korelasyon_elle_ornek():
    from strategies.ozel.tv_dpkq3n4o import correlation_with_index

    assert correlation_with_index(pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]), 5).iloc[-1] == pytest.approx(1.0)
    assert correlation_with_index(pd.Series([5.0, 4.0, 3.0, 2.0, 1.0]), 5).iloc[-1] == pytest.approx(-1.0)
    # y = [1,3,2,5,4]: t merkezli -2..2, y merkezli -2,0,-1,2,1: kov = 4 + 0 + 0 + 2 + 2 = 8; paydalar 10 ve 10 -> r = 8/10
    assert correlation_with_index(pd.Series([1.0, 3.0, 2.0, 5.0, 4.0]), 5).iloc[-1] == pytest.approx(0.8)


def test_dpkq3n4o_piramit_alani():
    card = load("dpkq3n4O")
    assert card["piramit"] == {"en_cok": 2}
    plan = ozel_plan(card, {"X": walk(600, 4, "1D")})
    assert plan.engine_kwargs["pyramid_max"] == 2


# ------------------------------------------------------------------ [1] kaymasi (Pine highest/lowest(...)[1]) taramasi
KAYDIR_BEKLENEN = {
    "n3eosaZK": ["hi126"], "3BXWqwnF": ["hh20", "ll10"], "ANmKXWWJ": ["hh20", "ll20"], "XRZCjbFr": ["hh50", "ll50"],
    "tuC7aGNI": ["hh30", "ll30"], "jc2hs2qK": ["hh60", "vh60"], "uC1oajDr": ["lowrec", "highrec"],
}


@pytest.mark.parametrize("script_id,names", sorted(KAYDIR_BEKLENEN.items()))
def test_pine_onceki_pencere_kartta_kaydir_1(script_id, names):
    """Pine'da highest/lowest(...)[1] (ya da highest(high[1], n)) 'onceki n bar' demektir: kartta kaydir: 1 olmali."""
    gost = load(script_id)["gostergeler"]
    for name in names:
        assert gost[name]["kaydir"] == 1, (script_id, name)


def test_n3eosaz_k_onceki_126_bar_elle_ornek():
    from engine import gosterge

    # high = 100; bar 100 high = 110 (126 bar once), bar 226 high = 105. Pine high126[1] bar 226'da bar 100..225'in en yuksegi = 110:
    # 105 >= 110 degil -> giris kosulu yanlis. Kaydirmasiz pencere (bar 101..226) 105 verir ve yanlislikla dogru olurdu.
    n = 240
    high = np.full(n, 100.0)
    high[100] = 110.0
    high[226] = 105.0
    frame = frame_from(np.full(n, 100.0), high=high)
    env = gosterge.build_env(frame, load("n3eosaZK")["gostergeler"])
    assert env["hi126"].iloc[226] == 110.0
    assert not (frame["high"].iloc[226] >= env["hi126"].iloc[226])
    # bar 227: pencere 101..226 -> en yuksek 105
    assert env["hi126"].iloc[227] == 105.0
