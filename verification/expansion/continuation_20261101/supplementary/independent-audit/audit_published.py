"""Independent read-only audit of the published November evidence bundle."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import datetime
import hashlib
import json
import re
import struct
import subprocess

ROOT = Path('/workspace/fallout-Marseille')
BASE = Path('/workspace/.cloud-setup/fallout-marseille/continuation-next')
BUNDLE = ROOT / 'verification/expansion/continuation_20261101'
OUT = BASE / 'independent-audit/PUBLISHED_BUNDLE_AUDIT.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def field(value, key):
    if isinstance(key, str) and key in value:
        return value[key]
    for part in key if isinstance(key, list) else key.split('.'):
        value = value[part]
    return value


def inside(name):
    p = Path(name)
    assert not p.is_absolute() and '..' not in p.parts, name
    resolved = (BUNDLE / p).resolve()
    assert resolved.is_relative_to(BUNDLE.resolve()), name
    return resolved


def main():
    assert BUNDLE.is_dir()
    assert not any(p.is_symlink() for p in BUNDLE.rglob('*'))
    manifest = read(BUNDLE / 'MANIFEST.json')['files']
    names = [row['file'] for row in manifest]
    assert len(names) == len(set(names))
    actual = {str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob('*') if p.is_file()}
    assert actual == set(names) | {'MANIFEST.json'}, (actual - set(names), set(names) - actual)
    for row in manifest:
        p = inside(row['file'])
        assert p.is_file() and p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], row['file']
    disallowed = [name for name in names if Path(name).suffix.lower() in {'.tif', '.tiff', '.f32', '.zip', '.pbf', '.html'}]
    assert not disallowed, disallowed

    aggregate = read(BUNDLE / 'CONTINUATION_INTEGRATION.json')
    config = read(BUNDLE / 'METHODS_CONFIG.json')
    qa = read(BUNDLE / 'QA_ONLY_ADAPTATIONS.json')
    native_inputs = read(BUNDLE / 'NATIVE_VALIDATION_INPUTS.json')
    frozen = aggregate['productionHashes']
    html = sha(ROOT / 'index.html')
    assert html == aggregate['html_sha256'] == config['html_sha256'] == qa['html_sha256']
    assert html == '98a78a1cd1ca8748d12f206ec5f5fe3562706b00057b84628343f22d36560241'
    assert len(native_inputs) == len(frozen) == aggregate['productionInputCount'] == 361
    assert set(native_inputs) == set(frozen)
    assert [n for n in frozen if frozen[n] != native_inputs[n]] == ['tools/check_v050.py']
    assert all(sha(ROOT / n) == h for n, h in frozen.items())
    assert len(qa['changes']) == 1 and qa['changes'][0]['path'] == 'tools/check_v050.py'
    change = qa['changes'][0]
    before = BUNDLE / 'supplementary/qa-cache-adaptation/check_v050_before.py'
    after = BUNDLE / 'supplementary/qa-cache-adaptation/check_v050_after.py'
    assert sha(before) == change['beforeSha256'] == native_inputs['tools/check_v050.py']
    assert sha(after) == change['afterSha256'] == frozen['tools/check_v050.py']
    assert before.read_bytes().count(b'fallout-mistral-v050-12') == 1
    assert before.read_bytes().replace(b'fallout-mistral-v050-12', b'fallout-mistral-v050-13', 1) == after.read_bytes()

    methods = aggregate['methods']
    expected_ids = {'models', 'rebuild', 'closure', 'legacy', 'fps', 'feedback', 'hud', 'controller', 'landmarks', 'interiors', 'lore', 'vending', 'north'}
    assert len(methods) == len(expected_ids) and {m['id'] for m in methods} == expected_ids
    assert aggregate['passed'] == sum(m['passed'] for m in methods) == 3310 and aggregate['failed'] == 0
    by_id = {m['id']: m for m in methods}
    for m in methods:
        assert sha(inside(m['report'])) == m['reportSha256'], m['id']

    models = read(inside(by_id['models']['report']))
    assert len(models['suites']) == 41 and models['total'] == sum(r['total'] for r in models['suites']) == 1763
    assert models['failedProcesses'] == models['skipped'] == 0 and not models['changedInputs']
    for row in models['suites']:
        assert row['exitCode'] == row['skipped'] == 0 and row['total'] > 0
        log = inside('models/' + row['log'])
        assert sha(log) == row['logSha256']
        matches = re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|^# tests (\d+)|"passed"\s*:\s*(\d+)', log.read_text(), re.M)
        assert len(matches) == 1 and int(next(v for v in matches[0] if v)) == row['total']
    assert models['phases'][0]['suiteCount'] + models['phases'][1]['suiteCount'] == 41
    assert models['phases'][0]['originalOuterExitCode'] is None
    for name, h in models['testScriptHashes'].items():
        assert sha(ROOT / name) == h

    closure = read(inside(by_id['closure']['report']))
    assert closure['passed'] == 3 and closure['failed'] == closure['exitCode'] == 0 and closure['stage'] == 'complete'
    rebuild = read(inside(by_id['rebuild']['report']))
    assert rebuild['exitCode'] == 0 and len(rebuild['files']) == 3 and all(r['same'] and r['sourceSha256'] == r['rebuiltSha256'] == sha(ROOT / r['path']) for r in rebuild['files'])
    legacy = read(inside(by_id['legacy']['report']))
    assert legacy['passed'] == legacy['total'] == 434 and legacy['failed'] == 0 and len(legacy['processes']) == 15
    assert all(r['exitCode'] == 0 for r in legacy['processes']) and legacy['allHtmlMatch'] and not legacy['javascriptErrors']

    capture_rows = []
    native_rows = []
    assert len(config['native_methods']) == 9
    for row in config['native_methods']:
        method = by_id[row['id']]
        report_path = inside(method['report'])
        report = read(report_path)
        folder = report_path.parent
        receipt = read(folder / Path(row['receipt']).name)
        log = folder / Path(row['log']).name
        assert field(receipt, row['exit_key']) == 0
        assert field(receipt, row['receipt_report_hash_key']) == sha(report_path)
        assert field(receipt, row['receipt_log_hash_key']) == sha(log)
        script_sha = field(receipt, row['receipt_script_hash_key'])
        assert any(sha(p) == script_sha for p in folder.glob('*.py'))
        assert report['passed'] == method['passed'] == len(report['checks']) and report['failed'] == 0
        assert all(c['ok'] is True for c in report['checks'])
        assert re.findall(r'^OK (.*)$', log.read_text(), re.M) == [c['name'] for c in report['checks']]
        assert (report.get('html_sha256') or report.get('pinned_inputs', {}).get('index.html')) == html
        for shot in report.get('shots', []):
            image_path = inside(row['id'] + '/' + shot['file'])
            data = image_path.read_bytes()
            assert data.startswith(b'\x89PNG\r\n\x1a\n') and sha(image_path) == shot['sha256']
            width, height = struct.unpack('>II', data[16:24])
            assert width > 0 and height > 0
            capture_rows.append({'method': row['id'], 'file': row['id'] + '/' + shot['file'], 'sha256': sha(image_path)})
        native_rows.append({'id': row['id'], 'passed': report['passed'], 'captureCount': len(report.get('shots', []))})
    assert capture_rows == aggregate['captures'] and aggregate['captureCount'] == len(capture_rows) == 76
    assert len({r['file'] for r in capture_rows}) == 76
    assert len([name for name in names if Path(name).suffix.lower() == '.png']) == 76

    markdown_files = set(BUNDLE.rglob('*.md'))
    modified = subprocess.check_output(['git', 'diff', '--name-only', '--', '*.md'], cwd=ROOT, text=True).splitlines()
    markdown_files.update(ROOT / name for name in modified if (ROOT / name).is_file())
    links = []
    for doc in sorted(markdown_files):
        text = re.sub(r'```.*?```', '', doc.read_text(), flags=re.S)
        text = re.sub(r'`[^`]*`', '', text)
        for raw in re.findall(r'\]\(([^)\n]+)\)', text):
            value = raw[1:raw.index('>')] if raw.startswith('<') and '>' in raw else raw.split()[0]
            parsed = urlsplit(value)
            if parsed.scheme or value.startswith('#'):
                continue
            value = unquote(parsed.path)
            if not value:
                continue
            p = ROOT / value.lstrip('/') if value.startswith('/') else doc.parent / value
            assert p.exists(), (str(doc.relative_to(ROOT)), raw)
            links.append({'document': str(doc.relative_to(ROOT)), 'target': raw})

    output = {'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'auditor': '/root/audit_release',
              'scope': 'Independent read-only verification, no collector invocation and no browser execution.',
              'bundle': str(BUNDLE), 'manifest_sha256': sha(BUNDLE / 'MANIFEST.json'),
              'aggregate_sha256': sha(BUNDLE / 'CONTINUATION_INTEGRATION.json'), 'manifestFilesVerified': len(names),
              'all_manifest_sizes_and_hashes_match': True, 'exact_file_set_no_symlinks': True,
              'productionInputCount': len(frozen), 'html_sha256': html, 'qaOnlyDeltaVerified': change,
              'methods': len(methods), 'passed': aggregate['passed'], 'native_methods': native_rows,
              'captureCount': len(capture_rows), 'all_capture_hashes_match': True,
              'local_markdown_links_verified': len(links), 'markdown_documents_checked': len(markdown_files),
              'new_native_assertions': 0, 'repository_edits': False}
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
