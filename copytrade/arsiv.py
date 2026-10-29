"""Yalnız eklemeli, R2 imleçli halka açık Hyperliquid arşivi."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from copytrade.izleme_motoru import load_list
from copytrade.kurallar import load_rules
from copytrade.tarama import PublicClient

SEMA_SURUMU = 1
FIFTEEN_MINUTES = 15 * 60 * 1000
ONE_HOUR = 60 * 60 * 1000


def day(now: datetime) -> str:
    return now.astimezone(UTC).date().isoformat()


def key(kind: str, row: dict) -> str:
    if kind == "dolum":
        return f"{row.get('adres')}:{row.get('tid')}"
    if kind == "funding":
        return f"{row.get('adres')}:{row.get('time')}:{row.get('hash')}"
    if kind == "mum_1dk":
        return f"{row.get('coin', row.get('s'))}:{row.get('t', row.get('time'))}"
    return hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()


class Arsiv:
    def __init__(self, root: Path, now: datetime | None = None):
        self.root = Path(root)
        self.now = now or datetime.now(UTC)

    def folder(self, kind: str) -> Path:
        return self.root / f"tur={kind}" / f"gun={day(self.now)}"

    def cursor_start(self, kind: str, subject: str, fallback: int) -> int:
        path = self.root / f"tur={kind}" / "son.json"
        if not path.exists():
            return fallback
        return int(json.loads(path.read_text()).get(subject, fallback))

    def set_cursor(self, kind: str, subject: str, value: int) -> None:
        path = self.root / f"tur={kind}" / "son.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        saved = json.loads(path.read_text()) if path.exists() else {}
        saved[subject] = int(value)
        path.write_text(json.dumps(saved, sort_keys=True), encoding="utf-8")

    def append(self, kind: str, rows: list[dict], *, subject: str | None = None, cursor: int | None = None) -> int:
        """Imleç aralığı çakışmadığı için eski parquet parçalarını okumadan ekle."""
        self.folder(kind).mkdir(parents=True, exist_ok=True)
        captured = int(self.now.timestamp() * 1000)
        values = []
        for raw in rows:
            row = dict(raw)
            row.update(sema_surumu=SEMA_SURUMU, alindi_ms=captured)
            values.append({"_anahtar": key(kind, row), "sema_surumu": SEMA_SURUMU, "alindi_ms": captured,
                           "veri": json.dumps(row, sort_keys=True, default=str)})
        if values:
            pd.DataFrame(values).drop_duplicates("_anahtar").to_parquet(
                self.folder(kind) / f"parca-{time.time_ns()}.parquet", index=False, compression="zstd")
        if subject is not None and cursor is not None:
            self.set_cursor(kind, subject, cursor)
        return len(values)

    def empty_schema(self, kind: str) -> None:
        path = self.folder(kind) / "sema.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            pd.DataFrame(columns=["_anahtar", "sema_surumu", "alindi_ms", "veri"]).to_parquet(path, index=False, compression="zstd")

    def poll(self, kind: str, subject: str, interval_ms: int) -> None:
        path = self.root / "tur=kapsam" / f"gun={day(self.now)}" / "yoklamalar.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        polls = json.loads(path.read_text()) if path.exists() else []
        polls.append({"tur": kind, "ozne": subject, "zaman_ms": int(self.now.timestamp() * 1000), "aralik_ms": interval_ms})
        path.write_text(json.dumps(polls), encoding="utf-8")

    def summary(self) -> dict:
        path = self.root / "tur=kapsam" / f"gun={day(self.now)}" / "yoklamalar.json"
        polls = json.loads(path.read_text()) if path.exists() else []
        gaps = expected = 0
        for _, group in pd.DataFrame(polls).groupby(["tur", "ozne"]) if polls else []:
            group = group.sort_values("zaman_ms")
            interval = int(group.iloc[0].aralik_ms)
            timestamps = list(group.zaman_ms)
            expected += len(timestamps)
            gaps += sum(max(0, (later - earlier) // interval - 1)
                        for earlier, later in zip(timestamps, timestamps[1:])
                        if later - earlier > int(load_rules()["arsiv_bosluk_carpani"]) * interval)
        result = {"yoklama": expected, "bosluk": gaps, "oran": gaps / max(1, expected)}
        (path.parent / "ozet.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        if result["oran"] > float(load_rules()["arsiv_bosluk_esigi"]):
            raise RuntimeError("Arşiv boşluk oranı eşiği aşıldı")
        return result


def secim_havuzu(secim: Path | None) -> set[str]:
    """``secim.json`` havuz katı (v1.3: 185 adres). Kapı sonuçlarından bağımsız garanti: birincil analiz havuzun tamamını ister."""
    if secim is None:
        return set()
    result = json.loads(Path(secim).read_text(encoding="utf-8"))
    return {a.lower() for a, e in result["adresler"].items() if "havuz" in e.get("kollar", [])}


def pool(root: Path, gate_root: Path | None, secim: Path | None = None) -> list[str]:
    addresses = {row["adres"].lower() for row in load_list(root / "copytrade/izleme_listesi.yaml")} | secim_havuzu(secim)
    if gate_root:
        for result in gate_root.glob("*/sonuc.csv"):
            for _, row in pd.read_csv(result).iterrows():
                if str(row.get("adim1")) == "Geçti" and str(row.get("adim2")) == "Geçti":
                    addresses.add(str(row.get("address", row.get("adres", ""))).lower())
    return sorted(address for address in addresses if address.startswith("0x"))


def next_cursor(rows: list[dict], fallback: int) -> int:
    times = [int(row.get("time", row.get("t", -1))) for row in rows]
    return max(times) + 1 if times and max(times) >= 0 else fallback


def collect(root: Path, output: Path, kinds: set[str], *, gate_root: Path | None = None, client=None, now=None, secim: Path | None = None):
    now = now or datetime.now(UTC)
    archive, api = Arsiv(output, now), client or PublicClient()
    fallback = int((now - timedelta(hours=1)).timestamp() * 1000)
    coins, addresses = set(), pool(root, gate_root, secim)
    for address in addresses:
        if "dolum" in kinds:
            rows = [dict(row, adres=address) for row in api.fills(address, archive.cursor_start("dolum", address, fallback))]
            coins.update(str(row["coin"]) for row in rows if row.get("coin"))
            archive.append("dolum", rows, subject=address, cursor=next_cursor(rows, int(now.timestamp() * 1000)))
            archive.poll("dolum", address, ONE_HOUR)
        if "funding" in kinds:
            start = archive.cursor_start("funding", address, fallback)
            rows = [dict(row, adres=address) for row in api.info({"type": "userFunding", "user": address, "startTime": start})]
            archive.append("funding", rows, subject=address, cursor=next_cursor(rows, int(now.timestamp() * 1000)))
            archive.poll("funding", address, ONE_HOUR)
        if "pozisyon" in kinds:
            state = api.info({"type": "clearinghouseState", "user": address}, weight=2)
            archive.append("pozisyon", [{"adres": address, "durum": state}])
            for position in state.get("assetPositions", []) if isinstance(state, dict) else []:
                coin = position.get("position", {}).get("coin")
                if coin:
                    coins.add(str(coin))
            archive.poll("pozisyon", address, FIFTEEN_MINUTES)
    if "mum_1dk" in kinds:
        for coin in sorted(coins):
            start = archive.cursor_start("mum_1dk", coin, fallback)
            rows = api.candles(coin, start, int(now.timestamp() * 1000), "1m")
            archive.append("mum_1dk", rows, subject=coin, cursor=next_cursor(rows, int(now.timestamp() * 1000)))
            archive.poll("mum_1dk", coin, FIFTEEN_MINUTES)
    if "leaderboard" in kinds:
        archive.append("leaderboard", api.leaderboard())
        archive.poll("leaderboard", "tum", 7 * 24 * ONE_HOUR)
    if "olay" in kinds:
        archive.empty_schema("olay")
    summary = archive.summary()
    measurement = {"havuz": len(addresses), "istek_agirligi": getattr(api.limiter, "weight_used", 0)}
    (archive.root / "tur=kapsam" / f"gun={day(now)}" / "k8.json").write_text(json.dumps(measurement, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary, measurement


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("arsiv"))
    parser.add_argument("--kapi-root", type=Path)
    parser.add_argument("--secim", type=Path, help="secim.json: havuz katı arşive her zaman girer")
    parser.add_argument("--tur", default="dolum,funding,pozisyon")
    args = parser.parse_args()
    print(collect(args.root, args.output, set(args.tur.split(",")), gate_root=args.kapi_root, secim=args.secim))
