#!/usr/bin/env python3
"""Prepared native HTTP architecture pilot. No browser starts without --run.

Uses the unchanged production HTML, GameHandler, installed source geometry and
native browser storage. One fresh context is reused through a document reload.
Existing diagnostic sector loading, measured placement, render/simulation freeze
and collision-controlled walking are declared assistance. Portal and landing
actions use real E key presses and visible buttons. This is not a human or an
unassisted citywide playthrough. No synthetic documentary plan is installed.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import html
import json
import math
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
CURVED = {'sourceId': 'batiment.9375075', 'cleabs': 'BATIMENT0000000258034734',
          'chunkPath': 'data/map_pack/city/m13055-r01-c12-c869798b17b6560c.json'}
CITY = 'geo_marseille_commune'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def area(ring):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1]))) / 2


def net_area(rings):
    return area(rings[0]) - sum(area(r) for r in rings[1:])


def source_anchor(geometry):
    polygon = geometry['coordinates'][0] if geometry['type'] == 'MultiPolygon' else geometry['coordinates']
    ring = polygon[0]
    return [(min(p[1] for p in ring) + max(p[1] for p in ring)) / 2,
            (min(p[0] for p in ring) + max(p[0] for p in ring)) / 2]


def point_in_ring(ring, point):
    x, z = point
    inside = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > z) != (b[1] > z) and x < (b[0] - a[0]) * (z - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def room_wall_coverage(room, walls):
    """Union of actual collinear wall intervals on all sides of a room."""
    ring = room['ring']
    covered, perimeter = 0.0, 0.0
    for a, b in zip(ring, ring[1:] + ring[:1]):
        length = math.dist(a, b)
        if length < 1e-8:
            continue
        perimeter += length
        tangent = [(b[0] - a[0]) / length, (b[1] - a[1]) / length]
        intervals = []
        for wall in walls:
            ends = [wall['a'], wall['b']]
            gaps = [abs((p[0] - a[0]) * tangent[1] - (p[1] - a[1]) * tangent[0]) for p in ends]
            if max(gaps) > 1e-5:
                continue
            at = sorted((p[0] - a[0]) * tangent[0] + (p[1] - a[1]) * tangent[1] for p in ends)
            lo, hi = max(0, at[0]), min(length, at[1])
            if hi > lo:
                intervals.append([lo, hi])
        cursor = 0
        for lo, hi in sorted(intervals):
            covered += max(0, hi - max(cursor, lo))
            cursor = max(cursor, hi)
    return {'perimeter': perimeter, 'covered': covered, 'unwalled': perimeter - covered,
            'expectedDoorWidth': room['door']['width']}


def write_layout_artifacts(output, report, report_path):
    """Render an engineering plan from the read-only native layout, never a screenshot edit."""
    interior = report.get('interior')
    if not interior or not interior.get('layout'):
        return
    layout = interior['layout']
    source_target = interior['chosen']['sourceTarget']
    record = {
        'title': 'Pièces inventées, contour source métrique',
        'scope': 'Read-only actual native runtime layout of a source building; invented rooms, doors, landing and furniture.',
        'nativeReportSha256': sha(Path(report_path).read_bytes()),
        'htmlSha256': report['html_sha256'], 'executedScriptSha256': report['script_sha256'],
        'buildingId': interior['initial']['id'], 'level': layout['level'],
        'frame': 'building-local-metre; X right and Z down in this plan',
        'sourceTarget': source_target,
        'actualLayout': layout,
        'assistedDoorCrossing': interior.get('assistedDoorCrossing'),
        'limitations': [
            'The source footprint is metric geographic data, not a measured room or facade survey.',
            'Room partitions, doorways, furniture and landing are invented; their actual runtime coordinates are retained unchanged.',
            'The red movement trace uses manually stepped production physics and diagnostic placement; it is not human walking.',
            'The connectivity summary is a bounded sampled computation, not an exhaustive proof over a continuous floor.',
        ],
    }
    raw = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode()
    (output / 'ACTUAL_LAYOUT_READONLY.json').write_bytes(raw)
    rings = layout['rings']
    min_x, max_x = min(p[0] for r in rings for p in r), max(p[0] for r in rings for p in r)
    min_z, max_z = min(p[1] for r in rings for p in r), max(p[1] for r in rings for p in r)
    scale = min(720 / max(max_x - min_x, .01), 585 / max(max_z - min_z, .01))
    offset_x, offset_z = 55 + (720 - (max_x - min_x) * scale) / 2, 125

    def xy(point):
        return offset_x + (point[0] - min_x) * scale, offset_z + (point[1] - min_z) * scale

    def points(ring):
        return ' '.join(f'{x:.4f},{y:.4f}' for x, y in map(xy, ring))

    def text(x, y, value, size=14, color='#23323b', weight='normal'):
        return f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(value))}</text>'

    def line(a, b, color, width, dash=''):
        x1, y1 = xy(a); x2, y2 = xy(b)
        return f'<line x1="{x1:.4f}" y1="{y1:.4f}" x2="{x2:.4f}" y2="{y2:.4f}" stroke="{color}" stroke-width="{width:.4f}" stroke-dasharray="{dash}"/>'

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850" role="img" aria-labelledby="title description">',
           '<title id="title">Pièces inventées, contour source métrique</title>',
           '<desc id="description">Plan d’audit des véritables coordonnées du layout natif : emprise source, pièces et mobilier inventés, portes et trajet physique assisté.</desc>',
           '<rect width="1200" height="850" fill="#fbfcfc"/>',
           '<g font-family="sans-serif">',
           text(40, 38, 'Pièces inventées, contour source métrique', 24, weight='bold'),
           text(40, 65, interior['initial']['id'] + ' · niveau ' + str(layout['level']), 14),
           text(40, 89, 'Vue de contrôle issue du navigateur natif · unités : mètres · aucune photographie ou façade mesurée', 13)]
    path = ' '.join('M ' + ' L '.join(f'{x:.4f},{y:.4f}' for x, y in map(xy, ring)) + ' Z' for ring in rings)
    svg.append(f'<path d="{path}" fill="#eef1f1" fill-rule="evenodd" stroke="#263f49" stroke-width="2.4"/>')
    for index, room in enumerate(layout['rooms'], 1):
        svg.append(f'<polygon points="{points(room["ring"])}" fill="#dceaf3" stroke="#819dad" stroke-width="1" stroke-dasharray="4 3"/>')
        ring = room['ring'][:-1] if room['ring'][0] == room['ring'][-1] else room['ring']
        x, y = xy([sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)])
        svg.append(text(x - 5, y, index, 17, '#335d76', 'bold'))
    for wall in layout['walls']:
        svg.append(line(wall['a'], wall['b'], '#34444c', max(2, wall['thickness'] * scale)))
    for door in layout.get('roomDoors', []):
        normal = [door['inside'][0] - door['outside'][0], door['inside'][1] - door['outside'][1]]
        length = math.hypot(*normal)
        tangent = [-normal[1] / length, normal[0] / length]
        a = [door['center'][0] - tangent[0] * door['width'] / 2, door['center'][1] - tangent[1] * door['width'] / 2]
        b = [door['center'][0] + tangent[0] * door['width'] / 2, door['center'][1] + tangent[1] * door['width'] / 2]
        svg.append(line(a, b, '#228658', 3))
    for index, furniture in enumerate(layout['furniture'], 1):
        svg.append(f'<polygon points="{points(furniture["ring"])}" fill="#d2b58c" stroke="#80613d" stroke-width="1.3"/>')
        x, y = xy(furniture['pos'])
        svg.append(text(x - 9, y + 3, 'F' + str(index), 10, '#4d3924', 'bold'))
        x, y = xy(furniture['approach'])
        svg.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="3.2" fill="#228658"/>')
    x, y = xy(layout['entry'])
    svg.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="7" fill="#7d59a0"/>')
    svg.append(text(x + 10, y + 5, 'P', 14, '#67417f', 'bold'))
    crossing = interior.get('assistedDoorCrossing')
    if crossing:
        trace = [[crossing['from'][0], crossing['from'][2]]] + [[p[0], p[2]] for p in crossing['positions']]
        svg.append(f'<polyline points="{points(trace)}" fill="none" stroke="#ba3e45" stroke-width="3"/>')
    legend_x, legend_y = 820, 128
    svg.extend([text(legend_x, legend_y, 'Lecture du plan', 19, weight='bold'),
                text(legend_x, legend_y + 29, 'Contour : emprise géographique source', 13),
                text(legend_x, legend_y + 52, 'Murs sombres : cloisons inventées', 13),
                text(legend_x, legend_y + 75, 'Vert : ouvertures de 1,20 m / accès libre', 13),
                text(legend_x, legend_y + 98, 'P : palier et entrée inventés', 13),
                text(legend_x, legend_y + 121, 'Rouge : franchissement physique assisté', 13)])
    y = legend_y + 160
    for index, room in enumerate(layout['rooms'], 1):
        svg.append(text(legend_x, y, f'{index}. {room["use"]} — inventé', 13)); y += 23
    y += 16
    for index, furniture in enumerate(layout['furniture'], 1):
        svg.append(text(legend_x, y, f'F{index}. {furniture["label"]}', 12)); y += 22
    navigation = layout['programCoverage']['navigation']
    svg.extend([text(40, 755, f'Emprise : {net_area(rings):.2f} m² · {len(layout["rooms"])} pièces fermées inventées · {len(layout["furniture"])} meubles solides inventés', 14),
                text(40, 779, f'Navigation échantillonnée : {navigation["sampledCells"]} cellules · nouvelles cellules inaccessibles : {navigation["newUnreachableCells"]}', 13),
                text(40, 805, 'Ce plan décrit le monde généré ; il ne certifie pas le plan réel du bâtiment. Placements et marche assistés déclarés dans le rapport.', 12),
                f'<line x1="55" y1="718" x2="{55 + 2 * scale:.4f}" y2="718" stroke="#263f49" stroke-width="3"/>',
                text(55, 739, '0', 11), text(55 + 2 * scale - 8, 739, '2 m', 11),
                '</g>', '<metadata>' + html.escape(json.dumps({'layoutJsonSha256': sha(raw), 'layoutSignature': layout['signature'],
                                                               'nativeReportSha256': record['nativeReportSha256'], 'htmlSha256': report['html_sha256']}, ensure_ascii=False)) + '</metadata>', '</svg>'])
    (output / 'ACTUAL_LAYOUT_AUDIT.svg').write_text('\n'.join(svg) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Run the native pilot against the frozen HTML and atlas SHA values.')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    parser.add_argument('--expect-architecture-sha', required=True)
    parser.add_argument('--ready-timeout', type=int, default=300)
    args = parser.parse_args()
    if not args.run:
        print('Prepared only. No server or browser started. Pass --run with the coordinated HTML and atlas SHA values.')
        return 0
    sys.path.insert(0, str(ROOT / 'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright

    started = time.monotonic()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {'scope': __doc__, 'stage': 'preflight', 'checks': [], 'shots': [], 'stages': [],
              'native_navigation': False, 'html_injected': False, 'network_mocked': False,
              'storage_mocked': False, 'synthetic_geography': False, 'synthetic_documents': False,
              'service_workers_disabled': True, 'contexts_created': 0, 'maximum_contexts': 1,
              'assistance': [
                  'Existing native macro and sector loading debug APIs; no lab or geography fixture.',
                  'Existing measured collision-free camera placement and QA simulation/render freeze.',
                  'Existing v020Approach for collision/LOS checked placement before real E-key portal actions.',
                  'Native KeyW plus existing v020Tick advances production movement/collisions in fixed 0.05 s steps under QA freeze; this is assisted movement, not recorded human walking.',
                  'Landing placement on a verified clear floor precedes real E-key and visible floor/exit buttons.',
                  'Read-only debug exports inspect actual runtime annotations, geometry and interior layout.',
              ],
              'page_errors': [], 'console_errors': [], 'javascript_console_errors': [], 'resource_console_diagnostics': [],
              'request_failures': [], 'local_geographic_request_failures': [], 'external_request_failures': [],
              'local_http_errors': [], 'http_responses': [], 'labels': [], 'interior_attempts': [],
              'script_sha256': sha(Path(__file__).read_bytes())}
    frozen, original_chunks = {}, {}
    page = server = worker = browser = context = None
    origin = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']), total=len(report['checks']))
        (args.output / 'ARCHITECTURE_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def check(name, ok, detail=None, required=True):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ') + name, flush=True)
        save()
        if required and not ok:
            raise AssertionError(name)

    def stage(name):
        report['stage'] = name
        report['stages'].append({'name': name, 'elapsed_seconds': round(time.monotonic() - started, 3)})
        print('STAGE ' + name, flush=True)
        save()

    def pin(relative):
        path = ROOT / relative
        raw = path.read_bytes()
        if relative in frozen and frozen[relative] != sha(raw):
            raise AssertionError('Input changed during QA: ' + relative)
        frozen[relative] = sha(raw)
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def shot(name, label):
        path = args.output / (name + '.png')
        player = debug('getState')['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])
        page.screenshot(path=str(path))
        report['shots'].append({'file': path.name, 'label': label, 'sha256': sha(path.read_bytes()),
                                'method': 'Actual WebGL render after declared diagnostic placement/freeze.'})
        save()

    def ready():
        deadline, last_print = time.monotonic() + args.ready_timeout, 0
        while time.monotonic() < deadline:
            info = debug('v047Info')
            if info['phase'] == 'failed':
                raise RuntimeError('Production geographic staging failed: ' + json.dumps(debug('v046Info')))
            if info['tiles'] > 0 and not info['loading'] and not info['anticipating']:
                return info
            if time.monotonic() - last_print > 15:
                print('LOAD ' + json.dumps({k: info[k] for k in ('phase', 'done', 'total', 'tiles')}), flush=True)
                last_print = time.monotonic()
            page.wait_for_timeout(250)
        report['readiness_failure'] = {'map': debug('v047Info'), 'city': debug('v051CityInfo')}
        raise TimeoutError('Production geography did not become ready within the bounded timeout')

    def native_document(response):
        check('Native HTTP document equals frozen production bytes', response is not None and response.status == 200
              and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("['v051CityReady','v052ArchitectureReady','v052ArchitectureTarget','v052CityInteriorLayout','v050FacadePage','v050FacadeOpeningSpans'].every(k=>typeof __MISTRAL_DEBUG[k]==='function')")
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})

    def camera_near(lat, lon):
        points = [[lat + dz / 111320, lon + dx / (111320 * math.cos(math.radians(lat)))]
                  for dz in range(-100, 101, 10) for dx in range(-100, 101, 10)]
        clear = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,height:h.height,sources:h.sources,clear:Number.isFinite(h.height)&&!h.missing&&!d.v046Collide(p[0],p[2])};}).filter(p=>p.clear);} """, points)
        if not clear:
            raise AssertionError('No measured collision-free camera point near ' + str([lat, lon]))
        clear.sort(key=lambda p: math.hypot(p['ll'][0] - lat, (p['ll'][1] - lon) * math.cos(math.radians(lat))))
        point = clear[0]
        debug('v018CaptureAt', [point['p'][0], point['height'] + 1.65, point['p'][2]], 0, -.12)
        debug('v050FacadeRefresh')
        debug('v050CityInteriorBind')
        return point

    def sector(lat, lon):
        check('Requested real sector loads successfully', debug('v046Load', lat, lon) is True, [lat, lon])
        ready()
        return camera_near(lat, lon)

    def physical_interaction(interaction_id, expected_label):
        approach = debug('v020Approach', interaction_id)
        if not approach:
            return None
        player = debug('getState')['player']
        if interaction_id.startswith('city-door:'):
            ll = debug('v046LL')
            ground = debug('v046Height', *ll)
            if not finite(ground['height']):
                return None
            position = [player['pos'][0], ground['height'] + 1.65, player['pos'][2]]
            if debug('v020Collides', position):
                return None
            debug('v018CaptureAt', position, player['yaw'], 0)
        else:
            debug('v018CaptureAt', player['pos'], player['yaw'], 0)
        label = page.locator('#interactLabel').inner_text()
        if expected_label.casefold() not in label.casefold():
            return None
        record = {'interaction': interaction_id, 'helper': 'v020Approach', 'label': label,
                  'position': debug('getState')['player']['pos'], 'actualKeyboardAction': 'e'}
        page.keyboard.press('e')
        return record

    def landing():
        interaction = next((i for i in debug('v020Stats')['interactables'] if i['id'] == 'city-interior-landing'), None)
        check('Actual interior exposes a landing interaction', interaction is not None)
        layout = debug('v052CityInteriorLayout')
        position = [interaction['pos'][0], layout['elevation'] + 1.65, interaction['pos'][2]]
        check('Diagnostic landing placement is clear of production colliders', not debug('v020Collides', position), position)
        debug('v018CaptureAt', position, 0, 0)
        check('Visible interaction identifies the actual landing', 'palier' in page.locator('#interactLabel').inner_text().lower())
        page.keyboard.press('e')
        page.locator('#dialogue').wait_for(state='visible')

    def go_floor(target):
        current = debug('v050CityInteriorInfo')['active']['floor']
        check('Floor transition requested through adjacent physical landing', abs(target - current) == 1, {'from': current, 'to': target})
        landing()
        text = ('Monter au niveau ' if target > current else 'Descendre au niveau ') + str(target)
        page.get_by_role('button', name=text, exact=True).click()
        page.wait_for_function('n=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.floor===n', arg=target)
        check('Actual landing dialog closes after floor change', page.locator('#dialogue').is_hidden())

    def exit_to_street():
        landing()
        page.get_by_role('button', name='Sortir vers la rue', exact=True).click()
        ready()
        page.wait_for_function('!__MISTRAL_DEBUG.v050CityInteriorInfo().exitPending && __MISTRAL_DEBUG.v050CityInteriorInfo().active===null', timeout=120000)

    def furniture_view(layout):
        """Choose a real clear doorway/landing view; inspect production LOS only."""
        candidates = [('outside-room-door:' + d['roomId'], d['outside']) for d in layout['roomDoors']]
        candidates.append(('landing', layout['entry']))
        best = None
        for anchor, point in candidates:
            position = [point[0], layout['elevation'] + 1.65, point[1]]
            if debug('v020Collides', position):
                continue
            visible = []
            for furniture in layout['furniture']:
                dx, dz = furniture['pos'][0] - point[0], furniture['pos'][1] - point[1]
                distance = math.hypot(dx, dz)
                aim = [furniture['pos'][0], layout['elevation'] + furniture['height'] + .1, furniture['pos'][1]]
                if 1.1 < distance < 16 and debug('v020LOS', position, aim):
                    visible.append({'id': furniture['id'], 'kind': furniture['kind'], 'pos': furniture['pos'],
                                    'yaw': math.atan2(dx, -dz), 'distance': distance, 'openSpace': furniture['roomId'] is None})
            for target in visible:
                framed = [f for f in visible if abs(math.atan2(math.sin(f['yaw'] - target['yaw']), math.cos(f['yaw'] - target['yaw']))) < .62]
                score = len(framed) * 100 + sum(f['openSpace'] for f in framed) * 10 - sum(f['distance'] for f in framed)
                if best is None or score > best['score']:
                    best = {'anchor': anchor, 'position': position, 'yaw': target['yaw'], 'pitch': -.27,
                            'score': score, 'visibleFurniture': framed,
                            'method': 'Diagnostic camera on a production collision-free doorway/landing point; furniture LOS checked, no scene or image modification.'}
        if best:
            debug('v018CaptureAt', best['position'], best['yaw'], best['pitch'])
        return best

    try:
        html = pin('index.html')
        check('Coordinated production HTML is installed', sha(html) == args.expect_html_sha, sha(html))
        atlas_raw = pin('data/map_pack/architecture/index.json')
        check('Coordinated architectural atlas is installed', sha(atlas_raw) == args.expect_architecture_sha, sha(atlas_raw))
        for relative in ['src/v050/06_architecture_sources.js', 'src/v050/07_facades.js', 'src/v050/08_city_interiors.js']:
            raw = pin(relative)
            check('Production HTML includes the current source: ' + relative, raw.decode() in html.decode())
        city_index = json.loads(pin('data/map_pack/city/index.json'))
        for relative in ['data/map_pack/city/terrain-index.json', 'data/map_pack/city/water-index.json',
                         city_index['municipality']['boundary']['path']]:
            pin(relative)
        atlas = json.loads(atlas_raw)
        check('Official site atlas has exactly 12 distinct attributed targets', len(atlas['records']) == 12
              and len({r['target']['cleabs'] for r in atlas['records']}) == 12)
        expected = {}
        for row in atlas['records']:
            cleabs = row['target']['cleabs']
            desc = row['associationEvidence']['buildingSource']
            if desc['chunkPath'] not in original_chunks:
                raw = pin(desc['chunkPath'])
                check('Source building partition matches its acquisition SHA', sha(raw) == desc['chunkSha256'], desc['chunkPath'])
                original_chunks[desc['chunkPath']] = {f['properties'].get('cleabs'): f for f in json.loads(raw)['features']}
            source_feature = original_chunks[desc['chunkPath']][cleabs]
            label, source = row['label'], row['source']
            check('Installed context retains the exact immutable footprint and attributed prudent label: ' + cleabs,
                  row['target']['rawGeometry'] == source_feature['geometry'] and desc['indexSha256'] == frozen['data/map_pack/city/index.json']
                  and label['kind'] == 'site-context' and label['geometryFictive'] is False and label['precisionMeters'] <= 3
                  and label['buildingOverlapRatio'] >= .99 and label['centroidInside'] is True
                  and label['text'].startswith('Bâtiment ') and source['url'].startswith('https://data.geopf.fr/')
                  and len(source['responseSha256']) == 64 and source['license'] == 'Licence Ouverte 2.0'
                  and bool(source['attribution']) and not row.get('facadeDocument') and not row.get('interiorDocument'))
            expected[cleabs] = {'cleabs': cleabs, 'sourceId': source_feature['properties']['sourceId'],
                                'geometry': source_feature['geometry'], 'sourceBuilding': desc,
                                'siteName': label['siteName'], 'label': label['text'],
                                'source': {'responseSha256': source['responseSha256']},
                                'geometryCanonicalSha256': sha(json.dumps(source_feature['geometry'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())}
        curved_raw = pin(CURVED['chunkPath'])
        curved_source = next(f for f in json.loads(curved_raw)['features'] if f['properties']['sourceId'] == CURVED['sourceId'])
        report['source_snapshot'] = dict(frozen)
        report['html_sha256'] = sha(html)
        report['architecture_sha256'] = sha(atlas_raw)

        class Handler(GameHandler):
            def log_message(self, *_arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin + '/index.html?skipboot'
        stage('actual_server_audit')
        with urllib.request.urlopen(origin + '/__mistral/city-sources', timeout=180) as response:
            audit = json.load(response)
            cache_control = response.headers.get('Cache-Control')
        report['server_audit'] = audit
        check('Actual GameHandler audits the installed municipal sources', cache_control == 'no-store' and audit['ok']
              and audit['indexSha256'] == frozen['data/map_pack/city/index.json'] and audit['totalBuildings'] == 291001)
        # The production menu requests this existing route with a bounded client
        # timeout. Complete the same real disk audit before browser startup so
        # concurrent source parsing does not turn its first inspection into an
        # unrelated metadata timeout. No response is substituted or fabricated.
        with urllib.request.urlopen(origin + '/__mistral/local-data', timeout=300) as response:
            local_audit = json.load(response)
            local_cache_control = response.headers.get('Cache-Control')
        report['local_pack_audit'] = local_audit
        check('Actual local-pack audit is complete before native menu probes',
              local_cache_control == 'no-store' and local_audit['complete'] is True)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                         args=['--no-sandbox', '--disable-dev-shm-usage'])
            report['browser_version'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
            report['contexts_created'] += 1
            page = context.new_page()
            page.set_default_timeout(30000)
            page.on('pageerror', lambda error: report['page_errors'].append(str(error)))

            def console_seen(message):
                if message.type != 'error':
                    return
                report['console_errors'].append(message.text)
                record = {'text': message.text, 'location': message.location}
                # Chromium emits this diagnostic for failed HTTP/tunnel loads;
                # it is not an uncaught JavaScript exception. Preserve it and
                # every request failure, while checking source traffic below.
                if message.text.startswith('Failed to load resource:'):
                    report['resource_console_diagnostics'].append(record)
                else:
                    report['javascript_console_errors'].append(record)

            page.on('console', console_seen)

            def geographic(url):
                parsed = urllib.parse.urlsplit(url)
                return url.startswith(origin + '/') and (parsed.path.startswith('/data/map_pack/') or parsed.path.startswith('/__mistral/'))

            def request_failed(request):
                record = {'url': request.url, 'failure': request.failure}
                report['request_failures'].append(record)
                if geographic(request.url):
                    report['local_geographic_request_failures'].append(record)
                elif not request.url.startswith(origin + '/'):
                    report['external_request_failures'].append(record)

            def response_seen(response):
                if response.url.startswith(origin + '/'):
                    record = {'url': response.url, 'status': response.status, 'from_service_worker': response.from_service_worker}
                    report['http_responses'].append(record)
                    if geographic(response.url) and response.status >= 400:
                        report['local_http_errors'].append(record)

            page.on('requestfailed', request_failed)
            page.on('response', response_seen)
            page.on('dialog', lambda dialog: dialog.accept())
            native_document(page.goto(report['url'], wait_until='load', timeout=60000))
            report['native_navigation'] = True
            debug('v051CityReady')
            debug('v052ArchitectureReady')
            architecture = debug('v052ArchitectureInfo')
            check('Runtime reads only real context labels, with zero asserted architectural plans', architecture['loaded']
                  and not architecture['missing'] and not architecture['error'] and architecture['records'] == architecture['siteLabels'] == 12
                  and architecture['facadeDocuments'] == architecture['interiorDocuments'] == 0, architecture)
            debug('v018LoadMacro', CITY)
            ready()
            check('Actual geographic world is outside the synthetic lab', debug('v046Info')['lab'] is False)

            groups = {}
            for row in expected.values():
                groups.setdefault(row['siteName'], []).append(row)
            for group_index, (site_name, rows) in enumerate(groups.items(), 1):
                stage('real_site_labels_' + str(group_index))
                lat, lon = source_anchor(rows[0]['geometry'])
                camera = sector(lat, lon)
                for expected_row in rows:
                    actual = debug('v052ArchitectureTarget', expected_row['cleabs'])
                    annotation = actual.get('annotation') if actual else None
                    label = annotation.get('architectureSite') if annotation else None
                    check('Runtime source geometry is intact: ' + expected_row['cleabs'], actual is not None
                          and actual['rawGeometry'] == expected_row['geometry'])
                    check('Actual scene carries the attributed site label: ' + expected_row['cleabs'],
                          annotation is not None and annotation['name'] == expected_row['label'] and label is not None
                          and label['text'] == expected_row['label'] and label['siteName'] == site_name
                          and label['kind'] == 'site-context' and label['geometryFictive'] is False
                          and label['source']['responseSha256'] == expected_row['source']['responseSha256']
                          and annotation.get('appliedSource') is not None, annotation)
                    report['labels'].append({'cleabs': expected_row['cleabs'], 'annotation': annotation,
                                             'geometryCanonicalSha256': expected_row['geometryCanonicalSha256']})
                report.setdefault('site_cameras', []).append({'site': site_name, 'camera': camera})
                shot('0' + str(group_index) + '_real_site_context', 'Real site geometry; names are context, procedural facades remain inventions.')
            architecture = debug('v052ArchitectureInfo')
            check('All 12 official site contexts are applied without geometry rejection', architecture['appliedRecords'] == 12 and not architecture['rejected'], architecture)

            stage('curved_source_facade')
            camera = sector(*source_anchor(curved_source['geometry']))
            target = debug('v052ArchitectureTarget', CURVED['sourceId'])
            check('Curved source building retains its complete original geometry', target is not None and target['rawGeometry'] == curved_source['geometry'])
            curved = debug('v050FacadeBuilding', CURVED['sourceId'])
            check('Dense segmented real outline receives actual rendered facade details', curved is not None and curved['rendered']
                  and not curved['ringsTruncated'] and curved['openingInventory']['curvedSurfaces'] >= 1
                  and any(o.get('surfaceId') and o.get('span', {}).get('segments', 0) > 1 for o in curved['openings']), curved)
            pages, openings, cursor = [], [], 0
            for _page_index in range(64):
                result = debug('v050FacadePage', CURVED['sourceId'], cursor, 128)
                check('Curved facade inventory page advances or terminates', result is not None and (result['done'] or result['nextCursor'] > cursor))
                pages.append({k: v for k, v in result.items() if k != 'openings'})
                openings.extend(result['openings'])
                cursor = result['nextCursor']
                if result['done']:
                    break
            check('Curved facade complete inventory finishes within the bounded pilot', bool(pages) and pages[-1]['done'])
            curved_doors = [d for d in debug('v050FacadeDoors') if d['buildingId'] == curved['id']]
            report['curved'] = {'source': CURVED, 'camera': camera, 'renderedFacade': curved,
                                'inventoryPages': pages, 'inventoryOpenings': openings, 'entranceCandidates': curved_doors}
            check('Curved openings declare source-segment spans without changing metric bounds',
                  bool(openings) and any(o.get('surfaceId') for o in openings)
                  and all(o['width'] > 0 and o['height'] > 0 and o['bottom'] >= 0 and o['bottom'] + o['height'] <= curved['height'] + 1e-6
                          and (not o.get('surfaceId') or o['span']['widthMeters'] == o['width'] and o['span']['segments'] >= 1)
                          for o in openings))
            fragments = []
            for opening in openings:
                spans = debug('v050FacadeOpeningSpans', CURVED['sourceId'], opening)
                valid = bool(spans) and abs(sum(s['width'] for s in spans) - opening['width']) < 1e-6
                for span in spans:
                    ring = curved['rings'][span['ringIndex']]
                    a, b = ring[span['edgeIndex']], ring[(span['edgeIndex'] + 1) % len(ring)]
                    valid = valid and span['offset'] >= -1e-7 and span['width'] > 0 and span['offset'] + span['width'] <= math.dist(a, b) + 1e-6
                fragments.append({'opening': opening, 'sourceSpans': spans, 'valid': bool(valid)})
            report['curved']['sourceOpeningSpans'] = fragments
            check('Every curved bay follows bounded intervals on the unchanged individual source edges',
                  all(f['valid'] for f in fragments) and any(len(f['sourceSpans']) > 1 for f in fragments), fragments)
            eligible_curved = [d for d in debug('v050CityInteriorInfo')['doors'] if d['building'] == curved['id']]
            report['curved']['accessiblePortals'] = eligible_curved
            if eligible_curved:
                approach = physical_interaction(eligible_curved[0]['id'], 'Entrer')
                check('Accessible curved source building enters through actual E-key portal', approach is not None and debug('v050CityInteriorInfo')['active'] is not None)
                report['curved']['entry'] = {'approach': approach, 'active': debug('v050CityInteriorInfo')['active']}
                shot('03_curved_source_interior', 'Real curved source footprint; invented arrangement, assisted E-key entrance.')
                exit_to_street()
            else:
                report['curved']['entry'] = {'status': 'not_physically_eligible_in_this_sector',
                                           'rejections': debug('v050CityInteriorInfo')['rejections'],
                                           'claim': 'Rendered facade verified; no accessible entry claimed.'}
                shot('03_curved_source_facade', 'Real curved source outline and rendered invented facade; access eligibility reported separately.')

            stage('enclosed_rooms_and_furnishing')
            sector(43.362, 5.312)
            candidates = []
            for door in debug('v050CityInteriorInfo')['doors']:
                if 2 <= door['levels'] <= 8:
                    target = debug('v052ArchitectureTarget', door['building'])
                    if target:
                        footprint_area = net_area(target['component']['rings'])
                        if 45 <= footprint_area <= 350:
                            candidates.append((abs(footprint_area - 110), door, target))
            check('Real sector provides a suitably sized multi-storey source portal', bool(candidates))
            chosen = initial = layout = None
            for _score, door, target in sorted(candidates, key=lambda c: (c[0], c[1]['id']))[:8]:
                approach = physical_interaction(door['id'], 'Entrer')
                if not approach or not debug('v050CityInteriorInfo')['active']:
                    report['interior_attempts'].append({'portal': door, 'entered': False})
                    continue
                info, candidate_layout = debug('v050CityInteriorInfo'), debug('v052CityInteriorLayout')
                suitable = len(candidate_layout['rooms']) >= 1 and len(candidate_layout['furniture']) >= 2
                report['interior_attempts'].append({'portal': door, 'entered': True, 'suitable': suitable,
                                                    'rooms': len(candidate_layout['rooms']), 'furniture': len(candidate_layout['furniture']),
                                                    'programCoverage': candidate_layout.get('programCoverage')})
                if suitable:
                    chosen, initial, layout = {'portal': door, 'sourceTarget': target, 'approach': approach}, info['active'], candidate_layout
                    break
                exit_to_street()
            check('A real entered building contains enclosed invented rooms and furnished uses', chosen is not None)
            state = debug('getState')
            building = state['v050City']['active']['building']
            return_point = state['v050City']['returnPoint']
            report['interior'] = {'chosen': chosen, 'initial': initial, 'layout': layout, 'returnPoint': return_point}
            check('Entered plan preserves the source-derived local outline and honest invented provenance',
                  layout['rings'] == building['rings'] and layout['layoutVersion'] == 2 and layout['provenance'] == 'invented'
                  and initial['layoutProvenance'] == 'invented' and not initial['documentSource'] and not initial['documentedLevels'])
            coverage = [dict(roomId=r['id'], **room_wall_coverage(r, layout['walls'])) for r in layout['rooms']]
            report['interior']['roomWallCoverage'] = coverage
            check('Actual room partitions enclose every side except the stated 1.20 m door',
                  all(r['coverage'] == 'enclosed-room' and r['provenance'] == 'invented' and abs(r['door']['width'] - 1.2) < 1e-7 for r in layout['rooms'])
                  and all(abs(c['unwalled'] - c['expectedDoorWidth']) < 1e-4 for c in coverage), coverage)
            furnishing = initial['furnishing']
            check('Actual furniture has distinct rendered parts and one solid collider per object',
                  furnishing['objects'] == len(layout['furniture']) == furnishing['colliderFurniture']
                  and furnishing['renderFurniture'] > furnishing['objects'] and len(furnishing['byKind']) >= 2, furnishing)
            probes = []
            for furniture in layout['furniture']:
                center = [furniture['pos'][0], layout['elevation'] + 1.65, furniture['pos'][1]]
                approach = [furniture['approach'][0], layout['elevation'] + 1.65, furniture['approach'][1]]
                probes.append({'id': furniture['id'], 'kind': furniture['kind'], 'solidAtCenter': debug('v020Collides', center),
                               'approachClear': not debug('v020Collides', approach)})
            report['interior']['furnitureCollisionProbes'] = probes
            check('Production furniture colliders are solid while every reserved approach remains free', all(p['solidAtCenter'] and p['approachClear'] for p in probes), probes)
            geom = debug('v018Geometry')
            floor = next(g for g in geom if str(g.get('id', '')).startswith('city-floor:'))
            triangles = [[floor['vertices'][i] for i in face] for face in floor['faces']]
            triangle_area = sum(area([[p[0], p[2]] for p in tri]) for tri in triangles)
            partition_draws = [g for g in geom if str(g.get('id', '')).startswith('city-partition:')]
            check('Rendered floor and real partition prisms preserve metric source area',
                  abs(triangle_area - net_area(layout['rings'])) < 1e-4 and len(partition_draws) == len(layout['walls']),
                  {'sourceArea': net_area(layout['rings']), 'triangleArea': triangle_area, 'partitionPrisms': len(partition_draws)})
            navigation = layout['programCoverage']['navigation']
            check('Bounded circulation proof adds no unreachable source cells', navigation['newUnreachableCells'] == 0, navigation)

            room = layout['rooms'][0]
            door = room['door']
            outside = [door['outside'][0], layout['elevation'] + 1.65, door['outside'][1]]
            inside = [door['inside'][0], layout['elevation'] + 1.65, door['inside'][1]]
            check('Both physical anchors of the enclosed-room doorway are clear', not debug('v020Collides', outside) and not debug('v020Collides', inside))
            debug('v018CaptureAt', outside, math.atan2(inside[0] - outside[0], -(inside[2] - outside[2])), 0)
            positions = []
            page.keyboard.down('w')
            try:
                for _step in range(24):
                    debug('v020Tick', .05, True)
                    current = debug('getState')['player']['pos']
                    positions.append(current)
                    if math.hypot(current[0] - inside[0], current[2] - inside[2]) <= .2:
                        break
            finally:
                page.keyboard.up('w')
            actual_position = debug('getState')['player']['pos']
            report['interior']['assistedDoorCrossing'] = {'method': 'Native KeyW with manually stepped v020Tick(.05,true); production movement/collisions, not human walking',
                                                          'from': outside, 'requested': inside, 'stepSeconds': .05,
                                                          'positions': positions, 'actualPosition': actual_position}
            check('Production movement crosses the actual 1.20 m room doorway into its enclosed volume',
                  bool(positions) and math.hypot(actual_position[0] - outside[0], actual_position[2] - outside[2]) > .6
                  and math.hypot(actual_position[0] - inside[0], actual_position[2] - inside[2]) <= .3
                  and point_in_ring(room['ring'], [actual_position[0], actual_position[2]]), report['interior']['assistedDoorCrossing'])
            debug('v018CaptureAt', actual_position, math.atan2(outside[0] - actual_position[0], -(outside[2] - actual_position[2])), -.22)
            shot('04a_enclosed_room_doorway', 'Actual invented room doorway after collision-controlled crossing, looking back into the source-footprint common space.')
            report['interior']['furnitureView'] = furniture_view(layout)
            shot('04_enclosed_room_furniture', 'Actual clear doorway/landing camera towards multiple invented furnishings when visible; no scene or image modification.')

            street_floor, entry_signature = initial['streetFloor'], initial['signature']
            adjacent = street_floor + 1 if street_floor + 1 < initial['levels'] else street_floor - 1
            go_floor(adjacent)
            upper = debug('v050CityInteriorInfo')['active']
            upper_layout = debug('v052CityInteriorLayout')
            check('Visible landing UI loads another metric floor of the same source building', upper['id'] == initial['id']
                  and upper['floor'] == adjacent and upper['signature'] != entry_signature
                  and upper_layout['elevation'] != layout['elevation'])
            before_reload = debug('getState')
            key = debug('v018PersistentStatus')['key']
            saved = page.evaluate('key=>JSON.parse(localStorage.getItem(key))', key)
            check('Real browser localStorage retains the current floor and geographic return point', saved['v050City']['active']['floor'] == adjacent
                  and saved['v050City']['active']['building']['id'] == initial['id'] and saved['v050City']['returnPoint'] == return_point)
            report['interior']['adjacent'] = upper
            shot('05_adjacent_floor', 'Actual adjacent floor loaded by the visible landing controls.')

            stage('cold_document_continue')
            native_document(page.reload(wait_until='load', timeout=60000))
            page.locator('#btnContinue').click()
            page.wait_for_function('id=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.id===id', arg=initial['id'], timeout=120000)
            restored = debug('v050CityInteriorInfo')['active']
            check('Native Continue restores building, floor and deterministic room/furniture signature', restored['id'] == initial['id']
                  and restored['floor'] == adjacent and restored['streetFloor'] == street_floor and restored['signature'] == upper['signature'], restored)
            check('Native Continue preserves inventory and exact exterior return point', debug('getState')['inventory'] == before_reload['inventory']
                  and debug('getState')['v050City']['returnPoint'] == return_point)
            report['interior']['restored'] = restored
            shot('06_continue_same_floor', 'Same fresh-context native storage and a real document reload; no save injection.')
            go_floor(street_floor)
            check('Return to the street storey reconstructs the same full plan signature', debug('v050CityInteriorInfo')['active']['signature'] == entry_signature)
            exit_to_street()
            exterior = debug('getState')
            check('Real exit UI restores the exact saved street position and inventory',
                  math.dist(exterior['player']['pos'], return_point['pos']) < .2 and exterior['inventory'] == before_reload['inventory']
                  and exterior['v050City']['returnPoint'] is None and exterior['v050City']['active'] is None)
            report['interior']['returnedPosition'] = exterior['player']['pos']
            shot('07_return_real_street', 'Actual geographic return after native Continue and floor controls.')
            final_city, final_interiors = debug('v051CityInfo'), debug('v050CityInteriorInfo')
            report['final_city'], report['final_interiors'] = final_city, final_interiors
            check('Real source and interior transactions record no runtime exception', not final_city['errors'] and not final_interiors['errors'])
            check('No synthetic documentary plan entered native storage', final_interiors['documentRegistry']['entries'] == 0)
            report['network_scope'] = {
                'requiredSuccess': 'Installed /data/map_pack files and actual local /__mistral audit endpoints.',
                'externalServices': 'All external request failures and Chromium resource diagnostics are retained separately. This pilot does not certify reachability of remote services.',
            }
            check('All installed geographic-source and local-audit HTTP responses succeeded', not report['local_http_errors'], report['local_http_errors'])
            check('No installed geographic-source or local-audit request failed or was aborted',
                  not report['local_geographic_request_failures'], report['local_geographic_request_failures'])
            check('No global JavaScript exception or application console error occurred', not report['page_errors'] and not report['javascript_console_errors'],
                  {'pageErrors': report['page_errors'], 'applicationConsoleErrors': report['javascript_console_errors'],
                   'retainedResourceDiagnostics': report['resource_console_diagnostics']})
            check('Pilot used one browser context through a native document reload', report['contexts_created'] == 1)
            context.close()
            context = None
            browser.close()
            browser = None
        stage('complete')
    except Exception:
        report['exception'] = traceback.format_exc()
        print(report['exception'], flush=True)
        check('Native architecture pilot completes', False, report['exception'], required=False)
        if page is not None and not page.is_closed():
            try:
                shot('FAILURE', 'Actual UI at failure; no substituted fixture or synthetic image.')
            except Exception:
                pass
    finally:
        for resource in [context, browser]:
            if resource is not None:
                try:
                    resource.close()
                except Exception as error:
                    report.setdefault('cleanup_errors', []).append(str(error))
        if server is not None:
            server.shutdown()
            server.server_close()
        if worker is not None:
            worker.join(timeout=5)
        changed = [{'path': relative, 'beforeSha256': digest,
                    'afterSha256': sha((ROOT / relative).read_bytes()) if (ROOT / relative).is_file() else None}
                   for relative, digest in frozen.items()
                   if not (ROOT / relative).is_file() or sha((ROOT / relative).read_bytes()) != digest]
        check('Frozen HTML, sources, atlas, selected geographic chunks and city indices remain unchanged', not changed, changed, required=False)
        save()
        if report.get('interior', {}).get('layout'):
            report['layout_artifacts'] = {'json': 'ACTUAL_LAYOUT_READONLY.json', 'svg': 'ACTUAL_LAYOUT_AUDIT.svg'}
            save()
            try:
                write_layout_artifacts(args.output, report, args.output / 'ARCHITECTURE_NATIVE.json')
            except Exception:
                check('Read-only native layout audit artifacts are generated', False, traceback.format_exc(), required=False)
    print(json.dumps({key: report[key] for key in ('passed', 'failed', 'total', 'stage')}, ensure_ascii=False), flush=True)
    return int(bool(report['failed'] or report['page_errors'] or report['stage'] != 'complete'))


if __name__ == '__main__':
    raise SystemExit(main())
