from datetime import date
import lzma
import struct

import pandas as pd
import pytest

from data import dukascopy


def bi5(rows):
    payload = b"".join(dukascopy.RECORD.pack(*row) for row in rows)
    return lzma.compress(payload)


class Response:
    def __init__(self, content=b"", status_code=200, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}

    @property
    def ok(self):
        return 200 <= self.status_code < 300


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.urls = []

    def get(self, url, timeout):
        self.urls.append(url)
        return next(self.responses)


def test_decode_and_merge_are_utc_mid_prices():
    day = date(2020, 1, 2)
    bid = dukascopy.decode(bi5([(60, 110000, 110100, 109900, 110200, 2.0)]), day, 1000)
    ask = dukascopy.decode(bi5([(60, 110100, 110200, 110000, 110300, 3.0)]), day, 1000)
    out = dukascopy.merge_sides(bid, ask)
    assert out.index[0] == pd.Timestamp("2020-01-02 00:01", tz="UTC")
    assert out.iloc[0]["close"] == pytest.approx(110.15)
    assert out.iloc[0]["spread"] == pytest.approx(0.1)
    assert out.iloc[0]["volume"] == pytest.approx(5.0)


def test_fetch_day_retries_429_and_obeys_request_spacing(monkeypatch):
    day = date(2020, 1, 2)
    session = Session([
        Response(status_code=429),
        Response(bi5([(0, 110000, 110000, 110000, 110000, 1.0)])),
        Response(bi5([(0, 110100, 110100, 110100, 110100, 1.0)])),
    ])
    sleeps = []
    monkeypatch.setattr(dukascopy.time, "sleep", sleeps.append)
    out = dukascopy.fetch_day(session, "USDJPY", day, delay=0.5)
    assert len(session.urls) == 3
    assert out.iloc[0]["close"] == pytest.approx(110.05)
    assert sleeps == [0.5, 0.5]


def test_fetch_year_skips_existing_days(monkeypatch):
    existing_index = pd.DatetimeIndex([pd.Timestamp("2020-01-02 00:00", tz="UTC")], name="timestamp")
    existing = pd.DataFrame({"open": [1], "high": [1], "low": [1], "close": [1], "volume": [2], "spread": [0.1]}, index=existing_index)
    monkeypatch.setattr(dukascopy, "date", date)
    monkeypatch.setattr(dukascopy, "fetch_day", lambda *args, **kwargs: pd.DataFrame())
    out = dukascopy.fetch_year("USDJPY", 2020, existing=existing, delay=0)
    assert len(out) == 1


def test_check_scale_rejects_wrong_divisor():
    frame = pd.DataFrame({"close": [110.2]})
    dukascopy.check_scale(frame, 110.0)
    with pytest.raises(ValueError):
        dukascopy.check_scale(frame, 1.102)


def test_supported_fx_metals_and_index_symbols_have_point_scales():
    assert dukascopy.POINT_DIVISOR["XAUUSD"] == 1_000
    assert dukascopy.POINT_DIVISOR["XAGUSD"] == 1_000
    assert dukascopy.POINT_DIVISOR["USATECHIDXUSD"] == 1_000
