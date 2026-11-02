#!/usr/bin/env python3
"""Conservative audit of the installed Fallout: Mistral v0.38 vector pack.

Missing files are distinct from topology errors. A transport endpoint is called
'unpaired' only when the neighboring tile is present and valid. Buildings touching a
tile edge are listed for later merge/control; exact duplicate footprints are counted.
"""
from __future__ import annotations
import argparse, collections, hashlib, html, json, math, time
from pathlib import Path
from mvt_audit_v036 import parse_tile,decode_geometry
ROOT=Path(__file__).resolve().parents[1];MANIFEST=ROOT/'data/map_pack/manifest_v038.json'
ROAD_HINTS=('transportation','road','roads','transport','highway','rail','railway','path','waterway')
BUILDING_HINTS=('building','buildings','batiment','bâtiment')
WATER_HINTS=('water','hydro','ocean');LAND_HINTS=('landuse','landcover','park','wood','forest','vegetation')
def group(name):
 n=name.lower()
 if any(x in n for x in BUILDING_HINTS):return'building'
 if any(x in n for x in ROAD_HINTS):return'transport'
 if any(x in n for x in WATER_HINTS):return'water'
 if any(x in n for x in LAND_HINTS):return'land'
 return'other'
def endpoint(z,x,y,extent,p,tol=3):
 px,py=p
 if px<=tol:return('v',z,x,round((y+py/extent)*extent)),(z,x-1,y)
 if px>=extent-tol:return('v',z,x+1,round((y+py/extent)*extent)),(z,x+1,y)
 if py<=tol:return('h',z,y,round((x+px/extent)*extent)),(z,x,y-1)
 if py>=extent-tol:return('h',z,y+1,round((x+px/extent)*extent)),(z,x,y+1)
 return None,None
def canonical(z,x,y,extent,ring):
 pts=[]
 for px,py in ring:
  gx=round((x+px/extent)*1_000_000);gy=round((y+py/extent)*1_000_000);pts.append((gx,gy))
 if len(pts)>1 and pts[0]==pts[-1]:pts.pop()
 if not pts:return''
 variants=[]
 for seq in (pts,list(reversed(pts))):
  m=min(range(len(seq)),key=lambda i:seq[i]);rot=seq[m:]+seq[:m];variants.append(';'.join(f'{a},{b}' for a,b in rot))
 return min(variants)
