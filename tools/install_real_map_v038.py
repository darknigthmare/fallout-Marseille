#!/usr/bin/env python3
"""Install or verify Fallout: Mistral v0.38 vector tiles.

The complete cloud cache is the default source. Official HTTP 204 responses are
stored as zero-byte .pbf files accompanied by an .empty.json proof marker; they
are valid no-content coordinates, not missing or corrupted files.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, random, time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from mvt_audit_v036 import parse_tile
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/map_pack/manifest_v038.json'
PUBLISHABLE='sb_publishable_hAcM5bQMkl9a0wn7tgzupg_DeSgYQZC'
MAX_BYTES=8_000_000
EMPTY_SHA=hashlib.sha256(b'').hexdigest()

def marker(path:Path)->Path:return path.with_suffix(path.suffix+'.empty.json')
def atomic(path:Path,data:bytes):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.part');tmp.write_bytes(data);os.replace(tmp,path)
def atomic_text(path:Path,text:str):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.part');tmp.write_text(text,encoding='utf-8');os.replace(tmp,path)
def validate(path:Path,sha:str|None=None):
 try:
  raw=path.read_bytes();m=marker(path)
  if not raw:
   if not m.exists():return False,{'error':'zero-byte file without official-empty marker'}
   proof=json.loads(m.read_text(encoding='utf-8'))
   if proof.get('officialEmpty') is not True:return False,{'error':'invalid empty marker'}
   return True,{'bytes':0,'sha256':EMPTY_SHA,'layers':0,'features':0,'empty':True}
  tile=parse_tile(raw);digest=hashlib.sha256(raw).hexdigest()
  if sha and digest!=sha:return False,{'error':'sha256 mismatch','sha256':digest}
  if m.exists():m.unlink()
  return True,{'bytes':len(raw),'sha256':digest,'layers':len(tile),'features':sum(len(x.features) for x in tile.values()),'empty':False}
 except Exception as e:return False,{'error':repr(e)}
def request(url:str,cloud:bool,timeout:int):
 headers={'User-Agent':'Fallout-Mistral-Real-Map-Installer/0.38','Accept':'application/x-protobuf,application/vnd.mapbox-vector-tile,application/octet-stream'}
 if cloud:headers['apikey']=PUBLISHABLE
 try:
  with urlopen(Request(url,headers=headers),timeout=timeout) as r:
   status=getattr(r,'status',r.getcode());raw=r.read(MAX_BYTES+1);meta={'status':status,'cache':r.headers.get('x-map-cache'),'remoteSha256':r.headers.get('x-map-sha256'),'contentType':r.headers.get('content-type'),'emptyHeader':r.headers.get('x-map-empty')}
 except HTTPError as e:
  if e.code==204:return b'',{'status':204,'cache':None,'remoteSha256':EMPTY_SHA,'contentType':None,'emptyHeader':'1'}
  raise
 if len(raw)>MAX_BYTES:raise RuntimeError('tile exceeds 8 MB')
 empty=status==204 or meta['emptyHeader']=='1' or not raw
 if empty:return b'',{**meta,'officialEmpty':True}
 parse_tile(raw);return raw,{**meta,'officialEmpty':False}
def fetch(row,out:Path,endpoint:str,retries:int,timeout:int):
 dest=out/row['local'].replace('data/map_pack/','')
 if dest.exists():
  ok,m=validate(dest,row.get('sha256'))
  if ok:return {**row,**m,'status':'cached','endpoint':'local'}
  dest.unlink(missing_ok=True);marker(dest).unlink(missing_ok=True)
 order=['cloud','direct'] if endpoint=='auto' else [endpoint];last=None
 for mode in order:
  url=row['relay'] if mode=='cloud' else row['direct']
  for attempt in range(retries):
   try:
    raw,remote=request(url,mode=='cloud',timeout)
    if remote.get('officialEmpty'):
     atomic(dest,b'');atomic_text(marker(dest),json.dumps({'version':'0.38.0','officialEmpty':True,'source':row['source'],'z':row['z'],'x':row['x'],'y':row['y'],'endpoint':mode,'sha256':EMPTY_SHA},ensure_ascii=False,indent=2));return {**row,'bytes':0,'sha256':EMPTY_SHA,'status':'empty','endpoint':mode,**remote}
    atomic(dest,raw);marker(dest).unlink(missing_ok=True);return {**row,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':'downloaded','endpoint':mode,**remote}
   except Exception as e:last=e;time.sleep(min(10,1.6**attempt+random.random()))
 return {**row,'bytes':0,'sha256':None,'status':'error','endpoint':endpoint,'error':repr(last)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=MANIFEST);ap.add_argument('--output',type=Path,default=ROOT/'data/map_pack')
 ap.add_argument('--source',choices=['all','base','cadastre'],default='all');ap.add_argument('--macro',choices=['all','geo_marseille','geo_huveaune','geo_garlaban','geo_calanques','geo_laciotat','geo_frioul','geo_etoile','geo_saintebaume'],default='all')
 ap.add_argument('--endpoint',choices=['auto','cloud','direct'],default='cloud');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--retries',type=int,default=4);ap.add_argument('--timeout',type=int,default=40);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--verify-only',action='store_true')
 a=ap.parse_args();m=json.loads(a.manifest.read_text());rows=m['tiles']
 if a.source!='all':rows=[r for r in rows if r['source']==a.source]
 if a.macro!='all':rows=[r for r in rows if a.macro in r['macros']]
 if a.limit:rows=rows[:a.limit]
 print(f"Sélection : {len(rows)} coordonnées · source={a.source} · macro={a.macro} · endpoint={a.endpoint}")
 if a.dry_run:return 0
 started=time.time();done=[];errors=empty=total_bytes=0
 if a.verify_only:
  for row in rows:
   dest=a.output/row['local'].replace('data/map_pack/','');good,meta=validate(dest,row.get('sha256')) if dest.exists() else (False,{'error':'missing'});status='empty' if good and meta.get('empty') else 'verified' if good else 'error';done.append({**row,**meta,'status':status});errors+=not good;empty+=status=='empty';total_bytes+=meta.get('bytes',0)
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,16))) as ex:
   jobs=[ex.submit(fetch,r,a.output,a.endpoint,a.retries,a.timeout) for r in rows]
   for i,j in enumerate(concurrent.futures.as_completed(jobs),1):
    result=j.result();done.append(result);errors+=result['status']=='error';empty+=result['status']=='empty';total_bytes+=result.get('bytes') or 0
    if i%100==0 or i==len(jobs):print(f"{i}/{len(jobs)} · vides {empty} · erreurs {errors} · {total_bytes/1048576:.1f} Mio",flush=True)
 report={'version':'0.38.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'macro':a.macro,'endpoint':a.endpoint,'selected':len(rows),'ok':len(rows)-errors,'officialEmpty':empty,'errors':errors,'bytes':total_bytes,'seconds':round(time.time()-started,2),'files':sorted(done,key=lambda r:(r['source'],r['z'],r['x'],r['y']))}
 a.output.mkdir(parents=True,exist_ok=True);dest=a.output/f'install_v038_{a.source}_{a.macro}.json';atomic_text(dest,json.dumps(report,ensure_ascii=False,indent=2));print('Rapport :',dest);return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
