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
import csv
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
import engine.pine.yorumlayici as yorumlayici
from engine.pine.yorumlayici import Desteklenmiyor, PineHatasi, PineStrateji
from engine.tv_emulator import Sonuc, calistir, gercekci, nedensellik

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "tv2"
OUT = ROOT / "results" / "tv2"
SURUMLER = ROOT / "arastirma" / "tv2_surumler.csv"
ESLESME = ROOT / "arastirma" / "tv2_veri_eslesme.csv"

KRIPTO_BORSALARI = {"BINANCE", "BYBIT", "OKX", "COINBASE", "BITSTAMP", "KUCOIN", "BITGET", "MEXC", "KRAKEN", "BINANCEUS",
                    "BITFINEX", "GATEIO", "PHEMEX", "CRYPTO", "BLACKBULL"}
KRIPTO_TAKMA_ADLARI = {"BTCUSD", "ETHUSD"}  # request.security() içindeki öneksiz sürekli spot takma adları
# Bir borsanın USDT paritesini Binance'e yönlendirmek yalnız aynı sözleşme için
# geçerlidir. NVDAXUSDT Pionex xStock adıdır; Binance'teki NVDAUSDT ayrı bir
# sözleşmedir ve yerine kullanılamaz.
BINANCE_ESLESME_HATALARI = {
    "NVDAXUSDT": "sembol eşlemesi yanlış: NVDAXUSDT için Binance USD-M eşdeğeri yok; NVDAUSDT farklı sözleşmedir",
}
BINANCE_ARALIK = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480,
                  "12h": 720, "1d": 1440, "3d": 4320, "1w": 10080}
YFINANCE = {"SPX": "^GSPC", "SPX500": "^GSPC", "US500": "^GSPC", "SPY": "SPY", "NDX": "^NDX", "NAS100": "^NDX", "US100": "^NDX",
            "QQQ": "QQQ", "DJI": "^DJI", "US30": "^DJI", "XAUUSD": "GC=F", "GOLD": "GC=F", "XAGUSD": "SI=F", "USOIL": "CL=F",
            "WTI": "CL=F", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "DAX": "^GDAXI",
            "DE40": "^GDAXI", "GER40": "^GDAXI", "VIX": "^VIX", "VIX9D": "^VIX9D", "VXN": "^VXN", "TNX": "^TNX",
            "DXY": "DX-Y.NYB", "US10Y": "^TNX", "ES1!": "ES=F", "NQ1!": "NQ=F", "MES1!": "MES=F", "MNQ1!": "MNQ=F", "YM1!": "YM=F", "RTY1!": "RTY=F", "GC1!": "GC=F", "CL1!": "CL=F", "BTC1!": "BTC=F"}
HISSE_BORSALARI = {"NASDAQ", "NYSE", "AMEX", "ARCA", "BATS", "NYSEARCA", "CBOE", "TVC", "CME", "CME_MINI", "COMEX", "NYMEX", ""}
KAPI_HAFTA = 10
NEDENSELLIK_BAR = 15_000
DAKIKALIK_ALT = 15            # bu dakikanın altı yalnız --dakikalik ile ve pencereli koşulur
DAKIKALIK_KOS = False
OKX_ARALIK = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1H", "2h": "2H", "4h": "4H", "6h": "6H", "12h": "12H", "1d": "1D"}
BINANCE_UM_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"


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


