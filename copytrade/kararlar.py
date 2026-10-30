"""Worker kararlarını açık veri dalına sözleşme biçiminde yazar."""
from __future__ import annotations

import argparse
import os
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

FIELDS = ('olay_id', 'zaman', 'karar', 'neden', 'not')
DECISIONS = {'acti', 'atladi'}
REASONS = {'gec_gordum', 'begenmedim', 'diger'}
LEGACY_REASONS = REASONS | {'bakiye_yok'}
NOTES = {''}


def validate(row: object) -> dict:
    if not isinstance(row, dict) or set(row) != set(FIELDS):
        raise ValueError('Geçersiz Worker karar alanları.')
    if not all(isinstance(row[field], str) for field in FIELDS):
        raise ValueError('Karar alanları metin olmalı.')
    if row['karar'] not in DECISIONS or row['neden'] not in LEGACY_REASONS or not row['olay_id']:
        raise ValueError('Geçersiz Worker kararı.')
    if row['not'] not in NOTES:
        raise ValueError('Geçersiz karar etiketi.')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*Z)?', row['zaman']):
        raise ValueError('Geçersiz karar zamanı.')
    result = {field: row[field] for field in FIELDS}
    result['zaman'] = result['zaman'][:10]
    if result['neden'] == 'bakiye_yok':
        result['neden'] = 'diger'
    return result


def merge(path: Path, incoming: list[object]) -> list[dict]:
    current: dict[str, dict] = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if line:
                row = validate(json.loads(line))
                current[row['olay_id']] = row
    for row in incoming:
        valid = validate(row)
        old = current.get(valid['olay_id'])
        if old is None or valid['zaman'] >= old['zaman']:
            current[valid['olay_id']] = valid
    return sorted(current.values(), key=lambda row: (row['zaman'], row['olay_id']))


def fetch(url: str) -> list[object]:
    # Cloudflare varsayılan Python-urllib kimliğini 403 ile reddediyor; açık bir User-Agent gerekir.
    headers = {'User-Agent': 'sg-arge-izleme/1.0', 'Accept': 'application/json'}
    if os.environ.get('KARAR_ANAHTARI'):         # Worker KARAR_ANAHTARI secret'ı tanımlıysa zorunlu (madde 19)
        headers['Authorization'] = f"Bearer {os.environ['KARAR_ANAHTARI']}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:  # nosec B310: URL is a reviewed GitHub variable.
        data = json.load(response)
    if not isinstance(data, list):
        raise ValueError('Worker karar yanıtı liste olmalı.')
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    rows = merge(args.output, fetch(args.url))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n' for row in rows), encoding='utf-8')


if __name__ == '__main__':
    main()
