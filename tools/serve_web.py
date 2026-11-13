#!/usr/bin/env python3
"""Local HTTP parity for the static Vercel output and its four audit rewrites."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1] / '.vercel-static'
AUDITS = {'local-data', 'world-sources', 'city-sources', 'precise-terrain'}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        route = path.split('?', 1)[0]
        if route.startswith('/__mistral/') and route.rsplit('/', 1)[-1] in AUDITS:
            path = route + '.json'
        return super().translate_path(path)

    def end_headers(self):
        if self.path.startswith('/data/'):
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Cache-Control', 'public, max-age=0, must-revalidate')
        else:
            self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=int, default=9402)
    args = p.parse_args()
    print('Static web distribution http://127.0.0.1:' + str(args.port), flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
