#!/usr/bin/env python3
"""Install or verify Fallout: Mistral v0.37 official vector tiles.

Resumable and atomic. Every response is parsed as Mapbox Vector Tile before it is
kept. The default `auto` endpoint tries the official data.gouv.fr source first and
uses the bounded v0.37 cache relay only as a fallback.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, random, threading, time
from pathlib import Path
from urllib.request import Request, urlopen
from mvt_audit_v036 import parse_tile
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/map_pack/manifest_v037.json'
PUBLISHABLE='sb_publishable_hAcM5bQMkl9a0wn7tgzupg_DeSgYQZC'
MAX_BYTES=8_000_000

def atomic(path:Path,data:bytes):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.part');tmp.write_bytes(data);os.replace(tmp,path)
def validate(path:Path,sha:str|None=None):
 try:
  raw=path.read_bytes();tile=parse_tile(raw);digest=hashlib.sha256(raw).hexdigest()
  if sha and digest!=sha:return False,{'error':'sha256 mismatch','sha256':digest}
  return True,{'bytes':len(raw),'sha256':digest,'layers':len(tile),'features':sum(len(x.features) for x in tile.values())}
 except Exception as e:return False,{'error':repr(e)}
def request(url:str,relay:bool,timeout:int):
 headers={'User-Agent':'Fallout-Mistral-Real-Map-Installer/0.37','Accept':'application/x-protobuf,application/vnd.mapbox-vector-tile,application/octet-stream'}
 if relay:headers['apikey']=PUBLISHABLE
 with urlopen(Request(url,headers=headers),timeout=timeout) as r:
  raw=r.read(MAX_BYTES+1);meta={'cache':r.headers.get('x-map-cache'),'remoteSha256':r.headers.get('x-map-sha256'),'contentType':r.headers.get('content-type')}
 if len(raw)>MAX_BYTES:raise RuntimeError('tile exceeds 8 MB')
 parse_tile(raw);return raw,meta
def fetch(row,out:Path,endpoint:str,retries:int,timeout:int):
 dest=out/row['local'].replace('data/map_pack/','')
 if dest.exists():
  ok,m=validate(dest,row.get('sha256'))
  if ok:return {**row,**m,'status':'cached','endpoint':'local'}
  dest.unlink(missing_ok=True)
 order=['direct','relay'] if endpoint=='auto' else [endpoint];last=None
 for mode in order:
  url=row['direct'] if mode=='direct' else row['relay']
  for attempt in range(retries):
   try:
    raw,remote=request(url,mode=='relay',timeout);atomic(dest,raw);digest=hashlib.sha256(raw).hexdigest()
    return {**row,'bytes':len(raw),'sha256':digest,'status':'downloaded','endpoint':mode,**remote}
   except Exception as e:last=e;time.sleep(min(10,1.6**attempt+random.random()))
 return {**row,'bytes':0,'sha256':None,'status':'error','endpoint':endpoint,'error':repr(last)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=MANIFEST);ap.add_argument('--output',type=Path,default=ROOT/'data/map_pack')
 ap.add_argument('--source',choices=['all','base','cadastre'],default='all');ap.add_argument('--macro',choices=['all','geo_marseille','geo_huveaune','geo_garlaban','geo_calanques','geo_laciotat','geo_frioul','geo_etoile','geo_saintebaume'],default='all')
 ap.add_argument('--endpoint',choices=['auto','direct','relay'],default='auto');ap.add_argument('--workers',type=int,default=6);ap.add_argument('--retries',type=int,default=4);ap.add_argument('--timeout',type=int,default=40);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--verify-only',action='store_true')
 a=ap.parse_args();m=json.loads(a.manifest.read_text());rows=m['tiles']
 if a.source!='all':rows=[r for r in rows if r['source']==a.source]
 if a.macro!='all':rows=[r for r in rows if a.macro in r['macros']]
 if a.limit:rows=rows[:a.limit]
 print(f"Sélection : {len(rows)} tuiles · source={a.source} · macro={a.macro} · endpoint={a.endpoint}")
 if a.dry_run:return 0
 started=time.time();done=[];errors=0;total_bytes=0
 if a.verify_only:
  for row in rows:
   dest=a.output/row['local'].replace('data/map_pack/','');good,meta=validate(dest,row.get('sha256')) if dest.exists() else (False,{'error':'missing'});done.append({**row,**meta,'status':'verified' if good else 'error'});errors+=not good;total_bytes+=meta.get('bytes',0)
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,16))) as ex:
   jobs=[ex.submit(fetch,r,a.output,a.endpoint,a.retries,a.timeout) for r in rows]
   for i,j in enumerate(concurrent.futures.as_completed(jobs),1):
    result=j.result();done.append(result);errors+=result['status']=='error';total_bytes+=result.get('bytes') or 0
    if i%50==0 or i==len(jobs):print(f"{i}/{len(jobs)} · erreurs {errors} · {total_bytes/1048576:.1f} Mio",flush=True)
 report={'version':'0.37.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'macro':a.macro,'endpoint':a.endpoint,'selected':len(rows),'ok':len(rows)-errors,'errors':errors,'bytes':total_bytes,'seconds':round(time.time()-started,2),'files':sorted(done,key=lambda r:(r['source'],r['z'],r['x'],r['y']))}
 a.output.mkdir(parents=True,exist_ok=True);dest=a.output/f'install_v037_{a.source}_{a.macro}.json';tmp=dest.with_suffix('.json.part');tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2));os.replace(tmp,dest);print('Rapport :',dest);return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
