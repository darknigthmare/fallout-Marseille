#!/usr/bin/env python3
"""Install or verify Fallout: Mistral v0.38 vector tiles.

The complete cloud cache is the default source. Official HTTP 204 responses are
stored as zero-byte .pbf files accompanied by an .empty.json proof marker; they
are valid no-content coordinates, not missing or corrupted files.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, random, time, zlib
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
def validate(path:Path,sha:str|None=None,row:dict|None=None):
 try:
  if path.stat().st_size>MAX_BYTES:return False,{'error':'tile exceeds size limit'}
  raw=path.read_bytes();m=marker(path)
  if not raw:
   if not m.exists():return False,{'error':'zero-byte file without official-empty marker'}
   if m.stat().st_size>64_000:return False,{'error':'empty marker exceeds size limit'}
   proof=json.loads(m.read_text(encoding='utf-8'))
   if proof.get('officialEmpty') is not True:return False,{'error':'invalid empty marker'}
   if row and any(k in proof and (type(proof[k]) is not type(row[k]) or proof[k]!=row[k]) for k in ('source','z','x','y')):return False,{'error':'empty marker belongs to another coordinate'}
   if proof.get('sha256') and proof['sha256']!=EMPTY_SHA:return False,{'error':'invalid empty hash'}
   if sha and sha.lower()!=EMPTY_SHA:return False,{'error':'empty tile differs from pinned SHA-256'}
   return True,{'bytes':0,'sha256':EMPTY_SHA,'layers':0,'features':0,'empty':True}
  tile=parse_tile(raw);digest=hashlib.sha256(raw).hexdigest()
  if sha and digest!=sha.lower():return False,{'error':'sha256 mismatch','sha256':digest}
  return True,{'bytes':len(raw),'sha256':digest,'layers':len(tile),'features':sum(len(x.features) for x in tile.values()),'empty':False}
 except Exception as e:return False,{'error':repr(e)}

def decode_http_body(raw:bytes,encoding:str|None=None,max_bytes:int=MAX_BYTES)->bytes:
 """urllib preserves Content-Encoding; bound both wire and decoded tile sizes."""
 if len(raw)>max_bytes:raise RuntimeError('tile exceeds wire size limit')
 encoding=(encoding or '').strip().lower()
 if encoding not in ('','identity','gzip','x-gzip'):raise RuntimeError(f'unsupported content encoding: {encoding}')
 compressed=raw.startswith(b'\x1f\x8b')
 if encoding in ('gzip','x-gzip') and not compressed:raise RuntimeError('gzip header without a gzip body')
 if not compressed:return raw
 try:
  decoder=zlib.decompressobj(16+zlib.MAX_WBITS)
  decoded=decoder.decompress(raw,max_bytes+1)
  if len(decoded)>max_bytes or decoder.unconsumed_tail:raise RuntimeError('decoded tile exceeds size limit')
  decoded+=decoder.flush(max_bytes+1-len(decoded))
  if len(decoded)>max_bytes:raise RuntimeError('decoded tile exceeds size limit')
  if not decoder.eof:raise RuntimeError('truncated gzip tile')
  if decoder.unused_data:raise RuntimeError('unexpected data after gzip tile')
  return decoded
 except zlib.error as e:raise RuntimeError(f'invalid gzip tile: {e}') from e

def request(url:str,cloud:bool,timeout:int):
 headers={'User-Agent':'Fallout-Mistral-Real-Map-Installer/0.38','Accept':'application/x-protobuf,application/vnd.mapbox-vector-tile,application/octet-stream'}
 if cloud:headers['apikey']=PUBLISHABLE
 try:
  with urlopen(Request(url,headers=headers),timeout=timeout) as r:
   status=getattr(r,'status',r.getcode());raw=r.read(MAX_BYTES+1);meta={'httpStatus':status,'cache':r.headers.get('x-map-cache'),'remoteSha256':r.headers.get('x-map-sha256'),'contentType':r.headers.get('content-type'),'contentEncoding':r.headers.get('content-encoding'),'emptyHeader':r.headers.get('x-map-empty')}
 except HTTPError as e:
  if e.code==204:return b'',{'httpStatus':204,'cache':None,'remoteSha256':EMPTY_SHA,'contentType':None,'emptyHeader':'1','officialEmpty':True}
  raise
 if status not in (200,204):raise RuntimeError(f'unexpected HTTP {status}')
 if len(raw)>MAX_BYTES:raise RuntimeError('tile exceeds 8 MB')
 empty=status==204 or meta['emptyHeader']=='1'
 if empty:
  if raw:raise RuntimeError('official-empty response contains bytes')
  if meta['remoteSha256'] and meta['remoteSha256'].lower()!=EMPTY_SHA:raise RuntimeError('official-empty response has a contradictory SHA-256')
  return b'',{**meta,'officialEmpty':True}
 if not raw:raise RuntimeError('empty HTTP 200 response without official proof')
 wire_bytes=len(raw);raw=decode_http_body(raw,meta['contentEncoding'])
 parse_tile(raw)
 digest=hashlib.sha256(raw).hexdigest()
 if meta['remoteSha256'] and meta['remoteSha256'].lower()!=digest:raise RuntimeError('remote tile SHA-256 differs from decoded content')
 return raw,{**meta,'wireBytes':wire_bytes,'officialEmpty':False}
def fetch(row,out:Path,endpoint:str,retries:int,timeout:int):
 dest=out/row['local'].replace('data/map_pack/','')
 if dest.exists():
  ok,m=validate(dest,row.get('sha256'),row)
  if ok:return {**row,**m,'status':'cached','endpoint':'local'}
 order=['cloud','direct'] if endpoint=='auto' else [endpoint];last=None
 for mode in order:
  url=row['relay'] if mode=='cloud' else row['direct']
  for attempt in range(retries):
   try:
    raw,remote=request(url,mode=='cloud',timeout)
    digest=hashlib.sha256(raw).hexdigest()
    if row.get('sha256') and digest!=row['sha256'].lower():raise RuntimeError('download differs from pinned SHA-256')
    if remote.get('officialEmpty'):
     # Publish the proof first: a crash must never leave a new zero-byte tile
     # accompanied by a stale proof from a different coordinate.
     atomic_text(marker(dest),json.dumps({'version':'0.38.0','officialEmpty':True,'source':row['source'],'z':row['z'],'x':row['x'],'y':row['y'],'endpoint':mode,'sha256':EMPTY_SHA},ensure_ascii=False,indent=2));atomic(dest,b'');return {**row,'bytes':0,'sha256':EMPTY_SHA,'status':'empty','endpoint':mode,**remote}
    atomic(dest,raw);marker(dest).unlink(missing_ok=True);return {**row,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'status':'downloaded','endpoint':mode,**remote}
   except Exception as e:
    last=e
    if attempt+1<retries:time.sleep(min(10,1.6**attempt+random.random()))
 return {**row,'bytes':0,'sha256':None,'status':'error','endpoint':endpoint,'error':repr(last)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=MANIFEST);ap.add_argument('--output',type=Path,default=ROOT/'data/map_pack')
 ap.add_argument('--source',choices=['all','base','cadastre'],default='all');ap.add_argument('--macro',choices=['all','geo_marseille','geo_huveaune','geo_garlaban','geo_calanques','geo_laciotat','geo_frioul','geo_etoile','geo_saintebaume'],default='all')
 ap.add_argument('--endpoint',choices=['auto','cloud','direct'],default='cloud');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--retries',type=int,default=4);ap.add_argument('--timeout',type=int,default=40);ap.add_argument('--limit',type=int,default=0);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--verify-only',action='store_true')
 a=ap.parse_args();m=json.loads(a.manifest.read_text());rows=m['tiles']
 if a.retries<1 or a.timeout<=0:ap.error('--retries and --timeout must be positive')
 if a.source!='all':rows=[r for r in rows if r['source']==a.source]
 if a.macro!='all':rows=[r for r in rows if a.macro in r['macros']]
 if a.limit:rows=rows[:a.limit]
 print(f"Sélection : {len(rows)} coordonnées · source={a.source} · macro={a.macro} · endpoint={a.endpoint}")
 if a.dry_run:return 0
 started=time.time();done=[];errors=empty=total_bytes=0
 if a.verify_only:
  for row in rows:
   dest=a.output/row['local'].replace('data/map_pack/','');good,meta=validate(dest,row.get('sha256'),row) if dest.exists() else (False,{'error':'missing'});status='empty' if good and meta.get('empty') else 'verified' if good else 'error';done.append({**row,**meta,'status':status});errors+=not good;empty+=status=='empty';total_bytes+=meta.get('bytes',0)
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,16))) as ex:
   jobs=[ex.submit(fetch,r,a.output,a.endpoint,a.retries,a.timeout) for r in rows]
   for i,j in enumerate(concurrent.futures.as_completed(jobs),1):
    result=j.result();done.append(result);errors+=result['status']=='error';empty+=result['status']=='empty';total_bytes+=result.get('bytes') or 0
    if i%100==0 or i==len(jobs):print(f"{i}/{len(jobs)} · vides {empty} · erreurs {errors} · {total_bytes/1048576:.1f} Mio",flush=True)
 report={'version':'0.38.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'macro':a.macro,'endpoint':a.endpoint,'selected':len(rows),'ok':len(rows)-errors,'officialEmpty':empty,'errors':errors,'bytes':total_bytes,'seconds':round(time.time()-started,2),'files':sorted(done,key=lambda r:(r['source'],r['z'],r['x'],r['y']))}
 a.output.mkdir(parents=True,exist_ok=True);dest=a.output/f'install_v038_{a.source}_{a.macro}.json';atomic_text(dest,json.dumps(report,ensure_ascii=False,indent=2));print('Rapport :',dest);return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
