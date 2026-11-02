#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,hashlib
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
H=R/'JOUER_FALLOUT_MISTRAL_v0.41.html';MAN=json.loads((R/'data/map_pack/manifest_v038.json').read_text())
checks=[];errors=[]
def ck(name,cond,detail=None):checks.append({'name':name,'ok':bool(cond),'detail':detail});print(('OK ' if cond else 'FAIL ')+name,flush=True)
def vi(n:int)->bytes:
 out=bytearray()
 while True:
  b=n&127;n>>=7;out.append(b|(128 if n else 0))
  if not n:return bytes(out)
def zz(n:int)->int:return (n<<1)^(n>>63)
def field(num:int,wire:int,payload):
 h=vi((num<<3)|wire)
 if wire==0:return h+vi(int(payload))
 return h+vi(len(payload))+payload
def packed(vals):return b''.join(vi(v) for v in vals)
def value_string(s):return field(1,2,s.encode())
def feature(fid,typ,geom,tags=(0,0)):return field(1,0,fid)+field(2,2,packed(tags))+field(3,0,typ)+field(4,2,packed(geom))
def layer(name,features,key='class',value='primary'):
 raw=field(15,0,2)+field(1,2,name.encode())
 for f in features:raw+=field(2,2,f)
 raw+=field(3,2,key.encode())+field(4,2,value_string(value))+field(5,0,4096)
 return field(3,2,raw)
