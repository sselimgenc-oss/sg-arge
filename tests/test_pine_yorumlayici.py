"""TV-2 Pine yorumlayıcısı: göstergeler, dil anlamı, request.security, desteklenmeyenin açık hatası, el çevirisiyle eşdeğerlik."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from engine import gosterge as g
from engine.pine import ta as T
from engine.pine.yorumlayici import Desteklenmiyor, PineStrateji, Yorumlayici
from engine.tv_emulator import calistir, nedensellik
from pynescript.ast import parse
from strategies.ozel import tv_ortak


def _veri(n: int = 600, seed: int = 0, freq: str = "4h") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, n))
    index = pd.date_range("2023-01-02", periods=n, freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": rng.uniform(1, 10, n)}, index=index)


def _seri(kaynak: str, df: pd.DataFrame, ad: str = "x", tf: str = "240") -> np.ndarray:
    """Betiği strateji bağlamı olmadan koşup `ad` değişkeninin bar bar değerini döndürür."""
    y = Yorumlayici(parse(kaynak), df, tf_dk=int(tf) if tf.isdigit() else 1440, sembol="BINANCE:TEST")
    y.surum = int(kaynak.split("@version=")[1][:1]) if "@version=" in kaynak else 5
    out = []
    for i in range(len(df)):
        y.adim(None, i)
        out.append(y._bul(ad).deger)
    return np.array(out, dtype=float)


def _ayni(a: np.ndarray, b: np.ndarray) -> None:
    assert np.array_equal(np.isnan(a), np.isnan(b))
    assert np.allclose(a[~np.isnan(a)], b[~np.isnan(b)], rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("pine, beklenen", [
    ("ta.ema(close, 10)", lambda df: g.ema(df, "close", 10)),
    ("ta.rma(close, 7)", lambda df: g.rma(df["close"], 7)),
    ("ta.sma(close, 20)", lambda df: g.sma(df, "close", 20)),
    ("ta.wma(close, 9)", lambda df: g.wma(df, "close", 9)),
    ("ta.rsi(close, 14)", lambda df: g.rsi(df, "close", 14)),
    ("ta.atr(14)", lambda df: g.atr(df, 14)),
    ("ta.stdev(close, 20)", lambda df: g.stdev(df, "close", 20)),
    ("ta.highest(high, 15)", lambda df: g.highest(df, "high", 15)),
    ("ta.lowest(12)", lambda df: g.lowest(df, "low", 12)),
    ("ta.cci(hlc3, 20)", lambda df: g.cci(df, 20)),
    ("ta.pivothigh(high, 3, 2)", lambda df: tv_ortak.pivothigh(df["high"], 3, 2)),
    ("ta.pivotlow(3, 3)", lambda df: tv_ortak.pivotlow(df["low"], 3, 3)),
    ("ta.percentrank(close, 10)", lambda df: tv_ortak.percentrank(df["close"], 10)),
])
def test_indicators_match_the_vectorised_pine_definitions(pine, beklenen) -> None:
    df = _veri()
    _ayni(_seri(f"//@version=5\nindicator('t')\nx = {pine}\n", df), beklenen(df).to_numpy(float))


def test_dmi_macd_and_supertrend_match() -> None:
    df = _veri()
    adx = _seri("//@version=5\nindicator('t')\n[p, m, x] = ta.dmi(14, 14)\n", df)
    _ayni(adx, g.dmi(df, 14)["adx"].to_numpy(float))
    hist = _seri("//@version=5\nindicator('t')\n[a, b, x] = ta.macd(close, 12, 26, 9)\n", df)
    _ayni(hist, g.macd(df, "close", 12, 26, 9)["hist"].to_numpy(float))
    yon = _seri("//@version=5\nindicator('t')\n[st, x] = ta.supertrend(3, 10)\n", df)
    ref = tv_ortak.supertrend(df, 10, 3.0)
    kolon = "dir" if "dir" in ref else ref.columns[-1]
    r = ref[kolon].to_numpy(float)
    # tv_ortak yön kuralı Pine'ınkiyle aynı işaretse birebir, ters işaretse negatifi
    assert np.array_equal(yon[50:], r[50:]) or np.array_equal(yon[50:], -r[50:])


def test_var_history_and_per_call_site_state_in_user_functions() -> None:
    df = _veri(50)
    src = """//@version=5
