"""Hyperliquid public-data candidate scanner.

This package deliberately has no signing, wallet, or order-placement code.
"""

from .kurallar import evaluate
from .olcut import calculate_metrics

__all__ = ["calculate_metrics", "evaluate"]
