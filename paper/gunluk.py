#!/usr/bin/env python3
"""T27: daily paper-trade run (virtual book, no money, no broker).

Every trading day after the close the whole portfolio is re-run **through the backtest engine path** (``tarama.prepare`` for cards,
``asama2b.prepare_codex`` for the Codex Algo rows) from the paper start to the last closed bar. No rule is copied: the engine
decides entries, exits, stops and fills (yesterday's orders fill at the *actual* open of the next bar, costs from
EVRENSEL_KURALLAR D). ``run_portfolio(record_state=True)`` additionally returns the fills, the open book and the orders that
signals of the last bar imply for the next open.

The ledger (``paper/defter/*.csv``) is append-only: a row is added when its key is new, history is never rewritten. A re-run that
disagrees with an existing row (data revision) leaves the row and writes an alarm. ``git_sha`` and ``data_hash`` are on every row.

Orders carry an *indicative* quantity (sized with the signal-bar close); the fill uses the real open, so the filled quantity can differ.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import asama2b, tarama  # noqa: E402
from backtests.run_codex21 import ROWS, _git_sha, _load_market  # noqa: E402
from data.fetch import Asset, normalize_ohlcv  # noqa: E402

PAPER_DIR = Path(__file__).resolve().parent
PORTFOLIO_PATH = PAPER_DIR / "portfoy.yaml"
LEDGER_DIR = PAPER_DIR / "defter"
GOLGE_LEDGER_DIR = LEDGER_DIR / "golge"
REPORT_PATH = PAPER_DIR / "RAPOR.md"
DATA_DIR = ROOT / "data" / "daily"
RESULTS_DIR = ROOT / "results"

LEDGER_COLUMNS = {
    "emirler": ["sinyal_tarihi", "satir", "sembol", "tip", "referans_fiyat", "adet_gosterge", "stop", "hedef"],
    "dolumlar": ["tarih", "satir", "sembol", "tip", "fiyat", "adet", "maliyet", "neden", "referans_fiyat", "kayma_pct", "stop"],
    "pozisyonlar": ["tarih", "satir", "sembol", "giris_tarihi", "giris_fiyati", "adet", "stop", "hedef", "son_kapanis", "acik_kar"],
    "ozkaynak": ["tarih", "satir", "ozkaynak"],
    "alarmlar": ["tarih", "tip", "satir", "mesaj"],
}
LEDGER_KEYS = {
    "emirler": ["sinyal_tarihi", "satir", "sembol", "tip"],
    "dolumlar": ["tarih", "satir", "sembol", "tip"],
    "pozisyonlar": ["tarih", "satir", "sembol"],
    "ozkaynak": ["tarih", "satir"],
    "alarmlar": ["tip", "satir"],  # an alarm is written once per (type, row); the report shows whether it still holds
}
STAMP = ["git_sha", "data_hash"]
PORTFOLIO_ROW = "PORTFOY"


# ----------------------------------------------------------------------------------------------- configuration
@dataclass(frozen=True)
class Satir:
    id: str
    piyasa: str
    kaynak: str  # "kart" | "codex"
    agirlik: float

    @property
    def etiket(self) -> str:
        return f"{self.id}:{self.piyasa}"


@dataclass
class Portfoy:
    sermaye: float
    baslangic: pd.Timestamp
    satirlar: list[Satir]
    alarm: dict[str, float]
    canli_baslangic: pd.Timestamp | None = None  # bars before this date are a retrospective run, not live paper


def yukle_portfoy(path: Path = PORTFOLIO_PATH) -> Portfoy:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = [Satir(str(r["id"]), str(r["piyasa"]), str(r["kaynak"]), float(r["agirlik"])) for r in raw["satirlar"]]
    if abs(sum(r.agirlik for r in rows) - 1.0) > 1e-4:
        raise ValueError("portfoy.yaml: agirliklar 1'e toplanmali")
    start = pd.Timestamp(str(raw["baslangic"]), tz="UTC")
    live = pd.Timestamp(str(raw["canli_baslangic"]), tz="UTC") if raw.get("canli_baslangic") else None
    return Portfoy(float(raw["sanal_sermaye"]), start, rows, {k: float(v) for k, v in (raw.get("alarmlar") or {}).items()}, live)


def golge_portfoy(ana: Portfoy | None = None, path: Path = PORTFOLIO_PATH) -> Portfoy:
    del ana
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    config = raw["golge"]
    start = pd.Timestamp(str(config["baslangic"]), tz="UTC")
    return Portfoy(float(config["sermaye"]), start, [Satir(str(config["id"]), str(config["piyasa"]), "kart", 1.0)], {"mdd_uyari": .15, "mdd_durdur": 1.0}, start)


# ----------------------------------------------------------------------------------------------- data
@dataclass
class Veri:
    """Daily frames per market plus the index series some cards need (``frames[market][symbol]``)."""

    frames: dict[str, dict[str, pd.DataFrame]]
    benchmarks: dict[str, pd.DataFrame | None]
    data_hash: str = ""

    def kes(self, as_of: pd.Timestamp) -> "Veri":
        """Only bars up to ``as_of`` (what the run would have known that evening)."""
        cut = {m: {s: f.loc[:as_of] for s, f in fr.items() if not f.loc[:as_of].empty} for m, fr in self.frames.items()}
        bench = {m: (b.loc[:as_of] if b is not None else None) for m, b in self.benchmarks.items()}
        return Veri(cut, bench, self.data_hash)


def kapanmamis_gunluk_bari_at(veri: Veri, simdi: pd.Timestamp | None = None) -> Veri:
    """Drop today's daily bar until the relevant US session is closed plus 30 minutes.

    Daily archives label a bar by its UTC calendar date.  An older final bar (for a
    weekend or exchange holiday) is therefore retained: only a bar labelled with
    today's New York date can be an in-progress session bar.
    """
    now = simdi or pd.Timestamp.now(tz="UTC")
    now = pd.Timestamp(now)
    now = now.tz_localize("UTC") if now.tzinfo is None else now.tz_convert("UTC")
    new_york_today = now.tz_convert("America/New_York").date()
    frames = {market: dict(series) for market, series in veri.frames.items()}
    benchmarks = dict(veri.benchmarks)
    for market in ("ABD25", "EMTIA"):
        market_frames = frames.get(market, {})
        dates = [frame.index[-1].tz_convert("UTC").date() for frame in market_frames.values() if len(frame)]
        if not dates:
            continue
        last_date = max(dates)
        close = pd.Timestamp(last_date, tz="America/New_York") + pd.Timedelta(hours=16, minutes=30)
        if last_date != new_york_today or now > close.tz_convert("UTC"):
            continue
        for symbol, frame in market_frames.items():
            frames[market][symbol] = frame[frame.index.tz_convert("UTC").date != last_date]
        benchmark = benchmarks.get(market)
        if benchmark is not None:
            benchmarks[market] = benchmark[benchmark.index.tz_convert("UTC").date != last_date]
    return Veri(frames, benchmarks, veri.data_hash)


def kapanmamis_4h_bari_at(frames: dict[str, pd.DataFrame], simdi: pd.Timestamp | None = None) -> dict[str, pd.DataFrame]:
    """Withhold the current UTC 4H bucket until its close plus five minutes."""
    now = pd.Timestamp(simdi or pd.Timestamp.now(tz="UTC"))
    now = now.tz_localize("UTC") if now.tzinfo is None else now.tz_convert("UTC")
    bucket = now.floor("4h")
    if now >= bucket + pd.Timedelta(hours=4, minutes=5):
        return {symbol: frame.copy() for symbol, frame in frames.items()}
    return {symbol: frame[frame.index < bucket].copy() for symbol, frame in frames.items()}


def ilk_bar_bekleniyor(portfoy: Portfoy, veri: Veri) -> list[str]:
    """Rows whose market has no closed daily bar on/after the paper start yet (e.g. Yahoo still serves the day without prices)."""
    bekleyen = []
    for satir in portfoy.satirlar:
        frames = [f for f in veri.frames.get(satir.piyasa, {}).values() if len(f)]
        if not frames or max(f.index[-1] for f in frames) < portfoy.baslangic:
            bekleyen.append(satir.etiket)
    return bekleyen


def indir(portfoy: Portfoy, directory: Path = DATA_DIR) -> list[str]:
    """Download only the symbols the portfolio needs (yfinance daily); returns the symbols that failed (their old archive stays)."""
    from backtests.run_codex21 import _symbols_for_market  # noqa: PLC0415
    from data.fetch import fetch_asset  # noqa: PLC0415

    failed = []
    for market in sorted({r.piyasa for r in portfoy.satirlar}):
        symbols = list(_symbols_for_market(market))
        if market in tarama.BENCHMARK_SYMBOL:
            symbols.append(tarama.BENCHMARK_SYMBOL[market])
        for symbol in dict.fromkeys(symbols):
            try:
                fetch_asset(
                    Asset(symbol, market, "binance" if market == "KRIPTO25" else "yfinance"),
                    "1d", append=False, directory=directory,
                )
            except Exception as exc:  # noqa: BLE001 - keep the stale archive, the staleness alarm reports it
                failed.append(f"{symbol} ({type(exc).__name__})")
    return failed


def indir_golge(directory: Path = ROOT / "data" / "hourly", *, simdi: pd.Timestamp | None = None) -> list[str]:
    """Refresh six shadow symbols, with only the 4H warm-up window on a fresh CI archive."""
    from data.fetch import fetch_asset  # noqa: PLC0415

    now = pd.Timestamp(simdi or pd.Timestamp.now(tz="UTC"))
    now = now.tz_localize("UTC") if now.tzinfo is None else now.tz_convert("UTC")
    start_override = now - pd.Timedelta(days=120)  # U4-H1 needs 100 × 4H bars plus a small buffer
    failed = []
    for symbol in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "TRXUSDT"):
        try:
            fetch_asset(Asset(symbol, "KRIPTO25", "binance"), "1h", append=True, start_override=start_override, directory=directory)
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{symbol} ({type(exc).__name__})")
    return failed


def yukle_veri(portfoy: Portfoy, directory: Path = DATA_DIR) -> Veri:
    frames, digests = {}, []
    for market in sorted({r.piyasa for r in portfoy.satirlar}):
        frames[market], digest, _missing = _load_market(market, directory)
        digests.append(digest)
    benchmarks: dict[str, pd.DataFrame | None] = {}
    for market, symbol in tarama.BENCHMARK_SYMBOL.items():
        if market not in frames:
            continue
        benchmarks[market] = frames[market].get(symbol)
        path = directory / f"{symbol}.parquet"
        if benchmarks[market] is None and path.exists():
            benchmarks[market] = normalize_ohlcv(pd.read_parquet(path))
            digests.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return Veri(frames, benchmarks, hashlib.sha256("".join(digests).encode()).hexdigest())


def yukle_golge_veri(path: Path = ROOT / "data" / "hourly") -> Veri:
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "TRXUSDT"]
    frames = {symbol: normalize_ohlcv(pd.read_parquet(path / f"{symbol}.parquet")) for symbol in symbols if (path / f"{symbol}.parquet").exists()}
    return Veri({"KRIPTO25": frames}, {}, "golge")


# ----------------------------------------------------------------------------------------------- one book through the engine
def _card(card_id: str) -> dict[str, Any]:
    return yaml.safe_load((ROOT / "docs" / "spec" / f"{card_id}.yaml").read_text(encoding="utf-8"))


def kitap(satir: Satir, veri: Veri, baslangic: pd.Timestamp, sermaye: float, *, maske_tarihi: pd.Timestamp | None = None,
          risk_per_trade: float = .005, max_total_risk: float = .02):
    """Run one portfolio row from ``baslangic`` to its last closed bar; entry signals on/after ``maske_tarihi`` are switched off (stop)."""
    frames = veri.frames[satir.piyasa]
    bitis = max(f.index[-1] for f in frames.values())
    if satir.kaynak == "codex":
        prepared = asama2b.prepare_codex(ROWS[satir.id], frames, baslangic, bitis)
    else:
        prepared = tarama.prepare(_card(satir.id), frames, satir.piyasa, benchmark=veri.benchmarks.get(satir.piyasa), start=baslangic, end=bitis)
    signals = prepared.plan.signals
    if maske_tarihi is not None:
        signals = {s: f.assign(entry=f["entry"].astype(bool) & ~(f.index >= maske_tarihi)) for s, f in signals.items()}
    result = prepared.run(1.0, signals=signals, record_state=True, initial_capital=sermaye,
                          risk_per_trade=risk_per_trade, max_total_risk=max_total_risk)
    return result, bitis


def ozkaynak_serisi(result, sermaye: float) -> pd.Series:
    """Marked equity per bar (the engine's last point is after the artificial end-of-test exit: replaced by the marked value)."""
    series = result.equity.astype(float).copy()
    if len(series) and np.isfinite(result.marked_equity):
        series.iloc[-1] = result.marked_equity
    return series


def portfoy_ozkaynak(seriler: dict[str, pd.Series], sermaye: float) -> pd.Series:
    index = pd.DatetimeIndex(sorted(set().union(*[s.index for s in seriler.values()])))
    total = pd.Series(0.0, index=index)
    for etiket, series in seriler.items():
        total += series.reindex(index).ffill().fillna(sermaye)
    return total


def max_dusus(series: pd.Series) -> float:
    peak = series.cummax()
    return float((1.0 - series / peak).max()) if len(series) else 0.0


def ilk_asim(series: pd.Series, esik: float) -> pd.Timestamp | None:
    drawdown = 1.0 - series / series.cummax()
    hit = drawdown[drawdown >= esik]
    return hit.index[0] if len(hit) else None


# ----------------------------------------------------------------------------------------------- ledger
def _read(directory: Path, name: str) -> pd.DataFrame:
    path = directory / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path, dtype={"satir": str, "sembol": str})
    return pd.DataFrame(columns=LEDGER_COLUMNS[name] + STAMP)


