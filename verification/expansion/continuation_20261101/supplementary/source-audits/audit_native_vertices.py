"""Supplementary source observations, outside the gameplay assertion sum."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import rasterio

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--cache',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
idx=json.loads((args.repo/'data/map_pack/landmark_surfaces/index.json').read_text())
raw=(args.repo/idx['surface']['path']).read_bytes()
atlas=json.loads(raw)
tiles=[]
for t in atlas['source']['tiles']:
    path=args.cache/t['filename']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==t['sha256']
    with rasterio.open(path) as raster:
        x0,y0=raster.xy(0,0)
        tiles.append({'data':raster.read(1),'x':x0,'y':y0,'width':raster.width,'height':raster.height,'sha256':t['sha256']})

def native(x,y):
    for tile in tiles:
        cc=(x-tile['x'])/.5;rr=(tile['y']-y)/.5
        col,row=round(cc),round(rr)
        if abs(cc-col)<1e-6 and abs(rr-row)<1e-6 and 0<=row<tile['height'] and 0<=col<tile['width']:
            height=float(tile['data'][row,col]);assert height!=-9999
            return height
    raise AssertionError(['source-centre-absent',x,y])

rows=[]
native_count=clipped_count=0
max_native=max_clipped=0
for record in atlas['records']:
    local_native=local_clipped=0
    local_error=0
    for x,y,height in record['vertices']:
        if abs(x*2-round(x*2))<2e-8 and abs(y*2-round(y*2))<2e-8:
            expected=native(round(x*2)/2,round(y*2)/2)
            error=abs(expected-height)
            assert error==0,(record['cleabs'],x,y,height,expected)
            native_count+=1;local_native+=1;max_native=max(max_native,error)
        else:
            x0,y0=math.floor(x*2)/2,math.ceil(y*2)/2
            u,v=(x-x0)/.5,(y0-y)/.5
            za,zb,zc,zd=[native(a,b) for a,b in [(x0,y0),(x0+.5,y0),(x0,y0-.5),(x0+.5,y0-.5)]]
            expected=za+u*(zb-za)+v*(zc-za) if u+v<=1 else zd+(1-u)*(zc-zd)+(1-v)*(zb-zd)
            error=abs(expected-height)
            assert error<.000001,(record['cleabs'],x,y,height,expected,error)
            clipped_count+=1;local_clipped+=1;max_clipped=max(max_clipped,error);local_error=max(local_error,error)
    rows.append({'cleabs':record['cleabs'],'nativeCentreVerticesCompared':local_native,'clippedPlaneVerticesCompared':local_clipped,'maximumClippedDifferenceMetres':local_error})
report={'scope':'Independent full payload vertex comparison against original received Float32 MNS GeoTIFF cells. Counts are source observations outside the final gameplay/assertion sum.',
        'payloadSha256':hashlib.sha256(raw).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'nativeSourceHashes':[t['sha256'] for t in tiles],'nativeCentreVerticesCompared':native_count,'clippedPlaneVerticesCompared':clipped_count,
        'totalCompared':native_count+clipped_count,'maximumNativeDifferenceMetres':max_native,'maximumClippedDifferenceMetres':max_clipped,'rows':rows,'passed':True}
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['nativeCentreVerticesCompared','clippedPlaneVerticesCompared','totalCompared','maximumNativeDifferenceMetres','maximumClippedDifferenceMetres','passed']}))
