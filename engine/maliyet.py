"""FXDK maliyet modeli (T36b, docs/EVRENSEL_KURALLAR.md D17): dakikalik FX/CFD, Dukascopy bid/ask ortasi veri.

Veri bid/ask ortasi oldugundan bir tam tur (alis + satis) bir TAM spread oder: her yon yarim spread. Her yone ayrica
kayma eklenir. Tek yon maliyeti (fiyat birimi):

    tek_yon = carpan x (spread_pip x SPREAD_TEK_YON_ORANI + KAYMA_PIP) x pip_boyutu

Varsayilanlar: ``SPREAD_TEK_YON_ORANI = 0.5`` (tam tur = bir spread), ``KAYMA_PIP = 0.2`` (yon basina). Yorum "medyan spread +
0,2 pip kayma" metnine gore lider onayina aciktir; ``SPREAD_TEK_YON_ORANI = 1.0`` tek yonde tam spread (tam tur iki spread)
demektir ve tek sabitle degisir. ``carpan`` 1x/2x/3x stres icindir.

``spread_pip`` Dukascopy'den olculen medyan spread'dir (T36a); o gelene kadar parametre olarak verilir.
"""

from __future__ import annotations

from typing import Mapping

SPREAD_TEK_YON_ORANI = 0.5
KAYMA_PIP = 0.2

# 1 pip'in fiyat karsiligi. JPY ciftlerinde 0.01, digerlerinde 0.0001; endeks CFD'lerinde 1 pip = 1 endeks puani.
PIP_ISTISNA: Mapping[str, float] = {"USATECHIDXUSD": 1.0}


def pip_boyutu(sembol: str) -> float:
    """Price increment of one pip for ``sembol`` (Dukascopy name such as ``USDJPY`` or ``USATECHIDXUSD``)."""
    ad = sembol.upper().replace("/", "").replace("=X", "")
    if ad in PIP_ISTISNA:
        return float(PIP_ISTISNA[ad])
    return 0.01 if "JPY" in ad else 0.0001


def fxdk_tek_yon_maliyet(
    sembol: str,
    spread_pip: float,
    *,
    kayma_pip: float = KAYMA_PIP,
    carpan: float = 1.0,
    spread_orani: float = SPREAD_TEK_YON_ORANI,
) -> float:
    """Per-side, per-unit cost in price units for ``run_portfolio(cost_abs=...)``."""
    if spread_pip < 0 or kayma_pip < 0 or carpan < 0:
        raise ValueError("spread_pip, kayma_pip ve carpan negatif olamaz")
    return float(carpan) * (float(spread_pip) * float(spread_orani) + float(kayma_pip)) * pip_boyutu(sembol)
