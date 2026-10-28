#!/usr/bin/env python3
"""Run the unchanged legacy checker in its isolated final copy and audit it."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import time

BASE = Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion')
GAME = BASE / 'legacy-game'
OUT = BASE / 'legacy-final'
PYTHON = Path('/workspace/.cloud-setup/fallout-marseille/venv/bin/python')
EXPECTED = '844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34'
INDEXES = [Path('/workspace/fallout-Marseille/index.html'), BASE / 'rebuild-final/index.html', GAME / 'index.html']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return {'sha256': digest(path), 'bytes': path.stat().st_size, 'mtime_ns': path.stat().st_mtime_ns} if path.is_file() else None


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tree = ast.parse((GAME / 'tools/check_v049.py').read_text())
    specs = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(n, ast.Name) and n.id == 'SPECS' for n in node.targets))
    legacy = GAME / 'verification/v050/legacy'
    legacy.mkdir(parents=True, exist_ok=True)
    report_path = GAME / 'verification/v050/QA_LEGACY.json'
    source_paths = INDEXES + [GAME / 'JOUER_FALLOUT_MISTRAL_v0.50.html', GAME / 'src/game.js', GAME / 'sw.js', GAME / 'tools/check_v050.py', GAME / 'tools/check_v049.py'] + [GAME / 'tests/v049' / name for name, _ in specs]
    sources = {str(p): record(p) for p in source_paths}
    baseline = {str(p): record(p) for p in [report_path] + list(legacy.iterdir()) if p.is_file()}
    command = [str(PYTHON), 'tools/check_v050.py', '--workers', '1']
    write('SOURCE_BEFORE.json', {'expected_html': EXPECTED, 'command': command, 'cwd': str(GAME), 'sources': sources, 'old_reports': baseline})
    if len(specs) != 15 or any(sources[str(p)]['sha256'] != EXPECTED for p in [INDEXES[0], INDEXES[2], GAME / 'JOUER_FALLOUT_MISTRAL_v0.50.html']):
        raise RuntimeError('Final input hashes or suite count do not match the assigned run')
    started = time.time_ns()
    write('RUN_STARTED.json', {'started_ns': started, 'command': command, 'cwd': str(GAME)})
    with (OUT / 'run.log').open('w', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=GAME, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            log.write(line)
            log.flush()
            print(line, end='', flush=True)
        code = process.wait()
    finished = time.time_ns()
    report = json.loads(report_path.read_text()) if report_path.is_file() else {}
    write('QA_LEGACY_RUN.json', report)
    after = {str(p): record(p) for p in source_paths}
    outputs = {str(p): record(p) for p in [report_path] + [legacy / filename for _, filename in specs] + [legacy / (name + '.log') for name, _ in specs]}
    processes = report.get('processes', [])
    checks = {
        'checker_exit_zero': code == 0,
        'actual_15_processes_exit_zero': len(processes) == 15 and [r.get('test') for r in processes] == [name for name, _ in specs] and all(r.get('exitCode') == 0 for r in processes),
        'exact_434_assertions': report.get('passed') == 434 and report.get('failed') == 0 and report.get('total') == 434,
        'final_html_matches': report.get('html_sha256') == EXPECTED and report.get('allHtmlMatch') is True,
        'no_javascript_errors': report.get('javascriptErrors') == [],
        'all_reports_and_logs_fresh': all(value is not None and value['mtime_ns'] >= started for value in outputs.values()),
        'all_input_sources_stable': all(after[key]['sha256'] == value['sha256'] for key, value in sources.items()),
        'three_indexes_stable': all(after[str(p)]['sha256'] == sources[str(p)]['sha256'] for p in INDEXES),
        '15_adaptations_audited': len(report.get('adaptations', [])) == 15,
    }
    result = {'started_ns': started, 'finished_ns': finished, 'duration_seconds': (finished - started) / 1e9, 'checker_exit_code': code, 'checks': checks, 'passed': all(checks.values()), 'sources_after': after, 'outputs': outputs, 'processes': processes}
    write('RUN_AUDIT.json', result)
    print(json.dumps({'auditPassed': result['passed'], 'checks': checks, 'checkerExitCode': code}), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
