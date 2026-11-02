#!/usr/bin/env python3
"""Acquire bounded official IGN extracts for the optional local world overlay.

The terrain endpoint samples RGE ALTI at the requested nodes; a 1 m request is
not a claim that every underlying source measurement has a native 1 m spacing.
TLS validation and the environment's proxy policy remain enabled. Downloads are
kept outside the shipped map pack until the source importer accepts them.
"""
from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlencode, parse_qs, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import install_terrain_v039 as terrain

ROOT = Path(__file__).resolve().parents[1]
WFS = 'https://data.geopf.fr/wfs/ows'
MAX_POINTS = 262_144
MAX_FEATURES = 10_000
MAX_RESPONSE = 12_000_000
LICENSE = 'Licence Ouverte 2.0'
REGIONS = {r['macro']: r['bbox'] for r in json.loads(terrain.DEFAULT_MANIFEST.read_text())['regions']}


def bbox(value):
    """Internal order is south, west, north, east, matching the game's grids."""
    if isinstance(value, str):
        value = [float(x) for x in value.split(',')]
    if len(value) != 4 or any(type(v) not in (int, float) or not math.isfinite(v) for v in value):
        raise ValueError('bbox requires four finite numbers: south,west,north,east')
    s, w, n, e = value
    if not (-85 <= s < n <= 85 and -180 <= w < e <= 180):
        raise ValueError('bbox is inverted or outside supported geographic coordinates')
    return list(value)


def terrain_plan(bounds, spacing):
    bounds = bbox(bounds)
    if not math.isfinite(spacing) or not 1 <= spacing <= 200:
        raise ValueError('requested node spacing must be between 1 and 200 metres')
    s, w, n, e = bounds
    width = max(2, math.ceil((e - w) * 111320 * math.cos(math.radians((s + n) / 2)) / spacing) + 1)
    height = max(2, math.ceil((n - s) * 111320 / spacing) + 1)
    points = width * height
    if points > MAX_POINTS:
        raise ValueError(f'{points:,} nodes exceeds the {MAX_POINTS:,} node bound; select a smaller bbox')
    return {'bbox': bounds, 'width': width, 'height': height, 'points': points,
            'requestedSpacingMeters': spacing, 'batches': math.ceil(points / terrain.MAX_BATCH_POINTS),
            'sourceResolution': 'Resolution of underlying IGN data is service-dependent; requested spacing is not a survey accuracy claim'}


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()
    temporary = path.with_suffix(path.suffix + '.part')
    temporary.write_bytes(raw)
    temporary.replace(path)


def read_response(url, timeout=40):
    request = Request(url, headers={'Accept': 'application/json, application/xml;q=0.8',
                                  'User-Agent': 'Fallout-Mistral-Official-Source-Importer/1.0'})
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f'official service returned HTTP {response.status}')
        raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ValueError('official response exceeds the bounded size limit')
        return raw


def recording_fetch(directory, fetch=read_response):
    """Archive the unmodified authoritative response and its exact query/hash."""
    directory = Path(directory)
    serial = 0
    def recorded(url):
        nonlocal serial
        raw = fetch(url)
        if not isinstance(raw, bytes) or not raw or len(raw) > MAX_RESPONSE:
            raise ValueError('official response is empty or exceeds the archive byte bound')
        serial += 1
        query = parse_qs(urlsplit(url).query)
        operation = query.get('REQUEST', ['response'])[0]
        if not operation.isalnum():
            operation = 'response'
        digest = hashlib.sha256(raw).hexdigest()
        stem = f'{serial:03d}-{operation}-{digest[:12]}'
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (stem + '.raw')
        temporary = target.with_suffix('.part')
        temporary.write_bytes(raw)
        temporary.replace(target)
        atomic_json(directory / (stem + '.provenance.json'), {
            'url': url, 'acquiredAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'bytes': len(raw), 'sha256': digest, 'rawFile': target.name,
            'scope': 'Exact HTTPS response body; no geometry/property normalization',
        })
        return raw
    return recorded