def _key(row: dict[str, Any] | pd.Series, name: str) -> tuple:
    return tuple(str(row[k]) for k in LEDGER_KEYS[name])


def ekle(directory: Path, name: str, rows: list[dict[str, Any]], stamp: dict[str, str]) -> int:
    """Append rows whose key is new; existing rows are never touched. Returns the number appended."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.csv"
    existing = _read(directory, name)
    known = {_key(r, name) for r in existing.to_dict("records")}
    fresh = []
    for row in rows:
        row = {**row, **stamp}
        if _key(row, name) not in known:
            known.add(_key(row, name))
            fresh.append({c: row.get(c) for c in LEDGER_COLUMNS[name] + STAMP})
    if fresh:
        frame = pd.DataFrame(fresh, columns=LEDGER_COLUMNS[name] + STAMP)
        frame.to_csv(path, mode="a", header=not path.exists() or path.stat().st_size == 0, index=False, float_format="%.10g")
    return len(fresh)


def _day(value: Any) -> str:
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _defter_tarihi(value: Any, *, zaman_damgali: bool) -> str:
    """Keep the daily ledger's dates stable; shadow rows need their closed 4H bar."""
    stamp = pd.Timestamp(value)
    return stamp.strftime("%Y-%m-%d %H:%M:%S") if zaman_damgali else _day(stamp)


