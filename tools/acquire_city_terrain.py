#!/usr/bin/env python3
"""Acquire actual IGN RGE ALTI grids covering a complete commune envelope.

The default point-elevation API supplies each requested coordinate. Exact NoData
and unusable provider observations are recorded separately. Optional WMS acquisition
checks pixel centres, one float band, masks and physical range; contaminated
NoData interpolation is refused. No provider kernel or accuracy is invented.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from convert_ign_dem import checked_bbox, grid_shape
from world_sources import atomic_write, canonical, terrain_digest
from install_terrain_v039 import OFFICIAL_RATE, official_payload

ROOT = Path(__file__).resolve().parents[1]
REGION = 'geo_marseille_commune'
WMS = 'https://data.geopf.fr/wms-r/wms'
LAYER = 'ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES'
MAX_RESPONSE_BYTES = 32 * 1024**2
MAX_GRID_NODES = 1_048_576
MAX_TILE_INTERVALS = 500
POINT_API = 'https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json'
POINT_RESOURCE = 'https://data.geopf.fr/altimetrie/resources/ign_rge_alti_wld'
POINT_NODATA = -99999


def node_request(bounds, width, height):
    """Expand half a pixel around the requested node coordinates (lon/lat CRS)."""
    south, west, north, east = checked_bbox(bounds)
    if type(width) is not int or type(height) is not int or min(width, height) < 2 or width * height > MAX_GRID_NODES:
        raise ValueError('grid dimensions exceed the bounded elevation request')
    dx, dy = (east-west)/(width-1), (north-south)/(height-1)
    raster_bounds = [west-dx/2, south-dy/2, east+dx/2, north+dy/2]
    query = {'SERVICE': 'WMS', 'VERSION': '1.3.0', 'REQUEST': 'GetMap',
             'LAYERS': LAYER, 'CRS': 'IGNF:WGS84G', 'BBOX': ','.join(format(v, '.15g') for v in raster_bounds),
             'WIDTH': width, 'HEIGHT': height, 'FORMAT': 'image/geotiff', 'STYLES': 'normal'}
    return WMS + '?' + urlencode(query), raster_bounds


def partitions(bounds, spacing=10, maximum_intervals=MAX_TILE_INTERVALS):
    """Partition one global grid; neighboring tiles share exact boundary nodes."""
    bounds = checked_bbox(bounds)
    if not math.isfinite(spacing) or not 1 <= spacing <= 100:
        raise ValueError('nominal spacing must be within 1..100 metres')
    if type(maximum_intervals) is not int or not 1 <= maximum_intervals <= 1023:
        raise ValueError('tile interval limit must be within 1..1023')
    # grid_shape deliberately bounds single grids; this global shape is only a
    # plan and is partitioned before any request, array or raster is allocated.
    south, west, north, east = bounds
    lat = math.radians((south+north)/2)
    e2 = 6.6943799901413165e-3
    q = 1-e2*math.sin(lat)**2
    dxm = math.radians(east-west)*6378137/math.sqrt(q)*math.cos(lat)
    dym = math.radians(north-south)*6378137*(1-e2)/q**1.5
    nx, ny = max(1,math.ceil(dxm/spacing)), max(1,math.ceil(dym/spacing))
    if (nx+1)*(ny+1) > 20_000_000:
        raise ValueError('global fine-grid plan exceeds twenty million nodes')
    result=[]
    for y in range(0,ny,maximum_intervals):
        y1=min(y+maximum_intervals,ny)
        for x in range(0,nx,maximum_intervals):
            x1=min(x+maximum_intervals,nx)
            b=[north-(north-south)*y1/ny, west+(east-west)*x/nx,
               north-(north-south)*y/ny, west+(east-west)*x1/nx]
            result.append({'id':f'{y:05d}-{x:05d}','bbox':b,'width':x1-x+1,'height':y1-y+1,
                           'globalWindow':[x,y,x1,y1], 'globalShape':[nx+1,ny+1],
                           'globalBBox':bounds, 'spacingMeters':[dxm/nx,dym/ny]})
    return result


def fetch(url, timeout=180):
    """Follow only the fixed HTTPS service with normal proxy and CA trust."""
    request=Request(url,headers={'User-Agent':'Fallout-Mistral-Commune-Terrain/1.0'})
    with urlopen(request,timeout=timeout) as response:
        if response.status != 200 or response.url.split('?',1)[0] != WMS:
            raise ValueError('unexpected numeric elevation response or destination')
        size=response.headers.get('Content-Length')
        if size is not None and not 0<int(size)<=MAX_RESPONSE_BYTES:
            raise ValueError('elevation response exceeds the bounded byte limit')
        raw=response.read(MAX_RESPONSE_BYTES+1)
        if not raw or len(raw)>MAX_RESPONSE_BYTES or size is not None and len(raw)!=int(size):
            raise ValueError('elevation response is empty, truncated or oversized')
        return raw


def decode_raster(raw, bounds, width, height):
    import numpy as np
    from rasterio.io import MemoryFile
    _, expected_bounds=node_request(bounds,width,height)
    with MemoryFile(raw) as file, file.open() as raster:
        if raster.driver!='GTiff' or raster.count!=1 or raster.dtypes[0] not in ('float32','float64'):
            raise ValueError('normal WMS export must be a single floating-point elevation GeoTIFF')
        if [raster.width,raster.height]!=[width,height] or any(abs(a-b)>1e-9 for a,b in zip(raster.bounds,expected_bounds)):
            raise ValueError('GeoTIFF dimensions/georeferencing differ from requested node centres')
        if raster.crs is None or not raster.crs.is_geographic:
            raise ValueError('GeoTIFF must declare the requested geographic CRS')
        if raster.crs.to_epsg()!=4326:
            raise ValueError('GeoTIFF must declare recognized WGS84 / EPSG:4326; a different or unrecognized geographic datum is not accepted')
        transform=raster.transform
        if transform.a<=0 or transform.e>=0 or abs(transform.b)>1e-12 or abs(transform.d)>1e-12:
            raise ValueError('rotated or inverted service grid is not accepted')
        data=raster.read(1,masked=True)
        mask=np.ma.getmaskarray(data)|~np.isfinite(data.data)
        measured=data.data[~mask]
        if ((measured<=-100)|(measured>=9000)).any():
            raise ValueError('unmasked elevations exceed supported physical range; source not clamped or filled')
        values=[None if missing else float(value) for value,missing in zip(data.data.ravel(),mask.ravel())]
        return values, {'format':'GeoTIFF','driver':raster.driver,'bands':raster.count,'dtype':raster.dtypes[0],
                        'rawCrsWkt':raster.crs.to_wkt(),'requestCrs':'IGNF:WGS84G',
                        'bounds':list(raster.bounds),'pixelSizeDegrees':[transform.a,-transform.e],
                        'nodata':raster.nodata,'nodeCentresVerified':True}


def read_cached(cache, url, timeout):
    key=hashlib.sha256(url.encode()).hexdigest()
    path=cache/(key+'.tif')
    receipt=cache/(key+'.json')
    if path.exists() or receipt.exists():
        if not path.is_file() or not receipt.is_file():
            raise ValueError('incomplete cached source; remove the incomplete pair explicitly before retrying')
        proof=json.loads(receipt.read_text())
        raw=path.read_bytes()
        if proof.get('url')!=url or proof.get('bytes')!=len(raw) or proof.get('sha256')!=hashlib.sha256(raw).hexdigest():
            raise ValueError('cached numeric source differs from its acquisition receipt')
        return raw,proof
    last=None
    for attempt in range(3):
        try:
            raw=fetch(url,timeout)
            proof={'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                   'acquiredAt':dt.datetime.now(dt.timezone.utc).isoformat()}
            atomic_write(path,raw)
            atomic_write(receipt,canonical(proof))
            return raw,proof
        except (OSError,ValueError) as error:
            last=error
            if attempt<2: time.sleep(1+attempt)
    raise last


def decode_points(raw, points, allow_invalid=False):
    """Keep exact NoData distinct from explicitly quarantined invalid reports."""
    payload=json.loads(raw)
    elevations=payload.get('elevations') if isinstance(payload,dict) else None
    if not isinstance(elevations,list) or len(elevations)!=len(points):
        raise ValueError('point API response omits requested coordinates')
    values=[];invalid=[]
    for index,(entry,(lat,lon)) in enumerate(zip(elevations,points)):
        if not isinstance(entry,dict) or any(type(entry.get(k)) not in (int,float) or not math.isfinite(entry[k]) for k in ('lat','lon')):
            raise ValueError('point API response has invalid geographic coordinates')
        if abs(entry['lat']-lat)>1e-9 or abs(entry['lon']-lon)>1e-9:
            raise ValueError('point API reordered or changed requested coordinates')
        value=entry.get('z','missing')
        if value is None or type(value) in (int,float) and value==POINT_NODATA:
            values.append(None)
        elif type(value) not in (int,float) or not math.isfinite(value):
            raise ValueError(f'point API altitude {value!r} at {(lat,lon)!r} is invalid, not an exact NoData sentinel; no value clamped')
        elif not -100<value<9000:
            if not allow_invalid:
                raise ValueError(f'point API altitude {value!r} at {(lat,lon)!r} is invalid, not an exact NoData sentinel; no value clamped')
            invalid.append({'index':index,'lat':lat,'lon':lon,'reportedZ':value,
                            'reason':'Provider observation outside the supported Marseille terrain range; not a valid altitude or an exact NoData sentinel'})
            values.append(None)
        else: values.append(value)
    return (values,invalid) if allow_invalid else values


def grid_nodes(plan):
    south,west,north,east=plan['bbox'];width,height=plan['width'],plan['height']
    # The request precision is stated explicitly; grid bboxes retain full source
    # coordinates. Rounding coordinates at 1e-10 degree is <0.02 mm here.
    if 'globalWindow' in plan:
        south,west,north,east=plan['globalBBox'];gw,gh=plan['globalShape'];ox,oy,_,_=plan['globalWindow']
        return [(round(north-(y+oy)*(north-south)/(gh-1),10),round(west+(x+ox)*(east-west)/(gw-1),10))
                for y in range(height) for x in range(width)]
    else:
        return [(round(north-y*(north-south)/(height-1),10),round(west+x*(east-west)/(width-1),10))
                for y in range(height) for x in range(width)]


def point_grid(plan, cache, timeout=180, workers=3):
    points=grid_nodes(plan)
    batches=[(start,points[start:start+5000]) for start in range(0,len(points),5000)]
    folder=cache/'point-api';folder.mkdir(exist_ok=True)
    def batch(item):
        start,selected=item;body=canonical(official_payload(selected));request_sha=hashlib.sha256(body).hexdigest()
        path=folder/(request_sha+'.json');proof_path=folder/(request_sha+'.proof.json')
        if path.exists() and proof_path.exists():
            raw=path.read_bytes();proof=json.loads(proof_path.read_text())
            if proof.get('requestSha256')!=request_sha or proof.get('responseSha256')!=hashlib.sha256(raw).hexdigest():
                raise ValueError('point API checkpoint checksum mismatch')
            values,invalid=decode_points(raw,selected,allow_invalid=True)
            return raw,values,{**proof,'providerInvalidSamples':invalid}
        last=None
        for attempt in range(3):
            try:
                OFFICIAL_RATE.wait()
                with urlopen(Request(POINT_API,data=body,headers={'Content-Type':'application/json','Accept':'application/json',
                             'User-Agent':'Fallout-Mistral-City-Terrain/1.0'},method='POST'),timeout=timeout) as response:
                    raw=response.read(4*1024**2+1)
                    if response.status!=200 or not raw or len(raw)>4*1024**2:
                        raise ValueError('point API response exceeds supported size/status')
                try:
                    values,invalid=decode_points(raw,selected,allow_invalid=True)
                except ValueError as error:
                    atomic_write(folder/(request_sha+'.rejected-response.json'),raw)
                    atomic_write(folder/(request_sha+'.rejected-proof.json'),canonical({'url':POINT_API,'requestSha256':request_sha,
                                 'responseSha256':hashlib.sha256(raw).hexdigest(),'reason':str(error)}))
                    raise
                proof={'url':POINT_API,'resource':'ign_rge_alti_wld','requestSha256':request_sha,
                       'responseSha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'points':len(selected),
                       'acquiredAt':dt.datetime.now(dt.timezone.utc).isoformat(),'providerInvalidSamples':invalid}
                atomic_write(path,raw);atomic_write(proof_path,canonical(proof))
                return raw,values,proof
            except (OSError,ValueError) as error:
                last=error
                if attempt<2:time.sleep(2+attempt)
        raise last
    values=[];proofs=[];digest=hashlib.sha256();size=0;invalid_samples=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for number,(raw,decoded,proof) in enumerate(pool.map(batch,batches),1):
            start=len(values)
            invalid_samples.extend({**item,'index':start+item['index'],'responseSha256':proof['responseSha256']}
                                   for item in proof.get('providerInvalidSamples',[]))
            digest.update(raw);size+=len(raw);values.extend(decoded)
            proofs.append({**{k:v for k,v in proof.items() if k!='providerInvalidSamples'},
                           'providerInvalidPoints':len(proof.get('providerInvalidSamples',[]))})
            if number%20==0 or number==len(batches):
                print(json.dumps({'tile':plan['id'],'pointBatches':number,'totalBatches':len(batches)},ensure_ascii=False),flush=True)
    receipt={'url':POINT_API,'sha256':digest.hexdigest(),'bytes':size,'acquiredAt':max(p['acquiredAt'] for p in proofs),
             'digestScope':'Concatenation of complete raw JSON response bodies in node-row order',
             'batchCount':len(batches),'batches':proofs,'providerInvalidSamples':invalid_samples}
    header={'format':'IGN point-elevation JSON','resource':'ign_rge_alti_wld','requestCrs':'EPSG:4326',
            'nodeCentresVerified':True,'coordinatePrecisionDegrees':1e-10,'nodata':POINT_NODATA,
            'accuracy':'Variable suivant la source de mesure','providerInvalidPoints':len(invalid_samples),
            'providerInvalidSamplesSha256':hashlib.sha256(canonical(invalid_samples)).hexdigest()}
    return values,receipt,header


def acquire_grid(plan, cache, output, timeout=180, base=False, method='points', point_workers=3):
    width,height,bounds=plan['width'],plan['height'],plan['bbox']
    if method=='points':
        values,receipt,header=point_grid(plan,cache,timeout,point_workers)
        url=POINT_API
    elif method=='wms':
        url,_=node_request(bounds,width,height)
        raw,receipt=read_cached(cache,url,timeout)
        values,header=decode_raster(raw,bounds,width,height)
    else:raise ValueError('unsupported terrain acquisition method')
    valid=sum(value is not None for value in values)
    invalid_points=header.get('providerInvalidPoints',0)
    grid={'macro':REGION if base else 'enrichment:'+REGION,'width':width,'height':height,'bbox':bounds,
          'rowOrder':'north-to-south','values':values,'sourceResource':'ign_rge_alti_wld',
          'verticalDatum':'NGF-IGN69 — RGE ALTI, France continentale','validPoints':valid,
          'missingPoints':len(values)-valid,
          'providerNoDataPoints':len(values)-valid-invalid_points,'providerInvalidPoints':invalid_points,
          'outOfSupportedRangePoints':invalid_points,
          'provenance':{'source':'IGN — MNT RGE ALTI, API points' if method=='points' else 'IGN — MNT RGE ALTI, WMS numérique','resource':'ign_rge_alti_wld',
                        'license':'Licence Ouverte 2.0','attribution':'IGN — RGE ALTI',
                        'acquiredAt':receipt['acquiredAt'][:10],'downloadedAt':receipt['acquiredAt'],
                        'url':url,'inputSha256':receipt['sha256'],
                        'inputCrs':'EPSG:4326' if method=='points' else 'IGNF:WGS84G',
                        'verticalDatum':'NGF-IGN69 — RGE ALTI, France continentale','resampled':True,
                        'serviceSampling':{'method':'IGN point-elevation POST API' if method=='points' else 'WMS GetMap, normal numeric GeoTIFF',
                                           'resampling':'provider-unspecified','requestedSpacingMeters':plan['spacingMeters'],
                                           'nativeResolution':None,'surveyAccuracy':None,
                                           'surveyDate':None,'nodataPreserved':True,
                                           'providerInvalidPoints':invalid_points,
                                           'outOfSupportedRangePoints':invalid_points,
                                           'unusableObservationPolicy':'providerInvalidPoints is a compatibility alias for observations outside the game supported range, not an assertion that every observation is a provider error or physical bathymetry',
                                           'providerInvalidSamplesSha256':header.get('providerInvalidSamplesSha256'),
                                           'sampleConvention':'regular WGS84 nodes submitted to the IGN point API' if method=='points' else 'regular WGS84 nodes at GeoTIFF pixel centres',
                                           'header':header}}}
    if not base: grid['macro']='enrichment:'+REGION+':'+terrain_digest(grid)[:16]
    encoded=canonical(grid)
    digest=hashlib.sha256(encoded).hexdigest()
    filename=f'terrain-{digest[:16]}.json'
    destination=output/filename
    if destination.exists() and destination.read_bytes()!=encoded:
        raise ValueError('immutable terrain destination contains different bytes')
    if not destination.exists(): atomic_write(destination,encoded)
    descriptor={'path':'data/map_pack/city/'+filename,'sha256':digest,'bytes':len(encoded),'bbox':bounds,
                'width':width,'height':height,'validPoints':valid,'missingPoints':len(values)-valid,
                'providerNoDataPoints':len(values)-valid-invalid_points,'providerInvalidPoints':invalid_points,
                'outOfSupportedRangePoints':invalid_points,
                'macro':grid['macro'],'sourceResource':grid['sourceResource'],'allNoData':valid==0}
    public={'id':plan['id'],'descriptor':descriptor,'input':receipt,'header':header,'globalWindow':plan.get('globalWindow')}
    print(json.dumps({'tile':plan['id'],'nodes':len(values),'valid':valid,'bytes':len(encoded)},ensure_ascii=False),flush=True)
    return descriptor,public


def terrain_index(bounds,base,result,requested_fine_count,fine_complete=False):
    if fine_complete and len(result)!=requested_fine_count:
        raise ValueError('cannot certify a fine-grid run with missing partitions')
    return {'schemaVersion':1,'region':REGION,'bbox':bounds,'base':base,
            'tiles':[descriptor for descriptor,_ in result if descriptor['validPoints']],
            'noDataTiles':[descriptor for descriptor,_ in result if not descriptor['validPoints']],
            'coverage':{'complete':True,'scope':'commune bounding envelope, without fabrication in source NoData',
                        'fineComplete':fine_complete,'requestedFinePartitions':requested_fine_count,
                        'completedFinePartitions':len(result)},
            'license':'Licence Ouverte 2.0','attribution':'IGN — RGE ALTI'}


def audit_shared_edges(index,output):
    """Compare actual source samples on every adjacent partition boundary."""
    descriptors=index.get('tiles',[])+index.get('noDataTiles',[])
    output=Path(output);pairs=[]
    def read(descriptor):
        path=output/Path(descriptor['path']).name;raw=path.read_bytes()
        if len(raw)!=descriptor['bytes'] or hashlib.sha256(raw).hexdigest()!=descriptor['sha256']:
            raise ValueError('terrain grid changed during source-seam audit')
        return json.loads(raw)
    same=lambda a,b:abs(a-b)<1e-12
    for a in descriptors:
        ab=a['bbox']
        for b in descriptors:
            if a is b:continue
            bb=b['bbox'];direction=None
            if same(ab[3],bb[1]) and same(ab[0],bb[0]) and same(ab[2],bb[2]):direction='east-west'
            elif same(ab[0],bb[2]) and same(ab[1],bb[1]) and same(ab[3],bb[3]):direction='north-south'
            if not direction:continue
            ag,bg=read(a),read(b)
            if direction=='east-west':av,bv=ag['values'][ag['width']-1::ag['width']],bg['values'][::bg['width']]
            else:av,bv=ag['values'][-ag['width']:],bg['values'][:bg['width']]
            if len(av)!=len(bv):raise ValueError('neighbor terrain edges have inconsistent node counts')
            mismatches=sum(x!=y for x,y in zip(av,bv))
            max_difference=max((abs(x-y) for x,y in zip(av,bv) if x is not None and y is not None),default=0)
            pairs.append({'a':a['sha256'],'b':b['sha256'],'direction':direction,'nodes':len(av),
                          'mismatches':mismatches,'maximumHeightDifferenceMeters':max_difference})
    return {'partitions':len(descriptors),'fineComplete':index['coverage']['fineComplete'],
            'pairs':pairs,'comparedNodes':sum(p['nodes'] for p in pairs),
            'mismatches':sum(p['mismatches'] for p in pairs),
            'maximumHeightDifferenceMeters':max((p['maximumHeightDifferenceMeters'] for p in pairs),default=0)}


def acquire(boundary, cache, output, *, base_spacing=25, fine_spacing=10, workers=3, base_only=False, timeout=180, method='points'):
    boundary=Path(boundary)
    payload=json.loads(boundary.read_text())
    features=payload.get('features') if isinstance(payload,dict) else None
    if not isinstance(features,list) or len(features)!=1 or features[0].get('properties',{}).get('code_insee')!='13055':
        raise ValueError('requires the actual single Marseille commune code_insee=13055 FeatureCollection')
    positions=[]
    def visit(value):
        if isinstance(value,list) and len(value)>=2 and type(value[0]) in (int,float): positions.append(value)
        elif isinstance(value,list):
            for child in value: visit(child)
    visit(features[0]['geometry']['coordinates'])
    bounds=[min(p[1] for p in positions),min(p[0] for p in positions),max(p[1] for p in positions),max(p[0] for p in positions)]
    checked_bbox(bounds)
    if type(workers) is not int or not 1<=workers<=3: raise ValueError('use one to three service workers')
    cache,output=Path(cache),Path(output)
    cache.mkdir(parents=True,exist_ok=True);output.mkdir(parents=True,exist_ok=True)
    resource_file=cache/'rge-alti-resource.json'
    if not resource_file.exists():
        with urlopen(POINT_RESOURCE,timeout=60) as response: raw=response.read(1_000_001)
        if len(raw)>1_000_000:raise ValueError('point-resource metadata exceeds supported byte bound')
        atomic_write(resource_file,raw)
    resource_raw=resource_file.read_bytes();resource=json.loads(resource_raw)
    if resource.get('_id')!='ign_rge_alti_wld':raise ValueError('unexpected point-elevation resource identity')
    caps_url='https://data.geopf.fr/wms-r?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities'
    caps=cache/'wms-capabilities.xml'
    if not caps.exists():
        with urlopen(caps_url,timeout=60) as response: raw=response.read(16*1024**2+1)
        if len(raw)>16*1024**2: raise ValueError('WMS capabilities exceed discovery bound')
        atomic_write(caps,raw)
    capraw=caps.read_bytes()
    if b'<!DOCTYPE' in capraw.upper() or b'<!ENTITY' in capraw.upper(): raise ValueError('XML entities not supported')
    namespace={'w':'http://www.opengis.net/wms'}
    root=ET.fromstring(capraw)
    layers=[layer for layer in root.findall('.//w:Layer',namespace) if layer.findtext('w:Name',None,namespace)==LAYER]
    if len(layers)!=1 or 'image/geotiff' not in [n.text for n in root.findall('.//w:GetMap/w:Format',namespace)]:
        raise ValueError('numeric RGE ALTI layer or GeoTIFF format absent from actual capabilities')
    width,height,actual=grid_shape(bounds,base_spacing)
    base,base_receipt=acquire_grid({'id':'base','bbox':bounds,'width':width,'height':height,'spacingMeters':actual},cache,output,timeout,True,method,workers)
    if not base['validPoints']: raise ValueError('base terrain contains no observed elevation')
    fine_plan=[] if base_only else partitions(bounds,fine_spacing)
    result=[]
    # Runtime preflights may use the complete coarse grid while fine requests
    # run. The index states the exact partial count, never a completed 10m map.
    atomic_write(output/'terrain-index.json',canonical(terrain_index(bounds,base,result,len(fine_plan))))
    if fine_plan:
        priority_points=[(43.36,5.31),(43.296,5.37)]
        def priority(plan):
            s,w,n,e=plan['bbox']
            for i,(lat,lon) in enumerate(priority_points):
                if s<=lat<=n and w<=lon<=e:return i
            return 2
        fine_plan.sort(key=lambda plan:(priority(plan),plan['id']))
        # Point requests already use a single globally rate-limited worker pool.
        # Keep grids sequential so concurrency never multiplies by tile count.
        if method=='points':
            for plan in fine_plan:
                result.append(acquire_grid(plan,cache,output,timeout,method=method,point_workers=workers))
                atomic_write(output/'terrain-index.json',canonical(terrain_index(bounds,base,result,len(fine_plan))))
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for item in pool.map(lambda plan:acquire_grid(plan,cache,output,timeout,method=method),fine_plan):
                    result.append(item)
                    atomic_write(output/'terrain-index.json',canonical(terrain_index(bounds,base,result,len(fine_plan))))
    # Only the final index can declare all fine partitions completed.
    index=terrain_index(bounds,base,result,len(fine_plan),not base_only)
    seams=audit_shared_edges(index,output)
    if seams['mismatches']:raise ValueError('actual numeric source samples disagree on adjacent fine-grid edges')
    receipt={'schemaVersion':1,'region':REGION,'bbox':bounds,'boundaryInputSha256':hashlib.sha256(boundary.read_bytes()).hexdigest(),
             'capabilities':{'url':caps_url,'sha256':hashlib.sha256(capraw).hexdigest(),'layer':LAYER},
             'pointResource':{'url':POINT_RESOURCE,'sha256':hashlib.sha256(resource_raw).hexdigest(),'metadata':resource},
             'index':index,'base':base_receipt,'tiles':[proof for _,proof in result],
             'sharedEdges':seams,
             'method':method,
             'limits':'Nominal sample spacing is not native resolution or absolute survey accuracy. Provider sampling kernel and survey dates were not supplied. Point-API exact NoData sentinel/null and unusable provider observations are counted separately. Invalid observations retain their raw values, coordinates and response hashes in this receipt and are not assigned an invented elevation. WMS NoData contamination remains refused. No missing values are filled.'}
    atomic_write(cache/'TERRAIN_ACQUISITION.json',canonical(receipt))
    atomic_write(output/'terrain-index.json',canonical(index))
    return receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--boundary',type=Path,required=True)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'data/map_pack/city')
    parser.add_argument('--base-spacing',type=float,default=25)
    parser.add_argument('--fine-spacing',type=float,default=10)
    parser.add_argument('--workers',type=int,default=3,help='one to three concurrent point requests or WMS grids')
    parser.add_argument('--base-only',action='store_true')
    parser.add_argument('--timeout',type=float,default=180)
    parser.add_argument('--method',choices=['points','wms'],default='points',help='points avoids WMS interpolation contamination at NoData borders')
    args=parser.parse_args(argv)
    try:
        receipt=acquire(args.boundary,args.cache,args.output,base_spacing=args.base_spacing,fine_spacing=args.fine_spacing,
                        workers=args.workers,base_only=args.base_only,timeout=args.timeout,method=args.method)
    except (ValueError,OSError,ImportError,ET.ParseError) as error:
        print(f'City terrain acquisition refused: {error}',file=sys.stderr);return 1
    print(json.dumps({'base':receipt['index']['base'],'fineGrids':len(receipt['index']['tiles']),
                      'noDataGrids':len(receipt['index']['noDataTiles']),'complete':receipt['index']['coverage']['complete']}))
    return 0


if __name__=='__main__': raise SystemExit(main())
