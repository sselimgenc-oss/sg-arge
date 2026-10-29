"""Risk ve anomali ölçüleri: martingale (zararda ekleme), tek coin yoğunlaşması (HHI), ekleme derinliği (Argon A12).

**Karar değil, yalnız ölçü**: sabit eşikle bayrak üretmez, kimseyi elemez; ``bayrak.py`` bunları ``bayrak_*`` bilgi sütunları olarak yayımlar.
Saf bellek içi hesaplama (ağ ve dosya yok), zamana göre kararlı sıralama, long/short tam simetri. Girdi: Hyperliquid dolum listesi; yalnız
perpetual dolumlar (``olcut.perp_fills``) işlenir. Ayrıştırılamayan satırlar atlanır ve her sonuçta ``atlanan_satir`` olarak sayılır.

Pencere öncesinden taşınan pozisyon (coinde ilk görülen dolumun ``startPosition``'ı sıfır değil): giriş fiyatı **bilinmiyor** sayılır; o coinde pozisyon
sıfırlanana (ya da ters yöne dönene) kadar zararda ekleme ölçülmez (ortalama giriş uydurulmaz).
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from copytrade.olcut import perp_fills

EPS = 1e-9
Dolumlar = Sequence[Mapping[str, Any]] | Iterable[Mapping[str, Any]]


def _isaret(side: str) -> int:
    return 1 if side == "B" else -1


def _hazirla(dolumlar: Dolumlar) -> tuple[list[dict[str, Any]], int]:
    """(zamana göre kararlı sıralı satırlar, atlanan satır sayısı). Spot dolumlar süzülür ve ``atlanan_satir`` sayılmaz."""
    kayitlar = dolumlar.to_dict(orient="records") if hasattr(dolumlar, "to_dict") else list(dolumlar)
    rows: list[dict[str, Any]] = []
    skipped = 0
    for raw in kayitlar:
        if not isinstance(raw, Mapping):
            skipped += 1
            continue
        try:
            coin = str(raw["coin"]).strip()
            side = str(raw["side"]).strip().upper()
            row = {"coin": coin, "px": float(raw["px"]), "sz": float(raw["sz"]), "side": side, "time": int(float(raw["time"])),
                   "startPosition": float(raw.get("startPosition", 0.0) or 0.0), "closedPnl": float(raw.get("closedPnl", 0.0) or 0.0)}
        except (KeyError, ValueError, TypeError):
            skipped += 1
            continue
        if not coin or side not in {"B", "A"} or not all(map(_finite, (row["px"], row["sz"], row["startPosition"], row["closedPnl"]))):
            skipped += 1
            continue
        rows.append(row)
    rows = perp_fills(rows)
    rows.sort(key=lambda r: r["time"])                  # kararlı: aynı ms'deki dolumlar giriş sırasını korur
    return rows, skipped


def _finite(value: float) -> bool:
    return value == value and abs(value) != float("inf")


def martingale_olcusu(dolumlar: Dolumlar, kat_esik: float = 1.0) -> dict[str, Any]:
    """Zarardaki pozisyona aynı yönde ekleme: sayı, katlama oranı (kat ≥ ``kat_esik`` olan eklemelerin payı) ve en büyük büyüme katsayısı.

    kat = ekleme büyüklüğü / pozisyonun açılış ya da en son ekleme büyüklüğü. Giriş fiyatı bilinmeyen (devralınan) pozisyonda ekleme ölçülmez."""
    rows, skipped = _hazirla(dolumlar)
    state: dict[str, dict[str, Any]] = {}
    losing = doubled = 0
    biggest = 0.0
    for row in rows:
        coin, px, sz = row["coin"], row["px"], row["sz"]
        if sz <= 0.0:
            continue
        if coin not in state:
            start = row["startPosition"]
            state[coin] = {"pos": start, "avg": None, "last": abs(start)} if abs(start) > EPS else {"pos": 0.0, "avg": 0.0, "last": 0.0}
        s = state[coin]
        signed = _isaret(row["side"]) * sz
        if abs(s["pos"]) <= EPS:
            state[coin] = {"pos": signed, "avg": px, "last": sz}
            continue
        direction = 1 if s["pos"] > 0 else -1
        if signed * s["pos"] > 0:                                        # aynı yönde ekleme
            if s["avg"] is not None and (px - s["avg"]) * direction < 0:   # long: px < giriş; short: px > giriş
                losing += 1
                kat = sz / (s["last"] if s["last"] > EPS else abs(s["pos"]))
                doubled += kat >= kat_esik - EPS
                biggest = max(biggest, kat)
            new = s["pos"] + signed
            s["avg"] = None if s["avg"] is None else (abs(s["pos"]) * s["avg"] + sz * px) / abs(new)
            s["pos"], s["last"] = new, sz
        else:                                                            # azaltma / kapanış / ters çevirme
            rest = s["pos"] + signed
            if abs(rest) <= EPS:
                state[coin] = {"pos": 0.0, "avg": 0.0, "last": 0.0}
            elif rest * s["pos"] > 0:
                s["pos"] = rest
            else:
                state[coin] = {"pos": rest, "avg": px, "last": abs(rest)}
    return {"zararda_ekleme_sayisi": int(losing), "katlama_orani": float(doubled) / losing if losing else 0.0, "en_buyuk_kat": float(biggest),
            "atlanan_satir": skipped}


def tek_coin_yogunlugu(dolumlar: Dolumlar) -> dict[str, Any]:
    """Coin başına ``closedPnl`` toplamından pozitif kâr payları ve HHI = Σ pay² (0–1); kâr yoksa 0 ve ``en_buyuk_coin`` None."""
    rows, skipped = _hazirla(dolumlar)
    per_coin: dict[str, float] = {}
    for row in rows:
        per_coin[row["coin"]] = per_coin.get(row["coin"], 0.0) + row["closedPnl"]
    positive = {c: p for c, p in per_coin.items() if p > EPS}
    total = sum(positive.values())
    base = {"coin_sayisi": len(per_coin), "atlanan_satir": skipped}
    if total <= EPS:
        return {"hhi": 0.0, "en_buyuk_coin": None, "en_buyuk_pay": 0.0, **base}
    shares = {c: p / total for c, p in positive.items()}
    top = min(shares, key=lambda c: (-shares[c], c))                     # eşitlikte alfabetik: deterministik
    return {"hhi": float(sum(v * v for v in shares.values())), "en_buyuk_coin": top, "en_buyuk_pay": float(shares[top]), **base}


def ekleme_derinligi(dolumlar: Dolumlar) -> dict[str, Any]:
    """Pozisyon döngüsü (sıfırdan açılıp sıfırlanana / ters dönene dek) başına aynı yönde ekleme adedi ve tepe boyut / ilk boyut oranı; en büyükleri."""
    rows, skipped = _hazirla(dolumlar)
    cycles: dict[str, dict[str, float]] = {}
    most, ratio, seen = 0, 0.0, False

    def close(c: dict[str, float]) -> None:
        nonlocal most, ratio, seen
        seen = True
        most = max(most, int(c["adds"]))
        if c["first"] > EPS:
            ratio = max(ratio, c["peak"] / c["first"])

    for row in rows:
        coin, sz = row["coin"], row["sz"]
        if sz <= 0.0:
            continue
        if coin not in cycles:
            start = row["startPosition"]
            cycles[coin] = {"pos": start, "first": abs(start), "peak": abs(start), "adds": 0.0}
        c = cycles[coin]
        signed = _isaret(row["side"]) * sz
        if abs(c["pos"]) <= EPS:
            c.update(pos=signed, first=sz, peak=sz, adds=0.0)
        elif signed * c["pos"] > 0:
            c["pos"] += signed
            c["adds"] += 1.0
            c["peak"] = max(c["peak"], abs(c["pos"]))
        else:
            rest = c["pos"] + signed
            if rest * c["pos"] > 0 and abs(rest) > EPS:
                c["pos"] = rest
            else:
                close(c)
                new = abs(rest) if abs(rest) > EPS and rest * c["pos"] < 0 else 0.0
                c.update(pos=rest if new else 0.0, first=new, peak=new, adds=0.0)
    for c in cycles.values():
        if abs(c["pos"]) > EPS and c["first"] > EPS:
            close(c)
    return {"en_fazla_ekleme_sayisi": int(most) if seen else 0, "en_buyuk_boy_orani": float(ratio) if seen else 0.0, "atlanan_satir": skipped}
