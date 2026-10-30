"""Etiket sonrasındaki gölge kopya kaydı; hesaplama yalnız ``defter.copy_ledger``dadır."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from copytrade.defter import HOUR, FundingRates, Market, capital_scale, copy_ledger
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
    allowed, skipped, skipped_openings = [], [], set()
    shadow: dict[str, float] = {}      # gölgenin kaynak birimiyle izlenen pozisyonu (yalnız izin verilen dolumlar)
    limit = float(rules["golge_fiyat_bandi"][style])
    for fill in fills:
        coin = str(fill["coin"])
        signed = (-1 if fill["side"] in {"A", "Sell", "sell"} else 1) * float(fill["sz"])
        before = float(fill.get("startPosition", 0))
        opening_or_add = before == 0 or before * signed > 0
        # Atlanan girişin sonraki kapanışı gölgede ters işlem başlatmamalı; ama gölgede (önceki izinli dolumlardan) pozisyon varsa kapanış
        # ona uygulanır: atlanan ekleme sonrası kapanış bastırılırsa gölge pozisyon yetim kalır (E2).
        if coin in skipped_openings and not opening_or_add:
            if abs(shadow.get(coin, 0.0)) > 1e-12:
                allowed.append(fill)
                shadow[coin] = shadow.get(coin, 0.0) + signed
                if abs(before + signed) < 1e-12:
                    skipped_openings.discard(coin)
                    shadow[coin] = 0.0
                continue
            skipped.append({"durum": "atlandi_bant", "dolum": fill, "neden": "giris_atlandi"})
            if before + signed == 0:
                skipped_openings.discard(coin)
            continue
        if not opening_or_add:
            allowed.append(fill)
            shadow[coin] = shadow.get(coin, 0.0) + signed
            if abs(before + signed) < 1e-12:
                shadow[coin] = 0.0
            continue
        execution = market.execution(coin, int(fill["time"]) + delay * 60_000)
        source = float(fill.get("px", 0))
        if execution and source and abs(execution[1] / source - 1) > limit:
            skipped.append({"durum": "atlandi_bant", "dolum": fill, "giris": execution[1]})
            skipped_openings.add(coin)
        else:
            allowed.append(fill)
            shadow[coin] = shadow.get(coin, 0.0) + signed
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


def kirp_pozisyon(fill: dict, shadow_before: float, account: float, rules: dict | None = None) -> tuple[dict, dict | None]:
    """Tavan tek doluma değil, ekleme SONRASI birikmiş gölge pozisyonuna uygulanır."""
    rules = rules or load_rules()
    cap = float(rules["golge_pozisyon_tavan_carpani"])
    price, size = abs(float(fill.get("px", 0))), float(fill["sz"])
    sign = -1 if fill["side"] in {"A", "Sell", "sell"} else 1
    signed = sign * size / float(account)
    # Tavan yalnız aynı yöndeki açılış/eklemeyi sınırlar; saf azaltma tavanı büyütmez ve kırpılmaz. Flip (ters çevirme) = çıkış + yeni giriş:
    # çıkış tam yapılır, ters yönde açılan yeni parça tavana tabidir (E2).
    if not price:
        return fill, None
    after = shadow_before + signed
    if shadow_before * signed < 0:
        if shadow_before * after >= 0 or abs(after) * price <= cap:
            return fill, None
        allowed = (abs(shadow_before) + cap / price) * float(account)
        clipped = dict(fill, sz=str(allowed))
        return clipped, {"durum": "kirpildi", "eski_sz": str(fill["sz"]), "yeni_sz": clipped["sz"], "tavan_usd": cap}
    if abs(after) * price <= cap:
        return fill, None
    allowed = max(0.0, cap / price - abs(shadow_before)) * float(account)
    clipped = dict(fill, sz=str(allowed))
    return clipped, {"durum": "kirpildi", "eski_sz": str(fill["sz"]), "yeni_sz": clipped["sz"], "tavan_usd": cap}


def _kapat(held: dict, coin: str, hour: int, mark: float, scale: Any, exits: list[dict]) -> None:
    """Pozisyonu o mumun mark fiyatında zorunlu çıkışla kapatır (defterde maliyetli çıkış satırı)."""
    size = held.pop(coin)[0]
    exits.append({"time": hour, "coin": coin, "side": "A" if size > 0 else "B",
                  "sz": str(abs(size) / scale(hour)), "startPosition": str(size / scale(hour)),
                  "px": str(mark), "_execution_time": hour, "_execution_price": mark})


def _denetle_ve_kapat(held: dict[str, tuple[float, float, int, int]], until: int, market: Market, style: str, rules: dict,
                      scale: Any, v2: bool, exits: list[dict], events: list[dict], suppressed: set[str]) -> None:
    """Açık tüm pozisyonları ``until``'a kadar her saatlik mum markında denetler.

    1. Çapraz teminat (A19): trader'ın açık pozisyonlarının TOPLAM K/Z'si (ayrılmış 1 birime oranlı) ``golge_likidasyon_esigi``'ne ya da altına inerse
       hepsi o mumun markında tasfiye edilir (``likidasyon``).
    2. Tek pozisyon: kendi K/Z'si eşiğe inerse ``likidasyon``; değilse V2 sınırı (``zarar_kes`` / ``kar_al``).
    Her pozisyon yalnız son denetlenen mumdan ileri taranır; eşik gerçek bakım teminatından önce olmadığı için iyimser sınırdır.
    """
    if not held:
        return
    esik = float(rules["golge_likidasyon_esigi"])
    first = min(max((st[2] // HOUR + 1) * HOUR, ((st[3] // HOUR) + 1) * HOUR) for st in held.values())
    for hour in range(first, until + 1, HOUR):
        active = [c for c, st in held.items() if hour >= (st[2] // HOUR + 1) * HOUR and hour >= ((st[3] // HOUR) + 1) * HOUR]
        marks = {c: market.mark(c, hour) for c in active}
        pnls = {c: held[c][0] * (marks[c] - held[c][1]) for c in active if marks[c] is not None}
        if not pnls:
            continue
        if sum(pnls.values()) <= esik:
            for c in pnls:
                _kapat(held, c, hour, marks[c], scale, exits)
                events.append({"durum": "likidasyon", "neden": "likidasyon", "coin": c, "zaman_ms": hour})
                suppressed.add(c)
            continue
        for c, pnl in pnls.items():
            opened = held[c][2]
            reason = "likidasyon" if pnl <= esik else (v2_sinir(style, (hour - opened) / 86_400_000, pnl, rules) if v2 else None)
            if reason:
                _kapat(held, c, hour, marks[c], scale, exits)
                events.append({"durum": "likidasyon" if reason == "likidasyon" else "v2_cikis", "neden": reason, "coin": c, "zaman_ms": hour})
                suppressed.add(c)
            else:
                st = held[c]
                held[c] = (st[0], st[1], st[2], hour)


def _v2_signed(fill: dict, own: float, scale: Any) -> float:
    """Defterin kaynak-kapanış oranını V2 gölge takibinde de uygular."""
    sign = -1.0 if fill["side"] in {"A", "Sell", "sell"} else 1.0
    raw = sign * float(fill["sz"])
    leader_before = float(fill.get("startPosition", 0))
    if leader_before * raw < 0:
        leader_close = min(abs(leader_before), abs(raw))
        close = abs(own) * leader_close / abs(leader_before) if own * leader_before > 0 else 0.0
        return sign * (close + max(0.0, abs(raw) - leader_close) * scale(int(fill["time"])))
    return raw * scale(int(fill["time"]))


def v2_cikislari(fills: list[dict], market: Market, account: Any, style: str, delay: int,
                 end_ms: int, rules: dict, v2: bool = True) -> tuple[list[dict], list[dict], list[dict]]:
    """V2'yi pozisyon başına ve trader toplamında (çapraz teminat likidasyonu), her mumda simüle eder ve deftere girecek kaynakları döndürür.

    ``getiri``, gölgenin trader için ayırdığı 1 birim sermayeye oranlı K/Z'dir.
    Zorunlu çıkıştan sonra trader pozisyonu sıfırlanana dek kaynak dolumları
    kopyalanmaz; sıfırlamadan sonraki yeni açılış yeniden kopyalanabilir.
    """
    scale = capital_scale(account)
    held: dict[str, tuple[float, float, int, int]] = {}
    exits, events, allowed = [], [], []
    suppressed: set[str] = set()
    for fill in sorted(fills, key=lambda x: int(x["time"])):
        coin = str(fill["coin"])
        raw_after = float(fill.get("startPosition", 0)) + (-1 if fill["side"] in {"A", "Sell", "sell"} else 1) * float(fill["sz"])
        if coin in suppressed:
            events.append({"durum": "atlandi_v2", "coin": coin, "dolum": fill,
                           "neden": "zorunlu_cikistan_sonra"})
            if abs(raw_after) < 1e-12:
                suppressed.discard(coin)
            continue
        target = int(fill["time"]) + delay * 60_000
        if "_execution_time" in fill:        # canlı yol (kopya_v2): yürütme fiyatı dakika mumundan önceden eklenmiş
            execution = (int(fill["_execution_time"]), float(fill["_execution_price"]))
        else:
            execution = market.execution(coin, target) if delay else (int(fill["time"]), float(fill["px"]))
        if execution is None:
            continue
        when, price = execution
        _denetle_ve_kapat(held, when, market, style, rules, scale, v2, exits, events, suppressed)
        if coin in suppressed:
            events.append({"durum": "atlandi_v2", "coin": coin, "dolum": fill, "neden": "zorunlu_cikistan_sonra"})
            if abs(raw_after) < 1e-12:
                suppressed.discard(coin)
            continue
        before, old_entry, opened, _ = held.get(coin, (0.0, price, when, when))
        amount = _v2_signed(fill, before, scale)
        if abs(amount) < 1e-15:           # etiketten önceki (miras) pozisyonu kapatan dolum: kopyada pozisyon yok, hiçbir şey olmaz (E3: 0/0 yok)
            allowed.append(fill)
            continue
        after = before + amount
        if before == 0 or before * amount > 0:
            entry = (old_entry * abs(before) + price * abs(amount)) / abs(after)
            held[coin] = (after, entry, opened if before else when, when)
        elif abs(after) < 1e-15:
            held.pop(coin, None)
        elif before * after > 0:          # kısmi azaltma: giriş ve pozisyon yaşı korunur (ağırlıklı ortalama giriş; E2)
            held[coin] = (after, old_entry, opened, when)
        else:                             # flip: yeni yönde yeni giriş, yeni yaş
            held[coin] = (after, price, when, when)
        allowed.append(fill)
    _denetle_ve_kapat(held, end_ms, market, style, rules, scale, v2, exits, events, suppressed)
    return allowed, exits, events


def calistir(fills: list[dict], candles: dict[str, list[dict]], account: Any, *, style: str,
             etiket_ms: int, end_ms: int, funding: list[dict] | None = None,
             variant: str = "V0", rules: dict | None = None, delay_min: int | None = None,
             gecikmeler: dict[int, Gecikme] | None = None) -> dict:
    """Etiketten sonraki dolumları tek defterden çalıştırır.

    V0 birebir; V1 fiyat bandı; V2 açık her pozisyonu her mumda teminatına
    oranlı K/Z ile denetler ve eşikte maliyetli zorunlu çıkışı tek deftere verir.
    """
    rules = rules or load_rules()
    delay = _delay(style, rules) if delay_min is None else delay_min
    source = [row for row in fills if int(row["time"]) >= etiket_ms]
    trader_source = list(source)
    market = Market(candles)
    skipped: list[dict] = []
    if variant == "V1":
        source, skipped = _band_fills(source, market, delay, style, rules)
    if variant not in {"V0", "V1", "V2"}:
        raise ValueError("Varyant V0, V1 veya V2 olmalı")
    capped = []
    cap_events = []
    shadow = {}
    account_scale = capital_scale(account)
    for row in source:
        coin = str(row["coin"])
        before = shadow.get(coin, 0.0)
        row, event = kirp_pozisyon(row, before, 1.0 / account_scale(int(row["time"])), rules)
        capped.append(row)
        sign = -1 if row["side"] in {"A", "Sell", "sell"} else 1
        shadow[coin] = before + sign * float(row["sz"]) * account_scale(int(row["time"]))
        if event:
            cap_events.append(event)
    capped, v2_exits, v2_events = v2_cikislari(capped, market, account, style, delay, end_ms, rules, variant == "V2")
    ledger = copy_ledger(capped + v2_exits, market, account, delay, etiket_ms, end_ms, FundingRates(funding), rules, daily=True)
    events = list(skipped) + cap_events
    if ledger.get("missing", 0):
        events.append({"durum": "eksik", "sayi": ledger["missing"]})
    # Trader girişinden önce çıkarsa gecikmeli giriş gerçekleşemez; satır kanıt olarak kalır.
    for fill in trader_source:
        target = int(fill["time"]) + delay * 60_000
        # Trader gecikmeli giriş zamanından önce aynı pozisyonu kapattıysa kaçırıldı.
        later_close = any(str(other["coin"]) == str(fill["coin"]) and int(fill["time"]) < int(other["time"]) < target
                          and float(other.get("startPosition", 0)) * ((-1 if other["side"] in {"A", "Sell", "sell"} else 1) * float(other["sz"])) < 0
                          for other in trader_source)
        if later_close:
            events.append({"durum": "kacirildi", "dolum": fill})
    events.extend(v2_events)
    zincir = []
    for row in source:
        record = (gecikmeler or {}).get(int(row.get("tid", row["time"])))
        zincir.append({"trader_ms": int(row["time"]), "tespit_ms": record.tespit_ms if record else None,
                       "telegram_ms": record.telegram_ms if record else None, "acti_ms": record.acti_ms if record else None,
                       "neden": None if record else "karar_kaydi_yok"})
    return {"varyant": variant, "gecikme_dk": delay, "defter": ledger, "olaylar": events,
            "gecikme_zinciri": zincir}


def saglama(fills: list[dict], candles: dict[str, list[dict]], account: Any, start_ms: int, end_ms: int,
             funding: list[dict] | None = None, rules: dict | None = None) -> dict:
    """Sıfır gecikme/maliyet sağlama; kaynak ve gölge aynı PnL'i üretmelidir."""
    rules = dict(rules or load_rules())
    rules.update(maliyet_taker=0.0, maliyet_kayma=0.0)
    ledger = copy_ledger(fills, Market(candles), account, 0, start_ms, end_ms, FundingRates(funding), rules)
    if ledger.get("missing") or ledger.get("net") is None:
        raise ValueError("Sağlama için eksiksiz fiyat ve geçerli hesap gerekir")
    return ledger
