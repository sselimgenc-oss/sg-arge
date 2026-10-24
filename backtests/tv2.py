"""TV-2 koşucusu: `strategies/tv2/<id>.py` modüllerini yazarın sembolü ve zaman diliminde koşar (docs/TEST_YAPISI.md Adım 0-2).

İki strateji türü: el çevirisi modül (`strategies/tv2/<id>.py`) ya da Pine kaynağının kendisi (`engine/pine`,
`arastirma/tv2_surumler.csv` satırı; kaynak pine-facade'den çekilip `data/tv2/kaynak/` önbelleğine yazılır).
Her strateji için iki sonuç: yazar (strategy() ayarları) ve uygulanabilir (gerçekçi maliyet). Sınama dönemi, test edilen kod
sürümünün tarihinden (`arastirma/tv2_surumler.csv`) sonrasıdır. Çıktı: `results/tv2/sonuclar.csv` (id başına bir satır,
yeniden koşuda güncellenir) ve `results/tv2/getiriler/<id>.csv` (uygulanabilir sonucun günlük net getirisi).

    python -m backtests.tv2 [id ...]              # id verilmezse bütün modüller
    python -m backtests.tv2 --ayri <id>           # tek strateji, results/tv2/satirlar/<id>.json (toplu koşu: xargs + timeout)
    python -m backtests.tv2 --birlestir           # satirlar/ -> sonuclar.csv
"""

from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import re
import time
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd

import requests

from data.fetch import Asset, fetch_binance
from engine.pine.yorumlayici import Desteklenmiyor, PineHatasi, PineStrateji
from engine.tv_emulator import Sonuc, calistir, gercekci, nedensellik

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "tv2"
OUT = ROOT / "results" / "tv2"
SURUMLER = ROOT / "arastirma" / "tv2_surumler.csv"

KRIPTO_BORSALARI = {"BINANCE", "BYBIT", "OKX", "COINBASE", "BITSTAMP", "KUCOIN", "BITGET", "MEXC", "KRAKEN", "BINANCEUS",
                    "BITFINEX", "GATEIO", "PHEMEX", "CRYPTO", "BLACKBULL"}
BINANCE_ARALIK = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480,
                  "12h": 720, "1d": 1440, "3d": 4320, "1w": 10080}
YFINANCE = {"SPX": "^GSPC", "SPX500": "^GSPC", "US500": "^GSPC", "SPY": "SPY", "NDX": "^NDX", "NAS100": "^NDX", "US100": "^NDX",
            "QQQ": "QQQ", "DJI": "^DJI", "US30": "^DJI", "XAUUSD": "GC=F", "GOLD": "GC=F", "XAGUSD": "SI=F", "USOIL": "CL=F",
            "WTI": "CL=F", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "DAX": "^GDAXI",
            "DE40": "^GDAXI", "GER40": "^GDAXI", "VIX": "^VIX", "VIX9D": "^VIX9D", "VXN": "^VXN", "TNX": "^TNX",
            "DXY": "DX-Y.NYB", "US10Y": "^TNX", "ES1!": "ES=F", "NQ1!": "NQ=F", "GC1!": "GC=F", "CL1!": "CL=F", "BTC1!": "BTC=F"}
HISSE_BORSALARI = {"NASDAQ", "NYSE", "AMEX", "ARCA", "BATS", "NYSEARCA", "CBOE", "TVC", "CME", "CME_MINI", "COMEX", "NYMEX", ""}
KAPI_HAFTA = 10
NEDENSELLIK_BAR = 15_000
DAKIKALIK_ALT = 15            # bu dakikanın altı ilk turda ertelenir


def dakika(tf: str) -> int:
    """TradingView aralığı → dakika ('60', '240', '1D', 'D', '1W', '45', '4H', '3D')."""
    tf = str(tf).strip().upper()
    m = re.fullmatch(r"(\d*)([SDWMH]?)", tf)
    if not m:
        raise ValueError(f"aralık okunamadı: {tf}")
    n, birim = int(m.group(1) or 1), m.group(2)
    return n * {"": 1, "H": 60, "D": 1440, "W": 10080, "M": 43200}.get(birim, 1)


def _binance_sembol(sembol: str) -> str:
    s = sembol.split(":")[-1].replace(".P", "").replace("PERP", "")
    if s.startswith("XBT"):
        s = "BTC" + s[3:]
    return s[:-3] + "USDT" if s.endswith("USD") and not s.endswith("USDT") else s


