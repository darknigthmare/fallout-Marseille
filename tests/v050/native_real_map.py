#!/usr/bin/env python3
"""Native Chromium proof against the actual loopback server and installed pack.

UI: menu, character creation, dialogue choices. Existing debug entry points are
used for prologue approaches/story actions, measured camera placement and small
collision-controlled movements. No HTML injection, network interception, fake
storage, synthetic map or security-policy relaxation is used.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import statistics
import socket
import subprocess
import sys
import time
import traceback
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def tile(lat, lon, zoom=16):
    n = 2 ** zoom
    return [math.floor((lon + 180) / 360 * n), math.floor((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)]


def geometry_hashes(signature):
    return {kind: {item['id']: digest(item) for item in signature[kind]} for kind in ('buildings', 'roads')}


def common_geometry(before, after):
    result = {}
    for kind in before:
        ids = set(before[kind]) & set(after[kind])
        changed = [i for i in sorted(ids) if before[kind][i] != after[kind][i]]
        result[kind] = {'before': len(before[kind]), 'after': len(after[kind]), 'common': len(ids), 'changed': changed[:30], 'changed_count': len(changed)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-root', default=str(ROOT))
    parser.add_argument('--output', default=str(ROOT / 'verification/v050'))
    parser.add_argument('--expect-version', default='0.50.0')
    parser.add_argument('--allow-debug-entry', action='store_true', help='Diagnostic only: retain a failed campaign-exit check, then enter real geography separately with existing debug APIs.')
    args = parser.parse_args()
    root, out = Path(args.game_root).resolve(), Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {'version': args.expect_version, 'scope': 'Real HTTP + native Chromium + installed geographic data', 'native_navigation': False,
              'assistance': ['UI menu, character creation and dialogue choice buttons', 'Existing v020Approach and v35p* story actions', 'Existing measured camera placement and v046Move collision-controlled steps', 'Simulation freeze and day/night clock for repeatable measurements; geography and collisions remain production data', 'Two explicitly named POIs discovered through the existing debug discovery action before their UI-only fast travel tests'],
              'network_mocked': False, 'storage_mocked': False, 'html_injected': False, 'synthetic_lab_used': False,
              'checks': [], 'shots': [], 'page_errors': [], 'console_errors': [], 'responses': [], 'request_failures': [], 'stage': 'server'}
    page = None

    def save():
        report['passed'] = sum(c['ok'] for c in report['checks'])
        report['failed'] = sum(not c['ok'] for c in report['checks'])
        report['total'] = len(report['checks'])
        (out / 'NATIVE_REAL_MAP.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ') + name, flush=True)
        save()

    def stage(name):
        report['stage'] = name
        print('STAGE ' + name, flush=True)
        save()

    def debug(name, *values):
        return page.evaluate('([name, values]) => __MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def shot(name, label):
        path = out / ('native_' + name + '.png')
        page.screenshot(path=str(path), full_page=False)
        report['shots'].append({'file': path.name, 'label': label, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        print('CAPTURE ' + path.name, flush=True)
        save()

    def ready(timeout=150):
        deadline = time.monotonic() + timeout
        last_print = 0
        while time.monotonic() < deadline:
            info = debug('v047Info')
            if info['phase'] == 'failed':
                raise RuntimeError('Real geography failed: ' + json.dumps(debug('v046Info'), ensure_ascii=False))
            if info['tiles'] > 0 and not info['loading'] and not info['anticipating']:
                return info
            if time.monotonic() - last_print > 12:
                progress = {k: info[k] for k in ('phase', 'done', 'total', 'tiles', 'loading', 'anticipating')}
                progress['preparation'] = debug('v048Info').get('preparation')
                print('LOAD ' + json.dumps(progress), flush=True)
                last_print = time.monotonic()
            page.wait_for_timeout(250)
        report['readiness_failure'] = {'info': debug('v047Info'), 'preparation': debug('v048Info'), 'zone': debug('getWorld'), 'mode': debug('getMode'), 'diagnostic': debug('v035Diagnostic')}
        shot('readiness_failure', 'Actual native UI at a geography-readiness failure')
        raise RuntimeError('Real geography readiness timeout: ' + json.dumps(debug('v047Info'), ensure_ascii=False))

    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    origin = f'http://127.0.0.1:{port}'
    report['url'] = origin + '/index.html'
    log = (out / 'NATIVE_SERVER.log').open('w')
    server = subprocess.Popen([sys.executable, str(root / 'tools/serve_game.py'), '--no-browser', '--port', str(port)], cwd=root, stdout=log, stderr=log)
    try:
        # Startup validates the retained municipal archive as well as the base
        # pack. This is bounded IO preparation before the HTTP listener opens.
        server_deadline = time.monotonic() + 300
        server_wait_print = 0
        while time.monotonic() < server_deadline:
            if server.poll() is not None:
                raise RuntimeError('Local game server exited during validated source preparation; see NATIVE_SERVER.log')
            try:
                with urllib.request.urlopen(report['url'], timeout=2) as response:
                    served = response.read()
                break
            except OSError:
                if time.monotonic() - server_wait_print > 15:
                    print('WAIT validated source preparation before HTTP startup', flush=True)
                    server_wait_print = time.monotonic()
                time.sleep(.1)
        else:
            raise RuntimeError('Local game server did not start')
        report['html_sha256'] = hashlib.sha256(served).hexdigest()
        check('Server delivers the exact index.html', served == (root / 'index.html').read_bytes())
        with urllib.request.urlopen(origin + '/__mistral/local-data', timeout=45) as response:
            local = json.load(response)
            report['server_audit_cache_control'] = response.headers.get('Cache-Control')
        report['server_audit'] = local
        check('Installed pack complete with all coordinates and terrain grids', local.get('complete') and local['vector']['pbf'] + local['vector']['officialEmpty'] == 5884 and local['terrain']['valid'] == 8 and not any(local[k][m] for k in ('vector', 'terrain') for m in ('missing', 'invalid')), local)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            report['browser_version'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
            page = context.new_page()
            page.set_default_timeout(25000)
            page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
            page.on('console', lambda msg: report['console_errors'].append(msg.text) if msg.type == 'error' else None)
            page.on('dialog', lambda dialog: dialog.accept())
            page.on('response', lambda response: report['responses'].append({'url': response.url, 'status': response.status, 'from_service_worker': response.from_service_worker}) if response.url.startswith(origin) else None)
            page.on('requestfailed', lambda req: report['request_failures'].append({'url': req.url, 'failure': req.failure}))
            stage('menu')
            response = page.goto(report['url'], wait_until='load', timeout=45000)
            report['native_navigation'] = True
            report['browser_document_sha256'] = hashlib.sha256(response.body()).hexdigest()
            check('Native HTTP document matches the served game', response.status == 200 and report['browser_document_sha256'] == report['html_sha256'])
            page.locator('#menuScreen.active').wait_for(state='visible')
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
            page.wait_for_timeout(800)
            report['title'] = page.title()
            report['menu_version'] = page.locator('.menu-version').inner_text()
            report['storage'] = page.evaluate("({localStorageType: Object.getPrototypeOf(localStorage).constructor.name, indexedDB: typeof indexedDB === 'object', secureContext: isSecureContext})")
            check('Global v050 and historical module versions reported honestly', debug('v050Info')['version'] == args.expect_version and debug('v049Info')['version'] == '0.49.0')
            report['menu_buttons'] = page.locator('#menuScreen .menu-actions button').evaluate_all('(buttons) => buttons.map(b => {const r=b.getBoundingClientRect();return {id:b.id,text:b.textContent,visible:!!(r.width&&r.height),inViewport:r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth,top:r.top,bottom:r.bottom}})')
            check('All visible menu actions fit the viewport', all(not b['visible'] or b['inViewport'] for b in report['menu_buttons']), report['menu_buttons'])
            shot('01_menu', 'Real menu, loaded by HTTP in Chromium')
            page.locator('#v050MapStatus').click()
            page.locator('#v047StatusContent').wait_for(state='visible')
            page.wait_for_function('__MISTRAL_DEBUG.v050Info().localData?.live === true')
            check('Menu status uses the live local audit', debug('v050Info')['localData'].get('complete') and debug('v050Info')['localData'].get('live'))
            shot('02_local_maps', 'Local map status from the running server')
            page.locator('#v047CloseStatus').click()
            stage('mobile_menu')
            original_viewport = page.viewport_size
            page.set_viewport_size({'width': 390, 'height': 844})
            page.wait_for_timeout(350)
            mobile = []
            for button in page.locator('#menuScreen .menu-actions button').all():
                if not button.is_visible():
                    continue
                button.scroll_into_view_if_needed()
                mobile.append(button.evaluate('(b)=>{const r=b.getBoundingClientRect();return {id:b.id,text:b.textContent,reachable:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight,width:r.width,height:r.height}}'))
            report['mobile_menu'] = {'viewport': page.viewport_size, 'buttons': mobile}
            check('Mobile menu actions can all be reached by scrolling', all(b['reachable'] and b['height'] >= 40 for b in mobile), report['mobile_menu'])
            page.locator('#btnNew').scroll_into_view_if_needed()
            shot('00_mobile_menu', '390 px mobile menu; native browser, scrollable actions')
            page.set_viewport_size(original_viewport)
            page.locator('#btnNew').scroll_into_view_if_needed()
            stage('character_creation')
            page.locator('#btnNew').click()
            page.locator('#creatorScreen.active').wait_for(state='visible')
            remaining = int(page.locator('#specialRemaining').inner_text())
            keys = page.locator('#specialList button[data-d="1"]').evaluate_all('(buttons) => buttons.map(b => b.dataset.k)')
            for i in range(remaining):
                page.locator(f'#specialList button[data-k="{keys[i % len(keys)]}"][data-d="1"]').click()
            shot('03_character', 'Character created with the actual UI')
            page.locator('#btnStartGame').click()
            page.wait_for_function("__MISTRAL_DEBUG.v020Stats().id === 'vault_prologue'")
            page.wait_for_timeout(3400)
            check('New campaign reaches the vault prologue', debug('v35pInfo')['stage'] == 1 and debug('v020Stats')['mode'] == 'PLAYING')
            shot('04_prologue', 'Native vault arrival through New campaign')
            stage('prologue_progression')
            for action, interaction, expected, choice in [
                ('v35pLocker', 'v35p-locker', 2, True), ('v35pClinic', 'v35p-clinic', 2, True),
                ('v35pFilter', 'v35p-filter', 3, True), ('v35pBreakfast', None, 4, True),
                ('v35pRation', 'v35p-ration', 5, False), ('v35pRecords', 'v35p-records', 6, True),
                ('v35pBrief', None, 7, True), ('v35pIssue', 'v35p-issue', 8, True)]:
                if interaction:
                    check('Debug physical approach: ' + interaction, debug('v020Approach', interaction) is not None)
                debug(action)
                if choice:
                    page.locator('#dialogueChoices button').first.click()
                else:
                    debug('v020ModalDismiss')
                check('Story action ' + action + ' reaches stage ' + str(expected), debug('v35pInfo')['stage'] == expected)
            debug('v020Approach', 'v35p-exit')
            shot('05_airlock', 'Native airlock after debug-assisted story progression')
            before_exit = debug('v35pInfo')
            debug('v35pExit')
            page.locator('#dialogueChoices button').first.click()
            page.wait_for_timeout(1200)
            first_exit = debug('v046Info')
            if first_exit['busy'] or first_exit['tiles']:
                ready()
            else:
                page.wait_for_timeout(1200)
            exit_info = debug('v047Info')
            report['campaign_exit'] = {'before': before_exit, 'after': debug('v35pInfo'), 'world': debug('v020Stats')['id'], 'real': exit_info['tiles'] > 0 and not exit_info['lab'], 'info': exit_info}
            check('Airlock commits directly to real exterior', report['campaign_exit']['real'], report['campaign_exit'])
            check('Campaign progresses only after the exit succeeds', debug('v35pInfo')['complete'] and debug('v020State')['quest']['main'] == 2)
            shot('06_exit', 'Actual airlock destination, without changing the exit result')
            if not report['campaign_exit']['real']:
                if not args.allow_debug_entry:
                    raise RuntimeError('Campaign exit did not enter the real exterior; no alternative entry used')
                stage('separate_debug_entry')
                report['assistance'].append('DIAGNOSTIC ONLY: v017LoadMacro then v046Load + measured camera placement; this does not repair the failed campaign-exit check')
                debug('v017LoadMacro', 'geo_huveaune')
                ready()
                loaded = debug('v046Load', 43.2966, 5.5708)
                check('Separate debug entry prepares actual Aubagne resources', loaded)
                ll = [43.2966, 5.5708]
                p = debug('v046Project', 'geo_huveaune', *ll)
                h = debug('v046Height', *ll)
                if not h.get('missing') and h.get('height') is not None:
                    debug('v046CameraAt', [p[0], max(0, h['height']) + 1.65, p[2]], 0, 0)
                ready()
            stage('real_exterior')
            page.wait_for_timeout(1200)
            info = ready()
            report['exterior'] = info
            report['location'] = debug('v046LL')
            check('Exterior is live geography, not a synthetic lab', not info['lab'] and info['tiles'] > 0 and bool(info['terrain']))
            check('All active vectors came from the installed pack', bool(info['origins']) and set(info['origins']) == {'pack local'}, info['origins'])
            check('Committed terrain grids contain measured heights', all(t['valid'] > 0 and t['width'] > 1 and t['height'] > 1 for t in info['terrain']), info['terrain'])
            p = debug('v046Info')['pos']
            ll = debug('v046LL')
            height = debug('v046Height', *ll)
            report['footing'] = {'player': p, 'latlon': ll, 'ground': height, 'eye_minus_ground': None if height['height'] is None else p[1] - max(0, height['height']), 'collision': debug('v046Collide', p[0], p[2])}
            check('Arrival has measured terrain with source attribution', height['height'] is not None and not height.get('missing') and bool(height.get('sources')), report['footing'])
            check('Player footing is finite and above measured ground', all(math.isfinite(v) for v in p) and height['height'] is not None and 1.2 < report['footing']['eye_minus_ground'] < 2.0, report['footing'])
            check('Arrival is clear of collision geometry', not report['footing']['collision'], report['footing'])
            signature = debug('v046Signature')
            report['geometry_counts'] = {k: len(signature[k]) for k in ('buildings', 'roads', 'nature')}
            check('Real roads and building geometry are present', bool(signature['buildings']) and bool(signature['roads']), report['geometry_counts'])
            check('All building ground and roof heights are finite', all(math.isfinite(b['baseY']) and math.isfinite(b['height']) for b in signature['buildings']))
            shot('07_real_aubagne', 'Real vector footprints and terrain around Aubagne; interpreted game buildings')
            if page.evaluate("typeof __MISTRAL_DEBUG.v050CampaignInfo === 'function'"):
                stage('native_campaign_bridge')
                run_campaign_bridge(page, debug, check, shot, ready, report)
            elif not args.allow_debug_entry:
                check('Campaign bridge is integrated in this native build', False)
            stage('native_continuity')
            run_continuity(page, debug, check, shot, ready, report)
            stage('native_courtyard')
            run_courtyard(root, page, debug, check, shot, ready, report)
            stage('native_fast_travel')
            run_fast_travel(page, debug, check, shot, ready, report)
            stage('native_save_reload')
            run_save_reload(page, debug, check, shot, ready, report)
            report['final_exterior'] = debug('v047Info')
            failed_map_responses = [r for r in report['responses'] if '/data/map_pack/' in r['url'] and any('/' + k + '/' in r['url'] for k in ('base', 'france-vector', 'cadastre', 'terrain')) and r['status'] >= 400]
            check('No installed tile or terrain request failed', not failed_map_responses, failed_map_responses)
            check('Native browser reports no JavaScript exception', not report['page_errors'], report['page_errors'])
            check('The tested HTML remains unchanged for the whole native run', hashlib.sha256((root / 'index.html').read_bytes()).hexdigest() == report['html_sha256'])
            stage('complete')
            context.close()
            browser.close()
    except Exception:
        report['exception'] = traceback.format_exc()
        check('Native pilot completes', False, report['exception'])
        if page and not page.is_closed():
            try:
                report['failure_world'] = debug('v046Info')
                shot('failure', 'Unmodified native UI at the observed failure')
            except Exception:
                pass
    finally:
        server.terminate()
        server.wait(timeout=10)
        log.close()
        save()
    print('TOTAL', report['passed'], report['failed'], report['stage'], flush=True)
    return bool(report['failed'] or report['page_errors'])


def run_campaign_bridge(page, debug, check, shot, ready, report):
    debug('v022Freeze', False)
    page.wait_for_timeout(2000)
    info = debug('v050CampaignInfo')
    gateway = info.get('gateway')
    check('A physical workshop gateway exists in the geographic scene', bool(gateway) and gateway['id'] == 'v050-campaign-workshops', gateway)
    if not gateway:
        raise RuntimeError('The geographic scene has no campaign gateway')
    approach = debug('v020Approach', gateway['id'])
    check('Measured exterior gateway can be approached', approach is not None, approach)
    if not approach:
        raise RuntimeError('Could not approach the exterior workshop gateway')
    point = point_batch(page, [debug('v046LL')])[0]
    if point['clear']:
        position = debug('v046Info')
        pose(debug, point, position['yaw'], position['pitch'])
    before = debug('v020State')
    report['campaign_bridge_probe'] = {'simulation_active': True, 'player': before['player']['pos'], 'enemies': debug('v042World')['enemies']}
    shot('07b_workshop_gateway', 'Physical campaign gateway in the real geographic scene; measured debug-assisted approach')
    opened = debug('v050CampaignOpenWorkshops')
    check('Nearby workshop gateway opens the actual dialogue', opened is True)
    if not opened:
        raise RuntimeError('Workshop dialogue refused at the actual nearby gateway')
    check('Workshop dialogue identifies the narrative scene', 'scène narrative' in page.locator('#dialogueScreen').inner_text() if page.locator('#dialogueScreen').count() else 'scène narrative' in page.locator('#dialogueChoices').inner_text())
    page.locator('#dialogueChoices button').filter(has_text='Entrer dans les ateliers').click()
    page.wait_for_function("__MISTRAL_DEBUG.v020Stats().id === 'aubagne'")
    narrative = debug('v050CampaignInfo')
    check('Campaign gateway enters the authored workshop scene', narrative['zone'] == 'aubagne' and narrative['saved']['workshopVisits'] >= 1 and debug('v047Info')['tiles'] == 0, narrative)
    check('Geographic return point is stored before the workshop visit', math.dist(narrative['saved']['returnPoint']['pos'], before['player']['pos']) < .01)
    debug('v046SetTime', 12, 0)
    debug('v046Render')
    shot('07c_narrative_workshops', 'Authored Aubagne workshops reached through the geographic gateway; explicitly a narrative scene')
    debug('v022Freeze', True)
    npc = next((n for n in debug('v042World')['npcs'] if n['id'] == 'mireille'), None)
    check('Mireille is present in the connected workshop scene', npc is not None, npc)
    if not npc:
        raise RuntimeError('Mireille is absent from the authored workshop scene')
    approach_npc = None
    for n in range(12):
        angle = n * math.tau / 12
        candidate = [npc['pos'][0] + math.sin(angle) * 2, npc['pos'][1] + 1.65, npc['pos'][2] + math.cos(angle) * 2]
        if not debug('v020Collides', candidate) and debug('v020LOS', candidate, [npc['pos'][0], npc['pos'][1] + 1.2, npc['pos'][2]]):
            approach_npc = candidate
            break
    check('Mireille has an accessible physical dialogue approach', approach_npc is not None, approach_npc)
    if approach_npc:
        yaw = math.atan2(npc['pos'][0] - approach_npc[0], -(npc['pos'][2] - approach_npc[2]))
        debug('v046CameraAt', approach_npc, yaw, 0)
        debug('v046Render')
    debug('talkNPC', 'mireille')
    page.locator('#dialogueChoices button').first.wait_for(state='visible')
    shot('07e_mireille_dialogue', 'Real Mireille campaign dialogue reached through the narrative workshop scene; existing dialogue API, actual choice button')
    page.locator('#dialogueChoices button').first.click()
    story_progress = debug('v020State')
    check('Mireille dialogue advances the existing campaign to stage 3', story_progress['quest']['main'] == 3)
    ret = narrative.get('gateway')
    if not ret:
        raise RuntimeError('Narrative workshops have no return gateway')
    check('Narrative return gateway can be approached', debug('v020Approach', ret['id']) is not None)
    opened = debug('v050CampaignOpenReturn')
    check('Workshop return opens the actual dialogue', opened is True)
    if not opened:
        raise RuntimeError('Narrative return dialogue refused at its gateway')
    page.locator('#dialogueChoices button').filter(has_text='Retourner au territoire').click()
    ready()
    page.wait_for_function("!__MISTRAL_DEBUG.v050CampaignInfo().pending && __MISTRAL_DEBUG.v050CampaignInfo().last?.kind === 'return' && __MISTRAL_DEBUG.v050CampaignInfo().last?.status === 'complete'")
    debug('v022Freeze', True)
    after = debug('v020State')
    check('Return restores the saved geographic point', math.dist(before['player']['pos'], after['player']['pos']) < .05, {'before': before['player']['pos'], 'after': after['player']['pos']})
    check('Workshop return preserves newly acquired campaign progress and inventory', story_progress['quest'] == after['quest'] and story_progress.get('inventory') == after.get('inventory') and story_progress['player']['caps'] == after['player']['caps'])
    report['campaign_bridge'] = {'approach': 'Existing physical approach helper and proximity-checked dialogue entry; actual dialogue choices clicked. Mireille uses the existing talkNPC API after a verified free physical approach.', 'gateway': gateway, 'narrative': {'zone': narrative['zone'], 'name': 'Ateliers d’Aubagne — scène narrative', 'returnPoint': narrative['saved']['returnPoint'], 'acquired_main_stage': story_progress['quest']['main']}, 'returned': {'position': after['player']['pos'], 'origins': debug('v047Info')['origins'], 'main_stage': after['quest']['main']}}
    debug('v046Render')
    shot('07d_geographic_return', 'Return from the authored workshops to the saved real geographic point')


def point_batch(page, coordinates):
    """Read production projection, terrain and collision APIs without injection."""
    return page.evaluate('''coordinates => {
      const d=__MISTRAL_DEBUG, region=d.v046Info().region;
      return coordinates.map(ll=>{const p=d.v046Project(region,...ll),ground=d.v046Height(...ll);
        return {ll,p,ground,clear:Number.isFinite(ground.height)&&!ground.missing&&!d.v046Collide(p[0],p[2])};});
    }''', coordinates)


def pose(debug, point, yaw=0, pitch=0):
    if not point['clear']:
        raise ValueError('QA camera setup requires measured, collision-free ground')
    p = point['p']
    debug('v046CameraAt', [p[0], max(0, point['ground']['height']) + 1.65, p[2]], yaw, pitch)
    debug('v046Render')


def find_boundary(page, debug):
    """Find a real cadastre tile edge with a clear, measured short crossing."""
    ll = debug('v046LL')
    x, y = tile(*ll)
    candidates = []
    # These are geometric samples in the loaded sector, never fabricated tiles.
    for edge in (x, x + 1):
        lon = edge / 65536 * 360 - 180
        for delta in range(-30, 31):
            lat = ll[0] + delta * .00008
            candidates.append([lat, lon])
    centers = point_batch(page, candidates)
    centers.sort(key=lambda p: abs(p['ll'][0]-ll[0]) + abs(p['ll'][1]-ll[1]))
    for center in centers:
        if not center['clear']:
            continue
        lat, lon = center['ll']
        unit = 1 / (111320 * math.cos(math.radians(lat)))
        line = point_batch(page, [[lat, lon + offset * unit] for offset in range(-14, 15, 2)])
        if all(p['clear'] for p in line) and max(p['ground']['height'] for p in line) - min(p['ground']['height'] for p in line) < 2.8:
            if tile(*line[0]['ll']) != tile(*line[-1]['ll']):
                return {'tile_before': tile(*line[0]['ll']), 'tile_after': tile(*line[-1]['ll']), 'center': center, 'start': line[0], 'end': line[-1], 'samples': line}
    raise RuntimeError('No measured collision-free short tile crossing found in this loaded sector')


def walk_to(page, debug, ready, target, step=.45):
    start = debug('v046Info')['pos']
    goal = target['p']
    distance = math.hypot(goal[0] - start[0], goal[2] - start[2])
    steps = max(1, math.ceil(distance / step))
    dx, dz = (goal[0] - start[0]) / steps, (goal[2] - start[2]) / steps
    blocked = 0
    for _ in range(steps):
        before = debug('v046Info')['pos']
        result = debug('v046Move', dx, dz)
        if result['busy']:
            ready()
            result = debug('v046Move', dx, dz)
        if math.hypot(result['pos'][0] - before[0], result['pos'][2] - before[2]) < .01:
            blocked += 1
        if blocked > 4:
            break
    actual = debug('v046Info')['pos']
    return {'start': start, 'target': goal, 'actual': actual, 'distance': distance, 'blocked_steps': blocked, 'error': math.hypot(actual[0] - goal[0], actual[2] - goal[2])}


def load_shifted_window(debug, ready, direction=1):
    """Request a real look-ahead window while retaining the player's position.

    The production movement margin is 170 m; all requested centers remain
    within 150 m. This is an explicit test scheduler action, not a simulated
    downloaded tile or a claimed automatic prediction.
    """
    before = set(debug('v047WorldIdentity')['tileRefs'])
    ll = debug('v046LL')
    requests = []
    for dx, dy in ((120*direction, 0), (0, 120*direction), (-120*direction, 0), (0, -120*direction)):
        target = [ll[0]+dy/111320, ll[1]+dx/(111320*math.cos(math.radians(ll[0])))]
        ok = debug('v046Load', *target)
        ready()
        after = set(debug('v047WorldIdentity')['tileRefs'])
        requests.append({'requested_latlon': target, 'published_anchor': debug('v047WorldIdentity')['anchor'], 'ok': ok, 'added': sorted(after-before), 'removed': sorted(before-after)})
        if after != before:
            return {'changed': True, 'requests': requests, 'before_count': len(before), 'after_count': len(after), 'player': debug('v046Info')['pos']}
    return {'changed': False, 'requests': requests, 'before_count': len(before), 'after_count': len(after), 'player': debug('v046Info')['pos']}


def run_collision(page, debug, check, report):
    signature = debug('v046Signature')
    start = debug('v046Info')['pos']
    candidates = []
    for building in signature['buildings']:
        if not building['rings']:
            continue
        ring = building['rings'][0]
        for a, b in zip(ring, ring[1:]):
            length = math.dist(a, b)
            if length < 4:
                continue
            center = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
            if math.dist(center, [start[0], start[2]]) > 90:
                continue
            normal = [-(b[1] - a[1]) / length, (b[0] - a[0]) / length]
            candidates.append({'building': building['id'], 'center': center, 'normal': normal})
    candidates.sort(key=lambda c: math.dist(c['center'], [start[0], start[2]]))
    observed = None
    for c in candidates[:120]:
        a = [c['center'][0] + c['normal'][0] * 1.7, c['center'][1] + c['normal'][1] * 1.7]
        b = [c['center'][0] - c['normal'][0] * 1.7, c['center'][1] - c['normal'][1] * 1.7]
        hits = page.evaluate('points=>points.map(p=>__MISTRAL_DEBUG.v046Collide(...p))', [a, b])
        if hits[0] == hits[1]:
            continue
        free, solid = (b, a) if hits[0] else (a, b)
        # v046Collide samples the real terrain for each point. The vertical
        # camera coordinate is adjusted by the real movement loop below.
        debug('v046CameraAt', [free[0], start[1], free[1]], 0, 0)
        ll = debug('v046LL')
        sample = point_batch(page, [ll])[0]
        if not sample['clear']:
            continue
        pose(debug, sample)
        displacement = [(solid[0] - free[0]) / 30, (solid[1] - free[1]) / 30]
        for _ in range(30):
            debug('v046Move', *displacement)
        final = debug('v046Info')['pos']
        for _ in range(8):
            debug('v046Move', *displacement)
        pushed = debug('v046Info')['pos']
        observed = {**c, 'free': free, 'inside': solid, 'intended_metres': math.dist(free, solid), 'moved_metres': math.dist(free, [final[0], final[2]]), 'remaining_push_moved': math.dist([final[0],final[2]], [pushed[0],pushed[2]]), 'loading': debug('v046Info')['busy'], 'end': pushed, 'end_collision': debug('v046Collide', pushed[0], pushed[2])}
        break
    check('A real cadastral wall blocks production movement', bool(observed) and observed['moved_metres'] < observed['intended_metres'] - .7 and observed['remaining_push_moved'] < .05 and not observed['loading'] and not observed['end_collision'], observed)
    report['collision'] = observed


def run_continuity(page, debug, check, shot, ready, report):
    debug('v022Freeze', True)
    debug('setRenderPaused', True)
    seam = find_boundary(page, debug)
    report['continuity'] = {'method': 'Measured camera setup, production collision-controlled steps across a real z16 cadastre boundary, then real look-ahead windows requested within the validated 170 m margin on each side. The scheduler request is debug-assisted; all fetched resources, preparation, publication and movement are production operations without network mocks.', 'seam': seam}
    debug('v046Load', *seam['start']['ll'])
    ready()
    yaw = math.atan2(seam['end']['p'][0] - seam['start']['p'][0], -(seam['end']['p'][2] - seam['start']['p'][2]))
    pose(debug, seam['start'], yaw)
    before = debug('v046Signature')
    hashes = geometry_hashes(before)
    debug('v047ProbeRemember')
    forward = walk_to(page, debug, ready, seam['end'])
    forward['tile'] = tile(*debug('v046LL'))
    check('Production movement crosses the real cadastre tile boundary', forward['error'] < .8 and forward['tile'] == seam['tile_after'], forward)
    shifted = load_shifted_window(debug, ready, 1)
    check('The crossing publishes a different window of real tiles', shifted['changed'], shifted)
    after = debug('v046Signature')
    common = common_geometry(hashes, geometry_hashes(after))
    check('Walking and publishing across the boundary keeps one scene', before['scene'] == after['scene'], {'before': before['scene'], 'after': after['scene']})
    check('Common real roads and buildings retain identical geometry', all(c['common'] > 0 and c['changed_count'] == 0 for c in common.values()), common)
    report['continuity']['forward'] = {'movement': forward, 'window': shifted, 'geometry': common, 'reuse': debug('v047ProbeReuse')}
    holes_before = {b['id']: digest(b) for b in before['buildings'] if len(b['rings']) > 1}
    holes_after = {b['id']: digest(b) for b in after['buildings'] if len(b['rings']) > 1}
    shared_holes = set(holes_before) & set(holes_after)
    report['continuity']['courtyards'] = {'shared_courtyard_buildings': len(shared_holes), 'note': 'This crossing has no source courtyard case; the separate native_courtyard scenario loads a verified real hole.' if not shared_holes else 'Common hole-bearing buildings compared here.'}
    if shared_holes:
        check('Courtyard holes remain present after publication', all(holes_before[k] == holes_after[k] for k in shared_holes), {'shared_courtyard_buildings': len(shared_holes)})
    backward = walk_to(page, debug, ready, seam['start'])
    backward['tile'] = tile(*debug('v046LL'))
    returned_window = load_shifted_window(debug, ready, -1)
    check('The return publishes another real tile window', returned_window['changed'], returned_window)
    final = debug('v046Signature')
    returned = common_geometry(hashes, geometry_hashes(final))
    check('Return crossing retains scene, position and common geometry', backward['error'] < .8 and backward['tile'] == seam['tile_before'] and final['scene'] == before['scene'] and all(c['changed_count'] == 0 for c in returned.values()), {'movement': backward, 'geometry': returned, 'scene': final['scene']})
    report['continuity']['return'] = {'movement': backward, 'window': returned_window, 'geometry': returned}
    debug('v046SetTime', 12, 0)
    pose(debug, seam['start'], yaw)
    shot('08_day_road', 'Measured road-side setup by a real cadastre boundary at noon; actual game render')
    debug('v046SetTime', 21, 0)
    debug('v046Render')
    shot('09_night_road', 'Same real road-side camera at 21:00; production night lighting')
    debug('v046SetTime', 12, 0)
    debug('v046Load', *debug('v046LL'))
    ready()
    run_collision(page, debug, check, report)
    pose(debug, seam['start'], yaw)
    # Headless CPU rendering is reported, never represented as a player GPU benchmark.
    debug('setRenderPaused', False)
    timing = page.evaluate('''()=>new Promise(resolve=>{const values=[];let previous=null,start=performance.now();
      function frame(now){if(previous!==null)values.push(now-previous);previous=now;
        if(now-start>=3500)resolve(values);else requestAnimationFrame(frame);}requestAnimationFrame(frame);})''')
    debug('setRenderPaused', True)
    gpu = page.evaluate('''()=>{const c=document.getElementById('gameCanvas'),g=c?.getContext('webgl')||c?.getContext('webgl2');if(!g)return null;const x=g.getExtension('WEBGL_debug_renderer_info');return {vendor:g.getParameter(x?x.UNMASKED_VENDOR_WEBGL:g.VENDOR),renderer:g.getParameter(x?x.UNMASKED_RENDERER_WEBGL:g.RENDERER)};}''')
    report['performance'] = {'scope': 'Native headless Chromium frame cadence in this execution environment; not a hardware or desktop FPS guarantee', 'samples': len(timing), 'median_ms': round(statistics.median(timing), 2) if timing else None, 'p95_ms': round(sorted(timing)[min(len(timing)-1, math.ceil(len(timing)*.95)-1)], 2) if timing else None, 'renderer': debug('v018RenderInfo'), 'gpu': gpu}
    print('PERFORMANCE ' + json.dumps(report['performance']), flush=True)
    check('Native frames continue while the real exterior is displayed', len(timing) > 1, report['performance'])


def inside_ring(point, ring):
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def run_courtyard(root, page, debug, check, shot, ready, report):
    """Exercise an actual hole from the acquired source, independently decoded."""
    from mvt_audit_v036 import parse_tile, decode_geometry
    tile_path = root / 'data/map_pack/cadastre/16/33789/24002.pbf'
    raw = tile_path.read_bytes()
    layer = next(l for name, l in parse_tile(raw).items() if name in ('batiments', 'building'))
    feature = next(f for f in layer.features if f.fid == 1653439797)
    paths = decode_geometry(feature)
    hole = next(r for r in paths if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:])) < -16000)
    cx, cy = [sum(p[k] for p in hole[:-1]) / (len(hole)-1) for k in (0, 1)]
    if not inside_ring([cx, cy], hole):
        raise RuntimeError('Source courtyard probe is no longer inside the source ring')
    lon = (33789 + cx/layer.extent) / 65536 * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1-2*(24002+cy/layer.extent)/65536))))
    original = point_batch(page, [debug('v046LL')])[0]
    original_view = debug('v046Info')
    check('The courtyard probe comes from an actual source hole', len(paths) > 1 and inside_ring([cx,cy], hole), {'file': str(tile_path.relative_to(root)), 'feature_id': feature.fid, 'sha256': hashlib.sha256(raw).hexdigest(), 'latlon': [lat,lon]})
    debug('v046Load', lat, lon)
    ready()
    sample = point_batch(page, [[lat,lon]])[0]
    signature = debug('v046Signature')
    building = next((b for b in signature['buildings'] if len(b['rings']) > 1 and any(inside_ring([sample['p'][0],sample['p'][2]], ring) for ring in b['rings'][1:])), None)
    check('Native rendered geometry retains the real courtyard ring', building is not None, {'source_feature': feature.fid, 'rendered_id': building['id'] if building else None, 'rings': len(building['rings']) if building else 0})
    check('The measured source courtyard is not filled by a collision', sample['clear'], sample)
    if not sample['clear'] or not building:
        raise RuntimeError('The independently decoded courtyard is not accessible in the native geometry')
    pose(debug, sample)
    debug('v046Move', .001, 0)
    candidates = point_batch(page, [[lat + dy/111320, lon + dx/(111320*math.cos(math.radians(lat)))] for dx,dy in ((2,0),(-2,0),(0,2),(0,-2))])
    target = next((p for p in candidates if p['clear'] and any(inside_ring([p['p'][0],p['p'][2]], ring) for ring in building['rings'][1:])), None)
    movement = walk_to(page, debug, ready, target) if target else None
    check('Production movement can enter the real open courtyard', movement is not None and movement['error'] < .5, movement)
    before_hash = digest(building)
    debug('v046Load', *debug('v046LL'))
    ready()
    after_signature = debug('v046Signature')
    after = next((b for b in after_signature['buildings'] if b['id'] == building['id']), None)
    check('The real courtyard survives re-publication with the same geometry', after is not None and digest(after) == before_hash and after_signature['scene'] == signature['scene'])
    debug('v046SetTime', 12, 0)
    # Elevated inspection camera, explicitly labelled; not a claimed walk.
    camera = [sample['p'][0], max(0,sample['ground']['height'])+22, sample['p'][2]+10]
    debug('v018CaptureAt', camera, 0, -.95)
    shot('09b_real_courtyard', 'Elevated QA inspection of a real cadastral courtyard; source ring retained, measured ground, not a player traversal camera')
    report['courtyard'] = {'source': str(tile_path.relative_to(root)), 'source_sha256': hashlib.sha256(raw).hexdigest(), 'feature_id': feature.fid, 'latlon': [lat,lon], 'rendered_geometry_id': building['id'], 'rings': len(building['rings']), 'movement': movement, 'same_geometry_after_publication': after is not None and digest(after) == before_hash, 'camera': {'elevated_qa_view': True, 'position': camera}}
    debug('v046Load', *original['ll'])
    ready()
    pose(debug, original, original_view['yaw'], original_view['pitch'])
    debug('v046Move', .001, 0)


def run_fast_travel(page, debug, check, shot, ready, report):
    original = debug('v046Info')['pos']
    catalog = debug('v042Catalog')
    safe = [s for s in catalog if s['kind'] == 'landmark']
    for site in safe:
        p = debug('v046Project', site['macro'], site['lat'], site['lon'])
        site['qa_distance'] = math.dist([p[0], p[2]], [original[0], original[2]])
    safe.sort(key=lambda s: s['qa_distance'])
    targets = [s for s in safe if 250 < s['qa_distance'] < 5000][:2]
    if len(targets) != 2:
        raise RuntimeError('Two real catalogue landmarks within 5 km are required for this native test')
    report['travel'] = {'precondition': 'Existing v042Discover debug action identifies these two catalogue POIs. This validates their subsequent UI travel, not a manual exploration to discover them.', 'targets': [{k: s[k] for k in ('id', 'name', 'macro', 'lat', 'lon', 'qa_distance')} for s in targets], 'journeys': []}
    for index, site in enumerate(targets, 1):
        debug('v042Discover', site['id'])
        if debug('getMode') != 'PIP':
            page.keyboard.press('Tab')
        page.locator('#pipboy:not(.hidden)').wait_for(state='visible')
        page.locator('#pipTabs [data-tab="map"]').click()
        page.locator('#p27Subnav [data-p27="sub"][data-arg="fallout"]').click()
        button = page.locator(f'[data-p27="v042-track"][data-arg="{site["id"]}"]')
        if button.count():
            button.click()
        else:
            page.locator(f'[data-v42-site="{site["id"]}"] circle').click()
        check('Pip-Boy shows the discovered destination ' + site['name'], site['name'] in page.locator('.v42-tracked').inner_text())
        block = debug('v050TravelBlock', site['id'])
        check('Native travel departure is permitted ' + str(index), block is None, block)
        if block:
            raise RuntimeError('Native travel blocked: ' + block)
        before = debug('v020State')
        scene = debug('v046Signature')['scene']
        quote = debug('v050TravelQuote', site['id'])
        page.locator('[data-p27="v050-travel"]').click()
        check('Travel UI asks for a priced duration confirmation ' + str(index), site['name'] in page.locator('.p27-confirm').inner_text() and 'Aucun coût en capsules' in page.locator('.p27-confirm').inner_text())
        if index == 1:
            page.locator('[data-p27="v050-travel-cancel"]').click()
            after_cancel = debug('v020State')
            check('Cancelling the UI confirmation preserves the player and time', before['player'] == after_cancel['player'] and before['worldTime'] == after_cancel['worldTime'] and before['quest'] == after_cancel['quest'])
            page.locator('[data-p27="v050-travel"]').click()
        page.locator('.v050-travel').scroll_into_view_if_needed()
        shot(f'10_travel_{index}_confirmation', 'Native Pip-Boy confirmation for ' + site['name'] + '; discovery precondition explicitly debug-assisted')
        page.locator('[data-p27="v050-travel-confirm"]').click()
        ready()
        page.wait_for_function('__MISTRAL_DEBUG.v050TravelInfo().last?.status === "complete"')
        after = debug('v020State')
        info = debug('v050TravelInfo')
        check('UI fast travel reaches ' + site['name'], info['last']['site'] == site['id'] and info['last']['status'] == 'complete', info['last'])
        check('Native travel keeps one scene ' + str(index), debug('v046Signature')['scene'] == scene)
        check('Native travel time is charged exactly once ' + str(index), math.isclose(after['worldTime'], (before['worldTime'] + quote['minutes'] / 60) % 24, abs_tol=1e-8), {'before': before['worldTime'], 'minutes': quote['minutes'], 'after': after['worldTime']})
        check('Native travel preserves inventory, experience and capsules ' + str(index), before.get('inventory') == after.get('inventory') and before['player']['caps'] == after['player']['caps'] and before['player']['xp'] == after['player']['xp'])
        p = after['player']['pos']
        check('Native travel arrival is clear of real collision ' + str(index), not debug('v046Collide', p[0], p[2]), {'player': p, 'terrain': debug('v046Height', *debug('v046LL'))})
        debug('v046Render')
        shot(f'11_travel_{index}_arrival', 'Actual geographic arrival at ' + site['name'] + '; interpreted game landmarks on measured geography')
        report['travel']['journeys'].append({'destination': site['id'], 'quote': quote, 'result': info['last'], 'scene': scene, 'source': debug('v047Info')['origins']})


def run_save_reload(page, debug, check, shot, ready, report):
    saved = debug('v020State')
    key = debug('v050Info')['saveKey']
    check('Native save API writes successfully', debug('v046Save') is not False)
    stored = page.evaluate('key=>localStorage.getItem(key)', key)
    check('Actual browser storage contains the geographic save', bool(stored) and saved['player']['zone'] in stored, {'key': key, 'bytes': len(stored or '')})
    parsed = json.loads(stored)
    report['continue_before_reload'] = {'current': {'key': key, 'lastSave': parsed.get('lastSave'), 'zone': parsed['player']['zone'], 'position': parsed['player']['pos']}, 'alternatives': [{'kind': item['kind'], 'slot': item.get('slot'), 'savedAt': item.get('savedAt'), 'zone': item.get('snapshot',{}).get('player',{}).get('zone')} for item in debug('v035Latest')]}
    response = page.reload(wait_until='load')
    check('Native reload uses the same release HTML', hashlib.sha256(response.body()).hexdigest() == report['html_sha256'])
    page.locator('#menuScreen.active').wait_for(state='visible')
    page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
    page.locator('#btnContinue').click()
    page.wait_for_timeout(1200)
    initial = debug('v047Info')
    if not initial['loading'] and not initial['tiles']:
        report['continue_wrong_destination'] = {'zone': debug('getWorld'), 'mode': debug('getMode'), 'position': initial['pos'], 'diagnostic': debug('v035Diagnostic')}
        check('Continue starts restoration of the saved geographic scene', False, report['continue_wrong_destination'])
        shot('12_continue_wrong_destination', 'Actual destination selected by Continue after native reload; no corrective debug action')
        raise RuntimeError('Continue selected a non-geographic scene instead of the last geographic save')
    ready()
    debug('v022Freeze', True)
    loaded = debug('v020State')
    check('Continue restores the geographic player position', math.dist(saved['player']['pos'], loaded['player']['pos']) < .6, {'saved': saved['player']['pos'], 'loaded': loaded['player']['pos']})
    check('Continue preserves discovered sites and campaign stage', saved['quest'] == loaded['quest'] and saved['v042']['discovered'] == loaded['v042']['discovered'])
    report['save_reload'] = {'key': key, 'saved_position': saved['player']['pos'], 'loaded_position': loaded['player']['pos'], 'source': debug('v047Info')['origins'], 'native_reload': True}
    shot('12_continue', 'Continue after a real browser reload, using native saved progress and installed geographic files')


if __name__ == '__main__':
    raise SystemExit(main())
