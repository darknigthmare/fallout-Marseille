#!/usr/bin/env python3
"""Loopback game server; bundled files are prepared before its read-only routes open."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Lock
import argparse, json, time, webbrowser
from validate_real_map_v046 import audit
from prepare_local_pack_v050 import prepare_if_bundled
from world_source_bundle import prepare_if_bundled as prepare_world_sources, audit_details as source_audit
from city_sources import prepare_if_bundled as prepare_city_sources, audit_details as city_audit
ROOT = Path(__file__).resolve().parents[1]
class GameHandler(SimpleHTTPRequestHandler):
    _audit_lock = Lock()
    _audit_cache = None
    _audit_time = 0.0
    _city_audit_lock = Lock()
    _city_audit_cache = None
    _city_audit_time = 0.0
    _city_audit_stamp = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_GET(self):
        route = self.path.split('?', 1)[0]
        if route == '/__mistral/city-sources':
            try:
                with type(self)._city_audit_lock:
                    directory = ROOT / 'data/map_pack/city'
                    stamp = self.city_fingerprint(directory)
                    if type(self)._city_audit_cache is None or stamp != type(self)._city_audit_stamp or time.monotonic() - type(self)._city_audit_time > 30:
                        data = city_audit(directory)
                        # Preserve the actual inspection time on cache hits. A
                        # changed or replaced source file invalidates the cache
                        # immediately; concurrent panels share one heavy audit.
                        if self.city_fingerprint(directory) != stamp:
                            raise ValueError('City sources changed during inspection')
                        data.update(inspectedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), scope='Partitions communales locales vérifiées ; détails documentés et inventions architecturales distingués dans le jeu.')
                        type(self)._city_audit_cache = data
                        type(self)._city_audit_time = time.monotonic()
                        type(self)._city_audit_stamp = stamp
                    data = type(self)._city_audit_cache
                self.send_json(200, data)
            except (OSError, ValueError, KeyError):
                self.send_json(503, {'ok': False, 'error': 'Les partitions communales ne passent pas la vérification.'})
            return
        if route == '/__mistral/world-sources':
            try:
                data = source_audit(ROOT / 'data/map_pack/enrichment')
                data.update(inspectedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), scope='Fichiers locaux vérifiés ; aucun téléchargement. Espacement des échantillons distinct de la précision du relevé.')
                self.send_json(200, data)
            except (OSError, ValueError, KeyError):
                self.send_json(503, {'ok': False, 'error': 'Les sources locales ne passent pas la vérification.'})
            return
        if route != '/__mistral/local-data':
            return super().do_GET()
        try:
            with type(self)._audit_lock:
                if type(self)._audit_cache is None or time.monotonic() - type(self)._audit_time > 30:
                    data = audit(ROOT / 'data/map_pack')
                    data.update(version='0.50.0', inspectedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), scope='Fichiers effectivement présents sur le disque du serveur local. Aucun téléchargement.')
                    type(self)._audit_cache = data
                    type(self)._audit_time = time.monotonic()
                payload = json.dumps(type(self)._audit_cache, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (OSError, ValueError, KeyError) as e:
            self.send_error(503, 'Local audit unavailable')
    def send_json(self, status, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
    @staticmethod
    def city_fingerprint(directory):
        if not directory.exists():
            return ()
        rows = []
        for item in directory.iterdir():
            if item.suffix != '.json':
                continue
            if len(rows) >= 8192:
                raise ValueError('City source directory exceeds its metadata budget')
            stat = item.lstat()
            rows.append((item.name, stat.st_size, stat.st_mtime_ns, stat.st_ino, stat.st_mode))
        return tuple(sorted(rows))
    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--no-prepare', action='store_true', help='Inspecter les fichiers présents sans extraire les archives fournies.')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Le port doit être compris entre 1 et 65535.')
    if not args.no_prepare:
        prepare_if_bundled(ROOT)
        prepare_world_sources(ROOT)
        prepare_city_sources(ROOT)
    url = f'http://127.0.0.1:{args.port}/index.html'
    print('Application locale v0.50 :', url, flush=True)
    try:
        with ThreadingHTTPServer(('127.0.0.1', args.port), GameHandler) as server:
            if not args.no_browser:
                webbrowser.open(url)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError as e:
        raise SystemExit(f'Impossible de démarrer le serveur local : {e}')
if __name__ == '__main__':
    main()