def binance_tick(bsym: str) -> float:
    """Binance PRICE_FILTER tickSize (önbellekli). Yazarın sembolünün tick'i bilinmediğinde kullanılır."""
    yol = CACHE / "ticksize.json"
    tablo = json.loads(yol.read_text()) if yol.exists() else {}
    if bsym not in tablo:
        r = requests.get("https://data-api.binance.vision/api/v3/exchangeInfo", params={"symbol": bsym}, timeout=30)
        r.raise_for_status()
        filtre = next(f for f in r.json()["symbols"][0]["filters"] if f["filterType"] == "PRICE_FILTER")
        tablo[bsym] = float(filtre["tickSize"])
        CACHE.mkdir(parents=True, exist_ok=True)
        yol.write_text(json.dumps(tablo))
    return tablo[bsym]


def veri(sembol: str, tf: str) -> tuple[pd.DataFrame | None, str]:
    """(OHLC, kaynak notu). Veri yoksa (None, neden). Kapanmamış son bar atılır."""
    borsa, _, ad = sembol.upper().partition(":")
    if not ad:                                  # önek yok: 'SPY', 'VIX', 'BTCUSDT'
        borsa, ad = "", borsa
    dk = dakika(tf)
    if borsa in KRIPTO_BORSALARI or ad.endswith(("USDT", "USDT.P", "USDC")):
        bsym = _binance_sembol(sembol.upper())
        taban = max((v for v in BINANCE_ARALIK.values() if dk % v == 0 and v <= dk), default=None)
        if taban is None:
            return None, f"veri_yok: aralık {tf}"
        aralik = next(k for k, v in BINANCE_ARALIK.items() if v == taban)
        yol = CACHE / f"{bsym}_{aralik}.parquet"
        if yol.exists() and time.time() - yol.stat().st_mtime < 6 * 3600:
            df = pd.read_parquet(yol)
        else:
            try:
                df = fetch_binance(Asset(bsym, "KRIPTO", "binance"), aralik)
            except requests.HTTPError:
                return None, f"veri_yok: Binance {bsym} yok"
            if df.empty:
                return None, f"veri_yok: Binance {bsym}"
            CACHE.mkdir(parents=True, exist_ok=True)
            df.to_parquet(yol)
        if taban != dk:
            df = _yeniden_ornekle(df, dk)
        return _kapanmis(df, dk), f"Binance {bsym} {aralik}" + ("" if taban == dk else f" → {tf}")
    kok = ad.split(".")[0]
    if dk >= 1440 and (kok in YFINANCE or (borsa in HISSE_BORSALARI and re.fullmatch(r"[A-Z]{1,5}", kok))):
        import yfinance as yf
        kod = YFINANCE.get(kok, kok)
        df = yf.download(kod, period="max", interval="1d" if dk < 10080 else "1wk", auto_adjust=False, progress=False)
        if df.empty:
            return None, f"veri_yok: yfinance {kod}"
        df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
        df.index = pd.to_datetime(df.index, utc=True)
        return _kapanmis(df[["open", "high", "low", "close", "volume"]].dropna(), dk), f"yfinance {kod}"
    return None, "veri_yok: gün içi/yerel piyasa (Dukascopy bekliyor)" if dk < 1440 else f"veri_yok: eşleme yok ({sembol})"


