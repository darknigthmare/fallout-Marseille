#!/usr/bin/env python3
"""Field-life UI contracts in real Chromium with installed map data.

The private document adapter prepares a funded character, places the camera on
measured clear ground, freezes simulation and introduces a named aid recipient.
Map/terrain HTTP, the production buttons, costs, guards, migrations and browser
storage are real. This is an assisted contract test, not an unmodified playthrough.
"""
from pathlib import Path
import argparse
import hashlib
import json
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

ADAPTER = r"""
window.__FIELD_TEST = {
 failSave:false,
 setup:async()=>{
  v046Cancel();state=migrateState(baseState());
  state.player.zone='geo_huveaune';state.player.discovered=['geo_huveaune'];state.quest.main=2;
  Object.assign(state.v035.prologue,{started:true,stage:9,complete:true});
  for(const id of['scrap','cloth','food','water','ration','stimpak','chemicals','ceramicFilter'])state.inventory[id]=30;
  state.player.hp=50;state.needs.fatigue=80;state.player.rad=25;state.status.infection=0;
  V046.lab=false;V047.auto=false;V018.qaFreeze=true;debugRenderPaused=true;gameStarted=true;inCombat=false;hideAllScreens();
  const p=v015GeoProject('geo_huveaune',43.2966,5.5708);
  await loadZone('geo_huveaune',{geoDirect:true,force:true,silent:true,noTravel:true,spawn:[p[0],1.65,p[2]]});
  v049Own(world);$('hud').classList.add('active');return world?.v046;
 },
 findClearing:()=>{
  world.enemies.forEach(e=>{e.alive=false;});inCombat=false;
  const original=state.player.pos.slice(),stage=v050CampStage();
  for(const r of[0,8,16,24,40,60,80,100])for(let n=0;n<16;n++){
   const angle=n/16*TAU,x=original[0]+Math.sin(angle)*r,z=original[2]+Math.cos(angle)*r;
   const h=v050TravelGround(stage,world,x,z,.5);if(h===null)continue;
   state.player.pos=[x,h+playerEyeHeight(),z];state.player.yaw=angle;onGround=true;
   if(v050CampSpot())return state.player.pos.slice();
  }
  state.player.pos=original;return null;
 },
 state:()=>deepClone(state),
 saved:()=>JSON.parse(localStorage.getItem(SAVE_KEY)),
 contact:()=>{
  const site=V042_CATALOG.find(s=>v050AidSite(s)&&s.macro==='geo_huveaune');
  state.v042.discovered[site.id]={at:new Date().toISOString()};
  const p=state.player.pos,n=addHumanNPC(world,'field-test-recipient','Réceptionnaire témoin','RÉCEPTION',[p[0]+1.5,p[1]-playerEyeHeight(),p[2]],COLORS.clothTan);
  n.v042Site=site.id;return site.id;
 },
 inspect:()=>({camp:state.v050Wasteland.camp,interaction:world.interactables.filter(i=>i.id==='v050-camp').length,rendered:!!V050_WASTELAND.drawCache,lab:V046.lab,origins:[...new Set([...world.v046Records.values()].map(r=>r.source))]}),
 freeze:()=>{V047.auto=false;V018.qaFreeze=true;debugRenderPaused=true;world?.enemies.forEach(e=>{e.alive=false;});inCombat=false;},
 render:()=>{v046RenderSafe();return true;}
};
function v046RenderSafe(){const t=state.playTime||0;sky.draw(currentEnv(),t*1000);renderer.render(collectDraws(t),getCamera(t),currentEnv());}
const fieldTestSave=saveGame;
saveGame=function(...args){return __FIELD_TEST.failSave?false:fieldTestSave(...args);};
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('/workspace/.cloud-setup/fallout-marseille/implementation/gameplay'))
    parser.add_argument('--expect-sha')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    original = (ROOT / 'index.html').read_text()
    digest = hashlib.sha256(original.encode()).hexdigest()
    if args.expect_sha and digest != args.expect_sha:
        raise SystemExit('Build SHA differs from the coordinated test target')
    needle = '\ninit();\nv018AfterInit();'
    assert original.count(needle) == 1
    instrumented = original.replace(needle, '\n' + ADAPTER + needle, 1)
    checks, errors = [], []
    report = {'scope': __doc__, 'html_sha256': digest, 'instrumented_document': True,
              'map_http_mocked': False, 'storage_mocked': False, 'checks': checks, 'page_errors': errors}

    def check(name, ok, detail=None):
        checks.append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ') + name, flush=True)

    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    origin = f'http://127.0.0.1:{port}'
    log = (out / 'SERVER.log').open('w')
    server = subprocess.Popen([sys.executable, 'tools/serve_game.py', '--no-browser', '--no-prepare', '--port', str(port)], cwd=ROOT, stdout=log, stderr=log)
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(origin + '/index.html', timeout=1):
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('Server startup failed')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
            page = context.new_page()
            page.set_default_timeout(30000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.route(origin + '/index.html', lambda route: route.fulfill(status=200, content_type='text/html', body=instrumented))
            page.goto(origin + '/index.html', wait_until='load')
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")

            def fixture(name, *values):
                return page.evaluate('([name,values])=>__FIELD_TEST[name](...values)', [name, list(values)])

            def debug(name, *values):
                return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

            def state():
                return fixture('state')

            def snapshot():
                s = state()
                return {k: s[k] for k in ['player', 'inventory', 'worldTime', 'rep', 'needs', 'v050Wasteland']}

            check('Funded test character loads installed real geography', fixture('setup'))
            page.wait_for_function("__MISTRAL_DEBUG.v047Info().tiles>0&&!__MISTRAL_DEBUG.v047Info().loading", timeout=180000)
            clearing = fixture('findClearing')
            check('Camp footprint is found on production measured terrain', clearing is not None, clearing)
            if not clearing:
                raise RuntimeError('No measured clear camp candidate found in loaded area')
            check('Real pack supplies active geographic vectors', fixture('inspect')['origins'] == ['pack local'])
            debug('v027Open', 'status', 'camp')
            check('Player-visible BIVOUAC tab and deployment button are present', page.locator('[data-p27="sub"][data-arg="camp"]').count() == 1 and page.locator('[data-p27="w50:pitch"]').is_enabled())
            before = state()
            page.locator('[data-p27="w50:pitch"]').click()
            after = state()
            check('Deployment UI spends exact finite materials and persists camp', after['v050Wasteland']['camp'] is not None and before['inventory']['scrap'] - after['inventory']['scrap'] == 3 and before['inventory']['cloth'] - after['inventory']['cloth'] == 1 and fixture('saved')['v050Wasteland']['camp'] == after['v050Wasteland']['camp'])
            fixture('render')
            check('Camp creates actual rendered props and a physical service interaction', fixture('inspect')['interaction'] == 1 and fixture('inspect')['rendered'])
            page.screenshot(path=str(out / '01_bivouac.png'))
            before = state()
            page.locator('[data-p27="w50:craft"][data-arg="ration"]').click()
            after = state()
            check('Production cooking UI pays recipe cost and produces two rations', before['inventory']['food'] - after['inventory']['food'] == 4 and before['inventory']['water'] - after['inventory']['water'] == 1 and after['inventory']['ration'] - before['inventory']['ration'] == 2)
            page.evaluate('__FIELD_TEST.failSave=true')
            before = snapshot()
            page.locator('[data-p27="w50:rest"][data-arg="4"]').click()
            check('Rejected browser save rolls back rest clock, health and supplies', snapshot() == before)
            page.evaluate('__FIELD_TEST.failSave=false')
            before = state()
            page.locator('[data-p27="w50:rest"][data-arg="1"]').click()
            after = state()
            check('Rest UI advances exactly one hour and spends one water', abs((after['worldTime'] - before['worldTime']) % 24 - 1) < 1e-6 and before['inventory']['water'] - after['inventory']['water'] == 1)
            check('Rest reduces fatigue while leaving radiation intact', after['needs']['fatigue'] == max(0, before['needs']['fatigue'] - 25) and after['player']['rad'] == before['player']['rad'])
            page.locator('[data-p27="w50:pack"]').click()
            check('Packing UI retains owned kit and removes deployed camp', state()['v050Wasteland']['kitOwned'] and state()['v050Wasteland']['camp'] is None)
            before = state()['inventory']
            page.locator('[data-p27="w50:pitch"]').click()
            check('Existing kit redeploys without creating or refunding resources', state()['v050Wasteland']['camp'] is not None and state()['inventory'] == before)
            site = fixture('contact')
            debug('v027Set', 'data', 'aid')
            delivery = page.locator('[data-p27="w50:aid"][data-arg="' + site + '|water"]')
            check('ENTRAIDE exposes an enabled delivery only near the fixture recipient', delivery.is_enabled())
            before = state()
            delivery.click()
            after = state()
            check('Delivery UI spends exact supplies and saves a finite receipt', before['inventory']['water'] - after['inventory']['water'] == 2 and after['v050Wasteland']['aid'][site]['water'] and fixture('saved')['v050Wasteland']['aid'][site]['water'])
            check('Received delivery becomes disabled and pays its reward once', delivery.is_disabled() and after['player']['caps'] - before['player']['caps'] == 10)
            page.screenshot(path=str(out / '02_entraide.png'))
            stored = state()['v050Wasteland']
            page.reload(wait_until='load')
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
            page.locator('#btnContinue').click()
            page.wait_for_function("__MISTRAL_DEBUG.v047Info().tiles>0&&!__MISTRAL_DEBUG.v047Info().loading", timeout=180000)
            fixture('freeze')
            check('Real Continue and migration restore camp, kit and delivery ledger', state()['v050Wasteland'] == stored)
            debug('v027Open', 'status', 'camp')
            check('Restored camp remains physically available in its saved geographic scene', debug('v050WastelandInfo')['campNear'] and page.locator('[data-p27="w50:rest"][data-arg="1"]').is_enabled())
            page.screenshot(path=str(out / '03_continue_camp.png'))
            check('No JavaScript exception in the assisted gameplay contracts', not errors, errors)
            check('Coordinated source HTML remains unchanged during the run', hashlib.sha256((ROOT / 'index.html').read_bytes()).hexdigest() == digest)
            context.close()
            browser.close()
    except Exception:
        report['exception'] = traceback.format_exc()
        check('Assisted gameplay UI contracts complete', False, report['exception'])
        print(report['exception'], flush=True)
    finally:
        server.terminate()
        server.wait(timeout=10)
        log.close()
        report.update(passed=sum(c['ok'] for c in checks), failed=sum(not c['ok'] for c in checks), total=len(checks))
        (out / 'GAMEPLAY_UI.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['passed', 'failed', 'total']}), flush=True)
    return bool(report['failed'] or errors)


if __name__ == '__main__':
    raise SystemExit(main())
