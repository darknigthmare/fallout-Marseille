#!/usr/bin/env python3
"""Combat feedback on exact production HTML and an existing authored hostile.

Readonly geometry/collision/LOS scouts and inherited camera/freeze diagnostics
prepare an Aubagne encounter, not a surveyed view or a continuous playthrough.
Ordinary starter pistol, enemy identities/health, ammunition and browser storage
are not granted or replaced. Mouse/keyboard fire and reload use production input.
v028NativeDamage invokes the real incoming-damage chain for the received-HP
display; it does not demonstrate an enemy attack. Simulation ticks and camera
placement are explicit diagnostic assistance. No randomness/network/HTML/storage
mocking; no private game variables are injected.
Scenes are rendered before transient feedback is emitted. Screenshots do not
redraw the slow 3D scene after an event; DOM visibility and real elapsed time are
recorded on both sides of each screenshot without extending feedback lifetimes.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import base64
import hashlib
import json
import math
import sys
import threading
import time
import traceback
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {'scope': __doc__, 'checks': [], 'shots': [], 'page_errors': [],
              'console_errors': [], 'request_failures': [], 'local_http_errors': [],
              'html_sha256': args.expect_html_sha, 'script_sha256': sha(Path(__file__)),
              'html_injected': False, 'network_mocked': False, 'storage_mocked': False,
              'randomness_mocked': False, 'stage': 'starting'}
    started = time.monotonic()
    server = browser = context = pw = worker = None
    pins = {str(p): sha(ROOT/p) for p in map(Path, [
        'index.html', 'JOUER_FALLOUT_MISTRAL_v0.50.html', 'src/game.js',
        'src/v050/19_fps_hud.js', 'src/v050/17_first_person.js',
        'tests/expansion/fps_feedback_native.py', 'tools/serve_game.py'])}

    def save():
        report.update(passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']),
                      elapsed_seconds=round(time.monotonic()-started, 3), pinned_inputs=pins)
        (args.output/'FPS_FEEDBACK_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ')+name, flush=True)
        save()
        if not ok:
            raise AssertionError(name)

    def debug(name, *values):
        return page.evaluate('([name,args])=>__MISTRAL_DEBUG[name](...args)', [name, list(values)])

    def feedback():
        return debug('v056HudInfo')['feedback']

    def enemy():
        return next(e for e in debug('v020Stats')['enemy'] if e['id'] == 'roux-hunter')

    def tick(n=1, simulate=False):
        page.evaluate('([n,sim])=>{for(let i=0;i<n;i++)__MISTRAL_DEBUG.v020Tick(.05,sim);}', [n, simulate])

    def capture_dom():
        return page.evaluate('''() => {
            const ids={hit:'fps57Hit',hurt:'fps57Hurt',subtitle:'subtitle',reload:'v018ReloadProgress'};
            const elements={};
            for(const [key,id] of Object.entries(ids)) {
                const el=document.getElementById(id),r=el?.getBoundingClientRect();
                let visible=!!el&&!!r&&r.width>0&&r.height>0;
                for(let node=el;visible&&node;node=node.parentElement) {
                    const s=getComputedStyle(node);
                    visible=s.display!=='none'&&s.visibility!=='hidden'&&s.visibility!=='collapse'&&s.opacity!=='0'&&!node.hidden;
                }
                elements[key]={visible,text:el?.textContent||'',rect:r?{x:r.x,y:r.y,width:r.width,height:r.height}:null};
            }
            const now=performance.now(),feedback=__MISTRAL_DEBUG.v056HudInfo().feedback;
            return {performance_now_ms:now,epoch_ms:Date.now(),elements,
                feedback_remaining_ms:{hit:feedback.hit?feedback.hit.until-now:null,hurt:feedback.hurt?feedback.hurt.until-now:null}};
        }''')

    def shot(name, expected=()):
        # The 3D scene is already rendered before the real transient event.
        # Rendering it here can outlast the production 750 ms hit lifetime.
        path = args.output/(name+'.png')
        before = capture_dom()
        screenshot_started = time.monotonic()
        raster = cdp.send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True,
                                                   'captureBeyondViewport': False,
                                                   'optimizeForSpeed': True})
        path.write_bytes(base64.b64decode(raster['data']))
        screenshot_seconds = time.monotonic()-screenshot_started
        after = capture_dom()
        observation = {'file': path.name, 'sha256': sha(path),
                       'expected_visible_elements': list(expected),
                       'dom_before': before, 'dom_after': after,
                       'screenshot_elapsed_seconds': screenshot_seconds,
                       'capture_method': 'Chromium Page.captureScreenshot of the unmodified viewport, lossless PNG optimizeForSpeed; no 3D redraw, clock change or transient replay between DOM observations.'}
        report['shots'].append(observation)
        save()
        if expected:
            check('Capture '+name+': expected feedback is visible immediately before the real screenshot',
                  all(before['elements'][key]['visible'] and
                      (key not in ('hit', 'hurt') or before['feedback_remaining_ms'][key] > 0)
                      for key in expected), observation)

    def free_lock():
        page.evaluate('document.exitPointerLock()')
        page.wait_for_function('!document.pointerLockElement')

    def lock():
        if not page.evaluate('!!document.pointerLockElement'):
            page.locator('#gameCanvas').click(position={'x': 710, 'y': 410})
            page.wait_for_function("document.pointerLockElement===document.getElementById('gameCanvas')")

    try:
        check('On-disk production HTML has expected identity', pins['index.html'] == pins['JOUER_FALLOUT_MISTRAL_v0.50.html'] == args.expect_html_sha)
        (args.output/'EXECUTED_FPS_FEEDBACK_NATIVE.py').write_bytes(Path(__file__).read_bytes())
        sys.path.insert(0, str(ROOT/'tools'))
        from serve_game import GameHandler
        from qa_support import chromium_path
        from playwright.sync_api import sync_playwright

        class Handler(GameHandler):
            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f'http://127.0.0.1:{server.server_port}'
        report['origin'] = origin
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        report['browser_version'] = browser.version
        context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
        page = context.new_page()
        cdp = context.new_cdp_session(page)
        page.on('pageerror', lambda e: report['page_errors'].append(str(e)))
        page.on('console', lambda e: report['console_errors'].append(e.text) if e.type == 'error' else None)
        page.on('requestfailed', lambda q: report['request_failures'].append({'url': q.url, 'failure': q.failure}))
        page.on('response', lambda q: report['local_http_errors'].append({'url': q.url, 'status': q.status}) if q.url.startswith(origin+'/') and q.status >= 400 else None)
        page.on('dialog', lambda d: d.accept())
        response = page.goto(origin+'/index.html?skipboot', wait_until='load', timeout=90000)
        check('HTTP serves exact frozen production HTML', response.status == 200 and hashlib.sha256(response.body()).hexdigest() == args.expect_html_sha)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v056HudInfo==='function'", timeout=120000)
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        debug('v020Load', 'aubagne')
        debug('v046SetTime', 12)
        debug('v018CaptureAt', [0, 1.65, 85], 0, 0)
        check('Starter pistol and living authored hostile are unmodified', debug('getState')['player']['weaponId'] == 'pistol10' and enemy()['hp'] == 70 and enemy()['alive'])
        check('Fresh play has no invented damage or hit receipt', feedback()['hit'] is None and feedback()['hurt'] is None and not page.locator('#fps57Hit').is_visible())
        # Aim well above the scene to exercise a real emitted miss.
        debug('v018CaptureAt', [0, 1.65, 85], 0, 1.2)
        lock()
        before = debug('v020Combat')
        page.mouse.click(710, 410)
        after = debug('v020Combat')
        check('Native left click emits one ordinary shot and spends one round', after['shots'] == before['shots']+1 and after['ammo'] == before['ammo']-1)
        check('An actual miss creates no positive confirmation', feedback()['hit'] is None and not page.locator('#fps57Hit').is_visible() and enemy()['hp'] == 70)
        tick(8)
        free_lock()
        debug('v018CaptureAt', [0, 1.65, 85], 0, 0)
        debug('v046Render')
        page.keyboard.press('r')
        remaining = debug('v020Combat')['reload']
        check('Native R starts the real reload and captures its complete adjusted duration', remaining > 0 and abs(feedback()['reloadTotal']-remaining) < 1e-8)
        tick(8, True)
        meter = page.locator('#v018ReloadProgress')
        partial = feedback()['reloadProgress']
        check('Reload bar follows the active timer and exposes a truthful accessible value', 0 < partial < 100 and meter.get_attribute('role') == 'progressbar' and abs(float(meter.get_attribute('aria-valuenow'))-partial) <= .5 and meter.is_visible())
        check('Reload hint includes the actual remaining seconds', 'RECHARGEMENT' in page.locator('#reloadHint').inner_text() and ' s' in page.locator('#reloadHint').inner_text())
        shot('01_actual_reload_progress', ('reload',))
        page.keyboard.press('Escape')
        paused = debug('v020Combat')['reload']
        page.wait_for_timeout(250)
        check('Real pause suspends reload instead of advancing the visual countdown', debug('v020Combat')['reload'] == paused and not page.locator('#fps57Hit').is_visible())
        page.locator('#btnResume').click()
        tick(60, True)
        check('Actual reload completion hides the bar and truthfully labels the full magazine', debug('v020Combat')['reload'] == 0 and not meter.is_visible() and page.locator('#reloadHint').inner_text() == 'CHARGEUR PLEIN')
        debug('v046Render')
        before_hp = debug('getState')['player']['hp']
        debug('v028NativeDamage', 12, 'Essai du retour de dégâts')
        lost = before_hp-debug('getState')['player']['hp']
        check('Received-damage receipt equals the real health change after armour', lost > 0 and abs(feedback()['hurt']['amount']-lost) < 1e-8 and page.locator('#fps57Hurt').is_visible(), {'lost': lost, 'receipt': feedback()['hurt']})
        check('Received-damage display contains no inferred enemy location or identity', page.locator('#fps57Hurt').inner_text().endswith(' PV') and set(feedback()['hurt']) == {'amount', 'until'})
        shot('02_actual_received_damage', ('hurt', 'subtitle'))
        page.keyboard.press('Tab')
        check('Opening the actual Pip-Boy clears transient damage feedback', feedback()['hurt'] is None and not page.locator('#fps57Hurt').is_visible())
        page.keyboard.press('Tab')
        target = enemy()
        idx = next(i for i, e in enumerate(debug('v020Stats')['enemy']) if e['id'] == target['id'])
        rig = debug('v025RigInfo', idx)
        aim = next(p['center'] for p in rig['parts'] if p['id'] == 'body')
        geometry = debug('worldGeometry')
        position = None
        for radius in (12, 15, 18, 21):
            for k in range(32):
                angle = k*math.tau/32
                candidate = [target['pos'][0]+math.sin(angle)*radius, 1.65, target['pos'][2]+math.cos(angle)*radius]
                raised = any(max(f.get('height', 0), f.get('startHeight', 0), f.get('endHeight', 0)) > .25 and f['minX'] <= candidate[0] <= f['maxX'] and f['minZ'] <= candidate[2] <= f['maxZ'] for f in geometry['floorZones'])
                if not raised and not debug('v020Collides', candidate) and debug('v020LOS', candidate, aim):
                    position = candidate
                    break
            if position:
                break
        check('Existing enemy has an actual collision-free and visible supported approach', position is not None, {'position': position, 'target': aim})
        yaw = math.atan2(aim[0]-position[0], -(aim[2]-position[2]))
        pitch = math.atan2(aim[1]-position[1], math.hypot(aim[0]-position[0], aim[2]-position[2]))
        report['combat_approach'] = {'position': position, 'yaw': yaw, 'pitch': pitch, 'actor': target, 'rig': rig}
        debug('v018CaptureAt', position, yaw, pitch)
        debug('v046Render')
        lock()
        successful = False
        for attempt in range(8):
            tick(8)
            old = enemy()
            page.mouse.click(710, 410)
            current = enemy()
            if current['hp'] < old['hp']:
                received = min(max(0, old['hp']), max(0, old['hp'])-max(0, current['hp']))
                receipt = feedback()['hit']
                check('Positive hit confirmation reports applied damage on the unchanged actor', receipt is not None and abs(receipt['damage']-received) < 1e-6 and receipt['targets'] == 1 and page.locator('#fps57Hit').is_visible(), {'before': old, 'after': current, 'receipt': receipt})
                if not successful:
                    shot('03_actual_hit_confirmation', ('hit',))
                successful = True
                if not current['alive']:
                    check('Neutralisation label requires an actual living-to-dead enemy transition', receipt['kills'] == 1 and page.locator('#fps57Hit b').inner_text() == 'NEUTRALISÉ')
                    shot('04_actual_neutralisation', ('hit',))
                    break
        check('Ordinary native shots hit and neutralise the original hostile without health edits', successful and not enemy()['alive'] and enemy()['hp'] <= 0)
        free_lock()
        page.wait_for_timeout(800)
        check('Hit confirmation expires without retaining a permanent target marker', not page.locator('#fps57Hit').is_visible())
        before_hp = debug('getState')['player']['hp']
        debug('v028Settings', {'reducedFlashes': True, 'reduceMotion': True})
        debug('v028NativeDamage', 2, 'Essai sobre')
        check('Reduced-flash setting retains readable static damage text', debug('getState')['player']['hp'] < before_hp and page.locator('#fps57Hurt').is_visible() and 'fps57-reduced-flashes' in page.locator('#hud').get_attribute('class'))
        for width, height in ((1440, 900), (1024, 768), (390, 844), (844, 390)):
            page.set_viewport_size({'width': width, 'height': height})
            debug('v018CaptureAt', [0, 1.65, 85], 0, 0)
            debug('v046Render')
            debug('v028NativeDamage', 1, 'Retour de dégâts')
            page.wait_for_timeout(150)
            delta = page.locator('#fps57Hurt').bounding_box()
            label = f'Actual feedback {width}x{height}'
            check(label+': damage receipt stays inside the viewport', delta is not None and delta['x'] >= 0 and delta['y'] >= 0 and delta['x']+delta['width'] <= width and delta['y']+delta['height'] <= height)
            rectangles = {key: page.locator('#'+key).bounding_box() for key in ('subtitle', 'statusBars', 'weaponHud')}
            def overlaps(a, b):
                return min(a['x']+a['width'], b['x']+b['width']) > max(a['x'], b['x'])+1 and min(a['y']+a['height'], b['y']+b['height']) > max(a['y'], b['y'])+1
            check(label+': actual damage subtitle remains visible without covering health or ammunition', page.locator('#subtitle').is_visible() and all(not overlaps(rectangles['subtitle'], rectangles[k]) for k in ('statusBars', 'weaponHud')), rectangles)
            shot(f'05_actual_feedback_{width}x{height}', ('hurt', 'subtitle'))
        debug('v020Load', 'marseille')
        check('Changing actual scene clears hit and health receipts', feedback()['hit'] is None and feedback()['hurt'] is None and not page.locator('#fps57Hit').is_visible() and not page.locator('#fps57Hurt').is_visible())
        check('No native JavaScript exception or same-origin HTTP error', not report['page_errors'] and not report['local_http_errors'])
        local_failures = [f for f in report['request_failures'] if urlsplit(f['url']).hostname in ('127.0.0.1', 'localhost', '::1')]
        external_failures = [f for f in report['request_failures'] if f not in local_failures]
        check('Raw network diagnostics contain only cancelled metadata or the known optional external relay', all(urlsplit(f['url']).path == '/__mistral/local-data' and f['failure'] == 'net::ERR_ABORTED' for f in local_failures) and all((urlsplit(f['url']).hostname or '').endswith('.supabase.co') for f in external_failures), report['request_failures'])
        check('No application console error accompanies the retained network diagnostics', all(e == 'Failed to load resource: net::ERR_TUNNEL_CONNECTION_FAILED' for e in report['console_errors']) and (not report['console_errors'] or bool(external_failures)), report['console_errors'])
        check('Exact production and pilot input bytes remain unchanged', all(sha(ROOT/p) == h for p, h in pins.items()))
        report['stage'] = 'complete'
    except Exception as error:
        report.update(stage='failed', error=repr(error), traceback=traceback.format_exc())
        print(report['traceback'], flush=True)
        if 'page' in locals():
            try:
                shot('failure')
            except Exception:
                pass
    finally:
        for obj in (context, browser):
            if obj:
                obj.close()
        if pw:
            pw.stop()
        if server:
            server.shutdown()
            server.server_close()
        if worker:
            worker.join(timeout=5)
        report['cleanup'] = {'context_closed': True, 'browser_closed': True, 'playwright_stopped': True, 'server_closed': True}
        save()
    return int(report['stage'] != 'complete')


if __name__ == '__main__':
    raise SystemExit(main())