def describe_feature_type(layer, fetch=read_response):
    raw = fetch(WFS + '?' + urlencode({'SERVICE': 'WFS', 'VERSION': '2.0.0',
                                     'REQUEST': 'DescribeFeatureType', 'TYPENAMES': layer}))
    root = ET.fromstring(raw)
    if root.tag != '{http://www.w3.org/2001/XMLSchema}schema':
        raise ValueError('official service did not return an XML Schema for the feature type')
    namespace = '{http://www.w3.org/2001/XMLSchema}'
    fields = []
    for complex_type in root.findall(namespace + 'complexType'):
        for element in complex_type.iter(namespace + 'element'):
            name, kind = element.get('name'), element.get('type')
            if not name or not kind:
                raise ValueError('official feature schema contains an unnamed or untyped field')
            fields.append({'name': name, 'type': kind, 'nillable': element.get('nillable') == 'true'})
    if not fields or len({f['name'] for f in fields}) != len(fields):
        raise ValueError('official feature schema has no fields or duplicate definitions')
    return {'layer': layer, 'targetNamespace': root.get('targetNamespace'), 'fields': fields,
            'schemaSha256': hashlib.sha256(raw).hexdigest()}


def validate_feature_schema(kind, schema):
    """Validate the actual public field names; do not promote guessed aliases."""
    fields = {field['name']: field['type'] for field in schema['fields']}
    required = ({'hauteur', 'altitude_minimale_sol', 'altitude_minimale_toit', 'altitude_maximale_toit'}
                if kind == 'buildings' else {'largeur_de_chaussee', 'nombre_de_voies', 'position_par_rapport_au_sol'})
    missing = required - fields.keys()
    geometry = fields.get('geometrie', '')
    if missing or ('Surface' not in geometry if kind == 'buildings' else not any(t in geometry for t in ('Curve', 'Line'))):
        raise ValueError('official layer schema is incompatible with this import: missing ' + ', '.join(sorted(missing)) + '; geometry ' + geometry)
    numeric = ({'hauteur', 'altitude_minimale_sol', 'altitude_minimale_toit', 'altitude_maximale_toit'}
               if kind == 'buildings' else {'largeur_de_chaussee', 'nombre_de_voies'})
    for name in numeric:
        if fields[name].split(':')[-1] not in ('double', 'float', 'decimal', 'int', 'integer'):
            raise ValueError('official measured field is not numeric: ' + name)
    return schema


def wfs_layers(fetch=read_response):
    raw = fetch(WFS + '?' + urlencode({'SERVICE': 'WFS', 'VERSION': '2.0.0', 'REQUEST': 'GetCapabilities'}))
    root = ET.fromstring(raw)
    if root.tag.rsplit('}', 1)[-1] != 'WFS_Capabilities':
        raise ValueError('service did not return WFS capabilities')
    return sorted({node.text.strip() for feature in root.iter() if feature.tag.rsplit('}', 1)[-1] == 'FeatureType'
                   for node in feature if node.tag.rsplit('}', 1)[-1] == 'Name' and node.text})


def complete_collection(features, layer, bounds):
    """Called only once pagination proved that every source query page arrived."""
    return {'type': 'FeatureCollection', 'features': features,
            'acquisitionCoverage': {'bbox': list(bounds), 'crs': 'EPSG:4326',
                                    'complete': True, 'layer': layer, 'returned': len(features)}}


