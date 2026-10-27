"""CT-Kapı v1 helpers and public-data runner.

This module never authenticates, places orders, or reads wallets.  It deliberately
keeps every unavailable public input as ``Yetersiz`` rather than estimating it.
"""
from __future__ import annotations

import argparse
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

from copytrade.olcut import _funding_amount, calculate_metrics, closed_round_trips, perp_fills
from copytrade.tarama import PublicClient, RateLimitError, RateLimiter, prefilter
from kapi.istatistik import deflated_sharpe_ratio, nw_alpha

TAKER = 0.00045
SLIPPAGE = 0.0005


def _portfolio_history(portfolio: list[dict]) -> pd.Series:
    periods = {name: value for name, value in portfolio if isinstance(value, dict)}
    data = periods.get("perpAllTime") or periods.get("allTime") or {}
    points = data.get("accountValueHistory", [])
    return pd.Series({pd.to_datetime(t, unit="ms", utc=True): float(v) for t, v in points}).sort_index()


def external_cashflows(ledger: list[dict]) -> pd.Series:
    """Only public deposit/withdraw ledger rows are external flows; transfers are not guessed."""
    items: list[tuple[pd.Timestamp, float]] = []
    for row in ledger:
        delta = row.get("delta", {})
        kind = str(delta.get("type", row.get("type", ""))).lower() if isinstance(delta, dict) else ""
        if kind not in {"deposit", "withdraw", "internaltransfer", "subaccounttransfer", "vaultdeposit", "vaultwithdraw", "spottransfer", "send"}:
            continue
        raw = delta.get("usdc", row.get("usdc", 0)) if isinstance(delta, dict) else row.get("usdc", 0)
        amount = abs(float(raw))
        sender, user = str(row.get("from", row.get("sender", ""))).lower(), str(row.get("user", "")).lower()
        if kind == "withdraw" or (sender and user and sender == user):
            amount = -amount
        items.append((pd.to_datetime(row.get("time"), unit="ms", utc=True), amount))
    if not items:
        return pd.Series(dtype=float, index=pd.DatetimeIndex([], tz="UTC"))
    return pd.Series(dict(items), dtype=float).groupby(level=0).sum().sort_index()


def time_weighted_monthly(portfolio: list[dict], ledger: list[dict], days: int = 365) -> pd.Series:
    """Monthly time-weighted returns, removing documented deposits and withdrawals.

    Values and cash flows are aligned at their public timestamps.  A flow is
    removed from the closing value of its subperiod before compounding.
    """
    values = _portfolio_history(portfolio)
    if len(values) < 2:
        return pd.Series(dtype=float)
    since = values.index[-1] - pd.Timedelta(days=days)
    values = values[values.index >= since]
    flows = external_cashflows(ledger)
    # A cash flow belongs to the first observed portfolio value after it; never invent a value point.
    assigned = pd.Series(0.0, index=values.index)
    for at, amount in flows.items():
        later = values.index[values.index >= at]
        if len(later): assigned.loc[later[0]] += amount
    flows = assigned
    prior = values.shift(1)
    returns = (values - flows) / prior - 1
    returns = returns.iloc[1:].replace([np.inf, -np.inf], np.nan).dropna()
    if returns.empty:
        return pd.Series(dtype=float)
    return (1 + returns).groupby(returns.index.to_period("M")).prod() - 1


def stage1_stats(portfolio: list[dict], ledger: list[dict]) -> dict[str, float] | None:
    monthly = time_weighted_monthly(portfolio, ledger)
    if monthly.empty:
        return None
    compounded = (1 + monthly).cumprod()
    return {"active_months": float(len(monthly)), "profitable_month_ratio": float((monthly > 0).mean()),
            "max_drawdown": float(abs((compounded / compounded.cummax() - 1).min())),
            "return_12m": float(compounded.iloc[-1] - 1)}


def stage1_pass(stats: dict[str, float] | None) -> bool:
    return bool(stats and stats["active_months"] >= 6 and stats["profitable_month_ratio"] >= .60
                and stats["max_drawdown"] <= .30 and stats["return_12m"] > 0)


def bhy(p_values: dict[str, float]) -> dict[str, float]:
    """Benjamini--Hochberg--Yekutieli adjusted q values."""
    keys = sorted(p_values, key=p_values.__getitem__)
    n = len(keys)
    if not n:
        return {}
    harmonic = sum(1 / i for i in range(1, n + 1))
    q, out = 1.0, {}
    for rank in range(n, 0, -1):
        key = keys[rank - 1]
        q = min(q, p_values[key] * n * harmonic / rank)
        out[key] = min(1.0, q)
    return out


