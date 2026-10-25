#!/usr/bin/env python3
"""Bounded assisted native chem pilot, prepared without starting a browser.

Uses unchanged production HTML, GameHandler, visible controls and real browser
storage. Diagnostic navigation selects authored scenes; collision/LOS checks
select camera approaches. Payment capsules and simulation freeze are declared
assistance. No chem, stock, addiction or quest state is granted or overwritten.
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

ROOT = Path(__file__).resolve().parents[2]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    parser.add_argument('--expect-chems-sha', required=True)
    args = parser.parse_args()
    if not args.run:
        print('Prepared only. No server or browser started. Coordinate frozen SHA values and pass --run.')
        return 0
    sys.path.insert(0, str(ROOT / 'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright

    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {'checks': [], 'shots': [], 'placements': [], 'page_errors': [], 'console_errors': [],
              'local_http_errors': [], 'request_failures': [], 'native_navigation': False,
              'html_injected': False, 'network_mocked': False, 'storage_mocked': False,
              'service_workers_disabled': True, 'maximum_contexts': 1, 'scope': __doc__,
              'assistance': ['v020Load selects authored Aubagne/Annexe scenes; these are fictional layouts, not IGN interiors.',
                             'v020Seed({caps:300}) supplies payment only. No item, stock, skill or addiction is seeded.',
                             'v046SetTime(12) opens the existing shop at daytime.',
                             'Existing render/simulation freeze and v018CaptureAt use collision/LOS-checked authored floor points.',
                             'A bounded loop calls real v020Tick(.05,true): up to 2,500 steps of actual active simulation.',
                             'Readonly exported diagnostics inspect state; native E, Tab and visible UI perform all purchases, doses, quotes and treatment.']}
    pinned = {}
    server = browser = context = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']), pinned_inputs=pinned)
        (args.output / 'CHEMS_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ') + name, flush=True)
        save()
        if not ok:
            raise AssertionError(name)

    def pin(relative):
        raw = (ROOT / relative).read_bytes()
        sha = digest(raw)
        if relative in pinned and pinned[relative] != sha:
            raise AssertionError('Frozen input changed: ' + relative)
        pinned[relative] = sha
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def state():
        return debug('getState')

    def info():
        return debug('v054ChemsInfo')

    def ui():
        return debug('v027UI')

    def click(action, arg=None):
        selector = 'button[data-p27=' + json.dumps(action) + ']'
        if arg is not None:
            selector += '[data-arg=' + json.dumps(str(arg)) + ']'
        button = page.locator('#pipboy').locator(selector).first
        check('Visible enabled production control: ' + action + ' ' + str(arg or ''),
              button.count() > 0 and button.is_visible() and button.is_enabled())
        button.click()

    def close_pip():
        if ui()['mode'] == 'PIP':
            page.keyboard.press('Tab')
            check('Native Tab closes Pip-Boy', ui()['mode'] == 'PLAYING')

    def pip(tab, sub):
        if ui()['mode'] != 'PIP':
            page.keyboard.press('Tab')
        click('tab', tab)
        click('sub', sub)
        check('Native Pip-Boy navigation: ' + tab + '/' + sub,
              ui()['mode'] == 'PIP' and ui()['tab'] == tab and ui()['sub'] == sub)

    def freeze():
        p = state()['player']
        debug('v018CaptureAt', p['pos'], p['yaw'], p['pitch'])

    def shot(name):
        freeze()
        output = args.output / (name + '.png')
        page.screenshot(path=str(output))
        report['shots'].append({'file': output.name, 'sha256': digest(output.read_bytes())})
        save()

    def document(response):
        check('Native HTTP document matches frozen production HTML',
              response is not None and response.status == 200 and digest(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v054ChemsInfo==='function'")
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        freeze()

    def authored(zone):
        close_pip()
        check('Existing authored scene selected without grants: ' + zone, debug('v020Load', zone)['id'] == zone)
        freeze()

    def approach(target, label):
        # Targets below are explicitly authored game coordinates from source.
        # Every actual approach must still pass production collision and LOS.
        points = [[target[0] + math.sin(n * math.tau / 24) * radius, 1.65,
                   target[2] + math.cos(n * math.tau / 24) * radius]
                  for radius in (1.7, 2.2, 2.65) for n in range(24)]
        for position in points:
            if debug('v020Collides', position) or not debug('v020LOS', position, target):
                continue
            yaw = math.atan2(target[0] - position[0], -(target[2] - position[2]))
            pitch = math.atan2(target[1] - position[1], math.hypot(target[0] - position[0], target[2] - position[2]))
            debug('v018CaptureAt', position, yaw, pitch)
            actual = page.locator('#interactLabel').inner_text()
            if label.casefold() in actual.casefold():
                report['placements'].append({'position': position, 'target': target, 'actual_label': actual,
                                             'source': 'Authored narrative coordinates, collision and LOS checked by production exports.'})
                check('Native selection physically reaches ' + label, True, report['placements'][-1])
                page.keyboard.press('e')
                return
        check('Native selection physically reaches ' + label, False, {'target': target})

    try:
        raw = pin('index.html')
        chem = pin('src/v050/15_chemistry.js')
        check('Coordinated HTML and chemistry are installed and composed',
              digest(raw) == args.expect_html_sha and digest(chem) == args.expect_chems_sha and chem.strip() in raw)
        for relative in ('src/v050/10_lore_continuity.js', 'src/v050/11_power_armor.js',
                         'src/v050/12_iconic_ecosystem.js', 'src/v028/01_body.js',
                         'src/v028/04_story.js', 'src/v026/04_trade_runtime.js', 'tools/serve_game.py'):
            source = pin(relative)
            if relative.startswith('src/'):
                check('Frozen dependency is in actual production bundle: ' + relative, source.strip() in raw)
        script = Path(__file__).read_bytes()
        (args.output / 'EXECUTED_CHEMS_NATIVE.py').write_bytes(script)
        report['script_sha256'] = digest(script)

        class Handler(GameHandler):
            def log_message(self, *_arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin + '/index.html?skipboot'
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                         args=['--no-sandbox', '--disable-dev-shm-usage'])
            report['browser_version'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
            page = context.new_page()
            page.set_default_timeout(30000)
            page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
            page.on('console', lambda msg: report['console_errors'].append(msg.text) if msg.type == 'error' else None)
            page.on('response', lambda response: report['local_http_errors'].append({'url': response.url, 'status': response.status})
                    if response.url.startswith(origin + '/') and response.status >= 400 else None)
            page.on('requestfailed', lambda request: report['request_failures'].append({'url': request.url, 'failure': request.failure}))
            page.on('dialog', lambda dialog: dialog.accept())
            document(page.goto(report['url'], wait_until='load', timeout=60000))
            report['native_navigation'] = True
            authored('aubagne')
            check('Fresh ordinary inventory contains no free chems',
                  all(state()['inventory'].get(key, 0) == 0 for key in ('jet', 'buffout', 'mentats', 'psycho')))
            debug('v020Seed', {'caps': 300})
            debug('v046SetTime', 12)
            # Actual Baptiste actor is [12,0,19] in the authored Aubagne scene.
            approach([12, 1.2, 19], 'Baptiste')
            check('Native E opens real merchant dialogue', debug('v020Stats')['mode'] == 'DIALOGUE')
            page.get_by_role('button', name='Ouvrir le comptoir.', exact=True).click()
            page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='TRADE'")
            before = state()
            check('Real finite old-campaign supply has three Mentats',
                  before['economy']['merchants']['aubagne']['stock']['mentats'] == 3)
            for _ in range(3):
                page.locator('button[data-buy="mentats"]').click()
            acquired = state()
            check('Visible purchases spend capsules and exhaust the same finite merchant stock',
                  acquired['inventory'].get('mentats') == 3 and acquired['player']['caps'] < before['player']['caps']
                  and acquired['economy']['merchants']['aubagne']['stock']['mentats'] == 0
                  and acquired['v054Chems']['stocked'].get('aubagne') is True)
            shot('01_real_finite_purchase')
            page.locator('#tradeClose').click()
            baseline = info()['skills']
            pip('inventory', 'aid')
            page.locator('#p27Search').fill('Mentats')
            click('select', 'mentats')
            for _ in range(3):
                click('use', 'mentats')
            used = info()
            check('Three real AIDE doses consume inventory and create bounded tolerance and dependency',
                  state()['inventory']['mentats'] == 0 and used['state']['agents']['mentats']['uses'] == 3
                  and used['state']['agents']['mentats']['active'] == 120
                  and used['state']['agents']['mentats']['dependent'] is True
                  and all(used['skills'][k] == min(100, baseline[k] + 12) for k in baseline))
            paused = used['state']
            page.evaluate("()=>{for(let i=0;i<200;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
            check('Actual simulation calls in the Pip-Boy preserve chem time', info()['state'] == paused)
            pip('status', 'chemistry')
            shot('02_tolerance_and_dependency')
            close_pip()
            # Each call uses the real updatePlayer and updateStatus with normal
            # dt. No clock/state setter or private IIFE variable is accessed.
            for _ in range(25):
                page.evaluate("()=>{for(let i=0;i<100;i++){if(__MISTRAL_DEBUG.v054ChemsInfo().state.agents.mentats.active<=0)break;__MISTRAL_DEBUG.v020Tick(.05,true);}}")
                if info()['state']['agents']['mentats']['active'] <= 0:
                    break
            withdrawn = info()
            check('Actual active updates end the bonus and impose cognitive withdrawal',
                  withdrawn['state']['agents']['mentats']['active'] == 0
                  and 299.8 <= withdrawn['state']['agents']['mentats']['withdrawal'] <= 300
                  and withdrawn['state']['agents']['mentats']['dependent'] is True
                  and all(withdrawn['skills'][k] == max(0, baseline[k] - 10) for k in baseline), withdrawn)
            authored('relay_cold')
            medic = next(i for i in debug('v020Stats')['interactables'] if i['id'] == 'v028:medic')
            # Original Sofia actor is [-3,0,9]; source interaction at [-3,1,9].
            approach(medic['pos'], 'Sofia')
            check('Actual Sofia dialogue preserves old service and new chem route',
                  page.get_by_role('button', name='Examiner mon état physique et les soins possibles.', exact=True).count() == 1
                  and page.get_by_role('button', name='Parler des consommables, de la tolérance et du sevrage.', exact=True).count() == 1)
            page.get_by_role('button', name='Parler des consommables, de la tolérance et du sevrage.', exact=True).click()
            check('Real nearby doctor route opens dependency page',
                  ui()['mode'] == 'PIP' and ui()['sub'] == 'chemistry' and info()['doctor']['near'] is True)
            click('c54:quote')
            check('Sofia provides a local sixty-capsule quote', info()['doctor']['quote']['cost'] == 60)
            before = state()
            click('c54:confirm')
            after = state()
            check('Visible confirmation pays once, clears withdrawal and preserves wounds/radiation/inventory',
                  after['player']['caps'] == before['player']['caps'] - 60 and after['v054Chems']['treatments'] == 1
                  and after['v054Chems']['agents']['mentats']['uses'] == 3
                  and after['v054Chems']['agents']['mentats']['dependent'] is False
                  and after['inventory'] == before['inventory'] and after['v028']['limbs'] == before['v028']['limbs']
                  and after['player']['hp'] == before['player']['hp'] and after['player']['rad'] == before['player']['rad'])
            shot('03_local_sofia_treatment')
            pip('data', 'system')
            click('save')
            close_pip()
            saved = state()
            check('Production save exists in native browser storage',
                  page.evaluate("()=>Object.values(localStorage).some(v=>typeof v==='string'&&v.length>1000)"))
            document(page.reload(wait_until='load', timeout=60000))
            check('Native Continue is available', page.locator('#btnContinue').is_enabled())
            page.locator('#btnContinue').click()
            page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='relay_cold'", timeout=120000)
            freeze()
            restored = state()
            report['before_continue'], report['after_continue'] = saved, restored
            check('Continue retains uses, treatment and exhausted finite stock without redose or reseed',
                  restored['v054Chems'] == saved['v054Chems'] and restored['inventory'] == saved['inventory']
                  and restored['economy']['merchants']['aubagne']['stock']['mentats'] == 0
                  and restored['player']['caps'] == saved['player']['caps']
                  and restored['v053Iconic'] == saved['v053Iconic'] and restored['v030'] == saved['v030'])
            pip('status', 'chemistry')
            shot('04_native_continue')
            for relative in list(pinned):
                pin(relative)
            check('No page exceptions or local failed HTTP resources',
                  not report['page_errors'] and not report['local_http_errors'],
                  {'page_errors': report['page_errors'], 'local_http_errors': report['local_http_errors']})
            report['stage'] = 'complete'
    except Exception as error:
        report['exception'], report['traceback'] = str(error), traceback.format_exc()
        report['stage'] = 'failed'
        save()
        print(report['traceback'], flush=True)
        return 1
    finally:
        save()
        if context:
            context.close()
        if browser:
            browser.close()
        if server:
            server.shutdown()
            server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
