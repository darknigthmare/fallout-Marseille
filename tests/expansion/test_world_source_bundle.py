"""Offline distribution of real source extracts: integrity and user preservation."""
from pathlib import Path
import hashlib
import json
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import world_source_bundle as archive
import world_sources as sources


class SourceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.active = self.root / 'active'
        self.receipt = self.root / 'archives/manifest.json'
        self.output = self.root / 'restored'
        self.source = sources.provenance(name='Archive test fixture', resource='archive-fixture', license='Test fixture',
                                         attribution='Synthetic test only', acquired_at='2026-10-23', vertical_datum='NGF-IGN69')
        collection = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'id': 'building.1', 'properties': {'height': 6},
            'geometry': {'type': 'Polygon', 'coordinates': [[[5.57, 43.296], [5.571, 43.296], [5.571, 43.297], [5.57, 43.297], [5.57, 43.296]],
                [[5.5703, 43.2963], [5.5703, 43.2967], [5.5707, 43.2967], [5.5707, 43.2963], [5.5703, 43.2963]]]}}]}
        features = sources.read_geojson(json.dumps(collection).encode(), self.source, [43.245, 5.43, 43.335, 5.64])
        sources.publish_bundle(self.active, 'geo_huveaune', self.source, features=features)
        self.packed = archive.package(self.active, self.receipt.parent / 'requested.zip', self.receipt)

    def tearDown(self):
        self.temporary.cleanup()

    def test_roundtrip_validates_all_runtime_bytes_and_holes(self):
        result = archive.install(self.receipt, self.output)
        self.assertEqual(result['status'], 'installed')
        before, _ = archive.validate_directory(self.active)
        after, _ = archive.validate_directory(self.output)
        self.assertEqual(before, after)
        bundle = json.loads(next(raw for name, raw in after.items() if name != 'index.json'))
        self.assertEqual(len(bundle['features'][0]['geometry']['coordinates']), 2)

    def test_rerun_preserves_an_existing_valid_user_import(self):
        archive.install(self.receipt, self.output)
        original = (self.output / 'index.json').read_bytes()
        result = archive.install(self.receipt, self.output)
        self.assertEqual(result['status'], 'preserved')
        self.assertEqual((self.output / 'index.json').read_bytes(), original)

    def test_damaged_existing_user_data_is_never_overwritten(self):
        archive.install(self.receipt, self.output)
        (self.output / 'index.json').write_bytes(b'{broken')
        with self.assertRaises(sources.SourceError):
            archive.install(self.receipt, self.output)
        self.assertEqual((self.output / 'index.json').read_bytes(), b'{broken')

    def test_outer_archive_corruption_fails_before_publishing_index(self):
        path = self.receipt.parent / self.packed['archive']
        raw = path.read_bytes(); path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        with self.assertRaisesRegex(sources.SourceError, 'SHA-256'):
            archive.install(self.receipt, self.output)
        self.assertFalse((self.output / 'index.json').exists())

    def test_member_digest_mismatch_fails_even_with_valid_outer_archive(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['members'][0]['sha256'] = '0' * 64
        self.receipt.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(sources.SourceError, 'member digest'):
            archive.install(self.receipt, self.output)
        self.assertFalse((self.output / 'index.json').exists())

    def test_path_traversal_receipt_cannot_create_external_files(self):
        receipt = json.loads(self.receipt.read_text())
        receipt['members'][0]['name'] = '../escaped.json'
        self.receipt.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(sources.SourceError, 'unsafe'):
            archive.install(self.receipt, self.output)
        self.assertFalse((self.root / 'escaped.json').exists())

    def test_extra_zip_members_are_rejected_before_extraction(self):
        path = self.receipt.parent / self.packed['archive']
        with zipfile.ZipFile(path, 'a') as z:
            z.writestr('undeclared.json', '{}')
        receipt = json.loads(self.receipt.read_text())
        receipt.update(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.receipt.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(sources.SourceError, 'undeclared'):
            archive.install(self.receipt, self.output)
        self.assertFalse((self.output / 'index.json').exists())

    def test_restoration_rejects_symlink_destination(self):
        real = self.root / 'real'; real.mkdir()
        self.output.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(sources.SourceError, 'symlink'):
            archive.install(self.receipt, self.output)
        self.assertEqual(list(real.iterdir()), [])

    def test_content_addressed_orphan_conflict_cannot_overwrite_user_file(self):
        self.output.mkdir()
        member = next(row['name'] for row in self.packed['members'] if row['name'] != 'index.json')
        (self.output / member).write_bytes(b'user file')
        with self.assertRaisesRegex(sources.SourceError, 'conflicts'):
            archive.install(self.receipt, self.output)
        self.assertEqual((self.output / member).read_bytes(), b'user file')
        self.assertFalse((self.output / 'index.json').exists())

    def test_pack_is_deterministic_and_requires_explicit_receipt_replacement(self):
        other = self.root / 'second/manifest.json'
        result = archive.package(self.active, other.parent / 'requested.zip', other)
        self.assertEqual(self.packed['sha256'], result['sha256'])
        with self.assertRaisesRegex(sources.SourceError, 'explicit --replace'):
            archive.package(self.active, other.parent / 'requested.zip', other)

    def test_no_archive_keeps_existing_base_game_workflow(self):
        self.assertIsNone(archive.prepare_if_bundled(self.root / 'not-a-distribution'))

    def test_audit_uses_verified_geometry_without_returning_grid_values(self):
        report = archive.audit_details(self.active)
        self.assertTrue(report['ok'])
        self.assertEqual(report['totalBuildings'], 1)
        self.assertEqual(report['totalRoads'], 0)
        self.assertEqual(report['regions'][0]['estimatedBuildingHeights'], 0)
        self.assertEqual(report['regions'][0]['terrain'], [])
        self.assertNotIn('coordinates', json.dumps(report))
        descriptor = json.loads((self.active / 'index.json').read_text())['regions']['geo_huveaune']
        path = self.active / Path(descriptor['path']).name
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaises(sources.SourceError):
            archive.audit_details(self.active)

    def test_absent_sources_are_distinct_from_invalid_sources(self):
        self.assertFalse(archive.audit_details(self.root / 'missing')['present'])
        (self.active / 'index.json').write_text('{}')
        with self.assertRaises(sources.SourceError):
            archive.audit_details(self.active)

    def test_receipt_cannot_point_to_an_archive_in_a_different_directory(self):
        with self.assertRaisesRegex(sources.SourceError, 'share'):
            archive.package(self.active, self.root / 'elsewhere/archive.zip', self.root / 'third/manifest.json')


if __name__ == '__main__':
    unittest.main()
