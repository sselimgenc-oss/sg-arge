"""Kopya defteri (docs/GOREV_TRADER_SECIMI.md 19–21): gerçek kopya ve plasebo AYNI fonksiyondan geçer.

Bir trader'ın dolumlarını, gecikmeli ve maliyetli olarak, kendi pozisyonumuz olarak yürütür:

* **Mum zaman sınırı:** yürütme fiyatı, hedef zamandan (dolum + gecikme) sonraki ilk saatlik mumun açılışıdır; o mum hedeften
  en çok 1 mum aralığı uzaktaysa (ya da yoksa) dolum "eksik"tir ve atlanır; sayısı döner (kapı satırı ``kopya_eksik`` işaretler).
* **Miras pozisyon:** pencereden önce açık olan pozisyonu azaltan/kapatan dolum, bizde olmayan bir pozisyonu kapatır; yeni ters
  pozisyon açmaz (``startPosition`` ile).
* **Açık pozisyonlar fiyatlanır:** gün sonu (UTC) ve pencere sonunda gerçekleşmemiş K/Z, mum açılışıyla işaretlenerek eğriye girer.
* **Funding kopyanın kendi pozisyonundan:** saatlik pozisyon × saatlik açılış fiyatı × funding oranı. Oran, trader'ın ``userFunding``
  satırlarındaki ``fundingRate`` değerinden okunur (trader'ın ``usdc`` ödemesi aktarılmaz); satırı olmayan saat için ±24 saatteki en yakın
  oran, o da yoksa coinin medyan oranı kullanılır.
* **Maliyet:** her dolumda taker + kayma (``kurallar.yaml``).

Tutarlar hesap değerine oranla (kesir) döner. Hiçbir eşik burada değildir; hepsi ``kurallar.yaml``'dadır.
"""
from __future__ import annotations

from bisect import bisect_right
from typing import Any

import numpy as np

from copytrade.kurallar import load_rules

HOUR = 3_600_000
DAY = 86_400_000


def cost_rate(rules: dict | None = None) -> float:
    rules = rules or load_rules()
    return float(rules["maliyet_taker"]) + float(rules["maliyet_kayma"])


