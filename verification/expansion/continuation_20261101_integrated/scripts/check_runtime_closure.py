#!/usr/bin/env python3
"""Exercise packaged Python helpers with the standard interpreter in isolation."""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    root, out = args.repo.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    namespace = runpy.run_path(str(root / 'tools/package_v050.py'))
    names = namespace['playable_tool_names']()
    assert len(names) == len(set(names)) and 'precise_terrain_sources.py' in names
    inputs = {str(path.relative_to(root)): sha(path) for path in
              [root / 'tools/package_v050.py', root / 'index.html'] + [root / 'tools' / name for name in names]}
    code = '''
from pathlib import Path
from http.server import ThreadingHTTPServer
import functools,hashlib,json,sys,threading,urllib.request
root=Path.cwd()
sys.path.insert(0,str(root/'tools'))
import serve_game,precise_terrain_sources
assert Path(precise_terrain_sources.__file__).resolve().parent==root/'tools'
handler=serve_game.GameHandler
server=ThreadingHTTPServer(('127.0.0.1',0),handler)
worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
checks=[]
try:
    base='http://127.0.0.1:'+str(server.server_port)
    with urllib.request.urlopen(base+'/index.html',timeout=10) as response:
        raw=response.read()
        checks.append({'name':'Packaged HTTP handler serves the exact production HTML','ok':response.status==200 and hashlib.sha256(raw).hexdigest()==sys.argv[1]})
    with urllib.request.urlopen(base+'/__mistral/precise-terrain',timeout=10) as response:
        audit=json.load(response)
        checks.append({'name':'Optional terrain route works with packaged stdlib helpers and no installed source atlas','ok':response.status==200 and audit=={'ok':True,'present':False,'chunks':0}})
    checks.append({'name':'Native terrain helper is imported from the isolated distribution toolset','ok':Path(precise_terrain_sources.__file__).resolve().parent==root/'tools'})
finally:
    server.shutdown();server.server_close();worker.join(timeout=5)
print(json.dumps({'checks':checks,'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks)}))
sys.exit(int(any(not x['ok'] for x in checks)))
'''
    with tempfile.TemporaryDirectory(prefix='runtime-closure-', dir=out) as temporary:
        folder = Path(temporary)
        (folder / 'tools').mkdir()
        for name in names:
            shutil.copyfile(root / 'tools' / name, folder / 'tools' / name)
        shutil.copyfile(root / 'index.html', folder / 'index.html')
        result = subprocess.run([sys.executable, '-I', '-c', code, inputs['index.html']], cwd=folder,
                                capture_output=True, text=True, timeout=30)
    (out / 'EXECUTION.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError('Isolated packaged runtime failed: ' + result.stderr[-3000:])
    report = json.loads(result.stdout)
    report.update(scope='Real HTTP in a fresh stdlib-only distribution of the playable Python helpers. Empty optional atlas is explicit; full terrain restoration is proved separately.',
                  sourceHashes=inputs, html_sha256=inputs['index.html'], runnerSha256=sha(Path(__file__)),
                  exitCode=result.returncode, stage='complete')
    assert all(sha(root / path) == expected for path, expected in inputs.items())
    (out / 'RUNTIME_CLOSURE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['stage', 'passed', 'failed', 'total', 'exitCode']}))
    return int(report['failed'] != 0)


if __name__ == '__main__':
    raise SystemExit(main())
