#!/usr/bin/env python3
"""Start the actual isolated-copy server and stop only that owned process."""
from pathlib import Path
import hashlib
import json
import socket
import subprocess
import time
import urllib.request

BASE = Path('/workspace/.cloud-setup/fallout-marseille/precision-expansion')
GAME = BASE / 'legacy-game'
OUT = BASE / 'legacy-final'
PYTHON = Path('/workspace/.cloud-setup/fallout-marseille/venv/bin/python')
EXPECTED = '120e04972fb08a6f59b929d8a0952010712cf3849b8e512c383ff3a8ae87d636'


def indexes():
    paths = [Path('/workspace/fallout-Marseille/index.html'), BASE / 'rebuild-game/index.html', GAME / 'index.html']
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main():
    before = indexes()
    started = time.time_ns()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    command = [str(PYTHON), '-u', 'tools/serve_game.py', '--port', str(port), '--no-browser']
    fetched = None
    error = None
    shutdown = None
    with (OUT / 'SERVER_PREFLIGHT.log').open('w') as log:
        process = subprocess.Popen(command, cwd=GAME, stdout=log, stderr=subprocess.STDOUT)
        (OUT / 'SERVER_PREFLIGHT_STARTED.json').write_text(json.dumps({'pid': process.pid, 'command': command, 'started_ns': started}) + '\n')
        try:
            deadline = time.monotonic() + 300
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    error = 'Owned server exited before HTTP readiness'
                    break
                try:
                    with urllib.request.urlopen('http://127.0.0.1:' + str(port) + '/index.html', timeout=3) as response:
                        raw = response.read()
                        fetched = {'status': response.status, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
                    break
                except OSError:
                    time.sleep(.1)
            if fetched is None and error is None:
                error = 'HTTP readiness timeout'
        finally:
            if process.poll() is None:
                shutdown = 'Explicit SIGTERM to this preflight-owned server after readiness check'
                process.terminate()
            code = process.wait(timeout=30)
    after = indexes()
    passed = fetched is not None and fetched['status'] == 200 and fetched['sha256'] == EXPECTED and before == after and all(v == EXPECTED for v in after.values())
    result = {'passed': passed, 'serverPid': process.pid, 'command': command, 'serverExitCode': code, 'intentionalShutdown': shutdown, 'error': error,
              'fetched': fetched, 'indexesBefore': before, 'indexesAfter': after, 'started_ns': started, 'finished_ns': time.time_ns()}
    (OUT / 'SERVER_PREFLIGHT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
