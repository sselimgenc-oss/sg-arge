"""Ön kayıt 1.6 oda değişimlerini, mevcut sanal-kopya durumuyla raporlar.

Bu modül yalnız rapor üretir; seçim, kapı ve izleme listesini değiştirmez.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from copytrade.gecis import oku


def rapor(kayit_yolu: Path, durum_yolu: Path) -> dict:
    durum = json.loads(durum_yolu.read_text(encoding='utf-8')) if durum_yolu.exists() else {'traderlar': []}
    traderlar = {str(t.get('adres', '')).lower(): t for t in durum.get('traderlar', [])}
    changes = []
    totals: dict[str, dict] = defaultdict(lambda: {'adet': 0, 'degisim_alfasi': []})
    for row in oku(kayit_yolu):
        out, incoming = traderlar.get(row['cikarilan'].lower()), traderlar.get(row['alinan'].lower())
        out_ret = out.get('sanal_kopya', {}).get('toplam') if out else None
        in_ret = incoming.get('sanal_kopya', {}).get('toplam') if incoming else None
        alpha = in_ret - out_ret if isinstance(in_ret, (int, float)) and isinstance(out_ret, (int, float)) else None
        item = {**row, 'cikarilan_sanal_net': out_ret, 'alinan_sanal_net': in_ret, 'degisim_alfasi': alpha,
                'durum': 'hazir' if alpha is not None else 'izleme verisi bekleniyor'}
        changes.append(item)
        totals[row['gerekce']]['adet'] += 1
        if alpha is not None:
            totals[row['gerekce']]['degisim_alfasi'].append(alpha)
    reasons = {key: {'adet': value['adet'], 'ortalama_degisim_alfasi': (sum(value['degisim_alfasi']) / len(value['degisim_alfasi']) if value['degisim_alfasi'] else None)}
               for key, value in sorted(totals.items())}
    return {'surum': 1, 'degisimler': changes, 'gerekce_toplamlari': reasons,
            'not': 'kullanici_takdiri gerekçesi diğer gerekçelerden ayrı tutulur; sonuçlar sanal kopyadır.'}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kayit', type=Path, default=Path('copytrade/degisim.jsonl'))
    parser.add_argument('--durum', type=Path, default=Path('izleme/durum.json'))
    parser.add_argument('--cikti', type=Path, default=Path('izleme/degisim.json'))
    args = parser.parse_args(argv)
    args.cikti.parent.mkdir(parents=True, exist_ok=True)
    args.cikti.write_text(json.dumps(rapor(args.kayit, args.durum), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