def _yeniden_ornekle(df: pd.DataFrame, dk: int) -> pd.DataFrame:
    kural = f"{dk}min"
    out = df.resample(kural, origin="epoch", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    return out.dropna(subset=["open"])


def _kapanmis(df: pd.DataFrame, dk: int) -> pd.DataFrame:
    simdi = pd.Timestamp.now(tz="UTC")
    return df[df.index + pd.to_timedelta(int(dk), unit="min") <= simdi]


def surum_tarihi(kimlik: str, kaynak: dict | None = None) -> tuple[pd.Timestamp | None, str]:
    """Test edilen sürümün tarihi: modülün KAYNAK['surum_tarihi'], yoksa arastirma/tv2_surumler.csv."""
    if kaynak and kaynak.get("surum_tarihi"):
        return pd.Timestamp(kaynak["surum_tarihi"], tz="UTC"), "temiz"
    if not SURUMLER.exists():
        return None, "tarih_belirsiz"
    tablo = pd.read_csv(SURUMLER, dtype=str)
    satir = tablo[tablo["id"] == kimlik]
    if satir.empty or pd.isna(satir.iloc[0].get("son_surum_tarihi")):
        return None, "tarih_belirsiz"
    return pd.Timestamp(satir.iloc[0]["son_surum_tarihi"], tz="UTC"), "temiz"


def _metrik(sonuc: Sonuc, bas: pd.Timestamp | None, on: str) -> dict[str, float]:
    t = sonuc.islemler
    if bas is not None:
        t = t[t["giris_zaman"] >= bas]
    kar, zarar = t.loc[t["net"] > 0, "net"].sum(), -t.loc[t["net"] < 0, "net"].sum()
    eq = sonuc.ozkaynak if bas is None else sonuc.ozkaynak[sonuc.ozkaynak.index >= bas]
    return {
        f"{on}_islem": len(t),
        f"{on}_net_yuzde": float(t["net"].sum() / sonuc.ayarlar.initial_capital * 100),
        f"{on}_pf": float(kar / zarar) if zarar > 0 else (np.inf if kar > 0 else np.nan),
        f"{on}_mdd": float((1 - eq / eq.cummax()).max()) if len(eq) else np.nan,
        f"{on}_hafta": int(t["giris_zaman"].dt.tz_convert(None).dt.to_period("W").nunique()) if len(t) else 0,
    }


def _dis_veri(sembol: str, dk: int) -> pd.DataFrame | None:
    """request.security başka sembol: aynı veri kuralları (Binance / yfinance günlük+); bulunamazsa None."""
    try:
        return veri(sembol, str(dk))[0]
    except Exception:                                   # dış veri hatası: yorumlayıcı 'veri yok' diye işaretler
        return None


def pine_kaynak(kimlik: str, pub: str) -> str | None:
    """Pine kaynağı (pine-facade, son sürüm), `data/tv2/kaynak/<id>.json` önbelleğinde."""
    yol = CACHE / "kaynak" / f"{kimlik}.json"
    if not yol.exists():
        q = urllib.parse.quote(pub)
        r = requests.get(f"https://pine-facade.tradingview.com/pine-facade/get/{q}/last?no_4xx=true", timeout=30)
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(r.text)
    return json.loads(yol.read_text()).get("source")


def strateji(kimlik: str):
    """(modül, KAYNAK sözlüğü): el çevirisi varsa o, yoksa tv2_surumler.csv satırından Pine yorumlayıcısı."""
    if (ROOT / "strategies" / "tv2" / f"{kimlik}.py").exists():
        modul = importlib.import_module(f"strategies.tv2.{kimlik}")
        return modul, modul.KAYNAK
    tablo = pd.read_csv(SURUMLER, dtype=str)
    eslesen = tablo[tablo["id"] == kimlik]
    if eslesen.empty:
        raise KeyError(f"{kimlik}: ne strategies/tv2 modülü ne arastirma/tv2_surumler.csv satırı var")
    satir = eslesen.iloc[0]
    kaynak = {"url": f"https://www.tradingview.com/script/{kimlik}/", "pub": satir["pub"], "sembol": satir["yayin_sembolu"],
              "tf": satir["tf"], "surum_tarihi": satir["son_surum_tarihi"], "pine": True}
    return None, kaynak


def kos(kimlik: str) -> dict:
    modul, kaynak = strateji(kimlik)
    satir: dict = {"id": kimlik, "sembol": kaynak["sembol"], "tf": kaynak["tf"], "url": kaynak["url"],
                   "tur": "pine" if kaynak.get("pine") else "modul"}
    if dakika(str(kaynak["tf"])) < DAKIKALIK_ALT:
        return satir | {"karar": "ertelendi", "neden": f"dakikalık ({kaynak['tf']}): ayrı, pencereli koşu (veri milyonlarca bar)"}
    df, notu = veri(str(kaynak["sembol"]), str(kaynak["tf"]))
    satir["veri"] = notu
    if df is None:
        return satir | {"karar": "veri_yok", "neden": notu}
    satir |= {"bas": df.index[0].date(), "son": df.index[-1].date(), "bar": len(df)}
    kripto = notu.startswith("Binance")
    try:
        if modul is None:
            src = pine_kaynak(kimlik, kaynak["pub"])
            if not src:
                return satir | {"karar": "kaynak_yok", "neden": "pine-facade kaynak vermedi"}
            tick = binance_tick(notu.split()[1]) if kripto else 0.01
            modul = PineStrateji(src, sembol=str(kaynak["sembol"]), tf=str(kaynak["tf"]), tz="UTC" if kripto else "America/New_York",
                                 mintick=tick, kimlik=kimlik)
            modul.veri_saglayici = _dis_veri
            satir["uyari"] = "; ".join(modul.uyarilar + ([f"mintick veri kaynağından ({tick})"] if re.search(
                r"\b(profit|loss|trail_points|trail_offset)\s*=|syminfo\.mintick", src) else []))
        yazar = calistir(modul, df)
        # nedensellik: geleceği gören kod kısa pencerede de aynı biçimde yakalanır; uzun geçmişte (1H ~80 bin bar) 6 kesim pahalı
        pencere = df.iloc[-NEDENSELLIK_BAR:]
        hatalar = nedensellik(modul, pencere, tam=yazar if len(pencere) == len(df) else None)
        uyg = calistir(modul, df, **gercekci(modul.AYARLAR, kripto=kripto))
    except Desteklenmiyor as e:
        return satir | {"karar": "desteklenmiyor", "neden": str(e)}
    except PineHatasi as e:
        return satir | {"karar": "pine_hatasi", "neden": str(e)}
    bas, etiket = surum_tarihi(kimlik, kaynak)
    if bas is not None and (df.index[-1] - bas).days < 365:
        etiket = "yetersiz_kanit"
    satir |= {"surum_tarihi": bas.date() if bas is not None else None, "etiket": etiket}
    satir |= _metrik(yazar, None, "yazar_tum") | _metrik(uyg, None, "uyg_tum")
    if bas is not None:
        satir |= _metrik(yazar, bas, "yazar_sinama") | _metrik(uyg, bas, "uyg_sinama")
        alt = df[df.index >= bas]
        satir["altut_sinama_yuzde"] = float((alt["close"].iloc[-1] / alt["open"].iloc[0] - 1) * 100) if len(alt) else np.nan
    OUT.joinpath("getiriler").mkdir(parents=True, exist_ok=True)
    uyg.ozkaynak.resample("1D").last().dropna().pct_change().dropna().rename("getiri").to_csv(OUT / "getiriler" / f"{kimlik}.csv")
    if hatalar:
        satir |= {"karar": "uygulanamaz", "neden": "nedensellik: " + hatalar[0]}
    elif bas is None:
        satir |= {"karar": "izle", "neden": "sürüm tarihi yok: sınama dönemi belirlenemedi"}
    elif etiket == "yetersiz_kanit":
        satir |= {"karar": "izle", "neden": "sürüm sonrası 1 yıldan az veri"}
    elif satir["uyg_sinama_hafta"] < KAPI_HAFTA:
        satir |= {"karar": "izle", "neden": f"sınamada {satir['uyg_sinama_hafta']} işlem haftası (< {KAPI_HAFTA})"}
    elif satir["uyg_sinama_net_yuzde"] > 0:
        satir |= {"karar": "gecti", "neden": ""}
    else:
        satir |= {"karar": "kaldi", "neden": "uygulanabilir sınama net <= 0"}
    return satir


def tum_moduller() -> list[str]:
    import strategies.tv2 as paket
    return sorted(m.name for m in pkgutil.iter_modules(paket.__path__) if not m.name.startswith("_"))


def _yaz(satirlar: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    yol = OUT / "sonuclar.csv"
    yeni = pd.DataFrame(satirlar)
    if yol.exists():
        eski = pd.read_csv(yol)
        yeni = pd.concat([eski[~eski["id"].isin(yeni["id"])], yeni], ignore_index=True)
    yeni.sort_values("id").to_csv(yol, index=False)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("idler", nargs="*")
    ap.add_argument("--ayri", action="store_true", help="her id için results/tv2/satirlar/<id>.json yaz")
    ap.add_argument("--birlestir", action="store_true", help="satirlar/ klasörünü sonuclar.csv'ye ekle")
    args = ap.parse_args(argv)
    klasor = OUT / "satirlar"
    if args.birlestir:
        _yaz([json.loads(p.read_text()) for p in sorted(klasor.glob("*.json"))])
        return
    if args.ayri:
        klasor.mkdir(parents=True, exist_ok=True)
        for k in args.idler:
            yol = klasor / f"{k}.json"
            yol.write_text(json.dumps({"id": k, "karar": "zaman_asimi", "neden": "koşu süre sınırında kesildi"}))
            try:
                satir = kos(k)
            except Exception as e:                               # beklenmeyen hata: nedeniyle kayda geçer
                satir = {"id": k, "karar": "hata", "neden": f"{type(e).__name__}: {e}"[:300]}
            yol.write_text(json.dumps(satir, default=str, ensure_ascii=False))
        return
    satirlar = [kos(k) for k in (args.idler or tum_moduller())]
    _yaz(satirlar)
    print(pd.DataFrame(satirlar)[["id", "veri", "etiket", "karar", "neden"]].to_string(index=False))


if __name__ == "__main__":
    main()
