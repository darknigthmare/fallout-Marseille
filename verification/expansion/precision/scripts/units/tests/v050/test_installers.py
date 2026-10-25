#!/usr/bin/env python3
"""Regression tests for map installation, with an optional real offline install.

Unit fixtures are deliberately tiny protobuf/terrain samples; only the separate
--offline-integration check uses the actual 24 shipped ZIPs and eight IGN grids.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import install_real_map_v038 as vector
import install_local_pack_v041 as pack
import install_terrain_v039 as terrain
from validate_real_map_v046 import audit

PBF = b'\x1a\x09\x0a\x05roads\x78\x02'
EMPTY_SHA = hashlib.sha256(b'').hexdigest()
REPORTS = ROOT / 'verification/v050'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def response(raw=b'', status=200, headers=None):
    class Response(io.BytesIO):
        def getcode(self):
            return self.status
    r = Response(raw)
    r.status = status
    r.headers = headers or {}
    return r


def tile_row(empty=False, y=1):
    raw = b'' if empty else PBF
    return {'path': f'cadastre/16/1/{y}.pbf', 'empty': empty,
            'bytes': len(raw), 'sha256': digest(raw)}


def proof(y=2):
    return {'officialEmpty': True, 'source': 'cadastre', 'z': 16,
            'x': 1, 'y': y, 'sha256': EMPTY_SHA}


def vector_row(empty=False, y=1):
    return {'source': 'cadastre', 'z': 16, 'x': 1, 'y': y,
            'local': f'data/map_pack/cadastre/16/1/{y}.pbf',
            'key': f'16/1/{y}', 'direct': 'https://example.invalid/tile.pbf',
            'relay': 'https://example.invalid/relay.pbf',
            'sha256': EMPTY_SHA if empty else digest(PBF)}


def make_chunk(directory, mutate=None, extras=None, duplicate=None):
    rows = [tile_row(), tile_row(True, 2)]
    meta = {'source': 'cadastre', 'cursor': 0, 'limit': 2, 'files': rows}
    files = {rows[0]['path']: PBF, rows[1]['path']: b'',
             rows[1]['path'] + '.empty.json': json.dumps(proof()).encode()}
    if mutate:
        mutate(meta, files)
    if extras:
        files.update(extras)
    path = directory / 'cadastre_00000_2.zip'
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as z:
        for name, raw in files.items():
            z.writestr(name, raw)
        z.writestr('chunk_manifest.json', json.dumps(meta))
        if duplicate:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                z.writestr(duplicate, files[duplicate])
    raw = path.read_bytes()
    expected = {'name': path.name, 'source': 'cadastre', 'cursor': 0,
                'rows': 2, 'sha256': digest(raw), 'archiveBytes': len(raw)}
    return path, expected


def terrain_fixture():
    manifest = copy.deepcopy(json.loads(terrain.DEFAULT_MANIFEST.read_text()))
    manifest['grid'].update(width=2, height=2)
    region = {'macro': 'geo_unit', 'bbox': [43.0, 5.0, 43.01, 5.01]}
    manifest['regions'] = [region]
    data = {'macro': region['macro'], 'bbox': region['bbox'], 'width': 2,
            'height': 2, 'rowOrder': 'north-to-south',
            'sourceResource': terrain.OFFICIAL_RESOURCE,
            'values': [110.52, None, 115.0, None]}
    return region, manifest, data


def official_response(request, values=None):
    payload = json.loads(request.data)
    points = list(zip(map(float, payload['lat'].split('|')),
                      map(float, payload['lon'].split('|'))))
    rows = [{'lat': lat, 'lon': lon, 'z': values[i] if values else 110.52}
            for i, (lat, lon) in enumerate(points)]
    return response(json.dumps({'elevations': rows}).encode())


class TemporaryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mistral-install-unit-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)


class VectorTests(TemporaryTest):
    def test_gzip_and_identity_decode_to_identical_tile(self):
        for raw, encoding in ((PBF, None), (PBF, 'identity'),
                              (gzip.compress(PBF), None),
                              (gzip.compress(PBF), 'gzip')):
            with self.subTest(encoding=encoding, compressed=raw != PBF):
                self.assertEqual(vector.decode_http_body(raw, encoding), PBF)

    def test_gzip_both_wire_and_decoded_limits(self):
        for raw, limit in ((b'x' * 101, 100), (gzip.compress(b'x' * 10000), 100)):
            with self.subTest(limit=limit, wire=len(raw)):
                with self.assertRaises(RuntimeError):
                    vector.decode_http_body(raw, max_bytes=limit)

    def test_corrupt_truncated_and_concatenated_gzip_rejected(self):
        gz = gzip.compress(PBF)
        for raw in (gz[:-1], gz + b'junk', gz + gz, b'\x1f\x8bbroken'):
            with self.subTest(raw=raw[:8]):
                with self.assertRaises(RuntimeError):
                    vector.decode_http_body(raw)

    def test_unsupported_or_contradictory_encoding_rejected(self):
        for encoding in ('br', 'gzip', 'gzip, br'):
            with self.subTest(encoding=encoding):
                with self.assertRaises(RuntimeError):
                    vector.decode_http_body(PBF, encoding)

    def test_http_gzip_checks_decoded_sha256(self):
        r = response(gzip.compress(PBF), headers={
            'content-encoding': 'gzip', 'x-map-sha256': digest(PBF)})
        with patch.object(vector, 'urlopen', return_value=r):
            raw, meta = vector.request('https://example.invalid/tile', False, 1)
        self.assertEqual(raw, PBF)
        self.assertFalse(meta['officialEmpty'])
        self.assertEqual(meta['wireBytes'], len(gzip.compress(PBF)))

    def test_http_200_empty_never_creates_official_proof(self):
        for raw, headers in ((b'', {}), (gzip.compress(b''), {'content-encoding': 'gzip'})):
            with self.subTest(compressed=bool(raw)):
                with patch.object(vector, 'urlopen', return_value=response(raw, headers=headers)):
                    with self.assertRaises((RuntimeError, ValueError)):
                        vector.request('https://example.invalid/tile', False, 1)

    def test_only_explicit_empty_response_is_accepted(self):
        for status, headers in ((204, {}), (200, {'x-map-empty': '1'})):
            with self.subTest(status=status):
                with patch.object(vector, 'urlopen', return_value=response(status=status, headers=headers)):
                    raw, meta = vector.request('https://example.invalid/tile', False, 1)
                self.assertEqual(raw, b'')
                self.assertIs(meta['officialEmpty'], True)

    def test_empty_with_payload_and_wrong_remote_hash_rejected(self):
        for raw, headers in ((PBF, {'x-map-empty': '1'}), (PBF, {'x-map-sha256': '0' * 64}),
                             (b'', {'x-map-empty': '1', 'x-map-sha256': '0' * 64})):
            with self.subTest(headers=headers):
                with patch.object(vector, 'urlopen', return_value=response(raw, headers=headers)):
                    with self.assertRaises(RuntimeError):
                        vector.request('https://example.invalid/tile', False, 1)

    def test_failed_download_preserves_previous_invalid_file(self):
        row = vector_row()
        dest = self.path / row['local'].removeprefix('data/map_pack/')
        dest.parent.mkdir(parents=True)
        dest.write_bytes(b'previous interrupted download')
        with patch.object(vector, 'request', side_effect=OSError('network unavailable')):
            result = vector.fetch(row, self.path, 'auto', 1, 1)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(dest.read_bytes(), b'previous interrupted download')
        self.assertFalse(vector.marker(dest).exists())

    def test_pinned_nonempty_tile_rejects_remote_empty(self):
        row = vector_row()
        with patch.object(vector, 'request', return_value=(b'', {'officialEmpty': True})):
            result = vector.fetch(row, self.path, 'direct', 1, 1)
        self.assertEqual(result['status'], 'error')
        self.assertFalse((self.path / 'cadastre/16/1/1.pbf').exists())

    def test_cache_validation_is_read_only_and_checks_empty_coordinate(self):
        dest = self.path / '1.pbf'
        dest.write_bytes(PBF)
        marker = vector.marker(dest)
        marker.write_text(json.dumps(proof(999)))
        self.assertTrue(vector.validate(dest, digest(PBF), vector_row())[0])
        self.assertTrue(marker.exists())
        dest.write_bytes(b'')
        self.assertFalse(vector.validate(dest, None, vector_row(True))[0])
        marker.write_text(json.dumps(proof(1)))
        self.assertFalse(vector.validate(dest, digest(PBF), vector_row())[0])
        self.assertTrue(vector.validate(dest, EMPTY_SHA, vector_row(True))[0])

    def test_empty_proof_is_committed_before_zero_byte_tile(self):
        row = vector_row(True)
        dest = self.path / 'cadastre/16/1/1.pbf'
        dest.parent.mkdir(parents=True)
        dest.write_bytes(b'previous')
        with patch.object(vector, 'request', return_value=(b'', {'officialEmpty': True})), \
             patch.object(vector, 'atomic_text', side_effect=OSError('disk full')):
            result = vector.fetch(row, self.path, 'direct', 1, 1)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(dest.read_bytes(), b'previous')


class ArchiveTests(TemporaryTest):
    def test_local_gzip_transport_recovers_exact_zip_without_network(self):
        path, expected = make_chunk(self.path)
        original = path.read_bytes()
        path.with_name(path.name + '.gz').write_bytes(gzip.compress(original, mtime=0))
        path.unlink()
        # Also exercise the case where supplied transports and the cache share
        # a directory: the decoded ZIP still has to be written.
        for cache in (self.path / 'cache', self.path):
            with self.subTest(cache=cache.name):
                with patch.object(pack, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
                    found = pack.request_chunk(expected, {}, cache, 1, 1, self.path)
                self.assertEqual(found.read_bytes(), original)
                self.assertEqual(pack.inspect_chunk(found, expected)[1][0]['sha256'], digest(PBF))
                net.assert_not_called()

    def test_local_gzip_corruption_preserves_existing_cache(self):
        path, expected = make_chunk(self.path)
        original = path.read_bytes()
        path.unlink()
        zipped = gzip.compress(original, mtime=0)
        compressed = path.with_name(path.name + '.gz')
        cache = self.path / 'cache'
        cache.mkdir()
        dest = cache / path.name
        previous = b'PKprevious interrupted archive'
        for raw in (b'not gzip', zipped[:-8], zipped + b'corrupt trailing bytes'):
            with self.subTest(rawBytes=len(raw)):
                compressed.write_bytes(raw)
                dest.write_bytes(previous)
                with patch.object(pack, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
                    with self.assertRaises(pack.PackError):
                        pack.request_chunk(expected, {}, cache, 1, 1, self.path)
                self.assertEqual(dest.read_bytes(), previous)
                net.assert_not_called()

    def test_local_gzip_expansion_is_bounded_by_pinned_zip_size(self):
        path, expected = make_chunk(self.path)
        original = path.read_bytes()
        path.unlink()
        path.with_name(path.name + '.gz').write_bytes(gzip.compress(original + b'x' * 4_000_000, mtime=0))
        with patch.object(pack, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
            with self.assertRaisesRegex(pack.PackError, 'expansion exceeds'):
                pack.request_chunk(expected, {}, self.path / 'cache', 1, 1, self.path)
        self.assertFalse((self.path / 'cache' / path.name).exists())
        net.assert_not_called()

    def test_local_gzip_requires_original_byte_and_sha256_pins(self):
        path, expected = make_chunk(self.path)
        original = path.read_bytes()
        path.unlink()
        path.with_name(path.name + '.gz').write_bytes(gzip.compress(original, mtime=0))
        for changed in ({'archiveBytes': None}, {'archiveBytes': True},
                        {'archiveBytes': len(original) + 1}, {'sha256': None},
                        {'sha256': '0' * 64}):
            with self.subTest(changed=changed):
                with self.assertRaises(pack.PackError):
                    pack.request_chunk({**expected, **changed}, {}, self.path / 'cache', 1, 1, self.path)
                self.assertFalse((self.path / 'cache' / path.name).exists())

    def test_valid_cache_is_preserved_when_gzip_source_is_corrupt(self):
        path, expected = make_chunk(self.path)
        original = path.read_bytes()
        path.unlink()
        path.with_name(path.name + '.gz').write_bytes(b'broken gzip')
        cache = self.path / 'cache'
        cache.mkdir()
        dest = cache / path.name
        dest.write_bytes(original)
        with patch.object(pack, 'read_gzip_chunk', side_effect=AssertionError('valid cache must be reused')) as decompress, \
             patch.object(pack, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
            found = pack.request_chunk(expected, {}, cache, 1, 1, self.path)
        self.assertEqual(found, dest)
        self.assertEqual(found.read_bytes(), original)
        decompress.assert_not_called()
        net.assert_not_called()

    def test_complete_chunk_round_trip_and_marker_cleanup(self):
        path, expected = make_chunk(self.path)
        output = self.path / 'out'
        stale = output / 'cadastre/16/1/1.pbf.empty.json'
        stale.parent.mkdir(parents=True)
        stale.write_text(json.dumps(proof(1)))
        result = pack.extract_chunk(path, expected, output)
        self.assertEqual((result['rows'], result['empty']), (2, 1))
        self.assertEqual((output / 'cadastre/16/1/1.pbf').read_bytes(), PBF)
        self.assertFalse(stale.exists())
        self.assertEqual(json.loads((output / 'cadastre/16/1/2.pbf.empty.json').read_text()), proof())

    def test_archive_pin_and_size_mismatch_rejected(self):
        path, expected = make_chunk(self.path)
        for changed in ({'sha256': '0' * 64}, {'sha256': 'invalid'}, {'archiveBytes': 1}):
            with self.subTest(changed=changed):
                with self.assertRaises(pack.PackError):
                    pack.inspect_chunk(path, {**expected, **changed})

    def test_corrupt_proof_coordinate_or_digest_rejected_before_extraction(self):
        output = self.path / 'out'
        dest = output / 'cadastre/16/1/1.pbf'
        dest.parent.mkdir(parents=True)
        dest.write_bytes(b'original kept')
        for changed in ({'y': 999}, {'source': 'base'}, {'z': True},
                        {'sha256': '0' * 64}, {'officialEmpty': False}):
            with self.subTest(changed=changed):
                def mutate(meta, files):
                    files['cadastre/16/1/2.pbf.empty.json'] = json.dumps({**proof(), **changed}).encode()
                path, expected = make_chunk(self.path, mutate)
                with self.assertRaises(pack.PackError):
                    pack.extract_chunk(path, expected, output)
                self.assertEqual(dest.read_bytes(), b'original kept')

    def test_each_member_requires_matching_byte_count_hash_and_empty_flag(self):
        for index, field, value in ((0, 'sha256', '0' * 64), (0, 'bytes', 1),
                                    (1, 'sha256', '0' * 64), (1, 'bytes', 4),
                                    (1, 'empty', 'true')):
            with self.subTest(index=index, field=field):
                def mutate(meta, files):
                    meta['files'][index][field] = value
                path, expected = make_chunk(self.path, mutate)
                with self.assertRaises(pack.PackError):
                    pack.inspect_chunk(path, expected)

    def test_missing_empty_proof_rejected(self):
        path, expected = make_chunk(self.path, lambda meta, files: files.pop('cadastre/16/1/2.pbf.empty.json'))
        with self.assertRaises(pack.PackError):
            pack.inspect_chunk(path, expected)

    def test_duplicate_zip_members_and_duplicate_rows_rejected(self):
        path, expected = make_chunk(self.path, duplicate='cadastre/16/1/1.pbf')
        with self.assertRaises(pack.PackError):
            pack.inspect_chunk(path, expected)
        def mutate(meta, files):
            meta['files'][1] = meta['files'][0].copy()
        path, expected = make_chunk(self.path, mutate)
        with self.assertRaises(pack.PackError):
            pack.inspect_chunk(path, expected)

    def test_undeclared_files_and_unsafe_paths_rejected(self):
        for extra in ('cadastre/16/1/3.pbf', '../escape.txt', '/absolute.txt',
                      'cadastre/../../escape.txt', 'cadastre\\escape.txt'):
            with self.subTest(extra=extra):
                path, expected = make_chunk(self.path, extras={extra: PBF})
                with self.assertRaises(pack.PackError):
                    pack.inspect_chunk(path, expected)

    def test_archive_limits_are_checked_before_decompression(self):
        path, expected = make_chunk(self.path)
        for field in ('MAX_MEMBER_BYTES', 'MAX_EXPANDED_BYTES'):
            with self.subTest(limit=field):
                with patch.object(pack, field, 1), \
                     patch.object(zipfile.ZipFile, 'read', side_effect=AssertionError('decompressed before size cap')):
                    with self.assertRaises(pack.PackError):
                        pack.inspect_chunk(path, expected)

    def test_wrong_source_or_zoom_is_rejected(self):
        for path in ('france-vector/14/1/1.pbf', 'cadastre/14/1/1.pbf',
                     'cadastre/16/65536/1.pbf'):
            with self.subTest(path=path):
                with self.assertRaises(pack.PackError):
                    pack.coordinate(path, 'cadastre')

    def test_invalid_local_chunk_cannot_fall_back_to_network_offline(self):
        path, expected = make_chunk(self.path)
        cache = self.path / 'cache'
        cache.mkdir()
        (cache / path.name).write_bytes(b'PKcorrupt')
        with patch.object(pack, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
            found = pack.request_chunk(expected, {}, cache, 1, 1, self.path)
            self.assertEqual(found.read_bytes(), path.read_bytes())
            path.unlink()
            found.unlink()
            with self.assertRaises(pack.PackError):
                pack.request_chunk(expected, {}, cache, 1, 1, self.path)
        net.assert_not_called()

    def test_offline_cli_propagates_output_and_offline_to_terrain(self):
        path, expected = make_chunk(self.path)
        manifest = self.path / 'manifest.json'
        manifest.write_text(json.dumps({'chunks': [expected]}))
        vectors = self.path / 'vectors.json'
        vectors.write_text(json.dumps({'tiles': [vector_row(), vector_row(True, 2)]}))
        output = self.path / 'new-target'
        args = ['install_local_pack_v041.py', '--manifest', str(manifest),
                '--vector-manifest', str(vectors), '--output', str(output),
                '--chunk-dir', str(self.path), '--offline']
        with patch.object(sys, 'argv', args), contextlib.redirect_stdout(io.StringIO()), \
             patch.object(pack, 'copy_bundled_terrain', return_value=[]), \
             patch.object(pack.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as child, \
             patch.object(pack, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
            self.assertEqual(pack.main(), 0)
        cmd = child.call_args.args[0]
        self.assertEqual(cmd[cmd.index('--output') + 1], str(output / 'terrain'))
        self.assertIn('--offline', cmd)
        net.assert_not_called()


class TerrainTests(TemporaryTest):
    def setUp(self):
        super().setUp()
        self.region, self.manifest, self.data = terrain_fixture()

    def test_grid_has_north_to_south_order_and_exact_corners(self):
        points = terrain.grid_coordinates(self.region, self.manifest)
        self.assertEqual(points, [(43.01, 5.0), (43.01, 5.01),
                                  (43.0, 5.0), (43.0, 5.01)])

    def test_nodata_remains_missing_and_non_numeric_values_are_not_altitudes(self):
        for value in (None, True, False, '123', -100, 9000, float('nan'),
                      float('inf'), -99.9999, 8999.9999):
            with self.subTest(value=value):
                self.assertIsNone(terrain.sanitise(value))
        self.assertEqual(terrain.sanitise(110.52), 110.52)
        clean, meta = terrain.validate_bytes(json.dumps(self.data).encode(), self.region, self.manifest)
        self.assertEqual(json.loads(clean)['values'], [110.52, None, 115.0, None])
        self.assertEqual((meta['valid'], meta['missing']), (2, 2))

    def test_terrain_requires_real_resource_bbox_shape_and_order(self):
        for change in ({'sourceResource': 'other'}, {'macro': 'other'},
                       {'width': 2.0}, {'rowOrder': 'south-to-north'},
                       {'bbox': [43, 5, 44, 6]}, {'values': [None] * 4}):
            with self.subTest(change=change):
                with self.assertRaises(terrain.TerrainError):
                    terrain.validate_bytes(json.dumps({**self.data, **change}).encode(), self.region, self.manifest)

    def test_official_batch_checks_count_coordinates_order_and_altitude_type(self):
        points = terrain.grid_coordinates(self.region, self.manifest)[:2]
        valid = [{'lat': p[0], 'lon': p[1], 'z': 110.52} for p in points]
        cases = [[], list(reversed(valid)), [{**valid[0], 'lat': 0}, valid[1]],
                 [{**valid[0], 'z': True}, valid[1]], [{**valid[0], 'z': '110'}, valid[1]],
                 [{'lat': points[0][0], 'lon': points[0][1]}, valid[1]]]
        for rows in cases:
            with self.subTest(rows=rows):
                with self.assertRaises(terrain.TerrainError):
                    terrain.decode_official_batch(json.dumps({'elevations': rows}).encode(), points, self.manifest)

    def test_official_batch_size_never_exceeds_5000(self):
        for size in (0, 5001):
            with self.subTest(size=size):
                with patch.object(terrain, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
                    with self.assertRaises(terrain.TerrainError):
                        terrain.fetch_official_region(self.region, self.manifest, self.path, 1, 1, size)
                net.assert_not_called()

    def test_official_post_batches_preserve_nodata_and_provenance(self):
        requests = []
        def fake(request, timeout):
            requests.append(request)
            self.assertEqual(request.get_method(), 'POST')
            self.assertEqual(request.full_url, terrain.OFFICIAL_API)
            payload = json.loads(request.data)
            self.assertEqual(payload['resource'], terrain.OFFICIAL_RESOURCE)
            self.assertEqual(len(payload['lat'].split('|')), 2)
            return official_response(request, [110.52, None] if len(requests) == 1 else [-99999, 120.0])
        with patch.object(terrain, 'urlopen', side_effect=fake), patch.object(terrain.OFFICIAL_RATE, 'wait'):
            result = terrain.fetch_official_region(self.region, self.manifest, self.path, 1, 1, 2)
        grid = json.loads((self.path / 'geo_unit.json').read_text())
        provenance = json.loads((self.path / 'geo_unit.proof.json').read_text())
        self.assertEqual(grid['values'], [110.52, None, None, 120.0])
        self.assertEqual((result['valid'], result['missing']), (2, 2))
        self.assertEqual(provenance['endpoint'], 'official')
        self.assertEqual(provenance['batchCount'], 2)
        self.assertEqual(provenance['sha256'], digest((self.path / 'geo_unit.json').read_bytes()))

    def _interrupted_first_batch(self):
        calls = []
        def fake(request, timeout):
            calls.append(request)
            if len(calls) == 2:
                raise OSError('interrupted second batch')
            return official_response(request)
        with patch.object(terrain, 'urlopen', side_effect=fake), patch.object(terrain.OFFICIAL_RATE, 'wait'):
            with self.assertRaises(terrain.TerrainError):
                terrain.fetch_official_region(self.region, self.manifest, self.path, 1, 1, 2)
        return calls

    def test_official_retry_reuses_only_validated_batches_and_preserves_previous_grid(self):
        dest = self.path / 'geo_unit.json'
        dest.write_bytes(b'previous incomplete grid')
        self._interrupted_first_batch()
        self.assertEqual(dest.read_bytes(), b'previous incomplete grid')
        with patch.object(terrain, 'urlopen', side_effect=lambda r, timeout: official_response(r)) as net, \
             patch.object(terrain.OFFICIAL_RATE, 'wait'):
            result = terrain.fetch_official_region(self.region, self.manifest, self.path, 1, 1, 2)
        self.assertEqual(net.call_count, 1)
        self.assertEqual(result['resumedBatches'], 1)
        self.assertEqual(json.loads(net.call_args.args[0].data)['lat'], '43.0000000000|43.0000000000')
        self.assertEqual(list((self.path / '.official_resume').iterdir()), [])

    def test_corrupt_checkpoint_is_downloaded_again(self):
        self._interrupted_first_batch()
        checkpoint = next((self.path / '.official_resume').glob('*/0000000.json'))
        checkpoint.write_bytes(b'corrupted response')
        with patch.object(terrain, 'urlopen', side_effect=lambda r, timeout: official_response(r)) as net, \
             patch.object(terrain.OFFICIAL_RATE, 'wait'):
            result = terrain.fetch_official_region(self.region, self.manifest, self.path, 1, 1, 2)
        self.assertEqual(net.call_count, 2)
        self.assertEqual(result['resumedBatches'], 0)

    def test_offline_missing_or_invalid_terrain_never_calls_relay_or_ign(self):
        dest = self.path / 'geo_unit.json'
        for original in (None, b'previous invalid terrain'):
            with self.subTest(existing=original is not None):
                if original is not None:
                    dest.write_bytes(original)
                with patch.object(terrain, 'urlopen', side_effect=AssertionError('network forbidden')) as net, \
                     patch.object(terrain, 'fetch_official_region', side_effect=AssertionError('IGN forbidden')) as fallback:
                    result = terrain.fetch_region(self.region, self.manifest, self.path, 1, 1, offline=True)
                self.assertEqual(result['status'], 'error')
                net.assert_not_called()
                fallback.assert_not_called()
                if original is not None:
                    self.assertEqual(dest.read_bytes(), original)

    def test_offline_valid_terrain_uses_local_data(self):
        clean, _ = terrain.validate_bytes(json.dumps(self.data).encode(), self.region, self.manifest)
        (self.path / 'geo_unit.json').write_bytes(clean)
        with patch.object(terrain, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
            result = terrain.fetch_region(self.region, self.manifest, self.path, 1, 1, offline=True)
        self.assertEqual(result['status'], 'cached')
        self.assertEqual((self.path / 'geo_unit.json').read_bytes(), clean)
        net.assert_not_called()

    def test_failed_relay_uses_official_post_fallback(self):
        urls = []
        def fake(request, timeout):
            urls.append(request.full_url)
            if request.full_url != terrain.OFFICIAL_API:
                raise OSError('historical relay unavailable')
            return official_response(request)
        with patch.object(terrain, 'urlopen', side_effect=fake), patch.object(terrain.OFFICIAL_RATE, 'wait'):
            result = terrain.fetch_region(self.region, self.manifest, self.path, 1, 1)
        self.assertEqual(result['status'], 'downloaded')
        self.assertEqual(result['endpoint'], 'official')
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[1], terrain.OFFICIAL_API)
        self.assertEqual(json.loads((self.path / 'geo_unit.proof.json').read_text())['fallbackFrom'], 'configured historical relay')

    def test_explicitly_disabled_official_fallback_does_not_call_ign(self):
        with patch.object(terrain, 'urlopen', side_effect=OSError('relay unavailable')), \
             patch.object(terrain, 'fetch_official_region', side_effect=AssertionError('IGN forbidden')) as fallback:
            result = terrain.fetch_region(self.region, self.manifest, self.path, 1, 1, official_fallback=False)
        self.assertEqual(result['status'], 'error')
        fallback.assert_not_called()

    def test_bundled_terrain_is_copied_into_output_after_validation(self):
        bundle = self.path / 'bundle'
        bundle.mkdir()
        clean, meta = terrain.validate_bytes(json.dumps(self.data).encode(), self.region, self.manifest)
        (bundle / 'geo_unit.json').write_bytes(clean)
        (bundle / 'geo_unit.proof.json').write_text(json.dumps({**meta, 'endpoint': 'official'}))
        manifest = bundle / 'manifest.json'
        manifest.write_text(json.dumps(self.manifest))
        output = self.path / 'new-output'
        with patch.object(terrain, 'DEFAULT_OUTPUT', bundle), patch.object(terrain, 'DEFAULT_MANIFEST', manifest), \
             patch.object(terrain, 'urlopen', side_effect=AssertionError('network forbidden')) as net:
            self.assertEqual(pack.copy_bundled_terrain(output), ['geo_unit'])
        self.assertEqual((output / 'geo_unit.json').read_bytes(), clean)
        self.assertEqual(json.loads((output / 'geo_unit.proof.json').read_text())['endpoint'], 'official')
        net.assert_not_called()

    def test_bundled_terrain_with_wrong_proof_digest_is_not_installed(self):
        bundle = self.path / 'bundle'
        bundle.mkdir()
        clean, _ = terrain.validate_bytes(json.dumps(self.data).encode(), self.region, self.manifest)
        (bundle / 'geo_unit.json').write_bytes(clean)
        (bundle / 'geo_unit.proof.json').write_text(json.dumps({'sha256': '0' * 64}))
        manifest = bundle / 'manifest.json'
        manifest.write_text(json.dumps(self.manifest))
        output = self.path / 'new-output'
        with patch.object(terrain, 'DEFAULT_OUTPUT', bundle), patch.object(terrain, 'DEFAULT_MANIFEST', manifest):
            with self.assertRaises(pack.PackError):
                pack.copy_bundled_terrain(output)
        self.assertFalse((output / 'geo_unit.json').exists())


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []

    def startTest(self, test):
        self.started_at = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        failed = any(case is test or getattr(case, 'test_case', None) is test
                     for case, _ in self.failures + self.errors)
        self.cases.append({'test': test.id(), 'passed': not failed,
                           'seconds': round(time.perf_counter() - self.started_at, 4)})
        super().stopTest(test)


def offline_integration(compressed_transport=False):
    """Run the real CLI into a virgin directory with network audit guards."""
    started = time.perf_counter()
    bundle = json.loads(pack.BUNDLED_MANIFEST.read_text())
    vectors = json.loads(pack.VECTOR_MANIFEST.read_text())
    tm = json.loads(terrain.DEFAULT_MANIFEST.read_text())
    with tempfile.TemporaryDirectory(prefix='mistral-v050-offline-') as tmp:
        tmp = Path(tmp)
        output = tmp / 'virgin-pack'
        install_root = ROOT
        transports = []
        report_name = 'INSTALL_OFFLINE_GZIP' if compressed_transport else 'INSTALL_OFFLINE'
        if compressed_transport:
            # Reproduce the GitHub bundle, including its tools and terrain,
            # without allowing the installer to see the original large ZIP.
            install_root = tmp / 'bundled-clone'
            clone_pack = install_root / 'data/map_pack'
            clone_archives = clone_pack / 'archives'
            clone_terrain = clone_pack / 'terrain'
            for directory in (install_root / 'tools', clone_archives, clone_terrain):
                directory.mkdir(parents=True, exist_ok=True)
            for name in ('install_local_pack_v041.py', 'install_real_map_v038.py',
                         'install_terrain_v039.py', 'mvt_audit_v036.py'):
                shutil.copy2(ROOT / 'tools' / name, install_root / 'tools' / name)
            shutil.copy2(pack.BUNDLED_MANIFEST, clone_archives / 'manifest.json')
            shutil.copy2(pack.VECTOR_MANIFEST, clone_pack / 'manifest_v038.json')
            shutil.copy2(terrain.DEFAULT_MANIFEST, clone_terrain / 'manifest_v039.json')
            for region in tm['regions']:
                for suffix in ('.json', '.proof.json'):
                    name = region['macro'] + suffix
                    shutil.copy2(terrain.DEFAULT_OUTPUT / name, clone_terrain / name)
            for chunk in bundle['chunks']:
                name = chunk['name']
                if name == 'base_00060_100.zip':
                    compressed = pack.BUNDLED_CHUNKS / (name + '.gz')
                    shutil.copy2(compressed, clone_archives / compressed.name)
                    assert not (clone_archives / name).exists()
                    transports.append({'suppliedPath': 'data/map_pack/archives/' + compressed.name,
                                       'compressedBytes': compressed.stat().st_size,
                                       'compressedSha256': digest(compressed.read_bytes()),
                                       'originalZipAbsentFromClone': True,
                                       'decodedBytesLimit': chunk['archiveBytes'],
                                       'expectedOriginalZipSha256': chunk['sha256']})
                else:
                    shutil.copy2(pack.BUNDLED_CHUNKS / name, clone_archives / name)
            assert len(transports) == 1
        guards = tmp / 'guard'
        guards.mkdir()
        log = tmp / 'network-audit.jsonl'
        (guards / 'sitecustomize.py').write_text('''import json, os, sys
_log = os.environ['MISTRAL_OFFLINE_NETWORK_LOG']
def _record(event):
    with open(_log, 'a', encoding='utf-8') as out:
        out.write(json.dumps({'event': event, 'pid': os.getpid()}) + '\\n')
def _audit(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto', 'socket.sendmsg'):
        _record(event)
        raise RuntimeError('Network forbidden during offline installation')
sys.addaudithook(_audit)
_record('guard-installed')
''', encoding='utf-8')
        env = {**os.environ, 'PYTHONPATH': str(guards), 'MISTRAL_OFFLINE_NETWORK_LOG': str(log)}
        # Prove that the guard actually rejects network access before relying on
        # an empty installation network log. The guard fails before socket I/O.
        probe = subprocess.run([sys.executable, '-c', "import socket; socket.create_connection(('127.0.0.1', 9))"],
                               env=env, capture_output=True, text=True)
        probe_events = [json.loads(line) for line in log.read_text().splitlines()]
        assert probe.returncode != 0 and any(e['event'].startswith('socket.') for e in probe_events)
        log.write_text('')
        command = [sys.executable, str(install_root / 'tools/install_local_pack_v041.py'),
                   '--offline', '--output', str(output), '--workers', '3']
        assert not output.exists()
        run = subprocess.run(command, cwd=install_root, env=env, capture_output=True, text=True, timeout=240)
        (REPORTS / (report_name + '.log')).write_text(run.stdout + '\n' + run.stderr, encoding='utf-8')
        events = [json.loads(line) for line in log.read_text().splitlines()]
        network = [e for e in events if e['event'].startswith('socket.')]
        guarded = {e['pid'] for e in events if e['event'] == 'guard-installed'}
        assert run.returncode == 0, run.stdout[-5000:] + run.stderr[-5000:]
        assert len(guarded) >= 2, 'Both the ZIP and terrain subprocesses must have a network guard'
        assert not network, network
        if compressed_transport:
            assert not (install_root / 'data/map_pack/archives/base_00060_100.zip').exists()
        state = audit(output)
        assert state['complete'], state
        installed = json.loads((output / 'local_pack_v041_status.json').read_text())
        assert installed['complete'] and installed['chunksInstalled'] == len(bundle['chunks'])
        assert installed['terrain']['ok']
        files = []
        coordinates = set()
        proofs = 0
        for chunk in bundle['chunks']:
            path = pack.BUNDLED_CHUNKS / chunk['name']
            # A fresh GitHub checkout legitimately has only the gzip transport
            # for the largest ZIP, including when this test is run there.
            expected_archive = (path.read_bytes() if path.is_file() else
                                pack.read_gzip_chunk(path.with_name(path.name + '.gz'), chunk))
            assert digest(expected_archive) == chunk['sha256']
            with zipfile.ZipFile(io.BytesIO(expected_archive)) as archive:
                rows = json.loads(archive.read('chunk_manifest.json'))['files']
                for row in rows:
                    assert row['path'] not in coordinates
                    coordinates.add(row['path'])
                    raw = (output / row['path']).read_bytes()
                    assert digest(raw) == row['sha256'] and len(raw) == row['bytes']
                    files.append({'path': row['path'], 'bytes': len(raw), 'sha256': digest(raw)})
                    if row['empty']:
                        name = row['path'] + '.empty.json'
                        marker = (output / name).read_bytes()
                        assert marker == archive.read(name), name
                        pack.check_empty_proof(marker, pack.coordinate(row['path'], chunk['source']))
                        proofs += 1
        assert coordinates == {r['local'].removeprefix('data/map_pack/') for r in vectors['tiles']}
        terrain_files = []
        for region in tm['regions']:
            relative = 'terrain/' + region['macro'] + '.json'
            raw = (output / relative).read_bytes()
            source = (terrain.DEFAULT_OUTPUT / (region['macro'] + '.json')).read_bytes()
            assert raw == source, relative + ' changed during copying'
            _, meta = terrain.validate_bytes(raw, region, tm)
            copied_proof = json.loads((output / 'terrain' / (region['macro'] + '.proof.json')).read_text())
            assert copied_proof['sha256'] == digest(raw)
            terrain_files.append({'path': relative, 'sha256': digest(raw), 'bytes': len(raw),
                                  'valid': meta['valid'], 'noData': meta['missing']})
        assert not (output / '.chunks_v041').exists(), 'Temporary archive cache was not removed'
        report = {'version': '0.50.0', 'passed': True,
                  'generatedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                  'scope': ('Fresh output from an isolated bundle clone; largest original ZIP absent, supplied only as gzip; '
                            'original ZIP byte count/SHA-256 enforced; actual vectors and IGN grids compared; subprocess network requests blocked and audited.'
                            if compressed_transport else
                            'Fresh output; actual bundled ZIPs and IGN grids; subprocess network requests blocked and audited.'),
                  'command': 'python3 tools/install_local_pack_v041.py --offline --output <empty-directory> --workers 3',
                  'archives': len(bundle['chunks']), 'archiveBytes': sum(c['archiveBytes'] for c in bundle['chunks']),
                  'coordinatesComparedBySha256': len(files), 'emptyProofsComparedByteForByte': proofs,
                  'terrainComparedByteForByte': terrain_files,
                  'networkGuardSelfTestPassed': True, 'guardedPythonProcesses': len(guarded),
                  'networkAttempts': len(network), 'installerExitCode': run.returncode,
                  'independentAudit': state,
                  'installedVectorInventorySha256': digest(json.dumps(sorted(files, key=lambda x: x['path']),
                                                                      sort_keys=True, separators=(',', ':')).encode()),
                  'temporaryArchiveCacheRemoved': True,
                  'seconds': round(time.perf_counter() - started, 3)}
        if compressed_transport:
            report['isolatedBundleClone'] = True
            report['gzipTransport'] = transports
        (REPORTS / (report_name + '.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: report[k] for k in ('passed', 'archives', 'coordinatesComparedBySha256',
                                                'emptyProofsComparedByteForByte', 'networkAttempts', 'seconds')}, indent=2))
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline-integration', action='store_true')
    parser.add_argument('--compressed-integration', action='store_true',
                        help='Install from an isolated bundle clone containing the largest archive only as .zip.gz')
    args = parser.parse_args()
    REPORTS.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    report = {'version': '0.50.0',
              'generatedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'scope': 'Synthetic unit fixtures for archive integrity, bounded HTTP/gzip decoding, exact coordinate responses, offline mode, resumable IGN fallback and preservation on failure.',
              'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'passed': result.wasSuccessful(), 'cases': result.cases}
    (REPORTS / 'QA_INSTALLERS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not result.wasSuccessful():
        return 1
    if args.offline_integration:
        offline_integration()
    if args.compressed_integration:
        offline_integration(compressed_transport=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
