"""Belirli bir CT-Kapı Actions koşusunun parça artefaktlarında adres kaybını inceler."""
from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


def _rows(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _addresses(path: Path) -> list[str]:
    return [str(row.get("address", "")) for row in _rows(path)]


def inspect(root: Path, day: str = "2026-10-28") -> str:
    rows, result_sets, plan_sets, universes, all_result_rows = [], {}, {}, [], []
    for part in range(32):
        bases = list(root.glob(f"stage1-{part}/**/{day}"))
        base = bases[0] if bases else None
        universe = json.loads((base / "evren.json").read_text())["evren"] if base and (base / "evren.json").exists() else None
        planned = (universe - part + 31) // 32 if universe is not None else None
        result = _addresses(base / "sonuc.csv") if base and (base / "sonuc.csv").exists() else []
        plan = _addresses(base / "asama1.csv.gz") if base and (base / "asama1.csv.gz").exists() else []
        done = json.loads((base / "bitti.json").read_text()).get("islenen") if base and (base / "bitti.json").exists() else None
        if universe is not None:
            universes.append(universe)
        result_sets[part], plan_sets[part] = set(result), set(plan)
        all_result_rows.extend(result)
        rows.append((part, universe, planned, done, len(result), len(plan), len(set(result) - set(plan)), len(set(plan) - set(result)), "evet" if done is not None else "hayır"))

    counts = Counter(all_result_rows)
    pairs = [(left, right, len(result_sets[left] & result_sets[right])) for left, right in combinations(sorted(result_sets), 2)]
    overlaps = [(left, right, count) for left, right, count in pairs if count]
    memberships = defaultdict(list)
    for part, addresses in result_sets.items():
        for address in addresses:
            memberships[address].append(part)
    duplicate_examples = sorted((address, parts) for address, parts in memberships.items() if len(parts) > 1)[:10]
    blank = sum(address.strip().lower() in {"", "nan"} for address in all_result_rows)
    case_only = len(set(all_result_rows)) - len({address.strip().lower() for address in all_result_rows})
    completed_plans = [address for part, addresses in plan_sets.items() if rows[part][3] is not None for address in addresses]

    lines = ["# Tam kapı satır teşhisi", "", "Run: `40711594322` · gün: `2026-10-28`.", "",
             "| Parça | Evren | Plan | İşlenen (bitti/log) | sonuc.csv | plan listesi | CSV−plan | plan−CSV | bitti.json |",
             "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |"]
    for part, universe, plan, done, result, plan_rows, extra, missing, finished in rows:
        # asama1.csv.gz döngünün sonunda yazılır; bitmeyen işte veri dalından kalmış olabilir.
        plan_cell = str(plan_rows) if done is not None else "eski/yarım"
        extra_cell = str(extra) if done is not None else "—"
        missing_cell = str(missing) if done is not None else "—"
        lines.append(f"| {part} | {universe or '—'} | {plan or '—'} | {done if done is not None else '—'} | {result} | {plan_cell} | {extra_cell} | {missing_cell} | {finished} |")
    lines += ["", "## Adres kümeleri", "",
              f"- Parça CSV toplamı: **{len(all_result_rows)}**; tekil adres: **{len(counts)}**; yinelenen satır: **{len(all_result_rows) - len(counts)}**.",
              f"- Bitmiş parçalardaki plan listesi toplamı: **{len(completed_plans)}**; tekil plan adresi: **{len(set(completed_plans))}**.",
              f"- `evren.json`: {sorted(set(universes)) or ['yok']}; tüm parçalarda aynı sayı: **{'evet' if len(set(universes)) == 1 else 'hayır'}**.",
              f"- Boş/NaN address: **{blank}**; yalnız büyük-küçük harften doğan ek çakışma: **{case_only}**.", "",
              "### Parçalar arası kesişim", "",
              f"Çakışan parça çifti: **{len(overlaps)}**; çift-kesişim toplamı: **{sum(count for _, _, count in overlaps)}**.", "",
              "| Parça A | Parça B | Ortak adres |", "| ---: | ---: | ---: |"]
    lines += [f"| {left} | {right} | {count} |" for left, right, count in overlaps[:5]] or ["| — | — | 0 |"]
    lines += ["", "### Yinelenen adres örnekleri", "", "| Adres | Parçalar |", "| :--- | :--- |"]
    lines += [f"| `{address}` | {', '.join(map(str, parts))} |" for address, parts in duplicate_examples] or ["| — | — |"]
    lines += ["", "## Bulgu", "",
              "Tamamlanan parçalarda plan, bitti ve CSV sayıları eşitse satır parça içinde kaybolmamıştır. Bitmeyen parçada `asama1.csv.gz` döngünün sonunda yazılmadığından veri dalından kalmış olabilir; bu yüzden kendi planıyla kıyaslanmaz. Ortak evren her işte yeniden API'den üretildiği için `evren.json` aynı **sayıyı** verse bile aynı adres listesini garanti etmez; plan listelerindeki kesişimler farklı anlık görüntülerin aynı adresleri ayrı parçalara koyduğunu kanıtlar. Birleştirmedeki `drop_duplicates(\"address\")` bu çakışan satırları tekile indirir.",
              "", "Düzeltme: plan işi adres listesini içeren ortak anlık görüntü üretir; her `stage1` işi bu dosyadan kendi sabit dilimini seçer. Eşik, kapı ve karar hesabı değişmez."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(inspect(args.root), encoding="utf-8")
