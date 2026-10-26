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
    point_value: float = 1.0                 # vadeli kontratta puan başına parasal değer (MNQ: 2 USD)
    close_entries_rule: str = "FIFO"           # FIFO: çıkış miktarı hedef girişten, uygulama en eski işlemden (Pine varsayılanı)
    calc_on_order_fills: bool = False          # dolum sonrası bar içi ek yürütme (modül `ara(ctx, i)` sağlar)


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
    oca: str | None = None                     # oca_type=cancel grubu: biri dolunca diğerleri iptal
    verildi: int = 0
    # izleyen stop durumu
    bagli: bool = False                        # çıkış emri bir kez açık işleme bağlandı mı
    son: tuple | None = None                   # FIFO: hedefin son bilinen (yön, ort. fiyat, adet)
    hedef_nesneleri: list = field(default_factory=list)
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
    kendi_cikisi: bool = False                 # kendi exit/close emriyle (yabancı FIFO kapanışı değil) azaldı mı
    yorum: str = ""                            # giriş emrinin comment'i (işlem listesinde entry_comment)


@dataclass
class Sonuc:
    islemler: pd.DataFrame
    ozkaynak: pd.Series
    emir_kaydi: list[tuple]
    ayarlar: Ayarlar
    # Paper katmanı, emülatörün zaten ürettiği gerçek dolumları ve son
    # durumunu kaydeder. Bunlar hesaplama yolunu değiştirmez; TV-2 sonucu
    # geriye dönük uyumlu kalır.
    dolumlar: list[dict] = field(default_factory=list)
    acik_islemler: list[dict] = field(default_factory=list)
    bekleyen_emirler: list[dict] = field(default_factory=list)

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
        self.dolumlar: list[dict] = []
        self.ara = False                               # bar içi ek yürütmede verilen emir aynı barda dolabilir
        self.dolum_sayisi = 0                          # gerçekleşen emir sayısı (strategy.risk.max_intraday_filled_orders)

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
        return float(sum(t.yon * (fiyat - t.fiyat) * t.adet * self.a.point_value for t in self.acik))

    # ---- emirler (Pine strategy.*) ----
    def entry(self, kimlik: str, yon: int, qty: float | None = None, limit: float | None = None,
              stop: float | None = None, comment: str = "", oca: str | None = None) -> None:
        self._ver(_Emir(kimlik, "giris", yon=yon, adet=qty, stop=_na(stop), limit=_na(limit), yorum=comment, oca=oca))

    def order(self, kimlik: str, yon: int, qty: float | None = None, limit: float | None = None,
              stop: float | None = None, comment: str = "", oca: str | None = None) -> None:
        """Pine strategy.order: ham emir; karşı pozisyonu adedi kadar azaltır, kalan yeni yönde açılır, pyramiding yok."""
        self._ver(_Emir(kimlik, "emir", yon=yon, adet=qty, stop=_na(stop), limit=_na(limit), yorum=comment, oca=oca))

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
            if eski.from_entry == emir.from_entry:
                emir.son, emir.hedef_nesneleri = eski.son, eski.hedef_nesneleri
        self._ver(emir, anahtar="X:" + kimlik)

    def close(self, kimlik: str, comment: str = "", qty: float | None = None, qty_percent: float | None = None,
              immediately: bool = False) -> None:
        if any(t.entry_id == kimlik for t in self.acik):
            self._ver(_Emir(kimlik, "kapat", from_entry=kimlik, adet=qty, qty_percent=qty_percent, yorum=comment),
                      anahtar="C:" + kimlik)
            if immediately:                            # Pine: aynı bar kapanış fiyatından
                self._isle_piyasa(self.c[self.i], self.i, sadece="C:" + kimlik)

    def close_all(self, comment: str = "", immediately: bool = False) -> None:
        if self.acik:
            self._ver(_Emir("__hepsi__", "kapat", yorum=comment), anahtar="C:__hepsi__")
            if immediately:
                self._isle_piyasa(self.c[self.i], self.i, sadece="C:__hepsi__")

    def cancel(self, kimlik: str) -> None:
        for anahtar in (kimlik, "X:" + kimlik):
            self.bekleyen.pop(anahtar, None)

    def cancel_all(self) -> None:
        self.bekleyen.clear()

    def _ver(self, emir: _Emir, anahtar: str | None = None) -> None:
        emir.verildi = self.i - 1 if self.ara else self.i
        if emir.tur in ("giris", "emir") and emir.adet is None:
            ref = emir.stop if emir.stop is not None else emir.limit if emir.limit is not None else self.c[self.i]
            emir.adet = self._varsayilan_adet(ref)
        self.bekleyen[anahtar or emir.kimlik] = emir
        self.emir_kaydi.append((self.i, anahtar or emir.kimlik, emir.tur, emir.yon, _yuvarla(emir.adet), _yuvarla(emir.stop),
                                _yuvarla(emir.limit), emir.from_entry, emir.qty_percent, emir.profit, emir.loss,
                                emir.trail_points, emir.trail_offset, _yuvarla(emir.trail_price)))
        if self.a.process_orders_on_close and emir.piyasa and emir.tur != "cikis" and \
                (anahtar or emir.kimlik) in self.bekleyen:
            self._isle_piyasa(self.c[self.i], self.i, sadece=anahtar or emir.kimlik)

    def _varsayilan_adet(self, fiyat: float) -> float:
        tip, deger = self.a.default_qty_type, self.a.default_qty_value
        if tip == "fixed":
            return float(deger)
        if tip == "cash":
            return float(deger) / (fiyat * self.a.point_value)
        if tip == "percent_of_equity":
            return self.equity * float(deger) / 100.0 / (fiyat * self.a.point_value)
        raise ValueError(f"default_qty_type bilinmiyor: {tip}")

    # ---- dolum ----
    def _komisyon(self, fiyat: float, adet: float) -> float:
        t, v = self.a.commission_type, self.a.commission_value
        if t == "percent":
            return abs(fiyat * adet * self.a.point_value) * v / 100.0
        if t == "cash_per_contract":
            return abs(adet) * v
        if t == "cash_per_order":
            return float(v)
        raise ValueError(f"commission_type bilinmiyor: {t}")

    def _kayma(self, fiyat: float, yon: int) -> float:
        return fiyat + yon * self.a.slippage * self.a.mintick

    def _ac(self, emir: _Emir, fiyat: float, bar: int, kaymali: bool) -> None:
        yon = emir.yon
        cevrildi = bool(self.acik and self.acik[0].yon == -yon)
        if cevrildi:                                   # ters çevirme: önce karşı pozisyon kapanır (tek emir sayılır)
            dolum = self._kayma(fiyat, yon) if kaymali else fiyat
            self._kapat(list(self.acik), None, dolum, bar, emir.kimlik, say=False, yorum=emir.yorum)
            self.dolum_sayisi += 1
        if sum(1 for t in self.acik if t.yon == yon) >= max(1, self.a.pyramiding):
            return
        dolum = self._kayma(fiyat, yon) if kaymali else fiyat
        adet = float(emir.adet or 0.0)
        if adet <= 0:
            return
        if not cevrildi:
            self.dolum_sayisi += 1
        self.acik.append(_Islem(emir.kimlik, yon, adet, adet, dolum, bar, self._komisyon(dolum, adet), yorum=emir.yorum))
        self.dolumlar.append({"tarih": self.df.index[bar], "tip": "giris", "yon": yon, "sembol": "",
                              "fiyat": dolum, "adet": adet, "maliyet": self._komisyon(dolum, adet), "neden": emir.kimlik})

    def _ham(self, emir: _Emir, fiyat: float, bar: int, kaymali: bool) -> None:
        yon, kalan = emir.yon, float(emir.adet or 0.0)
        dolum = self._kayma(fiyat, yon) if kaymali else fiyat
        if self.acik and self.acik[0].yon == -yon:
            mevcut = sum(t.adet for t in self.acik)
            kapanan = min(mevcut, kalan)
            self._kapat(list(self.acik), kapanan, dolum, bar, emir.kimlik, say=False, yorum=emir.yorum)
            kalan -= kapanan
        self.dolum_sayisi += 1
        if kalan > 1e-12:
            self.acik.append(_Islem(emir.kimlik, yon, kalan, kalan, dolum, bar, self._komisyon(dolum, kalan), yorum=emir.yorum))
            self.dolumlar.append({"tarih": self.df.index[bar], "tip": "giris", "yon": yon, "sembol": "",
                                  "fiyat": dolum, "adet": kalan, "maliyet": self._komisyon(dolum, kalan), "neden": emir.kimlik})

    def _oca_iptal(self, emir: _Emir) -> None:
        if emir.oca:
            for anahtar, diger in list(self.bekleyen.items()):
                if diger.oca == emir.oca:
                    del self.bekleyen[anahtar]

    def _kapat(self, hedef: list[_Islem], adet: float | None, fiyat: float, bar: int, exit_id: str, say: bool = True,
               yorum: str = "") -> None:
        kalan = sum(t.adet for t in hedef) if adet is None else adet
        if say and kalan > 1e-12:
            self.dolum_sayisi += 1
        for t in hedef:                                # FIFO
            if kalan <= 1e-12:
                break
            q = min(t.adet, kalan)
            pay = q / t.adet
            giris_kom = t.komisyon * pay
            cikis_kom = self._komisyon(fiyat, q)
            brut = t.yon * (fiyat - t.fiyat) * q * self.a.point_value
            net = brut - giris_kom - cikis_kom
            self.gerceklesen += net
            self.kapali.append({"entry_id": t.entry_id, "exit_id": exit_id, "yon": t.yon, "adet": q,
                                "giris_bar": t.bar, "giris_zaman": self.df.index[t.bar], "giris_fiyat": t.fiyat,
                                "cikis_bar": bar, "cikis_zaman": self.df.index[bar], "cikis_fiyat": fiyat,
                                "brut": brut, "komisyon": giris_kom + cikis_kom, "net": net,
                                "entry_comment": t.yorum, "exit_comment": yorum})
            self.dolumlar.append({"tarih": self.df.index[bar], "tip": "cikis", "yon": t.yon, "sembol": "",
                                  "fiyat": fiyat, "adet": q, "maliyet": cikis_kom, "neden": exit_id})
            t.adet -= q
            t.komisyon -= giris_kom
            kalan -= q
        self.acik = [t for t in self.acik if t.adet > 1e-12]

    def _cikis_hedefi(self, emir: _Emir) -> list[_Islem]:
        hedef = [t for t in self.acik if not emir.from_entry or t.entry_id == emir.from_entry]
        if emir.tur == "cikis":
            hedef = [t for t in hedef if emir.kimlik not in t.dolan_cikislar]
        return hedef

    def _uygulama(self, hedef: list[_Islem]) -> list[_Islem]:
        """Kapanışın uygulanacağı işlemler: ANY'de hedefin kendisi, FIFO'da o yöndeki en eski işlemden başlayarak hepsi."""
        if self.a.close_entries_rule == "ANY":
            return hedef
        return [t for t in self.acik if t.yon == hedef[0].yon]

    def _cikis(self, emir: _Emir) -> tuple[int, float, float, list[_Islem], list[_Islem]] | None:
        """Çıkış emrinin (yön, ort. giriş fiyatı, adet, hedef, uygulama) bilgisi. FIFO'da girişi yabancı bir emirle kapanmış
        bağlı çıkış, son bilinen adet ve fiyatla kalan pozisyona uygulanır (Pine belgesi: Buy1/Buy2 örneği)."""
        hedef = self._cikis_hedefi(emir)
        if hedef:
            yon = hedef[0].yon
            ort = sum(t.fiyat * t.adet for t in hedef) / sum(t.adet for t in hedef)
            adet = self._cikis_adedi(emir, hedef)
            emir.son, emir.hedef_nesneleri = (yon, ort, adet), list(hedef)
            return yon, ort, adet, hedef, self._uygulama(hedef)
        if self.a.close_entries_rule == "ANY" or emir.son is None or not emir.bagli:
            return None
        if any(t.adet > 1e-12 or t.kendi_cikisi for t in emir.hedef_nesneleri):
            return None
        yon, ort, adet = emir.son
        kalan = [t for t in self.acik if t.yon == yon]
        if not kalan:
            return None
        return yon, ort, min(adet, sum(t.adet for t in kalan)), [], kalan

    def _cikis_adedi(self, emir: _Emir, hedef: list[_Islem]) -> float:
        acik = sum(t.adet for t in hedef)
        if emir.adet is not None:
            return min(float(emir.adet), acik)
        if emir.qty_percent is not None:
            return min(sum(t.ilk_adet for t in hedef) * float(emir.qty_percent) / 100.0, acik)
        return acik

    def _seviyeler(self, emir: _Emir) -> list[tuple[str, int, float]]:
        """Bir emrin (ad, işlem yönü +1 alış/-1 satış, seviye) tetik listesi; tür ad: stop/limit."""
        if emir.tur in ("giris", "emir"):
            out = []
            if emir.stop is not None:
                out.append(("stop", emir.yon, emir.stop))
            if emir.limit is not None:
                out.append(("limit", emir.yon, emir.limit))
            return out
        bilgi = self._cikis(emir)
        if bilgi is None:
            return []
        yon, ort = bilgi[0], bilgi[1]
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
        bilgi = self._cikis(emir)
        if bilgi is None:
            return None
        yon, ort = bilgi[0], bilgi[1]
        if emir.trail_price is not None:
            return emir.trail_price
        if emir.trail_points is not None:
            return ort + yon * emir.trail_points * self.a.mintick
        return None

    def _doldur(self, anahtar: str, emir: _Emir, tur: str, fiyat: float, bar: int) -> None:
        del self.bekleyen[anahtar]
        kaymali = tur != "limit"
        if emir.tur in ("giris", "emir"):
            (self._ac if emir.tur == "giris" else self._ham)(emir, fiyat, bar, kaymali)
            self._oca_iptal(emir)
            return
        bilgi = self._cikis(emir)
        if bilgi is None:
            return
        yon, _, adet, hedef, uygula = bilgi
        dolum = self._kayma(fiyat, -yon) if kaymali else fiyat
        for t in hedef:
            t.dolan_cikislar.add(emir.kimlik)
            t.kendi_cikisi = True
        self._kapat(uygula, adet, dolum, bar, emir.kimlik, yorum=emir.yorum)

    def _temizle(self) -> None:
        """Bağlandığı işlemler kapanan çıkış emri düşer (Pine: girişi kapanan exit iptal olur)."""
        for anahtar, emir in list(self.bekleyen.items()):
            if emir.tur != "cikis":
                continue
            if self._cikis_hedefi(emir):
                emir.bagli = True
                self._cikis(emir)                      # son bilinen hedef bilgisi
            elif emir.bagli and self._cikis(emir) is None:
                del self.bekleyen[anahtar]

    def _isle_piyasa(self, fiyat: float, bar: int, sadece: str | None = None) -> None:
        for anahtar, emir in list(self.bekleyen.items()):
            if sadece is not None and anahtar != sadece:
                continue
            if emir.tur == "kapat":
                del self.bekleyen[anahtar]
                hedef = self._cikis_hedefi(emir)
                if hedef:
                    adet = self._cikis_adedi(emir, hedef)
                    for t in hedef:
                        t.kendi_cikisi = True
                    self._kapat(self._uygulama(hedef), adet, self._kayma(fiyat, -hedef[0].yon), bar,
                                emir.kimlik if emir.kimlik != "__hepsi__" else "close_all", yorum=emir.yorum)
            elif emir.tur in ("giris", "emir") and emir.piyasa:
                del self.bekleyen[anahtar]
                (self._ac if emir.tur == "giris" else self._ham)(emir, fiyat, bar, kaymali=True)
                self._oca_iptal(emir)

    def _bar_isle(self, j: int, ek: Callable[[], None] | None = None) -> None:
        """`ek` (calc_on_order_fills): dolum olan her fiyat noktasından (O, ara uçlar, C) sonra betik bar içinde yeniden
        yürür; o yürütmenin piyasa emirleri bir sonraki noktada, fiyat emirleri sonraki parçalarda dolabilir."""
        o, h, l, c = self.o[j], self.h[j], self.l[j], self.c[j]
        yol = [o, h, l, c] if abs(h - o) < abs(o - l) else [o, l, h, c]
        for t, b in enumerate(yol):
            once = self.dolum_sayisi
            if t == 0:
                self._isle_piyasa(o, j)
                self._temizle()
                self._yol(o, o, j)                     # açılışta zaten geçilmiş seviyeler (boşluk)
            else:
                if ek is not None:
                    self._isle_piyasa(b, j)
                    self._temizle()
                self._yol(yol[t - 1], b, j)
            if ek is not None and self.dolum_sayisi != once and t < len(yol) - 1:
                ek()

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
                    yon = self._cikis(emir)[0]
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
                bilgi = self._cikis(emir)
                if bilgi is not None:
                    emir.iz_uc = max(emir.iz_uc, b) if bilgi[0] == LONG else min(emir.iz_uc, b)


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
            ctx._bar_isle(i, (lambda i=i: _ara_yurut(modul, ctx, i)) if a.calc_on_order_fills else None)
            ctx._temizle()
        ctx.i = i
        modul.bar(ctx, i, v)
        eq[i] = ctx.equity
    islemler = pd.DataFrame(ctx.kapali, columns=["entry_id", "exit_id", "yon", "adet", "giris_bar", "giris_zaman", "giris_fiyat",
                                                  "cikis_bar", "cikis_zaman", "cikis_fiyat", "brut", "komisyon", "net"])
    acik = [{"entry_id": t.entry_id, "yon": t.yon, "adet": t.adet, "giris_tarihi": df.index[t.bar],
             "giris_fiyati": t.fiyat, "maliyet": t.komisyon} for t in ctx.acik]
    bekleyen = [{"kimlik": e.kimlik, "tur": e.tur, "yon": e.yon, "adet": e.adet, "stop": e.stop,
                 "limit": e.limit, "from_entry": e.from_entry, "verildi": e.verildi} for e in ctx.bekleyen.values()]
    return Sonuc(islemler, pd.Series(eq, index=df.index, name="ozkaynak"), ctx.emir_kaydi, a,
                 ctx.dolumlar, acik, bekleyen)


