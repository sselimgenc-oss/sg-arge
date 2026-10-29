"""Oda risk bayrakları (``docs/GOREV_ODA_RISK.md``; Argon A26 yönsüz trader tespiti, A27 kalabalıklaşma — lider denetim notlarındaki düzeltmelerle).

**Yalnız bilgi/uyarı:** seçim, kapı, oda ve eşik kararı değişmez; otomatik işlem yok. Eşikler ``kurallar.yaml``'da ve SEZGİSELdir.
* ``yonsuz_bayrak``: funding geliri payı (son ``yonsuz_pencere_gun`` gün), aynı coinde spot ↔ perp ters pozisyon örtüşmesi, maker payı; her biri değer + eşik + aşıldı mı; bayrak = herhangi biri.
* ``kalabalik``: oda düzeyinde coin başına net yön payı = |Σ x·yön| / Σ|x|, x = kopya ağırlığı × pozisyon nosyoneli / trader hesap değeri (nosyonel zaten kaldıraçlıdır: kaldıraç ikinci kez çarpılmaz).
Veri yoksa değer ``None`` (uydurulmaz); bir ölçü hesaplanamazsa yalnız o ölçü ``None``, hata gizlenmez (``hata`` alanı).
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from copytrade.kurallar import load_rules
from copytrade.olcut import _funding_amount, perp_fills

DAY_MS = 86_400_000
YONSUZ_KOLLAR = ("oda", "kontrol")


def _olcu(deger: float | None, esik: float) -> dict[str, Any]:
    return {"deger": deger, "esik": esik, "asildi": None if deger is None else bool(deger > esik)}


def funding_payi(funding_90g_usd: float | None, toplam_kar_usd: float | None, rules: dict) -> dict[str, Any]:
    """Funding geliri / max(|toplam kâr|, ε). Negatif funding (ödenen) pay olarak negatif çıkar, eşiği aşmaz."""
    esik = float(rules["yonsuz_funding_payi_esik"])
    if funding_90g_usd is None or toplam_kar_usd is None:
        return _olcu(None, esik)
    return _olcu(float(funding_90g_usd) / max(abs(float(toplam_kar_usd)), float(rules["yonsuz_pnl_taban_usd"])), esik)


def spot_perp_ters(spot: dict[str, float] | None, perp: dict[str, float], rules: dict) -> dict[str, Any]:
    """Aynı coinde spot uzun / perp kısa (S × P < 0) örtüşmesi: min(S, −P) / max(S, |P|); trader değeri coinlerin en yükseği. Spot durumu yoksa ``None``."""
    esik = float(rules["yonsuz_spot_perp_esik"])
    if spot is None:
        return _olcu(None, esik)
    esleme = rules["yonsuz_spot_esleme"]
    toplam: dict[str, float] = defaultdict(float)
    for token, miktar in spot.items():
        toplam[str(esleme.get(token, token))] += float(miktar)
    en_yuksek, coin = 0.0, None
    for c, s in toplam.items():
        p = float(perp.get(c, 0.0))
        if s * p < 0:
            oran = min(abs(s), abs(p)) / max(abs(s), abs(p))
            if oran > en_yuksek:
                en_yuksek, coin = oran, c
    out = _olcu(en_yuksek, esik)
    out["coin"] = coin
    return out


def maker_payi(fills: list[dict], now_ms: int, rules: dict) -> dict[str, Any]:
    """Son ``yonsuz_pencere_gun`` günde perp dolum hacminin (px × sz) ``crossed == false`` payı; hacim yoksa ``None``."""
    esik = float(rules["yonsuz_maker_payi_esik"])
    bas = now_ms - int(rules["yonsuz_pencere_gun"]) * DAY_MS
    toplam = maker = 0.0
    for f in perp_fills(fills):
        if bas <= int(f["time"]) <= now_ms and "crossed" in f:
            hacim = abs(float(f["px"]) * float(f["sz"]))
            toplam += hacim
            maker += 0.0 if f["crossed"] else hacim
    return _olcu(maker / toplam if toplam else None, esik)


def toplam_kar(portfolio: list, now_ms: int, rules: dict) -> float | None:
    """Portföy kümülatif PnL'sinin (``allTime.pnlHistory``) son ``yonsuz_pencere_gun`` gündeki değişimi; seri yoksa ``None``."""
    donemler = {ad: v for ad, v in portfolio if isinstance(v, dict)} if portfolio else {}
    seri = sorted((int(t), float(v)) for t, v in (donemler.get("allTime") or donemler.get("perpAllTime") or {}).get("pnlHistory", []) if int(t) <= now_ms)
    if not seri:
        return None
    bas = now_ms - int(rules["yonsuz_pencere_gun"]) * DAY_MS
    onceki = [v for t, v in seri if t <= bas]
    return seri[-1][1] - (onceki[-1] if onceki else seri[0][1])


