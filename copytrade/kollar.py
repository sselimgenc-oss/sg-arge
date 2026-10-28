"""Ön kayıtlı kohort/kontrol seçimi ve silinmeyen olay kaydı."""
from __future__ import annotations
import json
import random
from pathlib import Path


def sec(adresler: list[str], puan: dict[str, float], n: int, tohum: str) -> dict:
    havuz = sorted(set(adresler))
    kohort = sorted(havuz, key=lambda a: (-puan.get(a, float("-inf")), a))[:n]
    kontrol = random.Random(tohum).sample(havuz, min(n, len(havuz)))
    return {"kohort": kohort, "kontrol": kontrol, "tohum": tohum}


def terfi(adres: str, sirali_adresler: list[str], n: int) -> bool:
    """Ön kayıttaki kat/kol girişi: adres ilk ``n`` aday içindeyse terfi eder."""
    return adres in list(sirali_adresler)[:n]


def cikis(adres: str, sirali_adresler: list[str], n: int) -> bool:
    """Histerezis: mevcut kol, ancak ilk ``2n`` dışına düşünce çıkar."""
    return adres not in list(sirali_adresler)[: 2 * n]


def olay_yaz(path: Path, olay: dict) -> None:
    """Arşiv `olay` türü için yalnız eklemeli JSONL ara kaydı."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(olay, ensure_ascii=False, sort_keys=True) + "\n")
