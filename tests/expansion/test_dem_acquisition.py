"""Native acquisition contracts: scoped URLs, coverage and bounded responses."""
from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
import unittest
from urllib.parse import urlencode
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import acquire_ign_dem as acquisition


def native_url(**changes):
    params = {"SERVICE": "WMS", "REQUEST": "GetMap", "CRS": "EPSG:2154", "LAYERS": acquisition.MNT_LAYER,
              "FORMAT": "image/geotiff", "BBOX": "908000,6247000,909000,6248000", "WIDTH": "2000", "HEIGHT": "2000", "FILENAME": "fixture_MNT.tif"}
    params.update(changes)
    return "https://data.geopf.fr/wms-r?" + urlencode(params)


def metadata_feature(geometry=None):
    return {"type": "Feature", "id": "metadata.fixture", "properties": {"systeme_planimetrique": "LAMB93", "systeme_altimetrique": "IGN69", "url_mnt": native_url()},
            "geometry": geometry or {"type": "Polygon", "coordinates": [[[5.5, 43.2], [5.6, 43.2], [5.6, 43.4], [5.5, 43.4], [5.5, 43.2]]]}}


def atom(page=1, pages=1, total=1, title="LiDAR fixture"):
    return f'<feed xmlns="{acquisition.ATOM}" xmlns:g="{acquisition.GPF}" g:page="{page}" g:pagecount="{pages}" g:totalentries="{total}"><entry><title>{title}</title><link type="application/atom+xml" href="https://data.geopf.fr/telechargement/resource/FIXTURE"/></entry></feed>'.encode()


class AcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="native-dem-acquisition-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_urls_reject_extra_hosts_credentials_and_non_https(self):
        self.assertEqual(acquisition.checked_url(native_url()), native_url())
        for url in ["http://data.geopf.fr/wms-r", "https://other.example/wms-r", "https://key@data.geopf.fr/wms-r",
                    "https://data.geopf.fr:444/wms-r", "https://data.geopf.fr/unrelated", "https://data.geopf.fr/wms-r#fragment"]:
            with self.subTest(url=url), self.assertRaises(acquisition.AcquisitionError):
                acquisition.checked_url(url)

    def test_atom_pagination_and_entity_limits_are_checked(self):
        page, pages, total, entries = acquisition.atom_page(atom())
        self.assertEqual((page, pages, total), (1, 1, 1))
        self.assertEqual(entries[0]["title"], "LiDAR fixture")
        for raw in [atom(pages=21), b"<feed/>", b"<!DOCTYPE feed [<!ENTITY x 'x'>]><feed/>", atom()[:-6]]:
            with self.assertRaises(acquisition.AcquisitionError):
                acquisition.atom_page(raw)

    def test_complete_catalogue_pagination_is_required(self):
        class Fake:
            def __init__(self):
                self.calls = 0
            def read(self, _):
                self.calls += 1
                return atom(page=self.calls, pages=2, total=2)
        client = Fake()
        receipt = acquisition.discover_catalogue(client, self.root)
        self.assertEqual((client.calls, receipt["resources"], receipt["pages"]), (2, 2, 2))
        self.assertTrue((self.root / "catalogue-page-2.xml").exists())
        with self.assertRaisesRegex(acquisition.AcquisitionError, "pagination was ignored"):
            acquisition.discover_catalogue(type("Broken", (), {"read": lambda self, _: atom(page=1, pages=2, total=2)})(), self.root)

    def test_only_metadata_provided_numeric_mnt_requests_are_accepted(self):
        self.assertEqual(acquisition.native_request(native_url())["size"], [2000, 2000])
        for changes in [{"LAYERS": "SHADOW"}, {"FORMAT": "image/png"}, {"CRS": "EPSG:4326"}, {"WIDTH": "999999"},
                        {"BBOX": "1,2,0,4"}, {"FILENAME": "../unsafe.tif"}]:
            with self.subTest(changes=changes), self.assertRaises(acquisition.AcquisitionError):
                acquisition.native_request(native_url(**changes))

    def test_tile_must_cover_patch_and_have_documented_crs(self):
        feature = metadata_feature()
        payload = {"type": "FeatureCollection", "numberMatched": 1, "features": [feature]}
        selected, request = acquisition.select_tile(payload, [43.29, 5.56, 43.30, 5.57])
        self.assertEqual(selected["id"], "metadata.fixture")
        self.assertEqual(request["crs"], "EPSG:2154")
        with self.assertRaisesRegex(acquisition.AcquisitionError, "covers"):
            acquisition.select_tile(payload, [44, 5.56, 44.01, 5.57])
        feature["properties"]["systeme_altimetrique"] = "unknown"
        with self.assertRaisesRegex(acquisition.AcquisitionError, "covers"):
            acquisition.select_tile(payload, [43.29, 5.56, 43.30, 5.57])

    def test_holes_and_truncated_metadata_do_not_count_as_coverage(self):
        geometry = {"type": "MultiPolygon", "coordinates": [[[[5.5, 43.2], [5.6, 43.2], [5.6, 43.4], [5.5, 43.4], [5.5, 43.2]],
                                                                [[5.55, 43.25], [5.58, 43.25], [5.58, 43.35], [5.55, 43.35], [5.55, 43.25]]]]}
        payload = {"type": "FeatureCollection", "numberMatched": 1, "features": [metadata_feature(geometry)]}
        with self.assertRaisesRegex(acquisition.AcquisitionError, "covers"):
            acquisition.select_tile(payload, [43.29, 5.56, 43.30, 5.57])
        payload["numberMatched"] = 99
        with self.assertRaisesRegex(acquisition.AcquisitionError, "truncated"):
            acquisition.select_tile(payload, [43.29, 5.56, 43.30, 5.57])

    def fake_client(self, raw, length=None):
        class Response(io.BytesIO):
            def __init__(self):
                super().__init__(raw)
                self.headers = {"Content-Length": str(length if length is not None else len(raw))}
        return type("FakeClient", (), {"open": lambda self, _: Response()})()

    def test_downloads_are_content_addressed_and_declared_lengths_verified(self):
        client = self.fake_client(b"synthetic raster bytes")
        path, digest, size = acquisition.download(client, native_url(), self.root, "fixture.tif")
        self.assertTrue(path.name.startswith(digest[:16]))
        self.assertEqual(path.read_bytes(), b"synthetic raster bytes")
        self.assertEqual(size, 22)
        again = acquisition.download(client, native_url(), self.root, "fixture.tif")
        self.assertEqual(again[0], path)
        with self.assertRaisesRegex(acquisition.AcquisitionError, "truncated"):
            acquisition.download(self.fake_client(b"short", 10), native_url(), self.root, "bad.tif")
        self.assertEqual(list(self.root.glob("*.part")), [])

    def test_download_budget_is_enforced_without_publishing_partial_files(self):
        with patch.object(acquisition, "MAX_DOWNLOAD_BYTES", 3):
            with self.assertRaisesRegex(acquisition.AcquisitionError, "budget"):
                acquisition.download(self.fake_client(b"too large"), native_url(), self.root, "bad.tif")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_invalid_or_oversized_patch_is_rejected_before_network(self):
        with patch.object(acquisition, "Client", side_effect=AssertionError("network must not start")):
            with self.assertRaises(acquisition.DemConversionError):
                acquisition.acquire([43.29, 5.56, 43.30, 5.57], float("nan"), self.root)
            with self.assertRaisesRegex(acquisition.AcquisitionError, "native patch exceeds"):
                acquisition.acquire([43.295, 5.569, 43.298, 5.572], .5, self.root)


if __name__ == "__main__":
    unittest.main()
