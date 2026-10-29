"""Deneme defteri (``arastirma/copytrade/deneme_defteri.jsonl``): her keşif denemesi **sonucu görülmeden önce** bir satır olarak yazılır.

Yalnız eklemeli: önkayıt satırı (``tur: onkayit``; tarih, hipotez, skor tanımı, pencere, başarı ölçütü, kod sha), sonuç sonra ayrı satırla (``tur: sonuc``,
``id`` ile bağlı). Satır silinmez/değiştirilmez; sonuç yazmak için önkayıt gerekir, bir önkayıda tek sonuç yazılır. Toplam deneme sayısı (önkayıt sayısı) rapora
ve sonra panoya yazılır: çok deneme yapıldıysa tek 'anlamlı' sonucun ağırlığı düşer.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFTER = Path("arastirma/copytrade/deneme_defteri.jsonl")
ONKAYIT_ALANLARI = ("id", "tarih", "hipotez", "skor_tanimi", "pencere", "basari_olcutu", "kod_sha")


def oku(yol: Path = DEFTER) -> list[dict[str, Any]]:
    if not Path(yol).exists():
        return []
    return [json.loads(satir) for satir in Path(yol).read_text(encoding="utf-8").splitlines() if satir.strip()]


def _ekle(yol: Path, satir: dict[str, Any]) -> None:
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    with yol.open("a", encoding="utf-8") as handle:         # yalnız ekleme
        handle.write(json.dumps(satir, ensure_ascii=False, sort_keys=True) + "\n")


def kod_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "bilinmiyor"


def onkayit(id: str, hipotez: str, skor_tanimi: str, pencere: str, basari_olcutu: str, *, yol: Path = DEFTER, tarih: str | None = None, sha: str | None = None) -> dict[str, Any]:
    """Sonuç görülmeden önce çağrılır. Aynı ``id`` ikinci kez yazılamaz."""
    if any(r["id"] == id for r in oku(yol)):
        raise ValueError(f"deneme zaten kayıtlı: {id}")
    satir = {"tur": "onkayit", "id": id, "tarih": tarih or datetime.now(UTC).date().isoformat(), "hipotez": hipotez, "skor_tanimi": skor_tanimi,
             "pencere": pencere, "basari_olcutu": basari_olcutu, "kod_sha": sha or kod_sha()}
    if any(not str(satir[k]).strip() for k in ONKAYIT_ALANLARI):
        raise ValueError("önkayıtta boş alan olamaz")
    _ekle(yol, satir)
    return satir


def sonuc(id: str, ozet: str, *, yol: Path = DEFTER, tarih: str | None = None) -> dict[str, Any]:
    """Önkayıtlı denemenin sonucu (bir kez). Önkayıt yoksa ya da sonuç zaten varsa hata."""
    satirlar = oku(yol)
    if not any(r["tur"] == "onkayit" and r["id"] == id for r in satirlar):
        raise ValueError(f"önkayıt yok: {id} (sonuç görülmeden önce kayıt şart)")
    if any(r["tur"] == "sonuc" and r["id"] == id for r in satirlar):
        raise ValueError(f"sonuç zaten yazıldı: {id}")
    satir = {"tur": "sonuc", "id": id, "tarih": tarih or datetime.now(UTC).date().isoformat(), "ozet": ozet}
    _ekle(yol, satir)
    return satir


def sayim(yol: Path = DEFTER) -> dict[str, int]:
    """Toplam deneme (önkayıt), sonucu yazılmış ve bekleyen sayısı."""
    satirlar = oku(yol)
    on = {r["id"] for r in satirlar if r["tur"] == "onkayit"}
    bitti = {r["id"] for r in satirlar if r["tur"] == "sonuc"}
    return {"toplam": len(on), "sonuclu": len(on & bitti), "bekleyen": len(on - bitti)}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--yol", type=Path, default=DEFTER)
    alt = parser.add_subparsers(dest="komut", required=True)
    o = alt.add_parser("onkayit")
    for ad in ("id", "hipotez", "skor-tanimi", "pencere", "basari-olcutu"):
        o.add_argument("--" + ad, required=True)
    s = alt.add_parser("sonuc")
    s.add_argument("--id", required=True)
    s.add_argument("--ozet", required=True)
    alt.add_parser("sayim")
    args = parser.parse_args(argv)
    if args.komut == "onkayit":
        print(onkayit(args.id, args.hipotez, args.skor_tanimi, args.pencere, args.basari_olcutu, yol=args.yol))
    elif args.komut == "sonuc":
        print(sonuc(args.id, args.ozet, yol=args.yol))
    else:
        print(sayim(args.yol))


if __name__ == "__main__":
    main()
