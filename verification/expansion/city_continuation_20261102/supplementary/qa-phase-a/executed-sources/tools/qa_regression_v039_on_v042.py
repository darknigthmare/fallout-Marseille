#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,hashlib,math
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=R/'JOUER_FALLOUT_MISTRAL_v0.42.html';checks=[];errors=[]
def ck(n,c,d=None):checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
REGIONS=[
 {'macro':'geo_marseille','valid_points':22282,'missing_points':3639,'min_elevation':-17.9,'max_elevation':643.91,'mean_elevation':109.791,'bytes':144478},
 {'macro':'geo_huveaune','valid_points':25921,'missing_points':0,'min_elevation':24.82,'max_elevation':708.45,'mean_elevation':210.666,'bytes':176122},
 {'macro':'geo_garlaban','valid_points':25921,'missing_points':0,'min_elevation':60,'max_elevation':1031.19,'mean_elevation':304.142,'bytes':178206},
 {'macro':'geo_calanques','valid_points':21063,'missing_points':4858,'min_elevation':-8.52,'max_elevation':638.19,'mean_elevation':131.902,'bytes':137635},
 {'macro':'geo_laciotat','valid_points':21717,'missing_points':4204,'min_elevation':-8.94,'max_elevation':560.11,'mean_elevation':150.016,'bytes':144586},
 {'macro':'geo_frioul','valid_points':6198,'missing_points':19723,'min_elevation':-67.51,'max_elevation':81.92,'mean_elevation':2.891,'bytes':121364},
 {'macro':'geo_etoile','valid_points':25921,'missing_points':0,'min_elevation':64.99,'max_elevation':768.45,'mean_elevation':317.122,'bytes':178722},
 {'macro':'geo_saintebaume','valid_points':25921,'missing_points':0,'min_elevation':74.49,'max_elevation':1029.36,'mean_elevation':367.892,'bytes':179063},
]
STATUS={'service':'fallout-mistral-terrain-v039','version':'0.39.0','source':{'resource':'ign_rge_alti_wld','title':'Pyramide RGE Alti France Entière (Métropole, DOM et COM couvertes)','license':'Licence Ouverte 2.0','verticalDatum':'NGF-IGN69 — altitude normale, France continentale'},'grid':{'width':161,'height':161},'expected':[r['macro'] for r in REGIONS],'count':8,'complete':True,'totalBytes':1260176,'totalValid':174944,'totalMissing':32424,'regions':REGIONS}
GRID={'version':'0.39.0','macro':'geo_marseille','bbox':[43.22,5.285,43.34,5.51],'width':5,'height':5,'rowOrder':'north-to-south','values':[100,110,120,130,140,90,100,None,120,130,80,90,-99999,110,120,70,80,90,100,110,60,70,80,90,100],'source':'RGE ALTI IGN','sourceResource':'ign_rge_alti_wld','sourceTitle':STATUS['source']['title'],'license':'Licence Ouverte 2.0','verticalDatum':STATUS['source']['verticalDatum']}
VECTOR_STATUS={'service':'fallout-mistral-map-v038','version':'0.38.0','plan':{'base':367,'cadastre':5517,'total':5884},'cache':{'base':{'coordinates':367,'pbf':367,'empty':0,'bytes':29456613,'hits':31},'cadastre':{'coordinates':5517,'pbf':4190,'empty':1327,'bytes':57517126,'hits':1},'total':5884,'totalBytes':86973739,'totalEmpty':1327,'complete':True,'newest':'2026-09-19T01:51:42Z'}}
requests={'status':0,'terrain':0,'vector':0}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate(r'''() => {
  const databases=new Map();
  function open(name,version=1){const req={result:null,error:null};setTimeout(()=>{let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}const db={get objectStoreNames(){return{contains:n=>state.stores.has(n)}},createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,finished=false;const maybe=()=>setTimeout(()=>{if(!pending&&!finished){finished=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{if(!state.stores.has(n))throw new Error('missing store '+n);const store=state.stores.get(n),opts=state.options.get(n)||{};const request=fn=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.();tx.onerror?.()}finally{pending--;maybe()}},0);return q};return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())}};maybe();return tx},close(){}};req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}
  Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}});
 }''')
 def relay(route,req):
  u=req.url
  if u.endswith('/fallout-mistral-terrain-v039/status'):
   requests['status']+=1;route.fulfill(status=200,content_type='application/json',body=json.dumps(STATUS),headers={'access-control-allow-origin':'*'});return
  if '/fallout-mistral-terrain-v039/terrain/geo_marseille' in u:
   requests['terrain']+=1;route.fulfill(status=200,content_type='application/json',body=json.dumps(GRID),headers={'access-control-allow-origin':'*','etag':'"sha256-fixture"','x-terrain-valid':'23','x-terrain-missing':'2','x-terrain-source':'ign_rge_alti_wld'});return
  if u.endswith('/fallout-mistral-map-v038/coverage'):
   requests['vector']+=1;route.fulfill(status=200,content_type='application/json',body=json.dumps(VECTOR_STATUS),headers={'access-control-allow-origin':'*'});return
  route.continue_()
 p.route('**/fallout-mistral-terrain-v039/**',relay);p.route('**/fallout-mistral-map-v038/**',relay)
 p.set_content(H.read_text(),wait_until='load');p.wait_for_timeout(2800)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  info=c('v039Info');ck('runtime v0.42',info['version']=='0.42.0',info.get('version'));plan=c('v039TerrainPlan');ck('plan 8 × 161²',plan['regions']==8 and plan['width']==161 and plan['height']==161 and plan['totalSamples']==207368,plan)
  cloud=info['terrain']['cloud'];ck('cloud status 8/8',cloud['complete'] and cloud['count']==8 and cloud['totalValid']==174944 and cloud['totalMissing']==32424,cloud);ck('official resource named',cloud['source']['resource']=='ign_rge_alti_wld',cloud['source'])
  c('v018LoadMacro','geo_marseille');p.wait_for_timeout(250);c('v039TerrainClear')
  before_cloud=requests['terrain'];got=c('v039TerrainGet','geo_marseille');ck('cloud grid loads',got['source']=='cloud' and requests['terrain']==before_cloud+1 and got['valid']==23 and got['missing']==2 and got['min']==60 and got['max']==140,got)
  before=requests['terrain'];got2=c('v039TerrainGet','geo_marseille');ck('terrain is cached in IndexedDB',got2['source']=='indexeddb' and requests['terrain']==before,{'got':got2,'requests':requests})
  ck('terrain applies to current macro',c('v039TerrainApply',GRID) is True)
  info2=c('v039Info');active=info2['terrain']['active'];ck('active terrain reports NoData',active['valid']==23 and active['missing']==2 and active['min']==60 and active['max']==140,active)
  nw=c('geoProject','geo_marseille',43.34,5.285);z=c('v039TerrainAbsolute',nw[0],nw[2]);ck('north-west orientation is correct',abs(z-100)<.01,{'point':nw,'z':z})
  center=c('geoProject','geo_marseille',43.28,5.3975);zc=c('v039TerrainAbsolute',center[0],center[2]);ck('NoData grid point stays absent',zc is None,{'point':center,'z':zc})
  # A nearby interpolation has valid neighbours and must not use the -99999 sentinel.
  near=c('geoProject','geo_marseille',43.2875,5.37);zn=c('v039TerrainAbsolute',near[0],near[2]);ck('interpolation ignores NoData sentinel',zn is not None and -100<zn<200,{'z':zn})
  bad={**GRID,'values':[None]*25};ck('all-NoData terrain is rejected',c('v039TerrainApply',bad) is False)
  mesh=c('v039TerrainMesh');ck('terrain mesh is generated',mesh is not None and mesh['vertices']>0 and mesh['faces']>0 and mesh['maxY']>mesh['minY'],mesh)
  c('v027Open','map','terrain');text=' '.join(p.locator('#pipContent').inner_text().split());ck('Pip-Boy terrain panel','RELIEF OFFICIEL' in text and '8/8' in text and '174 944' in text and '32 424' in text,text[:1600]);c('closePip')
  c('v039OpenStatus');st=' '.join(p.locator('#v018StatusScreen').inner_text().split());ck('status separates vector and terrain','5 884/5 884' in st and '8/8' in st and 'NoData' in st,st[:1600]);ck('no JavaScript exception',not errors,errors)
 except Exception as e:ck('browser scenario',False,repr(e))
 b.close()
rep={'version':'0.42.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'requests':requests,'checks':checks,'scope':'Exact v0.42 HTML. Controlled RGE ALTI JSON fixture plus mocked 8/8 cloud status. IndexedDB uses an API-compatible memory adapter because opaque-origin native storage is blocked. Live terrain proof is verified separately.'}
(O/'QA_REGRESSION_V039_ON_V042.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors,'requests':requests},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errors))
