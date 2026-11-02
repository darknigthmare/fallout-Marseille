#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,hashlib,time
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=R/'JOUER_FALLOUT_MISTRAL_v0.37.html';MAN=json.loads((R/'data/map_pack/manifest_v037.json').read_text())
checks=[];errors=[]
def ck(name,cond,detail=None):checks.append({'name':name,'ok':bool(cond),'detail':detail});print(('OK ' if cond else 'FAIL ')+name,flush=True)
def vi(n:int)->bytes:
 out=bytearray()
 while True:
  b=n&127;n>>=7;out.append(b|(128 if n else 0))
  if not n:return bytes(out)
def zz(n:int)->int:return (n<<1)^(n>>63)
def field(num:int,wire:int,payload:bytes|int)->bytes:
 head=vi((num<<3)|wire)
 if wire==0:return head+vi(int(payload))
 assert wire==2 and isinstance(payload,(bytes,bytearray));return head+vi(len(payload))+payload
def packed(vals):return b''.join(vi(v) for v in vals)
def value_string(s):return field(1,2,s.encode())
def feature(fid,geom_type,geometry,tags=(0,0)):
 return field(1,0,fid)+field(2,2,packed(tags))+field(3,0,geom_type)+field(4,2,packed(geometry))
def layer(name,features,key='class',value='primary'):
 raw=field(15,0,2)+field(1,2,name.encode())
 for f in features:raw+=field(2,2,f)
 raw+=field(3,2,key.encode())+field(4,2,value_string(value))+field(5,0,4096)
 return field(3,2,raw)
