#!/usr/bin/env python3
"""Prepare bounded native IGN MNS surfaces for Bourse and Opera, entirely offline.

The original 19 surfaces, four tile receipts and 12 documentary-site records are
preserved. The Bourse source zone covers only part of the source building, so it
is context evidence only; it is never promoted into a measured facade or plan.
The caller validates the prepared payload before publishing its index.
"""
from pathlib import Path
import argparse
import hashlib
import json

from build_landmark_surfaces import canonical, clipped_surface, request

ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA = 'd784b256e926b8696b1173425e5fb4e02cddb88a1ade9168e37b07838bc1625d'
CITY_INDEX_SHA = '3a83c7f821a2f3bd824240d7f065568df7ae786b1f5719c8c57f004dbd817d61'
SITE_RESPONSE_SHA = 'a828afee591cb9445cfc166c972f270ba6212b083175d4a3caeced035ef6eb0f'
BUILDING_ID = 'BATIMENT0000000258927584'
BUILDING_SOURCE_ID = 'batiment.9967974'
ZONE_ID = 'SURFACTI0000002002709084'
SOURCE_CHUNK_SHA = 'bc93c7f7ec8b18f42b3398e0d97c81ccd3454bc0a6b8487a3089d1dcf6fa66b7'
MNS_TILE_SHA = 'a4d7f88153e7ee25a8f3043005c6db9619aa4d41d0bc0eb4abb939af3b459b96'
PROOF_DIRECTORY = ROOT / 'implementation/architecture-continuation/20261102'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, checksum):
    raw = path.read_bytes()
    if sha(raw) != checksum:
        raise ValueError('Pinned source bytes changed: ' + str(path))
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mns-cache', required=True, type=Path,
                        help='Existing verified native MNS TIFF cache; no network is used.')
    parser.add_argument('--new-mns-cache', required=True, type=Path, help='Verified 0892-6247 TIFF cache, acquired separately via the official metadata URL.')
    parser.add_argument('--include-opera', action='store_true', help='Add the three whole Opera-context footprints in the same newly acquired tile.')
    parser.add_argument('--output', required=True, type=Path, help='Prepare a payload, index and receipt here; does not install other sources.')
    args = parser.parse_args()
    import rasterio
    import numpy as np
    from rasterio.io import MemoryFile
    from shapely.geometry import shape
    from shapely.ops import transform
    from rasterio.warp import transform as warp

    baseline_path = ROOT / ('data/map_pack/landmark_surfaces/marseille-mns-' + BASELINE_SHA[:16] + '.json')
    baseline = json.loads(checked(baseline_path, BASELINE_SHA))
    if len(baseline['records']) != 19 or any(r['cleabs'] == BUILDING_ID for r in baseline['records']):
        raise ValueError('Expected the unchanged 19-record baseline')
    index = json.loads(checked(ROOT / 'data/map_pack/city/index.json', CITY_INDEX_SHA))
    chunk = next(t for t in index['tiles'] if t['sha256'] == SOURCE_CHUNK_SHA)
    source_raw = checked(ROOT / chunk['path'], SOURCE_CHUNK_SHA)
    source = next(f for f in json.loads(source_raw)['features'] if f['properties'].get('cleabs') == BUILDING_ID)
    if source['properties']['sourceId'] != BUILDING_SOURCE_ID or source['properties']['nature'] != 'Monument':
        raise ValueError('Unexpected original building identity or nature')
    catalogue = json.loads((PROOF_DIRECTORY / 'OFFICIAL_CATALOGUE_CHECKS.json').read_bytes())
    query = next(q for q in catalogue['requests'] if q['kind'] == 'ign-named-sites')
    raw_zones = checked(PROOF_DIRECTORY / (SITE_RESPONSE_SHA + '.geojson'), SITE_RESPONSE_SHA)
    zones = json.loads(raw_zones)
    if query['sha256'] != SITE_RESPONSE_SHA or zones['numberMatched'] != zones['numberReturned'] or zones['numberReturned'] != 58:
        raise ValueError('Incomplete or changed official site query')
    zone = next(f for f in zones['features'] if f['properties']['cleabs'] == ZONE_ID)
    properties = zone['properties']
    if properties['toponyme'] != 'Palais de la Bourse' or properties['fictif'] is not False or properties['precision_planimetrique'] != 3:
        raise ValueError('Changed site context; no automatic documentary association is inferred')

    def xy(geometry):
        def coords(value):
            return value[:2] if value and isinstance(value[0], (int, float)) else [coords(p) for p in value]
        return {'type': geometry['type'], 'coordinates': coords(geometry['coordinates'])}

    def project(x, y, z=None):
        return warp('EPSG:4326', 'EPSG:2154', x, y)

    building_polygon = transform(project, shape(xy(source['geometry'])))
    zone_polygon = transform(project, shape(xy(zone['geometry'])))
    intersection = building_polygon.intersection(zone_polygon).area
    relation = {
        'zoneCleabs': ZONE_ID, 'zoneSourceId': zone['id'], 'zoneProperties': properties,
        'sourceResponseSha256': SITE_RESPONSE_SHA, 'sourceUrl': query['url'],
        'sourceRequestedAt': query['requestedAt'],
        'intersectionAreaSquareMetres': intersection,
        'buildingOverlapRatio': intersection / building_polygon.area,
        'zoneOverlapRatio': intersection / zone_polygon.area,
        'buildingCentroidInsideZone': zone_polygon.covers(building_polygon.centroid),
        'zoneCentroidInsideBuilding': building_polygon.covers(zone_polygon.centroid),
        'documentarySiteLinkInstalled': False,
        'scope': 'Context only: partial source zone, insufficient for the strict whole-building documentary-link rule.',
    }
    if not .25 < relation['buildingOverlapRatio'] < .35 or relation['zoneOverlapRatio'] < .94:
        raise ValueError('Changed context geometry; review before rebuilding')

    upper_receipt = next(t for t in baseline['source']['tiles'] if t['sha256'] == MNS_TILE_SHA)
    lower_receipt = json.loads((PROOF_DIRECTORY / '0892-6247-MNS_RECEIPT.json').read_bytes())
    lower_sha = '4354e54417d2c2d00392f90820c69c3195145dd0bae244f36fe58aa8b7126b62'
    metadata_sha = 'd03791c589e23082add2d016a2db97ebe097a03a9f03c21f7c10930158ba0471'
    checked(PROOF_DIRECTORY / 'metadata-original.geojson', metadata_sha)
    if lower_receipt['sha256'] != lower_sha or lower_receipt['metadataResponseSha256'] != metadata_sha:
        raise ValueError('Changed new native MNS receipt')

    def validate_raster(raster, receipt, raw):
        spec = request(receipt['feature'])
        if (len(raw) != receipt['bytes'] or raster.count != 1 or raster.dtypes != ('float32',)
                or raster.nodata != -9999 or raster.res != (.5, .5)
                or [raster.width, raster.height] != spec['size'] or list(raster.bounds) != spec['bounds']
                or raster.crs.to_wkt() != receipt['header']['crsWkt']):
            raise ValueError('Native MNS header differs from the acquired official receipt')

    upper_path, lower_path = args.mns_cache / upper_receipt['filename'], args.new_mns_cache / lower_receipt['filename']
    upper_raw, lower_raw = checked(upper_path, MNS_TILE_SHA), checked(lower_path, lower_sha)
    records = []
    with rasterio.open(upper_path) as upper, rasterio.open(lower_path) as lower, MemoryFile() as memory:
        validate_raster(upper, upper_receipt, upper_raw)
        validate_raster(lower, lower_receipt, lower_raw)
        if upper.width != lower.width or upper.bounds.left != lower.bounds.left or upper.bounds.bottom != lower.bounds.top:
            raise ValueError('The two native grids do not meet on the declared vertical seam')
        profile = upper.profile.copy()
        profile['height'] = upper.height + lower.height
        with memory.open(**profile) as combined:
            combined.write(np.concatenate([upper.read(1), lower.read(1)], axis=0), 1)
            record = clipped_surface(source, [(combined, {'sha256': None, 'sourceHashes': [MNS_TILE_SHA, lower_sha]})])
            record['siteContext'] = 'Contexte du Palais de la Bourse'
            record['siteContextEvidence'] = relation
            records.append(record)
        if args.include_opera:
            opera_zone = next(f for f in zones['features'] if f['properties']['cleabs'] == 'SURFACTI0000000040212941')
            if opera_zone['properties']['toponyme'] != 'Opéra Municipal de Marseille' or opera_zone['properties']['fictif'] is not False:
                raise ValueError('Changed Opera context')
            all_features = {f['properties'].get('cleabs'): f for f in json.loads(source_raw)['features']}
            for cleabs in ['BATIMENT0000000273403820', 'BATIMENT0000000273403821', 'BATIMENT0000000273403819']:
                feature = all_features[cleabs]
                addition = clipped_surface(feature, [(lower, lower_receipt)])
                addition['siteContext'] = 'Contexte de l’Opéra Municipal de Marseille'
                addition['siteContextEvidence'] = {'zoneCleabs': opera_zone['properties']['cleabs'], 'zoneSourceId': opera_zone['id'],
                                                  'zoneProperties': opera_zone['properties'], 'sourceResponseSha256': SITE_RESPONSE_SHA,
                                                  'sourceUrl': query['url'], 'documentarySiteLinkInstalled': False,
                                                  'scope': 'Site context only; source-zone precision is 5 m. No measured facade, opening or interior is attached.'}
                records.append(addition)
        header_epsg = upper.crs.to_epsg()
    for record in records:
        original = next(f for f in json.loads(source_raw)['features'] if f['properties'].get('cleabs') == record['cleabs'])
        if record['measurements']['minimumElevation'] < original['properties']['altitude_minimale_sol'] - .01:
            raise ValueError('The surface falls below its unchanged historical building base: ' + record['cleabs'])
        if record['rawGeometry'] != original['geometry']:
            raise ValueError('Source binding changed')
    payload = {**baseline, 'inputHashes': {**baseline['inputHashes'], chunk['path']: SOURCE_CHUNK_SHA},
               'source': {**baseline['source'], 'tiles': baseline['source']['tiles'] + [lower_receipt],
                          'additionalMetadataSha256': metadata_sha}, 'records': baseline['records'] + records}
    if payload['records'][:19] != baseline['records'] or payload['source']['tiles'][:4] != baseline['source']['tiles']:
        raise ValueError('An earlier surface or source receipt changed')
    raw = canonical(payload)
    digest = sha(raw)
    if len(raw) > 16 * 1024**2 or sum(len(r['faces']) for r in payload['records']) > 220000:
        raise ValueError('Merged MNS payload exceeds the unchanged runtime budget')
    name = 'marseille-mns-' + digest[:16] + '.json'
    descriptor = {'schemaVersion': 1, 'surface': {'path': 'data/map_pack/landmark_surfaces/' + name,
                                               'sha256': digest, 'bytes': len(raw)},
                  'recordCount': len(payload['records']), 'siteContexts': list(dict.fromkeys(r['siteContext'] for r in payload['records'])),
                  'scope': payload['scope']}
    proof = {
        'schemaVersion': 1, 'kind': 'offline-native-mns-source-extension',
        'buildingCleabs': BUILDING_ID, 'buildingSourceId': BUILDING_SOURCE_ID,
        'baselineSurfaceSha256': BASELINE_SHA, 'previousRecordsUnchanged': 19,
        'cityIndexSha256': CITY_INDEX_SHA, 'sourceChunk': chunk['path'], 'sourceChunkSha256': SOURCE_CHUNK_SHA,
        'nativeMns': {'previousTileSha256': MNS_TILE_SHA, 'newTileSha256': lower_sha, 'newBytes': len(lower_raw), 'newUrl': request(lower_receipt['feature'])['url'],
                      'declaredHorizontalFrame': 'EPSG:2154 (LAMB93), official request and source metadata',
                      'verticalDatum': 'NGF-IGN69', 'dtype': 'float32', 'nativeSpacingMetres': .5, 'noData': -9999,
                      'headerEpsgAutoIdentification': header_epsg,
                      'headerNote': 'The acquired WKT is retained exactly; this WMS TIFF has no automatic EPSG identification.',
                      'license': 'Licence Ouverte 2.0', 'attribution': 'IGN — Géoplateforme, LiDAR HD et BD TOPO'},
        'siteContext': relation, 'newRecords': [{'cleabs': r['cleabs'], 'context': r['siteContext'], 'vertices': len(r['vertices']),
                                              'faces': len(r['faces']), 'measurements': r['measurements']} for r in records],
        'combinedRecords': len(payload['records']), 'combinedFaces': sum(len(r['faces']) for r in payload['records']),
        'output': descriptor, 'builderSha256': sha(Path(__file__).read_bytes()),
        'clippingToolSha256': sha((ROOT / 'tools/build_landmark_surfaces.py').read_bytes()),
        'scope': 'Observed upper source surface only; not measured facades, openings, rooms, semantic roof planes or a complete monument survey.',
        'refusals': ['No 13th documentary-site record: the Bourse source zone is partial and the strict 99% whole-building association does not hold.',
                     'Opera site precision is 5 m: context only, no strict documentary-site link.',
                     'Bourse cannot be clipped completely from 0892-6248 alone; the missing 0892-6247 tile was acquired instead of cropping or filling cells.',
                     'Saint-Victor and Saint-Jean are not added; this extension is bounded to two new contexts.'],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / name).write_bytes(raw)
    (args.output / 'index.json').write_bytes(canonical(descriptor))
    (args.output / 'BOURSE_OPERA_BUILD_RECEIPT.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'surface': descriptor['surface'], 'records': len(payload['records']),
                      'newRecords': [{k: r[k] for k in ['cleabs', 'context', 'vertices', 'faces']} for r in proof['newRecords']],
                      'combinedFaces': proof['combinedFaces']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
