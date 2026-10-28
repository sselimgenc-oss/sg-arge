from datetime import UTC, datetime, timedelta
import pandas as pd
from copytrade.arsiv import Arsiv, havuz
NOW=datetime(2026,10,28,tzinfo=UTC)
def test_altin_ornek_tekillestirme_imlec_ve_yol(tmp_path):
 a=Arsiv(tmp_path,NOW);r={"adres":"0xabc","tid":7,"time":1};assert a.append("dolum",[r],"0xabc",123)==1;assert a.append("dolum",[r],"0xabc",124)==0
 assert a.start("dolum","0xabc",0)==124;assert list((tmp_path/"tur=dolum"/"gun=2026-10-28").glob("*.parquet"))
def test_altin_ornek_44_dk_bosluk_degil_46_dk_bosluk(tmp_path):
 a=Arsiv(tmp_path,NOW);a.yoklama("pozisyon","a",900000);a.now=NOW+timedelta(minutes=44);a.yoklama("pozisyon","a",900000);assert a.kapsam()["bosluk"]==0
 a=Arsiv(tmp_path/"x",NOW);a.yoklama("pozisyon","a",900000);a.now=NOW+timedelta(minutes=46);a.yoklama("pozisyon","a",900000)
 try: a.kapsam()
 except RuntimeError: pass
 else: raise AssertionError("%10 üstü boşluk kırmızı olmalı")
 assert __import__("json").loads((tmp_path/"x"/"tur=kapsam"/"gun=2026-10-28"/"ozet.json").read_text())["bosluk"]==2
def test_altin_ornek_olay_bos_sema_ve_guncel_kapi_havuzu(tmp_path):
 (tmp_path/"copytrade").mkdir();(tmp_path/"copytrade"/"izleme_listesi.yaml").write_text("traderlar: []")
 k=tmp_path/"kapi"/"2026-10-28";k.mkdir(parents=True);pd.DataFrame([{"address":"0x"+"a"*40,"adim1":"Geçti","adim2":"Geçti"}]).to_csv(k/"sonuc.csv",index=False)
 assert havuz(tmp_path,tmp_path/"kapi")==["0x"+"a"*40];a=Arsiv(tmp_path/"a",NOW);a.empty_schema("olay");assert (tmp_path/"a"/"tur=olay"/"gun=2026-10-28"/"sema.parquet").exists()
