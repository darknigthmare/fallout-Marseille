#!/usr/bin/env python3
"""Assisted native HTTP pilot of Communes/Gilets relay decisions on real geography.

One native context serves unmodified production bytes and real installed sources.
The current NPCs are approached at measured, collision-free points; normal E,
visible dialogue and Pip-Boy actions collect two exact relay commitments per
story, pay finite inventory supplies, publish Canal 13 replies and save/Continue.
Declared sector selection, camera placement, freeze and payment supplies are
assistance. No source geometry, actor, proof, outcome or storage is fabricated.
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
CITY = 'geo_marseille_commune'
CONTACT_1 = 'v042-marseille-caravan-01'
CONTACT_2 = 'v042-marseille-caravan-02'
MODULES = {'lore': 'src/v050/10_lore_continuity.js'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def total_xp(player):
    level = player.get('level', 1)
    return player.get('xp', 0) + sum(90 + n * 45 for n in range(1, level))


def inverse_lambert(x, y):
    """Diagnostic inverse of the production Lambert frame; never terrain data."""
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
    parser.add_argument('--expect-architecture-sha', required=True)
    for name in MODULES:
        parser.add_argument('--expect-' + name + '-sha', required=True)
    parser.add_argument('--ready-timeout', type=int, default=300)
    args = parser.parse_args()
    if not args.run:
        print('Prepared only. No server or browser started. Coordinate frozen SHA values and pass --run.')
        return 0

    sys.path.insert(0, str(ROOT / 'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright

    started = time.monotonic()
    args.output.mkdir(parents=True, exist_ok=True)
    script_raw = Path(__file__).read_bytes()
    (args.output / 'EXECUTED_COMMUNITY_DOSSIERS_NATIVE.py').write_bytes(script_raw)
    report = {
        'scope': __doc__, 'stage': 'preflight', 'stages': [], 'checks': [], 'shots': [],
        'script_sha256': sha(script_raw), 'native_navigation': False,
        'html_injected': False, 'network_mocked': False, 'storage_mocked': False,
        'synthetic_geography': False, 'synthetic_documents': False,
        'service_workers_disabled': True, 'contexts_created': 0, 'maximum_contexts': 1,
        'assistance': [
            'Existing v020Load starts an authored scene, then v018LoadMacro/v046Load select actual installed geographic sectors without lab data.',
            'Existing v018CaptureAt places cameras only at measured collision-free points with real line of sight; actors and source geometry are never moved.',
            'Production render/simulation freeze and v047Control auto=false bound the visit. v020Tick(.05,true) establishes actual supported ground.',
            'One declared v020Seed sets caps=1000, water=16, food=12, scrap=12, circuitry=4, cloth=8 to pay real decision supplies. No quest or proof is seeded.',
            'Existing v046SetTime sets daytime. Native KeyE, Tab, dialogue buttons and visible dossier actions perform all feature mutations.',
            'Read-only debug exports inspect exact source identity, ledger, resources, contact admission and reward counts.',
        ],
        'interactions': [], 'placements': [], 'page_errors': [], 'console_errors': [],
        'javascript_console_errors': [], 'resource_console_diagnostics': [],
        'request_failures': [], 'local_request_failures': [], 'external_request_failures': [],
        'local_http_errors': [], 'http_responses': [],
    }
    frozen = {}
    page = server = worker = browser = context = pw = None
    origin = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']),
                      total=len(report['checks']), pinned_inputs=frozen)
        (args.output / 'COMMUNITY_DOSSIERS_NATIVE.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + '\n')

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
        raw = (ROOT / relative).read_bytes()
        if relative in frozen and frozen[relative] != sha(raw):
            raise AssertionError('Input changed during QA: ' + relative)
        frozen[relative] = sha(raw)
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def state():
        return debug('getState')

    def snapshot():
        s = state()
        return {'player': s['player'], 'inventory': s['inventory'], 'ammo': s['ammo'], 'special': s['character']['special'],
                'rep': s['rep'], 'v030': s['v030'], 'v053Lore': s['v053Lore'], 'v053Iconic': s['v053Iconic'],
                'loreRep': s['v046']['lore'].get('reputation', {})}

    def ui():
        return debug('v027UI')

    def click(action, arg=None, scope='#pipboy'):
        selector = 'button[data-p27=' + json.dumps(action) + ']'
        if arg is not None:
            selector += '[data-arg=' + json.dumps(str(arg)) + ']'
        target = page.locator(scope).locator(selector).first
        check('Visible enabled production UI: ' + action + (' ' + str(arg) if arg is not None else ''),
              target.count() > 0 and target.is_visible() and target.is_enabled())
        target.click()

    def receive_station(station):
        target = page.locator('#pipboy button[data-p27="station"][data-arg=' + json.dumps(station) + ']').first
        label = (target.text_content() or '').strip() if target.count() else ''
        check('Visible enabled production UI: station ' + station,
              target.count() > 0 and target.is_visible() and target.is_enabled()
              and label in ('Recevoir les bulletins', 'Couper la station'), {'currentAction': label})
        if label == 'Recevoir les bulletins':
            target.click()

    def close_pip():
        if ui()['mode'] == 'PIP':
            page.keyboard.press('Tab')
            check('Tab returns to actual play and saves native progress', ui()['mode'] == 'PLAYING')

    def pip(tab, sub):
        if ui()['mode'] != 'PIP':
            check('Pip-Boy opens from actual play', ui()['mode'] == 'PLAYING', ui())
            page.keyboard.press('Tab')
        click('tab', tab)
        click('sub', sub)
        check('Normal Pip-Boy navigation reaches ' + tab + '/' + sub,
              ui()['mode'] == 'PIP' and ui()['tab'] == tab and ui()['sub'] == sub)

    def shot(name, label):
        player = state()['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])
        path = args.output / (name + '.png')
        page.screenshot(path=str(path))
        report['shots'].append({'file': path.name, 'label': label, 'sha256': sha(path.read_bytes()),
                                'method': 'Native rendered game and UI, after declared diagnostic positioning/freeze.'})
        save()

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
        report['readiness_failure'] = {'map': debug('v047Info'), 'city': debug('v051CityInfo')}
        raise TimeoutError('Actual geography did not become ready within the bounded timeout')

    def native_document(response):
        check('HTTP document equals coordinated production bytes', response is not None
              and response.status == 200 and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("['v053LoreInfo','v053PowerArmorInfo','v053IconicInfo','v051CityReady'].every(k=>typeof __MISTRAL_DEBUG[k]==='function')")
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        # Freeze through the existing production diagnostic, including before
        # Continue publishes its scene, so remaining active time is comparable.
        player = state()['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])

    def place(position, target=None, reason='', ground=None):
        check('Declared camera point is clear of production colliders', not debug('v020Collides', position),
              {'position': position, 'reason': reason, 'ground': ground})
        yaw = math.atan2(target[0] - position[0], -(target[2] - position[2])) if target else 0
        pitch = math.atan2(target[1] - position[1], math.hypot(target[0] - position[0], target[2] - position[2])) if target else -.12
        pitch = max(-1.3, min(1.3, pitch))
        if target:
            check('Declared camera has actual production line of sight', debug('v020LOS', position, target),
                  {'position': position, 'target': target, 'reason': reason})
        debug('v018CaptureAt', position, yaw, pitch)
        report['placements'].append({'position': position, 'target': target, 'reason': reason, 'ground': ground})
        save()

    def authored(scene):
        close_pip()
        result = debug('v020Load', scene)
        check('Existing authored scene loaded without grants: ' + scene, result['id'] == scene, result)
        player = state()['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])

    def sector(site_id, inhabitant=True):
        close_pip()
        site = debug('v042Site', site_id)
        check('Target is a real existing geographic catalog site', site is not None and (not inhabitant or site['safe'] is True), site)
        check('Actual installed sector requested', debug('v046Load', site['lat'], site['lon']) is True,
              {'site': site_id, 'lat': site['lat'], 'lon': site['lon']})
        ready()
        # Pick an honest land point near the catalog anchor; actual fictional
        # actors can use a different safe placement within the measured sector.
        points = [[site['lat'] + dz / 111320,
                   site['lon'] + dx / (111320 * math.cos(math.radians(site['lat'])))]
                  for dz in range(-90, 91, 10) for dx in range(-90, 91, 10)]
        candidates = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,h,clear:Number.isFinite(h.height)&&!h.missing&&!d.v046Collide(p[0],p[2])};}).filter(p=>p.clear);}""", points)
        check('Sector supplies finite measured elevation and clear camera points', len(candidates) > 0, site_id)
        candidates.sort(key=lambda p: math.hypot((p['ll'][0] - site['lat']) * 111320,
                                                (p['ll'][1] - site['lon']) * 111320 * math.cos(math.radians(site['lat']))))
        point = candidates[0]
        place([point['p'][0], point['h']['height'] + 1.65, point['p'][2]],
              reason='source-measured sector arrival ' + site_id, ground=point['h'])
        debug('v042Update', .71)
        # Real update discovers nearby safe sites and materializes their people.
        actors = debug('v042World')['npcs']
        check('Actual world streams the existing source-positioned site', site_id in debug('v042Runtime')['active'] and (not inhabitant or any(n['site'] == site_id for n in actors)),
              {'site': site_id, 'world': debug('v042World')['id'], 'runtime': debug('v042Runtime')})
        return site

    def frame_origin(site):
        projected = debug('v046Project', 'geo_huveaune', site['lat'], site['lon'])
        absolute = debug('v018Projection', site['lat'], site['lon'])['xy']
        return [absolute[0] - projected[0], absolute[1] + projected[2]]

    def point_ll(position, frame):
        return inverse_lambert(position[0] + frame[0], frame[1] - position[2])

    def contact(site_id, technician=False):
        site = sector(site_id)
        actors = [n for n in debug('v042World')['npcs'] if n['site'] == site_id]
        for actor in actors:
            index = int(actor['id'].rsplit(':', 1)[1])
            actor['record'] = {'siteId': site_id, 'index': index, 'role': site['npcRoles'][index]}
        if technician:
            actors = [n for n in actors if 'mecanicien' in n['record']['role'].lower().replace('é', 'e')
                      or 'technicien' in n['record']['role'].lower()]
        check('Actual desired inhabitant is alive at the sourced relay', len(actors) > 0,
              {'site': site_id, 'technician': technician, 'actors': actors})
        # Capture the cached placement before approaching; never overwrite it.
        cached = state()['v046']['placements'].get(site_id)
        frame = frame_origin(site)
        for actor in actors:
            target = [actor['pos'][0], actor['pos'][1] + 1.2, actor['pos'][2]]
            points = [point_ll([target[0] + math.sin(n * math.tau / 24) * radius, 0,
                                target[2] + math.cos(n * math.tau / 24) * radius], frame)
                      for radius in (1.7, 2.2, 2.65) for n in range(24)]
            clear = page.evaluate("""([points,target])=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const h=d.v046Height(...ll),xz=d.v046Project('geo_huveaune',...ll),p=[xz[0],h.height+1.65,xz[2]];return{p,h,clear:Number.isFinite(h.height)&&!h.missing&&!d.v020Collides(p)&&d.v020LOS(p,target)};}).filter(p=>p.clear);}""", [points, target])
            for point in clear:
                place(point['p'], target, 'physical relay contact ' + actor['id'], point['h'])
                debug('v020Tick', .05, True)
                # A normal simulation step establishes actual stable ground.
                p = state()['player']
                debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])
                if technician:
                    info = debug('v053PowerArmorInfo')
                    valid = info['service'] == 'technician:' + actor['id']
                else:
                    info = debug('v053LoreInfo')
                    # info.contact is specifically giver presence; a named
                    # witness can have no dossier giver of its own. Admit an
                    # approach using the actual current actor geometry, then
                    # require the real visible witness action to be enabled.
                    # Production callbacks still revalidate their own contact,
                    # ground, discovery, threat and owner guards on each click.
                    current = next((n for n in debug('v042World')['npcs'] if n['id'] == actor['id']), None)
                    head = [current['pos'][0], current['pos'][1] + 1.4, current['pos'][2]] if current else None
                    live_player = state()['player']['pos']
                    horizontal = math.hypot(head[0] - live_player[0], head[2] - live_player[2]) if head else math.inf
                    vertical = abs(head[1] - live_player[1]) if head else math.inf
                    clear_contact = debug('v020LOS', live_player, head) if head else False
                    valid = (horizontal <= 8 and vertical < 2.8 and clear_contact
                             and any(q['available'] and (q['contactSite'] == site_id or site_id in q['witnessSites']) for q in info['quests']))
                    info['approachGeometry'] = {'horizontalDistance': horizontal, 'verticalDistance': vertical,
                                                'lineOfSight': clear_contact,
                                                'scope': 'Current real actor/player geometry; real visible actions recheck all production contact guards.'}
                current_label = page.locator('#interactLabel').inner_text()
                valid = valid and current_label.startswith('Parler à ')
                if valid:
                    actor['name'] = current_label.removeprefix('Parler à ')
                    placement = state()['v046']['placements'].get(site_id)
                    source = {'height': debug('v046Height', *point_ll(placement, frame)),
                              'scope': 'Native terrain read at the exact inverse projected saved position; source water/road admission is separately covered by world placement regressions.'} if placement else None
                    check('Active relay keeps cached XY and current measured elevation',
                          placement is not None and source is not None and source['height']['height'] is not None
                          and abs(placement[1] - source['height']['height']) < .15
                          and (cached is None or placement[0] == cached[0] and placement[2] == cached[2]),
                          {'site': site_id, 'cached': cached, 'placement': placement, 'source': source})
                    report['interactions'].append({'site': site_id, 'actor': actor, 'position': p['pos'],
                                                   'service': info['service'] if technician else 'physical lore contact',
                                                   'source': source,
                                                   'approachGeometry': info.get('approachGeometry')})
                    return actor
        raise AssertionError('No measured collision-free contact with the actual relay actor: ' + site['name'])

    try:
        raw_html = pin('index.html')
        report['html_sha256'] = sha(raw_html)
        check('Coordinated frozen production HTML is installed', sha(raw_html) == args.expect_html_sha, sha(raw_html))
        atlas = pin('data/map_pack/architecture/index.json')
        check('Coordinated actual architecture atlas is installed', sha(atlas) == args.expect_architecture_sha, sha(atlas))
        for name, relative in MODULES.items():
            raw = pin(relative)
            check('Frozen ' + name + ' module matches coordinator and inline production bundle',
                  sha(raw) == getattr(args, 'expect_' + name + '_sha') and raw.strip() in raw_html,
                  {'source': relative, 'sha256': sha(raw)})
        for relative in ('src/v046/02_environment.js', 'src/v050/04a_city_sources.js',
                         'src/v050/04aa_city_water.js', 'src/v050/07_facades.js',
                         'src/v050/08_city_interiors.js', 'tools/serve_game.py',
                         'data/map_pack/city/index.json', 'data/map_pack/city/terrain-index.json',
                         'data/map_pack/city/water-index.json'):
            pin(relative)
        exploration_core = pin('src/core-v017.js')
        exploration_rule = "if(!state.player.discovered.includes(id)){state.player.discovered.push(id);toast(`Lieu découvert — ${world.name}`,'good');gainXP(18,'Exploration')}".encode('utf-8')
        check('Pinned historical loadZone awards 18 XP only on first zone discovery',
              exploration_rule in exploration_core and exploration_rule in raw_html,
              {'source': 'src/core-v017.js', 'rewardXP': 18, 'condition': 'zone absent from player.discovered before load'})
        stage('actual_server_audits_before_chromium')

        class Handler(GameHandler):
            def log_message(self, *_arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin + '/index.html?skipboot'
        with urllib.request.urlopen(origin + '/__mistral/city-sources', timeout=180) as response:
            audit, cache_control = json.load(response), response.headers.get('Cache-Control')
        report['server_audit'] = audit
        check('Actual GameHandler audits all installed municipal buildings before browser start',
              cache_control == 'no-store' and audit['ok'] and audit['totalBuildings'] == 291001
              and audit['indexSha256'] == frozen['data/map_pack/city/index.json'])
        with urllib.request.urlopen(origin + '/__mistral/local-data', timeout=300) as response:
            audit, cache_control = json.load(response), response.headers.get('Cache-Control')
        report['local_pack_audit'] = audit
        check('Actual local-pack audit completes before native menu probe',
              cache_control == 'no-store' and audit['complete'] is True)

        pw = sync_playwright().start()
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
            if message.text.startswith('Failed to load resource:'):
                report['resource_console_diagnostics'].append(record)
            else:
                report['javascript_console_errors'].append(record)

        def request_failed(request):
            record = {'url': request.url, 'failure': request.failure, 'stage': report['stage'],
                      'elapsed_seconds': round(time.monotonic() - started, 3)}
            report['request_failures'].append(record)
            report['local_request_failures' if request.url.startswith(origin + '/') else 'external_request_failures'].append(record)

        def response_seen(response):
            if response.url.startswith(origin + '/'):
                record = {'url': response.url, 'status': response.status, 'from_service_worker': response.from_service_worker,
                          'stage': report['stage'], 'elapsed_seconds': round(time.monotonic() - started, 3)}
                path = urllib.parse.unquote(urllib.parse.urlsplit(response.url).path).lstrip('/')
                local = (ROOT / path).resolve()
                if path.startswith('data/map_pack/') and local.is_relative_to(ROOT) and local.is_file():
                    # Pin each actual source file as HTTP reaches it, then
                    # compare again at completion. Do not reacquire data.
                    record['source_sha256'] = sha(pin(str(local.relative_to(ROOT))))
                report['http_responses'].append(record)
                if response.status >= 400:
                    report['local_http_errors'].append(record)

        page.on('console', console_seen)
        page.on('requestfailed', request_failed)
        page.on('response', response_seen)
        page.on('dialog', lambda dialog: dialog.accept())
        stage('native_document_and_declared_payment_setup')
        native_document(page.goto(report['url'], wait_until='load', timeout=60000))
        report['native_navigation'] = True
        authored('aubagne')
        resources = {'caps': 1000, 'water': 16, 'food': 12, 'scrap': 12, 'circuitry': 4, 'cloth': 8}
        report['resource_setup'] = {'api': 'v020Seed', 'values': resources, 'purpose': 'Pay actual new dossier material costs without seeding proofs or outcomes.'}
        debug('v020Seed', resources)
        debug('v046SetTime', 12)
        initial = snapshot()
        check('Eight actual dossier definitions retain six shipped IDs and two new empty records',
              list(initial['v053Lore']['quests']) == ['cendres', 'formulaire', 'signaux', 'lazaret', 'cadences', 'attente', 'partage', 'passage_libre']
              and all(not q['accepted'] and not q['outcome'] for q in initial['v053Lore']['quests'].values()))

        stories = [
            {'id': 'partage', 'name': 'L’eau à hauteur de table', 'macro': CITY,
             'giver': CONTACT_1, 'witnesses': [CONTACT_1, CONTACT_2], 'choice': 'reserve',
             'cost': {'water': 3, 'cloth': 1}, 'caps': 40, 'xp': 90,
             'faction': 'communes', 'rep': {'ligue': 2, 'secours': 2},
             'radio': ['Trois eaux et un tissu', 'réserve finie', 'sans carte de naissance'],
             'shot': '01_communes_paid_reserve'},
            {'id': 'passage_libre', 'name': 'Le passage ne se vend pas', 'macro': 'geo_huveaune',
             'giver': 'v042-huveaune-caravan-02',
             'witnesses': ['v042-huveaune-caravan-02', 'v042-huveaune-caravan-01'],
             'choice': 'cantine', 'cost': {'food': 3, 'water': 2}, 'caps': 45, 'xp': 95,
             'faction': 'gilets', 'rep': {'ligue': 1, 'secours': 3},
             'radio': ['Les deux relais refusent le péage', 'Trois vivres et deux eaux', 'aucun convoi autonome'],
             'shot': '03_gilets_paid_cantine'},
        ]
        report['completed_stories'] = []
        for number, story in enumerate(stories):
            quest = story['id']
            stage('actual_' + quest + '_two_named_relay_commitments')
            debug('v018LoadMacro', story['macro'])
            ready()
            check('Story sector uses installed geography outside lab: ' + quest, debug('v046Info')['lab'] is False)
            actor = contact(story['giver'])
            check('Exact declared giver binds both named source relays: ' + quest,
                  next(q for q in debug('v053LoreInfo')['quests'] if q['id'] == quest)['contactSite'] == story['giver']
                  and set(next(q for q in debug('v053LoreInfo')['quests'] if q['id'] == quest)['witnessSites']) == set(story['witnesses']))
            page.keyboard.press('e')
            check('Native E opens live actual contact dialogue: ' + quest,
                  debug('v020Stats')['mode'] == 'DIALOGUE' and story['name'] in page.locator('#dialogue').inner_text())
            opener = page.locator('#dialogue button').filter(has_text='Ouvrir « ' + story['name'] + ' ».')
            check('Visible actual NPC offers the new story: ' + quest, opener.count() == 1 and opener.is_enabled())
            opener.click()
            check('Native NPC acceptance stores only the actual empty new ledger: ' + quest,
                  state()['v053Lore']['quests'][quest]['accepted'] is True
                  and state()['v053Lore']['quests'][quest]['witnesses'] == []
                  and state()['v053Lore']['quests'][quest]['outcome'] is None)
            page.locator('#dialogue button').filter(has_text='Prendre congé.').click()
            pip('data', 'continuity')
            guarded = page.locator('button[data-p27="l53:resolve"][data-arg=' + json.dumps(quest + '|' + story['choice']) + ']')
            check('Payment stays visibly disabled before exact commitments: ' + quest,
                  guarded.count() == 1 and not guarded.is_enabled())
            before_tracking = snapshot()
            click('l53:track', quest)
            check('Tracking selects a real pending witness without granting proofs or rewards: ' + quest,
                  state()['v042']['tracked'] in story['witnesses']
                  and snapshot()['v053Lore'] == before_tracking['v053Lore']
                  and snapshot()['inventory'] == before_tracking['inventory']
                  and snapshot()['player']['caps'] == before_tracking['player']['caps'])
            close_pip()
            for witness in story['witnesses']:
                contact(witness)
                pip('data', 'continuity')
                before_witness = snapshot()
                click('l53:witness', quest + '|' + witness)
                check('Visible contact records only one exact named source relay: ' + quest + '/' + witness,
                      state()['v053Lore']['quests'][quest]['witnesses'] == before_witness['v053Lore']['quests'][quest]['witnesses'] + [witness]
                      and snapshot()['inventory'] == before_witness['inventory']
                      and snapshot()['player']['caps'] == before_witness['player']['caps'])
                same = page.locator('button[data-p27="l53:witness"][data-arg=' + json.dumps(quest + '|' + witness) + ']')
                check('Repeated same-relay commitment is disabled: ' + quest + '/' + witness,
                      same.count() == 1 and not same.is_enabled())
                close_pip()
            actor = contact(story['giver'])
            pip('data', 'continuity')
            before = snapshot()
            click('l53:resolve', quest + '|' + story['choice'])
            after = snapshot()
            report['completed_stories'].append({'story': story, 'before': before, 'after': after})
            check('Finite actual supply allocation pays and rewards once: ' + quest,
                  after['v053Lore']['quests'][quest]['outcome'] == story['choice']
                  and all(after['inventory'][item] == before['inventory'][item] - n for item, n in story['cost'].items())
                  and after['player']['caps'] == before['player']['caps'] + story['caps']
                  and total_xp(after['player']) == total_xp(before['player']) + story['xp']
                  and after['loreRep'].get(story['faction'], 0) == before['loreRep'].get(story['faction'], 0) + 3
                  and all(after['rep'].get(key, 0) == before['rep'].get(key, 0) + n for key, n in story['rep'].items())
                  and len([j for j in after['v053Lore']['journal'] if j['quest'] == quest]) == 1)
            check('Completed story hides both exclusive reward actions: ' + quest,
                  page.locator('button[data-p27="l53:resolve"][data-arg^=' + json.dumps(quest + '|') + ']').count() == 0)
            # Scroll the actual relevant completed card into view before capture.
            page.locator('#pipContent section').filter(has=page.locator('h3', has_text=story['name'])).scroll_into_view_if_needed()
            shot(story['shot'], 'Actual completed ' + quest + ' card, named commitments and paid exclusive finite supply decision.')
            pip('radio', 'stations')
            click('select', 'canal13')
            receive_station('canal13')
            check('Actual Canal 13 reflects the finite commitment and its limits: ' + quest,
                  all(text in page.locator('#pipContent').inner_text() for text in story['radio']))
            if number == 1:
                check('Canal 13 combines Communes and Gilets without overwriting either decision',
                      all(text in page.locator('#pipContent').inner_text() for item in stories for text in item['radio']))
            shot('02_communes_radio' if number == 0 else '04_both_factions_radio',
                 'Actual text station reports only the paid finite decisions and explicitly limits physical world changes.')
            close_pip()
            p = state()['player']
            current_actor = next(n for n in debug('v042World')['npcs'] if n['id'] == actor['id'])
            target = [current_actor['pos'][0], current_actor['pos'][1] + 1.2, current_actor['pos'][2]]
            place(p['pos'], target, 'Reframe current live story contact after the radio; player and actor stay at actual positions.')
            check('Native E still physically targets the actual saved story contact: ' + quest,
                  page.locator('#interactLabel').inner_text() == 'Parler à ' + actor['name'])
            page.keyboard.press('e')
            check('Actual returned NPC remembers the saved decision and keeps commerce: ' + quest,
                  debug('v020Stats')['mode'] == 'DIALOGUE'
                  and all(text in page.locator('#dialogue').inner_text() for text in story['radio'])
                  and 'Parler du secteur et commercer.' in page.locator('#dialogue').inner_text())
            page.locator('#dialogue button').filter(has_text='Prendre congé.').click()

        stage('native_save_reload_continue_both_decisions')
        pip('data', 'system')
        click('save')
        close_pip()
        saved = snapshot()
        report['before_continue'] = saved
        check('All six shipped dossiers retain their exact initial untouched state',
              all(saved['v053Lore']['quests'][q] == initial['v053Lore']['quests'][q]
                  for q in ('cendres', 'formulaire', 'signaux', 'lazaret', 'cadences', 'attente')))
        native_document(page.reload(wait_until='load', timeout=60000))
        check('Normal Continue uses actual native browser storage', page.locator('#btnContinue').is_enabled())
        page.locator('#btnContinue').click()
        ready()
        restored = snapshot()
        report['after_continue'] = restored
        check('Native Continue preserves exact proofs, decisions and once-only journal', restored['v053Lore'] == saved['v053Lore'])
        prior_discoveries = saved['player']['discovered']
        continued_discoveries = restored['player']['discovered']
        loaded_zone = restored['player']['zone']
        newly_discovered = [zone for zone in continued_discoveries if zone not in prior_discoveries]
        expected_discovery_xp = (18 if newly_discovered == [loaded_zone]
                                 and loaded_zone == saved['player']['zone'] and loaded_zone not in prior_discoveries
                                 and continued_discoveries == prior_discoveries + [loaded_zone]
                                 else 0 if continued_discoveries == prior_discoveries else None)
        report['continue_discovery_receipt'] = {
            'before': prior_discoveries, 'after': continued_discoveries, 'loaded_zone': loaded_zone,
            'newly_discovered': newly_discovered, 'expected_exploration_xp': expected_discovery_xp,
            'actual_xp_delta': total_xp(restored['player']) - total_xp(saved['player']),
            'source': 'Pinned core loadZone: gainXP(18, Exploration) only if loaded zone was absent.',
            'scope': 'This first-load Exploration award is separate from the already verified 90/95 quest rewards.'}
        check('Native Continue preserves material costs, wallet and faction reputations',
              restored['inventory'] == saved['inventory'] and restored['player']['caps'] == saved['player']['caps']
              and restored['loreRep'] == saved['loreRep'] and restored['rep'] == saved['rep']
              and expected_discovery_xp is not None
              and total_xp(restored['player']) == total_xp(saved['player']) + expected_discovery_xp,
              report['continue_discovery_receipt'])
        contact(stories[-1]['giver'])
        pip('data', 'continuity')
        check('Both new dossiers stay final after Continue with no reward controls',
              all(page.locator('button[data-p27="l53:resolve"][data-arg^=' + json.dumps(story['id'] + '|') + ']').count() == 0
                  and page.locator('button[data-p27="l53:accept"][data-arg=' + json.dumps(story['id']) + ']').count() == 0 for story in stories))
        shot('05_two_decisions_after_continue', 'Both dossiers retained by native Continue; no seeded proof, direct outcome or fabricated storage.')
        close_pip()
        report['dossier_counters'] = debug('v053LoreInfo')
        report['limitations'] = [
            'Two newly authored dossier outcomes completed with assisted native visits and exact paid supplies; other branches use separate controlled contracts.',
            'No synthetic actor, source elevation, quest proof, decision, browser storage, HTML or HTTP response is supplied.',
            'Contacts and markers remain fictional existing game placements on real measured terrain; no surveyed station, shipyard or facade is claimed.',
            'No limitless water, animated pump, removed barricade, autonomous convoy, voice recording or recovered private ChatGPT lore is asserted.',
            'Public diagnostic sector selection, measured camera placement, fixed daytime/freeze and supply seed are declared assistance, not an unassisted human walkthrough.',
        ]
        stage('final_integrity')
        for relative in tuple(frozen):
            pin(relative)
        check('All pinned production modules, HTML and source indexes remain byte-identical', True, frozen)
        check('Native pilot created exactly one fresh browser context', report['contexts_created'] == 1)
        check('Application raises no uncaught JavaScript or non-resource console errors',
              not report['page_errors'] and not report['javascript_console_errors'],
              {'pageErrors': report['page_errors'], 'javascriptConsoleErrors': report['javascript_console_errors']})
        cancellations = [r for r in report['local_request_failures']
                         if urllib.parse.urlsplit(r['url']).path == '/__mistral/local-data'
                         and r['failure'] == 'net::ERR_ABORTED']
        unexpected = [r for r in report['local_request_failures'] if r not in cancellations]
        report['local_diagnostic_cancellations'] = cancellations
        check('Local production files and source traffic succeed; exact cancelled diagnostic probes remain observable',
              not unexpected and not report['local_http_errors'],
              {'unexpectedFailures': unexpected, 'errors': report['local_http_errors'],
               'cancelledMetadataProbes': cancellations})
        check('Local HTTP responses are served natively without a service worker',
              not any(r['from_service_worker'] for r in report['http_responses']))
        report['external_network_observation'] = {
            'classification': 'Preserved external requests, including legacy Supabase probes; not uncaught JavaScript exceptions.',
            'failures': report['external_request_failures'],
        }
        context.close()
        report['context_closed'] = True
        context = None
        browser.close()
        report['browser_closed'] = True
        browser = None
        stage('complete')
        return 0
    except Exception as error:
        report['exception'] = {'message': str(error), 'traceback': traceback.format_exc()}
        if page is not None:
            try:
                report['failure_state'] = {'runtime': debug('v020Stats'), 'map': debug('v047Info'),
                                            'lore': debug('v053LoreInfo'), 'city': debug('v051CityInfo')}
                shot('FAILED_' + report['stage'], 'Unmodified native failure state; see report for the actual failed assertion.')
            except Exception as capture_error:
                report['failure_capture_error'] = str(capture_error)
        save()
        print(traceback.format_exc(), flush=True)
        return 1
    finally:
        if context is not None:
            try:
                context.close()
                report['context_closed'] = True
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
                report['browser_closed'] = True
            except Exception:
                pass
        if pw is not None:
            pw.stop()
        if server is not None:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)
            report['server_closed'] = True
            report['server_worker_stopped'] = not worker.is_alive()
        save()


if __name__ == '__main__':
    raise SystemExit(main())
