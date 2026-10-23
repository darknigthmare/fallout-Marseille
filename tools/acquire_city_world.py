#!/usr/bin/env python3
"""Acquire the complete Marseille administrative extent as bounded IGN partitions.

Every rectangle touching the official municipality is queried completely. Source
objects are retained whole, including a border outside the municipality; no claim
is made that these object counts are strictly inside the administrative polygon.
Publication happens only after every leaf query and geometry has been verified.
"""
from __future__ import annotations

import argparse
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import acquire_public_world as public
import world_sources as sources

ROOT = Path(__file__).resolve().parents[1]
REGION = 'geo_marseille_commune'
CODE = '13055'
LAYERS = {'buildings': 'BDTOPO_V3:batiment', 'roads': 'BDTOPO_V3:troncon_de_route'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def immutable_write(path, raw):
    path = Path(path)
    if path.is_symlink() or path.exists() and (not path.is_file() or path.read_bytes() != raw):
        raise sources.SourceError('existing content-addressed city file differs; preserved unchanged')
    if not path.exists():
        sources.atomic_write(path, raw)


class Cache:
    """Exact URL/body receipts, resumed only after byte/hash verification."""
    def __init__(self, directory, network=public.read_response):
        self.directory = Path(directory)
        self.network = network
        self.receipts = []
        self.lock = threading.Lock()

    def __call__(self, url):
        key = sha(url.encode())
        raw_path = self.directory / (key + '.raw')
        receipt_path = self.directory / (key + '.json')
        if raw_path.exists() and receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            raw = raw_path.read_bytes()
            if receipt.get('url') != url or receipt.get('bytes') != len(raw) or receipt.get('sha256') != sha(raw):
                raise ValueError('cached official response differs from its receipt')
        else:
            for attempt in range(5):
                try:
                    raw = self.network(url)
                    break
                except (HTTPError, URLError, TimeoutError, OSError) as error:
                    if isinstance(error, HTTPError) and error.code not in (408, 429, 500, 502, 503, 504):
                        raise
                    if attempt == 4:
                        raise
                    time.sleep(min(12, 2 ** attempt))
            if not isinstance(raw, bytes) or not 0 < len(raw) <= public.MAX_RESPONSE:
                raise ValueError('official response exceeds the byte budget')
            receipt = {'url': url, 'bytes': len(raw), 'sha256': sha(raw),
                       'acquiredAt': dt.datetime.now(dt.timezone.utc).isoformat(), 'rawFile': raw_path.name}
            sources.atomic_write(raw_path, raw)
            sources.atomic_write(receipt_path, sources.canonical(receipt))
        with self.lock:
            self.receipts.append(receipt)
        return raw


def municipality(fetch):
    schema = public.describe_feature_type('BDTOPO_V3:commune', fetch)
    fields = {row['name'] for row in schema['fields']}
    if not {'code_insee', 'nom_officiel', 'geometrie'} <= fields:
        raise ValueError('official municipality schema is incompatible')
    query = {'SERVICE': 'WFS', 'VERSION': '2.0.0', 'REQUEST': 'GetFeature',
             'TYPENAMES': 'BDTOPO_V3:commune', 'OUTPUTFORMAT': 'application/json',
             'SRSNAME': 'urn:ogc:def:crs:OGC::CRS84', 'CQL_FILTER': "code_insee='13055'", 'COUNT': 2}
    raw = fetch(public.WFS + '?' + urlencode(query))
    result = sources.decode_json(raw)
    rows = result.get('features')
    if result.get('type') != 'FeatureCollection' or not isinstance(rows, list) or len(rows) != 1 or str(result.get('numberMatched')) != '1':
        raise ValueError('Marseille query must return exactly one administrative feature')
    feature = rows[0]
    if feature.get('properties', {}).get('code_insee') != CODE or feature['properties'].get('nom_officiel') != 'Marseille':
        raise ValueError('official administrative object is not Marseille 13055')
    geom = feature.get('geometry')
    if not isinstance(geom, dict) or geom.get('type') not in ('Polygon', 'MultiPolygon'):
        raise ValueError('municipality must have an official polygon')
    coords = list(sources.geometry_positions(geom['coordinates']))
    if not 4 <= len(coords) <= 200_000:
        raise ValueError('municipality boundary exceeds its bounded vertex budget')
    for point in coords:
        sources.position(point, 'EPSG:4326')
    polygons = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    for polygon in polygons:
        if not polygon or any(len(ring) < 4 or ring[0] != ring[-1] for ring in polygon):
            raise ValueError('official municipality has an unclosed ring')
    return result, sources.geometry_bbox(geom), schema


def rectangle_touches_polygon(box, geometry):
    """Conservative exact edge/point test; never discard an intersecting tile."""
    south, west, north, east = box
    corners = [[west, south], [east, south], [east, north], [west, north]]
    polygons = geometry['coordinates'] if geometry['type'] == 'MultiPolygon' else [geometry['coordinates']]
    for polygon in polygons:
        outer = polygon[0]
        ob = [min(p[1] for p in outer), min(p[0] for p in outer), max(p[1] for p in outer), max(p[0] for p in outer)]
        if not sources.intersects(box, ob):
            continue
        if any(west <= p[0] <= east and south <= p[1] <= north for p in outer):
            return True
        if any(sources._point_inside(outer, p) and not any(sources._point_inside(hole, p) for hole in polygon[1:]) for p in corners):
            return True
        for ring in polygon:
            for a, b in zip(ring, ring[1:]):
                if max(a[0], b[0]) < west or min(a[0], b[0]) > east or max(a[1], b[1]) < south or min(a[1], b[1]) > north:
                    continue
                if any(sources._segments_intersect(a, b, c, d) for c, d in zip(corners, corners[1:] + corners[:1])):
                    return True
    return False


def partition(bounds, geometry, step=.025):
    if not math.isfinite(step) or not .005 <= step <= .05:
        raise ValueError('partition step must be between .005 and .05 degrees')
    s, w, n, e = sources.checked_bbox(bounds)
    rows, cols = math.ceil((n - s) / step), math.ceil((e - w) / step)
    result = []
    for row in range(rows):
        for col in range(cols):
            box = [s + (n - s) * row / rows, w + (e - w) * col / cols,
                   s + (n - s) * (row + 1) / rows, w + (e - w) * (col + 1) / cols]
            if rectangle_touches_polygon(box, geometry):
                result.append({'id': f'm13055-r{row:02d}-c{col:02d}', 'queryBbox': box})
    if not result or len(result) > 1024:
        raise ValueError('municipality plan is empty or exceeds the partition budget')
    return result


def split(tile):
    s, w, n, e = tile['queryBbox']
    m, k = (s + n) / 2, (w + e) / 2
    return [{'id': tile['id'] + '-' + str(i), 'queryBbox': box}
            for i, box in enumerate(([s, w, m, k], [s, k, m, e], [m, w, n, k], [m, k, n, e]))]


def normalize_collection(collection, provider, bounds):
    """Keep anomalous source Z unavailable only when IGN explicitly says no Z.

    A real Marseille road contains -100 at one node with the joint provider
    fields 'Pas de Z' and precision 9999. The legacy -1000 handler remains
    unchanged. Raw HTTPS responses and the original collection hash retain the
    unavailable value; its XY remains intact and no replacement Z is supplied.
    """
    original_raw = sources.canonical(collection)
    prepared, anomalies, borders = copy.deepcopy(collection), {}, {}
    normalization_bounds = list(bounds)
    for feature in prepared['features']:
        props = feature.get('properties') or {}
        box = sources.geometry_bbox(feature['geometry'])
        if not sources.intersects(box, bounds):
            dy = max(bounds[0] - box[2], box[0] - bounds[2], 0) * 111320
            dx = max(bounds[1] - box[3], box[1] - bounds[3], 0) * 111320 * math.cos(math.radians((bounds[0] + bounds[2]) / 2))
            distance = math.hypot(dx, dy)
            if distance > 2:
                raise sources.SourceError('official WFS object lies more than two metres outside the municipality envelope: ' + str(feature.get('id')))
            borders[str(feature['id'])] = {'municipalityBbox': list(bounds), 'sourceGeometryBbox': box,
                                          'minimumSeparationMeters': distance,
                                          'condition': 'Whole object returned by the completed official WFS rectangle query; conservative spatial-index border result',
                                          'action': 'Original XY retained; no snapping, clipping or correction of the measured geometry'}
            normalization_bounds = [min(normalization_bounds[0], box[0]), min(normalization_bounds[1], box[1]),
                                    max(normalization_bounds[2], box[2]), max(normalization_bounds[3], box[3])]
        if provider.get('resource') != 'ign-bdtopo' or props.get('methode_d_acquisition_altimetrique') != 'Pas de Z' or props.get('precision_altimetrique') != 9999:
            continue
        removed = []
        def clean(value):
            if isinstance(value, list) and value and type(value[0]) in (int, float):
                if len(value) == 3 and type(value[2]) in (int, float) and value[2] != -1000 and not -100 < value[2] < 9000:
                    removed.append(value[2])
                    return value[:2]
                return value
            return [clean(row) for row in value] if isinstance(value, list) else value
        original_feature = sources.canonical(feature)
        feature['geometry']['coordinates'] = clean(feature['geometry']['coordinates'])
        if removed:
            anomalies[str(feature['id'])] = {'condition': 'IGN BD TOPO: methode_d_acquisition_altimetrique = Pas de Z AND precision_altimetrique = 9999',
                                            'removedCoordinates': len(removed), 'unavailableSourceValues': sorted(set(removed)),
                                            'originalFeatureSha256': sha(original_feature),
                                            'action': 'XY retained; out-of-range source Z explicitly unavailable, no altitude supplied'}
    result = sources.read_geojson(sources.canonical(prepared), provider, normalization_bounds)
    for feature in result:
        feature['properties']['provenance']['inputSha256'] = sha(original_raw)
        if feature['id'] in anomalies:
            feature['properties']['provenance']['sourceGeometryZUnavailable'] = anomalies[feature['id']]
        if feature['id'] in borders:
            feature['properties']['provenance']['sourceGeometryAdministrativeBorder'] = borders[feature['id']]
    return result


def descriptor(tile, bundle, raw):
    features = bundle['features']
    boxes = [tile['queryBbox']] + [sources.geometry_bbox(f['geometry']) for f in features]
    render_boxes = [tile['queryBbox']] + [sources.geometry_bbox(f['geometry']) for f in features if f['properties']['kind'] == 'building']
    bounds = [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]
    render_bounds = [min(b[0] for b in render_boxes), min(b[1] for b in render_boxes), max(b[2] for b in render_boxes), max(b[3] for b in render_boxes)]
    digest = sha(raw)
    return {'id': tile['id'], 'region': REGION, 'path': 'data/map_pack/city/' + tile['id'] + '-' + digest[:16] + '.json',
            'sha256': digest, 'bytes': len(raw), 'bbox': bounds, 'queryBbox': tile['queryBbox'], 'renderBbox': render_bounds,
            'counts': {'buildings': sum(f['properties']['kind'] == 'building' for f in features),
                       'roads': sum(f['properties']['kind'] == 'road' for f in features)}, 'coverages': bundle['coverages']}


def cached_leaf(tile, collections, providers, output):
    """Reuse an immutable accepted leaf only against current exact input hashes.

    Geometry is still fully validated by the final dataset/archive validator.
    This is an acquisition checkpoint, never a partial published city index.
    """
    expected = {('building' if kind == 'buildings' else 'road'): (sha(sources.canonical(collection)), collection)
                for kind, collection in collections.items()}
    for path in sorted(output.glob(tile['id'] + '-*.json')):
        suffix = path.name[len(tile['id']) + 1:]
        if len(suffix) != 21 or any(c not in '0123456789abcdef' for c in suffix[:16]) or suffix[16:] != '.json':
            continue
        if path.is_symlink():
            raise sources.SourceError('accepted city leaf symlink is refused')
        raw = sources.bounded_bytes(path)
        if sha(raw)[:16] != suffix[:16]:
            raise sources.SourceError('accepted city leaf differs from its content-addressed name')
        bundle = sources.decode_json(raw)
        if bundle.get('schemaVersion') != 1 or bundle.get('region') != REGION or bundle.get('queryBbox') != tile['queryBbox'] or bundle.get('sources') != providers or not isinstance(bundle.get('features'), list):
            continue
        if len(bundle['features']) > 3000 or len(raw) > 8 * 1024 * 1024:
            continue
        coverages = [collections[kind]['acquisitionCoverage'] for kind in LAYERS]
        if bundle.get('coverages') != coverages:
            continue
        actual = {'building': {}, 'road': {}}
        valid = True
        for feature in bundle['features']:
            props = feature.get('properties') or {}
            kind, identity = props.get('kind'), props.get('sourceId')
            if kind not in actual or not isinstance(identity, str) or identity in actual[kind] or props.get('provenance', {}).get('inputSha256') != expected[kind][0]:
                valid = False
                break
            actual[kind][identity] = feature
        if not valid:
            continue
        for kind, (_, collection) in expected.items():
            if set(actual[kind]) != {str(f.get('id')) for f in collection['features']}:
                valid = False
                break
            # The declared input hash is not a proof that a cached output still
            # represents that input. Compare original coordinates and attributes
            # as well; only the narrowly documented unavailable-Z omissions are
            # accepted, never a changed XY or a synthesized source attribute.
            for original in collection['features']:
                identity = str(original.get('id'))
                accepted = actual[kind][identity]
                original_props = original.get('properties') or {}
                expected_props = {**original_props, 'kind': kind, 'sourceId': identity}
                props = accepted['properties']
                if accepted.get('type') != 'Feature' or accepted.get('id') != identity or {k: v for k, v in props.items() if k != 'provenance'} != expected_props:
                    valid = False
                    break
                provider = providers[0 if kind == 'building' else 1]
                expected_proof = {'source': provider['name'], **{key: value for key, value in provider.items() if key != 'name'},
                                  'inputCrs': 'EPSG:4326', 'coverage': collection['acquisitionCoverage']}
                if any(props['provenance'].get(key) != value for key, value in expected_proof.items()):
                    valid = False
                    break
                no_z = provider.get('resource') == 'ign-bdtopo' and original_props.get('methode_d_acquisition_altimetrique') == 'Pas de Z'
                no_z_precision = original_props.get('precision_altimetrique') == 9999
                def expected_coordinates(value):
                    if isinstance(value, list) and value and type(value[0]) in (int, float):
                        if len(value) == 3 and no_z and (value[2] == -1000 or no_z_precision and type(value[2]) in (int, float) and not -100 < value[2] < 9000):
                            return value[:2]
                        return value
                    return [expected_coordinates(row) for row in value] if isinstance(value, list) else value
                original_geometry = original.get('geometry') or {}
                expected_geometry = {'type': original_geometry.get('type'), 'coordinates': expected_coordinates(original_geometry.get('coordinates'))}
                if accepted.get('geometry') != expected_geometry:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            return descriptor(tile, bundle, raw)
    return None


def acquire_tile(tile, fetch, advertised, output, boundary_bbox, date):
    providers, features, coverages, counts, collections = [], [], [], {}, {}
    try:
        for kind, layer in LAYERS.items():
            result = public.fetch_features(layer, tile['queryBbox'], fetch=fetch, advertised_layers=advertised)
            provider = sources.provenance(name='IGN BD TOPO — ' + layer, license=public.LICENSE,
                                          attribution='IGN — Géoplateforme', acquired_at=date,
                                          resource='ign-bdtopo', url=public.WFS, vertical_datum='NGF-IGN69')
            providers.append(provider)
            coverages.append(result['acquisitionCoverage'])
            counts[kind] = len(result['features'])
            collections[kind] = result
            if sum(counts.values()) > 3000:
                raise ValueError('combined partition exceeds the feature/vertex bound')
        cached = cached_leaf(tile, collections, providers, output)
        if cached is not None:
            return [cached]
        for (kind, result), provider in zip(collections.items(), providers):
            if result['features']:
                features.extend(normalize_collection(result, provider, boundary_bbox))
        counter = sum(1 for f in features for _ in sources.geometry_positions(f['geometry']['coordinates']))
        if counter > sources.MAX_VERTICES or len(features) > 3000:
            raise ValueError('combined partition exceeds the feature/vertex bound')
        bundle = {'schemaVersion': 1, 'region': REGION, 'source': sources._source_summary(providers),
                  'sources': providers, 'features': features, 'queryBbox': tile['queryBbox'], 'coverages': coverages}
        raw = sources.canonical(bundle)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError('combined partition exceeds the byte bound')
        digest = sha(raw)
        filename = tile['id'] + '-' + digest[:16] + '.json'
        immutable_write(output / filename, raw)
        return [descriptor(tile, bundle, raw)]
    except ValueError as error:
        message = str(error)
        if not any(text in message for text in ('exceeds the feature bound', 'exceeds the vertex budget', 'exceeds the feature/vertex bound', 'exceeds the byte bound')):
            raise
        if tile['id'].count('-') >= 6:
            raise ValueError('source remains over budget after four subdivisions') from error
        result = []
        for child in split(tile):
            result.extend(acquire_tile(child, fetch, advertised, output, boundary_bbox, date))
        return result


def acquire(cache, output, *, workers=3, step=.025, dry_run=False, replace=False):
    if not 1 <= workers <= 4:
        raise ValueError('workers must be between one and four')
    cache, output = Path(cache), Path(output)
    fetch = Cache(cache / 'http')
    boundary, bounds, schema = municipality(fetch)
    plan = partition(bounds, boundary['features'][0]['geometry'], step)
    public.atomic_json(cache / 'plan.json', {'municipality': CODE, 'bbox': bounds, 'tiles': plan})
    print(json.dumps({'municipality': CODE, 'bbox': bounds, 'plannedTiles': len(plan), 'workers': workers}), flush=True)
    if dry_run:
        return {'status': 'plan only', 'tiles': plan}
    advertised = public.wfs_layers(fetch)
    schemas = {kind: public.validate_feature_schema(kind, public.describe_feature_type(layer, fetch)) for kind, layer in LAYERS.items()}
    date = min(row['acquiredAt'][:10] for row in fetch.receipts)
    output.mkdir(parents=True, exist_ok=True)
    descriptors = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = {executor.submit(acquire_tile, tile, fetch, advertised, output, bounds, date): tile for tile in plan}
        for future in as_completed(pending):
            tile = pending[future]
            try:
                rows = future.result()
            except Exception as error:
                public.atomic_json(cache / 'failure.json', {'tile': tile, 'error': str(error), 'completedTiles': len(descriptors)})
                raise
            descriptors.extend(rows)
            print(json.dumps({'completed': tile['id'], 'leafTiles': len(rows), 'buildings': sum(r['counts']['buildings'] for r in rows),
                              'roads': sum(r['counts']['roads'] for r in rows), 'done': len(descriptors), 'planned': len(plan)}), flush=True)
    boundary_raw = sources.canonical(boundary)
    boundary_digest = sha(boundary_raw)
    boundary_name = 'boundary-' + boundary_digest[:16] + '.json'
    immutable_write(output / boundary_name, boundary_raw)
    unique = {'building': {}, 'road': {}}
    unavailable_z, administrative_border = set(), set()
    total_bytes = 0
    for descriptor in descriptors:
        raw = (output / Path(descriptor['path']).name).read_bytes()
        total_bytes += len(raw)
        for feature in json.loads(raw)['features']:
            props = feature['properties']
            if props['provenance'].get('sourceGeometryZUnavailable'):
                unavailable_z.add((props['kind'], props['sourceId']))
            if props['provenance'].get('sourceGeometryAdministrativeBorder'):
                administrative_border.add((props['kind'], props['sourceId']))
            original = {'geometry': feature['geometry'], 'properties': {k: v for k, v in props.items() if k != 'provenance'}}
            fingerprint = sha(sources.canonical(original))
            prior = unique[props['kind']].setdefault(props['sourceId'], fingerprint)
            if prior != fingerprint:
                raise ValueError('source feature changed between adjacent partition queries: ' + props['sourceId'])
    index = {'schemaVersion': 1, 'crs': 'EPSG:4326', 'region': REGION,
             'municipality': {'code': CODE, 'name': 'Marseille', 'bbox': bounds,
                              'boundary': {'path': 'data/map_pack/city/' + boundary_name, 'sha256': boundary_digest, 'bytes': len(boundary_raw)},
                              'source': {'name': 'IGN BD TOPO — commune', 'license': public.LICENSE, 'attribution': 'IGN — Géoplateforme',
                                         'acquiredAt': date, 'resource': 'ign-bdtopo', 'url': public.WFS}},
             'coverage': {'complete': True, 'tileCount': len(descriptors), 'queryTileCount': len(plan),
                          'partitionStepDegrees': step,
                          'method': 'Every rectangle intersecting the official municipality polygon queried completely for both advertised layers',
                          'objectScope': 'Whole source objects returned by completed WFS rectangle queries, including conservative spatial-index border results outside Marseille',
                          'uniqueBuildings': len(unique['building']), 'uniqueRoads': len(unique['road']), 'expandedBytes': total_bytes},
             'tiles': sorted(descriptors, key=lambda row: row['id'])}
    index['coverage'].update(nonAcquiredZAnomalies=len(unavailable_z), administrativeEnvelopeBorderObjects=len(administrative_border))
    # The previous published index remains usable until all immutable chunks and
    # both authoritative query layers have passed the complete acquisition.
    index_raw = sources.canonical(index)
    index_path = output / 'index.json'
    if index_path.is_symlink() or index_path.exists() and not replace and index_path.read_bytes() != index_raw:
        raise ValueError('city index already has another accepted source set; use --replace explicitly')
    sources.atomic_write(index_path, index_raw)
    receipt = {'schemaVersion': 1, 'acquiredAt': date, 'municipality': index['municipality'], 'coverage': index['coverage'],
               'schemas': {'boundary': schema, **schemas}, 'requests': sorted(fetch.receipts, key=lambda row: row['url']),
               'indexSha256': sha(sources.canonical(index)), 'indexBytes': len(sources.canonical(index))}
    public.atomic_json(cache / 'ACQUISITION.json', receipt)
    return index['coverage']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('/workspace/.cloud-setup/fallout-marseille/city-acquisition'))
    parser.add_argument('--output', type=Path, default=ROOT / 'data/map_pack/city')
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--step', type=float, default=.025)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--replace', action='store_true', help='Explicitly replace an existing published city index after complete acquisition')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(acquire(args.cache, args.output, workers=args.workers, step=args.step, dry_run=args.dry_run, replace=args.replace), ensure_ascii=False), flush=True)
        return 0
    except (ValueError, OSError) as error:
        print('Acquisition de Marseille refusée : ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
