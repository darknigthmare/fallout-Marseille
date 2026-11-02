#!/usr/bin/env python3
"""Audit locally installed Fallout: Mistral v0.39 RGE ALTI grids.

The audit validates provenance, grid dimensions, NoData preservation, checksums and
statistics. It also compares overlapping macro-regions at shared WGS84 points. An
overlap difference is a diagnostic, not automatic proof that either official sample
is wrong; grids are sampled independently from the same service.
"""
from __future__ import annotations
import argparse, hashlib, html, json, math, statistics, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=ROOT/'data/map_pack/terrain/manifest_v039.json'
DEFAULT_PACK=ROOT/'data/map_pack/terrain'
DEFAULT_OUTPUT=ROOT/'verification/AUDIT_TERRAIN_V039.json'

def sanitise(v,lo=-100,hi=9000):
    if v is None:return None
    try:z=float(v)
    except (TypeError,ValueError):return None
    return z if math.isfinite(z) and z>lo and z<hi else None

def validate(path:Path,region:dict,manifest:dict):
    raw=path.read_bytes();j=json.loads(raw);w=int(j.get('width',0));h=int(j.get('height',0));vals=j.get('values')
    if j.get('macro')!=region['macro']:raise ValueError('macro mismatch')
    if (w,h)!=(manifest['grid']['width'],manifest['grid']['height']):raise ValueError(f'grid {w}x{h}')
    if not isinstance(vals,list) or len(vals)!=w*h:raise ValueError('value count')
    bbox=j.get('bbox') or j.get('bboxWGS84')
    if not isinstance(bbox,list) or len(bbox)!=4:raise ValueError('bbox')
    if max(abs(float(bbox[i])-float(region['bbox'][i])) for i in range(4))>1e-6:raise ValueError('bbox mismatch')
    res=j.get('sourceResource') or j.get('source_resource') or j.get('resource')
    if res and res!=manifest['source']['resource']:raise ValueError('source resource')
    lo=manifest['noData']['minimumExclusive'];hi=manifest['noData']['maximumExclusive'];clean=[sanitise(v,lo,hi) for v in vals];valid=[v for v in clean if v is not None]
    if not valid:raise ValueError('no valid values')
    return {'macro':region['macro'],'path':str(path),'raw':j,'values':clean,'bbox':list(map(float,bbox)),'width':w,'height':h,'valid':len(valid),'missing':len(clean)-len(valid),'min':min(valid),'max':max(valid),'mean':sum(valid)/len(valid),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'coverage':len(valid)/len(clean)}

def sample(grid,lat,lon):
    south,west,north,east=grid['bbox']
    if lat<south or lat>north or lon<west or lon>east:return None
    u=(lon-west)/(east-west);v=(north-lat)/(north-south);gx=max(0,min(grid['width']-1,u*(grid['width']-1)));gy=max(0,min(grid['height']-1,v*(grid['height']-1)))
    x0=int(math.floor(gx));y0=int(math.floor(gy));x1=min(grid['width']-1,x0+1);y1=min(grid['height']-1,y0+1);tx=gx-x0;ty=gy-y0
    corners=[(x0,y0,(1-tx)*(1-ty)),(x1,y0,tx*(1-ty)),(x0,y1,(1-tx)*ty),(x1,y1,tx*ty)];num=den=0.0
    for x,y,w in corners:
        z=grid['values'][y*grid['width']+x]
        if z is None or w<=0:continue
        num+=z*w;den+=w
    return num/den if den>0 else None

def overlaps(grids,steps=9):
    out=[];ids=sorted(grids)
    for ai,a in enumerate(ids):
        for b in ids[ai+1:]:
            ga,gb=grids[a],grids[b];sa,wa,na,ea=ga['bbox'];sb,wb,nb,eb=gb['bbox'];s=max(sa,sb);w=max(wa,wb);n=min(na,nb);e=min(ea,eb)
            if s>=n or w>=e:continue
            diffs=[];samples=missing=0
            for iy in range(steps):
                lat=s+(n-s)*(iy+.5)/steps
                for ix in range(steps):
                    lon=w+(e-w)*(ix+.5)/steps;za=sample(ga,lat,lon);zb=sample(gb,lat,lon)
                    if za is None or zb is None:missing+=1;continue
                    samples+=1;diffs.append(abs(za-zb))
            out.append({'a':a,'b':b,'bbox':[s,w,n,e],'samples':samples,'noDataPairs':missing,'meanAbsoluteDelta':round(sum(diffs)/len(diffs),3) if diffs else None,'medianAbsoluteDelta':round(statistics.median(diffs),3) if diffs else None,'maxAbsoluteDelta':round(max(diffs),3) if diffs else None,'above5m':sum(d>5 for d in diffs),'above15m':sum(d>15 for d in diffs)})
    return out

