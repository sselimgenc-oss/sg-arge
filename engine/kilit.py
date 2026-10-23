"""U1 hidden-period guard.

U1 development data must not include the locked period after 2025-09-30.
The guard is deliberately opt-in only for opening the period, so an ordinary
run cannot accidentally use the final examination data.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping

import pandas as pd

KILIT_SONU = pd.Timestamp("2025-09-30 23:59:59.999999999", tz="UTC")
_LOGGER = logging.getLogger(__name__)


def acik(env: Mapping[str, str] | None = None) -> bool:
    """Return whether an explicit ``KILIT_AC=1`` override was supplied."""

    values = os.environ if env is None else env
    return values.get("KILIT_AC") == "1"


def kes(frame: pd.DataFrame, *, env: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Return data through the locked cutoff, unless the override is explicit.

    The input is never modified.  A timezone-aware index is required because
    all repository market data is normalized to UTC.
    """

    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is None:
        raise ValueError("kilit requires a timezone-aware DatetimeIndex")
    if acik(env):
        _LOGGER.warning("KILIT_AC=1: locked period opened through %s", KILIT_SONU.date())
        return frame
    return frame.loc[frame.index <= KILIT_SONU]


def uygula(data: Mapping[str, pd.DataFrame], *, env: Mapping[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Apply :func:`kes` to a symbol-to-frame mapping without mutating it."""

    return {symbol: kes(frame, env=env) for symbol, frame in data.items()}
