#!/usr/bin/env python3
"""Independent source-centre checks; read-only on the game and IGN GeoTIFFs."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import rasterio

ROOT = Path('/workspace/fallout-Marseille')
CACHE = Path('/workspace/.cloud-setup/fallout-marseille/precision-terrain/acquisition')
OUT = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def main():
    started = time.time()
    index_path = ROOT / 'data/map_pack/precise/index.json'
    proof_path = ROOT / 'data/map_pack/precise/ACQUISITION.json'
    index = json.loads(index_path.read_text())
    proof = json.loads(proof_path.read_text())
    opened = [(row, rasterio.open(CACHE / row['file'])) for row in proof['sources']]
    points, chunks, sources, failures = [], [], [], []
    try:
        for receipt, source in opened:
            path = CACHE / receipt['file']
            checksum = sha(path)
            if checksum != receipt['sha256']:
                failures.append({'kind': 'source_checksum', 'file': str(path)})
            sources.append({'file': str(path), 'sha256': checksum, 'bytes': path.stat().st_size,
                            'transform': list(source.transform), 'firstCentre': source.xy(0, 0),
                            'crs': source.crs.to_wkt(), 'nodata': source.nodata, 'shape': source.shape})
        for descriptor in index['tiles']:
            path = ROOT / descriptor['path']
            checksum = sha(path)
            if checksum != descriptor['sha256']:
                failures.append({'kind': 'chunk_checksum', 'file': str(path)})
            chunks.append({'file': str(path), 'sha256': checksum, 'bytes': path.stat().st_size,
                           'origin': descriptor['origin'], 'step': descriptor['step'],
                           'width': descriptor['width'], 'height': descriptor['height']})
            values = np.fromfile(path, dtype='<f4').reshape(descriptor['height'], descriptor['width'])
            positions = [(0, 0), (descriptor['width']-1, 0), (0, descriptor['height']-1),
                         (descriptor['width']-1, descriptor['height']-1),
                         (descriptor['width']//2, descriptor['height']//2), (123, 456)]
            for column, row in positions:
                east = descriptor['origin'][0] + column * .5
                north = descriptor['origin'][1] - row * .5
                candidates = [(receipt, source) for receipt, source in opened
                              if source.bounds.left < east < source.bounds.right
                              and source.bounds.bottom < north < source.bounds.top]
                if len(candidates) != 1:
                    failures.append({'kind': 'ambiguous_source', 'chunk': descriptor['path'],
                                     'column': column, 'row': row, 'candidates': len(candidates)})
                    continue
                receipt, source = candidates[0]
                source_row, source_column = source.index(east, north)
                x, y = source.xy(source_row, source_column)
                source_value = float(source.read(1, window=rasterio.windows.Window(source_column, source_row, 1, 1))[0, 0])
                runtime_value = float(values[row, column])
                ok = abs(x-east) < 1e-8 and abs(y-north) < 1e-8 and source_value == runtime_value
                point = {'chunk': descriptor['path'], 'column': column, 'row': row,
                         'runtimeCentre': [east, north], 'runtimeValue': runtime_value,
                         'source': receipt['file'], 'sourceColumn': source_column, 'sourceRow': source_row,
                         'sourceCentre': [x, y], 'sourceValue': source_value, 'equal': ok}
                points.append(point)
                if not ok:
                    failures.append(point)
    finally:
        for _, source in opened:
            source.close()
    citations = [
        {'file': 'src/patches/01_geometry.js', 'lines': [49, 64, 95],
         'claim': 'v018MeshData expands faces and chunks 18000 triangles per flatMesh; 54000 vertices <65536 before UNSIGNED_SHORT drawing'},
        {'file': 'src/core-v017.js', 'lines': [1006, 1078],
         'claim': 'GLStaticGeometryBatches.pack also flushes at54000 vertices before createMesh converts indices to Uint16Array'},
        {'file': 'src/v050/14_precise_terrain.js', 'lines': [114],
         'claim': 'The native patch removes coarse faces by centroid inside its expanded seam box before appending native and seam draws'},
    ]
    for citation in citations:
        citation['sha256'] = sha(ROOT / citation['file'])
    report = {'scope': 'Independent read-only rasterio checks against received IGN GeoTIFFs, no runtime sampling implementation reused; GPU splitting verified by cited production source, no GPU/hardware claim',
              'indexSha256': sha(index_path), 'acquisitionSha256': sha(proof_path),
              'sources': sources, 'chunks': chunks, 'points': points,
              'passed': sum(p['equal'] for p in points), 'failed': len(failures), 'expectedPoints': 288,
              'sourceCount': len(sources), 'chunkCount': len(chunks),
              'noDataPointsInAtlas': index['noDataPoints'], 'failures': failures,
              'rendererSourceReview': citations, 'durationSeconds': time.time()-started}
    (OUT / 'TERRAIN_INDEPENDENT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['passed', 'failed', 'expectedPoints', 'sourceCount', 'chunkCount', 'noDataPointsInAtlas', 'durationSeconds']}), flush=True)
    return int(bool(failures or report['passed'] != 288))


if __name__ == '__main__':
    raise SystemExit(main())
