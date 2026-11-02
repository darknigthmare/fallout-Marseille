"""Independent local replay of all new vertices against original native TIFF cells."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import rasterio

ROOT = Path('/workspace/fallout-Marseille')
BASE = Path(__file__).parent
OLD = Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion/landmarks/acquisition/0892-6248-mns.tif')
NEW = BASE / 'acquisition/0892-6247-mns.tif'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
index = json.loads((ROOT / 'data/map_pack/landmark_surfaces/index.json').read_bytes())
raw = (ROOT / index['surface']['path']).read_bytes()
assert sha(raw) == index['surface']['sha256']
payload = json.loads(raw)
assert len(payload['records']) == 23
assert sha(OLD.read_bytes()) == 'a4d7f88153e7ee25a8f3043005c6db9619aa4d41d0bc0eb4abb939af3b459b96'
assert sha(NEW.read_bytes()) == '4354e54417d2c2d00392f90820c69c3195145dd0bae244f36fe58aa8b7126b62'
with rasterio.open(OLD) as upper, rasterio.open(NEW) as lower:
    top, bottom = upper.read(1), lower.read(1)
    joined = np.concatenate([top, bottom], axis=0)
    x0, y0 = upper.xy(0, 0)
    lx0, ly0 = lower.xy(0, 0)
    results = []
    for record in payload['records'][19:]:
        grid, origin_x, origin_y = (joined, x0, y0) if len(record['sourceTileSha256']) == 2 else (bottom, lx0, ly0)
        native, interpolated, maximum_error = 0, 0, 0.
        for x, y, elevation in record['vertices']:
            u, v = (x - origin_x) / .5, (origin_y - y) / .5
            ni, nj = round(u), round(v)
            if abs(u - ni) < 2e-8 and abs(v - nj) < 2e-8:
                expected = float(grid[nj, ni])
                assert expected != -9999 and math.isfinite(expected)
                assert elevation == expected, (record['cleabs'], x, y, elevation, expected)
                native += 1
            else:
                col, row = math.floor(u), math.floor(v)
                a, b = u - col, v - row
                if a + b <= 1:
                    values = [float(grid[row, col]), float(grid[row, col + 1]), float(grid[row + 1, col])]
                    expected = values[0] * (1 - a - b) + values[1] * a + values[2] * b
                else:
                    values = [float(grid[row, col + 1]), float(grid[row + 1, col]), float(grid[row + 1, col + 1])]
                    expected = values[0] * (1 - b) + values[1] * (1 - a) + values[2] * (a + b - 1)
                assert all(math.isfinite(value) and value != -9999 for value in values)
                maximum_error = max(maximum_error, abs(elevation - expected))
                assert abs(elevation - expected) < 2e-5
                interpolated += 1
        assert native + interpolated == len(record['vertices'])
        results.append({'cleabs': record['cleabs'], 'vertices': len(record['vertices']),
                        'nativeCentresVerifiedExactly': native, 'triangleIntersectionsVerified': interpolated,
                        'maximumInterpolationErrorMetres': maximum_error, 'referencedNoData': 0})
proof = {'schemaVersion': 1, 'scope': 'Independent arithmetic replay against pinned original Float32 rasters; no new physical accuracy claim.',
         'surfaceSha256': index['surface']['sha256'], 'newRecords': results,
         'nativeCentresVerifiedExactly': sum(r['nativeCentresVerifiedExactly'] for r in results),
         'triangleIntersectionsVerified': sum(r['triangleIntersectionsVerified'] for r in results),
         'referencedNoData': 0, 'verificationScriptSha256': sha(Path(__file__).read_bytes())}
(BASE / 'NATIVE_CELL_REPLAY.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(proof, ensure_ascii=False))