indicator('t')
f(src) =>
    ta.sma(src, 3)
var int sayac = 0
sayac += 1
a = f(close)
b = f(open)
x = sayac[2] + (a - ta.sma(close, 3)) + (b - ta.sma(open, 3))
"""
    x = _seri(src, df)
    assert np.isnan(x[0]) and np.isnan(x[1])
    assert list(x[2:6]) == [1.0, 2.0, 3.0, 4.0]       # sayac[2]; iki f() çağrısı ayrı durum tutar (fark 0)


def test_loops_switch_ternary_and_integer_division_by_version() -> None:
    df = _veri(5)
    src = """//@version={v}
indicator('t')
toplam = 0
for i = 1 to 4
    if i == 3
        continue
    toplam += i
k = switch
    toplam > 100 => 1
    => 2
x = toplam * 10 + k + 7 / 2
"""
    assert _seri(src.format(v=5), df)[0] == 7 * 10 + 2 + 3       # v5: 7/2 = 3
    assert _seri(src.format(v=6), df)[0] == 7 * 10 + 2 + 3.5     # v6: 7/2 = 3.5


def test_arrays_and_user_types() -> None:
    df = _veri(10)
    src = """//@version=5
indicator('t')
type Nokta
    float fiyat = 0.0
    int bar = 0
var a = array.new_float(0)
a.push(close)
if a.size() > 3
    a.shift()
n = Nokta.new(close, bar_index)
x = array.sum(a) / a.size() + n.bar * 0
"""
    x = _seri(src, df)
    _ayni(x, df["close"].rolling(3, min_periods=1).mean().to_numpy(float))


def test_security_higher_timeframe_lookahead_off_and_on() -> None:
    df = _veri(24 * 6, freq="1h")
    off = _seri("//@version=5\nindicator('t')\nx = request.security(syminfo.tickerid, 'D', close)\n", df, tf="60")
    on = _seri("//@version=5\nindicator('t')\nx = request.security(syminfo.tickerid, 'D', close, lookahead=barmerge.lookahead_on)\n",
               df, tf="60")
    gunluk = df["close"].resample("1D").last().to_numpy()
    # lookahead_off: gün ilk 23 saat bir önceki günün kapanışı, son saatte (gün kapanışı) o günün kapanışı
    assert np.isnan(off[:23]).all() and off[23] == gunluk[0] and off[24] == gunluk[0] and off[47] == gunluk[1]
    # lookahead_on: günün her saatinde o günün (gelecekteki) kapanışı
    assert on[0] == gunluk[0] and on[24] == gunluk[1]


def _strateji(govde: str, surum: int = 5) -> PineStrateji:
    kaynak = f"//@version={surum}\nstrategy('t', overlay=true)\n" + govde
    return PineStrateji(kaynak, sembol="BINANCE:TEST", tf="60")


def test_causality_check_catches_lookahead_on_and_passes_lookahead_off() -> None:
    df = _veri(24 * 20, freq="1h")
    temiz = _strateji("d = request.security(syminfo.tickerid, 'D', close)\nif close > d\n    strategy.entry('L', strategy.long)\nif close < d\n    strategy.close('L')\n")
    sizinti = _strateji("d = request.security(syminfo.tickerid, 'D', close, lookahead=barmerge.lookahead_on)\nif close < d\n    strategy.entry('L', strategy.long)\nif close > d\n    strategy.close('L')\n")
    assert nedensellik(temiz, df) == []
    assert nedensellik(sizinti, df)


def test_unsupported_feature_raises_instead_of_running() -> None:
    df = _veri(30)
    with pytest.raises(Desteklenmiyor):
        calistir(_strateji("x = request.security('BINANCE:ETHUSDT', 'D', close)\n"), df)
    with pytest.raises(Desteklenmiyor):
        calistir(_strateji("x = ta.kagi_yok(close)\n"), df)
    with pytest.raises(Desteklenmiyor):
        _strateji("x = 1\n").__class__(  # calc_on_order_fills betik davranışını değiştirir
            "//@version=5\nstrategy('t', calc_on_order_fills=true)\n", sembol="BINANCE:TEST", tf="60")


OSPKEM6I = """//@version=5
strategy("EMA + MACD + RSI Confluence Strategy", overlay=true,
     default_qty_type=strategy.percent_of_equity, default_qty_value=10,
     commission_type=strategy.commission.percent, commission_value=0.04)
