"""R2'ye senkronlanan, yalnız eklemeli halka açık Hyperliquid arşivi."""
from __future__ import annotations
import argparse, hashlib, json, time
from datetime import UTC, datetime, timedelta
from pathlib import Path
import pandas as pd
from copytrade.izleme_motoru import load_list
from copytrade.kurallar import load_rules
from copytrade.tarama import PublicClient
SEMA_SURUMU = 1
def _day(now): return now.astimezone(UTC).date().isoformat()
def _key(t,r):
    if t=="dolum": return f"{r.get('adres')}:{r.get('tid')}"
    if t=="funding": return f"{r.get('adres')}:{r.get('time')}:{r.get('hash')}"
    if t=="mum_1dk": return f"{r.get('coin')}:{r.get('t',r.get('time'))}"
    return hashlib.sha256(json.dumps(r,sort_keys=True,default=str).encode()).hexdigest()
class Arsiv:
 def __init__(self,root,now=None): self.root,self.now=Path(root),now or datetime.now(UTC)
 def _folder(self,t): return self.root/f"tur={t}"/f"gun={_day(self.now)}"
 def start(self,t,s,fallback):
  p=self.root/f"tur={t}"/"son.json"; return (json.loads(p.read_text()).get(s) if p.exists() else None) or fallback
 def append(self,t,rows,subject=None,cursor=None):
  folder=self._folder(t);folder.mkdir(parents=True,exist_ok=True);known=set()
  for p in self.root.glob(f"tur={t}/gun=*/*.parquet"): known.update(pd.read_parquet(p,columns=["_anahtar"])["_anahtar"].astype(str))
  out=[]
  for raw in rows:
   r=dict(raw);r["sema_surumu"]=SEMA_SURUMU;r.setdefault("alindi_ms",int(self.now.timestamp()*1000));k=_key(t,r)
   if k not in known: known.add(k);out.append({"_anahtar":k,"sema_surumu":SEMA_SURUMU,"alindi_ms":r["alindi_ms"],"veri":json.dumps(r,sort_keys=True,default=str)})
  if out: pd.DataFrame(out).to_parquet(folder/f"parca-{time.time_ns()}.parquet",index=False,compression="zstd")
  if subject and cursor is not None:
   p=self.root/f"tur={t}"/"son.json";p.parent.mkdir(parents=True,exist_ok=True);d=json.loads(p.read_text()) if p.exists() else {};d[subject]=int(cursor);p.write_text(json.dumps(d,sort_keys=True))
  return len(out)
 def empty_schema(self,t):
  p=self._folder(t)/"sema.parquet";p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists(): pd.DataFrame(columns=["_anahtar","sema_surumu","alindi_ms","veri"]).to_parquet(p,index=False,compression="zstd")
 def yoklama(self,t,s,interval):
  p=self.root/"tur=kapsam"/f"gun={_day(self.now)}"/"yoklamalar.json";p.parent.mkdir(parents=True,exist_ok=True);d=json.loads(p.read_text()) if p.exists() else [];d.append({"tur":t,"ozne":s,"zaman_ms":int(self.now.timestamp()*1000),"aralik_ms":interval});p.write_text(json.dumps(d))
 def kapsam(self):
  p=self.root/"tur=kapsam"/f"gun={_day(self.now)}"/"yoklamalar.json";d=json.loads(p.read_text()) if p.exists() else []; gaps=expected=0
  for _,r in pd.DataFrame(d).groupby(["tur","ozne"]) if d else []:
   r=r.sort_values("zaman_ms");i=int(r.iloc[0].aralik_ms);ts=list(r.zaman_ms);expected+=len(ts);gaps+=sum(max(0,(b-a)//i-1) for a,b in zip(ts,ts[1:]) if b-a>int(load_rules()["arsiv_bosluk_carpani"])*i)
  x={"yoklama":expected,"bosluk":gaps,"oran":gaps/max(1,expected)};(p.parent/"ozet.json").write_text(json.dumps(x,ensure_ascii=False,indent=2))
  if x["oran"]>float(load_rules()["arsiv_bosluk_esigi"]):raise RuntimeError("Arşiv boşluk oranı eşiği aşıldı")
  return x
def havuz(root,kapi_root=None):
 out={x["adres"].lower() for x in load_list(Path(root)/"copytrade/izleme_listesi.yaml")}
 for f in (Path(kapi_root) if kapi_root else Path("/olmayan")).glob("*/sonuc.csv"):
  for _,r in pd.read_csv(f).iterrows():
   if str(r.get("adim1"))=="Geçti" and str(r.get("adim2"))=="Geçti":out.add(str(r.get("address",r.get("adres",""))).lower())
 return sorted(x for x in out if x.startswith("0x"))
def collect(root,out,kinds,kapi_root=None,client=None,now=None):
 now=now or datetime.now(UTC);a=Arsiv(out,now);c=client or PublicClient();pool=havuz(root,kapi_root);start=lambda t,s:a.start(t,s,int((now-timedelta(hours=1)).timestamp()*1000));coins=set()
 for ad in pool:
  if "dolum" in kinds:
   rows=[dict(x,adres=ad) for x in c.fills(ad,start("dolum",ad))];coins|={str(x.get("coin")) for x in rows if x.get("coin")};a.append("dolum",rows,ad,int(now.timestamp()*1000));a.yoklama("dolum",ad,3600000)
  if "funding" in kinds:
   rows=[dict(x,adres=ad) for x in c.info({"type":"userFunding","user":ad,"startTime":start("funding",ad)})];a.append("funding",rows,ad,int(now.timestamp()*1000));a.yoklama("funding",ad,3600000)
  if "pozisyon" in kinds:a.append("pozisyon",[{"adres":ad,"durum":c.info({"type":"clearinghouseState","user":ad},weight=2)}]);a.yoklama("pozisyon",ad,900000)
 if "mum_1dk" in kinds:
  for p in a.root.glob("tur=dolum/gun=*/*.parquet"):
   coins|={json.loads(x).get("coin") for x in pd.read_parquet(p)["veri"]}
  coins.discard(None)
  for coin in coins:a.append("mum_1dk",c.candles(coin,start("mum_1dk",coin),int(now.timestamp()*1000),"1m"),coin,int(now.timestamp()*1000));a.yoklama("mum_1dk",coin,900000)
 if "leaderboard" in kinds:a.append("leaderboard",c.leaderboard());a.yoklama("leaderboard","tum",604800000)
 if "olay" in kinds:a.empty_schema("olay")
 summary,olcum=a.kapsam(),{"havuz":len(pool),"istek_agirligi":getattr(c.limiter,"weight_used",0)}
 (a.root/"tur=kapsam"/f"gun={_day(now)}"/"k8.json").write_text(json.dumps(olcum,ensure_ascii=False,indent=2))
 return summary,olcum
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("."));p.add_argument("--output",type=Path,default=Path("arsiv"));p.add_argument("--kapi-root",type=Path);p.add_argument("--tur",default="dolum,funding,pozisyon");x=p.parse_args();print(collect(x.root,x.output,set(x.tur.split(",")),x.kapi_root))
