from pathlib import Path
import subprocess,sys,time,urllib.request,socket,json,hashlib,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[2];O=R/'verification/v048';tests=[];errors=[]
def ck(n,ok,d=None):
 tests.append({'name':n,'ok':bool(ok),'detail':d});print(('OK ' if ok else 'FAIL ')+n,flush=True)
with socket.socket() as sock:
 sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
log=open(O/'server_io.log','w');server=subprocess.Popen([sys.executable,str(R/'tools/serve_game.py'),'--port',str(port),'--no-browser'],cwd=R,stdout=log,stderr=log);base=f'http://127.0.0.1:{port}'
try:
 for _ in range(80):
  try:
   with urllib.request.urlopen(base+'/index.html',timeout=2) as r:html=r.read().decode('utf-8')
   break
  except OSError:time.sleep(.1)
 ck('Le serveur distribue le HTML final exact',hashlib.sha256(html.encode()).hexdigest()==hashlib.sha256((R/'index.html').read_bytes()).hexdigest())
 with urllib.request.urlopen(base+'/__mistral/local-data') as r:
  local=json.load(r);headers=dict(r.headers)
 ck('Audit local réellement exécuté',local['version']=='0.48.0',local)
 ck('Absence de pack signalée et non masquée',local['vector']['missing']==5884 and local['terrain']['missing']==8 and not local['complete'],local)
 ck('Audit interdit en cache périmé',headers.get('Cache-Control')=='no-store',headers)
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(e.stack));raw=(R/'data/fixtures/france-vector-z14-8437-6001.pbf').read_bytes();control={'bad':False,'html':False};calls=[]
  def remote(route):
   u=route.request.url
   if u.endswith('/14/8437/6001.pbf'):
    calls.append(u);body=b'<html>missing map</html>' if control['html'] else raw
    route.fulfill(status=200,body=body,headers={'Content-Type':'text/html' if control['html'] else 'application/x-protobuf','Access-Control-Allow-Origin':'*','Access-Control-Expose-Headers':'X-Map-SHA256','X-Map-SHA256':'0'*64 if control['bad'] else hashlib.sha256(body).hexdigest()})
   else:route.abort()
  p.route('https://**/*',remote);p.set_content(html,wait_until='load');p.wait_for_timeout(3100)
  def c(n,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(args))
  r=c('v047FetchKey','base:14:8437:6001');ck('PBF réel de fixture validé via réponses HTTP contrôlées',r['bytes']==len(raw) and len(r['layers'])>0,r)
  control['bad']=True
  result=p.evaluate("async()=>{try{await __MISTRAL_DEBUG.v047FetchKey('base:14:8437:6001');return {ok:true}}catch(e){return{ok:false,error:e.message}}}")
  ck('Empreinte corrompue refusée, même sans WebCrypto',not result['ok'] and 'Empreinte' in result['error'],result)
  control['html']=True
  result=p.evaluate("async()=>{try{await __MISTRAL_DEBUG.v047FetchKey('base:14:8437:6001');return {ok:true}}catch(e){return{ok:false,error:e.message}}}")
  ck('Une page HTML ne devient pas une tuile',not result['ok'] and 'HTML' in result['error'],result)
  r=p.evaluate("async()=>{try{await __MISTRAL_DEBUG.v047FetchKey('cadastre:16:0:0');return true}catch(e){return false}}")
  ck('Coordonnées hors manifeste refusées',r is False)
  c('v047OpenStatus');ck('Diagnostics sont rendus par le programme','LE TERRITOIRE EN AVANCE' in p.locator('#v047StatusContent').inner_text())
  ck('Aucune exception JavaScript',not errors,errors);b.close()
except Exception:ck('Scénario serveur et E/S',False,traceback.format_exc())
finally:
 server.terminate();server.wait(timeout=10);log.close()
r={'version':'0.47.0','html_sha256':hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.48.html').read_bytes()).hexdigest(),'passed':sum(t['ok'] for t in tests),'failed':sum(not t['ok'] for t in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'Serveur HTTP loopback réel interrogé par Python ; logique navigateur exécutée par set_content avec réponses réseau contrôlées. Navigation du navigateur bloquée par politique administrateur : pas de validation IndexedDB natif.'};(O/'QA_SERVER_IO.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(r['failed'] or errors))
