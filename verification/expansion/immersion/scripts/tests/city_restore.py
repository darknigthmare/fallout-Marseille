#!/usr/bin/env python3
"""Restore the shipped REAL Marseille archive into an empty temporary directory.

This verifies archive restoration, every runtime byte and the production HTTP
audit, including immediate corruption detection. It does not certify rendering
or an unassisted playthrough. No remote acquisition or synthetic map is used.
"""
from pathlib import Path
import argparse
import hashlib
from http.server import ThreadingHTTPServer
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import city_sources
from package_v050 import playable_tool_names
import serve_game


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def distribution_server(target, output, report, check, index, terrain, water, html_raw):
    """Run the shipped server with only the actual playable tool list and stdlib."""
    tools = target / 'tools'
    tools.mkdir()
    names = playable_tool_names()
    for name in names:
        if Path(name).name != name or not name.endswith('.py'):
            raise ValueError('The playable Python tool list contains an unsafe member')
        shutil.copy2(ROOT / 'tools' / name, tools / name)
    (target / 'index.html').write_bytes(html_raw)
    (target / 'JOUER_FALLOUT_MISTRAL_v0.50.html').write_bytes(html_raw)
    check('The isolated distribution contains exactly the real playable Python tool set',
          sorted(path.name for path in tools.iterdir()) == sorted(names))
    check('The isolated server has no regional or enrichment archive to prepare',
          not (target / 'data/map_pack/archives').exists()
          and not (target / 'data/map_pack/enrichment_archives').exists())
    # An absolute system interpreter and -S prevent the parent virtualenv or
    # optional GIS packages from satisfying a missing distribution dependency.
    interpreter = shutil.which('python3', path='/usr/bin:/bin')
    if not interpreter:
        raise RuntimeError('A standard system python3 is required for the isolated distribution proof')
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    command = [interpreter, '-S', '-u', 'tools/serve_game.py', '--port', str(port), '--no-browser']
    environment = os.environ.copy()
    for name in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'CONDA_PREFIX'):
        environment.pop(name, None)
    environment['PYTHONNOUSERSITE'] = '1'
    log_path = output / 'CITY_RESTORE_DISTRIBUTION_SERVER.log'
    report['distribution'] = {'command': command, 'python_site_packages': False,
                              'pythonpath_injected': False, 'tools': {name: sha((tools / name).read_bytes()) for name in names},
                              'server_log': str(log_path), 'readiness_timeout_seconds': 300}
    origin = 'http://127.0.0.1:' + str(port)
    started = time.monotonic()
    with log_path.open('wb') as log:
        process = subprocess.Popen(command, cwd=target, env=environment, stdout=log, stderr=log)
        try:
            deadline = started + 300
            response_html = None
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('The isolated distribution server exited: ' + log_path.read_text(errors='replace')[-4000:])
                try:
                    with urllib.request.urlopen(origin + '/index.html', timeout=min(1, deadline-time.monotonic())) as response:
                        response_html = response.read()
                    break
                except OSError:
                    time.sleep(.1)
            check('The real standard-library server starts through normal offline preparation within 300 seconds',
                  response_html is not None, {'seconds': round(time.monotonic()-started, 3), 'log': str(log_path)})
            check('The isolated server actually preserves the restored city through its normal startup helper',
                  'Sources de Marseille fournies : preserved' in log_path.read_text(errors='replace'))
            check('The isolated production server returns the exact frozen game HTML', response_html == html_raw)
            remaining = deadline-time.monotonic()
            if remaining <= 0:
                raise TimeoutError('The isolated city audit exceeded the bounded startup deadline')
            # Poll only the cheap HTML route above. The first city audit is a
            # full inspection; one bounded request avoids queuing heavy retries.
            with urllib.request.urlopen(origin + '/__mistral/city-sources', timeout=remaining) as response:
                audit = json.load(response)
                check('The isolated production city audit is successful no-store JSON',
                      response.status == 200 and response.headers.get('Cache-Control') == 'no-store'
                      and response.headers.get('Content-Type', '').startswith('application/json'))
            report['distribution']['audit'] = audit
            check('The isolated distribution verifies the frozen official city index and complete vector totals',
                  audit['ok'] is True and audit['present'] is True
                  and audit['indexSha256'] == report['source_snapshot']['index_sha256']
                  and audit['coverage'] == index['coverage']
                  and audit['totalBuildings'] == index['coverage']['uniqueBuildings']
                  and audit['totalRoads'] == index['coverage']['uniqueRoads'])
            check('The isolated distribution verifies all 25 measured terrain partitions',
                  audit['terrain']['present'] is True
                  and audit['terrain']['coverage'] == terrain['coverage']
                  and audit['terrain']['coverage']['fineComplete'] is True
                  and audit['terrain']['coverage']['completedFinePartitions'] == 25
                  and audit['terrain']['coverage']['requestedFinePartitions'] == 25
                  and audit['terrain']['base']['sha256'] == terrain['base']['sha256']
                  and audit['terrain']['tileCount'] == len(terrain['tiles']))
            check('The isolated distribution verifies its frozen source-derived sea atlas',
                  audit['water']['present'] is True and audit['water']['tileCount'] == len(water['tiles'])
                  and audit['water']['source'] == water['source']
                  and audit['water']['derivation'] == water['derivation'])
            with urllib.request.urlopen(origin + '/data/map_pack/city/water-index.json', timeout=10) as response:
                check('The isolated HTTP water index matches the frozen acquired bytes',
                      sha(response.read()) == report['source_snapshot']['water_index_sha256'])
            report['distribution']['duration_seconds'] = round(time.monotonic()-started, 3)
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            report['distribution']['server_returncode'] = process.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-html-sha256', help='Freeze the final HTML approved for this restore proof.')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {'scope': __doc__, 'checks': [], 'synthetic_geography': False,
              'network_acquisition': False, 'stage': 'started'}

    def save():
        report.update(passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']))
        (args.output / 'CITY_RESTORE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ') + name, flush=True)
        save()
        if not ok:
            raise AssertionError(name)

    previous_root = serve_game.ROOT
    try:
        active = ROOT / 'data/map_pack/city'
        index_raw = (active / 'index.json').read_bytes()
        terrain_raw = (active / 'terrain-index.json').read_bytes()
        water_raw = (active / 'water-index.json').read_bytes()
        html_raw = (ROOT / 'index.html').read_bytes()
        index, terrain, water = json.loads(index_raw), json.loads(terrain_raw), json.loads(water_raw)
        check('Final source indices cover the complete official vector and fine-terrain acquisition',
              index['municipality']['code'] == '13055' and index['coverage']['complete'] is True
              and terrain['coverage']['complete'] is True and terrain['coverage']['fineComplete'] is True
              and terrain['coverage']['completedFinePartitions'] == terrain['coverage']['requestedFinePartitions'] == 25)
        check('The final source-derived water atlas is present and frozen', water['source']['resource'] == 'ign-city-water'
              and water['derivation']['noSimplification'] is True and len(water['tiles']) > 0)
        check('The final game HTML is identical to its standalone distribution entry',
              (ROOT / 'JOUER_FALLOUT_MISTRAL_v0.50.html').read_bytes() == html_raw)
        if args.expected_html_sha256:
            check('The final game HTML matches the explicitly frozen build SHA-256', sha(html_raw) == args.expected_html_sha256)
        report['source_snapshot'] = {'index_sha256': sha(index_raw), 'terrain_index_sha256': sha(terrain_raw),
                                     'water_index_sha256': sha(water_raw), 'html_sha256': sha(html_raw),
                                     'coverage': index['coverage'], 'terrain_coverage': terrain['coverage']}
        expected, _ = city_sources.validate_directory(active)
        expected_hashes = {name: sha(raw) for name, raw in expected.items()}
        report['files'] = len(expected_hashes)
        del expected
        receipt = json.loads((ROOT / 'data/map_pack/city_archives/manifest.json').read_bytes())
        report['archive_sha256'] = receipt['sha256']
        with tempfile.TemporaryDirectory(prefix='mistral-real-city-restore-') as temporary:
            target = Path(temporary)
            shutil.copytree(ROOT / 'data/map_pack/city_archives', target / 'data/map_pack/city_archives')
            check('A fresh destination contains no extracted municipal files', not (target / 'data/map_pack/city').exists())
            result = city_sources.prepare_if_bundled(target)
            check('The normal server preparation helper installs the actual city archive offline', result['status'] == 'installed', result)
            restored = target / 'data/map_pack/city'
            actual, _ = city_sources.validate_directory(restored)
            actual_hashes = {name: sha(raw) for name, raw in actual.items()}
            del actual
            check('Every restored runtime file is byte-identical to the acquired active atlas', actual_hashes == expected_hashes)
            check('A second launch preserves already valid imports', city_sources.prepare_if_bundled(target)['status'] == 'preserved')
            check('Preservation leaves all source bytes unchanged', all(sha((restored / name).read_bytes()) == digest for name, digest in actual_hashes.items()))

            distribution_server(target, args.output, report, check, index, terrain, water, html_raw)

            serve_game.ROOT = target

            class Handler(serve_game.GameHandler):
                _city_audit_cache = None
                _city_audit_stamp = None
                _city_audit_time = 0

                def log_message(self, *args):
                    pass

            with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
                worker = threading.Thread(target=server.serve_forever, daemon=True)
                worker.start()
                origin = 'http://127.0.0.1:' + str(server.server_port)
                try:
                    with urllib.request.urlopen(origin + '/__mistral/city-sources', timeout=300) as response:
                        audit = json.load(response)
                        check('The production HTTP route serves a real no-store JSON audit', response.status == 200 and response.headers['Cache-Control'] == 'no-store' and response.headers['Content-Type'].startswith('application/json'))
                    report['audit'] = audit
                    check('The restored administrative coverage and unique source totals match the frozen acquisition', audit['coverage'] == index['coverage'] and audit['totalBuildings'] == index['coverage']['uniqueBuildings'] and audit['totalRoads'] == index['coverage']['uniqueRoads'])
                    check('The restored terrain includes the measured base and complete retained fine tiles', audit['terrain']['present'] is True and audit['terrain']['base']['sha256'] == terrain['base']['sha256'] and audit['terrain']['tileCount'] == len(terrain['tiles']))
                    check('The restored production audit includes the exact source-derived sea atlas', audit['water']['present'] is True
                          and audit['water']['tileCount'] == len(water['tiles']) and audit['water']['source'] == water['source']
                          and audit['water']['derivation'] == water['derivation'])
                    descriptor = index['tiles'][-1]
                    with urllib.request.urlopen(origin + '/' + descriptor['path'], timeout=30) as response:
                        raw = response.read()
                        check('A content-addressed city URL serves the exact restored source bytes', len(raw) == descriptor['bytes'] and sha(raw) == descriptor['sha256'])
                    changed = target / descriptor['path']
                    original = changed.read_bytes()
                    changed.write_bytes(original + b' ')
                    try:
                        urllib.request.urlopen(origin + '/__mistral/city-sources', timeout=300)
                        check('Corruption invalidates the live audit cache immediately', False)
                    except urllib.error.HTTPError as error:
                        check('Corruption invalidates the live audit cache immediately', error.code == 503 and json.load(error)['ok'] is False)
                    try:
                        city_sources.prepare_if_bundled(target)
                        check('Startup refuses corrupt user imports instead of replacing them silently', False)
                    except (OSError, ValueError):
                        check('Startup refuses corrupt user imports instead of replacing them silently', True)
                    changed.write_bytes(original)
                finally:
                    server.shutdown()
                    worker.join(timeout=10)
        check('The original city, terrain and water indices stayed unchanged during the restore proof',
              (active / 'index.json').read_bytes() == index_raw and (active / 'terrain-index.json').read_bytes() == terrain_raw
              and (active / 'water-index.json').read_bytes() == water_raw)
        check('The final game HTML stayed unchanged during the restore proof', (ROOT / 'index.html').read_bytes() == html_raw
              and (ROOT / 'JOUER_FALLOUT_MISTRAL_v0.50.html').read_bytes() == html_raw)
        report['stage'] = 'complete'
    except Exception as error:
        report['stage'] = 'failed'
        report['exception'] = str(error)
        report['traceback'] = traceback.format_exc()
        if not report['checks'] or report['checks'][-1]['ok']:
            check_failed = {'name': 'Restore driver completed without an unexpected exception', 'ok': False, 'detail': str(error)}
            report['checks'].append(check_failed)
    finally:
        serve_game.ROOT = previous_root
        save()
    print(json.dumps({k: report[k] for k in ('stage', 'passed', 'failed')}))
    return int(report['stage'] != 'complete' or report['failed'] != 0)


if __name__ == '__main__':
    raise SystemExit(main())
