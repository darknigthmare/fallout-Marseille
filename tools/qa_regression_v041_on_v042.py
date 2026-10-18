#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=R/'JOUER_FALLOUT_MISTRAL_v0.42.html';checks=[];errors=[]
def ck(n,c,d=None):checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort())
 p.set_content(H.read_text(encoding='utf-8'),wait_until='load');p.wait_for_timeout(600)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 try:
  ck('titre v0.42','v0.42' in p.title(),p.title());ck('surface debug pack',p.evaluate("typeof __MISTRAL_DEBUG.v041Info")=='function')
  info=c('v041Info');ck('snapshot 24 archives',info['remote']['chunkCount']==24 and info['remote']['coordinates']==5884,info['remote']);ck('répartition exacte',info['remote']['baseCoordinates']==367 and info['remote']['cadastreCoordinates']==5517 and info['remote']['officialEmpty']==1327,info['remote'])
  c('v020Reset');c('v020Load','transit_depot');p.wait_for_timeout(150);pi=c('v027Info');ck('onglet PACK LOCAL présent','pack' in pi['subtabs']['map'],pi['subtabs']['map'])
  c('v027Open','map','pack');txt=' '.join(p.locator('#pipContent').inner_text().split());ck('Pip-Boy explique le pack','PACK TERRITORIAL LOCAL' in txt and '24/24' in txt and '5 884' in txt,txt[:1600])
  c('closePip');c('v041SetLocal',{'state':'ready','complete':True,'coordinates':5884,'objects':4557,'officialEmpty':1327,'missing':0,'invalid':0,'bytes':86973739,'terrain':8});c('v041SetBenchmark',{'state':'ready','sampledPbf':4557,'decodedBytes':86973739,'seconds':4.2,'throughputMiBps':19.75,'tilesPerSecond':1085.0,'p95':2.1,'peakRssKiB':150000,'terrain':8,'completePack':True});c('v027Open','map','pack');txt2=' '.join(p.locator('#pipContent').inner_text().split());ck('état local complet rendu','PACK LOCAL CERTIFIÉ' in txt2 and '4557 PBF' in txt2 and '1085' in txt2,txt2[:1800]);c('closePip')
  c('v041OpenStatus');st=' '.join(p.locator('#v018StatusScreen').inner_text().split());ck('statut v0.42 local','PACK LOCAL ET BENCHMARK' in st and '5 884' in st and '19.75 Mio/s' in st,st[:1800])
  manifest=json.loads((R/'data/map_pack/local_pack_v041_manifest.json').read_text());ck('manifeste 24 lots',manifest['chunkCount']==24 and len(manifest['chunks'])==24,manifest);ck('taille distribution exacte',manifest['totalBase64Bytes']==119130028,manifest['totalBase64Bytes'])
  ck('aucune exception JavaScript',not errors,errors)
 except Exception as e:ck('scénario navigateur v0.42',False,repr(e))
 b.close()
rep={'version':'0.42.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'Exact v0.42 HTML with remote Supabase requests deliberately blocked. Embedded distribution snapshot, local-pack UI, benchmark rendering and production manifest are verified.'};(O/'QA_REGRESSION_V041_ON_V042.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errors))
