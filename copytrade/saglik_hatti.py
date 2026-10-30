"""Veri hattı sağlığı — Etre ``kalite.py`` karşılığı (GOREV_ETRE_GECIS.md E1).

Mevcut durum.json alanları (mutabakat, işaret eksikliği, veri geçerliliği, ışık) kol düzeyinde
(varsayılan "oda") tek kayda toplanır; hiçbir yeni ölçüm hesaplamaz, hiçbir pozisyonu etkilemez —
yalnız rapor. ``olc()`` saf ölçü fonksiyonu, ``kontrol()`` saf eşik fonksiyonudur (Etre deseni:
ayarlanabilir eşik sözlüğü + tekrarsız uyarı, tekrarlama bastırması çağıran tarafta — bkz. Worker
``checkStateAlerts``/``uyari_durum``).
"""

from __future__ import annotations

import pandas as pd

ODA_KOLU = 'oda'

ESIKLER = {
    'veri_tazeligi_kirmizi_dk': 180.0,
    'veri_tazeligi_sari_dk': 90.0,
    'yetim_golge_orani_kirmizi': 0.10,
    'veri_hata_orani_kirmizi': 0.20,
    'veri_hata_orani_sari': 0.10,
    'isaret_eksik_toplam_sari': 3,
}

# Bir pozisyonun açılışı bu süreden eskiyse "taze sinyal" sayılmaz (sinyal gecikmesi ölçüsüne girmez).
SINYAL_TAZELIK_DK = 180.0


def _kol_uyeleri(traderlar: list[dict], kol: str) -> list[dict]:
    return [t for t in traderlar if kol in (t.get('kollar') or [t.get('kol')])]


def _dakika(onceki, sonraki) -> float | None:
    try:
        return (pd.Timestamp(sonraki) - pd.Timestamp(onceki)).total_seconds() / 60.0
    except (ValueError, TypeError):
        return None


def olc(durum: dict, simdi, kol: str = ODA_KOLU) -> dict:
    """Tek kol için sağlık ölçüsü. ``durum``: ``docs/VERI_SOZLESMESI.md`` şemasındaki üst düzey sözlük."""
    uyeler = _kol_uyeleri(durum.get('traderlar') or [], kol)
    n = len(uyeler)
    if n == 0:
        return {
            'kol': kol, 'n': 0, 'veri_tazeligi_dk': None, 'yetim_golge_orani': None,
            'isaret_eksik_toplam': 0, 'veri_hata_orani': None, 'kirmizi_sayisi': 0, 'sari_sayisi': 0,
            'sinyal_gecikme_dk_medyan': None,
        }

    uretildi = durum.get('uretildi')
    veri_tazeligi_dk = _dakika(uretildi, simdi) if uretildi else None
    if veri_tazeligi_dk is not None and veri_tazeligi_dk < 0:
        veri_tazeligi_dk = 0.0

    yetim_toplam = sum(int((t.get('veri_kalitesi') or {}).get('mutabakat', {}).get('yetim') or 0) for t in uyeler)
    mutabakat_satir_toplam = sum(int((t.get('veri_kalitesi') or {}).get('mutabakat', {}).get('toplam') or 0) for t in uyeler)
    yetim_golge_orani = (yetim_toplam / mutabakat_satir_toplam) if mutabakat_satir_toplam else None

    isaret_eksik_toplam = sum(int((t.get('sanal_kopya') or {}).get('isaret_eksik') or 0) for t in uyeler)
    hata_sayisi = sum(1 for t in uyeler if t.get('gecerli') is False)
    veri_hata_orani = hata_sayisi / n

    kirmizi_sayisi = sum(1 for t in uyeler if (t.get('saglik') or {}).get('isik') == 'kirmizi')
    sari_sayisi = sum(1 for t in uyeler if (t.get('saglik') or {}).get('isik') == 'sari')

    gecikmeler: list[float] = []
    if uretildi:
        for t in uyeler:
            for p in (t.get('pozisyonlar') or []):
                acilis = p.get('acilis')
                if not acilis:
                    continue
                dk = _dakika(acilis, uretildi)
                if dk is not None and 0 <= dk <= SINYAL_TAZELIK_DK:
                    gecikmeler.append(dk)
    sinyal_gecikme_dk_medyan = float(pd.Series(gecikmeler, dtype='float64').median()) if gecikmeler else None

    return {
        'kol': kol, 'n': n,
        'veri_tazeligi_dk': veri_tazeligi_dk,
        'yetim_golge_orani': yetim_golge_orani,
        'isaret_eksik_toplam': isaret_eksik_toplam,
        'veri_hata_orani': veri_hata_orani,
        'kirmizi_sayisi': kirmizi_sayisi,
        'sari_sayisi': sari_sayisi,
        'sinyal_gecikme_dk_medyan': sinyal_gecikme_dk_medyan,
    }


def kontrol(olcu: dict, esikler: dict | None = None) -> dict:
    """Saf fonksiyon: ölçüden ışık + neden listesi üretir (kırmızı nedenler sarıdan önce)."""
    e = {**ESIKLER, **(esikler or {})}

    if olcu['n'] == 0:
        return {'isik': 'sari', 'nedenler': ['kol boş']}

    kirmizi: list[str] = []
    sari: list[str] = []

    tazelik = olcu['veri_tazeligi_dk']
    if tazelik is not None and tazelik >= e['veri_tazeligi_kirmizi_dk']:
        kirmizi.append(f"veri {tazelik:.0f} dk önce")
    elif tazelik is not None and tazelik >= e['veri_tazeligi_sari_dk']:
        sari.append(f"veri {tazelik:.0f} dk önce")

    yetim = olcu['yetim_golge_orani']
    if yetim is not None and yetim >= e['yetim_golge_orani_kirmizi']:
        kirmizi.append(f"yetim gölge payı %{yetim * 100:.0f}")

    hata = olcu['veri_hata_orani']
    if hata is not None and hata >= e['veri_hata_orani_kirmizi']:
        kirmizi.append(f"veri hatası payı %{hata * 100:.0f}")
    elif hata is not None and hata >= e['veri_hata_orani_sari']:
        sari.append(f"veri hatası payı %{hata * 100:.0f}")

    if olcu['isaret_eksik_toplam'] >= e['isaret_eksik_toplam_sari']:
        sari.append(f"işaret eksik: {olcu['isaret_eksik_toplam']}")

    isik = 'kirmizi' if kirmizi else 'sari' if sari else 'yesil'
    return {'isik': isik, 'nedenler': kirmizi + sari}
