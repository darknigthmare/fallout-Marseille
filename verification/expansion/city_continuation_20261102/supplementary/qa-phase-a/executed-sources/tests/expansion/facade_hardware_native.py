#!/usr/bin/env python3
"""Native facade hardware pilot; no server or Chromium starts without --run.

Five pinned, acquired IGN buildings are read from their actual installed city
partitions. The production HTML, source module, live opening inventory, emitted
WebGL vertex ranges, HTTP and localStorage remain real. No fixture is installed
as geography and no documentary plan is injected. Existing sector/camera APIs,
QA simulation/render freeze and a collision/LOS checked approach are declared
assistance; doorway and landing actions use real keyboard E and visible buttons.
Inspection cameras may be above standing height, explicitly recorded as such.
This is a bounded assisted integration pilot, not a human citywide playthrough.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import math
import subprocess
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
CITY = 'geo_marseille_commune'
ROLES = ('residential', 'commercial', 'industrial', 'religious', 'microcurve')
NEW_KINDS = ('joinery-relief', 'shutter-hardware')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def finite(n):
    return type(n) in (int, float) and math.isfinite(n)


def anchor(geometry):
    ring = (geometry['coordinates'][0] if geometry['type'] == 'MultiPolygon' else geometry['coordinates'])[0]
    return [(min(p[1] for p in ring) + max(p[1] for p in ring)) / 2,
            (min(p[0] for p in ring) + max(p[0] for p in ring)) / 2]


def inverse_lambert(x, y):
    e, n, c = .0818191910428158, .725607765053267, 11754255.426096
    dx, dy = x - 700000, 12655612.049876 - y
    value = -math.log(math.hypot(dx, dy) / c) / n
    phi = 2 * math.atan(math.exp(value)) - math.pi / 2
    for _ in range(12):
        phi = 2 * math.atan(math.exp(value) * ((1 + e * math.sin(phi)) / (1 - e * math.sin(phi))) ** (e / 2)) - math.pi / 2
    return [math.degrees(phi), 3 + math.degrees(math.atan2(dx, dy) / n)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    parser.add_argument('--expect-facade-sha', required=True)
    parser.add_argument('--ready-timeout', type=int, default=300)
    args = parser.parse_args()
    if not args.run:
        print(json.dumps({'preparedOnly': True, 'browserStarted': False, 'serverStarted': False,
                          'scriptSha256': sha(Path(__file__).read_bytes()),
                          'requiredRoles': ROLES, 'expectedHtmlSha256': args.expect_html_sha,
                          'expectedFacadeSha256': args.expect_facade_sha}))
        return 0
    if not 30 <= args.ready_timeout <= 900:
        parser.error('--ready-timeout must be between 30 and 900 seconds')
    sys.path.insert(0, str(ROOT / 'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright

    args.output.mkdir(parents=True, exist_ok=True)
    executed_script = Path(__file__).read_bytes()
    (args.output / 'EXECUTED_FACADE_HARDWARE_NATIVE.py').write_bytes(executed_script)
    started = time.monotonic()
    report = {'scope': __doc__, 'script_sha256': sha(executed_script), 'stage': 'preflight',
              'html_injected': False, 'network_mocked': False, 'storage_mocked': False,
              'synthetic_geography': False, 'synthetic_documents': False,
              'assistance': ['Diagnostic real sector loading; measured free initial camera',
                             'QA simulation/render freeze and actual explicit WebGL captures',
                             'Collision and LOS checked inspection cameras; elevated views separately labelled',
                             'Existing physical approach before real E-key and landing UI actions'],
              'checks': [], 'shots': [], 'cases': [], 'page_errors': [], 'console_errors': [],
              'request_failures': [], 'local_http_errors': [], 'cleanup_errors': [], 'contexts_created': 0}
    frozen, source_chunks, sources_by_cleabs = {}, {}, {}
    page = server = worker = browser = context = pw = None
    origin = None

    def save():
        report.update(passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']), total=len(report['checks']),
                      elapsed_seconds=round(time.monotonic() - started, 3))
        (args.output / 'FACADE_HARDWARE_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        save()
        print(('OK ' if ok else 'FAIL ') + name, flush=True)
        if not ok:
            raise AssertionError(name)

    def pin(relative):
        raw = (ROOT / relative).read_bytes()
        digest = sha(raw)
        if relative in frozen and frozen[relative] != digest:
            raise AssertionError('Frozen input changed: ' + relative)
        frozen[relative] = digest
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def stage(name):
        report['stage'] = name
        save()
        print('STAGE ' + name, flush=True)

    def ready():
        deadline, last = time.monotonic() + args.ready_timeout, 0
        while time.monotonic() < deadline:
            info = debug('v047Info')
            if info['phase'] == 'failed':
                raise RuntimeError('Production staging failed: ' + json.dumps(debug('v046Info')))
            if info['tiles'] > 0 and not info['loading'] and not info['anticipating']:
                return info
            if time.monotonic() - last > 15:
                print('LOAD ' + json.dumps({k: info[k] for k in ('phase', 'done', 'total', 'tiles')}), flush=True)
                last = time.monotonic()
            page.wait_for_timeout(250)
        report['readiness_failure'] = {'map': debug('v047Info'), 'city': debug('v051CityInfo')}
        raise TimeoutError('Real source staging exceeded the bounded timeout')

    def shot(name, label):
        path = args.output / (name + '.png')
        p = debug('getState')['player']
        rendering = debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])
        check('Screenshot uses the actual WebGL renderer: ' + name, rendering['renderer']['backend'] == 'WebGL')
        page.screenshot(path=str(path))
        report['shots'].append({'file': path.name, 'sha256': sha(path.read_bytes()), 'label': label,
                                'actualPlayerCamera': p, 'method': 'Raw native WebGL screenshot, declared diagnostic camera/freeze, no image edit'})
        save()

    def clear_initial_camera(lat, lon):
        points = [[lat + dz / 111320, lon + dx / (111320 * math.cos(math.radians(lat)))]
                  for dz in range(-100, 101, 10) for dx in range(-100, 101, 10)]
        clear = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,height:h.height,clear:Number.isFinite(h.height)&&!h.missing&&!d.v046Collide(p[0],p[2])};}).filter(p=>p.clear);} """, points)
        check('Measured collision-free source-sector camera exists', bool(clear), clear[:3])
        clear.sort(key=lambda p: math.hypot(p['ll'][0] - lat, (p['ll'][1] - lon) * math.cos(math.radians(lat))))
        point = clear[0]
        debug('v018CaptureAt', [point['p'][0], point['height'] + 1.65, point['p'][2]], 0, -.1)
        debug('v050CityInteriorBind')
        debug('v050FacadeRefresh')
        return point

    def aim_at(facade, opening):
        spans = debug('v050FacadeOpeningSpans', facade['id'], opening)
        if not spans:
            return None
        span = spans[len(spans) // 2]
        ring = facade['rings'][span['ringIndex']]
        a, b = ring[span['edgeIndex']], ring[span['edgeIndex'] + 1]
        length = math.dist(a, b)
        tangent = [(b[0] - a[0]) / length, (b[1] - a[1]) / length]
        signed = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:]))
        direction = (1 if signed > 0 else -1) * (1 if span['ringIndex'] == 0 else -1)
        normal = [tangent[1] * direction, -tangent[0] * direction]
        at = span['offset'] + span['width'] / 2
        return {'target': [a[0] + tangent[0] * at + normal[0] * .08,
                           facade['baseY'] + opening['bottom'] + opening['height'] * .55,
                           a[1] + tangent[1] * at + normal[1] * .08],
                'normal': normal, 'tangent': tangent, 'sourceSpans': spans}

    def camera_for(reference, aim):
        lat, lon = reference['geographicPoint'][1], reference['geographicPoint'][0]
        projected = debug('v046Project', CITY, lat, lon)
        absolute = debug('v018Projection', lat, lon)['xy']
        frame = [absolute[0] - projected[0], absolute[1] + projected[2]]
        target, normal, tangent = aim['target'], aim['normal'], aim['tangent']
        requests = []
        for distance in (1.0, 1.3, 1.7, 2.2, 3.0, 4.5, 6.0):
            for lateral in (0, -.35, .35, -.8, .8):
                x = target[0] + normal[0] * distance + tangent[0] * lateral
                z = target[2] + normal[1] * distance + tangent[1] * lateral
                requests.append({'distance': distance, 'lateral': lateral,
                                 'll': inverse_lambert(x + frame[0], frame[1] - z)})
        measured = page.evaluate("""([requests,target])=>{const d=__MISTRAL_DEBUG,out=[];for(const q of requests){const h=d.v046Height(...q.ll),xz=d.v046Project('geo_huveaune',...q.ll);if(!Number.isFinite(h.height)||h.missing){out.push({...q,measured:false});continue;}for(const elevated of[false,true]){const y=elevated?Math.max(h.height+1.65,target[1]):h.height+1.65,p=[xz[0],y,xz[2]],clear=!d.v020Collides(p),los=clear&&d.v020LOS(p,target);out.push({...q,p,height:h.height,measured:true,clear,los,elevated:y>h.height+1.650001});}}return out;}""", [requests, target])
        eligible = [p for p in measured if p.get('clear') and p.get('los')]
        eligible.sort(key=lambda p: (abs(p['lateral']) + abs(p['distance'] - 1.3) * .4,
                                     abs(target[1] - p['p'][1]), p['elevated']))
        return {'selected': eligible[0] if eligible else None, 'candidates': measured, 'target': target,
                'scope': 'Actual measured terrain, clear production body/camera and production LOS. Elevated inspection camera is explicitly recorded; no terrain or model is changed.'}

    def hardware_ranges(facade):
        order = sorted(enumerate(facade['openings']), key=lambda pair: (pair[1]['type'] != 'door', pair[1]['bottom'], pair[0]))[:12]
        result = []
        for i, _ in order:
            actual = debug('v055FacadeProfileGeometry', facade['id'], i)
            if not actual:
                continue
            fittings = [j for j in actual['fittings'] if j['kind'] in NEW_KINDS and j['rendered']]
            if fittings:
                result.append({'openingIndex': i, 'actualPublished': actual, 'newFittings': fittings})
        return result

    def inspect_ranges(facade, rows, role):
        edges = []
        for ri, ring in enumerate(facade['rings']):
            signed = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:]))
            direction = (1 if signed > 0 else -1) * (1 if ri == 0 else -1)
            for a, b in zip(ring, ring[1:]):
                length = math.dist(a, b)
                if length > 1e-8:
                    t = [(b[0] - a[0]) / length, (b[1] - a[1]) / length]
                    edges.append((a, length, t, [t[1] * direction, -t[0] * direction]))
        total, profiled, handle_faces, hinges = 0, 0, 0, 0
        native_bounded, valid_buffers, supported, atomic = True, True, True, True
        invalid_fragments = []
        for row in rows:
            native = row['actualPublished']
            native_bounded = native_bounded and (native['buildingId'] == facade['id'] and native['maximumBuildingQuads'] == 512
                              and native['opening'] == facade['openings'][row['openingIndex']]
                              and sum(len(m['vertices']) for j in native['fittings'] for m in j['meshes']) <= 2048)
            for fitting in row['newFittings']:
                quads = 0
                for mesh in fitting['meshes']:
                    vertices, faces = mesh['vertices'], mesh['faces']
                    valid_buffers = valid_buffers and (len(vertices) == mesh['vertexCount'] and len(faces) == len(vertices) // 2
                                      and all(len(f) == 3 and all(type(i) is int and 0 <= i < len(vertices) for i in f) for f in faces))
                    for k in range(0, len(vertices), 4):
                        patch = vertices[k:k + 4]
                        def coords(e, p):
                            a, _, t, n = e
                            return ((p[0] - a[0]) * t[0] + (p[2] - a[1]) * t[1],
                                    (p[0] - a[0]) * n[0] + (p[2] - a[1]) * n[1])
                        edge = next((e for e in edges if all(len(p) == 3 and all(finite(v) for v in p)
                                    and -1e-6 <= coords(e, p)[0] <= e[1] + 1e-6
                                    and -1e-6 <= coords(e, p)[1] <= .075001
                                    and facade['baseY'] - 1e-6 <= p[1] <= facade['baseY'] + facade['height'] + 1e-6 for p in patch)), None)
                        supported = supported and edge is not None
                        if edge is None:
                            if len(invalid_fragments) < 8:
                                invalid_fragments.append({'kind': fitting['kind'], 'opening': row['openingIndex'], 'patch': patch})
                            continue
                        ds = [coords(edge, p)[1] for p in patch]
                        profiled += int(max(ds) - min(ds) > .01)
                        handle_faces += int(mesh['material'] == 'iron' and all(abs(v - .074) < 1e-6 for v in ds))
                        hinges += int(fitting['kind'] == 'shutter-hardware')
                        quads += 1
                atomic = atomic and (quads == fitting['requiredQuads'] and fitting['provenance'] == 'invented' and fitting['reason'] is None)
                total += quads
        check(role + ': actual readonly geometry is bounded and references the rendered openings', native_bounded)
        check(role + ': all published hardware triangles have valid complete buffer indices', valid_buffers)
        check(role + ': every new fragment stays on original source segments within 7.5 cm', supported, invalid_fragments)
        check(role + ': every new kit is reserved before any triangle is emitted', atomic)
        check(role + ': actual new assemblies have changing depth under their fixed 64-quad ceiling',
              0 < total <= 64 and profiled > 0, {'quads': total, 'profiledFragments': profiled,
                                               'raisedHandleFrontFaces': handle_faces, 'hingeFragments': hinges})
        return {'quadsInspected': total, 'profiledFragments': profiled,
                'raisedHandleFrontFaces': handle_faces, 'hingeFragments': hinges}

    def capture_hardware(reference, facade, rows, stem):
        result = {'attempts': [], 'views': [], 'visibleHandle': False, 'visibleHinge': False}
        order = sorted(rows, key=lambda r: (not any(j['kind'] == 'shutter-hardware' for j in r['newFittings']),
                                            facade['openings'][r['openingIndex']]['type'] != 'door', r['openingIndex']))
        for actual in order:
            opening = facade['openings'][actual['openingIndex']]
            wanted_hinge = any(j['kind'] == 'shutter-hardware' for j in actual['newFittings'])
            if result['views'] and opening['type'] != 'door' and (result['visibleHinge'] or not wanted_hinge):
                continue
            aim = aim_at(facade, opening)
            view = camera_for(reference, aim) if aim else {'selected': None, 'reason': 'no-source-span'}
            attempt = {'openingIndex': actual['openingIndex'], 'view': view}
            result['attempts'].append(attempt)
            if view['selected'] is None:
                continue
            p, target = view['selected']['p'], view['target']
            yaw = math.atan2(target[0] - p[0], -(target[2] - p[2]))
            pitch = math.atan2(target[1] - p[1], math.hypot(target[0] - p[0], target[2] - p[2]))
            debug('v018CaptureAt', p, yaw, max(-1.3, min(1.3, pitch)))
            debug('v050CityInteriorBind')
            debug('v050FacadeRefresh')
            refreshed = debug('v050FacadeBuilding', reference['sourceId'])
            matching = next((i for i, o in enumerate((refreshed or {}).get('openings', [])) if o == opening), None)
            current = debug('v055FacadeProfileGeometry', refreshed['id'], matching) if matching is not None else None
            current_new = [j for j in (current or {}).get('fittings', []) if j['kind'] in NEW_KINDS and j['rendered']]
            attempt['stillRenderedNewFittings'] = current_new
            if not current_new:
                continue
            view_record = {'openingIndex': matching, 'opening': opening, 'view': view,
                           'kindsActuallyRenderedAtCapture': [j['kind'] for j in current_new],
                           'actualPublishedAtCapture': current}
            result['views'].append(view_record)
            result['visibleHandle'] |= opening['type'] == 'door' and any(j['kind'] == 'joinery-relief' for j in current_new)
            result['visibleHinge'] |= any(j['kind'] == 'shutter-hardware' for j in current_new)
            shot(stem + '_' + str(len(result['views'])),
                 'Raw close inspection of currently published invented returns/hardware; clear production camera and LOS; elevated inspection viewpoint explicitly flagged')
            if len(result['views']) >= 2 or result['visibleHandle'] and result['visibleHinge']:
                break
        if not result['views']:
            result['status'] = 'no-clear-current-fitting-view'
            result['claim'] = 'Actual emitted buffers were inspected; no visible close view claimed because no clear camera/current matching fitting was found'
        return result

    try:
        html = pin('index.html')
        module = pin('src/v050/07_facades.js')
        check('Coordinated HTML and facade module match both exact expected SHA-256 values',
              sha(html) == args.expect_html_sha and sha(module) == args.expect_facade_sha,
              {'html': sha(html), 'facade': sha(module)})
        check('The frozen HTML actually embeds the exact current facade source', module.decode() in html.decode())
        report.update(html_sha256=sha(html), facade_sha256=sha(module))
        pin('tests/expansion/facade_hardware_native.py')
        for relative in ('src/game.js', 'JOUER_FALLOUT_MISTRAL_v0.50.html', 'sw.js',
                         'src/v050/08_city_interiors.js', 'data/map_pack/city/index.json',
                         'data/map_pack/city/terrain-index.json', 'data/map_pack/architecture/index.json'):
            pin(relative)
        fixtures = json.loads(pin('tests/expansion/fixtures/facades_joinery_ign.json'))
        pin('tests/expansion/facades_joinery.cjs')
        references_raw = subprocess.check_output(['node', 'tests/expansion/facades_joinery.cjs', '--camera-points'], cwd=ROOT)
        (args.output / 'CURRENT_MODEL_REFERENCES.json').write_bytes(references_raw)
        references = json.loads(references_raw)
        check('Current model references pin the exact module, generator and immutable IGN fixtures',
              references['facadeModuleSha256'] == args.expect_facade_sha
              and references['generatorSha256'] == frozen['tests/expansion/facades_joinery.cjs']
              and references['sourceFixtureSha256'] == frozen['tests/expansion/fixtures/facades_joinery_ign.json'])
        check('Exactly five actual acquired profiles are required',
              len(fixtures['cases']) == len(ROLES) and {c['role'] for c in fixtures['cases']} == set(ROLES))
        cases = []
        for role in ROLES:
            fixture = next(c for c in fixtures['cases'] if c['role'] == role)
            reference = next(c for c in references['cases'] if c['role'] == role)
            path = fixture['sourcePath']
            raw = pin(path)
            if path not in source_chunks:
                source_chunks[path] = json.loads(raw)
                for feature in source_chunks[path]['features']:
                    if feature['properties'].get('kind') == 'building' and feature['properties'].get('cleabs'):
                        sources_by_cleabs[feature['properties']['cleabs']] = {'feature': feature, 'path': path, 'sha256': sha(raw)}
            source = next(f for f in source_chunks[path]['features'] if f['properties']['sourceId'] == reference['sourceId'])
            check(role + ': installed original partition and exact acquired feature match the pinned fixture',
                  sha(raw) == reference['sourceChunkSha256'] == fixture['sourceChunkSha256']
                  and source == fixture['feature'] and source['properties']['provenance']['license'] == 'Licence Ouverte 2.0'
                  and source['properties']['cleabs'] == reference['stableSourceId'])
            cases.append({'role': role, 'reference': reference, 'source': source})
        report['source_snapshot'] = dict(frozen)

        class Handler(GameHandler):
            def log_message(self, *arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1600, 'height': 1000})
        report['contexts_created'] += 1
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror', lambda e: report['page_errors'].append(str(e)))
        page.on('console', lambda message: report['console_errors'].append(message.text) if message.type == 'error' else None)
        page.on('requestfailed', lambda req: report['request_failures'].append({'url': req.url, 'failure': req.failure}))
        page.on('response', lambda res: report['local_http_errors'].append({'url': res.url, 'status': res.status})
                if res.url.startswith(origin + '/data/map_pack/') and res.status >= 400 else None)
        page.on('dialog', lambda dialog: dialog.accept())
        response = page.goto(origin + '/index.html?skipboot', wait_until='load', timeout=60000)
        check('Native Chromium receives the exact frozen production document over HTTP',
              response.status == 200 and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("['v051CityReady','v052ArchitectureTarget','v050FacadeInfo','v050FacadeBuilding','v050FacadePage','v055FacadeProfileGeometry','v052CityInteriorLayout'].every(k=>typeof __MISTRAL_DEBUG[k]==='function')")
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        debug('setQuality', 'high')
        debug('setTime', 12)
        debug('v051CityReady')
        debug('v018LoadMacro', CITY)
        ready()
        visible_roles, raised_handle, hinge_seen = set(), False, False
        visible_handle, visible_hinge = False, False
        portal = None
        for number, case in enumerate(cases, 1):
            role, reference, source = case['role'], case['reference'], case['source']
            stage(role)
            lat, lon = anchor(source['geometry'])
            check(role + ': native staging loads the actual source sector', debug('v046Load', lat, lon) is True)
            ready()
            camera = clear_initial_camera(lat, lon)
            before = debug('v052ArchitectureTarget', reference['sourceId'])
            facade = debug('v050FacadeBuilding', reference['sourceId'])
            check(role + ': real native metric facade matches its complete original IGN geometry',
                  before is not None and before['rawGeometry'] == source['geometry']
                  and facade is not None and facade['rendered'] and not facade['ringsTruncated'] and not facade['openingsTruncated']
                  and before['component']['id'] == facade['id'] == reference['buildingId']
                  and before['component']['rings'] == facade['rings']
                  and abs(facade['height'] - reference['height']) < 1e-7
                  and abs(facade['baseY'] - reference['ground']) < 1e-7)
            pages, inventory, cursor = [], [], 0
            for _ in range(16):
                result = debug('v050FacadePage', facade['id'], cursor, 128)
                pages.append(result)
                inventory.extend(result['openings'])
                if result['done']:
                    break
                check(role + ': complete source-opening inventory cursor advances', result['nextCursor'] > cursor)
                cursor = result['nextCursor']
            check(role + ': every rendered opening and its exact clear passage belongs to the unchanged authoritative program',
                  pages[-1]['done'] and all(o in inventory for o in facade['openings'])
                  and all(o.get('clearWidthMeters', o['width']) >= .78 - 1e-7 for o in facade['openings'] if o['type'] == 'door'))
            detail, coverage = facade['detailCoverage'], facade['detailCoverage']['joineryCoverage']
            quads = detail['openingQuads'] + detail['panelEdges'] + detail['decorationQuads']
            check(role + ': actual new assemblies share the existing 512-quad building and scene/cache limits',
                  quads <= 512 and 0 < coverage['joineryReliefQuads'] <= coverage['maximumJoineryReliefQuads'] == 64
                  and debug('v050FacadeInfo')['quads'] <= 8192
                  and debug('v050FacadeInfo')['cache']['bytes'] <= 8 * 1024 * 1024,
                  {'quads': quads, 'coverage': coverage})
            rows = hardware_ranges(facade)
            check(role + ': actual published hardware ranges are present', bool(rows))
            inspected = inspect_ranges(facade, rows, role)
            raised_handle |= inspected['raisedHandleFrontFaces'] > 0
            hinge_seen |= inspected['hingeFragments'] > 0
            row = {'role': role, 'source': {'path': reference['sourcePath'], 'sha256': reference['sourceChunkSha256'],
                                          'cleabs': reference['stableSourceId'], 'sourceId': reference['sourceId']},
                   'initialCamera': camera, 'sourceBefore': before, 'facade': facade, 'inventoryPages': pages,
                   'actualPublishedHardware': rows, 'inspected': inspected}
            report['cases'].append(row)
            shot(f'{number:02d}_{role}_context', 'Actual acquired IGN footprint; authored facade detail and measured initial street camera, not a facade survey')
            row['capture'] = capture_hardware(reference, facade, rows, f'{number:02d}_{role}_hardware')
            visible_handle |= row['capture']['visibleHandle']
            visible_hinge |= row['capture']['visibleHinge']
            if row['capture']['views']:
                visible_roles.add(role)
            after = debug('v052ArchitectureTarget', reference['sourceId'])
            check(role + ': readonly geometry inspection and captures preserve the source geometry and metric component',
                  after['rawGeometry'] == before['rawGeometry'] and after['component'] == before['component'])
            # The historical residential reference can face a real party wall.
            # Inspect at most twelve other actually published residential
            # portals in its already pinned acquired partition, never a demo.
            if role == 'residential' and not (visible_handle and visible_hinge):
                attempts = report.setdefault('supplementarySourceScout', [])
                for candidate in debug('v050CityInteriorInfo')['doors'][:12]:
                    cleabs = candidate['building'].split(':', 1)[0]
                    acquired = sources_by_cleabs.get(cleabs)
                    if not acquired:
                        continue
                    actual_source = debug('v052ArchitectureTarget', cleabs)
                    extra_facade = debug('v050FacadeBuilding', cleabs)
                    if not actual_source or not extra_facade or extra_facade['style'] != 'residential' or not extra_facade['rendered'] or extra_facade['openingsTruncated']:
                        continue
                    if actual_source['rawGeometry'] != acquired['feature']['geometry']:
                        continue
                    extra_rows = hardware_ranges(extra_facade)
                    if not any(j['kind'] == 'shutter-hardware' for r in extra_rows for j in r['newFittings']):
                        continue
                    geometry = acquired['feature']['geometry']
                    polygon = geometry['coordinates'][0] if geometry['type'] == 'MultiPolygon' else geometry['coordinates']
                    extra_reference = {'sourceId': cleabs, 'geographicPoint': polygon[0][0]}
                    record = {'sourcePath': acquired['path'], 'sourceSha256': acquired['sha256'], 'actualSource': actual_source,
                              'scope': 'Supplementary actually published acquired residential object, not one of the five fixed reference cases'}
                    attempts.append(record)
                    record['capture'] = capture_hardware(extra_reference, extra_facade, extra_rows, '06_scout_hardware_' + str(len(attempts)))
                    visible_handle |= record['capture']['visibleHandle']
                    visible_hinge |= record['capture']['visibleHinge']
                    check('Supplementary native view preserves its exact attributed source component',
                          debug('v052ArchitectureTarget', cleabs)['component'] == actual_source['component'])
                    if visible_handle and visible_hinge:
                        break
            if portal is None:
                choices = debug('v050CityInteriorInfo')['doors']
                for candidate in choices[:12]:
                    cleabs = candidate['building'].split(':', 1)[0]
                    acquired = sources_by_cleabs.get(cleabs)
                    if acquired is None:
                        continue
                    actual_source = debug('v052ArchitectureTarget', cleabs)
                    if not actual_source or actual_source['rawGeometry'] != acquired['feature']['geometry']:
                        continue
                    approach = debug('v020Approach', candidate['id'])
                    if not approach:
                        continue
                    player = debug('getState')['player']
                    ground = debug('v046Height', *debug('v046LL'))
                    p = [player['pos'][0], ground['height'] + 1.65, player['pos'][2]] if finite(ground['height']) else None
                    if p is None or debug('v020Collides', p):
                        continue
                    debug('v018CaptureAt', p, player['yaw'], 0)
                    label = page.locator('#interactLabel').inner_text()
                    if 'entrer' not in label.lower():
                        continue
                    entry_state = debug('getState')
                    page.keyboard.press('e')
                    page.wait_for_timeout(150)
                    active = debug('v050CityInteriorInfo')['active']
                    if active is None:
                        continue
                    portal = {'portal': candidate, 'acquiredSource': acquired, 'actualSourceBefore': actual_source,
                              'approach': approach, 'visibleLabel': label, 'actualKeyboardAction': 'e', 'active': active}
                    report['portal'] = portal
                    check('A real attributed source building is entered through its physical E-key portal', active['id'] == candidate['building'])
                    return_point = debug('getState')['v050City']['returnPoint']
                    shot('06_real_portal_interior', 'Actual keyboard E entry into an acquired building footprint; room plan and furniture remain invented')
                    landing = next(i for i in debug('v020Stats')['interactables'] if i['id'] == 'city-interior-landing')
                    layout = debug('v052CityInteriorLayout')
                    landing_pos = [landing['pos'][0], layout['elevation'] + 1.65, landing['pos'][2]]
                    check('The actual landing is physically clear before the keyboard exit interaction', not debug('v020Collides', landing_pos))
                    debug('v018CaptureAt', landing_pos, 0, 0)
                    check('Visible interaction identifies the true interior landing', 'palier' in page.locator('#interactLabel').inner_text().lower())
                    page.keyboard.press('e')
                    page.get_by_role('button', name='Sortir vers la rue', exact=True).click()
                    ready()
                    page.wait_for_function('__MISTRAL_DEBUG.v050CityInteriorInfo().active===null && !__MISTRAL_DEBUG.v050CityInteriorInfo().exitPending')
                    returned = debug('getState')
                    check('The real return preserves exact street coordinates and inventory',
                          math.dist(returned['player']['pos'], return_point['pos']) < .2
                          and returned['inventory'] == entry_state['inventory'])
                    portal['returnedPosition'] = returned['player']['pos']
                    break
            save()
        check('All five distinct acquired IGN profiles were inspected natively', {c['role'] for c in report['cases']} == set(ROLES))
        check('Several source profiles have collision/LOS checked raw close views', len(visible_roles) >= 3, sorted(visible_roles))
        check('Native emitted buffers confirm a raised handle front and actual shutter hinge geometry', raised_handle and hinge_seen)
        check('Raw close captures contain currently rendered raised entry joinery and persienne hardware', visible_handle and visible_hinge)
        check('At least one genuine acquired building portal was entered and returned through actual UI', portal is not None)
        check('No global JavaScript exception occurred', not report['page_errors'], report['page_errors'])
        check('No installed source HTTP request failed', not report['local_http_errors'], report['local_http_errors'])
        local_failed = [r for r in report['request_failures'] if r['url'].startswith(origin + '/data/map_pack/')]
        check('No installed geographic request failed before an HTTP response', not local_failed, local_failed)
        check('No geography or interior transaction error was recorded', not debug('v051CityInfo')['errors'] and not debug('v050GeographyInfo')['errors'] and not debug('v050CityInteriorInfo')['errors'])
        stage('complete')
    except Exception:
        report['exception'] = traceback.format_exc()
        print(report['exception'], flush=True)
        if not report['checks'] or report['checks'][-1]['ok']:
            report['checks'].append({'name': 'Native hardware pilot completes', 'ok': False, 'detail': report['exception']})
        if page is not None:
            try:
                page.screenshot(path=str(args.output / 'FAILURE.png'))
            except Exception as error:
                report['failure_capture_error'] = str(error)
    finally:
        for name, value in (('context', context), ('browser', browser), ('playwright', pw)):
            if value is not None:
                try:
                    value.stop() if name == 'playwright' else value.close()
                except Exception as error:
                    report['cleanup_errors'].append({'owner': name, 'error': str(error)})
        if server is not None:
            server.shutdown()
            server.server_close()
        if worker is not None:
            worker.join(timeout=5)
            report['server_thread_stopped'] = not worker.is_alive()
        changed = [p for p, digest in frozen.items() if not (ROOT / p).is_file() or sha((ROOT / p).read_bytes()) != digest]
        report['frozen_inputs_changed'] = changed
        if changed:
            report['checks'].append({'name': 'Frozen production and source inputs remain unchanged', 'ok': False, 'detail': changed})
        else:
            report['checks'].append({'name': 'Frozen production and source inputs remain unchanged', 'ok': True})
        report['checks'].append({'name': 'Only one native context was used and owned resources were closed',
                                 'ok': report['contexts_created'] == 1 and not report['cleanup_errors'] and report.get('server_thread_stopped', False),
                                 'detail': report['cleanup_errors']})
        save()
    print(json.dumps({k: report[k] for k in ('stage', 'passed', 'failed', 'total', 'elapsed_seconds')}, ensure_ascii=False))
    return int(report['stage'] != 'complete' or report['failed'] > 0)


if __name__ == '__main__':
    raise SystemExit(main())
