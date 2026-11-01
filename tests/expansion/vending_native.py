#!/usr/bin/env python3
"""Native finite Nuka-Cola cabinet loop on exact production HTML.

Existing diagnostic navigation and frozen collision/LOS-checked cameras select
authored Aubagne/Marseille and an actual installed Huveaune relay. Payment
capsules and repair materials are prepared explicitly, never bottles, cabinet
state, merchant stock, actors, source geometry or save contents. E, visible DOM
buttons, keyboard focus and the real Continue button perform the game actions.
Portrait is an emulated viewport, not a hardware touchscreen certification.
No HTML, network, storage or production function replacement is used.
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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inverse_lambert(x, y):
    e, n, c = .0818191910428158, .725607765053267, 11754255.426096
    value = -math.log(math.hypot(x-700000, 12655612.049876-y)/c)/n
    phi = 2*math.atan(math.exp(value))-math.pi/2
    for _ in range(12):
        phi = 2*math.atan(math.exp(value)*((1+e*math.sin(phi))/(1-e*math.sin(phi)))**(e/2))-math.pi/2
    return [math.degrees(phi), 3+math.degrees(math.atan2(x-700000, 12655612.049876-y)/n)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    parser.add_argument('--expect-vending-sha', required=True)
    args = parser.parse_args()
    if not args.run:
        print('Prepared; no server/browser started. Coordinate frozen hashes before --run.')
        return 0
    sys.path.insert(0, str(ROOT/'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {'scope': __doc__, 'stage': 'preflight', 'checks': [], 'shots': [], 'placements': [],
              'pinned_inputs': {}, 'page_errors': [], 'console_errors': [], 'request_failures': [],
              'http_errors': [], 'responses': [], 'html_sha256': args.expect_html_sha,
              'html_injected': False, 'network_mocked': False, 'storage_mocked': False,
              'synthetic_geography': False, 'service_workers_disabled': True,
              'assistance': ['v020Load selects existing authored scenes without item grants.',
                             'v020Seed supplies 500 capsules, 6 scrap and 3 circuitry only; no bottles or cabinet state are granted.',
                             'v046SetTime(12), render pause and v018CaptureAt freeze normal simulation for reproducible inspections.',
                             'v018LoadMacro/v046Load select an actual installed Huveaune sector; v042Update materializes the existing safe catalog relay.',
                             'Camera approaches are selected only after actual production body collision and LOS checks. Geographic camera heights come from the actual source terrain.',
                             'One viewport is resized to 390x844 to test responsive controls; this is not physical mobile input.'],
              'limitations': ['Two authored original game cabinets, not surveyed historical street furniture.',
                              'Native validation visits the Aubagne geographic counterpart. Marseille municipal alias is a controlled production-model contract.',
                              'The cabinet model is original stylized geometry, not a commercial Fallout asset.'], 'cleanup': {}}
    server = worker = browser = context = pw = page = None

    def save():
        report.update(passed=sum(x['ok'] for x in report['checks']), failed=sum(not x['ok'] for x in report['checks']),
                      total=len(report['checks']), elapsed_seconds=round(time.monotonic()-started, 3))
        (args.output/'VENDING_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ')+name, flush=True)
        save()
        if not ok:
            raise AssertionError(name)

    def pin(relative):
        raw = (ROOT/relative).read_bytes()
        digest = sha(raw)
        if relative in report['pinned_inputs'] and report['pinned_inputs'][relative] != digest:
            raise AssertionError('Frozen input changed: '+relative)
        report['pinned_inputs'][relative] = digest
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def state():
        return debug('getState')

    def info():
        return debug('v057VendingInfo')

    def mode():
        return debug('v020Stats')['mode']

    def freeze():
        p = state()['player']
        debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])

    def document(response):
        check('Native HTTP document equals frozen production HTML', response is not None and response.status == 200
              and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v057VendingInfo==='function'", timeout=60000)
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        freeze()

    def shot(name, label):
        freeze()
        path = args.output/(name+'.png')
        page.screenshot(path=str(path))
        report['shots'].append({'file': path.name, 'sha256': sha(path.read_bytes()), 'label': label,
                                'method': 'Actual unchanged production frame, declared diagnostic freeze/camera; no image editing.'})
        save()

    def click(action):
        button = page.locator('#vending57 button[data-v57='+json.dumps(action)+']')
        check('Visible enabled real cabinet control: '+action, button.count() == 1 and button.is_visible() and button.is_enabled())
        button.click()

    def ready():
        deadline = time.monotonic()+240
        while time.monotonic() < deadline:
            r = debug('v047Info')
            if r['phase'] == 'failed':
                raise RuntimeError(json.dumps(r))
            if r['tiles'] > 0 and not r['loading'] and not r['anticipating']:
                return r
            page.wait_for_timeout(200)
        raise TimeoutError('Actual geographic source readiness')

    def authored(scene):
        result = debug('v020Load', scene)
        check('Actual authored scene loads without cabinet grants: '+scene, result['id'] == scene)
        freeze()
        physical = info()['physical']
        check('One real physical cabinet is bound in '+scene, len(physical) == 1 and physical[0]['id'] == scene, physical)
        return physical[0]

    def approach(e, geographic_frame=None, activate=True):
        target = e['interaction']
        for radius in (1.95, 1.65, 1.35, 2.05):
            for angle in (0, -.20, .20, -.4, .4, -.6, .6):
                x = target[0]+math.sin(angle)*radius
                z = target[2]+math.cos(angle)*radius
                ground = None
                if geographic_frame:
                    ll = inverse_lambert(x+geographic_frame[0], geographic_frame[1]-z)
                    ground = debug('v046Height', *ll)
                    if ground.get('missing') or not isinstance(ground.get('height'), (int, float)) or not math.isfinite(ground['height']):
                        continue
                    height = ground['height']
                else:
                    height = e['pos'][1]
                position = [x, height+1.65, z]
                if debug('v020Collides', position) or not debug('v020LOS', position, target):
                    continue
                yaw = math.atan2(target[0]-position[0], -(target[2]-position[2]))
                pitch = math.atan2(target[1]-position[1], math.hypot(target[0]-position[0], target[2]-position[2]))
                debug('v018CaptureAt', position, yaw, pitch)
                actual = page.locator('#interactLabel').inner_text()
                current = next((r for r in info()['physical'] if r['id'] == e['id']), None)
                if not current or not current['usable'] or 'distributeur' not in actual.casefold():
                    continue
                report['placements'].append({'position': position, 'target': target, 'yaw': yaw, 'pitch': pitch,
                                              'actual_label': actual, 'ground': ground, 'source': 'Production collider/LOS and real cabinet interaction, not a fabricated actor or source.'})
                check('Actual body collision and LOS admit native E on '+e['id'], True, report['placements'][-1])
                if activate:
                    page.keyboard.press('e')
                    check('Native E opens the real cabinet modal', mode() == 'VENDING57' and page.locator('#vending57').is_visible())
                return
        check('Actual body collision and LOS admit native E on '+e['id'], False, {'cabinet': e, 'info': info()})

    try:
        raw = pin('index.html')
        module = pin('src/v050/20_iconic_vending.js')
        check('Exact new cabinet source is embedded in frozen HTML', sha(raw) == args.expect_html_sha
              and sha(module) == args.expect_vending_sha and module.strip() in raw)
        for relative in ['src/v050/12_iconic_ecosystem.js', 'src/v050/06_controller.js', 'src/v050/19_fps_hud.js',
                         'src/core-v017.js', 'tools/serve_game.py', 'data/map_pack/enrichment/index.json']:
            data = pin(relative)
            if relative.startswith('src/v050/'):
                check('Actual dependency is embedded in production: '+relative, data.strip() in raw)
        script = Path(__file__).read_bytes()
        (args.output/'EXECUTED_VENDING_NATIVE.py').write_bytes(script)
        report['script_sha256'] = sha(script)
        class Handler(GameHandler):
            def log_message(self, *_args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin+'/index.html?skipboot'
        with urllib.request.urlopen(origin+'/__mistral/local-data', timeout=300) as response:
            audit = json.load(response)
        check('Actual local source pack audits complete before native bootstrap', audit['complete'] is True)
        report['local_pack_audit'] = audit
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        report['browser_version'] = browser.version
        context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
        page.on('console', lambda msg: report['console_errors'].append({'text': msg.text, 'location': msg.location}) if msg.type == 'error' else None)
        page.on('requestfailed', lambda r: report['request_failures'].append({'url': r.url, 'failure': r.failure,
                    'stage': report['stage'], 'elapsed_seconds': round(time.monotonic()-started, 3)}))
        def response_seen(response):
            if not response.url.startswith(origin+'/'):
                return
            record = {'url': response.url, 'status': response.status, 'stage': report['stage']}
            report['responses'].append(record)
            if response.status >= 400:
                report['http_errors'].append(record)
            relative = urllib.parse.unquote(urllib.parse.urlsplit(response.url).path).lstrip('/')
            local = (ROOT/relative).resolve()
            if relative.startswith('data/map_pack/') and local.is_relative_to(ROOT) and local.is_file():
                pin(str(local.relative_to(ROOT)))
        page.on('response', response_seen)
        page.on('dialog', lambda dialog: dialog.accept())
        report['stage'] = 'authored-aubagne'
        document(page.goto(report['url'], wait_until='load', timeout=90000))
        e = authored('aubagne')
        debug('v046SetTime', 12)
        check('Fresh finite reserve starts broken without granting a bottle', not info()['ledger']['cabinets']['aubagne']['repaired']
              and info()['ledger']['cabinets']['aubagne']['stock'] == {'nukaCola': 3, 'nukaQuantum': 1}
              and state()['inventory'].get('nukaCola', 0) == 0 and state()['inventory'].get('nukaQuantum', 0) == 0)
        debug('v020Seed', {'caps': 500, 'scrap': 6, 'circuitry': 3})
        approach(e, activate=False)
        shot('01_authored_cabinet', 'Modèle original dans la scène narrative d’Aubagne ; position inventée, approche physique réelle.')
        page.keyboard.press('e')
        check('Native E presents finite stock and disabled unpaid controls', mode() == 'VENDING57'
              and page.locator('[data-v57="nukaCola"]').is_disabled()
              and page.locator('[data-v57="nukaQuantum"]').is_disabled())
        shot('02_broken_power_and_stock', 'Avant réparation : fournitures nécessaires et réserves finies réelles.')
        before = state()
        for key in ('Tab', 'Shift+Tab', 'p', 'n', 'v', 'w', 'r'):
            page.keyboard.press(key)
        paused = state()
        check('Tab traverses the modal and world hotkeys spend or move nothing', mode() == 'VENDING57'
              and paused['inventory'] == before['inventory'] and paused['player']['pos'] == before['player']['pos']
              and paused['v057Vending'] == before['v057Vending'] and paused['v055Ordnance'] == before['v055Ordnance']
              and paused['v056Mines'] == before['v056Mines'])
        check('Actual Tab focus remains within the modal', page.evaluate("document.querySelector('#vending57').contains(document.activeElement)"))
        click('repair')
        repaired = state()
        check('Actual repair debits precisely two scrap and one circuit once', repaired['inventory']['scrap'] == before['inventory']['scrap']-2
              and repaired['inventory']['circuitry'] == before['inventory']['circuitry']-1
              and repaired['player']['caps'] == before['player']['caps'] and repaired['v057Vending']['cabinets']['aubagne']['repaired'])
        check('Repaired cabinet removes repeated repair and enables finite purchases', page.locator('[data-v57="repair"]').count() == 0
              and page.locator('[data-v57="nukaCola"]').is_enabled() and page.locator('[data-v57="nukaQuantum"]').is_enabled())
        bottle_count = repaired['inventory'].get('nukaCola', 0)
        click('nukaCola')
        bought = state()
        check('Actual bottle purchase debits 30 caps and exactly one finite reserve', bought['player']['caps'] == repaired['player']['caps']-30
              and bought['inventory']['nukaCola'] == bottle_count+1 and bought['v057Vending']['cabinets']['aubagne']['stock']['nukaCola'] == 2)
        click('nukaQuantum')
        quantum = state()
        check('Actual Quantum purchase debits 65 caps and exhausts only its one original bottle', quantum['player']['caps'] == bought['player']['caps']-65
              and quantum['inventory']['nukaQuantum'] == 1 and quantum['v057Vending']['cabinets']['aubagne']['stock']['nukaQuantum'] == 0
              and page.locator('[data-v57="nukaQuantum"]').is_disabled())
        shot('03_paid_stock', 'Paiements et épuisement du Quantum appliqués à l’inventaire ordinaire.')
        page.keyboard.press('Escape')
        check('Native Escape closes and restores focus to the actual game canvas', mode() == 'PLAYING'
              and page.locator('#vending57').is_hidden() and page.evaluate("document.activeElement.id==='gameCanvas'"))
        page.keyboard.press('Tab')
        check('Native Tab opens the ordinary Pip-Boy after the cabinet closes', mode() == 'PIP')
        page.locator('#pipboy [data-p27="tab"][data-arg="inventory"]').click()
        page.locator('#pipboy [data-p27="sub"][data-arg="aid"]').click()
        check('Paid bottles appear in ordinary inventory and existing aid category', debug('v027UI')['sub'] == 'aid'
              and all(page.locator('#pipContent .p27-row[data-arg='+json.dumps(item)+']').is_visible()
                      and state()['inventory'].get(item, 0) == 1 for item in ('nukaCola', 'nukaQuantum')))
        # Consumption uses the visible existing inventory detail, with no direct
        # use helper or bottle grant. The corresponding read-only state proves
        # the actual dose and capsule effects.
        page.locator('.p27-row[data-arg="nukaCola"]').click()
        use = page.locator('#pipContent [data-p27="use"][data-arg="nukaCola"]')
        check('Ordinary existing aid control can consume the paid bottle', use.count() == 1 and use.is_enabled())
        pre_drink = state()
        use.click()
        drink = state()
        check('Consumption spends the paid bottle and returns exactly its existing one cap', drink['inventory']['nukaCola'] == pre_drink['inventory']['nukaCola']-1
              and drink['player']['caps'] == pre_drink['player']['caps']+1 and drink['v053Iconic']['drinks'] == pre_drink['v053Iconic']['drinks']+1
              and drink['v057Vending'] == pre_drink['v057Vending'])
        page.keyboard.press('Tab')
        check('Native Tab leaves ordinary inventory back to playing', mode() == 'PLAYING')
        authored('marseille')
        check('Separate Marseille cabinet retains its own broken four-plus-one reserve', info()['ledger']['cabinets']['marseille'] == {'repaired': False, 'stock': {'nukaCola': 4, 'nukaQuantum': 1}})
        e = authored('aubagne')
        approach(e)
        check('Returning to the authored scene retains repair and prior paid stock', info()['ledger']['cabinets']['aubagne']['repaired']
              and info()['ledger']['cabinets']['aubagne']['stock'] == {'nukaCola': 2, 'nukaQuantum': 0})
        click('nukaCola')
        click('nukaCola')
        check('The last two ordinary purchases exhaust the finite cabinet', info()['ledger']['cabinets']['aubagne']['stock'] == {'nukaCola': 0, 'nukaQuantum': 0}
              and page.locator('[data-v57="nukaCola"]').is_disabled())
        click('close')
        saved = state()
        report['before_continue'] = saved
        report['stage'] = 'real-continue'
        document(page.reload(wait_until='load', timeout=90000))
        check('Real Continue is enabled for the cabinet checkpoint', page.locator('#btnContinue').is_enabled())
        page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='aubagne'", timeout=120000)
        freeze()
        restored = state()
        report['after_continue'] = restored
        check('Native Continue preserves exact paid stock, bag and capsule wallet', restored['v057Vending'] == saved['v057Vending']
              and restored['inventory'] == saved['inventory'] and restored['player']['caps'] == saved['player']['caps'])
        check('Continue preserves all existing iconic, ordnance, mine and lore ledgers', all(restored[k] == saved[k] for k in ('v053Iconic', 'v055Ordnance', 'v056Mines', 'v053Lore', 'v030')))
        e = info()['physical'][0]
        approach(e)
        check('Continued cabinet exposes no repeat repair or free replenishment', page.locator('[data-v57="repair"]').count() == 0
              and page.locator('[data-v57="nukaCola"]').is_disabled() and page.locator('[data-v57="nukaQuantum"]').is_disabled())
        shot('04_exhausted_after_continue', 'Même réserve vide et alimentation rétablie après rechargement natif et Continuer.')
        click('close')
        report['stage'] = 'actual-geographic-counterpart'
        target = next(r for r in debug('v057VendingCatalog') if r['id'] == 'aubagne')
        site = debug('v042Site', target['siteId'])
        check('Counterpart belongs to an actual existing safe geographic relay', site['safe'] is True and site['macro'] == 'geo_huveaune', site)
        check('Actual metric Huveaune world is selected without laboratory or fixture', debug('v018LoadMacro', 'geo_huveaune') == 'geo_huveaune')
        ready()
        check('Actual installed counterpart sector is requested', debug('v046Load', site['lat'], site['lon']) is True)
        ready()
        points = [[site['lat']+dz/111320, site['lon']+dx/(111320*math.cos(math.radians(site['lat'])))]
                  for dz in range(-70, 71, 10) for dx in range(-70, 71, 10)]
        candidates = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,h,clear:Number.isFinite(h.height)&&!h.missing&&!d.v020Collides([p[0],h.height+1.65,p[2]])};}).filter(p=>p.clear);}""", points)
        check('Real source sector supplies at least one clear finite terrain arrival', bool(candidates))
        candidates.sort(key=lambda p: abs(p['ll'][0]-site['lat'])+abs(p['ll'][1]-site['lon']))
        candidate = candidates[0]
        debug('v018CaptureAt', [candidate['p'][0], candidate['h']['height']+1.65, candidate['p'][2]], 0, 0)
        debug('v042Update', .71)
        debug('v057VendingBind')
        check('Existing safe relay actually streams in the real source world', site['id'] in debug('v042Runtime')['active'])
        geo = info()['physical']
        check('Actual supported geographic cabinet binds the same exhausted identity', len(geo) == 1 and geo[0]['id'] == 'aubagne'
              and info()['ledger']['cabinets']['aubagne'] == saved['v057Vending']['cabinets']['aubagne'], {'physical': geo, 'sources': debug('v046Info')})
        projection = debug('v046Project', 'geo_huveaune', site['lat'], site['lon'])
        absolute = debug('v018Projection', site['lat'], site['lon'])['xy']
        frame = [absolute[0]-projection[0], absolute[1]+projection[2]]
        approach(geo[0], geographic_frame=frame, activate=False)
        shot('05_real_geographic_counterpart', 'Distributeur inventé posé sur un support source réellement validé au relais géographique ; identité et stock communs.')
        page.keyboard.press('e')
        check('Real geographic E opens the same exhausted paid stock without another repair', mode() == 'VENDING57'
              and page.locator('[data-v57="repair"]').count() == 0 and page.locator('[data-v57="nukaCola"]').is_disabled())
        click('close')
        report['stage'] = 'portrait-marseille-cabinet'
        e = authored('marseille')
        approach(e)
        page.set_viewport_size({'width': 390, 'height': 844})
        bounds = page.evaluate("""()=>{const e=document.getElementById('vending57'),r=e.getBoundingClientRect();return{left:r.left,top:r.top,right:r.right,bottom:r.bottom,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,buttons:[...e.querySelectorAll('button')].map(b=>{const r=b.getBoundingClientRect();return{width:r.width,height:r.height,disabled:b.disabled};})};}""")
        check('Portrait real modal stays inside viewport with no horizontal overflow and large buttons', bounds['left'] >= 0
              and bounds['right'] <= 390 and bounds['top'] >= 0 and bounds['bottom'] <= 844
              and bounds['scrollWidth'] <= bounds['clientWidth'] and all(b['height'] >= 44 for b in bounds['buttons']), bounds)
        shot('06_portrait_marseille_reserve', 'Format390×844 émulé, seconde machine avec son stock propre ; aucun appareil mobile physique certifié.')
        page.keyboard.press('Escape')
        check('Portrait Escape closes the second cabinet and restores game focus', mode() == 'PLAYING'
              and page.locator('#vending57').is_hidden() and page.evaluate("document.activeElement.id==='gameCanvas'"))
        check('No JavaScript page exception or failed local HTTP resource', not report['page_errors'] and not report['http_errors'],
              {'page_errors': report['page_errors'], 'http_errors': report['http_errors']})
        local = [r for r in report['request_failures'] if r['url'].startswith(origin+'/')]
        metadata = [r for r in local if urllib.parse.urlsplit(r['url']).path == '/__mistral/local-data' and r['failure'] == 'net::ERR_ABORTED']
        report['local_metadata_cancellations'] = metadata
        unexpected = [r for r in local if r not in metadata]
        check('No unexpected local source request failure', not unexpected, unexpected)
        for relative in list(report['pinned_inputs']):
            pin(relative)
        check('Every observed production/source input stayed byte-identical during native run', True)
        report['stage'] = 'complete'
    except Exception as error:
        report['exception'], report['traceback'] = str(error), traceback.format_exc()
        report['stage'] = 'failed'
        if page:
            try:
                shot('failure', 'Échec brut conservé pour diagnostic ; ne valide aucun parcours.')
            except Exception:
                pass
        print(report['traceback'], flush=True)
        return 1
    finally:
        for label, item in [('context', context), ('browser', browser), ('playwright', pw)]:
            if item:
                try:
                    item.stop() if label == 'playwright' else item.close()
                    report['cleanup'][label+'_closed'] = True
                except Exception as error:
                    report['cleanup'][label+'_error'] = str(error)
        if server:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)
            report['cleanup']['server_closed'] = True
            report['cleanup']['worker_stopped'] = not worker.is_alive()
        save()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
