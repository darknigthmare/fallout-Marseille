#!/usr/bin/env python3
"""Run current isolated production contracts; native pilots are separate."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('/workspace/fallout-Marseille'))
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'units')
    args = parser.parse_args()
    root, out = args.repo.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    names = ['renderer_batches.cjs', 'geography.test.cjs', 'dense_geometry.cjs',
             'surfaces_physics.cjs', 'roof_solids.cjs', 'gameplay_wasteland.cjs',
             'controller_model.cjs', 'source_status_model.cjs', 'city_streaming.cjs',
             'facades_model.cjs', 'facades_coverage.cjs', 'city_interiors.cjs',
             'city_water.cjs', 'city_water_physics.cjs', 'road_classification.cjs',
             'ground_road_surfaces.cjs', 'interior_document_persistence.cjs',
             'architecture_sources.cjs', 'architecture_runtime.cjs',
             'world_placements.cjs', 'lore_continuity.cjs', 'power_armor.cjs',
             'iconic_ecosystem.cjs', 'parallel_systems.cjs', 'regional_bestiary.cjs', 'precise_terrain.cjs', 'facades_joinery.cjs', 'chems_ecosystem.cjs']
    commands = [('source_tools', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/expansion', '-p', 'test_*.py']),
                ('base_installers', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/v050', '-p', 'test_installers.py'])]
    commands.extend((name, ['node', 'tests/expansion/' + name]) for name in names)
    source_paths = sorted(set((root/'src').rglob('*.js')) | set((root/'tools').glob('*.py')) | {root/'sw.js'})
    test_paths = sorted(set((root/'tests/expansion').rglob('*.cjs')) |
                        set((root/'tests/expansion').rglob('test_*.py')) |
                        set((root/'tests/expansion/fixtures').rglob('*')) |
                        {root/'tests/v050/test_installers.py'})
    source_hashes = {str(p.relative_to(root)): sha(p) for p in source_paths if p.is_file()}
    script_hashes = {str(p.relative_to(root)): sha(p) for p in test_paths if p.is_file()}
    report = {'scope': 'Isolated current production model/tool tests, including explicit synthetic documentary, actor, storage and source fixtures; not native playthroughs.',
              'html_sha256': sha(root/'index.html'), 'runner_sha256': sha(Path(__file__)),
              'sourceHashes': source_hashes, 'testScriptHashes': script_hashes,
              'stage': 'running', 'suites': [], 'total': 0, 'failedProcesses': 0}

    def save():
        (out/'UNITS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    save()
    for name, command in commands:
        started = time.monotonic()
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=360)
            code, log = result.returncode, result.stdout + '\n' + result.stderr
        except subprocess.TimeoutExpired as error:
            code, log = 124, str(error) + '\n'
        (out/(name+'.log')).write_text(log)
        matches = re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|^# tests (\d+)|"passed"\s*:\s*(\d+)', log, re.M)
        counts = [int(next(value for value in values if value)) for values in matches]
        total = counts[0] if len(counts) == 1 else None
        row = {'suite': name, 'command': command, 'exitCode': code, 'total': total,
               'log': name+'.log', 'logSha256': sha(out/(name+'.log')),
               'elapsedSeconds': round(time.monotonic()-started, 3)}
        if total is None:
            row['error'] = 'No single explicit test total in this process output.'
        report['suites'].append(row)
        report['total'] += total or 0
        report['failedProcesses'] += int(code != 0 or total is None)
        save()
        print(('PASS ' if code == 0 and total is not None else 'FAIL ') + name + ' ' + str(total), flush=True)
    changed = [name for name, expected in {**source_hashes, **script_hashes}.items()
               if not (root/name).is_file() or sha(root/name) != expected]
    if sha(root/'index.html') != report['html_sha256']:
        changed.append('index.html')
    report['changedInputs'] = changed
    report['stage'] = 'complete' if not report['failedProcesses'] and not changed else 'failed'
    save()
    print(json.dumps({key:report[key] for key in ['stage', 'html_sha256', 'total', 'failedProcesses', 'changedInputs']}, ensure_ascii=False))
    return int(report['stage'] != 'complete')


if __name__ == '__main__':
    raise SystemExit(main())
