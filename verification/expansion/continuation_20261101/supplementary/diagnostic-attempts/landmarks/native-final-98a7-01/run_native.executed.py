"""Run an exact-source MNS inspection, retaining real process evidence."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import socket
import subprocess
import sys
import time
from urllib.parse import urlsplit

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--expect-html-sha', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = Path('/workspace/fallout-Marseille')
freeze = Path('/workspace/.cloud-setup/fallout-marseille/continuation-next/FROZEN_RUNTIME.json')
frozen_raw = freeze.read_bytes()
frozen = json.loads(frozen_raw)
expected = args.expect_html_sha
assert hashlib.sha256((root/'index.html').read_bytes()).hexdigest() == expected
before_changed = [p for p,h in frozen.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest() != h]
assert not before_changed, before_changed
out = args.output
out.mkdir(parents=True, exist_ok=False)
(out/'FROZEN_RUNTIME_REFERENCE.json').write_bytes(frozen_raw)
(out/'run_native.executed.py').write_bytes(Path(__file__).read_bytes())
script = root/'tests/expansion/landmark_surfaces_native.py'
raw = script.read_bytes()
(out/'landmark_surfaces_native.executed.py').write_bytes(raw)
argv = [sys.executable, str(script), '--run', '--output', str(out), '--expect-html-sha', expected]
started = time.monotonic()
receipt = {'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'argv':argv, 'cwd':str(root), 'scriptSha256':hashlib.sha256(raw).hexdigest(), 'expectHtmlSha256':expected, 'inputFreezeSha256':hashlib.sha256(frozen_raw).hexdigest(), 'frozenInputCount':len(frozen), 'frozenInputsBeforeChanged':before_changed}
with (out/'run.log').open('wb') as log:
    process = subprocess.Popen(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        log.write(line)
        log.flush()
        sys.stdout.buffer.write(line)
        sys.stdout.buffer.flush()
    code = process.wait()
receipt.update(exitCode=code, elapsedSeconds=time.monotonic()-started, scriptUnchanged=script.read_bytes()==raw)
for name in ['run.log', 'LANDMARK_SURFACES_NATIVE.json']:
    path = out/name
    if path.exists():
        receipt[name+'Sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
report_path = out/'LANDMARK_SURFACES_NATIVE.json'
if report_path.exists():
    report = json.loads(report_path.read_text())
    url = report.get('url', '')
    if url:
        try:
            sock = socket.create_connection(('127.0.0.1',urlsplit(url).port),timeout=2)
            sock.close()
            receipt['closedServerConnectionRefused'] = False
        except OSError:
            receipt['closedServerConnectionRefused'] = True
changed = [p for p,h in frozen.items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest() != h]
receipt['frozenInputsAfterChanged'] = changed
(out/'FROZEN_RUNTIME_AFTER.json').write_text(json.dumps({'scope':'Source observations outside gameplay assertion sum.', 'referenceSha256':hashlib.sha256(frozen_raw).hexdigest(), 'inputCount':len(frozen), 'changed':changed, 'passed':not changed},indent=2)+'\n')
(out/'EXECUTION_STATUS.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False),flush=True)
raise SystemExit(code if code else int(bool(changed)))
