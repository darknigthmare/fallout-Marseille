"""Independent replay with explicit synthetic GeoTIFFs; no IGN data invented."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import audit_resampled_dem as replay
import convert_ign_dem as converter
import world_sources as sources

try:
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
except ImportError:
    rasterio = None


@unittest.skipUnless(rasterio is not None, 'Optional requirements-geo.txt is required')
class OriginalDemReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'synthetic-original.tif'
        values = np.array([[10, 11, 12], [20, -9999, 22], [30, 31, 32]], dtype='float32')
        with rasterio.open(self.path, 'w', driver='GTiff', count=1, height=3, width=3,
                           dtype='float32', crs='EPSG:4326', transform=from_origin(5.568, 43.299, .001, .001), nodata=-9999) as dataset:
            dataset.write(values, 1)
        self.bbox = [43.2965, 5.5685, 43.2985, 5.5705]
        self.grid = converter.convert_dem(self.path, self.bbox, 112, 'NGF-IGN69')
        self.source = sources.provenance(name='Independent replay synthetic fixture', resource='replay-fixture',
                                         license='Synthetic fixture', attribution='Test only', acquired_at='2026-10-28',
                                         vertical_datum='NGF-IGN69')

    def publish(self):
        raw = json.dumps(self.grid, allow_nan=False).encode()
        grid = sources.read_terrain(raw, 'geo_huveaune', self.source, self.bbox)
        sources.publish_bundle(self.root/'active', 'geo_huveaune', self.source, terrain=grid)

    def test_every_node_and_real_nodata_mask_are_compared(self):
        self.publish()
        result = replay.audit(self.root/'active', 'geo_huveaune', [self.path])
        self.assertTrue(result['ok'])
        self.assertEqual(result['nodesCompared'], 9)
        self.assertEqual(result['mismatchedNodes'], 0)
        self.assertEqual(result['grids'][0]['actualNoDataNodes'], 1)
        self.assertEqual(result['grids'][0]['maximumAbsoluteErrorMeters'], 0)

    def test_valid_repacked_import_cannot_hide_a_changed_elevation(self):
        self.grid['values'][1] = 100.
        self.publish()
        result = replay.audit(self.root/'active', 'geo_huveaune', [self.path])
        self.assertFalse(result['ok'])
        self.assertEqual(result['mismatchedNodes'], 1)
        self.assertEqual(result['grids'][0]['maximumAbsoluteErrorMeters'], 89)

    def test_filling_a_source_hole_is_detected_as_a_mismatch(self):
        self.grid['values'][4] = 0.
        self.grid['validPoints'] = 9
        self.grid['missingPoints'] = 0
        self.publish()
        result = replay.audit(self.root/'active', 'geo_huveaune', [self.path])
        self.assertFalse(result['ok'])
        self.assertEqual(result['mismatchedNodes'], 1)
        self.assertEqual(result['grids'][0]['actualNoDataNodes'], 1)

    def test_original_with_different_bytes_is_refused_before_any_comparison(self):
        self.publish()
        other = self.root/'different-original.tif'
        other.write_bytes(self.path.read_bytes() + b'different source bytes')
        with self.assertRaisesRegex(ValueError, 'Matching original GeoTIFF missing'):
            replay.audit(self.root/'active', 'geo_huveaune', [other])


if __name__ == '__main__':
    unittest.main()
