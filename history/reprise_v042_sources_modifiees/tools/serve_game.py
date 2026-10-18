#!/usr/bin/env python3
"""Optional loopback server for developers; no external bind and no map download."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import argparse, webbrowser
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
url=f'http://127.0.0.1:{a.port}/index.html'
print('Application locale v0.41 :',url,flush=True)
try:
 server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(SimpleHTTPRequestHandler,directory=str(root)))
 if not a.no_browser:webbrowser.open(url)
 server.serve_forever()
except KeyboardInterrupt:pass
except OSError as e:raise SystemExit(f'Impossible de démarrer le serveur : {e}')
