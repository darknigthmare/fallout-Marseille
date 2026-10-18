#!/usr/bin/env python3
"""Audit of locally available inputs; missing data is not considered success."""
from pathlib import Path
import argparse,json,math,hashlib,sys
from mvt_audit_v036 import parse_tile
ROOT=Path(__file__).resolve().parents[1]
def audit(pack:Path):
 manifest=json.loads((ROOT/'data/map_pack/manifest_v038.json').read_text())
 v={'expected':len(manifest['tiles']),'pbf':0,'officialEmpty':0,'missing':0,'invalid':0,'bytes':0,'examples':[]}
 for r in manifest['tiles']:
  f=pack/r['local'].replace('data/map_pack/','')
  if not f.is_file():v['missing']+=1;continue
  try:
   raw=f.read_bytes()
   if not raw:
    mark=json.loads(f.with_suffix(f.suffix+'.empty.json').read_text())
    if mark.get('officialEmpty') is not True:raise ValueError('marqueur vide absent')
    # A marker must not claim a different coordinate.
    if any(k in mark and mark[k]!=r[k] for k in ('source','z','x','y')):raise ValueError('marqueur associé à une autre tuile')
    v['officialEmpty']+=1
   else:
    parse_tile(raw);v['pbf']+=1;v['bytes']+=len(raw)
  except Exception as e:
   v['invalid']+=1
   if len(v['examples'])<12:v['examples'].append({'file':str(f),'reason':str(e)})
 terrain={'expected':8,'valid':0,'missing':0,'invalid':0,'samples':0,'noData':0,'examples':[]}
 tm=json.loads((ROOT/'data/map_pack/terrain/manifest_v039.json').read_text())
 for r in tm['regions']:
  f=pack/'terrain'/f"{r['macro']}.json"
  if not f.is_file():terrain['missing']+=1;continue
  try:
   j=json.loads(f.read_text());values=j.get('values',[]);b=j.get('bbox',[])
   if j.get('macro')!=r['macro'] or len(b)!=4 or any(abs(x-y)>1e-7 for x,y in zip(b,r['bbox'])):raise ValueError('emprise ou macro incorrecte')
   if j.get('sourceResource')!='ign_rge_alti_wld':raise ValueError('provenance absente')
   if j.get('rowOrder','north-to-south')!='north-to-south':raise ValueError('axe terrain invalide')
   if not isinstance(j.get('width'),int) or not isinstance(j.get('height'),int) or j['width']<2 or j['height']<2 or len(values)!=j['width']*j['height']:raise ValueError('grille incomplète')
   n=sum(isinstance(x,(int,float)) and math.isfinite(x) and -100<x<9000 for x in values)
   if not n:raise ValueError('aucune altitude exploitable')
   terrain['valid']+=1;terrain['samples']+=n;terrain['noData']+=len(values)-n
  except Exception as e:terrain['invalid']+=1;terrain['examples'].append({'file':str(f),'reason':str(e)})
 return {'version':'0.46.0','vector':v,'terrain':terrain,'complete':v['missing']==v['invalid']==terrain['missing']==terrain['invalid']==0,'scope':'État des fichiers réellement présents. Les anciens rapports de cache cloud ne sont pas une preuve de disponibilité actuelle.'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pack',type=Path,default=ROOT/'data/map_pack');ap.add_argument('--report',type=Path,default=ROOT/'verification/v046/LOCAL_DATA_STATE.json');ap.add_argument('--require-complete',action='store_true');a=ap.parse_args();r=audit(a.pack);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2));return int(a.require_complete and not r['complete'])
if __name__=='__main__':raise SystemExit(main())
