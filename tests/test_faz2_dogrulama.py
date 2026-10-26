from __future__ import annotations

import pandas as pd

from backtests.faz2_dogrulama import coinbase_mumlari, funding_nakit_akisi, mnq_back_adjust


def test_coinbase_sayfalama_ornek_yanitla() -> None:
    calls = []
    def get(_url, params, timeout):
        calls.append(params)
        start = int(pd.Timestamp(params["start"]).timestamp())
        class Yanıt:
            def raise_for_status(self): pass
            def json(self): return [[start + 900, 1, 3, 2, 2.5, 4], [start, 1, 2, 1.5, 1.8, 3]]
        return Yanıt()
    frame = coinbase_mumlari(pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-01-08", tz="UTC"), get)
    assert len(calls) == 3 and frame.index.is_monotonic_increasing
    assert frame.iloc[0].to_dict() == {"open": 1.5, "high": 2.0, "low": 1.0, "close": 1.8, "volume": 3.0}


def test_funding_long_short_ve_isaret() -> None:
    t = pd.Timestamp("2024-01-01", tz="UTC")
    islemler = pd.DataFrame({"giris_zaman": [t, t], "cikis_zaman": [t + pd.Timedelta(9, unit="h")] * 2,
                             "yon": [1, -1], "adet": [2., 1.]})
    funding = pd.DataFrame({"rate": [.01], "price": [100.]}, index=[t + pd.Timedelta(8, unit="h")])
    # Long -2 USD öder, short +1 USD alır: net -1.
    assert funding_nakit_akisi(islemler, funding)["nakit"].tolist() == [-1.0]


def test_mnq_back_adjust_devir_boslugunu_kapatir_sonrasi_sabit() -> None:
    ix = pd.date_range("2024-03-01", "2024-03-21", freq="1D", tz="UTC")
    close = pd.Series(range(100, 100 + len(ix)), index=ix, dtype=float)
    close.loc["2024-03-11":] += 100  # üçüncü Cuma öncesi Pazartesi devir boşluğu
    raw = pd.DataFrame({k: close for k in ("open", "high", "low", "close")})
    adjusted, rolls = mnq_back_adjust(raw)
    assert rolls and adjusted.loc["2024-03-11", "close"] == raw.loc["2024-03-11", "close"]
    assert adjusted.loc["2024-03-10", "close"] == raw.loc["2024-03-10", "close"] + 101