def _okx_veri(bsym: str, dk: int) -> tuple[pd.DataFrame | None, str]:
    """Try a public OKX swap candle page when Binance has no symbol."""
    interval = next((v for k, v in OKX_ARALIK.items() if dakika(k) == dk), None)
    if interval is None or not bsym.endswith(("USDT", "USDC")):
        return None, f"veri_yok: OKX aralık/sembol {bsym}"
    quote = "USDC" if bsym.endswith("USDC") else "USDT"
    inst = f"{bsym[:-len(quote)]}-{quote}-SWAP"
    try:
        response = requests.get("https://www.okx.com/api/v5/market/candles",
                                params={"instId": inst, "bar": interval, "limit": 1000}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("data", []) if payload.get("code") == "0" else []
    except (requests.RequestException, ValueError):
        return None, f"veri_yok: OKX {inst}"
    if not rows:
        return None, f"veri_yok: OKX {inst}"
    frame = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume", "volume_ccy", "volume_ccy_quote", "confirm"])
    frame.index = pd.to_datetime(frame.pop("timestamp").astype("int64"), unit="ms", utc=True)
    frame = frame[["open", "high", "low", "close", "volume"]].apply(pd.to_numeric, errors="coerce").dropna()
    return _kapanmis(frame.sort_index(), dk), f"OKX {inst} {interval} (ikinci kaynak)"


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


def veri(sembol: str, tf: str, bas: pd.Timestamp | None = None) -> tuple[pd.DataFrame | None, str]:
    """(OHLC, kaynak notu). Veri yoksa (None, neden). Kapanmamış son bar atılır. `bas`: pencere başlangıcı (dakikalık)."""
    borsa, _, ad = sembol.upper().partition(":")
    if not ad:                                  # önek yok: 'SPY', 'VIX', 'BTCUSDT'
        borsa, ad = "", borsa
    dk = dakika(tf)
    if borsa in KRIPTO_BORSALARI or ad.endswith(("USDT", "USDT.P", "USDC")) or ad in KRIPTO_TAKMA_ADLARI:
        bsym = _binance_sembol(sembol.upper())
        if bsym in BINANCE_ESLESME_HATALARI:
            return None, f"veri_yok: {BINANCE_ESLESME_HATALARI[bsym]}"
        taban = max((v for v in BINANCE_ARALIK.values() if dk % v == 0 and v <= dk), default=None)
        if taban is None:
            return None, f"veri_yok: aralık {tf}"
        aralik = next(k for k, v in BINANCE_ARALIK.items() if v == taban)
        ek = f"_{bas:%Y%m%d}" if bas is not None else ""
        yol = CACHE / f"{bsym}_{aralik}{ek}.parquet"
        kaynak = "Binance"
        if yol.exists() and time.time() - yol.stat().st_mtime < 6 * 3600:
            df = pd.read_parquet(yol)
        else:
            try:
                df = fetch_binance(Asset(bsym, "KRIPTO", "binance"), aralik, start=bas)
            except requests.HTTPError:
                # TradingView'deki bazı USDT perpetual'lar spotta listeli değildir.
                # Aynı sözleşmeyi USDⓈ-M klines'tan dene; sonuç satırı kaynağı taşır.
                try:
                    df = fetch_binance(Asset(bsym, "KRIPTO", "binance"), aralik, start=bas,
                                       url=BINANCE_UM_KLINES_URL)
                    kaynak = "binance_um"
                except requests.HTTPError:
                    alt, alt_note = _okx_veri(bsym, dk)
                    if alt is not None:
                        return alt, alt_note
                    return None, f"veri_yok: Binance spot/UM {bsym} yok"
            if df.empty:
                alt, alt_note = _okx_veri(bsym, dk)
                if alt is not None:
                    return alt, alt_note
                return None, f"veri_yok: Binance {bsym}"
            CACHE.mkdir(parents=True, exist_ok=True)
            df.to_parquet(yol)
        if taban != dk:
            df = _yeniden_ornekle(df, dk)
        return _kapanmis(df, dk), f"{kaynak} {bsym} {aralik}" + ("" if taban == dk else f" → {tf}")
    dis = _eslenmis_veri(sembol, dk)
    if dis is not None:
        return dis
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
    if dk < 1440 and (kok in YFINANCE or (borsa in HISSE_BORSALARI and re.fullmatch(r"[A-Z]{1,5}", kok))):
        return _yfinance_gun_ici(YFINANCE.get(kok, kok), dk)
    return None, "veri_yok: gün içi/yerel piyasa (Dukascopy bekliyor)" if dk < 1440 else f"veri_yok: eşleme yok ({sembol})"


def _esleme(sembol: str) -> dict[str, str] | None:
    """Return the first external-source mapping for a TradingView symbol."""
    if not ESLESME.exists():
        return None
    wanted = sembol.upper()
    with ESLESME.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("yayin_sembolu", "").upper() == wanted:
                return row
    return None


def _eslenmis_veri(sembol: str, dk: int) -> tuple[pd.DataFrame | None, str] | None:
    """Mapped Dukascopy/vnstock data.  Absence of a mapping lets normal fallbacks run."""
    row = _esleme(sembol)
    if row is None or row.get("kaynak") not in {"dukascopy", "vnstock"}:
        return None
    code = row.get("esdeger") or row.get("esdeger_sembol") or row.get("veri_sembolu") or ""
    if row["kaynak"] == "dukascopy":
        from data import dukascopy

        frames = [dukascopy.load_archive(code, year) for year in range(2010, pd.Timestamp.now(tz="UTC").year + 1)]
        frames = [frame for frame in frames if not frame.empty]
        if not frames:
            return None, f"veri_yok: Dukascopy önbelleği {code}"
        frame = pd.concat(frames).sort_index()
        if dk != 1:
            frame = _yeniden_ornekle(frame, dk)
        return _kapanmis(frame, dk), f"Dukascopy {code} (eşleme)"
    try:
        from vnstock import Vnstock  # type: ignore[import-not-found]
        raw = Vnstock().stock(symbol=code, source="VCI").quote.history(start="2010-01-01", end=pd.Timestamp.now().date().isoformat(), interval="1D")
    except (ImportError, AttributeError, ValueError) as exc:
        return None, f"veri_yok: vnstock {code} ({type(exc).__name__})"
    if raw is None or raw.empty:
        return None, f"veri_yok: vnstock {code}"
    raw.columns = [str(column).lower() for column in raw.columns]
    raw.index = pd.to_datetime(raw.index if not isinstance(raw.index, pd.RangeIndex) else raw["time"], utc=True)
    frame = raw[["open", "high", "low", "close", "volume"]].dropna()
    return _kapanmis(frame, dk), f"vnstock {code} (eşleme)"


YF_ARALIK = {1: ("1m", "7d"), 2: ("2m", "60d"), 5: ("5m", "60d"), 15: ("15m", "60d"), 30: ("30m", "60d"),
             60: ("60m", "730d"), 90: ("90m", "60d")}


def _yfinance_gun_ici(kod: str, dk: int) -> tuple[pd.DataFrame | None, str]:
    """yfinance gün içi: geçmiş sınırlı (1m 7 gün, 2-30m 60 gün, 60m 730 gün). Tam bölünen en büyük aralıktan
    birleştirilir; birleştirme UTC hizalı (TradingView seans hizası değil) — `veri` notunda yazılır."""
    import yfinance as yf
    taban = max((k for k in YF_ARALIK if dk % k == 0), default=None)
    if taban is None:
        return None, f"veri_yok: yfinance {dk}dk aralık yok"
    aralik, donem = YF_ARALIK[taban]
    yol = CACHE / f"yf_{re.sub(r'[^A-Za-z0-9]', '_', kod)}_{aralik}.parquet"
    if yol.exists() and time.time() - yol.stat().st_mtime < 6 * 3600:
        df = pd.read_parquet(yol)
    else:
        df = yf.download(kod, period=donem, interval=aralik, auto_adjust=False, progress=False)
        if df.empty:
            return None, f"veri_yok: yfinance {kod} {aralik}"
        df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
        df.index = pd.to_datetime(df.index, utc=True)
        df = df[["open", "high", "low", "close", "volume"]].dropna()
        CACHE.mkdir(parents=True, exist_ok=True)
        df.to_parquet(yol)
    if taban != dk:
        df = _yeniden_ornekle(df, dk)
    return _kapanmis(df, dk), f"yfinance {kod} {aralik} (son {donem})" + ("" if taban == dk else f" → {dk}dk, UTC hizalı")


def _yeniden_ornekle(df: pd.DataFrame, dk: int) -> pd.DataFrame:
    kural = f"{dk}min"
    out = df.resample(kural, origin="epoch", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    return out.dropna(subset=["open"])


def _kapanmis(df: pd.DataFrame, dk: int) -> pd.DataFrame:
    simdi = pd.Timestamp.now(tz="UTC")
    return df[df.index + pd.to_timedelta(int(dk), unit="min") <= simdi]


def _veri_kisa(notu: str) -> bool:
    """yfinance'ın 1-30 dakikalık, en çok 7/60 günlük penceresini yalnız bilgi olarak işaretle."""
    return notu.startswith("yfinance ") and bool(re.search(r"\(son (?:7d|60d)\)", notu))


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


BAGLAYICI = re.compile(r"input\.source\(|type\s*=\s*input\.source")
KUTUPHANELER = ROOT / "arastirma" / "tv2_kutuphaneler.csv"


def kutuphane_kaynak(kullanici: str, ad: str, surum: int) -> str | None:
    """Pine kütüphanesi kaynağı: `arastirma/tv2_kutuphaneler.csv` (yol -> PUB) + pine-facade sürüm; önbellek data/tv2/kutuphane."""
    yol = f"{kullanici}/{ad}"
    if not KUTUPHANELER.exists():
        return None
    tablo = pd.read_csv(KUTUPHANELER, dtype=str)
    satir = tablo[tablo["yol"] == yol]
    if satir.empty:
        return None
    dosya = CACHE / "kutuphane" / f"{kullanici}_{ad}_{surum}.json"
    if not dosya.exists():
        q = urllib.parse.quote(satir.iloc[0]["pub"])
        r = requests.get(f"https://pine-facade.tradingview.com/pine-facade/get/{q}/{surum}?no_4xx=true", timeout=30)
        dosya.parent.mkdir(parents=True, exist_ok=True)
        dosya.write_text(r.text)
    return json.loads(dosya.read_text()).get("source")


yorumlayici.KUTUPHANE_SAGLAYICI = kutuphane_kaynak

FOOTPRINT_TICK = {"BITSTAMP:BTCUSD": 1.0, "BITSTAMP:ETHUSD": 0.1}   # TradingView mintick (varsayım, uyarıda yazılır)


def _footprint_veri(sembol: str, dk: int):
    """request.footprint: Binance aggTrades özeti (backtests.tv2_footprint); `.P` vadeli (um), diğerleri spot."""
    from backtests import tv2_footprint
    bsym = _binance_sembol(sembol)
    piyasa = "um" if sembol.upper().endswith(".P") else "spot"
    okunan = tv2_footprint.oku(bsym, piyasa, dk)
    if okunan is None:
        return None
    barlar, taban = okunan
    return barlar, taban, FOOTPRINT_TICK.get(sembol.upper(), binance_tick(bsym))


yorumlayici.FOOTPRINT_SAGLAYICI = _footprint_veri


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


def _ucretli(sembol: str, tf: str, src: str | None) -> str | None:
    """GOREV_TV2 Ek 3 (kullanıcı kararı): ücretsiz verisi olmayan, yani CME/CBOT/COMEX/NYMEX işlem akışı (footprint).
    Gün içi kısa ücretsiz geçmiş (yfinance) ücretli sayılmaz: eldeki veriyle test edilir, etiketi yetersiz_kanit."""
    if str(sembol).upper().startswith(("CME", "CBOT", "COMEX", "NYMEX")) and src and "request.footprint" in src:
        return "CME işlem akışı (footprint) ücretli"
    return None


def kos(kimlik: str) -> dict:
    modul, kaynak = strateji(kimlik)
    satir: dict = {"id": kimlik, "sembol": kaynak["sembol"], "tf": kaynak["tf"], "url": kaynak["url"],
                   "tur": "pine" if kaynak.get("pine") else "modul"}
    ucret = _ucretli(kaynak["sembol"], kaynak["tf"], pine_kaynak(kimlik, kaynak["pub"]) if kaynak.get("pine") else None)
    if ucret:
        return satir | {"karar": "veri_ucretli", "neden": ucret}
    pencere_bas = None
    if dakika(str(kaynak["tf"])) < DAKIKALIK_ALT:
        if not DAKIKALIK_KOS:
            return satir | {"karar": "ertelendi", "neden": f"dakikalık ({kaynak['tf']}): ayrı, pencereli koşu (--dakikalik)"}
        surum, _ = surum_tarihi(kimlik, kaynak)
        if surum is not None:   # kullanıcı kararı 2026-10-24: sürüm tarihinden 1 yıl önce başlayan pencere
            pencere_bas = surum - pd.Timedelta(days=365)
            satir["pencere_bas"] = pencere_bas.date()
    df, notu = veri(str(kaynak["sembol"]), str(kaynak["tf"]), bas=pencere_bas)
    satir["veri"] = notu
    if _veri_kisa(notu):
        satir["veri_kisa"] = True
    if df is None:
        return satir | {"karar": "veri_yok", "neden": notu}
    satir |= {"bas": df.index[0].date(), "son": df.index[-1].date(), "bar": len(df)}
    kripto = notu.startswith("Binance")
    src = None
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
                r"\b(profit|loss|trail_points|trail_offset)\s*=|syminfo\.mintick", src) else []) + (
                ["footprint: Binance aggTrades (GOREV_TV2 Ek 3), satır mintick'i varsayım"] if "request.footprint" in src else []))
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
    elif satir["yazar_tum_islem"] == 0:
        baglayici = bool(src) and bool(BAGLAYICI.search(src))
        satir |= {"karar": "islem_yok", "neden": "tüm geçmişte 0 işlem" + (
            " (harici gösterge bağlayıcısı: sinyal input.source ile başka göstergeden bekleniyor)" if baglayici else "")}
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
    ap.add_argument("--dakikalik", action="store_true", help="15 dakikanın altını sürüm tarihi - 1 yıl penceresiyle koş")
    args = ap.parse_args(argv)
    global DAKIKALIK_KOS
    DAKIKALIK_KOS = args.dakikalik
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