def _kayma(order_rows: pd.DataFrame, satir: str, fill: dict[str, Any], signal_day: str | None) -> tuple[float, float]:
    """(reference price, slippage %) of a fill against the order of the signal bar just before it; (nan, nan) for stop/target exits."""
    tip = {"giris": "giris", "kismi": "kismi", "cikis": "cikis"}[fill["tip"]]
    if order_rows.empty or signal_day is None or fill["neden"] in {"stop", "gap_stop", "target", "gap_target", "roi"}:
        return float("nan"), float("nan")
    candidates = order_rows[(order_rows["satir"] == satir) & (order_rows["sembol"] == fill["sembol"]) & (order_rows["tip"] == tip)
                            & (order_rows["sinyal_tarihi"] == signal_day)]
    if candidates.empty:
        return float("nan"), float("nan")
    reference = float(candidates.iloc[-1]["referans_fiyat"])
    price = float(fill["fiyat"])
    return reference, (price / reference - 1.0 if tip == "giris" else reference / price - 1.0)


# ----------------------------------------------------------------------------------------------- the daily run
def calistir(
    portfoy: Portfoy, veri: Veri, defter: Path = LEDGER_DIR, *, git_sha: str | None = None,
    bugun: pd.Timestamp | None = None, risk_per_trade: float = .005, max_total_risk: float = .02,
    zaman_damgali: bool = False,
) -> dict[str, Any]:
    """Re-run every row, append what is new to the ledger, evaluate the alarms. ``veri`` must already end at the day being run."""
    stamp = {"git_sha": git_sha or _git_sha(), "data_hash": veri.data_hash}
    sermaye = {r.etiket: portfoy.sermaye * r.agirlik for r in portfoy.satirlar}
    alarms = _read(defter, "alarmlar")
    stop_rows = alarms[alarms["tip"] == "DURDUR"] if not alarms.empty else alarms
    stop_date = pd.Timestamp(stop_rows.iloc[0]["tarih"], tz="UTC") if len(stop_rows) else None

    def run_all(mask: pd.Timestamp | None):
        return {r.etiket: kitap(r, veri, portfoy.baslangic, sermaye[r.etiket], maske_tarihi=mask,
                                risk_per_trade=risk_per_trade, max_total_risk=max_total_risk)[0] for r in portfoy.satirlar}

    results = run_all(stop_date)
    series = {e: ozkaynak_serisi(res, sermaye[e]) for e, res in results.items()}
    total = portfoy_ozkaynak(series, portfoy.sermaye)
    new_alarms: list[dict[str, Any]] = []
    last_day = total.index[-1]
    if stop_date is None:
        crossed = ilk_asim(total, portfoy.alarm.get("mdd_durdur", 0.15))
        if crossed is not None:  # causal: the equity up to ``crossed`` does not depend on the entries switched off afterwards
            stop_date = crossed
            new_alarms.append({"tarih": _day(crossed), "tip": "DURDUR", "satir": PORTFOLIO_ROW,
                               "mesaj": f"portfoy MDD >= %{portfoy.alarm.get('mdd_durdur', 0.15):.0%}: yeni giris yok, devam icin kullanici karari gerekir"})
            results = run_all(stop_date)
            series = {e: ozkaynak_serisi(res, sermaye[e]) for e, res in results.items()}
            total = portfoy_ozkaynak(series, portfoy.sermaye)
    drawdown = max_dusus(total)
    if drawdown >= portfoy.alarm.get("mdd_uyari", 0.10):
        first = ilk_asim(total, portfoy.alarm.get("mdd_uyari", 0.10))
        new_alarms.append({"tarih": _day(first), "tip": "UYARI", "satir": PORTFOLIO_ROW, "mesaj": f"portfoy MDD %{drawdown:.1%}"})

    added = {name: 0 for name in LEDGER_COLUMNS}
    order_rows, fill_rows, position_rows, equity_rows = [], [], [], []
    existing_orders = _read(defter, "emirler")
    for satir in portfoy.satirlar:
        etiket, result = satir.etiket, results[satir.etiket]
        for order in result.next_orders:
            order_rows.append({
                "sinyal_tarihi": _defter_tarihi(order["sinyal_tarihi"], zaman_damgali=zaman_damgali), "satir": etiket, "sembol": order["sembol"], "tip": order["tip"],
                "referans_fiyat": order["referans_fiyat"], "adet_gosterge": order.get("adet"), "stop": order.get("stop"), "hedef": order.get("hedef"),
            })
        for fill in result.fills:
            if fill.get("neden") == "end_of_test":
                continue  # the engine closes every position at the end of a run; that is not a trade
            bars = veri.frames[satir.piyasa].get(fill["sembol"])
            before = bars.index[bars.index < pd.Timestamp(fill["tarih"])] if bars is not None else []
            reference, slip = _kayma(existing_orders, etiket, {**fill, "neden": fill.get("neden", "")},
                                     _defter_tarihi(before[-1], zaman_damgali=zaman_damgali) if len(before) else None)
            fill_rows.append({
                "tarih": _defter_tarihi(fill["tarih"], zaman_damgali=zaman_damgali), "satir": etiket, "sembol": fill["sembol"], "tip": fill["tip"], "fiyat": fill["fiyat"],
                "adet": fill["adet"], "maliyet": fill["maliyet"], "neden": fill.get("neden", ""), "referans_fiyat": reference, "kayma_pct": slip, "stop": fill.get("stop"),
            })
        for pos in result.open_positions:
            position_rows.append({
                "tarih": _defter_tarihi(last_day, zaman_damgali=zaman_damgali), "satir": etiket, "sembol": pos["sembol"], "giris_tarihi": _defter_tarihi(pos["giris_tarihi"], zaman_damgali=zaman_damgali),
                "giris_fiyati": pos["giris_fiyati"], "adet": pos["adet"], "stop": pos["stop"], "hedef": pos["hedef"], "son_kapanis": pos["son_kapanis"],
                "acik_kar": (pos["son_kapanis"] - pos["giris_fiyati"]) * pos["adet"],
            })
        for date, value in series[etiket].items():
            equity_rows.append({"tarih": _defter_tarihi(date, zaman_damgali=zaman_damgali), "satir": etiket, "ozkaynak": value})
    for date, value in total.items():
        equity_rows.append({"tarih": _defter_tarihi(date, zaman_damgali=zaman_damgali), "satir": PORTFOLIO_ROW, "ozkaynak": value})
    # profit-factor review: a row with >= N closed trades and PF < 1
    pf_limit = int(portfoy.alarm.get("pf_inceleme_islem", 30))
    summary_rows = {}
    for satir in portfoy.satirlar:
        trades = results[satir.etiket].trades
        trades = trades[~trades["exit_reason"].str.startswith("end_of_test")] if not trades.empty else trades
        wins, losses = (trades.loc[trades["net_pnl"] > 0, "net_pnl"].sum(), -trades.loc[trades["net_pnl"] < 0, "net_pnl"].sum()) if len(trades) else (0.0, 0.0)
        pf = float(wins / losses) if losses > 0 else (float("inf") if wins > 0 else float("nan"))
        summary_rows[satir.etiket] = {"islem": int(len(trades)), "pf": pf, "net": float(trades["net_pnl"].sum()) if len(trades) else 0.0}
        if len(trades) >= pf_limit and pf < 1.0:
            new_alarms.append({"tarih": _day(last_day), "tip": "INCELEME", "satir": satir.etiket, "mesaj": f"{len(trades)} islem sonra PF {pf:.2f} < 1"})
    # data staleness
    limit = int(portfoy.alarm.get("veri_eski_gun", 5))
    reference_day = bugun if bugun is not None else pd.Timestamp.now(tz="UTC").normalize()
    for market, frames in veri.frames.items():
        latest = max(f.index[-1] for f in frames.values())
        if (reference_day - latest).days > limit:
            new_alarms.append({"tarih": _day(reference_day), "tip": "VERI_ESKI", "satir": market, "mesaj": f"son bar {_day(latest)}"})
    # existing equity rows that the re-run now disagrees with (data revision): keep the row, write an alarm
    known = _read(defter, "ozkaynak")
    if not known.empty:
        merged = pd.DataFrame(equity_rows).merge(known[["tarih", "satir", "ozkaynak"]], on=["tarih", "satir"], suffixes=("", "_defter"))
        revised = merged[(merged["ozkaynak"] - merged["ozkaynak_defter"]).abs() > portfoy.sermaye * 1e-4]
        if len(revised):
            new_alarms.append({"tarih": _day(last_day), "tip": "VERI_REVIZYONU", "satir": PORTFOLIO_ROW,
                               "mesaj": f"{len(revised)} gecmis ozkaynak satiri yeniden hesapta farkli (defter degismedi), ilk: {revised.iloc[0]['tarih']}"})
    for name, rows in (("emirler", order_rows), ("dolumlar", fill_rows), ("pozisyonlar", position_rows), ("ozkaynak", equity_rows), ("alarmlar", new_alarms)):
        added[name] = ekle(defter, name, rows, stamp)
    return {
        "bitis": last_day, "ozkaynak": float(total.iloc[-1]), "mdd": drawdown, "durdur": stop_date, "eklenen": added,
        "sonuclar": results, "seriler": series, "toplam": total, "satir_ozet": summary_rows, "yeni_alarmlar": new_alarms,
    }


