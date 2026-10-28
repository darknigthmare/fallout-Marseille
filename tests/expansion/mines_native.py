#!/usr/bin/env python3
"""Bounded native persistent proximity-mine pilot, prepared without starting a browser.

Uses unchanged production HTML, GameHandler, visible controls and real browser
storage. Diagnostic navigation selects authored scenes; collision/LOS checks
select camera approaches. Payment capsules and simulation freeze are declared
assistance. No mine, merchant stock, enemy, health or quest state is granted or overwritten.
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
    parser.add_argument('--expect-mines-sha', required=True)
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
              'assistance': ['v020Load selects actual authored Aubagne, not a surveyed IGN scene.',
                             'v020Seed({caps:300,scrap:4,chemicals:3,circuitry:1}) supplies payment and workshop inputs only; no mine or merchant stock is granted.',
                             'v046SetTime(12) opens the historical shop at daytime.',
                             'v018CaptureAt and the inherited freeze place cameras/player at collision/LOS-checked existing floor points.',
                             'Bounded v020Tick(.05,true) calls step normal updatePlayer, enemy AI, collisions and updateStatus; no private IIFE variables or mine setters are used.',
                             'An existing Roux-hunter actor is approached from outside its normal detection distance using readonly worldGeometry floors, collision and LOS; no enemy state is overwritten.']}

    pinned = {}
    server = browser = context = pw = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']), pinned_inputs=pinned)
        (args.output / 'MINES_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

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
        return debug('v056MinesInfo')

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
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v056MinesInfo==='function'")
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
        module = pin('src/v050/18_iconic_mines.js')
        check('Frozen HTML contains the exact production mine module',
              digest(raw)==args.expect_html_sha and digest(module)==args.expect_mines_sha and module.strip() in raw)
        for relative in ('src/v050/16_iconic_ordnance.js','src/v050/15_chemistry.js','src/v050/10_lore_continuity.js',
                         'src/v050/11_power_armor.js','src/v050/12_iconic_ecosystem.js','src/v026/04_trade_runtime.js',
                         'src/v020/04_field.js','tools/serve_game.py'):
            source=pin(relative)
            if relative.startswith('src/'):
                check('Frozen real dependency appears in bundle: '+relative,source.strip() in raw)
        script=Path(__file__).read_bytes()
        (args.output/'EXECUTED_MINES_NATIVE.py').write_bytes(script)
        report['script_sha256']=digest(script)
        class Handler(GameHandler):
            def log_message(self, *_arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['url'] = origin+'/index.html?skipboot'
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(),headless=True,
                                    args=['--no-sandbox','--disable-dev-shm-usage'])
        report['browser_version'] = browser.version
        context = browser.new_context(viewport={'width':1440,'height':900},service_workers='block')
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror',lambda error:report['page_errors'].append(str(error)))
        page.on('console',lambda msg:report['console_errors'].append(msg.text) if msg.type=='error' else None)
        page.on('response',lambda response:report['local_http_errors'].append({'url':response.url,'status':response.status})
                if response.url.startswith(origin+'/') and response.status>=400 else None)
        page.on('requestfailed',lambda request:report['request_failures'].append({'url':request.url,'failure':request.failure}))
        page.on('dialog',lambda dialog:dialog.accept())
        document(page.goto(report['url'],wait_until='load',timeout=60000))
        report['native_navigation'] = True
        authored('aubagne')
        check('Fresh migration grants no mine or placed device',info()['quantity']==0 and not info()['ledger']['mines'])
        debug('v020Seed',{'caps':300,'scrap':4,'chemicals':3,'circuitry':1})
        debug('v046SetTime',12)
        approach([12,1.2,19],'Baptiste')
        check('Actual E reaches Baptiste dialogue',ui()['mode']=='DIALOGUE')
        page.get_by_role('button',name='Ouvrir le comptoir.',exact=True).click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='TRADE'")
        before=state()
        check('Baptiste exposes two finite mines through actual stock',before['economy']['merchants']['aubagne']['stock']['fragMine']==2)
        for _ in range(2):
            page.locator('button[data-buy="fragMine"]').click()
        bought=state()
        check('Actual purchases exhaust stock and debit one wallet without grants',bought['inventory']['fragMine']==2 and bought['player']['caps']<before['player']['caps'] and bought['economy']['merchants']['aubagne']['stock']['fragMine']==0)
        shot('01_finite_mine_purchase')
        page.locator('#tradeClose').click()
        pip('inventory','mines')
        text=page.locator('#pipContent').inner_text()
        check('Actual Pip-Boy mine page explains P, E, warning, persistence and danger',all(word in text for word in ('P pose','2,5','0,65','E permet','24 mines','peut vous tuer')))
        click('m56:aim')
        check('Visible mine aim action closes menu without consumption',ui()['mode']=='PLAYING' and info()['quantity']==2 and not info()['ledger']['mines'])
        safe=[0,1.65,85]
        check('Declared authored placement camera is collision-free',not debug('v020Collides',safe))
        debug('v018CaptureAt',safe,0,-.80)
        report['placements'].append({'position':safe,'yaw':0,'pitch':-.80,'purpose':'Actual pose, warning pause and cold Continue on existing free authored road.'})
        check('Production support validation admits this physical placement',info()['canPlace'])
        page.keyboard.press('p')
        placed=info()
        check('Native P spends exactly one mine and creates one real physical instance',placed['quantity']==1 and placed['ledger']['placed']==1 and len(placed['physical'])==1 and placed['physical'][0]['phase']=='arming')
        record=placed['ledger']['mines'][0]
        check('Placed mine uses actual authored floor and deterministic short forward reach',abs(record['pos'][0])<1e-8 and abs(record['pos'][1])<1e-8 and abs(record['pos'][2]-83.55)<1e-8)
        shot('02_real_placed_mine')
        page.evaluate("()=>{for(let i=0;i<10;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        partial=info()['ledger']['mines'][0]
        check('Normal active simulation advances actual arming delay',partial['phase']=='arming' and 1.999<partial['timer']<2.001)
        pip('inventory','mines')
        paused=info()['ledger']
        page.evaluate("()=>{for(let i=0;i<90;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        check('Actual open Pip-Boy pauses mine delays',info()['ledger']==paused)
        pip('data','system')
        click('save')
        close_pip()
        saved=state()
        document(page.reload(wait_until='load',timeout=60000))
        check('Native Continue is enabled for the real mine checkpoint',page.locator('#btnContinue').is_enabled())
        page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='aubagne'",timeout=120000)
        freeze()
        restored=state()
        report['before_mine_continue'],report['after_mine_continue']=saved,restored
        check('Native Continue preserves exact arming delay, bag, spent stock and existing ledgers',restored['v056Mines']==saved['v056Mines'] and restored['inventory']==saved['inventory'] and restored['economy']['merchants']['aubagne']['stock']['fragMine']==0 and restored['v053Lore']==saved['v053Lore'] and restored['v030']==saved['v030'] and restored['v055Ordnance']==saved['v055Ordnance'])
        check('Physical mine is rebound once after cold reload',len(info()['physical'])==1)
        authored('relay_cold')
        unloaded=info()['ledger']
        check('Travel unloads the old instance without a refund or remote explosion',not info()['physical'] and info()['quantity']==1 and unloaded==saved['v056Mines'])
        page.evaluate("()=>{for(let i=0;i<80;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        check('A different actual scene cannot consume the old mine delay',info()['ledger']==unloaded)
        authored('aubagne')
        debug('v018CaptureAt',safe,0,-.80)
        check('Returning restores exactly the original physical mine',len(info()['physical'])==1 and info()['ledger']==unloaded)
        page.evaluate("()=>{for(let i=0;i<40;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        check('Resumed mine arms without reacting to its owner standing nearby',info()['physical'][0]['phase']=='armed' and info()['ledger']['detonated']==0)
        freeze()
        selected=page.locator('#interactLabel').inner_text()
        check('Native E prompt identifies the physical armed mine', 'mine' in selected.casefold() and 'récupérer' in selected.casefold(),selected)
        shot('03_native_armed_recovery_prompt')
        page.keyboard.press('e')
        recovered=info()
        check('Native E recovers exactly the spent item and removes all mine instances',recovered['quantity']==2 and recovered['ledger']['recovered']==1 and not recovered['ledger']['mines'] and not recovered['physical'])
        authored('relay_cold')
        station=debug('v020Stats')['station']
        check('Existing real station remains available for the mine recipe',bool(station))
        check('Production collision and LOS approach reaches that station',debug('v020Approach',station['id']) is not None)
        page.keyboard.press('t')
        page.locator('button[data-v20="tab|atelier"]').click()
        page.locator('#v020Search').fill('mine')
        check('Actual station exposes enabled mine recipe',page.locator('button[data-v20="craft|fragMine"]').is_enabled())
        before=state()
        page.locator('button[data-v20="craft|fragMine"]').click()
        crafted=state()
        check('Native workshop consumes exact finite mine materials without XP farming',crafted['inventory']['fragMine']==before['inventory']['fragMine']+1 and crafted['inventory']['scrap']==before['inventory']['scrap']-4 and crafted['inventory']['chemicals']==before['inventory']['chemicals']-3 and crafted['inventory']['circuitry']==before['inventory']['circuitry']-1 and crafted['player']['xp']==before['player']['xp'])
        shot('04_actual_mine_workshop')
        page.locator('#v020Close').click()
        authored('aubagne')
        hunter=next(e for e in debug('v020Stats')['enemy'] if e['id']=='roux-hunter')
        target=hunter['pos']
        geometry=debug('worldGeometry')
        report['combat_authored_geometry']=geometry
        approach=None
        for radius in (3.3,3.6,3.9):
            for i in range(32):
                angle=i*math.tau/32
                position=[target[0]+math.sin(angle)*radius,1.65,target[2]+math.cos(angle)*radius]
                if debug('v020Collides',position):continue
                yaw=math.atan2(target[0]-position[0],-(target[2]-position[2]))
                debug('v018CaptureAt',position,yaw,-.55)
                if info()['canPlace']:
                    approach=(position,yaw)
                    break
            if approach:break
        check('Existing authored hostile actor is alive without health or actor overwrites',hunter['alive'] and hunter['hp']>0,hunter)
        check('Readonly placement scout finds an actual admitted mine near the hostile',approach is not None,approach)
        position,yaw=approach
        report['placements'].append({'position':position,'yaw':yaw,'purpose':'Collision/source/LOS-admitted proximity placement by an unmodified live authored Roux-hunter.'})
        quantity=info()['quantity']
        page.keyboard.press('p')
        combat=info()
        check('Second native P places one ordinary mine by the actual hostile',combat['quantity']==quantity-1 and len(combat['physical'])==1 and combat['ledger']['placed']==2)
        mine=combat['physical'][0]
        # Retreat camera assistance is explicit; ordinary actor AI still runs
        # during every subsequent active update. No enemy or mine is moved.
        retreats=[]
        for radius in (8,10):
            for i in range(32):
                angle=i*math.tau/32
                p=[mine['pos'][0]+math.sin(angle)*radius,1.65,mine['pos'][2]+math.cos(angle)*radius]
                if not debug('v020Collides',p) and debug('v020LOS',p,[mine['pos'][0],mine['pos'][1]+.16,mine['pos'][2]]):
                    retreats.append(p)
            if retreats:break
        check('A collision-free retreat beyond the six-metre blast exists',bool(retreats))
        retreat=min(retreats,key=lambda p:math.hypot(p[0]-position[0],p[2]-position[2]))
        yaw=math.atan2(mine['pos'][0]-retreat[0],-(mine['pos'][2]-retreat[2]))
        pitch=math.atan2(mine['pos'][1]+.16-retreat[1],math.hypot(mine['pos'][0]-retreat[0],mine['pos'][2]-retreat[2]))
        debug('v018CaptureAt',retreat,yaw,pitch)
        report['placements'].append({'position':retreat,'yaw':yaw,'pitch':pitch,'purpose':'Declared camera retreat outside blast radius. Existing enemy AI and mine proximity continue unchanged.'})
        page.evaluate("()=>{for(let i=0;i<100;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        blast=info()['lastBlast']
        current=next(e for e in debug('v020Stats')['enemy'] if e['id']=='roux-hunter')
        report['actual_mine_combat']={'before':hunter,'after':current,'blast':blast,'mine':mine}
        check('Real enemy proximity causes one ordinary mine blast with actual hostile damage',info()['ledger']['detonated']==1 and not info()['ledger']['mines'] and blast is not None and any(h['id']=='roux-hunter' and h['after']<h['before'] for h in blast['hits']) and current['hp']<hunter['hp'],report['actual_mine_combat'])
        check('Player survives declared retreat without an HP overwrite',state()['player']['hp']>0)
        shot('05_actual_hostile_mine_result')
        pip('inventory','mines')
        shot('06_mine_inventory_summary')
        pip('data','system')
        click('save')
        close_pip()
        final=state()
        document(page.reload(wait_until='load',timeout=60000))
        page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='aubagne'",timeout=120000)
        freeze()
        current=state()
        check('Final native Continue retains placement/recovery/blast counts, craft, bag and exhausted stock',current['v056Mines']==final['v056Mines'] and current['inventory']==final['inventory'] and current['v020']['craftCount']==final['v020']['craftCount'] and current['economy']['merchants']['aubagne']['stock']['fragMine']==0 and not info()['physical'])
        for relative in list(pinned):
            pin(relative)
        check('No page exceptions or local failed HTTP resources',not report['page_errors'] and not report['local_http_errors'],
              {'page_errors':report['page_errors'],'local_http_errors':report['local_http_errors']})
        report['stage']='complete'
    except Exception as error:
        report['exception'], report['traceback'] = str(error), traceback.format_exc()
        report['stage'] = 'failed'
        save()
        print(report['traceback'], flush=True)
        return 1
    finally:
        save()
        for item in (context,browser,pw):
            if item:
                try:
                    item.stop() if item is pw else item.close()
                except Exception as error:
                    report.setdefault('cleanup_errors',[]).append(str(error))
        report['browser_closed'] = not report.get('cleanup_errors')
        if server:
            server.shutdown()
            server.server_close()
        report['server_closed'] = True
        save()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
