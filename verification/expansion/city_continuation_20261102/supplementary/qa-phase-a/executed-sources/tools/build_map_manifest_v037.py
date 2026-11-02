#!/usr/bin/env python3
"""Build the exhaustive real-map tile manifest for Fallout: Mistral v0.37.

The manifest contains every vector tile intersecting the eight declared macro regions.
No network access is required and no tile is reported as downloaded by this script.
"""
from __future__ import annotations
import hashlib, json, math, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'map_pack'
MACROS={
 'geo_marseille':[43.2200,5.2850,43.3400,5.5100],
 'geo_huveaune':[43.2450,5.4300,43.3350,5.6400],
 'geo_garlaban':[43.2450,5.4850,43.3900,5.6900],
 'geo_calanques':[43.1450,5.3300,43.2850,5.6500],
 'geo_laciotat':[43.1250,5.5400,43.2550,5.7350],
 'geo_frioul':[43.2450,5.2550,43.3150,5.3500],
 'geo_etoile':[43.3000,5.4350,43.4200,5.6000],
 'geo_saintebaume':[43.2150,5.5650,43.4100,5.7550],
}
SOURCES={
 'base':{'id':'france-vector','zoom':14,'direct':'https://openmaptiles.data.gouv.fr/data/france-vector/{z}/{x}/{y}.pbf','local':'data/map_pack/france-vector/{z}/{x}/{y}.pbf'},
 'cadastre':{'id':'cadastre','zoom':16,'direct':'https://openmaptiles.data.gouv.fr/data/cadastre/{z}/{x}/{y}.pbf','local':'data/map_pack/cadastre/{z}/{x}/{y}.pbf'},
}
RELAY='https://hykklcvvwjwhcvukbzts.supabase.co/functions/v1/fallout-mistral-map-v037/tile/{source}/{z}/{x}/{y}.pbf'

def lonlat_tile(lat:float,lon:float,z:int)->tuple[int,int]:
 n=2**z
 x=int((lon+180)/360*n)
 y=int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
 return x,y

def bbox_tiles(bbox:list[float],z:int)->list[tuple[int,int]]:
 south,west,north,east=bbox
 x0,ys=lonlat_tile(south,west,z);x1,yn=lonlat_tile(north,east,z)
 return [(x,y) for x in range(min(x0,x1),max(x0,x1)+1) for y in range(min(yn,ys),max(yn,ys)+1)]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 union={k:{} for k in SOURCES}
 macro_counts={}
 for macro,bbox in MACROS.items():
  macro_counts[macro]={}
  for source,spec in SOURCES.items():
   tiles=bbox_tiles(bbox,spec['zoom'])
   macro_counts[macro][source]=len(tiles)
   for x,y in tiles:
    key=f"{spec['zoom']}/{x}/{y}"
    union[source].setdefault(key,set()).add(macro)
 rows=[]
 for source,spec in SOURCES.items():
  for key,macros in sorted(union[source].items()):
   z,x,y=map(int,key.split('/'))
   rows.append({
    'source':source,'dataset':spec['id'],'z':z,'x':x,'y':y,'key':key,
    'macros':sorted(macros),
    'local':spec['local'].format(z=z,x=x,y=y),
    'direct':spec['direct'].format(z=z,x=x,y=y),
    'relay':RELAY.format(source=source,z=z,x=x,y=y),
    'status':'planned','bytes':None,'sha256':None
   })
 counts={s:len(union[s]) for s in SOURCES};counts['total']=sum(counts.values())
 manifest={
  'version':'0.37.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
  'status':'planned-not-bundled','bounds':{'south':43.125,'west':5.255,'north':43.420,'east':5.755},
  'projection':'EPSG:2154 runtime / WGS84 source tiles','macros':MACROS,'sources':SOURCES,
  'relay':{'service':'fallout-mistral-map-v037','url':'https://hykklcvvwjwhcvukbzts.supabase.co/functions/v1/fallout-mistral-map-v037','publishableKeyRequired':True},
  'macroCounts':macro_counts,'counts':counts,'tiles':rows,
  'licenses':{
   'base':'OpenStreetMap contributors — ODbL 1.0',
   'cadastre':'Cadastre Etalab / DGFiP — Licence Ouverte 2.0',
   'terrain':'IGN RGE ALTI — Licence Ouverte 2.0; numeric pack not included in this build'
  }
 }
 out=OUT/'manifest_v037.json'
 out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 compact=OUT/'manifest_v037.compact.json'
 compact.write_text(json.dumps({'version':manifest['version'],'generated':manifest['generated'],'status':manifest['status'],'bounds':manifest['bounds'],'macros':manifest['macros'],'sources':manifest['sources'],'relay':manifest['relay'],'counts':counts,'macroCounts':macro_counts,'licenses':manifest['licenses']},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 report={'file':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'counts':counts,'macroCounts':macro_counts}
 (OUT/'manifest_v037_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if counts!={'base':367,'cadastre':5517,'total':5884}:raise SystemExit(f'Unexpected plan counts: {counts}')
if __name__=='__main__':main()