class Market:
    """Coin başına saatlik mum açılış/kapanış dizileri; yürütme ve işaretleme fiyatları."""

    def __init__(self, candles: dict[str, list[dict]], interval_ms: int = HOUR):
        self.interval, self._raw, self._arrays = interval_ms, candles, {}

    def arrays(self, coin: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if coin not in self._arrays:
            rows = sorted((int(c.get("t", c.get("time", 0))), float(c.get("o", c.get("open"))),
                           float(c.get("c", c.get("close", c.get("o", c.get("open")))))) for c in self._raw.get(coin, []))
            self._arrays[coin] = (np.array([r[0] for r in rows], dtype=np.int64), np.array([r[1] for r in rows]), np.array([r[2] for r in rows]))
        return self._arrays[coin]

    def execution(self, coin: str, target_ms: int) -> tuple[int, float] | None:
        """Hedeften sonraki ilk mum (zaman, açılış); en çok 1 mum aralığı uzaktaysa ya da yoksa ``None`` (eksik dolum)."""
        times, opens, _ = self.arrays(coin)
        index = int(np.searchsorted(times, target_ms, side="left"))
        if index >= len(times) or int(times[index]) - target_ms > self.interval:
            return None
        return int(times[index]), float(opens[index])

    def mark(self, coin: str, at_ms: int) -> float | None:
        """``at_ms``'de veya önce açılan son mumun açılışı (gün sonu / pencere sonu işaretlemesi)."""
        times, opens, _ = self.arrays(coin)
        index = int(np.searchsorted(times, at_ms, side="right")) - 1
        return float(opens[index]) if index >= 0 else None


class FundingRates:
    """Trader'ın funding satırlarından coin başına saatlik oran tablosu (kopyanın funding'i bu orandan hesaplanır)."""

    def __init__(self, rows: list[dict] | None = None):
        self.by_coin: dict[str, dict[int, float]] = {}
        for row in rows or []:
            delta = row.get("delta", row)
            if not isinstance(delta, dict) or delta.get("fundingRate") is None or delta.get("coin") is None:
                continue
            hour = int(row["time"]) // HOUR * HOUR
            self.by_coin.setdefault(str(delta["coin"]), {})[hour] = float(delta["fundingRate"])
        self._cache: dict[str, tuple[np.ndarray, np.ndarray, float]] = {}

    def _table(self, coin: str) -> tuple[np.ndarray, np.ndarray, float]:
        if coin not in self._cache:
            items = sorted(self.by_coin.get(coin, {}).items())
            times = np.array([t for t, _ in items], dtype=np.int64)
            rates = np.array([r for _, r in items])
            self._cache[coin] = (times, rates, float(np.median(rates)) if len(rates) else 0.0)
        return self._cache[coin]

    def array(self, coin: str, hours: np.ndarray, max_gap_ms: int = 24 * HOUR) -> np.ndarray:
        """Verilen saatler için oran: tam saat; yoksa ±24 saatteki en yakın; yoksa coinin medyanı."""
        times, rates, median = self._table(coin)
        if not len(times):
            return np.zeros(len(hours))
        right = np.clip(np.searchsorted(times, hours, side="left"), 0, len(times) - 1)
        left = np.clip(right - 1, 0, len(times) - 1)
        near_right, near_left = np.abs(times[right] - hours), np.abs(times[left] - hours)
        pick = np.where(near_right <= near_left, right, left)
        distance = np.minimum(near_right, near_left)
        return np.where(distance <= max_gap_ms, rates[pick], median)


def copy_ledger(fills: list[dict], market: Market, account: float, delay_min: int, start_ms: int, end_ms: int,
                rates: FundingRates | None = None, rules: dict | None = None, daily: bool = False) -> dict[str, Any]:
    """Tek kopya defteri. ``fills``: kaynak dolumlar (coin, side A/B, sz, startPosition, time, px), zamana göre sıralı olmak zorunda değil.

    Döner: ``net`` (gerçekleşen − maliyet + funding + pencere sonu gerçekleşmemiş K/Z; hesap değerine oranla), ``missing`` (eksik dolum),
    ``executed``, ``costs``, ``funding``, ``realized``, ``unrealized_end``; ``daily=True`` ise ``daily`` (UTC gün → net, açık pozisyon
    fiyatlaması dahil), ``exposure`` (gün → açık pozisyonlu saat oranı) ve ``max_drawdown`` (kopya eğrisinin zirveden düşüşü, kesir).
    """
    if account <= 0:
        return {"net": None, "missing": 0, "executed": 0}
    rate = cost_rate(rules)
    held: dict[str, float] = {}       # kopya pozisyonu (coin birimi)
    entry: dict[str, float] = {}
    timeline: dict[str, list[tuple[int, float, float]]] = {}   # coin -> (yürütme zamanı, pozisyon sonrası, ortalama giriş)
    realized = costs = 0.0
    flow: dict[int, float] = {}
    missing = executed = 0
    for fill in sorted(fills, key=lambda f: int(f["time"])):   # kararlı sıralama: aynı ms'deki dolumlar API sırasını korur
        coin = str(fill["coin"])
        sign = -1.0 if str(fill.get("side")) in {"A", "Sell", "sell"} else 1.0
        size = float(fill["sz"])
        before_leader = float(fill.get("startPosition", 0))
        signed = sign * size
        own = held.get(coin, 0.0)
        if before_leader * signed < 0:    # trader'ın pozisyonunu azaltıyor / kapatıyor / ters çeviriyor
            leader_close = min(abs(before_leader), abs(signed))
            close = min(abs(own), leader_close) if own * before_leader > 0 else 0.0
            signed = sign * (close + max(0.0, abs(signed) - leader_close))
        if abs(signed) < 1e-12:
            continue
        if delay_min == 0:
            when, price = int(fill["time"]), float(fill.get("px", 0))
        else:
            found = market.execution(coin, int(fill["time"]) + delay_min * 60_000)
            if found is None:
                missing += 1
                continue
            when, price = found
        if when > end_ms or when < start_ms:
            continue
        executed += 1
        pnl = 0.0
        new_entry = entry.get(coin, price)
        if own * signed < 0:               # kopyada azaltma / kapatma / ters çevirme
            closing = min(abs(own), abs(signed))
            pnl = closing * (price - entry[coin]) * (1.0 if own > 0 else -1.0)
            after = own + signed
            new_entry = price if abs(signed) > abs(own) else entry[coin]
            if abs(after) < 1e-12:
                after = 0.0
        else:                              # açma / ekleme
            after = own + signed
            new_entry = (entry.get(coin, price) * abs(own) + price * abs(signed)) / abs(after)
        cost = abs(signed) * price * rate
        realized += (pnl - cost) / account
        costs += cost / account
        flow[when // DAY] = flow.get(when // DAY, 0.0) + (pnl - cost) / account
        held[coin], entry[coin] = after, new_entry
        timeline.setdefault(coin, []).append((when, after, new_entry))
        if after == 0.0:
            entry.pop(coin, None)
    # Pencere sonu / gün sonu işaretlemesi ve funding
    funding_total = 0.0
    funding_by_day: dict[int, float] = {}
    for coin, events in timeline.items():
        times, opens, _ = market.arrays(coin)
        if not len(times):
            continue
        et = np.array([e[0] for e in events], dtype=np.int64)
        ep = np.array([e[1] for e in events])
        lo, hi = int(np.searchsorted(times, events[0][0], side="left")), int(np.searchsorted(times, end_ms, side="right"))
        grid, px = times[lo:hi], opens[lo:hi]
        if len(grid) and rates is not None:
            idx = np.searchsorted(et, grid, side="right") - 1
            position = np.where(idx >= 0, ep[np.clip(idx, 0, None)], 0.0)
            payments = -position * px * rates.array(coin, grid) / account
            funding_total += float(payments.sum())
            if daily:
                for day, value in zip((grid // DAY).tolist(), payments.tolist()):
                    funding_by_day[day] = funding_by_day.get(day, 0.0) + value
    boundaries = [end_ms]
    if daily and timeline:
        first_day = min(flow) if flow else start_ms // DAY
        boundaries = [(d + 1) * DAY for d in range(first_day, end_ms // DAY)] + [end_ms]

    event_times = {coin: [e[0] for e in events] for coin, events in timeline.items()}

    def unrealized_at(moment: int) -> tuple[float, int]:
        total, unknown = 0.0, 0
        for coin, events in timeline.items():
            index = bisect_right(event_times[coin], moment) - 1
            if index < 0 or events[index][1] == 0.0:
                continue
            mark = market.mark(coin, moment)
            if mark is None:
                unknown += 1
                continue
            total += events[index][1] * (mark - events[index][2]) / account
        return total, unknown

    unrealized_end, unknown_end = unrealized_at(end_ms)
    result: dict[str, Any] = {"net": realized + funding_total + unrealized_end, "missing": missing, "executed": executed, "costs": costs,
                              "funding": funding_total, "realized": realized, "unrealized_end": unrealized_end, "mark_missing": unknown_end}
    if daily:
        days: dict[int, float] = {}
        previous_u = 0.0
        for boundary in boundaries:
            day = (boundary - 1) // DAY
            u, _ = unrealized_at(boundary)
            days[day] = days.get(day, 0.0) + flow.get(day, 0.0) + funding_by_day.get(day, 0.0) + (u - previous_u)
            previous_u = u
        import pandas as pd
        series = pd.Series({pd.Timestamp(d * DAY, unit="ms", tz="UTC").normalize(): v for d, v in sorted(days.items())})
        curve = 1.0 + series.cumsum()
        drawdown = float((1.0 - curve / curve.cummax().clip(lower=1.0)).max()) if len(curve) else 0.0
        hours = np.arange(start_ms // HOUR * HOUR, end_ms, HOUR)
        exposed = np.zeros(len(hours), dtype=bool)
        for events in timeline.values():
            et = np.array([e[0] for e in events], dtype=np.int64)
            ep = np.array([e[1] for e in events])
            idx = np.searchsorted(et, hours, side="right") - 1
            exposed |= np.where(idx >= 0, ep[np.clip(idx, 0, None)] != 0.0, False)
        by_day = pd.Series(exposed.astype(float), index=pd.to_datetime(hours, unit="ms", utc=True)).resample("1D").mean()
        result.update({"daily": series, "exposure": by_day, "max_drawdown": drawdown})
    return result