ema_fast = ta.ema(close, 9)
ema_slow = ta.ema(close, 20)
[macdLine, signalLine, hist] = ta.macd(close, 12, 26, 9)
rsi = ta.rsi(close, 14)
longCondition = close > ema_fast and close > ema_slow and rsi > 50 and hist > 0
shortCondition = close < ema_fast and close < ema_slow and rsi < 50 and hist < 0
if (longCondition)
    strategy.entry("Long", strategy.long)
if (shortCondition)
    strategy.entry("Short", strategy.short)
strategy.exit("Exit Long", "Long", stop=close * 0.982, limit=close * 1.06)
strategy.exit("Exit Short", "Short", stop=close * 1.018, limit=close * 0.94)
"""


def test_interpreter_reproduces_the_hand_translation_trade_for_trade() -> None:
    from strategies.tv2 import ospkem6i
    df = _veri(1500, seed=7)
    ps = PineStrateji(OSPKEM6I, sembol="BINANCE:BTCUSDT.P", tf="240")
    assert ps.AYARLAR.default_qty_type == "percent_of_equity" and ps.AYARLAR.commission_value == 0.04
    a, b = calistir(ps, df).islemler, calistir(ospkem6i, df).islemler
    assert len(a) == len(b) > 50
    pd.testing.assert_frame_equal(a, b)


def test_generic_constructor_is_preprocessed_not_parsed_as_comparison() -> None:
    from engine.pine.yorumlayici import on_isle
    assert on_isle("var a = array.new<float>(0)\nb = array.new< Nokta >(2, na)") == "var a = array.new(0)\nb = array.new(2, na)"
    df = _veri(5)
    ps = _strateji("var a = array.new<float>(0)\na.push(close)\nif a.size() == 3\n    strategy.entry('L', strategy.long)\n")
    assert len(calistir(ps, df).emir_kaydi) == 1


def test_strategy_order_oca_cancel_and_close_immediately() -> None:
    df = _veri(40)
    # strategy.order: karşı yönde 3 adet, 1 adet long'u kapatır ve 2 adet short açar (pyramiding yok)
    s = calistir(_strateji("if bar_index == 1\n    strategy.order('A', strategy.long, 1)\nif bar_index == 3\n    strategy.order('B', strategy.short, 3)\n"), df)
    assert list(s.islemler["entry_id"]) == ["A"] and s.islemler.iloc[0]["exit_id"] == "B"
    # OCA cancel: iki yönlü bekleyen stop girişinden biri dolunca diğeri iptal; dar bant ikisini de tetikleyecek kadar yakın
    kod = ("if bar_index == 5\n    strategy.entry('U', strategy.long, 1, stop=close * 1.0001, oca_name='g', oca_type=strategy.oca.cancel)\n"
           "    strategy.entry('D', strategy.short, 1, stop=close * 0.9999, oca_name='g', oca_type=strategy.oca.cancel)\n"
           "if bar_index == 30\n    strategy.close_all()\n")
    assert len(calistir(_strateji(kod), df).islemler) == 1
    ocasiz = kod.replace(", oca_name='g', oca_type=strategy.oca.cancel", "")
    assert len(calistir(_strateji(ocasiz), df).islemler) == 2       # OCA yoksa ikisi de dolar (ters çevirme)
    # immediately: kapanış aynı barın kapanış fiyatından
    s = calistir(_strateji("if bar_index == 2\n    strategy.entry('L', strategy.long, 1)\nif bar_index == 6\n    strategy.close('L', immediately=true)\n"), df)
    t = s.islemler.iloc[0]
    assert t["cikis_bar"] == 6 and t["cikis_fiyat"] == pytest.approx(df["close"].iloc[6])


def test_security_other_symbol_uses_its_own_bars_and_never_the_unclosed_one() -> None:
    grafik = _veri(24 * 8, freq="1h")
    gunluk = _veri(10, seed=5, freq="D")                   # dış sembol (ör. VIX) günlük
    ps = _strateji("v = request.security('CBOE:VIX', 'D', close)\n"
                   "if close > 0 and v > 100\n    strategy.entry('L', strategy.long)\n")
    istekler = []
    ps.veri_saglayici = lambda sembol, dk: (istekler.append((sembol, dk)), gunluk)[1]
    ps.hazirla(grafik)
    degerler = []
    from engine.tv_emulator import Baglam
    ctx = Baglam(grafik, ps.AYARLAR)
    for i in range(len(grafik)):
        ctx.i = i
        ps.bar(ctx, i, {})
        degerler.append(ps.y._bul("v").deger)
    assert istekler == [("CBOE:VIX", 1440)]
    # gün d'nin değeri yalnız d günü kapandıktan sonra (o günün son saatlik barında) görünür
    assert np.isnan(degerler[0]) and degerler[23] == gunluk["close"].iloc[0] and degerler[24] == gunluk["close"].iloc[0]
    assert degerler[47] == gunluk["close"].iloc[1]
    assert nedensellik(ps, grafik) == []


def test_security_other_symbol_without_data_is_unsupported() -> None:
    ps = _strateji("v = request.security('CBOE:VIX', 'D', close)\n")
    ps.veri_saglayici = lambda sembol, dk: None
    with pytest.raises(Desteklenmiyor):
        calistir(ps, _veri(30, freq="1h"))


def test_map_put_get_keys_and_methods() -> None:
    df = _veri(6)
    src = """//@version=5
