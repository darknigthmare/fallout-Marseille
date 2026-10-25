#!/usr/bin/env python3
"""Bounded assisted native bestiary pilot; no browser starts without --run.

Unmodified production HTML, actual GameHandler, installed map pack and native
storage. Existing sector selection, measured camera placement, daytime and
simulation/render freeze are diagnostic assistance. Public debug APIs inspect
actual streamed actors and step production physics. No actor, reward, HTML,
terrain, document or save fixture is injected. This is not a human playthrough.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import math
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
MODULE = 'src/v050/13_regional_bestiary.js'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


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
    parser.add_argument('--expect-bestiary-sha', required=True)
    parser.add_argument('--expect-architecture-sha', required=True)
    parser.add_argument('--ready-timeout', type=int, default=300)
    parser.add_argument('--maximum-sectors', type=int, default=6)
    args = parser.parse_args()
    if not args.run:
        print('Prepared only. No server or browser started. Coordinate frozen SHAs and pass --run.')
        return 0

    sys.path.insert(0, str(ROOT / 'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright

    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {'scope': __doc__, 'stage': 'preflight', 'checks': [], 'shots': [], 'placements': [],
              'attempts': [], 'native_navigation': False, 'html_injected': False,
              'network_mocked': False, 'storage_mocked': False, 'synthetic_actors': False,
              'synthetic_geography': False, 'service_workers_disabled': True,
              'contexts_created': 0, 'maximum_contexts': 1, 'page_errors': [],
              'javascript_console_errors': [], 'resource_console_diagnostics': [],
              'local_request_failures': [], 'external_request_failures': [],
              'local_http_errors': [], 'http_responses': [],
              'assistance': ['Public v018LoadMacro/v046Load select real installed geographic sectors.',
                             'Public v018CaptureAt freezes simulation and places a measured collision-free camera with production LOS.',
                             'Public v047Control auto=false bounds background streaming; v046SetTime fixes daytime.',
                             'Public v042Update and v020Tick(.05,true) step actual production streaming/physics/AI.',
                             'Read-only public exports inspect actual actors, rigs and saves. No spawn/defeat/resource/quest debug API is used.',
                             'Native KeyW under v020Tick performs a prevalidated real physical escape from a Gabian target; view turning uses the public camera diagnostic.']}
    frozen = {}
    page = server = browser = context = None
    origin = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']),
                      total=len(report['checks']), pinned_inputs=frozen)
        (args.output / 'BESTIARY_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

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
                raise RuntimeError('Production geographic staging failed: ' + json.dumps(debug('v046Info')))
            if info['tiles'] > 0 and not info['loading'] and not info['anticipating']:
                return info
            if time.monotonic() - last_print > 15:
                print('LOAD ' + json.dumps({k: info[k] for k in ('phase', 'done', 'total', 'tiles')}), flush=True)
                last_print = time.monotonic()
            page.wait_for_timeout(250)
        raise TimeoutError('Actual map readiness timeout: ' + json.dumps(debug('v047Info')))

    def place(point, target=None, reason=''):
        pos = point['p']
        check('Measured diagnostic camera is outside actual colliders', not debug('v020Collides', pos), {'point': point, 'reason': reason})
        if target:
            check('Actual source-world camera ray reaches the regional actor', debug('v020LOS', pos, target), {'camera': pos, 'target': target})
        yaw = math.atan2(target[0] - pos[0], -(target[2] - pos[2])) if target else 0
        pitch = math.atan2(target[1] - pos[1], math.hypot(target[0] - pos[0], target[2] - pos[2])) if target else -.1
        debug('v018CaptureAt', pos, yaw, max(-1.3, min(1.3, pitch)))
        report['placements'].append({'position': pos, 'height': point['h'], 'target': target, 'reason': reason})
        save()

    def measured_points(points, target=None):
        return page.evaluate("""([points,target])=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{
          const h=d.v046Height(...ll),xz=d.v046Project('geo_huveaune',...ll),p=[xz[0],h.height+1.65,xz[2]];
          return{ll,p,h,clear:Number.isFinite(h.height)&&!h.missing&&!d.v020Collides(p)&&(!target||d.v020LOS(p,target))};
        }).filter(p=>p.clear);} """, [points, target])

    def shot(name, label):
        p = debug('getState')['player']
        debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])
        target = args.output / (name + '.png')
        page.screenshot(path=str(target))
        report['shots'].append({'file': target.name, 'sha256': sha(target.read_bytes()), 'label': label,
                                'method': 'Unmodified native production canvas and HUD after declared measured camera/freeze.'})
        save()

    def flight_slot_probe(row):
        projection = debug('v046Project', 'geo_huveaune', row['lat'], row['lon'])
        absolute = debug('v018Projection', row['lat'], row['lon'])['xy']
        frame = [absolute[0] - projection[0], absolute[1] + projection[2]]
        actors = [a for a in debug('v042World')['enemies'] if a['type'] == 'bloatfly' and a['site'] == row['site']]
        probes = []
        for actor in actors:
            samples = []
            for dx, dz in ((0, 0), (.96, 0), (-.96, 0), (0, .96), (0, -.96)):
                ll = inverse_lambert(actor['pos'][0] + dx + frame[0], frame[1] - actor['pos'][2] - dz)
                h = debug('v046Height', *ll)
                samples.append({'offset': [dx, dz], 'll': ll, 'height': h,
                                'actorYDelta': actor['pos'][1] - h['height'] if h['height'] is not None else None})
            probes.append({'actor': actor, 'sourceSamples': samples,
                           'cachedSitePlacement': debug('getState')['v046']['placements'].get(row['site'])})
        return {'world': debug('v042World'), 'actors': probes}

    def flight_native():
        stage('true_gabian_geographic_flight')
        current = debug('v053BestiaryInfo')
        flight_actor = next((a for a in current['visible'] if a['alive'] and a['species'] == 'gabianBombardier'), None)
        candidates = [r for r in current['eligibleSites'] if r['species'] == 'gabianBombardier']
        # Public catalog fallback includes an already assigned unloaded slot;
        # loading its sector cannot manufacture or reassign an encounter.
        catalog_rows = debug('v042Catalog')
        allowed = debug('v053BestiaryCatalog')['gabianBombardier']['macros']
        known = {r['site'] for r in candidates}
        for site in catalog_rows:
            if site['id'] not in known and site['macro'] in allowed and 'bloatfly' in site['enemyTypes'] and site['kind'] in ('nest', 'elite', 'boss'):
                candidates.append({'site': site['id'], 'lat': site['lat'], 'lon': site['lon']})
        candidates.sort(key=lambda r: (r['site'] != 'v042-marseille-nest-05', r['site']))
        for row in candidates[:args.maximum_sectors]:
            if flight_actor:
                break
            check('Gabian sector request uses the actual installed pack', debug('v046Load', row['lat'], row['lon']) is True)
            ready()
            coordinates = [[row['lat'] + dz / 111320,
                            row['lon'] + dx / (111320 * math.cos(math.radians(row['lat'])))]
                           for radius in (0, 14, 28, 42, 56, 70, 84, 98, 112) for angle in [i * math.tau / 12 for i in range(12)] for dx, dz in [(math.sin(angle) * radius, math.cos(angle) * radius)]]
            clear = measured_points(coordinates)
            if not clear:
                report['attempts'].append({'site': row['site'], 'result': 'no measured clear Gabian inspection arrival'})
                continue
            place(clear[0], reason='real Gabian sector arrival ' + row['site'])
            debug('v042Update', .71)
            debug('v020Tick', .05, True)
            info = debug('v053BestiaryInfo')
            report['attempts'].append({'site': row['site'], 'purpose': 'true flight', 'bestiary': info, 'map': debug('v047Info'), 'slotProbe': flight_slot_probe(row)})
            flight_actor = next((a for a in info['visible'] if a['alive'] and a['species'] == 'gabianBombardier'), None)
        check('A real existing territorial slot admits a Gabian', flight_actor is not None, debug('v053BestiaryInfo'))
        actor_id = flight_actor['id']
        actor = debug('v053BestiaryActor', actor_id)
        site = debug('v042Site', actor['site'])
        projection = debug('v046Project', 'geo_huveaune', site['lat'], site['lon'])
        absolute = debug('v018Projection', site['lat'], site['lon'])['xy']
        frame = [absolute[0] - projection[0], absolute[1] + projection[2]]

        def ll(point):
            return inverse_lambert(point[0] + frame[0], frame[1] - point[2])

        center = [sum(p['center'][i] for p in actor['rig']['parts']) / len(actor['rig']['parts']) for i in range(3)]
        cameras = measured_points([ll([actor['pos'][0] + math.sin(n * math.tau / 32) * radius, 0,
                                        actor['pos'][2] + math.cos(n * math.tau / 32) * radius])
                                   for radius in (2.1, 2.3, 3) for n in range(32)], center)
        check('Real Gabian has a measured clear close observation point', len(cameras) > 0)
        place(cameras[0], center, 'close physical Gabian observation without actor mutation')
        before = debug('v053BestiaryActor', actor_id)
        frames = []
        for _ in range(100):
            debug('v020Tick', .05, True)
            actor = debug('v053BestiaryActor', actor_id)
            if actor is None or not actor['alive'] or debug('getState')['player']['hp'] <= 0:
                check('Actual Gabian and player remain alive during the bounded approach', False)
            frames.append({'position': actor['pos'], 'flight': actor['flight']})
            if actor['flight']['windup'] and actor['flight']['relativeHeight'] >= 1.1:
                break
        report['flight_frames'] = frames
        check('Production AI takes off above measured terrain with a clear complete wing volume',
              actor['flight']['relativeHeight'] >= 1.1 and actor['flight']['volumeClear']
              and all(f['flight']['volumeClear'] for f in frames), actor['flight'])
        check('True aerial stepping preserves the same ID, original bloatfly type and PV',
              all(actor[k] == before[k] for k in ('id', 'species', 'baseType', 'health', 'maxHealth')) and actor['baseType'] == 'bloatfly')
        measured = debug('v046Height', *ll(actor['pos']))
        minimum_y = min(d['pos'][1] - d['scale'][1] / 2 for d in actor['rig']['draws'])
        check('Actually rendered wing/body vertices stand above actual source ground', measured['height'] is not None and minimum_y > measured['height'] + .05,
              {'height': measured, 'lowestMeshY': minimum_y, 'flight': actor['flight']})
        player = debug('getState')['player']
        center = [sum(p['center'][i] for p in actor['rig']['parts']) / len(actor['rig']['parts']) for i in range(3)]
        place({'p': player['pos'], 'h': debug('v046Height', *ll(player['pos']))}, center,
              'camera turn at the same player position; no displacement of the locked target')
        shot('02_true_gabian_flight', 'Actual Gabian above measured source ground with its real windup, rig and swept wing volume.')
        windup = actor['flight']['windup']
        check('Real airborne AI creates a locked, timed corrosive drop', windup is not None and windup['duration'] == 1.35)
        origin = debug('getState')['player']['pos']
        escape = None
        for index in range(16):
            angle = index * math.tau / 16
            points = [ll([origin[0] + math.sin(angle) * distance, 0, origin[2] - math.cos(angle) * distance])
                      for distance in (.4, .8, 1.2, 1.6, 2, 2.4, 2.8, 3.2, 3.6, 4, 4.4, 4.8, 5.2)]
            clear = measured_points(points)
            if len(clear) == len(points) and all(abs(p['h']['height'] - (origin[1] - 1.65)) < .4 for p in clear):
                escape = {'yaw': angle, 'points': clear}
                break
        check('The locked attack has a measured collision-free physical escape corridor', escape is not None)
        report['escape_corridor'] = escape
        debug('v046SetView', escape['yaw'], 0)
        before_hp = debug('getState')['player']['hp']
        page.keyboard.down('w')
        try:
            for _ in range(18):
                debug('v020Tick', .05, True)
        finally:
            page.keyboard.up('w')
        escaped = debug('getState')['player']
        displacement = math.hypot(escaped['pos'][0] - origin[0], escaped['pos'][2] - origin[2])
        check('Native KeyW and real production collision physics leave the locked impact radius', displacement > 1.2,
              {'start': origin, 'after': escaped['pos'], 'displacement': displacement})
        record, saw_projectile = None, False
        for _ in range(80):
            debug('v020Tick', .05, True)
            info = debug('v053BestiaryInfo')
            active = next((b for b in info['bombs'] if b['id'] == actor_id), None)
            if active and not saw_projectile:
                current_player = debug('getState')['player']
                target = active['pos']
                yaw = math.atan2(target[0] - current_player['pos'][0], -(target[2] - current_player['pos'][2]))
                pitch = math.atan2(target[1] - current_player['pos'][1], math.hypot(target[0] - current_player['pos'][0], target[2] - current_player['pos'][2]))
                debug('v046SetView', yaw, max(-1.3, min(1.3, pitch)))
                shot('03_real_corrosive_drop', 'Actual falling corrosive projectile after a real native walking escape; no HTML or actor injection.')
                saw_projectile = True
            record = next((i for i in info['lastImpacts'] if i['id'] == actor_id), None)
            if record:
                break
        check('A real rendered corrosive projectile descends from the airborne actor', saw_projectile)
        check('The locked Gabian projectile impacts and its escaped player is not hit', record is not None and record['hit'] is False, record)
        report['flight_attack'] = {'actorId': actor_id, 'windup': windup, 'nativeKey': 'KeyW', 'physicsSteps': 18,
                                   'before': origin, 'after': escaped['pos'], 'displacement': displacement,
                                   'impact': record, 'playerHpBefore': before_hp, 'playerHpAfter': debug('getState')['player']['hp'],
                                   'scope': 'HP changes from other real enemies are recorded separately; the selected actual Gabian impact reports its own hit result.'}
        debug('save')
        saved = debug('getState')
        actual = debug('v053BestiaryActor', actor_id)
        report['airborne_saved_actor'] = saved['v049']['actors'].get(actor_id)
        check('Native save retains the airborne position in its original v049 encounter',
              report['airborne_saved_actor'] is not None and report['airborne_saved_actor']['pos'] == actual['pos']
              and report['airborne_saved_actor']['health'] == actual['health']
              and saved['v053Bestiary']['assignments'][actor_id] == {'species': 'gabianBombardier', 'baseType': 'bloatfly'})
        report['flight_actor'] = actual

    try:
        raw_html = pin('index.html')
        report.update(html_sha256=sha(raw_html), bestiary_sha256=sha(pin(MODULE)),
                      script_sha256=sha(Path(__file__).read_bytes()))
        (args.output / 'EXECUTED_REGIONAL_BESTIARY_NATIVE.py').write_bytes(Path(__file__).read_bytes())
        check('Frozen production HTML matches coordination', sha(raw_html) == args.expect_html_sha)
        check('Frozen bestiary source is present unchanged in the production bundle',
              frozen[MODULE] == args.expect_bestiary_sha and pin(MODULE).strip() in raw_html)
        check('Frozen real architecture atlas matches coordination', sha(pin('data/map_pack/architecture/index.json')) == args.expect_architecture_sha)
        for relative in ('src/v042/00_catalog.js', 'src/v046/02_environment.js', 'tools/serve_game.py',
                         'data/map_pack/city/index.json', 'data/map_pack/city/terrain-index.json', 'data/map_pack/city/water-index.json'):
            pin(relative)

        class Handler(GameHandler):
            def log_message(self, *_arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin + '/index.html?skipboot'
        stage('actual_pack_audit_before_chromium')
        with urllib.request.urlopen(origin + '/__mistral/local-data', timeout=300) as response:
            audit = json.load(response)
        report['local_pack_audit'] = audit
        check('Actual GameHandler verifies complete installed source pack', audit['complete'] is True)

        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                         args=['--no-sandbox', '--disable-dev-shm-usage'])
            report['browser_version'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
            report['contexts_created'] += 1
            page = context.new_page()
            page.on('pageerror', lambda error: report['page_errors'].append(str(error)))

            def console_seen(message):
                if message.type == 'error':
                    key = 'resource_console_diagnostics' if message.text.startswith('Failed to load resource:') else 'javascript_console_errors'
                    report[key].append({'text': message.text, 'location': message.location})

            def request_failed(request):
                key = 'local_request_failures' if request.url.startswith(origin + '/') else 'external_request_failures'
                report[key].append({'url': request.url, 'failure': request.failure})

            def response_seen(response):
                if not response.url.startswith(origin + '/'):
                    return
                record = {'url': response.url, 'status': response.status, 'from_service_worker': response.from_service_worker}
                relative = urllib.parse.unquote(urllib.parse.urlsplit(response.url).path).lstrip('/')
                local = (ROOT / relative).resolve()
                if relative.startswith('data/map_pack/') and local.is_relative_to(ROOT) and local.is_file():
                    record['source_sha256'] = sha(pin(relative))
                report['http_responses'].append(record)
                if response.status >= 400:
                    report['local_http_errors'].append(record)

            page.on('console', console_seen)
            page.on('requestfailed', request_failed)
            page.on('response', response_seen)
            page.on('dialog', lambda dialog: dialog.accept())
            stage('native_http_document')
            response = page.goto(report['url'], wait_until='load', timeout=60000)
            check('Native HTTP document equals exact production bytes', response is not None and response.status == 200 and sha(response.body()) == args.expect_html_sha)
            report['native_navigation'] = True
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
            page.wait_for_function("['v053BestiaryInfo','v053BestiaryActor','v042World','v020Tick'].every(k=>typeof __MISTRAL_DEBUG[k]==='function')")
            debug('setRenderPaused', True)
            debug('v047Control', {'auto': False})
            p = debug('getState')['player']
            debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])
            debug('v046SetTime', 12)

            stage('real_geographic_publication')
            debug('v018LoadMacro', 'geo_huveaune')
            ready()
            debug('v020Tick', .05, True)
            initial = debug('v053BestiaryInfo')
            report['initial_bestiary'] = initial
            priority = ['v042-huveaune-nest-01', 'v042-marseille-nest-02', 'v042-marseille-nest-05']
            rows = sorted([r for r in initial['eligibleSites'] if r['species'] in ('ratCrowned', 'mistralCicada')], key=lambda r: (priority.index(r['site']) if r['site'] in priority else 3, r['site']))
            chosen = next((a for a in initial['visible'] if a['alive'] and a['species'] in ('ratCrowned', 'mistralCicada')), None)
            for row in rows[:args.maximum_sectors]:
                if chosen:
                    break
                site = debug('v042Site', row['site'])
                check('Candidate belongs to existing hostile territorial catalog', site is not None and not site['safe'], site)
                check('Public sector load requests actual installed geography', debug('v046Load', row['lat'], row['lon']) is True)
                ready()
                coordinates = [[row['lat'] + dz / 111320,
                                row['lon'] + dx / (111320 * math.cos(math.radians(row['lat'])))]
                               for radius in (0, 14, 28, 42, 56, 70, 84, 98, 112) for angle in [i * math.tau / 12 for i in range(12)] for dx, dz in [(math.sin(angle) * radius, math.cos(angle) * radius)]]
                clear = measured_points(coordinates)
                if not clear:
                    report['attempts'].append({'site': row['site'], 'result': 'no measured clear inspection arrival'})
                    continue
                place(clear[0], reason='measured sector arrival near existing hostile site ' + row['site'])
                pre = debug('v042World')
                debug('v042Update', .71)
                debug('v020Tick', .05, True)
                current = debug('v053BestiaryInfo')
                report['attempts'].append({'site': row['site'], 'before': pre, 'after': debug('v042World'),
                                           'bestiary': current, 'map': debug('v047Info')})
                chosen = next((a for a in current['visible'] if a['alive'] and a['species'] in ('ratCrowned', 'mistralCicada')), None)
                save()
            check('Actual published geography admits a newly materialized Rat-couronné or Cigale', chosen is not None, debug('v053BestiaryInfo'))
            check('Native actor is outside the laboratory on actual geographic world', debug('v046Info')['lab'] is False and debug('v042World')['geo'] is True)
            report['selected_actor'] = chosen

            stage('actual_rig_identity_and_native_capture')
            actor = debug('v053BestiaryActor', chosen['id'])
            catalog = debug('v042Site', actor['site'])
            slot = int(actor['id'].rsplit(':', 1)[1])
            check('Regional metadata retains the actual original slot/type/health',
                  actor['id'] == f"v042:{catalog['id']}:outside:{slot}"
                  and actor['baseType'] == catalog['enemyTypes'][slot % len(catalog['enemyTypes'])]
                  and actor['health'] > 0 and actor['health'] <= actor['maxHealth'])
            actual = next(e for e in debug('v042World')['enemies'] if e['id'] == actor['id'])
            check('Read-only regional view matches real world actor identity and PV',
                  actual['type'] == actor['baseType'] and actual['hp'] == actor['health'] and actual['pos'] == actor['pos'])
            rig = actor['rig']
            check('Actual actor rig contains original regional geometry and matching VATS groups',
                  len(rig['draws']) >= 23 and len(rig['parts']) >= 6
                  and all(d['v025Enemy'] == actor['id'] and d['v053RegionalPart'] == actor['species'] for d in rig['draws'])
                  and {d['v025Part'] for d in rig['draws']} == {p['id'] for p in rig['parts']})
            center = [sum(p['center'][i] for p in rig['parts']) / len(rig['parts']) for i in range(3)]
            projection = debug('v046Project', 'geo_huveaune', catalog['lat'], catalog['lon'])
            absolute = debug('v018Projection', catalog['lat'], catalog['lon'])['xy']
            frame = [absolute[0] - projection[0], absolute[1] + projection[2]]
            ll = [inverse_lambert(actor['pos'][0] + math.sin(n * math.tau / 24) * radius + frame[0],
                                  frame[1] - actor['pos'][2] - math.cos(n * math.tau / 24) * radius)
                  for radius in (3.8, 5, 7) for n in range(24)]
            cameras = measured_points(ll, center)
            check('A measured collision-free camera sees the real regional silhouette', len(cameras) > 0)
            place(cameras[0], center, 'regional actor native visual capture ' + actor['id'])
            shot('01_new_regional_actor', 'Actual source-world ' + actor['name'] + ' on its existing territorial encounter; diagnostic camera and simulation freeze.')
            before = debug('v053BestiaryActor', actor['id'])
            debug('v020Tick', .05, True)
            after = debug('v053BestiaryActor', actor['id'])
            check('Actual production player/AI update preserves regional identity, base type and PV',
                  after is not None and all(before[k] == after[k] for k in ('id', 'species', 'baseType', 'health', 'maxHealth')))
            debug('save')
            saved = debug('getState')
            report['actor_before_tick'], report['actor_after_tick'] = before, after
            report['saved_assignment'] = saved['v053Bestiary']['assignments'].get(actor['id'])
            report['saved_actor'] = saved['v049']['actors'].get(actor['id'])
            check('Native save records one variant with the existing encounter ledger',
                  report['saved_assignment'] == {'species': actor['species'], 'baseType': actor['baseType']}
                  and report['saved_actor']['health'] == after['health']
                  and report['saved_actor']['id'] == actor['id'])
            storage = page.evaluate('()=>Object.keys(localStorage).map(key=>({key,bytes:(localStorage.getItem(key)||" ").length}))')
            check('Production save reaches native browser storage', any(r['bytes'] > 1000 for r in storage), storage)
            report['final_bestiary'] = debug('v053BestiaryInfo')
            report['actual_actor_rig'] = after['rig']

            flight_native()

            stage('final_integrity')
            for relative in tuple(frozen):
                pin(relative)
            check('All pinned production/source bytes remain unchanged throughout the pilot', True, frozen)
            check('Exactly one fresh native context was created', report['contexts_created'] == 1)
            check('No uncaught JavaScript or application console error occurs',
                  not report['page_errors'] and not report['javascript_console_errors'],
                  {'page': report['page_errors'], 'console': report['javascript_console_errors']})
            check('Actual local source requests succeed without service-worker substitution',
                  not report['local_request_failures'] and not report['local_http_errors']
                  and not any(r['from_service_worker'] for r in report['http_responses']),
                  {'failures': report['local_request_failures'], 'errors': report['local_http_errors']})
            report['limitations'] = ['One Rat-couronné or Cigale and one genuinely airborne Gabian are required and captured; this does not certify all 41 potential slots or all five species natively.',
                                     'Wound/old-campaign/body/loot roundtrip and the other species are covered by separate production-wrapper VM regressions.',
                                     'No native enemy kill, resource grant, quest outcome or fabricated historical storage import is performed.',
                                     'Camera navigation, time and freeze are declared diagnostic assistance; no human or citywide 1:1 claim.']
            stage('complete')
            return 0
    except Exception as error:
        report['exception'] = {'message': str(error), 'traceback': traceback.format_exc()}
        if page:
            try:
                report['failure_state'] = {'map': debug('v047Info'), 'world': debug('v042World'), 'bestiary': debug('v053BestiaryInfo')}
                shot('FAILED_' + report['stage'], 'Unmodified native failure state; read the failed assertion in the report.')
            except Exception as capture_error:
                report['failure_capture_error'] = str(capture_error)
        save()
        print(traceback.format_exc(), flush=True)
        return 1
    finally:
        if context:
            try:
                context.close()
            except Exception:
                # sync_playwright's context manager already closes its loop
                # when the successful return leaves the with block.
                pass
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        if server:
            server.shutdown()
            server.server_close()
        save()


if __name__ == '__main__':
    raise SystemExit(main())
