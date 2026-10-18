#!/usr/bin/env python3
"""Sample supplied georeferenced elevation rasters over ALL eight region extents.
No network access and no implicit IGN provenance. NoData remains missing; incomplete
regions are never written under a runtime-loadable filename. All values are absolute
source heights; this tool does NOT convert vertical datums.
"""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import Affine
MACROS={
'geo_marseille':[43.2200,5.2850,43.3400,5.5100], 'geo_huveaune':[43.2450,5.4300,43.3350,5.6400],
'geo_garlaban':[43.2450,5.4850,43.3900,5.6900], 'geo_calanques':[43.1450,5.3300,43.2850,5.6500],
'geo_laciotat':[43.1250,5.5400,43.2550,5.7350], 'geo_frioul':[43.2450,5.2550,43.3150,5.3500],
'geo_etoile':[43.3000,5.4350,43.4200,5.6000], 'geo_saintebaume':[43.2150,5.5650,43.4100,5.7550]}
def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def atomic_json(path:Path,data:dict):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False),encoding='utf-8');os.replace(tmp,path)
def build(paths:list[Path],output:Path,size:int,source:str,vertical_datum:str)->dict:
 if not 2<=size<=1024:raise ValueError('Taille de grille comprise entre 2 et 1024 requise')
 output.mkdir(parents=True,exist_ok=True);inputs=[]
 for path in paths:
  with rasterio.open(path) as src:
   if not src.crs or src.count<1:raise ValueError(f'Raster non géoréférencé : {path}')
   inputs.append({'file':path.name,'sha256':sha(path),'crs':str(src.crs),'nodata':str(src.nodata)})
 report={'source':source,'verticalDatum':vertical_datum,'inputs':inputs,'gridSize':size,'regions':{},'note':'Grilles simplifiées ; ne restituent pas les détails inférieurs à leur pas. Aucun changement de référentiel vertical.'}
 for mid,(south,west,north,east) in MACROS.items():
  dx=(east-west)/(size-1);dy=(north-south)/(size-1)
  # Grid node endpoints, not raster cell boundaries, coincide with the runtime bbox.
  dst_t=Affine(dx,0,west-dx/2,0,-dy,north+dy/2);dest=np.full((size,size),np.nan,dtype='float32')
  for path in paths:
   with rasterio.open(path) as src:
    piece=np.full_like(dest,np.nan)
    reproject(source=rasterio.band(src,1),destination=piece,src_transform=src.transform,src_crs=src.crs,src_nodata=src.nodata,dst_transform=dst_t,dst_crs='EPSG:4326',dst_nodata=np.nan,resampling=Resampling.bilinear,init_dest_nodata=True,num_threads=1)
    use=np.isnan(dest)&np.isfinite(piece)&(piece>=-12000)&(piece<=9000);dest[use]=piece[use]
  valid=np.isfinite(dest);missing=int((~valid).sum());name=f'{mid}.json';live=output/name
  payload={'macro':mid,'bbox':[south,west,north,east],'width':size,'height':size,'source':source,'verticalDatum':vertical_datum,'missingCells':missing,'inputs':inputs,'min':float(dest[valid].min()) if valid.any() else None,'max':float(dest[valid].max()) if valid.any() else None,'values':[round(float(v),3) if np.isfinite(v) else None for v in dest.ravel()]}
  if missing:
   # Preserve any earlier valid pack; write a separate diagnostic, never overwrite it.
   diagnostic=output/f'{mid}.incomplete.json';atomic_json(diagnostic,payload);status='incomplete'
  else:atomic_json(live,payload);status='complete'
  report['regions'][mid]={'status':status,'missingCells':missing,'min':payload['min'],'max':payload['max'],'output':name if not missing else f'{mid}.incomplete.json'}
 atomic_json(output/'terrain_manifest.json',report);return report
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('geotiff',nargs='+',type=Path);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'data/map_pack/terrain');p.add_argument('--size',type=int,default=128);p.add_argument('--source',required=True,help='Nom réel du jeu de données et millésime');p.add_argument('--vertical-datum',required=True,help='Référentiel altimétrique du raster fourni')
 a=p.parse_args();r=build(a.geotiff,a.output,a.size,a.source,a.vertical_datum);print(json.dumps(r['regions'],ensure_ascii=False,indent=2))
 if any(v['status']!='complete' for v in r['regions'].values()):raise SystemExit(2)
if __name__=='__main__':main()
