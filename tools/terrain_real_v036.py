#!/usr/bin/env python3
"""Prepare official numeric terrain files for Fallout: Mistral v0.36.

This tool never invents elevations. It consumes user-supplied IGN RGE ALTI GeoTIFFs
(or any GeoTIFF explicitly documented as EPSG:2154), resamples each of the eight
macro regions and writes the compact terrain JSON files used by the game.
"""
from __future__ import annotations
import argparse, json, math, hashlib, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MACROS={
 'geo_marseille':[43.2200,5.2850,43.3400,5.5100],'geo_huveaune':[43.2450,5.4300,43.3350,5.6400],
 'geo_garlaban':[43.2450,5.4850,43.3900,5.6900],'geo_calanques':[43.1450,5.3300,43.2850,5.6500],
 'geo_laciotat':[43.1250,5.5400,43.2550,5.7350],'geo_frioul':[43.2450,5.2550,43.3150,5.3500],
 'geo_etoile':[43.3000,5.4350,43.4200,5.6000],'geo_saintebaume':[43.2150,5.5650,43.4100,5.7550]
}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('geotiffs',nargs='*',type=Path);p.add_argument('--output',type=Path,default=ROOT/'data'/'map_pack'/'terrain');p.add_argument('--width',type=int,default=321);p.add_argument('--height',type=int,default=321);p.add_argument('--source-label',default='IGN RGE ALTI — fichier numérique fourni par l’utilisateur');p.add_argument('--plan-only',action='store_true')
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 plan={'version':'0.36.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'waiting-official-numeric-source','macros':MACROS,'expectedFiles':[f'terrain/{m}.json' for m in MACROS],'sourceLabel':a.source_label,'inputFiles':[str(x) for x in a.geotiffs]}
 (a.output/'terrain_plan_v036.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 if a.plan_only or not a.geotiffs:
  print(json.dumps(plan,ensure_ascii=False,indent=2));return 0
 try:import rasterio
 except Exception as e:raise SystemExit('rasterio requis : pip install rasterio') from e
 from rasterio.merge import merge
 from rasterio.warp import transform_bounds,reproject,Resampling
 import numpy as np
 sources=[rasterio.open(str(x)) for x in a.geotiffs]
 try:
  crs=sources[0].crs
  if not crs:raise SystemExit('Le GeoTIFF ne déclare aucun système de coordonnées.')
  reports=[]
  for macro,b in MACROS.items():
   south,west,north,east=b;left,bottom,right,top=transform_bounds('EPSG:4326',crs,west,south,east,north,densify_pts=21)
   transform=rasterio.transform.from_bounds(left,bottom,right,top,a.width,a.height);dest=np.full((a.height,a.width),np.nan,dtype='float32')
   for ds in sources:
    tmp=np.full_like(dest,np.nan)
    reproject(source=rasterio.band(ds,1),destination=tmp,src_transform=ds.transform,src_crs=ds.crs,src_nodata=ds.nodata,dst_transform=transform,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear)
    mask=np.isfinite(tmp);dest[mask]=tmp[mask]
   valid=np.isfinite(dest);coverage=float(valid.sum()/dest.size)
   if coverage<.999:raise SystemExit(f'{macro}: couverture numérique incomplète {coverage:.2%}')
   payload={'version':'0.36.0','macro':macro,'source':a.source_label,'license':'Licence Ouverte 2.0 — vérifier la provenance du fichier source','crs':str(crs),'width':a.width,'height':a.height,'bboxWGS84':b,'min':float(dest.min()),'max':float(dest.max()),'coverage':coverage,'data':[round(float(v),2) for v in dest.ravel()]}
   out=a.output/f'{macro}.json';out.write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8');reports.append({'macro':macro,'file':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'min':payload['min'],'max':payload['max']})
  report={'version':'0.36.0','source':a.source_label,'complete':len(reports)==8,'files':reports};(a.output/'terrain_report_v036.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
 finally:
  for ds in sources:ds.close()
 return 0
if __name__=='__main__':raise SystemExit(main())