def yonsuz_bayrak(funding_90g_usd: float | None, toplam_kar_usd: float | None, spot: dict[str, float] | None, perp: dict[str, float],
                  fills: list[dict], now: datetime | str | int, rules: dict | None = None, hata: str | None = None) -> dict[str, Any]:
    """Trader başına ``yonsuz_bayrak``: üç ölçü (değer + eşik + aşıldı mı) ve ``bayrak`` (herhangi biri aşıldıysa). Hesaplanamayan ölçü ``None`` (bayrağa katılmaz)."""
    rules = rules or load_rules()
    now_ms = int(now) if isinstance(now, int) else int((now if isinstance(now, datetime) else datetime.fromisoformat(str(now).replace("Z", "+00:00"))).timestamp() * 1000)
    olcular = {"funding_payi": funding_payi(funding_90g_usd, toplam_kar_usd, rules), "spot_perp_ters": spot_perp_ters(spot, perp, rules), "maker_payi": maker_payi(fills, now_ms, rules)}
    out: dict[str, Any] = {**olcular, "bayrak": any(o["asildi"] for o in olcular.values()), "pencere_gun": int(rules["yonsuz_pencere_gun"]), "sezgisel": True}
    if hata:
        out["hata"] = hata
    return out


def kalabalik(uyeler: list[dict[str, Any]], rules: dict | None = None) -> dict[str, Any]:
    """Oda düzeyinde kalabalıklaşma. ``uyeler``: oda üyeleri ``{"hesap_degeri", "pozisyonlar": [{"coin", "yon", "buyukluk_usd"}]}`` (yalnız geçerli veri).
    Kopya ağırlığı eşit (1/N) olduğundan oranda sadeleşir; ``x = ağırlık × nosyonel / hesap değeri``. Coin başına: net yön payı, aynı yöndeki üye sayısı, çakışma oranı."""
    rules = rules or load_rules()
    uyeler = [u for u in uyeler if u.get("hesap_degeri") and float(u["hesap_degeri"]) > 0]
    n = len(uyeler)
    w = 1.0 / n if n else 0.0
    net: dict[str, float] = defaultdict(float)
    uye_say: dict[str, dict[str, int]] = defaultdict(lambda: {"long": 0, "short": 0})
    brut = 0.0
    for u in uyeler:
        goruldu: set[tuple[str, str]] = set()
        for p in u.get("pozisyonlar", []):
            yon = 1.0 if p["yon"] == "long" else -1.0
            x = w * float(p["buyukluk_usd"]) / float(u["hesap_degeri"])
            net[p["coin"]] += x * yon
            brut += x
            if (p["coin"], p["yon"]) not in goruldu:
                goruldu.add((p["coin"], p["yon"]))
                uye_say[p["coin"]][p["yon"]] += 1
    coinler = []
    for coin, deger in net.items():
        say = uye_say[coin]
        toplam = say["long"] + say["short"]
        coinler.append({"coin": coin, "net_yon": "long" if deger > 0 else "short" if deger < 0 else "yok", "net_pay": abs(deger) / brut if brut else 0.0,
                        "ayni_yon": max(say["long"], say["short"]), "toplam": toplam, "cakisma": max(say["long"], say["short"]) / toplam if toplam else 0.0})
    coinler.sort(key=lambda c: (-c["net_pay"], c["coin"]))
    esikler = float(rules["kalabalik_net_pay_esik"]), int(rules["kalabalik_min_trader"]), float(rules["kalabalik_cakisma_esik"]), int(rules["kalabalik_ayni_yon_sayi"])

    def asildi(c: dict[str, Any]) -> bool:
        return (c["net_pay"] > esikler[0] or (c["toplam"] >= esikler[1] and c["cakisma"] >= esikler[2]) or c["ayni_yon"] >= esikler[3])

    uyarili = [c for c in coinler if asildi(c)]
    metin = None
    if uyarili:
        c = uyarili[0]
        metin = f"Kalabalık: {c['coin']} net {c['net_yon']} oda payı %{round(100 * c['net_pay'])}, {c['ayni_yon']}/{n} trader aynı yönde"
    return {"n_oda": n, "coinler": coinler[:10], "uyari": bool(uyarili), "uyari_metni": metin, "sezgisel": True}
