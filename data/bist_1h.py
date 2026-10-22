"""Deterministic session normalisation and quality gate for Yahoo BIST 1h bars."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

BIST_TIMEZONE = "Europe/Istanbul"
SESSION_OPEN_MINUTE = 10 * 60
SESSION_CLOSE_MINUTE = 18 * 60
SUSPICIOUS_ZERO_VOLUME_LIMIT = 0.01


@dataclass(frozen=True)
class Bist1HQuality:
    rows: int
    outside_session: int
    zero_volume: int
    zero_volume_flat: int
    zero_volume_changed: int

    @property
    def suspicious_zero_volume_rate(self) -> float:
        return self.zero_volume_changed / self.rows if self.rows else 1.0

    @property
    def passed(self) -> bool:
        return (
            self.rows > 0
            and self.outside_session == 0
            and self.suspicious_zero_volume_rate < SUSPICIOUS_ZERO_VOLUME_LIMIT
        )


def _aggregate_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    """Merge bars mapped to one session label without inventing observations."""

    grouped = frame.groupby(level=0, sort=True)
    return grouped.agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )


def normalize_bist_1h(frame: pd.DataFrame) -> pd.DataFrame:
    """Align Yahoo's half-hour labels to BIST session boundaries.

    Yahoo labels BIST hourly bars on ``09:30, 10:30, ...`` local time.  These
    are source interval labels, not a three-hour timezone error.  They are
    represented here by their next whole-hour session boundary.  A Yahoo
    closing-auction observation at 18:00--18:10 maps to 18:00 and is merged
    with a possible 17:30 bar using first/max/min/last/sum OHLCV aggregation.
    Truly out-of-session observations are discarded; missing bars are never
    filled and zero volume is never fabricated.
    """

    if frame.empty:
        return frame.copy()
    clean = frame.copy()
    index = pd.DatetimeIndex(clean.index)
    if index.tz is None:
        index = index.tz_localize("UTC")
    else:
        index = index.tz_convert("UTC")
    local = index.tz_convert(BIST_TIMEZONE)
    minute_of_day = local.hour * 60 + local.minute

    yahoo_half_hour = local.minute == 30
    continuous_label = (minute_of_day >= 9 * 60 + 30) & (minute_of_day < SESSION_CLOSE_MINUTE)
    closing_auction = (minute_of_day >= SESSION_CLOSE_MINUTE) & (minute_of_day <= 18 * 60 + 10)
    already_aligned = (
        (local.minute == 0)
        & (minute_of_day >= SESSION_OPEN_MINUTE)
        & (minute_of_day <= SESSION_CLOSE_MINUTE)
    )
    keep = (yahoo_half_hour & continuous_label) | closing_auction | already_aligned
    clean = clean.loc[keep].copy()
    local = local[keep]
    yahoo_half_hour = yahoo_half_hour[keep]

    closing_kept = closing_auction[keep]
    target = pd.DatetimeIndex(
        [
            timestamp.replace(hour=18, minute=0, second=0, microsecond=0, nanosecond=0)
            if is_closing
            else timestamp.ceil("h") if is_half_hour else timestamp
            for timestamp, is_half_hour, is_closing in zip(
                local, yahoo_half_hour, closing_kept, strict=True
            )
        ]
    )
    clean.index = target.tz_convert("UTC")
    clean.index.name = "timestamp"
    return _aggregate_ohlcv(clean).sort_index()


def quality(frame: pd.DataFrame) -> Bist1HQuality:
    """Measure the cleaned series; changed-price zero-volume bars are suspicious."""

    if frame.empty:
        return Bist1HQuality(0, 0, 0, 0, 0)
    local = pd.DatetimeIndex(frame.index).tz_convert(BIST_TIMEZONE)
    minute = local.hour * 60 + local.minute
    outside = int(((minute < SESSION_OPEN_MINUTE) | (minute > SESSION_CLOSE_MINUTE)).sum())
    zero = pd.to_numeric(frame["volume"], errors="coerce").fillna(0).le(0)
    flat = frame[["open", "high", "low", "close"]].nunique(axis=1).eq(1)
    return Bist1HQuality(
        rows=len(frame),
        outside_session=outside,
        zero_volume=int(zero.sum()),
        zero_volume_flat=int((zero & flat).sum()),
        zero_volume_changed=int((zero & ~flat).sum()),
    )


def normalize_market_1h(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    """Limit BIST-specific session semantics to BIST; every other market is untouched."""

    return normalize_bist_1h(frame) if market.upper() == "BIST30" else frame


def quality_gate(frames: dict[str, pd.DataFrame]) -> tuple[bool, dict[str, Bist1HQuality]]:
    """Pass only when every symbol has clean session labels and <1% suspicious bars."""

    measurements = {symbol: quality(frame) for symbol, frame in frames.items()}
    return bool(measurements) and all(item.passed for item in measurements.values()), measurements
