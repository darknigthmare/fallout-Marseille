#!/usr/bin/env python3
"""Bounded native hand-grenade pilot, prepared without starting a browser.

Uses unchanged production HTML, GameHandler, visible controls and real browser
storage. Diagnostic navigation selects authored scenes; collision/LOS checks
select camera approaches. Payment capsules and simulation freeze are declared
assistance. No grenade, merchant stock, enemy, health or quest state is granted or overwritten.
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
    parser.add_argument('--expect-ordnance-sha', required=True)
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
                             'v020Seed({caps:300,scrap:3,chemicals:3,weaponParts:1}) supplies payment and workshop inputs only; no grenade or merchant stock is granted.',
                             'v046SetTime(12) opens the historical shop at daytime.',
                             'v018CaptureAt and the inherited freeze place cameras/player at collision/LOS-checked existing floor points.',
                             'Bounded v020Tick(.05,true) calls step normal updatePlayer, enemy AI, collisions and updateStatus; no private IIFE variables or projectile setters are used.',
                             'An existing Roux-hunter actor is approached from outside its normal detection distance using readonly worldGeometry floors, collision and LOS; no enemy state is overwritten.']}

    pinned = {}
    server = browser = context = pw = None

    def save():
        report.update(elapsed_seconds=round(time.monotonic() - started, 3),
                      passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']), pinned_inputs=pinned)
        (args.output / 'ORDNANCE_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

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
        return debug('v055OrdnanceInfo')

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
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v055OrdnanceInfo==='function'")
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
        module = pin('src/v050/16_iconic_ordnance.js')
        check('Frozen HTML contains the exact production ordnance module',
              digest(raw) == args.expect_html_sha and digest(module) == args.expect_ordnance_sha and module.strip() in raw)
        for relative in ('src/v050/10_lore_continuity.js','src/v050/11_power_armor.js',
                         'src/v050/12_iconic_ecosystem.js','src/v050/15_chemistry.js',
                         'src/v026/04_trade_runtime.js','src/v020/04_field.js','tools/serve_game.py'):
            source = pin(relative)
            if relative.startswith('src/'):
                check('Frozen real dependency appears in bundle: '+relative, source.strip() in raw)
        script = Path(__file__).read_bytes()
        (args.output/'EXECUTED_ORDNANCE_NATIVE.py').write_bytes(script)
        report['script_sha256'] = digest(script)

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
        check('Fresh migration grants no grenade or armed projectile',
              info()['quantity']==0 and info()['ledger']['armed'] is None and info()['ledger']['launched']==0)
        debug('v020Seed',{'caps':300,'scrap':3,'chemicals':3,'weaponParts':1})
        debug('v046SetTime',12)
        approach([12,1.2,19],'Baptiste')
        check('Actual E reaches Baptiste dialogue',ui()['mode']=='DIALOGUE')
        page.get_by_role('button',name='Ouvrir le comptoir.',exact=True).click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='TRADE'")
        before = state()
        check('Baptiste exposes three finite grenades through real stock',
              before['economy']['merchants']['aubagne']['stock']['fragGrenade']==3)
        for _ in range(3):
            page.locator('button[data-buy="fragGrenade"]').click()
        acquired = state()
        check('Native purchases debit caps and exhaust the one ordinary stock',
              acquired['inventory'].get('fragGrenade')==3 and acquired['player']['caps']<before['player']['caps']
              and acquired['economy']['merchants']['aubagne']['stock']['fragGrenade']==0)
        shot('01_finite_baptiste_purchase')
        page.locator('#tradeClose').click()
        pip('inventory','ordnance')
        check('Actual explosives page explains aiming, fuse and self blast',
              page.locator('#pipContent').inner_text().find('3 secondes')>=0
              and page.locator('#pipContent').inner_text().find('6 mètres')>=0)
        click('o55:aim')
        check('Visible aim action closes menu without spending a grenade',ui()['mode']=='PLAYING' and info()['quantity']==3)

        safe = [0,1.65,85]
        check('Safe authored launch point is collision-free',not debug('v020Collides',safe))
        debug('v018CaptureAt',safe,0,-.08)
        report['placements'].append({'position':safe,'yaw':0,'pitch':-.08,'purpose':'Launch, pause and native Continue; authored clear road.'})
        check('Clickable grenade HUD control is visible and enabled',
              page.locator('[data-o55-grenade]').is_visible() and page.locator('[data-o55-grenade]').is_enabled())
        def grenade_in_view():
            return page.locator('[data-o55-grenade]').evaluate('(button)=>{const r=button.getBoundingClientRect(),all=[...button.parentElement.querySelectorAll("button")].map(b=>{const q=b.getBoundingClientRect();return {text:b.textContent,left:q.left,top:q.top,right:q.right,bottom:q.bottom,width:q.width,height:q.height};}).filter(q=>q.width>0&&q.height>0),overlaps=all.some((a,i)=>all.some((b,j)=>i<j&&a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top)),inside=all.every(q=>q.left>=0&&q.top>=0&&q.right<=innerWidth&&q.bottom<=innerHeight&&q.width>=40&&q.height>=40);return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height,innerWidth,innerHeight,buttons:all,overlaps,visible:inside&&!overlaps};}')
        desktop = grenade_in_view()
        check('Desktop grenade HUD button is fully inside the real viewport',desktop['visible'] and len(desktop['buttons'])==8,desktop)
        page.set_viewport_size({'width':390,'height':844})
        freeze()
        narrow = grenade_in_view()
        check('Narrow viewport keeps the fourth visible terrain action fully onscreen',narrow['visible'] and len(narrow['buttons'])==4,narrow)
        page.set_viewport_size({'width':1440,'height':900})
        freeze()
        page.keyboard.press('n')
        check('Native N consumes one grenade and publishes two real draw meshes',
              info()['quantity']==2 and info()['ledger']['launched']==1 and info()['draws']==2
              and info()['ledger']['armed']['fuse']==3)
        page.evaluate("()=>{for(let i=0;i<8;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        airborne = info()['ledger']['armed']
        check('Normal active updates move a real airborne projectile',
              airborne['fuse']<2.61 and airborne['fuse']>2.59 and airborne['pos'][2]<82
              and airborne['pos'][1]>safe[1])
        shot('02_native_airborne_grenade')
        pip('inventory','ordnance')
        paused = info()['ledger']
        page.evaluate("()=>{for(let i=0;i<120;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        check('Actual Pip-Boy simulation calls preserve the armed fuse and position',info()['ledger']==paused)
        pip('data','system')
        click('save')
        close_pip()
        saved = state()
        check('Production save stores one spent item and actual airborne state',
              saved['inventory']['fragGrenade']==2 and saved['v055Ordnance']['armed']==airborne)
        document(page.reload(wait_until='load',timeout=60000))
        check('Native Continue is enabled',page.locator('#btnContinue').is_enabled())
        page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='aubagne'",timeout=120000)
        freeze()
        restored = state()
        report['before_airborne_continue'],report['after_airborne_continue'] = saved,restored
        check('Native Continue restores exact remaining fuse, ballistics and finite stock without refund',
              restored['v055Ordnance']==saved['v055Ordnance']
              and restored['inventory']==saved['inventory']
              and restored['economy']['merchants']['aubagne']['stock']['fragGrenade']==0
              and restored['v053Lore']==saved['v053Lore'] and restored['v030']==saved['v030'])
        pip('inventory','ordnance')
        shot('03_native_armed_continue')
        close_pip()
        page.evaluate("()=>{for(let i=0;i<52;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        check('Resumed active projectile detonates exactly once away from the player',
              info()['ledger']['armed'] is None and info()['ledger']['detonated']==1 and info()['quantity']==2
              and info()['lastBlast'] is not None and info()['lastBlast']['player'] is False)

        hunter = next(e for e in debug('v020Stats')['enemy'] if e['id']=='roux-hunter')
        target = hunter['pos']
        geometry = debug('worldGeometry')
        report['combat_authored_geometry'] = geometry
        launch = None
        # Existing Aubagne includes raised authored floors. Scout flat source
        # ground rather than assuming that a camera LOS also clears the arc.
        # This is readonly placement assistance, not projectile manipulation.
        for angle in (0,math.pi/2,-math.pi/2,math.pi,.75,-.75,2.4,-2.4):
            candidate = [target[0]+math.sin(angle)*21,1.65,target[2]+math.cos(angle)*21]
            blocked_floor = False
            for k in range(41):
                x = candidate[0]+(target[0]-candidate[0])*k/40
                z = candidate[2]+(target[2]-candidate[2])*k/40
                for floor in geometry['floorZones']:
                    height = max(floor.get('height',0),floor.get('startHeight',0),floor.get('endHeight',0))
                    if height>.25 and floor['minX']<=x<=floor['maxX'] and floor['minZ']<=z<=floor['maxZ']:
                        blocked_floor = True
                        break
                if blocked_floor:
                    break
            if blocked_floor or debug('v020Collides',candidate) or not debug('v020LOS',candidate,[target[0],target[1]+1,target[2]]):
                continue
            launch = candidate
            break
        check('Unmodified authored Roux-hunter is alive at its ordinary source position',hunter['alive'] and hunter['hp']>0)
        check('Real combat approach has flat authored support, free collision and actual LOS',launch is not None,
              {'position':launch,'target':target})
        yaw = math.atan2(target[0]-launch[0],-(target[2]-launch[2]))
        debug('v018CaptureAt',launch,yaw,0)
        report['placements'].append({'position':launch,'yaw':yaw,'pitch':0,
                                     'purpose':'Actual pre-existing hostile actor; readonly floor/collision/LOS scout, no actor or health overwrite.'})
        page.locator('[data-o55-grenade]').click()
        check('Visible HUD grenade control performs the same real launch',
              info()['quantity']==1 and info()['ledger']['launched']==2 and info()['ledger']['armed'] is not None)
        page.evaluate("()=>{for(let i=0;i<60;i++)__MISTRAL_DEBUG.v020Tick(.05,true);}")
        blast = info()['lastBlast']
        report['actual_combat_blast'] = blast
        hunter_after = next(e for e in debug('v020Stats')['enemy'] if e['id']=='roux-hunter')
        check('Real authored enemy receives ordinary blast damage from the physical grenade',
              info()['ledger']['detonated']==2 and info()['ledger']['armed'] is None
              and blast is not None and any(h['id']=='roux-hunter' and h['after']<h['before'] for h in blast['hits'])
              and hunter_after['hp']<hunter['hp'],{'before':hunter,'after':hunter_after,'blast':blast})
        check('Player survived the real encounter without any health overwrite',state()['player']['hp']>0)
        look = math.atan2(blast['pos'][0]-launch[0],-(blast['pos'][2]-launch[2]))
        pitch = math.atan2(blast['pos'][1]-launch[1],math.hypot(blast['pos'][0]-launch[0],blast['pos'][2]-launch[2]))
        debug('v018CaptureAt',launch,look,pitch)
        shot('04_real_authored_blast_result')

        authored('relay_cold')
        station = debug('v020Stats')['station']
        check('A real existing clinic station is available for workshop validation',bool(station))
        check('Existing station approach succeeds with collision/LOS checked export',
              debug('v020Approach',station['id']) is not None)
        page.keyboard.press('t')
        page.locator('button[data-v20="tab|atelier"]').click()
        check('Real workshop exposes enabled grenade recipe at the actual station',
              page.locator('button[data-v20="craft|fragGrenade"]').is_enabled())
        page.locator('#v020Search').fill('grenade')
        before = state()
        page.locator('button[data-v20="craft|fragGrenade"]').click()
        crafted = state()
        check('Native workshop consumes actual materials and adds one grenade without XP farming',
              crafted['inventory']['fragGrenade']==before['inventory']['fragGrenade']+1
              and crafted['inventory']['scrap']==before['inventory']['scrap']-3
              and crafted['inventory']['chemicals']==before['inventory']['chemicals']-3
              and crafted['inventory']['weaponParts']==before['inventory']['weaponParts']-1
              and crafted['player']['xp']==before['player']['xp'])
        shot('05_real_station_recipe')
        page.locator('#v020Close').click()
        pip('data','system')
        click('save')
        close_pip()
        final = state()
        document(page.reload(wait_until='load',timeout=60000))
        page.locator('#btnContinue').click()
        page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'&&__MISTRAL_DEBUG.v020Stats().id==='relay_cold'",timeout=120000)
        freeze()
        current = state()
        check('Final native Continue retains both detonations, recipe count, bag and finite stock',
              current['v055Ordnance']==final['v055Ordnance']
              and current['v020']['craftCount']==final['v020']['craftCount']
              and current['inventory']==final['inventory']
              and current['economy']['merchants']['aubagne']['stock']['fragGrenade']==0)
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
