#!/usr/bin/env python3
"""Acquire published native IGN MNT tiles and split exact Float32 cells offline.

No reprojection/resampling of elevations. The WGS84 bboxes are index bounds only;
runtime sampling uses the original Lambert-93 pixel centres and metre spacing.
Original GeoTIFFs stay in the explicit external cache. Runtime ZIPs are separate
from previous source archives and contain attributed proof samples and receipts.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import math
import sys
import zipfile
from urllib.parse import urlencode

from acquire_ign_dem import Client, METADATA_LAYER, native_request
from precise_terrain_sources import canonical, digest, MAX_TOTAL

ROOT = Path(__file__).resolve().parents[1]
NATIVE_BOUNDS = [892000, 6245000, 895000, 6249000]
DISCOVERY_BBOX = [43.267, 5.35, 43.325, 5.413]


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != raw:
        raise ValueError('Existing immutable terrain output differs: ' + str(path))
    path.write_bytes(raw)


def metadata_url():
    south, west, north, east = DISCOVERY_BBOX
    return 'https://data.geopf.fr/wfs/ows?' + urlencode({
        'service': 'WFS', 'version': '2.0.0', 'request': 'GetFeature', 'typenames': METADATA_LAYER,
        'srsName': 'urn:ogc:def:crs:OGC:1.3:CRS84',
        'bbox': f'{west},{south},{east},{north},urn:ogc:def:crs:OGC:1.3:CRS84',
        'count': 100, 'outputFormat': 'application/json'})


def download_native(url, cache, filename):
    raw = Client(120).read(url, 24 * 1024**2)
    checksum = hashlib.sha256(raw).hexdigest()
    path = cache / (checksum[:16]+'-'+filename)
    put(path, raw)
    return path, checksum, len(raw)


def acquire(cache, offline=False):
    import rasterio
    cache.mkdir(parents=True, exist_ok=True)
    metadata = cache / 'metadata.json'
    if not metadata.exists():
        if offline:
            raise ValueError('Offline cache lacks official WFS metadata')
        metadata.write_bytes(Client(120).read(metadata_url(), 8 * 1024**2))
    payload = json.loads(metadata.read_text())
    if payload.get('numberReturned') != len(payload.get('features', [])) or payload.get('numberMatched') != payload.get('numberReturned'):
        raise ValueError('Bounded metadata query is not complete')
    selected = []
    for feature in payload['features']:
        props = feature['properties']
        if props.get('systeme_planimetrique') != 'LAMB93' or props.get('systeme_altimetrique') != 'IGN69':
            continue
        request = native_request(props.get('url_mnt', ''))
        b = request['bounds']
        # Native first centres are exactly integer metres; source metadata
        # supplies the half-pixel-expanded export bbox, never a guessed URL.
        x, north = b[0] + .25, b[3] - .25
        if NATIVE_BOUNDS[0] <= x < NATIVE_BOUNDS[2] and NATIVE_BOUNDS[1] < north <= NATIVE_BOUNDS[3]:
            selected.append((feature, request))
    selected.sort(key=lambda row: row[1]['filename'])
    if len(selected) != 12:
        raise ValueError('Expected twelve complete adjacent native source tiles')
    receipts = []
    for feature, request in selected:
        proof_path = cache / (feature['id'].replace('.', '-') + '.receipt.json')
        if proof_path.exists():
            proof = json.loads(proof_path.read_text())
            path = cache / proof['file']
            if proof['downloadUrl'] != feature['properties']['url_mnt'] or not path.is_file() or digest(path) != proof['sha256']:
                raise ValueError('Native external cache differs from its receipt')
        else:
            if offline:
                raise ValueError('Offline cache lacks source: ' + feature['id'])
            path, checksum, size = download_native(feature['properties']['url_mnt'], cache, request['filename'])
            proof = {'feature': feature, 'file': path.name, 'sha256': checksum, 'bytes': size,
                     'downloadUrl': feature['properties']['url_mnt'],
                     'downloadedAt': dt.datetime.now(dt.timezone.utc).isoformat(), 'nativeRequest': request,
                     'checksumScope': 'Received bytes over verified HTTPS; no independent upstream checksum supplied.'}
        with rasterio.open(path) as raster:
            if raster.driver != 'GTiff' or raster.count != 1 or raster.dtypes[0] != 'float32' or [raster.width, raster.height] != [2000, 2000]:
                raise ValueError('Native numeric source must have one 2000x2000 Float32 band')
            if raster.nodata != -9999 or raster.res != (.5, .5) or any(abs(a-b) > 1e-6 for a, b in zip(raster.bounds, request['bounds'])):
                raise ValueError('Native source resolution/NoData/georeference differs')
            if raster.crs is None or raster.crs.to_epsg() not in (None, 2154):
                raise ValueError('Unexpected declared native CRS')
            proof['header'] = {'wkt': raster.crs.to_wkt(), 'recognizedEpsg': raster.crs.to_epsg(),
                               'effectiveCrs': 'EPSG:2154', 'crsBasis': 'Published WFS url_mnt CRS and LAMB93 metadata; not inferred from coordinate values.',
                               'transform': list(raster.transform)[:6], 'nodata': raster.nodata,
                               'nativePixelSize': list(raster.res), 'verticalDatum': 'NGF-IGN69'}
        put(proof_path, canonical(proof))
        receipts.append(proof)
        print('SOURCE ' + feature['id'] + ' ' + proof['sha256'], flush=True)
    return receipts, metadata


def build(cache, root, offline=False):
    import numpy as np
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import Window
    receipts, metadata = acquire(cache, offline)
    output = root / 'data/map_pack/precise'
    atlas_origin = [NATIVE_BOUNDS[0], NATIVE_BOUNDS[3]]
    width, height, block = 6000, 8000, 1000
    opened = []
    try:
        for proof in receipts:
            source = rasterio.open(cache / proof['file'])
            first_x, first_y = source.xy(0, 0)
            ox, oy = (first_x-atlas_origin[0])/.5, (atlas_origin[1]-first_y)/.5
            if abs(ox-round(ox)) > 1e-7 or abs(oy-round(oy)) > 1e-7:
                raise ValueError('Native source is not aligned to the shared half-metre lattice')
            opened.append((source, round(ox), round(oy), proof))
        tiles, probes = [], []
        for row in range(0, height, block):
            for column in range(0, width, block):
                w, h = min(block+1, width-column), min(block+1, height-row)
                values = np.full((h, w), -9999, dtype='<f4')
                covered = np.zeros((h, w), dtype=bool)
                source_ids = []
                for source, ox, oy, proof in opened:
                    x0, y0, x1, y1 = max(column, ox), max(row, oy), min(column+w, ox+2000), min(row+h, oy+2000)
                    if x0 >= x1 or y0 >= y1:
                        continue
                    part = source.read(1, window=Window(x0-ox, y0-oy, x1-x0, y1-y0))
                    mask = source.read_masks(1, window=Window(x0-ox, y0-oy, x1-x0, y1-y0)) == 0
                    if np.any(mask & np.isfinite(part) & (part != -9999)):
                        raise ValueError('Source has an unencoded mask; refusing to lose its NoData')
                    values[y0-row:y1-row, x0-column:x1-column] = part
                    covered[y0-row:y1-row, x0-column:x1-column] = True
                    source_ids.append(proof['feature']['id'])
                if not covered.all():
                    raise ValueError('Native source coverage has an unaccounted hole')
                missing = ~np.isfinite(values) | (values == -9999)
                if np.any((~missing) & ((values <= -100) | (values >= 9000))):
                    raise ValueError('Native source contains unsupported non-NoData altitudes')
                raw = values.tobytes(order='C')
                checksum = hashlib.sha256(raw).hexdigest()
                name = f'native-r{row:05d}-c{column:05d}-{checksum[:16]}.f32'
                relative = 'data/map_pack/precise/' + name
                put(root / relative, raw)
                first = [atlas_origin[0]+column*.5, atlas_origin[1]-row*.5]
                native = [first[0], first[1]-(h-1)*.5, first[0]+(w-1)*.5, first[1]]
                west, south, east, north = transform_bounds('EPSG:2154', 'EPSG:4326', *native, densify_pts=21)
                identity = hashlib.sha256(canonical({'sha256': checksum, 'origin': first, 'width': w, 'height': h,
                                                     'step': [.5, -.5], 'crs': 'EPSG:2154', 'nodata': -9999})).hexdigest()[:16]
                descriptor = {'id': 'enrichment:geo_marseille_commune:' + identity, 'path': relative,
                              'bytes': len(raw), 'sha256': checksum, 'width': w, 'height': h,
                              'bbox': [south, west, north, east], 'nativeBounds': native,
                              'origin': first, 'step': [.5, -.5], 'crs': 'EPSG:2154', 'verticalDatum': 'NGF-IGN69',
                              'nodata': -9999, 'rowOrder': 'north-to-south', 'dataType': 'Float32LE',
                              'validPoints': int((~missing).sum()), 'noDataPoints': int(missing.sum()), 'sourceIds': source_ids}
                tiles.append(descriptor)
                for ix, iy in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1), (w//2, h//2)]:
                    value = float(values[iy, ix])
                    probes.append({'chunk': name, 'column': ix, 'row': iy,
                                   'easting': first[0]+ix*.5, 'northing': first[1]-iy*.5,
                                   'z': value if math.isfinite(value) and value != -9999 else None})
                valid = np.argwhere(~missing)
                absent = np.argwhere(missing)
                for group in (valid, absent):
                    if len(group):
                        iy, ix = map(int, group[len(group)//2])
                        probes.append({'chunk': name, 'column': ix, 'row': iy,
                                       'easting': first[0]+ix*.5, 'northing': first[1]-iy*.5,
                                       'z': None if missing[iy, ix] else float(values[iy, ix])})
        proof = {'schemaVersion': 1, 'provider': 'IGN', 'product': 'MNT LiDAR HD',
                 'metadataUrl': metadata_url(), 'metadataSha256': digest(metadata), 'sources': receipts,
                 'conversion': {'resampled': False, 'elevationReprojection': False,
                                'operation': 'Exact source Float32 cells split into overlapping windows on the unchanged native lattice.',
                                'indexBboxesOnly': 'WGS84 index bounding boxes transformed from native node-centre bounds; elevations remain Lambert-93.'},
                 'license': 'Licence Ouverte 2.0', 'attribution': 'IGN — LiDAR HD', 'probes': probes}
        index = {'schemaVersion': 1, 'kind': 'native-lidar-f32', 'sourceResource': 'ign_lidar_hd_mnt',
                 'sourceTiles': len(receipts), 'nativeSpacingMeters': .5, 'coverageSquareMeters': 12_000_000,
                 'nativeExtent': NATIVE_BOUNDS, 'verticalDatum': 'NGF-IGN69', 'crs': 'EPSG:2154',
                 'validPoints': sum(t['validPoints'] for t in tiles), 'noDataPoints': sum(t['noDataPoints'] for t in tiles),
                 'countScope': 'Chunk sample counts include one shared halo row/column; native source footprint is twelve square kilometres.',
                 'provenance': {'source': 'IGN — MNT LiDAR HD', 'license': proof['license'], 'attribution': proof['attribution'],
                                'acquiredAt': max(r['downloadedAt'] for r in receipts), 'verticalDatum': 'NGF-IGN69',
                                'nativeSpacingMeters': .5, 'resampled': False}, 'tiles': tiles}
        put(output / 'index.json', canonical(index))
        put(output / 'ACQUISITION.json', canonical(proof))
        package(root, [root/t['path'] for t in tiles] + [output/'index.json', output/'ACQUISITION.json'])
        return index
    finally:
        for source, *_ in opened:
            source.close()


def package(root, paths):
    paths = sorted(paths)
    if sum(p.stat().st_size for p in paths) > MAX_TOTAL:
        raise ValueError('Runtime native atlas exceeds expanded budget')
    folder = root / 'data/map_pack/precision_archives'
    folder.mkdir(parents=True, exist_ok=True)
    groups, selected, size = [], [], 0
    for path in paths:
        if selected and size+path.stat().st_size > 32*1024**2:
            groups.append(selected); selected, size = [], 0
        selected.append(path); size += path.stat().st_size
    if selected:
        groups.append(selected)
    archives = []
    for number, group in enumerate(groups):
        path = folder / f'marseille-native-{number:02d}.zip'
        temporary = path.with_suffix('.zip.tmp')
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
            for p in group:
                info = zipfile.ZipInfo(p.relative_to(root).as_posix(), (2026, 10, 25, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
                bundle.writestr(info, p.read_bytes())
        if path.exists() and digest(path) != digest(temporary):
            raise ValueError('Existing native archive differs; choose a distinct atlas revision')
        temporary.replace(path)
        if path.stat().st_size >= 64*1024**2:
            raise ValueError('Native terrain archive exceeds its Git transport budget')
        archives.append({'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size, 'sha256': digest(path),
                         'files': [{'path': p.relative_to(root).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in group]})
    put(folder/'manifest.json', canonical({'schemaVersion': 1, 'archives': archives,
                                         'scope': 'Separate native central Marseille terrain, no previous source archive replaced.'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True, help='External native GeoTIFF cache, never added to Git')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    result = build(args.cache, args.root, args.offline)
    print(json.dumps({k: result[k] for k in ('sourceTiles', 'coverageSquareMeters', 'validPoints', 'noDataPoints')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
