#!/usr/bin/env python3
"""Assisted native HTTP pilot for two actual source-based interior programmes.

No browser starts without --run and coordinated frozen SHA values. Source usage
and footprints come from real installed IGN chunks; partitions, portals and all
furniture remain explicitly invented. Sector selection, measured collision-free
camera placement, render/simulation freeze, v020Approach and stepped production
physics use the same public diagnostic APIs as architecture_native_browser.py.
E-key entries, visible exit controls and cold Continue are native browser actions.
No synthetic terrain, actor, plan, save, HTML or HTTP response is injected.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import ast
import json
import math
import sys
import threading
import time
import traceback
import urllib.request

from architecture_native_browser import sha, finite, source_anchor, point_in_ring

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = 'tests/expansion/fixtures/interior_source_uses.json'
MODULE = 'src/v050/08_city_interiors.js'
CITY = 'geo_marseille_commune'
HELPER_MODULE = 'tests/expansion/architecture_native_browser.py'
HELPER_NAMES = {'sha', 'finite', 'source_anchor', 'point_in_ring'}


def helper_definitions(raw):
    """Pin only the four reused pure helpers, independently of the other pilot main."""
    tree = ast.parse(raw.decode())
    definitions = {node.name: sha(ast.dump(node, include_attributes=False).encode())
                   for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in HELPER_NAMES}
    if set(definitions) != HELPER_NAMES:
        raise AssertionError('Missing read-only architecture geometry helper')
    return definitions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--room-doors', action='store_true', help='Also exercise the real version-five room door lifecycle with native E and KeyW.')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    parser.add_argument('--expect-interior-sha', required=True)
    parser.add_argument('--expect-architecture-sha', required=True)
    parser.add_argument('--ready-timeout', type=int, default=300)
    parser.add_argument('--maximum-sectors', type=int, default=6)
    args = parser.parse_args()
    if not args.run:
        print('Prepared only. No server or browser started; --run requires coordinated frozen SHA values.')
        return 0
    sys.path.insert(0, str(ROOT / 'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright

    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {'scope': __doc__, 'stage': 'preflight', 'checks': [], 'shots': [], 'attempts': [],
              'programmes': [], 'native_navigation': False, 'html_injected': False,
              'network_mocked': False, 'storage_mocked': False, 'synthetic_geography': False,
              'synthetic_documents': False, 'contexts_created': 0, 'maximum_contexts': 1,
              'service_workers_disabled': True, 'page_errors': [], 'javascript_console_errors': [],
              'resource_console_diagnostics': [], 'local_request_failures': [],
              'external_request_failures': [], 'local_http_errors': [], 'http_responses': [],
              'script_sha256': sha(Path(__file__).read_bytes()),
              'assistance': ['Public native macro/sector selection loads real installed sources.',
                             'Public v046Height/v046Collide choose measured clear camera positions.',
                             'Public v018CaptureAt freezes simulation/render and frames actual geometry.',
                             'Public v020Approach chooses production collision/LOS checked placement before a real E key.',
                             'Native KeyW plus v020Tick(.05,true) manually steps actual production movement/collisions.',
                             'Read-only public exports inspect source identity, programme, furniture, storage and collisions.']}
    frozen, originals, imported_helpers = {}, {}, {}
    page = server = browser = context = worker = pw = None
    origin = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']), total=len(report['checks']),
                      pinned_inputs=dict(frozen))
        (args.output / 'INTERIOR_PROGRAMS_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def check(name, ok, detail=None, required=True):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ') + name, flush=True)
        save()
        if required and not ok:
            raise AssertionError(name)

    def stage(name):
        report['stage'] = name
        print('STAGE ' + name, flush=True)
        save()

    def pin(relative):
        raw = (ROOT / relative).read_bytes()
        digest = sha(raw)
        if relative in frozen and frozen[relative] != digest:
            raise AssertionError('Pinned input changed: ' + relative)
        frozen[relative] = digest
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def ready():
        deadline, last_print = time.monotonic() + args.ready_timeout, 0
        while time.monotonic() < deadline:
            info = debug('v047Info')
            if info['phase'] == 'failed':
                raise RuntimeError('Actual geographic staging failed: ' + json.dumps(debug('v046Info')))
            if info['tiles'] > 0 and not info['loading'] and not info['anticipating']:
                return info
            if time.monotonic() - last_print > 15:
                print('LOAD ' + json.dumps({k: info[k] for k in ('phase', 'done', 'total', 'tiles')}), flush=True)
                last_print = time.monotonic()
            page.wait_for_timeout(250)
        raise TimeoutError('Actual map readiness timeout: ' + json.dumps(debug('v047Info')))

    def native_document(response):
        check('Native HTTP document equals the frozen production bytes', response is not None
              and response.status == 200 and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("['v051CityReady','v052ArchitectureReady','v052ArchitectureTarget','v052CityInteriorLayout','v050CityInteriorBind'].every(k=>typeof __MISTRAL_DEBUG[k]==='function')")
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})

    def shot(name, label):
        player = debug('getState')['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])
        path = args.output / (name + '.png')
        page.screenshot(path=str(path))
        report['shots'].append({'file': path.name, 'sha256': sha(path.read_bytes()), 'label': label,
                                'method': 'Actual WebGL rendering after declared diagnostic placement/freeze.'})
        save()

    def sector(lat, lon):
        if not debug('v046Load', lat, lon):
            return None
        ready()
        points = [[lat + dz / 111320, lon + dx / (111320 * math.cos(math.radians(lat)))]
                  for dz in range(-100, 101, 10) for dx in range(-100, 101, 10)]
        clear = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,height:h.height,sources:h.sources,clear:Number.isFinite(h.height)&&!h.missing&&!d.v046Collide(p[0],p[2])};}).filter(p=>p.clear);}""", points)
        if not clear:
            return None
        clear.sort(key=lambda p: math.hypot(p['ll'][0] - lat, (p['ll'][1] - lon) * math.cos(math.radians(lat))))
        point = clear[0]
        debug('v018CaptureAt', [point['p'][0], point['height'] + 1.65, point['p'][2]], 0, -.12)
        debug('v050FacadeRefresh')
        debug('v050CityInteriorBind')
        return point

    def physical_entry(door):
        if not debug('v020Approach', door['id']):
            return None
        player = debug('getState')['player']
        ll = debug('v046LL')
        ground = debug('v046Height', *ll)
        if not finite(ground['height']) or ground.get('missing'):
            return None
        position = [player['pos'][0], ground['height'] + 1.65, player['pos'][2]]
        if debug('v020Collides', position):
            return None
        debug('v018CaptureAt', position, player['yaw'], 0)
        label = page.locator('#interactLabel').inner_text()
        if 'entrer' not in label.casefold():
            return None
        record = {'interaction': door['id'], 'label': label, 'position': position, 'actualKeyboardAction': 'e'}
        page.keyboard.press('e')
        page.wait_for_function('id=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.id===id', arg=door['building'], timeout=15000)
        return record

    def exit_to_street():
        interaction = next((i for i in debug('v020Stats')['interactables'] if i['id'] == 'city-interior-landing'), None)
        check('Actual programme exposes its native landing interaction', interaction is not None)
        layout = debug('v052CityInteriorLayout')
        position = [interaction['pos'][0], layout['elevation'] + 1.65, interaction['pos'][2]]
        check('Landing camera placement is clear of actual production solids', not debug('v020Collides', position))
        debug('v018CaptureAt', position, 0, 0)
        check('Visible E-key interaction identifies the actual landing', 'palier' in page.locator('#interactLabel').inner_text().casefold())
        page.keyboard.press('e')
        page.locator('#dialogue').wait_for(state='visible')
        page.get_by_role('button', name='Sortir vers la rue', exact=True).click()
        ready()
        page.wait_for_function('!__MISTRAL_DEBUG.v050CityInteriorInfo().exitPending && !__MISTRAL_DEBUG.v050CityInteriorInfo().active', timeout=120000)

    try:
        pin('tests/expansion/interior_programs_native.py')
        if args.room_doors:
            pin('tests/expansion/interior_doors_native.py')
            from interior_doors_native import probe_room_door
            report['room_door_pilot'] = {'script': 'tests/expansion/interior_doors_native.py', 'sha256': frozen['tests/expansion/interior_doors_native.py']}
        helper_raw = (ROOT / HELPER_MODULE).read_bytes()
        imported_helpers.update(helper_definitions(helper_raw))
        report['imported_geometry_helpers'] = {'sourcePath': HELPER_MODULE, 'definitionsSha256': dict(imported_helpers),
                                               'moduleSha256AtPreflight': sha(helper_raw),
                                               'scope': 'Only these four pure geometry/hash helpers are imported; the concurrently maintained pilot main is not executed.'}
        helper_archive = args.output / 'architecture_native_browser.imported.py'
        check('Archived geometry helper definitions equal the imported helper definitions', helper_archive.is_file()
              and helper_definitions(helper_archive.read_bytes()) == imported_helpers)
        html = pin('index.html')
        check('Coordinated production HTML is installed', sha(html) == args.expect_html_sha)
        check('Coordinated interior source is frozen', sha(pin(MODULE)) == args.expect_interior_sha)
        atlas_raw = pin('data/map_pack/architecture/index.json')
        check('Coordinated architecture atlas is frozen', sha(atlas_raw) == args.expect_architecture_sha)
        for relative in [MODULE, 'src/v050/07_facades.js', 'src/v050/06_architecture_sources.js']:
            check('Production HTML includes current ' + relative, pin(relative).decode() in html.decode())
        fixture = json.loads(pin(FIXTURE))
        check('Case fixture describes attributed real source geometries', fixture['license'] == 'Licence Ouverte 2.0'
              and fixture['attribution'] == 'IGN — Géoplateforme' and len(fixture['cases']) == 3)
        for case in fixture['cases']:
            relative = case['sourcePath']
            raw = pin(relative)
            check('Actual source chunk matches the case acquisition SHA', sha(raw) == case['sourceChunkSha256'], relative)
            records = json.loads(raw)['features']
            originals.update({f['properties']['cleabs']: {'feature': f, 'path': relative} for f in records
                              if f['properties'].get('kind') == 'building'})
            actual = next(f for f in records if f['properties'].get('sourceId') == case['sourceId'])
            check('Pinned real feature exactly equals the attributed case geometry and properties', actual == case['rawFeature'], case['sourceId'])
        city_index = json.loads(pin('data/map_pack/city/index.json'))
        for relative in ['data/map_pack/city/terrain-index.json', 'data/map_pack/city/water-index.json',
                         city_index['municipality']['boundary']['path']]:
            pin(relative)
        report.update(html_sha256=sha(html), interior_sha256=args.expect_interior_sha,
                      architecture_sha256=sha(atlas_raw), source_snapshot=dict(frozen))

        class Handler(GameHandler):
            def log_message(self, *_arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin + '/index.html?skipboot'
        stage('actual_server_source_audit')
        with urllib.request.urlopen(origin + '/__mistral/city-sources', timeout=180) as response:
            audit = json.load(response)
            no_store = response.headers.get('Cache-Control') == 'no-store'
        check('Real GameHandler audits the installed source pack', no_store and audit['ok']
              and audit['indexSha256'] == frozen['data/map_pack/city/index.json'])
        with urllib.request.urlopen(origin + '/__mistral/local-data', timeout=300) as response:
            local_audit = json.load(response)
        check('Real disk audit is complete before native menu probes', local_audit['complete'] is True)
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        report['browser_version'] = browser.version
        context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
        report['contexts_created'] += 1
        page = context.new_page()
        page.on('pageerror', lambda error: report['page_errors'].append(str(error)))

        def console_seen(message):
            if message.type == 'error':
                target = 'resource_console_diagnostics' if message.text.startswith('Failed to load resource:') else 'javascript_console_errors'
                report[target].append({'text': message.text, 'location': message.location})

        def request_failed(request):
            report['local_request_failures' if request.url.startswith(origin + '/') else 'external_request_failures'].append({'url': request.url, 'failure': request.failure})

        def response_seen(response):
            if response.url.startswith(origin + '/'):
                item = {'url': response.url, 'status': response.status, 'from_service_worker': response.from_service_worker}
                report['http_responses'].append(item)
                if response.status >= 400:
                    report['local_http_errors'].append(item)

        page.on('console', console_seen)
        page.on('requestfailed', request_failed)
        page.on('response', response_seen)
        page.on('dialog', lambda dialog: dialog.accept())
        native_document(page.goto(report['url'], wait_until='load', timeout=60000))
        report['native_navigation'] = True
        debug('v051CityReady')
        debug('v052ArchitectureReady')
        debug('v018LoadMacro', CITY)
        ready()
        check('Actual geographic world is outside the synthetic lab', debug('v046Info')['lab'] is False)

        for group, uses, equipment in [('commerce', ['Commercial et services'], 'checkout'),
                                       ('atelier', ['Industriel', 'Agricole'], 'tool_cabinet')]:
            stage('actual_' + group + '_programme')
            preferred = [c['rawFeature']['properties']['cleabs'] for c in fixture['cases'] if c['rawFeature']['properties']['usage_1'] in uses]
            candidates = [r for r in originals.values() if r['feature']['properties'].get('usage_1') in uses]
            candidates.sort(key=lambda r: (r['feature']['properties']['cleabs'] not in preferred,
                                           preferred.index(r['feature']['properties']['cleabs']) if r['feature']['properties']['cleabs'] in preferred else 999,
                                           r['feature']['properties']['cleabs']))
            chosen = None
            for record in candidates[:args.maximum_sectors]:
                anchor = source_anchor(record['feature']['geometry'])
                measured = sector(*anchor)
                attempt = {'group': group, 'anchor': anchor, 'sourceId': record['feature']['properties']['sourceId'], 'measuredCamera': measured}
                report['attempts'].append(attempt)
                if not measured:
                    attempt['residual'] = 'no-measured-clear-camera'
                    save()
                    continue
                doors = []
                for door in debug('v050CityInteriorInfo')['doors']:
                    target = debug('v052ArchitectureTarget', door['building'])
                    source = originals.get(target['cleabs']) if target else None
                    if source and source['feature']['properties'].get('usage_1') in uses:
                        doors.append((door, target, source))
                doors.sort(key=lambda row: row[1]['cleabs'] != record['feature']['properties']['cleabs'])
                attempt['eligiblePortals'] = [d[0] for d in doors]
                for door, target, source in doors[:8]:
                    entry = physical_entry(door)
                    if not entry:
                        continue
                    layout = debug('v052CityInteriorLayout')
                    if not any(f['kind'] == equipment for f in layout['furniture']):
                        attempt.setdefault('programmeOmissions', []).append({'building': door['building'], 'coverage': layout['programCoverage']})
                        exit_to_street()
                        continue
                    chosen = {'portal': door, 'target': target, 'source': source, 'entry': entry, 'layout': layout}
                    break
                if chosen:
                    break
                save()
            check('A real admissible ' + group + ' source portal opens via native E with its trade equipment', chosen is not None, report['attempts'])
            layout, target, source = chosen['layout'], chosen['target'], chosen['source']
            state = debug('getState')
            active = debug('v050CityInteriorInfo')['active']
            return_point, inventory = state['v050City']['returnPoint'], state['inventory']
            item = {'group': group, 'sourcePath': source['path'], 'sourceFeature': source['feature'],
                    'chosen': {k: v for k, v in chosen.items() if k != 'source'}, 'initial': active,
                    'returnPoint': return_point}
            report['programmes'].append(item)
            check('Entered source footprint and explicit primary use remain attributable and unchanged',
                  target['rawGeometry'] == source['feature']['geometry'] and layout['rings'] == state['v050City']['active']['building']['rings']
                  and layout['layoutVersion'] == 5 and layout['provenance'] == 'invented' and layout['source'] is None
                  and layout['programCoverage']['useBasis'] == {'kind': layout['theme'], 'basis': 'source-attribute', 'field': 'usage_1', 'value': source['feature']['properties']['usage_1']})
            check('Actual trade equipment has rendered parts and solid colliders',
                  active['furnishing']['objects'] == len(layout['furniture']) == active['furnishing']['colliderFurniture']
                  and active['furnishing']['renderFurniture'] > len(layout['furniture']) and active['furnishing']['byKind'].get(equipment, 0) > 0)
            furniture = next(f for f in layout['furniture'] if f['kind'] == equipment)
            center = [furniture['pos'][0], layout['elevation'] + 1.65, furniture['pos'][1]]
            approach = [furniture['approach'][0], layout['elevation'] + 1.65, furniture['approach'][1]]
            aim = [center[0], layout['elevation'] + furniture['height'] + .1, center[2]]
            check('New trade equipment is physically solid and its reserved camera approach is clear',
                  debug('v020Collides', center) and not debug('v020Collides', approach), {'kind': equipment, 'center': center, 'approach': approach})
            check('Production line of sight reaches the actual visible trade equipment', debug('v020LOS', approach, aim))
            yaw = math.atan2(center[0] - approach[0], -(center[2] - approach[2]))
            pitch = math.atan2(layout['elevation'] + furniture['height'] * .6 - approach[1], math.hypot(center[0] - approach[0], center[2] - approach[2]))
            debug('v018CaptureAt', approach, yaw, max(-1.3, pitch))
            shot(group + '_equipment', 'Actual invented trade furniture inside a source footprint; diagnostic clear camera and native WebGL.')
            trace = []
            page.keyboard.down('w')
            try:
                for _ in range(16):
                    debug('v020Tick', .05, True)
                    trace.append(debug('getState')['player']['pos'])
            finally:
                page.keyboard.up('w')
            final = trace[-1]
            advance = math.hypot(final[0] - approach[0], final[2] - approach[2])
            item['assistedEquipmentCollision'] = {'method': 'Native KeyW with v020Tick(.05,true), production collision, diagnostic initial placement',
                                                   'from': approach, 'positions': trace, 'advanceMeters': advance}
            check('Actual movement advances then stops against the trade equipment solid',
                  .01 < advance < .65 and not debug('v020Collides', final)
                  and not point_in_ring(furniture['ring'], [final[0], final[2]]), item['assistedEquipmentCollision'])
            check('Bounded programme circulation creates no newly unreachable source cells', layout['programCoverage']['navigation']['newUnreachableCells'] == 0)
            if args.room_doors:
                item['roomDoor'] = probe_room_door(page, debug, check, shot, group)
            key = debug('v018PersistentStatus')['key']
            saved = page.evaluate('key=>JSON.parse(localStorage.getItem(key))', key)
            check('Native storage retains the actual source programme and exterior return point', saved['v050City']['active']['building']['layoutVersion'] == 5
                  and saved['v050City']['active']['building']['id'] == active['id'] and saved['v050City']['returnPoint'] == return_point)
            native_document(page.reload(wait_until='load', timeout=60000))
            page.locator('#btnContinue').click()
            page.wait_for_function('id=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.id===id', arg=active['id'], timeout=120000)
            restored = debug('v050CityInteriorInfo')['active']
            check('Cold native Continue restores the same source building, floor and full programme signature',
                  restored['id'] == active['id'] and restored['floor'] == active['floor'] and restored['signature'] == active['signature']
                  and debug('v052CityInteriorLayout')['programCoverage']['useBasis'] == layout['programCoverage']['useBasis'])
            check('Native Continue preserves inventory and the exact geographic return point', debug('getState')['inventory'] == inventory
                  and debug('getState')['v050City']['returnPoint'] == return_point)
            if args.room_doors:
                prior_door = item['roomDoor']['door']
                restored_doors = debug('v050CityInteriorInfo')['roomDoors']['doors']
                if prior_door is None:
                    check('Cold native Continue keeps the originally open hall without an invented room door', not restored_doors)
                else:
                    restored_door = next((d for d in restored_doors if d['id'] == prior_door['id']), None)
                    check('Cold native Continue restores the exact closed leaf, handles and collision', restored_door == prior_door)
            item['restored'] = restored
            shot(group + '_continue', 'Native Continue after a real document reload in the same browser context.')
            exit_to_street()
            exterior = debug('getState')
            check('Visible native exit restores the original street point and inventory',
                  math.dist(exterior['player']['pos'], return_point['pos']) < .2 and exterior['inventory'] == inventory
                  and exterior['v050City']['active'] is None and exterior['v050City']['returnPoint'] is None)
            shot(group + '_street_return', 'Actual source street after native exit, with original return point preserved.')

        if args.room_doors:
            report['room_door_scope'] = {'physically_exercised': [r['group'] for r in report['programmes'] if r['roomDoor']['door'] is not None],
                                         'open_programmes_without_eligible_room_doors': [r['group'] for r in report['programmes'] if r['roomDoor']['door'] is None]}
            check('At least one actual source programme completes the full native physical room-door cycle', bool(report['room_door_scope']['physically_exercised']))
        check('Both native programmes are distinct and retain source use provenance',
              len(report['programmes']) == 2 and {r['chosen']['layout']['theme'] for r in report['programmes']} == {'commercial', 'industrial'})
        check('No synthetic documentary record entered native storage', debug('v050CityInteriorInfo')['documentRegistry']['entries'] == 0)
        check('Actual source and interior transactions contain no runtime exception', not debug('v051CityInfo')['errors'] and not debug('v050CityInteriorInfo')['errors'])
        check('Native session records no JavaScript application failure', not report['page_errors'] and not report['javascript_console_errors'], report['javascript_console_errors'])
        check('Native local HTTP data loads succeed without a service worker', not report['local_request_failures'] and not report['local_http_errors']
              and all(not r['from_service_worker'] for r in report['http_responses']))
        check('One fresh browser context was used through native cold Continues', report['contexts_created'] == 1)
        context.close()
        report['context_closed'] = True
        context = None
        browser.close()
        report['browser_closed'] = True
        browser = None
        stage('complete')
    except Exception:
        report['exception'] = traceback.format_exc()
        print(report['exception'], flush=True)
        check('Native source programme pilot completes', False, report['exception'], required=False)
        if page is not None and not page.is_closed():
            try:
                shot('FAILURE', 'Actual native UI at failure, without substituted fixture or image.')
            except Exception:
                pass
    finally:
        for label, resource in [('context', context), ('browser', browser)]:
            if resource is not None:
                try:
                    resource.close()
                    report[label + '_closed'] = True
                except Exception as error:
                    report.setdefault('cleanup_errors', []).append(str(error))
        if pw is not None:
            try:
                pw.stop()
                report['playwright_stopped'] = True
            except Exception as error:
                report.setdefault('cleanup_errors', []).append(str(error))
        if server is not None:
            server.shutdown()
            server.server_close()
        if worker is not None:
            worker.join(timeout=5)
        changed = [relative for relative, digest in frozen.items()
                   if not (ROOT / relative).is_file() or sha((ROOT / relative).read_bytes()) != digest]
        check('Frozen HTML, modules, fixtures and selected real source chunks remain unchanged', not changed, changed, required=False)
        check('The four imported read-only architecture helpers remain unchanged',
              not imported_helpers or helper_definitions((ROOT / HELPER_MODULE).read_bytes()) == imported_helpers,
              report.get('imported_geometry_helpers'), required=False)
        save()
    print(json.dumps({k: report[k] for k in ('passed', 'failed', 'total', 'stage')}, ensure_ascii=False), flush=True)
    return int(bool(report['failed'] or report['page_errors'] or report['stage'] != 'complete'))


if __name__ == '__main__':
    raise SystemExit(main())
