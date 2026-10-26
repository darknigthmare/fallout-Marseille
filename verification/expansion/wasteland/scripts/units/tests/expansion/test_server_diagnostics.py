"""Actual diagnostic HTTP routes over isolated synthetic file/audit fixtures."""
from http.server import ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import serve_game as server


class DiagnosticCacheTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.pack = self.root / 'data/map_pack'
        self.tile = self.pack / 'france-vector/16/1/2.pbf'
        self.tile.parent.mkdir(parents=True)
        self.tile.write_bytes(b'valid')
        self.terrain = self.pack / 'terrain/test.json'
        self.terrain.parent.mkdir()
        self.terrain.write_text('{"valid":true}')
        (self.pack / 'manifest_v038.json').write_text('{"fixture":true}')
        self.calls = 0
        self.mutate_during_audit = False

        class Handler(server.GameHandler):
            _audit_cache = None
            _audit_time = 0.0
            _audit_stamp = None

            def log_message(self, *args):
                pass

        self.handler_class = Handler
        self.root_patch = patch.object(server, 'ROOT', self.root)
        self.audit_patch = patch.object(server, 'audit', side_effect=self.inspect)
        self.root_patch.start()
        self.audit_patch.start()
        self.http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.worker = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.worker.start()
        self.origin = 'http://127.0.0.1:' + str(self.http.server_address[1])

    def tearDown(self):
        self.http.shutdown()
        self.worker.join(5)
        self.http.server_close()
        self.audit_patch.stop()
        self.root_patch.stop()
        self.temporary.cleanup()

    def inspect(self, pack):
        self.assertEqual(pack, self.pack)
        self.calls += 1
        raw = self.tile.read_bytes() if self.tile.is_file() else None
        valid = raw == b'valid' and json.loads(self.terrain.read_text())['valid']
        if raw == b'':
            valid = json.loads(self.tile.with_suffix('.pbf.empty.json').read_text()).get('officialEmpty') is True
        if self.mutate_during_audit:
            self.mutate_during_audit = False
            self.tile.write_bytes(b'changed during audit')
        return {'complete': valid, 'fixture': True}

    def get(self):
        with urlopen(self.origin + '/__mistral/local-data', timeout=5) as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            return json.load(response)

    def test_unchanged_files_share_the_actual_inspection_and_time(self):
        first = self.get()
        inspected = self.handler_class._audit_time
        self.assertEqual(self.get(), first)
        self.assertEqual(self.calls, 1)
        self.assertEqual(self.handler_class._audit_time, inspected)

    def test_corrupt_or_missing_tile_invalidates_a_warm_cache_immediately(self):
        self.assertTrue(self.get()['complete'])
        self.tile.write_bytes(b'broken')
        self.assertFalse(self.get()['complete'])
        self.tile.unlink()
        self.assertFalse(self.get()['complete'])
        self.assertEqual(self.calls, 3)

    def test_same_size_replacement_with_preserved_mtime_is_reinspected(self):
        self.get()
        stat = self.tile.stat()
        replacement = self.tile.with_suffix('.new')
        replacement.write_bytes(b'wrong')
        os.utime(replacement, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        os.replace(replacement, self.tile)
        self.assertFalse(self.get()['complete'])
        self.assertEqual(self.calls, 2)

    def test_empty_tile_proof_change_invalidates_a_warm_cache(self):
        self.tile.write_bytes(b'')
        marker = self.tile.with_suffix('.pbf.empty.json')
        marker.write_text('{"officialEmpty":true}')
        self.assertTrue(self.get()['complete'])
        marker.write_text('{"officialEmpty":false}')
        self.assertFalse(self.get()['complete'])
        self.assertEqual(self.calls, 2)

    def test_terrain_change_is_not_hidden_by_the_vector_cache(self):
        self.get()
        self.terrain.write_text('{"valid":false}')
        self.assertFalse(self.get()['complete'])
        self.assertEqual(self.calls, 2)

    def test_changed_inputs_during_audit_are_never_published_as_stable(self):
        self.mutate_during_audit = True
        with self.assertRaises(HTTPError) as raised:
            self.get()
        self.assertEqual(raised.exception.code, 503)
        self.assertIsNone(self.handler_class._audit_cache)
        self.assertFalse(self.get()['complete'])
        self.assertEqual(self.calls, 2)

    def test_expiry_rechecks_contents_even_when_metadata_did_not_change(self):
        self.get()
        self.handler_class._audit_time -= 31
        self.assertTrue(self.get()['complete'])
        self.assertEqual(self.calls, 2)

    def test_panel_cancellation_cannot_turn_a_valid_audit_into_a_false_503(self):
        self.get()
        for error in (BrokenPipeError, ConnectionResetError):
            with self.subTest(error=error.__name__):
                handler = object.__new__(self.handler_class)
                handler.path = '/__mistral/local-data'
                statuses = []
                handler.send_response = lambda status: statuses.append(status)
                handler.send_header = lambda *args: None
                handler.end_headers = lambda: None
                handler.send_error = lambda status, *args: statuses.append(status)

                class Disconnected(io.BytesIO):
                    def write(self, data):
                        raise error('The browser closed its diagnostic panel')

                handler.wfile = Disconnected()
                handler.do_GET()
                self.assertEqual(statuses, [200])
        self.assertEqual(self.calls, 1)


if __name__ == '__main__':
    unittest.main()
