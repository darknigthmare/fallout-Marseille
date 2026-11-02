#!/usr/bin/env python3
"""Native collection of three original regional holobands on frozen production HTML.

The existing diagnostic scene selector and collision/LOS-checked camera positions
are declared assistance. No inventory, collection flag, quest proof or bookmark
is granted. Native E, existing RADIO/HOLODISQUES buttons and the actual Continue
button perform collection, playback, cold resume and finite-counterpart checks.
The geographic sector uses real installed HTTP sources. Render/camera freezing
and a 390x844 viewport remain diagnostics, not a human or physical-mobile test.
No production function, HTML, network response or browser storage is replaced.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import math
import re
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
    parser.add_argument('--expect-holotapes-sha', required=True)
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
              'assistance': ['v020Load selects existing authored scenes; no supplies or collection flags are granted.',
                             'v046SetTime(12), setRenderPaused and v018CaptureAt freeze normal simulation for reproducible inspections.',
                             'v018LoadMacro/v046Load and v042Update select and materialize an actual installed safe Huveaune relay.',
                             'Each camera position is admitted by actual body collision and line-of-sight functions; geographic height uses the native source terrain.',
                             'The same viewport is resized to 390x844; this does not certify physical mobile hardware.'],
              'limitations': ['Three invented models, placements and original transcriptions, not surveyed street furniture or recovered recordings.',
                              'Native geography checks the first band’s actual Huveaune counterpart. The Marseille commune alias has separate controlled model coverage.',
                              'The maintained timed reader is reused without any recorded voice. Assisted camera placement is not an exhaustive human playthrough.'], 'cleanup': {}}
    server = worker = browser = context = pw = page = None

    def save():
        report.update(passed=sum(x['ok'] for x in report['checks']), failed=sum(not x['ok'] for x in report['checks']),
                      total=len(report['checks']), elapsed_seconds=round(time.monotonic()-started, 3))
        (args.output/'HOLOTAPES_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

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
        return debug('v058HolotapesInfo')

    def mode():
        return debug('v020Stats')['mode']

    def freeze():
        p = state()['player']
        debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])

    def document(response):
        check('Native HTTP document equals frozen production HTML', response is not None and response.status == 200
              and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v058HolotapesInfo==='function'", timeout=60000)
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

    def click(selector, label):
        button = page.locator(selector)
        check('Visible enabled existing reader control: '+label, button.count() == 1 and button.is_visible() and button.is_enabled())
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

    def authored(scene, identity):
        result = debug('v020Load', scene)
        check('Actual authored scene loads without holoband grants: '+scene, result['id'] == scene)
        freeze()
        physical = info()['physical']
        entry = next((t for t in physical if t['id'] == identity), None)
        check('Real physical holoband is bound in '+scene, entry is not None, physical)
        return entry

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
                if not current or not current['usable'] or 'holobande' not in actual.casefold():
                    continue
                report['placements'].append({'position': position, 'target': target, 'yaw': yaw, 'pitch': pitch,
                                              'actual_label': actual, 'ground': ground, 'source': 'Production collider/LOS and real holoband interaction, not a fabricated actor or source.'})
                check('Actual body collision and LOS admit native E on '+e['id'], True, report['placements'][-1])
                if activate:
                    before = state()
                    page.keyboard.press('e')
                    check('Native E collects the actual finite holoband', e['id'] in info()['found'] and mode() == 'PLAYING'
                          and state()['inventory'] == before['inventory'] and state()['player']['caps'] == before['player']['caps'])
                return
        check('Actual body collision and LOS admit native E on '+e['id'], False, {'holoband': e, 'info': info()})

    try:
        raw = pin('index.html')
        module = pin('src/v050/21_holotapes.js')
        check('Exact holoband source is embedded in frozen HTML', sha(raw) == args.expect_html_sha
              and sha(module) == args.expect_holotapes_sha and module.strip() in raw)
        for relative in ['src/v050/12_iconic_ecosystem.js', 'src/v050/20_iconic_vending.js', 'src/v027/04_map_radio.js',
                         'src/core-v017.js', 'tools/serve_game.py', 'data/map_pack/enrichment/index.json']:
            data = pin(relative)
            if relative.startswith('src/v050/'):
                check('Actual dependency is embedded in production: '+relative, data.strip() in raw)
        script = Path(__file__).read_bytes()
        (args.output/'EXECUTED_HOLOTAPES_NATIVE.py').write_bytes(script)
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
        first, second, third = 'h58-atelier-releve', 'h58-deux-colonnes', 'h58-canal13-veille'
        e = authored('aubagne', first)
        debug('v046SetTime', 12)
        original = state()
        report['initial_legacy_holodiscs'] = {k: v for k, v in original['lore']['holotapes'].items() if not k.startswith('h58-')}
        check('All three new finite copies start undiscovered in the existing lore owner', all(not original['lore']['holotapes'].get(i) for i in (first, second, third)))
        approach(e, activate=False)
        shot('01_authored_holoband', 'Bande et présentoir originaux dans les ateliers narratifs d’Aubagne, avec approche physique admise.')
        before = state()
        page.keyboard.press('e')
        collected = state()
        check('Native E collects only the actual first band with no supplies, caps or attribute reward', first in info()['found']
              and collected['inventory'] == before['inventory'] and collected['player']['caps'] == before['player']['caps']
              and collected['character'] == before['character'] and collected['v053Lore'] == before['v053Lore'])
        check('Successful persistence removes the same physical exemplar and never creates a parallel ledger', not info()['physical']
              and not any(k.startswith('v058') for k in collected))
        page.keyboard.press('Tab')
        check('Native Tab opens the maintained Pip-Boy', mode() == 'PIP')
        click('#pipboy [data-p27="tab"][data-arg="radio"]', 'RADIO')
        click('#pipboy [data-p27="sub"][data-arg="tapes"]', 'HOLODISQUES')
        click('#pipContent .p27-row[data-arg="'+first+'"]', 'band row')
        check('The original reader exposes the new title and full five-segment transcript', page.locator('#pipContent').inner_text().find('La relève ne tient pas dans une colonne') >= 0
              and page.locator('#pipContent .p27-transcript li').count() == 5
              and 'VOIX NON ENREGISTRÉE' in page.locator('#pipContent').inner_text())
        click('#pipContent [data-p27="tape-start"][data-arg="'+first+'"]', 'start timed transcription')
        check('Maintained playback starts without consuming the band', state()['lore']['holotapePlays'][first] == 1
              and first in info()['found'])
        click('#pipContent [data-p27="tape-pause"]', 'pause')
        click('#pipContent [data-p27="tape-step"][data-arg="1"]', 'next segment')
        check('The existing reader advances its real bookmark to segment two', state()['v018']['tapeBookmarks'][first]['index'] == 1)
        page.locator('#pipContent .p27-transcript summary').click()
        shot('02_original_transcription', 'Lecteur RADIO → HOLODISQUES existant, texte intégral original et marque-page au deuxième segment, sans voix enregistrée.')
        page.keyboard.press('Tab')
        check('Closing the real Pip-Boy returns to play and saves the bookmark', mode() == 'PLAYING' and state()['v018']['tapeBookmarks'][first]['index'] == 1)
        saved = state()
        report['before_continue'] = saved
        report['stage'] = 'real-continue'
        document(page.reload(wait_until='load', timeout=90000))
        check('Actual Continue is enabled for the collected band checkpoint', page.locator('#btnContinue').is_enabled())
        page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='aubagne'", timeout=120000)
        freeze()
        restored = state()
        report['after_continue'] = restored
        check('Cold native Continue preserves collection, plays and exact saved bookmark', restored['lore']['holotapes'] == saved['lore']['holotapes']
              and restored['lore']['holotapePlays'] == saved['lore']['holotapePlays']
              and restored['v018']['tapeBookmarks'][first] == saved['v018']['tapeBookmarks'][first])
        check('Native Continue preserves ordinary inventory, wallet, original dossiers and finite vending stock', restored['inventory'] == saved['inventory']
              and restored['player']['caps'] == saved['player']['caps'] and all(restored[k] == saved[k] for k in ('v053Lore', 'v053Iconic', 'v057Vending', 'v055Ordnance', 'v056Mines')))
        check('A continued authored scene cannot recreate or take the already collected first band', first in info()['found'] and not info()['physical'])
        report['stage'] = 'two-other-authored-bands'
        for scene, identity in [('marseille', second), ('saintcharles', third)]:
            e = authored(scene, identity)
            approach(e)
            check('Distinct authored band joins the same finite collection: '+identity, identity in info()['found'])
        page.keyboard.press('Tab')
        click('#pipboy [data-p27="tab"][data-arg="radio"]', 'RADIO')
        click('#pipboy [data-p27="sub"][data-arg="tapes"]', 'HOLODISQUES')
        check('All three physical bands are available through the actual maintained list', all(page.locator('#pipContent .p27-row[data-arg="'+i+'"]').is_visible() for i in (first, second, third)))
        click('#pipboy [data-p27="tab"][data-arg="data"]', 'DATA')
        click('#pipboy [data-p27="sub"][data-arg="legacy"]', 'historical archives')
        archive = page.locator('#pipContent [data-v13data="holotapes"]')
        label = archive.inner_text()
        historical = re.fullmatch(r'HOLODISQUES HISTORIQUES \((\d+)/(\d+)\)', label)
        old_count = sum(value is True for value in report['initial_legacy_holodiscs'].values())
        check('Historical archive keeps its own zone counter separate from the three regional bands', historical is not None
              and int(historical.group(1)) == old_count and int(historical.group(2)) >= max(1,old_count), {'label':label,'legacy_count':old_count})
        click('#pipContent [data-v13data="holotapes"]', 'historical holodisc archive')
        check('The historical archive exposes the separately collected three regional copies', 'Bandes des relais · 3/3' in page.locator('#pipContent').inner_text())
        click('#pipContent [data-h58-radio]', 'existing radio reader from archive')
        check('Archive navigation returns to the same maintained RADIO/tapes list', debug('v027UI')['tab'] == 'radio'
              and debug('v027UI')['sub'] == 'tapes' and all(page.locator('#pipContent .p27-row[data-arg="'+i+'"]').is_visible() for i in (first,second,third)))
        click('#pipContent .p27-row[data-arg="'+third+'"]', 'Canal 13 band')
        check('Canal 13 transcription does not resolve the saved faction dossiers', state()['v053Lore'] == saved['v053Lore']
              and 'Canal 13' in page.locator('#pipContent').inner_text())
        page.set_viewport_size({'width':390,'height':844})
        bounds = page.evaluate("""()=>{const e=document.getElementById('pipContent'),r=e.getBoundingClientRect();return{left:r.left,right:r.right,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,screen:innerWidth};}""")
        check('Existing reader remains within the emulated portrait viewport without horizontal overflow', bounds['left'] >= 0 and bounds['right'] <= 390
              and bounds['scrollWidth'] <= bounds['clientWidth'], bounds)
        shot('03_three_bands_portrait', 'Trois bandes réellement collectées, consultation de Canal 13 dans le Pip-Boy en format390×844 émulé.')
        page.keyboard.press('Tab')
        page.set_viewport_size({'width':1440,'height':900})
        report['stage'] = 'actual-geographic-counterpart'
        target = next(t for t in debug('v058HolotapesCatalog') if t['id'] == first)
        site = debug('v042Site', target['siteId'])
        check('Finite counterpart binds an actual safe Huveaune catalogue relay', site['safe'] is True and site['macro'] == 'geo_huveaune', site)
        check('Actual metric Huveaune world is selected without laboratory or source fixture', debug('v018LoadMacro', 'geo_huveaune') == 'geo_huveaune')
        ready()
        check('The actual installed counterpart sector is requested', debug('v046Load', site['lat'], site['lon']) is True)
        ready()
        points = [[site['lat']+dz/111320, site['lon']+dx/(111320*math.cos(math.radians(site['lat'])))]
                  for dz in range(-70,71,10) for dx in range(-70,71,10)]
        candidates = page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{ll,p,h,clear:Number.isFinite(h.height)&&!h.missing&&!d.v020Collides([p[0],h.height+1.65,p[2]])};}).filter(p=>p.clear);}""", points)
        check('Real source terrain supplies at least one finite clear arrival', bool(candidates))
        candidates.sort(key=lambda p:abs(p['ll'][0]-site['lat'])+abs(p['ll'][1]-site['lon']))
        candidate = candidates[0]
        debug('v018CaptureAt', [candidate['p'][0],candidate['h']['height']+1.65,candidate['p'][2]],0,0)
        debug('v042Update',.71)
        debug('v058HolotapesBind')
        check('The real geographic relay actually streams before counterpart assertions', site['id'] in debug('v042Runtime')['active'])
        check('The collected original copy stays absent at its actual geographic counterpart', first in info()['found']
              and not any(t['id'] == first for t in info()['physical'])
              and state()['lore']['holotapes'].get(first) is True)
        check('Legacy holodisc collection remains unchanged by all three additions', {k:v for k,v in state()['lore']['holotapes'].items() if not k.startswith('h58-')} == report['initial_legacy_holodiscs'])
        shot('04_real_counterpart_no_duplicate', 'Relais réel de l’Huveaune chargé sur sources installées ; la bande déjà collectée reste absente, sans seconde copie géographique.')
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
