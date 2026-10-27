"""CT-Kapı v1 helpers and public-data runner.

This module never authenticates, places orders, or reads wallets.  It deliberately
keeps every unavailable public input as ``Yetersiz`` rather than estimating it.
"""
from __future__ import annotations

import argparse
import json
import math
from bisect import bisect_left
from functools import lru_cache
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

from copytrade.kurallar import load_rules
from copytrade.olcut import _funding_amount, asset_class, calculate_metrics, closed_round_trips, perp_fills
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


def stage1_stats(portfolio: list[dict], ledger: list[dict] | None = None, days: int = 365) -> dict[str, float] | None:
    """1. aşama, Hyperliquid'in kendi kümülatif PnL serisinden (``allTime.pnlHistory``; yatırma/çekme içermez).

    Lider denetimi 2 (2026-10-27): hesap değeri serisinden zaman ağırlıklı getiri yatırma/çekme, spot↔perp ve
    örnekleme sıklığı yüzünden −%100 / +%10^40 gibi sonuçlar verdi; kullanılmaz. Kârlı ay = aylık PnL farkı > 0
    (payda gerekmez). Getiri ve düşüş, penceredeki pozitif hesap değerlerinin medyanına bölünür. ``ledger``
    geriye dönük uyumluluk içindir, kullanılmaz.
    """
    periods = {name: value for name, value in portfolio if isinstance(value, dict)} if portfolio else {}
    data = periods.get("allTime") or {}
    points = data.get("pnlHistory", [])
    if len(points) < 2:
        return None
    pnl = pd.Series({pd.to_datetime(t, unit="ms", utc=True): float(v) for t, v in points}).sort_index()
    values = pd.Series({pd.to_datetime(t, unit="ms", utc=True): float(v) for t, v in data.get("accountValueHistory", [])})
    since = pnl.index[-1] - pd.Timedelta(days=days)
    before = pnl[pnl.index < since]
    window = pnl[pnl.index >= since]
    if len(window) < 2:
        return None
    base = float(before.iloc[-1]) if len(before) else float(window.iloc[0])
    month_end = window.resample("ME").last().dropna()
    monthly = month_end.diff()
    if len(before):
        monthly.iloc[0] = month_end.iloc[0] - base
    else:
        monthly = monthly.iloc[1:]  # pencereden önce başlamıyorsa ilk ay kısmi ve tabansız
    active = monthly[monthly.abs() > 0]
    positive = values[(values.index >= since) & (values > 0)]
    if active.empty or positive.empty:
        return None
    denominator = float(positive.median())
    cumulative = window - base
    drawdown = float((cumulative.cummax() - cumulative).max()) / denominator
    span = (pnl.index[-1] - max(pnl.index[0], since)).days
    return {"active_months": float(len(active)), "profitable_month_ratio": float((active > 0).mean()),
            "max_drawdown": drawdown, "return_12m": float(active.sum()) / denominator, "pnl_history_days": float(span),
            # Hesabın tüm geçmişi (365 gün pencereyle kırpılmaz): genç aday ayrımı için.
            "account_age_days": float((pnl.index[-1] - pnl.index[0]).days)}


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


@lru_cache(maxsize=1)
def _binance_aliases() -> dict[str, str]:
    return {str(k).upper(): str(v).upper() for k, v in (load_rules().get("binance_takma_ad") or {}).items()}


def binance_symbol(coin: str, aliases: dict[str, str] | None = None) -> str:
    """Hyperliquid coin → Binance USDⓈ-M sembolü; spot eşlenemez (``yok``).

    HIP-3 (``dex:AD``): önek atılır, takma ad tablosu (kurallar.yaml ``binance_takma_ad``: GOLD→XAU, SILVER→XAG,
    BRENTOIL→BZ; diğerleri aynı ad) + ``USDT``. Sembolün Binance'te gerçekten bulunması ``binance_availability``'de.
    """
    coin = str(coin)
    if coin.startswith("@") or "/" in coin:
        return "yok"
    if ":" in coin:
        name = coin.split(":", 1)[1].upper()
        return (aliases if aliases is not None else _binance_aliases()).get(name, name) + "USDT"
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


