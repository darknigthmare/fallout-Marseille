#!/usr/bin/env python3
from pathlib import Path
import json, hashlib, math, subprocess, tempfile, shutil
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
from mvt_audit_v036 import parse_tile

R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True)
H=(R/'JOUER_FALLOUT_MISTRAL_v0.36.html').read_text(encoding='utf-8')
MAN=json.loads((R/'data/map_pack/manifest_v036.json').read_text(encoding='utf-8'))
BASE=(R/'data/fixtures/france-vector-z14-8437-6001.pbf').read_bytes();CAD=(R/'data/fixtures/cadastre-z16-33750-24006.pbf').read_bytes()
checks=[];errors=[]
def ck(name,cond,detail=None):checks.append({'name':name,'ok':bool(cond),'detail':detail});print(('OK ' if cond else 'FAIL ')+name,flush=True)
# Static/source contract
ck('manifest 367 tuiles base',MAN['counts']['base']==367,MAN['counts'])
ck('manifest 5517 tuiles cadastre',MAN['counts']['cadastre']==5517,MAN['counts'])
ck('manifest total 5884',MAN['counts']['total']==5884,MAN['counts'])
ck('huit macro-régions au manifeste',len(MAN['macros'])==8,list(MAN['macros']))
ck('aucune tuile marquée installée artificiellement',all(x['status']=='planned' and x['sha256'] is None for x in MAN['tiles']))
ck('fixtures MVT valides',bool(parse_tile(BASE)) and bool(parse_tile(CAD)))
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
 def route_handler(route,req):
  url=req.url
  if url.endswith('/meta'):
   route.fulfill(status=200,content_type='application/json',body=json.dumps({'service':'fallout-mistral-map-v036','version':'0.36.0','sources':{'base':{'count':367},'cadastre':{'count':5517}},'total':5884}))
  elif '/tile/base/' in url: route.fulfill(status=200,content_type='application/x-protobuf',body=BASE)
  elif '/tile/cadastre/' in url: route.fulfill(status=200,content_type='application/x-protobuf',body=CAD)
  else: route.continue_()
 p.route('**/fallout-mistral-map-v036/**',route_handler)
 p.set_content(H,wait_until='load');p.wait_for_timeout(3500)
 p.evaluate("window.__CAPSTORE={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__CAPSTORE[k]??null,setItem:(k,v)=>__CAPSTORE[k]=String(v),removeItem:k=>delete __CAPSTORE[k]}})")
 def c(name,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+name+'(...a)',list(args))
 try:
  info=c('v036Info');ck('runtime v0.36 chargé',info['version']=='0.36.0',info)
  ck('huit macro-régions dans le moteur',len(c('v036Macros'))==8,c('v036Macros'))
  # health/manifest through the authenticated-relay code path (network fulfilled in-browser)
  ck('vérification manifeste relayée',c('v036Health'))
  p.wait_for_timeout(100);ck('état relais prêt',c('v036Info')['relay']['state']=='ready',c('v036Info')['relay'])
  # Real streaming pipeline, with valid MVT bytes delivered by the route fixture.
  c('v018LoadMacro','geo_marseille');p.wait_for_timeout(500)
  c('v018Queue','base',14,8437,6001);c('v018Queue','cadastre',16,33750,24006);p.wait_for_timeout(1200)
  st=c('v036Info');ck('deux tuiles passées par le pipeline MVT',st['runtime']['loaded']>=2,st)
  geom=c('v018Geometry');ck('routes/polygones/bâtiments rendus',len(geom)>0,{'geometry':len(geom),'status':st})
  ck('source de streaming officielle/relay',st['runtime']['source'] in ('relay','live','cache','pack'),st['runtime']['source'])
  # Coverage UI no longer claims that all official data are absent.
  c('v027Open','map','coverage');txt=p.locator('#pipContent').inner_text();ck('Pip-Boy affiche 5 884',('5884' in txt.replace(' ','').replace('\u202f','').replace('\xa0','')),txt[:900]);ck('terrain 0/8 signalé',('0/8' in txt.replace(' ','')),txt[:900]);c('closePip')
  # Seamless macro transfer preserves geographic location.
  c('v018LoadMacro','geo_marseille');p.wait_for_timeout(400);target=[43.2900,5.5200];c('v036SetLatLon',*target);before=c('v036Position')['ll'];moved=c('v036TryTransfer');p.wait_for_timeout(700);after=c('v036Position')
  ck('transfert automatique Marseille→Huveaune',moved and after['id']=='geo_huveaune',{'before':before,'after':after})
  ck('position WGS84 conservée',abs(after['ll'][0]-target[0])<2e-5 and abs(after['ll'][1]-target[1])<2e-5,after)
  # Metadata/source contract in runtime.
  sources=c('v036Sources');ck('source locale + relay + directe',all(all(k in sources[s] for k in ['local','relayUrl','directUrl']) for s in ['base','cadastre']),sources)
  ck('aucun MNT officiel faussement annoncé',c('v036Plan')['terrainBundled']==0,c('v036Plan'))
 except Exception as e:
  ck('scénario navigateur sans exception',False,repr(e))
 b.close()
# Installer/audit tool dry contracts.
proc=subprocess.run(['python3',str(R/'tools/install_real_map_v036.py'),'--dry-run','--source','base','--macro','geo_marseille'],capture_output=True,text=True)
ck('installateur reprenable sélectionne Marseille',proc.returncode==0 and '88 tuiles' in proc.stdout,proc.stdout+proc.stderr)
proc2=subprocess.run(['python3',str(R/'tools/terrain_real_v036.py'),'--plan-only'],capture_output=True,text=True)
ck('terrain refuse d’inventer des altitudes',proc2.returncode==0 and 'waiting-official-numeric-source' in proc2.stdout,proc2.stdout[:600])
rep={'version':'0.36.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'Exact v0.36 HTML; valid synthetic MVT bytes only for browser pipeline QA. Server-side external verification is documented separately. No official numeric terrain bundled.'}
(O/'QA_V036.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors},ensure_ascii=False));raise SystemExit(0 if not rep['failed'] and not errors else 1)