def placebo_pvalue(actual: float, placebo: list[float]) -> float:
    """Frozen one-sided CT-Kapı p value (1,000 repetitions in the runner)."""
    return (1 + sum(value >= actual for value in placebo)) / (len(placebo) + 1)


def matched_btc_alpha(strategy: pd.Series, btc: pd.Series, exposure: pd.Series) -> dict[str, float]:
    """365-day exposure-matched BTC benchmark for CT-Kapı adım 6."""
    index = strategy.index.union(btc.index).sort_values()[-365:]
    return nw_alpha(strategy.reindex(index, fill_value=0.0),
                    btc.reindex(index, fill_value=0.0) * exposure.reindex(index, fill_value=0.0), periods=365)


def binance_symbol(coin: str) -> str:
    """The leader-approved informational mapping; HIP-3 and spot cannot map."""
    coin = str(coin)
    if coin.startswith("@") or ":" in coin or "/" in coin:
        return "yok"
    return ("1000" + coin[1:] if coin.startswith("k") else coin) + "USDT"


def write_binance_universe(root: Path, now: datetime | None = None, get=requests.get) -> tuple[set[str] | None, str]:
    now = now or datetime.now(UTC)
    path = root / "binance_vadeli.txt"
    source = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    try:
        response = get(source, timeout=30)
        if response.status_code in (403, 451):
            path.write_text(f"# {source} | {now.isoformat()} | erişim engeli: HTTP {response.status_code}\n", encoding="utf-8")
            return None, f"HTTP {response.status_code}"
        response.raise_for_status()
        symbols = sorted(x["symbol"] for x in response.json().get("symbols", [])
                         if x.get("status") == "TRADING" and x.get("contractType") == "PERPETUAL"
                         and x.get("quoteAsset") == "USDT")
        path.write_text(f"# {source} | {now.isoformat()}\n" + "\n".join(symbols) + "\n", encoding="utf-8")
        return set(symbols), "ok"
    except requests.RequestException as exc:
        path.write_text(f"# {source} | {now.isoformat()} | erişim hatası: {type(exc).__name__}\n", encoding="utf-8")
        return None, type(exc).__name__


def binance_availability(coin: str, symbols: set[str] | None) -> str:
    if binance_symbol(coin) == "yok":
        return "yok"
    return "bilinmiyor" if symbols is None else ("var" if binance_symbol(coin) in symbols else "yok")


def next_candle_open(candles: list[dict], event_ms: int, delay_minutes: int) -> float | None:
    """Use the first candle opening at/after the requested delay; never its close."""
    target = event_ms + delay_minutes * 60_000
    for candle in sorted(candles, key=lambda x: int(x.get("t", x.get("time", 0)))):
        if int(candle.get("t", candle.get("time", 0))) >= target:
            return float(candle.get("o", candle.get("open")))
    return None


def delayed_copy(fills: list[dict], candles: dict[str, list[dict]], account_value: float, delay_minutes: int,
                 funding: list[dict] | None = None) -> tuple[pd.Series | None, int]:
    """Net daily virtual-copy PnL, using delayed candle opens and exact stated friction."""
    if account_value <= 0:
        return None
    position: dict[str, float] = {}; missing = 0
    entry: dict[str, float] = {}
    rows: list[tuple[pd.Timestamp, float]] = []
    for fill in sorted(perp_fills(fills), key=lambda x: int(x.get("time", 0))):
        coin, size = str(fill.get("coin")), float(fill.get("sz", 0)) / account_value
        signed = -size if str(fill.get("side")) in {"A", "Sell", "sell"} else size
        price = float(fill.get("px", 0)) if delay_minutes == 0 else next_candle_open(candles.get(coin, []), int(fill["time"]), delay_minutes)
        if price is None:
            missing += 1; continue
        before = position.get(coin, 0.0)
        close = min(abs(before), abs(signed)) if before and before * signed < 0 else 0.0
        pnl = close * (price - entry.get(coin, price)) * (1 if before > 0 else -1)
        after = before + signed
        if before == 0 or before * signed > 0:
            entry[coin] = (entry.get(coin, price) * abs(before) + price * abs(signed)) / abs(after)
        elif after == 0 or before * after < 0:
            entry[coin] = price
        position[coin] = after
        rows.append((pd.to_datetime(fill["time"], unit="ms", utc=True), pnl - abs(signed * price) * (TAKER + SLIPPAGE)))
    for item in funding or []:
        rows.append((pd.to_datetime(item["time"], unit="ms", utc=True), _funding_amount(item) / account_value))
    if not rows:
        return None, missing
    frame = pd.DataFrame(rows, columns=["time", "pnl"]).set_index("time")
    return frame.pnl.resample("1D").sum(), missing


