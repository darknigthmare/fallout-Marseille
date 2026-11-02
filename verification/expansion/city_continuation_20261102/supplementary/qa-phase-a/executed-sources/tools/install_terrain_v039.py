#!/usr/bin/env python3
"""Install or verify the eight official RGE ALTI sampled grids for Fallout: Mistral v0.39.

The configured historical relay is preferred. If it fails, the official IGN
point-elevation API is queried in bounded, resumable batches. Offline mode never
contacts either service. NoData stays null; no synthetic altitude is inserted.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, math, os, re, shutil, threading, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from install_real_map_v038 import decode_http_body

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=ROOT/'data/map_pack/terrain/manifest_v039.json'
DEFAULT_OUTPUT=ROOT/'data/map_pack/terrain'
MAX_BYTES=6_000_000
OFFICIAL_API='https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json'
OFFICIAL_RESOURCE='ign_rge_alti_wld'
MAX_BATCH_POINTS=5000

class TerrainError(RuntimeError): pass

class RateLimiter:
    """One shared budget for all workers; IGN currently allows 5 requests/s/IP."""
    def __init__(self,per_second=4):
        self.interval=1/per_second;self.next_at=0.0;self.lock=threading.Lock()
    def wait(self):
        with self.lock:
            now=time.monotonic();due=max(now,self.next_at);self.next_at=due+self.interval
        if due>now:time.sleep(due-now)

OFFICIAL_RATE=RateLimiter()

def atomic(path:Path,data:bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.part')
    tmp.write_bytes(data)
    os.replace(tmp,path)

def atomic_json(path:Path,obj):
    atomic(path,(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())

def sanitise(value,lo=-100,hi=9000):
    if type(value) not in (int,float):return None
    z=float(value)
    if not math.isfinite(z) or not lo<z<hi:return None
    z=round(z,2)
    return z if lo<z<hi else None

def validate_bytes(raw:bytes,region:dict,manifest:dict):
    if not raw:raise TerrainError('empty terrain JSON')
    if len(raw)>MAX_BYTES:raise TerrainError(f'terrain exceeds {MAX_BYTES} bytes')
    try:j=json.loads(raw)
    except Exception as e:raise TerrainError(f'invalid JSON: {e}') from e
    if not isinstance(j,dict):raise TerrainError('terrain JSON must be an object')
    grid=manifest['grid'];w=j.get('width');h=j.get('height');macro=region['macro']
    if type(w) is not int or type(h) is not int:raise TerrainError('grid dimensions must be integers')
    if j.get('macro')!=macro:raise TerrainError(f'macro mismatch {j.get("macro")} != {macro}')
    if (w,h)!=(int(grid['width']),int(grid['height'])):raise TerrainError(f'grid mismatch {w}x{h}')
    vals=j.get('values')
    if not isinstance(vals,list) or len(vals)!=w*h:raise TerrainError(f'value count {len(vals) if isinstance(vals,list) else 0}/{w*h}')
    resource=j.get('sourceResource') or j.get('source_resource') or j.get('resource')
    if resource!=manifest['source']['resource']:raise TerrainError(f'unexpected or missing resource {resource}')
    bbox=j.get('bbox') or j.get('bboxWGS84')
    if not isinstance(bbox,list) or len(bbox)!=4 or any(type(x) not in (int,float) or not math.isfinite(x) for x in bbox):raise TerrainError('invalid bbox')
    if bbox[0]>=bbox[2] or bbox[1]>=bbox[3]:raise TerrainError('inverted bbox')
    if max(abs(float(bbox[i])-float(region['bbox'][i])) for i in range(4))>1e-7:raise TerrainError('bbox differs from manifest')
    if j.get('rowOrder')!='north-to-south':raise TerrainError('terrain row order is missing or incompatible')
    lo=manifest['noData']['minimumExclusive'];hi=manifest['noData']['maximumExclusive']
    clean=[];valid=[];changed=0
    for v in vals:
        z=sanitise(v,lo,hi)
        if z is None and v is not None:changed+=1
        clean.append(z)
        if z is not None:valid.append(z)
    if not valid:raise TerrainError('no valid RGE ALTI values')
    j['values']=clean;j['validPoints']=len(valid);j['missingPoints']=len(clean)-len(valid);j['coverage']=len(valid)/len(clean)
    j['min']=min(valid);j['max']=max(valid);j['mean']=sum(valid)/len(valid)
    j['source']='RGE ALTI IGN';j['sourceResource']=manifest['source']['resource'];j['sourceTitle']=manifest['source']['title'];j['license']=manifest['source']['license'];j['verticalDatum']=manifest['source']['verticalDatum'];j['rowOrder']='north-to-south'
    j['noDataPolicy']='null, non-finite, <= -100 m and >= 9000 m remain NoData; no synthetic altitude is inserted'
    canonical=(json.dumps(j,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    if len(canonical)>MAX_BYTES:raise TerrainError('canonical terrain exceeds size limit')
    return canonical,{'macro':macro,'width':w,'height':h,'valid':len(valid),'missing':len(clean)-len(valid),'min':min(valid),'max':max(valid),'mean':sum(valid)/len(valid),'sanitised':changed,'bytes':len(canonical),'sha256':hashlib.sha256(canonical).hexdigest(),'coverage':len(valid)/len(clean)}

def grid_coordinates(region,manifest):
    macro=region['macro'];bbox=region['bbox'];w=manifest['grid']['width'];h=manifest['grid']['height']
    if not re.fullmatch(r'[A-Za-z0-9_-]+',macro):raise TerrainError('invalid macro identifier')
    if type(w) is not int or type(h) is not int or min(w,h)<2 or w*h>1_048_576:raise TerrainError('invalid official grid dimensions')
    if not isinstance(bbox,list) or len(bbox)!=4 or any(type(x) not in (int,float) or not math.isfinite(x) for x in bbox):raise TerrainError('invalid official grid bbox')
    south,west,north,east=bbox
    if not (-90<=south<north<=90 and -180<=west<east<=180):raise TerrainError('invalid official grid extent')
    return [(round(north-y*(north-south)/(h-1),10),round(west+x*(east-west)/(w-1),10)) for y in range(h) for x in range(w)]

def official_payload(points):
    return {'lon':'|'.join(f'{lon:.10f}' for lat,lon in points),'lat':'|'.join(f'{lat:.10f}' for lat,lon in points),'resource':OFFICIAL_RESOURCE,'delimiter':'|','indent':'false','measures':'false','zonly':'false'}

def decode_official_batch(raw,points,manifest):
    if not raw or len(raw)>MAX_BYTES:raise TerrainError('invalid official response size')
    try:response=json.loads(raw)
    except (ValueError,UnicodeError) as e:raise TerrainError('official response is not JSON') from e
    elevations=response.get('elevations') if isinstance(response,dict) else None
    if not isinstance(elevations,list) or len(elevations)!=len(points):raise TerrainError('official response has the wrong point count')
    values=[]
    for item,(lat,lon) in zip(elevations,points):
        if not isinstance(item,dict):raise TerrainError('official response omits point coordinates')
        if any(type(item.get(k)) not in (int,float) or not math.isfinite(item[k]) for k in ('lat','lon')):raise TerrainError('invalid official point coordinates')
        if abs(item['lat']-lat)>1e-7 or abs(item['lon']-lon)>1e-7:raise TerrainError('official response reordered or changed a coordinate')
        if 'z' not in item or (item['z'] is not None and type(item['z']) not in (int,float)):raise TerrainError('official altitude is missing or malformed')
        values.append(sanitise(item['z'],manifest['noData']['minimumExclusive'],manifest['noData']['maximumExclusive']))
    return values

def fetch_official_region(region,manifest,output,timeout,retries,batch_size=MAX_BATCH_POINTS):
    """Fetch measured points, keeping validated batches when an attempt fails."""
    if manifest['source']['resource']!=OFFICIAL_RESOURCE:raise TerrainError('unsupported official terrain resource')
    if not 1<=batch_size<=MAX_BATCH_POINTS:raise TerrainError('official batch size must be between 1 and 5000')
    points=grid_coordinates(region,manifest);macro=region['macro']
    signature=hashlib.sha256(json.dumps({'endpoint':OFFICIAL_API,'resource':OFFICIAL_RESOURCE,'points':points,'batchSize':batch_size},separators=(',',':')).encode()).hexdigest()
    checkpoint=output/'.official_resume'/f'{macro}-{signature}';checkpoint.mkdir(parents=True,exist_ok=True)
    values=[];batches=[];resumed=0
    for start in range(0,len(points),batch_size):
        selected=points[start:start+batch_size];body=json.dumps(official_payload(selected),separators=(',',':')).encode()
        request_sha=hashlib.sha256(body).hexdigest();path=checkpoint/f'{start:07d}.json';proof_path=path.with_suffix('.proof.json');raw=None;clean=None
        if path.exists() and proof_path.exists() and path.stat().st_size<=MAX_BYTES and proof_path.stat().st_size<=10_000:
            try:
                candidate=path.read_bytes();proof=json.loads(proof_path.read_text())
                if proof.get('requestSha256')!=request_sha or proof.get('responseSha256')!=hashlib.sha256(candidate).hexdigest():raise TerrainError('checkpoint checksum mismatch')
                clean=decode_official_batch(candidate,selected,manifest);raw=candidate;resumed+=1
            except (OSError,ValueError,TypeError,TerrainError):pass
        cached=raw is not None
        if raw is None:
            last=None
            for attempt in range(max(1,retries)):
                try:
                    OFFICIAL_RATE.wait()
                    request=Request(OFFICIAL_API,data=body,headers={'Content-Type':'application/json','Accept':'application/json','User-Agent':'Fallout-Mistral-Terrain-Installer/0.50'},method='POST')
                    with urlopen(request,timeout=timeout) as response:
                        if response.status!=200:raise TerrainError(f'official HTTP {response.status}')
                        candidate=decode_http_body(response.read(MAX_BYTES+1),response.headers.get('content-encoding'),MAX_BYTES)
                    clean=decode_official_batch(candidate,selected,manifest);raw=candidate
                    proof={'endpoint':OFFICIAL_API,'resource':OFFICIAL_RESOURCE,'start':start,'points':len(selected),'requestSha256':request_sha,'responseSha256':hashlib.sha256(raw).hexdigest(),'acquiredAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
                    atomic(path,raw);atomic_json(proof_path,proof);break
                except Exception as e:
                    last=e
                    if attempt+1<max(1,retries):time.sleep(min(6,1.7**attempt))
            if raw is None:raise TerrainError(f'official batch {start}/{len(points)} failed: {last!r}; validated batches retained for retry')
        values.extend(clean)
        batches.append({'start':start,'points':len(selected),'requestSha256':request_sha,'responseSha256':hashlib.sha256(raw).hexdigest(),'resumed':cached})
    payload={'version':'0.39.0','macro':macro,'bbox':region['bbox'],'width':manifest['grid']['width'],'height':manifest['grid']['height'],'rowOrder':'north-to-south','source':'RGE ALTI IGN','sourceResource':OFFICIAL_RESOURCE,'sourceTitle':manifest['source']['title'],'values':values,'generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'acquisition':'IGN official point-elevation POST API; measured grid nodes, without invented values','sourceEndpoint':OFFICIAL_API,'approximateSpacingMeters':{'x':round((region['bbox'][3]-region['bbox'][1])*111320*math.cos(math.radians((region['bbox'][0]+region['bbox'][2])/2))/(manifest['grid']['width']-1),2),'y':round((region['bbox'][2]-region['bbox'][0])*111320/(manifest['grid']['height']-1),2)}}
    canonical,meta=validate_bytes(json.dumps(payload,allow_nan=False).encode(),region,manifest)
    dest=output/f'{macro}.json';proof={**meta,'status':'downloaded','endpoint':'official','url':OFFICIAL_API,'sourceResource':OFFICIAL_RESOURCE,'batchCount':len(batches),'resumedBatches':resumed,'batches':batches,'verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    # Only the completed, validated grid replaces the installed terrain.
    atomic(dest,canonical);atomic_json(output/f'{macro}.proof.json',proof)
    shutil.rmtree(checkpoint,ignore_errors=True)
    return {**meta,'status':'downloaded','endpoint':'official','resumedBatches':resumed,'path':str(dest)}

def fetch_region(region,manifest,output,timeout,retries,offline=False,official_fallback=True,batch_size=MAX_BATCH_POINTS):
    macro=region['macro']
    if not isinstance(macro,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',macro):raise TerrainError('invalid macro identifier')
    dest=output/f'{macro}.json';report=output/f'{macro}.proof.json'
    if dest.exists():
        try:
            clean,meta=validate_bytes(dest.read_bytes(),region,manifest)
            if clean!=dest.read_bytes():atomic(dest,clean)
            try:old_proof=json.loads(report.read_text()) if report.exists() else {}
            except (OSError,ValueError):old_proof={}
            if not isinstance(old_proof,dict):old_proof={}
            atomic_json(report,{**old_proof,**meta,'status':'cached','verification':'local','endpoint':old_proof.get('endpoint','local'),'verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
            return {**meta,'status':'cached','path':str(dest)}
        except Exception:pass
    if offline:return {'macro':macro,'status':'error','error':'offline: required local terrain is missing or invalid; no network request made','path':str(dest)}
    url=f"{manifest['relay']}/terrain/{macro}.json";headers={'apikey':manifest['publicKey'],'Accept':'application/json','User-Agent':'Fallout-Mistral-Terrain-Installer/0.39'};last=None
    for attempt in range(retries):
        try:
            with urlopen(Request(url,headers=headers),timeout=timeout) as r:
                if getattr(r,'status',r.getcode())!=200:raise TerrainError(f'HTTP {getattr(r,"status",r.getcode())}')
                raw=decode_http_body(r.read(MAX_BYTES+1),r.headers.get('content-encoding'),MAX_BYTES)
            clean,meta=validate_bytes(raw,region,manifest);atomic(dest,clean);atomic_json(report,{**meta,'status':'downloaded','endpoint':'cloud','url':url,'verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
            return {**meta,'status':'downloaded','path':str(dest)}
        except Exception as e:
            last=e
            if attempt+1<retries:time.sleep(min(6,1.7**attempt))
    if official_fallback:
        try:
            result=fetch_official_region(region,manifest,output,timeout,retries,batch_size)
            proof=json.loads(report.read_text());proof['fallbackFrom']='configured historical relay';proof['relayError']=repr(last);atomic_json(report,proof)
            return result
        except Exception as e:return {'macro':macro,'status':'error','error':repr(e),'relayError':repr(last),'path':str(dest)}
    return {'macro':macro,'status':'error','error':repr(last),'path':str(dest)}

def verify_region(region,manifest,output):
    path=output/f"{region['macro']}.json"
    if not path.exists():return {'macro':region['macro'],'status':'missing','path':str(path)}
    try:
        clean,meta=validate_bytes(path.read_bytes(),region,manifest)
        if clean!=path.read_bytes():atomic(path,clean)
        return {**meta,'status':'verified','path':str(path)}
    except Exception as e:return {'macro':region['macro'],'status':'error','error':repr(e),'path':str(path)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,default=DEFAULT_MANIFEST);ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    ap.add_argument('--macro',default='all');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--timeout',type=int,default=60);ap.add_argument('--retries',type=int,default=4)
    ap.add_argument('--verify-only',action='store_true');ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--offline',action='store_true',help='Validate local terrain only; never contact a relay or IGN')
    ap.add_argument('--no-official-fallback',action='store_true',help='Do not query IGN if the configured historical relay fails')
    ap.add_argument('--batch-size',type=int,default=MAX_BATCH_POINTS,help='Number of measured points per official POST, maximum 5000')
    a=ap.parse_args()
    if not 1<=a.batch_size<=MAX_BATCH_POINTS:ap.error('--batch-size must be between 1 and 5000')
    if a.retries<1 or a.timeout<=0:ap.error('--retries and --timeout must be positive')
    manifest=json.loads(a.manifest.read_text(encoding='utf-8'));regions=manifest['regions']
    if a.macro!='all':
        wanted={x.strip() for x in a.macro.split(',') if x.strip()};regions=[r for r in regions if r['macro'] in wanted]
        unknown=wanted-{r['macro'] for r in regions}
        if unknown:raise SystemExit('Macro inconnue: '+', '.join(sorted(unknown)))
    print(f"Reliefs sélectionnés : {len(regions)} · grille {manifest['grid']['width']}×{manifest['grid']['height']}")
    if a.dry_run:return 0
    a.output.mkdir(parents=True,exist_ok=True);started=time.time()
    if a.verify_only:results=[verify_region(r,manifest,a.output) for r in regions]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,8))) as ex:results=list(ex.map(lambda r:fetch_region(r,manifest,a.output,a.timeout,a.retries,a.offline,not a.no_official_fallback,a.batch_size),regions))
    errors=sum(r['status'] in ('error','missing') for r in results);valid=sum(r.get('valid',0) for r in results);missing=sum(r.get('missing',0) for r in results);total_bytes=sum(r.get('bytes',0) for r in results)
    report={'version':'0.39.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'selected':len(regions),'ok':len(regions)-errors,'errors':errors,'validPoints':valid,'missingPoints':missing,'bytes':total_bytes,'seconds':round(time.time()-started,2),'regions':sorted(results,key=lambda x:x['macro'])}
    atomic_json(a.output/'install_terrain_v039_report.json',report)
    print(json.dumps({k:report[k] for k in ('selected','ok','errors','validPoints','missingPoints','bytes')},ensure_ascii=False,indent=2))
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
