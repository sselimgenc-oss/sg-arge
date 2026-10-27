"""Paper panosu için kurallı, bilgi amaçlı koç bulguları."""

from __future__ import annotations

from typing import Any

import pandas as pd

KAYMA_CARPANI = 1.5
YOGUNLASMA_KITAP = 3


def bulgular(sagliklar: dict[str, dict[str, Any]], fills: pd.DataFrame, alarms: pd.DataFrame, *, simdi: pd.Timestamp) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for kitap, health in sagliklar.items():
        for metric, values in (("MDD oranı", health["mdd"]), ("CUSUM", health["cusum"]), ("sinyal sıklığı", health["sinyal_sikligi"]), ("ardışık kayıp", health["ardisik_kayip"])):
            status = values.get("durum")
            if status in {"yellow", "red"}:
                out.append({"kitap": kitap, "olcu": metric, "deger": values, "esik": status, "tarih": simdi.isoformat(), "seviye": status})
    if not fills.empty:
        entries = fills[fills["tip"] == "giris"].copy()
        if len(entries):
            entries["gun"] = pd.to_datetime(entries["tarih"], utc=True).dt.date
            for day, group in entries.groupby("gun"):
                if group["satir"].nunique() >= YOGUNLASMA_KITAP:
                    out.append({"kitap": "portföy", "olcu": "yoğunlaşma", "deger": int(group["satir"].nunique()), "esik": YOGUNLASMA_KITAP, "tarih": str(day), "seviye": "yellow"})
        slips = pd.to_numeric(fills.get("kayma_pct"), errors="coerce").abs().dropna()
        if len(slips) and (slips > KAYMA_CARPANI * .0005).any():
            out.append({"kitap": "portföy", "olcu": "kayma", "deger": float(slips.max()), "esik": KAYMA_CARPANI * .0005, "tarih": simdi.isoformat(), "seviye": "yellow"})
    if not alarms.empty:
        recent = alarms[pd.to_datetime(alarms["tarih"], utc=True, errors="coerce") >= simdi - pd.Timedelta(hours=24)]
        for row in recent[recent["tip"].isin(["KAYNAK_HATASI", "VERI_ESKI"])].to_dict("records"):
            out.append({"kitap": row["satir"], "olcu": row["tip"], "deger": row["mesaj"], "esik": "son 24 saat", "tarih": row["tarih"], "seviye": "red"})
    return out
