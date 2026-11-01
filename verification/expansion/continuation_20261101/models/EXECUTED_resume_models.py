"""Resume only a strictly verified completed prefix from an interrupted model run.

This is a two-phase evidence composition, not a claim that the original outer
runner completed. Original report, stdout, runner and completed logs are copied
byte-for-byte before UNITS.json is changed. Native browser pilots are separate.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    temporary = path.with_name(path.name + '.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, path)


def command_list(runner):
    """Evaluate only the maintained literal command-list construction AST."""
    tree = ast.parse(runner.read_text())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    chosen = []
    for node in main.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('names', 'commands'):
            chosen.append(node)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == 'commands' and node.value.func.attr == 'extend':
            chosen.append(node)
    assert len(chosen) == 3, 'Maintained command construction is no longer recognized.'
    allowed = (ast.Module, ast.Assign, ast.Name, ast.List, ast.Tuple, ast.Constant,
               ast.Load, ast.Store, ast.Attribute, ast.Expr, ast.Call,
               ast.GeneratorExp, ast.comprehension, ast.BinOp, ast.Add)
    module = ast.Module(body=chosen, type_ignores=[])
    for node in ast.walk(module):
        assert isinstance(node, allowed), ('Unexpected command AST', type(node).__name__)
        if isinstance(node, ast.Name):
            assert node.id in ('names', 'commands', 'name', 'sys')
        if isinstance(node, ast.Attribute):
            assert isinstance(node.value, ast.Name) and (node.value.id, node.attr) in (('sys', 'executable'), ('commands', 'extend'))
        if isinstance(node, ast.Call):
            assert isinstance(node.func, ast.Attribute) and node.func.attr == 'extend' and not node.keywords
    namespace = {'__builtins__': {}, 'sys': SimpleNamespace(executable=sys.executable)}
    exec(compile(module, str(runner), 'exec'), namespace)
    commands = namespace['commands']
    assert len(commands) == 41 and len({name for name, _ in commands}) == len(commands)
    assert all(isinstance(name, str) and isinstance(command, list) and command and all(isinstance(part, str) for part in command) for name, command in commands)
    return commands


def counts(log):
    matches = re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|^# tests (\d+)|"passed"\s*:\s*(\d+)', log, re.M)
    values = [int(next(value for value in match if value)) for match in matches]
    total = values[0] if len(values) == 1 else None
    skips = re.findall(r'ℹ skipped (\d+)|^# skipped (\d+)|skipped=(\d+)', log, re.M)
    skipped = sum(int(next(value for value in match if value)) for match in skips)
    return total, skipped


def input_hashes(root):
    sources = sorted(set((root/'src').rglob('*.js')) | set((root/'tools').glob('*.py')) | {root/'sw.js'})
    tests = sorted(set((root/'tests/expansion').rglob('*.cjs')) |
                   set((root/'tests/expansion').rglob('test_*.py')) |
                   set((root/'tests/expansion/fixtures').rglob('*')) |
                   {root/'tests/v050/test_installers.py'})
    return ({str(p.relative_to(root)): sha(p) for p in sources if p.is_file()},
            {str(p.relative_to(root)): sha(p) for p in tests if p.is_file()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--freeze', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    args = parser.parse_args()
    root, out = args.repo.resolve(), args.output.resolve()
    runner = root/'tools/check_expansion.py'
    original_path = out/'UNITS.json'
    original_bytes = original_path.read_bytes()
    original = json.loads(original_bytes)
    original_stdout = (out/'stdout.log').read_bytes()
    own_hash = sha(Path(__file__))
    frozen_bytes = args.freeze.read_bytes()
    frozen = json.loads(frozen_bytes)
    assert len(frozen) == 361
    assert all((root/name).is_file() and sha(root/name) == expected for name, expected in frozen.items())
    assert sha(root/'index.html') == args.expect_html_sha == original['html_sha256'] == frozen['index.html']
    assert original['stage'] == 'running' and not original.get('changedInputs')
    assert original['failedProcesses'] == original['skipped'] == 0
    assert sha(runner) == original['runner_sha256'] == sha(out/'EXECUTED_check_expansion.py')
    sources, scripts = input_hashes(root)
    assert sources == original['sourceHashes'], 'Source file set or bytes changed.'
    assert scripts == original['testScriptHashes'], 'Test/fixture file set or bytes changed.'
    commands = command_list(runner)
    prefix = original['suites']
    assert 0 < len(prefix) < len(commands)
    assert len({row['log'] for row in prefix}) == len(prefix)
    for index, row in enumerate(prefix):
        name, command = commands[index]
        assert row['suite'] == name and row['command'] == command, 'Completed suites must be an exact maintained prefix.'
        assert row['exitCode'] == 0 and row['skipped'] == 0 and row['total'] > 0 and not row.get('error')
        assert row['log'] == name+'.log'
        log = out/row['log']
        assert log.is_file() and not log.is_symlink() and sha(log) == row['logSha256']
        assert counts(log.read_text()) == (row['total'], 0)
    assert original['total'] == sum(row['total'] for row in prefix)
    expected_stdout = ''.join('PASS '+row['suite']+' '+str(row['total'])+'\n' for row in prefix).encode()
    assert original_stdout == expected_stdout, 'Original stdout must exactly identify the completed prefix.'
    assert all(not (out/(name+'.log')).exists() for name, _ in commands[len(prefix):]), 'Unreported suite output must not be reused.'
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            argv = (path/'cmdline').read_bytes().split(b'\0')
        except (OSError, ProcessLookupError):
            continue
        assert not any(Path(os.fsdecode(part)).name == 'check_expansion.py' for part in argv if part), 'Original runner is still live.'

    archive = out/'original-interrupted'
    assert not archive.exists() and not (out/'RESUME_PROVENANCE.json').exists()
    archive.mkdir()
    original_files = [original_path, out/'stdout.log', out/'EXECUTED_check_expansion.py'] + [out/row['log'] for row in prefix]
    archive_manifest = []
    for source in original_files:
        expected = sha(source)
        destination = archive/source.name
        shutil.copy2(source, destination)
        assert expected == sha(source) == sha(destination)
        archive_manifest.append({'file': str(destination.relative_to(out)), 'bytes': destination.stat().st_size, 'sha256': expected})
    assert original_bytes == original_path.read_bytes() == (archive/'UNITS.json').read_bytes()
    assert original_stdout == (out/'stdout.log').read_bytes() == (archive/'stdout.log').read_bytes()
    (out/'FROZEN_RUNTIME_REFERENCE.json').write_bytes(frozen_bytes)
    executed = out/'EXECUTED_resume_models.py'
    shutil.copy2(Path(__file__), executed)
    assert sha(executed) == own_hash
    provenance = {'method': 'Strict exact-prefix continuation of one interrupted run, same frozen inputs; two observed execution phases.',
                  'originalOuterExitCode': None,
                  'originalOuterExitObservation': 'No original outer process exit receipt exists. Child exits are preserved from the original runner report and cross-checked against exact logs and stdout.',
                  'originalReportSha256': hashlib.sha256(original_bytes).hexdigest(),
                  'originalStdoutSha256': hashlib.sha256(original_stdout).hexdigest(),
                  'originalRunnerSha256': original['runner_sha256'],
                  'resumerSha256': own_hash, 'frozenRuntimeSha256': hashlib.sha256(frozen_bytes).hexdigest(),
                  'frozenRuntimeInputCount': len(frozen), 'html_sha256': args.expect_html_sha,
                  'verifiedPrefixSuiteCount': len(prefix), 'verifiedPrefixTotal': original['total'],
                  'remainingSuiteCount': len(commands)-len(prefix), 'maintainedCommands': commands,
                  'originalFiles': archive_manifest, 'startedAtEpoch': time.time()}
    write(out/'RESUME_PROVENANCE.json', provenance)
    report = copy.deepcopy(original)
    report.update(scope=original['scope']+' Evidence composes an archived interrupted phase (verified completed child processes only; original outer exit unobserved) and an explicitly recorded continuation phase; no completed suite is rerun or counted twice.',
                  stage='resuming', resumer_sha256=own_hash,
                  resumeProvenance='RESUME_PROVENANCE.json',
                  phases=[{'id': 'original-interrupted', 'suiteCount': len(prefix), 'total': original['total'], 'originalOuterExitCode': None, 'archive': 'original-interrupted/UNITS.json'},
                          {'id': 'continuation', 'suiteCount': 0, 'total': 0, 'receipt': 'EXECUTION_RESUME.json'}])
    write(original_path, report)
    print('RESUME verified '+str(len(prefix))+' completed suites / '+str(original['total'])+' tests; '+str(len(commands)-len(prefix))+' maintained suites remain.', flush=True)
    for name, command in commands[len(prefix):]:
        started = time.monotonic()
        try:
            process = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=360)
            code, log = process.returncode, process.stdout+'\n'+process.stderr
        except subprocess.TimeoutExpired as error:
            code, log = 124, str(error)+'\n'
        path = out/(name+'.log')
        path.write_text(log)
        total, skipped = counts(log)
        row = {'skipped': skipped, 'suite': name, 'command': command, 'exitCode': code, 'total': total,
               'log': path.name, 'logSha256': sha(path), 'elapsedSeconds': round(time.monotonic()-started, 3)}
        if total is None:
            row['error'] = 'No single explicit test total in this process output.'
        report['suites'].append(row)
        report['total'] += total or 0
        report['skipped'] += skipped
        report['failedProcesses'] += int(code != 0 or total is None or skipped != 0)
        report['phases'][1]['suiteCount'] += 1
        report['phases'][1]['total'] += total or 0
        write(original_path, report)
        print(('PASS ' if code == 0 and total is not None and skipped == 0 else 'FAIL ')+name+' '+str(total), flush=True)

    current_sources, current_scripts = input_hashes(root)
    changed = sorted(name for name, expected in {**sources, **scripts}.items() if not (root/name).is_file() or sha(root/name) != expected)
    changed += sorted(set(current_sources).symmetric_difference(sources) | set(current_scripts).symmetric_difference(scripts))
    changed += [name for name, expected in frozen.items() if not (root/name).is_file() or sha(root/name) != expected]
    if sha(Path(__file__)) != own_hash or sha(runner) != original['runner_sha256']:
        changed.append('runner/resumer')
    for row in report['suites']:
        assert sha(out/row['log']) == row['logSha256'] and counts((out/row['log']).read_text()) == (row['total'], row['skipped'])
    assert all(sha(out/row['file']) == row['sha256'] for row in archive_manifest)
    assert (out/'stdout.log').read_bytes() == original_stdout
    assert report['suites'][:len(prefix)] == original['suites']
    assert [(row['suite'], row['command']) for row in report['suites']] == commands
    assert report['total'] == sum(row['total'] or 0 for row in report['suites'])
    report['changedInputs'] = sorted(set(changed))
    report['stage'] = 'complete' if not report['failedProcesses'] and not changed else 'failed'
    write(original_path, report)
    provenance.update(finishedAtEpoch=time.time(), changedInputs=report['changedInputs'],
                      continuedSuiteCount=report['phases'][1]['suiteCount'], continuedTotal=report['phases'][1]['total'],
                      composedSuiteCount=len(report['suites']), composedTotal=report['total'],
                      composedReportSha256=sha(original_path), stage=report['stage'])
    write(out/'RESUME_PROVENANCE.json', provenance)
    print(json.dumps({key: report[key] for key in ('stage', 'html_sha256', 'total', 'failedProcesses', 'changedInputs', 'phases')}, ensure_ascii=False), flush=True)
    return int(report['stage'] != 'complete')


if __name__ == '__main__':
    raise SystemExit(main())
