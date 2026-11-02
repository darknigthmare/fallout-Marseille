#!/usr/bin/env python3
"""Compare every imported DEM node with original, caller-supplied GeoTIFFs.

This is a read-only replay using rasterio's sample API, independently of the
import converter's window/index implementation. No TIFF is downloaded or copied
into the distribution. Original TIFF SHA-256 values must match the conversion
receipts. Reprojection and nearest-cell sampling remain explicitly declared.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

from world_source_bundle import validate_directory


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(directory, region, originals):
    import rasterio
    from rasterio.warp import transform

    files, _ = validate_directory(directory)
    index = json.loads(files['index.json'])
    descriptor = index['regions'][region]
    bundle = json.loads(files[Path(descriptor['path']).name])
    grids = bundle.get('terrainTiles', [bundle['terrain']] if bundle.get('terrain') else [])
    paths = {digest(path): Path(path) for path in originals}
    report = {'scope': __doc__, 'region': region, 'bundleSha256': descriptor['sha256'],
              'nodesCompared': 0, 'mismatchedNodes': 0, 'grids': []}
    if not grids:
        raise ValueError('Selected region contains no terrain grids')
    for grid in grids:
        conversion = grid['provenance'].get('conversion')
        if not conversion or conversion['resampling'] != 'nearest' or not conversion['resampled']:
            raise ValueError('Only explicit nearest-resampled GeoTIFF conversions are supported')
        checksum = conversion['inputSha256']
        if checksum not in paths:
            raise ValueError('Matching original GeoTIFF missing: ' + checksum)
        path = paths[checksum]
        south, west, north, east = grid['bbox']
        width, height = grid['width'], grid['height']
        row = {'id': grid['macro'], 'originalFile': path.name, 'originalSha256': checksum,
               'bbox': grid['bbox'], 'width': width, 'height': height,
               'nodesCompared': 0, 'mismatchedNodes': 0, 'maximumAbsoluteErrorMeters': 0,
               'actualNoDataNodes': 0, 'sourceProbeSamples': []}
        with rasterio.open(path) as source:
            if source.count != 1 or list(source.shape) != list(reversed(conversion['sourceSize'])):
                raise ValueError('Original raster dimensions differ from conversion receipt')
            if list(source.transform)[:6] != conversion['nativeTransform']:
                raise ValueError('Original transform differs from conversion receipt')
            if source.crs is None or source.crs.to_epsg() not in (None, int(conversion['crs'].split(':')[1])):
                raise ValueError('Original CRS conflicts with explicit conversion CRS')
            for start in range(0, width * height, 4096):
                stop = min(width * height, start + 4096)
                indices = list(range(start, stop))
                latitudes = [north - (north-south)*(i//width)/(height-1) for i in indices]
                longitudes = [west + (east-west)*(i%width)/(width-1) for i in indices]
                xs, ys = transform('EPSG:4326', conversion['crs'], longitudes, latitudes)
                for offset, sample in enumerate(source.sample(zip(xs, ys), indexes=1, masked=True)):
                    index_in_grid = start + offset
                    expected = None if bool(sample.mask[0]) else float(sample.data[0]) * source.scales[0] + source.offsets[0]
                    if expected is not None and not math.isfinite(expected):
                        expected = None
                    actual = grid['values'][index_in_grid]
                    row['nodesCompared'] += 1
                    row['actualNoDataNodes'] += int(expected is None)
                    matches = actual is None and expected is None or actual is not None and expected is not None and actual == expected
                    if not matches:
                        row['mismatchedNodes'] += 1
                    if actual is not None and expected is not None:
                        row['maximumAbsoluteErrorMeters'] = max(row['maximumAbsoluteErrorMeters'], abs(actual-expected))
                    if index_in_grid in {0, width-1, (height-1)*width, width*height-1, (height//2)*width+width//2}:
                        row['sourceProbeSamples'].append({'index': index_in_grid, 'lat': latitudes[offset],
                                                         'lon': longitudes[offset], 'original': expected, 'imported': actual})
        report['grids'].append(row)
        report['nodesCompared'] += row['nodesCompared']
        report['mismatchedNodes'] += row['mismatchedNodes']
    report['ok'] = report['nodesCompared'] > 0 and report['mismatchedNodes'] == 0
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--original', type=Path, action='append', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.directory, args.region, args.original)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: result[key] for key in ['ok', 'region', 'nodesCompared', 'mismatchedNodes']}, ensure_ascii=False))
    return int(not result['ok'])


if __name__ == '__main__':
    raise SystemExit(main())
