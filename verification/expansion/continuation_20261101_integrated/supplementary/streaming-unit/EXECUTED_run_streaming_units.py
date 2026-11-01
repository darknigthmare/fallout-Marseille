"""Run three maintained standalone source regressions without inventing test totals.

These are real Node child process executions of controlled source fixtures.
They do not share a machine-readable assertion count and are not browser runs.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

ROOT = Path('/workspace/fallout-Marseille')
BASE = Path('/workspace/.cloud-setup/fallout-marseille/integrated-release')
OUT = BASE/'streaming-unit'
HTML = 'c0f13de317f1678cd20a2ed9ea3f2ee687054eb67f3815026357707828ff77b1'
SCRIPTS = ['tests/expansion/city_wait_cancel.test.cjs',
           'tests/expansion/city_partition_seams.test.cjs',
           'tests/expansion/city_geometry_identity.test.cjs']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT/'STREAMING_UNIT_PROCESSES.json'
    assert not report_path.exists()
    freeze_bytes = (BASE/'FROZEN_RUNTIME.json').read_bytes()
    frozen = json.loads(freeze_bytes)
    assert len(frozen) == 363 and sha(ROOT/'index.html') == HTML == frozen['index.html']
    assert all((ROOT/name).is_file() and sha(ROOT/name) == expected for name, expected in frozen.items())
    inputs = SCRIPTS + ['src/v050/04a_city_sources.js', 'src/v050/04_source_geometry.js',
                       'src/v046/00_integrity.js', 'src/v047/00_stream_primitives.js',
                       '.github/workflows/city-streaming-regression.yml', 'AGENTS.md']
    hashes = {name: sha(ROOT/name) for name in inputs}
    report = {'scope': __doc__, 'stage': 'running', 'html_sha256': HTML,
              'sourceHashes': hashes, 'runnerSha256': sha(Path(__file__)),
              'frozenRuntimeInputCount': len(frozen),
              'frozenRuntimeSha256': hashlib.sha256(freeze_bytes).hexdigest(),
              'assertionCount': None,
              'countingNote': 'Only process exits are summarized. Standalone script outputs are retained exactly; no assertion count is invented or merged into the main model total.',
              'processes': []}

    def save():
        report['processCount'] = len(report['processes'])
        report['passedProcesses'] = sum(row['exitCode'] == 0 for row in report['processes'])
        report['failedProcesses'] = sum(row['exitCode'] != 0 for row in report['processes'])
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    save()
    for name in SCRIPTS:
        script = ROOT/name
        archive = OUT/('EXECUTED_'+script.name)
        shutil.copy2(script, archive)
        assert sha(archive) == hashes[name] == sha(script)
        command = ['node', name]
        started = time.time()
        child = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        log = OUT/(script.name+'.log')
        log.write_text(child.stdout+'\n'+child.stderr)
        row = {'script': name, 'argv': command, 'cwd': str(ROOT),
               'startedAtEpoch': started, 'durationSeconds': round(time.time()-started, 3),
               'exitCode': child.returncode, 'scriptSha256Before': hashes[name],
               'scriptSha256After': sha(script), 'executedScript': archive.name,
               'executedScriptSha256': sha(archive), 'log': log.name, 'logSha256': sha(log),
               'logFormat': 'Captured stdout followed by a newline followed by captured stderr.',
               'citySourceSha256': hashes['src/v050/04a_city_sources.js']}
        report['processes'].append(row)
        save()
        print(('PASS ' if child.returncode == 0 else 'FAIL ')+name+' exit='+str(child.returncode), flush=True)
    changed = [name for name, expected in hashes.items() if not (ROOT/name).is_file() or sha(ROOT/name) != expected]
    runtime_changed = [name for name, expected in frozen.items() if not (ROOT/name).is_file() or sha(ROOT/name) != expected]
    report.update(changedInputs=changed, runtimeChanged=runtime_changed,
                  freezeManifestUnchanged=(BASE/'FROZEN_RUNTIME.json').read_bytes() == freeze_bytes)
    report['stage'] = 'complete' if not report['failedProcesses'] and not changed and not runtime_changed and report['freezeManifestUnchanged'] else 'failed'
    save()
    print(json.dumps({key: report[key] for key in ('stage', 'html_sha256', 'processCount', 'passedProcesses', 'failedProcesses', 'assertionCount', 'changedInputs', 'runtimeChanged')}, ensure_ascii=False), flush=True)
    return int(report['stage'] != 'complete')


if __name__ == '__main__':
    raise SystemExit(main())
