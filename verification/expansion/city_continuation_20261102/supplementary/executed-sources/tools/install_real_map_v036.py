#!/usr/bin/env python3
"""Install the complete real vector territory pack for Fallout: Mistral v0.36.

The downloader is resumable, atomic and validates every Mapbox Vector Tile before
keeping it. Direct official endpoints are preferred; the authenticated Supabase
relay can be used when a browser/network requires a CORS-compatible source.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, random, threading, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from mvt_audit_v036 import parse_tile

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=ROOT/'data'/'map_pack'/'manifest_v036.json'
ANON_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5a2tsY3Z2d2p3aGN2dWtienRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4NTgwNjAsImV4cCI6MjA5NzQzNDA2MH0.630TpeNsO-W7CT2QTQ53_3Y36ioOjvHB6-Pst6AQY7g'
TLS=threading.local()

def atomic_write(path:Path,data:bytes):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.part');tmp.write_bytes(data);os.replace(tmp,path)

def valid(path:Path,expected_sha:str|None=None)->tuple[bool,dict]:
 try:
  data=path.read_bytes();layers=parse_tile(data);sha=hashlib.sha256(data).hexdigest()
  if expected_sha and sha!=expected_sha:return False,{'error':'sha256 mismatch','sha256':sha}
  return True,{'bytes':len(data),'sha256':sha,'layers':len(layers),'features':sum(len(l.features) for l in layers.values())}
 except Exception as e:return False,{'error':repr(e)}

def fetch(row:dict,root:Path,use_relay:bool,retries:int,timeout:int)->dict:
 dest=root/row['local'].replace('data/map_pack/','')
 if dest.exists():
  ok,meta=valid(dest,row.get('sha256'))
  if ok:return {**row,**meta,'status':'cached'}
  dest.unlink(missing_ok=True)
 url=row['relay'] if use_relay else row['direct']
 headers={'User-Agent':'Fallout-Mistral-Real-Map-Installer/0.36','Accept':'application/x-protobuf,application/vnd.mapbox-vector-tile,*/*'}
 if use_relay:headers.update({'Authorization':'Bearer '+ANON_KEY,'apikey':ANON_KEY})
 last=None
 for attempt in range(retries):
  try:
   with urlopen(Request(url,headers=headers),timeout=timeout) as r:data=r.read(8_000_001)
   if len(data)>8_000_000:raise RuntimeError('tile exceeds 8 MB')
   parse_tile(data);atomic_write(dest,data)
   return {**row,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'status':'downloaded','endpoint':'relay' if use_relay else 'direct'}
  except Exception as e:
   last=e;time.sleep(min(12,(1.7**attempt)+random.random()))
 return {**row,'bytes':0,'sha256':None,'status':'error','endpoint':'relay' if use_relay else 'direct','error':repr(last)}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--manifest',type=Path,default=DEFAULT_MANIFEST);ap.add_argument('--output',type=Path,default=ROOT/'data'/'map_pack')
 ap.add_argument('--source',choices=['all','base','cadastre'],default='all');ap.add_argument('--macro',choices=['all','geo_marseille','geo_huveaune','geo_garlaban','geo_calanques','geo_laciotat','geo_frioul','geo_etoile','geo_saintebaume'],default='all')
 ap.add_argument('--workers',type=int,default=6);ap.add_argument('--retries',type=int,default=5);ap.add_argument('--timeout',type=int,default=35);ap.add_argument('--limit',type=int,default=0)
 ap.add_argument('--relay',action='store_true',help='use the authenticated CORS relay instead of direct official endpoints');ap.add_argument('--dry-run',action='store_true');ap.add_argument('--verify-only',action='store_true')
 a=ap.parse_args();manifest=json.loads(a.manifest.read_text());rows=manifest['tiles']
 if a.source!='all':rows=[r for r in rows if r['source']==a.source]
 if a.macro!='all':rows=[r for r in rows if a.macro in r['macros']]
 if a.limit:rows=rows[:a.limit]
 print(f"Sélection : {len(rows)} tuiles · source={a.source} · macro={a.macro} · mode={'relay' if a.relay else 'direct'}")
 if a.dry_run:return 0
 started=time.time();done=[];errors=0;bytes_total=0
 if a.verify_only:
  for row in rows:
   dest=a.output/row['local'].replace('data/map_pack/','');ok,meta=valid(dest,row.get('sha256')) if dest.exists() else (False,{'error':'missing'})
   done.append({**row,**meta,'status':'verified' if ok else 'error'});errors+=not ok;bytes_total+=meta.get('bytes',0)
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,a.workers)) as ex:
   futures=[ex.submit(fetch,row,a.output,a.relay,a.retries,a.timeout) for row in rows]
   for i,f in enumerate(concurrent.futures.as_completed(futures),1):
    row=f.result();done.append(row);errors+=row['status']=='error';bytes_total+=row.get('bytes',0) or 0
    if i%50==0 or i==len(futures):print(f"{i}/{len(futures)} · erreurs {errors} · {bytes_total/1024/1024:.1f} Mio",flush=True)
 report={'version':'0.36.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'macro':a.macro,'endpoint':'relay' if a.relay else 'direct','selected':len(rows),'ok':len(rows)-errors,'errors':errors,'bytes':bytes_total,'seconds':round(time.time()-started,2),'files':sorted(done,key=lambda r:(r['source'],r['z'],r['x'],r['y']))}
 a.output.mkdir(parents=True,exist_ok=True);name=f"install_v036_{a.source}_{a.macro}.json";tmp=a.output/(name+'.part');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,a.output/name)
 print(f"Rapport : {a.output/name}")
 return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
