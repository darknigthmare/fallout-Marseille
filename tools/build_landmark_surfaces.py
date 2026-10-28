#!/usr/bin/env python3
"""Clip official native MNS triangles to unchanged IGN landmark footprints.

The three GeoTIFFs are downloaded only from their already acquired IGN metadata
url_mns. Elevations at native pixel centres remain Float32 source values;
vertices introduced by footprint clipping use triangle-plane interpolation.
No silhouette, opening, statue, room or semantic roof plane is invented.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TILES = ('0891-6248', '0892-6248', '0892-6246')
CHUNKS = ('m13055-r05-c05-e010c49d49243bae.json', 'm13055-r04-c06-2-0-8dc4e4c60da6c304.json')
SITES = ('Cathédrale de la Major', 'Notre-Dame de la Garde')


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def lambert(lon, lat):
    e, n, c = .0818191910428158, .725607765053267, 11754255.426096
    phi = math.radians(lat)
    s = math.sin(phi)
    value = math.log(math.tan(math.pi/4+phi/2)*((1-e*s)/(1+e*s))**(e/2))
    r, g = c*math.exp(-n*value), n*math.radians(lon-3)
    return [700000+r*math.sin(g), 12655612.049876-r*math.cos(g)]


def request(feature):
    p = feature['properties']
    url = p['url_mns']
    parsed = urlsplit(url)
    q = {k.upper(): v for k, v in parse_qs(parsed.query).items()}
    if parsed.scheme != 'https' or parsed.hostname != 'data.geopf.fr' or parsed.path != '/wms-r' or parsed.username or parsed.password:
        raise ValueError('MNS URL must be the official HTTPS metadata URL')
    expected = {'SERVICE': ['WMS'], 'REQUEST': ['GetMap'], 'CRS': ['EPSG:2154'],
                'LAYERS': ['IGNF_LIDAR-HD_MNS_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93'], 'FORMAT': ['image/geotiff']}
    if any(q.get(k) != v for k, v in expected.items()) or p['systeme_altimetrique'] != 'IGN69' or p['systeme_planimetrique'] != 'LAMB93':
        raise ValueError('Incompatible MNS service or datum')
    return {'url': url, 'bounds': [float(x) for x in q['BBOX'][0].split(',')],
            'size': [int(q['WIDTH'][0]), int(q['HEIGHT'][0])]}


def clipped_surface(feature, rasters):
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.ops import triangulate
    geometry = feature['geometry']
    groups = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    footprints = [Polygon([lambert(*p[:2]) for p in rings[0]],
                          [[lambert(*p[:2]) for p in ring] for ring in rings[1:]]) for rings in groups]
    footprint = MultiPolygon(footprints) if len(footprints) > 1 else footprints[0]
    if not footprint.is_valid or footprint.area <= 0:
        raise ValueError('Invalid official footprint')
    vertices, faces, index = [], [], {}
    native_vertices = clipped_vertices = 0
    native_checks = []
    def vertex(x, y, z, native):
        nonlocal native_vertices, clipped_vertices
        key = (round(x, 8), round(y, 8))
        if key in index:
            i = index[key]
            if abs(vertices[i][2]-z) > 2e-5:
                raise ValueError('Nonconforming MNS seam')
            return i
        i = len(vertices)
        index[key] = i
        vertices.append([x, y, z])
        if native:
            native_vertices += 1
            if len(native_checks) < 32 or i % 107 == 0:
                native_checks.append({'vertex': i, 'elevation': z})
        else:
            clipped_vertices += 1
        return i
    area = 0.
    used = []
    for raster, receipt in rasters:
        west, south, east, north = footprint.bounds
        if east < raster.bounds.left or west > raster.bounds.right or north < raster.bounds.bottom or south > raster.bounds.top:
            continue
        used.extend(receipt.get('sourceHashes', [receipt['sha256']]))
        x0, y0 = raster.xy(0, 0)
        step = raster.res[0]
        c0, c1 = max(0, math.floor((west-x0)/step)), min(raster.width-2, math.ceil((east-x0)/step))
        r0, r1 = max(0, math.floor((y0-north)/step)), min(raster.height-2, math.ceil((y0-south)/step))
        from rasterio.windows import Window
        data = raster.read(1, window=Window(c0, r0, c1-c0+2, r1-r0+2))
        for row in range(r0, r1+1):
            for col in range(c0, c1+1):
                x, y = x0+col*step, y0-row*step
                coords = [(x,y), (x+step,y), (x,y-step), (x+step,y-step)]
                heights = [float(data[row-r0+dr,col-c0+dc]) for dr,dc in [(0,0),(0,1),(1,0),(1,1)]]
                for ids in [(0,2,1),(1,2,3)]:
                    points = [coords[i] for i in ids]
                    triangle = Polygon(points)
                    overlap = triangle.intersection(footprint)
                    if overlap.is_empty or overlap.area < 1e-12:
                        continue
                    if any(not math.isfinite(heights[i]) or heights[i] == raster.nodata for i in ids):
                        raise ValueError('MNS NoData intersects the source footprint')
                    parts = [overlap] if overlap.geom_type == 'Polygon' else [p for p in getattr(overlap, 'geoms', []) if p.geom_type == 'Polygon']
                    a,b,c = points
                    za,zb,zc = [heights[i] for i in ids]
                    den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                    def elevation(px, py):
                        for index,p in enumerate(points):
                            if math.dist((px,py),p)<1e-8:
                                return [za,zb,zc][index]
                        u = ((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
                        v = ((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den
                        return u*za+v*zb+(1-u-v)*zc
                    for part in parts:
                        for t in triangulate(part):
                            if not part.covers(t) or t.area < 1e-12:
                                continue
                            ring = list(t.exterior.coords)[:3]
                            ids_out = [vertex(px,py,elevation(px,py), any(math.dist((px,py),p)<1e-8 for p in points)) for px,py in ring]
                            faces.append(ids_out)
                            area += t.area
    if abs(area-footprint.area) > max(.0001, footprint.area*1e-7):
        raise ValueError(f'MNS clipping incomplete: {area} != {footprint.area}')
    if not faces or len(faces) > 60000 or len(vertices) > 40000:
        raise ValueError('MNS mesh outside its bounded budget')
    edges = {}
    for f in faces:
        for a,b in zip(f, f[1:]+f[:1]):
            key = tuple(sorted((a,b)))
            edges[key] = edges.get(key,0)+1
    if any(n > 2 for n in edges.values()):
        raise ValueError('Nonmanifold source mesh')
    boundary = [list(edge) for edge,n in edges.items() if n == 1]
    boundary_length = sum(math.dist(vertices[a][:2],vertices[b][:2]) for a,b in boundary)
    if abs(boundary_length-footprint.length) > .002:
        raise ValueError('Boundary contains an interior crack')
    props = feature['properties']
    return {'cleabs': props['cleabs'], 'sourceId': props['sourceId'], 'rawGeometry': geometry,
            'sourceProperties': {k:props.get(k) for k in ['altitude_minimale_sol','altitude_maximale_sol','altitude_minimale_toit','altitude_maximale_toit','hauteur','nombre_d_etages']},
            'vertices': vertices, 'faces': faces, 'boundary': boundary,
            'sourceTileSha256': used,
            'measurements': {'footprintAreaSquareMetres': footprint.area, 'roofProjectedAreaSquareMetres': area,
                             'boundaryLengthMetres': boundary_length, 'sourceBoundaryLengthMetres': footprint.length,
                             'minimumElevation': min(p[2] for p in vertices), 'maximumElevation': max(p[2] for p in vertices),
                             'nativeVertices': native_vertices, 'clippedVertices': clipped_vertices, 'nativeChecks': native_checks}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'data/map_pack/landmark_surfaces')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    import rasterio
    from acquire_ign_dem import Client
    args.cache.mkdir(parents=True, exist_ok=True)
    metadata_raw = args.metadata.read_bytes()
    metadata = json.loads(metadata_raw)
    if metadata['numberMatched'] != metadata['numberReturned'] or metadata['numberReturned'] != len(metadata['features']):
        raise ValueError('Truncated original metadata')
    rasters, receipts, memory_files, composites = [], [], [], []
    try:
        for tile in TILES:
            feature = next(f for f in metadata['features'] if f['properties']['coordonnees_nw'] == tile)
            req = request(feature)
            path = args.cache/(tile+'-mns.tif')
            if not path.exists():
                if args.offline:
                    raise ValueError('Native MNS tile missing offline')
                path.write_bytes(Client(120).read(req['url'], 24*1024**2))
            raw = path.read_bytes()
            raster = rasterio.open(path)
            if raster.count != 1 or raster.dtypes != ('float32',) or [raster.width,raster.height] != req['size'] or raster.res != (.5,.5) or raster.nodata != -9999 or any(abs(a-b)>1e-6 for a,b in zip(raster.bounds,req['bounds'])):
                raise ValueError('Unexpected native MNS raster geometry')
            receipt = {'feature': feature, 'sha256': sha(raw), 'bytes': len(raw), 'filename': path.name,
                       'header': {'crsWkt': raster.crs.to_wkt(), 'bounds': list(raster.bounds), 'size': [raster.width,raster.height], 'resolutionMeters': [.5,.5], 'nodata': -9999},
                       'checksumScope': 'Received verified-HTTPS bytes; no independent upstream checksum published.'}
            rasters.append((raster,receipt)); receipts.append(receipt)
        # Adjacent native grids share a 0.5 m centre-to-centre seam. Concatenate
        # their unchanged Float32 cells before triangulation; separate clipping
        # would otherwise omit the strip between their last/first centres.
        import numpy as np
        from rasterio.io import MemoryFile
        left,right = rasters[:2]
        a,b = left[0],right[0]
        if a.height != b.height or a.bounds.top != b.bounds.top or abs(a.bounds.right-b.bounds.left)>1e-8:
            raise ValueError('MNS source tiles do not share their declared seam')
        memory = MemoryFile(); memory_files.append(memory)
        profile = a.profile.copy(); profile['width'] = a.width+b.width
        composite = memory.open(**profile)
        composite.write(np.concatenate([a.read(1),b.read(1)],axis=1),1)
        composites.append(composite)
        surfaces = [(composite, {'sha256':None,'sourceHashes':[left[1]['sha256'],right[1]['sha256']]}),rasters[2]]
        catalogue = json.loads((ROOT/'implementation/architecture-continuation/IGN_SITE_CONTEXT_CATALOGUE.json').read_text())
        candidates = {c['cleabs']:row['name'] for row in catalogue['rows'] if row['name'] in SITES for c in row['candidates']}
        features = {}
        input_hashes = {}
        for name in CHUNKS:
            path = ROOT/'data/map_pack/city'/name
            raw = path.read_bytes(); input_hashes[str(path.relative_to(ROOT))] = sha(raw)
            for f in json.loads(raw)['features']:
                if f['properties'].get('cleabs') in candidates:
                    features[f['properties']['cleabs']] = f
        if set(features) != set(candidates):
            raise ValueError('An original source landmark candidate is absent')
        records = []
        for cleabs,feature in sorted(features.items()):
            record = clipped_surface(feature,surfaces)
            record['siteContext'] = candidates[cleabs]
            records.append(record)
            print(cleabs, len(record['vertices']), len(record['faces']), record['measurements']['minimumElevation'],record['measurements']['maximumElevation'],flush=True)
        payload = {'schemaVersion': 1, 'kind':'ign-native-mns-landmark-surfaces', 'frame':'EPSG:2154-NGF-IGN69',
                   'source': {'provider':'IGN', 'product':'MNS LiDAR HD', 'license':'Licence Ouverte 2.0', 'attribution':'IGN — Géoplateforme, LiDAR HD et BD TOPO',
                              'nativeSpacingMeters': .5, 'metadataSha256':sha(metadata_raw), 'tiles': receipts},
                   'interpolation':'Native pixel centres preserved; new clipped vertices use their original raster triangle plane.',
                   'scope':'Measured upper visible surface within unchanged BD TOPO XY; not semantic roof planes, facades, rooms or a full monument survey.',
                   'inputHashes':input_hashes, 'records':records}
        raw = canonical(payload); checksum = sha(raw)
        args.output.mkdir(parents=True,exist_ok=True)
        name = 'marseille-mns-'+checksum[:16]+'.json'
        (args.output/name).write_bytes(raw)
        index = {'schemaVersion':1,'surface':{'path':'data/map_pack/landmark_surfaces/'+name,'sha256':checksum,'bytes':len(raw)},
                 'recordCount':len(records),'siteContexts':list(SITES),'scope':payload['scope']}
        (args.output/'index.json').write_bytes(canonical(index))
        print(json.dumps({'sha256':checksum,'bytes':len(raw),'records':len(records),'faces':sum(len(r['faces']) for r in records)},ensure_ascii=False))
    finally:
        for composite in composites:
            composite.close()
        for memory in memory_files:
            memory.close()
        for raster,_ in rasters:
            raster.close()


if __name__ == '__main__':
    main()
