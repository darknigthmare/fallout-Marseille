from pathlib import Path
import subprocess,sys,time,urllib.request,socket,json,hashlib,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2];O=R/'verification/v047';O.mkdir(exist_ok=True);tests=[];errors=[]
def ck(n,ok,d=None):
 tests.append({'name':n,'ok':bool(ok),'detail':d});print(('OK ' if ok else 'FAIL ')+n,flush=True)
with socket.socket() as sock:
 sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
log=open(O/'native_server.log','w');server=subprocess.Popen([sys.executable,str(R/'tools/serve_game.py'),'--port',str(port),'--no-browser'],cwd=R,stdout=log,stderr=log)
base=f'http://127.0.0.1:{port}'
try:
 for _ in range(80):
  try:urllib.request.urlopen(base+'/index.html',timeout=1).close();break
  except OSError:time.sleep(.1)
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);ctx=b.new_context(viewport={'width':1440,'height':900},service_workers='block');p=ctx.new_page();p.on('pageerror',lambda e:errors.append(e.stack))
  raw=(R/'data/fixtures/france-vector-z14-8437-6001.pbf').read_bytes();digest=hashlib.sha256(raw).hexdigest();calls=[];control={'bad':False,'disabled':False,'emptyWrong':False}
  def remote(route):
   u=route.request.url
   if '/14/8437/6001.pbf' in u and not control['disabled']:
    calls.append(u);route.fulfill(status=200,body=raw,headers={'Content-Type':'application/x-protobuf','Access-Control-Allow-Origin':'*','Access-Control-Expose-Headers':'X-Map-SHA256,X-Map-Empty','X-Map-SHA256':'0'*64 if control['bad'] else digest})
   else:route.abort()
  p.route('https://**/*',remote)
  p.goto(base+'/index.html',wait_until='load');p.wait_for_timeout(3100)
  def c(n,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
  # The manifest/status is a real loopback endpoint, not an injected success counter.
  local=c('v047ReadLocal');ck('Audit local depuis le serveur exécuté',local is not None and local['version']=='0.47.0',local)
  ck('Les fichiers non installés sont comptés comme absents',local['vector']['missing']==5884 and local['terrain']['missing']==8 and not local['complete'],local)
  r=c('v047FetchKey','base:14:8437:6001');ck('PBF existant de fixture reçu par HTTP contrôlé',r['bytes']==len(raw) and r['origin']=='cache distant',r)
  databases=p.evaluate('indexedDB.databases()');ck('IndexedDB natif réellement ouvert',any('mistral' in x.get('name','').lower() for x in databases),databases)
  old=len(calls);control['disabled']=True;r=c('v047FetchKey','base:14:8437:6001');ck('Deuxième lecture depuis le cache natif',r['origin']=='cache navigateur' and len(calls)==old,r)
  p.reload(wait_until='load');p.wait_for_timeout(1000);r=c('v047FetchKey','base:14:8437:6001');ck('Cache natif conservé après rechargement de page',r['origin']=='cache navigateur',r)
  # New origin storage context for an invalid checksum test.
  other=b.new_context(service_workers='block');q=other.new_page();q.on('pageerror',lambda e:errors.append(e.stack));control['disabled']=False;control['bad']=True;q.route('https://**/*',remote);q.goto(base+'/index.html',wait_until='load');q.wait_for_timeout(1100)
  checksum=q.evaluate('''async()=>{try{await __MISTRAL_DEBUG.v047FetchKey('base:14:8437:6001');return {accepted:true}}catch(e){return {accepted:false,message:e.message}}}''');ck('Empreinte SHA-256 fausse refuse la ressource',not checksum['accepted'] and 'Empreinte' in checksum['message'],checksum)
  # A body declared officially empty must not point to a different tile.
  q.route('**/data/map_pack/cadastre/16/33750/24006.pbf',lambda r:r.fulfill(status=200,body=b'',content_type='application/x-protobuf'))
  q.route('**/data/map_pack/cadastre/16/33750/24006.pbf.empty.json',lambda r:r.fulfill(status=200,json={'officialEmpty':True,'source':'cadastre','z':16,'x':0,'y':0}))
  empty=q.evaluate('''async()=>{try{await __MISTRAL_DEBUG.v047FetchKey('cadastre:16:33750:24006');return {accepted:true}}catch(e){return {accepted:false,message:e.message}}}''');ck('Marqueur vide d’une autre coordonnée refusé',not empty['accepted'],empty)
  # Menu not a new global assertion: the visible screen itself reads the actual report.
  c('v047OpenStatus');txt=p.locator('#v047StatusContent').inner_text();ck('Statut du disque visible dans le programme','5884 absentes' in txt and 'serveur local' in txt,txt[-2000:])
  ck('Aucune exception JavaScript',not errors,errors);other.close();ctx.close();b.close()
except Exception:ck('Scénario HTTP et cache',False,traceback.format_exc())
finally:
 server.terminate();server.wait(timeout=10);log.close()
r={'version':'0.47.0','html_sha256':hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.47.html').read_bytes()).hexdigest(),'passed':sum(t['ok'] for t in tests),'failed':sum(not t['ok'] for t in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'Serveur loopback réel, IndexedDB natif de Chromium. Une fixture PBF fournie est transportée par réponses réseau contrôlées ; aucune nouvelle donnée territoriale acquise.'};(O/'QA_NATIVE_CACHE.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(r['failed'] or errors))
