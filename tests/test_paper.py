"""T27: paper trade infrastructure (virtual ledger, parity, alarms, dashboard file)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtests import tarama
from engine.portfolio import run_portfolio  # noqa: F401
from data import fetch
from paper import anlik, gunluk, panel, parite
from tests.test_tarama import synthetic

ROOT = Path(__file__).resolve().parents[1]
BARS = 1500


def veri(seed: int = 0, bars: int = BARS) -> gunluk.Veri:
    frames = {
        "ABD25": {f"S{i}": synthetic(seed + i, periods=bars) for i in range(8)},
        "EMTIA": {f"E{i}": synthetic(seed + 40 + i, periods=bars) for i in range(6)},
    }
    return gunluk.Veri(frames, {"ABD25": synthetic(seed + 99, periods=bars)}, "hash-" + str(seed))


def portfoy(start: str = "2016-06-01", **alarm) -> gunluk.Portfoy:
    p = gunluk.yukle_portfoy()
    p.baslangic = pd.Timestamp(start, tz="UTC")
    p.alarm.update(alarm)
    return p


def last_days(data: gunluk.Veri, count: int) -> list[pd.Timestamp]:
    dates = sorted(set().union(*[set(f.index) for fr in data.frames.values() for f in fr.values()]))
    return dates[-count:]


def first_after(data: gunluk.Veri, day: pd.Timestamp) -> pd.Timestamp:
    return min(d for fr in data.frames.values() for f in fr.values() for d in f.index if d >= day)


def csv(defter: Path, name: str) -> pd.DataFrame:
    return gunluk._read(defter, name)  # noqa: SLF001


# ------------------------------------------------------------------------------------------ engine state recording
def test_recording_the_state_does_not_change_the_backtest() -> None:
    data = veri()
    satir = gunluk.yukle_portfoy().satirlar[1]  # R01: card path with partial profit
    prepared = tarama.prepare(gunluk._card(satir.id), data.frames["ABD25"], "ABD25", benchmark=data.benchmarks["ABD25"],  # noqa: SLF001
                              start=pd.Timestamp("2016-01-04", tz="UTC"), end=pd.Timestamp("2017-12-29", tz="UTC"))
    plain, recorded = prepared.run(), prepared.run(record_state=True)
    pd.testing.assert_frame_equal(plain.trades, recorded.trades)
    pd.testing.assert_series_equal(plain.equity, recorded.equity)
    assert recorded.fills and not plain.fills  # only recorded on request
    exits = [f for f in recorded.fills if f["tip"] == "cikis"]
    assert len(exits) == len(plain.trades)  # every closed trade has its exit fill


# ------------------------------------------------------------------------------------------ day flow
def test_orders_fill_at_the_next_actual_open_and_positions_follow(tmp_path: Path) -> None:
    data, p = veri(), portfoy()
    days = [first_after(data, p.baslangic + pd.Timedelta(days=60))] + last_days(data, 14)
    parite.tekrar_oyna(p, data, tmp_path, gunler=days)
    orders, fills, positions = csv(tmp_path, "emirler"), csv(tmp_path, "dolumlar"), csv(tmp_path, "pozisyonlar")
    entries = fills[fills["tip"] == "giris"]
    assert len(entries) and len(orders[orders["tip"] == "giris"])
    matched = 0
    for fill in entries.to_dict("records"):
        market = "EMTIA" if fill["satir"].endswith("EMTIA") else "ABD25"
        frame = data.frames[market][fill["sembol"]]
        assert fill["fiyat"] == pytest.approx(frame.at[pd.Timestamp(fill["tarih"], tz="UTC"), "open"])  # the real open, not the signal close
        assert fill["adet"] > 0 and fill["maliyet"] == pytest.approx(fill["adet"] * fill["fiyat"] * (0.0005))  # ABD/EMTIA base cost 0.05 %
        bars = frame.index
        signal_day = bars[bars.get_loc(pd.Timestamp(fill["tarih"], tz="UTC")) - 1].strftime("%Y-%m-%d")  # the bar before the fill
        order = orders[(orders["satir"] == fill["satir"]) & (orders["sembol"] == fill["sembol"]) & (orders["tip"] == "giris")
                       & (orders["sinyal_tarihi"] == signal_day)]
        if len(order):  # the ledger knew the order the evening before (earlier fills come from the catch-up day)
            matched += 1
            assert fill["referans_fiyat"] == pytest.approx(order.iloc[-1]["referans_fiyat"])
            assert fill["referans_fiyat"] == pytest.approx(frame.at[pd.Timestamp(signal_day, tz="UTC"), "close"])  # reference = signal-bar close
            assert fill["kayma_pct"] == pytest.approx(fill["fiyat"] / fill["referans_fiyat"] - 1.0)
    assert matched >= 1
    snapshot = positions[positions["tarih"] == positions["tarih"].max()]
    exits = fills[fills["tip"] == "cikis"]
    for held in snapshot.to_dict("records"):  # an open position has its entry fill and no exit since
        entry = entries[(entries["satir"] == held["satir"]) & (entries["sembol"] == held["sembol"]) & (entries["tarih"] == held["giris_tarihi"])]
        assert len(entry) == 1 and entry.iloc[0]["fiyat"] == pytest.approx(held["giris_fiyati"])
        assert exits[(exits["satir"] == held["satir"]) & (exits["sembol"] == held["sembol"]) & (exits["tarih"] > held["giris_tarihi"])].empty
    assert all(csv(tmp_path, name)["git_sha"].eq("parite").all() and csv(tmp_path, name)["data_hash"].eq("hash-0").all() for name in ("dolumlar", "ozkaynak"))
    assert exits["neden"].notna().all() and set(exits["neden"]) - {"signal", "stop", "gap_stop", "target", "gap_target"} == set()


# ------------------------------------------------------------------------------------------ parity (the key test)
def test_partial_sells_before_the_end_do_not_count_as_closed_trades(tmp_path: Path) -> None:
    """A position that already took its partial profit is force-closed at the end of a run with reason ``end_of_test+partial``."""
    data, p = veri(1), portfoy("2016-06-01")
    ozet = gunluk.calistir(p, data, tmp_path, git_sha="t")
    for etiket, result in ozet["sonuclar"].items():
        forced = result.trades[result.trades["exit_reason"].str.startswith("end_of_test")]
        assert len(forced) == len(result.open_positions)  # exactly the open book, partial or not
        assert ozet["satir_ozet"][etiket]["islem"] == len(result.trades) - len(forced)


def test_replayed_ledger_equals_one_backtest(tmp_path: Path) -> None:
    data, p = veri(1), portfoy("2016-06-01")
    days = [first_after(data, p.baslangic + pd.Timedelta(days=60))] + last_days(data, 12)
    parite.tekrar_oyna(p, data, tmp_path, gunler=days)
    report = parite.karsilastir(p, data, tmp_path)
    assert report["farklar"] == []
    assert report["islem_backtest"] >= 10 and report["islem_backtest"] == report["islem_defter"]


def test_parity_detects_a_tampered_ledger(tmp_path: Path) -> None:
    data, p = veri(1), portfoy("2016-06-01")
    parite.tekrar_oyna(p, data, tmp_path, gunler=last_days(data, 3))
    fills = csv(tmp_path, "dolumlar")
    victim = fills[fills["tip"] == "cikis"].index[0]
    fills.loc[victim, "fiyat"] = fills.loc[victim, "fiyat"] * 1.05
    fills.to_csv(tmp_path / "dolumlar.csv", index=False)
    assert parite.karsilastir(p, data, tmp_path)["farklar"]


# ------------------------------------------------------------------------------------------ alarms
def test_drawdown_stop_blocks_new_entries_but_keeps_exits(tmp_path: Path) -> None:
    data, p = veri(2), portfoy("2016-01-04", mdd_uyari=0.001, mdd_durdur=0.004)
    first = gunluk.calistir(p, data.kes(first_after(data, p.baslangic + pd.Timedelta(days=200))), tmp_path, git_sha="t")
    assert first["durdur"] is not None
    alarms = csv(tmp_path, "alarmlar")
    stop_day = alarms[alarms["tip"] == "DURDUR"].iloc[0]["tarih"]
    assert "UYARI" in set(alarms["tip"])
    parite.tekrar_oyna(p, data, tmp_path, gunler=last_days(data, 20))
    fills = csv(tmp_path, "dolumlar")
    assert fills[(fills["tip"] == "giris") & (fills["tarih"] > stop_day)].empty  # nothing opened after the stop
    assert not fills[(fills["tip"] == "cikis") & (fills["tarih"] > stop_day)].empty  # positions still close
    assert (csv(tmp_path, "alarmlar")["tip"] == "DURDUR").sum() == 1  # written once, persists
    text = gunluk.rapor_yaz(p, gunluk.calistir(p, data, tmp_path, git_sha="t"), tmp_path, tmp_path / "RAPOR.md", tmp_path)
    assert "Durum: **DURDUR**" in text and "DURDUR" in text.split("## Alarmlar")[1]


def test_profit_factor_review_alarm(tmp_path: Path) -> None:
    data, p = veri(0), portfoy("2016-01-04", pf_inceleme_islem=1, mdd_durdur=0.9, mdd_uyari=0.9)
    ozet = gunluk.calistir(p, data, tmp_path, git_sha="t")
    losers = [e for e, s in ozet["satir_ozet"].items() if s["islem"] >= 1 and s["pf"] < 1.0]
    reviewed = set(csv(tmp_path, "alarmlar").query("tip == 'INCELEME'")["satir"])
    assert reviewed == set(losers) and losers


# ------------------------------------------------------------------------------------------ holiday / missing data
def test_missing_bar_keeps_the_order_waiting_and_never_invents_a_fill(tmp_path: Path) -> None:
    data, p = veri(4), portfoy("2016-06-01")
    base = tmp_path / "base"
    gunluk.calistir(p, data, base, git_sha="t")
    fills = csv(base, "dolumlar")
    entry = fills[(fills["tip"] == "giris") & (fills["satir"] == "A6-010:EMTIA")].iloc[40]  # an entry well inside the history
    symbol, fill_day = entry["sembol"], pd.Timestamp(entry["tarih"], tz="UTC")
    holed = gunluk.Veri({m: {s: (f.drop(fill_day) if (s == symbol and m == "EMTIA") else f) for s, f in fr.items()} for m, fr in data.frames.items()},
                        data.benchmarks, data.data_hash)
    other = tmp_path / "holiday"
    gunluk.calistir(p, holed, other, git_sha="t")
    after = csv(other, "dolumlar")
    assert after[(after["sembol"] == symbol) & (after["tarih"] == fill_day.strftime("%Y-%m-%d"))].empty  # no fill on the missing day
    frame = holed.frames["EMTIA"][symbol]
    later = after[(after["satir"] == entry["satir"]) & (after["sembol"] == symbol) & (after["tip"] == "giris")]
    for row in later.to_dict("records"):  # every fill that exists is at a real bar's open
        assert row["fiyat"] == pytest.approx(frame.at[pd.Timestamp(row["tarih"], tz="UTC"), "open"])


def test_incomplete_us_daily_bar_is_excluded_until_close_plus_30_minutes() -> None:
    index = pd.DatetimeIndex(["2026-10-23", "2026-10-26"], tz="UTC")
    frame = pd.DataFrame({"open": [1.0, 2.0], "high": [2.0, 3.0], "low": [0.0, 1.0], "close": [1.5, 2.5], "volume": [1, 1]}, index=index)
    data = gunluk.Veri({"ABD25": {"AAA": frame}, "EMTIA": {"BBB": frame}}, {"ABD25": frame}, "half")
    before = gunluk.kapanmamis_gunluk_bari_at(data, pd.Timestamp("2026-10-26 15:00", tz="UTC"))
    after = gunluk.kapanmamis_gunluk_bari_at(data, pd.Timestamp("2026-10-26 21:30", tz="UTC"))
    assert before.frames["ABD25"]["AAA"].index[-1] == pd.Timestamp("2026-10-23", tz="UTC")
    assert before.frames["EMTIA"]["BBB"].index[-1] == pd.Timestamp("2026-10-23", tz="UTC")
    assert after.frames["ABD25"]["AAA"].index[-1] == pd.Timestamp("2026-10-26", tz="UTC")


def test_no_bar_after_the_paper_start_waits_instead_of_failing() -> None:
    # Yahoo sometimes serves the latest day without prices; the cleaned archive then ends before the paper start
    index = pd.DatetimeIndex(["2026-10-21", "2026-10-22"], tz="UTC")
    frame = pd.DataFrame({"open": [1.0, 2.0], "high": [2.0, 3.0], "low": [0.0, 1.0], "close": [1.5, 2.5], "volume": [1, 1]}, index=index)
    p = portfoy()
    early = gunluk.Portfoy(**{**p.__dict__, "baslangic": pd.Timestamp("2026-10-23", tz="UTC")})
    data = gunluk.Veri({m: {"AAA": frame} for m in {r.piyasa for r in p.satirlar}}, {}, "bos")
    assert gunluk.ilk_bar_bekleniyor(early, data) == [r.etiket for r in p.satirlar]
    later = gunluk.Portfoy(**{**p.__dict__, "baslangic": pd.Timestamp("2026-10-22", tz="UTC")})
    assert gunluk.ilk_bar_bekleniyor(later, data) == []


def test_indir_forwards_the_requested_data_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = []

    def fake_fetch(asset, interval, *, append, directory, **_kwargs):
        calls.append((asset.symbol, interval, append, directory))

    monkeypatch.setattr(fetch, "fetch_asset", fake_fetch)
    assert gunluk.indir(portfoy(), tmp_path) == []
    assert calls and all(call[1:] == ("1d", False, tmp_path) for call in calls)


# ------------------------------------------------------------------------------------------ append-only ledger
def test_ledger_is_append_only_and_a_data_revision_only_raises_an_alarm(tmp_path: Path) -> None:
    data, p = veri(5), portfoy("2016-06-01")
    cut = last_days(data, 10)
    for day in cut[:5]:
        gunluk.calistir(p, data.kes(day), tmp_path, git_sha="t")
    snapshot = {n: (tmp_path / f"{n}.csv").read_text() for n in ("emirler", "dolumlar", "ozkaynak") if (tmp_path / f"{n}.csv").exists()}
    again = gunluk.calistir(p, data.kes(cut[4]), tmp_path, git_sha="t")
    assert sum(again["eklenen"].values()) == 0  # idempotent: the same day adds nothing
    for day in cut[5:]:
        gunluk.calistir(p, data.kes(day), tmp_path, git_sha="t")
    for name, text in snapshot.items():
        assert (tmp_path / f"{name}.csv").read_text().startswith(text)  # old rows are byte-identical, new ones only after them
    revised = veri(5)
    for market, frames in revised.frames.items():
        for symbol, frame in frames.items():
            frame.iloc[-400:, frame.columns.get_indexer(["open", "high", "low", "close"])] *= 1.03  # adjusted history
    gunluk.calistir(p, revised, tmp_path, git_sha="t")
    assert "VERI_REVIZYONU" in set(csv(tmp_path, "alarmlar")["tip"])
    for name, text in snapshot.items():
        assert (tmp_path / f"{name}.csv").read_text().startswith(text)  # history stays as it was written


def test_no_fallback_prices_anywhere() -> None:
    for name in ("gunluk.py", "panel.py", "parite.py"):
        source = (ROOT / "paper" / name).read_text(encoding="utf-8")
        assert "FALLBACK" not in source and "fallback_price" not in source.lower()


def test_hourly_valuation_only_changes_dashboard_data_not_the_ledger(tmp_path: Path) -> None:
    data, p = veri(6), portfoy("2016-06-01")
    gunluk.calistir(p, data, tmp_path, git_sha="t")
    dashboard = tmp_path / "data.json"
    panel.yaz(panel.uret(tmp_path, p, ROOT / "results" / "SONUC.csv"), dashboard)
    before = {path.name: path.read_bytes() for path in tmp_path.glob("*.csv")}
    payload = anlik.guncelle(
        tmp_path, dashboard,
        fiyat_al=lambda _symbol: (123.45, pd.Timestamp("2026-10-26 15:00", tz="UTC")),
        simdi=pd.Timestamp("2026-10-26 15:01", tz="UTC"),
    )
    assert {path.name: path.read_bytes() for path in tmp_path.glob("*.csv")} == before
    assert payload["meta"]["fiyat_kaynagi"] == "anlik"
    assert payload["meta"]["fiyat_zamani"] == "2026-10-26T15:00:00+00:00"
    assert payload["meta"]["anlik_not"] == anlik.ANLIK_NOT
    assert all(item["current_price"] == 123.45 for item in payload["open_positions"])


# ------------------------------------------------------------------------------------------ dashboard file
def _kind(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float)):
        return "number"
    return {str: "string", list: "list", dict: "dict"}[type(value)]


def _compatible(expected: str, value) -> bool:
    return expected == "any" or value is None or _kind(value) == expected or (expected == "null")


def test_panel_file_has_the_dashboards_keys_and_types(tmp_path: Path) -> None:
    data, p = veri(6), portfoy("2016-06-01")
    ozet = gunluk.calistir(p, data, tmp_path, git_sha="t")
    payload = panel.uret(tmp_path, p, ROOT / "results" / "SONUC.csv", usdtry=41.5, simdi=pd.Timestamp("2018-11-24 12:00", tz="UTC"))
    panel.yaz(payload, tmp_path / "data.json")  # strict JSON (no NaN)
    loaded = json.loads((tmp_path / "data.json").read_text(encoding="utf-8"))
    sema = json.loads((ROOT / "tests" / "panel_sema.json").read_text(encoding="utf-8"))

    def check(path: str, obj: dict) -> None:
        for key, expected in sema[path].items():
            assert key in obj, f"{path}: eksik anahtar {key}"
            assert _compatible(expected, obj[key]), f"{path}.{key}: {expected} bekleniyordu, {_kind(obj[key])} bulundu"

    check("top", loaded)
    for section in ("meta", "kpis", "stats", "shadow_mode", "last_24h", "coach", "risk", "calendar"):
        check(section, loaded[section])
    check("calendar.selected_day", loaded["calendar"]["selected_day"])
    for item in loaded["calendar"]["selected_day"]["account_breakdown"]:
        check("calendar.selected_day.account_breakdown[]", item)
    for section in ("accounts", "strategies_27", "alerts", "periodic_returns", "open_positions", "closed_trades_list", "pending_orders"):
        assert loaded[section] or section in ("pending_orders",), section
        for item in loaded[section]:
            check(section + "[]", item)
    for item in loaded["calendar"]["days"]:
        check("calendar.days[]", item)
    for item in loaded["last_24h"]["chips"]:
        check("last_24h.chips[]", item)
    for item in loaded["coach"]["simulator_strategies"]:
        check("coach.simulator_strategies[]", item)
    assert [a["id"] for a in loaded["accounts"]] == ["C07", "R01", "A6-010"]
    assert loaded["kpis"]["total_value"] == pytest.approx(ozet["ozkaynak"], abs=0.01)
    assert loaded["kpis"]["initial_total_capital"] == 5000.0 and loaded["kpis"]["total_try"] == round(ozet["ozkaynak"] * 41.5)
    assert sum(a["initial_capital"] for a in loaded["accounts"]) == pytest.approx(5000.0, abs=0.05)


def test_panel_values_come_from_the_ledger_and_results_not_from_invention(tmp_path: Path) -> None:
    data, p = veri(6), portfoy("2016-06-01")
    gunluk.calistir(p, data, tmp_path, git_sha="t")
    payload = panel.uret(tmp_path, p, ROOT / "results" / "SONUC.csv", usdtry=None, simdi=pd.Timestamp("2018-11-24", tz="UTC"))
    sonuc = pd.read_csv(ROOT / "results" / "SONUC.csv").set_index("id")
    for item in payload["strategies_27"]:
        assert item["status"] == sonuc.loc[item["code"], "nihai_durum"]  # status straight from SONUC.csv
        assert item["score"] is None and item["j_score"] is None and item["p_main"] is None  # no unvalidated score
    assert payload["scorecards"] == [] and payload["risk"]["leverage_drawdown_montecarlo"] == [] and payload["coach"]["findings"] == []
    assert all(a["luck_prob"] == "veri yok" and a["score"] is None for a in payload["accounts"])
    assert payload["meta"]["exchange_rate"] is None and payload["kpis"]["total_try"] is None  # no rate -> no invented TRY value
    fills, positions = csv(tmp_path, "dolumlar"), csv(tmp_path, "pozisyonlar")
    assert len(payload["closed_trades_list"]) == len(parite.defter_islemleri(tmp_path))
    assert len(payload["open_positions"]) == len(positions[positions["tarih"] == positions["tarih"].max()])
    net = sum(t["pnl"] for t in payload["closed_trades_list"])
    assert payload["stats"]["net_pnl"] == pytest.approx(net, abs=0.01 * max(1, len(payload["closed_trades_list"])))
    for trade in payload["closed_trades_list"]:  # a trade's entry price is a real fill of the ledger
        assert ((fills["sembol"] == trade["asset"]) & (fills["fiyat"].round(4) == trade["entry_price"])).any()


def test_workflow_writes_only_to_the_paper_branch_and_guards_the_panel_token() -> None:
    import yaml

    text = (ROOT / ".github" / "workflows" / "paper.yml").read_text(encoding="utf-8")
    flow = yaml.safe_load(text)
    triggers = flow[True]  # YAML reads the key `on` as True
    assert triggers["schedule"] == [{"cron": "17 * * * *"}] and "workflow_dispatch" in triggers
    assert flow["permissions"] == {"contents": "write"}
    steps = flow["jobs"]["paper"]["steps"]
    publish = next(s for s in steps if "dashboard repo" in s.get("name", ""))
    assert publish["if"] == "env.PANEL_TOKEN != ''" and "secrets.PANEL_TOKEN" in flow["jobs"]["paper"]["env"]["PANEL_TOKEN"]
    pushes = [line.strip() for line in text.splitlines() if "git push" in line]
    assert pushes and all("paper-defter" in line or "origin HEAD" in line for line in pushes)  # never `main`
    assert flow["jobs"]["paper"]["timeout-minutes"] == 10
    assert flow["jobs"]["paper"]["env"]["PANEL_REPO"] == "sselimgenc-oss/sg-pano"
    assert any(step.get("run") == "python paper/anlik.py" for step in steps)
    assert "git push origin main" not in text and "${PANEL_REPO}" in text and "sg-test-panel" not in text and "bot_engine" not in text
