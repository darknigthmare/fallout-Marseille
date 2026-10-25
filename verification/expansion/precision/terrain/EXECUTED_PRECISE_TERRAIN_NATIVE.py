#!/usr/bin/env python3
"""Prepared native HTTP pilot for real LiDAR cells, rendering and atlas edges.

No browser without --run. Uses production HTML, local HTTP files, existing
diagnostic sector/camera/freeze APIs and original external GeoTIFF receipts.
No HTML, network or storage substitution; no synthetic NoData is installed.
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


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--expect-html-sha',required=True)
    parser.add_argument('--expect-precise-sha',required=True)
    parser.add_argument('--expect-index-sha',required=True)
    parser.add_argument('--native-cache',type=Path,required=True)
    parser.add_argument('--ready-timeout',type=int,default=300)
    args=parser.parse_args()
    if not args.run:
        print('Prepared only. No server or browser started.');return 0
    sys.path.insert(0,str(ROOT/'tools'))
    import rasterio
    from rasterio.warp import transform
    from rasterio.windows import Window
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright
    started=time.monotonic();args.output.mkdir(parents=True,exist_ok=True)
    executed=Path(__file__).read_bytes();(args.output/'EXECUTED_PRECISE_TERRAIN_NATIVE.py').write_bytes(executed)
    report={'scope':__doc__,'stage':'preflight','checks':[],'stages':[],'shots':[],
            'html_injected':False,'network_mocked':False,'storage_mocked':False,'synthetic_geography':False,
            'contexts_created':0,'maximum_contexts':1,'service_workers_disabled':True,
            'script_sha256':sha(executed),'page_errors':[],'javascript_console_errors':[],
            'resource_console_diagnostics':[],'request_failures':[],'http_errors':[],'responses':[],
            'source_comparisons':[],'mesh_comparisons':[],
            'assistance':['Existing macro and sector loading APIs; actual installed geographic sources, outside the lab.',
                          'Existing render/simulation freeze and measured collision-free diagnostic camera placement.',
                          'Native inverse coordinate conversion from original TIFF pixel centres; no height supplied to the game.',
                          'One declared load/cancel sequence through existing v046Load/v046Cancel; expected HTTP aborts remain recorded.']}
    frozen={};page=server=browser=context=pw=None;origin=None;datasets=[]

    def save():
        report.update(elapsed_seconds=round(time.monotonic()-started,3),passed=sum(c['ok'] for c in report['checks']),
                      failed=sum(not c['ok'] for c in report['checks']),total=len(report['checks']),pinned_inputs=frozen)
        (args.output/'PRECISE_TERRAIN_NATIVE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def check(name,ok,detail=None):
        report['checks'].append({'name':name,'ok':bool(ok),'detail':detail});print(('OK ' if ok else 'FAIL ')+name,flush=True);save()
        if not ok:raise AssertionError(name)
    def stage(name):
        report['stage']=name;report['stages'].append({'name':name,'elapsed_seconds':round(time.monotonic()-started,3)});print('STAGE '+name,flush=True);save()
    def pin(relative):
        raw=(ROOT/relative).read_bytes();checksum=sha(raw)
        if relative in frozen and frozen[relative]!=checksum:raise AssertionError('Frozen source changed: '+relative)
        frozen[relative]=checksum;return raw
    def debug(name,*values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)',[name,list(values)])
    def ll(e,n):
        lon,lat=transform('EPSG:2154','EPSG:4326',[e],[n]);return [lat[0],lon[0]]
    def original(e,n):
        for source,proof in datasets:
            x0,y0=source.xy(0,0);x=(e-x0)/.5;y=(y0-n)/.5
            if not 0<=x<=1999 or not 0<=y<=1999:continue
            a,b=math.floor(x),math.floor(y);c,d=min(1999,a+1),min(1999,b+1);u,v=x-a,y-b
            data=source.read(1,window=Window(a,b,c-a+1,d-b+1));total=weight=0
            for ix,iy,w in ((a,b,(1-u)*(1-v)),(c,b,u*(1-v)),(a,d,(1-u)*v),(c,d,u*v)):
                if w<=1e-12:continue
                z=float(data[iy-b,ix-a])
                if not math.isfinite(z) or z==source.nodata:return {'z':None,'source':proof['file'],'pixel':[x,y]}
                total+=z*w;weight+=w
            return {'z':total/weight,'source':proof['file'],'pixel':[x,y]}
        return None
    def ready():
        deadline=time.monotonic()+args.ready_timeout;last=0
        while time.monotonic()<deadline:
            info=debug('v047Info')
            if info['phase']=='failed':raise RuntimeError('Production staging failed: '+json.dumps(debug('v046Info')))
            if info['tiles']>0 and not info['loading'] and not info['anticipating']:return info
            if time.monotonic()-last>15:print('LOAD '+json.dumps({k:info[k] for k in ('phase','done','total','tiles')}),flush=True);last=time.monotonic()
            page.wait_for_timeout(250)
        raise TimeoutError('Real geographic staging exceeded bounded readiness time')
    def camera_near(e,n):
        points=[ll(e+dx,n+dy) for dy in range(-100,101,10) for dx in range(-100,101,10)]
        clear=page.evaluate("""points=>{const d=__MISTRAL_DEBUG;return points.map(ll=>{const p=d.v046Project('geo_huveaune',...ll),h=d.v046Height(...ll);return{p,h,ll,clear:Number.isFinite(h.height)&&h.height>.4&&!h.missing&&!d.v046Collide(p[0],p[2])};});}""",points)
        report.setdefault('camera_attempts',[]).append({'target':[e,n],'candidates':clear,'map':debug('v047Info'),'precise':debug('v054PreciseTerrainInfo')});save()
        clear=[p for p in clear if p['clear']]
        check('Camera uses actual finite terrain and production collision clearance',bool(clear),[e,n])
        clear.sort(key=lambda p:(p['ll'][0]-ll(e,n)[0])**2+((p['ll'][1]-ll(e,n)[1])*math.cos(math.radians(ll(e,n)[0])))**2)
        p=clear[0];debug('v018CaptureAt',[p['p'][0],p['h']['height']+1.65,p['p'][2]],0,-.38)
        report.setdefault('placements',[]).append(p);save()
    def sector(e,n):
        check('Existing API loads the actual requested source sector',debug('v046Load',*ll(e,n)) is True,[e,n]);ready();camera_near(e,n)
        info=debug('v054PreciseTerrainInfo')
        check('Native active bank and caches respect declared bounds',len(info['activeChunks'])<=9 and info['activeBytes']<=37*1024**2
              and info['cache']['overBudgetBytes']==0 and info['meshCache']['overBudgetBytes']==0,info)
        return info
    def shot(name,label):
        p=debug('getState')['player'];debug('v018CaptureAt',p['pos'],p['yaw'],p['pitch'])
        out=args.output/(name+'.png');page.screenshot(path=str(out));report['shots'].append({'file':out.name,'label':label,'sha256':sha(out.read_bytes())});save()
    def compare(e,n):
        expected=original(e,n);actual=debug('v054PreciseTerrainSample',*ll(e,n))
        record={'easting':e,'northing':n,'latlon':ll(e,n),'source':expected,'runtime':actual}
        report['source_comparisons'].append(record)
        check('Runtime height agrees with the original received GeoTIFF at '+str([e,n]),expected is not None
              and expected['z'] is not None and actual['sourceResource']=='ign_lidar_hd_mnt'
              and actual['height'] is not None and abs(expected['z']-actual['height'])<1e-4,record)
    def mesh():
        detail=debug('v054PreciseTerrainMeshSamples');check('Actual scene contains bounded native half-metre render vertices',detail is not None
              and detail['uniqueVertices']==261121 and detail['nativeSpacingMeters']==.5 and detail['faces']<=520200,detail)
        for p in detail['samples']:
            expected=original(p['easting'],p['northing']);record={'mesh':p,'source':expected}
            report['mesh_comparisons'].append(record)
            check('Actual rendered vertex agrees with its original native source centre',expected is not None and expected['z'] is not None
                  and abs(p['position'][1]+.06-expected['z'])<1e-6,record)
        return detail

    try:
        html=pin('index.html');report['html_sha256']=sha(html)
        check('Coordinated production HTML is exact',sha(html)==args.expect_html_sha)
        source=pin('src/v050/14_precise_terrain.js')
        check('Frozen precise module is the actual production inline source',sha(source)==args.expect_precise_sha and source.strip() in html)
        index=json.loads(pin('data/map_pack/precise/index.json'))
        check('Native atlas equals coordinated SHA',frozen['data/map_pack/precise/index.json']==args.expect_index_sha)
        proof=json.loads(pin('data/map_pack/precise/ACQUISITION.json'))
        for t in index['tiles']:pin(t['path'])
        for p in ('tools/serve_game.py','tools/precise_terrain_sources.py','data/map_pack/precision_archives/manifest.json',
                  'data/map_pack/city/index.json','data/map_pack/city/terrain-index.json','data/map_pack/city/water-index.json'):pin(p)
        for received in proof['sources']:
            path=args.native_cache/received['file'];raw=path.read_bytes()
            check('Original external native GeoTIFF receipt SHA is exact',sha(raw)==received['sha256'],{'file':path.name,'sha256':sha(raw)})
            datasets.append((rasterio.open(path),received))
        check('Source absence is reported honestly rather than installed as a fake hole',index['noDataPoints']==0 and all(t['noDataPoints']==0 for t in index['tiles']))
        report['nodata_scope']='These twelve real source tiles have zero NoData cells. Sentinel propagation and missing triangles are tested by explicit synthetic model fixtures only; no synthetic NoData enters this native run.'
        class Handler(GameHandler):
            def log_message(self,*_):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
        stage('actual_local_server_audits')
        for route,field in (('/__mistral/city-sources','server_city_audit'),('/__mistral/local-data','server_local_audit'),('/__mistral/precise-terrain','server_precise_audit')):
            with urllib.request.urlopen(origin+route,timeout=300) as response:payload=json.load(response);control=response.headers.get('Cache-Control')
            report[field]=payload;check('Actual no-store local audit succeeds: '+route,control=='no-store' and payload.get('ok',payload.get('complete',False)) is True,payload)
        pw=sync_playwright().start()
        browser=pw.chromium.launch(executable_path=chromium_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block');report['contexts_created']+=1
        page=context.new_page();page.set_default_timeout(30000)
        page.on('pageerror',lambda e:report['page_errors'].append(str(e)))
        def console(m):
            if m.type=='error':report['resource_console_diagnostics' if m.text.startswith('Failed to load resource:') else 'javascript_console_errors'].append({'text':m.text,'location':m.location})
        page.on('console',console)
        page.on('requestfailed',lambda r:report['request_failures'].append({'url':r.url,'failure':r.failure,'stage':report['stage'],'elapsed_seconds':round(time.monotonic()-started,3)}))
        def response(r):
            if r.url.startswith(origin+'/'):
                record={'url':r.url,'status':r.status,'from_service_worker':r.from_service_worker};report['responses'].append(record)
                if r.status>=400:report['http_errors'].append(record)
        page.on('response',response);page.on('dialog',lambda d:d.accept())
        stage('native_document')
        document=page.goto(origin+'/index.html?skipboot',wait_until='load',timeout=60000)
        check('Native HTTP document equals frozen production bytes',document.status==200 and sha(document.body())==args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')",timeout=120000)
        page.wait_for_function("typeof __MISTRAL_DEBUG.v054PreciseTerrainInfo==='function'")
        debug('setRenderPaused',True);debug('v047Control',{'auto':False});p=debug('getState')['player'];debug('v018CaptureAt',p['pos'],p['yaw'],p['pitch'])
        debug('v054PreciseTerrainReady');debug('v018LoadMacro','geo_marseille_commune');ready()
        check('Native terrain pilot is outside the synthetic laboratory',debug('v046Info')['lab'] is False)
        stage('vieux_port_native_source_and_render')
        sector(892487.5,6246771)
        for e,n in ((892487.5,6246771),(892488,6246771),(892487.5,6246770.5),(892487.75,6246770.75)):compare(e,n)
        mesh();shot('01_vieux_port_native_half_metre','Actual central Marseille scene with native 0.5 m source nodes in the local rendered LOD.')
        stage('cancel_source_load')
        before={'stamp':debug('v047TerrainIdentity'),'terrain':debug('v054PreciseTerrainInfo')['activeChunks']}
        page.evaluate('ll=>{void __MISTRAL_DEBUG.v046Load(...ll);return true;}',ll(894709.5,6248228.5))
        page.wait_for_function('()=>__MISTRAL_DEBUG.v047Info().loading',timeout=30000)
        debug('v046Cancel');page.wait_for_timeout(500)
        after={'stamp':debug('v047TerrainIdentity'),'terrain':debug('v054PreciseTerrainInfo')['activeChunks']}
        check('Cancelling real source loading keeps the published bank and native cells unchanged',before==after,{'before':before,'after':after})
        compare(892487.5,6246771)
        stage('longchamp_native_north_south')
        sector(894709.5,6248228.5)
        for e,n in ((894709.5,6248228.5),(894709.5,6248228),(894709.5,6248227.5)):compare(e,n)
        mesh();shot('02_longchamp_native_relief','Actual Longchamp native terrain and sourced height alignment.')
        stage('western_atlas_transition')
        sector(891900,6245800)
        outside=debug('v054PreciseTerrainSample',*ll(891920,6245800))
        check('Outside the real native atlas keeps its explicit older terrain source',outside['height'] is not None and outside['sourceResource']!='ign_lidar_hd_mnt',outside)
        shot('03_outside_native_atlas','Older terrain outside the actual native source rectangle, before the measured boundary transition.')
        sector(892010,6245800);detail=mesh();compare(892010,6245800)
        check('Edge LOD is recentered inside actual native support',detail['bounds']['minE']>=892000 and detail['bounds']['maxE']<=894999.5,detail['bounds'])
        west=debug('v054PreciseTerrainRenderedAt',891920,6245800)
        check('Actual coarse triangles remain rendered west of native support',any(not d['native'] for d in west),west)
        east=debug('v054PreciseTerrainRenderedAt',892010,6245800)
        check('Actual native fine triangles render on the inside of the same boundary',any(d['native'] and not d['seam'] for d in east),east)
        report['boundary']={'outsideSample':outside,'outsideRendered':west,'insideRendered':east,'nativeMeshBounds':detail['bounds']}
        shot('04_inside_western_native_edge','Native half-metre LOD at the western boundary; valid older terrain outside the atlas is retained.')
        stage('integrity_and_observations')
        for relative in tuple(frozen):pin(relative)
        check('All frozen runtime files and source indexes remain identical',True,frozen)
        check('Application raises no JavaScript exceptions',not report['page_errors'] and not report['javascript_console_errors'],{'page':report['page_errors'],'console':report['javascript_console_errors']})
        local=[r for r in report['request_failures'] if r['url'].startswith(origin+'/')]
        known=[r for r in local if r['failure']=='net::ERR_ABORTED' and (r['stage']=='cancel_source_load' or urllib.parse.urlsplit(r['url']).path=='/__mistral/local-data')]
        unexpected=[r for r in local if r not in known];report['expected_local_cancellations']=known
        report['external_network_observations']=[r for r in report['request_failures'] if not r['url'].startswith(origin+'/')]
        check('All production source HTTP succeeds except the declared cancellation sequence',not unexpected and not report['http_errors'],{'unexpected':unexpected,'httpErrors':report['http_errors'],'declaredCancellations':known})
        check('Native pilot uses one context and zero service-worker substitutions',report['contexts_created']==1 and not any(r['from_service_worker'] for r in report['responses']))
        report['limitations']=['Twelve central square kilometres, not the whole Marseille municipality.',
                              'The source product is native 0.5 m MNT; this is sample spacing, not a claim of absolute survey accuracy.',
                              'Native half-metre rendering is a bounded local 255 m square with explicit outer LOD and seam.',
                              'Four native captures and diagnostic placements are an assisted bounded pilot, not a human citywide tour.',
                              report['nodata_scope']]
        stage('complete');return 0
    except Exception as e:
        report['exception']={'message':str(e),'traceback':traceback.format_exc()}
        if page:
            try:report['failure_state']={'map':debug('v047Info'),'precise':debug('v054PreciseTerrainInfo')};shot('FAILED_'+report['stage'],'Unmodified native failure state.')
            except Exception as capture:report['failure_capture_error']=str(capture)
        save();print(traceback.format_exc(),flush=True);return 1
    finally:
        for dataset,_ in datasets:dataset.close()
        if context:
            try:context.close()
            except Exception:pass
        if browser:
            try:browser.close()
            except Exception:pass
        if pw:
            try:pw.stop()
            except Exception:pass
        if server:server.shutdown();server.server_close()
        save()


if __name__=='__main__':
    raise SystemExit(main())
