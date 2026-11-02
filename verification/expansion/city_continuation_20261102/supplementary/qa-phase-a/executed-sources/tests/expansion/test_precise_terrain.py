#!/usr/bin/env python3
"""Real source alignment/offline installation tests; no browser or network mocks."""
from pathlib import Path
from http.server import ThreadingHTTPServer
import hashlib
import json
import struct
import sys
import tempfile
import threading
import unittest
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import precise_terrain_sources as P


class NativeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads((ROOT/'data/map_pack/precise/index.json').read_text())
        cls.proof = json.loads((ROOT/'data/map_pack/precise/ACQUISITION.json').read_text())

    def test_native_counts_and_absence_of_resampling(self):
        self.assertEqual(self.index['sourceTiles'], 12)
        self.assertEqual(self.index['coverageSquareMeters'], 12000000)
        self.assertFalse(self.proof['conversion']['resampled'])
        self.assertFalse(self.proof['conversion']['elevationReprojection'])
        self.assertEqual(self.index['validPoints']+self.index['noDataPoints'], 6005*8007)
        self.assertEqual(self.index['noDataPoints'], 0, 'The actual selected source has no NoData; do not invent a documentary hole')

    def test_every_binary_matches_declared_hash_and_point_count(self):
        for row in self.index['tiles']:
            path = ROOT/row['path']
            self.assertEqual(path.stat().st_size, row['width']*row['height']*4)
            self.assertEqual(P.digest(path), row['sha256'])
            self.assertLessEqual(row['width']*row['height'], 1048576)

    def test_native_centres_and_rows_agree_with_attributed_source_probes(self):
        rows = {Path(r['path']).name:r for r in self.index['tiles']}
        for probe in self.proof['probes']:
            row = rows[probe['chunk']]
            self.assertEqual(probe['easting'], row['origin'][0]+probe['column']*.5)
            self.assertEqual(probe['northing'], row['origin'][1]-probe['row']*.5)
            with (ROOT/row['path']).open('rb') as source:
                source.seek((probe['row']*row['width']+probe['column'])*4)
                value = struct.unpack('<f', source.read(4))[0]
            self.assertEqual(None if value == -9999 else value, probe['z'])

    def test_shared_halos_are_exactly_the_same_native_cells(self):
        import numpy as np
        by_origin = {tuple(t['origin']):t for t in self.index['tiles']}
        for t in self.index['tiles']:
            current = np.fromfile(ROOT/t['path'], dtype='<f4').reshape(t['height'], t['width'])
            right = by_origin.get((t['origin'][0]+500, t['origin'][1]))
            below = by_origin.get((t['origin'][0], t['origin'][1]-500))
            if right:
                other = np.fromfile(ROOT/right['path'], dtype='<f4').reshape(right['height'], right['width'])
                np.testing.assert_array_equal(current[:, -1], other[:, 0])
            if below:
                other = np.fromfile(ROOT/below['path'], dtype='<f4').reshape(below['height'], below['width'])
                np.testing.assert_array_equal(current[-1, :], other[0, :])

    def test_native_receipts_are_attributed_and_do_not_ship_original_geotiffs(self):
        self.assertEqual(len(self.proof['sources']), 12)
        for source in self.proof['sources']:
            self.assertTrue(source['downloadUrl'].startswith('https://data.geopf.fr/wms-r?'))
            self.assertEqual(source['header']['nativePixelSize'], [.5, .5])
            self.assertEqual(source['header']['effectiveCrs'], 'EPSG:2154')
            self.assertEqual(source['header']['verticalDatum'], 'NGF-IGN69')
            self.assertEqual(source['header']['nodata'], -9999)
            self.assertEqual(source['bytes'], 16000513)
        self.assertTrue(all(not f['path'].endswith('.tif') for a in P.manifest(ROOT)['archives'] for f in a['files']))

    def test_archives_are_bounded_and_crc_inventory_checksums_match(self):
        total = 0
        for archive in P.manifest(ROOT)['archives']:
            path = ROOT/archive['path']
            self.assertLess(path.stat().st_size, 64*1024**2)
            self.assertEqual(P.digest(path), archive['sha256'])
            total += path.stat().st_size
            with zipfile.ZipFile(path) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(set(z.namelist()), {f['path'] for f in archive['files']})
        self.assertLess(total, 192*1024**2)

    def test_real_http_serves_identical_binary_and_honest_source_audit(self):
        from serve_game import GameHandler
        class Handler(GameHandler):
            def log_message(self, *_):
                pass
        server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            origin = 'http://127.0.0.1:'+str(server.server_port)
            tile = self.index['tiles'][0]
            with urllib.request.urlopen(origin+'/'+tile['path']) as response:
                raw = response.read()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), tile['sha256'])
            with urllib.request.urlopen(origin+'/__mistral/precise-terrain') as response:
                self.assertEqual(response.headers['Cache-Control'], 'no-store')
                audit = json.load(response)
            self.assertTrue(audit['ok'])
            self.assertEqual(audit['chunks'], 48)
            self.assertEqual(audit['noDataPoints'], 0)
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)


class ArchiveBoundaryTests(unittest.TestCase):
    def make(self, root, name='data/map_pack/precise/test.f32', raw=b'1234'):
        folder=root/'data/map_pack/precision_archives';folder.mkdir(parents=True)
        archive=folder/'test.zip'
        with zipfile.ZipFile(archive,'w') as z:z.writestr(name,raw)
        row={'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        data={'schemaVersion':1,'archives':[{'path':archive.relative_to(root).as_posix(),'bytes':archive.stat().st_size,'sha256':P.digest(archive),'files':[row]}]}
        (folder/'manifest.json').write_bytes(P.canonical(data))
        return archive

    def test_offline_install_is_verified_and_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.make(root)
            self.assertEqual(P.prepare_if_bundled(root)['installed'],1)
            self.assertEqual(P.prepare_if_bundled(root)['installed'],0)
            self.assertEqual((root/'data/map_pack/precise/test.f32').read_bytes(),b'1234')

    def test_altered_existing_member_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.make(root);P.prepare_if_bundled(root)
            (root/'data/map_pack/precise/test.f32').write_bytes(b'evil')
            with self.assertRaises(ValueError):P.prepare_if_bundled(root)

    def test_altered_archive_is_refused_before_extraction(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);archive=self.make(root);archive.write_bytes(b'changed')
            with self.assertRaises(ValueError):P.prepare_if_bundled(root)
            self.assertFalse((root/'data/map_pack/precise/test.f32').exists())

    def test_path_escape_and_duplicate_members_are_refused(self):
        for name in ('data/map_pack/precise/../../escape','data/map_pack/precise/../escape','/tmp/escape'):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);self.make(root,name)
                with self.assertRaises(ValueError):P.prepare_if_bundled(root)


if __name__=='__main__':
    unittest.main(verbosity=2)
