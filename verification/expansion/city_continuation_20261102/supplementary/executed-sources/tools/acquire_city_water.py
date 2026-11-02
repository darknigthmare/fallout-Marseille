#!/usr/bin/env python3
"""Derive a bounded sea atlas from official open-water and high-water shoreline.

No altitude or administrative land mask classifies the sea. The connected sea
face is selected by overlap with the official BD CARTO open-water polygon; its
shoreline follows actual BD TOPO high-water lines. Rectangle cuts are declared
clipping boundaries. No simplification, snapping or invented shoreline is used.
Shapely is required only during acquisition, never by runtime atlas validation.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import math
from urllib.parse import urlencode

from acquire_city_world import Cache
from acquire_public_world import WFS
from city_water_sources import BOUNDS, PREFIX, validate_directory_files
from world_sources import SourceError, atomic_write, canonical, geometry


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def query_url(layer, condition, count=1000):
    return WFS + '?' + urlencode(dict(SERVICE='WFS', VERSION='2.0.0', REQUEST='GetFeature', TYPENAMES=layer,
                                      OUTPUTFORMAT='application/json', SRSNAME='EPSG:4326',
                                      CQL_FILTER=condition, COUNT=count, SORTBY='cleabs', STARTINDEX=0))


def acquire(cache, output):
    from shapely.geometry import shape, box, mapping, Polygon, MultiPolygon
    from shapely.ops import polygonize, unary_union
    fetch = Cache(cache)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    def tx(lon):
        return math.floor((lon + 180) / 360 * 2**14)
    def ty(lat):
        return math.floor((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2**14)
    def lon(x):
        return x / 2**14 * 360 - 180
    def lat(y):
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2*y/2**14))))
    original_s, original_w, original_n, original_e = BOUNDS
    grid = {'zoom': 14, 'minX': tx(original_w), 'maxX': tx(original_e), 'minY': ty(original_n), 'maxY': ty(original_s)}
    s, w, n, e = lat(grid['maxY']+1), lon(grid['minX']), lat(grid['minY']), lon(grid['maxX']+1)
    atlas_bounds = [s,w,n,e]
    query = f"BBOX(geometrie,{w},{s},{e},{n},'EPSG:4326') AND nature='Eau libre'"
    coast = f"BBOX(geometrie,{w-.02},{s-.02},{e+.02},{n+.02},'EPSG:4326') AND niveau='Plus hautes eaux'"
    urls = [query_url('BDCARTO_V5:occupation_du_sol', query), query_url('BDTOPO_V3:limite_terre_mer', coast)]
    receipts, collections = [], []
    def store(value):
        raw = canonical(value)
        digest = sha(raw)
        name = 'water-' + digest[:16] + '.json'
        target = output / name
        if target.exists() and target.read_bytes() != raw:
            raise SourceError('immutable water source path collision')
        if not target.exists():
            atomic_write(target, raw)
        return {'path': PREFIX + name, 'bytes': len(raw), 'sha256': digest}
    for url in urls:
        raw = fetch(url)
        payload = json.loads(raw)
        features = payload.get('features', [])
        if type(payload.get('numberMatched')) is not int or payload['numberMatched'] != len(features) or payload.get('numberReturned') != len(features):
            raise SourceError('official water query is incomplete; reduce bounds or paginate')
        receipts.append(store({'schemaVersion': 1, 'role': 'source-response', 'url': url, 'bytes': len(raw), 'sha256': sha(raw), 'body': raw.decode('utf-8')}))
        collections.append(features)
    clip = box(w, s, e, n)
    candidates = [(f, shape(f['geometry']).intersection(clip)) for f in collections[0] if f['properties'].get('nature') == 'Eau libre']
    if not candidates:
        raise SourceError('no authoritative open-water source exists in the query')
    # The largest connected open-water source in this coastal extent is the
    # Mediterranean. Its source ID is recorded, not guessed from zero heights.
    sea_feature, coarse_sea = max(candidates, key=lambda pair: pair[1].area)
    if not coarse_sea.is_valid or coarse_sea.area < .005:
        raise SourceError('the authoritative coastal sea seed is invalid or too small')
    lines = []
    for feature in collections[1]:
        if feature['properties'].get('niveau') != 'Plus hautes eaux':
            raise SourceError('unexpected shoreline reference level')
        line = shape(feature['geometry'])
        if not line.is_valid or line.geom_type not in ('LineString', 'MultiLineString'):
            raise SourceError('invalid official high-water line')
        lines.append(line.intersection(clip))
    faces = list(polygonize(unary_union([clip.boundary, *lines])))
    if not faces:
        raise SourceError('official shoreline failed to form bounded coastal faces')
    sea = max(faces, key=lambda polygon: polygon.intersection(coarse_sea).area)
    overlap = sea.intersection(coarse_sea).area / coarse_sea.area
    if overlap < .85 or not sea.is_valid:
        raise SourceError('source-derived sea face lacks a sufficient authoritative seed overlap')
    source = {'source': 'IGN BD TOPO high-water shoreline / BD CARTO open water', 'license': 'Licence Ouverte 2.0',
              'attribution': 'IGN — Géoplateforme', 'acquiredAt': dt.datetime.now(dt.timezone.utc).date().isoformat(),
              'resource': 'ign-city-water', 'url': WFS}
    descriptors = []
    discarded = []
    def bounded_parts(polygon, depth=0):
        if polygon.area <= 1e-14:
            discarded.append({'areaDegreesSquared':polygon.area,'geometrySha256':sha(canonical(json.loads(json.dumps(mapping(polygon)))))})
            return []
        if all(len(r.coords)<=2048 for r in [polygon.exterior,*polygon.interiors]):
            return [polygon]
        if depth>=8:
            raise SourceError('water polygon remains over the vertex budget after exact subdivision')
        a,b,c,d=polygon.bounds;mx,my=(a+c)/2,(b+d)/2;out=[]
        for rect in [box(a,b,mx,my),box(mx,b,c,my),box(a,my,mx,d),box(mx,my,c,d)]:
            part=polygon.intersection(rect)
            polygons=[part] if isinstance(part,Polygon) else list(part.geoms) if isinstance(part,MultiPolygon) else [g for g in getattr(part,'geoms',[]) if isinstance(g,Polygon)]
            for p in polygons:
                if not p.is_empty:out.extend(bounded_parts(p,depth+1))
        return out
    for x in range(grid['minX'], grid['maxX'] + 1):
        for y in range(grid['minY'], grid['maxY'] + 1):
            bounds = [max(s, lat(y+1)), max(w, lon(x)), min(n, lat(y)), min(e, lon(x+1))]
            if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]:
                continue
            clipped = sea.intersection(box(bounds[1], bounds[0], bounds[3], bounds[2]))
            if clipped.is_empty or clipped.area <= 0:
                continue
            polys = [clipped] if isinstance(clipped, Polygon) else list(clipped.geoms) if isinstance(clipped, MultiPolygon) else [g for g in clipped.geoms if isinstance(g, Polygon)]
            features, counter = [], [0]
            pieces=[]
            for polygon in polys:pieces.extend(bounded_parts(polygon))
            for i, polygon in enumerate(pieces):
                geom = geometry(json.loads(json.dumps(mapping(polygon))), 'EPSG:4326', counter)
                identity = f'ign-sea:14:{x}:{y}:{i}'
                features.append({'type': 'Feature', 'id': identity, 'geometry': geom,
                                 'properties': {'kind': 'water', 'class': 'ocean', 'v051Water': True, 'sourceId': identity, 'provenance': source}})
            if features:
                tile = {'z': 14, 'x': x, 'y': y}
                descriptor = store({'schemaVersion': 1, 'role': 'water-tile', 'bbox': bounds, 'tile': tile, 'source': source, 'features': features})
                descriptor.update(tile=tile, bbox=bounds, features=len(features), vertices=counter[0])
                descriptors.append(descriptor)
    index = {'schemaVersion': 1, 'crs': 'EPSG:4326', 'bbox': atlas_bounds, 'municipalityBbox':BOUNDS, 'grid':grid, 'source': source, 'inputs': receipts, 'tiles': descriptors,
             'derivation': {'algorithm': 'Exact GEOS intersection and planar polygonization; no coordinate snapping or simplification',
                            'noSimplification': True, 'sourceSeedId': sea_feature['id'], 'shorelineFeatures': len(lines),
                            'polygonizedFaces': len(faces), 'seaSeedOverlapRatio': overlap, 'seaHoles': len(sea.interiors),
                            'shorelineLevel': 'Plus hautes eaux', 'renderSeaLevelMetres': 0,
                            'renderSeaLevelBasis': 'Nominal game sea surface, not an instantaneous tidal measurement',
                            'artificialEdges': 'Outer XYZ tile coverage rectangle, XYZ tile cuts, and exact polygon subdivision only',
                            'unsupportedTinyFragments':discarded}}
    atomic_write(output / 'water-index.json', canonical(index))
    validate_directory_files(output)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    index = acquire(args.cache, args.output)
    print(json.dumps({'tiles': len(index['tiles']), 'source': index['source'], 'derivation': index['derivation']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