def candle_coverage(fills: list[dict], candles: dict[str, list[dict]]) -> float:
    """Notional-weighted share of fills whose coin has a candle at/after its time."""
    total = covered = 0.0
    for fill in perp_fills(fills):
        weight = abs(float(fill.get("px", 0)) * float(fill.get("sz", 0)))
        if not weight:
            continue
        total += weight
        if next_candle_open(candles.get(str(fill.get("coin")), []), int(fill["time"]), 0) is not None:
            covered += weight
    return covered / total if total else 0.0


class CandleCache:
    """One 1-hour `candleSnapshot` request per coin, shared by all addresses in a run."""
    def __init__(self, client: PublicClient, start_ms: int, end_ms: int):
        self.client, self.start_ms, self.end_ms, self.items = client, start_ms, end_ms, {}

    def get(self, coin: str) -> list[dict]:
        if coin not in self.items:
            self.items[coin] = self.client.candles(coin, self.start_ms, self.end_ms, interval="1h")
        return self.items[coin]

    def for_fills(self, fills: list[dict]) -> dict[str, list[dict]]:
        return {coin: self.get(coin) for coin in {str(row.get("coin")) for row in perp_fills(fills)}}


def randomize_trades(trades: list[dict], start: pd.Timestamp, end: pd.Timestamp, seed: int = 0) -> list[dict]:
    """Randomly re-place whole trades without overlap, retaining coin, side, size and holding time.

    It is intentionally a rejection sampler: an impossible placement is data
    insufficiency, never a shortened or overlapping placebo trade.
    """
    rng, placed = np.random.default_rng(seed), []
    ordered = list(trades)
    rng.shuffle(ordered)
    for trade in ordered:
        duration = pd.Timedelta(hours=max(1.0, float(trade["holding_hours"])))
        latest = end - duration
        if latest < start:
            raise ValueError("trade does not fit placebo window")
        span = int((latest - start).total_seconds() // 60)
        for _ in range(10_000):
            opened = start + pd.Timedelta(minutes=int(rng.integers(span + 1)))
            closed = opened + duration
            if all(closed <= item["open_time"] or opened >= item["close_time"] for item in placed):
                placed.append({**trade, "open_time": opened, "close_time": closed})
                break
        else:
            raise ValueError("non-overlapping placebo placement unavailable")
    return sorted(placed, key=lambda x: x["open_time"])


def _trade_templates(fills: list[dict], account_value: float) -> list[dict]:
    """Closed fills -> placebo templates; incomplete openings are deliberately excluded."""
    templates = []
    for trip in closed_round_trips(perp_fills(fills)):
        if trip["open_time"] is None or trip["holding_hours"] is None:
            continue
        opening = next((f for f in fills if str(f.get("coin")) == trip["coin"] and
                        pd.to_datetime(f["time"], unit="ms", utc=True) == trip["open_time"]), None)
        if opening:
            templates.append({"coin": trip["coin"], "side": opening.get("side", "B"),
                              "size_ratio": abs(float(opening.get("sz", 0))) / account_value,
                              "holding_hours": trip["holding_hours"]})
    return templates


def placebo_scores(fills: list[dict], candles: dict[str, list[dict]], account_value: float,
                   start: pd.Timestamp, end: pd.Timestamp, repetitions: int = 1000) -> list[float]:
    """1,000 non-overlapping hourly-candle placements using identical coin/direction/size/duration/cost."""
    templates = _trade_templates(fills, account_value)
    if not templates:
        return []
    scores = []
    for seed in range(repetitions):
        total = 0.0
        for trade in randomize_trades(templates, start, end, seed):
            begin = int(trade["open_time"].timestamp() * 1000)
            finish = int(trade["close_time"].timestamp() * 1000)
            entry, exit_ = next_candle_open(candles.get(trade["coin"], []), begin, 0), next_candle_open(candles.get(trade["coin"], []), finish, 0)
            if entry is None or exit_ is None:
                continue
            direction = -1 if str(trade["side"]) in {"A", "Sell", "sell"} else 1
            size = trade["size_ratio"]
            total += direction * size * (exit_ - entry) - size * (entry + exit_) * (TAKER + SLIPPAGE)
        scores.append(total)
    return scores


def copy_window_metrics(fills: list[dict], funding: list[dict], account_value: float, cache: CandleCache,
                        now_ms: int, active_months: int) -> tuple[dict[str, Any], dict[int, float | None]]:
    """Prepare documented steps 1--4 and all informational delay results for one trader."""
    start_200 = now_ms - 200 * 86_400_000
    recent = [row for row in fills if int(row.get("time", 0)) >= start_200]
    recent_funding = [row for row in funding if int(row.get("time", 0)) >= start_200]
    candles = cache.for_fills(recent)
    metrics = calculate_metrics(fills, funding=funding, account_value=account_value)
    metrics["active_months"] = active_months
    metrics["candle_coverage"] = candle_coverage(recent, candles)
    metrics["complete_data"] = metrics["candle_coverage"] >= .90
    nets: dict[int, float | None] = {}
    for delay in (0, 5, 30, 120):
        ledger, missing = delayed_copy(recent, candles, account_value, delay, recent_funding)
        nets[delay] = None if ledger is None else float(ledger.sum())
        metrics[f"gecikme_{delay}dk_eksik_dolum"] = missing
    return metrics, nets


def evidence_status(history_days: int, trades: int, active_months: int) -> str:
    return "Geçti" if history_days >= 180 and trades >= 50 and active_months >= 6 else "Yetersiz"


def gate_status(metrics: dict[str, Any], copy_net: float | None, placebo_p: float | None,
                alpha: dict[str, float] | None) -> dict[str, str]:
    """Classify documented CT-Kapı steps without silently converting missing data to failure."""
    out = {"adim1": "Geçti" if metrics.get("complete_data") else "Yetersiz"}
    out["adim2"] = evidence_status(int(metrics.get("history_days", 0)), int(metrics.get("closed_trades", 0)), int(metrics.get("active_months", 0)))
    if out["adim1"] != "Geçti" or out["adim2"] != "Geçti":
        out.update({f"adim{i}": "Yetersiz" for i in range(3, 8)})
        return out
    out["adim3"] = "Geçti" if metrics.get("median_holding_hours", 0) >= 1 and metrics.get("median_leverage", math.inf) <= 3 and metrics.get("max_leverage", math.inf) <= 10 and copy_net is not None and copy_net > 0 else "Kaldı"
    out["adim4"] = "Geçti" if metrics.get("profitable_month_ratio", 0) >= .60 and metrics.get("largest_trade_share", 1) < .30 and metrics.get("profit_factor_without_best", 0) > 1.2 and not metrics.get("martingale_signal") else "Kaldı"
    out["adim5"] = "Geçti" if placebo_p is not None and placebo_p <= .05 else "Kaldı"
    if alpha is None or not np.isfinite(alpha.get("alfa_yillik", np.nan)):
        out["adim6"] = "Yetersiz"
    elif alpha["alfa_yillik"] <= 0:
        out["adim6"] = "Kaldı"
    else:
        out["adim6"] = "Geçti" if alpha["nw_t"] >= 2 else "Yetersiz"
    return out


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="CT-Kapı v1 public-data stage-1 runner")
    parser.add_argument("--root", type=Path, default=Path("copytrade"))
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--yalniz-adim5", action="store_true")
    parser.add_argument("--devam", action="store_true")
    parser.add_argument("--birlestir", type=Path)
    args = parser.parse_args(argv)
    if args.birlestir:
        merge_shards(args.birlestir, args.root)
        return
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("shard index/count geçersiz")
    now, today = datetime.now(UTC), datetime.now(UTC).date().isoformat()
    out = args.root / "kapi" / today
    out.mkdir(parents=True, exist_ok=True)
    client, rows = PublicClient(limiter=RateLimiter(1000)), []
    leaders = prefilter(client.leaderboard())
    if args.yalniz_adim5:
        previous = sorted((args.root / "kapi").glob("*/sonuc.csv"))
        eligible = set(pd.read_csv(previous[-1]).query("adim1 == 'Geçti' and adim2 == 'Geçti' and adim3 == 'Geçti' and adim4 == 'Geçti'").address) if previous else set()
        leaders = [row for row in leaders if row["address"] in eligible]
    leaders = leaders[args.shard_index::args.shard_count]
    symbols, binance_note = write_binance_universe(out, now)
    start = int((now - timedelta(days=365)).timestamp() * 1000)
    start_200 = int((now - timedelta(days=200)).timestamp() * 1000)
    cache = CandleCache(client, start_200, int(now.timestamp() * 1000))
    previous_path = out / "sonuc.csv"
    previous_rows = pd.read_csv(previous_path).to_dict("records") if args.devam and previous_path.exists() else []
    done = {str(row["address"]) for row in previous_rows}
    rows = previous_rows
    for leader in leaders:
        address = leader["address"]
        if address in done:
            continue
        row: dict[str, Any] = {"address": address, "account_value": leader["accountValue"]}
        try:
            portfolio = client.portfolio(address)
            crude = stage1_stats(portfolio, [])
            if crude and crude["profitable_month_ratio"] >= .50 and crude["return_12m"] > 0:
                ledger = client.non_funding_ledger(address, start)
            else:
                ledger = []
            stats = stage1_stats(portfolio, ledger)
            row.update(stats or {})
            row["asama1"] = "Geçti" if stage1_pass(stats) else "Yetersiz"
            if row["asama1"] == "Geçti":
                fills = client.fills(address, start)
                funding = client.info({"type": "userFunding", "user": address, "startTime": start}, weight=20) or []
                metrics, nets = copy_window_metrics(fills, funding, float(leader["accountValue"]), cache,
                                                    int(now.timestamp() * 1000), int(stats["active_months"]))
                recent = [x for x in fills if int(x.get("time", 0)) >= start_200]
                candles = cache.for_fills(recent)
                actual = nets[30]
                scores = placebo_scores(recent, candles, float(leader["accountValue"]),
                                        pd.to_datetime(start_200, unit="ms", utc=True), pd.to_datetime(int(now.timestamp() * 1000), unit="ms", utc=True))
                p_value = placebo_pvalue(actual, scores) if actual is not None and len(scores) == 1000 else None
                # Daily 0-delay copy is the trader series; public BTC hourly closes build the matched comparator.
                own, _ = delayed_copy(fills, candles, float(leader["accountValue"]), 0, funding)
                btc = pd.Series({pd.to_datetime(x.get("t", x.get("time")), unit="ms", utc=True): float(x.get("c", x.get("o"))) for x in cache.get("BTC")}).sort_index()
                btc = btc.resample("1D").last().pct_change().fillna(0.0)
                exposure = pd.Series(1.0, index=own.index) if own is not None else pd.Series(dtype=float)
                alpha = matched_btc_alpha(own, btc, exposure) if own is not None else None
                statuses = gate_status(metrics, nets[30], p_value, alpha)
                row.update(metrics)
                row.update({"plasebo_p": p_value, **({"alfa_yillik": alpha["alfa_yillik"], "nw_t": alpha["nw_t"]} if alpha else {})})
                row.update({f"gecikme_{delay}dk_net": value for delay, value in nets.items()})
                row.update(statuses)
        except (RateLimitError, requests.RequestException, ValueError, TypeError, KeyError) as exc:
            row.update({"asama1": "Yetersiz", "sinif": "Yetersiz", "neden": "veri hatası: " + type(exc).__name__})
        rows.append(row)
        pd.DataFrame(rows).to_csv(out / "sonuc.csv", index=False)  # partial results survive a time limit
    pd.DataFrame(leaders).to_csv(out / "asama1.csv.gz", index=False, compression="gzip")
    passed = sum(r.get("asama1") == "Geçti" for r in rows)
    (out / "RAPOR.md").write_text(
        f"# CT-Kapı v1\n\n- Evren: {len(leaders)}\n- İşlenen: {len(rows)}\n- 1. aşamayı geçen: {passed}\n"
        f"- Binance listesi: {binance_note}\n- Gecikme saat başına yuvarlandı (üst sınır).\n- Karar önerisi yok.\n",
        encoding="utf-8")


def merge_shards(shards: Path, root: Path) -> None:
    """Merge partial artifacts even if some timeout jobs produced no CSV."""
    groups: dict[str, list[pd.DataFrame]] = {}
    for path in shards.rglob("sonuc.csv"):
        groups.setdefault(path.parent.name, []).append(pd.read_csv(path))
    for date, frames in groups.items():
        output = root / "kapi" / date
        output.mkdir(parents=True, exist_ok=True)
        table = pd.concat(frames, ignore_index=True).drop_duplicates("address", keep="last")
        table.to_csv(output / "sonuc.csv", index=False)
        pd.DataFrame({"address": table.address}).to_csv(output / "asama1.csv.gz", index=False, compression="gzip")
        (output / "RAPOR.md").write_text(f"# CT-Kapı v1\n\n- Evren: {len(table)}\n- İşlenen: {len(table)}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
