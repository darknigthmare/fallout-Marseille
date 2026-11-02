"""Commune imports use the installed declared envelope, not legacy macro bounds.

All grids and city declarations in these tests are explicit synthetic fixtures.
"""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import import_world_sources as importer
from world_sources import SourceError, canonical


class CommuneImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.old = [43.22, 5.285, 43.34, 5.51]
        self.city = [43.1696313, 5.22875102, 43.39105653, 5.53254336]
        self.manifest = self.root / 'data/map_pack/terrain/manifest_v039.json'
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_bytes(canonical({'regions': [{'macro': 'geo_marseille', 'bbox': self.old}]}))
        self.city_path = self.root / 'data/map_pack/city/index.json'
        self.city_path.parent.mkdir(parents=True)
        self.city_data = {'schemaVersion': 1, 'crs': 'EPSG:4326', 'region': 'geo_marseille_commune',
                          'municipality': {'code': '13055', 'bbox': self.city}, 'coverage': {'complete': True}}
        self.city_path.write_bytes(canonical(self.city_data))

    def tearDown(self):
        self.temporary.cleanup()

    def test_complete_city_adds_northern_extent_without_changing_legacy_region(self):
        regions = importer.region_bounds(self.root)
        self.assertEqual(regions['geo_marseille_commune'], self.city)
        self.assertEqual(regions['geo_marseille'], self.old)
        self.assertGreater(regions['geo_marseille_commune'][2], 43.37)
        self.assertLess(regions['geo_marseille'][2], 43.37)

    def test_missing_optional_city_leaves_all_old_imports_available(self):
        self.city_path.unlink()
        self.assertEqual(importer.region_bounds(self.root), {'geo_marseille': self.old})

    def test_partial_wrong_crs_or_unrelated_municipality_never_grants_city_extent(self):
        for change in ({'coverage': {'complete': False}}, {'crs': 'EPSG:2154'},
                       {'region': 'geo_unknown'}, {'municipality': {'code': '13001', 'bbox': self.city}},
                       {'municipality': {'code': '13055', 'bbox': self.city[::-1]}}):
            with self.subTest(change=change):
                self.city_path.write_bytes(canonical({**self.city_data, **change}))
                with self.assertRaises(SourceError):
                    importer.region_bounds(self.root)

    def test_city_index_symlink_is_refused(self):
        original = self.city_path.with_name('real-index.json')
        self.city_path.rename(original)
        self.city_path.symlink_to(original)
        with self.assertRaisesRegex(SourceError, 'symlink'):
            importer.region_bounds(self.root)

    def test_cli_imports_a_northern_grid_but_refuses_nodes_outside_actual_commune(self):
        terrain = self.root / 'northern-fixture.json'
        grid = {'width': 2, 'height': 2, 'bbox': [43.369, 5.357, 43.372, 5.361],
                'values': [35, 36, 37, 38], 'rowOrder': 'north-to-south'}
        terrain.write_bytes(canonical(grid))
        args = ['--region', 'geo_marseille_commune', '--terrain', str(terrain),
                '--source', 'Synthetic northern fixture', '--resource', 'fixture-northern',
                '--license', 'CC0 fixture', '--attribution', 'Synthetic fixture only',
                '--acquired-at', '2026-11-01', '--vertical-datum', 'NGF-IGN69',
                '--output', str(self.root / 'output')]
        with patch.object(importer, 'region_bounds', return_value=importer.region_bounds(self.root)):
            with redirect_stdout(StringIO()):
                self.assertEqual(importer.main(args), 0)
            before = (self.root / 'output/index.json').read_bytes()
            terrain.write_bytes(canonical({**grid, 'bbox': [43.40, 5.357, 43.41, 5.361]}))
            with redirect_stderr(StringIO()):
                self.assertEqual(importer.main(args), 1)
            self.assertEqual((self.root / 'output/index.json').read_bytes(), before)
            descriptor = json.loads(before)['regions']['geo_marseille_commune']
            bundle = json.loads((self.root / 'output' / Path(descriptor['path']).name).read_bytes())
            self.assertEqual(bundle['terrain']['values'], grid['values'])


if __name__ == '__main__':
    unittest.main()
