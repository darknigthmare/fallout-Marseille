from pathlib import Path
import hashlib, json, os, re, subprocess, sys

root = Path('/workspace/fallout-Marseille')
out = Path(__file__).parent
commands = [
    ('source_tools', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/expansion', '-p', '*.py']),
    ('base_installers', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/v050', '-p', 'test_installers.py']),
]
for name in ['renderer_batches.cjs', 'geography.test.cjs', 'dense_geometry.cjs', 'surfaces_physics.cjs', 'roof_solids.cjs', 'gameplay_wasteland.cjs', 'controller_model.cjs', 'source_status_model.cjs', 'city_streaming.cjs', 'facades_model.cjs', 'city_interiors.cjs', 'city_water.cjs', 'city_water_physics.cjs', 'road_classification.cjs', 'ground_road_surfaces.cjs', 'interior_document_persistence.cjs', 'architecture_sources.cjs', 'architecture_runtime.cjs']:
    commands.append((name, ['node', 'tests/expansion/' + name]))
rows = []
for name, command in commands:
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=240)
    log = result.stdout + '\n' + result.stderr
    (out / (name + '.log')).write_text(log)
    matches = re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|"passed"\s*:\s*(\d+)', log)
    counts = [int(next(value for value in group if value)) for group in matches]
    if len(counts) != 1:
        raise RuntimeError('One explicit test total required: ' + name)
    rows.append({'suite': name, 'exitCode': result.returncode, 'total': counts[0], 'log': name + '.log'})
report = {'scope': 'Pure production geometry/physics/input/model tests and validated source tools; fixtures explicitly isolated',
          'sourceHashes': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'src/v050').glob('*.js'))}, 'html_sha256': hashlib.sha256((root / 'index.html').read_bytes()).hexdigest(), 'suites': rows,
          'total': sum(row['total'] for row in rows), 'failedProcesses': sum(row['exitCode'] != 0 for row in rows)}
(out / 'UNITS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(bool(report['failedProcesses']))
