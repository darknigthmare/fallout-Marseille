"""Real GeoTIFF conversion tests; all rasters are explicit synthetic fixtures."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import convert_ign_dem as converter

try:
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.warp import transform
except ImportError:
    rasterio = None


@unittest.skipUnless(rasterio is not None, "install optional requirements-geo.txt for real GeoTIFF tests")
class DemConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dem-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.values = np.array([[10, 11, 12], [20, -9999, 22], [30, 31, 32]], dtype="float32")
        self.bbox = [43.2965, 5.5685, 43.2985, 5.5705]
        self.path = self.write("geographic.tif", self.values)

    def write(self, name, values, *, crs="EPSG:4326", affine=None, scales=None, offsets=None):
        target = self.root / name
        with rasterio.open(target, "w", driver="GTiff", height=values.shape[0], width=values.shape[1],
                           count=1, dtype=str(values.dtype), crs=crs,
                           transform=affine if affine is not None else from_origin(5.568, 43.299, .001, .001), nodata=-9999) as raster:
            raster.write(values, 1)
            if scales is not None:
                raster.scales = scales
            if offsets is not None:
                raster.offsets = offsets
        return target

    def convert(self, path=None, bbox=None, spacing=112):
        return converter.convert_dem(path or self.path, bbox or self.bbox, spacing, "NGF-IGN69")

    def test_actual_geotiff_preserves_rows_axes_samples_and_nodata(self):
        result = self.convert()
        self.assertEqual((result["width"], result["height"]), (3, 3))
        self.assertEqual(result["rowOrder"], "north-to-south")
        self.assertEqual(result["values"], [10., 11., 12., 20., None, 22., 30., 31., 32.])
        self.assertEqual((result["validPoints"], result["missingPoints"]), (8, 1))
        proof = result["conversion"]
        self.assertEqual(proof["inputSha256"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(proof["crs"], "EPSG:4326")
        self.assertEqual(proof["nativePixelSize"], [.001, .001])
        self.assertTrue(proof["resampled"])
        self.assertTrue(proof["nodataPreserved"])
        self.assertEqual(proof["resampling"], "nearest")

    def test_projected_lambert93_raster_uses_correct_xy_order(self):
        path = self.write("lambert.tif", self.values, crs="EPSG:2154", affine=from_origin(906000, 6257000, 10, 10))
        lons, lats = transform("EPSG:2154", "EPSG:4326", [906005, 906025], [6256975, 6256995])
        bbox = [min(lats), min(lons), max(lats), max(lons)]
        result = self.convert(path, bbox=bbox, spacing=11)
        self.assertEqual((result["width"], result["height"]), (3, 3))
        self.assertEqual(result["values"][:3], [10., 11., 12.])
        self.assertEqual(result["values"][-3:], [30., 31., 32.])
        self.assertIsNone(result["values"][4])
        self.assertEqual(result["conversion"]["nativePixelSize"], [10., 10.])
        self.assertEqual(result["conversion"]["crs"], "EPSG:2154")

    def test_finer_grid_does_not_interpolate_across_nodata(self):
        result = self.convert(spacing=20)
        values = result["values"]
        self.assertGreater(result["missingPoints"], 1)
        self.assertTrue(set(v for v in values if v is not None).issubset({10, 11, 12, 20, 22, 30, 31, 32}))
        centre = (result["height"] // 2) * result["width"] + result["width"] // 2
        self.assertIsNone(values[centre])

    def test_missing_source_crs_is_rejected_instead_of_guessed(self):
        path = self.write("unknown-crs.tif", self.values, crs=None)
        with self.assertRaisesRegex(converter.DemConversionError, "EPSG CRS"):
            self.convert(path)

    def test_documented_source_crs_override_is_explicit_and_cannot_conflict(self):
        malformed = 'PROJCS["EPSG:2154",GEOGCS["unknown",DATUM["unnamed",SPHEROID["unretrievable - using WGS84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",3],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],UNIT["metre",1]]'
        path = self.write("unrecognized-wkt.tif", self.values, crs=malformed, affine=from_origin(906000, 6257000, 10, 10))
        with rasterio.open(path) as source:
            self.assertIsNone(source.crs.to_epsg())
        lons, lats = transform("EPSG:2154", "EPSG:4326", [906005, 906025], [6256975, 6256995])
        bbox = [min(lats), min(lons), max(lats), max(lons)]
        with self.assertRaisesRegex(converter.DemConversionError, "source-crs"):
            self.convert(path, bbox=bbox, spacing=11)
        result = converter.convert_dem(path, bbox, 11, "NGF-IGN69", source_crs="EPSG:2154")
        self.assertEqual(result["values"][:3], [10., 11., 12.])
        self.assertEqual(result["conversion"]["crs"], "EPSG:2154")
        with self.assertRaisesRegex(converter.DemConversionError, "conflicts"):
            converter.convert_dem(self.path, self.bbox, 112, "NGF-IGN69", source_crs="EPSG:2154")

    def test_nonoverlap_and_invalid_grid_budgets_fail_before_large_read(self):
        with self.assertRaisesRegex(converter.DemConversionError, "does not overlap"):
            self.convert(bbox=[44, 6, 44.001, 6.001])
        with self.assertRaisesRegex(converter.DemConversionError, "sample budget"):
            self.convert(bbox=[40, 0, 50, 10], spacing=.5)
        with patch.object(converter, "MAX_WINDOW_CELLS", 4):
            with self.assertRaisesRegex(converter.DemConversionError, "source crop exceeds"):
                self.convert()

    def test_partial_coverage_stays_nodata_and_all_missing_is_rejected(self):
        result = self.convert(bbox=[43.2955, 5.5675, 43.2985, 5.5705], spacing=90)
        self.assertGreater(result["missingPoints"], 1)
        self.assertIsNone(result["values"][0])
        path = self.write("all-nodata.tif", np.full((3, 3), -9999, dtype="float32"))
        with self.assertRaisesRegex(converter.DemConversionError, "no measured altitude"):
            self.convert(path)

    def test_band_scale_offset_are_applied_to_measured_values(self):
        path = self.write("scaled.tif", self.values.astype("int16"), scales=(.5,), offsets=(100,))
        result = self.convert(path)
        self.assertEqual(result["values"][0], 105.)
        self.assertEqual(result["values"][-1], 116.)
        self.assertIsNone(result["values"][4])

    def test_rotated_raster_and_unmasked_invalid_altitude_are_rejected(self):
        affine = rasterio.Affine(.001, .00001, 5.568, 0, -.001, 43.299)
        rotated = self.write("rotated.tif", self.values, affine=affine)
        with self.assertRaisesRegex(converter.DemConversionError, "north-up"):
            self.convert(rotated)
        values = self.values.copy()
        values[0, 0] = -99999
        invalid = self.write("bad-nodata.tif", values)
        with self.assertRaisesRegex(converter.DemConversionError, "unmasked elevation"):
            self.convert(invalid)

    def test_cli_output_roundtrips_through_measured_source_importer(self):
        from world_sources import read_terrain, provenance
        target = self.root / "converted.json"
        args = [str(self.path), "--bbox", ",".join(map(str, self.bbox)), "--spacing", "112",
                "--vertical-datum", "NGF-IGN69", "--output", str(target)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(converter.main(args), 0)
        source = provenance(name="Synthetic GeoTIFF fixture", license="Test fixture", attribution="Conversion test",
                            acquired_at="2026-10-23", resource="test-dem", vertical_datum="NGF-IGN69")
        imported = read_terrain(target.read_bytes(), "geo_huveaune", source, self.bbox)
        self.assertEqual(imported["values"], json.loads(target.read_text())["values"])
        self.assertTrue(imported["provenance"]["resampled"])
        self.assertEqual(imported["provenance"]["conversion"]["inputSha256"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertNotEqual(imported["provenance"]["inputSha256"], imported["provenance"]["conversion"]["inputSha256"])
        previous = target.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(converter.main(args), 1)
        self.assertEqual(target.read_bytes(), previous)

    def test_output_does_not_clobber_source_and_writes_are_explicit(self):
        args = [str(self.path), "--bbox", ",".join(map(str, self.bbox)), "--spacing", "112",
                "--vertical-datum", "NGF-IGN69", "--output", str(self.path), "--replace"]
        previous = self.path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(converter.main(args), 1)
        self.assertEqual(self.path.read_bytes(), previous)
        target = self.root / "grid.json"
        target.write_text("existing")
        with self.assertRaisesRegex(converter.DemConversionError, "output exists"):
            converter.write_grid(target, self.convert())
        self.assertEqual(target.read_text(), "existing")


if __name__ == "__main__":
    unittest.main()