def audit(a):
 manifest=json.loads(a.manifest.read_text());rows=manifest['tiles']
 if a.source!='all':rows=[r for r in rows if r['source']==a.source]
 if a.macro!='all':rows=[r for r in rows if a.macro in r['macros']]
 if a.limit:rows=rows[:a.limit]
 expected=len(rows);present=valid=invalid=empty_tiles=bytes_total=features=0;layers=collections.Counter();groups=collections.Counter();valid_tiles=set();endpoints=[];building_signatures=collections.Counter();split_buildings=[];files=[];missing=[];bad=[]
 for i,row in enumerate(rows,1):
  path=a.pack/row['local'].replace('data/map_pack/','')
  if not path.exists():missing.append(row['key']);continue
  present+=1
  try:
   raw=path.read_bytes();empty_marker=path.with_suffix(path.suffix+'.empty.json')
   if not raw:
    if not empty_marker.exists():raise RuntimeError('zero-byte file without official-empty marker')
    proof=json.loads(empty_marker.read_text(encoding='utf-8'))
    if proof.get('officialEmpty') is not True:raise RuntimeError('invalid official-empty marker')
    valid+=1;empty_tiles+=1;valid_tiles.add((row['source'],row['z'],row['x'],row['y']));files.append({'key':row['key'],'source':row['source'],'bytes':0,'sha256':hashlib.sha256(b'').hexdigest(),'layers':0,'features':0,'empty':True});continue
   tile=parse_tile(raw);valid+=1;valid_tiles.add((row['source'],row['z'],row['x'],row['y']));bytes_total+=len(raw);fc=0
   for name,layer in tile.items():
    g=group(name);layers[name]+=len(layer.features);groups[g]+=len(layer.features)
    for f in layer.features:
     fc+=1;features+=1
     paths=decode_geometry(f)
     if g=='transport' and f.geom_type==2:
      for line in paths:
       if len(line)<2:continue
       for pt in (line[0],line[-1]):
        edge,neighbor=endpoint(row['z'],row['x'],row['y'],layer.extent,pt)
        if edge:endpoints.append({'source':row['source'],'tile':(row['z'],row['x'],row['y']),'neighbor':neighbor,'edge':edge,'layer':name,'point':pt})
     if g=='building' and f.geom_type==3:
      for ring in paths:
       if len(ring)<4:continue
       sig=canonical(row['z'],row['x'],row['y'],layer.extent,ring);building_signatures[sig]+=1
       if any(px<=3 or px>=layer.extent-3 or py<=3 or py>=layer.extent-3 for px,py in ring):split_buildings.append({'tile':row['key'],'layer':name,'feature':f.fid})
   files.append({'key':row['key'],'source':row['source'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'layers':len(tile),'features':fc})
  except Exception as e:invalid+=1;bad.append({'key':row['key'],'file':str(path),'error':repr(e)})
 # endpoint classification. Matching edge key from a distinct tile means continuous.
 by_edge=collections.defaultdict(list)
 for ep in endpoints:by_edge[tuple(ep['edge'])].append(ep)
 matched_pairs=set();pending=[];unpaired=[]
 for ep in endpoints:
  neighbor_key=(ep['source'],*ep['neighbor'])
  if neighbor_key not in valid_tiles:pending.append(ep);continue
  matches=[x for x in by_edge[tuple(ep['edge'])] if x['tile']!=ep['tile']]
  if matches:
   other=matches[0];matched_pairs.add(tuple(sorted([ep['tile'],other['tile']]))+(tuple(ep['edge']),))
  else:unpaired.append(ep)
 duplicates=sum(n-1 for n in building_signatures.values() if n>1)
 report={'version':'0.38.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'selection':{'source':a.source,'macro':a.macro},'expected':expected,'present':present,'valid':valid,'invalid':invalid,'missing':expected-present,'coveragePercent':round(valid/expected*100,4) if expected else 100,'bytes':bytes_total,'officialEmptyTiles':empty_tiles,'features':features,'groups':dict(groups),'layers':dict(layers),'transportTopology':{'edgeEndpoints':len(endpoints),'matchedSeams':len(matched_pairs),'pendingNeighborTiles':len(pending),'unpairedWithNeighborLoaded':len(unpaired),'unpairedExamples':unpaired[:200]},'buildings':{'exactDuplicateFootprints':duplicates,'edgeTouchingFootprints':len(split_buildings),'edgeExamples':split_buildings[:200]},'missingExamples':missing[:200],'invalidFiles':bad,'files':files,'truth':{'complete':valid==expected and invalid==0 and not unpaired,'vectorFilesComplete':valid==expected and invalid==0,'transportSeamsClean':not unpaired,'terrainNumericAudited':False,'note':'Pending endpoints are caused by absent neighbors and are not counted as confirmed seam defects. Vector completeness does not certify official terrain or visual fidelity.'}}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2))
 cards=[('Coordonnées valides',f'{valid} / {expected}'),('Vides officielles',str(empty_tiles)),('Couverture',f"{report['coveragePercent']:.2f} %"),('Raccords appariés',str(len(matched_pairs))),('Anomalies confirmées',str(len(unpaired))),('Voisins manquants',str(len(pending))),('Bâtiments coupés',str(len(split_buildings)))]
 a.output.with_suffix('.html').write_text(f'''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Audit cartographique v0.38</title><style>body{{background:#101712;color:#dde7d3;font:15px/1.55 system-ui;margin:0}}main{{max-width:1150px;margin:auto;padding:32px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}article{{border:1px solid #475d48;background:#18231a;padding:18px}}b{{font-size:25px;color:#e8dca3}}code{{color:#e6d49d}}</style><main><h1>Fallout : Mistral — Audit vectoriel v0.38</h1><p>Les tuiles HTTP 204 possèdent un marqueur distinct. Les voisins absents sont séparés des raccords réellement défectueux.</p><div class="grid">{''.join(f'<article><small>{html.escape(k)}</small><br><b>{html.escape(v)}</b></article>' for k,v in cards)}</div><h2>Conclusion</h2><p>{'Sélection vectorielle complète et raccords contrôlés.' if report['truth']['complete'] else 'Sélection encore incomplète ou nécessitant une correction de raccord.'}</p><p>Relief numérique officiel : non certifié par cet audit.</p></main></html>''')
 print(json.dumps({k:report[k] for k in ['expected','present','valid','invalid','missing','coveragePercent']},ensure_ascii=False,indent=2));print(json.dumps(report['transportTopology'],ensure_ascii=False,indent=2)[:1200]);return 0 if report['truth']['complete'] else 2
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=MANIFEST);p.add_argument('--pack',type=Path,default=ROOT/'data/map_pack');p.add_argument('--source',choices=['all','base','cadastre'],default='all');p.add_argument('--macro',choices=['all','geo_marseille','geo_huveaune','geo_garlaban','geo_calanques','geo_laciotat','geo_frioul','geo_etoile','geo_saintebaume'],default='all');p.add_argument('--output',type=Path,default=ROOT/'verification/AUDIT_CARTE_REELLE_V038.json');p.add_argument('--limit',type=int,default=0);raise SystemExit(audit(p.parse_args()))
if __name__=='__main__':main()
