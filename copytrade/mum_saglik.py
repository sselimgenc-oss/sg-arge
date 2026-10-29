"""Mum (fiyat) akıl sağlığı (Argon A15): Hyperliquid saatlik mumlarında bozuk / sıçrama / boşluk / hacimsiz denetimi.

Karar değil ölçüdür; ağ ve dosya yok. Eşikler çağırandan gelir (``kurallar.yaml``: ``mum_sicrama_kat``, ``mum_medyan_pencere``); modülde varsayılan yok.
* ``bozuk``: sayısal olmayan/sonlu olmayan ya da pozitif olmayan fiyat, ``h < l``, ``o`` ya da ``c`` ``[l, h]`` dışında.
* ``sicrama``: açılış, önceki ``pencere`` **geçerli** mumun kapanış medyanından **oranla** ``sicrama_kat`` kat uzak: ``max(o/medyan, medyan/o) >= sicrama_kat``
  (yükselişler ve çöküşler simetrik yakalanır). Medyana yalnız geçerli (hiç sorunu olmayan) mumların kapanışı girer.
* ``bosluk``: ardışık iki mum arası 1 saatten büyük. * ``hacimsiz``: ``v == 0`` ve ``n == 0``.
"""
from __future__ import annotations

import math
import statistics
from typing import Any

BIR_SAAT_MS = 3_600_000


def _sayi(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def mum_kontrol(mumlar: list[dict], sicrama_kat: float, pencere: int) -> list[dict]:
    """Zamana göre sıralı mumlar için ``{'t', 'sorunlar', 'gecerli'}``; ``gecerli`` = hiç sorun yok."""
    ordered = sorted(mumlar, key=lambda m: m.get("t", 0))
    results: list[dict] = []
    closes: list[float] = []                      # yalnız geçerli mumların kapanışları
    for i, mum in enumerate(ordered):
        problems: list[str] = []
        o, c, h, l = (_sayi(mum.get(k)) for k in ("o", "c", "h", "l"))
        if None in (o, c, h, l) or min(o, c, h, l) <= 0 or h < l or not (l <= o <= h) or not (l <= c <= h):
            problems.append("bozuk")
        if o is not None and o > 0 and pencere > 0 and closes:
            median = statistics.median(closes[-pencere:])
            if max(o / median, median / o) >= sicrama_kat:
                problems.append("sicrama")
        if i and mum.get("t") is not None and ordered[i - 1].get("t") is not None and mum["t"] - ordered[i - 1]["t"] > BIR_SAAT_MS:
            problems.append("bosluk")
        v = _sayi(mum.get("v"))
        try:
            n = int(mum["n"]) if mum.get("n") is not None and not isinstance(mum.get("n"), bool) else None
        except (TypeError, ValueError):
            n = None
        if v == 0.0 and n == 0:
            problems.append("hacimsiz")
        if not problems:
            closes.append(c)
        results.append({"t": mum.get("t"), "sorunlar": problems, "gecerli": not problems})
    return results


def isaret_yasi(sonuclar: list[dict], an_ms: int) -> int | None:
    """``an_ms``'e kadar (dâhil) en son **geçerli** mumun yaşı (``an_ms − t``, ms); geçerli mum yoksa ``None``. ``sonuclar`` = ``mum_kontrol`` çıktısı."""
    valid = [r["t"] for r in sonuclar if r["gecerli"] and r["t"] is not None and r["t"] <= an_ms]
    return int(an_ms - max(valid)) if valid else None


def ozet(sonuclar: list[dict]) -> dict[str, Any]:
    """Her sorun türünün sayısı ve geçerli mum oranı (``gecerli_orani``; boş girdide 0.0)."""
    counts = {kind: sum(kind in r["sorunlar"] for r in sonuclar) for kind in ("bozuk", "sicrama", "bosluk", "hacimsiz")}
    ratio = sum(r["gecerli"] for r in sonuclar) / len(sonuclar) if sonuclar else 0.0
    return {**counts, "gecerli_orani": float(ratio)}
