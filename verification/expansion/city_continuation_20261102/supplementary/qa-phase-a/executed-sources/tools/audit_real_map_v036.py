#!/usr/bin/env python3
"""Audit the installed Fallout: Mistral v0.36 real vector pack.

The audit is conservative: planned tiles are never counted as installed. It validates
all present PBFs, reports missing/invalid files, counts layers/features and checks
cross-tile line endpoints for obvious road/rail discontinuities. It is dependency free.
"""
from __future__ import annotations
import argparse, collections, hashlib, html, json, math, time
from pathlib import Path
from mvt_audit_v036 import parse_tile, decode_geometry, attributes

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data'/'map_pack'/'manifest_v036.json'
ROAD_HINTS=('transportation','road','roads','transport','highway','rail','railway','path')
BUILDING_HINTS=('building','buildings','batiment','bâtiment')
WATER_HINTS=('water','waterway','hydro','ocean')
LAND_HINTS=('landuse','landcover','park','wood','forest','vegetation')

def layer_group(name:str)->str:
 n=name.lower()
 if any(h in n for h in ROAD_HINTS):return 'transport'
 if any(h in n for h in BUILDING_HINTS):return 'building'
 if any(h in n for h in WATER_HINTS):return 'water'
 if any(h in n for h in LAND_HINTS):return 'land'
 return 'other'

def edge_key(z:int,x:int,y:int,extent:int,p:tuple[int,int],tol=3):
 px,py=p
 if px<=tol:return ('v',z,x,round((y+py/extent)*extent))
 if px>=extent-tol:return ('v',z,x+1,round((y+py/extent)*extent))
 if py<=tol:return ('h',z,y,round((x+px/extent)*extent))
 if py>=extent-tol:return ('h',z,y+1,round((x+px/extent)*extent))
 return None

def audit(args):
 manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
 rows=manifest['tiles']
 if args.source!='all':rows=[r for r in rows if r['source']==args.source]
 if args.macro!='all':rows=[r for r in rows if args.macro in r['macros']]
 expected=len(rows);present=valid=invalid=0;bytes_total=features_total=0
 layers=collections.Counter();groups=collections.Counter();feature_types=collections.Counter();
 endpoint_hits=collections.Counter();endpoint_examples={};files=[];missing=[];bad=[]
 for index,row in enumerate(rows,1):
  path=args.pack/row['local'].replace('data/map_pack/','')
  if not path.exists():missing.append(row['key']);continue
  present+=1
  try:
   data=path.read_bytes();tile=parse_tile(data);valid+=1;bytes_total+=len(data)
   file_features=0
   for name,layer in tile.items():
    layers[name]+=len(layer.features);g=layer_group(name);groups[g]+=len(layer.features)
    for f in layer.features:
     file_features+=1;features_total+=1;feature_types[str(f.geom_type)]+=1
     if g=='transport' and f.geom_type==2:
      for path_geom in decode_geometry(f):
       if len(path_geom)<2:continue
       for p in (path_geom[0],path_geom[-1]):
        key=edge_key(row['z'],row['x'],row['y'],layer.extent,p)
        if key:
         endpoint_hits[key]+=1;endpoint_examples.setdefault(key,{'tile':row['key'],'layer':name,'point':p})
   files.append({'source':row['source'],'key':row['key'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'layers':len(tile),'features':file_features})
  except Exception as e:
   invalid+=1;bad.append({'source':row['source'],'key':row['key'],'file':str(path),'error':repr(e)})
  if args.limit and index>=args.limit:break
 unmatched=[]
 for key,count in endpoint_hits.items():
  if count==1:unmatched.append({**endpoint_examples[key],'edge':key})
 report={
  'version':'0.36.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
  'selection':{'source':args.source,'macro':args.macro},
  'expected':expected,'present':present,'valid':valid,'invalid':invalid,'missing':expected-present,
  'coveragePercent':round(valid/expected*100,4) if expected else 100,
  'bytes':bytes_total,'features':features_total,'groups':dict(groups),'layers':dict(layers),
  'geometryTypes':dict(feature_types),'edgeEndpoints':len(endpoint_hits),'unmatchedTransportEdgeEndpoints':len(unmatched),
  'unmatchedExamples':unmatched[:200],'missingExamples':missing[:200],'invalidFiles':bad,'files':files,
  'truth':{
    'complete':valid==expected and invalid==0,
    'terrainNumericAudited':False,
    'note':'A complete vector audit does not certify official numeric terrain, visual fidelity or every semantic road connection.'
  }
 }
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 html_out=args.output.with_suffix('.html')
 cards=[('Tuiles valides',f"{valid} / {expected}"),('Couverture',f"{report['coveragePercent']:.2f} %"),('Entités',f"{features_total:,}".replace(',',' ')),('Extrémités transport non appariées',str(len(unmatched)))]
 html_out.write_text(f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Audit cartographique v0.36</title><style>body{{background:#101712;color:#dde7d3;font:15px/1.55 system-ui;margin:0}}main{{max-width:1100px;margin:auto;padding:32px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}article{{border:1px solid #475d48;background:#18231a;padding:18px}}b{{font-size:25px;color:#e8dca3}}table{{border-collapse:collapse;width:100%;margin-top:25px}}td,th{{padding:8px;border-bottom:1px solid #394b3b;text-align:left}}code{{color:#e6d49d}}</style><main><h1>Fallout : Mistral — Audit vectoriel v0.36</h1><p>Sélection : <code>{html.escape(args.source)}</code> / <code>{html.escape(args.macro)}</code>. Les fichiers absents ne sont jamais comptés comme intégrés.</p><div class="grid">{''.join(f'<article><small>{a}</small><br><b>{b}</b></article>' for a,b in cards)}</div><h2>Groupes de couches</h2><table><tr><th>Groupe</th><th>Entités</th></tr>{''.join(f'<tr><td>{html.escape(k)}</td><td>{v}</td></tr>' for k,v in sorted(groups.items()))}</table><h2>Conclusion</h2><p>{'Pack vectoriel complet pour cette sélection.' if report['truth']['complete'] else 'Pack incomplet : utilisez install_real_map_v036.py puis relancez cet audit.'}</p><p>Le relief numérique officiel reste un chantier distinct et n’est pas certifié par ce rapport.</p></main></html>''',encoding='utf-8')
 print(json.dumps({k:report[k] for k in ['expected','present','valid','invalid','missing','coveragePercent','features','unmatchedTransportEdgeEndpoints']},ensure_ascii=False,indent=2))
 return 0 if report['truth']['complete'] else 2

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=MANIFEST);p.add_argument('--pack',type=Path,default=ROOT/'data'/'map_pack')
 p.add_argument('--source',choices=['all','base','cadastre'],default='all');p.add_argument('--macro',choices=['all','geo_marseille','geo_huveaune','geo_garlaban','geo_calanques','geo_laciotat','geo_frioul','geo_etoile','geo_saintebaume'],default='all')
 p.add_argument('--output',type=Path,default=ROOT/'verification'/'AUDIT_CARTE_REELLE_V036.json');p.add_argument('--limit',type=int,default=0)
 a=p.parse_args();raise SystemExit(audit(a))
if __name__=='__main__':main()
