"""Registry for source-faithful strategy modules that do not fit the card DSL."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Mapping

from engine.kart_sinyal import KartPlan

MODULES = {
    "A1-027": "strategies.ozel.a1_027",
}


def has_strategy(card_id: str) -> bool:
    return card_id in MODULES


def build_plan(card: Mapping[str, Any], data: Mapping, **kwargs: Any) -> KartPlan:
    module_name = MODULES.get(str(card["id"]))
    if module_name is None:
        raise KeyError(f"ozel strateji modulu yok: {card['id']}")
    return import_module(module_name).build_plan(card, data, **kwargs)
