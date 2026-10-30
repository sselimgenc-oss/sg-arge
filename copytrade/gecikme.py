"""Worker'ın GET /gecikme'de ölçtüğü gerçek algılama gecikmesini okur, oda genelinde özet üretir ve
``izleme/gecikme.json``'a yazar (E1 devamı, Sol denetimi 2026-10-30 — `docs/DENETIM_ETRE_GECIS_2026-10-30.md`).

Bu, ``copytrade/saglik_hatti.py``'deki ``acik_pozisyon_yasi_dk_medyan``'dan ayrıdır: burada ölçülen, trader'ın
gerçek Hyperliquid dolum zamanı ile Worker'ın onu görmesi arasındaki **gerçek** süre (Worker dakikalık çalıştığı
için aynı mantıkla `copytrade/kararlar.py`'nin izlediği "Worker'dan açık veriye aktar" desenini izler).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd


def ozet(rows: list[dict]) -> dict:
    """Saf fonksiyon: Worker'dan gelen ``{trader, gecikme_dk, zaman}`` satırlarından oda genelinde özet üretir."""
    degerler = [float(row['gecikme_dk']) for row in rows if row.get('gecikme_dk') is not None]
    if not degerler:
        return {'n': 0, 'gecikme_dk_medyan': None, 'gecikme_dk_maks': None}
    return {
        'n': len(degerler),
        'gecikme_dk_medyan': float(pd.Series(degerler).median()),
        'gecikme_dk_maks': float(max(degerler)),
    }


def fetch(url: str) -> list[dict]:
    # Cloudflare varsayılan Python-urllib kimliğini 403 ile reddediyor; açık bir User-Agent gerekir.
    request = Request(url, headers={'User-Agent': 'sg-arge-izleme/1.0', 'Accept': 'application/json'})
    with urlopen(request, timeout=20) as response:  # nosec B310: URL is a reviewed GitHub variable.
        data = json.load(response)
    if not isinstance(data, list):
        raise ValueError('Worker gecikme yanıtı liste olmalı.')
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = fetch(args.url)
    result = {**ozet(rows), 'trader_detay': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
