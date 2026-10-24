#!/usr/bin/env python3
"""Real local-source endpoint/UI proof, then labelled response/error fixtures.

The first inventory comes from the actual running server and installed files.
Only the optional summary endpoint is intercepted in later presentation cases;
these are not geographic accuracy or full-game traversal tests.
"""
from pathlib import Path
import argparse, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8767/index.html?skipboot=1')
    parser.add_argument('--output',type=Path,default=Path('/workspace/.cloud-setup/fallout-marseille/implementation/current/source-status'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    checks=[];errors=[];requests=[];digest=None;real_inventory=None
    def check(name,ok,detail=None,scope='real local server and UI'):
        checks.append({'name':name,'ok':bool(ok),'detail':detail,'scope':scope});print(('OK ' if ok else 'FAIL ')+name,flush=True)
        if not ok:raise AssertionError(name+': '+str(detail))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        # Intercept only the diagnostic endpoint in later fixture cases. A
        # service worker would otherwise own those fetches outside page.route.
        context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block')
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:requests.append(r.url) if '/__mistral/world-sources' in r.url else None)
        try:
            response=page.goto(args.url,wait_until='load',timeout=60000);digest=hashlib.sha256(response.body()).hexdigest()
            page.locator('#menuScreen.active').wait_for(timeout=45000)
            page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')")
            page.evaluate('__MISTRAL_DEBUG.setRenderPaused(true)')
            before=page.evaluate('JSON.stringify(Object.entries(localStorage))')
            page.locator('#v050MapStatus').click()
            page.wait_for_function("__MISTRAL_DEBUG.v050SourceStatus().data?.present===true&&!__MISTRAL_DEBUG.v050SourceStatus().pending",timeout=45000)
            real_inventory=page.evaluate('__MISTRAL_DEBUG.v050SourceStatus().data')
            panel=page.locator('[data-v050-source-status]');body=panel.inner_text()
            check('Live endpoint confirms the installed vector additions',real_inventory['totalBuildings']==1404 and real_inventory['totalRoads']==472,{'buildings':real_inventory['totalBuildings'],'roads':real_inventory['totalRoads']})
            check('Live inventory lists both real terrain grids',sum(len(r['terrain']) for r in real_inventory['regions'])==2)
            check('Visible panel distinguishes sample spacing and survey accuracy','espacement des échantillons' in body and 'pas une précision altimétrique' in body)
            check('Visible panel identifies local coverage instead of a whole-city claim','Couverture locale uniquement' in body and '43.29300' in body and '5.57600' in body)
            check('LiDAR source date and nearest resampling remain visible','26/06/2021' in body and 'nearest' in body and '2025-03-14' in body)
            check('Missing heights and missing-Z flags keep precise labels','sans hauteur déclarée' in body and 'Z signalé comme manquant' in body)
            check('Inspection/extraction are not described as a new survey','date d’inspection n’est pas une date de levé' in body and 'date d’extraction' in body)
            check('Opening the inventory leaves campaign storage unchanged',page.evaluate('JSON.stringify(Object.entries(localStorage))')==before)
            start=len(requests)
            page.evaluate('Promise.all([__MISTRAL_DEBUG.v050RefreshSourceStatus(),__MISTRAL_DEBUG.v050RefreshSourceStatus()])')
            check('Concurrent refreshes share a single real local request',len(requests)==start+1,{'requests':len(requests)-start})
            page.screenshot(path=str(args.output/'SOURCE_STATUS_REAL.png'),full_page=False)
            panel.locator('.v050-source-terrain').last.scroll_into_view_if_needed()
            page.screenshot(path=str(args.output/'SOURCE_STATUS_TERRAIN.png'),full_page=False)
            fixture_scope='controlled summary-endpoint presentation fixture'
            pattern='**/__mistral/world-sources'
            page.route(pattern,lambda route:route.abort())
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            text=panel.inner_text()
            check('Unavailable server has a clear state and hides stale ready counters','serveur local est inaccessible' in text and 'dans les ajouts vérifiés' not in text,text,scope=fixture_scope)
            page.locator('#v047CloseStatus').click()
            check('A failed optional audit does not trap the player in a loading screen',page.evaluate("__MISTRAL_DEBUG.getMode()==='MENU'"),scope=fixture_scope)
            page.locator('#v050MapStatus').click();page.unroute(pattern)
            page.route(pattern,lambda route:route.fulfill(status=503,content_type='application/json',body='{"ok":false}'))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('Unverified source files are not presented as ready','n’a pas pu valider les sources locales' in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            page.route(pattern,lambda route:route.fulfill(status=503,content_type='text/plain',body='Ressource locale indisponible'))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('Service-worker network fallback does not claim a failed file validation','serveur local est inaccessible' in panel.inner_text() and 'n’a pas pu valider' not in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            page.route(pattern,lambda route:route.fulfill(status=404,content_type='text/plain',body='not found'))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('An older server explains that this diagnostic is unavailable','ne fournit pas ce diagnostic' in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            malicious='<img src=x onerror="window.__source_status_xss=true">'
            fake={'ok':True,'present':True,'totalBuildings':1,'totalRoads':0,'regions':[{'id':'test-region','source':{'name':malicious},'buildings':1,'roads':0,'coverage':[],'terrain':[]}]}
            page.route(pattern,lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(fake)))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('Source names are inert text, never executable markup',malicious in panel.inner_text() and panel.locator('img').count()==0 and page.evaluate('window.__source_status_xss===undefined'),scope=fixture_scope)
            check('Undeclared quality values remain unknown','sans hauteur déclarée non renseigné' in panel.inner_text() and 'date de levé' in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            page.route(pattern,lambda route:route.fulfill(status=200,content_type='application/json',body='{"ok":true,"present":false,"regions":[],"totalBuildings":0,"totalRoads":0}'))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('An absent optional pack is clearly distinguished from verified additions','Aucune source complémentaire installée' in panel.inner_text() and 'fidélité 1:1' in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            page.route(pattern,lambda route:route.fulfill(status=200,content_type='application/json',body='{"ok":true,"regions":42}'))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('A malformed summary cannot become a successful inventory','Rapport des sources incompatible' in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            page.route(pattern,lambda route:route.fulfill(status=200,content_type='application/json',body='not valid JSON'))
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            check('Unreadable JSON has a user-facing recovery message','diagnostic local est illisible' in panel.inner_text(),scope=fixture_scope)
            page.unroute(pattern)
            page.evaluate('__MISTRAL_DEBUG.v050RefreshSourceStatus()')
            restored=page.evaluate('__MISTRAL_DEBUG.v050SourceStatus()')
            check('Retry restores the actual verified local inventory after controlled failures',not restored['error'] and restored['data']['totalBuildings']==1404 and restored['data']['totalRoads']==472)
            check('All summary requests remain on the local server origin',all(url.startswith(args.url.split('/index.html')[0]+'/__mistral/world-sources') for url in requests))
            check('No JavaScript exceptions in the source-quality panel',not errors,errors)
        except Exception as error:
            checks.append({'name':'Source-quality browser scenario completes','ok':False,'detail':str(error)});print('FAIL '+str(error),flush=True)
            page.screenshot(path=str(args.output/'failure.png'))
        finally:
            report={'html_sha256':digest,'scope':'Actual local inventory and UI first; labelled controlled error/presentation fixtures thereafter. Service worker disabled to intercept only this diagnostic endpoint. No PWA or full-territory accuracy claim.','realInventory':real_inventory,'passed':sum(c['ok'] for c in checks),'failed':sum(not c['ok'] for c in checks),'total':len(checks),'errors':errors,'checks':checks}
            (args.output/'SOURCE_STATUS_BROWSER.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps({k:report[k] for k in ['passed','failed','total','errors']}),flush=True);context.close();browser.close()
    return int(bool(report['failed'] or errors))

if __name__=='__main__':raise SystemExit(main())
