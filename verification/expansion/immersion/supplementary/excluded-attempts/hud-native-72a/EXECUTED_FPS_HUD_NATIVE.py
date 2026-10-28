#!/usr/bin/env python3
"""Native HUD layouts and controls on exact production HTML.

Authored Aubagne is selected by the existing diagnostic navigation API. Camera
placement/freeze and render pause are declared assistance. Input uses real DOM
controls, keyboard and Playwright pointer events; coarse pointer is emulated,
not a physical touchscreen certification. No HTML/storage/network mocking.
Temporary document observers count bubbling activation keys without intercepting
them or altering production handlers or state.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expect-html-sha', required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT/'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright
    report = {'scope': __doc__, 'checks': [], 'shots': [], 'rectangles': [], 'page_errors': [],
              'request_failures': [], 'http_errors': [], 'html_sha256': args.expect_html_sha,
              'script_sha256': sha(Path(__file__).read_bytes()), 'network_mocked': False,
              'storage_mocked': False, 'html_injected': False, 'stage': 'starting'}
    before = {str(x.relative_to(ROOT)): sha(x.read_bytes()) for x in (ROOT/'src').rglob('*') if x.is_file()}
    started = time.monotonic()
    server = browser = context = pw = None

    def save():
        report.update(passed=sum(x['ok'] for x in report['checks']),
                      failed=sum(not x['ok'] for x in report['checks']),
                      elapsed_seconds=round(time.monotonic()-started, 3))
        (args.output/'FPS_HUD_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ')+name, flush=True)
        save()
        if not ok:
            raise AssertionError(name)

    def debug(name, *values):
        return page.evaluate('([name,args])=>__MISTRAL_DEBUG[name](...args)', [name, list(values)])

    def prepare():
        response = page.goto(origin+'/index.html?skipboot', wait_until='load', timeout=90000)
        check('HTTP document equals frozen production bytes', response.status == 200 and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v056HudInfo==='function'", timeout=120000)
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        debug('v020Load', 'aubagne')
        debug('v046SetTime', 12)
        debug('v018CaptureAt', [0, 1.65, 10], 0, 0)
        page.wait_for_function("__MISTRAL_DEBUG.getMode()==='PLAYING'")
        page.wait_for_timeout(400)

    def shot(name):
        # Browser resize clears WebGL's drawing buffer while diagnostic render
        # pause is active. Redraw the unchanged scene through its normal renderer.
        debug('v046Render')
        target = args.output/(name+'.png')
        page.screenshot(path=str(target))
        report['shots'].append({'file': target.name, 'sha256': sha(target.read_bytes())})
        save()

    def rectangles(label):
        result = page.evaluate("""()=>{
          const ids=['statusBars','weaponHud','compass','locationCard','v020Quickbar','fps56ObjectiveToggle','interactPrompt'];
          const rect=el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,visible:!!el.getClientRects().length&&getComputedStyle(el).display!=='none'}};
          const data=Object.fromEntries(ids.map(id=>[id,rect(document.getElementById(id))]));
          data.buttons=[...document.querySelectorAll('#v020Quickbar button')].filter(el=>el.getClientRects().length&&getComputedStyle(el).display!=='none').map(el=>({text:el.textContent,...rect(el)}));
          data.condition=[...document.querySelectorAll('#weaponHud .condition-line>*')].filter(el=>el.getClientRects().length).map(rect);
          data.touch=[...document.querySelectorAll('#touchControls button,#touchMove')].filter(el=>el.getClientRects().length).map(el=>({id:el.id||el.dataset.touch,...rect(el)}));
          data.viewport={w:innerWidth,h:innerHeight};return data;
        }""")
        report['rectangles'].append({'label': label, **result})
        w, h = result['viewport'].values()
        def inside(r):
            return r['x'] >= -0.5 and r['y'] >= -0.5 and r['right'] <= w+.5 and r['bottom'] <= h+.5
        check(label+': vital, ammunition, navigation and quickbar stay in viewport', all(inside(result[k]) for k in ('statusBars','weaponHud','compass','locationCard','v020Quickbar')))
        check(label+': every visible quickbar control has 40px target and stays inside viewport', all(inside(b) and b['w'] >= 40 and b['h'] >= 40 for b in result['buttons']))
        def overlap(a, b):
            return min(a['right'],b['right'])-max(a['x'],b['x']) > 1 and min(a['bottom'],b['bottom'])-max(a['y'],b['y']) > 1
        pairs = [('statusBars','weaponHud'),('statusBars','v020Quickbar'),('weaponHud','v020Quickbar'),('locationCard','compass')]
        check(label+': primary HUD groups do not overlap', all(not overlap(result[a],result[b]) for a,b in pairs), pairs)
        weapon = result['weaponHud']
        check(label+': weapon and armour condition gauges stay inside ammunition panel', all(r['x'] >= weapon['x'] and r['right'] <= weapon['right']+.5 for r in result['condition']))
        if result['touch']:
            check(label+': touch controls stay inside viewport with 40px targets', all(inside(r) and r['w']>=40 and r['h']>=40 for r in result['touch']))
            check(label+': touch controls do not overlap vitals, ammunition or quickbar', all(not overlap(t,result[k]) for t in result['touch'] for k in ('statusBars','weaponHud','v020Quickbar')))
        save()

    try:
        check('On-disk HTML has expected identity', sha((ROOT/'index.html').read_bytes()) == args.expect_html_sha)
        (args.output/'EXECUTED_FPS_HUD_NATIVE.py').write_bytes(Path(__file__).read_bytes())
        class Handler(GameHandler):
            def log_message(self, *_args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_address[1]}'
        report['origin'] = origin
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=['--no-sandbox','--disable-dev-shm-usage'])
        report['browser_version'] = browser.version
        context = browser.new_context(viewport={'width':1440,'height':900},service_workers='block')
        page = context.new_page()
        def listen(page):
            page.on('pageerror', lambda e: report['page_errors'].append(str(e)))
            page.on('requestfailed', lambda r: report['request_failures'].append({'url':r.url,'failure':r.failure}))
            page.on('response', lambda r: report['http_errors'].append({'url':r.url,'status':r.status}) if r.url.startswith(origin+'/') and r.status>=400 else None)
        listen(page)
        prepare()
        for width,height in ((1440,900),(1024,768),(390,844),(844,390)):
            page.set_viewport_size({'width':width,'height':height})
            page.wait_for_timeout(250)
            rectangles(f'desktop pointer {width}x{height}')
            shot(f'{width}x{height}_hud')
        page.set_viewport_size({'width':1440,'height':900})
        page.locator('#fps56ObjectiveToggle').click()
        check('Native objective toggle hides cards without changing game objective', not debug('v056HudInfo')['preferences']['objectives'] and 'fps56-objective-hidden' in page.locator('#questCard').get_attribute('class'))
        page.locator('#fps56ObjectiveToggle').click()
        check('Native objective toggle restores objective visibility', debug('v056HudInfo')['preferences']['objectives'])
        before_state = debug('getState')['player']
        page.keyboard.press('ControlLeft')
        page.wait_for_timeout(100)
        check('Actual crouch presents actual stance', debug('getState')['player']['crouched'] and page.locator('#fps56Stance').inner_text()=='ACCROUPI')
        page.keyboard.press('ControlLeft')
        check('Actual standing restores player posture', not debug('getState')['player']['crouched'])
        check('HUD posture/quest controls preserve health, ammunition and inventory wallet', all(debug('getState')['player'][k] == before_state[k] for k in ('hp','ammoClip','ammoReserve','caps')))
        page.evaluate("""()=>{window.__fpsHudKeyCount=0;window.__fpsHudKeyObserver=e=>{if(['Space','Enter'].includes(e.code)&&e.target.matches('[data-fps56-aim]'))window.__fpsHudKeyCount++;};document.addEventListener('keydown',window.__fpsHudKeyObserver);document.addEventListener('keyup',window.__fpsHudKeyObserver);}""")
        aim_button = page.locator('[data-fps56-aim]')
        aim_button.focus()
        for code in ('Space','Enter'):
            page.keyboard.down(code)
            check('Keyboard '+code+' holds HUD aim without bubbling into gameplay', page.evaluate('v056FirstPersonIsAiming()&&window.__fpsHudKeyCount===0'))
            page.keyboard.up(code)
            check('Keyboard '+code+' release clears aim without bubbling into gameplay', page.evaluate('!v056FirstPersonIsAiming()&&window.__fpsHudKeyCount===0'))
        page.evaluate("""()=>{document.removeEventListener('keydown',window.__fpsHudKeyObserver);document.removeEventListener('keyup',window.__fpsHudKeyObserver);delete window.__fpsHudKeyObserver;delete window.__fpsHudKeyCount;}""")
        page.keyboard.press('Escape')
        page.locator('#btnPauseOptions').click()
        page.locator('[data-fps56=compact]').check()
        check('Options control stores compact preference in native localStorage', debug('v056HudInfo')['preferences']['compact'] and json.loads(page.evaluate("localStorage.getItem('mistral_fps_hud_v1')"))['compact'])
        page.locator('#btnOptionsClose').click()
        page.locator('#btnResume').click()
        page.wait_for_timeout(100)
        rectangles('compact 1440x900')
        shot('compact_hud')
        # A deliberate reload may cancel metadata requests; raw failures remain
        # in the report and are classified separately from geography sources.
        response = page.reload(wait_until='load',timeout=90000)
        check('Native reload still serves exact frozen HTML', sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v056HudInfo==='function'")
        check('Native reload restores compact display preference', debug('v056HudInfo')['preferences']['compact'])
        context.close()
        context = browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=1,service_workers='block')
        page = context.new_page()
        listen(page)
        prepare()
        check('Coarse pointer context activates production touch layout', 'touch' in page.locator('#hud').get_attribute('class'))
        rectangles('emulated coarse pointer 390x844')
        shot('touch_390x844_hud')
        aim = page.locator('[data-fps56-aim]')
        box = aim.bounding_box()
        page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
        page.mouse.down()
        check('Real HUD pointer hold presents the weapon in aim mode', page.evaluate('v056FirstPersonIsAiming()'))
        shot('touch_aim_presentation')
        page.mouse.up()
        check('Pointer release clears HUD aim mode', not page.evaluate('v056FirstPersonIsAiming()'))
        page.set_viewport_size({'width':844,'height':390})
        page.wait_for_timeout(250)
        rectangles('emulated coarse pointer 844x390')
        shot('touch_844x390_hud')
        check('No native JavaScript exception or same-origin HTTP error', not report['page_errors'] and not report['http_errors'], {'page_errors':report['page_errors'],'http_errors':report['http_errors']})
        after = {str(x.relative_to(ROOT)):sha(x.read_bytes()) for x in (ROOT/'src').rglob('*') if x.is_file()}
        changed = sorted(name for name in before.keys()|after.keys() if before.get(name)!=after.get(name))
        check('Production sources unchanged throughout native pilot', not changed, changed)
        check('HTML unchanged throughout native pilot', sha((ROOT/'index.html').read_bytes()) == args.expect_html_sha)
        report['stage'] = 'complete'
    except Exception as error:
        report.update(stage='failed', error=str(error), traceback=traceback.format_exc())
        print(report['traceback'], flush=True)
        if 'page' in locals():
            try:
                shot('failure')
            except Exception:
                pass
    finally:
        if context:
            context.close()
        if browser:
            browser.close()
        if pw:
            pw.stop()
        if server:
            server.shutdown()
            server.server_close()
        report['cleanup'] = {'context_closed': True,'browser_closed': True,'playwright_stopped': True,'server_closed': True}
        save()
    return int(report['stage'] != 'complete')


if __name__=='__main__':
    raise SystemExit(main())
