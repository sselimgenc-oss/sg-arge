"""Pozisyon mutabakatı ve yetim pozisyon tespiti (Argon A13).

Kopya defterindeki (izleme motorunun dolumlardan türettiği) pozisyonlar ile Hyperliquid ``clearinghouseState`` yanıtını karşılaştırır.
**Yalnız raporlar**: hiçbir pozisyon otomatik kapatılmaz, defter değiştirilmez. Saf bellek içi hesap (ağ ve dosya yok).
Tolerans çağırandan gelir (``kurallar.yaml``: ``mutabakat_goreli_tolerans``, ``mutabakat_mutlak_tolerans``); modülde varsayılan eşik yoktur.

Durumlar: ``uyumlu`` (ikisi de kapalı ya da aynı yönde ve |fark| ≤ max(mutlak, göreli × |defter|); sınır dâhil), ``yetim`` (defterde açık, borsada kapalı),
``eksik`` (borsada açık, defterde kapalı), ``yon_farki`` (zıt işaret), ``boy_farki`` (aynı yön, fark tolerans üstü). ``fark = defter − borsa``.
"""
from __future__ import annotations

import math
from typing import Any

import pandas as pd

DURUMLAR = ("uyumlu", "yetim", "eksik", "yon_farki", "boy_farki")


def _sonlu(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def borsa_pozisyonlari(borsa_durumu: dict | None) -> tuple[dict[str, float], int]:
    """``clearinghouseState`` → ({coin: işaretli büyüklük}, bozuk satır sayısı).

    Sıfır büyüklükler elenir; aynı coinin satırları netleştirilir (net sıfırsa elenir). Eksik/geçersiz/sayısal olmayan (nan, inf) satırlar
    atlanır ve **sayılır**; ``assetPositions`` liste değilse boş sonuç (bozuk 0)."""
    rows = borsa_durumu.get("assetPositions") if isinstance(borsa_durumu, dict) else None
    if not isinstance(rows, list):
        return {}, 0
    net: dict[str, float] = {}
    broken = 0
    for row in rows:
        position = row.get("position", row) if isinstance(row, dict) else None
        coin = position.get("coin") if isinstance(position, dict) else None
        size = _sonlu(position.get("szi")) if isinstance(position, dict) else None
        if not isinstance(coin, str) or not coin.strip() or size is None:
            broken += 1
            continue
        net[coin.strip()] = net.get(coin.strip(), 0.0) + size
    return {coin: size for coin, size in net.items() if size != 0.0}, broken


def mutabakat(defter_pozisyon: dict[str, float] | None, borsa_durumu: dict | None, goreli_tolerans: float,
              mutlak_tolerans: float) -> tuple[list[dict[str, Any]], int]:
    """Coin başına satırlar (``coin, defter, borsa, fark, durum``; coin adına göre sıralı) ve atlanan bozuk satır sayısı
    (borsa yanıtındaki bozuk satırlar + defterdeki geçersiz girdiler). Negatif tolerans ``ValueError``."""
    if goreli_tolerans < 0.0 or mutlak_tolerans < 0.0:
        raise ValueError("Goreli ve mutlak tolerans degerleri negatif olamaz.")
    book: dict[str, float] = {}
    broken = 0
    for coin, value in (defter_pozisyon or {}).items():
        number = _sonlu(value)
        if isinstance(coin, str) and coin.strip() and number is not None:
            book[coin.strip()] = number
        else:
            broken += 1
    exchange, exchange_broken = borsa_pozisyonlari(borsa_durumu)
    rows = []
    for coin in sorted(set(book) | set(exchange)):
        defter, borsa = book.get(coin, 0.0), exchange.get(coin, 0.0)
        diff = defter - borsa or 0.0                           # -0.0 → 0.0
        if defter != 0.0 and borsa == 0.0:
            state = "yetim"
        elif defter == 0.0 and borsa != 0.0:
            state = "eksik"
        elif defter == 0.0:
            state = "uyumlu"
        elif defter * borsa < 0.0:
            state = "yon_farki"
        else:
            limit = max(mutlak_tolerans, goreli_tolerans * abs(defter))
            state = "uyumlu" if abs(diff) <= limit or math.isclose(abs(diff), limit, rel_tol=1e-9, abs_tol=1e-12) else "boy_farki"
        rows.append({"coin": coin, "defter": defter, "borsa": borsa, "fark": diff, "durum": state})
    return rows, broken + exchange_broken


def ozet(satirlar: list[dict[str, Any]] | pd.DataFrame | None) -> dict[str, Any]:
    """Durum sayıları, ``toplam`` ve ``uyumsuz_oran`` = (toplam − uyumlu) / toplam."""
    counts = {state: 0 for state in DURUMLAR}
    frame = satirlar if isinstance(satirlar, pd.DataFrame) else pd.DataFrame(satirlar or [])
    if frame.empty or "durum" not in frame:
        return {**counts, "toplam": 0, "uyumsuz_oran": 0.0}
    for state, number in frame["durum"].value_counts().items():
        if state in counts:
            counts[state] = int(number)
    total = len(frame)
    return {**counts, "toplam": total, "uyumsuz_oran": float((total - counts["uyumlu"]) / total)}


def mutabakat_dataframe(defter_pozisyon: dict[str, float] | None, borsa_durumu: dict | None, goreli_tolerans: float,
                        mutlak_tolerans: float) -> pd.DataFrame:
    rows, _ = mutabakat(defter_pozisyon, borsa_durumu, goreli_tolerans, mutlak_tolerans)
    return pd.DataFrame(rows, columns=["coin", "defter", "borsa", "fark", "durum"]) if rows else pd.DataFrame(columns=["coin", "defter", "borsa", "fark", "durum"])
