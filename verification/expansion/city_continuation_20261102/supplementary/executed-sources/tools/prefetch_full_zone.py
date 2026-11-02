#!/usr/bin/env python3
"""Télécharge le pack vectoriel complet de Fallout: Mistral v0.17.

Sources publiques :
- france-vector (OpenMapTiles / OpenStreetMap)
- cadastre (Etalab / DINUM)

Le script est reprenable et vérifie chaque réponse avant de l'écrire. Il ne modifie
pas le jeu et peut être relancé autant de fois que nécessaire.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, math, os, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

MACROS = {
    "geo_marseille": [43.2200,5.2850,43.3400,5.5100],
    "geo_huveaune": [43.2450,5.4300,43.3350,5.6400],
    "geo_garlaban": [43.2450,5.4850,43.3900,5.6900],
    "geo_calanques": [43.1450,5.3300,43.2850,5.6500],
    "geo_laciotat": [43.1250,5.5400,43.2550,5.7350],
    "geo_frioul": [43.2450,5.2550,43.3150,5.3500],
    "geo_etoile": [43.3000,5.4350,43.4200,5.6000],
    "geo_saintebaume": [43.2150,5.5650,43.4100,5.7550],
}
SOURCES = {
    "france-vector": {"z": 14, "url": "https://openmaptiles.data.gouv.fr/data/france-vector/{z}/{x}/{y}.pbf"},
    "cadastre": {"z": 16, "url": "https://openmaptiles.data.gouv.fr/data/cadastre/{z}/{x}/{y}.pbf"},
}

def lonlat_tile(lat: float, lon: float, z: int) -> tuple[int,int]:
    n=2**z
    x=int((lon+180.0)/360.0*n)
    y=int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
    return x,y

def bbox_tiles(bbox: list[float], z: int) -> set[tuple[int,int]]:
    south,west,north,east=bbox
    x0,ys=lonlat_tile(south,west,z); x1,yn=lonlat_tile(north,east,z)
    return {(x,y) for x in range(min(x0,x1),max(x0,x1)+1) for y in range(min(yn,ys),max(yn,ys)+1)}

def plan() -> dict[str,list[tuple[int,int,int]]]:
    out={}
    for name,src in SOURCES.items():
        tiles=set()
        for bbox in MACROS.values(): tiles |= bbox_tiles(bbox,src["z"])
        out[name]=[(src["z"],x,y) for x,y in sorted(tiles)]
    return out

def valid_pbf(data: bytes) -> bool:
    if len(data)<8: return False
    head=data[:64].lstrip().lower()
    return not (head.startswith(b"<html") or head.startswith(b"<!doctype") or head.startswith(b"{"))

def fetch_one(root:Path, source:str, z:int, x:int, y:int, retries:int=4) -> dict:
    dest=root/source/str(z)/str(x)/f"{y}.pbf"
    if dest.exists() and dest.stat().st_size>8:
        data=dest.read_bytes()
        if valid_pbf(data): return {"source":source,"z":z,"x":x,"y":y,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"status":"cached"}
    url=SOURCES[source]["url"].format(z=z,x=x,y=y)
    last=None
    for attempt in range(retries):
        try:
            req=Request(url,headers={"User-Agent":"Fallout-Mistral-Map-Pack/0.17 (+non-commercial fan prototype)"})
            with urlopen(req,timeout=35) as r: data=r.read()
            if not valid_pbf(data): raise RuntimeError("réponse non PBF")
            dest.parent.mkdir(parents=True,exist_ok=True)
            tmp=dest.with_suffix('.part'); tmp.write_bytes(data); tmp.replace(dest)
            return {"source":source,"z":z,"x":x,"y":y,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),"status":"downloaded"}
        except Exception as exc:
            last=exc; time.sleep(min(8,1.5**attempt))
    return {"source":source,"z":z,"x":x,"y":y,"bytes":0,"sha256":"","status":"error","error":repr(last)}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'data'/'map_pack')
    ap.add_argument('--workers',type=int,default=8)
    ap.add_argument('--source',choices=['all',*SOURCES],default='all')
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--limit',type=int,default=0,help='limite de test; 0 = tout')
    args=ap.parse_args(); p=plan(); selected=list(SOURCES) if args.source=='all' else [args.source]
    jobs=[(s,*t) for s in selected for t in p[s]]
    if args.limit: jobs=jobs[:args.limit]
    summary={"version":"0.17.0","generated":time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),"macros":MACROS,"sources":SOURCES,"counts":{s:len(p[s]) for s in SOURCES},"total":sum(len(p[s]) for s in SOURCES),"selected":len(jobs),"files":[]}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'plan.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Plan complet : {summary['counts']} · total {summary['total']} tuiles")
    if args.dry_run: return 0
    done=errors=bytes_total=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.workers)) as ex:
        futs=[ex.submit(fetch_one,args.output,*j) for j in jobs]
        for fut in concurrent.futures.as_completed(futs):
            row=fut.result(); summary['files'].append(row); done+=1; bytes_total+=row.get('bytes',0)
            if row['status']=='error': errors+=1
            if done%50==0 or done==len(jobs): print(f"{done}/{len(jobs)} · erreurs {errors} · {bytes_total/1024/1024:.1f} Mio",flush=True)
    summary['downloaded_bytes']=bytes_total; summary['errors']=errors
    (args.output/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Pack terminé :',args.output)
    return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
