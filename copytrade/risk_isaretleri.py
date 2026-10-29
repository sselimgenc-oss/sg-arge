"""Risk işaretleri (ön kayıt D v1.4 madde 2): oda üyesi için haftalık rapora YALNIZ BİLGİ olarak yazılır.

Otomatik çıkış yoktur; işaretler performans (kâr/zarar, getiri) içermez, körlükle uyumludur. Bir işaretin çıkışa dönüşmesi ayrı kullanıcı kararıdır.
Her işaret ``True`` (işaretli), ``False`` (işaretsiz) ya da ``None`` (veri yok) döner; veri yoksa işaret uydurulmaz.
Eşikler ``kurallar.yaml``: ``risk_kaldirac_sicrama_kat``, ``risk_tutma_anomali_kat`` ve martingale için ``bayrak_kat_esik``.
"""
from __future__ import annotations

from typing import Any

from copytrade import bayrak_ek
from copytrade.kurallar import load_rules


def _sayi(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number and abs(number) != float("inf") else None


def kaldirac_sicramasi(etiket_medyan: Any, son_hafta_en_yuksek: Any, rules: dict) -> bool | None:
    """Son haftanın en yüksek kaldıracı, etiket anındaki medyan kaldıracın ``risk_kaldirac_sicrama_kat`` katından BÜYÜKSE (tam kat işaretlenmez)."""
    medyan, son = _sayi(etiket_medyan), _sayi(son_hafta_en_yuksek)
    if medyan is None or son is None or medyan <= 0:
        return None
    return son > float(rules["risk_kaldirac_sicrama_kat"]) * medyan


def martingale_baslangici(etiket_oran: Any, dolumlar: list[dict] | None, hafta_baslangic_ms: int | None, rules: dict) -> bool | None:
    """``bayrak_katlama_orani`` etiket anındakinden YÜKSEK ve son haftada (``hafta_baslangic_ms`` ve sonrası) en az 1 zararda katlama (kat ≥ ``bayrak_kat_esik``)."""
    onceki = _sayi(etiket_oran)
    if onceki is None or dolumlar is None or hafta_baslangic_ms is None:
        return None
    esik = float(rules["bayrak_kat_esik"])
    olaylar, _ = bayrak_ek.zararda_eklemeler(dolumlar)
    simdi = bayrak_ek.martingale_olcusu(dolumlar, esik)["katlama_orani"]
    son_hafta = sum(1 for zaman, kat in olaylar if zaman >= hafta_baslangic_ms and kat >= esik - bayrak_ek.EPS)
    return simdi > onceki and son_hafta >= 1


def tutma_anomalisi(zarardaki_acik_yaslar_saat: list[Any] | None, medyan_tutma_saat: Any, rules: dict) -> bool | None:
    """Zarardaki bir açık pozisyonun yaşı, trader'ın medyan tutma süresinin ``risk_tutma_anomali_kat`` katından BÜYÜKSE (tam kat işaretlenmez)."""
    medyan = _sayi(medyan_tutma_saat)
    if zarardaki_acik_yaslar_saat is None or medyan is None or medyan <= 0:
        return None
    return any((_sayi(y) or 0.0) > float(rules["risk_tutma_anomali_kat"]) * medyan for y in zarardaki_acik_yaslar_saat)


def uye_isaretleri(etiket: dict[str, Any], son: dict[str, Any], rules: dict | None = None) -> dict[str, bool | None]:
    """``etiket``: medyan_kaldirac, katlama_orani, medyan_tutma_saat (etiket anı). ``son``: en_yuksek_kaldirac, dolumlar, hafta_baslangic_ms,
    zarardaki_acik_yaslar_saat (son hafta). Eksik alan ilgili işareti ``None`` yapar."""
    rules = rules or load_rules()
    return {"kaldirac_sicramasi": kaldirac_sicramasi(etiket.get("medyan_kaldirac"), son.get("en_yuksek_kaldirac"), rules),
            "martingale_baslangici": martingale_baslangici(etiket.get("katlama_orani"), son.get("dolumlar"), son.get("hafta_baslangic_ms"), rules),
            "tutma_anomalisi": tutma_anomalisi(son.get("zarardaki_acik_yaslar_saat"), etiket.get("medyan_tutma_saat"), rules)}