def calistir_golge(portfoy: Portfoy, veri: Veri, defter: Path = GOLGE_LEDGER_DIR, *, simdi: pd.Timestamp | None = None) -> dict[str, Any] | None:
    frames = kapanmamis_4h_bari_at(veri.frames.get("KRIPTO25", {}), simdi)
    if not frames or max(frame.index[-1] for frame in frames.values()) < portfoy.baslangic:
        return None
    return calistir(portfoy, Veri({"KRIPTO25": frames}, {}, veri.data_hash), defter, risk_per_trade=.0025, max_total_risk=.01,
                    zaman_damgali=True)


# ----------------------------------------------------------------------------------------------- report
def _expectations(results_dir: Path) -> pd.DataFrame:
    base, pit = results_dir / "asama2b.csv", results_dir / "asama2b_pit.csv"
    table = pd.read_csv(base) if base.exists() else pd.DataFrame()
    if pit.exists():
        rerun = pd.read_csv(pit)
        if not table.empty:
            keys = set(zip(rerun["id"], rerun["piyasa"]))
            table = table[[(i, m) not in keys for i, m in zip(table["id"], table["piyasa"])]]
        table = pd.concat([table, rerun], ignore_index=True)
    return table


def _f(value: Any, fmt: str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "-"
    return "-" if number != number else format(number, fmt)


def rapor_yaz(portfoy: Portfoy, ozet: dict[str, Any], defter: Path = LEDGER_DIR, path: Path = REPORT_PATH, results_dir: Path = RESULTS_DIR) -> str:
    total, sermaye = ozet["toplam"], portfoy.sermaye
    status = "DURDUR" if ozet["durdur"] is not None else ("UYARI" if ozet["mdd"] >= portfoy.alarm.get("mdd_uyari", 0.10) else "NORMAL")
    expect = _expectations(results_dir)
    fills = _read(defter, "dolumlar")
    lines = [
        "# Paper trade takip raporu", "",
        f"Son kapanmış bar: **{_day(ozet['bitis'])}** · Paper başlangıcı: {_day(portfoy.baslangic)} · Durum: **{status}**", "",
        "Sanal defter; gerçek para ve aracı kurum bağlantısı yoktur. Sinyal ve dolumlar backtest motoruyla aynı yoldan üretilir (`paper/gunluk.py`).", "",
        "## Portföy", "", "| Sanal sermaye | Özkaynak | Getiri | MDD | MDD uyarı / durdur |", "|---:|---:|---:|---:|---|",
        f"| {sermaye:,.0f} USD | {ozet['ozkaynak']:,.0f} USD | {ozet['ozkaynak'] / sermaye - 1:.2%} | {ozet['mdd']:.2%} | "
        f"{portfoy.alarm.get('mdd_uyari', 0.10):.0%} / {portfoy.alarm.get('mdd_durdur', 0.15):.0%} |", "",
        "## Satırlar: gerçekleşen ve backtest OOS beklentisi", "",
        "| Satır | Ağırlık | Kapanmış işlem | Gerçekleşen PF | Net (USD) | Açık poz. | Backtest OOS getiri | OOS işlem | OOS ortR | Bootstrap MDD95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for satir in portfoy.satirlar:
        mine = ozet["satir_ozet"][satir.etiket]
        e = expect[(expect["id"] == satir.id) & (expect["piyasa"] == satir.piyasa)] if not expect.empty else expect
        e = e.iloc[-1] if len(e) else {}
        opened = len(ozet["sonuclar"][satir.etiket].open_positions)
        get = (lambda key: e.get(key) if len(e) else None)
        lines.append(
            f"| {satir.etiket} | {satir.agirlik:.0%} | {mine['islem']} | {_f(mine['pf'], '.2f')} | {_f(mine['net'], ',.0f')} | {opened} | "
            f"{_f(get('oos_net'), '.1%')} | {_f(get('oos_islem'), '.0f')} | {_f(get('oos_ort_r'), '.3f')} | {_f(get('bootstrap_mdd_p95'), '.1%')} |"
        )
    lines += ["", "Beklenti sütunları `results/asama2b(_pit).csv` içindeki backtest OOS sonuçlarıdır (2024-10 sonrası); paper kısa olduğu sürece rakamlar karşılaştırma değil yön gösterir.", ""]

    lines += ["## Yarın açılışta verilecek emirler", ""]
    orders = [(s.etiket, o) for s in portfoy.satirlar for o in ozet["sonuclar"][s.etiket].next_orders]
    if orders:
        lines += ["| Satır | Sembol | Emir | Gösterge adet | Referans (son kapanış) | Stop | Hedef |", "|---|---|---|---:|---:|---:|---:|"]
        lines += [f"| {e} | {o['sembol']} | {o['tip']} | {_f(o.get('adet'), '.2f')} | {_f(o['referans_fiyat'], '.2f')} | {_f(o.get('stop'), '.2f')} | {_f(o.get('hedef'), '.2f')} |" for e, o in orders]
        lines += ["", "Adet göstergedir (son kapanışla boyutlanır); gerçek adet açılış fiyatıyla hesaplanır."]
    else:
        lines += ["- Yok."]
    lines += ["", "## Açık pozisyonlar", ""]
    positions = [(s.etiket, p) for s in portfoy.satirlar for p in ozet["sonuclar"][s.etiket].open_positions]
    if positions:
        lines += ["| Satır | Sembol | Giriş | Giriş fiyatı | Adet | Stop | Son kapanış | Açık kâr |", "|---|---|---|---:|---:|---:|---:|---:|"]
        lines += [f"| {e} | {p['sembol']} | {_day(p['giris_tarihi'])} | {_f(p['giris_fiyati'], '.2f')} | {_f(p['adet'], '.2f')} | {_f(p['stop'], '.2f')} | {_f(p['son_kapanis'], '.2f')} | {_f((p['son_kapanis'] - p['giris_fiyati']) * p['adet'], ',.0f')} |" for e, p in positions]
    else:
        lines += ["- Yok."]

    lines += ["", "## Kayma (dolum fiyatı - sinyal anı beklentisi)", ""]
    slip = fills.dropna(subset=["kayma_pct"]) if not fills.empty else fills
    if len(slip):
        lines += ["| Satır | Dolum | Ortalama kayma | Medyan | Kötü yönde en büyük |", "|---|---:|---:|---:|---:|"]
        for etiket, group in slip.groupby("satir"):
            lines.append(f"| {etiket} | {len(group)} | {group['kayma_pct'].mean():.3%} | {group['kayma_pct'].median():.3%} | {group['kayma_pct'].max():.3%} |")
        lines += ["", "Pozitif = beklentiden kötü. Referans, sinyal barının kapanışıdır; stop/hedef çıkışlarının emri olmadığı için kayma hesaplanmaz."]
    else:
        lines += ["- Henüz sinyal emriyle eşleşen dolum yok."]

    alarms = _read(defter, "alarmlar")
    lines += ["", "## Alarmlar", ""]
    if alarms.empty:
        lines += ["- Yok."]
    else:
        lines += ["| Tarih | Tip | Satır | Mesaj |", "|---|---|---|---|"]
        lines += [f"| {r.tarih} | {r.tip} | {r.satir} | {r.mesaj} |" for r in alarms.itertuples()]
    lines += ["", "Kurallar: portföy MDD ≥ %10 uyarı; ≥ %15 **durdur** (yeni giriş yok, çıkışlar sürer; devam kullanıcı kararıdır); bir satır 30 kapanmış işlemden sonra PF < 1 ise inceleme; son bar 5 günden eskiyse veri alarmı.", ""]
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfoy", type=Path, default=PORTFOLIO_PATH)
    parser.add_argument("--defter", type=Path, default=LEDGER_DIR)
    parser.add_argument("--rapor", type=Path, default=REPORT_PATH)
    parser.add_argument("--veri-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--indirme", action="store_true", help="download the needed symbols first (yfinance)")
    args = parser.parse_args()
    portfoy = yukle_portfoy(args.portfoy)
    if args.indirme:
        failed = indir(portfoy, args.veri_dir)
        failed += indir_golge()
        if failed:
            print("UYARI indirilemeyen semboller (eski arsiv kullanilir):", ", ".join(failed), file=sys.stderr)
    veri = kapanmamis_gunluk_bari_at(yukle_veri(portfoy, args.veri_dir))
    # The shadow book is independent of the daily book: a missing daily bar
    # must never prevent a closed 4H bar from being booked.
    calistir_golge(golge_portfoy(path=args.portfoy), yukle_golge_veri(ROOT / "data" / "hourly"))
    bekleyen = ilk_bar_bekleniyor(portfoy, veri)
    if bekleyen:  # nothing to book yet: leave the ledger untouched instead of failing the hourly run
        mesaj = f"paper baslangicindan ({_day(portfoy.baslangic)}) sonra kapanmis gunluk bar yok: {', '.join(bekleyen)}. Defter degismedi."
        args.defter.mkdir(parents=True, exist_ok=True)
        if not args.rapor.exists():
            args.rapor.write_text(f"# Paper raporu\n\nBekleniyor: {mesaj}\n", encoding="utf-8")
        print("BEKLENIYOR:", mesaj)
        return 0
    ozet = calistir(portfoy, veri, args.defter)
    rapor_yaz(portfoy, ozet, args.defter, args.rapor)
    print(json.dumps({"bitis": str(ozet["bitis"].date()), "ozkaynak": round(ozet["ozkaynak"], 2), "mdd": round(ozet["mdd"], 4),
                      "durdur": str(ozet["durdur"]), "eklenen": ozet["eklenen"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