def fetch_features(layer, bounds, limit=MAX_FEATURES, fetch=read_response, pause=time.sleep, advertised_layers=None):
    """Validate the advertised layer and finish every page or fail explicitly."""
    bounds = bbox(bounds)
    if not 1 <= limit <= MAX_FEATURES:
        raise ValueError('feature limit must be between 1 and 10000')
    if layer not in (advertised_layers if advertised_layers is not None else wfs_layers(fetch)):
        raise ValueError('requested layer is not advertised by the current official WFS: ' + layer)
    s, w, n, e = bounds
    features, ids, start, expected = [], set(), 0, None
    page_size = min(1000, limit)
    for page in range(100):
        if page:
            pause(.3)
        # CRS84 explicitly means longitude, latitude and avoids WFS EPSG:4326
        # latitude-axis ambiguity. The importer receives ordinary GeoJSON lon/lat.
        params = {'SERVICE': 'WFS', 'VERSION': '2.0.0', 'REQUEST': 'GetFeature',
                  'TYPENAMES': layer, 'OUTPUTFORMAT': 'application/json',
                  'SRSNAME': 'urn:ogc:def:crs:OGC::CRS84',
                  'BBOX': f'{w},{s},{e},{n},urn:ogc:def:crs:OGC::CRS84',
                  'COUNT': page_size, 'STARTINDEX': start}
        response = json.loads(fetch(WFS + '?' + urlencode(params)))
        rows = response.get('features')
        if response.get('type') != 'FeatureCollection' or not isinstance(rows, list) or len(rows) > page_size:
            raise ValueError('official WFS response is not a bounded GeoJSON FeatureCollection')
        returned = response.get('numberReturned')
        if returned is not None and (isinstance(returned, bool) or str(returned) != str(len(rows))):
            raise ValueError('official WFS returned count does not match its feature array')
        matched = response.get('numberMatched')
        if isinstance(matched, str) and matched.isdecimal():
            matched = int(matched)
        if isinstance(matched, int) and not isinstance(matched, bool):
            if matched < 0 or matched > limit:
                raise ValueError('official extract exceeds the feature bound; reduce the bbox')
            if expected is not None and expected != matched:
                raise ValueError('official layer changed during pagination; rerun the extract')
            expected = matched
        for feature in rows:
            if not isinstance(feature, dict) or feature.get('type') != 'Feature' or not feature.get('geometry'):
                raise ValueError('official response contains an invalid feature')
            identity = str(feature.get('id') or hashlib.sha256(json.dumps(feature, sort_keys=True).encode()).hexdigest())
            if identity in ids:
                raise ValueError('duplicate/repeated WFS page; incomplete extracts are not accepted')
            ids.add(identity)
            features.append(feature)
        if len(features) > limit:
            raise ValueError('official extract exceeds the feature bound; reduce the bbox')
        start += len(rows)
        if expected is not None:
            if len(features) == expected:
                return complete_collection(features, layer, bounds)
            if not rows or len(features) > expected:
                raise ValueError('official WFS ended before its advertised feature count')
        elif not rows:
            return complete_collection(features, layer, bounds)
    raise ValueError('official WFS pagination did not finish within the page budget')


