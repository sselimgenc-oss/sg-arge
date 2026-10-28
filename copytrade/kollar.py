"""Ön kayıtlı kohort/kontrol seçimi ve silinmeyen olay kaydı."""
from __future__ import annotations
import json
import random
from pathlib import Path
from copytrade.kurallar import load_rules


def sec(adresler: list[str], puan: dict[str, float], n: int, tohum: str) -> dict:
    havuz = sorted(set(adresler))
    kohort = sorted(havuz, key=lambda a: (-puan.get(a, float("-inf")), a))[:n]
    kontrol = random.Random(tohum).sample(havuz, min(n, len(havuz)))
    return {"kohort": kohort, "kontrol": kontrol, "tohum": tohum}


def adaylar(sirali_havuz: list[str], rules: dict | None = None) -> list[str]:
    """Havuz puan sırasından ön kayıttaki en iyi %15 aday katını döndürür."""
    rules = rules or load_rules()
    import math
    return list(sirali_havuz)[:math.ceil(len(sirali_havuz) * float(rules["secim_aday_orani"]))]


def terfi(adres: str, sirali_havuz: list[str], golge_gun: int, kapanmis_islem: int,
          oda_sayisi: int | None = None, rules: dict | None = None) -> bool:
    """Odaya terfi: ≥3 hafta, ≥10 kapanmış işlem ve adayın oda sırası."""
    rules = rules or load_rules()
    oda = int(oda_sayisi or rules["secim_oda_min"])
    if not int(rules["secim_oda_min"]) <= oda <= int(rules["secim_oda_max"]):
        raise ValueError("oda sayısı ön kayıtlı 10–20 aralığında olmalı")
    return (golge_gun >= int(rules["golge_terfi_min_hafta"]) * 7
            and kapanmis_islem >= int(rules["golge_terfi_min_kapanmis_islem"])
            and adres in adaylar(sirali_havuz, rules)[:oda])


def cikis(adres: str, sirali_adaylar: list[str]) -> bool:
    """Oda üyesi aday katının alt yarısına düştüğünde çıkar."""
    import math
    return adres not in list(sirali_adaylar)[:math.ceil(len(sirali_adaylar) / 2)]


def olay_yaz(path: Path, olay: dict) -> None:
    """Arşiv `olay` türü için yalnız eklemeli JSONL ara kaydı."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(olay, ensure_ascii=False, sort_keys=True) + "\n")
