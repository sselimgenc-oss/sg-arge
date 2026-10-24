"""TV-2: TradingView strateji test aracı (broker emulator) taklidi, long + short (docs/TEST_YAPISI.md, docs/GOREV_TV2.md).

Bir TV-2 modülü (`strategies/tv2/<id>.py`) Pine kodunu bar bar emirlere çevirir:

    AYARLAR = Ayarlar(initial_capital=10_000, default_qty_type="percent_of_equity", default_qty_value=10, ...)
    def hazirla(df) -> dict: ...            # nedensel, vektörel göstergeler (bar i yalnız <= i'yi kullanır)
    def bar(ctx, i, v) -> None: ...         # bar i KAPANIŞINDA Pine gövdesi: ctx.entry / exit / close / cancel

Dolum semantiği (TradingView varsayılanı, `process_orders_on_close=False`):
- Bar i kapanışında verilen emir bar i+1'de işlenir. Piyasa emri açılışta dolar.
- Bar içi fiyat yolu: yüksek açılışa düşükten yakınsa açılış → yüksek → düşük → kapanış, değilse açılış → düşük → yüksek → kapanış.
  Stop/limit emirleri bu yol boyunca ilk dokundukları noktada dolar; açılış seviyenin ötesindeyse (boşluk) açılıştan.
- Giriş bar içinde dolarsa ona bağlı `exit` emirleri aynı yolun kalanında etkindir.
- Kayma (tick) piyasa ve stop dolumlarına aleyhte eklenir, limit dolumlarına eklenmez. Komisyon her dolumda.
- `entry` karşı pozisyonu kapatıp ters çevirir; aynı yönde `pyramiding` (en az 1) sınırı dolum anında uygulanır.
- Bekleyen emirler iptal edilene, dolana ya da aynı kimlikle yeniden verilene kadar kalır.
Varsayımlar (belgelenmiş): adet emir verilirken hesaplanır (piyasa emrinde sinyal kapanışı, stop/limitte seviye);
`qty_percent` girişin dolum adedine göre; marj/kaldıraç sınırı yok; kapanışlar FIFO.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Callable

import numpy as np
import pandas as pd

LONG, SHORT = 1, -1


@dataclass(frozen=True)
class Ayarlar:
    """Pine `strategy()` argümanları (adlar Pine'daki gibi)."""
    initial_capital: float = 1_000_000.0
    default_qty_type: str = "fixed"            # fixed | cash | percent_of_equity
    default_qty_value: float = 1.0
    commission_type: str = "percent"           # percent | cash_per_contract | cash_per_order
    commission_value: float = 0.0
    slippage: int = 0                          # tick
    pyramiding: int = 1
    process_orders_on_close: bool = False
    mintick: float = 0.01


@dataclass
class _Emir:
    kimlik: str
    tur: str                                   # giris | cikis | kapat
    yon: int = 0                               # giris: LONG/SHORT
    adet: float | None = None
    stop: float | None = None
    limit: float | None = None
    from_entry: str | None = None
    qty_percent: float | None = None
    profit: float | None = None                # tick
    loss: float | None = None                  # tick
    trail_price: float | None = None
    trail_points: float | None = None          # tick
    trail_offset: float | None = None          # tick
    yorum: str = ""
    verildi: int = 0
    # izleyen stop durumu
    bagli: bool = False                        # çıkış emri bir kez açık işleme bağlandı mı
    iz_aktif: bool = False
    iz_uc: float = float("nan")

    @property
    def piyasa(self) -> bool:
        return self.stop is None and self.limit is None


@dataclass
class _Islem:
    entry_id: str
    yon: int
    adet: float
    ilk_adet: float
    fiyat: float
    bar: int
    komisyon: float
    dolan_cikislar: set = field(default_factory=set)   # Pine: aynı exit kimliği aynı giriş için bir kez dolar


@dataclass
class Sonuc:
    islemler: pd.DataFrame
    ozkaynak: pd.Series
    emir_kaydi: list[tuple]
    ayarlar: Ayarlar

    def ozet(self) -> dict[str, float]:
        t = self.islemler
        kar = t.loc[t["net"] > 0, "net"].sum() if len(t) else 0.0
        zarar = -t.loc[t["net"] < 0, "net"].sum() if len(t) else 0.0
        eq = self.ozkaynak
        mdd = float((1 - eq / eq.cummax()).max()) if len(eq) else 0.0
        return {
            "islem": float(len(t)),
            "net": float(t["net"].sum()) if len(t) else 0.0,
            "net_yuzde": float(t["net"].sum() / self.ayarlar.initial_capital * 100) if len(t) else 0.0,
            "pf": float(kar / zarar) if zarar > 0 else (float("inf") if kar > 0 else float("nan")),
            "kazanma": float((t["net"] > 0).mean()) if len(t) else float("nan"),
            "mdd": mdd,
        }


class Baglam:
    """Pine `strategy.*` arayüzü; yalnız bar i'ye kadar bilinenleri gösterir."""

    def __init__(self, df: pd.DataFrame, ayarlar: Ayarlar) -> None:
        self.df = df
        self.a = ayarlar
        self.o, self.h, self.l, self.c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        self.i = -1
        self.acik: list[_Islem] = []
        self.kapali: list[dict] = []
        self.bekleyen: dict[str, _Emir] = {}
        self.gerceklesen = 0.0
        self.emir_kaydi: list[tuple] = []

    # ---- durum (Pine strategy.*) ----
    @property
    def position_size(self) -> float:
        return float(sum(t.yon * t.adet for t in self.acik))

    @property
    def position_avg_price(self) -> float:
        q = sum(t.adet for t in self.acik)
        return float(sum(t.fiyat * t.adet for t in self.acik) / q) if q > 0 else float("nan")

    @property
    def openprofit(self) -> float:
        return self._acik_kz(self.c[self.i]) if self.i >= 0 else 0.0

    @property
    def netprofit(self) -> float:
        return self.gerceklesen

    @property
    def equity(self) -> float:
        return self.a.initial_capital + self.gerceklesen + self.openprofit

    @property
    def opentrades(self) -> int:
        return len(self.acik)

    @property
    def closedtrades(self) -> int:
        return len(self.kapali)

    def _acik_kz(self, fiyat: float) -> float:
        return float(sum(t.yon * (fiyat - t.fiyat) * t.adet for t in self.acik))

    # ---- emirler (Pine strategy.*) ----
    def entry(self, kimlik: str, yon: int, qty: float | None = None, limit: float | None = None,
              stop: float | None = None, comment: str = "") -> None:
        self._ver(_Emir(kimlik, "giris", yon=yon, adet=qty, stop=_na(stop), limit=_na(limit), yorum=comment))

    def exit(self, kimlik: str, from_entry: str | None = None, qty: float | None = None, qty_percent: float | None = None,
             profit: float | None = None, limit: float | None = None, loss: float | None = None, stop: float | None = None,
             trail_price: float | None = None, trail_points: float | None = None, trail_offset: float | None = None,
             comment: str = "") -> None:
        emir = _Emir(kimlik, "cikis", adet=qty, stop=_na(stop), limit=_na(limit), from_entry=from_entry or None,
                     qty_percent=qty_percent, profit=_na(profit), loss=_na(loss), trail_price=_na(trail_price),
                     trail_points=_na(trail_points), trail_offset=_na(trail_offset), yorum=comment)
        if all(x is None for x in (emir.stop, emir.limit, emir.profit, emir.loss, emir.trail_price, emir.trail_points)):
            return  # Pine: fiyat parametresi olmayan exit hiçbir şey yapmaz
        eski = self.bekleyen.get("X:" + kimlik)
        if eski is not None:                           # yeniden verilen exit: bağ ve izleyen stop durumu korunur
            emir.bagli, emir.iz_aktif, emir.iz_uc = eski.bagli, eski.iz_aktif, eski.iz_uc
        self._ver(emir, anahtar="X:" + kimlik)

    def close(self, kimlik: str, comment: str = "", qty: float | None = None, qty_percent: float | None = None) -> None:
        if any(t.entry_id == kimlik for t in self.acik):
            self._ver(_Emir(kimlik, "kapat", from_entry=kimlik, adet=qty, qty_percent=qty_percent, yorum=comment),
                      anahtar="C:" + kimlik)

    def close_all(self, comment: str = "") -> None:
        if self.acik:
            self._ver(_Emir("__hepsi__", "kapat", yorum=comment), anahtar="C:__hepsi__")

    def cancel(self, kimlik: str) -> None:
        for anahtar in (kimlik, "X:" + kimlik):
            self.bekleyen.pop(anahtar, None)

    def cancel_all(self) -> None:
        self.bekleyen.clear()

    def _ver(self, emir: _Emir, anahtar: str | None = None) -> None:
        emir.verildi = self.i
        if emir.tur == "giris" and emir.adet is None:
            ref = emir.stop if emir.stop is not None else emir.limit if emir.limit is not None else self.c[self.i]
            emir.adet = self._varsayilan_adet(ref)
        self.bekleyen[anahtar or emir.kimlik] = emir
        self.emir_kaydi.append((self.i, anahtar or emir.kimlik, emir.tur, emir.yon, _yuvarla(emir.adet), _yuvarla(emir.stop),
                                _yuvarla(emir.limit), emir.from_entry, emir.qty_percent, emir.profit, emir.loss,
                                emir.trail_points, emir.trail_offset, _yuvarla(emir.trail_price)))
        if self.a.process_orders_on_close and emir.piyasa and emir.tur != "cikis":
            self._isle_piyasa(self.c[self.i], self.i, sadece=anahtar or emir.kimlik)

    def _varsayilan_adet(self, fiyat: float) -> float:
        tip, deger = self.a.default_qty_type, self.a.default_qty_value
        if tip == "fixed":
            return float(deger)
        if tip == "cash":
            return float(deger) / fiyat
        if tip == "percent_of_equity":
            return self.equity * float(deger) / 100.0 / fiyat
        raise ValueError(f"default_qty_type bilinmiyor: {tip}")

    # ---- dolum ----
    def _komisyon(self, fiyat: float, adet: float) -> float:
        t, v = self.a.commission_type, self.a.commission_value
        if t == "percent":
            return abs(fiyat * adet) * v / 100.0
        if t == "cash_per_contract":
            return abs(adet) * v
        if t == "cash_per_order":
            return float(v)
        raise ValueError(f"commission_type bilinmiyor: {t}")

    def _kayma(self, fiyat: float, yon: int) -> float:
        return fiyat + yon * self.a.slippage * self.a.mintick

    def _ac(self, emir: _Emir, fiyat: float, bar: int, kaymali: bool) -> None:
        yon = emir.yon
        if self.acik and self.acik[0].yon == -yon:   # ters çevirme: önce karşı pozisyon kapanır
            dolum = self._kayma(fiyat, yon) if kaymali else fiyat
            self._kapat(list(self.acik), None, dolum, bar, emir.kimlik)
        if sum(1 for t in self.acik if t.yon == yon) >= max(1, self.a.pyramiding):
            return
        dolum = self._kayma(fiyat, yon) if kaymali else fiyat
        adet = float(emir.adet or 0.0)
        if adet <= 0:
            return
        self.acik.append(_Islem(emir.kimlik, yon, adet, adet, dolum, bar, self._komisyon(dolum, adet)))

    def _kapat(self, hedef: list[_Islem], adet: float | None, fiyat: float, bar: int, exit_id: str) -> None:
        kalan = sum(t.adet for t in hedef) if adet is None else adet
        for t in hedef:                                # FIFO
            if kalan <= 1e-12:
                break
            q = min(t.adet, kalan)
            pay = q / t.adet
            giris_kom = t.komisyon * pay
            cikis_kom = self._komisyon(fiyat, q)
            brut = t.yon * (fiyat - t.fiyat) * q
            net = brut - giris_kom - cikis_kom
            self.gerceklesen += net
            self.kapali.append({"entry_id": t.entry_id, "exit_id": exit_id, "yon": t.yon, "adet": q,
                                "giris_bar": t.bar, "giris_zaman": self.df.index[t.bar], "giris_fiyat": t.fiyat,
                                "cikis_bar": bar, "cikis_zaman": self.df.index[bar], "cikis_fiyat": fiyat,
                                "brut": brut, "komisyon": giris_kom + cikis_kom, "net": net})
            t.adet -= q
            t.komisyon -= giris_kom
            kalan -= q
        self.acik = [t for t in self.acik if t.adet > 1e-12]

    def _cikis_hedefi(self, emir: _Emir) -> list[_Islem]:
        hedef = [t for t in self.acik if not emir.from_entry or t.entry_id == emir.from_entry]
        if emir.tur == "cikis":
            hedef = [t for t in hedef if emir.kimlik not in t.dolan_cikislar]
        return hedef

    def _cikis_adedi(self, emir: _Emir, hedef: list[_Islem]) -> float:
        acik = sum(t.adet for t in hedef)
        if emir.adet is not None:
            return min(float(emir.adet), acik)
        if emir.qty_percent is not None:
            return min(sum(t.ilk_adet for t in hedef) * float(emir.qty_percent) / 100.0, acik)
        return acik

    def _seviyeler(self, emir: _Emir) -> list[tuple[str, int, float]]:
        """Bir emrin (ad, işlem yönü +1 alış/-1 satış, seviye) tetik listesi; tür ad: stop/limit."""
        if emir.tur == "giris":
            out = []
            if emir.stop is not None:
                out.append(("stop", emir.yon, emir.stop))
            if emir.limit is not None:
                out.append(("limit", emir.yon, emir.limit))
            return out
        hedef = self._cikis_hedefi(emir)
        if not hedef:
            return []
        yon = hedef[0].yon
        ort = sum(t.fiyat * t.adet for t in hedef) / sum(t.adet for t in hedef)
        tick = self.a.mintick
        out = []
        limit = emir.limit if emir.limit is not None else (ort + yon * emir.profit * tick if emir.profit is not None else None)
        stop = emir.stop if emir.stop is not None else (ort - yon * emir.loss * tick if emir.loss is not None else None)
        if limit is not None:
            out.append(("limit", -yon, limit))
        if stop is not None:
            out.append(("stop", -yon, stop))
        if emir.iz_aktif and emir.trail_offset is not None:
            out.append(("stop", -yon, emir.iz_uc - yon * emir.trail_offset * tick))
        return out

    def _iz_aktivasyon(self, emir: _Emir) -> float | None:
        if emir.tur != "cikis" or emir.trail_offset is None or emir.iz_aktif:
            return None
        hedef = self._cikis_hedefi(emir)
        if not hedef:
            return None
        yon = hedef[0].yon
        if emir.trail_price is not None:
            return emir.trail_price
        if emir.trail_points is not None:
            ort = sum(t.fiyat * t.adet for t in hedef) / sum(t.adet for t in hedef)
            return ort + yon * emir.trail_points * self.a.mintick
        return None

    def _doldur(self, anahtar: str, emir: _Emir, tur: str, fiyat: float, bar: int) -> None:
        del self.bekleyen[anahtar]
        kaymali = tur != "limit"
        if emir.tur == "giris":
            self._ac(emir, fiyat, bar, kaymali)
            return
        hedef = self._cikis_hedefi(emir)
        if not hedef:
            return
        dolum = self._kayma(fiyat, -hedef[0].yon) if kaymali else fiyat
        for t in hedef:
            t.dolan_cikislar.add(emir.kimlik)
        self._kapat(hedef, self._cikis_adedi(emir, hedef), dolum, bar, emir.kimlik)

    def _temizle(self) -> None:
        """Bağlandığı işlemler kapanan çıkış emri düşer (Pine: girişi kapanan exit iptal olur)."""
        for anahtar, emir in list(self.bekleyen.items()):
            if emir.tur != "cikis":
                continue
            if self._cikis_hedefi(emir):
                emir.bagli = True
            elif emir.bagli:
                del self.bekleyen[anahtar]

    def _isle_piyasa(self, fiyat: float, bar: int, sadece: str | None = None) -> None:
        for anahtar, emir in list(self.bekleyen.items()):
            if sadece is not None and anahtar != sadece:
                continue
            if emir.tur == "kapat":
                del self.bekleyen[anahtar]
                hedef = self._cikis_hedefi(emir)
                if hedef:
                    adet = None if emir.adet is None and emir.qty_percent is None else self._cikis_adedi(emir, hedef)
                    self._kapat(hedef, adet, self._kayma(fiyat, -hedef[0].yon), bar, emir.kimlik if emir.kimlik != "__hepsi__" else "close_all")
            elif emir.tur == "giris" and emir.piyasa:
                del self.bekleyen[anahtar]
                self._ac(emir, fiyat, bar, kaymali=True)

    def _bar_isle(self, j: int) -> None:
        o, h, l, c = self.o[j], self.h[j], self.l[j], self.c[j]
        self._isle_piyasa(o, j)
        self._temizle()
        yol = [o, h, l, c] if abs(h - o) < abs(o - l) else [o, l, h, c]
        self._yol(o, o, j)                             # açılışta zaten geçilmiş seviyeler (boşluk)
        for a, b in zip(yol[:-1], yol[1:]):
            self._yol(a, b, j)

    def _yol(self, a: float, b: float, j: int) -> None:
        cur = a
        for _ in range(100):
            aday = None
            for anahtar, emir in self.bekleyen.items():
                if emir.tur == "kapat" or emir.verildi >= j:
                    continue
                for tur, isyon, seviye in self._seviyeler(emir):
                    p = _tetik(tur, isyon, seviye, cur, b)
                    if p is None:
                        continue
                    mesafe = abs(p - cur)
                    sira = (mesafe, 0 if emir.tur == "cikis" else 1)
                    if aday is None or sira < aday[0]:
                        aday = (sira, anahtar, emir, tur, p)
                aktiv = self._iz_aktivasyon(emir)
                if aktiv is not None:
                    yon = self._cikis_hedefi(emir)[0].yon
                    p = _tetik("limit", -yon, aktiv, cur, b)
                    if p is not None:
                        sira = (abs(p - cur), -1)
                        if aday is None or sira < aday[0]:
                            aday = (sira, anahtar, emir, "aktivasyon", p)
            if aday is None:
                break
            _, anahtar, emir, tur, p = aday
            if tur == "aktivasyon":
                emir.iz_aktif, emir.iz_uc = True, p
            else:
                self._doldur(anahtar, emir, tur, p, j)
                self._temizle()
            cur = p
        # izleyen stop uç noktası segment sonunda güncellenir
        for emir in self.bekleyen.values():
            if emir.tur == "cikis" and emir.iz_aktif:
                hedef = self._cikis_hedefi(emir)
                if hedef:
                    emir.iz_uc = max(emir.iz_uc, b) if hedef[0].yon == LONG else min(emir.iz_uc, b)


def _na(x: Any) -> float | None:
    if x is None:
        return None
    x = float(x)
    return None if np.isnan(x) else x


def _yuvarla(x: Any) -> Any:
    return None if x is None else round(float(x), 10)


def _tetik(tur: str, isyon: int, seviye: float, a: float, b: float) -> float | None:
    """a'dan b'ye giden fiyat parçasında emir dokunuyorsa dolum fiyatı (a = b: açılış/boşluk kontrolü)."""
    alis_stop = (tur == "stop" and isyon == LONG) or (tur == "limit" and isyon == SHORT)   # yukarıdan tetiklenir
    if alis_stop:
        if a >= seviye:
            return a
        return seviye if b >= seviye else None
    if a <= seviye:
        return a
    return seviye if b <= seviye else None


def calistir(modul: Any, df: pd.DataFrame, ayarlar: Ayarlar | None = None, **degisiklik: Any) -> Sonuc:
    """Modülü `df` üzerinde koşar. `degisiklik`: yazar ayarlarının üstüne yazılanlar (ör. gerçekçi maliyet)."""
    a = ayarlar or modul.AYARLAR
    if degisiklik:
        a = replace(a, **degisiklik)
    df = df[["open", "high", "low", "close"] + (["volume"] if "volume" in df else [])].astype(float)
    v = modul.hazirla(df)
    ctx = Baglam(df, a)
    eq = np.empty(len(df))
    for i in range(len(df)):
        if i > 0:
            ctx._temizle()
            ctx._bar_isle(i)
            ctx._temizle()
        ctx.i = i
        modul.bar(ctx, i, v)
        eq[i] = ctx.equity
    islemler = pd.DataFrame(ctx.kapali, columns=["entry_id", "exit_id", "yon", "adet", "giris_bar", "giris_zaman", "giris_fiyat",
                                                  "cikis_bar", "cikis_zaman", "cikis_fiyat", "brut", "komisyon", "net"])
    return Sonuc(islemler, pd.Series(eq, index=df.index, name="ozkaynak"), ctx.emir_kaydi, a)


def gercekci(ayarlar: Ayarlar, kripto: bool) -> dict[str, Any]:
    """TEST_YAPISI Adım 0, uygulanabilir sonuç maliyeti: kripto %0,1/taraf, diğerleri %0,05/taraf + 1 tick."""
    return {"commission_type": "percent", "commission_value": 0.1 if kripto else 0.05,
            "slippage": max(ayarlar.slippage, 0 if kripto else 1)}


def nedensellik(modul: Any, df: pd.DataFrame, kesimler: tuple[float, ...] = (.3, .42, .54, .66, .78, .9)) -> list[str]:
    """Adım 0: veriyi kesince kesimden önceki emirler değişiyorsa modül geleceği görüyordur. Boş liste = temiz.

    Kesimler yüksek zaman dilimi barlarının (gün, hafta) ortasına düşsün diye küçük asal kaydırmalarla seçilir:
    sınırda kesilen veri, bir sonraki barı gören koda (lookahead) sızıntıyı göstermez.
    """
    tam = calistir(modul, df).emir_kaydi
    hatalar = []
    for sira, oran in enumerate(kesimler):
        k = min(int(len(df) * oran) + (7, 13, 19, 23, 29, 31)[sira % 6], len(df) - 1)
        kisa = calistir(modul, df.iloc[:k]).emir_kaydi
        once = [e for e in tam if e[0] < k]
        kisa_once = [e for e in kisa if e[0] < k]
        if once != kisa_once:
            fark = next((x, y) for x, y in zip(once + [None], kisa_once + [None]) if x != y)
            hatalar.append(f"kesim {k}: emir farkı {fark}")
    return hatalar
