"""TV-2 footprint verisi: Binance aggTrades arşivinden (data.binance.vision) bar ve fiyat seviyesi başına alıcı/satıcı hacmi.

Her aggTrade'in `is_buyer_maker` bayrağı vardır: yanlışsa alıcı agresif (buy), doğruysa satıcı (sell). Günlük zip indirilir,
`dk` dakikalık UTC barlarına ve `taban` adımlı fiyat seviyelerine toplanır, ham dosya silinir. Sonuç
`data/tv2/footprint/<SEMBOL>_<piyasa>_<dk>.parquet` (sütunlar: bar_ms, seviye, buy, sell; fiyat = seviye x taban).
Yorumlayıcı satır boyunu (ticks_per_row x mintick) bu seviyelerden birleştirir; taban satırdan küçük seçilir.

    python -m backtests.tv2_footprint BTCUSDT spot 120 2026-03-12 [2026-10-24]
"""

from __future__ import annotations

import io
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
KLASOR = ROOT / "data" / "tv2" / "footprint"
TABAN = {"BTCUSDT": 1.0, "ETHUSDT": 0.1}          # fiyat seviyesi adımı (USD); satırlar bunun katı
YOL = {"spot": "spot", "um": "futures/um"}


def dosya(sembol: str, piyasa: str, dk: int) -> Path:
    return KLASOR / f"{sembol}_{piyasa}_{dk}.parquet"


def _gun(sembol: str, piyasa: str, gun: pd.Timestamp, dk: int, taban: float) -> pd.DataFrame | None:
    url = (f"https://data.binance.vision/data/{YOL[piyasa]}/daily/aggTrades/{sembol}/"
           f"{sembol}-aggTrades-{gun:%Y-%m-%d}.zip")
    for deneme in range(4):
        try:
            r = requests.get(url, timeout=120)
            break
        except requests.RequestException:
            time.sleep(2 ** (deneme + 1))
    else:
        return None
    if r.status_code == 404:
        return None
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        ham = z.read(z.namelist()[0])
    ilk = ham[:200].decode(errors="ignore")
    basliklı = not ilk[:1].isdigit()
    df = pd.read_csv(io.BytesIO(ham), header=0 if basliklı else None, usecols=[1, 2, 5, 6])
    df.columns = ["price", "qty", "ts", "maker"]
    ts = df["ts"].to_numpy(np.int64)
    ts = np.where(ts > 10 ** 14, ts // 1000, ts)                    # spot 2025'ten beri mikrosaniye
    bar = ts // (dk * 60_000) * (dk * 60_000)
    seviye = np.floor(df["price"].to_numpy(float) / taban).astype(np.int64)
    maker = df["maker"].astype(str).str.lower().isin(["true", "1"]).to_numpy()
    q = df["qty"].to_numpy(float)
    out = pd.DataFrame({"bar_ms": bar, "seviye": seviye, "buy": np.where(maker, 0.0, q), "sell": np.where(maker, q, 0.0)})
    return out.groupby(["bar_ms", "seviye"], as_index=False)[["buy", "sell"]].sum()


def hazirla(sembol: str, piyasa: str, dk: int, bas: str, bit: str | None = None) -> Path:
    """Eksik günleri indirip özetler (kaldığı yerden devam eder)."""
    taban = TABAN[sembol]
    KLASOR.mkdir(parents=True, exist_ok=True)
    hedef = dosya(sembol, piyasa, dk)
    kayit = hedef.with_suffix(".gunler.json")
    yapilan = set(json.loads(kayit.read_text())) if kayit.exists() else set()
    parcalar = [pd.read_parquet(hedef)] if hedef.exists() else []
    son = pd.Timestamp(bit) if bit else pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() - pd.Timedelta(days=1)
    for gun in pd.date_range(bas, son, freq="D"):
        anahtar = f"{gun:%Y-%m-%d}"
        if anahtar in yapilan:
            continue
        p = _gun(sembol, piyasa, gun, dk, taban)
        if p is not None:
            parcalar.append(p)
        yapilan.add(anahtar)
        if len(yapilan) % 10 == 0:                   # ara kayıt
            pd.concat(parcalar).to_parquet(hedef)
            kayit.write_text(json.dumps(sorted(yapilan)))
            print(anahtar, flush=True)
    if parcalar:
        tum = pd.concat(parcalar).groupby(["bar_ms", "seviye"], as_index=False)[["buy", "sell"]].sum()
        tum.to_parquet(hedef)
    kayit.write_text(json.dumps(sorted(yapilan)))
    return hedef


def oku(sembol: str, piyasa: str, dk: int) -> tuple[dict, float] | None:
    """{bar_ms: (seviyeler, buy, sell)} ve taban; dosya yoksa None."""
    hedef = dosya(sembol, piyasa, dk)
    if not hedef.exists():
        return None
    df = pd.read_parquet(hedef).sort_values(["bar_ms", "seviye"])
    out = {}
    for bar, g in df.groupby("bar_ms"):
        out[int(bar)] = (g["seviye"].to_numpy(), g["buy"].to_numpy(), g["sell"].to_numpy())
    return out, TABAN[sembol]


if __name__ == "__main__":
    s, piyasa, dk, bas = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    print(hazirla(s, piyasa, dk, bas, sys.argv[5] if len(sys.argv) > 5 else None))
