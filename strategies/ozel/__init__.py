"""Registry for source-faithful strategy modules that do not fit the card DSL."""

from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec
from typing import Any, Mapping

from engine.kart_sinyal import KartPlan

MODULES = {
    "A1-027": "strategies.ozel.a1_027",
    "RD-01": "strategies.ozel.rd_01",
    "RD-02": "strategies.ozel.rd_02",
}


def _tv_module(card_id: str) -> str | None:
    """U6: TV-<id> kartlari `strategies/ozel/tv_<id kucuk harf>.py` modulunden gelir (kayit gerekmez)."""
    if not str(card_id).startswith("TV-"):
        return None
    name = "strategies.ozel.tv_" + str(card_id)[3:].lower()
    return name if find_spec(name) is not None else None


def has_strategy(card_id: str) -> bool:
    return card_id in MODULES or _tv_module(card_id) is not None


def build_plan(card: Mapping[str, Any], data: Mapping, **kwargs: Any) -> KartPlan:
    module_name = MODULES.get(str(card["id"])) or _tv_module(str(card["id"]))
    if module_name is None:
        raise KeyError(f"ozel strateji modulu yok: {card['id']}")
    return import_module(module_name).build_plan(card, data, **kwargs)