# Full-width line at y=2048 and base HLOD building in NW quarter.
line=[9,zz(0),zz(2048),10,zz(4096),zz(0)]
base_poly=[9,zz(2500),zz(2500),26,zz(500),zz(0),zz(0),zz(500),zz(-500),zz(0),15]
BASE=layer('transportation',[feature(1,2,line)])+layer('building',[feature(10,3,base_poly)],'class','building')
# Same geographic footprint at z16; duplicated twice on purpose.
cad_poly=[9,zz(1800),zz(1800),26,zz(2000),zz(0),zz(0),zz(2000),zz(-2000),zz(0),15]
CAD=layer('batiments',[feature(20,3,cad_poly),feature(21,3,cad_poly)],'nature','dur')
# Static contracts.
ck('manifest v0.37 exact',MAN['version']=='0.37.0' and MAN['counts']=={'base':367,'cadastre':5517,'total':5884},MAN.get('counts'))
ck('relay v0.37 in every row',all('/fallout-mistral-map-v037/' in r['relay'] for r in MAN['tiles']))
requests={'coverage':0,'base':0,'cadastre':0,'direct':0}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 # The production sandbox blocks all navigations and native IndexedDB on opaque origins.
 # Install an API-compatible in-memory adapter before loading the exact HTML.
 p.evaluate(r'''() => {
  const databases=new Map();
  function open(name,version=1){
   const req={result:null,error:null};setTimeout(()=>{
    let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}
    const db={
     get objectStoreNames(){return{contains:n=>state.stores.has(n)}},
     createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},
     transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,finished=false;
      const maybe=()=>setTimeout(()=>{if(!pending&&!finished){finished=true;tx.oncomplete?.()}},0);
      tx.objectStore=n=>{if(!state.stores.has(n))throw new Error('missing store '+n);const store=state.stores.get(n),opts=state.options.get(n)||{};
       const request=(fn)=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.();tx.onerror?.()}finally{pending--;maybe()}},0);return q};
       return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);if(key===undefined)throw new Error('key required');store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())};};maybe();return tx
     },close(){}
    };req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.();
   },0);return req
  }
  Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});
  Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}});
 }''')
 def relay(route,req):
  u=req.url
  if u.endswith('/coverage'):
   requests['coverage']+=1;route.fulfill(status=200,content_type='application/json',body=json.dumps({'service':'fallout-mistral-map-v037','version':'0.37.0','plan':{'base':367,'cadastre':5517,'total':5884},'cache':{'base':{'count':1,'bytes':len(BASE),'hits':4},'cadastre':{'count':1,'bytes':len(CAD),'hits':3},'total':2,'totalBytes':len(BASE)+len(CAD),'newest':'2026-09-19T00:56:40Z'}}));return
  if '/tile/base/' in u:
   requests['base']+=1;route.fulfill(status=200,body=BASE,headers={'content-type':'application/x-protobuf','x-map-cache':'miss','x-map-sha256':hashlib.sha256(BASE).hexdigest(),'x-map-bytes':str(len(BASE)),'x-map-fetched-at':'2026-09-19T00:56:40Z'});return
  if '/tile/cadastre/' in u:
   requests['cadastre']+=1;route.fulfill(status=200,body=CAD,headers={'content-type':'application/x-protobuf','x-map-cache':'miss','x-map-sha256':hashlib.sha256(CAD).hexdigest(),'x-map-bytes':str(len(CAD)),'x-map-fetched-at':'2026-09-19T00:56:40Z'});return
  route.continue_()
 p.route('**/fallout-mistral-map-v037/**',relay)
 p.set_content(H.read_text(),wait_until='load');p.wait_for_timeout(3500)
 def c(name,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+name+'(...a)',list(args))
 try:
  info=c('v037Info');ck('runtime v0.37',info['version']=='0.37.0',info)
  ck('IndexedDB available on local origin',c('v037Local')['error'] is None,c('v037Local'))
  ck('coverage cloud verified',c('v037Cloud'))
  cloud=c('v037Info')['cloud'];ck('coverage reports only acquired files',cloud['total']==2 and cloud['bytes']==len(BASE)+len(CAD),cloud)
  ck('exact manifest accepts real sample',c('v037Allowed','base',14,8437,6001) and c('v037Allowed','cadastre',16,33750,24006))
  ck('exact manifest rejects out-of-plan',not c('v037Allowed','base',14,0,0) and not c('v037Allowed','cadastre',16,33748,1))
  c('v027Dispatch','v037-toggle-auto');c('v018LoadMacro','geo_marseille');p.wait_for_timeout(300)
  # Explicit adjacent base tiles + corresponding cadastre tile.
  c('v018Queue','base',14,8437,6001);c('v018Queue','base',14,8438,6001);c('v018Queue','cadastre',16,33750,24006);p.wait_for_timeout(1800)
  st=c('v037Info');ck('three fixture tiles rendered',st['runtime']['loaded']>=3,st['runtime'])
  geom=c('v018Geometry');topo=c('v037Topology');ck('cross-tile road seam matched',topo['seamMatched']>=1,topo);ck('no confirmed seam defect for loaded pair',topo['seamUnpaired']==0,topo)
  ck('cadastre duplicate suppressed',topo['duplicatesSuppressed']>=1,topo);ck('base HLOD building replaced',topo['baseBuildingsSuppressed']>=1,topo)
  local=c('v037Local');ck('IndexedDB contains fetched PBF',local['count']>=3 and local['bytes']>0,local)
  # Same tile now comes from IndexedDB and must not issue a new relay call.
  before=requests['base'];got=c('v037Get','base',14,8437,6001);after=requests['base'];ck('second read served by local cache',got['source']=='cache' and got['bytes']==len(BASE),{'got':got,'before':before,'after':after,'requests':requests})
  # Queue filter is enforced, not only exposed as a helper.
  ck('out-of-manifest queue refused',c('v018Queue','base',14,0,0) is False)
  # Directional prefetch adds only exact-manifest jobs; then cancellation is immediate.
  added=c('v037Near',1);ck('directional prefetch schedules valid neighbors',added>0,added);c('v037Cancel');p.wait_for_timeout(100)
  # Player UI.
  c('v027Open','map','cache');txt=p.locator('#pipContent').inner_text();flat=''.join(txt.split());ck('Pip-Boy cache screen shows cloud and local',('CACHE' in txt and str(cloud['total']) in txt and str(local['count']) in txt),txt[:1200]);ck('terrain remains truthful 0/8','0/8' in flat,txt[:1200]);c('closePip')
  c('v037OpenStatus');txt2=p.locator('#v018StatusScreen').inner_text();norm=' '.join(txt2.split());ck('status separates plan and acquired files','5 884' in norm and 'cache cloud' in norm.lower(),txt2[:1200])
  ck('no JavaScript exception',not errors,errors)
 except Exception as e:ck('browser scenario',False,repr(e))
 b.close()
rep={'version':'0.37.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'requests':requests,'checks':checks,'scope':'Exact v0.37 HTML via set_content. Controlled synthetic MVT for seam/dedup QA only; IndexedDB logic uses an explicit API-compatible memory adapter because opaque-origin storage is blocked. Live cloud cache verified separately. No official terrain bundled.'}
(O/'QA_V037.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2));print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors,'requests':requests},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errors))