def _ara_yurut(modul: Any, ctx: Baglam, i: int) -> None:
    ctx.i, ctx.ara = i, True
    try:
        modul.ara(ctx, i)
    finally:
        ctx.ara = False
        ctx.i = i - 1


def gercekci(ayarlar: Ayarlar, kripto: bool) -> dict[str, Any]:
    """TEST_YAPISI Adım 0, uygulanabilir sonuç maliyeti: kripto %0,1/taraf, diğerleri %0,05/taraf + 1 tick."""
    return {"commission_type": "percent", "commission_value": 0.1 if kripto else 0.05,
            "slippage": max(ayarlar.slippage, 0 if kripto else 1)}


def nedensellik(modul: Any, df: pd.DataFrame, kesimler: tuple[float, ...] = (.3, .42, .54, .66, .78, .9),
                tam: "Sonuc | None" = None) -> list[str]:
    """Adım 0: veriyi kesince kesimden önceki emirler değişiyorsa modül geleceği görüyordur. Boş liste = temiz.

    Kesimler yüksek zaman dilimi barlarının (gün, hafta) ortasına düşsün diye küçük asal kaydırmalarla seçilir:
    sınırda kesilen veri, bir sonraki barı gören koda (lookahead) sızıntıyı göstermez.
    """
    tam = (tam or calistir(modul, df)).emir_kaydi   # tam koşu (yazar ayarları) verildiyse yeniden koşulmaz
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
