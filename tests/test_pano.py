"""Faz 2 pano: bilgi amaçlı sağlık ve koç kuralları."""

from __future__ import annotations

import pandas as pd

from pano import koc, saglik



def test_block_bootstrap_is_deterministic_and_marks_below_band() -> None:
    bt = pd.Series([.01, -.01, .02, 0, .01, -.02, .01, .01])
    first = saglik.blok_bootstrap(bt, 4, seed=7)
    second = saglik.blok_bootstrap(bt, 4, seed=7)
    assert first == second and first is not None
    assert all(len(first[key]) == 4 for key in ("p1", "p5", "p50", "p95", "p99"))


def test_cusum_and_health_lights(monkeypatch, tmp_path) -> None:
    weekly = pd.Series([.01, -.01] * 10, index=pd.date_range("2025-01-03", periods=20, freq="W-FRI", tz="UTC"))
    monkeypatch.setattr(saglik, "backtest_haftalik", lambda *_args: weekly)
    monkeypatch.setattr(saglik, "backtest_islem_sayisi", lambda *_args: (52, 52))
    equity = pd.Series([100, 90, 80, 70], index=pd.date_range("2026-01-02", periods=4, freq="W-FRI", tz="UTC"))
    red = saglik.hesapla("X", "ABD25", equity, [{"pnl": -1}] * 4, root=tmp_path)
    assert red["cusum"]["durum"] == "red" and red["isik"] == "🔴"
    flat = pd.Series([100, 101, 102, 103], index=equity.index)
    green = saglik.hesapla("X", "ABD25", flat, [], root=tmp_path)
    assert green["cusum"]["durum"] is None or green["cusum"]["durum"] != "red"


def test_coach_rules_trigger_only_for_rule_breaks() -> None:
    health = {"A": {"mdd": {"durum": "yellow"}, "cusum": {"durum": None}, "sinyal_sikligi": {"durum": None}, "ardisik_kayip": {"durum": None}}}
    now = pd.Timestamp("2026-10-27", tz="UTC")
    empty = koc.bulgular({"A": {key: {"durum": None} for key in ("mdd", "cusum", "sinyal_sikligi", "ardisik_kayip")}}, pd.DataFrame(), pd.DataFrame(), simdi=now)
    assert empty == []
    fills = pd.DataFrame([{"tarih": "2026-10-27", "tip": "giris", "satir": key, "kayma_pct": 0.0} for key in ("A", "B", "C")])
    findings = koc.bulgular(health, fills, pd.DataFrame(), simdi=now)
    assert {item["olcu"] for item in findings} == {"MDD oranı", "yoğunlaşma"}


def test_coach_marks_slippage_and_recent_source_alarm() -> None:
    now = pd.Timestamp("2026-10-27", tz="UTC")
    health = {"A": {key: {"durum": None} for key in ("mdd", "cusum", "sinyal_sikligi", "ardisik_kayip")}}
    fills = pd.DataFrame([{"tarih": "2026-10-27", "tip": "cikis", "satir": "A", "kayma_pct": .001}])
    alarms = pd.DataFrame([{"tarih": "2026-10-27", "tip": "KAYNAK_HATASI", "satir": "A", "mesaj": "erişim yok"}])
    findings = koc.bulgular(health, fills, alarms, simdi=now)
    assert {item["olcu"] for item in findings} == {"kayma", "KAYNAK_HATASI"}


def test_health_frequency_and_losing_streak_thresholds(monkeypatch, tmp_path) -> None:
    weekly = pd.Series([.01, -.01] * 30, index=pd.date_range("2024-01-05", periods=60, freq="W-FRI", tz="UTC"))
    monkeypatch.setattr(saglik, "backtest_haftalik", lambda *_args: weekly)
    monkeypatch.setattr(saglik, "backtest_islem_sayisi", lambda *_args: (100, 52))
    equity = pd.Series([100, 101, 100, 101], index=pd.date_range("2026-01-02", periods=4, freq="W-FRI", tz="UTC"))
    health = saglik.hesapla("X", "ABD25", equity, [], root=tmp_path)
    assert health["sinyal_sikligi"]["durum"] == "red"  # expected ~8 trades, none closed in time
    losses = saglik.hesapla("X", "ABD25", equity, [{"pnl": -1}] * 5, root=tmp_path)
    assert losses["ardisik_kayip"]["durum"] in {"yellow", "red"}
