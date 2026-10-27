"""Worker kararlarını açık veri dalına sözleşme biçiminde yazar."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

FIELDS = ('olay_id', 'zaman', 'karar', 'neden', 'not')
DECISIONS = {'acti', 'atladi'}
REASONS = {'gec_gordum', 'begenmedim', 'bakiye_yok', 'diger'}


def validate(row: object) -> dict:
    if not isinstance(row, dict) or set(row) != set(FIELDS):
        raise ValueError('Geçersiz Worker karar alanları.')
    if not all(isinstance(row[field], str) for field in FIELDS):
        raise ValueError('Karar alanları metin olmalı.')
    if row['karar'] not in DECISIONS or row['neden'] not in REASONS or not row['olay_id']:
        raise ValueError('Geçersiz Worker kararı.')
    return {field: row[field] for field in FIELDS}


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
    with urlopen(url, timeout=20) as response:  # nosec B310: URL is a reviewed GitHub variable.
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
