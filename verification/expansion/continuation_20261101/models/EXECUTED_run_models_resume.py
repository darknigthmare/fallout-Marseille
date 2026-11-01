"""Observe the actual continuation child exit; never infer an original outer exit."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

BASE = Path('/workspace/.cloud-setup/fallout-marseille/continuation-next')
ROOT = Path('/workspace/fallout-Marseille')
OUT = BASE/'models-final'
PYTHON = '/workspace/.cloud-setup/fallout-marseille/venv/bin/python'
EXPECTED = '98a78a1cd1ca8748d12f206ec5f5fe3562706b00057b84628343f22d36560241'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    script = BASE/'scripts/resume_models.py'
    command = [PYTHON, str(script), '--repo', str(ROOT), '--output', str(OUT), '--freeze', str(BASE/'FROZEN_RUNTIME.json'), '--expect-html-sha', EXPECTED]
    assert not (OUT/'EXECUTION_RESUME.json').exists() and not (OUT/'resume.stdout.log').exists()
    before = sha(script)
    own_before = sha(Path(__file__))
    shutil.copy2(Path(__file__), OUT/'EXECUTED_run_models_resume.py')
    started = time.time()
    receipt = {'method': 'Actual child exit for the continuation phase only; original interrupted outer exit remains unobserved.',
               'originalOuterExitCode': None, 'argv': command, 'cwd': str(ROOT), 'scriptSha256': before,
               'wrapperSha256': own_before, 'startedAtEpoch': started}
    with (OUT/'resume.stdout.log').open('w') as log:
        child = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        receipt['childPid'] = child.pid
        for line in child.stdout:
            log.write(line)
            log.flush()
            print(line, end='', flush=True)
        code = child.wait()
    frozen = json.loads((BASE/'FROZEN_RUNTIME.json').read_text())
    receipt.update(exitCode=code, durationSeconds=round(time.time()-started, 3),
                   scriptUnchanged=sha(script) == before, wrapperUnchanged=sha(Path(__file__)) == own_before,
                   reportSha256=sha(OUT/'UNITS.json'), provenanceSha256=sha(OUT/'RESUME_PROVENANCE.json') if (OUT/'RESUME_PROVENANCE.json').exists() else None,
                   logSha256=sha(OUT/'resume.stdout.log'), html_sha256=sha(ROOT/'index.html'),
                   runtimeInputCount=len(frozen), runtimeChanged=[name for name, expected in frozen.items() if not (ROOT/name).is_file() or sha(ROOT/name) != expected])
    (OUT/'EXECUTION_RESUME.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return code or int(bool(receipt['runtimeChanged']) or not receipt['scriptUnchanged'] or not receipt['wrapperUnchanged'])


if __name__ == '__main__':
    raise SystemExit(main())
