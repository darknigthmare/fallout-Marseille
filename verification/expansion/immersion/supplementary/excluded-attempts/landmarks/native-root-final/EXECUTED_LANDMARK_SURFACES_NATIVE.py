#!/usr/bin/env python3
"""Native HTTP inspection of real IGN MNS landmark surfaces, never a fixture.

One real browser context visits the Major and Notre-Dame de la Garde through
diagnostic geographic navigation. Source loading, mesh publication, collision,
LOS and save/Continue are production functions; cameras/freeze/time selection
are declared assistance. Elevated captures are labelled inspections and are
not evidence of unassisted walking or a complete architectural survey.
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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inverse_lambert(x, y):
    e,n,c = .0818191910428158,.725607765053267,11754255.426096
    value = -math.log(math.hypot(x-700000,12655612.049876-y)/c)/n
    phi = 2*math.atan(math.exp(value))-math.pi/2
    for _ in range(12):
        phi = 2*math.atan(math.exp(value)*((1+e*math.sin(phi))/(1-e*math.sin(phi)))**(e/2))-math.pi/2
    return [math.degrees(phi),3+math.degrees(math.atan2(x-700000,12655612.049876-y)/n)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--expect-html-sha',required=True)
    args = parser.parse_args()
    if not args.run:
        print('Prepared; no browser/server started. Freeze source hashes before --run.')
        return 0
    sys.path.insert(0,str(ROOT/'tools'))
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright
    args.output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    report={'checks':[],'shots':[],'placements':[],'page_errors':[],'console_errors':[],
            'local_http_errors':[],'request_failures':[],'stages':[],'pinned_inputs':{},
            'html_sha256':args.expect_html_sha,'scope':__doc__,'html_injected':False,
            'network_mocked':False,'storage_mocked':False,'service_workers_disabled':True,
            'assistance':['Existing v020Load initializes the historical playing state without item or quest grants; v018LoadMacro then creates the real municipal metric world before sector ensure calls.',
                          'Existing v046Load selects real source sectors; automatic prefetch is paused for bounded observations.',
                          'v018CaptureAt freezes simulation and places real cameras at collision-checked MNT floor points, or explicitly elevated inspection positions.',
                          'Source maximum vertices are selected from the actual acquired payload to compare native mesh heights and production collision/LOS.'],
            'cleanup':{}}
    server=worker=browser=context=pw=page=None
    def save():
        report.update(passed=sum(c['ok'] for c in report['checks']),failed=sum(not c['ok'] for c in report['checks']),total=len(report['checks']),elapsed_seconds=round(time.monotonic()-started,3))
        (args.output/'LANDMARK_SURFACES_NATIVE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def check(name,ok,detail=None):
        report['checks'].append({'name':name,'ok':bool(ok),'detail':detail});print(('OK 'if ok else'FAIL ')+name,flush=True);save()
        if not ok:raise AssertionError(name)
    def pin(relative):
        raw=(ROOT/relative).read_bytes();digest=sha(raw)
        if relative in report['pinned_inputs'] and report['pinned_inputs'][relative]!=digest:raise AssertionError('Input changed '+relative)
        report['pinned_inputs'][relative]=digest;return raw
    def debug(name,*values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)',[name,list(values)])
    def ready():
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            i=debug('v047Info')
            if i['phase']=='failed':raise RuntimeError(json.dumps(i))
            if i['tiles']>0 and not i['loading'] and not i['anticipating']:return i
            page.wait_for_timeout(200)
        raise TimeoutError('Geographic source readiness')
    def document(response):
        check('Native HTTP document equals frozen production HTML',response is not None and response.status==200 and sha(response.body())==args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')",timeout=120000)
        page.wait_for_function("typeof __MISTRAL_DEBUG?.v056LandmarkInfo==='function'")
        debug('setRenderPaused',True);debug('v047Control',{'auto':False})
        i=debug('v056LandmarkReady')
        check('Actual attributed MNS atlas loads without error',i['loaded'] and not i['missing'] and i['error'] is None and i['records']==17,i)
    def shot(name,label):
        p=args.output/(name+'.png');page.screenshot(path=str(p));report['shots'].append({'file':p.name,'sha256':sha(p.read_bytes()),'label':label,'method':'Actual unchanged production WebGL frame; declared frozen diagnostic camera, no image editing.'});save()
    try:
        raw=pin('index.html');module=pin('src/v050/06a_landmark_surfaces.js')
        check('Frozen native bundle includes the exact MNS module',sha(raw)==args.expect_html_sha and module.strip() in raw)
        for relative in ['src/v050/04c_roof_collisions.js','src/v050/06_architecture_sources.js','src/v050/07_facades.js','tools/serve_game.py','tools/build_landmark_surfaces.py']:
            data=pin(relative)
            if relative.startswith('src/'):check('Actual source dependency is in bundle '+relative,data.strip() in raw)
        index=json.loads(pin('data/map_pack/landmark_surfaces/index.json'));data_raw=pin(index['surface']['path']);data=json.loads(data_raw)
        check('Native surface payload matches its exact source descriptor',len(data_raw)==index['surface']['bytes'] and sha(data_raw)==index['surface']['sha256'])
        for relative in data['inputHashes']:check('Original BD TOPO chunk remains exact '+relative,sha(pin(relative))==data['inputHashes'][relative])
        script=Path(__file__).read_bytes();(args.output/'EXECUTED_LANDMARK_SURFACES_NATIVE.py').write_bytes(script);report['script_sha256']=sha(script)
        class Handler(GameHandler):
            def log_message(self,*_args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        origin=f'http://127.0.0.1:{server.server_address[1]}';report['url']=origin+'/index.html?skipboot'
        pw=sync_playwright().start();browser=pw.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage']);report['browser_version']=browser.version
        context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block');page=context.new_page();page.set_default_timeout(30000)
        page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
        page.on('console',lambda m:report['console_errors'].append(m.text)if m.type=='error'else None)
        page.on('response',lambda r:report['local_http_errors'].append({'url':r.url,'status':r.status})if r.url.startswith(origin+'/')and r.status>=400 else None)
        page.on('requestfailed',lambda r:report['request_failures'].append({'url':r.url,'failure':r.failure}))
        page.on('dialog',lambda d:d.accept())
        document(page.goto(report['url'],wait_until='load',timeout=60000));debug('v020Load','aubagne');debug('v046SetTime',12)
        debug('v051CityReady');debug('v052ArchitectureReady')
        check('Actual municipal metric world is initialized before sector navigation',debug('v018LoadMacro','geo_marseille_commune')=='geo_marseille_commune');ready()
        sites=[('major',43.2999,5.3648,'BATIMENT0000000258938065',5),('garde',43.284,5.3712,'BATIMENT0000000273400985',11)]
        saved_camera=None
        for name,lat,lon,target,expected in sites:
            report['stage']=name;report['stages'].append({'name':name,'elapsed_seconds':time.monotonic()-started});save()
            loaded=debug('v046Load',lat,lon)
            check('Production geographic sector loads '+name,loaded is True,{'result':loaded,'map':debug('v046Info'),'city':debug('v051CityInfo'),'mns':debug('v056LandmarkInfo')});ready()
            info=debug('v056LandmarkInfo');rows=[r for r in info['applied']if r['siteContext']==('Cathédrale de la Major'if name=='major'else'Notre-Dame de la Garde')]
            check('Actual imported landmark surfaces are attached '+name,len(rows)==expected,rows)
            rec=next(r for r in data['records']if r['cleabs']==target);peak=max(rec['vertices'],key=lambda p:p[2]);peak_ll=inverse_lambert(*peak[:2]);world_id=debug('v020Stats')['id'];point=debug('v046Project',world_id,*peak_ll)
            actual=debug('v056LandmarkSurface',target,point[0],point[2]);report[name+'_surface']=actual
            check('Native cap uses exact source geometry '+name,actual['rawGeometry']==rec['rawGeometry']and actual['sourceProperties']==rec['sourceProperties'])
            check('Native roof triangle count equals acquired clipped source '+name,actual['roofTriangles']==len(rec['faces'])and actual['roofVertices']==len(rec['vertices']))
            check('Actual highest vertex retains measured elevation '+name,abs(actual['height']-peak[2])<.0001,{'source':peak,'native':actual['height']})
            check('Measured silhouette adds the source summit above the former envelope '+name,peak[2]-(rec['sourceProperties']['altitude_minimale_sol']+rec['sourceProperties']['hauteur'])>25,{'sourceMaximum':peak[2],'oldFlatTop':rec['sourceProperties']['altitude_minimale_sol']+rec['sourceProperties']['hauteur']})
            above=[point[0],peak[2]+3,point[2]];below=[point[0],peak[2]-.5,point[2]]
            check('Production line of sight hits the real upper cap '+name,not debug('v020LOS',above,below),{'from':above,'to':below})
            check('Air above the measured summit stays clear '+name,debug('v020LOS',above,[above[0]+.3,above[1],above[2]]))
            # Find a real MNT floor point around the site; no terrain values,
            # source vertices or collision records are replaced.
            candidate_ll=[[lat+math.cos(a*math.tau/16)*r/111320,lon+math.sin(a*math.tau/16)*r/(111320*math.cos(math.radians(lat)))]for r in [65,85,110,140]for a in range(16)]
            candidates=page.evaluate("""([lls,id])=>lls.map(ll=>{const d=__MISTRAL_DEBUG,p=d.v046Project(id,...ll),h=d.v046Height(...ll);return{ll,p,height:h.height,sources:h.sources,clear:Number.isFinite(h.height)&&!h.missing&&!d.v020Collides([p[0],h.height+1.65,p[2]])};}).filter(p=>p.clear)""",[candidate_ll,world_id])
            check('A measured collision-free MNT viewing point exists '+name,bool(candidates))
            cam=candidates[0];pos=[cam['p'][0],cam['height']+1.65,cam['p'][2]];dx,dz=point[0]-pos[0],point[2]-pos[2];yaw=math.atan2(dx,-dz);pitch=math.atan2(peak[2]-15-pos[1],math.hypot(dx,dz))
            debug('v018CaptureAt',pos,yaw,pitch);report['placements'].append({'site':name,'kind':'measured-ground-view','position':pos,'yaw':yaw,'pitch':pitch,'MNT':cam});shot(name+'_ground','Vue à hauteur des yeux depuis un sol MNT réel, placement assisté.')
            if name=='major':
                layout=page.evaluate("""()=>{const box=e=>{if(!e)return null;const r=e.getBoundingClientRect(),s=getComputedStyle(e);return{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height,visible:s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0,text:e.textContent};};return{legacy:box(document.querySelector('.geo-hud')),attribution:box(document.getElementById('geoAttribution')),quickbar:box(document.getElementById('v020Quickbar')),viewport:{width:innerWidth,height:innerHeight}};}""")
                attribution,bar,viewport=layout['attribution'],layout['quickbar'],layout['viewport']
                check('Legacy geographic debug cartouche is hidden in the actual FPS view',layout['legacy']is not None and not layout['legacy']['visible'],layout['legacy'])
                check('Compact real source attribution stays fully inside the viewport',attribution is not None and attribution['visible']and attribution['left']>=0 and attribution['top']>=0 and attribution['right']<=viewport['width']and attribution['bottom']<=viewport['height']and all(s in attribution['text']for s in ['OpenStreetMap','Cadastre','IGN']),{'attribution':attribution,'viewport':viewport})
                check('Compact attribution lies below the quickbar without covering its controls',bar is not None and bar['visible']and attribution is not None and attribution['top']>=bar['bottom'],{'attribution':attribution,'quickbar':bar})
                page.locator('#geoAttribution').click()
                page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='STATUS'")
                sources_open=page.locator('#v047StatusContent .v047-integrity').is_visible()
                page.locator('#v047CloseStatus').click()
                page.wait_for_function("__MISTRAL_DEBUG.v020Stats().mode==='PLAYING'")
                check('Visible source attribution opens the real map/source panel and its Retour button resumes play',sources_open and page.locator('#v018StatusScreen').is_hidden())
            elevated=[point[0]-95,peak[2]+55,point[2]+95];dx,dz=point[0]-elevated[0],point[2]-elevated[2];eyaw=math.atan2(dx,-dz);epitch=math.atan2(peak[2]-20-elevated[1],math.hypot(dx,dz));debug('v018CaptureAt',elevated,eyaw,epitch);report['placements'].append({'site':name,'kind':'elevated-source-inspection','position':elevated,'yaw':eyaw,'pitch':epitch});shot(name+'_elevated','Inspection élevée du MNS découpé ; position de diagnostic hors parcours piéton.')
            debug('v018CaptureAt',pos,yaw,pitch);saved_camera={'pos':pos,'yaw':yaw,'pitch':pitch,'target':target}
        info=debug('v056LandmarkInfo')
        check('MNS below the unchanged IGN base is explicitly refused',any(r['cleabs']=='BATIMENT0000000273400986'and'base'in r['reason']for r in info['rejected']),info['rejected'])
        check('Original architecture contextual labels remain a separate atlas',debug('v052ArchitectureInfo')['records']==12)
        debug('v046Save');before=debug('getState')['player'];report['saved_player']=before
        document(page.reload(wait_until='load',timeout=60000));page.locator('#btnContinue').click();ready()
        restored=debug('getState')['player'];cap=debug('v056LandmarkSurface',saved_camera['target'])
        check('Real Continue preserves the selected position and yaw',math.dist(before['pos'],restored['pos'])<.01 and abs(before['yaw']-restored['yaw'])<1e-7,{'before':before,'after':restored})
        check('Real Continue reapplies source MNS without saving a copied mesh',cap is not None and cap['roofTriangles']==len(next(r for r in data['records']if r['cleabs']==saved_camera['target'])['faces']) and 'v056MeasuredSurface'not in json.dumps(debug('getState')))
        debug('v018CaptureAt',saved_camera['pos'],saved_camera['yaw'],saved_camera['pitch']);shot('garde_continue','Même source MNS après rechargement et bouton Continuer natif.')
        check('No JavaScript page exception in the native inspection',not report['page_errors'],report['page_errors'])
        check('No missing local source resource or HTTP failure',not report['local_http_errors'],report['local_http_errors'])
        for relative in list(report['pinned_inputs']):pin(relative)
        check('All observed production/source inputs stayed unchanged',True)
        report['stage']='complete'
    except Exception as error:
        report['stage']='failed';report['error']=str(error);report['traceback']=traceback.format_exc();print(report['traceback'],flush=True)
    finally:
        if context:context.close();report['cleanup']['context_closed']=True
        if browser:browser.close();report['cleanup']['browser_closed']=True
        if pw:pw.stop();report['cleanup']['playwright_stopped']=True
        if server:server.shutdown();server.server_close();report['cleanup']['server_closed']=True
        if worker:worker.join(timeout=5);report['cleanup']['server_thread_joined']=not worker.is_alive()
        save()
    return int(report.get('stage')!='complete'or report['failed']!=0)


if __name__=='__main__':
    raise SystemExit(main())
