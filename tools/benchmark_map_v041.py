#!/usr/bin/env python3
"""Benchmark an installed v0.41 vector/terrain pack and corridor working sets."""
from __future__ import annotations
import argparse, concurrent.futures, json, os, statistics, time, sys
try:
    import resource
except ImportError:
    resource=None
from pathlib import Path
from mvt_audit_v036 import parse_tile
ROOT=Path(__file__).resolve().parents[1]

def decode(path:Path):
    t=time.perf_counter();raw=path.read_bytes();tile=parse_tile(raw);return {'path':str(path),'bytes':len(raw),'layers':len(tile),'features':sum(len(x.features) for x in tile.values()),'ms':(time.perf_counter()-t)*1000}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT/'data/map_pack');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--sample',type=int,default=0);a=ap.parse_args()
    pbf=sorted([p for d in ('france-vector','cadastre') for p in (a.root/d).rglob('*.pbf') if p.stat().st_size]);empty=sum(1 for d in ('france-vector','cadastre') for p in (a.root/d).rglob('*.pbf') if not p.stat().st_size)
    if a.sample and len(pbf)>a.sample:pbf=pbf[::max(1,len(pbf)//a.sample)][:a.sample]
    started=time.perf_counter();rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,16))) as ex:
        for r in ex.map(decode,pbf):rows.append(r)
    seconds=time.perf_counter()-started;ms=[r['ms'] for r in rows];total=sum(r['bytes'] for r in rows);features=sum(r['features'] for r in rows)
    terrain=[];terrain_started=time.perf_counter()
    for p in sorted((a.root/'terrain').glob('geo_*.json')):
        t=time.perf_counter();j=json.loads(p.read_text());terrain.append({'macro':j.get('macro'),'bytes':p.stat().st_size,'cells':len(j.get('values') or []),'valid':j.get('validPoints'),'missing':j.get('missingPoints'),'ms':(time.perf_counter()-t)*1000})
    corridors={}
    for p in sorted((ROOT/'data/corridors').glob('*.json')):
        j=json.loads(p.read_text());tiles={'base':0,'cadastre':0,'missing':0,'bytes':0}
        # Proof files carry counts; local-presence certification is completed by the full vector audit.
        corridors[j['id']]={'distanceM':j.get('distanceM'),'pathPoints':len(j.get('path') or []),'tileCount':j.get('tileCount'),'macros':j.get('macroSequence')}
    rss=(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None)
    if rss is not None and sys.platform=="darwin":rss/=1024
    report={'version':'0.41.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sampledPbf':len(rows),'officialEmpty':empty,'decodedBytes':total,'features':features,'seconds':round(seconds,3),'throughputMiBps':round(total/1048576/max(seconds,.001),2),'tilesPerSecond':round(len(rows)/max(seconds,.001),2),'decodeMs':{'mean':round(statistics.mean(ms),3) if ms else 0,'median':round(statistics.median(ms),3) if ms else 0,'p95':round(sorted(ms)[max(0,int(len(ms)*.95)-1)],3) if ms else 0,'max':round(max(ms),3) if ms else 0},'terrain':terrain,'terrainParseSeconds':round(time.perf_counter()-terrain_started,3),'corridors':corridors,'peakRssKiB':rss,'completePack':len(rows)==4557 and empty==1327 and len(terrain)==8}
    out=a.root/'benchmark_v041.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
