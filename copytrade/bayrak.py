"""Kırmızı bayraklar (``docs/GOREV_SECIM_V1.md`` Ek; kaynak ``arastirma/copytrade/argon_kirmizi_bayrak.md``).

**Bilgi sütunlarıdır, kimseyi elemez**; eşik yok, yalnız ham oran/değer. Yalnız aday katı için hesaplanır.
Her sütun ayrı korunur: istek düşerse değeri boş kalır ve ``bayrak_not`` = "kontrol edilemedi: <sütun>, …".
"""
from __future__ import annotations

import time
from typing import Any

import requests

from copytrade.kapi import funding_all
from copytrade.tarama import PublicClient, RateLimitError

SUTUNLAR = ("bayrak_rol", "bayrak_vault_orani", "bayrak_funding_payi", "bayrak_alt_hesap_ters", "bayrak_hacim_orani", "bayrak_not")
GUN_MS = 86_400_000
EVET, HAYIR, YOK = "evet", "hayır", "kontrol edilemedi"
HATALAR = (RateLimitError, requests.RequestException, ValueError, TypeError, KeyError)


def rol(user_role: dict[str, Any]) -> str:
    """``userRole`` → ``vault`` | ``subAccount:<master>`` | diğer rol adı (``user`` vb.)."""
    name = str(user_role.get("role", "")).strip()
    master = str((user_role.get("data") or {}).get("master", "")).lower()
    return f"subAccount:{master}" if name == "subAccount" and master else name


def vault_orani(equities: list[dict[str, Any]], hesap_degeri: float) -> float | None:
    """``userVaultEquities`` toplamı / hesap değeri."""
    return sum(float(x["equity"]) for x in equities) / hesap_degeri if hesap_degeri > 0 else None


def funding_payi(funding: list[dict[str, Any]], fills: list[dict[str, Any]]) -> float | None:
    """365 gün ``userFunding`` toplamı (alınan +) / aynı dönem gerçekleşen PnL (``closedPnl`` toplamı); işaretli. PnL 0 ise ``None``."""
    total = sum(float(x["delta"]["usdc"]) for x in funding)
    pnl = sum(float(x.get("closedPnl", 0) or 0) for x in fills)
    return total / pnl if pnl else None


def hacim_orani(portfolio: list, hesap_degeri: float) -> float | None:
    """``portfolio`` 30 günlük (``month``) hacim / hesap değeri."""
    month = next((v for k, v in portfolio if k == "month" and isinstance(v, dict)), None)
    return float(month["vlm"]) / hesap_degeri if month and hesap_degeri > 0 else None


def pozisyonlar(state: dict[str, Any]) -> dict[str, float]:
    """``clearinghouseState`` → {coin: işaretli büyüklük}; sıfır pozisyonlar atılır."""
    out: dict[str, float] = {}
    for item in state.get("assetPositions", []):
        pos = item.get("position", item)
        size = float(pos.get("szi", 0) or 0)
        if size:
            out[str(pos["coin"])] = out.get(str(pos["coin"]), 0.0) + size
    return out


def ters_pozisyon(own: dict[str, float], others: list[dict[str, float]]) -> bool:
    """Başka bir hesapta aynı coinde zıt işaretli açık pozisyon var mı."""
    return any(coin in other and own[coin] * other[coin] < 0 for other in others for coin in own)


def alt_hesap_ters(address: str, role: str, client: Any) -> str:
    """Master'ın diğer alt hesaplarında (alt hesapsa master'ın kendisinde de) aynı coinde ters pozisyon: evet | hayır."""
    master = role.split(":", 1)[1] if role.startswith("subAccount:") else address.lower()
    subs = client.sub_accounts(master)
    own = pozisyonlar(client.info({"type": "clearinghouseState", "user": address}, weight=2) or {})
    others = [pozisyonlar(s.get("clearinghouseState") or {}) for s in subs if str(s.get("subAccountUser", "")).lower() != address.lower()]
    if master != address.lower():
        others.append(pozisyonlar(client.info({"type": "clearinghouseState", "user": master}, weight=2) or {}))
    return EVET if ters_pozisyon(own, others) else HAYIR


def hesapla(client: PublicClient, address: str, hesap_degeri: float, now_ms: int | None = None) -> dict[str, Any]:
    """Tek adres için 5 bayrak sütunu + ``bayrak_not``. Başarısız istek yalnız kendi sütununu boş bırakır."""
    now_ms = now_ms or int(time.time() * 1000)
    out: dict[str, Any] = {name: None for name in SUTUNLAR}
    failed: list[str] = []

    def attempt(column: str, call):
        try:
            return call()
        except HATALAR:
            failed.append(column)
            return None

    role = attempt("bayrak_rol", lambda: rol(client.info({"type": "userRole", "user": address}, weight=2) or {}))
    out["bayrak_rol"] = role
    out["bayrak_vault_orani"] = attempt("bayrak_vault_orani", lambda: vault_orani(client.vault_equities(address), hesap_degeri))
    out["bayrak_funding_payi"] = attempt("bayrak_funding_payi", lambda: funding_payi(
        funding_all(client, address, now_ms - 365 * GUN_MS, now_ms), client.fills(address, now_ms - 365 * GUN_MS)))
    out["bayrak_alt_hesap_ters"] = (attempt("bayrak_alt_hesap_ters", lambda: alt_hesap_ters(address, role, client))
                                    if role is not None else None) or YOK
    if out["bayrak_alt_hesap_ters"] == YOK and "bayrak_alt_hesap_ters" not in failed:
        failed.append("bayrak_alt_hesap_ters")
    out["bayrak_hacim_orani"] = attempt("bayrak_hacim_orani", lambda: hacim_orani(client.portfolio(address), hesap_degeri))
    out["bayrak_not"] = "kontrol edilemedi: " + ", ".join(failed) if failed else ""
    return out
