"""Etiket sonrasındaki gölge kopya kaydı; hesaplama yalnız ``defter.copy_ledger``dadır."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from copytrade.defter import FundingRates, Market, copy_ledger
from copytrade.kurallar import load_rules


@dataclass(frozen=True)
class Gecikme:
    trader_ms: int
    tespit_ms: int | None = None
    telegram_ms: int | None = None
    acti_ms: int | None = None


def _delay(style: str, rules: dict) -> int:
    return int(rules["kopya_gecikme_dk"].get(style, rules["kopya_gecikme_dk"]["intraday"]))


def _band_fills(fills: list[dict], market: Market, delay: int, style: str, rules: dict) -> tuple[list[dict], list[dict]]:
    """V1: bandı aşan giriş/eklemeyi silmez, denetim için `atlandi_bant` kaydeder."""
    allowed, skipped = [], []
    limit = float(rules["golge_fiyat_bandi"][style])
    for fill in fills:
        execution = market.execution(str(fill["coin"]), int(fill["time"]) + delay * 60_000)
        source = float(fill.get("px", 0))
        if execution and source and abs(execution[1] / source - 1) > limit:
            skipped.append({"durum": "atlandi_bant", "dolum": fill, "giris": execution[1]})
        else:
            allowed.append(fill)
    return allowed, skipped


def v2_sinir(style: str, gecen_gun: float, getiri: float, rules: dict | None = None) -> str | None:
    """Ön kayıttaki V2 eşiği; ``getiri`` ayrılan teminata oranlıdır."""
    rules = rules or load_rules()
    if style == "intraday":
        return "zarar_kes" if getiri <= float(rules["golge_v2"]["intraday"]["zarar_kes"]) else None
    stage = "gun_14" if gecen_gun >= 14 else "gun_7" if gecen_gun >= 7 else "gun_0"
    limits = rules["golge_v2"]["swing"][stage]
    if getiri <= float(limits["zarar_kes"]):
        return "zarar_kes"
    if limits["kar_al"] is not None and getiri >= float(limits["kar_al"]):
        return "kar_al"
    return None


def kirp_pozisyon(fill: dict, account: float, rules: dict | None = None) -> tuple[dict, dict | None]:
    """Tek işlemdeki gölge notionalını ön kayıtlı 3× teminat tavanına kırpar."""
    rules = rules or load_rules()
    cap = float(account) * float(rules["golge_pozisyon_tavan_carpani"])
    price, size = abs(float(fill.get("px", 0))), float(fill["sz"])
    if not price or abs(size) * price <= cap:
        return fill, None
    clipped = dict(fill, sz=str(cap / price))
    return clipped, {"durum": "kirpildi", "eski_sz": str(fill["sz"]), "yeni_sz": clipped["sz"], "tavan_usd": cap}


def calistir(fills: list[dict], candles: dict[str, list[dict]], account: Any, *, style: str,
             etiket_ms: int, end_ms: int, funding: list[dict] | None = None,
             variant: str = "V0", rules: dict | None = None, delay_min: int | None = None) -> dict:
    """Etiketten sonraki dolumları tek defterden çalıştırır.

    V0 birebir; V1 fiyat bandı; V2 aynı defter üzerinde ön-kayıtlı zarar/süre sınırlarını raporlar.
    V2'nin zorunlu çıkış dolumları Faz 3 öncesi liderin donduracağı sayılara bağlıdır; bu katman
    onları üretmez ve gerçek dışı ikinci bir defter yaratmaz.
    """
    rules = rules or load_rules()
    delay = _delay(style, rules) if delay_min is None else delay_min
    source = [row for row in fills if int(row["time"]) >= etiket_ms]
    market = Market(candles)
    skipped: list[dict] = []
    if variant == "V1":
        source, skipped = _band_fills(source, market, delay, style, rules)
    if variant not in {"V0", "V1", "V2"}:
        raise ValueError("Varyant V0, V1 veya V2 olmalı")
    capped = []
    cap_events = []
    for row in source:
        row, event = kirp_pozisyon(row, float(account), rules)
        capped.append(row)
        if event:
            cap_events.append(event)
    ledger = copy_ledger(capped, market, account, delay, etiket_ms, end_ms, FundingRates(funding), rules, daily=True)
    events = list(skipped) + cap_events
    if ledger.get("missing", 0):
        events.append({"durum": "eksik", "sayi": ledger["missing"]})
    # Trader girişinden önce çıkarsa gecikmeli giriş gerçekleşemez; satır kanıt olarak kalır.
    for fill in source:
        target = int(fill["time"]) + delay * 60_000
        if target > end_ms:
            events.append({"durum": "kacirildi", "dolum": fill})
    if variant == "V2" and ledger.get("net") is not None:
        reason = v2_sinir(style, (end_ms - etiket_ms) / 86_400_000, float(ledger["net"]), rules)
        if reason:
            events.append({"durum": reason, "varyant": "V2"})
    return {"varyant": variant, "gecikme_dk": delay, "defter": ledger, "olaylar": events,
            "gecikme_zinciri": [{"trader_ms": int(row["time"])} for row in source]}


def saglama(fills: list[dict], candles: dict[str, list[dict]], account: Any, start_ms: int, end_ms: int,
             funding: list[dict] | None = None, rules: dict | None = None) -> dict:
    """Sıfır gecikme/maliyet sağlama; kaynak ve gölge aynı PnL'i üretmelidir."""
    rules = dict(rules or load_rules())
    rules.update(maliyet_taker=0.0, maliyet_kayma=0.0)
    ledger = copy_ledger(fills, Market(candles), account, 0, start_ms, end_ms, FundingRates(funding), rules)
    if ledger.get("missing") or ledger.get("net") is None:
        raise ValueError("Sağlama için eksiksiz fiyat ve geçerli hesap gerekir")
    return ledger
