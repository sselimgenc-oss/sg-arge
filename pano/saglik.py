"""Paper kitapları için salt-okunur canlı/backtest sağlık ölçüleri."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BLOCK_WEEKS = 4
PATHS = 5_000
CUSUM_K = 0.5
CUSUM_YELLOW = 3.5
CUSUM_RED = 4.77


def _clean(value: float | int | None, digits: int = 4) -> float | int | None:
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), digits)


def haftalik_getiriler(series: pd.Series) -> pd.Series:
    """Dated equity or return series -> compounded Friday-week returns."""
    if series.empty:
        return pd.Series(dtype=float)
    values = pd.Series(series.to_numpy(dtype=float), index=pd.to_datetime(series.index, utc=True)).sort_index()
    if (values <= -1).any():
        return pd.Series(dtype=float)
    # Return files are labelled explicitly by their value; equity values are much larger than one.
    if values.abs().max() <= 1:
        return (1 + values).resample("W-FRI").prod() - 1
    return values.resample("W-FRI").last().pct_change().dropna()


def _varyant(kitap_id: str, piyasa: str | None, tf: str | None) -> list[str]:
    """Paper ids name the card (``U4-H2``); U7 stores each expansion as ``U4-H2:KRIPTO25:1D`` (file ``U4-H2_KRIPTO25_1D``)."""
    names = [kitap_id]
    if piyasa and tf:
        names.insert(0, f"{kitap_id}:{piyasa}:{tf}")
    return names


def _return_file(kitap_id: str, root: Path = ROOT, piyasa: str | None = None, tf: str | None = None) -> Path | None:
    for name in _varyant(kitap_id, piyasa, tf):
        found = sorted((root / "results").glob(f"**/getiriler/{name.replace(':', '_')}.csv"))
        if found:
            return found[0]
    return None


def _sinama_basi(kitap_id: str, root: Path = ROOT) -> pd.Timestamp | None:
    """TV-2: test window starts at the script version date (TEST_YAPISI); U7 files already hold OOS 2023+."""
    tv2 = root / "results" / "tv2" / "satirlar" / f"{kitap_id}.json"
    if tv2.exists():
        date = json.loads(tv2.read_text(encoding="utf-8")).get("surum_tarihi")
        return pd.Timestamp(date, tz="UTC") if date else None
    return None


def backtest_haftalik(kitap_id: str, root: Path = ROOT, piyasa: str | None = None, tf: str | None = None) -> pd.Series:
    path = _return_file(kitap_id, root, piyasa, tf)
    if path is None:
        return pd.Series(dtype=float)
    frame = pd.read_csv(path)
    date = next((c for c in frame if c.lower() in {"tarih", "datetime", "date"}), None)
    value = next((c for c in frame if c.lower() in {"net_getiri", "getiri", "return", "returns"}), None)
    if date is None or value is None:
        return pd.Series(dtype=float)
    daily = pd.Series(pd.to_numeric(frame[value], errors="coerce").fillna(0).to_numpy(),
                      index=pd.to_datetime(frame[date], utc=True))
    start = _sinama_basi(kitap_id, root)
    if start is not None:
        daily = daily[daily.index >= start]
    return haftalik_getiriler(daily)


def backtest_islem_sayisi(kitap_id: str, piyasa: str, root: Path = ROOT, tf: str | None = None) -> tuple[int | None, float | None]:
    """Return actual test-window trade count and weeks, never infer it from returns."""
    tv2 = root / "results" / "tv2" / "satirlar" / f"{kitap_id}.json"
    if tv2.exists():
        row = json.loads(tv2.read_text(encoding="utf-8"))
        return row.get("uyg_sinama_islem"), row.get("uyg_sinama_hafta")
    ozet = root / "results" / "u7" / "huni_ozet.csv"
    if ozet.exists():
        table = pd.read_csv(ozet)
        for name in _varyant(kitap_id, piyasa, tf):
            hit = table[table["varyant"] == name]
            if len(hit) and pd.notna(hit.iloc[0].get("oos_islem")) and pd.notna(hit.iloc[0].get("oos_islem_hafta")):
                return int(hit.iloc[0]["oos_islem"]), float(hit.iloc[0]["oos_islem_hafta"])
    for path in sorted((root / "results" / "u7").glob(f"**/parca/{kitap_id}.csv")):
        row = pd.read_csv(path)
        if len(row):
            r = row.iloc[0]
            return int(r.get("oos_islem", r.get("is_islem"))), float(r.get("oos_islem_hafta", np.nan))
    return None, None


def blok_bootstrap(returns: pd.Series, weeks: int, *, seed: int = 0) -> dict[str, list[float]] | None:
    if weeks <= 0 or returns.empty:
        return None
    values = returns.to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    paths = np.zeros((PATHS, weeks))
    for row in range(PATHS):
        out: list[float] = []
        while len(out) < weeks:
            start = int(rng.integers(0, len(values)))
            out.extend(values[(start + np.arange(BLOCK_WEEKS)) % len(values)].tolist())
        paths[row] = out[:weeks]
    equity = np.cumprod(1 + paths, axis=1) - 1
    return {f"p{q}": [float(v) for v in np.quantile(equity, q / 100, axis=0)] for q in (1, 5, 50, 95, 99)}


def _mdd(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    equity = (1 + returns).cumprod()
    return float(((equity.cummax() - equity) / equity.cummax()).max())


def _cusum(live: pd.Series, backtest: pd.Series) -> float | None:
    if not len(live) or len(backtest) < 2:
        return None
    sigma = float(backtest.std(ddof=1))
    if sigma <= 0:
        return None
    total = 0.0
    for value in live:
        z = (float(value) - float(backtest.mean())) / sigma
        total = max(0.0, total - z - CUSUM_K)
    return total


def _streak(trades: list[dict[str, Any]], backtest: pd.Series) -> tuple[int, float | None, float | None]:
    values = [float(t["pnl"]) for t in trades if t.get("pnl") is not None]
    if not values:
        return 0, None, None
    # Trade-level backtest outcomes are not retained for every legacy U7 run.
    # Its non-zero return observations are the auditable fallback, rather than
    # treating a short live losing streak as its own expected win rate.
    observed = backtest[backtest != 0]
    win_rate = float((observed > 0).mean()) if len(observed) else None
    if win_rate is None:
        return 0, None, None
    streak = best = 0
    for value in values:
        streak = streak + 1 if value < 0 else 0
        best = max(best, streak)
    # Union bound for at least one k-loss sequence, using the book's own win rate.
    probability = min(1.0, max(0.0, (len(values) - best + 1) * (1 - win_rate) ** best)) if best else 1.0
    return best, win_rate, probability


def _light(flags: list[str]) -> str:
    return "🔴" if "red" in flags else ("🟡" if "yellow" in flags else "🟢")


def hesapla(kitap_id: str, piyasa: str, equity: pd.Series, trades: list[dict[str, Any]], *, root: Path = ROOT,
            tf: str | None = None) -> dict[str, Any]:
    """Build the dashboard health payload. Missing source data stays explicit, never fabricated."""
    live = haftalik_getiriler(equity).tail(26)
    backtest = backtest_haftalik(kitap_id, root, piyasa, tf)
    cone = blok_bootstrap(backtest, len(live), seed=sum(map(ord, kitap_id)))
    flags: list[str] = []
    live_mdd, bt_mdd = _mdd(live), _mdd(backtest)
    mdd_ratio = live_mdd / bt_mdd if bt_mdd > 0 else None
    mdd_status = None
    if mdd_ratio is not None:
        mdd_status = "red" if mdd_ratio >= 1.5 else "yellow" if mdd_ratio >= 1 else "green"
        flags.append(mdd_status)
    cusum = _cusum(live, backtest)
    cusum_status = None
    if cusum is not None:
        cusum_status = "red" if cusum >= CUSUM_RED else "yellow" if cusum >= CUSUM_YELLOW else "green"
        flags.append(cusum_status)
    bt_n, bt_weeks = backtest_islem_sayisi(kitap_id, piyasa, root, tf)
    # The stored week count is "weeks with a trade"; the rate needs all calendar weeks of the test window.
    if len(backtest):
        bt_weeks = float(len(backtest))
    live_n = len(trades)
    frequency: dict[str, Any] = {"canli": live_n, "beklenen": None, "p95": None, "p99": None, "durum": None}
    if bt_n is not None and bt_weeks and bt_weeks > 0 and len(live):
        expected = bt_n / bt_weeks * len(live)
        delta95, delta99 = 1.96 * np.sqrt(expected), 2.576 * np.sqrt(expected)
        frequency.update({"beklenen": _clean(expected, 2), "p95": [_clean(max(0, expected-delta95), 2), _clean(expected+delta95, 2)],
                          "p99": [_clean(max(0, expected-delta99), 2), _clean(expected+delta99, 2)]})
        status = "red" if live_n < expected * .5 or abs(live_n - expected) > delta99 else ("yellow" if abs(live_n - expected) > delta95 else "green")
        frequency["durum"] = status
        flags.append(status)
    streak, win_rate, probability = _streak(trades, backtest)
    streak_status = None if win_rate is None else ("red" if probability < .01 else "yellow" if probability < .05 else "green")
    if streak_status:
        flags.append(streak_status)
    percentile = None
    if cone and len(live):
        actual = float((1 + live).prod() - 1)
        terminal = np.array([cone[k][-1] for k in ("p1", "p5", "p50", "p95", "p99")])
        percentile = "p1_altinda" if actual < terminal[0] else ("p5_altinda" if actual < terminal[1] else "bant_icinde")
        flags.append("red" if percentile == "p1_altinda" else "yellow" if percentile == "p5_altinda" else "green")
    few = bt_n is not None and bt_weeks and bt_n / bt_weeks * 52 < 30
    return {
        "isik": _light(flags), "haftalar": len(live), "mini_seri": [_clean(v, 6) for v in live.tolist()],
        "koni": cone, "koni_durumu": percentile,
        "mdd": {"canli": _clean(live_mdd), "backtest": _clean(bt_mdd), "oran": _clean(mdd_ratio), "sari": 1.0, "kirmizi": 1.5, "durum": mdd_status},
        "cusum": {"deger": _clean(cusum), "sari": CUSUM_YELLOW, "kirmizi": CUSUM_RED, "durum": cusum_status},
        "sinyal_sikligi": frequency,
        "ardisik_kayip": {"adet": streak, "kazanma_orani": _clean(win_rate), "olasilik": _clean(probability, 6), "durum": streak_status},
        "orneklem_kucuk": bool(few),
        # Later methods reserve a stable location without asserting values today.
        "kiyas": None, "null_bant": None,
    }