def source_record(name, url, raw_path):
    return {'name': name, 'license': LICENSE, 'attribution': 'IGN — Géoplateforme',
            'url': url, 'acquiredAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['terrain', 'buildings', 'roads', 'layers'])
    parser.add_argument('--region', choices=sorted(REGIONS))
    parser.add_argument('--bbox', help='south,west,north,east; select a bounded playable sector')
    parser.add_argument('--spacing', type=float, default=2, help='requested terrain node spacing in metres, not claimed source accuracy')
    parser.add_argument('--layer', help='WFS layer name; use layers to inspect current capabilities')
    parser.add_argument('--cache', type=Path, default=Path('/workspace/.cloud-setup/fallout-marseille/public-sources'))
    parser.add_argument('--output', type=Path, default=ROOT / 'data/map_pack/enrichment')
    parser.add_argument('--dry-run', action='store_true', help='print the bounded acquisition plan without network access')
    parser.add_argument('--replace', action='store_true', help='explicitly replace a previously imported regional overlay')
    args = parser.parse_args(argv)
    try:
        if args.kind == 'layers':
            if args.dry_run:
                print(json.dumps({'endpoint': WFS, 'operation': 'GetCapabilities'}))
            else:
                print(json.dumps(wfs_layers(), ensure_ascii=False, indent=2))
            return 0
        if not args.region or not args.bbox:
            parser.error('--region and --bbox are required for a local extract')
        bounds = bbox(args.bbox)
        region_bounds = REGIONS[args.region]
        if not (region_bounds[0] <= bounds[0] < bounds[2] <= region_bounds[2] and
                region_bounds[1] <= bounds[1] < bounds[3] <= region_bounds[3]):
            raise ValueError('requested bbox must stay within the selected game region')
        plan = terrain_plan(bounds, args.spacing) if args.kind == 'terrain' else {'bbox': bounds, 'maximumFeatures': MAX_FEATURES}
        layer = args.layer or {'buildings': 'BDTOPO_V3:batiment', 'roads': 'BDTOPO_V3:troncon_de_route'}.get(args.kind)
        plan.update(kind=args.kind, region=args.region, layer=layer,
                    endpoint=terrain.OFFICIAL_API if args.kind == 'terrain' else WFS)
        print(json.dumps(plan, ensure_ascii=False, indent=2), flush=True)
        if args.dry_run:
            return 0
        signature = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:16]
        cache = args.cache / signature
        cache.mkdir(parents=True, exist_ok=True)
        if args.kind == 'terrain':
            manifest = copy.deepcopy(json.loads(terrain.DEFAULT_MANIFEST.read_text()))
            manifest['grid'].update(width=plan['width'], height=plan['height'])
            region = {'macro': args.region, 'bbox': bounds}
            terrain.fetch_official_region(region, manifest, cache, 40, 2)
            raw_path = cache / (args.region + '.json')
            # Preserve the actual grid's explicit datum, including the manifest's
            # full NGF-IGN69 description. An abbreviated CLI label must not reject
            # an otherwise verified official grid or silently change its datum.
            vertical_datum = json.loads(raw_path.read_text())['verticalDatum']
            name, url = 'IGN RGE ALTI — points échantillonnés', terrain.OFFICIAL_API
        else:
            fetch = recording_fetch(cache / 'http', fetch=read_response)
            advertised = wfs_layers(fetch)
            if layer not in advertised:
                raise ValueError('requested layer is not advertised by the current official WFS: ' + layer)
            schema = validate_feature_schema(args.kind, describe_feature_type(layer, fetch))
            atomic_json(cache / 'schema.json', schema)
            result = fetch_features(layer, bounds, fetch=fetch, advertised_layers=advertised)
            # The importer handles native BD TOPO names and retains source props.
            for feature in result['features']:
                feature.setdefault('properties', {})['kind'] = 'building' if args.kind == 'buildings' else 'road'
            raw_path = cache / (args.kind + '.geojson')
            atomic_json(raw_path, result)
            vertical_datum = 'NGF-IGN69'
            name, url = 'IGN BD TOPO — ' + layer, WFS
        record = source_record(name, url, raw_path)
        atomic_json(cache / 'source.json', record)
        # Import is a separate validating transaction. A failed download never
        # replaces the shipped map or an existing accepted overlay.
        command = [sys.executable, str(ROOT / 'tools/import_world_sources.py'),
                   '--region', args.region, '--output', str(args.output),
                   '--source', name, '--license', LICENSE,
                   '--resource', 'ign_rge_alti_wld' if args.kind == 'terrain' else 'ign-bdtopo',
                   '--source-url', url, '--vertical-datum', vertical_datum,
                   '--attribution', record['attribution'], '--acquired-at', record['acquiredAt'][:10]]
        command += ['--terrain' if args.kind == 'terrain' else '--geojson', str(raw_path)]
        if args.replace:
            command.append('--replace')
        else:
            command.append('--merge')
        return subprocess.run(command, cwd=ROOT).returncode
    except (ValueError, OSError, ET.ParseError, terrain.TerrainError) as error:
        print('Acquisition refusée : ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
