#!/usr/bin/env python3
"""Install or verify the eight official RGE ALTI sampled grids for Fallout: Mistral v0.39.

Source order is intentionally explicit: the private v0.39 cloud cache is used by
this installer. Every JSON file is decoded, sanitised and written atomically.
NoData stays null; the tool never interpolates or fabricates an official height.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, math, os, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=ROOT/'data/map_pack/terrain/manifest_v039.json'
DEFAULT_OUTPUT=ROOT/'data/map_pack/terrain'
MAX_BYTES=6_000_000

class TerrainError(RuntimeError): pass

def atomic(path:Path,data:bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.part')
    tmp.write_bytes(data)
    os.replace(tmp,path)

def atomic_json(path:Path,obj):
    atomic(path,(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())

def sanitise(value,lo=-100,hi=9000):
    if value is None:return None
    try:z=float(value)
    except (TypeError,ValueError):return None
    return round(z,2) if math.isfinite(z) and z>lo and z<hi else None

def validate_bytes(raw:bytes,region:dict,manifest:dict):
    if not raw:raise TerrainError('empty terrain JSON')
    if len(raw)>MAX_BYTES:raise TerrainError(f'terrain exceeds {MAX_BYTES} bytes')
    try:j=json.loads(raw)
    except Exception as e:raise TerrainError(f'invalid JSON: {e}') from e
    grid=manifest['grid'];w=int(j.get('width',0));h=int(j.get('height',0));macro=region['macro']
    if j.get('macro')!=macro:raise TerrainError(f'macro mismatch {j.get("macro")} != {macro}')
    if (w,h)!=(int(grid['width']),int(grid['height'])):raise TerrainError(f'grid mismatch {w}x{h}')
    vals=j.get('values')
    if not isinstance(vals,list) or len(vals)!=w*h:raise TerrainError(f'value count {len(vals) if isinstance(vals,list) else 0}/{w*h}')
    resource=j.get('sourceResource') or j.get('source_resource') or j.get('resource')
    if resource and resource!=manifest['source']['resource']:raise TerrainError(f'unexpected resource {resource}')
    bbox=j.get('bbox') or j.get('bboxWGS84')
    if not isinstance(bbox,list) or len(bbox)!=4 or any(not isinstance(x,(int,float)) for x in bbox):raise TerrainError('invalid bbox')
    if max(abs(float(bbox[i])-float(region['bbox'][i])) for i in range(4))>1e-6:raise TerrainError('bbox differs from manifest')
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
    canonical=(json.dumps(j,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    return canonical,{'macro':macro,'width':w,'height':h,'valid':len(valid),'missing':len(clean)-len(valid),'min':min(valid),'max':max(valid),'mean':sum(valid)/len(valid),'sanitised':changed,'bytes':len(canonical),'sha256':hashlib.sha256(canonical).hexdigest(),'coverage':len(valid)/len(clean)}

def fetch_region(region,manifest,output,timeout,retries):
    macro=region['macro'];dest=output/f'{macro}.json';report=output/f'{macro}.proof.json'
    if dest.exists():
        try:
            clean,meta=validate_bytes(dest.read_bytes(),region,manifest)
            if clean!=dest.read_bytes():atomic(dest,clean)
            atomic_json(report,{**meta,'status':'cached','endpoint':'local','verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
            return {**meta,'status':'cached','path':str(dest)}
        except Exception:
            dest.unlink(missing_ok=True);report.unlink(missing_ok=True)
    url=f"{manifest['relay']}/terrain/{macro}.json";headers={'apikey':manifest['publicKey'],'Accept':'application/json','User-Agent':'Fallout-Mistral-Terrain-Installer/0.39'};last=None
    for attempt in range(retries):
        try:
            with urlopen(Request(url,headers=headers),timeout=timeout) as r:
                if getattr(r,'status',r.getcode())!=200:raise TerrainError(f'HTTP {getattr(r,"status",r.getcode())}')
                raw=r.read(MAX_BYTES+1)
            clean,meta=validate_bytes(raw,region,manifest);atomic(dest,clean);atomic_json(report,{**meta,'status':'downloaded','endpoint':'cloud','url':url,'verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
            return {**meta,'status':'downloaded','path':str(dest)}
        except Exception as e:
            last=e;time.sleep(min(6,1.7**attempt))
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
    a=ap.parse_args();manifest=json.loads(a.manifest.read_text(encoding='utf-8'));regions=manifest['regions']
    if a.macro!='all':
        wanted={x.strip() for x in a.macro.split(',') if x.strip()};regions=[r for r in regions if r['macro'] in wanted]
        unknown=wanted-{r['macro'] for r in regions}
        if unknown:raise SystemExit('Macro inconnue: '+', '.join(sorted(unknown)))
    print(f"Reliefs sélectionnés : {len(regions)} · grille {manifest['grid']['width']}×{manifest['grid']['height']}")
    if a.dry_run:return 0
    a.output.mkdir(parents=True,exist_ok=True);started=time.time()
    if a.verify_only:results=[verify_region(r,manifest,a.output) for r in regions]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,8))) as ex:results=list(ex.map(lambda r:fetch_region(r,manifest,a.output,a.timeout,a.retries),regions))
    errors=sum(r['status'] in ('error','missing') for r in results);valid=sum(r.get('valid',0) for r in results);missing=sum(r.get('missing',0) for r in results);total_bytes=sum(r.get('bytes',0) for r in results)
    report={'version':'0.39.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'selected':len(regions),'ok':len(regions)-errors,'errors':errors,'validPoints':valid,'missingPoints':missing,'bytes':total_bytes,'seconds':round(time.time()-started,2),'regions':sorted(results,key=lambda x:x['macro'])}
    atomic_json(a.output/'install_terrain_v039_report.json',report)
    print(json.dumps({k:report[k] for k in ('selected','ok','errors','validPoints','missingPoints','bytes')},ensure_ascii=False,indent=2))
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
