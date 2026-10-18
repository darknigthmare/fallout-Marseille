#!/usr/bin/env python3
"""Loopback-only game server with read-only inspection of the installed map pack."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Lock
import argparse, json, time, webbrowser
from validate_real_map_v046 import audit
ROOT = Path(__file__).resolve().parents[1]
class GameHandler(SimpleHTTPRequestHandler):
    _audit_lock = Lock()
    _audit_cache = None
    _audit_time = 0.0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_GET(self):
        if self.path.split('?', 1)[0] != '/__mistral/local-data':
            return super().do_GET()
        try:
            with type(self)._audit_lock:
                if type(self)._audit_cache is None or time.monotonic() - type(self)._audit_time > 30:
                    data = audit(ROOT / 'data/map_pack')
                    data.update(version='0.49.0', inspectedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), scope='Fichiers effectivement présents sur le disque du serveur local. Aucun téléchargement.')
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
    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Le port doit être compris entre 1 et 65535.')
    url = f'http://127.0.0.1:{args.port}/index.html'
    print('Application locale v0.49 :', url, flush=True)
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