def make_html(report,path):
    cards=[('Grilles valides',f"{report['validRegions']} / {report['expectedRegions']}"),('Mesures valides',f"{report['validPoints']:,}".replace(',',' ')),('Cellules NoData',f"{report['missingPoints']:,}".replace(',',' ')),('Fichiers absents',str(report['missingRegions'])),('Fichiers invalides',str(report['invalidRegions'])),('Recouvrements',str(len(report['overlaps'])))]
    rows=''.join(f"<tr><td>{html.escape(x['a'])}</td><td>{html.escape(x['b'])}</td><td>{x['samples']}</td><td>{x['meanAbsoluteDelta'] if x['meanAbsoluteDelta'] is not None else '—'}</td><td>{x['maxAbsoluteDelta'] if x['maxAbsoluteDelta'] is not None else '—'}</td></tr>" for x in report['overlaps'])
    path.write_text(f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Audit relief v0.39</title><style>body{{background:#101712;color:#dce8d5;font:15px/1.55 system-ui;margin:0}}main{{max-width:1100px;margin:auto;padding:32px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}article{{background:#18231a;border:1px solid #465c49;padding:18px}}b{{font-size:25px;color:#e8dca3}}table{{width:100%;border-collapse:collapse;margin-top:20px}}td,th{{border:1px solid #425344;padding:8px;text-align:left}}</style><main><h1>Fallout : Mistral — Audit RGE ALTI v0.39</h1><p>Les cellules NoData restent absentes. Les écarts de recouvrement sont des diagnostics entre échantillonnages, pas des corrections automatiques.</p><div class="grid">{''.join(f'<article><small>{k}</small><br><b>{v}</b></article>' for k,v in cards)}</div><h2>Recouvrements</h2><table><tr><th>Région A</th><th>Région B</th><th>Échantillons</th><th>Δ moyen m</th><th>Δ max m</th></tr>{rows}</table><h2>Conclusion</h2><p>{'Pack local terrain complet et valide.' if report['complete'] else 'Pack local terrain absent, incomplet ou invalide.'}</p></main></html>''',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=DEFAULT_MANIFEST);ap.add_argument('--pack',type=Path,default=DEFAULT_PACK);ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);ap.add_argument('--macro',default='all');ap.add_argument('--overlap-steps',type=int,default=9);a=ap.parse_args()
    manifest=json.loads(a.manifest.read_text(encoding='utf-8'));regions=manifest['regions']
    if a.macro!='all':
        wanted={x.strip() for x in a.macro.split(',') if x.strip()};regions=[r for r in regions if r['macro'] in wanted]
    grids={};missing=[];invalid=[];files=[]
    for r in regions:
        path=a.pack/f"{r['macro']}.json"
        if not path.exists():missing.append(r['macro']);continue
        try:g=validate(path,r,manifest);grids[r['macro']]=g;files.append({k:v for k,v in g.items() if k not in ('raw','values')})
        except Exception as e:invalid.append({'macro':r['macro'],'path':str(path),'error':repr(e)})
    ovs=overlaps(grids,max(2,min(31,a.overlap_steps)))
    report={'version':'0.39.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':manifest['source'],'expectedRegions':len(regions),'validRegions':len(grids),'missingRegions':len(missing),'invalidRegions':len(invalid),'validPoints':sum(g['valid'] for g in grids.values()),'missingPoints':sum(g['missing'] for g in grids.values()),'bytes':sum(g['bytes'] for g in grids.values()),'complete':len(grids)==len(regions) and not invalid,'missing':missing,'invalid':invalid,'overlaps':ovs,'files':files,'truth':{'officialSource':'ign_rge_alti_wld','nativeResolutionClaimed':False,'syntheticHeightsInserted':False,'note':'This audit validates the sampled grids installed locally. It does not certify every native RGE ALTI cell or every road/building alignment.'}}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');make_html(report,a.output.with_suffix('.html'));print(json.dumps({k:report[k] for k in ('expectedRegions','validRegions','missingRegions','invalidRegions','validPoints','missingPoints','bytes','complete')},ensure_ascii=False,indent=2));return 0 if report['complete'] else 2
if __name__=='__main__':raise SystemExit(main())
