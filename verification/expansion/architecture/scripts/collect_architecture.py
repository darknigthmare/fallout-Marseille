#!/usr/bin/env python3
"""Validate and optionally publish architecture QA evidence, never run the game.

Default/check-only validates without writing. --publish is an explicit final
publication step after completed browser/legacy results have been approved.
All source inputs are rehashed before a staged directory becomes public.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import json
import os
import re
import runpy
import shutil
import tempfile
import xml.etree.ElementTree as ET

INDICES = {
    'index.json': '3a83c7f821a2f3bd824240d7f065568df7ae786b1f5719c8c57f004dbd817d61',
    'terrain-index.json': '53887ce8a6707dafee45ef9993e545f9c23b7c8d926f61696aa6117f21c359cd',
    'water-index.json': 'f46745db1df594a2ea8a4d60f5ef53ce6fa3ca82bb4e16ab686d62ef2102d927',
}
FROZEN_MODULES = {
    'src/v050/07_facades.js': '9ccc2c01a9c91d5b1c2f0611f8d18c814f2616e0ec9711b37393c2cb78ec8335',
    'src/v050/08_city_interiors.js': '94fc240ce308f71c0618ae1c1fec611b00b9867b2a91355579c3615b33cf7ce5',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_relative(value):
    require(isinstance(value, str) and value and '\\' not in value, 'Invalid relative path')
    result = Path(value)
    require(not result.is_absolute() and '..' not in result.parts, 'Unsafe relative path: ' + value)
    return result


class Collection:
    def __init__(self, root, evidence):
        self.root, self.evidence = root, evidence
        self.snapshots, self.files, self.captures = {}, {}, []

    def read(self, path):
        path = Path(path)
        require(path.is_file() and not path.is_symlink(), 'Missing/unsafe input: ' + str(path))
        raw = path.read_bytes()
        require(raw, 'Empty input: ' + str(path))
        actual = digest(raw)
        require(path not in self.snapshots or self.snapshots[path] == actual, 'Input changed: ' + str(path))
        self.snapshots[path] = actual
        return raw

    def obj(self, path):
        value = json.loads(self.read(path), parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + value)))
        require(isinstance(value, dict), 'Expected JSON object: ' + str(path))
        return value

    def add(self, source, target):
        target = str(safe_relative(target))
        raw = self.read(source)
        require(target not in self.files or self.files[target] == raw, 'Conflicting archive path: ' + target)
        self.files[target] = raw
        return raw

    def generated(self, target, value):
        require(target not in self.files, 'Repeated generated path: ' + target)
        self.files[target] = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()

    def unchanged(self):
        for path, expected in self.snapshots.items():
            require(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected, 'Input changed during collection: ' + str(path))


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, 'Invalid integer: ' + label)
    return value


def checked(report, label, expected=None):
    passed, failed = integer(report.get('passed'), label + '.passed', 1), integer(report.get('failed'), label + '.failed')
    total = integer(report.get('total', passed + failed), label + '.total', 1)
    require(failed == 0 and passed == total, label + ': failed or incomplete totals')
    require(expected is None or total == expected, label + ': unexpected total')
    for key in ('error', 'exception', 'traceback'):
        require(not report.get(key), label + ': ' + key)
    for key in ('errors', 'page_errors', 'javascriptErrors', 'javascript_console_errors', 'local_geographic_request_failures', 'local_http_errors'):
        if key in report:
            require(isinstance(report[key], list) and not report[key], label + ': nonempty ' + key)
    if 'checks' in report:
        require(isinstance(report['checks'], list) and len(report['checks']) == total, label + ': incomplete checks')
        require(all(row.get('ok') is True for row in report['checks']), label + ': failed check')
    return {'passed': passed, 'failed': 0, 'total': total}


def verify_frozen(c):
    frozen = c.obj(c.evidence / 'FROZEN_BUILD.json')
    files = frozen.get('files')
    require(isinstance(files, dict) and set(FROZEN_MODULES).issubset(files), 'Incomplete frozen build')
    for name, spec in files.items():
        raw = c.read(c.root / safe_relative(name))
        require(digest(raw) == spec['sha256'] and len(raw) == spec['bytes'], 'Frozen production changed: ' + name)
    for name, expected in FROZEN_MODULES.items():
        require(files[name]['sha256'] == expected, 'Wrong architecture freeze: ' + name)
    html = files['index.html']['sha256']
    require(files['JOUER_FALLOUT_MISTRAL_v0.50.html']['sha256'] == html, 'Two HTML outputs differ')
    for name, expected in INDICES.items():
        require(digest(c.read(c.root / 'data/map_pack/city' / name)) == expected, 'Municipal source index changed: ' + name)
    c.add(c.evidence / 'FROZEN_BUILD.json', 'FROZEN_BUILD.json')
    return frozen, html


def units(c, html):
    report = c.obj(c.evidence / 'UNITS.json')
    require(report.get('html_sha256') == html and report.get('failedProcesses') == 0, 'Units stale or failed')
    rows = report.get('suites')
    require(isinstance(rows, list) and len(rows) == 20 and len({r.get('suite') for r in rows}) == 20, 'Expected 20 unique unit suites')
    require(sum(integer(r.get('total'), 'unit suite total', 1) for r in rows) == report.get('total') == 877, 'Expected exactly 877 unit assertions')
    for relative, expected in report['sourceHashes'].items():
        require(digest(c.read(c.root / safe_relative(relative))) == expected, 'Unit production source changed: ' + relative)
    for row in rows:
        require(type(row.get('exitCode')) is int and row['exitCode'] == 0, 'Unit process failed: ' + row['suite'])
        log = c.add(c.evidence / safe_relative(row['log']), 'units/' + row['log']).decode()
        values = [int(next(x for x in group if x)) for group in re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|"passed"\s*:\s*(\d+)', log)]
        require(values == [row['total']], 'Unit log count differs: ' + row['suite'])
        require(not re.search(r'ℹ fail [1-9]|"failed"\s*:\s*[1-9]|FAILED\s*\(', log), 'Unit log reports failure: ' + row['suite'])
        if row['suite'].endswith('.cjs'):
            c.add(c.root / 'tests/expansion' / safe_relative(row['suite']), 'scripts/units/' + row['suite'])
    c.add(c.evidence / 'UNITS.json', 'UNITS.json')
    require(c.add(c.evidence / 'UNITS_RUN.log', 'units/UNITS_RUN.log') == c.read(c.evidence / 'UNITS.json'), 'Unit execution summary differs')
    c.add(c.evidence / 'verify_units.py', 'scripts/verify_units.py')
    for script in sorted((c.root / 'tests/expansion').glob('*.py')):
        c.add(script, 'scripts/units/python/' + script.name)
    c.add(c.root / 'tests/v050/test_installers.py', 'scripts/units/test_installers.py')
    for relative, expected in report.get('testScriptHashes', {}).items():
        require(digest(c.read(c.root / safe_relative(relative))) == expected, 'Executed unit script changed: ' + relative)
    return report, {'passed': 877, 'failed': 0, 'total': 877, 'suites': 20, 'method': 'Isolated production model/tool assertions, including explicitly synthetic documentary fixtures.', 'executedTestScriptHashesProvided': bool(report.get('testScriptHashes')), 'scriptIdentityLimit': None if report.get('testScriptHashes') else 'Current runner and test sources archived; original unit report pins production modules and logs but does not pin every executed test script.'}


def rebuild(c, frozen, html):
    report = c.obj(c.evidence / 'REBUILD.json')
    totals = checked(report, 'rebuild', 3)
    require(report.get('html_sha256') == html and report.get('syntaxExitCode') == 0, 'Rebuild stale or syntax failed')
    rows = report['checks']
    require({r.get('name') for r in rows} == {'index.html', 'JOUER_FALLOUT_MISTRAL_v0.50.html', 'src/game.js'}, 'Rebuild outputs incomplete')
    for row in rows:
        require(row['sha256'] == frozen['files'][row['name']]['sha256'] and row['bytes'] == frozen['files'][row['name']]['bytes'], 'Rebuild bytes differ')
    c.add(c.evidence / 'REBUILD.json', 'REBUILD.json')
    c.add(c.root / 'tools/build_single.py', 'scripts/build_single.py')
    return report, {**totals, 'method': 'Independent staging rebuild: three byte-identical outputs and JavaScript syntax check; no gameplay count.'}


def legacy(c, html):
    folder = c.evidence / 'legacy-final/verification/v050'
    report = c.obj(folder / 'QA_LEGACY.json')
    totals = checked(report, 'legacy', 434)
    require(report.get('html_sha256') == html and report.get('allHtmlMatch') is True, 'Legacy HTML stale')
    suites, processes, adaptations = (report.get(k) for k in ('suites', 'processes', 'adaptations'))
    require(all(isinstance(v, list) and len(v) == 15 for v in (suites, processes, adaptations)), 'Legacy process/adaptation lists incomplete')
    names = [{r.get('test') for r in values} for values in (suites, processes, adaptations)]
    require(all(len(n) == 15 and n == names[0] for n in names), 'Legacy suite identities differ')
    require(all(p.get('exitCode') == 0 for p in processes), 'Legacy process failure')
    require(sum(s['total'] for s in suites) == 434, 'Legacy suite sum mismatch')
    adapter_path = c.root / 'tools/check_v050.py'
    c.add(adapter_path, 'scripts/legacy/check_v050.py')
    c.add(c.root / 'tools/check_v049.py', 'scripts/legacy/check_v049.py')
    adapter = runpy.run_path(str(adapter_path))
    specifications = adapter['specifications']()
    require({row[0] for row in specifications} == names[0], 'Inherited specification differs')
    expected_adaptations = {r['test']: r for r in adaptations}
    for suite in suites:
        checked(suite, 'legacy/' + suite['test'])
        require(suite.get('sameHtml') is True, 'Legacy suite HTML mismatch')
        source = c.read(c.root / 'tests/v049' / safe_relative(suite['test']))
        executed = adapter['adapt'](suite['test'], source.decode()).encode()
        binding = expected_adaptations[suite['test']]
        require(digest(source) == binding['sourceSha256'] and digest(executed) == binding['executedSha256'], 'Legacy recreated executed bytes differ: ' + suite['test'])
        c.files['legacy/source-scripts/' + suite['test']] = source
        c.files['legacy/executed-scripts/' + suite['test']] = executed
        raw_report = c.obj(folder / 'legacy' / safe_relative(suite['file']))
        checked(raw_report, 'legacy detail/' + suite['test'], suite['total'])
        require(not raw_report.get('html_sha256') or raw_report['html_sha256'] == html, 'Legacy detailed report stale')
        c.add(folder / 'legacy' / suite['file'], 'legacy/reports/' + suite['file'])
        c.add(folder / 'legacy' / (suite['test'] + '.log'), 'legacy/logs/' + suite['test'] + '.log')
    c.add(folder / 'QA_LEGACY.json', 'legacy/QA_LEGACY.json')
    return report, {**totals, 'method': '15 inherited suites with controlled/synthetic harnesses, adapted for current contracts; not native city playthroughs.', 'adapterExecutedBytesRecreatedAndMatched': True}


def browser(c, key, relative, html, frozen):
    folder = c.evidence / relative
    name = 'ARCHITECTURE_NATIVE.json' if key == 'native' else 'CITY_ARCHITECTURE_BROWSER.json'
    report = c.obj(folder / name)
    totals = checked(report, key)
    require(report.get('stage') == 'complete' and report.get('html_sha256') == html, key + ': unfinished or stale HTML')
    for field in ('html_injected', 'network_mocked', 'storage_mocked', 'synthetic_geography'):
        require(report.get(field) is False, key + ': native method missing/changed: ' + field)
    require(isinstance(report.get('assistance'), list) and report['assistance'], key + ': assistance declaration missing')
    require(report.get('server_audit', {}).get('ok') is True, key + ': server source audit absent')
    snapshot = report.get('source_snapshot')
    require(isinstance(snapshot, dict), key + ': source snapshot missing')
    if key == 'native':
        require(report.get('native_navigation') is True and report.get('synthetic_documents') is False, 'Native document/movement declaration missing')
        require(report.get('local_pack_audit', {}).get('complete') is True, 'Native local pack audit incomplete')
        for relative_source, expected in snapshot.items():
            require(digest(c.read(c.root / safe_relative(relative_source))) == expected, 'Native source snapshot stale: ' + relative_source)
        require(report.get('architecture_sha256') == frozen['files']['data/map_pack/architecture/index.json']['sha256'], 'Native architectural atlas stale')
        terminal = 'Frozen HTML, sources, atlas, selected geographic chunks and city indices remain unchanged'
    else:
        for field, filename in [('index_sha256','index.json'),('terrain_index_sha256','terrain-index.json'),('water_index_sha256','water-index.json')]:
            require(snapshot.get(field) == INDICES[filename], 'City source snapshot stale: ' + field)
        require(snapshot.get('html_sha256') == html, 'City source snapshot HTML stale')
        terminal = 'Production HTML, all three city indices and official boundary stayed unchanged'
    require(report['checks'][-1].get('name') == terminal, key + ': terminal unchanged check absent')
    shots = report.get('shots')
    require(isinstance(shots, list) and shots, key + ': captures absent')
    for shot in shots:
        image = safe_relative(shot['file'])
        require(image.name == str(image) and image.suffix == '.png', 'Unsafe browser capture')
        raw = c.add(folder / image, key + '/' + str(image))
        require(digest(raw) == shot['sha256'], key + ': capture SHA mismatch')
        c.captures.append({'path': key + '/' + str(image), 'sha256': digest(raw), 'html_sha256': html, 'label': shot.get('label'), 'method': shot.get('method', 'Actual WebGL capture with diagnostic assistance declared in report')})
    executed = folder / 'EXECUTED_SCRIPT.py'
    if not executed.is_file():
        executed = c.root / 'tests/expansion' / ('architecture_native_browser.py' if key == 'native' else 'city_architecture_browser.py')
    script_raw = c.add(executed, key + '/EXECUTED_SCRIPT.py')
    script_sha = report.get('script_sha256') or report.get('executed_script_sha256')
    execution_log = folder / 'EXECUTION.log'
    log_raw = c.add(execution_log, key + '/EXECUTION.log')
    script_identity = {'method': 'Script SHA recorded by the browser runner in its runtime report.', 'capturedAfterExecution': False, 'runtimeReportContainsScriptHash': True}
    if key == 'city' and not script_sha:
        identity = c.obj(folder / 'EXECUTION_IDENTITY.json')
        script_sha = identity.get('scriptSha256')
        require(identity.get('capturedAfterExecution') is True and identity.get('runtimeReportContainsScriptHash') is False, 'City post-completion identity declaration missing')
        require(identity.get('reportSha256') == digest(c.read(folder / name)) and identity.get('executionLogSha256') == digest(log_raw), 'City post-completion report/stdout identity stale')
        require(digest(c.read(c.root / 'tests/expansion/city_architecture_browser.py')) == script_sha, 'City archived/current executed script differ')
        command = identity.get('command')
        require(isinstance(command, list) and 'tests/expansion/city_architecture_browser.py' in command and '--expect-html-sha' in command and command[command.index('--expect-html-sha') + 1] == html, 'City recorded command/build identity differs')
        require(datetime.fromisoformat(identity['capturedAt']) >= datetime.fromisoformat(identity['scriptLastModifiedAt']), 'City post-completion identity timestamp inconsistent')
        c.add(folder / 'EXECUTION_IDENTITY.json', key + '/EXECUTION_IDENTITY.json')
        script_identity = {'method': identity['scope'], 'capturedAfterExecution': True, 'runtimeReportContainsScriptHash': False, 'scriptReportAndStdoutHashesVerified': True, 'archivedAndCurrentScriptMatch': True}
    require(script_sha and digest(script_raw) == script_sha, key + ': executed browser script identity missing/stale')
    if key == 'native':
        artifacts = report.get('layout_artifacts', {})
        layout_file, svg_file = safe_relative(artifacts.get('json')), safe_relative(artifacts.get('svg'))
        layout = c.obj(folder / layout_file)
        require(layout.get('nativeReportSha256') == digest(c.read(folder / name)), 'Layout bound to another native report')
        require(layout.get('htmlSha256') == html and layout.get('executedScriptSha256') == script_sha, 'Layout build/script binding stale')
        require(layout.get('actualLayout') == report['interior']['layout'] and layout.get('sourceTarget') == report['interior']['chosen']['sourceTarget'], 'Layout differs from actual runtime export')
        layout_raw = c.add(folder / layout_file, key + '/' + str(layout_file))
        svg_raw = c.add(folder / svg_file, key + '/' + str(svg_file))
        metadata = ET.fromstring(svg_raw).find('{http://www.w3.org/2000/svg}metadata')
        require(metadata is not None, 'SVG provenance absent')
        svg_binding = json.loads(metadata.text)
        require(svg_binding.get('layoutJsonSha256') == digest(layout_raw) and svg_binding.get('nativeReportSha256') == digest(c.read(folder / name)) and svg_binding.get('htmlSha256') == html and svg_binding.get('layoutSignature') == layout['actualLayout']['signature'], 'SVG layout provenance mismatch')
        integrity = c.obj(folder / 'EVIDENCE_INTEGRITY.json')
        expected_integrity = {'scriptSha256': script_sha, 'reportSha256': digest(c.read(folder / name)), 'shotsVerified': len(shots), 'layoutJsonSha256': digest(layout_raw), 'svgSha256': digest(svg_raw), 'executionLogSha256': digest(log_raw), 'sourceSnapshotsStillMatch': True}
        require(all(integrity.get(k) == v for k,v in expected_integrity.items()), 'Native evidence integrity summary differs')
        c.add(folder / 'EVIDENCE_INTEGRITY.json', key + '/EVIDENCE_INTEGRITY.json')
    c.add(folder / name, key + '/' + name)
    return report, {**totals, 'method': report['scope'] + ('\nThe executed script/report/stdout identity was captured after completion, rather than pinned inside the runtime report.' if script_identity['capturedAfterExecution'] else ''), 'scriptIdentity': script_identity, 'assistance': report['assistance'], 'nativePilotCount': 1, 'remoteNetworkObservations': {field: report.get(field, []) for field in ('external_request_failures', 'resource_console_diagnostics', 'request_failures')}, 'rawNetworkObservationsAreNotJavaScriptFailures': True}


def manifested_tree(c, source_name, target_name, manifest_name):
    folder = c.evidence / source_name
    manifest = c.obj(folder / manifest_name)
    require(isinstance(manifest.get('files'), dict) and manifest['files'], 'Evidence manifest empty: ' + source_name)
    for name, row in manifest['files'].items():
        relative = safe_relative(name)
        raw = c.add(folder / relative, target_name + '/' + str(relative))
        require(digest(raw) == row['sha256'] and len(raw) == row['bytes'], 'Evidence manifest stale: ' + source_name + '/' + name)
    c.add(folder / manifest_name, target_name + '/' + manifest_name)


def coverage(c, frozen):
    manifested_tree(c, 'coverage', 'coverage-initial', 'COVERAGE_MANIFEST.json')
    manifested_tree(c, 'coverage-final', 'coverage-final', 'MANIFEST.json')
    curves = c.obj(c.evidence / 'coverage-final/CURVES_COMPARE.json')
    attributes = c.obj(c.evidence / 'coverage-final/ATTRIBUTES_COMPARE.json')
    require(curves.get('status') == 'frozen-code-comparison', 'Curve comparison not final')
    for name, curve_key, attr_key in [('src/v050/07_facades.js','currentFacade','facadesCurrent'),('src/v050/08_city_interiors.js','currentInterior','interiorsCurrent')]:
        expected = frozen['files'][name]['sha256']
        require(curves['moduleHashes'][curve_key] == attributes['modulesAndEvidence'][attr_key]['sha256'] == expected, 'Coverage uses another module freeze')
    require(curves['summary']['sourcesUnchanged'] is True and attributes['summary']['allDrawsAndFootprintsUnchanged'] is True, 'Comparison changed source geometry')
    require(attributes.get('moduleAndEvidenceHashesUnchangedDuringRun') is True, 'Attribute comparison stability missing')
    require(curves['summary']['allPaginationConsistent'] is True and curves['summary']['currentCompatibleSpanFailures'] == 0, 'Facade span/pagination failure')
    return {'countedInValidationTotals': False, 'scope': 'Actual IGN source comparisons; counts describe sampled model coverage, not browser playthroughs. Initial documentary roundtrip/order reproducers use explicitly synthetic fixtures.', 'curves': curves['summary'], 'attributes': attributes['summary'], 'baselineCommit': curves['baselineCommit']}


def history(c):
    rows = []
    for source, target, report_name in [('native/failed-initial-network','historical/failed-initial-network','ARCHITECTURE_NATIVE.json'),('city-failed-helper','historical/city-failed-helper','CITY_ARCHITECTURE_BROWSER.json'),('city-failed-helper-anchor','historical/city-failed-helper-anchor','CITY_ARCHITECTURE_BROWSER.json')]:
        folder = c.evidence / source
        report = c.obj(folder / report_name)
        for item in sorted(folder.rglob('*')):
            if item.is_file() and '__pycache__' not in item.parts:
                c.add(item, target + '/' + str(item.relative_to(folder)))
        for shot in report.get('shots', []):
            require(digest(c.read(folder / safe_relative(shot['file']))) == shot['sha256'], 'Historical capture changed')
        rows.append({'path': target + '/' + report_name, 'stage': report.get('stage'), 'passed': report.get('passed'), 'failed': report.get('failed'), 'total': report.get('total'), 'html_sha256': report.get('html_sha256'), 'countedInValidationTotals': False, 'role': 'Failed superseded attempt retained verbatim; not final validation.'})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(os.environ.get('MISTRAL_REPO_ROOT', '/workspace/fallout-Marseille')))
    parser.add_argument('--evidence', type=Path, default=Path(os.environ.get('MISTRAL_EVIDENCE_DIR', Path(__file__).parent)))
    parser.add_argument('--output', type=Path)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--publish', action='store_true', help='Publish only after all complete frozen evidence validates')
    action.add_argument('--check-only', action='store_true', help='Validate without publication (default)')
    parser.add_argument('--replace', action='store_true', help='Permit replacing an earlier evidence directory after validation')
    args = parser.parse_args()
    root, evidence = args.repo.resolve(), args.evidence.resolve()
    destination = (args.output or root / 'verification/expansion/architecture').resolve()
    require(destination != root and not destination.is_relative_to(evidence), 'Unsafe publication destination')
    c = Collection(root, evidence)
    frozen, html = verify_frozen(c)
    unit_report, unit_result = units(c, html)
    _, rebuild_result = rebuild(c, frozen, html)
    _, legacy_result = legacy(c, html)
    city_report, city_result = browser(c, 'city', 'city-native', html, frozen)
    native_report, native_result = browser(c, 'native', 'native/final', html, frozen)
    comparisons, histories = coverage(c, frozen), history(c)
    c.add(Path(__file__).resolve(), 'scripts/collect_architecture.py')
    for relative in ['tests/expansion/architecture_sources.cjs','tests/expansion/architecture_runtime.cjs','tests/expansion/interior_document_persistence.cjs','tests/expansion/architecture_native_browser.py','tools/architecture_documents.cjs']:
        c.add(root / relative, 'scripts/repository/' + relative)
    results = {'isolatedUnits': unit_result, 'inheritedControlledContracts': legacy_result, 'independentRebuildOutputs': rebuild_result, 'assistedCityBrowser': city_result, 'assistedArchitectureBrowser': native_result}
    now = datetime.now(timezone.utc).isoformat()
    integration = {'schemaVersion': 1, 'createdAt': now, 'stage': 'complete', 'ok': True, 'html_sha256': html, 'allHtmlMatch': True, 'completeGameOrOneToOneWorldClaimed': False, 'scope': 'Separate reported assertion totals by method. Unit fixtures, inherited synthetic/controlled contracts, byte comparisons, assisted native pilots and source-geometry comparisons are distinct evidence; their counts are not equivalent gameplay runs.', 'checksByMethod': results, 'nativePilotCount': 2, 'comparisonsExcludedFromValidationTotals': comparisons, 'historicalReportsExcludedFromValidationTotals': histories, 'sourceIndices': INDICES, 'frozenProduction': frozen['files'], 'captures': c.captures, 'documentaryFixtures': {'isolatedTests': 'Explicit synthetic attributed plans test validation/persistence; they are never installed in the delivered atlas.', 'browserPilots': 'Actual IGN geometry and 12 attributed site contexts; procedural rooms/facades are invented and no synthetic documentary plan is installed.'}, 'limits': ['Source acquisition and metric reproduction do not certify a surveyed 1:1 facade/interior for every real building.', 'Diagnostic sector/camera placement, frozen simulation/rendering and stepped native physics remain declared assistance.', 'Remote request failures remain observations in original native reports; qualified local-geography and JavaScript errors must be empty.', 'Comparison coverage cases and failed historical attempts are excluded from final assertion totals.'], 'inputHashes': {str(p): h for p, h in c.snapshots.items()}}
    integration['reportedAssertionSum'] = sum(result['total'] for result in results.values())
    integration['assertionSumIsNotEquivalentPlaythroughCount'] = True
    c.generated('ARCHITECTURE_INTEGRATION.json', integration)
    readme = f'''# Architecture Marseille : preuves de validation\n\nBuild HTML : `{html}`. Les rapports originaux sont conservés sans modification.\n\n- Unités isolées : **877 assertions**, zéro processus en échec ; voir `UNITS.json` et `units/`.\n- Contrats hérités : **434 assertions**, quinze suites avec bancs contrôlés/synthétiques ; voir `legacy/`. Les scripts adaptés sont recréés et vérifiés contre leurs empreintes d’exécution.\n- Rebuild indépendant : **3 sorties identiques**, syntaxe JavaScript valide ; voir `REBUILD.json`.\n- Navigateur ville assisté : **{city_result['total']} assertions** ; navigateur architecture assisté : **{native_result['total']} assertions**. Les aides et observations réseau restent décrites dans chaque rapport.\n\nPour le pilote ville hérité, l’identité du script exécuté, du rapport et de stdout est attestée après exécution : `city/EXECUTION_IDENTITY.json` conserve cette limite explicitement ; le rapport original est intact. Le nouveau pilote architecture inscrit le SHA du script dans son rapport d’exécution.\n\nLes deux pilotes natifs utilisent le HTML de production, les données IGN locales, le vrai HTTP et le stockage navigateur. Les placements de caméra, gels QA et déplacements physiques cadencés sont assistés. Les captures sont des rendus WebGL ; le SVG est une vue d’audit dérivée du véritable export de layout et conserve ses liens SHA. Aucun plan documentaire synthétique n’est installé dans ces pilotes.\n\n`coverage-initial/` contient les reproducers baseline, y compris les fixtures documentaires explicitement synthétiques. `coverage-final/` contient les comparaisons sur objets IGN réels et la procédure portable. Leurs cas de couverture ne sont pas comptés comme parcours navigateur. `historical/` conserve les trois tentatives en échec, exclues des totaux finaux.\n\nLes façades/pièces inventées ne sont pas des relevés réels. Cette publication ne certifie pas une reproduction documentaire intégrale de Marseille ni un jeu complet.\n\n`ARCHITECTURE_INTEGRATION.json` sépare toutes les méthodes, totaux et limites. `MANIFEST.json` donne les SHA-256 de tous les fichiers publiés, hors lui-même. Le collecteur ne lance ni test, navigateur, acquisition réseau, ni build : `python scripts/collect_architecture.py --repo CHEMIN --evidence DOSSIER_QA --check-only`. La publication exige `--publish` ; `--replace` permet de remplacer un ancien dossier après validation complète.\n'''
    c.files['README.md'] = readme.encode()
    c.unchanged()
    if not args.publish:
        print(json.dumps({'status': 'validated without publication', 'html_sha256': html, 'files': len(c.files), 'totalsByMethod': {k: v['total'] for k,v in results.items()}, 'comparisonCasesExcluded': True}, ensure_ascii=False))
        return 0
    require(not destination.exists() or args.replace, 'Destination already exists; --replace required')
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.architecture-stage-', dir=destination.parent))
    backup = None
    try:
        for relative, raw in c.files.items():
            target = staging / safe_relative(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            require(digest(target.read_bytes()) == digest(raw), 'Staged file differs: ' + relative)
        manifest = {'schemaVersion': 1, 'createdAt': now, 'html_sha256': html, 'selfExcluded': True, 'files': {name: {'sha256': digest(raw), 'bytes': len(raw)} for name,raw in sorted(c.files.items())}}
        (staging / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        c.unchanged()
        if destination.exists():
            backup = Path(tempfile.mkdtemp(prefix='.architecture-previous-', dir=destination.parent))
            backup.rmdir()
            os.replace(destination, backup)
        os.replace(staging, destination)
        if backup:
            shutil.rmtree(backup)
    except Exception:
        if backup and backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(json.dumps({'status': 'published validated architecture evidence', 'directory': str(destination), 'files': len(c.files) + 1, 'totalsByMethod': {k:v['total'] for k,v in results.items()}}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        raise SystemExit('Architecture evidence not published: ' + str(error))
