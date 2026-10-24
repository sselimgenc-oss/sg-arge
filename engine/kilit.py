"""Compatibility helpers after the U7 locked-period policy was removed."""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

def acik(env: Mapping[str, str] | None = None) -> bool:
    """Retained for callers during the transition; data is always available."""
    del env
    return True


def kes(frame: pd.DataFrame, *, env: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Return data unchanged; U7 removed the locked-period guard."""

    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is None:
        raise ValueError("kilit requires a timezone-aware DatetimeIndex")
    del env
    return frame


def uygula(data: Mapping[str, pd.DataFrame], *, env: Mapping[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Apply :func:`kes` to a symbol-to-frame mapping without mutating it."""

    return {symbol: kes(frame, env=env) for symbol, frame in data.items()}
