#!/usr/bin/env python3
"""Native continuation pilot, prepared without starting a browser by default.

Runs unchanged production HTML and GameHandler against installed source files,
with native browser storage. Equipment is bought at a real counter, collections
use physical E interactions, and dossier actions use visible Pip-Boy buttons.
Sector/scene selection, measured camera placement, simulation freeze, resource
setup and a controlled armour impact are explicit diagnostic assistance. This
is a bounded assisted pilot, not an unassisted citywide playthrough or a survey.
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
TECHNICIAN = 'v042-marseille-settlement-02'
HUV_COLLECTION = 'v042-huveaune-caravan-01'
MODULES = {
    'lore': 'src/v050/10_lore_continuity.js',
    'power': 'src/v050/11_power_armor.js',
    'iconic': 'src/v050/12_iconic_ecosystem.js',
}


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
    (args.output / 'EXECUTED_CONTINUATION_NATIVE.py').write_bytes(script_raw)
    report = {
        'scope': __doc__, 'stage': 'preflight', 'stages': [], 'checks': [], 'shots': [],
        'script_sha256': sha(script_raw), 'native_navigation': False,
        'html_injected': False, 'network_mocked': False, 'storage_mocked': False,
        'synthetic_geography': False, 'synthetic_documents': False,
        'service_workers_disabled': True, 'contexts_created': 0, 'maximum_contexts': 1,
        'assistance': [
            'Existing v020Load selects authored narrative scenes without granting equipment or quest outcomes. These scenes are not IGN replicas.',
            'Existing v018LoadMacro/v046Load select installed geographic sectors; no lab or generated geographic fixture.',
            'Existing v018CaptureAt places the player only at a measured or authored collision-free point, with actual line of sight.',
            'Diagnostic Lambert inverse converts actual exported world points back to latitude/longitude for native terrain reads; it supplies no elevation.',
            'Existing simulation/render freeze, and v047Control auto=false, make the bounded inspection repeatable.',
            'One declared v020Seed sets caps=10000, scrap=100, circuitry=20, weaponParts=30. No armour, core, collectible, SPECIAL or quest is seeded.',
            'Existing v046SetTime sets daytime once. Native KeyW plus v020Tick(.05,true) steps production movement under freeze.',
            'One existing v030Hurt(40,torso) creates a declared controlled impact after actual equipment purchase; no HP restoration or free repair.',
            'Read-only state/runtime exports inspect results. Native E, U, Tab and visible production buttons perform feature actions.',
        ],
        'interactions': [], 'placements': [], 'page_errors': [], 'console_errors': [],
        'javascript_console_errors': [], 'resource_console_diagnostics': [],
        'request_failures': [], 'local_request_failures': [], 'external_request_failures': [],
        'local_http_errors': [], 'http_responses': [],
    }
    frozen = {}
    page = server = worker = browser = context = None
    origin = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']),
                      total=len(report['checks']), pinned_inputs=frozen)
        (args.output / 'CONTINUATION_NATIVE.json').write_text(
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

    def power():
        close_pip()
        page.keyboard.press('u')
        check('Native U opens STAT / ARMURE', ui()['mode'] == 'PIP' and ui()['tab'] == 'status'
              and ui()['sub'] == 'power', ui())

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

    def physical(interaction_id, label):
        """Approach using the real interaction and actual sampled terrain, never grant."""
        close_pip()
        it = next((i for i in debug('v020Stats')['interactables'] if i['id'] == interaction_id), None)
        check('Physical production interaction exists: ' + interaction_id, it is not None)
        target = it['pos']
        # The existing helper checks the actual world's ground/colliders/LOS
        # inside the production closure. These three pickups are authored scenes.
        approach = debug('v020Approach', interaction_id)
        check('Existing collision/LOS helper reaches actual interaction', approach is not None, interaction_id)
        points = [{'p': approach['pos']}]
        if interaction_id == 'drydock-trade':
            counter = debug('v053PowerArmorInfo').get('drydockService') or {}
            if counter.get('approach'):
                points.insert(0, {'p': counter['approach']})
        selected = None
        for point in points:
            place(point['p'], target, 'existing physical approach to ' + interaction_id)
            actual = page.locator('#interactLabel').inner_text()
            if label.casefold() in actual.casefold():
                selected = {'id': interaction_id, 'label': actual, 'position': point['p'], 'target': target,
                            'action': 'Native KeyE', 'source': 'Existing v020Approach or actual retained counter approach plus actual visible interaction label.'}
                break
        check('Native selection reaches requested physical interaction', selected is not None,
              {'id': interaction_id, 'lastLabel': page.locator('#interactLabel').inner_text(), 'candidates': len(points)})
        report['interactions'].append(selected)
        if interaction_id.startswith('iconic:'):
            shot('physical_' + interaction_id.replace(':', '_'),
                 'Actual original game object in its authored narrative scene, before the native E pickup.')
        page.keyboard.press('e')
        save()
        return selected

    def authored(scene):
        close_pip()
        result = debug('v020Load', scene)
        check('Existing authored scene loaded without grants: ' + scene, result['id'] == scene, result)
        player = state()['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])

    def sector(site_id):
        close_pip()
        site = debug('v042Site', site_id)
        check('Target is a real existing geographic catalog relay', site is not None and site['safe'] is True, site)
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
        check('Actual municipal world streams existing relay inhabitants', any(n['site'] == site_id for n in actors),
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
                    valid = any(q['contact'] for q in info['quests'] if q['contactSite'] == site_id or site_id in q['witnessSites'])
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
                                                   'source': source})
                    return actor
        raise AssertionError('No measured collision-free contact with the actual relay actor: ' + site['name'])

    def consume(item):
        pip('inventory', 'aid')
        # Real search keeps rows available even when many legacy aids exist.
        names = {'nukaCola': 'Nuka-Cola', 'magazineRepair': 'Le Mécano du désert'}
        page.locator('#p27Search').fill(names[item])
        click('select', item)
        before = snapshot()
        click('use', item)
        after = snapshot()
        close_pip()
        return before, after

    def walk_steps(count=25):
        close_pip()
        before = snapshot()
        page.keyboard.down('w')
        try:
            for _ in range(count):
                debug('v020Tick', .05, True)
        finally:
            page.keyboard.up('w')
        after = snapshot()
        return before, after

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
            stage('native_document_and_finite_purchase')
            native_document(page.goto(report['url'], wait_until='load', timeout=60000))
            report['native_navigation'] = True
            authored('drydock')
            check('Pilot starts without a free T45 suit or fusion core',
                  't45Armor' not in state()['equipment']['ownedArmors'] and state()['ammo'].get('fusionCore', 0) == 0)
            resources = {'caps': 10000, 'scrap': 100, 'circuitry': 20, 'weaponParts': 30}
            report['resource_setup'] = {'api': 'v020Seed', 'values': resources, 'purpose': 'Pay real finite trade and maintenance costs.'}
            debug('v020Seed', resources)
            debug('v046SetTime', 12)
            physical('drydock-trade', 'magasin de la cale')
            check('Real E opens the physical drydock merchant', debug('v020Stats')['mode'] == 'TRADE')
            initial_stock = state()['economy']['merchants']['drydock']['stock'].copy()
            before_buy = snapshot()
            page.locator('button[data-buy="t45Armor"]').click()
            page.locator('button[data-buy="fusionCore"]').click()
            after_buy = snapshot()
            check('Visible merchant buys one finite suit and one finite new core',
                  't45Armor' in state()['equipment']['ownedArmors'] and after_buy['ammo']['fusionCore'] == 1
                  and after_buy['player']['caps'] < before_buy['player']['caps']
                  and state()['economy']['merchants']['drydock']['stock']['t45Armor'] == initial_stock['t45Armor'] - 1
                  and state()['economy']['merchants']['drydock']['stock']['fusionCore'] == initial_stock['fusionCore'] - 1,
                  {'initialStock': initial_stock, 'afterStock': state()['economy']['merchants']['drydock']['stock']})
            shot('01_finite_merchant', 'Actual merchant after paid finite T45 and core purchase; authored drydock scene.')
            page.locator('#tradeClose').click()
            power()
            click('p30:equip', 't45Armor')
            click('p30:insert', 'new')
            click('p30:power', '')
            check('U panel equips the purchased suit and inserts its paid core',
                  debug('v030Health')['armor'] == 't45Armor' and debug('v030Health')['online']
                  and debug('v030Health')['core'] == 100 and state()['ammo']['fusionCore'] == 0)
            shot('02_powered_u_panel', 'Native U / STAT ARMURE with six plates and paid installed core.')
            close_pip()
            # Select an actually clear short path near the real authored spawn,
            # including the random crates of this particular production scene.
            lane = page.evaluate("""()=>{const d=__MISTRAL_DEBUG,spawn=d.v018World().spawn;for(let dx=-8;dx<=8;dx+=2)for(let dz=0;dz<=6;dz+=2){const x=spawn[0]+dx,z=spawn[2]-dz,y=spawn[1];let clear=true;for(let t=0;t<=6;t+=.4)if(d.v020Collides([x,y,z-t])){clear=false;break;}if(clear)return{pos:[x,y,z],target:[x,y,z-6],ground:y-1.65};}return null;}""")
            check('Actual authored spawn contains a short collision-free movement lane', lane is not None, lane)
            place(lane['pos'], lane['target'], 'read-only sampled actual drydock access lane', lane['ground'])
            moving_before, moving_after = walk_steps()
            distance = math.dist(moving_before['player']['pos'], moving_after['player']['pos'])
            check('Actual native movement spends only a finite portion of the core', distance > .4
                  and 0 < moving_after['v030']['core'] < moving_before['v030']['core'],
                  {'distance': distance, 'before': moving_before['v030']['core'], 'after': moving_after['v030']['core']})
            power()
            paused = debug('v030State')['core']
            for _ in range(10):
                debug('v020Tick', .05, True)
            check('Production simulation steps in Pip-Boy preserve installed core charge', debug('v030State')['core'] == paused)
            click('p30:power', '')
            click('p30:eject', '')
            ejected = debug('v030State')
            check('Ejection conserves exact spent core in finite spare ledger',
                  ejected['core'] is None and ejected['spares'] == [paused])
            click('p30:used', '0')
            check('Reinsertion retains partial charge without a free recharge',
                  debug('v030State')['core'] == paused and debug('v030State')['spares'] == [])
            close_pip()

            stage('physical_collections_and_inventory_use')
            authored('aubagne')
            before_figurine = snapshot()
            physical('iconic:figurine-s', 'Figurine')
            check('Native E collects physical figurine and changes Force once',
                  debug('v053IconicInfo')['found'].get('figurine-s') is True
                  and state()['character']['special']['S'] == min(10, before_figurine['special']['S'] + 1))
            physical('iconic:bouteille-classique', 'Nuka-Cola')
            check('Physical bottle enters real inventory before use', state()['inventory'].get('nukaCola', 0) >= 1)
            shot('03_collection_authored_world', 'Actual authored Aubagne collectibles reached by normal E.')
            drink_before, drink_after = consume('nukaCola')
            bp, ap = drink_before['player'], drink_after['player']
            check('Inventory Nuka use applies finite quantity, capped vitals, radiation and one cap',
                  drink_after['inventory']['nukaCola'] == drink_before['inventory']['nukaCola'] - 1
                  and ap['hp'] == min(bp['maxHp'], bp['hp'] + 12)
                  and ap['ap'] == min(bp['maxAp'], bp['ap'] + 20)
                  and ap['rad'] == min(100, bp['rad'] + 2) and ap['caps'] == bp['caps'] + 1
                  and drink_after['v053Iconic']['drinks'] == drink_before['v053Iconic']['drinks'] + 1)
            authored('relay_vent')
            physical('iconic:edition-repair', 'Mécano')
            base_skill = debug('v023Skills')['repair']
            book_before, book_after = consume('magazineRepair')
            check('Real magazine use consumes one copy and grants bounded skill duration',
                  book_after['inventory']['magazineRepair'] == book_before['inventory']['magazineRepair'] - 1
                  and book_after['v053Iconic']['read']['magazineRepair'] == 1
                  and book_after['v053Iconic']['effects']['repair'] == 120
                  and debug('v023Skills')['repair'] == min(100, base_skill + 10))
            pip('data', 'iconic')
            paused_effect = debug('v053IconicInfo')['effects']['repair']
            for _ in range(10):
                debug('v020Tick', .05, True)
            check('Production simulation steps in Collection UI pause magazine duration', debug('v053IconicInfo')['effects']['repair'] == paused_effect)
            shot('04_collection_pipboy', 'Normal DATA / COLLECTION, one-time figurine and temporary magazine ledger.')
            close_pip()
            before_tick = debug('v053IconicInfo')['effects']['repair']
            debug('v020Tick', .05, True)
            check('Actual active production tick consumes magazine duration',
                  abs(debug('v053IconicInfo')['effects']['repair'] - (before_tick - .05)) < 1e-6)
            authored('aubagne')
            check('Re-entering narrative scene does not respawn collected figurine or bottle',
                  not any(p['id'] in ('figurine-s', 'bouteille-classique') for p in debug('v053IconicInfo')['physical']))

            stage('real_municipal_dossier_two_witnesses')
            debug('v018LoadMacro', CITY)
            ready()
            check('City path uses actual installed geography outside lab', debug('v046Info')['lab'] is False)
            first_actor = contact(CONTACT_1)
            pip('data', 'continuity')
            click('l53:accept', 'cendres')
            click('l53:witness', 'cendres|' + CONTACT_1)
            check('First real relay witness is committed by visible dossier controls',
                  state()['v053Lore']['quests']['cendres']['witnesses'] == [CONTACT_1])
            shot('05_first_cendres_contact', 'Real Marseille relay contact and first witness through DATA / RELAIS ET DOSSIERS.')
            contact(CONTACT_2)
            pip('data', 'continuity')
            click('l53:witness', 'cendres|' + CONTACT_2)
            q = next(q for q in debug('v053LoreInfo')['quests'] if q['id'] == 'cendres')
            check('Two distinct physical relays provide the actual required evidence',
                  q['progress']['ready'] and set(q['witnesses']) == {CONTACT_1, CONTACT_2}, q)
            first_actor = contact(CONTACT_1)
            pip('data', 'continuity')
            before_resolution = snapshot()
            click('l53:resolve', 'cendres|anonymes')
            after_resolution = snapshot()
            report['cendres_reward'] = {'before': before_resolution, 'after': after_resolution}
            check('One dossier resolves at giver with its exact finite canonical reward',
                  after_resolution['v053Lore']['quests']['cendres']['outcome'] == 'anonymes'
                  and after_resolution['player']['caps'] == before_resolution['player']['caps'] + 45
                  and total_xp(after_resolution['player']) == total_xp(before_resolution['player']) + 80
                  and after_resolution['rep']['ligue'] == before_resolution['rep']['ligue'] + 2
                  and after_resolution['loreRep'].get('convention', 0) == before_resolution['loreRep'].get('convention', 0) + 3
                  and len([j for j in after_resolution['v053Lore']['journal'] if j['quest'] == 'cendres']) == 1)
            check('Completed dossier removes reward actions and explains finality',
                  page.locator('button[data-p27="l53:resolve"][data-arg^="cendres|"]').count() == 0
                  and 'Ce dossier ne se renouvelle pas' in page.locator('#pipContent').inner_text())
            shot('06_completed_cendres', 'Dossier complete: physical testimony, final decision and finite reward.')
            pip('radio', 'stations')
            click('select', 'canal13')
            click('station', 'canal13')
            check('Normal RADIO reports the saved dossier decision',
                  'Les attestations restent sous la garde des familles' in page.locator('#pipContent').inner_text())
            shot('07_canal13_consequence', 'Actual Canal 13 bulletin reflects the saved dossier outcome.')
            close_pip()
            # Contact point was retained while the Pip-Boy was open. Actual E
            # must identify a person, not a debug conversation dispatch.
            p = state()['player']
            debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])
            check('Physical E still targets the real relay NPC',
                  page.locator('#interactLabel').inner_text() == 'Parler à ' + first_actor['name'],
                  page.locator('#interactLabel').inner_text())
            page.keyboard.press('e')
            check('Returned NPC dialogue recalls decision and keeps historical sector commerce',
                  debug('v020Stats')['mode'] == 'DIALOGUE'
                  and 'Les attestations restent sous la garde des familles' in page.locator('#dialogue').inner_text()
                  and 'Parler du secteur et commercer.' in page.locator('#dialogue').inner_text())
            shot('08_npc_remembers', 'Actual living contact remembers dossier outcome and keeps existing dialogue choices.')
            page.locator('#dialogue button').filter(has_text='Prendre congé.').click()

            stage('physical_geographic_technician_maintenance')
            mechanic = contact(TECHNICIAN, technician=True)
            check('Real discovered mechanic enables geographical service',
                  debug('v053PowerArmorInfo')['service'] == 'technician:' + mechanic['id'])
            before_impact = snapshot()
            debug('v030Hurt', 40, 'torso')
            after_impact = snapshot()
            report['controlled_impact'] = {'api': 'v030Hurt', 'arguments': [40, 'torso'],
                                           'before': before_impact, 'after': after_impact}
            check('Declared production impact really wears the purchased plastron',
                  after_impact['v030']['rigs']['t45Armor']['parts']['torso'] < before_impact['v030']['rigs']['t45Armor']['parts']['torso'])
            power()
            click('p30:slot', 'torso')
            cost = debug('v030ServiceCost', 'torso')
            click('p30:repair', 'torso')
            check('Real mechanic presents an actual material quote', cost is not None
                  and page.locator('.p30-quote').is_visible(), cost)
            before_repair = snapshot()
            click('p30:confirm')
            after_repair = snapshot()
            report['technician_maintenance'] = {'actor': mechanic, 'service': debug('v053PowerArmorInfo'),
                                               'cost': cost, 'before': before_repair, 'after': after_repair}
            check('Physical mechanic repairs one plate for exact quoted materials without healing',
                  after_repair['v030']['rigs']['t45Armor']['parts']['torso'] == 100
                  and all(after_repair['inventory'].get(k, 0) == before_repair['inventory'].get(k, 0) - n for k, n in cost.items())
                  and after_repair['player']['hp'] == before_repair['player']['hp']
                  and after_repair['v030']['core'] == before_repair['v030']['core'])
            shot('09_native_technician_u', 'U / ARMURE after paid service by a real discovered Marseille mechanic.')
            close_pip()
            shot('10_native_technician_world', 'Actual geographically streamed mechanic at a source-measured safe fictional relay.')

            stage('shared_ledger_geography_and_native_continue')
            sector(HUV_COLLECTION)
            p = state()['player']
            debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])
            iconic = debug('v053IconicInfo')
            targets = debug('v053IconicCatalog')
            check('Real geographic relay is the actual shared target for the three collected counterparts',
                  all(next(t for t in targets if t['id'] == k)['siteId'] == HUV_COLLECTION
                      for k in ('figurine-s', 'edition-repair', 'bouteille-classique')))
            check('Geographical counterparts do not duplicate story-collected objects',
                  all(iconic['found'].get(k) for k in ('figurine-s', 'edition-repair', 'bouteille-classique'))
                  and not any(p['id'] in ('figurine-s', 'edition-repair', 'bouteille-classique') for p in iconic['physical']),
                  {'site': HUV_COLLECTION, 'collection': iconic})
            pip('data', 'system')
            click('save')
            close_pip()
            saved = snapshot()
            report['before_continue'] = saved
            storage = page.evaluate("()=>Object.keys(localStorage).map(k=>({key:k,bytes:(localStorage.getItem(k)||'').length}))")
            check('Real save created native browser storage without storage substitution',
                  any(s['bytes'] > 1000 for s in storage), storage)
            stage('native_continue_reload')
            native_document(page.reload(wait_until='load', timeout=60000))
            check('Normal Continue menu is enabled from real native save', page.locator('#btnContinue').is_enabled())
            page.locator('#btnContinue').click()
            ready()
            restored = snapshot()
            report['after_continue'] = restored
            check('Normal reload / Continue migration preserves collection, consumed items and finite armor ledger',
                  restored['v053Iconic'] == saved['v053Iconic']
                  and restored['special'] == saved['special']
                  and restored['v030']['core'] == saved['v030']['core']
                  and restored['v030']['spares'] == saved['v030']['spares']
                  and restored['v030']['rigs'] == saved['v030']['rigs']
                  and restored['ammo']['fusionCore'] == saved['ammo']['fusionCore']
                  and all(restored['inventory'].get(k, 0) == saved['inventory'].get(k, 0)
                          for k in ('nukaCola', 'magazineRepair')))
            check('Continue preserves complete dossier proofs and single final reward journal',
                  restored['v053Lore'] == saved['v053Lore']
                  and len([j for j in restored['v053Lore']['journal'] if j['quest'] == 'cendres']) == 1)
            pip('data', 'iconic')
            check('Normal collection UI survives Continue with remaining active-time duration',
                  'RÉCUPÉRÉE' in page.locator('#pipContent').inner_text()
                  and '1 lecture(s)' in page.locator('#pipContent').inner_text())
            shot('11_collection_after_continue', 'Native Continue retains one-time collection and remaining skill duration.')
            close_pip()
            contact(CONTACT_1)
            pip('data', 'continuity')
            before_revisit = snapshot()
            check('Revisiting completed giver after Continue exposes no repeatable reward action',
                  page.locator('button[data-p27="l53:resolve"][data-arg^="cendres|"]').count() == 0
                  and page.locator('button[data-p27="l53:accept"][data-arg="cendres"]').count() == 0
                  and 'Ce dossier ne se renouvelle pas' in page.locator('#pipContent').inner_text())
            page.wait_for_timeout(200)
            after_revisit = snapshot()
            check('Inspection of completed dossier cannot grant another reward',
                  after_revisit['player']['caps'] == before_revisit['player']['caps']
                  and total_xp(after_revisit['player']) == total_xp(before_revisit['player'])
                  and after_revisit['v053Lore']['journal'] == before_revisit['v053Lore']['journal'])
            report['dossier_counters'] = debug('v053LoreInfo')
            report['limitations'] = [
                'One of four new faction dossiers is completed natively. Other dossier counters are exported, not claimed complete.',
                'One of seven figurines, one of four magazines and one of two bottle types are collected and used as appropriate.',
                'One paid armor acquisition and one paid real-relay plate repair; failure rollback/concurrency are covered by separate VM regressions.',
                'Reload/Continue exercises current native save migration. No fabricated historical storage import is installed.',
                'Geographic actors, stands and lore are authored fiction placed on measured terrain; no claim of surveyed facades or rooms.',
                'The pilot uses bounded diagnostic positioning, fixed simulation steps and seeded payment materials; it is not a human walkthrough.',
                'An ERR_ABORTED on the exact local-data diagnostic route is retained separately as a cancelled metadata probe, with its actual stage and time. Other local failures remain fatal.',
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
            stage('complete')
            return 0
    except Exception as error:
        report['exception'] = {'message': str(error), 'traceback': traceback.format_exc()}
        if page is not None:
            try:
                report['failure_state'] = {'runtime': debug('v020Stats'), 'map': debug('v047Info'),
                                            'lore': debug('v053LoreInfo'), 'armor': debug('v053PowerArmorInfo'),
                                            'iconic': debug('v053IconicInfo')}
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
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass
        if server is not None:
            server.shutdown()
            server.server_close()
        save()


if __name__ == '__main__':
    raise SystemExit(main())