indicator('t')
var m = map.new<string, float>()
m.put("son", close)
if bar_index == 0
    map.put(m, "ilk", close)
x = m.get("son") - map.get(m, "ilk") + (m.contains("yok") ? 1000 : 0) + m.size() * 0
"""
    x = _seri(src, df)
    _ayni(x, (df["close"] - df["close"].iloc[0]).to_numpy(float))


def test_intraday_risk_limits_halt_trading_until_the_next_day() -> None:
    df = _veri(24 * 10, freq="1h")
    govde = "if strategy.position_size == 0\n    strategy.entry('L', strategy.long, 1)\nelse\n    strategy.close('L')\n"
    serbest = calistir(_strateji(govde), df).islemler
    # 2 dolum (giriş + çıkış) sınırı: günde en çok bir işlem
    sinirli = calistir(_strateji("strategy.risk.max_intraday_filled_orders(2)\n" + govde), df).islemler
    gunler = pd.to_datetime(sinirli["giris_zaman"]).dt.normalize()
    assert len(serbest) > 3 * len(sinirli) and gunler.value_counts().max() == 1 and gunler.nunique() >= 9
    # gün içi zarar: gün başından beri herhangi bir zararda dur; aynı gün sonraki barda giriş yok
    zarar = calistir(_strateji("strategy.risk.max_intraday_loss(1e-9, strategy.cash)\n" + govde), df)
    assert 0 < len(zarar.islemler) < len(serbest)
    with pytest.raises(Desteklenmiyor):
        calistir(_strateji("strategy.risk.max_cons_loss_days(3)\n"), df)


def test_heikin_ashi_security_matches_the_formula_and_v4_alias() -> None:
    from engine.pine.yorumlayici import heikin_ashi
    df = _veri(200)
    ha = heikin_ashi(df)
    x = _seri("//@version=5\nindicator('t')\nx = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)\n", df)
    _ayni(x, ha["close"].to_numpy())
    x4 = _seri("//@version=4\nstudy('t')\nx = security(heikinashi(syminfo.tickerid), timeframe.period, open)\n", df)
    _ayni(x4, ha["open"].to_numpy())
    assert ha["high"].ge(ha[["open", "close"]].max(axis=1)).all() and ha["open"].iloc[1] == pytest.approx((ha["open"].iloc[0] + ha["close"].iloc[0]) / 2)


def test_volume_variables_nvi_pvt_accdist() -> None:
    df = _veri(150)
    c, v, h, l = df["close"].to_numpy(), df["volume"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy()
    nvi = [1.0]
    for i in range(1, len(c)):
        nvi.append(nvi[-1] * (1 + (c[i] - c[i - 1]) / c[i - 1]) if v[i] < v[i - 1] else nvi[-1])
    _ayni(_seri("x = ta.nvi\n", df), np.array(nvi))
    pvt = np.r_[0.0, np.cumsum((c[1:] - c[:-1]) / c[:-1] * v[1:])]
    _ayni(_seri("x = ta.pvt\n", df), pvt)
    _ayni(_seri("x = ta.accdist\n", df), np.cumsum((2 * c - l - h) / (h - l) * v))
