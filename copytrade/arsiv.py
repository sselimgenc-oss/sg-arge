"""Append-only public Hyperliquid archive.  Credentials never enter this module."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from copytrade.izleme_motoru import load_list
from copytrade.kurallar import load_rules
from copytrade.tarama import PublicClient

SEMA_SURUMU = 1


def _day(now: datetime) -> str:
    return now.astimezone(UTC).date().isoformat()


def _key(kind: str, row: dict) -> str:
    if kind == "dolum":
        return f"{row.get('adres','')}:{row.get('tid','')}"
    if kind == "funding":
        return f"{row.get('adres','')}:{row.get('time','')}:{row.get('hash','')}"
    if kind == "mum_1dk":
        return f"{row.get('coin','')}:{row.get('t', row.get('time',''))}"
    if kind == "pozisyon":
        return f"{row.get('adres','')}:{row.get('alindi_ms','')}"
    return hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()


class Arsiv:
    def __init__(self, root: Path, now: datetime | None = None):
        self.root, self.now = root, now or datetime.now(UTC)

    def append(self, kind: str, rows: list[dict]) -> int:
        """Write only unseen rows to a new zstd parquet part."""
        folder = self.root / f"tur={kind}" / f"gun={_day(self.now)}"
        folder.mkdir(parents=True, exist_ok=True)
        known: set[str] = set()
        for file in folder.glob("*.parquet"):
            known.update(pd.read_parquet(file, columns=["_anahtar"])["_anahtar"].astype(str))
        stamped = []
        for raw in rows:
            row = dict(raw); row.setdefault("alindi_ms", int(self.now.timestamp() * 1000)); row["sema_surumu"] = SEMA_SURUMU
            row["_anahtar"] = _key(kind, row)
            if row["_anahtar"] not in known:
                known.add(row["_anahtar"]); stamped.append({"_anahtar": row["_anahtar"], "sema_surumu": row["sema_surumu"], "alindi_ms": row["alindi_ms"], "veri": json.dumps(row, sort_keys=True, default=str)})
        if stamped:
            name = f"parca-{int(time.time_ns())}.parquet"
            pd.DataFrame(stamped).to_parquet(folder / name, index=False, compression="zstd")
        return len(stamped)

    def kapsam(self, counts: dict[str, int], expected: dict[str, int]) -> Path:
        rows = []
        for kind in sorted(set(counts) | set(expected)):
            want, got = expected.get(kind, 0), counts.get(kind, 0)
            rows.append({"tur": kind, "satir": got, "beklenen": want, "bosluk": max(0, want - got)})
        path = self.root / "tur=kapsam" / f"gun={_day(self.now)}" / "ozet.json"
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        gap = sum(x["bosluk"] for x in rows) / max(1, sum(x["beklenen"] for x in rows))
        if gap > float(load_rules()["arsiv_max_bosluk_orani"]):
            raise RuntimeError(f"Arşiv boşluk oranı %{gap:.1%}; kural eşiğini aşıyor")
        return path


def havuz(root: Path) -> list[str]:
    """The single pool source: pre-filtered gate rows plus the explicit watch list."""
    addresses = {x["adres"].lower() for x in load_list(root / "copytrade/izleme_listesi.yaml")}
    for result in (root / "copytrade" / "kapi").glob("*/sonuc.csv"):
        table = pd.read_csv(result)
        for _, row in table.iterrows():
            if str(row.get("adim1")) == "Geçti" and str(row.get("adim2")) == "Geçti":
                addresses.add(str(row.get("address", row.get("adres", ""))).lower())
    return sorted(x for x in addresses if x.startswith("0x"))


def collect(root: Path, out: Path, kinds: set[str]) -> None:
    now, archive, client = datetime.now(UTC), Arsiv(out), PublicClient()
    pool, counts, expected = havuz(root), {}, {}
    if "leaderboard" in kinds:
        counts["leaderboard"] = archive.append("leaderboard", client.leaderboard()); expected["leaderboard"] = 1
    for address in pool:
        if "dolum" in kinds:
            rows = [dict(x, adres=address) for x in client.fills(address, int((now-timedelta(hours=1)).timestamp()*1000))]
            counts["dolum"] = counts.get("dolum", 0) + archive.append("dolum", rows); expected["dolum"] = expected.get("dolum", 0) + 1
        if "funding" in kinds:
            rows = [dict(x, adres=address) for x in client.info({"type":"userFunding","user":address,"startTime":int((now-timedelta(hours=1)).timestamp()*1000)})]
            counts["funding"] = counts.get("funding", 0) + archive.append("funding", rows); expected["funding"] = expected.get("funding", 0) + 1
        if "pozisyon" in kinds:
            counts["pozisyon"] = counts.get("pozisyon", 0) + archive.append("pozisyon", [{"adres":address,"durum":client.info({"type":"clearinghouseState","user":address}, weight=2)}]); expected["pozisyon"] = expected.get("pozisyon", 0) + 1
    archive.kapsam(counts, expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=Path(".")); parser.add_argument("--output", type=Path, default=Path("arsiv")); parser.add_argument("--tur", default="dolum,funding,pozisyon")
    args = parser.parse_args(); collect(args.root, args.output, set(args.tur.split(",")))