def _circular_shift(items: list[dict], start: pd.Timestamp, end: pd.Timestamp, rng: np.random.Generator) -> list[dict]:
    """Bir coinin işlem dizisini bütün olarak rastgele dairesel kaydırır (sıra ve aralıklar korunur).

    Pencerenin sonunu aşan işlem pencerenin başına sarılır. Yalnız coin başına çakışmasız yerleşemeyen coin için kullanılır.
    """
    length = (end - start).total_seconds()
    shift = float(rng.uniform(0, length))
    moved = []
    for item in sorted(items, key=lambda x: x["open_time"]):
        duration = pd.Timedelta(hours=max(1.0, float(item["holding_hours"])))
        offset = ((item["open_time"] - start).total_seconds() + shift) % length
        opened = start + pd.Timedelta(seconds=offset)
        if opened + duration > end:
            opened = start  # sarma: pencere sonunu aşan işlem başa taşınır
        moved.append({**item, "open_time": opened, "close_time": opened + duration})
    return moved


def randomize_trades(trades: list[dict], start: pd.Timestamp, end: pd.Timestamp, seed: int = 0,
                     notes: list[str] | None = None) -> list[dict]:
    """Plasebo yerleştirmesi (v1.1): çakışma yasağı **coin başına**; farklı coinler aynı anda açık olabilir.

    Coin, yön, büyüklük ve süre korunur. Bir coinin işlemleri tekdüze rastgele, birbirine değmeden yerleştirilir
    (rastgele sıra + sıralı rastgele boşluklar; ret örneklemesi yok). Süreler toplamı pencereye sığmayan coin için
    işlem dizisi bütün olarak dairesel kaydırılır ve ``notes``'a yazılır (özgün açılış/kapanış saatleri gerekir).
    """
    rng, placed = np.random.default_rng(seed), []
    length = (end - start).total_seconds()
    by_coin: dict[str, list[dict]] = {}
    for trade in trades:
        by_coin.setdefault(str(trade["coin"]), []).append(trade)
    for coin in sorted(by_coin):
        items = by_coin[coin]
        durations = [max(1.0, float(x["holding_hours"])) * 3600 for x in items]
        if max(durations) > length:
            raise ValueError("trade does not fit placebo window")
        if sum(durations) > length:
            if any("open_time" not in x for x in items):
                raise ValueError("non-overlapping placebo placement unavailable")
            placed.extend(_circular_shift(items, start, end, rng))
            if notes is not None and f"{coin}: dairesel kaydırma" not in notes:
                notes.append(f"{coin}: dairesel kaydırma")
            continue
        order = rng.permutation(len(items))
        gaps = np.sort(rng.uniform(0, length - sum(durations), len(items)))
        used = 0.0
        for gap, index in zip(gaps, order):
            opened = start + pd.Timedelta(seconds=float(gap + used))
            placed.append({**items[index], "open_time": opened, "close_time": opened + pd.Timedelta(seconds=durations[index])})
            used += durations[index]
    return sorted(placed, key=lambda x: x["open_time"])


