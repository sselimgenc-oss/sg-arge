"""Arşiv kesinti alarmı: ``arsiv.yml`` art arda başarısız (ya da hiç koşmayan) süre ``arsiv_kesinti_saat``'i aşarsa kırmızı uyarı.

Neden (Argon A21): halka açık API yalnız son 10.000 dolumu verir; çok aktif adreste ~1 haftadan uzun boşluk geri alınamaz.
Girdi: GitHub Actions ``workflows/arsiv.yml/runs`` yanıtı (``gh api``). Eşik yalnız ``kurallar.yaml``. Alarmda çıkış kodu 1 (iş kırmızı),
``--bilgi`` ile (haftalık rapor) çıkış 0 ama özet yine ``alarm: true`` yazar. Özet kol bazında getiri içermez.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from copytrade.kurallar import load_rules


def _zaman(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def kesinti(runs: list[dict[str, Any]], now: datetime, esik_saat: float) -> dict[str, Any]:
    """Son başarılı koşudan (``conclusion == success``, ``updated_at``) bu yana geçen saat; esik **aşılırsa** (eşitlikte değil) alarm. Başarılı koşu yoksa alarm."""
    basarili = [_zaman(r["updated_at"]) for r in runs if r.get("conclusion") == "success" and r.get("updated_at")]
    son = max(basarili) if basarili else None
    saat = None if son is None else (now - son).total_seconds() / 3600
    basarisiz = sum(1 for r in runs if r.get("conclusion") in {"failure", "timed_out", "cancelled"} and (son is None or _zaman(r["updated_at"]) > son))
    return {"son_basari": son.isoformat() if son else None, "kesinti_saat": None if saat is None else round(saat, 2), "esik_saat": esik_saat,
            "ardisik_basarisiz": basarisiz, "alarm": son is None or saat > esik_saat}


def mesaj(o: dict[str, Any]) -> str:
    if o["son_basari"] is None:
        return f"Arşiv: kayıtlı hiç başarılı koşu yok (eşik {o['esik_saat']} saat)."
    return f"Arşiv: son başarılı koşu {o['son_basari']} ({o['kesinti_saat']} saat önce; eşik {o['esik_saat']} saat; ondan sonra {o['ardisik_basarisiz']} başarısız koşu)."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=Path, required=True, help="`gh api repos/<repo>/actions/workflows/arsiv.yml/runs?per_page=50` çıktısı")
    parser.add_argument("--yaz", type=Path, default=None, help="özet JSON (haftalık raporun --arsiv-kesinti girdisi)")
    parser.add_argument("--bilgi", action="store_true", help="alarmda bile çıkış 0 (haftalık rapor: özet alarm=true yazar, rapor kırmızı işaretler)")
    args = parser.parse_args(argv)
    data = json.loads(args.runs.read_text(encoding="utf-8"))
    sonuc = kesinti(data["workflow_runs"] if isinstance(data, dict) else data, datetime.now(UTC), float(load_rules()["arsiv_kesinti_saat"]))
    metin = mesaj(sonuc)
    if args.yaz:
        args.yaz.write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding="utf-8")
    ozet = os.environ.get("GITHUB_STEP_SUMMARY")
    if ozet:
        with open(ozet, "a", encoding="utf-8") as handle:
            handle.write(("🔴 **ARŞİV KESİNTİSİ** — " if sonuc["alarm"] else "🟢 ") + metin + "\n")
    print(("::error::ARŞİV KESİNTİSİ " if sonuc["alarm"] else "") + metin)
    return 1 if sonuc["alarm"] and not args.bilgi else 0


if __name__ == "__main__":
    raise SystemExit(main())