line=[9,zz(0),zz(2048),10,zz(4096),zz(0)]
base_poly=[9,zz(2500),zz(2500),26,zz(500),0,0,zz(500),zz(-500),0,15]
BASE=layer('transportation',[feature(1,2,line)])+layer('building',[feature(10,3,base_poly)],'class','building')
cad_poly=[9,zz(1800),zz(1800),26,zz(2000),0,0,zz(2000),zz(-2000),0,15]
CAD=layer('batiments',[feature(20,3,cad_poly),feature(21,3,cad_poly)],'nature','dur')
EMPTY_SHA=hashlib.sha256(b'').hexdigest()
ck('manifest v0.38 exact',MAN['version']=='0.38.0' and MAN['counts']=={'base':367,'cadastre':5517,'total':5884},MAN.get('counts'))
ck('manifest cache complete',MAN['cloudCache']['complete'] is True and MAN['cloudCache']['storedPbf']==4557 and MAN['cloudCache']['officialEmpty']==1327,MAN['cloudCache'])
ck('relay v0.38 in every row',all('/fallout-mistral-map-v038/' in r['relay'] for r in MAN['tiles']))
requests={'coverage':0,'base':0,'cadastre':0,'empty':0}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate(r'''() => {
  const databases=new Map();
  function open(name,version=1){const req={result:null,error:null};setTimeout(()=>{let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}const db={get objectStoreNames(){return{contains:n=>state.stores.has(n)}},createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,finished=false;const maybe=()=>setTimeout(()=>{if(!pending&&!finished){finished=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{if(!state.stores.has(n))throw new Error('missing store '+n);const store=state.stores.get(n),opts=state.options.get(n)||{};const request=fn=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.();tx.onerror?.()}finally{pending--;maybe()}},0);return q};return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())}};maybe();return tx},close(){}};req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}
  Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}});
 }''')
 def relay(route,req):
  u=req.url
  if u.endswith('/coverage'):
   requests['coverage']+=1;route.fulfill(status=200,content_type='application/json',body=json.dumps({'service':'fallout-mistral-map-v038','version':'0.39.0','plan':{'base':367,'cadastre':5517,'total':5884},'cache':{'base':{'coordinates':367,'pbf':367,'empty':0,'bytes':29456613,'hits':31},'cadastre':{'coordinates':5517,'pbf':4190,'empty':1327,'bytes':57517126,'hits':1},'total':5884,'totalBytes':86973739,'totalEmpty':1327,'complete':True,'newest':'2026-09-19T01:51:42Z'}}));return
  if '/tile/base/' in u:
   requests['base']+=1;route.fulfill(status=200,body=BASE,headers={'content-type':'application/x-protobuf','x-map-cache':'hit','x-map-empty':'0','x-map-sha256':hashlib.sha256(BASE).hexdigest(),'x-map-bytes':str(len(BASE)),'access-control-allow-origin':'*','access-control-expose-headers':'X-Map-Cache, X-Map-Empty, X-Map-SHA256, X-Map-Bytes'});return
  if '/tile/cadastre/16/33730/23996' in u:
   requests['empty']+=1;route.fulfill(status=200,body=b'',headers={'content-type':'application/x-protobuf','x-map-cache':'hit-empty','x-map-empty':'1','x-map-sha256':EMPTY_SHA,'x-map-bytes':'0','access-control-allow-origin':'*','access-control-expose-headers':'X-Map-Cache, X-Map-Empty, X-Map-SHA256, X-Map-Bytes'});return
  if '/tile/cadastre/' in u:
   requests['cadastre']+=1;route.fulfill(status=200,body=CAD,headers={'content-type':'application/x-protobuf','x-map-cache':'hit','x-map-empty':'0','x-map-sha256':hashlib.sha256(CAD).hexdigest(),'x-map-bytes':str(len(CAD)),'access-control-allow-origin':'*','access-control-expose-headers':'X-Map-Cache, X-Map-Empty, X-Map-SHA256, X-Map-Bytes'});return
  route.continue_()
 p.route('**/fallout-mistral-map-v038/**',relay)
 p.set_content(H.read_text(),wait_until='load');p.wait_for_timeout(3600)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  info=c('v038Info');ck('runtime v0.41',info['version']=='0.41.0',info)
  cloud=info['cloud'];ck('coverage cloud is complete',cloud['total']==5884 and cloud['complete'] and cloud['base']==367 and cloud['cadastre']==5517,cloud)
  ck('PBF and empty split exact',cloud['basePbf']==367 and cloud['cadastrePbf']==4190 and cloud['cadastreEmpty']==1327,cloud)
  ck('cloud bytes exact',cloud['bytes']==86973739,cloud)
  ck('manifest permits proof tiles',c('v037Allowed','base',14,8431,6000) and c('v037Allowed','cadastre',16,33757,23976) and c('v037Allowed','cadastre',16,33730,23996))
  full=c('v037Get','cadastre',16,33757,23976);ck('filled cadastral tile loads',full['bytes']==len(CAD) and not full['meta'].get('empty'),full)
  empty=c('v037Get','cadastre',16,33730,23996);ck('official empty tile loads as valid zero bytes',empty['bytes']==0 and empty['meta'].get('empty') is True,empty)
  # Queue the proof tiles in a real macro so the production cache path stores them.
  c('v018LoadMacro','geo_marseille');p.wait_for_timeout(300)
  c('v018Queue','base',14,8431,6000);c('v018Queue','cadastre',16,33757,23976);c('v018Queue','cadastre',16,33730,23996);p.wait_for_timeout(1900)
  local=c('v037Local');ck('local cache tracks filled and empty tiles',local['count']>=3,local)
  before=requests['empty'];empty2=c('v037Get','cadastre',16,33730,23996);ck('official empty tile cached locally',empty2['source']=='cache' and empty2['bytes']==0 and requests['empty']==before,{'got':empty2,'requests':requests})
  c('v027Open','map','coverage');txt=p.locator('#pipContent').inner_text();norm=' '.join(txt.split());ck('Pip-Boy shows complete cache','5 884 / 5 884' in norm and '4 190 PBF + 1 327 vides' in norm,norm[:1500]);ck('Pip-Boy shows RGE ALTI terrain','8 / 8' in norm,norm[:1000]);c('closePip')
  c('v038OpenStatus');txt2=' '.join(p.locator('#v018StatusScreen').inner_text().split());ck('status distinguishes PBF and empty','4 190 + 1 327' in txt2 and '5 884 / 5 884' in txt2,txt2[:1500]);ck('no JavaScript exception',not errors,errors)
 except Exception as e:ck('browser scenario',False,repr(e))
 b.close()
rep={'version':'0.38.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'requests':requests,'checks':checks,'scope':'Exact v0.41 HTML. Controlled MVT plus explicit official-empty fixture. IndexedDB uses an API-compatible memory adapter because opaque-origin native storage is blocked. Live full cache is verified separately; official terrain is verified separately at 8/8.'}
(O/'QA_REGRESSION_V038_ON_V041.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors,'requests':requests},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errors))