def _trade_templates(fills: list[dict], account_value: float) -> list[dict]:
    """Closed fills -> placebo templates; incomplete openings are deliberately excluded."""
    first: dict[tuple[str, int], dict] = {}
    for fill in fills:  # (coin, ms) -> o saniyedeki ilk dolum (eski kod her işlem için tüm dolumları tarıyordu: O(n²))
        first.setdefault((str(fill.get("coin")), int(fill["time"])), fill)
    templates = []
    for trip in closed_round_trips(perp_fills(fills)):
        if trip["open_time"] is None or trip["holding_hours"] is None:
            continue
        opening = first.get((trip["coin"], int(trip["open_time"].value // 1_000_000)))
        if opening:
            templates.append({"coin": trip["coin"], "side": opening.get("side", "B"),
                              "size_ratio": abs(float(opening.get("sz", 0))) / account_value,
                              "holding_hours": trip["holding_hours"],
                              "open_time": trip["open_time"], "close_time": trip["close_time"]})
    return templates


class _Opens:
    """Bir coinin mum açılışları: ``at(t)`` = t'de veya sonra açılan ilk mumun açılışı (kapanışı asla)."""
    def __init__(self, candles: list[dict]):
        rows = sorted((int(x.get("t", x.get("time", 0))), float(x.get("o", x.get("open")))) for x in candles)
        self.times, self.opens = [t for t, _ in rows], [o for _, o in rows]

    def at(self, ms: int) -> float | None:
        index = bisect_left(self.times, ms)
        return self.opens[index] if index < len(self.times) else None


def placebo_scores(fills: list[dict], candles: dict[str, list[dict]], account_value: float,
                   start: pd.Timestamp, end: pd.Timestamp, repetitions: int = 1000, delay_minutes: int = 0,
                   notes: list[str] | None = None) -> list[float]:
    """Plasebo skorları: coin başına çakışmasız saatlik-mum yerleştirmeleri, aynı coin/yön/büyüklük/süre/maliyet.

    ``delay_minutes``: giriş ve çıkışa gerçek kopyadakiyle aynı gecikme (intraday 30, swing 120 dk).
    """
    templates = _trade_templates(fills, account_value)
    if not templates:
        return []
    lookup = {coin: _Opens(candles.get(coin, [])) for coin in {t["coin"] for t in templates}}
    delay_ms = delay_minutes * 60_000
    scores = []
    for seed in range(repetitions):
        total = 0.0
        for trade in randomize_trades(templates, start, end, seed, notes if seed == 0 else None):
            begin = int(trade["open_time"].timestamp() * 1000) + delay_ms
            finish = int(trade["close_time"].timestamp() * 1000) + delay_ms
            entry, exit_ = lookup[trade["coin"]].at(begin), lookup[trade["coin"]].at(finish)
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
    for delay in (0, 5, 30, 120, 480):
        ledger, missing = delayed_copy(recent, candles, account_value, delay, recent_funding)
        nets[delay] = None if ledger is None else float(ledger.sum())
        metrics[f"gecikme_{delay}dk_eksik_dolum"] = missing
    return metrics, nets


# ---------------------------------------------------------------- CT-Kapı v1.1: tarz, katman, kıyas
def classify_style(median_holding_hours: float | None, rules: dict | None = None) -> str | None:
    """Medyan elde tutma süresine göre tarz: < 1 sa ``scalp``, 1–24 sa ``intraday``, ≥ 24 sa ``swing``."""
    if median_holding_hours is None or not np.isfinite(median_holding_hours):
        return None
    rules = rules or load_rules()
    if median_holding_hours < float(rules["tarz_scalp_alti_saat"]):
        return "scalp"
    return "swing" if median_holding_hours >= float(rules["tarz_swing_ustu_saat"]) else "intraday"


def delay_for_style(tarz: str | None, rules: dict | None = None, key: str = "kopya_gecikme_dk") -> int:
    """Tarza göre gecikme (dk). Scalp ve bilinmeyen tarz intraday gecikmesini kullanır (adım 3 zaten Kaldı)."""
    rules = rules or load_rules()
    return int(rules[key]["swing" if tarz == "swing" else "intraday"])


def short_trade_share(fills: list[dict], tarz: str | None, rules: dict | None = None) -> float | None:
    """Süresi biliniyor olan kapanmış işlemler arasında tarzın 'kısa' sınırından kısa olanların payı."""
    rules = rules or load_rules()
    limit = float(rules["kisa_islem_dk"]["swing" if tarz == "swing" else "intraday"]) / 60
    held = [t["holding_hours"] for t in closed_round_trips(perp_fills(fills)) if t["holding_hours"] is not None]
    return float(sum(h < limit for h in held) / len(held)) if held else None


def market_shares(fills: list[dict], symbols: set[str] | None = None) -> dict[str, float | None]:
    """İşlem hacminin varlık sınıfı payları (``pay_<sınıf>``) ve Binance'te karşılığı olan hacim payı."""
    volume: dict[str, float] = {}
    for fill in perp_fills(fills):
        volume[str(fill.get("coin"))] = volume.get(str(fill.get("coin")), 0.0) + abs(float(fill.get("px", 0)) * float(fill.get("sz", 0)))
    total = sum(volume.values())
    out: dict[str, float | None] = {f"pay_{name}": 0.0 for name in ("kripto", "hisse", "endeks", "emtia")}
    out["binance_payi"] = None
    if not total:
        return out
    for coin, value in volume.items():
        out[f"pay_{asset_class(coin)}"] = (out.get(f"pay_{asset_class(coin)}") or 0.0) + value / total
    if symbols is not None:
        out["binance_payi"] = sum(v for c, v in volume.items() if binance_availability(c, symbols) == "var") / total
    return out


def benchmark_kind(crypto_share: float, rules: dict | None = None) -> str:
    """Alfa kıyası: hacmin ≥ %50'si kripto ise BTC, değilse işlem yapılan varlıkların sepeti."""
    rules = rules or load_rules()
    return "BTC" if crypto_share >= float(rules["alfa_kripto_payi_esigi"]) else "sepet"


def daily_close_returns(candles: list[dict]) -> pd.Series:
    close = pd.Series({pd.to_datetime(x.get("t", x.get("time")), unit="ms", utc=True): float(x.get("c", x.get("o")))
                       for x in candles}).sort_index()
    return close.resample("1D").last().pct_change().fillna(0.0) if len(close) else pd.Series(dtype=float)


def basket_returns(candles: dict[str, list[dict]], coins: list[str]) -> pd.Series:
    """İşlem yapılan varlıkların eşit ağırlıklı al-tut sepeti: her gün mumu olan coinlerin getiri ortalaması."""
    series = [daily_close_returns(candles[c]) for c in coins if candles.get(c)]
    series = [x for x in series if len(x)]
    if not series:
        return pd.Series(dtype=float)
    return pd.concat(series, axis=1).mean(axis=1).fillna(0.0)


def katman(statuses: dict[str, str]) -> str:
    """kopyalanabilir = adım 1–7 Geçti; izleme_adayi = adım 1, 2, 3 Geçti; yok = diğer."""
    if all(statuses.get(f"adim{i}") == "Geçti" for i in range(1, 8)):
        return "kopyalanabilir"
    if all(statuses.get(f"adim{i}") == "Geçti" for i in (1, 2, 3)):
        return "izleme_adayi"
    return "yok"



def evidence_status(history_days: int, trades: int, active_months: int) -> str:
    return "Geçti" if history_days >= 180 and trades >= 50 and active_months >= 6 else "Yetersiz"


def gate_status(metrics: dict[str, Any], copy_net: float | None, placebo_p: float | None,
                alpha: dict[str, float] | None, rules: dict | None = None) -> dict[str, str]:
    """Classify documented CT-Kapı steps without silently converting missing data to failure.

    Adım 3 (v1.1): tarz (scalp → Kaldı), kısa işlem payı, kaldıraç ve ``copy_net`` — tarzın gecikmesindeki sanal
    kopya neti (intraday 30 dk, swing 120 dk), çağıran doğru gecikmeyi verir.
    """
    rules = rules or load_rules()
    out = {"adim1": "Geçti" if metrics.get("complete_data") else "Yetersiz"}
    out["adim2"] = evidence_status(int(metrics.get("history_days", 0)), int(metrics.get("closed_trades", 0)), int(metrics.get("active_months", 0)))
    if out["adim1"] != "Geçti" or out["adim2"] != "Geçti":
        out.update({f"adim{i}": "Yetersiz" for i in range(3, 8)})
        return out
    def value(name: str, missing: float) -> float:
        """Eksik ya da hesaplanamayan (None/NaN) ölçüt şartı sağlamaz; TypeError'a (veri hatası) düşmez."""
        number = metrics.get(name)
        return missing if number is None or not np.isfinite(number) else float(number)

    tarz = metrics.get("tarz") or classify_style(metrics.get("median_holding_hours"), rules)
    short = metrics.get("kisa_islem_payi")
    out["adim3"] = "Geçti" if (tarz in {"intraday", "swing"}
                               and (short is None or short <= float(rules["kisa_islem_payi_max"]))
                               and value("median_leverage", math.inf) <= float(rules["kapi_max_medyan_kaldirac"])
                               and value("max_leverage", math.inf) <= float(rules["kapi_max_kaldirac"])
                               and copy_net is not None and copy_net > 0) else "Kaldı"
    out["adim4"] = "Geçti" if (value("profitable_month_ratio", 0) >= .60 and value("largest_trade_share", 1) < .30
                               and value("profit_factor_without_best", 0) > 1.2 and not metrics.get("martingale_signal")) else "Kaldı"
    out["adim5"] = "Geçti" if placebo_p is not None and placebo_p <= float(rules["plasebo_p_max"]) else "Kaldı"
    if alpha is None or not np.isfinite(alpha.get("alfa_yillik", np.nan)):
        out["adim6"] = "Yetersiz"
    elif alpha["alfa_yillik"] <= 0:
        out["adim6"] = "Kaldı"
    else:
        out["adim6"] = "Geçti" if alpha["nw_t"] >= 2 else "Yetersiz"
    return out


def evaluate_address(leader: dict, client: PublicClient, cache: CandleCache, now: datetime, start: int, start_200: int,
                     symbols: set[str] | None, rules: dict, yalniz_adim5: bool = False) -> dict[str, Any]:
    """Tek adres için 1. aşama + adım 1–6 (adım 7 ve katman birleştirmede). ``yalniz_adim5``: plaseboyu adım 3–4'e
    bakmadan hesaplar (hızlı koşu; satırın adım değerleri yine kurallara göre kalır)."""
    address = leader["address"]
    row: dict[str, Any] = {"address": address, "account_value": leader["accountValue"]}
    try:
        portfolio = client.portfolio(address)
        stats = stage1_stats(portfolio)
        row.update(stats or {})
        row["asama1"] = "Geçti" if stage1_pass(stats) else "Yetersiz"
        if row["asama1"] != "Geçti":
            return row
        account, now_ms = float(leader["accountValue"]), int(now.timestamp() * 1000)
        fills = client.fills(address, start)
        funding = client.info({"type": "userFunding", "user": address, "startTime": start}, weight=20) or []
        metrics, nets = copy_window_metrics(fills, funding, account, cache, now_ms, int(stats["active_months"]))
        metrics["history_days"] = max(int(metrics.get("history_days", 0)), int(stats["pnl_history_days"]))
        recent = [x for x in fills if int(x.get("time", 0)) >= start_200]
        candles = cache.for_fills(recent)
        tarz = classify_style(metrics.get("median_holding_hours"), rules)
        metrics["tarz"], metrics["kisa_islem_payi"] = tarz, short_trade_share(fills, tarz, rules)
        delay = delay_for_style(tarz, rules)
        actual = nets.get(delay)
        pre = gate_status(metrics, actual, None, None, rules)
        p_value, notes = None, []
        if actual is not None and (yalniz_adim5 or all(pre[f"adim{i}"] == "Geçti" for i in range(1, 5))):
            repetitions = int(rules["plasebo_tekrar"])
            try:
                scores = placebo_scores(recent, candles, account, pd.to_datetime(start_200, unit="ms", utc=True),
                                        pd.to_datetime(now_ms, unit="ms", utc=True), repetitions, delay, notes)
                if len(scores) == repetitions:
                    p_value = placebo_pvalue(actual, scores)
                else:
                    row["plasebo_hata"] = "yerleştirilecek kapanmış işlem yok"
            except ValueError as exc:
                row["plasebo_hata"] = str(exc)[:80]
        if notes:
            row["plasebo_not"] = "; ".join(notes)[:200]
        shares = market_shares(fills, symbols)
        kind = benchmark_kind(shares["pay_kripto"] or 0.0, rules)
        own, _ = delayed_copy(fills, candles, account, 0, funding)
        bench = (daily_close_returns(cache.get("BTC")) if kind == "BTC"
                 else basket_returns(candles, sorted({str(f.get("coin")) for f in perp_fills(recent)})))
        # Maruziyet: kopya defterinde PnL/funding hareketi olan gün = pozisyonda (sabit 1 değil).
        exposure = (own.abs() > 0).astype(float) if own is not None else pd.Series(dtype=float)
        alpha = matched_btc_alpha(own, bench, exposure) if own is not None and len(bench) else None
        statuses = gate_status(metrics, actual, p_value, alpha, rules)
        row.update(metrics)
        row.update(shares)
        row.update({"plasebo_p": p_value, "alfa_kiyas": kind, "kapi_gecikme_dk": delay,
                    **({"alfa_yillik": alpha["alfa_yillik"], "nw_t": alpha["nw_t"]} if alpha else {})})
        row.update({f"gecikme_{d}dk_net": value for d, value in nets.items()})
        if tarz == "swing" and (nets.get(delay_for_style(tarz, rules, "stres_gecikme_dk")) or 0) < 0:
            row["not"] = "gece riskli"
        row.update(statuses)
    except (RateLimitError, requests.RequestException, ValueError, TypeError, KeyError) as exc:
        row.setdefault("asama1", "Yetersiz")  # 1. aşama sonucu hesaplandıysa korunur
        row.update({"sinif": "Yetersiz", "neden": "veri hatası: " + type(exc).__name__ + ": " + str(exc)[:60]})
    return row


def missing_addresses(leaders: list[dict], reference: pd.DataFrame | None) -> list[dict]:
    """Aynı günün sonuc.csv'sinde olmayan veya ``neden`` alanı "veri hatası" olan adresler (``--eksikleri-tamamla``)."""
    if reference is None or reference.empty:
        return leaders
    bad = reference["neden"].fillna("").astype(str).str.startswith("veri hatası") if "neden" in reference else False
    ok = set(reference.loc[~bad, "address"].astype(str)) if "neden" in reference else set(reference["address"].astype(str))
    return [row for row in leaders if str(row["address"]) not in ok]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="CT-Kapı v1.1 public-data stage-1 runner")
    parser.add_argument("--root", type=Path, default=Path("copytrade"))
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--yalniz-adim5", action="store_true")
    parser.add_argument("--eksikleri-tamamla", action="store_true",
                        help="aynı günün sonuc.csv'sinde olmayan veya 'veri hatası' olan adresleri işle")
    parser.add_argument("--devam", action="store_true")
    parser.add_argument("--birlestir", type=Path)
    args = parser.parse_args(argv)
    if args.birlestir:
        merge_shards(args.birlestir, args.root)
        return
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("shard index/count geçersiz")
    rules = load_rules()
    now, today = datetime.now(UTC), datetime.now(UTC).date().isoformat()
    out = args.root / "kapi" / today
    out.mkdir(parents=True, exist_ok=True)
    client = PublicClient(limiter=RateLimiter(1000))
    leaders = prefilter(client.leaderboard())
    evren = len(leaders)
    (out / "evren.json").write_text(json.dumps({"evren": evren}), encoding="utf-8")
    previous_path = out / "sonuc.csv"
    if args.yalniz_adim5:
        previous = sorted((args.root / "kapi").glob("*/sonuc.csv"))
        eligible = set(pd.read_csv(previous[-1]).query("adim1 == 'Geçti' and adim2 == 'Geçti' and adim3 == 'Geçti' and adim4 == 'Geçti'").address) if previous else set()
        leaders = [row for row in leaders if row["address"] in eligible]
    if args.eksikleri_tamamla:
        leaders = missing_addresses(leaders, pd.read_csv(previous_path) if previous_path.exists() else None)
    leaders = leaders[args.shard_index::args.shard_count]
    symbols, binance_note = write_binance_universe(out, now)
    start = int((now - timedelta(days=365)).timestamp() * 1000)
    start_200 = int((now - timedelta(days=200)).timestamp() * 1000)
    cache = CandleCache(client, start_200, int(now.timestamp() * 1000))
    previous_rows = pd.read_csv(previous_path).to_dict("records") if args.devam and previous_path.exists() else []
    done = {str(row["address"]) for row in previous_rows}
    rows = previous_rows
    for number, leader in enumerate(leaders, 1):
        if leader["address"] in done:
            continue
        rows.append(evaluate_address(leader, client, cache, now, start, start_200, symbols, rules, args.yalniz_adim5))
        if number % 10 == 0 or len(leaders) <= 20:  # Actions günlüğünde ilerleme
            last = rows[-1]
            print(f"{number}/{len(leaders)} {leader['address']} asama1={last.get('asama1')} plasebo_p={last.get('plasebo_p')} "
                  f"hata={last.get('plasebo_hata') or last.get('neden') or ''}", flush=True)
        pd.DataFrame(rows).to_csv(out / "sonuc.csv", index=False)  # partial results survive a time limit
    pd.DataFrame(leaders).to_csv(out / "asama1.csv.gz", index=False, compression="gzip")
    passed = sum(r.get("asama1") == "Geçti" for r in rows)
    (out / "RAPOR.md").write_text(
        f"# CT-Kapı v1.1\n\n- Evren: {evren}\n- Bu parçada işlenen: {len(rows)}\n- 1. aşamayı geçen: {passed}\n"
        f"- Binance listesi: {binance_note}\n- Gecikme saat başına yuvarlandı (üst sınır).\n- Karar önerisi yok.\n",
        encoding="utf-8")


def _md(frame: pd.DataFrame) -> str:
    """Bağımlılıksız Markdown tablo (tabulate yok)."""
    cells = lambda v: f"{v:.3g}" if isinstance(v, float) else str(v)
    lines = ["| " + " | ".join(frame.columns) + " |", "|" + "---|" * len(frame.columns)]
    lines += ["| " + " | ".join(cells(v) for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join(lines)


def finalize(table: pd.DataFrame, rules: dict | None = None) -> pd.DataFrame:
    """Parçalar birleştikten sonra adım 7 (BHY, plaseboya ulaşan herkes), nihai sınıf, katman ve genç aday."""
    rules = rules or load_rules()
    table = table.copy()
    steps = [f"adim{i}" for i in range(1, 7)]
    for col in steps + ["plasebo_p", "nw_t", "asama1", "sinif"]:
        if col not in table:
            table[col] = np.nan
    reached = table["plasebo_p"].notna()
    q = bhy({a: float(p) for a, p in zip(table.loc[reached, "address"], table.loc[reached, "plasebo_p"])})
    table["bhy_q"] = table["address"].map(q)
    all_pass = (table[steps] == "Geçti").all(axis=1)
    table["adim7"] = np.where(table["bhy_q"].notna(), np.where(table["bhy_q"] <= .10, "Geçti", "Kaldı"), "Yetersiz")

    def klass(row) -> str:
        if row.get("asama1") != "Geçti":
            return "Yetersiz"
        values = [row.get(f"adim{i}") for i in range(1, 8)]
        if "Kaldı" in values:
            return "Kaldı"
        return "Geçti" if all(v == "Geçti" for v in values) else "Yetersiz"

    table["sinif"] = table.apply(klass, axis=1)
    table.loc[~all_pass & (table["sinif"] == "Geçti"), "sinif"] = "Yetersiz"
    table["katman"] = table.apply(lambda row: katman({f"adim{i}": row.get(f"adim{i}") for i in range(1, 8)}), axis=1)
    for col in ("history_days", "account_age_days"):
        if col not in table:
            table[col] = np.nan
    table["gecmis_gun"] = table[["history_days", "account_age_days"]].max(axis=1)
    minimum, young = float(rules["min_history_days"]), float(rules["genc_aday_gun"])
    table["genc_aday"] = (table["gecmis_gun"] >= minimum) & (table["gecmis_gun"] < young)
    return table


def funnel_report(table: pd.DataFrame, evren: int | None) -> str:
    """RAPOR.md gövdesi: işlenen / evren, huni tarza ve katmana göre ayrı."""
    total = len(table)
    lines = [f"- İşlenen / evren: {total} / {evren if evren else '?'}"
             + (f" (%{100 * total / evren:.1f}; hedef ≥ %98: {'✓' if total / evren >= .98 else '✗'})" if evren else ""),
             f"- 1. aşama (kâr eğrisi) geçti: {(table.asama1 == 'Geçti').sum()}",
             f"- Veri hatası: {table.get('neden', pd.Series(dtype=str)).fillna('').astype(str).str.startswith('veri hatası').sum()}",
             "- Sınıf: " + ", ".join(f"{k} {v}" for k, v in table.sinif.value_counts().items())]
    tarz = table["tarz"].fillna("belirsiz") if "tarz" in table else pd.Series("belirsiz", index=table.index)
    rows = []
    for name in ["intraday", "swing", "scalp", "belirsiz"]:
        part = table[tarz == name]
        if part.empty:
            continue
        rows.append({"tarz": name, "adres": len(part), **{f"adım {i}": int((part.get(f"adim{i}") == "Geçti").sum()) for i in range(1, 8)},
                     "izleme_adayi": int((part.katman == "izleme_adayi").sum()),
                     "kopyalanabilir": int((part.katman == "kopyalanabilir").sum())})
    return ("\n".join(lines) + "\n\n## Huni — tarza göre (geçen sayısı)\n\n" + (_md(pd.DataFrame(rows)) if rows else "_Veri yok._")
            + "\n\n## Katman\n\n" + "\n".join(f"- {k}: {v}" for k, v in table.katman.value_counts().items()))


def merge_shards(shards: Path, root: Path) -> None:
    """Merge partial artifacts even if some timeout jobs produced no CSV.

    Aynı günün mevcut ``sonuc.csv``'si (ör. veri dalından) önce okunur; parçalardaki satırlar onu geçersiz kılar
    (``--eksikleri-tamamla`` ve hızlı koşu böyle birleşir).
    """
    groups: dict[str, list[pd.DataFrame]] = {}
    evren: dict[str, int] = {}
    for path in sorted(shards.rglob("sonuc.csv")):
        groups.setdefault(path.parent.name, []).append(pd.read_csv(path))
    for path in shards.rglob("evren.json"):
        evren[path.parent.name] = max(evren.get(path.parent.name, 0), int(json.loads(path.read_text(encoding="utf-8"))["evren"]))
    for date, frames in groups.items():
        output = root / "kapi" / date
        output.mkdir(parents=True, exist_ok=True)
        existing = output / "sonuc.csv"
        if existing.exists():
            old = pd.read_csv(existing)
            if "katman" in old:  # v1.1 öncesi (katman sütunu yok) sonuç yeni kurallarla karıştırılmaz
                frames = [old] + frames
        if not evren.get(date) and (output / "evren.json").exists():
            evren[date] = int(json.loads((output / "evren.json").read_text(encoding="utf-8"))["evren"])
        table = pd.concat(frames, ignore_index=True).drop_duplicates("address", keep="last")
        table = finalize(table)
        table.to_csv(output / "sonuc.csv", index=False)
        pd.DataFrame({"address": table.address}).to_csv(output / "asama1.csv.gz", index=False, compression="gzip")
        if evren.get(date):
            (output / "evren.json").write_text(json.dumps({"evren": evren[date]}), encoding="utf-8")
        cols = [c for c in ["address", "tarz", "katman", "genc_aday", "profitable_month_ratio", "max_drawdown", "return_12m", "closed_trades",
                            "median_holding_hours", "median_leverage", "kisa_islem_payi", "gecikme_30dk_net", "gecikme_120dk_net",
                            "gecikme_480dk_net", "plasebo_p", "nw_t", "alfa_kiyas", "bhy_q", "adim3", "adim4", "adim5", "adim6", "adim7", "sinif"] if c in table]
        near = table[table.get("adim2") == "Geçti"].sort_values("nw_t", ascending=False)[cols].head(15)
        (output / "RAPOR.md").write_text("# CT-Kapı v1.1\n\n" + funnel_report(table, evren.get(date))
                                         + "\n\n## Adım 2'yi geçenler (alfa t'ye göre ilk 15)\n\n" + _md(near)
                                         + "\n\nGecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
